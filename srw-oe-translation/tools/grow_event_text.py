#!/usr/bin/env python3
"""Grow one text record inside an SRW OE event member (a decrypted EDAT body).

The member format, measured on the real files rather than assumed
----------------------------------------------------------------
::

    "EDAT"  u32 size (= file size - 8)  u32 section_count
    section_count x ( magic[4]  u32 body_size  body )      # first section at byte 12

The section walk lands exactly on end-of-file for every file checked.  Inside an
``EVNT`` body the event commands are self-sizing records, and the narration
records (type ``b7 01 00 00``) chain end to end: each holds ``u32 type``, ``u32
length``, ``u32 parameter``, the text, then a ``00 00`` terminator, with
``length`` counting the whole record -- ``length == 12 + len(text) + 2``.  On the
file measured here the chain runs 184 -> 316 -> 460 -> 540 -> 632 -> 676, each
step exactly the previous record's length.

So these files are *walked*, not indexed: no pointer table points at a string,
which is why growing one is safe.  Growing a record means rewriting its length
and its enclosing section's body size and the ``EDAT`` size, and shifting the
bytes that follow.  Nothing needs repointing.

Text inside a record uses ``0x0A`` as an explicit line break, which is why a
string captured from a memory monitor does not appear in the file as one
contiguous run: the monitor shows the breaks rendered, the file stores them.

``--check`` re-parses the result and fails unless the section walk still lands on
end-of-file, the record chain still walks from the same start, and the text reads
back as exactly what was asked for.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

RECORD_TYPE = bytes.fromhex("b7010000")
HEADER_OVERHEAD = 12   # type + length + parameter
TERMINATOR = b"\x00\x00"
RECORD_OVERHEAD = HEADER_OVERHEAD + len(TERMINATOR)
BREAK = b"\x0a"


def parse_edat(data: bytes) -> Tuple[int, List[Tuple[int, int, int]]]:
    """Return (declared size, [(magic_offset, body_start, body_size), ...]).

    Raises if the header does not describe the file, or if walking the sections
    does not land exactly on end-of-file -- a member whose layout this cannot
    account for is not written.
    """
    if data[:4] != b"EDAT":
        raise ValueError(f"not an EDAT member ({data[:4]!r})")
    declared, count = struct.unpack_from("<II", data, 4)
    if declared != len(data) - 8:
        raise ValueError(f"header size {declared} but the file is {len(data) - 8} bytes past it")
    sections = []
    pos = 12
    for _ in range(count):
        if pos + 8 > len(data):
            raise ValueError(f"section header runs past the end at {pos}")
        body_size = struct.unpack_from("<I", data, pos + 4)[0]
        sections.append((pos, pos + 8, body_size))
        pos += 8 + body_size
    if pos != len(data):
        raise ValueError(f"section walk ends at {pos}, file is {len(data)} bytes")
    return declared, sections


def find_record(data: bytes, needle: bytes, start: int = 0) -> int:
    """Return the offset of the narration record whose text contains `needle`."""
    hits = []
    cursor = start
    while True:
        cursor = data.find(needle, cursor)
        if cursor < 0:
            break
        hits.append(cursor)
        cursor += 1
    if not hits:
        raise ValueError("the text to replace was not found in this member")
    if len(hits) > 1:
        raise ValueError(f"the text occurs {len(hits)} times; refusing to guess which one to change")
    at = hits[0]
    # Walk back over the record header to its type field.
    record_offset = data.rfind(RECORD_TYPE, 0, at)
    if record_offset < 0:
        raise ValueError(f"no narration record header before the text at {at}")
    length = struct.unpack_from("<I", data, record_offset + 4)[0]
    text_start = record_offset + HEADER_OVERHEAD
    if not record_offset <= at < text_start + (length - RECORD_OVERHEAD):
        raise ValueError(
            f"the text at {at} is not inside the record at {record_offset} "
            f"(text {text_start}..{text_start + length - RECORD_OVERHEAD})"
        )
    return record_offset


def record_text(data: bytes, record_offset: int) -> bytes:
    length = struct.unpack_from("<I", data, record_offset + 4)[0]
    if length < RECORD_OVERHEAD:
        raise ValueError(f"record at {record_offset} declares length {length}, too small for a record")
    end = record_offset + length
    if data[end - len(TERMINATOR):end] != TERMINATOR:
        raise ValueError(f"record at {record_offset} is not terminated by 00 00")
    return data[record_offset + HEADER_OVERHEAD:end - len(TERMINATOR)]


def grow_record(data: bytes, record_offset: int, new_text: bytes) -> bytes:
    """Return the member with one record's text replaced by a longer one."""
    old_length = struct.unpack_from("<I", data, record_offset + 4)[0]
    old_text_length = old_length - RECORD_OVERHEAD
    if old_text_length < 0:
        raise ValueError(f"record at {record_offset} declares length {old_length}, too small for a record")
    text_start = record_offset + HEADER_OVERHEAD
    text_end = text_start + old_text_length

    out = bytearray(data)
    out[text_start:text_end] = new_text
    delta = len(new_text) - old_text_length
    struct.pack_into("<I", out, record_offset + 4, len(new_text) + RECORD_OVERHEAD)

    # The EDAT size and the one section holding the text both grow by the change.
    _declared, sections = parse_edat(data)
    owner = [s for s in sections if s[1] <= record_offset < s[1] + s[2]]
    if len(owner) != 1:
        raise ValueError(f"the record at {record_offset} is inside {len(owner)} sections, expected 1")
    struct.pack_into("<I", out, 4, struct.unpack_from("<I", out, 4)[0] + delta)
    struct.pack_into("<I", out, owner[0][0] + 4, owner[0][2] + delta)
    return bytes(out)


def check(original: bytes, modified: bytes, record_offset: int, new_text: bytes) -> List[str]:
    """Re-parse the result and report what holds and what does not."""
    problems: List[str] = []
    try:
        _declared, sections = parse_edat(modified)
    except ValueError as error:
        return [f"the modified member no longer parses: {error}"]

    _before, before_sections = parse_edat(original)
    if len(sections) != len(before_sections):
        problems.append(f"section count changed from {len(before_sections)} to {len(sections)}")

    delta = len(modified) - len(original)
    try:
        if record_text(modified, record_offset) != new_text:
            problems.append("the record does not read back as the requested text")
    except ValueError as error:
        problems.append(f"the record does not re-parse: {error}")

    # The record chain must still walk from the same start to the same end.
    def chain(data: bytes, start: int) -> List[int]:
        positions = []
        pos = start
        while pos + HEADER_OVERHEAD <= len(data):
            if data[pos:pos + 4] != RECORD_TYPE:
                break
            length = struct.unpack_from("<I", data, pos + 4)[0]
            if length < RECORD_OVERHEAD:
                break
            positions.append(pos)
            pos += length
        return positions

    before, after = chain(original, record_offset), chain(modified, record_offset)
    if len(before) != len(after):
        problems.append(f"the record chain walks {len(before)} records before, {len(after)} after")
    if after[:1] != [record_offset]:
        problems.append(f"the chain no longer starts at {record_offset}")

    # Every byte outside the edited record must be untouched.
    old_length = struct.unpack_from("<I", original, record_offset + 4)[0]
    tail_original = original[record_offset + old_length:]
    new_length = struct.unpack_from("<I", modified, record_offset + 4)[0]
    tail_modified = modified[record_offset + new_length:]
    if tail_original != tail_modified:
        problems.append("the bytes after the edited record changed")
    # Stop before the record's own length field, which is meant to change.
    head_limit = record_offset + 4
    head_original = bytearray(original[:head_limit])
    head_modified = bytearray(modified[:head_limit])
    # Two further size fields legitimately change: the EDAT size at 4, and the
    # body size of the one section holding the record. Blank those before
    # comparing so the check still catches anything else that moved.
    allowed = [range(4, 8)]
    owner = [s for s in before_sections if s[1] <= record_offset < s[1] + s[2]]
    if owner:
        allowed.append(range(owner[0][0] + 4, owner[0][0] + 8))
    for span in allowed:
        for at in span:
            if at < head_limit:
                head_original[at] = 0
                head_modified[at] = 0
    if bytes(head_original) != bytes(head_modified):
        problems.append("the bytes before the edited record changed")
    if len(owner) != 1:
        problems.append(f"the record sits inside {len(owner)} sections, expected 1")
    else:
        new_body = struct.unpack_from("<I", modified, owner[0][0] + 4)[0]
        if new_body != owner[0][2] + delta:
            problems.append(
                f"the owning section's body size is {new_body}, expected {owner[0][2] + delta}"
            )
    if delta != len(new_text) - (old_length - RECORD_OVERHEAD):
        problems.append(f"the file grew by {delta} but the text by {len(new_text) - (old_length - RECORD_OVERHEAD)}")
    return problems


def _decode(text: bytes) -> str:
    """Decode CP932 for a report line, showing line breaks as they are stored."""
    return text.decode("cp932", "replace").replace("\n", "\\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Grow one text record in an event member.")
    parser.add_argument("member", type=Path, help="the extracted .bin member")
    parser.add_argument("--find", required=True, help="CP932 text identifying the record (use \\n for 0x0A breaks)")
    parser.add_argument("--replace", required=True, help="new text, same escaping")
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)

    def unescape(value: str) -> bytes:
        return value.replace("\\n", "\n").encode("cp932")

    data = args.member.read_bytes()
    needle = unescape(args.find)
    new_text = unescape(args.replace)

    record_offset = find_record(data, needle)
    old_text = record_text(data, record_offset)
    modified = grow_record(data, record_offset, new_text)

    problems = check(data, modified, record_offset, new_text)
    if problems:
        for problem in problems:
            print(f"REFUSED: {problem}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(modified)
    print(f"{args.member.name}: record at {record_offset}")
    print(f"  text {len(old_text)} -> {len(new_text)} bytes, file {len(data)} -> {len(modified)} ({len(modified) - len(data):+d})")
    print(f"  before: {_decode(old_text)}")
    print(f"  after : {_decode(new_text)}")
    print(f"  checks: section walk lands on EOF, record chain intact, {len(modified) - len(data)} bytes added, tail unchanged")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
