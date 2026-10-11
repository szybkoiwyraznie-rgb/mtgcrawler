#!/usr/bin/env python3
"""Extract CP932 strings from the STRUCTURED SRW OE containers.

``extract_tables.py`` walks NUL-separated string pools. The structured files
(``configst/system/tacsys/tactics/taclevup/navisys/logodata``) instead keep their
text inside fixed-width records, so there are no NUL separators to split on.
This tool byte-scans each (decompressed) member for maximal Shift-JIS double-byte
runs and records each one with its member-relative offset, using the same row
schema as the other extractors so the fill-target/apply shape is shared:

    {member, offset, source, source_bytes, target}

Read-only: nothing is written back into the cpk. (Repacking these fixed-record
tables is a separate, still-open problem -- see docs/EXTRACTION_MAP.md.)
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_write  # noqa: E402
import crilayla  # noqa: E402

LEAD = lambda c: (0x81 <= c <= 0x9F) or (0xE0 <= c <= 0xEF)
TRAIL = lambda c: (0x40 <= c <= 0xFC) and c != 0x7F


def _wide_count(s: str) -> int:
    return sum(1 for ch in s if unicodedata.east_asian_width(ch) in ("W", "F"))


def scan_runs(blob: bytes, min_wide: int = 2, min_bytes: int = 4):
    """Yield (offset, decoded) for maximal CP932 double-byte runs that look like text."""
    i = 0
    n = len(blob)
    while i < n:
        if LEAD(blob[i]):
            j = i
            while j + 1 < n and LEAD(blob[j]) and TRAIL(blob[j + 1]):
                j += 2
            if j > i:
                try:
                    s = blob[i:j].decode("cp932")
                except Exception:
                    s = None
                if s and (j - i) >= min_bytes and _wide_count(s) >= min_wide and not s.isspace():
                    yield i, s
                i = j
                continue
        i += 1


def member_blobs(cpk) -> List[tuple]:
    out = []
    for m in cpk.members:
        blob = m.blob
        if crilayla.is_crilayla(blob):
            try:
                blob = crilayla.decompress(blob).data
            except Exception:
                continue
        out.append((m.name, blob))
    return out


def extract_package(path: Path, min_wide: int) -> List[dict]:
    cpk = cpk_write.load(path)
    rows = []
    for name, blob in member_blobs(cpk):
        for off, s in scan_runs(blob, min_wide):
            rows.append({"member": name, "offset": off, "source": s,
                         "source_bytes": len(s.encode("cp932")), "target": ""})
    return rows


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    min_wide = 2
    outdir = Path("local/tables")
    if "--min-wide" in args:
        k = args.index("--min-wide"); min_wide = int(args[k + 1]); del args[k:k + 2]
    if "--out" in args:
        k = args.index("--out"); outdir = Path(args[k + 1]); del args[k:k + 2]
    if not args:
        print(__doc__); return 2
    outdir.mkdir(parents=True, exist_ok=True)
    for a in args:
        p = Path(a)
        rows = extract_package(p, min_wide)
        out = outdir / f"{p.stem}.strings.json"
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{p.name}: {len(rows)} strings -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
