# Importer zwrotek SRW Y — 2026-10-27

**Zaimplementowany i sprawdzony na danych syntetycznych.** Nie sprawdzono jeszcze
pełnego prywatnego pakietu v8 ani prawdziwej zwrotki tłumacza. Nie jest to test
polskiego patcha w grze (`runtime_tested: false`).

## Audyt względem OE — aktualizacja tej samej daty

Po przeglądzie oryginalnego importera i testów OE uzupełniono ochronę aktualności
S6, kontrolę kolejności/formatów tokenów, strukturalnych pustych linii i powtórzeń.
Pełne porównanie i świadome różnice: [IMPORTER_OE_PARITY.md](IMPORTER_OE_PARITY.md).
Aktualny wynik skupiony: **109 passed, 1 skipped, 57 subtests passed**.

## Przygotowanie i użycie

W katalogu `srw-y-translation`, z lokalnymi danymi S6:

```sh
python tools/build_translator_package.py
```

Builder zapisuje teraz także **prywatny**
`build/plik_dla_tlumacza/import_manifest.json`. Zawiera dokładny wzorzec Markdown
oraz powiązania element → źródłowy rekord gry. **Schema 2** wiąże także wszystkie
wejścia S6 hashem: sceny, tabele, limity, grupy, mapy głosów i misji. Obecność/brak
opcjonalnego wejścia też jest częścią pieczęci. Stary manifest schema 1 należy
odtworzyć i porównać z v8; nie wystarczy ręcznie zmienić numeru schematu. Nie trafia do żadnego ZIP-a dla
tłumacza. Zachować go razem z wersją pakietu, którą faktycznie wysłano. Jest to
zaufane wejście operatora, nie plik od tłumacza. Nie edytować go dla obejścia błędów.
Dane gry i wyniki pozostają w ignorowanych `local/` / `build/`.

**Dla już dostarczonego v8:** odtworzyć pakiet z tych samych lokalnych danych
(włącznie z mapami głosów i misji), porównać zawartości Markdown z dostarczonym
archiwum, dopiero wtedy używać wygenerowanego manifestu. Porównywać rozpakowane
teksty, nie hash ZIP-a (jego metadane mogą się różnić). Tego porównania nie dało się
wykonać w bieżącym checkoutcie: prywatne dane S6 nie są obecne. Nie trzeba ponownie
wysyłać paczki tłumaczowi — manifest nie zmienia widocznego formatu.

Import partii:

```sh
python tools/pl_import.py \
  --manifest build/plik_dla_tlumacza/import_manifest.json \
  --input local/zwrotka \
  --output local/import_pl.json
```

Kontrola bez zapisu:

```sh
python tools/pl_import.py --manifest build/plik_dla_tlumacza/import_manifest.json \
  --input local/zwrotka --source-dir local/s6 --check
```

`--check` nie wymaga `--output` i nie tworzy plików. `--source-dir` domyślnie wskazuje
projektowe `local/s6`. Pieczęć **całych** aktualnych źródeł musi się zgadzać, a każdy
rekord manifestu jest porównywany z żywym S6 po adresie i JP/EN. Nie ma opcji obejścia
kontroli. Zmiana źródła nawet poza odesłaną partią wymaga świadomej ponownej walidacji
pakietu. Nie zmieniać S6 równolegle podczas budowy/importu.

Wejście: pojedynczy `.md`, katalog (także z podkatalogami, ale bez kolizji nazw)
lub płaski ZIP plików `.md`, np. osobno `sceny.zip` / `widoki.zip`. Nie przyjmuje
zewnętrznego ZIP-a z zagnieżdżonymi ZIP-ami. Limit partii po rozpakowaniu: 64 MiB.
Nie wypakowuje ZIP-a na dysk, odrzuca ścieżki i duplikaty nazw. Indeksy z pakietu
można odesłać niezmienione; nieznane pliki lub zmienione indeksy są błędem.

Domyślnie puste `PL:` są pomijane — można importować nieukończone pliki.
`--require-complete` wymaga wypełnienia wszystkich slotów **przesłanych plików**,
nie całego pakietu. Brak pliku w partii nie usuwa wcześniejszego tłumaczenia:
każdy wynik jest samodzielnym planem tej partii, nie automatycznym scaleniem z
wcześniejszymi importami. Zachować zwrotki i wyniki poszczególnych partii.

## Kontrole i odmowa zapisu

- Cały plik poza wartościami `PL:` musi zgadzać się z manifestem: numery, kolejność,
  JP i jego linie kontynuacji, EN, limity, etykiety, mapa misji i powtórzenia.
  Dopuszczalne są UTF-8 BOM oraz zamiana LF ↔ CRLF.
- Dokładnie jeden fizyczny wiersz po `PL:`. Bez wstawionych `\\n`, `\\r`, dodatkowych
  slotów, znaków sterujących, zamknięcia literału Lua `]]` czy ukrytych znaków Unicode.
- Tokeny sprawdzane jako **multizbiór** względem źródłowego JP: rodzaj, wartość i liczba
  wystąpień. Dwa `%s` wymagają dwóch `%s`; dodanie tokenu także jest błędem.
  Kolejność tokenów sterujących/argumentów musi pozostać niezmieniona (jak w OE).
  Wyjątek: `%%` nie pobiera argumentu i może się przemieścić. Chronione są też
  printf z szerokością/precyzją, np. `%02d`, `%.2f`; `50% obrażeń` to zwykła proza.
- Limit liczy wszystkie znaki wpisanej wartości, łącznie ze spacjami i tokenami.
  Brak zmierzonego limitu = odmowa, nie ciche przyjęcie bez ograniczeń.
- Zatwierdzony zestaw prozy jest celowo konserwatywny: drukowalne ASCII, polskie
  litery, `„”’‘–—…«»「」『』（）～`; tokeny obecne w JP mogą zawierać inne znaki.
  Pozostałe znaki wymagają osobnej weryfikacji czcionki, nie automatycznego
  usunięcia lub transliteracji. Nie jest to pełny zrzut pokrycia fontu gry.
- Powtórzenia dziedziczą po dokładnym JP+EN w tym samym pliku, zgodnie z rendererem.
  Nie są wyszukiwane globalnie ani po samym numerze (numery scen się restartują).
  Limit i tokeny sprawdzane są ponownie dla każdego celu powtórzenia.
- Sceny: automatyczne łamanie na granicach słów/tokenów do maks. 3 × 90 znaków.
  Zachowuje też strukturalne separatory na brzegach źródła; one również liczą się
  do trzech linii. Nie dzieli tokenów; odrzuca tekst, który nie daje się tak złożyć, nawet gdy
  sam licznik jest ≤270. **90 to nadal heurystyka, nie pomiar pikselowy.**
- Tabele: zachowana liczba przejść do nowej linii z JP, podział na możliwie równe
  niepuste linie na granicach słów/tokenów. Puste linie i końcowe separatory
  LF/CRLF/CR są zachowane jako struktura, a nie dodatkowe miejsca na słowa. To heurystyka układu, nie odtworzenie semantyki
  poszczególnych linijek formularza. Gdy słów jest za mało, import jest odrzucany.
  Wcięcia typograficzne JP nie są kopiowane do polskiej prozy. Takie pola wymagają
  później kontroli ekranowej; nie deklarujemy zgodności wszystkich paneli.

**Dowolny błąd odrzuca całą partię.** Zwracany kod to 1; istniejący plik wyniku
pozostaje nietknięty. Po pełnej walidacji JSON jest zapisywany przez plik tymczasowy
w tym samym katalogu i atomowe `os.replace`. Nie modyfikuje zwrotki, manifestu ani bundli.
Nie koryguje samodzielnie tekstu, nie skraca go i nie dopisuje tłumaczeń.

## Wynik i przekazanie do zapisu

`local/import_pl.json` zawiera hashe wejść, manifestu i źródeł S6, liczniki oraz:

- `tables[table][key] = {jp, en, pl}` — format czytany bezpośrednio przez
  `build_pl_table_patch.plan(path)` / `build(..., base=...)`;
- `scenes[asset_name][string_id#occurrence] = {jp, en, pl}` — dokładne cele w Lua.
  Dla wskazanego assetu przekazuje się do `build_pl_scene_patch.apply_pl`:

```python
replacements = {key: row['pl'] for key, row in data['scenes'][asset_name].items()}
patched_script, used = apply_pl(script, replacements)
assert used == set(replacements)
```

`apply_pl` obsługuje teraz klucze `ID#numer_wystąpienia`, zachowując stare gołe ID
dla istniejących zestawów testowych. Importer nigdy nie emituje gołych ID: jeden
numer tekstu może wystąpić w skrypcie kilka razy.

To **intake i plan**, nie nowy automatyczny builder całej gry. Dobór oryginalnych
bundli/assetów scen, przebudowa, ponowna kontrola zapisanych tekstów, szyfrowanie i
MANIFEST patchera pozostają kolejnym etapem. Dotychczasowy `build_pl_scene_patch.build`
czyta format pojedynczej sceny testowej (`file`, `source_bundles`, `lines`), więc nie
należy podawać mu zbiorczego JSON-a importera jako `--trans`. Używać powyższego adaptera
na poziomie `apply_pl`; zbiorczy orchestrator nie jest częścią tego narzędzia.

## Testy

```sh
python -m pytest -q tests/test_pl_import.py tests/test_pl_import_oe_regressions.py tests/test_translator_package.py tests/test_pl_patch.py
```

2026-10-27 po audycie OE: **109 passed, 1 skipped, 57 subtests passed**. Obejmują generowanie
prywatnego manifestu (bez wycieku do ZIP-a), import, powtórzenia między scenami z
restartowaną numeracją, uszkodzenia JP/EN/struktury, tokeny i ich krotność, znaki,
limity, układ, ZIP/katalog, atomową odmowę oraz przekazanie wyniku do istniejącego
planu tabel i do podmiany konkretnego wystąpienia ID sceny.

Pełna seria po audycie OE: **433 passed, 44 skipped,
20 failed, 65 subtests passed**. Niepowodzenia dotyczą brakujących prywatnych
listingów (test misji i 18 podtestów kitów PS) oraz bundli test6 (patcher).
Nie naprawiano ich przez dodawanie danych gry do repo ani przez maskowanie testów.
Nadal otwarte: odtworzenie i porównanie pełnego v8, rzeczywista zwrotka,
przebudowa całej partii i kontrola układu w grze.
