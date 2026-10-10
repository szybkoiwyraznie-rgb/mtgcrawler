"""Export event strings to readable, translation-AI-friendly files.

This is the *source-extraction* half of the pipeline: it walks every narration record in
every EVNT member of the given event packages, decodes the Shift-JIS (CP932) text, and writes
structured JSON that a specialised translation model can consume. It performs **no
translation** -- it only produces clean, machine-readable source files plus per-line display
widths that bound the target text (the in-game box clips over-long lines).

The output is written under ``local/`` (gitignored): the full Japanese script must never be
committed to the repository, so these files live outside git by design.

Record layout (see grow_event_text): ``type(4) length(4) parameter(4) text(N) 00 00`` with
``length == 12 + N + 2``. Lines inside a record are separated by 0x0A.
"""
from __future__ import annotations

import json
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Iterable, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_write
import crilayla

RECORD_TYPE = bytes.fromhex("b7010000")
TERMINATOR = b"\x00\x00"
HEADER_OVERHEAD = 12  # type + length + parameter
RECORD_OVERHEAD = HEADER_OVERHEAD + len(TERMINATOR)


def iter_records(data: bytes) -> Iterable[tuple[int, bytes]]:
    """Yield ``(record_offset, text_bytes)`` for every narration record in *data*."""
    cursor = 0
    while True:
        at = data.find(RECORD_TYPE, cursor)
        if at < 0 or at % 4:
            # Only accept 4-aligned occurrences; stray byte patterns are ignored.
            if at < 0:
                return
            cursor = at + 1
            continue
        length = struct.unpack_from("<I", data, at + 4)[0]
        if length < RECORD_OVERHEAD or at + HEADER_OVERHEAD + (length - RECORD_OVERHEAD) > len(data):
            cursor = at + 4
            continue
        text_len = length - RECORD_OVERHEAD
        text = data[at + HEADER_OVERHEAD: at + HEADER_OVERHEAD + text_len]
        # A record's text must be followed by the 00 00 terminator.
        if data[at + HEADER_OVERHEAD + text_len: at + HEADER_OVERHEAD + text_len + 2] != TERMINATOR:
            cursor = at + 4
            continue
        yield at, text
        cursor = at + length


def decode(text: bytes) -> str:
    return text.decode("cp932", errors="replace")


def display_width(s: str) -> int:
    """Approximate on-screen width: full-width (CJK) chars count 2, others 1."""
    total = 0
    for ch in s:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 2
        else:
            total += 1
    return total


def export_member(member_name: str, data: bytes) -> List[dict]:
    out = []
    for idx, (off, text) in enumerate(iter_records(data)):
        decoded = decode(text)
        lines = decoded.split("\n")
        out.append({
            "member": member_name,
            "record_index": idx,
            "record_offset": off,
            "source": decoded,
            "lines": lines,
            "source_bytes": len(text),
            "max_line_width": max((display_width(l) for l in lines), default=0),
            "line_count": len(lines),
            "target": "",
        })
    return out


def export_package(path: Path) -> List[dict]:
    cpk = cpk_write.load(path)
    rows: List[dict] = []
    for m in cpk.members:
        try:
            body = crilayla.decompress(m.blob).data if crilayla.is_crilayla(m.blob) else m.blob
        except Exception:
            continue
        if body[:4] != b"EDAT":
            continue
        rows.extend(export_member(m.name, body))
    return rows


def main(argv: Optional[list[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: export_strings.py <eventPxx.EDAT> [...] [--out DIR]")
        return 2
    out_dir = Path("local/strings")
    if "--out" in args:
        i = args.index("--out")
        out_dir = Path(args[i + 1])
        del args[i:i + 2]
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for arg in args:
        rows = export_package(Path(arg))
        name = Path(arg).stem
        dest = out_dir / f"{name}.strings.json"
        dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        summary[name] = {"records": len(rows), "file": str(dest)}
        print(f"{name}: {len(rows)} records -> {dest}")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
