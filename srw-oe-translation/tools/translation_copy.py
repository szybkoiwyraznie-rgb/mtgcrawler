#!/usr/bin/env python3
"""Fill the repeated rows of the package from the row they repeat.

A later DLC pack ships some scenes again (``DL102_50`` -> ``DL102_50B``).  Where the text is
identical, the package marks every row of the re-release with ``copy_of`` = the id of the row that
holds the same Japanese text in the base scene, and the scene itself with ``duplicate_of``.  Where
the re-release was edited, the scene is marked ``variant_of`` and only the rows whose text still
matches get ``copy_of``.

This tool copies ``en`` from the source row, so every text is translated once:

* the target is only filled when its ``en`` is empty (a translation is never overwritten),
* the source text must still equal the target ``jp`` (a moved or edited row is refused, not guessed),
* a file is rewritten only when at least one of its rows was filled.

Usage:
    python tools/translation_copy.py --package local/translation            # fill
    python tools/translation_copy.py --package local/translation --check    # report only
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

import item_skill_write as ISW  # noqa: E402


def load_package(paths) -> Tuple[List[Path], Dict[Path, List[dict]]]:
    """Every package file (a directory means its ``*.jsonl``, sorted) with its rows in file order."""
    files: List[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.jsonl")))
        else:
            files.append(path)
    return files, {path: ISW.read_package(path) for path in files}


def copy_rows(rows: List[dict], check_only: bool = False) -> dict:
    """Fill every row that has ``copy_of`` from its source. Returns the counters and problems."""
    by_id = {row["id"]: row for row in rows if row.get("id")}
    report = {"rows": len(rows), "copies": 0, "filled": 0, "already": 0, "source_empty": 0,
              "missing_source": 0, "text_mismatch": 0, "problems": []}
    for row in rows:
        source_id = row.get("copy_of")
        if not source_id:
            continue
        report["copies"] += 1
        source = by_id.get(source_id)
        if source is None:
            report["missing_source"] += 1
            report["problems"].append(f"{row['id']}: source row {source_id} is not in the package")
            continue
        if source.get("jp") != row.get("jp"):
            report["text_mismatch"] += 1
            report["problems"].append(f"{row['id']}: source text differs from {source_id}")
            continue
        if (row.get("en") or "").strip():
            report["already"] += 1
            continue
        if not (source.get("en") or "").strip():
            report["source_empty"] += 1
            continue
        if not check_only:
            row["en"] = source["en"]
        report["filled"] += 1
    return report


def write_package(files: List[Path], rows_by_file: Dict[Path, List[dict]], touched: List[Path]) -> None:
    """Rewrite the touched files with the rows that were read from them (same order, same dump)."""
    for path in touched:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows_by_file[path]:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, nargs="+", required=True,
                        help="package JSONL files, or a directory holding them")
    parser.add_argument("--check", action="store_true", help="only report what would be filled")
    args = parser.parse_args(argv)

    files, rows_by_file = load_package(args.package)
    files = [path for path in files if not path.name.startswith("06_")]   # the scene index has no text
    all_rows = [row for path in files for row in rows_by_file[path]
                if "id" in row and "en" in row]
    before = {id(row): (row.get("en") or "") for row in all_rows}
    report = copy_rows(all_rows, check_only=args.check)
    if not args.check:
        touched = [path for path in files
                   if any((row.get("en") or "") != before[id(row)] for row in rows_by_file[path])]
        write_package(files, rows_by_file, touched)
        print("written files:", ", ".join(path.name for path in touched) or "none")
    print(json.dumps({key: value for key, value in report.items() if key != "problems"},
                     ensure_ascii=False, indent=1))
    for problem in report["problems"][:20]:
        print("  !", problem)
    return 1 if (report["missing_source"] or report["text_mismatch"]) else 0


if __name__ == "__main__":
    sys.exit(main())
