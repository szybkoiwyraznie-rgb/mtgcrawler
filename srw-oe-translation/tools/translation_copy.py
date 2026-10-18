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

``--resync`` is the one exception to "never overwritten": after a tool rewrote the SOURCE rows
(``skill_shrink.py`` shortened the Skill00 fragment pool on 2026-10-15; the 8 DLC copies
``config01-08.EDAT/srwDL_Skill01-08.bin`` kept the old English, 408 rows) the copies are set to the
source's current ``en`` again - still only where the Japanese matches, and every overwritten row is
counted in ``resynced``.  The build writes a copy row's own ``en``, so an out-of-sync copy ships a
different text in chapters 2-8 than in chapter 1 (``translation_check`` reports it as
"copy differs from its source row").

Usage:
    python tools/translation_copy.py --package local/translation            # fill
    python tools/translation_copy.py --package local/translation --check    # report only
    python tools/translation_copy.py --package local/translation --resync   # copies follow edited sources
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


def copy_rows(rows: List[dict], check_only: bool = False, resync: bool = False,
              field: str = "en", token_map=None) -> dict:
    """Copy the selected field through JP-identical chains, independent of file order.

    PL targets are checked against their OWN writer budgets. EN remains the legacy default.
    Cycles, missing sources and stale source text are refused; check-only never mutates rows.
    """
    import translation_check
    # IDs are reused across chapter tables (some copies even point to their own ID).
    # Also several legacy pool rows reuse an ID with DIFFERENT Japanese strings.
    by_id, ids = {}, {r.get("id") for r in rows}
    for r in rows:
        key = (r.get("id"), r.get("jp"))
        if key not in by_id or (by_id[key].get("copy_of") and not r.get("copy_of")):
            by_id[key] = r
    report = {"rows": len(rows), "copies": 0, "filled": 0, "already": 0, "source_empty": 0,
              "missing_source": 0, "text_mismatch": 0, "resynced": 0, "cycles": 0,
              "invalid_target": 0, "problems": []}
    for row in rows:
        if not row.get("copy_of"):
            continue
        report["copies"] += 1
        source, seen, failed = row, set(), False
        while source.get("copy_of"):
            key = id(source)
            if key in seen:
                report["cycles"] += 1
                report["problems"].append(f"{row['id']}: copy_of cycle")
                failed = True
                break
            seen.add(key)
            donor = by_id.get((source["copy_of"], source.get("jp")))
            if donor is None:
                if source["copy_of"] in ids:
                    report["text_mismatch"] += 1
                    report["problems"].append(f"{row['id']}: source text differs from {source['copy_of']}")
                else:
                    report["missing_source"] += 1
                    report["problems"].append(f"{row['id']}: source row {source['copy_of']} is not in the package")
                failed = True
                break
            if donor.get("jp") != source.get("jp"):
                report["text_mismatch"] += 1
                report["problems"].append(f"{row['id']}: source text differs from {source['copy_of']}")
                failed = True
                break
            source = donor
        if failed:
            continue
        old, text = row.get(field) or "", source.get(field) or ""
        if old.strip() and (not resync or not text.strip() or old == text):
            report["already"] += 1
            continue
        if not text.strip():
            report["source_empty"] += 1
            continue
        if field == "pl":
            errors, _ = translation_check.check_row({**row, field: text}, field=field,
                              pct=(token_map or {}).get(row.get("id")))
            if errors:
                report["invalid_target"] += 1
                report["problems"].extend(f"{row['id']}: {e}" for e in errors)
                continue
        if not check_only:
            row[field] = text
        report["resynced" if old.strip() else "filled"] += 1
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
    parser.add_argument("--resync", action="store_true",
                        help="also overwrite filled copies whose English differs from their source "
                             "(after a tool rewrote the source rows)")
    parser.add_argument("--field", choices=("en", "pl"), default="en")
    args = parser.parse_args(argv)

    files, rows_by_file = load_package(args.package)
    files = [path for path in files if not path.name.startswith("06_")]   # the scene index has no text
    all_rows = [row for path in files for row in rows_by_file[path]
                if "id" in row and "jp" in row]
    before = {id(row): (row.get(args.field) or "") for row in all_rows}
    import token_map as TMAP
    sidecar = TMAP.find_sidecar(args.package)
    report = copy_rows(all_rows, check_only=args.check, resync=args.resync, field=args.field,
                       token_map=TMAP.load_map(sidecar) if sidecar else {})
    if not args.check:
        touched = [path for path in files
                   if any((row.get(args.field) or "") != before[id(row)] for row in rows_by_file[path])]
        write_package(files, rows_by_file, touched)
        print("written files:", ", ".join(path.name for path in touched) or "none")
    print(json.dumps({key: value for key, value in report.items() if key != "problems"},
                     ensure_ascii=False, indent=1))
    for problem in report["problems"][:20]:
        print("  !", problem)
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
