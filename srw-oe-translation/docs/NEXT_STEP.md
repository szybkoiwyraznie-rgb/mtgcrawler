# Next step — current state and open work

**Updated 2026-10-17 (UTC).** This page replaces the old "superseded plan" notice.
It lists only what is still open; the delivered products are frozen snapshots and
must not be regenerated or re-uploaded without a new owner request.

For format knowledge and tooling read [`HANDOFF.md`](HANDOFF.md); for the last game-QA
delivery read [`QA_V17.md`](QA_V17.md); the running log is
[`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md), and the newest entries are at the top of
[`STATUS.md`](STATUS.md).

## Delivered — do not redo

| Product | State | Where |
|---|---|---|
| Game patch kit **v17** | delivered 2026-10-17; offline/extracted-kit checks pass; **owner runtime confirmation pending** | [Drive](https://drive.google.com/file/d/1TnJziZix9DxrC5XykEZM1vC0ujTBAjaw/view), 7,245,833 B, SHA-256 `5afdd00fec393edba9bc76371e4283cc17c5cc90cd05eab0b6a711b7bec87937`; GitHub tag `patch-v17` |
| English **reading edition**, story episodes **00–34** | complete; 35 individual episodes + batch archives on Drive | [`reading-script/README.md`](reading-script/README.md), folder `English reading script` |
| **Mech catalogue** presentation **v3** | delivered 2026-10-18 (owner's a–h list); identical model to v1/v2 | [Drive](https://drive.google.com/file/d/1h32WYqZ9SfrzO5BseooIdLzBNhNns-nt/view), 667,590 B; [`mech-catalog/README.md`](mech-catalog/README.md) |

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
