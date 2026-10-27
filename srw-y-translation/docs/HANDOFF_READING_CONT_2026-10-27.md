# SRW Y — czytanki: co dostarczono i co zostało (2026-10-27, wersja po korekcie właściciela)

Kontynuacja [`HANDOFF_READING_Y_2026-10-27.md`](HANDOFF_READING_Y_2026-10-27.md).
Gałąź `arena/ff68be19-mtgcrawler`, draft PR #28
(`https://github.com/szybkoiwyraznie-rgb/mtgcrawler/pull/28`).

## 0. Korekta właściciela — obowiązuje od teraz

- **Pliki docelowe czytanek mają być w 100% po polsku**, tak jak czytanki OE.
  Żadnych opcjonalnych kolumn japońskich/angielskich, nawet wyraźnie oznaczonych.
  Wczesne wydanie „referencyjne” z kolumnami JP/EN zostało **wycofane** (stara
  paczka na Drive przeniesiona do kosza).
- **Protagonista:** domyślnie mężczyzna; wariant żeński tylko w misjach, w których
  nie ma wariantu męskiego (misje unikalne dla kobiety-protagonistki). Linie
  wspólne zostają. To jest już w kodzie i w wygenerowanych plikach.
- **Dane encyklopedii w `deployment.md` są kluczowe**, więc powiązanie jest
  niezbędne. Właściciel prosi o pakiet bat+ps1, jeśli potrzebne są assety —
  pakiet jest zbudowany (§3).

## 1. Co zostało dostarczone

**Pliki `.md`** w [`docs/reading/pl-2026-10-27/`](reading/pl-2026-10-27/) —
14 plików, łącznie **22 595 207 B**: `README.md`, `rozdzial-01..07.md`,
`sceny-poza-rozdzialami.md`, `sceny-bez-misji.md`, `deployment.md`, `piloci.md`,
`mechy.md`, `encyklopedia.md` + `receipt-summary.json`.

Automatyczny skan wszystkich 14 plików: **0 linii z pismem japońskim/chińskim,
0 etykiet `JP (źródło…)` / `EN (odniesienie…)`, 0 zapasowych etykiet mówcy po
japońsku**. Jedyny tekst w plikach to polskie nagłówki, polskie opisy, identyfikatory
techniczne i jawne polskie znaczniki braku.

Paczka na Drive: **`SRW_Y_CZYTANKI_PL_2026-10-27.zip`**, 2 653 232 B,
SHA-256 `e2ce1b5323c88eafccc8a7c3b8dcc8b926668dad45c571fb15e9433f2dcd6814`,
id `1mn6zJ5j_t1GiOUvQVcnQwyTFVImPMYk5`. Zawiera te same `.md`, pełny
`receipt.json` i deterministyczny `srwy_reading_PL.zip`.

**To wciąż nie jest pełne polskie wydanie pod względem treści.** Tłumacz nie
zwrócił wypełnionych `PL:`; pusty pakiet v8 nie jest zwrotem. Dlatego
**115 153 pozycje mają jawny `[BRAK PL: …]`** — bez podkładania jakiegokolwiek
tekstu obcego. Gdy przyjdzie zwrot, generator wstawi polską prozę w te same
adresy, bez zmiany numeracji. Wydanie ma `polish_only: true` w recepcie.

`encyklopedia.md` jest teraz **polskim indeksem haseł**: komplet kluczy Shared
Data i adresów S6 dla `dic_text_pilot/robot/name/word` (podstawka + DLC),
bez tekstu JP/EN. `piloci.md` i `mechy.md` mają własne polskie indeksy biografii
i opisów. Biografie przy pierwszym wystąpieniu nadal nie są przypisane — §4 A.

## 2. Zmiany w kodzie

- `tools/build_reading_y.py`: **usunięto tryb `--reference` i wszystkie kolumny
  JP/EN**; `text()` zwraca wyłącznie polski tekst albo `[BRAK PL]`; `speaker()`
  nie wypisuje już japońskiej etykiety mówcy (zamiast niej PID). Zachowano
  `encyklopedia.md`, klucze `m_Key` w nagłówkach, `dictionary_stats()`,
  `--evidence` i pieczęć źródeł. Receipt ma `polish_only: true` i `schema: 2`
  przy przekazanej evidencji.
- W `README.md` i nagłówkach rozdziałów zapisana jest wprost reguła
  protagonisty (mężczyzna domyślnie, kobieta tylko bez wariantu męskiego,
  linie wspólne zostają). Implementacja: `protagonist_for_assets()` wybiera `F`
  tylko wtedy, gdy w całej misji występuje `F` i nie występuje `M`; testy
  `test_male_default_excludes_female_variant`,
  `test_female_only_mission_uses_female_and_shared_lines`,
  `test_gender_is_selected_over_whole_mission_not_each_file`.
- `tests/test_reading_polish_only.py` (9 testów) pilnuje braku obcej prozy
  (zakresy Unicode CJK/kana + strażnicze napisy), jawności braków,
  braku flagi `--reference` w API i reprodukowalności buildu.
  Dawny `tests/test_reading_reference.py` został zastąpiony.
- `tools/build_dictionary_request.py`, `tools/collect_dictionary_tables.ps1`,
  `docs/PROSBA_ENCYKLOPEDIA_Y.md`, `tests/test_dictionary_request.py` (7 testów)
  — nowy kit (§3); kit wpisany też do `tests/test_ps_kits.py`.
- `data/dictionary_owner_assets.json` uzupełniony o `folder`, `file`,
  `relative_path` (wszystkie 11 w `aa/StandaloneWindows64`).
- `.github/workflows/srw-y-import.yml` — nowe pliki testów w CI.

Testy: **pełne `pytest -q`: 531 passed, 28 skipped, 90 subtests passed**;
zestaw CI: **186 passed, 63 subtests passed**.

## 3. Pakiet bat+ps1 dla właściciela — DO URUCHOMIENIA

**`SRW_Y_ENCYKLOPEDIA_PROSBA.zip`** — 3 704 B,
SHA-256 `05b684b179326f6bf2411a3d46745e5098ba7f5576d70f1202baff14c7512437`,
id Drive `1HHzkphxag2CwFkSmFq7UKQDFLe6a2YMK`
([pobierz](https://drive.google.com/file/d/1HHzkphxag2CwFkSmFq7UKQDFLe6a2YMK/view?usp=drivesdk)).
W środku: `URUCHOM_TO.bat`, `ZBIERZ_ENCYKLOPEDIA.ps1`, `CZYTAJ_TO.txt` —
identyczny format jak `SRW_Y_MISSION_PROSBA.zip`. Generator:
`python3 tools/build_dictionary_request.py`; skrypt jest BOM+CRLF+ASCII,
bez przecinka przed `)`, testowany deterministycznie.

**Co robi:** szuka gry w typowych folderach Steam, kopiuje **11 małych bundli**
(58 461 B łącznie) z `StreamingAssets/aa/StandaloneWindows64` do
`SRW_Y_ENCYKLOPEDIA` na pulpicie, pakuje do **`SRW_Y_ENCYKLOPEDIA.zip`**
i wypisuje rozmiar + SHA-256. Niczego w grze nie zmienia.

**Co odesłać:** `SRW_Y_ENCYKLOPEDIA.zip` z pulpitu na ten sam folder Drive.
Jeśli skrypt wypisze `BRAK`, wyślij zip mimo to razem z logiem
`SRW_Y_ENCYKLOPEDIA_log.txt`.

Zbierane assety (wszystkie z bazowego `catalog.json`):

| asset | klasa | rozmiar |
|---|---|---:|
| `PilotDictionaryEntryTable` + `_D1.._D4` | `PilotDicEntryList` | 5 plików |
| `RobotDictionaryEntryTable` + `_D1.._D4` | `RobotDicEntryList` | 5 plików |
| `WordDictionaryEntryTable` | `WordDicEntryList` | 1 plik |

**To NIE jest prośba o presety** i nie ma związku z 91 PPtr. Nie potrzebujemy
całej gry, audio, scen ani `GameAssembly.dll`. Szczegóły:
[`docs/PROSBA_ENCYKLOPEDIA_Y.md`](PROSBA_ENCYKLOPEDIA_Y.md).

## 4. Co jeszcze nie jest zrobione (A–D)

### A. Biografie/opisy przy pierwszym wystąpieniu — OTWARTE, teraz z konkretną prośbą

Mamy teksty `dic_text_*`, ale nie mamy rekordów mówiących, **która postać/mech
dostaje który wariant**. Audyt na świeżym indeksie, 741 nazwanych obiektach
MonoBehaviour i 11 katalogach: 11/11 bundli właścicielskich nie istnieje w
odzyskanych paczkach, 0 obiektów źródłowych dla 10 audytowanych assetów
(11. to `WordDicEntryList`). `reading_audit.py` odtwarza to w
`local/reading-research/prerequisite-mode-audit-next.json`.

Dlaczego nie łączymy po kluczu: `dic_text_pilot` ma 427 grup,
`dic_text_robot` 297, `dic_text_name` 29, `dic_text_word` 78; 16 grup pilotów
i 29 robotów nie ma żadnego dokładnego ID w rekordach gry, a pozostałe grupy
pasują do wielu różnych pól (`listFacialSettingData`, `listShotdownMessageData`,
`defaultReferenceId`…). Równość `dic_pilot_X` z jakimś `X` nie wyznacza
właściciela. Dlatego `deployment.md` ma dziś jawny
`[BRAK POTWIERDZONEGO POWIĄZANIA BIOGRAFII/OPISU]`.

**Po odesłaniu kitu:** odszyfrowanie → zrzut drzew obiektów z proweniencją →
odtworzenie dokładnego schematu trzech klas → połączenie `entry → ID → dic_text_*`
po rzeczywistym ID → polska biografia/opis przy pierwszym wystąpieniu w
`deployment.md`, `piloci.md`, `mechy.md`.

⚠️ **Ważne:** assety dają **powiązanie własności**, ale nie dają **polskiej
prozy**. Teksty encyklopedii są dziś tylko po japońsku i angielsku; skoro pliki
mają być w 100% po polsku, po przypisaniu nadal będzie tam `[BRAK PL]` aż do
zwrotu tłumacza (albo do wykonania osobnego polskiego tłumaczenia tych haseł).

### B. 91 nierozwiązanych PPtr — bez zmian, bez prośby o presety

**Co to jest.** `preset` to obiekt danych w bundlu gry z listą rozstawienia
jednostek misji (`playerPlacementData`, `enemyPlacementData`,
`rpObjectRegisterDatas`). Misja wskazuje go wskaźnikiem Unity **PPtr**
=`{m_FileID, m_PathID}`: numer pliku z listy `externals` danego obiektu +
identyfikator obiektu w tym pliku. `deployment.md` buduje z tego listę
uczestników. 91 takich wskaźników (w 82 misjach) nie znalazło celu w żadnym
odzyskanym bundlu — czyli dla tych kompozycji nie mamy rozstawienia.

**Pomiar z 2026-10-27 (`local/reading-research/pptr-analysis.json`,
`pptr-script-bundles.json`):**

| sprawdzenie | wynik |
|---|---:|
| nierozwiązane wskaźniki | 91 (82 misje, 91 różnych docelowych CAB-ów) |
| docelowe CAB-y w 716 odzyskanych bundlach | **0 / 91** |
| obiekty o docelowych PathID gdziekolwiek w odzyskanych danych | **0** |
| ten sam PathID w innym CAB | 0 |
| `script_file` tych kompozycji w katalogach gry | **91 / 91 to `Unity.VisualScripting.ScriptGraphAsset`** |
| różne bundl e z tymi grafami | **89**, razem **2 618 505 B**, wszystkie w listingu właściciela |
| z tego wśród 366 bundli grafów z punktu C | **89 / 89** |

Czyli 91 wskaźników nie jest dowodem brakujących plików u właściciela: pliki
istnieją w jego grze (są w `listing_sizes.txt`), po prostu **żadna z dotychczasowych
paczek nie zawierała tych 89 bundli z grafami zdarzeń DLC/bonusów**. To luka w
tym, co kiedykolwiek poproszono i odzyskano, a nie błąd po stronie właściciela.
Dlatego zgodnie z jego decyzją nie prosimy o „kolejne presety” — prosimy co
najwyżej o konkretne, nazwane po hashach bundl e grafów, co jest jednocześnie
wejściem do punktu C.

**Co musi się stać, żeby punkt był załatwiony:** odzyskać te 89 bundli
(2,5 MB; albo od razu wszystkie 366 bundli grafów = 12 650 148 B, co domyka
też chronologię), sprawdzić, czy docelowe CAB-y i PathID-y w nich są, i dodać
brakujące rozstawienia do `deployment.md`. Do tego czasu w czytankach te
kompozycje są po prostu pominięte — bez zgadywania i bez dopisywania presetów
z innych misji. Właściciel **nie musi teraz nic robić**; kit z §3 zbiera zupełnie
inne 11 plików.

### C. Chronologia scen / wywołań zdarzeń — NIEPOTWIERDZONA

`receipt.json`: `literal_order_verified: true`,
`conditional_event_order_verified: false`, `mission_chronology_verified: false`.
589 kompozycji z `script_file`: 368 wskazuje `ScriptGraphAsset`, 218 ma
`serifuOnly = 1` bez wpisu w katalogu, 3 nie mają ani wpisu, ani flagi.
Te 368 wpisów mapuje się na **366 bundli, z których 0 jest w odzyskanych
archiwach**. Kolejność literałów Lua nie dowodzi kolejności wywołań
warunkowych; czytanki mają bloki opisane jako „kolejność źródłowa, nie
kolejność rozegrania”. To osobny, późniejszy temat — nie jest częścią kitu z §3.

### D. Pozostałe ograniczenia przed pełnym wydaniem

- **Brak polskiego tekstu:** 115 153 jawne braki; bez zwrotu od tłumacza nie
  wolno ogłaszać wydania pełnym.
- **Importer zwrotek niezweryfikowany** na prawdziwym, wypełnionym zwrocie v8
  w tym checkoucie; testowany syntetycznie.
- **Pełna przebudowa bundle'i / patch / test w grze:** `runtime_tested = false`.
- **Różnice snapshotów:** odtworzony pełny S6 ma 120 794 wiersze scen,
  614 scen, 144 tabele, 44 344 wiersze tabel; v8/historyczny handoff ma
  120 665 / 611 / 143 / 44 340. Nie wolno mieszać pieczęci źródeł przy
  imporcie zwrotki.
- **Cytaty bitewne poza czytankami**; deployment bez momentów wejścia do bitwy.

## 5. Jak odtworzyć (prywatne `local/`, poza Git)

```
.venv/bin/python tools/reading_index.py \
  --bundles local/reading-research/{SRW_Y_MISSION,SRW_Y_GLOSY,srw_y_text,\
srw_y_tekst,srw_y_dlc_bundle,srw_y_free_patch} \
  --out local/reading-research/context-index-next.json
.venv/bin/python local/reading-research/restore_s6_full.py
.venv/bin/python tools/build_reading_y.py \
  --source-dir local/reading-research/s6-full \
  --index local/reading-research/context-index-next.json \
  --evidence data/dictionary_owner_assets.json \
  --out local/reading-research/polish-edition
.venv/bin/python tools/build_dictionary_request.py
```

Nie ma już flagi `--reference`; próba jej użycia kończy się błędem argparse.

## 6. Czego nie robić (decyzje nadal wiążące)

- Nie wstawiać japońskiego źródła ani angielskiego odniesienia do plików `.md`
  — nawet jako opcjonalnej, oznaczonej kolumny.
- Nie dopasowywać encyklopedii po nazwie, prefiksie `dic_*` ani fuzzy matching.
- Nie interpretować 91 PPtr jako brakujących plików u właściciela.
- Nie twierdzić, że kolejność literałów Lua to chronologia zdarzeń.
- Nie wykorzystywać `samples-b080-2026-10-27.zip` (inny projekt).

## 7. Następny krok

1. Właściciel uruchamia `SRW_Y_ENCYKLOPEDIA_PROSBA.zip` i odsyła
   `SRW_Y_ENCYKLOPEDIA.zip`.
2. My robimy dokładne powiązanie encyklopedii (§4 A) i aktualizujemy czytanki.
3. Gdy przyjdzie zwrot tłumacza: `pl_import` na zregenerowanym S6 (uwaga na
   pieczęć v8), potem `build_reading_y.py` bez żadnych flag językowych —
   znaczniki `[BRAK PL]` znikają wraz z polską prozą.
