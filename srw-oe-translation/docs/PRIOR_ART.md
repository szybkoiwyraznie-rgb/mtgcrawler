# Prior art — what other people have already solved

Survey run on 2026-10-10 (GitHub API + web search). Recorded so the search is not repeated, and
because **it changes the plan**: the container-level questions this project has been measuring
byte-by-byte are already answered for this exact game and for the engine family around it.

**Boundary kept here:** everything below is *format* knowledge — where text lives, how a translation
was fitted, how the font was made to render new characters. No translated text is taken from any of
these projects; the user asked for a fresh translation and rejected the Akurasu script as a source.

## 1. A working Korean patch exists for this exact game — base *and* DLC

`z3oo3z` publishes 21 Korean fan patches across PS1/PS2/PS3/PSP, two of them for Super Robot Wars
Operation Extend (`NPJH50521`, the game in this project):

| Repo | Version | Release assets | Size | Downloads |
|---|---|---|---|---|
| [`z3oo3z/PSP-SRWOE-KPatch`](https://github.com/z3oo3z/PSP-SRWOE-KPatch) | `v250810` (2025-08-10) | `srwOE_v250810.7z` | 54,258,657 B | 321 |
| | | `srwOE_texture_NPJH50521_UI.7z` | 10,343,773 B | 276 |
| [`z3oo3z/PSP-SRWOEDLC-KPatch`](https://github.com/z3oo3z/PSP-SRWOEDLC-KPatch) | `v250617` (2026-06-17) | `srwOEKDLC_v250617.7z` | 2,938,903 B | 246 |
| | | `srwOEKDLC_eventP01.EDAT.7z` | 151,313 B | 221 |

Both repos contain **only a README** (verified: one blob each, no tools, no scripts, no issues, no
code). Everything below is what those READMEs claim; the archives themselves were **not** downloaded
or inspected (the sandbox cannot reach `release-assets.githubusercontent.com`).

What the READMEs state, and why each item matters here:

- **Base game:** the patch is applied by dragging the original ISO onto `여기에원본iso올려놔.bat`
  ("put the original ISO here.bat") — i.e. an in-place ISO patcher, and a *patch distribution*, not
  a shared ROM ("본 패치에는 한글패치 데이터만 들어 있습니다"). Original MD5
  `ce57eb21bcdc9bdd6204f63a4fd9f716`, patched MD5 `1b5e7e8c984f07bf3620c8399d158efa`.
  → A one-command check settles whether our ISO is the same edition: the project's ISO is `SRW OE
  1.08.iso`, and its MD5 is unknown here.
- **DLC:** `srwOEKDLC_v250617.7z` holds an `xdelta` folder with **73 patch files**, an `org` folder
  for the originals, `1.move_org.bat`, `2.dlcpatch.bat`, and `dlcmd5checker.exe`, which verifies each
  original and then each patched file and names any file that failed.
  → **73 xdelta patches, one per DLC file, applied to the user's own originals** is exactly the
  distribution model this project committed to. It is proven to work for the DLC, which was the part
  expected to be hardest.
- **The patched DLC output is an `.EDAT`** (`eventP01.EDAT`), placed in
  `memstick/PSP/GAME/NPJH50521`, with a further 2026-06-23 individual update applied with xdeltaUI.
  → They patch the *encrypted* file as the unit of distribution. Our plan assumed patching
  decrypted/rebuilt data; both are on the table now.
- **Menus are done as PPSSPP texture replacement**: PNGs into `memstick/PSP/TEXTURES/NPJH50521`, with
  a note about `textures.ini` dumping if a name does not match.
  → Anything baked into UI art is out of scope for a text pipeline. This is a shortcut worth adopting.
- **Tested on PPSSPP 1.18.1 (PC); "실기 실행 여부 모릅" — unknown whether it runs on real hardware.**
  → The honest verification level for this route is the emulator, matching our own open item.
- **v250810 changelog: fixed the spirit command 축복 (Blessing) not working.**
  → Data-level patching, not only graphics: they changed game data and hit data-level bugs.

## 2. A partial English patch also exists — but not the dialogue

- [cdromance: *Super Robot Taisen: Operation Extend* (J+English Patched) PSP ISO](https://cdromance.org/psp/super-robot-taisen-oe-operation-extend-english-patched/),
  by **CrashmanX**: level names, item names and song names fully translated; battle menus ~90%; unit
  and attack names ~80%; main menus ~70%; character names ~60%; terrain effects ~30%. **Story
  dialogue is not in that list** — the part this project targets.
- It is distributed as a whole patched ISO for **v1.02** (`PLAYASiA.iso` CRC-32 `2866c6c0`), while the
  clean Japanese v1.08 is CRC-32 `1718f49a`. A patch for one version will not apply to the other.
- No GitHub presence found for `CrashmanX` (no repositories).
- [r/SRW, 2015](https://www.reddit.com/r/SRW/comments/3t0iaj/english_translation_patches/): "SRW
  Operation Extend (PSP) — was stopped at some point because of a bug, but a partial patch is
  available."
- [r/Super_Robot_Wars, 2021](https://www.reddit.com/r/Super_Robot_Wars/comments/nc4dcy/super_robot_wars_oe_line_by_line_translation/):
  a line-by-line translation effort, Japanese lines pulled out with Cheat Engine and translated with
  DeepL — no container knowledge published.

## 3. The SRW-Z project this workflow is modelled on already hit our exact wall

[`retro-trans/SRW-Z`](https://github.com/retro-trans/SRW-Z) (PS2, published docs in `docs/`):

- **"String indexing is offset-based … There is no contiguous offset/length table anywhere in the
  record (checked as u16/u32, absolute and relative). Conclusion: string offsets are embedded inline
  in the scenario bytecode."** — the same negative result this project measured three different ways
  (`docs/STATUS.md` item 61), reached independently on a sibling engine.
- They settled it with a **grow-test**, not with static scanning: lengthen one early string so
  everything after it shifts, run the game, and see which lines go blank. In-game, the grown line
  rendered and the shifted lines after it were blank.
- **In-place replacement that preserves each string's exact byte length is "safe and verified."**
  Growing strings requires rewriting every inline offset operand.
- **Relocation ("option 3")**: a row that grows past its slot is appended at the record end and every
  4-aligned pointer to it is rewritten, the old slot zeroed. This is the byte-budget escape hatch.
- **Static signature search for the glyph renderer did not converge** (too many false positives); the
  answer came from a **PCSX2 memory breakpoint** on the decompressed dialogue buffer and stepping out
  to the reader (`docs/DEBUGGER_TRACE.md`, `docs/RENDERER.md`).
- **The dialogue font is fullwidth Shift-JIS only; raw ASCII renders as blank boxes.** Their fix is an
  ELF renderer patch remapping ASCII to the existing fullwidth glyph at draw time, "matching the
  documented approach of other PS2 SRW fan patches (e.g. camd11's OG Gaiden, which added a VWF + font
  width table into dead ELF space)."
- Display box is **3 lines × 34 columns**, fullwidth counts 2 — a *display* limit, not a byte limit,
  so relocation buys bytes but not screen space.

## 4. The Korean SRW patches share one method: substitute glyphs, keep byte length

- [`snake759494/NDS-SRW-K`](https://github.com/snake759494/NDS-SRW-K) (SRW K, NDS) is the most
  complete open example of the delivery model this project wants: translation held as JSON in
  `data/*_ko.json`, one `.xdelta` per release in `patch/`, a `docs/PATCHING.md` that gates on the ROM
  CRC-32 and states the expected patched size and CRC-32, and published injection tools
  (`_inject_font.py`, `_inject_arm9.py`, `_inject_credits_fit.py`).
  - Its font solution: the ROM's single glyph font is a table of 26-byte records
    (`[u16 SJIS BE][24-byte 1bpp 12×16 bitmap]`), and the patch **overwrites the entries for codes
    ≥ `0x889F` with KS X 1001 Hangul (2,349–2,350 glyphs)** rendered from Galmuri11 (SIL OFL 1.1).
    A side effect they document: kanji in that code range then print as Hangul.
- The same approach is described for PS2 SRW Z in a Korean community log
  ([beeshass blog, 2024](https://m.blog.naver.com/beeshass/223527624760)): put ~2,350 Hangul glyphs
  into the font, unpack the CPK in the `STAGE` folder, edit the DAT's dialogue, and add a texture pack
  for the interface.
- [`snake7594/srwcb-korean-patch`](https://github.com/snake7594/srwcb-korean-patch) (PS1 SRW
  Complete Box) ships its own tools, a Korean overlay, a glossary and docs, and applies the patch with
  a drag-and-drop `.bat` doing SHA-256 verification → patch → result verification. Same shape as this
  project's `RUN_PIPELINE.bat`.

## 5. On repacking these CPKs — an independent confirmation of our Gate 2

[gbatemp, "Super Robot Wars OE"](https://gbatemp.net/threads/super-robot-wars-oe.351431/):

- A QuickBMS script for the `.cpk` was shared in that thread, plus the note that the DLC files work by
  **renaming `.EDAT` to `.CPK`** (they are CPK containers underneath — consistent with what this
  project's `tools/cpk_table.py` already does).
- **"i tried to repack 'without any changes' the game crash so i may need a special tool for these."**
  → A naive repack of an unmodified CPK already breaks the game. This is exactly why repack,
  write-back, reinsertion and ISO rebuild are gated in this project.
- Recommended alternative tool: *cri packed file maker* (reported as used for a Digimon translation).

## What this changes

1. **The container question is answered by evidence, not by more scanning.** Applying the Korean
   DLC patches to the user's own originals and diffing the result gives ground truth in one run:
   which files hold text, whether strings grow, whether neighbouring bytes (offset operands) are
   rewritten, whether the file length changes, and how the font was made to render new glyphs.
   That is strictly more information than any further `RUN_PROBE.bat` run, and it is cheap: the DLC
   archive is 2.9 MB.
2. **The distribution model is validated end-to-end for this game** — xdelta patches against the
   user's own files, MD5/CRC gates, a `.bat`, emulator verification. That is the shape this project
   already committed to.
3. **The font problem has two known solutions** (renderer/ELF remap as in SRW-Z; glyph-table
   substitution as in the Korean patches) and English needs far fewer glyphs than Korean.
4. **The dialogue is still nobody's.** No public English translation of the OE story text exists, and
   neither Korean repo publishes its tools — so the extraction and reinsertion tooling is still this
   project's to build. What is no longer unknown is the shape of the answer.

## Suggested order

1. Check our ISO's MD5 against `ce57eb21bcdc9bdd6204f63a4fd9f716` (one command).
2. Download `srwOEKDLC_v250617.7z` (2.9 MB) and diff the patched DLC against the user's originals,
   aligning the changed byte ranges with this project's extracted units.
3. If the ISO matches, do the same for the base game from `srwOE_v250810.7z`.
4. Only then, if a question is still open, spend a `RUN_PROBE.bat` run on it.
