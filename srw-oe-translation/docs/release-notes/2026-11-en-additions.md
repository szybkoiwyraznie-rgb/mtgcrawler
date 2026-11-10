## English patcher — what ships in this build (PR #33)

This is the technical-parity English release: every technical correction that
went into the Polish kit between 2026-10-19 and 2026-11-10 is now also in the
English package, plus one terminology alignment. Story text is intentionally
untouched — the game already ships in English; the language layer is out of
scope by design.

**Text & slots**

- Mission-select bottom bar: all mission titles shortened to fit the 32-cell
  slot established by the Polish kit (57 rows). The editorial English reference
  set was renewed to match (25 episode editions re-pinned), so the Polish
  reading build and its audit chain keep working.
- Mission notes & Reference: 72 previously empty English strings filled in
  (32 mission-note slots — e.g. the chapter-1 cards — and 40 Reference /
  Tactics pages, including Stack System and Download Notes).
- Settings tabs and short sysmes pool: captions shortened to the JP-sized
  slots (#31 tabs and shared/half-width variants, 12 rows; plus the v2.6–v3.0
  UI port, ~156 rows) so they no longer bleed into neighboring tabs.
- five-screens UI pass (96 rows): battle top-bar Capture/A-H badges, Bind
  line widths, Coord. Atk / Stun / Detonate trims, Slow/Eva line fit,
  help-bar and status-banner rows; clipboard token-spacing fixes (4 rows).
- sysmes battle top bar: "Action Cmds" → "Acts" (4 cells ≤ the 5-cell Polish
  parity slot).

**Content corrections**

- Download error message: the game showed its own name ("Super Robot Wars
  Operation Extend.") where the Japanese says a full version will download;
  now reads "Download the full version." (4 rows).
- "Eldoran" → "Eldran": 11 skill-description rows and the 4 episode-18
  finale dialogue lines (Le Cain / Asuka / Jin / Koji), matching the
  Japanese エルドラン and the Polish kit.

**By design**

- PSP system-font dialog lines remain byte-identical to the original English
  text (owner mandate).
- Every edit keeps the Japanese line/token structure and CP932 encoding;
  the package passes `translation_check --strict` with 0 errors and the
  reading-script audit chain is green.

**QA status**

- Audited statically only — **no PPSSPP runtime QA yet**
  (`runtime_tested=false`). After patching, start a fresh save and re-test
  the mission-select bar, the settings tabs, and the save-failure/download
  flows; report anything that overflows its slot.

Full audit trail: `srw-oe-translation/docs/EN_PL_PARITY_LEDGER.md` (etapy
1–16) and the port plans in `srw-oe-translation/config/en/`.
