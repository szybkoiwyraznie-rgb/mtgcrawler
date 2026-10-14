#!/usr/bin/env python3
"""Fill an empty ``en`` of a name/label row from a row that carries the same text of the same file.

The package contains one game string in as many rows as the game reads it in as many tables: the
name of an item that the shop draws and the name of the same item in the sort list are the same bytes
of ``srwDL_Item00.bin``, and both are exported (``02_items.jsonl`` and ``04_config_text.jsonl``, the
same way for skills, units, weapons and the character tables).  Translating them twice is wasted work
and a real risk of two different English answers for one string in one game.

This tool therefore fills a row that still has an empty ``en`` from a row with the identical ``jp``
that lives in the same member of the same container and is already translated:

* only rows that are **not** dialogue or battle quotes take part at all - a spoken line may
  legitimately read differently in two scenes, so there the translator decides, not the tool,
* the target must be empty (a translation is never overwritten),
* both rows must share ``source.container`` and ``source.member``, i.e. the same bytes of the game,
* a donor text that does not fit the target's ``max_bytes`` is reported, not written,
* two donors with different text are a conflict: nothing is written, the pair is reported.

Usage:
    python tools/translation_mirror.py --package local/translation            # fill
    python tools/translation_mirror.py --package local/translation --check    # report only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import translation_copy as TC  # noqa: E402

SPOKEN = ("dialogue", "battle_quote")   # decided by the translator, never mirrored


def mirror_key(row: dict) -> Tuple[str, object, object]:
    """The identity of the game bytes a row was exported from: its text, container and member."""
    source = row.get("source") or {}
    return (row.get("jp") or "", source.get("container"), source.get("member"))


def mirror_rows(rows: List[dict], check_only: bool = False) -> dict:
    """Fill every empty name/label row that has a translated twin; returns the counters and problems."""
    index: Dict[Tuple[str, object, object], List[dict]] = {}
    for row in rows:
        if "id" in row and "jp" in row and "en" in row and row.get("category") not in SPOKEN:
            index.setdefault(mirror_key(row), []).append(row)
    report = {"rows": len(rows), "with_twin": 0, "filled": 0, "waiting": 0, "conflicts": [],
              "problems": []}
    for row in rows:
        if "id" not in row or "jp" not in row or "en" not in row:
            continue
        if row.get("category") in SPOKEN or (row.get("en") or "").strip():
            continue
        twins = [twin for twin in index.get(mirror_key(row), ()) if twin is not row]
        translated = [twin for twin in twins if (twin.get("en") or "").strip()]
        if not twins:
            continue
        report["with_twin"] += 1
        if not translated:
            report["waiting"] += 1
            continue
        texts = {twin["en"] for twin in translated}
        if len(texts) > 1:
            report["conflicts"].append(
                f"{row['id']}: twins disagree ({', '.join(sorted(t['id'] for t in translated))})")
            continue
        text = texts.pop()
        if row.get("max_bytes") is not None and len(text.encode("cp932")) > row["max_bytes"]:
            report["problems"].append(f"{row['id']}: text of its twin is wider than max_bytes "
                                      f"{row['max_bytes']}")
            continue
        if not check_only:
            row["en"] = text
        report["filled"] += 1
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, nargs="+", required=True,
                        help="package JSONL files, or a directory holding them")
    parser.add_argument("--check", action="store_true", help="only report what would be filled")
    args = parser.parse_args(argv)

    files, rows_by_file = TC.load_package(args.package)
    files = [path for path in files if not path.name.startswith("06_")]   # the scene index has no text
    all_rows = [row for path in files for row in rows_by_file[path]
                if "id" in row and "jp" in row and "en" in row]
    before = {id(row): (row.get("en") or "") for row in all_rows}
    report = mirror_rows(all_rows, check_only=args.check)
    if not args.check:
        touched = [path for path in files
                   if any((row.get("en") or "") != before[id(row)] for row in rows_by_file[path])]
        TC.write_package(files, rows_by_file, touched)
        print("written files:", ", ".join(path.name for path in touched) or "none")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if (report["conflicts"] or report["problems"]) else 0


if __name__ == "__main__":
    sys.exit(main())
