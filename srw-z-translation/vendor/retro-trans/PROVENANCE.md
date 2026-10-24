# Vendored upstream: retro-trans/SRW-Z

- **Source:** https://github.com/retro-trans/SRW-Z
- **Pinned commit:** `fed4c8b910028e964c5c6de87b2d58b3b92628b9`
  ("Document SRW Z English v0.9.88 release")
- **Imported:** 2026-10-24, into `srw-z-translation/vendor/retro-trans/`
- **License:** MIT (see `LICENSE` in this directory; upstream scope covers
  the tools, docs and the English text data in their `analysis/`).
- **Local modifications at import:** none — files are byte-pinned copies.
  Only `README.md` was renamed to `UPSTREAM_README.md` to avoid clashing
  with project documentation.

## Imported paths (19 files, 180,088 B)

- `tools/` — the 7-file dependency closure of the script pipeline
  (66,772 B): `extract_script.py`, `apply_script.py`,
  `verify_pointers.py`, `scan_visible_defects.py`, `build_compare.py`,
  `banlz.py`, `rewrap_dialogue.py`.
- `docs/` — all 9 upstream documents (`BASE_RULES.md`, `CUSTOM_FONT.md`,
  `DEBUGGER_TRACE.md`, `FINDINGS.md`, `LZ_FORMAT.md`, `RENDERER.md`,
  `STANDARD_RELEASES.md`, `TECHNICAL.md`, `VWF.md`).
- `LICENSE`, `TRANSLATING.md`, `UPSTREAM_README.md`.

## Deliberately not imported

- The remaining upstream tools (~269 Python one-offs + 6 PowerShell
  helpers): many embed English string data, and three contain the
  upstream author's personal absolute Windows paths
  (`build_texture_pack.py`, `gen_intro_cards.py`, `zkn_deepseek.py`).
- `analysis/` (~26 MB, incl. `english_script.json`, `glossary.json`):
  fetched pinned only when translator views are built (phase 2), with
  hashes recorded in `../../docs/EXPERIMENT_LOG.md`.

## Rules

- Do not edit vendored files in place. Our adapters live in `../../tools/`.
- Any future import from the same pinned commit (or a deliberate re-pin)
  must update this file and `../../docs/EXPERIMENT_LOG.md` in the same
  commit, after the audit: dependency closure, no personal absolute
  paths, no proprietary game data.
- Audit evidence for this import: `docs/EXPERIMENT_LOG.md` entry
  2026-10-24 (closure computation, byte counts, `ast` parse of all 7
  tools, personal-path scan of the imported set = none).
