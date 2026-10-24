# SRW Z project — agent instructions

Read the root [`../AGENTS.md`](../AGENTS.md) first (mandatory PR/checkpoint
workflow, multi-title rules), then this file, `README.md`, `docs/STATUS.md`,
`docs/PRIOR_ART.md` and the latest entries of `docs/EXPERIMENT_LOG.md`.

## Scope and independence

- All SRW Z work stays under `srw-z-translation/`. Never mix SRW OE paths,
  hashes, packages or status notes into this project (and vice versa).
- The only planned cross-project input is shared SRW terminology: import it
  later as a deliberate, documented glossary export — never reach silently
  into `srw-oe-translation/` internals.

## Game data handling (OE model, owner decision 2026-10-24)

- The owner's `SLPS-25887` ISO (~3.7 GB) stays on the owner's PC. **Never**
  ask for it, never download it to the sandbox, never commit it or any
  extracted game file, save, screenshot or derived build.
- Work in the sandbox on individual extracted files from the owner's Drive
  tree (`SRW/SRWZ/rozpakowane ISO`). Download only the files a given step
  needs, into the ignored `local/`; record Drive ID, size and SHA-256 in
  `docs/EXPERIMENT_LOG.md` or a receipt before processing them.
- Deliverables that touch the real image are owner-side kits (`PATCH.bat` +
  tools + translation package). The kit must write a **new** image and
  never modify the owner's original in place; it should print/keep logs and
  hashes the owner can send back.
- Runtime claims require owner evidence (PCSX2 screenshots/logs). Label
  everything else confirmed / hypothesis / unknown.

## Upstream (retro-trans) rules

- `vendor/retro-trans/` is pinned at commit
  `fed4c8b910028e964c5c6de87b2d58b3b92628b9` (MIT; see its `LICENSE` and
  `PROVENANCE.md`). **Do not edit vendored files in place.** Put our
  wrappers/adapters in `tools/`; if a vendored file ever must change,
  record the patch and reason in `PROVENANCE.md` in the same commit.
- Only an audited core was imported (script pipeline + docs). Import further
  upstream tools only when a step needs them, after the same audit
  (dependency closure; no personal absolute paths; no embedded translated
  text we would end up reusing). `analysis/` ( incl. the English script) is
  fetched pinned only when building translator views, with hashes recorded.
- The Polish translation is written fresh from Japanese. The retro-trans
  English text is a translator *reference column* (owner-approved), never a
  translation source to copy phrasing from.

## Technical gates

- No translation production until the phase-1 proof passes: extract →
  apply-unchanged → byte-identical extent + pointer verification, first in
  the sandbox on the extracted `DATA/stage.bin` (sparse virtual image at
  LBA 1651029 × 2048), then owner-side on the real ISO via the bat.
- The upstream tools rewrite the script extent **in place, same size**
  (3,910,128 B). Any future step that would grow a file beyond its ISO
  extent or use disc slack is a separate design decision — document it
  before building it.
- Font work happens on a copy of the extracted `SLPS_258.87`. Both routes
  (fullwidth remap; half-width/VWF GS injection per vendored
  `CUSTOM_FONT.md`/`VWF.md`) stay open until the owner sees a prototype in
  PCSX2. Polish coverage must include ą ć ę ł ń ó ś ź ż and capitals.
- Until a committed translation-package policy exists for this title, full
  extracted Japanese script dumps stay in `local/`/Drive, not in Git.
