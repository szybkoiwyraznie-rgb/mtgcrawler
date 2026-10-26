# PROŚBA 5 — dane misji gry (`SRW_Y_MISSION_PROSBA.zip`)

## Po co

Tłumacz poprosił o **prawdziwą mapę „scena → rozdział → tytuł misji”**, żeby nie musiał
niczego domyślać się z kolejności. Poprzednia odpowiedź („takiego powiązania nie ma
w danych”) była przedwczesna — powiązania nie ma **w tekstach**, ale gra ma osobne
**dane misji**, i to jest ich jedyne miejsce.

## Co sprawdzono w danych, które już mam

| sprawdzenie | wynik |
|---|---|
| tytuły misji w treści skryptów scen (946 plików) | **15 z 378** tytułów występuje gdziekolwiek, i tylko jako zwykłe słowa w dialogu (np. nazwa odcinka wypowiedziana przez postać) — ani jednego jako nagłówek sceny |
| dowolny identyfikator misji/sceny w kodzie skryptów | **0** — przeszukane wszystkie 45 komend `Cmd_*`, żadna nie ustawia tytułu ani rozdziału |
| etykiety rozdziałów w tabelach | **są**: `system_text` zawiera `CHAPTER 01` … `CHAPTER 07` oraz `ミッションチャート` (ekran mapy misji) |
| tabele tekstów misji | `mission_title` 527, `mission_outline` 294, `mission_detail` 526 — klucze **nie** przecinają się między tabelami, więc misja jest identyfikowana z zewnątrz |

Wniosek: skrypt sceny nie wie, do której misji należy; wiedzą to dane misji.

## Co jest w tej paczce

Klasa assetów nazwana wprost po misjach — jedyne assety w całym katalogu gry o takich
nazwach (przeszukane wszystkie adresy podstawki i 54,470 adresów dziesięciu paczek):

| asset | paczka | rozmiar |
|---|---|---|
| `AnniversaryStoryPreset` | `AnniversaryExpansionPack` | 8,686 B |
| `MissionB1Data` | `base` | 13,635 B |
| `MissionB2Data` | `base` | 15,694 B |
| `MissionB3Data` | `base` | 6,511 B |
| `MissionB4Data` | `base` | 12,114 B |
| `MissionBnData` | `BonusMission` | 19,277 B |
| `MissionD1Data` | `Dlc1` | 9,267 B |
| `MissionD2Data` | `Dlc2` | 9,288 B |
| `MissionD3Data` | `ExpansionPack` | 11,763 B |
| `MissionD4Data` | `AnniversaryExpansionPack` | 118,029 B |
| `MissionData` | `base` | 411,774 B |
| `MissionDlData` | `DeluxeEdition` | 4,656 B |
| `MissionErData` | `EarlyPurchase` | 5,684 B |
| `MissionLayerList` | `base` | 2,477 B |
| `MissionLayerList_main` | `base` | 17,864 B |
| `MissionPrData` | `PremiumSound` | 4,609 B |
| `MissionSzData` | `SeasonPassBonus` | 5,910 B |
| `MissionUlData` | `UltimateEdition` | 4,639 B |

**18 plików, 681,877 B** (≈ 0.7 MB),
bez audio i bez scen. W katalogu są też `MissionChart_*` (obrazy mapy misji, 32–55 KB) —
ich nie zamawiam, bo to grafika, nie dane.

## Co uruchomić

**`SRW_Y_MISSION_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`), **id `1cUKgovgAZjEVTZXg6tVQi0t-EOolZshY`**,
4 145 B, sha256 `f7bbe5795a16f08f588692a1dca59db4331bbddbdb1fa2def3920c6d43add5e5`,
pobrany ponownie z Drive i identyczny bajt w bajt. W środku `URUCHOM_TO.bat`,
`ZBIERZ_MISSION.ps1`, `CZYTAJ_TO.txt` — ten sam format co poprzednie paczki.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_MISSION.zip`** — wgraj go na Drive.

## Co z tego będzie

Z tych plików odczytam dla każdej misji: numer, tytuł (klucz do `mission_title`), plik
scenariusza (`cse20_…`), rozdział i pozycję na mapie misji. Wtedy do paczki tłumacza
wchodzi plik `spis-scen.md` z kolumną **rozdział / misja** przy każdej scenie —
bez domyślania się z kolejności. Jeśli w środku okaże się, że pola są inne, niż zakładam,
powiem to liczbą i opiszę, co jest, zamiast dopisywać własną interpretację.

## Stan paczki

| | |
|---|---|
| plik | `SRW_Y_MISSION_PROSBA.zip` |
| rozmiar / sha256 | 4 145 B / `f7bbe5795a16f08f588692a1dca59db4331bbddbdb1fa2def3920c6d43add5e5` |
| Drive | `1cUKgovgAZjEVTZXg6tVQi0t-EOolZshY` |
| read-back | pobrany ponownie, `cmp` — identyczny |
| zawartość | `URUCHOM_TO.bat`, `ZBIERZ_MISSION.ps1` (18 plików), `CZYTAJ_TO.txt` |
| generator | `tools/build_mission_request.py` → `local/s6/mission_request.json` |
| testy | `tests/test_mission_request.py` (7), lint PS 5.1 w `tests/test_ps_kits.py` (kit `mission`) |
