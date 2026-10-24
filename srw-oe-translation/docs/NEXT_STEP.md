# Next step — current state and open work

**PL v4.5 delivered for owner re-test (2026-10-24).**
[`srw-oe-translation-pl-v4.5.zip`](https://drive.google.com/file/d/1LNhc0MhX6xf53CnEn415LpgLHSYiXoI1/view)
`8,764,842 B`, SHA-256 `6a602305…d025`; `48` mission-title rows shortened so that
every title (menu + `*_ext.dat` copy) fits `32` cells in the bottom bar, the Ep. 2
case included (`Ep. 2: Groźba pod ziemią`). UI labels/font/geometry and the story
text are identical to v4.4; coverage unchanged. **Next owner-side: patch from a
clean JP ISO with the v4.5 kit and re-take the mission-select screenshot of Ep. 2**
— that single screen is the whole regression test for this fix. If a title still
touches the badge (e.g. a longer counter on another mission), report it and the cap
can be lowered in one more plan. `runtime_tested` stays `false`. ISO YES / DLC NO
unchanged for the owner's 1.08 path.

**PL v4.4 delivered for owner re-test (2026-10-24).**
[`srw-oe-translation-pl-v4.4.zip`](https://drive.google.com/file/d/18v1dXAeMyhnHOZvDPPjaBBACnXU-7Sud/view)
`8,764,460 B`, SHA-256 `91b83aea…146`; `22` fixes in the extra/simulator
scenes (`evept101`–`evept108` + `eventP*` rows outside the episodes), which
the v4.3 pass did not cover; UI/font/geometry identical to v4.3, coverage
unchanged. **Next owner-side: patch from a clean JP ISO with the v4.4 kit and
spot-check the corrected lines in PPSSPP** — the Kamina/Yoko exchange in the
`evept108`-family scene, the GoShogun line, and (if convenient) the Patlabor
extra missions. `runtime_tested` stays `false`. ISO YES / DLC NO unchanged
for the owner's 1.08 path.

**Extra-scene review scope is now complete for `evept101`–`evept108` and the
`eventP*` rows outside the episode blocks** (`16,725` rows reviewed against
JP/EN and against the accepted rendering of identical Japanese lines; `22`
corrections landed in v4.4, `12` divergent renderings kept as deliberate
context variants). Remaining unreviewed prose categories are the non-dialogue
files: `02_items`, `03_skills`, `05_mission_text`, `06_scenes`, `08_names_*`
bios and `04_config_text` help pages — no decision made yet, ask the owner
first.

**PL v4.3 delivered for owner re-test (2026-10-24).**
[`srw-oe-translation-pl-v4.3.zip`](https://drive.google.com/file/d/1mKWOPN3_ZlE8ye2UR8UFQvtAoIFWYlmD/view)
`8,763,908 B`, SHA-256 `df589843…4d20`; story-language review of episodes
`00`–`34` plus the „Zostaw to mi” sweep (`656` snapshot rows rewritten, `0`
defects left), UI/font/geometry identical to v4.2. Reading archive reissued
with the catalogues bundled (`2,176,460 B`, SHA-256 `1253927d…4e36`).
**Next owner-side: patch from a clean JP ISO with the v4.3 kit and
spot-check corrected lines in PPSSPP (the sweep touched battle quotes as
well as dialogue)** — `runtime_tested` stays `false` until then. ISO YES /
DLC NO unchanged for the owner's 1.08 path.

**Review scope for this session: the extra/simulator scenarios.**
The `00`–`34` review covered `32,156` of the `48,879` dialogue rows. The
remaining `16,723` are outside the reading episodes and have never been
language-reviewed: `evept101`–`evept108` (`15,645` rows — `evept102` `300`,
`evept107` `378`, `evept101` `1,153`, `evept106` `1,547`, `evept103` `2,530`,
`evept108` `2,853`, `evept105` `3,047`, `evept104` `3,837`) and `1,078` rows
in `eventP00`–`eventP32` that fall outside the episode blocks (e.g.
`eventP22` `200`, `eventP09` `97`). Method is the established one: scan for
controlled defect classes, verify every candidate against JP and EN, land
confirmed fixes as source-bound plans through `tools/pl_story_corrections.py`
and re-materialise the whole package before committing. Smallest containers
first; the ledger `pl/PL_STORY_LANGUAGE_FIXES_2026-10-24.md` gains an
“extra scenes” section.

**v4.2 pair delivered for owner re-test (2026-10-24).**
[`srw-oe-translation-pl-v4.2.zip`](https://drive.google.com/file/d/1A7H2VzAo-X7245wmrymxyvJhDGo8f_DD/view)
`8,763,213 B`, SHA-256 `eebf0a1b…64e2` (EN pair `srw-oe-translation-v4.2.zip`
`7,285,821 B`, `64f90885…`, local only). Adds the TXCL geometry alignment for
the English/shared texture captions (`intsys_01` LNK, `intsys_03` upgrade
screen, `intsys_04` EN boxes) on top of v4.1 — see
`pl/pl-v4.2-kit-delivery.json`. **Next: owner re-patches from a clean JP ISO
(v4.2 kit; fresh `patched.iso` + full `DLC\`, normal save after cold boot)
and re-checks the v4.1 screens (Pilot tab, Records & Parts header/footer,
parts conversion panel) plus the upgrade screen captions
(`Unit / Pilot`, `Upgrades`, `Linked Units`, `Support`,
`Upgrade Limit Break`) and — if the EN kit is used — the EN parts screen
(`Owned`/`Convert`/`Progress` now render fully inside their cells at
size 7/6/8).** Until then `runtime_tested` stays `false`. The EN-geometry
item from v4.1 is closed; textures without TXCL cell data (`mensys_*`,
`tacsys_*`, `navisys_*`) remain as-is.

**PL v4.1 kit delivered for owner re-test (2026-10-23).**
[`srw-oe-translation-pl-v4.1.zip`](https://drive.google.com/file/d/1gqGO1nMg-9BC17Mjve4JEQaJiDWaZaDI/view)
`8,762,312 B`, SHA-256 `0775aa2d…813cf`; fixes the three owner-reported v4.0
PPSSPP screens (Pilot-tab labels, Records & Parts header `Postęp`/`Premia`,
Owned footer vs Lv counters) — see `pl/UI_QA_V41_2026-10-23.md` and
`pl/pl-v4.1-kit-delivery.json`. **Next: owner re-patches from a clean JP ISO
(fresh `patched.iso` + full `DLC\`, normal save after cold boot) and
re-checks the same three screens plus the parts conversion panel
(`Warunki`, `Wym.`, `Masz`, `Lista części`).** Until then `runtime_tested`
stays `false` and no runtime claim is made. Open optional item: the EN
`intsys_04` caption boxes have the same latent TXCL mismatch (measured
`80` ink px outside the sampled cells); aligning EN geometry would change
the shipped EN kit and needs an explicit decision. Everything below is
history/open scope from earlier releases.

**PL v4.0 complete; all four derived artefacts republished (2026-10-23).**
[`srw-oe-translation-pl-v4.0.zip`](https://drive.google.com/file/d/1yPe_24aTq0qbBHT_40UGsxIKvIU8_4hC/view)
`8,761,508 B`, SHA-256 `c88f37be5effe5ccc1dbad3b56f01c0c9fd0c9cbd83edbc2a6eef0ff03f46d6a`,
`108,805 / 109,176` rows filled, `0` errors. Rebuilt from the final package and
byte-verified against Drive: mech catalogue `873,130 B` (`07f11deb…`),
pilot catalogue `303,266 B` (`800a27fd…`), mission deployments `11,560,402 B`
(`d166592b…`) and reading archive `917,233 B` (`c295fbe2…`, 35 episodes,
`47,056 / 47,056` prose entries). Superseded v3.5 copies and interim PL3/PL4
archives trashed; `145/145` test modules OK. Receipts: `pl/pl-v4.0-kit-delivery.json`,
`reading-script/polish/PL5_v4.0_reading.delivery.json`,
`reading-script/polish/catalogue-v4.0.delivery.json`, `pilot-catalog/delivery.json`,
`mission-deployments.delivery.json`. The only open item is the owner-side
PPSSPP/runtime check of the v4.0 kit; no runtime claim is made.

**PL4 translator return integrated and source-bound (2026-10-20).** [v2.7-PL4 kit](https://drive.google.com/file/d/1T4EPs_7fbJEyAVLIdCmDYLkEtNcWFViF/view). All nine views and episodes00–21 imported; 67,143 explicit blocks strict-checked/read back, no rejects/unknowns. 28,078/28,079 visible episode elements have PL; the lone empty is structural whitespace. All1,283 local owner-UI bindings and32 promoted mission rows preserved;57 TM correction records match. Overall validator0 hard errors/25,165 soft warnings. New text maps to25 specific DLC EDAT containers; full physical build/outputs and runtime remain pending because original assets are absent here. [Coverage/install limits](pl/PL4_RETURN_REVIEW.md). Do not overwrite user UI/protagonist/cache/font. Episodes22–34/simulator remain incomplete.

**Seven-screen PL UI batch v2.6 DELIVERED (2026-10-20).**
[Download](https://drive.google.com/file/d/1ZYLUYsDd97K1itqHGDqQQTDgX33wGVQg/view).
100existing PL edits (90Spirit name aliases,9sysmes,1terrain),10missing base
mission title copies promoted;527/527physical title slots read back across47
original containers. All20Spirit families/60levels reviewed;7cell compact names,
full accepted Skupienie9 unchanged. Cache/native font and all shipped tools
unchanged; only configst,eventP00,terrain-string slot in EBOOT differ vs v2.5.
1724tests OK/2skip, extracted-kit filtered authentic NONPLAYABLE fixture passes;
44rebuilt DLC files identical and ALL79050DLC-backed source rows identical.
**Owner PPSSPP1.20.4 upgrade: ISOYES (`patched.iso`), DLCNO, PBOOTNO recopy.**
New visual fit still needs owner confirmation; no new cache/font experiment.
See [UI batch](pl/UI_SIX_2026-10-20.md), [receipt](pl/pl3-ui-six-delivery.json).
Catalogue/reading exports unchanged; do not restart them.

**PL catalogue naming revision v4 DELIVERED (2026-10-19).**
[Catalogue](https://drive.google.com/file/d/146dxudsT9vEzGua6s--Z58s_QP8m_yF0/view),
[00–03+catalogue v4 ZIP](https://drive.google.com/file/d/1vslHzkyfkF39ewgIEkhsltDHiUw-tWn0/view).
Roster name first, differing display name in parentheses, identical pair once.
393source-bound pairs;242headers changed,151same; exact non-heading byte proof
preserves all1485weapon rows and descriptions. Four episode files unchanged.
1712tests OK/3skip; both downloads byte-identical. Only reading presentation:
no EN/source/game changes or ISO/DLC transfer. [Receipt](reading-script/polish/catalogue-v4.delivery.json).
Do not restart completed exports or reinterpret this as runtime/game changes.


**Latest model-viewer UI follow-up (2026-10-19): v2.5 delivered.**
[Download](https://drive.google.com/file/d/1lTiINU17MPaHcm1SwOFm-A1zzYkZhic8/view).
Clipped L/R/analog/SELECT labels now `Zmień jedn.`/`Obr.`/`Ukryj`; only4sysmes
physical entries changed. All other text/resources/code/font/skills identical to
v2.4.1705tests OK3skip, normal extracted-kit NONPLAYABLE authentic six-file CLI
and independent readback pass; actual PPSSPP visual check pending.
**ISO YES / DLC NO / no PBOOT recopy** on owner's accepted ISO-loading path.
[Proof and receipt](pl/UI_MECH_VIEWER_2026-10-19.md). Preserve accepted Skupienie/cache/
font; no new hypothesis experiments. Reading00 supplement below remains complete.


**Polish reading supplement (2026-10-19): missing Episode00 DELIVERED.**
[Episode00 PL](https://drive.google.com/file/d/1KEbIEpURPJXpGeAqBsLL-UMPkcXCaLhL/view),
[complete00–03+catalogue ZIP](https://drive.google.com/file/d/1s27uNT-vv2S153m5JTGfsLiUeDUgSQTQ/view).
All253prose rows retained (242dialogue+11narration), independently source-verified;
old01–03/catalogue bytes unchanged.1703tests OK/3skip, both outputs download-back
identical. No story/source/game changes or new translation. ISO/DLC NO changes.
[Details/receipt](reading-script/polish/README.md). Do not restart completed exports.


**Latest owner UI batch (2026-10-19): v2.4-PL3-UI delivered.**
[Download](https://drive.google.com/file/d/1O8p3IdvyTYLLrenmAwhj83613t20Nkjr/view).
Owner NOW accepts v2.3 Skupienie/details without crash; no further cache/font
experiment. New925source-bound fixes: proven PSP SYSTEM consumers stay English,
all120Spirit/1985Skill description fields checked for fragment-join spaces, compact
Results/drop/Search labels, PL-only Parts atlas cleanup with EN render unchanged.
Normal authentic six-file NONPLAYABLE ISO CLI/readback pass;1697tests OK/3skip;
Skill00216488<=216768 (280margin), all numeric mechanics/fragment pools unchanged.
**Current PPSSPP1.20.4 upgrade: ISO YES; DLC NO; no PBOOT recopy for ISO path.**
One cold-start ordinary-save UI check pending (not all-game approval).
[Details/receipts](pl/UI_QA_THIRD_2026-10-19.md). Local EN+PL release pair passes;
GitHub Actions queued at handoff, no claim of CI success/main publication. Older
size/test/runtime-pending notes below are historical, not next tasks to repeat.


**PL3 release (2026-10-19):** partial standalone PL patcher delivered from actual
PL3.zip. Quotes19841/19841, all editable visible views filled (protected/binary
blanks preserved), scenes00–03 fully filled after copies.0 import/validation errors;
634 leading spaces preserved;48326 explicit MD blocks compared after propagation,
0 mismatches. **Physical Skill00215764B (1004B margin)**,8 DLC pools15329B each
(309B margin), extracted-kit CLI on authentic-container NONPLAYABLE fixture0problems.
[Download PL patcher](https://drive.google.com/file/d/1jkVKOzRyy8QE58elwLqezi19-iNXRNGq/view).
EN+PL workflow now tested successfully on GitHub Actions; publishes BOTH only
on main after merge, not from PR. Source-bound PL text snapshot tracked, no Drive
secrets/game data in CI. **PR20 still open; main publication awaits merge.**
1644 tests OK/25 skipped. Quote gender/158 formatting findings/later story/runtime
QA remain open; not a literary/full-game approval. This supersedes PL2's686B
blocker below. See [PL3_RELEASE.md](pl/PL3_RELEASE.md) and its delivery receipt.

**PL2 return (2026-10-18):** audited actual PL2.zip. Leading spaces preserved in
all 634 config fields; all 33 prior join suspects corrected in 1421 format previews.
**Skill00 remains 217454 B vs 216768 (+686 B)**; normal builder refuses it,
no bypass/new oversized test. All eight physical DLC pools build/read back at
15331 B each (307 B margin). Delivered quotes are **11801/19841**, not reported
13460 — request newest MD export before further edits. One glossary full/short
variant to review, no import errors. Fixed EN-only chapter-4 DLC readback for PL.
1626 tests OK/27 skipped; no playable ISO/runtime claim. See
[PL2_RETURN_REVIEW.md](pl/PL2_RETURN_REVIEW.md). Keep translator's literary work;
next: latest MD export and remaining ≥686 B of actual Skill00 savings.

**Masaki v17 update (2026-10-18):** delivered-kit reproduction confirms the
reported JP/EN mix in the config19 dictionary while imenu19 is fully EN. The
global config-side viewer safety gate is the cause of those held-back fields;
not missing translator work. A private existing-cell-only TEST1 for three
characters is delivered and owner-confirmed ("wszystko pięknie przetłumaczone").
Narrow integration is now active automatically in the normal shared **EN and PL**
builder; global gate stays enabled elsewhere. The EN container is byte-identical
to accepted TEST1; PL uses its own source-stamped returned fields (no EN fallback).
[Tools-only updater](https://drive.google.com/file/d/1ssmlgTfscMTp-da2Ou_2t3STjua6h-f2/view)
for both existing kits is delivered; no translations/launchers/game files included.
1620 tests OK/28 skipped; isolated updated-kit EN/PL builds and independent
original-DLC readback pass. No playable ISO/full-game QA here. See
[QA_MASAKI_V17.md](QA_MASAKI_V17.md) and [delivery receipt](masaki-builder-update-delivery.json).

**V5 runtime update (2026-10-18): owner accepts the font on two opening
narration/dialogue screenshots, with no further styling objections.** Missing
Ł/Ś (also Ó) in all-caps headings were ASCII caption literals in the exact delivered
ZIP, not a font defect. Source captions corrected; font/codec unchanged. No new
font build/test requested. [Details](pl/PL_FONT_STYLE.md). Older pending notes below
refer to the state at delivery, not the latest feedback.

**Translator PL audit complete (2026-10-18, PR #20).** Replace the old
`sceny_PL.zip` / `widoki_PL.zip` with checked **v2** archives linked in
[`pl/TRANSLATOR_VIEWS_AUDIT.md`](pl/TRANSLATOR_VIEWS_AUDIT.md).
All 109144 extracted text rows classified: 108761 editable/inherited, 19 protected,
364 unclassified leftovers quarantined (8 necessary leftover roots retained).
Full synthetic PL import/copy/check/build-load passed; 1591 tests OK, 25 skipped.
Tools from `0053e01` or newer are required; use `--lang pl --require-template`.
Next: external translator fills PL only; later validate returned text and runtime
layout. No literary PL translation done; **v5 opening-screen appearance now accepted by owner**.
Manifest: [`pl/translator-views-v2-delivery.json`](pl/translator-views-v2-delivery.json).

> **Latest PL handoff (2026-10-18, PR #20): v4 works; native-style v5 delivered.**
> Four owner screenshots confirm v4 opening prose, dialogue, scene title and unit
> name. Feedback: Polish letters too bold and lowercase bodies too low. The old
> Roboto raster has peak value 15 vs native 9 (lowercase l 6); some bodies start
> at row 5 vs native row 4. [TEST_PL v5](https://drive.google.com/file/d/13tWWoHO6nBSmEVGFj4y46BtDIV2kz3uD/view)
> composes accents over **pixel-identical native ASCII bodies** at build time.
> No game bitmap is committed/shipped; only accent recipes. No scaling/shifting,
> original ASCII remains unchanged. Natural v4 probe sentences are unchanged,
> apart from version labels. 1569 unittest tests OK (25 skipped); isolated actual
> ZIP build/read-back with original-container fixture ISO pass; native-body audit
> catches boldening/shifting/missing marks. **V5 runtime styling is unconfirmed.**
> Details: [`pl/PL_FONT_STYLE.md`](pl/PL_FONT_STYLE.md),
> [`pl/test-v5-delivery.json`](pl/test-v5-delivery.json),
> [`../README_TEST_PL.md`](../README_TEST_PL.md).
> One first-panel or first-dialogue screenshot suffices if evaluating appearance;
> no menu hunt or hypothesis-by-hypothesis rebuild. Full PL translator material
> remains external/pending; no claim of a finished Polish translation.

**Updated 2026-10-17 (UTC).** This page replaces the old "superseded plan" notice.
It lists only what is still open; the delivered products are frozen snapshots and
must not be regenerated or re-uploaded without a new owner request.

For format knowledge and tooling read [`HANDOFF.md`](HANDOFF.md); for the last game-QA
delivery read [`QA_V17.md`](QA_V17.md); the running log is
[`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md), and the newest entries are at the top of
[`STATUS.md`](STATUS.md).

## Delivered — do not redo

| Product                                               | State                                                                                           | Where                                                                            |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Game patch kit **v17**                                | delivered 2026-10-17; offline/extracted-kit checks pass; **owner runtime confirmation pending** | [Drive](https://drive.google.com/file/d/1TnJziZix9DxrC5XykEZM1vC0ujTBAjaw/view), |
|                                                       |                                                                                                 |   7,245,833 B, SHA-256                                                           |
|                                                       |                                                                                                 |   `5afdd00fec393edba9bc76371e4283cc17c5cc90cd05eab0b6a711b7bec87937`;            |
|                                                       |                                                                                                 |   GitHub tag `patch-v17`                                                         |
| English **reading edition**, story episodes **00–34** | complete; 35 individual episodes + batch archives on Drive                                      | [`reading-script/README.md`](reading-script/README.md),                          |
|                                                       |                                                                                                 |   folder `English reading script`                                                |
| **Mech catalogue** presentation **v3**                | delivered 2026-10-18 (owner's a–h list); identical model to v1/v2                               | [Drive](https://drive.google.com/file/d/1h32WYqZ9SfrzO5BseooIdLzBNhNns-nt/view), |
|                                                       |                                                                                                 |   667,590 B;                                                                     |
|                                                       |                                                                                                 |   [`mech-catalog/README.md`](mech-catalog/README.md)                             |

The source package [`pakiet_EN/`](../pakiet_EN/) is the translation source of record.
Catalogue-only wording repairs (17 rows) were **not** backported to the game.

## Blocked on the owner

1. **In-game confirmation of kit v17.** Cold start from the new build (not an old
   save state); preserve saves. Points to check: restored player-name markers in
   mission 0-1, `F.`/`O.`/`P-Mv` labels, 21 DLC titles, the `Basic Training` card,
   the `Space Str.` terrain label and the two chapter-4 DLC records.
2. **If the two DLC titles are still Japanese** in the activation popup, run
   `CHECK_DLC.bat` against the **installed** DLC folder and return
   `DLC_TITLE_CHECK.json`. The cause on the owner's machine is not proven; the kit
   already reproduces both title fields as English in the source build, so another
   translation-only edit is not justified yet.

No new build should be produced until this feedback arrives.

## Open scope, not blocking — do not silently expand

- **Simulator scenes.** 36 `simulator` scenes / 108 dialogue rows plus 22 mission
  titles in `05_mission_text.jsonl`. They are a separate reading scope, not part of
  the numbered story 00–34. Almost all prose is a shared briefing line plus win/lose
  conditions; a reading edition would be a small companion, not new translation.
- **Catalogue limits** (documented and intentionally visible): 20 unrecorded series;
  skill references `110` (unit 10115) and `230` (unit 491) unresolved; exact gate
  unlock missions not decoded; 115 empty native-skill slots (not proof of no
  effects); no full battle simulation or scenario-specific reassignments.
- **Distribution/legal model.** The current model is a patch applied to the user's
  own matching files; the final format (xdelta vs. kit) and legal review are
  undecided. Game data is never published to GitHub.
- **Package decode noise.** Rows whose ID starts with `leftover:` and fields that
  decode as isolated kanji/half-width fragments are known binary/decode artifacts.
  Do not present them as translated user-visible text, and do not "fix" them without
  evidence from the container structure.

## Potential translation gap found 2026-10-17 — evidence needed before editing

Running the release gate over the package finds **149 empty `en` rows** (known count,
but never classified):

```sh
python3 tools/translation_check.py --package pakiet_EN --require-complete
# 109,144 rows, 108,995 filled, 149 empty, 149 errors, 3,241 notes
```

All 149 are outside the accepted story text: 143 in `04_config_text.jsonl`
(103 `config_dlc_id`, 40 `config_reference`), 2 blank dialogue rows whose `jp` is a
single space, and 3 executable rows. **Every one of the 143 config rows is in
`config01`–`config08`; `config00` has zero empties.** Of those, 35 repeat a Japanese
string that is translated in another row, and **108 unique strings have no English
copy anywhere in the package**. They include:

- chapter-download descriptions ("Download the Chapter 2 main story…");
- additional-mission / unit / simulator download descriptions;
- in-game help pages such as the **stack-unit system** and **download notes**, which
  occur only in `srwDL_Reference03/08`, not in `srwDL_Reference00`.

Hypothesis, **not proven**: the game may read the chapter-specific `configNN`
reference/DLC tables, in which case those help pages and download texts stay Japanese.
The 2026-10-17 owner report covers only two DLC titles and one terrain label, so this
was not observed in game. Do **not** translate or rebuild these rows on the strength
of the file layout alone: first establish which `configNN` tables the game actually
displays (runtime check or container-read evidence), then translate the confirmed
subset with the established terminology and rebuild a kit.

**Decision needed from the owner before this becomes work.**

## Verification baseline in the agent sandbox

This checkout has **no game files**: `local/`, `google_drive/` and any ISO/EDAT are
absent by design. Only offline/synthetic checks can run here. (During the 2026-10-18
Polish stage the seven USRDIR originals were re-downloaded from Drive into the ignored
`google_drive/` and `local/font_ID00000.bin` was re-extracted; both are untracked.)

```sh
cd srw-oe-translation
python3 -m unittest discover tests      # 1,547 tests, OK (25 skipped), ~30 s
```

`pytest` is not installed in the sandbox. Delivery documents report 1,493–1,509
passed under their own pytest environment; the different count is a runner
difference, not a failing suite. Real-input tests skip without the private
originals (this is expected).

## Polish stage (2026-10-18, in progress)

Goal: a full PL pipeline analogous to EN, with the translator work done by an
external specialized model. The agent prepares code and packages only — **no
translating**. Delivered so far (all on the session branch, PR #18):

* `tools/font_pl.py` — appends the 18 diacritic glyphs (ą ć ę ł ń ó ś ź ż + uppercase)
  to `kanji.fta` as slots 3540–3557 and points the free JIS row-4 codes
  0x82FA–0x830B at them via `kanjiL.tbl`. Full round: `font.cpk` →
  `local/font_pl.cpk` (identity gate on the original passes, read-back verifies
  all 18). Composing art = the game's own `ank.fta` Latin glyphs + a drawn mark.
* `tools/pl_text.py` — the PL codec: 18 letters ⇄ private two-byte codes, rest CP932
  (both directions fail closed; the codes are illegal CP932, so no aliasing).
  `display_width` counts a PL letter 2 (conservative hypothesis pending in-game test).
* `tools/apply_strings.py --lang pl`, `tools/translation_check.py --field pl`
  (exe/terrain rows stay CP932/ASCII-strict on purpose).
* `tools/pl_package_build.py` + `docs/translator_pl/INSTRUKCJA_PL.md` — the
  translator handoff. `pakiet_PL.zip` (61 files, 6.3 MB) generated from `pakiet_EN`
  (109,144 rows, `pl` field added) and uploaded to Drive as `pakiet_PL_v1.zip`.
  This **supersedes the obsolete `widoki.zip`/`sceny.zip`** packages.
* `tools/text_codec.py` + writer funnel points (`event_text_apply`, `table_write`,
  `item_skill_write`, `sysmes_pack`, `gim_label` caption pick) —
  `build_translation_patch.py --lang pl` maps `pl`→`en` at load, encodes through
  the PL codec, and runs `font_step` (extends the ISO's `font.cpk`, queued for
  `patched.iso`; needs `--iso`; honors `--only/--skip`). `--views` is refused
  under `pl` (that import path is EN-only). `exe_strings` is untouched: a PL
  letter in an exe row is refused with a reason (fail closed until proven).
* Kit: `PATCH_PL.bat` (file/folder pickers, same flow as EN) +
  `README_DIST_PL.md` + `build_distribution.py --lang pl` →
  `local/release/srw-oe-translation-pl-v1.zip` (88 files). Built with the still
  empty package — runnable today: the font patch alone can be checked in game.

### Translator handoff v2 (2026-10-18, owner's correction)

The JSONL handoff (`pakiet_PL_v1.zip`) was **rejected by the owner**: the package
for the translator must have *exactly the same shape as `sceny.zip` and `widoki.zip`*
— md files with context, speakers, expected lengths — because the translation is
to be literary and context-embedded, not purely technical. Delivered:

* `scene_view.py --lang pl` / `table_view.py --lang pl` — render the same views
  as the EN flow, with the English kept as a read-only `EN:` reference block and
  the empty `PL:` slot under it (headers adjusted, zip named `sceny_PL.zip` /
  `widoki_PL.zip`, the instruction rides along as `INSTRUKCJA_PL.txt`).
* `translation_import.py --lang pl` — parses the `PL:` blocks in parallel to
  `EN:`, validates with `TC.check_row(..., field="pl")`, writes `row["pl"]`, and
  never touches `en` (the reference). Round trip pinned by
  `tests/test_translation_import.py::PolishFlowTest` (7 tests).
* Generated from `local/pakiet_PL` and uploaded to Drive (folder `SRW OE`):
  `sceny_PL.zip` (38 files, 2.8 MB) and `widoki_PL.zip` (8 files, 1.2 MB);
  the instruction also lives in `docs/INSTRUKCJA_WIDOKI_PL.md`.

### Small in-game PL test (2026-10-18, owner's request)

Before any full patch, the owner wants a test patcher that swaps the elements of
the ISO so Polish subtitles and font are visible at the start of mission 0-0, in
the Exart mech description and its weapons. Delivered:

* `tools/test_pl_package.py` → `local/test_PL`: the real package with **probe
  texts** (no translation) in `pl` for the opening of mission 0-0 (dialogue rows
  1–16 of `eventP00.cpk/DL100_01.bin`: narration, location header, Seishiro and
  Himari lines, the `＜主人公名＞` token row), the mission title, and the Exart
  name/display/8 weapons in `config00.cpk`. `translation_check --field pl`:
  36 filled rows, 0 errors. Empty `pl` rows are skipped by the build (original
  bytes stay), so nothing else changes.
* `TEST_PL.bat` + `README_TEST_PL.md` — the test kit
  `local/release/srw-oe-test-pl-v1.zip` (87 files; tools carry all fixes below),
  uploaded to Drive. It patches **only** `eventP00.cpk config00.cpk font.cpk`
  (`--only ... --no-ui-textures`, no DLC) into `output/patched.iso`.

**PL bugs found by the e2e and fixed** (the font-only kit v1 never exercised
these paths): the 18 PL codes are 0x82FA–0x830B, so `ś` (0x8300) carries a
literal NUL trail — every reader that NUL-split a text broke on it.

* `text_codec.cstring(data, start, end)` — Shift-JIS-aware NUL-terminated read
  (a NUL that is the trail of a double-byte char does not terminate); used by
  `event_text_apply` (`text_of`, `text_start_of`, `_text_spans`, `_map_inside`)
  and `name_table_write.cstring`. For valid SJIS/ASCII input the result is
  byte-identical to the old `split(b"\x00")[0]`.
* `text_codec.decode()` added (pl ⇄ cp932 per lang); `slot_text_apply` now
  encodes through `text_codec` instead of hardcoded cp932.
* `build_translation_patch._advance` shrinks the summary in the no-change
  branch too (raw bytes in `detail` crashed the JSON report dump).
* `slot_apply` (the orchestrator's slot writer) was audited: it writes through
  `TW.encode_en` (codec-aware) and verifies by byte windows, so it was already
  PL-safe — pinned by `tests/test_slot_apply.py::PolishSlotTests`.
* New e2e: `tests/test_pl_build.py::OnlyFilterPlTests` — synthetic containers
  in the real formats (DL100_01.bin narration+dialogue, config00 unit_list +
  wp_list with the Exart records, the font container), full
  `BTP.build(..., only=(eventP00, config00, font), lang="pl")`, readback of the
  PL bytes from `patched.iso`, plus the negative test that `font.cpk` must be
  listed in `--only` for the font step to run.
* Suite: **1,547 tests OK (25 skipped)**.

Waiting on the owner: (1) run `srw-oe-test-pl-v1.zip` → `TEST_PL.bat` on the
real ISO and report whether all 18 letters render (and which do not, and where:
subtitles / mech name / weapon names); (2) the filled `sceny_PL`/`widoki_PL`
md files back from the translator. After both: import with
`translation_import.py --lang pl`, commit `pakiet_PL/`, rebuild the full kit,
release.

### Notes for the full PL patch (not needed for the test)

The remaining NUL-split readers (`table_write`, `item_skill_write`,
`config_text_tables`, `mission_text`, `event_dialogue` extractor,
`slot_text_apply.read_slot` for re-reads) have not been audited for the 0x00
trail of `ś` — none of them is on the test kit's path (event writers, name
cells, font, byte-window verifies). Audit them before the first full PL build
that fills 02/03/04 rows.

## Before starting new work

1. Make a checkpoint commit and push to the session branch; reuse its PR.
2. Confirm with the owner which scope is wanted: owner-side v17 QA feedback,
   the simulator reading companion, or a deeper catalogue pass.
3. Never commit ISO/EDAT/CPK/BIN/saves/screenshots; exchange them via Drive and keep
   outputs under ignored `local/`.

Polish reading/reference handoff (2026-10-19): episodes01–03 and catalogue v3
are now delivered and verified, not pending work. See
`docs/reading-script/polish/README.md` / `delivery.json`. Do not regenerate or
retranslate them unless the owner asks or returns corrected PL source. The
existing translator/QA follow-up remains separate; this export changes no game.
