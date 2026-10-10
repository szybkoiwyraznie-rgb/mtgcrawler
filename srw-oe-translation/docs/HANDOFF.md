# HANDOFF — everything a successor needs to continue (read this first)

> If you only read one file, read this one. It is the condensed, current (2026-10-10) state of
> the SRW OE English fan-translation project. It supersedes the measurement-route plan still
> visible in `NEXT_STEP.md`/`TECHNICAL_FINDINGS.md` (kept as history). Chronology lives in
> `EXPERIMENT_LOG.md`; the milestone index in `STATUS.md`. Everything below was *proven*,
> mostly in the real game via PPSSPP, unless labelled hypothesis.

## 1. The goal and the model

Translate the whole game to English and ship it as a patch applied to the user's own Japanese
copy (chapter 1 from the disc ISO `SRW OE 1.08.iso`, chapters 2–8 from PSN DLC in
`NPJH50521`). Modelled on `retro-trans/SRW-Z`. The user wants a **fresh translation** (Akurasu
script rejected) and, as of 2026-10-10, has **deferred the actual translating to a separate
workflow**: the current job is the *process* — read / write / unpack ISO / pack ISO — and
producing **readable source files** a specialised translation model can consume. UI, names and
menus are also in scope, as separate tables, later.

## 2. What is PROVEN (do not re-litigate)

- **Containers are CPK.** Both the disc (`*.cpk`, e.g. `eventP00.cpk`) and the DLC (`*.EDAT`)
  hold CPK archives. `tools/cpk_write.py` (`load`/`rebuild`) and `tools/cpk_table.py`
  (`read_cpk_table`) parse and rebuild them. `eventP02.EDAT`: 367,480 B, 96 files,
  `Align 2048`, `CpkMode 2`, `Version 7`, `EtocOffset 366592`. Invariant: content end
  (= `EtocOffset`) is a multiple of `Align`. **EToc holds only `UpdateDateTime`+`LocalDir`** (no
  per-file sizes) — moving it as a blob loses nothing. The game reads member sizes from the
  **TOC**, not the ITOC.
- **Members are CRILAYLA-compressed.** `tools/crilayla.py` decompresses (header `CRILAYLA` +
  u32 usize + u32 csize, then stream + 0x100 trailer; `data = trailer + decoded`,
  `usize = extract_size - 0x100`; bit reader backwards MSB-first). **Stored members are accepted
  by the game** (a stored control booted), so a rebuilt member may be written stored
  (`FileSize == ExtractSize`). `compress_literal` exists but is a **dead end**: 9 bits/byte makes
  the stream larger (`FileSize > ExtractSize`), which `cpk_table` and likely the game reject.
- **Event members are EDAT scripts.** `EDAT` + u32 size + u32 count + sections
  (tag4 + size4 + body); section 0 is `EVNT`. Narration records:
  `type b7010000 | u32 length | u32 param | text | 00 00`, with `length == 12 + len(text) + 2`,
  lines separated by `0x0A`; the chain is walked by length (no offset index exists).
- **The growth crash root cause (the big one).** The EVNT section has an *inner* size field at
  body offset **60** that is always `EVNTsize - 36` (region `[56, EVNT_end)`), found by a
  differential across eventP01/02/03/09. The old `grow_record` bumped only the EDAT size (off 4)
  and the outer EVNT size (off 16), leaving offset 60 stale → the loader wrote through a bad
  pointer (fixed PC, data-dependent address) on *every* grown build. **Fix in
  `grow_event_text.grow_record`: also bump every u32 field before the record whose value equals
  `owner_end - f + 4`.** With it, **growth works in the real game** (jp +33 B booted). Equal-
  length edits were always safe.
- **Line-width limit.** The in-game dialogue box clips lines past ~**46 half-width** units
  (observed in a screenshot). `tools/export_strings.py` records `max_line_width` per record; a
  target must wrap within it (or the font must shrink).

## 3. The tooling (all under `tools/`, tested; suite 316 OK, 1 skipped)

| tool | purpose |
|---|---|
| `cpk_write.py` | load / rebuild CPK; `verify-identity`/`extract-member`/`replace-member` CLIs |
| `cpk_table.py` | read CPK tables; fails closed on `FileSize > ExtractSize` |
| `crilayla.py` | CRILAYLA decompress (+ `compress_literal`, dead end) |
| `grow_event_text.py` | `find_record`/`record_text`/`grow_record` (with inner-size fix)/`check`/`parse_edat` |
| `build_event_text_test.py` | driver; `verify_image` structural gate |
| `export_strings.py` | **readable source JSON** for translation AI → `local/strings/*.strings.json` (gitignored) |
| `iso9660.py` | read-only ISO index (`inspect_iso9660`) + `extract_members` |
| `iso_pack.py` | **pack** a spec-shaped ISO9660, preserves 32 KiB system area; round-trip tested |
| `iso_prep.py` + `PREP_ISO.bat` | on user's PC, bundle a small uploadable slice of the big ISO (inventory + system_area.bin + event/evept/PARAM.SFO, both `.EDAT` and `.cpk`) |
| `apply_strings.py` | **apply** translated `*.strings.json` back into a package via `grow_record`; enforces `max_line_width` (46), verifies source match, CP932-encodes; refuses over-wide/mismatched. Tested |
| `iso_pack.repack_iso` + `REPACK_ISO.bat` | **streaming** ISO repack from a local unpacked tree (sizes first, then sequential write; no 660 MB in RAM); `patch` map overrides members; preserves 32 KiB system area. Tested round-trip + patch |

Readable export format (one object per record): `member`, `record_index`, `record_offset`,
`source`, `lines`, `source_bytes`, `max_line_width`, `line_count`, empty `target`. **These live
in `local/` (gitignored): the full Japanese script must never enter git.**

## 4. Where the data is (Google Drive, folder `1oZ6xnvpV64ZcJhfrob8tVNs_SoPF3H1w`)

- `FULL_DLC/` `155zwn1AuwR_O8Sx0UpNPGIi52ysAlaPU` — 307 DLC files (`eventP01..13.EDAT`, …).
- `SRW_OE_1.08/` `1W7gCzfZRnPCFrqiajYnsC4YZcIk-ClY2` — the **full unpacked disc ISO**;
  `PSP_GAME/USRDIR/` `1FyM77fcFLQfXgxRhnS0cJ98oKZaZG72x`; chapter-1 container
  `eventP00.cpk` `1or9mKqqJzL_0aFqHOxLCTLKN3lEyNG1w` (162,264 B).
- original `eventP02.EDAT` `1yLV3NKrD4WKWf_pv9K6hxwvv3N531bbu` (MD5
  `60316f4639b906cf70b91fc28fc863be`).
- various test builds (00/03/05/06/07-*.EDAT) — see `EXPERIMENT_LOG.md` for which booted.

`download_file` stages into `<repo>/google_drive/` (inside the git tree): **always copy the file
out and delete the in-repo copy** so game data never lands in git.

## 5. Proven build hashes (what booted / what crashed)

- Booted: stored-no-growth `6752f04ed6d6dd06b869d47ffe868193`; same-length content
  `fa5319f5f930cf7114e168e89888d4a9`; EN same-length `391770431ef5efd32e46b40777461a38` (renders
  3 lines); **jp grown (fixed)** `cecd72631f73d469131e42eb42cc177e` (boots); en grown
  `4f82950c3b9074a248d8f9fa42b5f4ec` (renders, line 2 clipped by width).
- Crashed (do not reuse): unaligned grown `14e0d138…`/`91118db8…`; aligned-stored grown
  `cf1e703c…`/`ee40c5b4…`.

## 6. Remaining process (status 2026-10-10)

1. **Apply step — DONE.** `tools/apply_strings.py` (tested, 5 unit tests). Closes
   read → translate → write; enforces the 46-wide budget and source-match before writing.
2. **Streaming repack — DONE (tooling).** `iso_pack.repack_iso` + `REPACK_ISO.bat` (tested:
   round-trip + patch on a disk tree). Still to do: run it for real on the user's 660 MB tree
   and boot the result in PPSSPP.
3. **UI / names / menus export — NOT started.** Separate tables from containers `imenu*`,
   `mesbmp*`, `mesbtl*`, `u16tbl.cpk`, `system.cpk`, `font.cpk`; their formats are not yet
   reversed. This is the main open reverse-engineering area.

## 7. Pitfalls (each cost real time)

- Alignment was *not* the crash cause (two crashes shared the same PC). Stored-vs-compressed
  was *not* either (stored control booted). The inner size field was.
- The `google_drive` connector must be re-loaded via `list_connector_tools` every turn.
- Local-only files (`/home/user/src`, `/home/user/out2`) may not persist across sessions; the
  Drive copies are the durable store. Re-download by Drive id when missing.
- `local/` is gitignored on purpose; never commit the Japanese script or game binaries.
- Session/branch is fixed to `arena/c656a5df-mtgcrawler`; commit and push only there.
