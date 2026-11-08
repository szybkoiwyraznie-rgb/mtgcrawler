# SRW Y — łamanie linii w opisach umiejętności

## O co chodzi

Właściciel przysłał zrzut ekranu z **Data Help**: polski opis umiejętności leci
jedną linią i wychodzi za ramkę, podczas gdy angielski łamie się w czterech
miejscach. Prośba: „Opisy umiejętności pilotów też nie zawijają się same, trzeba
je łamać jak w angielskiej wersji.”

## Dlaczego polski wyszedł jedną linią

Sprawdzone na danych, nie zgadywane:

- Ekran **nie zawija tekstu sam**. Bajty `\n` w stringu *są* liniami, które
  widzi gracz — akapitów nie składa silnik UI.
- Tabele angielskie (`*_en-US`) mają te przejścia zapisane; japońskie też.
- Nasz pakiet dla tłumacza mówił odwrotnie: **„cały tekst wpisujesz w jednej
  linii po `PL:`, łamaniem zajmują się narzędzia”**. Narzędzia do tej pory łamały
  tylko dialogi scen (tam gra faktycznie zawija), a tabele `widoki` szły do gry
  bez zmian. Stąd płaski tekst w każdej tabeli wystawionej na ekran.

Poprawka ma więc dwa ruchy: **przepisać katalog z łamaniami** i **przebudować
patch z prawdziwych obiektów tabel**, bo dotychczasowy patch był robiony z
płaskich stringów.

## Co robi `tools/wrap_like_en.py`

Dla każdego elementu, w którym `EN:` ma więcej niż jedną linię, a `PL:` dokładnie
jedną, dzieli polski tekst na **tyle samo linii co angielski**:

- dzieli **tylko na spacjach** — żadne słowo nie jest cięte;
- koszt to kwadrat odchyłki od *proporcjonalnej* długości odpowiedniej linii
  angielskiej (krótka linia EN → krótka linia PL), z karą za złamanie w środku
  zdania (`NO_PUNCT_COST = 30`) i przed słowem funkcyjnym typu „i”, „w”, „gdy”,
  „się” (`STOPWORD_COST = 40`);
- nie zaczyna linii znakiem interpunkcyjnym i nie kończy jej myślnikiem ani
  nawiasem otwierającym;
- traktuje jako nierozdzielne: cytaty w grze (`'Penetr. barier'`, `„…”`), rich
  text (`<link=0>…</link>`) i placeholdery (`{…}`);
- **nie zmienia ani jednego znaku tekstu**: spacja staje się `\n`, więc długość
  rekordu (i budżet `limit:`) zostaje ta sama.

Uruchomienie: bez `--write` to przebieg próbny, `--write` zapisuje, `--out`
odkłada raport JSON.

```
python tools/wrap_like_en.py --out /tmp/wrap_dry.json
python tools/wrap_like_en.py --write --out translations/pl2/WRAP_REVIEW.json
```

## Co zostało zrobione

- Przepisane **804 wpisy** w `translations/pl2/PL/widoki/03_umiejetnosci.md`
  (umiejętności pilotów, duchy, programy, bonusy ACE). 18 wpisów trafiło do
  raportu jako *do przejrzenia* — polska linia jest tam o ponad 12 znaków dłuższa
  od swojej angielskiej; łamanie jest poprawne, tylko tekst jest gęstszy.
- Sprawdzone na **wszystkich 2 694 elementach** pliku: po `PL:` jest ten sam
  tekst co przed łamaniem, różnią się wyłącznie spacje i przejścia linii.
- Nagłówek reguły poprawiony w plikach `widoki` i w generatorze pakietu
  (`tools/build_translator_package.py`, reguła 3 + wyjątek), żeby tłumacz od
  razu pisał z łamaniami tam, gdzie ekran ich wymaga.
- Testy: `tests/test_wrap_like_en.py` (10) — m.in. tokenizacja nie wstawia
  spacji w `('Baza danych')`, złożony katalog jest już połamany, a ponowne
  uruchomienie narzędzia nie ma nic do roboty.

## Czego jeszcze brakuje: prawdziwe tabele

Patch PL pisze do tabel **japońskich** (`*_ja-JP`), a nie do angielskich. Żeby
wstawić połamane stringi, muszę mieć prawdziwe obiekty tych tabel — katalog
`s6-full` ma tylko teksty, nie obiekty Unity. Wszystkie potrzebne tabele leżą w
**5 bundlach** (`data/ja_table_bundles.json`, razem 1 200 544 B):

| Bundel | Rozmiar | Tabele |
|--------|--------:|--------|
| `1cc7e02ee5711c6ba87a0e364f62198c.bundle` | 940 012 B | 15 tabel podstawki |
| `cfc11e93f1dadabea385427266e4e252.bundle` | 61 099 B | 8 tabel DLC1 |
| `59feeef15e1736ef5c7166d6b4ab2740.bundle` | 40 230 B | 9 tabel DLC2 |
| `08b8a34806d30abe7e38e3f6464d41e9.bundle` | 80 790 B | 8 tabel DLC3 |
| `af95e769e79a11b531fbf1629475bb58.bundle` | 78 413 B | 6 tabel DLC4 |

Zestaw `SRW_Y_ZBIERZ_TABELE_JA.zip` (3 179 B, SHA-256
`31a097c85db089be8afadf448c0064e3ce4703abebfc76484ed57acabdbcd16f`,
budowany przez `tools/build_ja_tables_kit.py`) **nic nie zmienia w grze**:
dwuklik `ZBIERZ_TABELE_JA.bat` kopiuje te pięć plików i pakuje je na Pulpit w
`TABELE_JA.zip`. Po ich otrzymaniu powstaje patch z połamanymi opisami.

## Zakres i ograniczenia

- Połamanego jest `03_umiejetnosci.md`. Pozostałe pliki `widoki` to w większości
  nazwy własne i krótkie cytaty; przebieg próbny po całym katalogu pokazuje 4 737
  elementów z jednym `PL:` — jeśli właściciel zobaczy rozjechaną ramkę gdzie
  indziej, wystarczy puścić to samo narzędzie na tym pliku.
- `08_pokrewne.md` to tekst prologu z tabeli, nie plansza Data Help; zostawiony
  bez zmian do czasu, aż będzie wiadomo, czy to pole zawija samo.
- Kolejność i numeracja elementów są nietknięte, `limit:` bez zmian.
