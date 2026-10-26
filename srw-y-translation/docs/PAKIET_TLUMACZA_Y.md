# Pakiet dla tłumacza SRW Y — stan i forma

Forma jest **taka sama jak przy SRW OE**: jedno archiwum, w środku instrukcja i dwa zipy
z plikami `.md` do tłumaczenia. Różnica wynika tylko z języka docelowego — w OE
tłumacz wpisywał angielski po `EN:`, tutaj polski po `PL:`, a `EN:` jest gotowym
odniesieniem.

```text
plik_dla_tlumacza.zip
├── README.md      instrukcja (polski, ten sam układ co w OE)
├── sceny.zip      spis-scen.md + 36 plików scen (601 scen, 119 151 linii)
└── widoki.zip     9 plików tabel (44 344 elementy)
```

Element ma układ z OE:

```text
14. [Dialog - ちせ] 「ん…？」
   limit: 1 linia — nie zmieniaj liczby przejść
   tokeny: zachowaj dokładnie: $c
   EN: "Huh?"
   PL:
```

Grupy plików: `odcinek-NN[_x].md` dla podstawki (numeracja z nazw scenariuszy) oraz
`dlc-<Pakiet>[_x].md` dla dodatków; plik dzieli się na części `_a`, `_b`, … powyżej
8 000 linii. `spis-scen.md` listuje wszystkie 601 scen z grupą, mówcami i liczbą linii.

## Co jest w środku (zmierzone, 2026-10-25)

| część | elementy | sloty `PL:` | źródło |
|---|---|---|---|
| sceny | 114 542 | 96 093 | 1 883 plików Lua podstawki i DLC |
| widoki | 44 344 | 41 228 | 144 tabele × 2 języki |
| razem | 158 886 | **137 321** | |

Pozostałe 21 565 elementów to powtórzenia w obrębie pliku — mają znacznik
`(powtórzenie elementu N)`, tłumaczenie dziedziczy się automatycznie, tak jak kopie w OE.

## Kompletność

- podstawka: 605 plików jp + 678 en (z tego 605 par; 73 to starsze wersje angielskie),
- DLC: 601 bundli (323 jp / 278 en), w tym `Dlc1` bez angielskiego,
- **brakuje 19 scen z darmowej łatki** (`DLC_EXP/FreePatch`) — 38 bundli, 357 783 B;
  bez nich pakietu nie wysyłam, żeby nie powtórzyć błędu z niepełnymi danymi.

## Odtworzenie

```text
python3 tools/s6_tables.py
python3 tools/s6_scenario.py
python3 tools/build_translator_package.py
```

Dane wejściowe: `local/s6/tables.jsonl`, `local/s6/scenario.jsonl` (oba poza repozytorium,
bo zawierają tekst gry), skrypty w `local/s4_plain/` i `local/s6/plain/`.

## Limity w paczce (2026-10-26)

Każdy element ma linię `limit:` policzoną z danych gry (`tools/s6_limits.py`,
`local/s6/limits.json`, opis w `docs/LIMITY_Y.md`):

```text
14. [Dialog - ちせ] 「ん…？」
   limit: 1 linia (tyle ma japoński) — japoński ma 12 celi — okno mieści 3 linie
          — najszersza kwestia w grze: 240 celi
   EN: "Huh?"
   PL:

7. [Nazwa broni] ゴッドミサイル
   limit: do 50 celi (tyle ma najdłuższy tekst, jaki gra pokazuje w tym miejscu
          - cały ten typ danych: japoński 50 / angielski 49); japoński: 14 celi / 21 B

3. [Tekst interfejsu] 冷酷非情
   limit: do 14 celi (tyle ma najdłuższy tekst, jaki gra pokazuje w tym miejscu
          - to pole: japoński 14 / angielski 14)
          pole mieści np. „Cold, ruthless“, „Upbeat, cheery“; japoński: 8 celi / 12 B
```

Zmierzone: okno dialogowe mieści **3 linie** (tyle ma najdłuższa kwestia w obu językach),
angielska wersja gry wyświetla kwestie do **240 celi**, a najdłuższy napis w każdej z 144
tabel jest znany osobno. Nie zmierzone: szerokość kolumn list i marginesy okien.

**Limit jest na pole, nie na pojedyncze słowo** (decyzja właściciela, 2026-10-26):
- tabela z jednym rodzajem danych (nazwy broni, imiona pilotów, nazwy misji) → **jeden
  limit dla wszystkich wpisów**, równy najdłuższemu tekstowi tego rodzaju w grze;
- tabela mieszana (`system_text` trzyma etykietę `Traits`, jej wartości, potem `Hobbies`
  i jego wartości) → **każde pole ma własny limit**, a wiersz `limit:` wymienia teksty
  stojące w tym polu.

Granice pól wyznacza `tools/s6_groups.py` (`local/s6/groups.json`) z samych tekstów gry:
nowe pole zaczyna się, gdy długość skacze o więcej niż 1,6x albo zmienia się liczba linii.
Tabele jednorodne dostają jedno pole na całość. Sprawdzone w grze: `Chłodny, bezwzględny`
(20 celi) nachodził na etykietę `Charakter`, której pole mieści 14 celi.

Który limit jest twardy, zależy od trybu zapisu — patrz `docs/POWROT_TLUMACZEN.md`.
