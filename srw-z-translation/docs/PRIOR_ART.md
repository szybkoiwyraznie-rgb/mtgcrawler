# Prior art — retro-trans/SRW-Z (survey, 2026-10-24)

Source: <https://github.com/retro-trans/SRW-Z>, pinned at
`fed4c8b910028e964c5c6de87b2d58b3b92628b9` ("Document SRW Z English
v0.9.88 release", pushed 2026-10-19). English fan translation of SRW Z
(PS2) for `SLPS-25887` (our edition) and The Best `SLPS-73270`,
distributed as xdelta patches. **License: MIT** — the license file covers
the tools, the docs and the English text data in `analysis/`. We still
translate fresh from Japanese; their English is used only as an
owner-approved translator reference column.

## Script pipeline (what we vendored)

All core tools address the disc **image** and one file extent: the
banlz-compressed `DATA/STAGE.BIN` at LBA 1651029 × 2048, 3,910,128 bytes
(205 records). Dependency closure of the pipeline is just 7 files
(66,772 B): `extract_script.py`, `apply_script.py`, `verify_pointers.py`,
`scan_visible_defects.py`, `build_compare.py`, plus shared `banlz.py`
(compression, byte-exact round-trip over all 205 records per
`LZ_FORMAT.md`) and `rewrap_dialogue.py` (holds the LBA/SIZE constants).

Workflow per `TRANSLATING.md`: `extract_script.py <image> script.json`
(JSON dict with `note` + `rows`; edit `text` fields) →
`apply_script.py <image> script.json --write` (validates rows, refuses on
errors, rewrites the extent **in place, same size**, slack re-padded with
NULs) → `verify_pointers.py` + `scan_visible_defects.py`. Upstream claims
a byte-exact no-change round-trip; **we have not reproduced it yet**
(phase 1). Script scale per upstream: **87,835 lines**.

Consequence for our OE-style workflow: because addressing is a single
contiguous extent rewritten at fixed size, the pipeline can run unchanged
against a sparse virtual image holding the owner's extracted
`DATA/stage.bin` at the same offset — no ISO needed in the sandbox. The
owner-side bat runs the same tools against the real image.

## Font state upstream (why Polish glyphs are a research item)

- The dialogue renderer indexes glyphs purely by 2-byte SJIS code; the
  font has **fullwidth glyphs only** — no half-width Latin, and no Polish
  diacritics at all (`FINDINGS.md`, `RENDERER.md`).
- The **shipped** English build remaps ASCII → fullwidth SJIS twins in the
  message buffer (patch site at the byte read; layout routine `0x2212B0`,
  blit `0x13A290`). Wide but robust.
- A true half-width custom font (ELF-embedded 12 px glyphs, GS/VRAM DMA
  injection, hooks at layout `0x221644` / dialogue `0x13B304`) renders
  in-game but is **blocked on a two-pen ghost artifact and mid-word wrap**
  (`CUSTOM_FONT.md` OUTCOME 2026-08-12); the shipping build reverted to
  fullwidth. `VWF.md` (33 KB) documents the variable-width attempts.
- For Polish (ąćęłńóśźż + capitals) both routes need new glyphs; the
  master font atlas source on disc is unidentified/packed upstream. This
  is harder than SRW OE's font work and is our phase-1 prototype topic.

## What we imported, what we deliberately did not

- **Imported** (unmodified, byte-pinned): the 7 core tools above, all 9
  `docs/*.md`, `LICENSE`, `TRANSLATING.md`, `README.md` (as
  `UPSTREAM_README.md`). See `vendor/retro-trans/PROVENANCE.md`.
- **Not imported:** the remaining ~269 Python one-off tools (many embed
  English string data; three contain the upstream author's personal
  absolute Windows paths — `build_texture_pack.py`, `gen_intro_cards.py`,
  `zkn_deepseek.py`), the 6 `.ps1` helpers, and `analysis/` (~26 MB,
  incl. `english_script.json` + `glossary.json`). Anything further is
  imported pinned, on demand, after the same audit, with hashes logged.

## Other text surfaces named upstream (phase-2 inventory)

`DATA/HSFC.BIN`, `DATA/compdata.bn` (menu-encoded names/titles),
`BTL/SRVC.BIN` (battle captions, byte budgets), `MAP/MAPNAME.BIN`
(195 names, fixed 256-byte stride), ELF strings, ZKN encyclopedia
archives and PCSX2 texture-replacement captions. Each has its own
constraints; none is in scope until inventoried against the owner's copy.
