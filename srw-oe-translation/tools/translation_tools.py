"""Translation workspace: a CSV template from the text exports, and a checker for filled-in translations.

    python tools/translation_tools.py template "<run folder>" "<translation folder>"
    python tools/translation_tools.py check "<translation folder>"

`template` reads every text/<package>/units.jsonl of a run (including the hidden colliding-name
exports) and writes units.csv: one row per text unit, the source in the lossless view, an empty
`target_text` column, and `budget_bytes` (the original byte length of the text, which a translation
must fit into until the engine's limits are known).

`check` reads units.csv and reports, per filled row: control tokens that differ from the source,
line breaks that differ, text that cannot be encoded to CP932 byte-exactly, and translations over
their byte budget. It writes check_report.txt. Nothing is written back to the game files.

Text is written in the same view as the source: characters stay as typed, and control bytes use
{XX} tokens. The checker uses the same codec as the exporter, so a row that passes can be turned
back into bytes exactly.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_event_text  # noqa: E402

COLUMNS = ("unit_id", "package_id", "file", "source_text", "target_text", "budget_bytes", "status", "note")
CSV_NAME = "units.csv"
REPORT_NAME = "check_report.txt"
TEMPLATE_REPORT_NAME = "template_report.txt"


def _package_units(run_dir: Path) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for units_path in sorted((run_dir / "text").glob("*/units.jsonl")):
        package_id = units_path.parent.name
        for line in units_path.read_text(encoding="utf-8").splitlines():
            if line:
                rows.append((package_id, json.loads(line)))
    return rows


def _source_round_trips(unit: dict[str, Any]) -> bool:
    """The source view must turn back into the exact original bytes."""
    try:
        return extract_event_text.from_view(unit["source_text"]) == bytes.fromhex(unit["prefix_raw_hex"])
    except ValueError:
        return False


def write_template(run_dir: Path, out_dir: Path) -> dict[str, Any]:
    rows = _package_units(run_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / CSV_NAME
    per_package: Counter = Counter()
    per_file: Counter = Counter()
    with_tokens = 0
    zero_budget = 0
    broken: list[str] = []
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for package_id, unit in rows:
            budget = len(bytes.fromhex(unit["prefix_raw_hex"]))
            per_package[package_id] += 1
            per_file[unit["file"]] += 1
            with_tokens += bool(unit.get("tokens"))
            zero_budget += budget == 0
            if not _source_round_trips(unit):
                broken.append(unit["unit_id"])
            writer.writerow(
                {
                    "unit_id": unit["unit_id"],
                    "package_id": package_id,
                    "file": unit["file"],
                    "source_text": unit["source_text"],
                    "target_text": "",
                    "budget_bytes": budget,
                    "status": "todo",
                    "note": "",
                }
            )
    lines = [
        "Translation template check (source views only; no game file is written)",
        f"  units: {len(rows)} in {len(per_package)} packages, {len(per_file)} files",
        f"  units with control tokens: {with_tokens}",
        f"  units with zero byte budget: {zero_budget}",
        f"  units whose source view does not round-trip to the original bytes: {len(broken)}",
    ]
    if broken:
        lines += ["  first failing unit ids:"] + [f"    {unit_id}" for unit_id in broken[:50]]
    lines += ["", "Units per package (top 20):"] + [f"  {count:6d}  {name}" for name, count in per_package.most_common(20)]
    (out_dir / TEMPLATE_REPORT_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "units": len(rows),
        "csv": str(path),
        "round_trip_failures": len(broken),
        "report": str(out_dir / TEMPLATE_REPORT_NAME),
    }


def _tokens(text: str) -> Counter:
    return Counter(match.group(0) for match in extract_event_text.TOKEN_RE.finditer(text))


def check_row(source: str, target: str, budget: int) -> list[str]:
    """Problems for one filled-in translation; an empty list means it is usable."""
    problems: list[str] = []
    if _tokens(source) != _tokens(target):
        problems.append("control tokens differ from the source (copy every {XX} token unchanged)")
    if source.count("\n") != target.count("\n") or source.count("\r") != target.count("\r"):
        problems.append("line breaks differ from the source")
    try:
        encoded = extract_event_text.from_view(target)
    except ValueError as error:
        problems.append(f"not encodable: {error}")
        return problems
    if extract_event_text.to_view(encoded) != target:
        problems.append("does not round-trip through the byte view")
    if len(encoded) > budget:
        problems.append(f"over the byte budget: {len(encoded)} bytes, budget {budget}")
    return problems


def check(out_dir: Path) -> dict[str, Any]:
    path = out_dir / CSV_NAME
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    filled = [row for row in rows if (row.get("target_text") or "").strip()]
    failures: list[tuple[str, list[str]]] = []
    for row in filled:
        problems = check_row(row["source_text"], row["target_text"], int(row["budget_bytes"]))
        if problems:
            failures.append((row["unit_id"], problems))
    lines = [
        "Translation check (no game file is written)",
        f"  units: {len(rows)}, filled: {len(filled)}, passing: {len(filled) - len(failures)}, failing: {len(failures)}",
        "",
    ]
    if failures:
        kinds = Counter(problem.split(":")[0].split(" (")[0] for _unit, problems in failures for problem in problems)
        lines.append("Problem kinds:")
        lines += [f"  {count} x {kind}" for kind, count in kinds.most_common()]
        lines += ["", "First failing rows (ids only):"]
        lines += [f"  {unit_id}: {'; '.join(problems)}" for unit_id, problems in failures[:50]]
    (out_dir / REPORT_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"units": len(rows), "filled": len(filled), "failing": len(failures), "report": str(out_dir / REPORT_NAME)}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    template_parser = sub.add_parser("template")
    template_parser.add_argument("run_dir", type=Path)
    template_parser.add_argument("out_dir", type=Path)
    check_parser = sub.add_parser("check")
    check_parser.add_argument("out_dir", type=Path)
    args = parser.parse_args(argv)
    if args.command == "template":
        print(json.dumps(write_template(args.run_dir.resolve(), args.out_dir.resolve()), ensure_ascii=False))
    else:
        print(json.dumps(check(args.out_dir.resolve()), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
