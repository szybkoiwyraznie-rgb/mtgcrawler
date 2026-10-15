#!/usr/bin/env python3
"""Write translated item/skill texts back into a config container (the `apply` path, part 1).

The record layout is the one measured by ``item_skill_records``: twenty u16 parameter words, six
field boundaries at +40, one more parameter word, the five NUL-terminated fields, then the numeric
tail.  Because the boundaries are explicit, growing a field only means rebuilding the record: the
member's record-offset table and its ``tail_offset`` are re-derived, and everything after the record
shifts.  Two more things point at text.  The fragment pool behind the records starts with its own
table of **absolute** string offsets (``item_skill_records.parse_tail_pool``), so the rebuild
re-points that table at the pool's new home - copied verbatim it would send the game into the
record area.  And **every record carries the pool's position at +36**, as a u32 *relative to the
record start* (``tail_offset - record_offset``; measured 2230/2230 records of the five original
members 2026-10-14 - Skill00 1469, Item00 300, Item 300, StatusChange 101, Spirit 60).  A rebuild
moves both the record and the pool, so the word is recomputed for every record; builds #6-#9
copied it verbatim (and mis-read 46 of them as record cross references), which left the game a
pool pointer landing inside the record area - the crash candidate under test since build #10.
The pool strings themselves are translated by :func:`apply_tail_pool` (the
orchestrator's ``tail-pool`` step): the strings are rewritten at any length and the table
recomputed, exactly as ``table_write`` does for the convention-C DLC members.

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
import bisect
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
PREAMBLE_WORD = 26         # u16 at +52: record-relative position of the PARAMETER WORDS (see below)
LAST_BOUNDARY_WORD = PARAM_WORDS + ISR.BOUNDARY_COUNT - 1   # word 25 = end of the last text field
BASE_POINTER = 32          # i32: the member start relative to the record (= -record_offset)
POOL_POINTER = 36          # u32: the fragment pool's offset relative to the record start

# The u16 at +52 is a THIRD record-relative pointer [ZWERYFIKOWANE na 2 230 oryginalnych rekordach,
# 2026-10-15]: it marks where the numeric parameter words start, i.e. it equals
# ``last_boundary + delta`` with a record-specific ``delta`` of 2..18 bytes (the counted list of
# pairs that sits right after the texts: ``1, 78, 0`` = 6 bytes in 1 107 of 1 469 Skill00 records).
# Builds #6-#13 copied the word verbatim, so in every record whose texts grew or shrank the game
# read its parameters from inside the text (or past the real words).  A new game survived it; the
# user's chapter-2 save crashed on load ("CPU Jump to ffffffff") with the rebuilt Skill00 alone,
# and the Japanese member grown with spaces (Y3, every record touched) crashed the same way.
# The rebuilt record keeps ``delta``: the pointer follows the texts exactly like +32/+36 follow
# the record.

# In-game size budget of ``srwDL_Skill00.bin`` [ZWERYFIKOWANE w grze, 2026-10-14/15, PPSSPP,
# "SRW OE 1.08" + original DLC]: the game crashes at "Loading" (memcpy to NULL) once the member
# is too big, whatever its content - Japanese text padded with spaces to 217 086 B loads (T3 and
# W5), 221 182 B crashes (T4), 228 202 B crashes (T6/S1/build #10); a tightly packed .pac does
# not help (U2: pac 905 216 B, member 228 202 B - crashes) while the original member in the same
# tight pac loads (U1), so the limit sits on this member, not on the archive.  Original size
# 208 958 B; the largest size that loaded is 217 086 B; the budget below keeps 318 B under it,
# covering the net growth (+311 B) of the other translated config00 members in case the game
# allocates them from the same pool (unknown).
SKILL00_LIMIT = 216_768
MEMBER_SIZE_LIMITS = {"srwDL_Skill00.bin": SKILL00_LIMIT}


class WriteError(Exception):
    """The member or the edit list cannot be rebuilt safely."""


class SizeBudgetError(WriteError):
    """The rebuilt member would exceed its in-game size budget (the game would crash at Loading).

    Raised instead of a plain refusal because a container holding this member must not be
    written at all: ``build_translation_patch`` turns it into "NOT written" and exit status 1,
    where an ordinary refusal only drops the rows and ships the rest.
    """


def size_limit_problem(member: str, size: int) -> Optional[str]:
    """The refusal text when ``member`` rebuilt to ``size`` bytes would crash the game, else None."""
    limit = MEMBER_SIZE_LIMITS.get(member)
    if limit is None or size <= limit:
        return None
    return (f"{member}: {size} B exceeds the in-game budget of {limit} B (+{size - limit} B over; "
            f"the game crashes at Loading above it, measured 2026-10-15) - shorten the English "
            f"(tools/skill_shrink.py); the member is refused")


def pool_pointer_faults(blob: bytes, parsed: dict) -> List[int]:
    """Records whose u32 at +36 is not ``tail_offset - record_offset``.

    Empty for all 2230 records of the five original convention-B members (measured 2026-10-14);
    a non-empty list means the layout is not the understood one and the member must be refused.
    """
    tail_offset = parsed["tail_offset"]
    faults = []
    for row in parsed["records"]:
        offset = row["offset"]
        if offset + POOL_POINTER + 4 > len(blob):
            faults.append(row["record"])
            continue
        if struct.unpack_from("<I", blob, offset + POOL_POINTER)[0] != tail_offset - offset:
            faults.append(row["record"])
    return faults


def base_pointer_faults(blob: bytes, parsed: dict) -> List[int]:
    """Records whose i32 at +32 is not ``-record_offset`` (the member start relative to the record).

    Measured 2026-10-15 on the five original convention-B members: 2230/2230 records carry it
    (Skill00 1469, Item00 300, Item 300, StatusChange 101, Spirit 60).  Builds #6-#11 copied the
    word verbatim after moving the records, so in every record but the first the game's
    ``record + value`` no longer reached the member start - the Loading screen does not care,
    the pilot's spirit list (hover = crash) and the intermission (crash before it opens) do
    [ZWERYFIKOWANE w grze, build #11].  A non-empty list on a source means a layout this writer
    does not understand - refuse it rather than guess.
    """
    faults = []
    for row in parsed["records"]:
        offset = row["offset"]
        if offset + BASE_POINTER + 4 > len(blob):
            faults.append(row["record"])
            continue
        if struct.unpack_from("<i", blob, offset + BASE_POINTER)[0] != -offset:
            faults.append(row["record"])
    return faults


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
    delta = parameter_delta(header)
    if delta is None:
        raise WriteError(f"record {row.get('record')}: the parameter pointer at +{2 * PREAMBLE_WORD} "
                         f"({header[PREAMBLE_WORD]}) does not sit between the last text boundary "
                         f"({header[LAST_BOUNDARY_WORD]}) and the record end; refused")
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
    # the parameter pointer moves with the texts: new last boundary + the record's own delta
    return (struct.pack("<%dH" % PARAM_WORDS, *header[:PARAM_WORDS])
            + struct.pack("<%dH" % ISR.BOUNDARY_COUNT, *boundaries)
            + struct.pack("<H", boundaries[-1] + delta)
            + blob + tail)


def parameter_delta(header: List[int]) -> Optional[int]:
    """Bytes between the end of the last text field and the parameter words of a record.

    ``None`` when the record does not follow the measured rule (pointer before the texts' end or
    past the record), which no original record does.
    """
    if len(header) <= PREAMBLE_WORD:
        return None
    delta = header[PREAMBLE_WORD] - header[LAST_BOUNDARY_WORD]
    if delta < 0 or header[PREAMBLE_WORD] > 2 * len(header):
        return None
    return delta


def parameter_pointer_faults(blob: bytes, parsed: dict) -> List[int]:
    """Records whose u16 at +52 does not lie between the last text boundary and the record end."""
    faults = []
    for row in parsed["records"]:
        pointer = struct.unpack_from("<H", blob, row["offset"] + 2 * PREAMBLE_WORD)[0]
        if not (row["boundaries"][-1] <= pointer <= row["length"]):
            faults.append(row["record"])
    return faults


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
    # the u32 at +36 of every record is the fragment pool's position relative to the record
    # (tail_offset - record_offset, 2230/2230 original records); a source that breaks the rule
    # is a layout this writer does not understand - refuse it rather than guess
    faults = pool_pointer_faults(blob, parsed)
    if faults:
        raise WriteError(f"{member or kind}: {len(faults)} record(s) {faults[:5]} do not carry "
                         f"the pool pointer (tail_offset - offset) at +{POOL_POINTER}; "
                         f"the member is refused")
    # likewise the i32 at +32 is the member start relative to the record (-record_offset,
    # 2230/2230 original records); builds #6-#11 left it stale and the game crashed as soon as
    # a screen followed it (spirit list hover, intermission)
    faults = base_pointer_faults(blob, parsed)
    if faults:
        raise WriteError(f"{member or kind}: {len(faults)} record(s) {faults[:5]} do not carry "
                         f"the member base pointer (-offset) at +{BASE_POINTER}; "
                         f"the member is refused")
    # and the u16 at +52 points at the parameter words right after the texts (2230/2230
    # original records); builds #6-#13 left it stale and the chapter-2 save crashed on load
    faults = parameter_pointer_faults(blob, parsed)
    if faults:
        raise WriteError(f"{member or kind}: {len(faults)} record(s) {faults[:5]} do not carry "
                         f"the parameter pointer (last boundary + delta) at +{2 * PREAMBLE_WORD}; "
                         f"the member is refused")
    records = [rebuild_record(row, edits.get(row["record"], {})) for row in rows]
    count = len(records)
    offsets, position = [], 8 + 4 * count
    for record in records:
        offsets.append(position)
        position += len(record)
    # records and pool both move: every record's pool pointer is recomputed for the new layout
    # (builds #6-#9 copied the old value verbatim, which pointed into the record area)
    rewritten = 0
    base_rewritten = 0
    patched = []
    for record, offset in zip(records, offsets):
        rec = bytearray(record)
        pointer = position - offset
        if struct.unpack_from("<I", rec, POOL_POINTER)[0] != pointer:
            struct.pack_into("<I", rec, POOL_POINTER, pointer)
            rewritten += 1
        # the member base pointer moves with the record as well (-new offset; build #11 crashed
        # in the spirit list and before the intermission with the old values)
        if struct.unpack_from("<i", rec, BASE_POINTER)[0] != -offset:
            struct.pack_into("<i", rec, BASE_POINTER, -offset)
            base_rewritten += 1
        patched.append(bytes(rec))
    # the fragment pool keeps its strings but its pointer table holds absolute offsets: it is
    # rebuilt at the new tail position (an unparseable pool refuses the member - fail closed)
    try:
        _, pool_strings = ISR.parse_tail_pool(blob, parsed["tail_offset"])
    except ValueError as exc:
        raise WriteError(f"{member or kind}: the fragment pool does not parse ({exc}); "
                         f"the member is refused") from exc
    tail_pool = ISR.build_tail_pool(position, pool_strings)
    out = (struct.pack("<2I", position, count)
           + b"".join(struct.pack("<I", offset) for offset in offsets)
           + b"".join(patched) + tail_pool)
    # prove it on the result: same record count, every pool pointer right, the pool parses
    after = ISR.parse_member(out, kind, member)
    if after["errors"] or len(after["records"]) != count or after["tail_offset"] != position:
        raise WriteError(f"{member or kind}: the rebuilt member does not parse back "
                         f"({after['errors'][:2]}); the member is refused")
    if pool_pointer_faults(out, after):
        raise WriteError(f"{member or kind}: pool pointers wrong after the rebuild; "
                         f"the member is refused")
    if base_pointer_faults(out, after):
        raise WriteError(f"{member or kind}: base pointers wrong after the rebuild; "
                         f"the member is refused")
    try:
        _, check_strings = ISR.parse_tail_pool(out, position)
    except ValueError as exc:
        raise WriteError(f"{member or kind}: the rebuilt pool does not parse ({exc})") from exc
    if check_strings != pool_strings:
        raise WriteError(f"{member or kind}: the rebuilt pool lost strings; the member is refused")
    too_big = size_limit_problem(member, len(out))
    if too_big:
        raise SizeBudgetError(too_big)
    report = {"member": member, "kind": kind, "records": count,
              "edited_records": len(edits), "edited_roles": sum(len(v) for v in edits.values()),
              "pool_pointers_rewritten": rewritten, "base_pointers_rewritten": base_rewritten,
              "pool_strings": len(pool_strings),
              "pool_shift": position - parsed["tail_offset"],
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
    sits in the tail pool are not record fields - they belong to :func:`plan_pool_edits` /
    :func:`apply_tail_pool`, which rewrite the pool with its pointer table.
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
            skipped.append(f"{row.get('id')}: tail-pool row, left to the pool writer")
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


def plan_pool_edits(rows: Iterable[dict], member: str, parsed: dict, blob: bytes,
                    container: str = "") -> Tuple[Dict[int, bytes], List[str], dict]:
    """``{pool index: new bytes}`` for the rows that address the fragment pool of ``member``.

    Two row addressings exist in ``04``: the older export gives every string of a pool the
    pool's *start* offset (one id per pool) - such a row is matched by content against every
    pool string and every string that reads back as its ``jp`` gets the English (duplicates in
    the pool are the same fragment); a row carrying the exact offset of a string (the per-string
    export) is matched to that string only, and its ``jp`` must still read back from it.  A row
    whose offset falls *inside* a string (the leftover scan anchors a tokenised run a few bytes
    into it - measured on 13 Skill00 rows) is matched to that one string, again by its whole
    ``jp``.  A row that reads back from nothing is stale and refused; two rows asking two
    different texts for one string refuse that string.
    """
    edits: Dict[int, bytes] = {}
    owners: Dict[int, str] = {}
    skipped: List[str] = []
    stats = {"rows": 0, "applied": 0, "empty": 0, "mismatch": 0, "foreign": 0, "strings": 0}
    tail_offset = parsed.get("tail_offset", len(blob))
    try:
        pointers, strings = ISR.parse_tail_pool(blob, tail_offset)
    except ValueError as exc:
        raise WriteError(f"{member}: the fragment pool does not parse ({exc})") from exc
    index_of = {pointer: index for index, pointer in enumerate(pointers)}
    conflicts: set = set()
    for row in rows:
        source = row.get("source") or {}
        if (container and source.get("container") not in (None, container)) \
                or source.get("member") != member:
            stats["foreign"] += 1
            continue
        offset = source.get("offset")
        if not isinstance(offset, int) or offset < tail_offset:
            continue                        # a record row - the record planners own it
        stats["rows"] += 1
        target = TW.english(row)
        if not target:
            stats["empty"] += 1
            continue
        if offset == tail_offset:
            candidates = list(range(len(strings)))
        elif offset in index_of:
            candidates = [index_of[offset]]
        else:
            inside = bisect.bisect_right(pointers, offset) - 1
            if inside >= 0 and offset < pointers[inside] + len(strings[inside]):
                candidates = [inside]
            else:
                stats["mismatch"] += 1
                skipped.append(f"{row.get('id')}: offset {offset} is not a string of the pool")
                continue
        hits = []
        for index in candidates:
            form = TW.match_form(row.get("jp"), strings[index])
            if form is not None:
                hits.append((index, form))
        if not hits:
            stats["mismatch"] += 1
            skipped.append(f"{row.get('id')}: no pool string reads back as this jp")
            continue
        applied = False
        for index, form in hits:
            try:
                value = TW.encode_en(target, strings[index], form)
            except TW.TableError as exc:
                stats["mismatch"] += 1
                skipped.append(f"{row.get('id')}: {exc}")
                break
            previous = edits.get(index)
            if previous is not None and previous != value:
                conflicts.add(index)
                skipped.append(f"{row.get('id')}: conflicts with {owners[index]} on pool string "
                               f"{index}; the string stays Japanese")
                continue
            edits[index] = value
            owners[index] = str(row.get("id"))
            applied = True
        if applied:
            stats["applied"] += 1
    for index in conflicts:
        edits.pop(index, None)
    stats["strings"] = len(edits)
    return edits, skipped, stats


def rebuild_pool(blob: bytes, parsed: dict, edits: Dict[int, bytes]) -> bytes:
    """The member with the given pool strings replaced; the table is recomputed, the records
    and everything before the pool stay byte for byte."""
    tail_offset = parsed.get("tail_offset", len(blob))
    try:
        _, strings = ISR.parse_tail_pool(blob, tail_offset)
    except ValueError as exc:
        raise WriteError(f"the fragment pool does not parse ({exc})") from exc
    for index, value in edits.items():
        if not (0 <= index < len(strings)):
            raise WriteError(f"pool edit addresses string {index} of {len(strings)}")
        strings[index] = value
    out = blob[:tail_offset] + ISR.build_tail_pool(tail_offset, strings)
    # prove it: the result parses to the same count, the edited strings read back, no other moved
    _, check = ISR.parse_tail_pool(out, tail_offset)
    _, before = ISR.parse_tail_pool(blob, tail_offset)
    if len(check) != len(before) or any(
            check[i] != (edits.get(i) if i in edits else before[i]) for i in range(len(check))):
        raise WriteError("pool rebuild did not reproduce the requested strings")
    return out


def apply_tail_pool(src: Path, dst: Path, rows: List[dict], dry_run: bool = False) -> dict:
    """Translate the fragment pools of one config container (the orchestrator's ``tail-pool``
    step), at any length, and verify by re-reading the written file."""
    cpk = cpk_write.load(src)
    replacement = None
    report = {"container": src.name, "members": [], "problems": [], "applied": 0,
              "refused": 0, "per_member": {}}
    wanted: Dict[Tuple[str, int], bytes] = {}
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
            if parsed["errors"]:
                continue
            try:
                edits, skipped, stats = plan_pool_edits(rows, sub["name"], parsed, sub["data"],
                                                        src.name)
            except WriteError as exc:
                report["problems"].append(f"{sub['name']}: {exc}")
                continue
            if not stats["rows"]:
                continue
            report["problems"].extend(f"{sub['name']}: refused: {message}" for message in skipped)
            report["applied"] += stats["applied"]
            report["refused"] += stats["mismatch"]
            report["per_member"][sub["name"]] = {"rows": stats["rows"], "applied": stats["applied"],
                                                 "refused": stats["mismatch"],
                                                 "strings": stats["strings"]}
            if not edits:
                continue
            try:
                new_blob = rebuild_pool(sub["data"], parsed, edits)
            except WriteError as exc:
                report["problems"].append(f"{sub['name']}: {exc}")
                continue
            too_big = size_limit_problem(sub["name"], len(new_blob))
            if too_big:
                raise SizeBudgetError(too_big)       # the container must not ship at all
            for index, value in edits.items():
                wanted[(sub["name"], index)] = value
            report["members"].append({"member": sub["name"], "kind": kind,
                                      "strings": stats["strings"],
                                      "old_size": len(sub["data"]), "new_size": len(new_blob)})
            sub["data"] = new_blob
            changed = True
        if changed:
            replacement = (member.name, configst_pack.rebuild_pac(pac))
    report["changed"] = replacement is not None
    if replacement is None or dry_run:
        return report
    out = cpk_write.rebuild(cpk, replacement=replacement)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(out)
    report["verification"] = verify_pools(dst, wanted)
    return report


def verify_pools(path: Path, wanted: Dict[Tuple[str, int], bytes]) -> dict:
    """Re-read a written container: every requested pool string must be there, at its index."""
    found: Dict[Tuple[str, int], bytes] = {}
    for member_name, blob in SM.read_members(path):
        subs = list(IN.pac_subfiles(blob)) if member_name.lower().endswith(".pac") \
            else [(member_name, blob)]
        for sub_name, sub_blob in subs:
            kind = _kind_of(sub_name)
            if kind is None:
                continue
            parsed = ISR.parse_member(sub_blob, kind, sub_name, path.name)
            if parsed["errors"]:
                continue
            try:
                _, strings = ISR.parse_tail_pool(sub_blob, parsed["tail_offset"])
            except ValueError:
                continue
            for index, text in enumerate(strings):
                if (sub_name, index) in wanted:
                    found[(sub_name, index)] = text
    failures = [f"{member}#{index}: {found.get((member, index))!r} != {value!r}"
                for (member, index), value in wanted.items() if found.get((member, index)) != value]
    return {"checked": len(wanted), "ok": len(wanted) - len(failures), "failures": failures[:5]}


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
