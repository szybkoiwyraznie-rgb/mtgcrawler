#!/usr/bin/env python3
"""Fit the short system labels (``sysmes.bin``) into the width the Japanese layout gives them.

In-game observation (build 12, 2026-10-15, two screenshots): the button bar draws its labels at
positions sized by the JAPANESE label - ``精神コマンド`` (12 half-width cells) was replaced by
``Spirit Commands`` (15 cells) and the next button's icon landed on top of ``ds``; ``表情変更``
(8) by ``Change Expression`` (17) ran across two slots.  The slot positions do not follow the
current string (an English label measured at runtime would not overlap), so they are constants
of the Japanese layout and the rule for such labels is:

    cells(English) <= cells(Japanese),  cells = CP932 bytes with the control tokens removed
    (``＠4``/``＠6`` colour, ``%s`` placeholders; ASCII and half-width kana are one cell,
    full-width characters two).

The rule applies to every one-line ``sysmes.bin`` label of at most ``MAX_JP_BYTES`` (16) bytes:
the button-bar labels cannot be told apart from menu labels by content, the same strings serve
both (``精神コマンド`` is a bar label on one screen and a list entry on another), and a menu label
that is no wider than the Japanese fits wherever the Japanese did.  Longer strings (dialog
sentences, help lines) wrap in boxes and keep their own rules.

``config/label_fit_rules.tsv`` holds the English for every label that broke the rule in the
2026-10-15 package (187 distinct pairs, 280 rows); this tool applies the rules to all package rows
of the member with that exact Japanese (so a label reads the same on every screen), refuses a
rule that is still too wide or changes the token sequence, and reports what is left over -
labels with ``0x0F`` kana tokens are reported, not touched (their cell width is not measured).

Usage::

    python tools/label_fit.py --package local/pakiet --check
    python tools/label_fit.py --package local/pakiet --out local/pakiet_fit --report local/shrink/label_fit.json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import translation_check as TC   # noqa: E402

MEMBER = "sysmes.bin"
CONFIG_FILE = "04_config_text.jsonl"
MAX_JP_BYTES = 16
RULES_FILE = HERE.parent / "config" / "label_fit_rules.tsv"


class LabelFitError(ValueError):
    """A rule breaks the width or token rule; nothing is written."""


PRINTF_RE = re.compile(r"%[-+ #0-9]*[a-zA-Z%]")   # %s %d %+3d %-16d %% - same value on both sides


def cells(text: str) -> int:
    """Display cells of a label: CP932 bytes without the control tokens and printf fields."""
    bare = PRINTF_RE.sub("", TC.TOKEN_RE.sub("", text))
    return len(bare.encode("cp932", errors="replace"))


def pool_start_rows(rows: Iterable[dict]) -> List[dict]:
    """The sysmes rows that are pool entries of their own.

    The export also lists every suffix of a longer string that starts after a line break or
    colour token as a row of its own (1 095 of 2 196 rows); the sysmes writer skips those
    (``sysmes_text``: "tails of longer strings, not pool entries") and so does this rule.
    """
    member_rows = sorted((row for row in rows if (row.get("source") or {}).get("member") == MEMBER),
                         key=lambda row: row["source"]["offset"])
    out, reach = [], -1
    for row in member_rows:
        offset = row["source"]["offset"]
        if offset >= reach:
            out.append(row)
            reach = offset + len((row.get("jp") or "").encode("cp932", "replace")) + 1
    return out


def is_short_label(jp: str) -> bool:
    return "\n" not in jp and "\x0f" not in jp and 0 < len(jp.encode("cp932", "replace")) <= MAX_JP_BYTES


def load_rules(path: Path = RULES_FILE) -> Dict[str, str]:
    rules: Dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2 or not parts[0]:
            raise LabelFitError(f"{path.name}:{number}: expected jp<TAB>en, got {line!r}")
        jp, en = parts
        if jp in rules and rules[jp] != en:
            raise LabelFitError(f"{path.name}:{number}: {jp!r} has two different rules")
        rules[jp] = en
    return rules


def check_rule(jp: str, en: str) -> Optional[str]:
    """Why a rule is unacceptable, or None."""
    if not is_short_label(jp):
        return "jp is not a short one-line label"
    if cells(en) > cells(jp):
        return f"still too wide: {cells(en)} > {cells(jp)} cells"
    if TC.tokens(en) != TC.tokens(jp):
        return f"token sequence differs: {TC.tokens(jp)} -> {TC.tokens(en)}"
    if "\x0f" in en or "\n" in en:
        return "control byte in the English"
    return None


def read_jsonl(path: Path) -> List[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def violations(rows: Iterable[dict]) -> List[dict]:
    """Short sysmes labels whose English is wider than the Japanese (translated rows only)."""
    out = []
    for row in pool_start_rows(rows):
        jp, en = row.get("jp") or "", row.get("en") or ""
        if not en.strip() or en.strip() == jp.strip():
            continue
        if "\n" in jp or len(jp.encode("cp932", "replace")) > MAX_JP_BYTES:
            continue
        if "\x0f" in jp:
            out.append({"id": row["id"], "jp": jp, "en": en, "reason": "kana token (0x0F): width not measured, left to the translator"})
            continue
        if cells(en) > cells(jp):
            out.append({"id": row["id"], "jp": jp, "en": en, "cells_jp": cells(jp), "cells_en": cells(en),
                        "reason": "no rule"})
    return out


def apply(package: Path, out: Optional[Path], rules: Dict[str, str], check: bool = False) -> dict:
    bad = {jp: check_rule(jp, en) for jp, en in rules.items()}
    bad = {jp: why for jp, why in bad.items() if why}
    if bad:
        raise LabelFitError("refused rules: " + "; ".join(f"{jp!r} -> {rules[jp]!r}: {why}" for jp, why in bad.items()))
    rows = read_jsonl(package / CONFIG_FILE)
    before = violations(rows)
    changed: List[Tuple[str, str, str, str]] = []
    unused = set(rules)
    for row in rows:
        source = row.get("source") or {}
        if source.get("member") != MEMBER:
            continue
        jp = row.get("jp") or ""
        if jp not in rules:
            continue
        unused.discard(jp)
        if (row.get("en") or "") != rules[jp]:
            changed.append((row["id"], jp, row.get("en") or "", rules[jp]))
            row["en"] = rules[jp]
    after = violations(rows)
    report = {"package": str(package), "rules": len(rules), "rules_unused": sorted(unused),
              "violations_before": len(before), "violations_after": len(after),
              "rows_changed": len(changed), "changed": [{"id": i, "jp": j, "from": f, "to": t} for i, j, f, t in changed],
              "left": after, "written": None}
    if check or out is None:
        return report
    if out.resolve() != package.resolve():
        if out.exists():
            shutil.rmtree(out)
        shutil.copytree(package, out)
    write_jsonl(out / CONFIG_FILE, rows)
    report["written"] = str(out)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="output package (copy of --package with the labels fitted)")
    parser.add_argument("--rules", type=Path, default=RULES_FILE)
    parser.add_argument("--check", action="store_true", help="report only")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = apply(args.package, args.out, load_rules(args.rules), check=args.check)
    except LabelFitError as error:
        print(f"label_fit: {error}", file=sys.stderr)
        return 2
    print(f"{args.package}: short sysmes labels wider than the Japanese: {report['violations_before']}"
          f" -> {report['violations_after']} after {report['rules']} rules; rows changed {report['rows_changed']};"
          f" written: {report['written']}")
    for item in report["left"][:40]:
        print(f"  left: {item['id']} {item['jp']!r} -> {item['en']!r} ({item['reason']})")
    if report["rules_unused"]:
        print(f"  unused rules: {report['rules_unused']}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
