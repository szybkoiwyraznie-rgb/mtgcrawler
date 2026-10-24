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
- Owner's `DATA/` also holds the other text-bearing candidates named by
  upstream docs: `HSFC.BIN` 250,112 B, `compdata.bn` 144,990 B (plus
  `BTL/SRVC.BIN`, `MAP/MAPNAME.BIN` outside `DATA/` — sizes not listed yet).

## Owner decisions on record (2026-10-24)

1. **OE workflow:** ISO stays local with the owner; sandbox works on
   extracted files from Drive; deliverable = `PATCH.bat` kit patching the
   owner's ISO. *This supersedes the ISO-upload idea from earlier the same
   day — no ISO upload is needed or wanted.*
2. **Translator files:** JP original + retro-trans English as reference
   column + our SRW OE terminology glossary; Polish written fresh from JP.
3. **Order of work:** technical proof first (round-trip + font prototype),
   translator files after.
4. **Font route:** decided after the prototype.

## Phases

- **Phase 0 — setup (done):** scaffold, decisions, vendored core, registry.
- **Phase 1 — technical proof (next):**
  1. Download `DATA/stage.bin` (+ `SLPS_258.87`) to `local/`, record SHA-256.
  2. Build a sparse virtual image with `stage.bin` at offset
     1651029 × 2048; run unmodified vendored extract → apply-unchanged →
     compare extent bytes; run `verify_pointers.py`. *Planned approach —
     hypothesis until executed and logged.*
  3. Owner-side `PATCH.bat` no-op test on the real ISO (new image must be
     byte-identical to the original); owner returns log + hashes.
  4. Polish-glyph font prototype on the extracted ELF copy; owner judges
     screenshots in PCSX2; then the font-route decision.
- **Phase 2 — translator files:** format with JP + EN reference + OE
  glossary, re-injectable through the proven pipeline; inventory of the
  remaining text files (`HSFC.BIN`, `compdata.bn`, `SRVC.BIN`,
  `MAPNAME.BIN`, ELF strings, textures).
- **Phase 3 — translation production** (scope/order decided with owner).

## Unknowns / blockers

- Whether the owner's extracted `stage.bin` bytes are identical to the ISO
  extent (to be proven by the phase-1 owner-side no-op test).
- Text limits beyond the main script (byte budgets, encodings per file).
- Polish glyph source: the game font is fullwidth-SJIS; free slots/atlas
  location unidentified (upstream font docs are the starting point).
- Owner's PCSX2 version/settings — needed when the first test build ships.
- No emulator runtime result of any kind yet.
