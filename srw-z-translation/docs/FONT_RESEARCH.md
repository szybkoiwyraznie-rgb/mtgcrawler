# Polish font — research and design (2026-10-24)

**Owner decision (2026-10-24, supersedes "font route after the
prototype"):** fonts are the **first** work track, and the target is the
ambitious route — Polish glyphs at **normal English (half-width) metrics**,
drawn on the English letterforms with added diacritics (the SRW OE v5
approach). Fullwidth is **not** a shipping fallback.

## Verified on the owner's ELF

`SLPS_258.87` SHA-256
`6c4c81c4e5aa3db1f52d70b8183ce11c01fc6b265ae4d53fa4d6a657c5019b50`
(3,471,624 B, Drive `1p4ek8vUsC5ukrHWeZSopO6ehhWEo1q4y`, kept in ignored
`local/inputs/`). `readelf` confirms the upstream mapping (single code
PT_LOAD: vaddr `0x00100000`, file offset `0x1A80`, filesz `0x34BC80`), and
**all five renderer landmarks from `RENDERER.md` match byte-for-byte**:

| vaddr | file off | word | meaning |
|---|---|---|---|
| `0x22137C` | `0x122DFC` | `0x28410080` | layout: `slti at,v0,0x80` (ASCII = half cell) |
| `0x13A390` | `0x3BE10` | `0x92820000` | blit: `lbu v0,(s4)` (read text byte) |
| `0x13A608` | `0x3C088` | `0x00441025` | form 2-byte SJIS code |
| `0x13A6C0` | `0x3C140` | `0x3401827A` | fullwidth A–Z bound `0x827A` |
| `0x13A6F8` | `0x3C178` | `0x340182F2` | fullwidth lower/digit bound `0x82F2` |

Lead-byte jump table at `0x433E30` reads
`13A7D8 13A7F8 13A818 13A838 13A898 13A898 13A858 13A878` — banks
`0x81..0x88` as documented. The upstream renderer/font research therefore
applies to the owner's edition; what remains unproven is runtime behavior,
which only owner PCSX2 evidence can settle.

## Substrate: upstream half-width font v2 (master-font stamping)

Vendored in batch 2 (`patch_renderer.py`, `patch_hwfont.py`, `patch.py`;
see `vendor/retro-trans/PROVENANCE.md`). How it works:

- The game decodes glyphs into a **master font in RAM**: linear 24×24
  4 bpp cells, 288 B each, base pointer at `0x46E3A8` (stock `0x9AE610`);
  `cell(code) = base + ((lead-0x81)*192 + trail-0x40) * 288`. Cells are
  demand-decoded on first display, so stamps can be overwritten — the
  stamper runs per glyph and heals.
- `patch_renderer.py` hooks `setText` (`0x20C9B0`) and converts ASCII in
  the message buffer; `patch_hwfont.py` maps ASCII to **private
  half-width SJIS codes `0x8540..`** (`HW_MAP`: `."'!,-?`, digits, A–Z,
  a–z = 69 arts; regular + bold = 138 codes, `..0x85C9`) and **stamps
  12-px letterforms into those master-font cells** (12×16 art at cell
  rows 8..23). Blit/advance hooks (`BHOOK`, `SADV`, `FHOOK2`, `MHOOK`,
  `ADV2`) give 12 px draw/advance instead of the fullwidth cell.
  Letterforms upstream: BIZ UDGothic Regular rendered at 12 px
  (CHANGELOG). No VRAM atlas, no DMA.

Doc conflict to resolve by testing, not by reading: `CUSTOM_FONT.md`
(OUTCOME 2026-08-12) says the deliverable stayed fullwidth over a
two-pen ghost + word-wrap, while the pinned `patch_hwfont.py` v2 and
later CHANGELOG entries (0.9.57+, width-measure fixes) describe the
half-width system as shipped and iterated. We adopt it as
**adopt-and-verify**: baseline English hwfont build first, judged on the
owner's PCSX2 v2.9.144.

## Polish extension design

- **Glyphs:** 18 letters (Ą Ć Ę Ł Ń Ó Ś Ź Ż + lowercase) × regular/bold.
  Bodies = the same Latin arts (identical metrics to English); diacritics
  drawn in-cell. Pixel risks to inspect in the prototype: ogonek (ą ę)
  needs descender room below the baseline, acute accents (ć ń ó ś ź)
  above x-height/cap height, Ł stroke. Our stamper may use more of the
  24-row cell than rows 8..23; master baseline is ~row 21.
- **Codes:** extend the private range after `0x85C9`. Owner-copy
  inventory (119,837 extracted STAGE rows): SJIS lead bytes `0x84`,
  `0x85`, `0x86` occur **0 times** — 54 free codes in `0x85CA..0x85FF`
  alone, and whole banks behind them. Reserve 36 codes (18×2) plus a few
  Polish typographic extras („ ” – — … ×) to decide. Other surfaces
  (SRVC/COMPDATA/ELF) get the same inventory in phase 2 before codes are
  frozen.
- **Text encoding:** translator files keep real Unicode (ą, ę, …). Our
  apply-side encoder maps Polish letters to the private SJIS codes
  (2 B/char, 12 px display; slot/relocation is the pipeline's existing
  machinery). A single-byte private encoding remapped by the hook (as
  upstream does for ASCII) is the byte-cheaper alternative — decided at
  prototype time from measured slot pressure.
- **Do not repurpose printable specials** (`%$^&*`…): unnecessary given
  private codes, and unsafe — `$` is the placeholder prefix (6,396× in
  the script: `$n` 4,398, `$c` 912, `$Y` 738, `$v` 115, `$F` 72…), and
  fullwidth `％` (35×) / `＆` (10×) are real text. `%` is also needed by
  Polish UI text itself.
- **Metrics:** Polish = 1 half-width column, same advance as English;
  our rewrap/cols counting must treat private codes accordingly
  (dialogue box 3 × 34 columns, fullwidth = 2).

## Prototype sequence

- **P1 (sandbox):** build the unmodified upstream renderer+hwfont ELF
  patch on a copy of the owner's ELF (English baseline); byte-diff
  report only.
- **P2 (sandbox):** Polish atlas extension (36 glyphs) + encoder for one
  sample record: pangram dialogue covering every Polish letter, both
  cases, with placeholders intact; inject via the proven STAGE
  sparse-image pipeline.
- **P3 (owner):** `PATCH.bat` test build writing a **new** ISO (patched
  ELF + STAGE extents); owner screenshots in PCSX2: dialogue box, menu
  (bold path), name plate. Judged on: ghosting, wrap, ogonek/acute
  legibility at native res, spacing vs English.
- **P4:** fix/extend hooks per evidence (measure paths, menu encoding in
  COMPDATA is a separate surface), then freeze code assignments in this
  document.

## Proven in the sandbox already (2026-10-24)

Sparse virtual image with the owner's `stage.bin` (SHA-256
`9c56d42f96df7b409ccf468b24412322ed627b9cbbd656864818a404d89240dc`) at
offset 1651029×2048: unmodified vendored `extract_script.py` →
**119,837 rows** (95,627 with Japanese, 24,210 Latin-only; JSON
15,778,893 B, kept in `local/`); `apply_script.py --write` of the
unchanged JSON → 119,837 unchanged / 0 to write / 0 rejected, extent
**byte-identical**; `verify_pointers.py` virgin baseline: 205 records,
131,976 pointers, 121,382 (91.97%) on a string start. A *changed-row*
write test is part of P2. No runtime claims anywhere yet.

## Progress: P1–P3 built in the sandbox (2026-10-24)

- **Atlas** (`tools/gen_pl_atlas.py`, DejaVu Sans em 20, baseline row 20,
  supersample 4×, 4 alpha levels): 87 glyphs × 72 B = 6,264 B, SHA-256
  `38ec24bd…44202` (69-glyph baseline slice `17d68def…a4add`). Polish ink:
  capitals with acute rows 1..20, ogonek letters (Ą Ę ą ę) descend to
  row 23 — no clipping. Assignments frozen-for-prototype in
  `tools/pl_font_codes.json`. Known cosmetics to tune after screenshots:
  DejaVu renders heavy; descenders sit near the cell bottom.
- **Space solution:** the cave segment patch_renderer appends is 6,320 B
  (file bytes at `0x34D770` = the ELF section-header table, disposable),
  heap moved to `0x78CD00` (gap 12,288 B). `tools/patch_hwfont_pl.py`
  (fork-by-import of the vendored patcher) extends that PT_LOAD to
  8,192 B (file end `0x34F770` ≤ EOF `0x34F908`; vaddr end `0x78C070` <
  heap `0x78CD00`), sets NART=87/NGLYPH=174 and points the setText table
  entries of 18 reserved ASCII bytes (`@ # & * + < = > [ \ ] ^ _ \` { | } ~`)
  at the Polish regular codes `0x8585..0x8596`.
- **P1 (unmodified vendor tools on the owner's ELF):** same file size,
  e_phnum 209→210, 3,847 diff bytes confined to phdr/heap args, the four
  hook sites and the cave file region. PL ELF vs P1: only 879 further
  diff bytes (PT_LOAD fields, hook immediates, table entries, Polish
  atlas tail); total vs original 4,680 B; PL ELF SHA-256 `7bfc9a20…b7ba`.
- **P2 (sample injection):** row idx 632 (rec 0, off 129008, slot 112 B;
  speaker Henken kept), body replaced by the reserved-byte encoding of
  "Zażółć gęślą jaźń! / ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż" (105→51 B): apply wrote
  1 row / 0 rejected, re-extraction reproduces the intended text exactly,
  `verify_pointers` 121,383/131,977 (91.97%). Extent diff 54,538 B in one
  range `0xD..0xD85F` (record recompression, expected); sample stage
  SHA-256 `c1ca930e…cc63`.
- **P3 (owner kit):** `kit/` + `tools/build_test_kit.py` →
  `srwz-pl-font-test-p3.zip` (14 members, 43,748 B, SHA-256
  `7040ca98…38a4`), sandbox-tested end-to-end on a combined virtual
  image: extent hashes reproduce the references exactly. Delivered to
  Drive `SRWZ` as file `1PMiZXRKJWvL9z0ETRGq-3lpENPvhJRAN`. The patcher
  aborts unless the source ISO extents hash to the recorded values and
  only ever writes a `*_PLTEST` copy. **Awaiting owner PCSX2
  screenshots — still no runtime claim.**
