# Pakiet dla tłumacza — część wewnętrzna (stan prac i kuchnia techniczna)

Ten plik **nie idzie do tłumacza**. Instrukcja dla niego to `docs/TRANSLATOR_PACKAGE.md`
(wgrywana na Dysk jako `README.md`). Tu trzymamy to, co wcześniej siedziało na końcu tamtego
dokumentu jako rozdziały 6 i 7 — żeby instrukcja była czysta, a wiedza nie zginęła.

## 1. Stan prac (co jest gotowe, a co nie)

* **Do przetłumaczenia**: 96 698 elementów — 83 536 z linią `EN:` (39 424 fabuła + 44 112 widoki)
  + 13 162 dziedziczone (8 016 kopii scen DLC + 5 146 powtórzeń w widokach). Widoki są gotowe
  i czekają.
* **Tłumaczenie w grze** — działa wtryskiwanie przedmiotów oraz **dialogów, narracji i tytułów
  misji** (sprawdzone na roboczej kopii: cała scena 1 — 88 linii dialogu/narracji + 15 tytułów
  misji; kontener przebudowany i odczytany z powrotem bajt w bajt, bez różnic poza tymi tekstami).
  Kwestie mówców i angielskie linie w grze widział już człowiek (PPSSPP); reszta do pokazania,
  zanim cokolwiek ogłosimy gotowym.
* **Kwestie bez mówcy** — 451 z 27 383 (1,65 %), w ustalonych granicach (≤ 2 %).
* **Nazwy mówców w dialogach** — bez nazwy tylko 2 wiersze z 47 175 (0,0 %); kwestie bez mówcy
  w cytatach: 451 z 27 383 (1,65 %), w ustalonej granicy.
* **Format dystrybucji i ocena prawna** — nadal nieustalone; danych gry nie rozpowszechniamy.

## 2. Kuchnia techniczna

* Pakiet to pliki `00_dialogue.jsonl` … `08_names_units_weapons.jsonl` (105 372 wiersze tekstu +
  282 wiersze strukturalne scen) — jedyne źródło prawdy dla gry. Widoki `.md` są generowane
  z pakietu i do niego wracają.
* Klucz elementu fabuły: numer sceny (`seq` z `06_scenes.jsonl`) + numer elementu (`order`).
  Klucz elementu nazw/tabel: numer grupy + numer elementu w planie zbudowanym z tych samych
  wierszy, które idą z powrotem do pliku; import dodatkowo porównuje tekst japoński, żeby wykryć
  nieaktualny widok.
* Tytuł misji i uwagi do misji są elementami sceny (`T1`, `N1`, `N2`) i trafiają do
  `05_mission_text.jsonl` (mają twardy `max_bytes`).
* Jedna linia `EN:` może wypełnić **kilka wierszy gry** — gdy ta sama postać/mech figuruje w kilku
  tablicach rozdziałów (1 097 scalonych par w `07`, 300 w `08`, 7 542 identycznych kwestii w `01`).
* Powtórzenia: `tools/package_copies.py` znaczy wiersze jako `copy_of` (6 504 wiersze), a widoki
  pokazują je jako elementy „dziedziczące" (5 146 pozycji) — tłumaczysz raz.
* Fabuła dociągana z kontenerów gry: `tools/event_refresh.py` (dodaje brakujące wiersze, zachowuje
  `id`/`en`/mówców, aktualizuje `06_scenes`; `--check` nic nie pisze).
* Narzędzia: `tools/scene_view.py` (widoki fabuły + zip), `tools/table_view.py` (widoki nazw i tabel
  + zip), `tools/translation_import.py`, `tools/translation_copy.py`, `tools/translation_mirror.py`,
  `tools/translation_check.py`, `tools/event_refresh.py`, `tools/package_copies.py`.
  Testy: 734 (1 pominięty).
* Kontrola całego pakietu: 105 372 wiersze, **0 błędów** (przed tłumaczeniem wszystkie puste).
* Brama pokrycia: `tools/coverage_audit.py` porównuje bajty kontenerów z pakietem — **0 braków**
  (wpis 51 dziennika). Teksty menu/helpów z `sysmes.bin` dodał `tools/sysmes_text.py`,
  doczyszczenia per członek — `tools/text_runs_export.py`.
* Wgrywanie na Dysk i kolejność kroków: `tools/drive_manifest.tsv` oraz `docs/STATUS.md`
  (sesja 5, część 11).
