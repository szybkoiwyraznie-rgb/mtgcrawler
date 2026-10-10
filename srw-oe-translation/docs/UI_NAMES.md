# UI / names / menus — reverse-engineering notes (started 2026-10-10)

The story script (event `EVNT` records) is solved and exportable (`export_strings.py`). This
file records the *separate* track for UI text, character/robot names and menus: what each
candidate container actually holds, why the generic CPK writer refuses some of them, and the
next hypotheses. Everything below was observed from the disc (`SRW_OE_1.08`, unpacked on
Drive) and the DLC.

## Container census (disc `PSP_GAME/USRDIR`)

| container | loads in `cpk_write`? | contents |
|---|---|---|
| `u16tbl.cpk` | **no** — ExtractSize is a *constant-storage* column | `jis2ucs.bin`, `ucs2jis.bin` |
| `system.cpk` | **no** — `CpkMode 0`, ITOC-only (no TOC) | system strings (TBD) |
| `imenu00.cpk` | yes (6 members, all CRILAYLA) | `srwDL_*` dictionaries (see below) |
| `mesbtl00.cpk` / `mesbmp00.cpk` | TBD | battle / message bitmaps (likely images) |
| `config00.cpk` / `configst.cpk` | TBD | config / system text (TBD) |
| `font.cpk` | TBD | glyph bitmaps |

## `u16tbl.cpk` = the encoding bridge (important for the font question)

Decompressed members are 131,072 B each = 65,536 little-endian u16 entries:
`jis2ucs.bin` maps a JIS/Shift-JIS code to a Unicode (UCS) codepoint; `ucs2jis.bin` is the
inverse. The low range is the identity map (JIS 0x20.. maps to the same UCS), i.e. **ASCII
passes through unchanged** — the game renders through UCS, so whether English shows up depends
on the *font* having Latin glyphs, not on the table. This is the concrete handle for the
"blank glyphs" risk noted in `METHOD.md`: to add/confirm Latin glyphs one edits `font.cpk`
(and possibly `u16tbl`), and `jis2ucs` tells us the codepoint pipeline.

`u16tbl.cpk` cannot be rebuilt by `cpk_write` (constant-storage ExtractSize column). Writing it
needs a TOC-row-layout rebuild or a byte-level in-place edit (its members are fixed-size).

## `imenu00.cpk` dictionaries are ID maps, not name strings

Members: `srwDL_BMP00`, `srwDL_CharaDictionary00`, `srwDL_DLC_ID00`, `srwDL_Reference00`,
`srwDL_Shop00`, `srw_DL_RoboDictionary00`. The `*Dictionary*` members begin with a u32 offset
table (e.g. Chara: `[100,404,628,...]`, 25 entries; Robo: `[68,276,...]`, 17) whose targets are
*further u32 data*, not CP932/UTF-16 display strings. So these map IDs to records; the actual
display names live elsewhere (a string heap referenced by those records, or another container).
Next: parse one dictionary record fully (field-by-field) and follow its string references.

## Why the writer refuses two of them (and what that implies)

- `u16tbl.cpk`: ExtractSize constant-storage → members can't be resized without rebuilding the
  TOC row layout. For translation we likely don't need to resize it (fixed-size tables), so an
  in-place byte edit of the decompressed member + re-compress may suffice.
- `system.cpk`: `CpkMode 0` (ITOC-only). `cpk_write` rewrites the TOC, which this container
  lacks. A writer path for ITOC-only containers is needed to patch system strings.

## Next steps

1. Reverse one `imenu` dictionary record fully; follow string references to the display-name
   heap; then export names as a table.
2. Locate the display-name string heap (candidates: `config*`, `system.cpk`, or a heap inside
   `imenu`/`mesbtl`).
3. Inspect `font.cpk` glyph coverage (does it include Latin A–Z?) against `jis2ucs`, to settle
   the blank-glyph risk for English before any UI text is written.
4. Add an ITOC-only / constant-storage write path to `cpk_write` (or a byte-level member
   re-compressor) so `system.cpk` / `u16tbl.cpk` can be patched.
