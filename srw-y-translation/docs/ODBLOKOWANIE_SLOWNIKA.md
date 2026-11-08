# Kiedy gra odsłania kolejne części wpisu w Słowniku (round 13)

Data: 2026-11-09. Źródło: `KOD_GRY.zip` od właściciela
(SHA-256 `744a8417…5f35a`, 31 279 461 B) → `GameAssembly.dll` (74 865 152 B),
`global-metadata.dat` (18 909 544 B), `spis.txt` (619 B).

## 1. Co już wiemy na pewno

- Build jest **IL2CPP**: `spis.txt` pokazuje `…_Data\il2cpp_data` i
  `RuntimeInitializeOnLoads.json`, a **nie ma folderu `Managed`**. W związku z tym
  `Assembly-CSharp.dll` nie istnieje — typy i pola trzeba odtworzyć z
  `global-metadata.dat` (wersja 31, magic `af1bb1fa`).
- Tabele tekstowe (`dic_text_pilot*`, `dic_text_robot*`, `dic_text_word*`,
  `dic_text_name_*`) **nie mają żadnego pola warunku** — sprawdzone na wszystkich
  2 084 wierszach (`data/dictionary_entries_y.json`). Kolumna `Option` jest pusta
  w każdym wierszu. Czyli: **moment odsłonięcia nie jest zapisany w tekście**.
- W metadanych są za to nazwy klas i metod, które ten moment liczą:

| Element | Rola |
| --- | --- |
| `Com.BBStudio.SRTeam.Data.LibraryEntryManager` | właściciel stanu wpisów Słownika |
| `JudgeRobotDicEntry`, `JudgePilotDicEntry`, `judgeProductDicEntry` | funkcje „czy ten wpis pokazać” dla robota / pilota / produktu |
| `GetContrlFlag`, `SetContrlFlag`, `ControlFlags`, `ControlStatus`, enum `ControlFlagType` | flagi stanu (m.in. `AnniversaryPlayed`, `AnniversaryCleared`) |
| `LibraryEntryType` (`Word`, `PlayedEndMessage`, …) | typ wpisu |
| `LibraryDataPackageNumber`, `D0_0`…`D0_5` | numer paczki danych wpisu (DLC / partia) |
| `openCondition`, `missionOpenCond`, `MissionOpenCondition`, `runtimeWorkForOpenData`, `unOpenSlots` | warunki otwarcia liczone w kodzie |
| `EndMessageManager`: `UnOpenEntryList`, `UnOpenListTable`, `CheckedMission`, `CheckedFlag`, `EndMessageEntryStatus`, `ProductID`, `Order` | lista wpisów jeszcze nieodsłoniętych |

- Tabela `mission_open_cond` w `data/s6-full/tables.jsonl` zawiera **szablony
  zdań** warunków (np. `「$mission$」のクリア`, `$p$の撃墜数$number$以上`), a nie
  warunki wpisów encyklopedii. Czyli system warunków istnieje, ale dla misji.

## 2. Czego jeszcze nie wiemy i dlaczego

`Judge*DicEntry` **czyta dane spoza tekstu**. Nie ma ich w żadnym z 11 bundli
słownika (sprawdzone), nie ma ich też w tabelach misji. Zostają dwa nośniki:

1. **obiekt serializowany** w `resources.assets` (+ `resources.assets.resS`)
   albo `globalgamemanagers.assets` — klasa z listą „BaseID → warunek/paczka”,
2. **stan zapisu gry** (`ControlFlags`/`ControlStatus`), ustawiany w trakcie gry
   przez `SetContrlFlag` — wtedy „odsłonięcie” nie wynika z żadnej tabeli, tylko
   z postępu gracza, i nie da się go odczytać z plików gry bez jego sejwa.

Rozstrzygnięcie wymaga zajrzenia do `resources.assets`. Dlatego jest osobny
zestaw `SRW_Y_ZBIERZ_ASSETY.zip` — kopiuje **4 pliki** z `…_Data`
(`resources.assets`, `resources.assets.resS`, `globalgamemanagers.assets`,
`globalgamemanagers`), robi `spis.txt` i pakuje wszystko w `ASSETY_GRY.zip`
na Pulpit. Gra nie jest w niczym zmieniana, nic nie jest uruchamiane.

Co z tym zrobię: w `resources.assets` szukam `TextAsset`-ów i `MonoBehaviour`
o nazwach z tabeli powyżej; jeśli warunek jest listą `BaseID → paczka`, dostanę
dokładną regułę i przepiszę sekcję „Teksty encyklopedii, których gra jeszcze nie
pokazuje” na wpisy odsłaniane po konkretnych misjach. Jeśli okaże się, że stan
siedzi w sejwie, powiem to wprost i zostawimy obecne, uczciwe rozwiązanie
(wszystkie 1 307 odroczonych fragmentów w jednej sekcji, bez zmyślonych misji).

## 3. Co jest w v12 (stan bez tej odpowiedzi)

`SRW_Y_CZYTANKI_PL2_POPRAWIONE_v12.zip` trzyma 1 307 fragmentów, których gra
jeszcze nie pokazuje, w jednej sekcji
`## Teksty encyklopedii, których gra jeszcze nie pokazuje`, z rozbiciem na
tabele (`dic_text_pilot-DLC4` 459, `dic_text_pilot` 348, `dic_text_robot` 243,
`dic_text_word` 81) i rodzaj (pilot 880, robot 314, word 81, nazwa 32). Żadna
misja nie jest tam podana jako moment odsłonięcia — bo nie mamy na to źródła.

## 4. Zestaw do pobrania

`SRW_Y_ZBIERZ_ASSETY.zip` — 3 803 B, SHA-256
`f09f90dea2eeb021603f3fe9fa654b8a85052cfe8c58b4f861b2513feb2b5bc7`,
Drive `17XeDsao8KoNFhu_-H-aRwzvg-BYHk4Ih`
(`https://drive.google.com/file/d/17XeDsao8KoNFhu_-H-aRwzvg-BYHk4Ih/view`).

W środku: `CZYTAJ_TO.md`, `ZBIERZ_ASSETY.bat`, `zbierz.ps1` (buduje
`tools/build_assets_kit.py`, dwa buildy bit w bit takie same). Bat kopiuje
4 pliki z `…_Data`, dopisuje `spis.txt` z zawartością folderu i pakuje
`ASSETY_GRY.zip` na Pulpit. Limit 400 MB na plik. Gra nie jest uruchamiana ani
zmieniana.
