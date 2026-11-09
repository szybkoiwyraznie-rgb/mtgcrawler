# Dodatek 8.1 — domknięcie scen, których v8 nie miało

**Data:** 2026-11-06. **Wydanie:** `SRW_Y_PACZKA_v8_1_DODATEK.zip` (20 312 B,
SHA-256 `f71e2487…96cbab`), Drive `12RvGQT8hhXBl9vTKobMCsq_BiuyW6mqM`
(folder projektu `1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`).

## Co było nie tak

Paczka v8, którą tłumacz ma na dysku (`plik_dla_tlumacza_v8.zip`), zawiera
**611 scen i 116 056 elementów**. Korpus gry ma 615 scen i — po dodaniu japońskiego
z paczek właściciela — 116 359 elementów z tekstem japońskim. Różnica to **299 elementów
w 6 scenach**, do których japoński dotarł po zbudowaniu v8.

Liczby mierzone są na wydanej paczce, nie na szablonie w repozytorium. Szablon
`translations/template-v8/` ma 611 scen, ale 116 187 linii japońskich (liczy też linie
bez slotu `PL:`), więc wyliczony z niego zapas (172 elementy) był za mały. Pierwsza
wersja tego dokumentu opierała się właśnie na szablonie — to był błąd i jest tu opisany,
żeby nikt go nie powtórzył: **mierzymy na `plik_dla_tlumacza_v8.zip`**.

## Co jest w dodatku

| Scena | Klucz | Elementy | Skąd |
|---|---|---|---|
| D1/6 | `cse20_2000_0106300a` | 149 | `m2000_0106300` 街角に微笑むは / A Smile on the Street Corner, DLC 1 — w v8 scena 404 jest pustą sekcją |
| D2/6 | `cse20_2010_0201710a` | 2 | `m2010_0201710`, dwie linie nieobecne w tekście v8 (v8 ma 275 z 276 elementów) |
| D3/6 | `cse20_3000_0100000a` | 38 | `m3000_0100000` 予兆 / Omen, DLC 2 — scena 435 |
| D4/6 | `cse20_3499_0107410a` | 87 | `m3499_0107410` サバイバル・ミッション2, DLC 2 — scena 436 |
| D5/6 | `cse20_3738_0999900a` | 20 | `m3738_0999900` アシストトーク：イーリス / Assist Chat: Iris, DLC 2 |
| D6/6 | `cse20_8000_0000300a` | 3 | scena bez wpisu misji |

Razem **299 elementów**: 279 slotów do wypełnienia i 20 jawnych powtórzeń
(`repeat`, wypełniają się z wcześniejszego wystąpienia tego samego tekstu).

Wiersze dodatku leżą w `data/package_appendix_y.json` (299 rekordów: `id`, `scene`,
`kind`, `string_id`, `why`). Plik dla tłumacza powstaje z nich przez
`tools/build_package_appendix.py --write`, a paczkę składa `tools/build_appendix_kit.py`.

## Dlaczego osobny plik, a nie wpisanie w odcinki

Numeracja elementów w v8 jest pozycyjna: wstawienie 149 kwestii w scenie 404 przesunęłoby
wszystkie późniejsze numery, a tłumacz ma już wypełnione linie `PL:`. Dlatego dodatek ma
**własną numerację** (`Scena D1/6 … D6/6`, elementy od 1 w każdej scenie) i jest osobnym
plikiem obok `odcinek-*.md`. Żaden numer w v8 się nie zmienia; żadna wypełniona linia
`PL:` się nie przesuwa.

## Gdzie mieszkają nowe dane

`data/s6-full/scenario.jsonl` jest **przypięty sumą SHA-256** do
`data/reading-index-sourcebound.json` (`compaction.source_sha256`). Zmiana tego pliku
unieważnia indeks czytanek, a indeksu nie da się odtworzyć bez pełnego indeksu
z maszyny właściciela. Dlatego:

* `data/s6-extra/scenario_y.jsonl` — wiersze scen, których w korpusie nie było (20 wierszy
  `cse20_3738_0999900a`),
* `data/s6-extra/jp_overrides_y.json` — japoński dolany do istniejących wierszy
  (152 wiersze; klucz to `id` wiersza korpusu),
* `tools/s6_extra.py` — `patch()` dokłada jedno i drugie; `applies()` pilnuje, żeby
  dotyczyło to tylko korpusu projektu, a nie katalogów syntetycznych w testach.

Narzędzia czytające korpus (`build_translator_package.load_scenes`,
`build_missing_data_request`, `pl_import.verify_bindings`, `fill_scene_jp`) przechodzą
przez tę warstwę. Test `tests/test_s6_extra.py` pilnuje, że suma korpusu nadal zgadza się
z indeksem i że dodatki nie przeciekają do przypiętego pliku.

`tools/fill_scene_jp.py --write` zapisuje teraz do `data/s6-extra/jp_overrides_y.json`,
nie nadpisuje korpusu.

## Zwrotka

Tłumacz odsyła **tylko** `odcinek-99-dodatek.md` (nazwa bez zmian). Manifest
`translations/patch-v8-1/import_manifest.json` (schemat 2, 299 elementów) jest w repo,
więc `tools/pl_import.py` przyjmie zwrotkę po sprawdzeniu sum plików i zgodności wierszy
z korpusem razem z dodatkami. `python3 tools/build_appendix_kit.py --check` porównuje
wydaną paczkę ze źródłem.

## Czego nie zrobiono i dlaczego

* **Nie przenumerowano v8** (wariant „v9”): 1 724 linie w 15 scenach bazowych
  przesunęłyby się, a tłumacz musiałby zacząć od nowa.
* **Nie przebudowano całej paczki jako 8.1**: zwykły rebuild nie odtwarza v8 —
  gubi linie `- misja:` / `- tytuł misji:`, pomija `dlc-FreePatch.md` oraz
  `widoki/09_grupy_bez_mowcy.md` i przenumerowuje sceny `/611` → `/615`.
  Wydanie całej paczki zmieniłoby to, co tłumacz już ma na dysku.
* **Nie wpisano dodatku do `translations/template-v8/`**: szablon jest zamrożony
  i podpisany w `SHA256SUMS` — to referencja, po której sprawdzane są zwrotki PL1.
  Dodatek ma własny katalog `translations/patch-v8-1/`.

## Stan testów

`python3 -m pytest -q tests/` → **774 passed, 4558 subtests passed** (plus
`tests/test_s6_extra.py` i `tests/test_package_appendix.py`). Wcześniejsze czerwone testy
odtwarzalności PL2 (`tests/test_reading_rebuild.py`) były skutkiem podmiany korpusu —
po przeniesieniu dodatków do `data/s6-extra/` znów przechodzą.
