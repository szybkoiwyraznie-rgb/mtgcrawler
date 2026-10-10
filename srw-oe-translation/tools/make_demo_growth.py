"""Produce a *grown* eventP00.cpk for the ISO patch boot test (FAZA 2).

This is a process demo, not a translation: it lengthens ONE narration record in
DL100_01.bin so the resulting eventP00.cpk is larger than the original, then the
user patches it into the ISO with `iso_pack.py patchiso` and boots it. If it boots,
edit -> repack -> patchiso -> boot with growth is proven on a real UMD.

Usage:
    python tools/make_demo_growth.py <eventP00.cpk> <output.cpk>
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
EXTRA = "（成長テスト：この行は意図的に伸ばされています）"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        raise SystemExit("usage: make_demo_growth.py <eventP00.cpk> <output.cpk>")
    src = Path(argv[0])
    out = Path(argv[1])

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

    off = g.find_record(blob, NEEDLE.encode("cp932"))
    old = g.record_text(blob, off)
    new = old + EXTRA.encode("cp932")
    grown = g.grow_record(blob, off, new)
    problems = g.check(blob, grown, off, new)
    if problems:
        for p in problems:
            print("REFUSED:", p, file=sys.stderr)
        return 1

    out_bytes = cpk_write.replace_appended(cpk, MEMBER, grown)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(out_bytes)
    print(f"{src.name}: {MEMBER} record text {len(old)} -> {len(new)} bytes")
    print(f"  cpk {len(cpk.data)} -> {len(out_bytes)} bytes (+{len(out_bytes) - len(cpk.data)})")
    print(f"  before: {g._decode(old)}")
    print(f"  after : {g._decode(new)}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
