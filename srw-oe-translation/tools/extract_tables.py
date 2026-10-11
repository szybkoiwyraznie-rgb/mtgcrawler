"""Extract NUL-separated CP932 string tables from CPK containers (read side).

Complements ``export_strings.py`` (EVNT narration). Many UI/name/help containers store their
text as plain NUL-terminated CP932 strings inside ``.bin``/``.pac`` members (e.g. the character
dictionary in imenu00, battle quotes in mesbtl00, map/terrain names in config00). This tool
emits one readable JSON row per such string, keyed by member + byte offset, with an empty
``target`` for the translator.

Usage:
    python tools/extract_tables.py <file.cpk> [...] [--out DIR] [--min-wide N]
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path
from typing import List

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_write
import crilayla


def _wide_count(s: str) -> int:
    return sum(1 for ch in s if unicodedata.east_asian_width(ch) in ("W", "F"))


def iter_strings(blob: bytes, min_wide: int = 2):
    """Yield ``(offset, decoded)`` for every NUL-terminated CP932 string that looks like text."""
    start = 0
    for idx, byte in enumerate(blob):
        if byte != 0:
            continue
        chunk = blob[start:idx]
        start = idx + 1
        if len(chunk) < 4:
            continue
        try:
            s = chunk.decode("cp932")
        except Exception:
            continue
        if _wide_count(s) >= min_wide and not s.isspace():
            yield (idx - len(chunk), s)


def extract_member(member_name: str, blob: bytes, min_wide: int) -> List[dict]:
    return [{
        "member": member_name,
        "offset": off,
        "source": s,
        "source_bytes": len(s.encode("cp932")),
        "target": "",
    } for off, s in iter_strings(blob, min_wide)]


def extract_package(path: Path, min_wide: int) -> List[dict]:
    rows: List[dict] = []
    try:
        cpk = cpk_write.load(path)
        members = []
        for m in cpk.members:
            blob = m.blob
            if crilayla.is_crilayla(blob):
                try:
                    blob = crilayla.decompress(blob).data
                except Exception:
                    continue
            members.append((m.name, blob))
    except Exception:
        members = [(path.name, path.read_bytes())]
    for name, blob in members:
        rows.extend(extract_member(name, blob, min_wide))
    return rows


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    min_wide = 2
    out_dir = Path("local/tables")
    if "--min-wide" in argv:
        i = argv.index("--min-wide"); min_wide = int(argv[i + 1]); del argv[i:i + 2]
    if "--out" in argv:
        i = argv.index("--out"); out_dir = Path(argv[i + 1]); del argv[i:i + 2]
    paths = [Path(a) for a in argv]
    if not paths:
        print("usage: extract_tables.py <file.cpk> [...] [--out DIR] [--min-wide N]")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for path in paths:
        rows = extract_package(path, min_wide)
        dest = out_dir / (path.stem + ".tables.json")
        dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        summary[path.name] = {"strings": len(rows), "file": str(dest)}
        print(f"{path.name}: {len(rows)} strings -> {dest}")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
