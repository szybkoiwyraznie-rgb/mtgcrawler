# Aktualny częściowy przekład PL do automatycznych wydań

**Najnowszy import PL4 (2026-10-20):** wszystkie widoki i epizody00–21.
Ścisły import:67,143 jawnych pól,0 odmów/obcych/duplikatów; readback0 różnic.
1,283 wiązań naszych lokalnych poprawek UI oraz32 osobnych tytułów/uwag misji
zachowane. 57 zapisanych poprawek pamięci przejrzanych. 28,078/28,079 widocznych
elementów epizodów00–21 wypełnionych (jeden pusty rekord to biały znak JP).
Łączna walidacja:87,794/109,176 wierszy wypełnionych,0 twardych błędów,
25,165 miękkich ostrzeżeń. Nie ukończono epizodów22–34/symulatora ani runtime QA.
Szczegóły: `docs/pl/PL4_RETURN_REVIEW.md`.

Poprzednie źródło: sprawdzony import `PL3.zip` (2026-10-19); jego skróty i UI
pozostają zachowane. Ten katalog służy do kontroli wersji i budowania wydań.

- `polish.jsonl`: wyłącznie polskie teksty i wiązania do źródła; bez JP,
  pełnej kopii pakietu EN, archiwum tłumacza i bez binariów gry.
- `snapshot.json`: wersja schematu, SHA256 i pochodzenie zwrotu.
- Identyfikator wiersza nie zawsze jest unikalny w odziedziczonym pakiecie.
  Wiązanie obejmuje plik i hash wszystkich metadanych poza EN/PL/polami roboczymi.
  Zmiana samego brzmienia EN nie kasuje PL. Zmiana JP/offsetów/roli powoduje
  jawne zatrzymanie wydania zamiast przyłączenia starego tekstu do nowego źródła.

Materializacja, offline (nie potrzebuje Drive ani gry):

```sh
python tools/pl_release_package.py materialize --base pakiet_EN --stored pakiet_PL --out local/pakiet_PL
python tools/build_distribution.py --lang pl --package local/pakiet_PL --version WERSJA
```

`local/pakiet_PL` musi być nowym katalogiem. Samo `build_distribution.py --lang pl`
również materializuje bieżący snapshot w katalogu tymczasowym. Puste PL nie mają
fallbacku do EN; nowo dodane źródła pozostają nieprzetłumaczone.

Aktualizacja po kolejnym zwrocie: ścisły import do kopii pakietu, walidacja,
pomiary normalnym builderem na prywatnych oryginałach, dopiero potem:

```sh
python tools/pl_release_package.py snapshot --base pakiet_EN --package local/SPRAWDZONY_PAKIET --out local/NOWY_SNAPSHOT --source-name PL4.zip --source-sha256 SHA256_ZWROTU
```

Porównać nowy snapshot, zastąpić dwa pliki danych w tym katalogu i wnieść w PR.
Nie wykonywać skryptów z pamięci tłumaczeń i nie commitować zwróconych ZIP-ów.

Stan nie jest pełnym ani w całości przetestowanym w grze tłumaczeniem:
widoki/cytaty i epizody00–03 zaimportowane; dalsza fabuła częściowo pusta.
Rodzaj gramatyczny niektórych cytatów, zgłoszone158 złożeń i układ dłuższych
linii pozostają do przeglądu tłumacza/runtime QA. Snapshot nie usuwa tych uwag.

Historical v2.2 owner UI QA follow-up (2026-10-19): the snapshot now includes57 source-bound compact
label/spelling corrections and22 recovered structured base mission-note fields.
The original PL3 return hash remains historical provenance, NOT a claim that
owner UI corrections were in that archive. Separate plans/hashes are recorded in
`snapshot.json` under `owner_ui_corrections`; see `docs/pl/UI_QA_2026-10-19.md`.
Full `Skupienie` stays unchanged; its repair is a guarded executable cache-layout
fix, not a snapshot abbreviation. These changes have offline gates; owner runtime
confirmation is pending.

Current **v2.4-PL3-UI** owner batch (2026-10-19): v2.3 full Skupienie/details
now owner-confirmed working without crash. The accepted14-word tail buffer/native
font stay unchanged. Latest925source-bound corrections add template join spaces
(audited120Spirit/1985Skill fields), compact Results/drop/Search labels and English
on proven PSP SYSTEM-font consumers. PL-only atlas geometry clears stale header
glyphs; EN render unchanged. Skill00216488<=216768 B. These are not new literary
translation or all-screen runtime approval. See `docs/pl/UI_QA_THIRD_2026-10-19.md`
and its two verification/delivery receipts. Current owner PPSSPP ISO path: replace
ISO only, **no DLC/PBOOT recopy**. Cold-start visual approval of this batch pending.

Model-viewer v2.5-PL3-UI supplement:4source-bound standalone sysmes edits only:
unit switch `Zmień jedn.` (two whole-root copies), rotation `Obr.`, SELECT `Ukryj`.
Existing control semantics unchanged. No changes to long help text, executable,
font, descriptions, DLC rows or reading editions. Physical readback isolates4
strings; all other resources byte-identical to v2.4. See
`docs/pl/UI_MECH_VIEWER_2026-10-19.md`. Current owner ISO loader: replace ISO only,
no DLC/PBOOT recopy. Visual confirmation remains pending.

Latest **PL4 Enemy Robots type-caption correction** (2026-10-20): the Zaku screenshot prompted an audit of every `「…」タイプ` leftover in the extracted RoboDictionary sources. The package contains 18 distinct weapon/type captions across 36 config/imenu mirror rows; four Zaku rows were added in the first pass and 32 more exact source-bound rows in the follow-up. This includes the Char red Zaku unit, which reuses the machine-gun/bazooka captions rather than introducing a third unique footer. All 18 Polish strings fit their measured source byte budgets and route through the normal `table_write` path. Other generic leftovers remain quarantined. Snapshot: 36 caption rows total; **runtime/physical ISO build not tested**. See `config/pl/ui-robot-type-captions-2026-10-20.json` and `docs/pl/UI_ROBOT_TYPE_CAPTIONS_2026-10-20.md`.

Latest **v2.6-PL3-UI** (2026-10-20): seven-screen owner batch delivered.
100existing source-bound PL fields changed (90Spirit names/9sysmes/1terrain),
10missing title copies at344/40B promoted with ENempty and accepted menu PL.
All527physical menu/ext titles independently audited/read back, all20Spirit
families/60records/180name aliases reviewed. Compact7cells except accepted full
Skupienie9; effect prose, parameters, cache/font code unchanged. Source snapshot
65598entries.1724tests OK/2skip; visual fit still pending owner confirmation.
Current PPSSPP1.20.4 upgrade: ISOYES/DLCNO/PBOOTNO recopy. See
`docs/pl/UI_SIX_2026-10-20.md`, `pl3-ui-six-delivery.json`.
