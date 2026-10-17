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

## Verification baseline in the agent sandbox

This checkout has **no game files**: `local/`, `google_drive/` and any ISO/EDAT are
absent by design. Only offline/synthetic checks can run here.

```sh
cd srw-oe-translation
python3 -m unittest discover tests      # 1,474 tests, OK (25 skipped), ~43 s
```

`pytest` is not installed in the sandbox. Delivery documents report 1,493–1,509
passed under their own pytest environment; the different count is a runner
difference, not a failing suite. Real-input tests skip without the private
originals (this is expected).

## Before starting new work

1. Make a checkpoint commit and push to the session branch; reuse its PR.
2. Confirm with the owner which scope is wanted: owner-side v17 QA feedback,
   the simulator reading companion, or a deeper catalogue pass.
3. Never commit ISO/EDAT/CPK/BIN/saves/screenshots; exchange them via Drive and keep
   outputs under ignored `local/`.
