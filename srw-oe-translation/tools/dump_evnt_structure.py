"""Dump the EVNT structure of the first event member (DL100_01.bin) of eventP00.cpk.

Read-only diagnostic. Prints the section list, the narration record offsets, and every
u32 word in the owner section header that precedes the first narration record, tagging
words that look like forward offsets to a record (absolute or section-relative). Paste the
output back so the growth fix can update the right table.

Usage:
    python tools/dump_evnt_structure.py <eventP00.cpk>
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import struct

import cpk_write
import grow_event_text as g

MEMBER = "DL100_01.bin"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit("usage: dump_evnt_structure.py <eventP00.cpk>")
    cpk = cpk_write.load(Path(argv[0]))
    member = next((m for m in cpk.members if m.name == MEMBER), None)
    if member is None:
        raise SystemExit(f"{MEMBER} not in {cpk.path.name}")
    blob = member.blob
    if member.extract_size > member.file_size:
        import crilayla
        blob = crilayla.decompress(blob).data

    declared, sections = g.parse_edat(blob)
    print(f"member {MEMBER}: {len(blob)} bytes, declared {declared}, sections {len(sections)}")
    for s_off, s_body, s_size in sections:
        print(f"  section off={s_off} body={s_body} size={s_size} end={s_body + s_size}")

    # narration record offsets (walk RECORD_TYPE chain)
    recs = []
    pos = 0
    while True:
        i = blob.find(g.RECORD_TYPE, pos)
        if i < 0:
            break
        try:
            length = struct.unpack_from("<I", blob, i + 4)[0]
            if length < g.RECORD_OVERHEAD or i + length > len(blob):
                pos = i + 1
                continue
            recs.append(i)
            pos = i + length
        except Exception:
            pos = i + 1
    print("narration records:", recs)

    if not recs:
        return 0
    first = recs[0]
    owner = [s for s in sections if s[1] <= first < s[1] + s[2]]
    if not owner:
        print("no owner section for first record")
        return 1
    s_off, s_body, s_size = owner[0]
    s_end = s_body + s_size
    print(f"owner section off={s_off} body={s_body} end={s_end}; first record at {first}")
    print("u32 words from section body to first record:")
    for off in range(s_body, first, 4):
        v = struct.unpack_from("<I", blob, off)[0]
        tag = ""
        if v in recs:
            tag = "ABS record offset"
        elif s_off + v in recs or s_body + v in recs:
            tag = "REL record offset"
        elif s_body <= v < s_end or off + v <= s_end:
            tag = "in-section value"
        print(f"  @{off:#06x} = {v}  {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
