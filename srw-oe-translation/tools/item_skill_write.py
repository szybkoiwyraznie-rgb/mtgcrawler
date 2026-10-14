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

    python tools/item_skill_write.py --translations local/translation \\
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
import table_write as TW  # noqa: E402

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


def rebuild_record(row: dict, edits: Dict[str, object]) -> bytes:
    """One record with the five fields replaced by ``edits`` (missing roles keep their text).

    An edit value is either text (encoded CP932 here) or the ready bytes a planner produced with
    :func:`table_write.encode_target`, which restores the control tokens a ``%s`` stands for.
    """
    header = row.get("header")
    if not header or len(header) <= PREAMBLE_WORD:
        raise WriteError(f"record {row.get('record')}: header too short to rebuild")
    raws = []
    for role in ISR.FIELDS:
        value = edits.get(role, row.get(role, ""))
        raws.append((value if isinstance(value, bytes) else encode(value)) + b"\x00")
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
    # every record word at +36 that holds the offset of another record is a mutual cross
    # reference (measured 62/62 on Spirit, StatusChange, Item00 and Skill00): after a rebuild
    # the offsets move, so the word has to point at the record's new home
    old_to_new = {row["offset"]: new for row, new in zip(rows, offsets)}
    remapped = 0
    patched = []
    for record in records:
        rec = bytearray(record)
        if len(rec) >= 40:
            word = struct.unpack_from("<I", rec, 36)[0]
            if word in old_to_new and old_to_new[word] != word:
                struct.pack_into("<I", rec, 36, old_to_new[word])
                remapped += 1
        patched.append(bytes(rec))
    tail_pool = blob[parsed["tail_offset"]:]
    out = (struct.pack("<2I", position, count)
           + b"".join(struct.pack("<I", offset) for offset in offsets)
           + b"".join(patched) + tail_pool)
    report = {"member": member, "kind": kind, "records": count,
              "edited_records": len(edits), "edited_roles": sum(len(v) for v in edits.values()),
              "cross_refs_remapped": remapped,
              "old_size": len(blob), "new_size": len(out)}
    return out, report


def field_raw(blob: bytes, rec_row: dict, role: str) -> bytes:
    """The raw bytes of one field: from its boundary start to its NUL."""
    start = rec_row["offset"] + rec_row[f"{role}_offset"]
    return blob[start:start + rec_row[f"{role}_slot"]].split(b"\x00", 1)[0]


def plan_edits(rows: Iterable[dict], member: str, parsed: dict,
               container: str = "", blob: Optional[bytes] = None
               ) -> Tuple[Dict[int, Dict[str, object]], List[str], dict]:
    """Per-record role edits for one member, plus skipped/match problems.

    A row is applied only when its ``jp`` still equals the text the file holds for that record and
    role - a stale translation sheet must never overwrite a different string.  These structured
    rows (``02``/``03`` and the structured rows of ``04``) carry their ``jp`` in the file's own
    form: control bytes as the characters themselves and the game formatter's placeholders as the
    literal ASCII ``%s`` - so the comparison and the CP932 encoding need no token mapping.

    Rows of ``part='text'`` and no record index are the offset rows of ``04`` - this planner
    leaves them to :func:`plan_offset_edits`.
    """
    edits: Dict[int, Dict[str, object]] = {}
    skipped: List[str] = []
    stats = {"rows": 0, "applied": 0, "empty": 0, "mismatch": 0, "foreign": 0, "deferred": 0}
    by_record = {row["record"]: row for row in parsed["records"]}
    for row in rows:
        source = row.get("source") or {}
        if (container and source.get("container") not in (None, container)) \
                or source.get("member") != member:
            stats["foreign"] += 1
            continue
        stats["rows"] += 1
        target = TW.english(row)
        if not target:
            stats["empty"] += 1
            continue
        record = row.get("record")
        role = row.get("part")
        if record is None:
            record = _record_from_id(row.get("id"))
        if record is None:
            if role == "text" and isinstance(source.get("offset"), int):
                stats["deferred"] += 1     # an offset row: plan_offset_edits owns it
            else:
                skipped.append(f"{row.get('id')}: not an item/skill field row")
            continue
        if role not in ISR.FIELDS or record not in by_record:
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


def plan_offset_edits(rows: Iterable[dict], member: str, parsed: dict, blob: bytes,
                      container: str = "") -> Tuple[Dict[int, Dict[str, bytes]], List[str], dict]:
    """Per-record role edits from the offset rows of ``04`` (part='text', no record index).

    The offset lands inside one record; the row applies when the field's bytes read back as the
    row's ``jp``.  Two jp forms exist in ``04`` and the category tells them apart: the structured
    exports keep the file's own form (control bytes as characters, literal ``%s`` placeholders),
    while the ``config_leftover`` scan displays every control byte as ``%s`` -
    :func:`table_write.match_form` recognises which form a row carries and
    :func:`table_write.encode_en` puts the right bytes back.  Rows whose offset
    sits in the tail pool are refused here - the tail is a mixed binary/text region this writer
    rebuilds verbatim, and those rows go through the slot writer, which never changes a member's
    size.
    """
    edits: Dict[int, Dict[str, bytes]] = {}
    skipped: List[str] = []
    stats = {"rows": 0, "applied": 0, "empty": 0, "mismatch": 0, "foreign": 0, "tail": 0}
    tail_offset = parsed.get("tail_offset", len(blob))
    for row in rows:
        source = row.get("source") or {}
        if (container and source.get("container") not in (None, container)) \
                or source.get("member") != member:
            stats["foreign"] += 1
            continue
        if row.get("record") is not None or _record_from_id(row.get("id")) is not None \
                or row.get("part") != "text" or not isinstance(source.get("offset"), int):
            continue                        # not an offset row - plan_edits owns it
        stats["rows"] += 1
        target = TW.english(row)
        if not target:
            stats["empty"] += 1
            continue
        offset = source["offset"]
        if offset >= tail_offset:
            stats["tail"] += 1
            skipped.append(f"{row.get('id')}: tail-pool row, left to the slot writer")
            continue
        hit = None
        for rec_row in parsed["records"]:
            if not (rec_row["offset"] <= offset < rec_row["offset"] + rec_row["length"]):
                continue
            for role in ISR.FIELDS:
                start = rec_row["offset"] + rec_row[f"{role}_offset"]
                if start <= offset < start + rec_row[f"{role}_slot"]:
                    raw = field_raw(blob, rec_row, role)
                    form = TW.match_form(row.get("jp"), raw)
                    if form is not None:
                        hit = (rec_row["record"], role, raw, form)
                    break
            break
        if hit is None:
            stats["mismatch"] += 1
            skipped.append(f"{row.get('id')}: no field at {offset} holds this jp")
            continue
        record, role, raw, form = hit
        try:
            value = TW.encode_en(target, raw, form)
        except (TW.TableError, WriteError) as exc:
            stats["mismatch"] += 1
            skipped.append(f"{row.get('id')}: {exc}")
            continue
        previous = edits.setdefault(record, {}).get(role)
        if previous is not None and previous != value:
            skipped.append(f"{row.get('id')}: conflicts with another row targeting record "
                           f"{record} role {role}; the member is refused")
            stats["mismatch"] += 1
            edits[record].pop(role)
            edits[record]["__conflict__"] = True
            continue
        edits[record][role] = value
        stats["applied"] += 1
    return edits, skipped, stats


def _norm_value(value: object) -> bytes:
    """Comparable bytes of an edit value: planners emit text (plan_edits) or the ready bytes
    of encode_target (plan_offset_edits) for the same physical field."""
    if isinstance(value, bytes):
        return value
    try:
        return encode(str(value))
    except WriteError:
        return b"\x00unencodable:" + str(value).encode("utf-8", "replace")


def merge_edits(*plans) -> Tuple[Dict[int, Dict[str, object]], List[str]]:
    """Merge edit plans; a physical target named twice with different bytes refuses the member.

    The two planners represent the same translation differently (text vs encoded bytes), so
    the conflict test compares encoded bytes - a structured row and an offset row covering the
    same field with the same English are one edit, not a conflict.
    """
    merged: Dict[int, Dict[str, object]] = {}
    problems: List[str] = []
    for edits in plans:
        for record, roles in edits.items():
            for role, value in roles.items():
                if role == "__conflict__":
                    continue
                previous = merged.setdefault(record, {}).get(role)
                if previous is not None and _norm_value(previous) != _norm_value(value):
                    problems.append(f"record {record} role {role}: two rows, two translations")
                    merged[record].pop(role)
                    merged[record]["__conflict__"] = True
                else:
                    merged[record][role] = value
    for record in list(merged):
        if "__conflict__" in merged[record]:
            merged.pop(record)
    return merged, problems


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


def collect_rows(paths: Iterable[Path]) -> Tuple[List[dict], List[Path]]:
    """Rows of every ``*.jsonl`` given; a directory means all of its ``*.jsonl`` (sorted)."""
    files: List[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.jsonl")))
        else:
            files.append(path)
    rows: List[dict] = []
    for path in files:
        rows.extend(read_package(path))
    return rows, files


def apply_container(src: Path, dst: Path, rows: List[dict], dry_run: bool = False) -> dict:
    """Apply the item/skill rows of a package to one config container, then verify by re-reading."""
    cpk = cpk_write.load(src)
    replacement = None
    report = {"container": src.name, "members": [], "skipped": [], "applied_rows": 0,
              "empty_rows": 0, "mismatch_rows": 0, "foreign_rows": 0}
    for member in cpk.members:
        if not member.name.lower().endswith(".pac"):
            continue
        pac = configst_pack.parse_pac(cpk_write.decompressed(member.blob))
        changed = False
        for sub in pac["subs"]:
            kind = _kind_of(sub["name"])
            if kind is None:
                continue
            parsed = ISR.parse_member(sub["data"], kind, sub["name"], src.name)
            edits, skipped, stats = plan_edits(rows, sub["name"], parsed, src.name)
            offset_edits, offset_skipped, offset_stats = plan_offset_edits(
                rows, sub["name"], parsed, sub["data"], src.name)
            edits, conflicts = merge_edits(edits, offset_edits)
            skipped.extend(offset_skipped)
            skipped.extend(conflicts)
            for key in ("rows", "applied", "empty", "mismatch"):
                stats[key] += offset_stats[key]
            stats["tail_rows"] = stats.get("tail_rows", 0) + offset_stats["tail"]
            report["skipped"].extend(skipped)
            report["applied_rows"] += stats["applied"]
            report["empty_rows"] += stats["empty"]
            report["mismatch_rows"] += stats["mismatch"]
            report["foreign_rows"] += stats["foreign"]
            if not edits:
                continue
            new_blob, member_report = rebuild_member(sub["data"], kind, edits, sub["name"])
            sub["data"] = new_blob
            changed = True
            report["members"].append(member_report)
        if changed:
            replacement = (member.name, configst_pack.rebuild_pac(pac))
    report["applied"] = report["applied_rows"]   # the orchestrator reads this key
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
        target = TW.english(row)
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
                        found[key] = TW.display(field_raw(sub_blob, row, role))
    failures = []
    for (member, record, role), target in want.items():
        got = found.get((member, record, role))
        if got != target:
            failures.append(f"{member}#{record}:{role}: {got!r} != {target!r}")
    return {"checked": len(want), "ok": len(want) - len(failures), "failures": failures[:5]}


EXTRA_KINDS = {"srwDL_Spirit.bin": "spirit", "srwDL_StatusChange.bin": "status_change"}


def _kind_of(member_name: str) -> Optional[str]:
    if member_name in ISR.EXCLUDED:
        return None
    if member_name in EXTRA_KINDS:
        return EXTRA_KINDS[member_name]
    for kind, prefix in ISR.KIND_PREFIX.items():
        if member_name.startswith(prefix) and not member_name.endswith(
                tuple(f"{i:02d}.bin" for i in range(1, 9))):
            return kind
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--translations", type=Path, nargs="+", required=True,
                        help="package JSONL files, or a directory holding them")
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    rows, files = collect_rows(args.translations)
    dst = args.out or Path("local/patched") / args.container.name
    report = apply_container(args.container, dst, rows, dry_run=args.dry_run)
    report["translation_files"] = [path.name for path in files]
    report["rows_read"] = len(rows)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if not args.dry_run and report.get("changed"):
        print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
