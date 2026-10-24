# Text surfaces — where the game's text lives (survey, 2026-10-24)

Short answer to "is everything in `stage.bin`?": **no.** As in SRW OE, the
text is spread over several files with different formats and constraints.
`DATA/stage.bin` holds only the main scenario. This inventory is derived
from the vendored upstream docs (`FINDINGS.md`, `TECHNICAL.md`) and the
pinned upstream region table (`bisect_build.py`, not vendored); owner-copy
sizes below are Drive metadata observed on 2026-10-24. **Nothing here is
verified on the owner's copy yet** beyond those file sizes — each surface
gets its own proof before production (phase gates in `STATUS.md`).

| File (owner tree) | Contents | Format / constraints | Owner size / status |
|---|---|---|---|
| `DATA/stage.bin` (`STAGE.BIN`) | **Main scenario**: story dialogue and stage prose; 205 banlz records, one scenario each (~400–1450 rows). Row = locked speaker line + body, box max **3 lines × 34 columns**; placeholders (`$n/$F/$c`…) expand at runtime; `《term》` glossary links must resolve or the scene crashes. | banlz; string offsets embedded inline in scenario bytecode — in-place edits must keep exact byte length unless rows are relocated with pointer rewrites. Vendored `apply_script.py` rewrites the whole extent in place, same size. | **3,910,128 B**, LBA 1651029 — phase-1 proof target |
| `DATA/HSFC.BIN` | Stage synopses (4 banlz records). | banlz, same codec as STAGE. | 250,112 B |
| `btl/SRVC.BIN` (+ `.SEG`) | **Battle dialogue / battle quotes** (~1.08M chars upstream; ~19,213 battle lines per upstream README). | **Uncompressed**, `.SEG`-indexed; byte budgets are a known pain point upstream. | Upstream regions: 3,313,040 B + SEG 1,416 B; owner sizes TBD |
| `DATA/compdata.bn` (`COMPDATA.BN` rec0) | **Names/titles/bios**: unit & pilot names, weapon/item/ability text, 55 ability/skill descriptions, episode/scenario titles, route-select labels, character-select taglines/bios, leader/squad-bonus and stat/search-screen UI strings; some pilot defeat/retreat quotes. | One banlz record → 524,032 B at hardcoded RAM `0x006D6800`; pointer tables `0x904..0x61658` (9,483 words), string pool `0x61680..0x7FF00` (~3,433 entries, 8 B aligned) referenced by **absolute RAM pointers**. Cannot lengthen in place; pool can be repacked if pointers move (no per-name byte budget; UI width is the limit). **Menu encoding**: ASCII `0x2E–0x3D` are control codes for the menu reader. Pool/compdata tools are *not* vendored yet — import after audit in phase 2. | 144,990 B (compressed) |
| `SLPS_258.87` (boot ELF) | Part of the **UI**: skills, series titles, system messages (plain SJIS in the ELF). Also the renderer/font patch site. Exact ELF-vs-COMPDATA split of UI text is still TBD. | Plain SJIS strings inside the ELF; renderer patch details in vendored `RENDERER.md`. | 3,471,624 B |
| `MAP/MAPNAME.BIN` | 195 map names. | Plain SJIS, fixed 256-byte stride (195 × 256 = 49,920 B), no pointers. | Owner size TBD |
| `DATA/MtVZknKW.bin` / `MtVZknPt.bin` / `MtVZknRt.bin` | Encyclopedia (zukan) archives — in upstream's TEXT region group. | Format/semantics to verify in phase 2. | 29,936 / 293,696 / 185,600 B |
| `DATA/MtV_ProS.BIN` (`MTV_PROS`) | Unknown text-bearing region (upstream TEXT group). | TBD. | 9,056 B |
| Textures / painted text (`jtim.bin`, `NisVData.bin`, `vt1.bin`, OP/KVMDATA/MAPMODEL regions…) | Captions painted into graphics (upstream ART group). Upstream also used PCSX2 texture replacements for some captions — that is emulator-side, *not* a disc patch; our equivalent scope is undecided. | Graphics formats; separate inventory, **not in scope** until phase 2+. | e.g. `jtim.bin` 7,539,728 B; `NisVData.bin` 555,056 B; `vt1.bin` 127,500,736 B |

Notes:

- Upstream's shipped build also relocates some files into the `DMY`
  region (`bisect_build.py`: "DMY carries the RELOCATED files (COMPDATA
  and friends)"). That does not affect the phase-1 STAGE proof (in-place
  extent), but any future relocation for other surfaces is an owner-side
  image-level design decision for the bat — documented before built.
- Speaker-name lines inside STAGE rows are locked in the dialogue
  pipeline; renames go through a separate names pass upstream. Our
  translator-file design (phase 2) must respect that split.
