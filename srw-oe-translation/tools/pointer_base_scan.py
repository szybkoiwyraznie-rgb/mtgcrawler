"""Find the load base that turns this file's u32 words into pointers at its strings.

Why this tool exists. `retro-trans/SRW-Z`, `tools/pool.py`, on the sibling engine:

    THE FINDING (2026-08-26). Weapon/ability/item names are NOT walked and NOT indexed.
    COMPDATA.BN's single 524,032-byte record ends in a string pool, and every string is
    reached through an ABSOLUTE PS2 RAM POINTER stored earlier in the same record.
    ...
    That is why the byte budget looked immovable: every static search for an index, a
    record-relative offset, or an offset/8 failed, because the stored value is 0x0073xxxx.

So the stored value is `LOAD_BASE + file_offset`. A search for the bare offset finds nothing, which is
exactly what `tools/boundary_probe.py` measured here (milestone 61) and why that negative result said
less than it looked like.

The search is cheap because one file holds only a few hundred strings. For every candidate base B and
every string start S in the file, ask whether `B + S` occurs as a u32 anywhere in the file. If a
pointer table exists, one B lights up most of the strings at once.

Candidates are the PSP's user-memory window (0x08800000-0x0A000000, where a PSP game loads a file),
plus small constants, in case the base is a buffer offset rather than a RAM address.

Usage::

    python tools/pointer_base_scan.py FILE [FILE ...]
    python tools/pointer_base_scan.py --out report.json FILE

Read-only; prints counts and offsets, never decoded text.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_event_text  # noqa: E402  (the project's own unit scanner)

SCHEMA = "srw-oe-pointer-base-scan/1"
PSP_USER_LO = 0x0880_0000
PSP_USER_HI = 0x0A00_0000
PSP_STEP = 0x4000  # 16 KiB: fine enough to land on a buffer start, coarse enough to be cheap
SMALL_CONSTANTS = tuple(range(0, 65))  # a header length, or an offset from the content start
TOP_N = 8


def text_starts(data: bytes) -> list[int]:
    """Every unit's text start: the byte after `FF FF`."""
    envelopes, _tail = extract_event_text.select_envelopes(data)
    return [envelope.start_offset for envelope in envelopes]


def marker_offsets(data: bytes) -> list[int]:
    envelopes, _tail = extract_event_text.select_envelopes(data)
    return [envelope.marker_offset for envelope in envelopes]


def word_values(data: bytes, aligned_only: bool) -> Counter:
    """Every u32 little-endian word in the file, as value -> how many times it occurs."""
    step = 4 if aligned_only else 1
    limit = len(data) - 3
    counter: Counter = Counter()
    for offset in range(0, limit, step):
        counter[struct.unpack_from("<I", data, offset)[0]] += 1
    return counter


def candidate_bases() -> tuple[int, ...]:
    psp = range(PSP_USER_LO, PSP_USER_HI, PSP_STEP)
    return tuple(SMALL_CONSTANTS) + tuple(psp)


def scan(
    data: bytes,
    targets: Iterable[int],
    values: Counter,
    bases: Iterable[int] = (),
) -> list[dict[str, Any]]:
    """Rank candidate bases by how many of `targets` they turn into a word present in the file."""
    targets = sorted(set(targets))
    if not targets:
        return []
    rows: list[dict[str, Any]] = []
    for base in bases or candidate_bases():
        hits = [target for target in targets if (base + target) in values]
        if not hits:
            continue
        rows.append(
            {
                "base": base,
                "base_hex": f"0x{base:08X}",
                "hits": len(hits),
                "share": round(len(hits) / len(targets), 4),
                "occurrences": sum(values[base + target] for target in hits),
            }
        )
    rows.sort(key=lambda row: (-row["hits"], row["base"]))
    return rows


def hit_positions(data: bytes, base: int, targets: Iterable[int], aligned_only: bool) -> list[int]:
    """Where the words `base + target` actually sit, so a table shows up as a run of positions."""
    wanted = {base + target for target in targets}
    step = 4 if aligned_only else 1
    limit = len(data) - 3
    positions = []
    for offset in range(0, limit, step):
        if struct.unpack_from("<I", data, offset)[0] in wanted:
            positions.append(offset)
    return positions


def scan_file(path: Path, aligned_only: bool = True) -> dict[str, Any]:
    data = path.read_bytes()
    starts = text_starts(data)
    values = word_values(data, aligned_only)
    rows = scan(data, starts, values)
    control = scan(data, [start + 1 for start in starts], values)

    best = rows[0] if rows else None
    positions: list[int] = []
    clustered = False
    if best:
        positions = hit_positions(data, best["base"], starts, aligned_only)
        if positions:
            span = positions[-1] - positions[0]
            # A table is a dense run: many hits inside a span proportional to their count.
            clustered = span < len(positions) * 64
    return {
        "schema": SCHEMA,
        "file": path.name,
        "size": len(data),
        "aligned_only": aligned_only,
        "units": len(starts),
        "distinct_words": len(values),
        "top_bases": rows[:TOP_N],
        "best_control": control[0] if control else None,
        "best_positions_head": positions[:24],
        "best_positions_span": (positions[-1] - positions[0]) if positions else None,
        "best_positions_clustered": clustered,
        "candidates_tested": len(candidate_bases()),
    }


def report_lines(result: dict[str, Any]) -> list[str]:
    lines = [
        f"{result['file']}: {result['size']} bytes, {result['units']} text starts,"
        f" {result['candidates_tested']} candidate bases tested"
        f" ({'4-aligned' if result['aligned_only'] else 'every byte offset'} u32 words)",
    ]
    if not result["top_bases"]:
        lines.append("  no candidate base turned any text start into a word in this file")
        return lines
    top = ", ".join(
        f"{row['base_hex']} x{row['hits']} ({row['share']:.0%})" for row in result["top_bases"][:5]
    )
    lines.append(f"  best bases by strings reached: {top}")
    control = result["best_control"]
    if control:
        lines.append(
            f"  same search with every start shifted by +1: best {control['base_hex']}"
            f" x{control['hits']} - if that is close to the real best, the result is chance"
        )
    else:
        lines.append("  control (starts shifted by +1): no base reached any of them")
    if result["best_positions_span"] is not None:
        verdict = "a dense run, i.e. a table" if result["best_positions_clustered"] else "scattered"
        lines.append(
            f"  the winning words sit across {result['best_positions_span']} bytes: {verdict}"
        )
    return lines


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--unaligned", action="store_true", help="also read words at every byte offset (slow)")
    parser.add_argument("--out", type=Path, help="write the JSON result here")
    args = parser.parse_args(argv)

    results = []
    for path in args.files:
        if not path.is_file():
            print(f"input not found: {path}", file=sys.stderr)
            return 2
        result = scan_file(path, aligned_only=not args.unaligned)
        results.append(result)
        for line in report_lines(result):
            print(line)
    if args.out:
        args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"json written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
