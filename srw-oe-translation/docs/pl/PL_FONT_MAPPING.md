# PL font: renderer mapping correction (2026-10-18)

## Confirmed by static executable analysis, not yet by PPSSPP

Private owner input: Japanese 1.08 disc-side `EBOOT.BIN`, 5,531,024 bytes,
plain ELF. `font.cpk` SHA-256
`a986115e793e4c0b69ec803650d1f7052909e6d6bb60cc09abffb72b1f49bed6`.
EBOOT SHA-256 `26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`.
Only tools/findings are committed; originals and disassembly stay ignored.

The ELF has segment 0 at file offset 0xA0, relative address zero. The glyph
lookup starts at relative 0xDC090 (runtime 0x088E0090 with base 0x08804000).
The ordinary single-byte branch is at relative 0xDC1F8, file 0xDC298:

- compare code with 0xA0;
- for code < 0xA0: subtract 0x20 (branch-likely delay slot);
- otherwise: subtract **0x40**, not 0x20;
- load bitmap base from object +0x24;
- multiply index by 64 minus index times 8 = **56 bytes**;
- return bitmap base plus this offset.

Thus `0xD5` (PL `ą`) selects physical cell **149**, not 181. The previous writer
and verifier shared the same wrong formula, so their agreement did not prove
that the game would read the modified cell. The correction changes both, with
an additional independent test of physical byte slices and preservation of all
other cells. ASCII stays unchanged; cells 160–191 stay untouched.

The 0x0F-prefixed special-code branch uses a different formula (low byte +0x80).
That is not the ordinary katakana path and is not changed by this correction.
No executable instructions, lookup tables, codecs or English text are patched.

## Owner interaction rule

Do as much analysis/read-back as possible without the owner. If runtime evidence
is needed, put labelled character/spacing/case probes directly at the start of
mission 0-0 in **one** kit. Do not ask the owner to hunt for katakana in menus or
rebuild an ISO for each hypothesis. Screenshots can be inspected by the agent;
file-level checks are not a substitute for actual PPSSPP rendering confirmation.

## Initial checkpoint checks

`python -m unittest discover -s srw-oe-translation/tests -p test_font_pl.py`:
13 tests OK, including raw physical offsets and unchanged-cell checks.
A standalone re-check of the executable mapping and a batch opening-scene kit
are the next coherent work chunk. No new runtime result is claimed.

## Second correction: paired-pixel order

An offline preview made from the actual patched ISO compared the original ASCII
cells and PL cells under both nibble orders. Original ASCII (`acelnoszz ACELNOSZZ`)
is coherent with **low nibble = left pixel**, high nibble = right pixel; the old
high-first interpretation swaps every adjacent pixel pair. The old PL rasterizer
packed high-first, so the former verifier again agreed with the writer while
using a wrong image interpretation. This explains another source of malformed
marks; it is bitmap evidence, not a claim that v3 has run in PPSSPP.

The corrected packer/reader use low-first. A regression pins `[1,2,3,4,5,6,7,8]`
to raw `21 43 65 87` bytes, and the independent ISO verifier packs the JSON art
itself rather than calling the font writer's packing/index helpers. Original
ASCII bitmap bytes remain unchanged. The local preview is derived game data and
is not committed or included in the kit.

## Delivery and completed checks

[TEST_PL v3](https://drive.google.com/file/d/16mPAOMpab8aSFbuqv1LSxMWyStEQmn_K/view)
is delivered; [manifest](test-v3-delivery.json). The read-only MIPS probe and batch
kit listed in the initial checkpoint are now implemented and tested. Final suite:
1553 unittest tests OK (25 skipped). The delivered ZIP's isolated CLI build and
independent read-back pass using original containers in an ISO fixture. A corrupt
glyph is detected. First-panel PPSSPP screenshot remains pending, not a blocker
requiring the owner to investigate the technical mapping.
