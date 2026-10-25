#!/usr/bin/env python3
"""Turn the memory string table into a translation worklist.

`tools/mem_carve.py` writes `strings_objects.tsv` (`address<TAB>length<TAB>text`)
from the running game. This reads one or more of those files and produces:

- a JSONL worklist, one line per string worth translating, with a stable id, the
  category, the Japanese source and its length;
- a summary with counts and character totals per category, which is the number
  the phase-0 feasibility decision hangs on.

Nothing here guesses at meaning: the categories are structural (does it look like
a menu label, a sentence, a name, a technical identifier). Review is manual.

Usage:
    python3 tools/strings_to_worklist.py --strings a.tsv b.tsv \
        --worklist worklist.jsonl --summary summary.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = 1

KANA = re.compile(r"[\u3041-\u30ff]")
HAN = re.compile(r"[\u4e00-\u9fff]")
JP_PUNCT = re.compile(r"[\u3000-\u303f\uff01-\uff60]")
SENTENCE_END = re.compile(r"[。！？!?]$")
QUOTED = re.compile(r"[「『].*[」』]")
FORMAT_TOKEN = re.compile(r"\{[0-9]+\}|\{[^{}]{1,40}\}|<[^<>]{1,40}>|%[sdf]")
ASCII_ONLY = re.compile(r"^[\x20-\x7e]+$")
VERTICAL = re.compile(r"[\u30a0\u30fc]")
TRANSLATABLE = ("fragment", "label_or_name", "sentence", "template")


def is_japanese(text: str) -> bool:
    return bool(KANA.search(text) or HAN.search(text))


MAX_UNIT = 400


def plausible(text: str) -> bool:
    """Reject heap objects that decode but are not language (font tables etc.)."""
    if not 1 <= len(text) <= MAX_UNIT:
        return False
    if ASCII_ONLY.match(text):
        return True                      # identifiers are useful context
    return is_japanese(text)


def classify(text: str) -> str:
    """Structural category. Deliberately simple and explainable."""
    if ASCII_ONLY.match(text):
        return "identifier"
    if not is_japanese(text):
        return "symbols"
    if FORMAT_TOKEN.search(text) and len(text) <= 16:
        return "template"
    if len(text) <= 12 and not SENTENCE_END.search(text) and not QUOTED.search(text):
        return "label_or_name"
    if SENTENCE_END.search(text) or QUOTED.search(text):
        return "sentence"
    return "fragment"


def unit_id(text: str) -> str:
    """Stable id from the source text, so a worklist survives re-scans."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_rows(paths: list[Path]) -> list[tuple[str, int, str]]:
    rows = []
    seen = set()
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t", 2)
            if len(parts) != 3:
                continue
            address, length, text = parts
            if text in seen:
                continue
            seen.add(text)
            rows.append((address, int(length) if length.isdigit() else len(text), text))
    return rows


def build(rows: list[tuple[str, int, str]]) -> tuple[list[dict], dict]:
    units = []
    totals: dict[str, dict] = {}
    for address, length, text in rows:
        if not plausible(text):
            continue
        category = classify(text)
        if category in TRANSLATABLE:
            units.append({"id": unit_id(text), "category": category,
                          "chars": len(text), "address": address, "jp": text})
        bucket = totals.setdefault(category, {"strings": 0, "chars": 0})
        bucket["strings"] += 1
        bucket["chars"] += len(text)
    units.sort(key=lambda item: (item["category"], -item["chars"]))
    summary = {
        "schema": SCHEMA,
        "totals": {
            "rows": len(rows),
            "translatable": sum(bucket["strings"] for name, bucket in totals.items()
                                if name in TRANSLATABLE),
            "translatable_chars": sum(bucket["chars"]
                                      for name, bucket in totals.items()
                                      if name in TRANSLATABLE),
        },
        "per_category": dict(sorted(totals.items(),
                                    key=lambda kv: -kv[1]["chars"])),
    }
    return units, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strings", type=Path, nargs="+", required=True)
    parser.add_argument("--worklist", type=Path, default=Path("worklist.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("summary.json"))
    args = parser.parse_args(argv)

    rows = load_rows(args.strings)
    if not rows:
        print("error: no rows read; is this a strings_objects.tsv?", file=sys.stderr)
        return 2
    units, summary = build(rows)

    args.worklist.parent.mkdir(parents=True, exist_ok=True)
    args.worklist.write_text(
        "".join(json.dumps(unit, ensure_ascii=False) + "\n" for unit in units),
        encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")

    totals = summary["totals"]
    print(f"rows read: {totals['rows']:,}")
    print(f"translatable: {totals['translatable']:,} strings, "
          f"{totals['translatable_chars']:,} characters")
    for name, bucket in summary["per_category"].items():
        print(f"  {name:<14} {bucket['strings']:>7,} strings  "
              f"{bucket['chars']:>9,} chars")
    print(f"worklist: {args.worklist} ({args.worklist.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
