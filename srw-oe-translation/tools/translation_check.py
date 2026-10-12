#!/usr/bin/env python3
"""Check a filled-in translation package before it goes back into the game files.

The checher is deliberately strict about everything the game cares about and forgiving about style:

* every ``en`` must be CP932-encodable (the font's charset is CP932),
* the ordered list of control tokens must match ``jp`` exactly (``＠0``…``＠9``, ``%s``, ``%%``,
  ``％s``, ``＄n``, ``＃``, ``{XX}`` — the game substitutes them),
* the number of ``\\n`` line breaks must match ``jp`` (the dialogue boxes and list rows are drawn
  around them),
* ``max_bytes`` (a fixed slot) is a hard error, ``suggested_max`` (item/skill UI width) is a warning.

Rows with an empty ``en`` are reported as untranslated, not as errors, so the check can be run while
translating.  ``--require-complete`` turns them into errors for a release check.

Usage::

    python tools/translation_check.py --package local/translation
    python tools/translation_check.py --package local/translation --require-complete --strict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import item_skill_write as ISW  # noqa: E402

TOKEN_RE = re.compile(r"＠[0-9]|%%|%s|％[A-Za-z0-9]+|＄[0-9]*|＃|\{[0-9A-Fa-f]{2}\}")
CATEGORIES = ("dialogue", "quote", "item", "skill", "config", "mission", "name")


def tokens(text: str) -> List[str]:
    """Control tokens of one string, in order."""
    return TOKEN_RE.findall(text)


def encode(text: str) -> Optional[str]:
    """None when the text encodes to CP932, otherwise the failure message."""
    try:
        text.encode("cp932")
    except UnicodeEncodeError as exc:
        return f"not CP932-encodable ({exc.reason} at {exc.start})"
    return None


def check_row(row: dict, require_complete: bool = False) -> Tuple[List[str], List[str]]:
    """(errors, warnings) for one package row."""
    errors: List[str] = []
    warnings: List[str] = []
    text = (row.get("en") or "").strip()
    jp = row.get("jp") or ""
    if not text:
        message = "untranslated (empty en)"
        (errors if require_complete else warnings).append(message)
        return errors, warnings
    problem = encode(text)
    if problem:
        errors.append(problem)
    if tokens(text) != tokens(jp):
        errors.append(f"control tokens changed: {tokens(jp)} -> {tokens(text)}")
    if text.count("\n") != jp.count("\n"):
        errors.append(f"line breaks changed: {jp.count(chr(10))} -> {text.count(chr(10))}")
    size = len(text.encode("cp932")) if not problem else 0
    if row.get("max_bytes") is not None and size > row["max_bytes"]:
        errors.append(f"over budget: {size} > max_bytes {row['max_bytes']}")
    elif row.get("suggested_max") and size > row["suggested_max"]:
        warnings.append(f"wider than the game's field: {size} > suggested_max {row['suggested_max']}")
    return errors, warnings


def check_rows(rows: Iterable[dict], require_complete: bool = False) -> dict:
    """Per-file counters plus the first problems of every kind."""
    report = {"files": {}, "errors": [], "warnings": []}
    for row in rows:
        name = row.get("_file") or row.get("category") or "?"
        bucket = report["files"].setdefault(name, {"rows": 0, "filled": 0, "empty": 0,
                                                   "errors": 0, "warnings": 0})
        bucket["rows"] += 1
        errors, warnings = check_row(row, require_complete)
        if (row.get("en") or "").strip():
            bucket["filled"] += 1
        else:
            bucket["empty"] += 1
        bucket["errors"] += len(errors)
        bucket["warnings"] += len(warnings)
        row_id = row.get("id", "?")
        report["errors"].extend(f"{row_id}: {message}" for message in errors[:3])
        report["warnings"].extend(f"{row_id}: {message}" for message in warnings[:3])
        if len(report["errors"]) > 400 and len(report["warnings"]) > 400:
            break
    report["totals"] = {
        "rows": sum(b["rows"] for b in report["files"].values()),
        "filled": sum(b["filled"] for b in report["files"].values()),
        "empty": sum(b["empty"] for b in report["files"].values()),
        "errors": sum(b["errors"] for b in report["files"].values()),
        "warnings": sum(b["warnings"] for b in report["files"].values()),
    }
    return report


def format_report(report: dict) -> str:
    lines = ["# Raport kontroli pakietu", ""]
    lines.append(f"{'plik':<28}{'wiersze':>8}{'wypełnione':>12}{'puste':>8}{'błędy':>7}{'uwagi':>7}")
    for name in sorted(report["files"]):
        bucket = report["files"][name]
        lines.append(f"{name:<28}{bucket['rows']:>8}{bucket['filled']:>12}{bucket['empty']:>8}"
                     f"{bucket['errors']:>7}{bucket['warnings']:>7}")
    totals = report["totals"]
    lines.append("")
    lines.append(f"RAZEM: {totals['rows']} wierszy, {totals['filled']} wypełnionych, "
                 f"{totals['empty']} pustych, {totals['errors']} błędów, {totals['warnings']} uwag")
    for label, key in (("BŁĘDY", "errors"), ("UWAGI", "warnings")):
        if report[key]:
            lines.append("")
            lines.append(f"## {label} (pierwsze {min(len(report[key]), 200)})")
            lines.extend("  " + line for line in report[key][:200])
    return "\n".join(lines) + "\n"


def collect(paths: Iterable[Path]) -> List[dict]:
    """Package rows of every ``*.jsonl`` given; each row remembers its file name."""
    rows, files = ISW.collect_rows(paths)
    by_name = {}
    for path in files:
        for row in ISW.read_package(path):
            row["_file"] = path.name
            by_name.setdefault(path.name, []).append(row)
    return [row for name in sorted(by_name) for row in by_name[name]]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, nargs="+", required=True,
                        help="package JSONL files, or a directory holding them")
    parser.add_argument("--out", type=Path, default=None, help="where to write the text report")
    parser.add_argument("--require-complete", action="store_true",
                        help="treat an empty en as an error (release check)")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any error")
    args = parser.parse_args(argv)

    rows = collect(args.package)
    report = check_rows(rows, require_complete=args.require_complete)
    text = format_report(report)
    print(text)
    out = args.out or (args.package[0] / "check_report.txt" if args.package[0].is_dir()
                       else Path("local/translation/check_report.txt"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("wrote", out)
    if args.strict and report["totals"]["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
