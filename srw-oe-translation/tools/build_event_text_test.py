#!/usr/bin/env python3
"""Build the two eventP02.EDAT test variants on the machine that has the game files.

Why this is a script and not a download
---------------------------------------
The modified containers are game data, so they are not committed to this
repository, and the agent's workspace does not survive between sessions -- a
built archive kept there is gone by the next turn. What does survive is this
script, which rebuilds both variants from the user's own decrypted
``eventP02.EDAT`` in a few seconds and then checks the result against the MD5s
recorded when they were first built. If the hashes match, the file on the user's
disk is byte for byte the file that was verified here.

What it builds
--------------
Both variants grow the same record: the opening narration of event 2.0, inside
member ``DL105_50.bin`` (TOC entry 0), record at byte 184, text at byte 196. The
original text is 118 bytes of CP932 including two ``0x0A`` line breaks.

* ``01-jp/eventP02.EDAT`` -- one extra Japanese line in front. Same charset as
  the original, so it isolates the container mechanics from font coverage.
* ``02-en/eventP02.EDAT`` -- an English translation, 118 -> 148 bytes. This also
  shows whether the font has Latin glyphs at all.

The changed member is written stored (``FileSize == ExtractSize``) because this
repository has a CRILAYLA decompressor and no compressor -- the same as leaving
"Force Compress" unchecked, which is what the working Korean patch did.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Optional, Sequence

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_write  # noqa: E402
import grow_event_text  # noqa: E402

MEMBER = "DL105_50.bin"
BREAK = "\n"

# The original line, exactly as stored: three lines joined by 0x0A.
ORIGINAL = (
    "コロニー格闘技、その覇者たる証…" + BREAK +
    "キング・オブ・ハートの紋章を右手に持つ" + BREAK +
    "ガンダムファイター、その名はドモン・カッシュ。"
)

VARIANTS = (
    (
        "01-jp",
        "japoński, jedna linia więcej (ta sama gra znaków co oryginał)",
        "これは長いテキストのテストです。" + BREAK + ORIGINAL,
        "14e0d138084a4080e4a3617b63aaf3e5",
    ),
    (
        "02-en",
        "angielskie tłumaczenie (testuje też łacińskie glify)",
        "Colony martial arts, the proof of its champion..." + BREAK +
        "The Gundam Fighter who bears the King of Heart emblem in his right hand," + BREAK +
        "his name is Domon Kasshu.",
        "91118db85ae22752194ce48963dfb89d",
    ),
)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def build(container: Path, out_dir: Path) -> int:
    """Build every variant and report how each one compares to the recorded hash."""
    original = container.read_bytes()
    print(f"source : {container}  ({len(original)} bytes, MD5 {md5(original)})")

    cpk = cpk_write.load(container)
    member = next((m for m in cpk.members if m.name == MEMBER), None)
    if member is None:
        print(f"REFUSED: {container.name} has no member named {MEMBER!r}", file=sys.stderr)
        return 1
    if member.extract_size > member.file_size:
        import crilayla

        blob = crilayla.decompress(member.blob).data
        if len(blob) != member.extract_size:
            print(
                f"REFUSED: {MEMBER} decompressed to {len(blob)} bytes, the TOC says "
                f"{member.extract_size}",
                file=sys.stderr,
            )
            return 1
    else:
        blob = member.blob
    print(f"member : {MEMBER}  ({len(blob)} bytes)")

    needle = ORIGINAL.encode("cp932")
    record_offset = grow_event_text.find_record(blob, needle)
    stored = grow_event_text.record_text(blob, record_offset)
    if stored != needle:
        print(
            f"REFUSED: the record at {record_offset} holds {len(stored)} bytes, expected the "
            f"{len(needle)}-byte line",
            file=sys.stderr,
        )
        return 1
    print(f"record : at byte {record_offset}, text {len(stored)} bytes\n")

    failures = 0
    for folder, description, replacement, expected in VARIANTS:
        new_text = replacement.encode("cp932")
        grown = grow_event_text.grow_record(blob, record_offset, new_text)
        problems = grow_event_text.check(blob, grown, record_offset, new_text)
        if problems:
            for problem in problems:
                print(f"REFUSED ({folder}): {problem}", file=sys.stderr)
            failures += 1
            continue

        out = out_dir / folder / "eventP02.EDAT"
        out.parent.mkdir(parents=True, exist_ok=True)
        image = cpk_write.rebuild(cpk, (MEMBER, grown))
        out.write_bytes(image)

        actual = md5(image)
        verdict = "matches the recorded build" if actual == expected else "DIFFERS from the recorded build"
        if actual != expected:
            failures += 1
        print(f"{folder}/eventP02.EDAT  {len(image)} bytes  {description}")
        print(f"    text {len(stored)} -> {len(new_text)} bytes")
        print(f"    MD5 {actual}  {verdict}")
        if actual != expected:
            print(f"    recorded: {expected}")
        print()

    if failures:
        print(f"{failures} variant(s) did not reproduce the recorded build", file=sys.stderr)
        return 1
    print(f"Both variants reproduced. Put them in memstick/PSP/GAME/NPJH50521/eventP02.EDAT,")
    print(f"one at a time, Japanese first -- keep a copy of the original before overwriting.")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build the eventP02.EDAT length-test variants.")
    parser.add_argument("container", type=Path, help="the decrypted eventP02.EDAT")
    parser.add_argument(
        "-o", "--out-dir", type=Path, default=Path("srw-oe-test-eventP02"),
        help="where to write the variants (default: srw-oe-test-eventP02)",
    )
    args = parser.parse_args(argv)
    if not args.container.is_file():
        print(f"no such file: {args.container}", file=sys.stderr)
        return 1
    return build(args.container, args.out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
