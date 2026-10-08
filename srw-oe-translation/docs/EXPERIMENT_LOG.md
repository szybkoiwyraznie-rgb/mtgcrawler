# Experiment log

Only user-reported tests are recorded. No game files are stored in this repository.

## 2026-10-08 — identify outer archive signatures

**Inputs:** local PPSSPP content under `PSP/GAME/NPJH50521`.

**Action:** Read the first 16 bytes of `imenu01.EDAT`, `eventP01.EDAT`, and `config01.EDAT` in PowerShell.

**Result:** All three began `43-50-4B-20` (`CPK `), followed by the same-looking header bytes. Confirmed CPK signature for these three files.

## 2026-10-08 — extract `imenu01`

**Action:** Opened a copy of `imenu01.EDAT` with YACpkTool.

**Result:** Extracted:

- `srwDL_BMP01.bin` — 4 bytes
- `srwDL_CharaDictionary01.bin` — 15,688 bytes
- `srwDL_DLC_ID01.bin` — 3,336 bytes
- `srwDL_Reference01.bin` — 4 bytes
- `srwDL_Shop01.bin` — 4 bytes
- `srw_DL_RoboDictionary01.bin` — 9,702 bytes

Names suggest dictionary/DLC-related tables, but their exact field formats have not been inspected.

## 2026-10-08 — extract `eventP01`

**Action:** Opened a copy of `eventP01.EDAT` with YACpkTool.

**Result:** The archive contains 88 files in repeated groups. Scenario-like IDs include `DL102_20`, `DL102_30`, `DL102_40`, `DL102_50`, `DL102_60`, `DL102_70`, `DL102_90`, `DL103_11`, `DL103_12`, `DL103_20`, `DL103_30`, `DL103_40`, `DL104_11`, `DL104_20`, `DL104_30`, `DL105_11`, `DL105_12`, `DL105_20`, `DL105_30`, `DL105_40`, plus `SM001` and `SM002`. Most groups have `.bin`, `_edit.dat`, `_Entry.dat`, and `_ext.dat` members. See `FILE_INVENTORY.md`.

`DL102_20.bin` is 16,216 bytes; its companion files are `DL102_20_edit.dat` (28), `DL102_20_Entry.dat` (1,024), and `DL102_20_ext.dat` (388).

## 2026-10-08 — inspect `DL102_20.bin`

**Action:** Viewed the file in Notepad++ with Shift-JIS selected; searched for a known Japanese substring and inspected a 0x0580–0x0680 hex window.

**Result:** Japanese dialogue is directly present in CP932-compatible byte sequences. The visible section includes `FF FF`, line-break bytes `0A`, and apparent `00 00` endings. File tags observed: `EDAT`, `EVNT`, `ECHK`. These marker interpretations remain hypotheses.

## 2026-10-08 — CPK no-change round trip

**Action:** Packed the unchanged extracted `eventP01` directory with YACpkTool, then extracted the resulting `eventP01.cpk` into a fresh folder.

**Result:** Re-extraction included all expected files. `DL102_20.bin` had the same size (16,216 bytes) and the user reported its SHA-256 matched the original extraction. Rebuilt archive was reported at about 500 KB; original `eventP01.EDAT` was 326,456 bytes. No in-game test has been performed.

## 2026-10-08 — candidate text dump

**Action:** Ran the read-only `FF FF ... 00 00` CP932 candidate scanner on `DL102_20.bin`.

**Result:** It wrote 215 output lines and included the known Japanese substring. The output also contains control/binary-looking characters (the user cited characters like U+0001/U+0002 and a full-width space). These may be meaningful control tokens mixed with text or false-positive candidates; do not strip them until their role is understood.

**Output-format note:** The offset/text separator appeared as a literal backtick followed by `t` because the PowerShell format string was single-quoted. This is a display-formatting issue, not game data; the corrected line and reproducible scanner are recorded in `NEXT_STEP.md`. Offsets and candidate text are unaffected.

## 2026-10-08 — review candidate examples

**Input:** The user supplied two readable candidate rows (offsets `0x158C` and `0x1D68`) and two visually noisy but still coherent Japanese rows (`0x14E8` and `0x25A8`).

**Observation:** The decoded row at `0x14E8` ends with a space, ASCII `v`, and U+0001; the row at `0x25A8` ends with a space, ASCII double quote, and U+0002. If decoded directly from CP932 bytes, these suffixes are expected to include `20 76 01` and `20 22 02`; raw bytes have not yet been checked.

**Interpretation:** The noisy rows are not wholly gibberish; coherent Japanese dialogue is present. The trailing bytes may be inline control codes, record metadata, or an overlong candidate span. Their function and the `00 00` boundary assumption remain unverified. Do not strip them.

## Pending

- Collect short raw-hex windows around the first `00 00` after candidate offsets `0x14E8` and `0x25A8`; determine whether the suffix bytes are inside the candidate span or the boundary needs revision.
- Validate the scanner on more records/files and replace it with a structured extractor that preserves controls and stable IDs.
- Record actual SHA-256 values for the source ISO and relevant original CPK files before any release/patched-file tests.
- Test a rebuilt archive in a disposable PPSSPP copy only after preserving/validating originals.
