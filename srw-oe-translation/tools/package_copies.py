#!/usr/bin/env python3
"""Mark repeated strings so the translator writes each text once.

The dictionary-like categories hold the same string many times over: one series name appears once
per mech of that series, one item effect once per item that shares it, one voice actor once per
character they play.  Measured on the current package: 1 581 repeats in ``07``, 2 303 in ``08``,
757 in ``02``, 1 863 in ``03`` -- about 6 500 elements a translator would otherwise type twice (and,
sooner or later, type two different ways).

Every repeat gets ``copy_of`` = the id of the first row carrying the same Japanese text.  The tools
that already understand ``copy_of`` do the rest: the ``*.md`` views show the repeat as a note with
no ``EN:`` line, and ``tools/translation_copy.py`` fills it from the row it repeats (it refuses when
the Japanese no longer matches, so a moved or edited repeat fails loudly instead of guessing).

Not touched: story text ``00`` (a re-released scene inherits from the scene it repeats, which is its
own rule), quotes ``01`` (their rows already share one element per speaker), config text ``04`` and
mission text ``05`` (measured: ``04`` deliberately keeps its 17 duplicate offsets separate, and the
``05`` slots have per-slot byte budgets that a blindly copied text could overflow).

Usage:
    python tools/package_copies.py --package local/translation            # mark
    python tools/package_copies.py --package local/translation --check    # report only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

FILES = ("02_items.jsonl", "03_skills.jsonl", "07_names_characters.jsonl",
         "08_names_units_weapons.jsonl")


def mark(rows: List[dict]) -> Tuple[int, Dict[str, int]]:
    """Set ``copy_of`` on every row repeating an earlier row's (category, part, text).

    Returns (newly marked, counts per part).  A row that already carries ``copy_of`` is left alone,
    and rows without a text are skipped (there is nothing to inherit).
    """
    first: Dict[Tuple[str, str, str], str] = {}
    marked = 0
    per_part: Dict[str, int] = {}
    for row in rows:
        text = row.get("jp")
        if not text:
            continue
        key = (str(row.get("category")), str(row.get("part")), text)
        if key not in first:
            first[key] = str(row.get("id"))
            continue
        if row.get("copy_of"):
            continue
        row["copy_of"] = first[key]
        marked += 1
        per_part[str(row.get("part"))] = per_part.get(str(row.get("part")), 0) + 1
    return marked, per_part


def run(package: Path, files: Sequence[str] = FILES, check: bool = False) -> dict:
    """Mark every package file in ``files``; write a file back only when it changed."""
    report: dict = {"files": {}, "marked": 0, "bytes_written": 0}
    for name in files:
        path = Path(package) / name
        if not path.exists():
            report["files"][name] = {"marked": 0, "note": "brak pliku"}
            continue
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = [json.loads(line) for line in lines]
        marked, per_part = mark(rows)
        report["files"][name] = {"marked": marked, "parts": per_part}
        report["marked"] += marked
        if marked and not check:
            text = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
            path.write_text(text, encoding="utf-8")
            report["bytes_written"] += len(text.encode("utf-8"))
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--files", nargs="*", default=list(FILES))
    parser.add_argument("--check", action="store_true", help="report only, change nothing")
    args = parser.parse_args(argv)
    report = run(args.package, args.files, args.check)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if args.check:
        print("--check: nic nie zapisałem")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
