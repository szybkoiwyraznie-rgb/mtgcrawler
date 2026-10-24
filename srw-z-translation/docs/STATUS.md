# SRW Z (Polish) — status

*2026-10-24 — phase 0 (setup/research) complete; phase 1 not started.*

## Confirmed

- Owner's edition is **`SLPS-25887`** (original Japanese PS2 release):
  `SLPS_258.87` (3,471,624 B) + `SYSTEM.CNF` in the extracted Drive tree
  `SRW/SRWZ/rozpakowane ISO` (Drive folder `1ujHDKXOlj_OtgY-A9i53JhS7Fuw14D1g`
  inside `SRWZ` `1HnENcLdKxc_2j3k5CBewUhyvYrXFhKl0`; 16 top-level entries).
- The main script extent used by the upstream tools is `DATA/STAGE.BIN` at
  **LBA 1651029, 3,910,128 bytes** (`rewrap_dialogue.py`: `LBA, SIZE,
  SECTOR = 1651029, 3910128, 2048`). The owner's extracted `DATA/stage.bin`
  (Drive `1dG_w3QBS3AEE_HJaolVV0HjskpaJYRDd`) is exactly **3,910,128 B**.
- `apply_script.py` rewrites that extent **in place at the same size**
  (seek `LBA*SECTOR`, write the same `SIZE` bytes back). So a sandbox
  round-trip on the extracted file alone is technically meaningful, and the
  owner-side bat can run the identical apply step on the real ISO.
- Upstream retro-trans/SRW-Z pinned at `fed4c8b…` (MIT), audited core
  vendored: 19 files / 180,088 B (7-tool dependency closure 66,772 B +
  9 docs + `LICENSE` + `TRANSLATING.md` + `UPSTREAM_README.md`); all 7
  tools parse (`ast`), no personal absolute paths in the imported set.
- Owner's test emulator will be **PCSX2 v2.9.144** (Windows x64 Qt;
  owner-reported download on 2026-10-24). Settings still to record; no
  runtime result yet.
- The text is **not** all in `stage.bin`: doc-derived inventory of all
  text surfaces (STAGE, HSFC, SRVC battle quotes, COMPDATA names/UI, ELF
  UI strings, MAPNAME, ZKN, textures) is in
  [`TEXT_SURFACES.md`](TEXT_SURFACES.md) — to be verified on the owner's
  copy surface by surface.
- Owner's `DATA/` also holds the other text-bearing candidates named by
  upstream docs: `HSFC.BIN` 250,112 B, `compdata.bn` 144,990 B (plus
  `BTL/SRVC.BIN`, `MAP/MAPNAME.BIN` outside `DATA/` — sizes not listed yet).
- Inputs are in `local/inputs/` with SHA-256 recorded (`stage.bin`
  `9c56d42f…240dc`, `SLPS_258.87` `6c4c81c4…9b50`). The sparse-image
  sandbox proof passed (extract 119,837 rows; unchanged apply
  byte-identical), and all five upstream renderer landmarks match the
  owner's ELF byte-for-byte — see [`FONT_RESEARCH.md`](FONT_RESEARCH.md).
  SJIS lead banks `0x84/0x85/0x86` are entirely unused in the JP script,
  leaving ample private code space for Polish glyphs.

## Owner decisions on record (2026-10-24)

1. **OE workflow:** ISO stays local with the owner; sandbox works on
   extracted files from Drive; deliverable = `PATCH.bat` kit patching the
   owner's ISO. *This supersedes the ISO-upload idea from earlier the same
   day — no ISO upload is needed or wanted.*
2. **Translator files:** JP original + retro-trans English as reference
   column + our SRW OE terminology glossary; Polish written fresh from JP.
3. **Order of work:** technical proof first (round-trip + font prototype),
   translator files after.
4. **Font route (updated later on 2026-10-24):** fonts are now the
   **first** work track, ambitious route — Polish glyphs at normal
   English (half-width) metrics, built on the Latin letterforms with
   added diacritics; fullwidth is not a shipping fallback. Design and
   prototype sequence: [`FONT_RESEARCH.md`](FONT_RESEARCH.md).

## Phases

- **Phase 0 — setup (done):** scaffold, decisions, vendored core, registry.
- **Phase 1 — technical proof (in progress; font track first per owner):**
  1. ✅ Downloaded `DATA/stage.bin` + `SLPS_258.87` to `local/inputs/`
     (SHA-256 in `FONT_RESEARCH.md` / experiment log).
  2. ✅ Sparse virtual image proof in the sandbox: extract → 119,837
     rows; apply-unchanged → 0 writes, extent byte-identical;
     `verify_pointers.py` baseline 121,382/131,976 (91.97%).
  3. ✅ **Font prototype built (sandbox):** P1 vendor baseline + P2
     Polish atlas (87 glyphs, DejaVu-rendered) + pangram sample row —
     all byte-diffs/hashes in `FONT_RESEARCH.md`. P3 owner test kit
     `srwz-pl-font-test-p3.zip` delivered to Drive `SRWZ`
     (`1PMiZXRKJWvL9z0ETRGq-3lpENPvhJRAN`) and sandbox-tested
     end-to-end (deterministic extent hashes).
  4. **Awaiting owner:** run `PATCH_TEST.bat` on the real ISO (writes a
     `*_PLTEST` copy; source hashes enforced), boot in PCSX2 v2.9.144,
     return dialogue/menu screenshots + `srwz_patch_log.txt`. Then P4:
     tune glyphs/metrics from evidence and freeze code assignments.
     The standalone STAGE no-op bat test folds into this run (the
     patcher verifies both source extents before writing).
- **Phase 2 — translator files:** format with JP + EN reference + OE
  glossary, re-injectable through the proven pipeline; verify the
  doc-derived inventory in [`TEXT_SURFACES.md`](TEXT_SURFACES.md) against
  the owner's copy, surface by surface (`HSFC.BIN`, `compdata.bn`,
  `SRVC.BIN`, `MAPNAME.BIN`, ZKN/MTV_PROS, ELF strings, textures).
- **Phase 3 — translation production** (scope/order decided with owner).

## Unknowns / blockers

- Whether the owner's extracted `stage.bin` bytes are identical to the ISO
  extent (to be proven by the phase-1 owner-side no-op test).
- Text limits beyond the main script (byte budgets, encodings per file).
- Polish glyph source: the game font is fullwidth-SJIS; free slots/atlas
  location unidentified (upstream font docs are the starting point).
- Owner's PCSX2 **settings** (version known: v2.9.144, Windows x64 Qt) —
  GS/graphics settings to record when the first test build ships.
- No emulator runtime result of any kind yet.
