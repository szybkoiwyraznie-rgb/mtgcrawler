# Mapa scena → misja → rozdział (z danych misji gry)

Poprzednia odpowiedź brzmiała „tego powiązania nie ma w danych”. Była **za szeroka**:
nie ma go w *skryptach scen*, ale jest w **danych misji**, o które poprosiłem (prośba 5,
`SRW_Y_MISSION.zip`, 18 plików, 681 877 B, odebrane 2026-10-26).

## Skąd bierze się powiązanie

```text
Mission*Data.missionRomList[]
  id            m0001_0000310          numer misji
  name          m0001_0000310：…        tytuł, który gra pokazuje
  title         m0001_0000310_title    klucz do tabeli mission_title
  chapterNo     1 … 7  (0 = bez rozdziału: dodatki, bonusy, poboczne)
  composition[] sdemo_file / dlgev_file / script_file → cse20_0001_0000310a_…
```

Scena trafia do misji **po nazwie pliku**, nie po kolejności. Drugie wiązanie to preset:
`m0001_0000310a_preset` niesie klucze `ICE_OP_ADVICE_m…`, a te nazywają pliki scen
wydarzeń bitewnych, których nie ma w `composition`.

## Co wyszło

| miara | liczba |
|---|---|
| misje w danych | **533** |
| misje z numerem rozdziału 1–7 | **144** |
| misje bez rozdziału (0: dodatki, bonusy, poboczne) | **389** |
| sceny w paczce tłumacza | **611** |
| sceny przypisane do misji | **588** (96.2%) |
| — po nazwie pliku | 580 |
| — po kluczu presetu (`ICE_OP_ADVICE`) | 8 |
| sceny **bez wpisu misji** w danych | **23** (3.8%) |
| wiersze `mission_title` powiązane z misją | **444** z 533 |

Sceny bez wpisu nie dostają zmyślonej misji — mają w paczce jawną adnotację
„scena bez wpisu misji”. To 23 plików, w większości wydarzenia
bitewne (`_dlgev`), samouczek i ekrany systemowe wołane z innych miejsc niż lista misji.
Wszystkie, bez wyjątku, są tu wypisane:

- `cse20_0024_0202800a`
- `cse20_0024_0202800b`
- `cse20_0041_0202810a`
- `cse20_0041_0202810b`
- `cse20_0047_0202820a`
- `cse20_0900_0000000a`
- `cse20_0900_0000001a`
- `cse20_0900_0000002a`
- `cse20_0900_0000003a`
- `cse20_0900_0000004a`
- `cse20_0952_0999900`
- `cse20_0953_0999900`
- `cse20_0954_0999900`
- `cse20_0955_0999900`
- `cse20_0962_0999900`
- `cse20_1014_0200900a`
- `cse20_8000_0000200a`
- `cse20_8000_0000201a`
- `cse20_8000_0000301a`
- `cse20_8000_0000400a`
- `cse20_8000_0000401a`
- `cse20_8000_0000501a`
- `cse20_9040_0000000a`

Szukane w **całej paczce danych misji** (18 plików `.bundle`, 321 obiektów
`MonoBehaviour`), dla każdej z tych 23 nazw z osobna:

- `missionRomList` — brak wpisu (533 misje przejrzane);
- `missionPatchList` — 15 wpisów, żaden nie nazywa tych plików;
- klucze `ICE_OP_ADVICE_*` w 277 presetach — brak klucza z tą nazwą;
- pola `composition` (sdemo / dlgev / script) — brak dokładnej nazwy; podobieństwo
  „tej samej rodziny” numerów to tylko wspólny prefiks, nie dowód.

Dlatego etykieta zostaje pusta. Gdyby w kolejnej wersji danych gry pojawił się ich wpis,
mapa doda je automatycznie, bez zmian w kodzie paczki.

## Rozdziały (tak, jak numeruje je gra: `CHAPTER 01`…`CHAPTER 07`)

| rozdział | misje |
|---|---|
| 0 | 389 |
| 1 | 8 |
| 2 | 34 |
| 3 | 24 |
| 4 | 18 |
| 5 | 22 |
| 6 | 22 |
| 7 | 16 |

Rozdział 0 to nie „rozdział zerowy”, tylko brak rozdziału w danych: misje dodatków
(DLC1–4), bonusy, samouczki i poboczne.

## Misje per paczka

| paczka | misje |
|---|---|
| `AnniversaryExpansionPack` | 39 |
| `BonusMission` | 16 |
| `DeluxeEdition` | 1 |
| `Dlc1` | 29 |
| `Dlc2` | 26 |
| `EarlyPurchase` | 6 |
| `ExpansionPack` | 42 |
| `PremiumSound` | 1 |
| `SeasonPassBonus` | 9 |
| `UltimateEdition` | 1 |
| `base` | 363 |

## Co z tego dostaje tłumacz (paczka v8)

- `spis-scen.md`: przy każdej scenie **misja** (`m0001_0000310`) i **rozdział**
  (`1`…`7`, albo `—` przy scenach bez wpisu) — bez zgadywania z kolejności;
- `06_teksty_misji.md`: przy każdym tytule/opisie **misja + rozdział**, żeby tytuł dało się
  powiązać z konkretnym plikiem scenariusza;
- reszta plików bez zmian, numeracja elementów bez zmian — nic przetłumaczonego nie
  trzeba przerabiać.

Dane techniczne: `tools/mission_map.py` → `local/s6/mission_map.json`
(tekst japoński zostaje w `local/`, poza repozytorium).
