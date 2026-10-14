#!/usr/bin/env python3
"""Grow/shrink writer for the pointer-pool config tables (convention A and C).

The config containers keep their dictionaries and catalogues as *pools*: a u32 record count, a
table of absolute record offsets, and per record a small table of u32 string pointers followed by
the NUL-terminated CP932 strings.  ``dict_pool_shift`` proved the rebuild on the 12-pointer
character dictionaries; this module generalises the same engine to every measured family and to
the pure string pools of the DLC item/skill catalogues (convention C), so a translation longer
than the Japanese original fits everywhere the pool form is used:

    FAMILY                  pointers  ptr_start  record key      measured on
    srwDL_CharaDictionary   12        0          u16 @ +0x40     config00/imenu00-19, all DLC
    srw_DL_RoboDictionary    7        0          u16 @ +28       config00/imenu00-19, all DLC
    srwDL_Reference         10        0          -               config00, config03, imenu*
    srwDL_DLC_ID             8        0          -               config00-19
    srwDL_Shop               2        0          -               config00-19
    srwDL_Skill_Tag          5        8          u32 id @ +0     configst
    srwDL_Achievement        2        0          -               configst

Rebuild rules (all measured, all fail-closed):

* every string of a record sits between its pointer and the next one (the last runs to its NUL);
  bytes before the first pointer (ids, flags) and after the last NUL (padding) are kept verbatim;
* a prefix word that points into the record's own string region without being one of the string
  pointers is an unexplained reference - edits to that record are refused (the guard that
  ``dict_pool_shift`` established; the three CharaDictionary ID words at +0x30..0x3C are exempt);
* the top-level offset table and every record-relative pointer are recomputed, so growth only
  moves bytes inside this member - nothing outside a pool points into it by offset (the exports
  of every other family address these members by record key or by their own offsets);
* an edit-free rebuild must reproduce the input byte for byte, and after an edit the module
  re-parses the result and checks that exactly the requested strings changed.

Convention C (``srwDL_Item01-08``, ``srwDL_Skill01-08`` of the DLC chapters): u32 table start at
+0, the offset table at +8 addresses NUL-terminated strings to EOF; the rebuild recomputes the
table and keeps the count, so only the string bytes move.

Row addressing, matching the package:

* ``04`` offset rows carry the byte offset of the string inside the member; the writer maps it to
  (record, pointer index) and refuses a row whose ``jp`` is not the string found there;
* ``07``/``08`` rows carry the record ``key`` and a ``part``: CharaDictionary
  name/voice_actor/entry/series/nickname -> slots 0/1/2/3/4, RoboDictionary
  length/weight/series -> slots 0/1/3.  The entry slot keeps its ``＠０\\r`` template prefix and
  the nickname slot its ``愛称：`` label when the row's jp is the bare text behind them;
* ``%s`` in a row is the display of one control byte of the original string (the export's
  ``text_of``); the writer puts the i-th control byte back for the i-th ``%s`` of the English and
  refuses a row whose counts differ, so a token can move inside the sentence but never vanish.

Usage::

    python3 tools/table_write.py --container ../google_drive/config00.cpk \
        --package local/translation --out local/patched/config00.cpk
    python3 tools/table_write.py --container ../google_drive/config00.cpk --identity
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP   # noqa: E402
import cpk_write              # noqa: E402
import inline_names as IN     # noqa: E402
import speaker_map as SM      # noqa: E402

PACKAGE_FILES = ("04_config_text.jsonl", "07_names_characters.jsonl", "08_names_units_weapons.jsonl")


class TableError(ValueError):
    """The member does not have the layout its family promises; nothing is written."""


@dataclass(frozen=True)
class Family:
    pointers: int
    ptr_start: int = 0
    key: Optional[Tuple[str, int]] = None       # ("u16", offset) or ("u32", offset)
    exempt: Tuple[Tuple[int, int], ...] = ()    # prefix word ranges that are ids, not references


FAMILY_BY_PREFIX: Dict[str, Family] = {
    "srwDL_CharaDictionary": Family(12, 0, ("u16", 0x40), exempt=((0x30, 0x40),)),
    "srw_DL_RoboDictionary": Family(7, 0, ("u16", 28)),
    "srwDL_Reference": Family(10),
    # DLC_ID record: 8 pointers, then 26 bytes of numbers before the first string at +58 -
    # +32 price (0/2000/3000/4000/5000), +36 running number 45..106 or a packed u16 pair,
    # +40/+44 packed small fields, +48 points (0/50/100/150/200, tracks the price), +52 flags
    # [ZWERYFIKOWANE 2026-10-14, 51 records of DLC_ID00/01]; the running number and the points
    # land inside the string range by arithmetic coincidence (73..106 >= 58), not as pointers
    "srwDL_DLC_ID": Family(8, exempt=((32, 56),)),
    "srwDL_Shop": Family(2),
    "srwDL_Skill_Tag": Family(5, ptr_start=8, key=("u32", 0)),
    "srwDL_Achievement": Family(2),
}

#: 07/08 part -> pointer slot, per family prefix.
PART_SLOT: Dict[str, Dict[str, int]] = {
    "srwDL_CharaDictionary": {"name": 0, "voice_actor": 1, "entry": 2, "series": 3,
                              "nickname": 4},
    "srw_DL_RoboDictionary": {"length": 0, "weight": 1, "series": 3},
}

ENTRY_TEMPLATE = "＠０\r".encode("cp932")
NICKNAME_LABEL = "愛称：".encode("cp932")


def family_of(member: str) -> Optional[Family]:
    for prefix, family in FAMILY_BY_PREFIX.items():
        if member.startswith(prefix):
            return family
    return None


@dataclass
class Record:
    prefix: bytes
    strings: List[bytes]        # without their NUL terminators
    tail: bytes
    pointers: List[int]
    unexplained_refs: List[Tuple[int, int]] = field(default_factory=list)


def _u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def parse_record(rec: bytes, family: Family) -> Record:
    nptr, start0 = family.pointers, family.ptr_start
    if len(rec) < start0 + 4 * nptr:
        raise TableError("record shorter than its pointer table")
    p = [_u32(rec, start0 + 4 * j) for j in range(nptr)]
    if not (start0 + 4 * nptr <= p[0] < len(rec)):
        raise TableError(f"first pointer {p[0]:#x} outside the record")
    if any(p[j] >= p[j + 1] for j in range(nptr - 1)):
        raise TableError("pointers not strictly increasing")
    strings: List[bytes] = []
    tail_start = len(rec)
    for j in range(nptr):
        if j + 1 < nptr:
            end = p[j + 1]
            if rec[end - 1:end] != b"\x00":
                raise TableError(f"string {j} not NUL-terminated at its boundary")
            body = rec[p[j]:end - 1]
        else:
            nul = rec.find(b"\x00", p[j])
            if nul < 0:
                raise TableError("last string has no NUL terminator")
            body = rec[p[j]:nul]
            tail_start = nul + 1
        if b"\x00" in body:
            raise TableError(f"string {j} contains an embedded NUL")
        strings.append(body)
    unexplained: List[Tuple[int, int]] = []
    for off in range(start0 + 4 * nptr, p[0] - 3, 4):
        if any(low <= off < high for low, high in family.exempt):
            continue
        value = _u32(rec, off)
        if p[0] <= value < tail_start and value not in p:
            unexplained.append((off, value))
    return Record(prefix=rec[:p[0]], strings=strings, tail=rec[tail_start:], pointers=p,
                  unexplained_refs=unexplained)


def record_spans(b: bytes) -> List[Tuple[int, int]]:
    if len(b) < 4:
        raise TableError("pool too short")
    n = _u32(b, 0)
    if n == 0 and len(b) == 4:
        return []
    if not (0 < n < 20000) or 4 + 4 * n > len(b):
        raise TableError("implausible record count")
    offs = [_u32(b, 4 + 4 * i) for i in range(n)]
    if offs[0] != 4 + 4 * n or any(offs[i] >= offs[i + 1] for i in range(n - 1)):
        raise TableError("record offset table not monotonic from 4+4n")
    if offs[-1] >= len(b):
        raise TableError("last record offset beyond the pool")
    return list(zip(offs, offs[1:] + [len(b)]))


def parse_pool(b: bytes, family: Family) -> List[Record]:
    return [parse_record(b[s:e], family) for s, e in record_spans(b)]


def rebuild_pool(b: bytes, family: Family,
                 edits: Optional[Dict[Tuple[int, int], bytes]] = None) -> bytes:
    """A new pool with ``{(record, slot): bytes}`` replaced; edit-free means byte-identical."""
    records = parse_pool(b, family)
    by_rec: Dict[int, Dict[int, bytes]] = {}
    for (r, s), v in (edits or {}).items():
        if not (0 <= r < len(records)) or not (0 <= s < family.pointers):
            raise TableError(f"edit index out of range: {(r, s)}")
        if records[r].unexplained_refs:
            raise TableError(f"record {r} has unexplained in-record references; refusing edit")
        by_rec.setdefault(r, {})[s] = v
    new_recs = []
    for i, rec in enumerate(records):
        strings = list(rec.strings)
        for s, v in by_rec.get(i, {}).items():
            strings[s] = v
        prefix = bytearray(rec.prefix)
        pos = len(prefix)
        body = bytearray()
        ptrs = []
        for text in strings:
            if b"\x00" in text:
                raise TableError("string contains NUL")
            ptrs.append(pos + len(body))
            body += text + b"\x00"
        for j, value in enumerate(ptrs):
            struct.pack_into("<I", prefix, family.ptr_start + 4 * j, value)
        new_recs.append(bytes(prefix) + bytes(body) + rec.tail)
    head = bytearray(4 + 4 * len(new_recs))
    struct.pack_into("<I", head, 0, len(new_recs))
    pos = len(head)
    for i, r in enumerate(new_recs):
        struct.pack_into("<I", head, 4 + 4 * i, pos)
        pos += len(r)
    return bytes(head) + b"".join(new_recs)


# --------------------------------------------------------------------------- convention C

def parse_pool_c(b: bytes) -> Tuple[List[int], List[bytes]]:
    """(offsets, strings-without-NUL) of a convention-C member (pure string pool)."""
    if len(b) < 12:
        raise TableError("member too short for a convention-C header")
    table_start = _u32(b, 0)
    if table_start < 8 or table_start % 4 or table_start + 4 > len(b) \
            or struct.unpack_from("<I", b, 4)[0] != 0:
        raise TableError("not a convention-C header")
    table_end = _u32(b, table_start)
    if table_end <= table_start or (table_end - table_start) % 4 or table_end > len(b):
        raise TableError("convention-C table does not describe the file")
    count = (table_end - table_start) // 4
    offs = list(struct.unpack_from("<%dI" % count, b, table_start))
    if offs[0] != table_end or any(offs[i] > offs[i + 1] for i in range(count - 1)):
        raise TableError("convention-C offsets not monotonic from the table end")
    strings = []
    for i, off in enumerate(offs):
        end = offs[i + 1] if i + 1 < count else len(b)
        seg = b[off:end]
        nul = seg.find(b"\x00")
        if nul < 0:
            raise TableError(f"pool string {i} has no NUL terminator")
        strings.append(seg[:nul])
    return offs, strings


def rebuild_pool_c(b: bytes, edits: Optional[Dict[int, bytes]] = None) -> bytes:
    offs, strings = parse_pool_c(b)
    for i, text in (edits or {}).items():
        if b"\x00" in text:
            raise TableError("string contains NUL")
        strings[i] = text
    table_start = _u32(b, 0)
    count = len(strings)
    # the count never changes, so the pool keeps its header, the table position and the offset
    # of the first string; only the table cells and the string bytes are rewritten
    out = bytearray(b[:table_start])
    new_offs, pos = [], table_start + 4 * count
    for text in strings:
        new_offs.append(pos)
        pos += len(text) + 1
    out += b"".join(struct.pack("<I", o) for o in new_offs)
    out += b"".join(text + b"\x00" for text in strings)
    return bytes(out)


# --------------------------------------------------------------------------- text plumbing

CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def display(raw: bytes) -> str:
    """The package's jp display of a string: control bytes as ``%s``, 0x0A as a line break.

    Mirrors ``text_runs_export.text_of`` for the byte shapes the pools actually hold, so a row's
    ``jp`` can be compared with the member byte by byte without re-exporting the package.
    """
    out: List[str] = []
    i = 0
    while i < len(raw):
        byte = raw[i]
        if byte == 0x0A:
            out.append("\n")
            i += 1
            continue
        if byte < 0x20 or byte == 0x7F:
            out.append("%s")
            i += 1
            continue
        if (0x81 <= byte <= 0x9F or 0xE0 <= byte <= 0xFC) and i + 1 < len(raw):
            try:
                out.append(raw[i:i + 2].decode("cp932"))
                i += 2
                continue
            except UnicodeDecodeError:
                return ""
        try:
            out.append(raw[i:i + 1].decode("cp932"))
        except UnicodeDecodeError:
            return ""
        i += 1
    return "".join(out)


def token_kinds(original: bytes) -> List[object]:
    """What every ``%s`` of the display form stands for, in order.

    The pools hold two things that display as ``%s``: a control byte (a runtime token such as
    0x0F) and the literal ASCII ``%s`` the game's own formatter substitutes (both measured inside
    the same skill fields).  The walk of the original tells them apart, so the writer knows which
    tokens the English must keep (literals and functional controls) and which it must drop (the
    0x0F kana glyphs - see :func:`encode_target`).
    """
    kinds: List[object] = []
    i = 0
    while i < len(original):
        byte = original[i]
        if (byte < 0x20 and byte != 0x0A) or byte == 0x7F:
            kinds.append(byte)
            i += 1
            continue
        if original[i:i + 2] == b"%s":
            kinds.append(b"%s")
            i += 2
            continue
        i += 2 if (0x81 <= byte <= 0x9F or 0xE0 <= byte <= 0xFC) and i + 1 < len(original) else 1
    return kinds


#: the lead byte of the voiced-kana glyph token ``0x0F xx`` (xx always 0x20-0x39 in this game,
#: verified across the whole package): one Japanese glyph with no place in an English line
KANA_TOKEN = 0x0F


def encode_target(en: str, original: bytes) -> bytes:
    """CP932 bytes of a display-form translation: every kept ``%s`` restored to what it stands for.

    The display form shows two things as ``%s``: the game formatter's literal ``%s`` and a control
    token.  The English must carry every literal placeholder and every functional control token
    (a ``\r`` clearing the box, for instance), in order, but must NEVER carry the kana tokens
    ``0x0F xx`` - they draw one voiced kana glyph in the middle of the English text, so English
    drops them (translation_check refuses 0x0F in English, and raw-form rows drop them the same
    way).  A dropped token leaves no trace, so the English ``%s`` count must equal the kept-token
    count exactly and anything else is refused; nothing is guessed from the surrounding text,
    because a literal ``%s2`` and a kana token ``%s2`` are indistinguishable by eye (measured:
    the glyph's second byte is a digit, a space or punctuation as often as a symbol).
    """
    kinds = token_kinds(original)
    kept = [kind for kind in kinds if kind == b"%s" or kind != KANA_TOKEN]
    dropped = len(kinds) - len(kept)
    pieces = en.split("%s")
    if len(pieces) - 1 != len(kept):
        detail = ""
        if dropped:
            detail = (f"; the other {dropped} of the jp's %s are kana tokens (0x0F) - drop them "
                      "from the English together with the character after them")
        raise TableError(f"the translation has {len(pieces) - 1} %s but the original string "
                         f"carries {len(kept)} tokens the English must keep{detail}")
    out = bytearray()
    for i, piece in enumerate(pieces):
        try:
            out += piece.replace("\n", "\x0a").encode("cp932")
        except UnicodeEncodeError as exc:
            raise TableError(f"target is not CP932-encodable: {exc}") from exc
        if i < len(kept):
            kind = kept[i]
            out += bytes([kind]) if isinstance(kind, int) else kind
    return bytes(out)


def match_form(jp: Optional[str], original: bytes) -> Optional[str]:
    """Which package form a row's ``jp`` is in: the file's own or the display with ``%s``.

    The structured exports keep control bytes as the characters themselves (a ``\x0f`` voiced
    kana token reads back as ``\x0f``), the leftover scan displays every control byte as ``%s``;
    the game's literal ``%s`` formatter placeholders appear in both forms identically.  Trying
    the raw reading first and the display second tells the writer which encoding the English
    needs, and a jp that matches neither is stale and refuses the row.
    """
    if jp is None:
        return None
    if original.decode("cp932", "replace") == jp:
        return "raw"
    if display(original) == jp:
        return "display"
    return None


def english(row: dict) -> str:
    """The row's English exactly as written, or ``""`` when it is blank (untranslated).

    The writers used to ``strip()`` the English.  That silently dropped what the package check
    had just insisted on - a trailing ``\\n`` matching the jp - and the leading/trailing spaces
    that centre a mission title (``　　 サブミッション　　``), indent a sysmes line or align a
    skill column (`` Lv``).  Whitespace is the translator's; only an all-whitespace cell means
    "not translated" (the event and quote writers never stripped).
    """
    en = row.get("en") or ""
    return en if en.strip() else ""


def encode_en(en: str, original: bytes, form: str) -> bytes:
    """The bytes to store for a translation validated against ``original`` in ``form``."""
    if form == "raw":
        try:
            return en.replace("\n", "\x0a").encode("cp932")
        except UnicodeEncodeError as exc:
            raise TableError(f"target is not CP932-encodable: {exc}") from exc
    return encode_target(en, original)


def keyed_target(part: str, en: str, original: bytes, family_member: str) -> bytes:
    """Slot bytes for a key+part row: template/label prefixes stay, the text behind them changes."""
    text = encode_target(en, original)
    if part == "entry" and original.startswith(ENTRY_TEMPLATE):
        return ENTRY_TEMPLATE + text
    if part == "nickname" and original.startswith(NICKNAME_LABEL) \
            and family_member.startswith("srwDL_CharaDictionary"):
        return NICKNAME_LABEL + text
    return text


# --------------------------------------------------------------------------- rows -> edits

def member_matches(row_member: Optional[str], sub_name: str) -> bool:
    """A row targets a member by full name, or the 08 robonote rows by bare family prefix."""
    if not row_member:
        return False
    if row_member == sub_name:
        return True
    return (row_member in FAMILY_BY_PREFIX and "." not in row_member
            and sub_name.startswith(row_member))


def record_key(blob: bytes, span: Tuple[int, int], family: Family) -> Optional[int]:
    if family.key is None:
        return None
    kind, off = family.key
    start, end = span
    size = 2 if kind == "u16" else 4
    if end - start < off + size:
        return None
    return int.from_bytes(blob[start + off:start + off + size], "little")


def resolve_rows(blob: bytes, sub_name: str, rows: Iterable[dict]) -> Tuple[dict, List[str]]:
    """Turn package rows into edits for one pool member.  Returns (plan, problems).

    ``plan`` is ``{"convention": "A"|"C", "edits": {(record, slot) | (index,): bytes},
    "resolved": [...], "refused": [...]}`` - ``resolved`` records the physical target of every
    accepted row so the orchestrator can deduplicate double coverage (04 offset rows and 07/08
    key rows can name the same string); ``refused`` lists the row-level skips (foreign keyspace,
    stale jp, resolved conflicts) that do not poison the member.  ``problems`` stays reserved
    for member-fatal structural failures.
    """
    rows = [r for r in rows if member_matches((r.get("source") or {}).get("member"), sub_name)]
    problems: List[str] = []
    family = family_of(sub_name)
    if family is not None:
        spans = record_spans(blob)
        records = parse_pool(blob, family)
        by_offset: Dict[int, Tuple[int, int]] = {}
        ranges: List[Tuple[int, int, int, int]] = []      # (start, end, record, slot)
        for i, (rec, span) in enumerate(zip(records, spans)):
            for j, ptr in enumerate(rec.pointers):
                start = span[0] + ptr
                by_offset[start] = (i, j)
                ranges.append((start, start + len(rec.strings[j]) + 1, i, j))
        ranges.sort()
        keyed: Dict[Optional[int], List[int]] = {}
        for i, span in enumerate(spans):
            keyed.setdefault(record_key(blob, span, family), []).append(i)
        edits: Dict[Tuple[int, int], bytes] = {}
        resolved: List[tuple] = []
        refused: List[str] = []
        for row in rows:
            en = english(row)
            if not en:
                continue                      # partial package: the string stays Japanese
            source = row.get("source") or {}
            targets = resolve_one(row, en, blob, spans, records, by_offset, keyed, family,
                                  sub_name, refused, ranges)
            for (i, j), value in targets:
                if records[i].unexplained_refs:
                    # the rebuild guard would refuse the whole member for this one record;
                    # refuse the row here so the other records still get their text
                    refused.append(f"{row.get('id')}: record {i} has unexplained in-record "
                                   f"references (offsets {records[i].unexplained_refs[:3]}); "
                                   f"left as is")
                    continue
                resolved.append((sub_name, i, j, row.get("id")))
                if (i, j) in edits and edits[(i, j)] != value:
                    refused.append(
                        f"{row.get('id')}: conflicts with another row targeting record "
                        f"{i} slot {j}; keeping the row whose jp covers the whole string")
                    if not row.get("key"):
                        edits[(i, j)] = value  # offset rows carry the full labeled string
                    continue
                edits[(i, j)] = value
        return {"convention": "A", "edits": edits, "resolved": resolved, "member": sub_name,
                "records": len(records), "refused": refused}, problems
    # convention C?
    try:
        offs, strings = parse_pool_c(blob)
    except TableError:
        if rows:
            problems.append(f"{sub_name}: no pool writer for this member "
                            f"({len(rows)} rows skipped)")
        return {"convention": None, "edits": {}, "resolved": [], "records": 0,
                "member": sub_name}, problems
    by_offset = {off: i for i, off in enumerate(offs)}
    edits_c: Dict[int, bytes] = {}
    dead: set = set()          # pool strings refused for conflicting rows
    resolved = []
    refused = []
    for row in rows:
        en = english(row)
        if not en:
            continue
        source = row.get("source") or {}
        offset = source.get("offset")
        index = by_offset.get(offset) if isinstance(offset, int) else None
        if index is None and isinstance(offset, int):
            # the leftover scan can point into the middle of a string: take the string that
            # contains the offset (its jp still has to match, so a wrong hit is refused)
            for i2, off2 in enumerate(offs):
                if off2 > offset:
                    break
                if off2 <= offset < off2 + len(strings[i2]) + 1:
                    index = i2
                    break
        if index is None:
            refused.append(f"{row.get('id')}: offset {offset} is not a pool string start")
            continue
        if index in dead:
            refused.append(f"{row.get('id')}: pool string {index} is already refused "
                           f"(conflicting rows)")
            continue
        form = match_form(row.get("jp"), strings[index])
        if form is None:
            refused.append(f"{row.get('id')}: jp does not match the string at {offset}")
            continue
        try:
            value = encode_en(en, strings[index], form)
        except TableError as exc:
            refused.append(f"{row.get('id')}: {exc}")
            continue
        previous = edits_c.get(index)
        if previous is not None and previous != value:
            # two offset rows, one string, two translations: a package bug - refuse the string
            refused.append(f"{row.get('id')}: conflicts with another row targeting pool "
                           f"string {index}; the string is refused")
            edits_c.pop(index)
            dead.add(index)
            continue
        if previous is None:
            resolved.append((sub_name, index, None, row.get("id")))
        edits_c[index] = value
    return {"convention": "C", "edits": edits_c, "resolved": resolved, "member": sub_name,
            "records": len(strings), "refused": refused}, problems


def resolve_one(row: dict, en: str, blob: bytes, spans, records, by_offset, keyed,
                family: Family, sub_name: str, refused: List[str],
                ranges: Optional[List[Tuple[int, int, int, int]]] = None) -> List[tuple]:
    """[((record, slot), bytes)] for one row; empty when it is skipped or refused.

    Every skip lands in ``refused`` - a row-level note.  Rows that do not belong to this
    member's keyspace (the 07/08 broadcast) or whose jp went stale refuse themselves without
    poisoning the rest of the member; only structural failures (parse/verify) are problems.
    """
    source = row.get("source") or {}
    if row.get("category") == "config_item_drop":
        refused.append(f"{row.get('id')}: ItemDrop rows are binary noise; skipped")
        return []
    if row.get("key") is not None and family.key is not None \
            and row.get("part") in PART_SLOT.get(sub_name_prefix(sub_name), {}):
        slot = PART_SLOT[sub_name_prefix(sub_name)][row["part"]]
        matches = keyed.get(int(row["key"]), [])
        if not matches:
            refused.append(f"{row.get('id')}: no record with key {row['key']}")
            return []
        out = []
        for i in matches:
            original = records[i].strings[slot]
            prefix = template_prefix(row["part"], original, sub_name)
            form = match_form(row.get("jp"), original[len(prefix):])
            if form is None:
                refused.append(f"{row.get('id')}: jp does not match record {i} slot {slot}")
                return []
            try:
                value = prefix + encode_en(en, original[len(prefix):], form)
            except TableError as exc:
                refused.append(f"{row.get('id')}: {exc}")
                return []
            out.append(((i, slot), value))
        return out
    offset = source.get("offset")
    ij = by_offset.get(offset) if isinstance(offset, int) else None
    if ij is None and isinstance(offset, int):
        # the leftover scan can point into the middle of a string: take the string that
        # contains the offset (its jp still has to match, so a wrong hit is refused)
        for start, end, ri, rj in (ranges or ()):
            if start > offset:
                break
            if start <= offset < end:
                ij = (ri, rj)
                break
    if ij is None:
        refused.append(f"{row.get('id')}: offset {offset} is not a string start of this pool")
        return []
    i, j = ij
    original = records[i].strings[j]
    form = match_form(row.get("jp"), original)
    if form is None:
        refused.append(f"{row.get('id')}: jp does not match the string at {offset}")
        return []
    try:
        value = encode_en(en, original, form)
    except TableError as exc:
        refused.append(f"{row.get('id')}: {exc}")
        return []
    return [((i, j), value)]


def sub_name_prefix(sub_name: str) -> str:
    for prefix in FAMILY_BY_PREFIX:
        if sub_name.startswith(prefix):
            return prefix
    return sub_name


def template_prefix(part: str, original: bytes, sub_name: str) -> bytes:
    if part == "entry" and original.startswith(ENTRY_TEMPLATE):
        return ENTRY_TEMPLATE
    if part == "nickname" and sub_name.startswith("srwDL_CharaDictionary") \
            and original.startswith(NICKNAME_LABEL):
        return NICKNAME_LABEL
    return b""


# --------------------------------------------------------------------------- rebuild + verify

def apply_member(blob: bytes, sub_name: str, rows: Iterable[dict]) -> Tuple[bytes, dict]:
    """Rebuild one pool member with the translations of its rows.  Returns (bytes, report)."""
    plan, problems = resolve_rows(blob, sub_name, rows)
    report = {"member": sub_name, "convention": plan["convention"], "records": plan["records"],
              "edits": len(plan["edits"]), "resolved": plan["resolved"],
              "problems": problems, "refused": plan.get("refused", []), "skipped_empty": 0}
    if plan["convention"] is None or not plan["edits"]:
        return blob, report
    family = family_of(sub_name)
    if plan["convention"] == "A":
        modified = rebuild_pool(blob, family, plan["edits"])
    else:
        modified = rebuild_pool_c(blob, plan["edits"])
    report["problems"] += verify_member(blob, modified, plan)
    report["bytes"] = len(modified) - len(blob)
    if report["problems"]:
        return blob, report
    return modified, report


def verify_member(original: bytes, modified: bytes, plan: dict) -> List[str]:
    """Re-parse the result: same record count, only the requested strings changed."""
    problems: List[str] = []
    if plan["convention"] == "C":
        offs_a, strings_a = parse_pool_c(original)
        offs_c, strings_c = parse_pool_c(modified)
        if len(strings_a) != len(strings_c):
            return ["convention-C string count changed"]
        for i, (before, after) in enumerate(zip(strings_a, strings_c)):
            want = plan["edits"].get(i, before)
            if after != want:
                problems.append(f"pool string {i}: unexpected text after the rebuild")
        return problems
    family = family_of(plan["member"])
    spans_a = record_spans(original)
    before = parse_pool(original, family)
    after = parse_pool(modified, family)
    if len(before) != len(after):
        return ["record count changed"]
    for i, (ra, rc) in enumerate(zip(before, after)):
        keep = bytearray(ra.prefix)
        for j in range(family.pointers):
            struct.pack_into("<I", keep, family.ptr_start + 4 * j, 0)
        kept = bytearray(rc.prefix)
        for j in range(family.pointers):
            struct.pack_into("<I", kept, family.ptr_start + 4 * j, 0)
        if bytes(keep) != bytes(kept):
            problems.append(f"record {i}: non-pointer prefix bytes changed")
        if ra.tail != rc.tail:
            problems.append(f"record {i}: tail changed")
        for j in range(family.pointers):
            want = plan["edits"].get((i, j), ra.strings[j])
            if rc.strings[j] != want:
                problems.append(f"record {i} slot {j}: unexpected text after the rebuild")
    return problems


# --------------------------------------------------------------------------- container level

def rows_for_container(package: Path, container: str) -> List[dict]:
    rows: List[dict] = []
    for name in PACKAGE_FILES:
        path = Path(package) / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            source = row.get("source") or {}
            if source.get("container") not in (container, None):
                continue
            if not (row.get("en") or "").strip():
                continue
            rows.append(row)
    return rows


def apply_container(src: Path, dst: Path, rows: List[dict], dry_run: bool = False) -> dict:
    """Rebuild the container with every translated pool member, chained through ``dst``."""
    summary = {"container": src.name, "members": 0, "edits": 0, "applied": 0, "refused": 0,
               "problems": [], "per_member": {}, "written": None, "dry_run": dry_run,
               "resolved": []}
    current = src
    produced = False
    cpk = cpk_write.load(src)
    for member in cpk.members:
        targets: List[Tuple[str, bytes]] = []
        if member.name.lower().endswith(".pac"):
            pac = CSP.parse_pac(cpk_write.decompressed(member.blob))
            changed = False
            for sub in pac["subs"]:
                blob, report = _apply_sub(sub["name"], sub["data"], rows, summary)
                if report is None:
                    continue
                if report["problems"] or not report["edits"]:
                    continue
                sub["data"] = blob
                changed = True
            if changed:
                targets.append((member.name, CSP.rebuild_pac(pac)))
        else:
            blob, report = _apply_sub(member.name, cpk_write.decompressed(member.blob),
                                      rows, summary)
            if report is not None and not report["problems"] and report["edits"]:
                targets.append((member.name, blob))
        for name, blob in targets:
            if dry_run:
                continue
            cpk_now = cpk_write.load(current)
            out = cpk_write.rebuild(cpk_now, (name, blob))
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(out)
            produced = True
            current = dst
    if produced and not dry_run:
        summary["written"] = str(dst)
        summary["container_bytes"] = dst.stat().st_size - src.stat().st_size
    return summary


def _apply_sub(sub_name: str, data: bytes, rows: List[dict], summary: dict):
    """Apply rows to one (sub)member when a pool writer owns it; feed the summary.

    A member whose rebuild raises (e.g. the unexplained-in-record-references guard) is
    refused on its own - the rest of the container still gets its edits.
    """
    mine = [r for r in rows if member_matches((r.get("source") or {}).get("member"), sub_name)]
    if not mine:
        return None, None
    if family_of(sub_name) is None:
        try:
            parse_pool_c(data)
        except TableError:
            summary["problems"].append(f"{sub_name}: {len(mine)} rows but no pool writer")
            return None, None
    try:
        modified, report = apply_member(data, sub_name, mine)
    except TableError as exc:
        summary["problems"].append(f"{sub_name}: {exc}")
        return None, None
    summary["members"] += 1
    summary["edits"] += report["edits"]
    summary["resolved"] += report["resolved"]
    summary["refused"] += len(report["refused"])
    if report["edits"] and not report["problems"]:
        summary["applied"] += report["edits"]   # the orchestrator reads this key
    for message in report["problems"]:
        summary["problems"].append(f"{sub_name}: {message}")
    for message in report["refused"][:8]:
        summary["problems"].append(f"{sub_name}: refused: {message}")
    summary["per_member"][sub_name] = {k: report[k] for k in
                                       ("convention", "records", "edits", "problems")}
    summary["per_member"][sub_name]["refused"] = len(report["refused"])
    return modified, report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--identity", action="store_true",
                        help="rebuild every pool member unchanged and compare")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.identity:
        failures = []
        checked = 0
        for name, blob in SM.read_members(args.container):
            subs = list(IN.pac_subfiles(blob)) if name.lower().endswith(".pac") else [(name, blob)]
            for sub_name, data in subs:
                family = family_of(sub_name)
                try:
                    if family is not None:
                        checked += 1
                        if rebuild_pool(data, family) != data:
                            failures.append(f"{name}/{sub_name}: A-pool identity differs")
                    else:
                        parse_pool_c(data)
                        checked += 1
                        if rebuild_pool_c(data) != data:
                            failures.append(f"{name}/{sub_name}: C-pool identity differs")
                except TableError:
                    continue
        for line in failures:
            print("FAIL " + line)
        print(f"identity: {checked - len(failures)}/{checked} pools rebuild byte-identically")
        return 1 if failures else 0

    rows = rows_for_container(args.package, args.container.name)
    if not args.out and not args.dry_run:
        parser.error("--out is needed unless --identity or --dry-run is given")
    summary = apply_container(args.container, args.out or args.container, rows,
                              dry_run=args.dry_run)
    summary["resolved"] = len(summary["resolved"])
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 1 if summary["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
