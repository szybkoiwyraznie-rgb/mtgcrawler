#!/usr/bin/env python3
"""Write translated item/skill texts back into a config container (the `apply` path, part 1).

The record layout is the one measured by ``item_skill_records``: twenty u16 parameter words, six
field boundaries at +40, one more parameter word, the five NUL-terminated fields, then the numeric
tail.  Because the boundaries are explicit, growing a field only means rebuilding the record: the
member's record-offset table and its ``tail_offset`` are re-derived, and everything after the record
shifts.  Nothing else in the member points at a text.

Layers, all fail-closed:

1. ``rebuild_member``  - pure bytes-in/bytes-out for one item/skill member.
2. ``plan_edits``      - turns translator rows (the package JSONL) into per-record role edits and
   refuses a row whose ``jp`` no longer matches the file (a stale sheet never clobbers other bytes).
3. ``apply_container`` - rebuilds the inner PAC (``configst_pack``) and the CPK (``cpk_write``) and
   re-reads the result to prove every applied text is really there.

Game text never enters the repository: edited containers go to ``local/`` (gitignored).

Usage::

    python tools/item_skill_write.py --translations local/translation/03_skills.jsonl \\
        --container ../google_drive/config00.cpk --out local/patched/config00.cpk
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack  # noqa: E402
import cpk_write  # noqa: E402
import inline_names as IN  # noqa: E402
import item_skill_records as ISR  # noqa: E402
import speaker_map as SM  # noqa: E402

PARAM_WORDS = 20           # parameter words before the boundary table
BOUNDARY_BYTES = 12        # six u16 field boundaries
PREAMBLE_WORD = 26         # the parameter word sitting between the boundaries and the fields


class WriteError(Exception):
    """The member or the edit list cannot be rebuilt safely."""


def encode(text: str) -> bytes:
    """CP932 bytes of a translation, refused when the font's charset cannot hold it."""
    try:
        return text.encode("cp932")
    except UnicodeEncodeError as exc:
        raise WriteError(f"target is not CP932-encodable: {exc}") from exc


def rebuild_record(row: dict, edits: Dict[str, str]) -> bytes:
    """One record with the five fields replaced by ``edits`` (missing roles keep their text)."""
    header = row.get("header")
    if not header or len(header) <= PREAMBLE_WORD:
        raise WriteError(f"record {row.get('record')}: header too short to rebuild")
    fields = [edits.get(role, row.get(role, "")) for role in ISR.FIELDS]
    raws = [encode(text) + b"\x00" for text in fields]
    tail = b"".join(struct.pack("<H", word) for word in row.get("tail", []))
    # every real record is a multiple of 4 bytes long and the slack always sits in the last field
    fixed = PARAM_WORDS * 2 + BOUNDARY_BYTES + 2 + len(tail)
    slack = (-(fixed + sum(len(raw) for raw in raws))) % 4
    raws[-1] += b"\x00" * slack
    boundaries = [ISR.STRING_BASE]
    blob = b""
    for raw in raws:
        blob += raw
        boundaries.append(boundaries[-1] + len(raw))
    return (struct.pack("<%dH" % PARAM_WORDS, *header[:PARAM_WORDS])
            + struct.pack("<%dH" % ISR.BOUNDARY_COUNT, *boundaries)
            + struct.pack("<H", header[PREAMBLE_WORD])
            + blob + tail)


def rebuild_member(blob: bytes, kind: str, edits: Dict[int, Dict[str, str]],
                   member: str = "") -> Tuple[bytes, dict]:
    """Rebuild one convention-B member with per-record role edits. Returns (bytes, report)."""
    parsed = ISR.parse_member(blob, kind, member)
    if parsed["errors"]:
        raise WriteError(f"{member or kind}: source member does not parse: {parsed['errors'][:3]}")
    rows = parsed["records"]
    unknown = sorted(set(edits) - set(range(len(rows))))
    if unknown:
        raise WriteError(f"{member or kind}: edits reference unknown records {unknown[:5]}")
    records = [rebuild_record(row, edits.get(row["record"], {})) for row in rows]
    count = len(records)
    offsets, position = [], 8 + 4 * count
    for record in records:
        offsets.append(position)
        position += len(record)
    tail_pool = blob[parsed["tail_offset"]:]
    out = (struct.pack("<2I", position, count)
           + b"".join(struct.pack("<I", offset) for offset in offsets)
           + b"".join(records) + tail_pool)
    report = {"member": member, "kind": kind, "records": count,
              "edited_records": len(edits), "edited_roles": sum(len(v) for v in edits.values()),
              "old_size": len(blob), "new_size": len(out)}
    return out, report


def plan_edits(rows: Iterable[dict], member: str, parsed: dict,
               container: str = "") -> Tuple[Dict[int, Dict[str, str]], List[str], dict]:
    """Per-record role edits for one member, plus skipped/match problems.

    A row is applied only when its ``jp`` still equals the text the file holds for that record and
    role - a stale translation sheet must never overwrite a different string.
    """
    edits: Dict[int, Dict[str, str]] = {}
    skipped: List[str] = []
    stats = {"rows": 0, "applied": 0, "empty": 0, "mismatch": 0, "foreign": 0}
    by_record = {row["record"]: row for row in parsed["records"]}
    for row in rows:
        source = row.get("source") or {}
        if (container and source.get("container") not in (None, container)) \
                or source.get("member") != member:
            stats["foreign"] += 1
            continue
        stats["rows"] += 1
        target = (row.get("en") or "").strip()
        if not target:
            stats["empty"] += 1
            continue
        record = row.get("record")
        role = row.get("part")
        if record is None:
            record = _record_from_id(row.get("id"))
        if record is None or role not in ISR.FIELDS or record not in by_record:
            skipped.append(f"{row.get('id')}: not an item/skill field row")
            continue
        current = by_record[record].get(role, "")
        if current != row.get("jp"):
            stats["mismatch"] += 1
            skipped.append(f"{row.get('id')}: source text differs from the file "
                           f"({current!r} != {row.get('jp')!r})")
            continue
        edits.setdefault(record, {})[role] = target
        stats["applied"] += 1
    return edits, skipped, stats


def _record_from_id(row_id: Optional[str]) -> Optional[int]:
    """``skill:config00.cpk/srwDL_Skill00.bin:r12:effect`` -> 12."""
    if not row_id:
        return None
    for chunk in row_id.split(":"):
        if chunk.startswith("r") and chunk[1:].isdigit():
            return int(chunk[1:])
    return None


def read_package(path: Path) -> List[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def apply_container(src: Path, dst: Path, rows: List[dict], dry_run: bool = False) -> dict:
    """Apply the item/skill rows of a package to one config container, then verify by re-reading."""
    cpk = cpk_write.load(src)
    replacement = None
    report = {"container": src.name, "members": [], "skipped": [], "applied_rows": 0,
              "empty_rows": 0, "mismatch_rows": 0}
    for member in cpk.members:
        if not member.name.lower().endswith(".pac"):
            continue
        pac = configst_pack.parse_pac(member.blob)
        changed = False
        for sub in pac["subs"]:
            kind = _kind_of(sub["name"])
            if kind is None:
                continue
            parsed = ISR.parse_member(sub["data"], kind, sub["name"], src.name)
            edits, skipped, stats = plan_edits(rows, sub["name"], parsed, src.name)
            report["skipped"].extend(skipped)
            report["applied_rows"] += stats["applied"]
            report["empty_rows"] += stats["empty"]
            report["mismatch_rows"] += stats["mismatch"]
            if not edits:
                continue
            new_blob, member_report = rebuild_member(sub["data"], kind, edits, sub["name"])
            sub["data"] = new_blob
            changed = True
            report["members"].append(member_report)
        if changed:
            replacement = (member.name, configst_pack.rebuild_pac(pac))
    if replacement is None:
        report["changed"] = False
        return report
    report["changed"] = True
    if dry_run:
        return report
    out = cpk_write.rebuild(cpk, replacement=replacement)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(out)
    report["verification"] = verify_container(dst, rows, src.name)
    return report


def wanted_targets(rows: Iterable[dict], container: Optional[str] = None
                   ) -> Dict[Tuple[str, int, str], str]:
    """{(member, record, role): target} for the filled rows of one container (rows are the package)."""
    want: Dict[Tuple[str, int, str], str] = {}
    for row in rows:
        target = (row.get("en") or "").strip()
        source = row.get("source") or {}
        if not target or source.get("member") is None:
            continue
        if container and source.get("container") not in (None, container):
            continue
        record = row.get("record") if row.get("record") is not None else _record_from_id(row.get("id"))
        if record is None or row.get("part") not in ISR.FIELDS:
            continue
        want[(source["member"], int(record), row["part"])] = target
    return want


def verify_container(path: Path, rows: List[dict], container: Optional[str] = None) -> dict:
    """Re-read a written container and check that every requested target text is in place."""
    want = wanted_targets(rows, container)
    if not want:
        return {"checked": 0, "ok": 0, "failures": []}
    found: Dict[Tuple[str, int, str], str] = {}
    for member_name, blob in SM.read_members(path):
        kind = _kind_of(member_name)
        subs = list(IN.pac_subfiles(blob)) if kind is None and member_name.lower().endswith(".pac") \
            else [(member_name, blob)]
        for sub_name, sub_blob in subs:
            kind = _kind_of(sub_name)
            if kind is None:
                continue
            for row in ISR.parse_member(sub_blob, kind, sub_name, path.name)["records"]:
                for role in ISR.FIELDS:
                    key = (sub_name, row["record"], role)
                    if key in want:
                        found[key] = row[role]
    failures = []
    for (member, record, role), target in want.items():
        got = found.get((member, record, role))
        if got != target:
            failures.append(f"{member}#{record}:{role}: {got!r} != {target!r}")
    return {"checked": len(want), "ok": len(want) - len(failures), "failures": failures[:5]}


def _kind_of(member_name: str) -> Optional[str]:
    if member_name in ISR.EXCLUDED:
        return None
    for kind, prefix in ISR.KIND_PREFIX.items():
        if member_name.startswith(prefix) and not member_name.endswith(
                tuple(f"{i:02d}.bin" for i in range(1, 9))):
            return kind
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    rows = read_package(args.translations)
    dst = args.out or Path("local/patched") / args.container.name
    report = apply_container(args.container, dst, rows, dry_run=args.dry_run)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if not args.dry_run and report.get("changed"):
        print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
