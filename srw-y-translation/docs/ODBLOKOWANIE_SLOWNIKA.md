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

## 5. `ASSETY_GRY.zip` przeczytany — `resources.assets` to nie to (2026-11-09)

Właściciel przysłał `ASSETY_GRY.zip` (14 940 453 B, SHA-256
`123c2e3b6bc5a5fdc6e792fbbb177f44d2ea73b382d98addbc4d64cd6aa35ea1`,
`spis.txt` zgodny). W środku `resources.assets` 69 275 040 B,
`resources.assets.resS` 7 854 144 B, `globalgamemanagers.assets` 1 347 580 B,
`globalgamemanagers` 277 028 B.

Census obiektów `resources.assets` (UnityPy, oba pliki `.assets` razem):

| Typ | Ile |
| --- | --: |
| `MonoBehaviour` | 447 |
| `GameObject` | 348 |
| `RectTransform` | 348 |
| `CanvasRenderer` | 223 |
| `Material` | 34 |
| `Texture2D` | 32 |
| `Shader` | 17 |
| `Font` | 7 |
| `Sprite` | 6 |
| `TextAsset` | 4 |
| `Canvas` | 2 |

447 `MonoBehaviour` to **wyłącznie** komponenty interfejsu i renderu:
`UnityEngine.UI` 336, `Unity.RenderPipelines.Core.Runtime` 92,
`Unity.TextMeshPro` 19, `Unity.RenderPipelines.Universal.Runtime` 7,
`Assembly-CSharp` **2** (`VideoBufferRenderFeature`, `PostProcessRenderFeature`),
`Unity.Localization` 1, `Unity.InputSystem` 1. Cztery `TextAsset` to
`PerformanceTestRunInfo`, `PerformanceTestRunSettings` i dwa zestawy znaków
łamania linii. **Żadnych danych gry.** Czyli `resources.assets` nie jest
nośnikiem warunku — nie trzeba go już nigdy więcej wysyłać.

## 6. Tabele wpisów słownika — sprawdzone po pełnym opisie typu

Wcześniejsze „brak warunku” opierało się na odczycie wierszy; teraz potwierdza to
**wbudowany opis typu (typetree)** z bundli, które przysłałeś w
`SLOWNIK_ENCYKLOPEDII.zip` (11 plików, 58 461 B). Schematy wierszy są dokładnie
takie:

| Tabela | Pola wiersza |
| --- | --- |
| `PilotDicEntry` | `BaseID, TextID, FaceID, VoiceActorID, Face[4], Voice[4], order, pkg, Option` |
| `RobotDicEntry` | `BaseID, TextID, HeightStr, HeightNumStr, HeightUnit, WeightStr, WeightNumStr, WeightUnit, Direction, pkg, Option` |
| `WordDicEntry` | `ProductID, TextID, pkg, Option` |

- 2 084 wiersze, `Option` pusty we **wszystkich** (nie „w większości”).
- `pkg`: 0 → 1 531, 10 → 62, 20 → 51, 30 → 88, 40 → 352.
- Piloty: 786 wierszy na **779** różnych `BaseID` (772 po jednym, 7 po dwa —
  duplikat base/DLC z tym samym `order`). Czyli **jedna pozycja wpisu = jeden
  wiersz**. Części wpisu (`_00_1`, `_00_2`, …) nie są osobnymi wierszami tych
  tabel — te części żyją tylko w tabelach tekstu.

Wniosek: bramki „pokaż część 2” **nie da się** zapisać w tej strukturze. Dlatego
dalej szukamy w sąsiadach, których nazwy podaje katalog Addressables.

## 7. Następne osiem bundli (zestaw gotowy)

Z `catalog.json` (41 543 062 B, SHA-256 `12c17bf9…73b4`, leży na Drive od sierpnia)
narzędziem `tools/map_catalog.py` rozwiązałem nazwy bundli dla ośmiu obiektów,
które są jedynymi pozostałymi kandydatami:

| Obiekt (adres w katalogu) | Bundle |
| --- | --- |
| `EndMessageEntryTable` | `6780e8931f996403ae7d7e2da74e27c1.bundle` |
| `EndMessageEntryTable_D1` | `6f71b9cd90341f7ce30f676bd1d877b4.bundle` |
| `EndMessageEntryTable_D2` | `7327bab9936c556e99778b8649ca81d8.bundle` |
| `EndMessageEntryTable_D3` | `6ab37b100cc46941eaea66387a61b22e.bundle` |
| `EndMessageEntryTable_D4` | `b7866e3acf857f18ad905817a00773a8.bundle` |
| `DicDetail_Pilot` | `1b5da0ef65aef8e3db19c7f1b4a62ad2.bundle` |
| `DicDetail_Robot` | `89807f3be3a7048e8e26f7e8edccb6da.bundle` |
| `LibraryTutorial` | `9e56e5c953cea02a1e42b2ed1dba787f.bundle` |

Zestaw: `SRW_Y_ZBIERZ_TABELE.zip` — 3 514 B, SHA-256
`72547d9957782ae76fe4c13a142e04c9b813a5cc0c82949d285883f5f02bfd8f`,
Drive `16vvzNKW9BdEWhtYonCKVdUNik2QS9iBx`
(`https://drive.google.com/file/d/16vvzNKW9BdEWhtYonCKVdUNik2QS9iBx/view`).
Buduje `tools/build_entry_tables_kit.py` (dwa buildy bit w bit takie same);
lista nazw w `data/entry_table_assets.json`. Bat kopiuje te 8 plików z
`…_Data\StreamingAssets\aa\StandaloneWindows64` i pakuje `TABELE_WPISOW.zip`
na Pulpit.

## 8. Status hipotezy „jednostka wystąpiła w misji”

Nie jest obalona ani potwierdzona. Przykład właściciela (A. Advent cz. 2 /
Willforce ukryta w misji 1) da się wytłumaczyć dwojako: albo to inny `BaseID`
(czyli inna pozycja, a nie „późniejsza część”), albo ten sam `BaseID` z częścią
zablokowaną warunkiem. Tabele wpisów mają **jeden wiersz na `BaseID`**, więc
rozstrzygnięcie wymaga albo tych ośmiu bundli, albo mapy `wpis → misja` od
właściciela.

## 9. `TABELE_WPISOW.zip` przeczytany — jest odpowiedź, tylko nie tam, gdzie ją podejrzewałem

Wejście: `TABELE_WPISOW.zip` 715 355 B, SHA-256
`a4cc666e3c640ef4379a1d7e16c4e055dc2460f4127119d9d12698fee5f81fd8`, 8 bundli.
Po odszyfrowaniu i wczytaniu:

| Bundle | Co jest w środku |
| --- | --- |
| `1b5da0ef…bundle` (`DicDetail_Pilot`) | prefab UI: 166 `GameObject`, 166 `RectTransform`, 138 `CanvasRenderer`, 4 `CanvasGroup`, 1 `Canvas`, animatory — **żadnych danych** |
| `89807f3b…bundle` (`DicDetail_Robot`) | prefab UI: 150 `GameObject`, 150 `RectTransform`, 122 `CanvasRenderer`, 3 animatory — **żadnych danych** |
| `9e56e5c9…bundle` (`LibraryTutorial`) | prefab UI: 260 `GameObject`, 260 `RectTransform`, 217 `CanvasRenderer`, 9 `AnimationClip` — **żadnych danych** |
| `6780e893…bundle` (`EndMessageEntryTable`) | tabela danych, 123 wiersze |
| `6f71b9cd…bundle` (`EndMessageEntryTable_D1`) | 5 wierszy |
| `7327bab9…bundle` (`EndMessageEntryTable_D2`) | 6 wierszy |
| `6ab37b10…bundle` (`EndMessageEntryTable_D3`) | 12 wierszy |
| `b7866e3a…bundle` (`EndMessageEntryTable_D4`) | 2 wiersze |

### Co mówi `EndMessageEntryTable` — i to jest ta reguła

Pola wiersza: `ID, ListOrder, ScenarioNo, ProductID, BGM, MissionID_1,
MissionID_2, Flag, pkg, Option`. Razem 148 wierszy:

- `ScenarioNo` wypełniony w 147 — numer odcinka,
- `MissionID_1` w 34 — **„pokaż po ukończeniu tej misji”**,
- `MissionID_2` w 1 — dodatkowy warunek misji,
- `Flag` w 12 — nazwana flaga postępu, np. `M0014b_RESSY_NOCHANGE`,
  `M0031A_LGAIM2`, `M0027A_GODNION_JOIN`, `M0106A_ENDING`,
- `Option` pusty we wszystkich 148.

Czyli gra **ma** konwencję „wpis pojawia się po misji / po flagie” — i zapisuje ją
wprost w tabeli, kolumną `MissionID_1` albo `Flag`. Nazwy flag są tej samej
postaci, co flagi misji w danych misji (`M000B_FHERO`), więc to ten sam system
flag postępu, który widziałem w kodzie jako `ControlFlags`/`ControlStatus`.

Tabele encyklopedii (`PilotDicEntry`, `RobotDicEntry`, `WordDicEntry`) **nie mają
ani `MissionID_*`, ani `Flag`, ani żadnej innej kolumny warunku** — potwierdzone
pełnym opisem typu. Jedyna ich kolumna „warunkowa”, `Option`, jest pusta we
wszystkich 2 084 wierszach.

### Wniosek, wprost

- Moment odsłonięcia wpisów **zapowiedzi końcowych** (`PlayedEndMessage`) jest
  w danych i jest odtwarzalny — 148 wierszy, 21 misji z jawnym `MissionID_1`
  (np. `m0001_0000310` → `EMESS_114`, `EMESS_115`; `m2002_0102000` →
  `EMESS_200`, `EMESS_201`). Zapis: `data/end_message_entries_y.json`
  (35 902 B, SHA-256 `b4cb7789…9184`), narzędzie
  `tools/read_end_message_entries.py`.
- Moment odsłonięcia **dalszych części wpisów encyklopedii** nie jest zapisany
  w żadnym pliku danych. Skoro gra zapisuje warunki w tabeli, gdy je ma, a tabele
  encyklopedii takiej kolumny nie mają, to warunek jest liczony w kodzie z flag
  postępu w sejwie — a nie z plików gry. Bez sejwa (albo bez Twojej mapy
  `wpis → misja`) tego nie odtworzę i nie będę zgadywał.

### Co to znaczy dla czytań

Obecne wydanie v12 trzyma 1 307 fragmentów, których gra jeszcze nie pokazuje,
w jednej sekcji bez przypisanych misji — i to jest jedyne uczciwe rozwiązanie
bez mapy od Ciebie. Jeśli chcesz, żeby numery misji jednak były, potrzebuję
Twojej listy `wpis → misja`; alternatywnie mogę w v13 dopisać do każdej misji
**wpisy zapowiedzi końcowych**, które się po niej odsłaniają — te są w danych.
