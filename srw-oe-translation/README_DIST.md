# Super Robot Wars OE — English Translation Patch

Fan translation of **Super Robot Wars OE** (PSP) from Japanese to English.

> **v17:** adds map terrain names, flat/unambiguous DLC deployment, and explicit
> read-back checks for the two reported chapter-4 DLC titles. Visual/gameplay QA
> continues; see `translation/CO_NOWEGO_v17.txt`. Existing saves must be preserved.
>
> **Caption geometry fix (2026-10-24):** English captions on the intermission /
> upgrade / parts textures (`intsys_01`, `intsys_03`, `intsys_04`) are now drawn
> inside the exact TXCL rectangles the game samples (verified identical in
> IM1000/IM3000/IM9000), so no caption is clipped, none bleeds into a neighbouring
> caption, and no Japanese glyph remnants remain (e.g. full-size `Convert` /
> `Progress` on the parts screen, clean `Upgrade Limit Break` ribbon). The
> translation text itself is unchanged; repatch from a clean ISO as usual.

---

## What you need

| Requirement | Notes |
|---|---|
| **Game ISO** | `SRW OE 1.08.iso` — your own legally obtained copy |
| **DLC files** (optional) | Decrypted DLC folder (`NPJH50521`) for chapters 2–8, e.g. decrypted with `psnpkgdecryptextract` |
| **PPSSPP** | PSP emulator — https://www.ppsspp.org/ |
| **Windows 10/11** | The patcher is a `.bat` script |
| **Python 3.8+** | Auto-installed if missing (needs `winget`) |
| **Pillow** | Python image library — auto-installed if missing |

## Quick start

1. **Unzip** this archive to any folder (e.g. `C:\Games\SRW-OE-Patch\`).

2. **Double-click `PATCH.bat`**. It will:
   - Check that Python and Pillow are installed (install them if needed)
   - Ask you to **select your game ISO** (a file picker window opens)
   - Ask you to **select your DLC folder** (or Cancel to skip DLC)
   - Build the patched files

3. **Find the output** in the `output\` subfolder:
   | File | What to do with it |
   |---|---|
   | `patched.iso` | Open in PPSSPP (File → Load...) |
   | `DLC\` | Copy the **files inside** directly into the existing `memstick\PSP\GAME\NPJH50521\` folder |
   | `build_report.json` | Technical details (not needed for playing) |

4. **Keep backups and existing saves.** Build from the original Japanese ISO and
   decrypted DLC, not a previous patched ISO or a mixture of original/old outputs.
   Overlay the flat files from `output\DLC\` onto the existing complete installed
   DLC folder. Do not nest an extra `DLC`, chapter or `NPJH50521` folder inside it,
   and do not delete untouched original DLC/audio files.

5. **Cold-start the game** using the new `patched.iso`, then load a normal in-game
   save. An old emulator save state can retain old resources in RAM. There is no
   need to delete saves. Previously claimed DLC bonuses may not pop up again.

### If the two DLC names still appear Japanese

Run **CHECK_DLC.bat**, select the **installed** NPJH50521 folder actually used by
PPSSPP (not the original backup or patcher's output), and send `DLC_TITLE_CHECK.json`.
This is read-only: no game/save files are changed. It reports the actual title
fields, matching descriptions, hashes, missing files and duplicate backup copies.
A file PASS verifies disk bytes, not the contents of an old emulator save state.

### Terrain labels and output size

The missing `宇宙構造物` label is now **Space Str.** (Space Structure). The same
terrain-name table exists in 271 map archives; v17 handles all copies and all 111
nonempty names. Only fixed-size name cells change; numeric attributes, geometry
and texture bytes are preserved. Map members use the established STORED CPK path,
so rebuilt `lmap.cpk` is about **156 MB** instead of 81 MB. The ISO packer appends
changed members rather than reclaiming old sectors, so the output ISO grows too.
Allow at least **3 GB free workspace** (recommended; the exact requirement depends
on the selected game/DLC and backups). This larger file is expected, not an error.

## Folder structure after unzip

```
SRW-OE-Patch/
├── PATCH.bat              ← double-click this
├── CHECK_DLC.bat          ← read-only installed-file check
├── README.md              ← this file
├── translation/           ← translation data (JSONL files, glossary)
│   ├── 00_dialogue.jsonl
│   ├── 01_battle_quotes.jsonl
│   ├── ...
│   └── tokeny.tsv
├── tools/                 ← Python build scripts
│   ├── build_translation_patch.py
│   ├── pick_path.py       ← file picker for .bat
│   └── ... (35 files)
└── docs/                  ← reference materials
    ├── translator/        ← glossary, voice cards, style guide
    └── ...
```

## Troubleshooting

**"Python not found"** — Install Python from https://www.python.org/ and check
"Add Python to PATH" during installation.

**"Pillow not found"** — Open a command prompt and run: `python -m pip install pillow`

**Build fails** — Read the error message. Most common causes:
- ISO is not `SRW OE 1.08` (different version)
- DLC files are encrypted (need to be decrypted first)
- Not enough disk space (at least 3 GB free workspace recommended)
- Duplicate .EDAT/.CPK/.PBP filenames in backup/decryption subfolders; select a
  clean input folder. v17 refuses ambiguous copies instead of silently choosing one.

**Game crashes after patching** — Report the issue. Include `build_report.json`.

## For translators

If you want to contribute translations, see `docs/translator/` for:
- `STYLE.md` — translation style guide
- `glossary.json` — character names, series, terms
- `voice_cards.md` — how each character speaks
- `bible/` — episode summaries

## License

This is an unofficial fan translation. Super Robot Wars OE is © Bandai Namco.
Do not distribute the original game files — this patch contains only translation data
and tools. You must provide your own legally obtained game copy.