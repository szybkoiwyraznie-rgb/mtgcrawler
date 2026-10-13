#!/usr/bin/env python3
"""Write translated dialogue from the package into an event member, and the member into its CPK.

This closes the read -> translate -> write loop for the story text.  The package row
(``local/translation/00_dialogue.jsonl``) carries the exact place of every line::

    {"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "jp": "（俺は今、…）", "en": "",
     "source": {"container": "eventP00.cpk", "member": "DL100_01.bin", "offset": 1844}}

``offset`` is where the text starts, measured when the package was exported - on every row of every
measured member the Japanese text sits there byte for byte, which is what this tool checks first.

The dialogue record, measured on the real file
----------------------------------------------
A dialogue line is a record of type ``0xC9``; it sits inside a ``0xC8`` wrapper, which sits inside
an ``EVNT`` section, which sits inside the ``EDAT`` header of the member::

    C9 00 00 00  size  6 x u16 (1, speaker id, 0, 0, 0, FFFF)  text … 00 00 00
    ^ type       ^ whole record, 4-byte aligned      ^ offset of the text = record + 20

so, unlike the narration records that ``grow_event_text`` handles, the record carries a real size
field and the padding is alignment, not a terminator.  Growing a line therefore means rewriting the
record's size, the size of every ``0xC8`` wrapper around it, the section size and the ``EDAT`` size -
all of them fields *before* the inserted bytes, so nothing has to be repointed (the file is walked,
never indexed: no pointer table points at a string).

What this refuses
-----------------
* a row whose text is not at its recorded offset (a stale package never clobbers bytes),
* a row that is not a ``0xC9`` dialogue record (the other kinds - narration, victory conditions,
  labels - are read out of records without a text length field and need their own writer),
* a target that does not encode in CP932 or does not fit the game's dialogue box,
* any result whose block walk, chain walk or text list does not match the original.

Usage::

    python3 tools/event_text_apply.py --container ../google_drive/eventP00.cpk --member DL100_01.bin \
        --package local/translation --out local/patched/eventP00.cpk
    python3 tools/event_text_apply.py --container ../google_drive/eventP00.cpk --identity
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_write          # noqa: E402
import evnt_walk as EW    # noqa: E402
import export_strings     # noqa: E402
import speaker_map as SM  # noqa: E402

RECORD_TEXT = 0xC9
RECORD_NARRATION = 0x1B7
#: record type -> where its text starts inside the record (8-byte record header + own header)
TEXT_START = {RECORD_TEXT: 20, RECORD_NARRATION: 12}
#: narration is drawn wider than the dialogue box (measured: up to 26 full-width characters)
NARRATION_WIDTH = 52     # a dialogue line
RECORD_WRAPPER = 0xC8  # the record that holds the chain of one scene
TEXT_HEADER = 12       # 6 u16 words in front of the text (evnt_walk.TEXT_HEADER)
RECORD_HEADER = 8      # type + size
TEXT_OFFSET_IN_RECORD = RECORD_HEADER + TEXT_HEADER   # 20: measured on the real files
BOX_WIDTH = 46         # the in-game dialogue box, half-width units


def record_text_length(size: int, text: bytes) -> int:
    """Length of the text inside a record of ``size`` bytes (text runs to the first NUL)."""
    return len(text)


def padded_size(text_length: int, text_start: int = TEXT_OFFSET_IN_RECORD) -> int:
    """The size a record takes for a text of this length.

    Measured for both record types (0xC9 dialogue and 0x1B7 narration, 2026-10-12): every record is
    4-byte aligned and keeps at least one NUL after the text (pads of 1…4 bytes occur, never 0).
    """
    pad = (-(text_start + text_length)) % 4
    return text_start + text_length + (pad or 4)


def parse_block_records(blob: bytes) -> Tuple[List[dict], List[str]]:
    """Every record of every block, with its depth (0 = directly in the block's chain)."""
    errors: List[str] = []
    records: List[dict] = []
    blocks, block_errors = EW.blocks(blob)
    errors.extend(block_errors)
    for block in blocks:
        if block["chain_start"] is None:
            continue

        def walk(start: int, end: int, depth: int) -> None:
            for offset, rtype, size in EW.walk_chain(blob, start, end):
                records.append({"offset": offset, "type": rtype, "size": size, "depth": depth,
                                "block": block})
                if rtype == RECORD_WRAPPER:
                    walk(offset + RECORD_HEADER, offset + size, depth + 1)

        walk(block["chain_start"], block["end"], 0)
    return records, errors


def text_of(blob: bytes, record: dict) -> bytes:
    """The text bytes of a record (everything before the first NUL of its payload)."""
    start = TEXT_START.get(record["type"])
    if start is None:
        raise ValueError(f"record type {record['type']:#x} has no text field I know")
    offset, size = record["offset"], record["size"]
    payload = blob[offset + RECORD_HEADER:offset + size]
    return payload[start - RECORD_HEADER:].split(b"\x00", 1)[0]


def find_record(blob: bytes, text_offset: int, text: bytes) -> Optional[dict]:
    """The innermost record with a length field whose text starts exactly at ``text_offset``.

    Dialogue and narration are both measured to keep their text at a fixed place after the record
    header, so both are found the same way; anything else has no length field and is refused here
    (its own writer is still to come).
    """
    records, _ = parse_block_records(blob)
    candidates = [r for r in records
                  if r["type"] in TEXT_START
                  and r["offset"] + TEXT_START[r["type"]] == text_offset
                  and blob[r["offset"]:r["offset"] + r["size"]].startswith(
                      struct.pack("<II", r["type"], r["size"]))]
    if not candidates:
        return None
    record = min(candidates, key=lambda r: r["size"])
    if text_of(blob, record) != text:
        return None
    return record


def find_edat(blob: bytes) -> int:
    """Offset of the ``EDAT`` header inside a member (0 for event members).

    The battle-quote pacs of the ``mesbtl`` containers put a pac header in front of the ``EDAT``
    header (measured on mesbtl00.cpk/p0050.pac: ``EDAT`` sits at 5732, its count field names the
    176 ``EVNT`` sections that follow at ``edat + 12``).  An ``EDAT`` occurrence only counts when
    the first section tag really follows it, so game text that happens to spell ``EDAT`` cannot
    fool the search.  Returns -1 when there is no such header.
    """
    pos = 0
    while True:
        i = blob.find(b"EDAT", pos)
        if i < 0:
            return -1
        if blob[i + 12:i + 16] == b"EVNT":
            return i
        pos = i + 4


def grow_text(blob: bytes, record: dict, new_text: bytes, edat_at: int = 0) -> bytes:
    """Return the member with one dialogue record's text replaced by ``new_text``.

    Everything around it is updated: the record's own size, the size of every wrapper that holds it,
    the ``EVNT`` section size and the ``EDAT`` size.  All of those fields sit *before* the record, so
    their offsets do not move when the text grows.

    ``edat_at`` is the offset of the ``EDAT`` header (see :func:`find_edat`): 0 for event members,
    deeper for the ``mesbtl`` battle-quote pacs.  The EDAT size field lives at ``edat_at + 4`` and
    grows by the same delta as the record (it is a linear function of the section span, which grows
    by exactly delta), for both the event rule (size = span) and the mesbtl rule (size = span minus
    four bytes per section) -- measured on the real files.
    """
    offset, old_size = record["offset"], record["size"]
    start = TEXT_START.get(record["type"])
    if start is None:
        raise ValueError(f"record type {record['type']:#x} has no text field I know")
    old_text = text_of(blob, record)
    if struct.unpack_from("<I", blob, offset)[0] != record["type"]:
        raise ValueError(f"record at {offset} is not a {record['type']:#x} record")
    if not blob.startswith(struct.pack("<I", old_size), offset + 4):
        raise ValueError(f"record at {offset} declares {old_size} bytes")
    size = padded_size(len(new_text), start)
    delta = size - old_size
    head = blob[offset:offset + start]
    tail = blob[offset + old_size:]
    new_record = head + new_text + b"\x00" * (size - start - len(new_text))
    out = bytearray(blob[:offset] + new_record + tail)
    if delta:
        struct.pack_into("<I", out, offset + 4, size)
        # every wrapper record that holds this record grows with it
        records, _ = parse_block_records(blob)
        wrappers = [r for r in records
                    if r["type"] == RECORD_WRAPPER and r["offset"] < offset
                    and r["offset"] + r["size"] >= offset + old_size]
        for wrapper in sorted(wrappers, key=lambda r: r["offset"], reverse=True):
            struct.pack_into("<I", out, wrapper["offset"] + 4, wrapper["size"] + delta)
        # the section that holds the record, and the EDAT header of the member
        section = owner_section(blob, offset)
        if section is None:
            raise ValueError(f"no EVNT section holds the record at {offset}")
        struct.pack_into("<I", out, section["magic_offset"] + 4, section["size"] + delta)
        struct.pack_into("<I", out, edat_at + 4,
                         struct.unpack_from("<I", blob, edat_at + 4)[0] + delta)
    if len(old_text) == len(new_text) and blob[offset:offset + old_size] == bytes(out[offset:offset + size]):
        return bytes(blob)          # no change at all
    return bytes(out)


def owner_section(blob: bytes, offset: int) -> Optional[dict]:
    """The ``EVNT`` section (magic offset, body start, size) that holds a byte offset."""
    sections = EW.blocks(blob)[0]
    for block in sections:
        if block["end"] > offset >= block["payload_start"]:
            return {"magic_offset": block["payload_start"] - 8,
                    "body_start": block["payload_start"], "size": block["size"]}
    return None


def kind_of(record_type: int) -> str:
    """The package's name for a record type (``dialogue`` for 0xC9, ``narration`` for 0x1B7…)."""
    import event_dialogue

    if record_type == RECORD_TEXT:
        return "dialogue"
    return event_dialogue.KIND.get(record_type, f"type_{record_type:#x}")


def texts_of_member(blob: bytes, container: str = "", member: str = "") -> List[Tuple[str, int, str]]:
    """``[(kind, record_type, text)]`` of every text of a member, in reading order.

    Records that have a length field are read with the writer's own reader -- the extractor only
    reports runs with Japanese characters, so it would not see an English line we just wrote, and
    a verification that cannot see its own result is worthless.  Everything else (the table texts
    with no length field) still comes from the extractor, unchanged.
    """
    import event_dialogue

    rows: List[Tuple[str, int, str]] = []
    records, _ = parse_block_records(blob)
    for record in records:
        if record["type"] in TEXT_START:
            rows.append((kind_of(record["type"]), record["type"],
                         text_of(blob, record).decode("cp932", errors="replace")))
    found = event_dialogue.extract_member(blob, container, member)
    rows += [(item["kind"], item["record_type"], item["text"])
             for item in found["other"] if item["record_type"] not in TEXT_START]
    rows += [("embedded", 0, item["text"]) for item in found["embedded"]]
    return sorted(rows, key=lambda item: (item[0], item[2]))


def _text_kind(records: List[dict], text_offset: int) -> Tuple[Optional[str], Optional[int]]:
    """``(kind, record type)`` of the record whose text starts at this offset."""
    for record in records:
        start = TEXT_START.get(record["type"])
        if start is not None and record["offset"] + start == text_offset:
            return kind_of(record["type"]), record["type"]
    return None, None


def _error_kind(message: str) -> str:
    """An error message without the byte offsets (they move when a text grows)."""
    return re.sub(r"\d+", "#", message)


def verify(original: bytes, modified: bytes, changed: List[Tuple[int, bytes, bytes]],
           edat_at: int = 0) -> List[str]:
    """Re-parse the result and report what does not hold.

    ``changed`` is ``[(text_offset, old_text, new_text)]``.  The check is deliberately strict: no new
    block-walk error, the blocks still cover the whole file, the record count is unchanged, and the
    texts of the member are exactly the texts it had before minus the ones we replaced plus the new
    ones - a growth that lost or invented a text is refused.

    ``edat_at`` is the offset of the ``EDAT`` header (:func:`find_edat`); the sections must cover
    the file from ``edat_at + 12`` on, each section spanning ``8 + size`` bytes in the event
    variant and ``4 + size`` in the mesbtl variant (its size field counts itself), both measured.
    """
    problems: List[str] = []
    before_blocks, before_errors = EW.blocks(original)
    after_blocks, after_errors = EW.blocks(modified)
    # an error message carries an offset that legitimately moves with the text, so compare kinds
    before_kinds = collections.Counter(_error_kind(message) for message in before_errors)
    for message in after_errors:
        kind = _error_kind(message)
        if before_kinds[kind]:
            before_kinds[kind] -= 1
        else:
            problems.append(f"block walk: {message}")
    if len(after_blocks) != len(before_blocks):
        problems.append(f"block count changed: {len(before_blocks)} -> {len(after_blocks)}")
    if after_blocks and after_blocks[-1]["end"] != len(modified):
        problems.append(f"the block walk ends at {after_blocks[-1]['end']}, "
                        f"the file is {len(modified)} bytes")
    # the sections start right after the 12-byte EDAT header and must cover the rest exactly;
    # a mesbtl section's size field counts itself, so it spans 4 + size, an event one 8 + size
    covered = sum((4 if block["variant"] == "mesbtl" else 8) + block["size"]
                  for block in after_blocks)
    if after_blocks and (after_blocks[0]["tag"] != edat_at + 12
                         or covered != len(modified) - (edat_at + 12)):
        problems.append(f"the sections cover {covered} bytes, the file leaves "
                        f"{len(modified) - (edat_at + 12)} for them")

    before_records, _ = parse_block_records(original)
    after_records, _ = parse_block_records(modified)
    if len(before_records) != len(after_records):
        problems.append(f"record count changed: {len(before_records)} -> {len(after_records)}")
    for record in after_records:
        if record["size"] < RECORD_HEADER or record["offset"] + record["size"] > len(modified):
            problems.append(f"record at {record['offset']} runs past the file")
            break

    before = collections.Counter(texts_of_member(original))
    after = collections.Counter(texts_of_member(modified))
    expected = before.copy()
    for offset, old, new in changed:
        kind, rtype = _text_kind(before_records, offset)
        if kind is None:
            problems.append(f"no record of a known type holds the text at {offset}")
            continue
        expected[(kind, rtype, old.decode("cp932", errors="replace"))] -= 1
        expected[(kind, rtype, new.decode("cp932", errors="replace"))] += 1
    expected = collections.Counter({key: value for key, value in expected.items() if value > 0})
    for key, count in (expected - after).items():
        problems.append(f"text missing after the change ({count}x): {key[2][:40]!r}")
    for key, count in (after - expected).items():
        problems.append(f"text appeared that was not there before ({count}x): {key[2][:40]!r}")
    return problems


def rows_for_member(package: Path, container: str, member: str) -> List[dict]:
    """Package rows of one member that carry English and are dialogue records."""
    rows: List[dict] = []
    for line in (Path(package) / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        source = row.get("source") or {}
        if source.get("container") != container or source.get("member") != member:
            continue
        if not (row.get("en") or "").strip():
            continue
        rows.append(row)
    return rows


def box_problems(text: str) -> List[str]:
    problems = []
    for line in text.split("\n"):
        width = export_strings.display_width(line)
        if width > BOX_WIDTH:
            problems.append(f"a line is {width} wide, the box fits {BOX_WIDTH}")
    return problems


def apply_member(blob: bytes, rows: List[dict], verify_result: bool = True) -> Tuple[bytes, dict]:
    """Apply every row to the member and return the new member plus a report.

    With ``verify_result`` (the default) the result is re-parsed before it is returned: the block
    walk, the record count and every text of the member are compared with the original, so a change
    that would break the file is reported instead of written out.

    The member may be an event member (``EDAT`` at byte 0) or a decompressed battle-quote pac of
    the ``mesbtl`` containers (a pac header, then ``EDAT``): :func:`find_edat` tells the two apart
    and every size fix lands on the header that is really there.
    """
    report = {"rows": len(rows), "applied": 0, "skipped": [], "refused": [], "changed": [],
              "problems": [], "notes": []}
    edat_at = find_edat(blob)
    if edat_at < 0:
        report["problems"].append("the member has no EDAT header followed by an EVNT section")
        return blob, report
    report["edat_at"] = edat_at
    ordered = sorted(rows, key=lambda row: row["source"]["offset"], reverse=True)
    out = blob
    for row in ordered:
        offset = int(row["source"]["offset"])
        jp = (row["jp"] or "").encode("cp932")
        en = (row["en"] or "").encode("cp932")
        if blob[offset:offset + len(jp)] != jp:
            report["skipped"].append(f"{row['id']}: the Japanese text is not at {offset}")
            continue
        record = find_record(out, offset, jp)
        if record is None:
            report["skipped"].append(
                f"{row['id']}: kind {row.get('kind')} has no length field at {offset} "
                "(its own writer is still to come)")
            continue
        if record["type"] == RECORD_TEXT:
            problems = box_problems(row["en"] or "")
            if problems:
                report["refused"].extend(f"{row['id']}: {problem}" for problem in problems)
                continue
        else:
            # narration is drawn in a wider field, so its width is a note, not a refusal
            wide = [(export_strings.display_width(line), line)
                    for line in (row["en"] or "").split("\n")
                    if export_strings.display_width(line) > NARRATION_WIDTH]
            if wide:
                report["notes"].append(
                    f"{row['id']}: narration line {wide[0][0]} wide, widest measured is "
                    f"{NARRATION_WIDTH}")
        out = grow_text(out, record, en, edat_at)
        report["applied"] += 1
        report["changed"].append((offset, jp, en))
    if verify_result and report["changed"]:
        report["problems"] = verify(blob, out, report["changed"], edat_at)
    return out, report


def apply_container(container: Path, member: str, rows: List[dict], out_path: Path) -> dict:
    """Apply the rows to one member and rebuild the container around it."""
    members = dict(SM.read_members(container))
    if member not in members:
        raise ValueError(f"{container.name} has no member {member}")
    blob = members[member]
    modified, report = apply_member(blob, rows)
    report["member"] = member
    report["bytes"] = len(modified) - len(blob)
    if report["problems"]:
        report["written"] = None
        return report
    cpk = cpk_write.load(container)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(cpk_write.rebuild(cpk, (member, modified)))
    report["written"] = str(out_path)
    report["container_bytes"] = out_path.stat().st_size - container.stat().st_size
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--member", help="one member name; every event member when omitted")
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--out", type=Path, help="where to write the rebuilt container")
    parser.add_argument("--identity", action="store_true",
                        help="rebuild the container unchanged and compare with the original")
    args = parser.parse_args(argv)

    if args.identity:
        ok, message = cpk_write.verify_identity(args.container)
        print(("IDENTITY OK: " if ok else "IDENTITY FAILED: ") + message)
        return 0 if ok else 1

    if not args.out:
        parser.error("--out is needed unless --identity is given")
    members = dict(SM.read_members(args.container))
    names = [args.member] if args.member else [name for name in members if name.endswith(".bin")]
    total = {"members": 0, "applied": 0, "skipped": 0, "refused": 0, "bytes": 0}
    for name in names:
        rows = rows_for_member(args.package, args.container.name, name)
        if not rows:
            continue
        report = apply_container(args.container, name, rows, args.out)
        total["members"] += 1
        total["applied"] += report["applied"]
        total["skipped"] += len(report["skipped"])
        total["refused"] += len(report["refused"])
        total["bytes"] += report["bytes"]
        print(json.dumps({k: v for k, v in report.items() if k != "changed"},
                         ensure_ascii=False, indent=1))
        for message in report["skipped"][:10]:
            print("  pominięte:", message)
        for message in report["refused"][:10]:
            print("  odrzucone:", message)
        if report["problems"]:
            return 1
    print(json.dumps(total, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
