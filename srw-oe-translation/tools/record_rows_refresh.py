#!/usr/bin/env python3
"""Add the convention-B record fields an older package never saw to ``04_config_text.jsonl``.

The spirit-command and status-change tables (``srwDL_Spirit.bin``, ``srwDL_StatusChange.bin``)
reached the translator only through the NUL-run scan of ``config_text_tables`` (no record rows
like items and skills have).  A run starts at the first non-NUL byte, so wherever the binary
word in front of a record's first field has two non-zero bytes (``04 01`` before ``集中``),
the scan glued the word to the name, rejected the run for its control bytes and the field got
no row at all: 12 spirit names (``集中``, ``鉄壁``, ``感応``, ``信頼`` x3 levels) stayed Japanese
in build #11 while their siblings were English [ZWERYFIKOWANE w grze, 2026-10-15].

This tool walks the records the way the writer does (``item_skill_records.parse_member`` for
every member ``item_skill_write._kind_of`` knows) and appends, for every field with text that no
package row addresses - neither a record row (``record`` + ``part``) nor an offset row at the
field's exact offset - a normal ``grow`` offset row of ``04_config_text.jsonl``.  When another
field of the same record carries the identical Japanese and is already translated (the spirit's
``name_level`` and ``effect_brief`` repeat its ``name``), the new row takes that English, so the
game shows one name everywhere; otherwise ``en`` stays empty for the translator.  Fields holding
control bytes (the ``0x0F xx`` kana tokens) are reported, not added: their rows need the token
map of ``tools/pool_rows_refresh.py`` and stay with the translator package tooling.

Nothing is removed and no existing English is changed.

Usage:
    python tools/record_rows_refresh.py --package local/pakiet --dlc local/usrdir [--check]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import container_mix as CM          # noqa: E402
import item_skill_records as ISR    # noqa: E402
import item_skill_write as ISW      # noqa: E402

CONFIG_FILE = "04_config_text.jsonl"
PACKAGE_FILES = ("02_items.jsonl", "03_skills.jsonl", "04_config_text.jsonl")


def read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def covered_targets(rows: Iterable[dict]) -> Tuple[set, set]:
    """(set of (member, offset), set of (member, record, part)) the package already addresses."""
    offsets, fields = set(), set()
    for row in rows:
        source = row.get("source") or {}
        member = source.get("member")
        if not member:
            continue
        if isinstance(source.get("offset"), int) and row.get("part") == "text":
            offsets.add((member, source["offset"]))
        if row.get("record") is not None and row.get("part") in ISR.FIELDS:
            fields.add((member, row["record"], row["part"]))
    return offsets, fields


def sibling_english(rows: Iterable[dict], member: str, record: dict, jp: str) -> Optional[str]:
    """The English of another field of the same record with the identical Japanese, if any."""
    span = range(record["offset"], record["offset"] + record["length"])
    for row in rows:
        source = row.get("source") or {}
        if source.get("member") != member or row.get("jp") != jp:
            continue
        en = (row.get("en") or "")
        if not en.strip() or en.strip() == jp:
            continue
        if source.get("offset") in span or row.get("record") == record["record"]:
            return en
    return None


def missing_fields(blob: bytes, member: str, container: str, kind: str, covered_offsets: set,
                   covered_fields: set) -> Tuple[List[dict], List[str]]:
    """(record fields without any row, control-byte fields skipped) of one member."""
    parsed = ISR.parse_member(blob, kind, member, container)
    if parsed["errors"]:
        return [], [f"{member}: does not parse ({parsed['errors'][:2]}); skipped"]
    out, skipped = [], []
    for record in parsed["records"]:
        for role in ISR.FIELDS:
            text = record[role]
            if not text:
                continue
            offset = record["offset"] + record[f"{role}_offset"]
            if (member, offset) in covered_offsets or (member, record["record"], role) in covered_fields:
                continue
            if any(ord(ch) < 0x20 and ch != "\n" for ch in text):
                skipped.append(f"{member}: record {record['record']} {role} holds control bytes "
                               f"(kana tokens) - needs the token map, not added: {text[:30]!r}")
                continue
            out.append({"record": record, "role": role, "offset": offset, "text": text})
    return out, skipped


def refresh(package: Path, containers: Dict[str, Path], check: bool = False) -> dict:
    """``containers``: {container name: path of the ORIGINAL container}."""
    rows_by_file = {name: read_jsonl(package / name) for name in PACKAGE_FILES}
    all_rows = [row for rows in rows_by_file.values() for row in rows]
    covered_offsets, covered_fields = covered_targets(all_rows)
    added: List[dict] = []
    skipped: List[str] = []
    prefilled = 0
    for container in sorted(containers):
        _, subs, _ = CM.members_of(containers[container])
        for member in sorted(subs):
            kind = ISW._kind_of(member)
            if kind is None:
                continue
            fields, member_skipped = missing_fields(subs[member], member, container, kind,
                                                    covered_offsets, covered_fields)
            skipped.extend(member_skipped)
            for field in fields:
                en = sibling_english(all_rows, member, field["record"], field["text"])
                if en is not None:
                    prefilled += 1
                row = {"id": f"{kind}:{container}/{member}:{field['offset']}",
                       "category": f"config_{kind}", "part": "text", "jp": field["text"],
                       "en": en or "", "bytes": len(field["text"].encode("cp932")),
                       "mode": "grow", "max_bytes": None,
                       "source": {"container": container, "member": member,
                                  "offset": field["offset"]},
                       "note": f"record {field['record']['record']} {field['role']} "
                               f"(record_rows_refresh 2026-10-15)"}
                added.append(row)
    report = {"package": str(package), "added": len(added), "prefilled": prefilled,
              "skipped": skipped, "rows": [{"id": r["id"], "jp": r["jp"], "en": r["en"]}
                                           for r in added], "written": False}
    if added and not check:
        path = package / CONFIG_FILE
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            for row in added:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        report["written"] = True
    return report


def load_containers(folder: Path, names: Iterable[str]) -> Dict[str, Path]:
    out = {}
    for name in names:
        hits = sorted(folder.rglob(name))
        if hits:
            out[name] = hits[0]
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--dlc", type=Path, required=True,
                        help="folder holding config00.cpk / configst.cpk (searched recursively)")
    parser.add_argument("--containers", nargs="*", default=["config00.cpk", "configst.cpk"])
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    containers = load_containers(args.dlc, args.containers)
    if not containers:
        print(f"no {args.containers} under {args.dlc}", file=sys.stderr)
        return 2
    report = refresh(args.package, containers, check=args.check)
    print(f"{args.package}: {report['added']} field(s) without a row"
          f" ({report['prefilled']} English prefilled from the same record);"
          f" {len(report['skipped'])} skipped; written: {report['written']}")
    for row in report["rows"]:
        print(f"  + {row['id']}  {row['jp']!r} -> {row['en']!r}")
    for line in report["skipped"]:
        print(f"  ! {line}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
