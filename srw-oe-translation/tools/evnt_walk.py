#!/usr/bin/env python3
"""Framing of the SRW OE ``EVNT`` containers (read-only, no game text is written here).

Two measured variants of the same block format live in this game (2026-10-12) [ZWERYFIKOWANE]:

**mesbtl variant** (battle quotes, ``p<NNN>.pac`` members)::

    'EVNT'           4-byte ASCII tag
    u32 block_size   counted from the *size field*: the block ends at tag+4+size
    u32 zero         payload starts with one zero word
    record...        u32 type, u32 size (counted from the *type* field)
                     type 200 (0xC8) wraps, type 201 (0xC9) is a text record

**event variant** (story scenes, ``DL*`` / ``SM*`` members of eventP*/evept*)::

    'EDAT'           optional file header (present in every event member measured)
    u32 file_size    counted from this field
    u32 block_count  number of EVNT blocks that follow
    'EVNT' u32 block_size
                     counted from the *tag*: the block ends at tag+8+size
    u32 block_kind   1 / 2 - the payload marker (never 0)
    'ECHK' u32 size  a 24-byte check chunk, then a few more u32 header words
    record...        same record framing; the chain lands exactly on the block end

The block-end rule differs per variant, so :func:`blocks` decides it per block by matching the
offset of the next ``EVNT`` tag (or end of file) - a variant guess is never silent.  The record
chain inside a block is found by scanning the first :data:`CHAIN_SCAN` bytes of the payload for
the first start whose chain lands exactly on the block end; that is what makes the event variant
readable (its header words are not records).

Text record payload (both variants) = 6 u16 words then a CP932 NUL-terminated string::

    u16 anchor       **battle quotes only**: 0x0029 with a flag nibble in the top bits
                     (0x8029 occurs), mask 0x0FFF.  Story dialogue puts its own flag word here
                     (measured 0x0001/0x0009/0x0011/0x0019), which is why the anchor check is
                     optional in this module.
    u16 speaker_key  character key of the speaker
    u16 flags        observed 0/1/3/4/7/8/9/20..27
    u16 0
    u16 0
    u16 extra        voice/asset id, 0xFFFF when absent
    text             CP932, NUL-terminated

Usage (library)::

    import evnt_walk
    result = evnt_walk.text_records(blob, "eventP00.cpk", "DL100_01.bin")
    result["records"]   # every type-201 record: key, text, offsets, header words
    result["types"]     # record-type histogram of the whole member
    result["errors"]    # framing problems, never swallowed
"""
from __future__ import annotations

import struct
import unicodedata
from typing import Dict, List, Optional, Tuple

TAG = b"EVNT"
FILE_HEADER = b"EDAT"
TYPE_WRAPPER = 0xC8
TYPE_TEXT = 0xC9
ANCHOR_MASK = 0x0FFF
ANCHOR_EXPECTED = 0x0029
TEXT_HEADER = 12           # 6 u16 words in front of the text
CHAIN_SCAN = 64            # bytes of payload scanned for the first sane record chain


def is_clean(text: str) -> bool:
    """Reject private-use and control characters; keep tab/newline/CR."""
    for ch in text:
        code = ord(ch)
        if unicodedata.category(ch) == "Co":
            return False
        if code < 0x20 and ch not in "\t\n\r":
            return False
        if code == 0x7F:
            return False
    return True


def file_header(blob: bytes) -> Optional[dict]:
    """The ``EDAT`` file header of an event member, or None when the member has none."""
    if blob[:4] != FILE_HEADER or len(blob) < 12:
        return None
    size, count = struct.unpack_from("<2I", blob, 4)
    return {"size": size, "blocks": count, "start": 12}


def _chain_lands(blob: bytes, start: int, block_end: int) -> bool:
    """True when the record chain from ``start`` lands exactly on ``block_end``."""
    pos = start
    while pos + 8 <= block_end:
        _t, size = struct.unpack_from("<II", blob, pos)
        if size < 8 or pos + size > block_end:
            return False
        pos += size
    return pos == block_end


def _candidate_chain(blob: bytes, start: int, block_end: int) -> Optional[int]:
    """Number of records when the chain from ``start`` lands exactly on ``block_end``, else None.

    Record sizes are always a multiple of four and types fit a ``u16`` (measured across every
    event member); both tests drop starts that only *look* like a chain because of a size word
    in the header.
    """
    pos = start
    count = 0
    while pos + 8 <= block_end:
        rtype, size = struct.unpack_from("<II", blob, pos)
        if size < 8 or size % 4 or rtype > 0xFFFF or pos + size > block_end:
            return None
        count += 1
        pos += size
    return count if pos == block_end else None


def find_chain(blob: bytes, payload_start: int, block_end: int) -> Optional[int]:
    """Start of the record chain in a block payload, or None.

    Measured 2026-10-12 [ZWERYFIKOWANE]: the chain does **not** begin within the first few dozen
    bytes of the payload.  The event variant carries a header between the block start and the first
    record whose length grows with the block (index tables: 36 bytes in the first block of
    ``DL830_13.bin``, 76 and 96 bytes in its later blocks), so the old 64-byte :data:`CHAIN_SCAN`
    window found no chain in 60 of that member's 65 blocks and every record inside them was lost.
    The scan now covers the whole payload.

    The chain is the **outermost wrapper**: its first record has type :data:`TYPE_WRAPPER`, and the
    block's other records follow inside it.  Measured over every event container: each of the 5,211
    event blocks has such a start, and a start inside it (the wrapped chain, first type ``0x12C``)
    also lands on the block end with *more* records -- picking that one by a record count loses the
    wrapper, whose size field has to grow with the text.  So the earliest start whose first record
    is a wrapper wins; when a block has no wrapper, the earliest start that lands on the block end
    does.  Both tests are strict: record sizes are a multiple of four and types fit a ``u16``
    (measured across every member), which drops starts that only *look* like a chain because of a
    size word in the header (``DL623_11.bin``, ``DL726_12.bin`` would otherwise start on a record
    type of 4,294,965,863).

    A leading zero word is the mesbtl payload marker: the measured ``u32 0`` + ``u32 0xC8`` pair
    parses as a type-0 record whose size eats the whole block, which hides every quote it wraps.
    So a zero first word forces the start one word later (checked, not assumed).
    """
    if len(blob) >= payload_start + 4 and struct.unpack_from("<I", blob, payload_start)[0] == 0 \
            and _chain_lands(blob, payload_start + 4, block_end):
        return payload_start + 4
    first_landing: Optional[int] = None
    for start in range(payload_start, block_end, 4):
        count = _candidate_chain(blob, start, block_end)
        if count is None:
            continue
        if first_landing is None:
            first_landing = start
        if struct.unpack_from("<I", blob, start)[0] == TYPE_WRAPPER:
            return start
    return first_landing


def blocks(blob: bytes) -> Tuple[List[dict], List[str]]:
    """Every ``EVNT`` block of a member. Returns (blocks, errors).

    Each block dict: ``tag``, ``size``, ``end``, ``payload_start``, ``chain_start`` (may be None),
    ``variant`` ('mesbtl' when the payload starts with a zero word, else 'event').
    """
    out: List[dict] = []
    errors: List[str] = []
    offsets = []
    pos = 0
    while True:
        i = blob.find(TAG, pos)
        if i < 0:
            break
        offsets.append(i)
        pos = i + 4
    for idx, tag_pos in enumerate(offsets):
        if tag_pos + 8 > len(blob):
            errors.append(f"block tag at {tag_pos} runs past EOF")
            break
        size = struct.unpack_from("<I", blob, tag_pos + 4)[0]
        next_tag = offsets[idx + 1] if idx + 1 < len(offsets) else len(blob)
        candidates = {"event": tag_pos + 8 + size, "mesbtl": tag_pos + 4 + size}
        match = [name for name, end in candidates.items() if end == next_tag]
        payload_start = tag_pos + 8
        if not match:
            errors.append(f"block at {tag_pos}: size {size} lands on {sorted(candidates.values())}, "
                          f"next EVNT tag at {next_tag}")
            # keep going with the event rule, clamped, so later blocks stay readable
            end = min(candidates["event"], len(blob))
            variant = "event"
        else:
            variant = match[0]
            end = candidates[variant]
        zero_word = len(blob) >= payload_start + 4 and \
            struct.unpack_from("<I", blob, payload_start)[0] == 0
        chain_start = find_chain(blob, payload_start, end)
        if chain_start is None:
            errors.append(f"block at {tag_pos}: no record chain lands on block end {end}")
        out.append({"tag": tag_pos, "size": size, "end": end, "payload_start": payload_start,
                    "chain_start": chain_start,
                    "variant": "mesbtl" if (variant == "mesbtl" or zero_word) else "event"})
    return out, errors


def walk_chain(blob: bytes, start: int, end: int) -> List[Tuple[int, int, int]]:
    """Records of one chain: list of (offset, type, size). Empty when the chain is not clean."""
    out: List[Tuple[int, int, int]] = []
    pos = start
    while pos + 8 <= end:
        rtype, size = struct.unpack_from("<II", blob, pos)
        if size < 8 or pos + size > end:
            return []
        out.append((pos, rtype, size))
        pos += size
    return out if pos == end else []


def payload_text(payload: bytes, anchor: Optional[int] = None) -> Optional[dict]:
    """Decode a type-201 payload (see the module docstring), or None when it is not one.

    ``anchor`` (e.g. :data:`ANCHOR_EXPECTED`) adds the battle-quote subtype test; story dialogue
    uses its own flag word there, so pass None for events.
    """
    if len(payload) < TEXT_HEADER:
        return None
    words = struct.unpack_from("<6H", payload, 0)
    if anchor is not None and words[0] & ANCHOR_MASK != anchor:
        return None
    raw = payload[TEXT_HEADER:].split(b"\x00", 1)[0]
    try:
        text = raw.decode("cp932")
    except UnicodeDecodeError:
        return None
    if not is_clean(text):
        return None
    return {"anchor": words[0], "key": words[1], "flags": words[2], "extra": words[5],
            "header": list(words), "raw": raw, "text": text}


def _collect(blob: bytes, start: int, end: int, records: List[dict], errors: List[str],
             where: str, anchor: Optional[int] = None) -> None:
    for offset, rtype, size in walk_chain(blob, start, end):
        payload_start = offset + 8
        if rtype == TYPE_WRAPPER:
            _collect(blob, payload_start, offset + size, records, errors, where, anchor)
            continue
        if rtype != TYPE_TEXT:
            continue
        parsed = payload_text(blob[payload_start:offset + size], anchor)
        if parsed is None:
            errors.append(f"{where}: type-201 record at {offset} is not decodable")
            continue
        records.append({
            "record_offset": offset, "record_size": size,
            "text_offset": payload_start + TEXT_HEADER,
            "key": parsed["key"], "anchor": parsed["anchor"], "flags": parsed["flags"],
            "extra": parsed["extra"], "header": parsed["header"],
            "text": parsed["text"], "bytes": len(parsed["raw"]),
        })


def _count_types(blob: bytes, start: int, end: int, types: Dict[int, int]) -> None:
    """Count every record type, descending into the wrappers (the histogram covers them all)."""
    for offset, rtype, size in walk_chain(blob, start, end):
        types[rtype] = types.get(rtype, 0) + 1
        if rtype == TYPE_WRAPPER:
            _count_types(blob, offset + 8, offset + size, types)


def text_records(blob: bytes, container: str = "", member: str = "",
                 anchor: Optional[int] = None) -> dict:
    """Every type-201 record of a member plus the framing report.

    ``anchor`` selects the battle-quote subtype test (see :func:`payload_text`).
    """
    where = f"{container}:{member}".strip(":")
    records: List[dict] = []
    errors: List[str] = []
    types: Dict[int, int] = {}
    chain_blocks = 0
    block_list, block_errors = blocks(blob)
    for block in block_list:
        if block["chain_start"] is None:
            continue
        chain_blocks += 1
        _count_types(blob, block["chain_start"], block["end"], types)
        _collect(blob, block["chain_start"], block["end"], records, errors, where, anchor)
    return {"header": file_header(blob), "blocks": len(block_list), "chain_blocks": chain_blocks,
            "records": records, "types": types, "errors": errors + block_errors}
