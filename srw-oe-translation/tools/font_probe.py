#!/usr/bin/env python3
"""Read-only probe of font.cpk (PSP font container), numbers only.

FACTS (2026-10-11, measured on the disc-side font.cpk from USRDIR, 242896 bytes):
* CPK header: Files=1, ContentOffset=4096, ItocOffset=2048 (ITOC layout, no TOC).
* The only entry is ID00000 (ITOC blob layout: ID / FileSize / ExtractSize, no offsets). Its data
  starts at ContentOffset (4096) and is CRILAYLA-compressed: 238800 stored -> 397504 extracted.
* Decompressed archive starts with a small header (u32 0x10, u32 7, u32 0x20) followed by
  per-file records (u32 offset, u32 size, name). Names seen: ``ank.fta``, ``kanji22.fta`` and a
  ``kanji21L.tbl``-style table (name spans a record boundary, so the table is not split cleanly).
* The ``.tbl`` block (5320 bytes) is a u16 array of 2660 entries: 2561 are 0xFFFF (empty), 99 are
  small indices (0x01..0x60). Not yet proven to be the 0x0F token map.

This tool does NOT decide what the 0x0F tokens are. It only extracts the archive and reports
the structure so the next step (tokens -> glyph) can be tested. Writes the decompressed archive
to --out (keep it under local/: it is game data).

Usage:
    python tools/font_probe.py --cpk /path/font.cpk --out local/font_ID00000.bin
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import crilayla  # noqa: E402


def extract_single_itoc(data: bytes) -> tuple[int, int, int]:
    """Return (content_offset, stored_size, extract_size) for a one-entry ITOC CPK."""
    if data[:4] != b"CPK ":
        raise ValueError("not a CPK")
    # Header fields are read by cpk_table; here only the ITOC single-entry path is supported.
    import cpk_table
    t = cpk_table.read_cpk_table(Path(_PATH))  # noqa: F821 (set in main)
    h = t["header"]["fields"]
    if h.get("Files") != 1 or t["entries"][0].get("absolute_offset") is not None:
        raise ValueError("only the one-entry ITOC layout is handled here")
    e = t["entries"][0]
    return h["ContentOffset"], e["file_size"], e["extract_size"]


def main(argv=None) -> int:
    global _PATH
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cpk", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    _PATH = args.cpk
    data = args.cpk.read_bytes()
    content_off, stored, extracted = extract_single_itoc(data)
    raw = data[content_off:content_off + stored]
    if crilayla.is_crilayla(raw):
        out = crilayla.decompress(raw).data
    else:
        out = raw
    print(f"content offset {content_off}, stored {stored}, extracted {len(out)} (expect {extracted})")
    if len(out) != extracted:
        print("SIZE MISMATCH", file=sys.stderr)
        return 1
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(out)
        print("wrote", args.out)
    # header: u32 0x10, u32 count, u32 0x20 (no names here)
    h = struct.unpack_from("<3I", out, 0)
    print("archive header u32:", [hex(x) for x in h])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
