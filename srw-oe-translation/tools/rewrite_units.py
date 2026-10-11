"""Write translated text back into an extracted game file, byte for byte in length.

This is the step the method sources say is safe. Two independent accounts of this engine family:

- `retro-trans/SRW-Z`, `docs/FINDINGS.md`: "In-place replacement must preserve each string's **exact
  byte length** ... This is safe and verified. Growing strings is not safe without also rewriting
  every inline offset operand."
- CrashmanX, who started the English patch for this very game (gbatemp thread 351431, 2013): "I'm
  currently dealing with the constraint of having to use the same amount of spaces as the Japanese
  characters."

So the writer enforces one rule and nothing else: **the replacement is exactly as long as the
original.** Because the file length never changes, no offset anywhere in the file can move — which is
why the project does not have to understand the pointer layout to produce a testable patch.

Input is the filled-in `translation/units.csv` (`unit_id, package_id, file, source_text,
target_text, budget_bytes, ...`). Each `unit_id` is `<file name>@<start offset in hex>`, so a row is
located directly, and its `source_text` is re-encoded and compared with the bytes actually in the file
before anything is written. If they disagree, the file is refused, not patched.

Output goes to `--out`; the extracted files are opened read-only and never modified.

Usage::

    python tools/rewrite_units.py --csv units.csv --extracted work/extracted --out work/rewritten
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_event_text  # noqa: E402  (the project's own codec and envelope scanner)
import translation_tools  # noqa: E402  (the same row checks the template report already applies)

MARKER = extract_event_text.MARKER
STOP = extract_event_text.STOP
DEFAULT_PAD_BYTE = 0x20  # ASCII space: cannot create a 00 00 stop and cannot be mistaken for data


class RewriteError(ValueError):
    """Raised for anything that would make a written file differ in length or content from intent."""


def parse_unit_id(unit_id: str) -> tuple[str, int]:
    """`name@1A40` -> ('name', 0x1A40)."""
    name, _, offset = unit_id.rpartition("@")
    if not name or not offset:
        raise RewriteError(f"unit id {unit_id!r} is not '<file>@<hex offset>'")
    try:
        return name, int(offset, 16)
    except ValueError as error:
        raise RewriteError(f"unit id {unit_id!r} has a non-hex offset: {error}") from error


def unit_span(data: bytes, start_offset: int, unit_id: str) -> tuple[int, int, bytes, bytes]:
    """Return (start, pair, prefix, suffix) for the unit starting at `start_offset`."""
    if data[start_offset - len(MARKER) : start_offset] != MARKER:
        raise RewriteError(f"{unit_id}: no FF FF marker immediately before offset {start_offset}")
    pair = data.find(STOP, start_offset)
    if pair < 0:
        raise RewriteError(f"{unit_id}: no 00 00 stop after offset {start_offset}")
    body = data[start_offset:pair]
    first_nul = body.find(b"\x00")
    if first_nul < 0:
        return start_offset, pair, body, b""
    return start_offset, pair, body[:first_nul], body[first_nul:]


def resolve_file(root: Path, wanted: str) -> Path:
    """Find the extracted file a CSV row refers to, refusing anything ambiguous."""
    direct = root / wanted
    if direct.is_file():
        return direct
    matches = [path for path in root.rglob("*") if path.is_file() and path.name == wanted]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise RewriteError(f"{wanted}: not found under {root}")
    raise RewriteError(f"{wanted}: {len(matches)} files with that name under {root}, so it is ambiguous")


def rewrite_bytes(
    data: bytes,
    rows: list[dict[str, str]],
    pad_byte: int = DEFAULT_PAD_BYTE,
) -> tuple[bytes, dict[str, Any]]:
    """Apply every row to `data` in memory. The result is always exactly `len(data)` bytes."""
    if not 0 < pad_byte < 0x100 or pad_byte == 0:
        raise RewriteError("pad byte must be 1..255 and cannot be 0x00 (it would end the string)")

    stats = {"rewritten": 0, "skipped_empty": 0, "skipped_same": 0, "padded": 0, "refused": []}
    out = bytearray(data)
    for row in rows:
        unit_id = row["unit_id"]
        source = row.get("source_text", "")
        target = row.get("target_text", "")
        if not target.strip():
            stats["skipped_empty"] += 1
            continue
        if target == source:
            stats["skipped_same"] += 1
            continue

        problems = translation_tools.check_row(source, target, int(row.get("budget_bytes") or 0))
        if problems:
            stats["refused"].append((unit_id, problems))
            continue

        try:
            _name, start_offset = parse_unit_id(unit_id)
            start, pair, prefix, suffix = unit_span(bytes(out), start_offset, unit_id)
        except RewriteError as error:
            stats["refused"].append((unit_id, [str(error)]))
            continue

        if extract_event_text.from_view(source) != prefix:
            stats["refused"].append(
                (unit_id, ["source_text does not match the bytes in the file, so the file is stale"])
            )
            continue

        replacement = extract_event_text.from_view(target)
        if len(replacement) > len(prefix):
            stats["refused"].append(
                (unit_id, [f"{len(replacement)} bytes over the {len(prefix)}-byte slot"])
            )
            continue
        if len(replacement) < len(prefix):
            replacement += bytes([pad_byte]) * (len(prefix) - len(replacement))
            stats["padded"] += 1
        assert len(replacement) == len(prefix), "length-preserving write-back broke"
        out[start:pair] = replacement + suffix
        stats["rewritten"] += 1

    if len(out) != len(data):
        raise RewriteError(f"internal error: output is {len(out)} bytes, input was {len(data)}")
    return bytes(out), stats


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    missing = [name for name in ("unit_id", "file", "source_text", "target_text") if rows and name not in rows[0]]
    if missing:
        raise RewriteError(f"{csv_path}: missing columns {', '.join(missing)}")
    return rows


def rewrite_tree(csv_path: Path, extracted: Path, out_root: Path, pad_byte: int = DEFAULT_PAD_BYTE) -> dict:
    """Rewrite every file the CSV touches, mirroring its path under `out_root`."""
    rows = load_rows(csv_path)
    by_file: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_file.setdefault(row["file"], []).append(row)

    files: list[dict[str, Any]] = []
    totals = {"files": 0, "rewritten": 0, "padded": 0, "skipped_empty": 0, "skipped_same": 0, "refused": 0}
    for name, file_rows in sorted(by_file.items()):
        source_path = resolve_file(extracted, name)
        data = source_path.read_bytes()
        rewritten, stats = rewrite_bytes(data, file_rows, pad_byte)
        target_path = out_root / source_path.relative_to(extracted)
        if rewritten != data:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(rewritten)
        totals["files"] += 1
        totals["rewritten"] += stats["rewritten"]
        totals["padded"] += stats["padded"]
        totals["skipped_empty"] += stats["skipped_empty"]
        totals["skipped_same"] += stats["skipped_same"]
        totals["refused"] += len(stats["refused"])
        files.append(
            {
                "file": name,
                "path": str(target_path.relative_to(out_root)),
                "changed": rewritten != data,
                "size": len(data),
                "size_after": len(rewritten),
                **{key: stats[key] for key in ("rewritten", "padded", "skipped_empty", "skipped_same")},
                "refused": stats["refused"],
            }
        )
    return {"totals": totals, "files": files}


def report_lines(result: dict[str, Any]) -> list[str]:
    totals = result["totals"]
    lines = [
        "rewrite (equal-length write-back):"
        f" {totals['files']} files, {totals['rewritten']} units rewritten,"
        f" {totals['padded']} padded with 0x20, {totals['refused']} refused,"
        f" {totals['skipped_empty']} blank, {totals['skipped_same']} unchanged",
    ]
    for entry in result["files"]:
        if entry["changed"] or entry["refused"]:
            flag = "rewrote" if entry["changed"] else "unchanged"
            lines.append(
                f"  {entry['file']}: {flag}, {entry['rewritten']} units,"
                f" size {entry['size']} -> {entry['size_after']}"
            )
        for unit_id, problems in entry["refused"][:10]:
            lines.append(f"    refused {unit_id}: {'; '.join(problems)}")
    refused = totals["refused"]
    if refused:
        lines.append(f"  {refused} units were refused and left in Japanese; nothing else was touched")
    return lines


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path, help="the filled-in translation/units.csv")
    parser.add_argument("--extracted", required=True, type=Path, help="the run folder's extracted tree")
    parser.add_argument("--out", required=True, type=Path, help="where to write the rewritten files")
    parser.add_argument(
        "--pad-byte",
        type=lambda text: int(text, 0),
        default=DEFAULT_PAD_BYTE,
        help="byte used to fill a shorter translation (default 0x20, never 0x00)",
    )
    args = parser.parse_args(argv)

    for path in (args.csv, args.extracted):
        if not path.exists():
            print(f"input not found: {path}", file=sys.stderr)
            return 2
    try:
        result = rewrite_tree(args.csv, args.extracted, args.out, args.pad_byte)
    except RewriteError as error:
        print(f"refusing to write: {error}", file=sys.stderr)
        return 2
    for line in report_lines(result):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
