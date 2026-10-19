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

Owner UI QA follow-up (2026-10-19): the snapshot now includes57 source-bound compact
label/spelling corrections and22 recovered structured base mission-note fields.
The original PL3 return hash remains historical provenance, NOT a claim that
owner UI corrections were in that archive. Separate plans/hashes are recorded in
`snapshot.json` under `owner_ui_corrections`; see `docs/pl/UI_QA_2026-10-19.md`.
Full `Skupienie` stays unchanged; its repair is a guarded executable cache-layout
fix, not a snapshot abbreviation. These changes have offline gates; owner runtime
confirmation is pending.
