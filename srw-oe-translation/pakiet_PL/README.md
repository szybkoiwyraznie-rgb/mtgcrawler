# Aktualny częściowy przekład PL do automatycznych wydań

Źródło: sprawdzony import `PL3.zip` (2026-10-19). Ten katalog jest przeznaczony
do kontroli wersji i budowania wydań na prośbę właściciela projektu.

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
