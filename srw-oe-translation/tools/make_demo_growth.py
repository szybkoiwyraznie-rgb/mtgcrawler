"""Produce a modified eventP00.cpk for the ISO patch boot test (FAZA 2).

Process demo, not a translation. By default it lengthens ONE narration record in
DL100_01.bin; with `--control` the member is decompressed and stored back UNCHANGED,
isolating the cpk writer from the growth. `--method` selects the cpk write strategy:
`rebuild` keeps the member inside the content region (shifts followers, updates
ContentSize); `append` tacks it on at the end (repointing only its TOC row). The game's
CRI reader only resolves members inside the content region, so `rebuild` is the one a
real PPSSPP can load.

Usage:
    python tools/make_demo_growth.py <eventP00.cpk> <output.cpk> [--control] [--method rebuild|append]
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
    method = "rebuild"
    if "--method" in args:
        i = args.index("--method")
        method = args[i + 1]
        del args[i:i + 2]
    if method not in ("rebuild", "append"):
        raise SystemExit("--method must be rebuild or append")
    if len(args) != 2:
        raise SystemExit("usage: make_demo_growth.py <eventP00.cpk> <output.cpk> [--control] [--method rebuild|append]")
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

    if method == "rebuild":
        out_bytes = cpk_write.rebuild(cpk, (MEMBER, newblob))
    else:
        out_bytes = cpk_write.replace_appended(cpk, MEMBER, newblob)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(out_bytes)
    print(f"  method {method}: cpk {len(cpk.data)} -> {len(out_bytes)} bytes (+{len(out_bytes) - len(cpk.data)})")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
