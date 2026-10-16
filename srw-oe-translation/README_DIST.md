# Super Robot Wars OE — English Translation Patch

Fan translation of **Super Robot Wars OE** (PSP) from Japanese to English.

> **Status:** The game is fully translated — all menus, UI, items, skills,
> character names, battle quotes, and story dialogue (chapters 1–8) are in English.

---

## What you need

| Requirement | Notes |
|---|---|
| **Game ISO** | `SRW OE 1.08.iso` — your own legally obtained copy |
| **DLC files** (optional) | Decrypted DLC folder (`NPJH50521`) for chapters 2–8 |
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
   | `DLC\NPJH50521\` | Copy to `memstick\PSP\GAME\NPJH50521\` |
   | `build_report.json` | Technical details (not needed for playing) |

4. **Play!** Load `patched.iso` in PPSSPP.

## Folder structure after unzip

```
SRW-OE-Patch/
├── PATCH.bat              ← double-click this
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
- Not enough disk space (~500 MB free recommended)

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