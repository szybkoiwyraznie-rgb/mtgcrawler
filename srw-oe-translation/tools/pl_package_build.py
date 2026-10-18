#!/usr/bin/env python3
"""Build the Polish translator package (``pakiet_PL``) from the committed ``pakiet_EN``.

The English package is the complete, current text of the game (109 144 rows, patch v17).
The Polish package is the same rows with one new field - ``"pl": ""`` - so the external
translator model fills exactly what the PL patch will later read, and nothing else:

* every row that carries a ``jp`` gets ``"pl": ""`` inserted right after its ``en``/``en_full``
  group (key order is kept stable so a filled package diffs cleanly against this one);
* structural rows (``06_scenes`` - no ``jp``) pass through untouched;
* ``tokeny.tsv`` and ``name_map.tsv`` are copied byte for byte;
* the translator's reference material lands in ``dokumenty/`` (glossary, voice cards, style
  guide, briefs, bible - the English canon, see ``docs/translator_pl/INSTRUKCJA_PL.md`` §6);
* ``index.json`` records the per-part row counts, the ``pl`` coverage (0 now) and where the
  package came from;
* ``--zip`` writes the handoff archive (contents at the zip root, the instruction first).

The output goes to an ignored folder (default ``local/pakiet_PL``): the empty package is a
handoff artifact, not repo content - the FILLED package is what gets committed later, the
same way ``pakiet_EN`` is the committed filled state of the English handoff.

Usage:
    python tools/pl_package_build.py --package pakiet_EN --out local/pakiet_PL --zip local/pakiet_PL.zip
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
ROOT = HERE.parent

#: where the translator reference material lives in the repo
DOC_SOURCES = ("STYLE.md", "glossary.json", "glossary_extra.tsv", "voice_cards.md")
DOC_DIRS = ("briefy", "bible")
INSTRUCTION = ROOT / "docs" / "translator_pl" / "INSTRUKCJA_PL.md"

GLOSSARY_PL_HEADER = (
    "# glossary_pl.tsv - polskie postaci nazw własnych (dopisuj na końcu)\n"
    "# format: EN<TAB>PL<TAB>uwaga\n"
    "# EN = forma kanoniczna z glossary.json; PL = przyjęta forma polska\n"
)


def insert_pl(row: dict) -> dict:
    """Return the row with ``"pl": ""`` after its jp/en field group (stable key order)."""
    if "pl" in row:
        return row
    keys = list(row)
    anchor = None
    for candidate in ("en_full", "en", "jp"):
        if candidate in keys:
            anchor = keys.index(candidate)
            break
    if anchor is None:
        return row                      # structural row (no jp): nothing to translate
    out = {}
    for key in keys:
        out[key] = row[key]
        if keys.index(key) == anchor:
            out["pl"] = ""
    return out


def build_package(package: Path, out: Path) -> Dict[str, dict]:
    """Write the PL package; returns the per-part stats for ``index.json``."""
    if not package.is_dir():
        raise SystemExit(f"package {package} is not a directory")
    out.mkdir(parents=True, exist_ok=True)
    stats: Dict[str, dict] = {}
    for path in sorted(package.glob("*.jsonl")):
        rows: List[dict] = []
        translated = structural = 0
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if "jp" in row:
                    row = insert_pl(row)
                    translated += 1
                else:
                    structural += 1
                rows.append(row)
        with (out / path.name).open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        stats[path.name] = {"rows": translated, "structural": structural,
                            "pl_filled": sum(1 for r in rows if (r.get("pl") or "").strip())}
    for name in ("tokeny.tsv", "name_map.tsv"):
        source = package / name
        if source.exists():
            shutil.copyfile(source, out / name)
    return stats


def copy_documents(out: Path) -> int:
    """docs/translator + the PL instruction -> ``out/dokumenty`` (+ instruction at root)."""
    docs = ROOT / "docs" / "translator"
    if not INSTRUCTION.exists():
        raise SystemExit(f"missing {INSTRUCTION}")
    shutil.copyfile(INSTRUCTION, out / INSTRUCTION.name)
    target = out / "dokumenty"
    target.mkdir(parents=True, exist_ok=True)
    copied = 1
    for name in DOC_SOURCES:
        if (docs / name).exists():
            shutil.copyfile(docs / name, target / name)
            copied += 1
    for folder in DOC_DIRS:
        source = docs / folder
        if source.is_dir():
            (target / folder).mkdir(parents=True, exist_ok=True)
            for path in sorted(source.iterdir()):
                if path.is_file():
                    shutil.copyfile(path, target / folder / path.name)
                    copied += 1
    glossary_pl = out / "dokumenty" / "glossary_pl.tsv"
    if not glossary_pl.exists():
        glossary_pl.write_text(GLOSSARY_PL_HEADER, encoding="utf-8")
    return copied


def write_index(out: Path, package: Path, stats: Dict[str, dict]) -> Path:
    try:
        import subprocess
        describe = subprocess.run(["git", "describe", "--always", "--dirty"],
                                  cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:
        describe = "?"
    index = {
        "field": "pl",
        "generated_from": {"package": package.name, "repo": describe},
        "parts": stats,
        "totals": {
            "rows": sum(p["rows"] for p in stats.values()),
            "pl_filled": sum(p["pl_filled"] for p in stats.values()),
        },
    }
    path = out / "index.json"
    path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def make_zip(out: Path, zip_path: Path) -> int:
    """Zip the package contents (instruction first) for the Drive handoff."""
    files = sorted(p for p in out.rglob("*") if p.is_file())
    files.sort(key=lambda p: (p.name != INSTRUCTION.name, str(p.relative_to(out))))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            zf.write(path, path.relative_to(out))
    return len(files)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build pakiet_PL from pakiet_EN.")
    parser.add_argument("--package", type=Path, default=ROOT / "pakiet_EN")
    parser.add_argument("--out", type=Path, default=ROOT / "local" / "pakiet_PL")
    parser.add_argument("--zip", type=Path, default=None)
    args = parser.parse_args(argv)

    stats = build_package(args.package, args.out)
    docs = copy_documents(args.out)
    index = write_index(args.out, args.package, stats)
    print(json.dumps(stats, indent=1))
    print(f"documents copied: {docs}; index: {index.name}")
    if args.zip:
        count = make_zip(args.out, args.zip)
        print(f"zip: {args.zip} ({count} files, {args.zip.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
