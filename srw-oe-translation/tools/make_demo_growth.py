"""Produce a modified eventP00.cpk for the ISO patch boot test (FAZA 2).

Process demo, not a translation. By default it lengthens ONE narration record in
DL100_01.bin (so the cpk is larger than the original) and writes the result with the
surgical cpk swap; the user then patches it into the ISO with `iso_pack.py patchiso`.

With `--control` the member is decompressed and stored back UNCHANGED (same content,
stored instead of CRILAYLA). That isolates the cpk write path from the growth: if the
control build boots, the writer is fine and any crash of the grown build is the growth;
if the control build crashes, the cpk writer itself is wrong.

Usage:
    python tools/make_demo_growth.py <eventP00.cpk> <output.cpk> [--control]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_write
import grow_event_text as g

MEMBER = "DL100_01.bin"
NEEDLE = "地球統一政府である地球連邦の樹立から数十年。"
EXTRA = " GROWTH TEST: THIS LINE IS NOW LONGER AND IN ENGLISH."


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    control = "--control" in args
    args = [a for a in args if a != "--control"]
    if len(args) != 2:
        raise SystemExit("usage: make_demo_growth.py <eventP00.cpk> <output.cpk> [--control]")
    src = Path(args[0])
    out = Path(args[1])

    cpk = cpk_write.load(src)
    member = next((m for m in cpk.members if m.name == MEMBER), None)
    if member is None:
        raise SystemExit(f"{MEMBER} not in {src.name}")
    blob = member.blob
    if member.extract_size > member.file_size:
        import crilayla
        blob = crilayla.decompress(blob).data
        if len(blob) != member.extract_size:
            raise SystemExit(f"{MEMBER}: decompressed to {len(blob)}, TOC says {member.extract_size}")

    if control:
        newblob = blob
        print(f"{src.name}: CONTROL (member stored unchanged, {len(blob)} bytes)")
    else:
        off = g.find_record(blob, NEEDLE.encode("cp932"))
        old = g.record_text(blob, off)
        new = old + EXTRA.encode("cp932")
        newblob = g.grow_record(blob, off, new)
        problems = g.check(blob, newblob, off, new)
        if problems:
            for p in problems:
                print("REFUSED:", p, file=sys.stderr)
            return 1
        print(f"{src.name}: {MEMBER} record text {len(old)} -> {len(new)} bytes")
        print(f"  before: {g._decode(old)}")
        print(f"  after : {g._decode(new)}")

    out_bytes = cpk_write.replace_appended(cpk, MEMBER, newblob)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(out_bytes)
    print(f"  cpk {len(cpk.data)} -> {len(out_bytes)} bytes (+{len(out_bytes) - len(cpk.data)})")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
