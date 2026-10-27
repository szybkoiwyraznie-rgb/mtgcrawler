# SRW Y — czytanki: wyniki obu zwrotów właściciela i co zostało (2026-10-27)

Aktualny handoff. Poprzedni — [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md)
— opisuje stan **przed** odesłaniem zipów i pozostaje jako historia decyzji.
Gałąź `arena/ff68be19-mtgcrawler`, draft PR #28
(`https://github.com/szybkoiwyraznie-rgb/mtgcrawler/pull/28`).

Decyzje właściciela nadal obowiązują: czytanki **w 100% po polsku** (bez kolumn
JP/EN), protagonista domyślnie mężczyzna (żeński tylko w misjach bez wariantu
męskiego, linie wspólne zostają), encyklopedia w `deployment.md` jest kluczowa.

---

## 1. Co przyszło i czy jest kompletne

| paczka | id Drive | bajty | SHA-256 (lokalnie = na Drive) |
|---|---|---:|---|
| `SRW_Y_ENCYKLOPEDIA.zip` | `1zOvGytrG1URVxi8f5UvDprwmlzKbDkFJ` | 60 738 | `7e0bf19047bbffb7ec697e61dd77016064d6fa1c3206082263cc38bada9fdca0` |
| `SRW_Y_GRAFY.zip` | `1YolDKYGk0nryG2wuk8qq-VxQVY6rRzQW` | 12 726 061 | `8c6451349ef1e80037a648af9f4ee34287086d5e800fc549c59405a4c8563156` |

Zawartość: dokładnie **11** bundli / 58 461 B oraz **366** bundli / 12 650 148 B
— tyle, ile prosiły oba kity. Rozpakowano do prywatnego
`local/reading-research/{ENCYKLOPEDIA,GRAFY}` poza Git, z normalizacją
windowsowych separatorów w nazwach ZIP.

---

## 2. A. Encyklopedia — POWIĄZANIE ZAMKNIĘTE (proza nadal po polsku nie istnieje)

11 assetów to nie tajemnicze `PilotDicEntryList`, tylko tabele o schematach:

- `PilotDictionaryEntryTable` + `_D1.._D4`: **786 wierszy**,
  `BaseID → TextID` (+ `FaceID`, `VoiceActorID`, `Face`, `Voice`, `order`, `pkg`);
- `RobotDictionaryEntryTable` + `_D1.._D4`: **1 220 wierszy**,
  `BaseID → TextID` (+ `HeightNumStr`, `WeightNumStr`, `Direction`, `pkg`);
- `WordDictionaryEntryTable`: **78 wierszy**, `TextID → ProductID`.

`TextID` łączy się z kluczami Shared Data **dosłownie**:
`dic_pilot_{TextID}_*`, `dic_robot_{TextID}_*`, `dic_word_{TextID}_*`,
`dic_name_{ProductID}_*`. Trzeba przeszukać **wszystkie** warianty tabel
(`dic_text_pilot` + `-DLC1..4` itd.), bo DLC dopisuje dalsze części hasła
(np. `dic_pilot_SHOU_00_2` jest wyłącznie w `dic_text_pilot-DLC4`). To nie jest
dopasowanie po nazwie — to wyszukanie klucza o identycznym prefiksie złożonym
z pola `TextID` odczytanego z assetu.

Wynik w `data/dictionary_links.json` (`tools/build_dictionary_links.py`):

| rodzina | grup TextID | dokładnych kluczy | grup bez kluczy |
|---|---:|---:|---|
| pilot | 419 | 1 320 | 0 |
| robot | 294 | 628 | 0 |
| word | 78 | 243 | 0 |
| name | 17 | 48 | 1 (`ORGNL` — brak wpisu w tabelach gry) |

Każdy rekord ma proweniencję: nazwa assetu, SHA-256 bundla, CAB, PathID.

**W wydaniu czytanek** (`docs/reading/pl-2026-10-27/`, schema recepty 3):

- `deployment.md`: pierwsze wystąpienie ma `Powiązanie biografii/opisu:
  potwierdzone`, ID rekordu, klucz tekstu, źródło (bundle/CAB/PathID), liczbę
  części i każdą część z kluczem Shared Data. Mechy dostają też językowo
  neutralne dane liczbowe z encyklopedii (wysokość, masa; japońskie
  placeholdery `－－－` są odrzucane).
- `piloci.md` i `mechy.md`: własna sekcja encyklopedii przy każdym rekordzie.
- `encyklopedia.md`: tabela 11 assetów i pełna tabela potwierdzonych powiązań
  `ID rekordu → klucz tekstu → liczba części`.
- Jeśli ID nie ma wpisu w 11 assetach, jest jawny
  `[BRAK WPISU ENCYKLOPEDII]` — to **zweryfikowany brak**, nie zgadywanie.

Zmierzone pokrycie w recepcie (`encyclopedia_links.rendered_links`):

| | powiązane | bez wpisu |
|---|---:|---:|
| pierwsze wystąpienia postaci | 579 | 148 |
| pierwsze wystąpienia mechów | 880 | 37 |
| rekordy w `piloci.md` | 499 | 184 |
| rekordy w `mechy.md` | 1 139 | 59 |

⚠️ **Polska proza encyklopedii wciąż nie istnieje.** Każda część tekstu to
`[BRAK PL: dic_text_pilot/…]` itd. bez żadnego tekstu JP/EN. Powiązanie jest
gotowe: zwrot tłumacza (albo osobne polskie tłumaczenie haseł) podmieni te
znaczniki bez zmiany numeracji adresów. Wydanie pozostaje częściowe.

---

## 3. B. 91 PPtr — wynik negatywny, ale z konkretnym następnym krokiem

**Grafy nie są presetami.** W 366 bundlach `SRW_Y_GRAFY.zip` zmierzono
(`data/script_graph_evidence.json`, `tools/build_graph_evidence.py`):

| sprawdzenie | wynik |
|---|---:|
| 91 docelowych CAB-ów wśród 366 nazw plików serializowanych | **0 / 91** |
| 91 docelowych PathID-ów wśród obiektów | **0 / 91** |
| obiekty `*_preset` | **0** |
| zależności AssetBundle wskazujące na docelowe CAB-y | **0** |
| obiekty z `_data._json` (grafy Visual Scripting) | 1 570 (399 nazw) |

To są bundl e adresowane przez `script_file`; 91 wskaźników dotyczy `preset_file`.
`deployment.md` nadal jawnie pomija te rozstawienia — bez dopisywania presetów
z innych misji. Receipt: `structural_issues = 91`.

**Co znaleźliśmy zamiast tego:** katalogi Addressables mają jawne adresy
`m####_#######x_preset` (i wersje `_Patch`). Dla 88 misji pasują wprost; trzy
(`m4003_0202500`, `m4020_0200230`, `m5003_0107330`) używają `_Normal`/`_Hard`.
`bundle_for` wskazuje **109 konkretnych bundli (994 215 B)** w siedmiu folderach
`StreamingAssets`; żadnego nie ma w dziewięciu dotychczasowych archiwach.

**Trzeci kit jest zbudowany i wgrany na Drive:**
`SRW_Y_PRESETY_PROSBA.zip`, 5 792 B,
SHA-256 `42618455ab9bfa5384f7802d2871d8b8a034f18458ed6228b0eee83f44d3a305`,
id `1_6wNI8WM0bq7QuqjMqDayAaJSMu5d1QH`. Generator
`tools/build_preset_request.py`, skrypt `tools/collect_missing_presets.ps1`,
opis [`PROSBA_PRESETY_Y.md`](PROSBA_PRESETY_Y.md). Wynik do odesłania:
`SRW_Y_PRESETY.zip`. Po jego otrzymaniu rebuild indeksu z nowymi bundlami,
sprawdzenie dokładnych par (CAB, PathID) i uzupełnienie `deployment.md`.

---

## 4. C. Chronologia wywołań zdarzeń — PRÓBA STATYCZNA, bez dowodu

Grafy zawierają pełny JSON Visual Scripting: jednostki i połączenia sterowania.
Zmierzono (`data/script_graph_evidence.json`):

| jednostki / połączenia | liczba |
|---|---:|
| `TalkStartUnit` | 7 410 |
| `AdventureStartUnit` | 724 |
| `EventStartUnit` | 1 986 |
| `NumberedEventUnit` | 1 525 |
| `Unity.VisualScripting.If` (rozgałęzienia) | 1 382 |
| `ControlConnection` | 67 214 |
| `ValueConnection` | 25 243 |
| zakresy (graf + podgrafy) z wywołaniami zdarzeń | 1 089 |
| zakresy o **jednoznacznym liniowym ciągu ze statycznymi numerami** | **668** |

`tools/build_graph_evidence.py` wyciąga łańcuchy sterowania (`control_order`)
i porównuje je ze statycznym rejestrem `t_tbl` w Lua. Rejestr Lua jest
**tablicą odczytu, nie harmonogramem** (`reading_events.py` mówi to wprost),
a 421 zakresów ma rozgałęzienia, równoległe wyzwalacze lub numery zdarzeń
podawane przez `ValueConnection`. Nie ma więc dowodu na pełną chronologię
wywołań warunkowych.

**Receipt nadal:** `literal_order_verified: true`,
`conditional_event_order_verified: false`, `mission_chronology_verified: false`.
Nagłówki rozdziałów dostały jawną informację o 366 przeanalizowanych paczkach
grafów. Nie zmieniamy kolejności bloków zdarzeń na „kolejność rozegrania”.

---

## 5. Nowe wydanie czytanek (100% PL)

`docs/reading/pl-2026-10-27/` — 14 plików `.md` + `receipt-summary.json`.
Skan: **0 znaków CJK/kana, 0 kolumn JP/EN, 0 japońskich etykiet mówcy**.
Jedyny obcy zapis to identyfikatory techniczne (`dic_*`, CAB, PathID,
`ScriptGraphAsset`) i nazwy pól danych gry.

Paczka na Drive: **`SRW_Y_CZYTANKI_PL_2026-10-27.zip`**,
3 084 996 B, SHA-256
`c00fa4b3b6031bbf9faecaa2c6da24711b7c63d19d1c116889737d259e5325fb`,
id `1DPXcvpZTBrxrD33BVncFpFky6FdVzaKD`. Zawiera 14 `.md`, skrócony recepcik,
pełny `receipt.json` i deterministyczny `srwy_reading_PL.zip`. Stara paczka
(id `1mn6zJ5j_t1GiOUvQVcnQwyTFVImPMYk5`) przeniesiona do kosza Drive.

Recepcik (schema 3): `polish_only: true`, `runtime_tested: false`,
114 652 jawne braki `[BRAK PL]` / `[BRAK WPISU ENCYKLOPEDII]`,
112 692 unikalnych użytych adresów, `structural_issues: 91`,
`encyclopedia_links` i `script_graphs` z pieczęciami obu nowych plików
metadanych. Protagonista bez zmian: 566 `M` / 1 `F`.

### Uwaga o odtworzeniu korpusu

Prywatny `restore_s6_full.py` z poprzedniej sesji zniknął. Zastąpuje go
**commitowany** `tools/restore_s6_full.py`: czyta bundl e z archiwów Drive,
język każdego assetu Lua bierze z adresu w 11 katalogach Addressables,
a tabele lokalizacyjne z obiektów `*_ja-JP`/`*_en-US`. Wynik:
**120 794 wiersze scen, 614 scen, 144 tabele, 44 344 wiersze tabel** —
zgodne z poprzednim wydaniem. `tables.jsonl` ma identyczną sumę SHA-256;
`scenario.jsonl` ma nową (`03455b67…`), bo:

- adresy `…lua.txt_Patch` / `_Patch2` są jawnie obsłużone (poprawia 1 linię
  `cse20_2010_0201710a_sdemo.lua/103.1#1`),
- deklarowane `/en/…_Patch` bundl e zawierają japoński dialog i są pomijane,
- dodano konserwatywne liniowe domknięcie wariantów EN-tylko (5 wierszy,
  z których 2 były już w poprzednich czytankach).

Weryfikacja: wszystkie rozdziały, `piloci.md` i `mechy.md` z rebuildu bez
nowych dowodów są **bajt w bajt identyczne** z opublikowanym wydaniem, a zbiór
adresów scen poprzedniego wydania jest w pełni zawarty w nowym. Nic nie zginęło.

---

## 6. Co zostało (pozostałe braki)

1. **Zwrot tłumacza.** Bez wypełnionych `PL:` czytanki pozostają częściowe;
   114 652 jawne znaczniki. `plik_dla_tlumacza_v8.zip` ma puste `PL:`.
2. **109 bundli z presetami.** Trzeci kit czeka na uruchomienie; bez nich
   91 PPtr i rozstawienia w `deployment.md` są niekompletne.
3. **Chronologia wywołań warunkowych.** `false` w recepcie; grafy dają 668
   jednoznacznych zakresów z 1 089, nie pełny dowód. Wymagałoby to albo
   runtime’u, albo pełnej semantyki wyzwalaczy gry.
4. **Importer zwrotek** niezweryfikowany na prawdziwym, wypełnionym zwrocie
   v8; testowany syntetycznie. Uwaga na różnicę pieczęci: v8 ma
   120 665 / 611 / 143 / 44 340, pełny S6 ma 120 794 / 614 / 144 / 44 344.
   Nie wolno mieszać snapshotów.
5. **Runtime / patch:** `runtime_tested = false`. Nie zrobiono pełnej
   przebudowy patcha ani testu w grze.
6. **Cytaty bitewne** są poza czytankami; deployment nie ma momentów wejścia
   do bitwy.

---

## 7. Jak odtworzyć (prywatne `local/`, poza Git)

```
.venv/bin/python tools/reading_index.py \
  --bundles local/reading-research/{SRW_Y_MISSION,SRW_Y_GLOSY,srw_y_text,\
srw_y_tekst,srw_y_dlc_bundle,srw_y_free_patch} \
  --out local/reading-research/context-index-next.json
.venv/bin/python tools/restore_s6_full.py \
  --bundles local/reading-research/{srw_y_text,srw_y_tekst,srw_y_dlc_bundle,\
srw_y_free_patch} \
  --catalog ../google_drive/catalog.json \
  --dlc-catalogs local/reading-research/srw_y_dlc_catalog \
  --listing ../google_drive/listing_sizes.txt \
  --out local/reading-research/s6-full
.venv/bin/python tools/build_dictionary_links.py \
  --bundles local/reading-research/ENCYKLOPEDIA \
  --index local/reading-research/context-index-next.json \
  --archive ../google_drive/SRW_Y_ENCYKLOPEDIA.zip --out data/dictionary_links.json
.venv/bin/python tools/build_graph_evidence.py \
  --bundles local/reading-research/GRAFY \
  --index local/reading-research/context-index-next.json \
  --archive ../google_drive/SRW_Y_GRAFY.zip \
  --catalog ../google_drive/catalog.json \
  --dlc-catalogs local/reading-research/srw_y_dlc_catalog \
  --listing ../google_drive/listing_sizes.txt --out data/script_graph_evidence.json
.venv/bin/python tools/build_reading_y.py \
  --source-dir local/reading-research/s6-full \
  --index local/reading-research/context-index-next.json \
  --evidence data/dictionary_owner_assets.json \
  --links data/dictionary_links.json \
  --graph-evidence data/script_graph_evidence.json \
  --out local/reading-research/final-edition
.venv/bin/python tools/summarize_receipt.py \
  --receipt local/reading-research/final-edition/receipt.json \
  --out docs/reading/pl-2026-10-27/receipt-summary.json
.venv/bin/python tools/build_preset_request.py
```

Nie ma flagi `--reference`; próba jej użycia kończy się błędem argparse.

## 8. Czego nie robić (bez zmian)

- Nie wstawiać japońskiego źródła ani angielskiego odniesienia do plików `.md`.
- Nie dopasowywać encyklopedii po nazwie ani fuzzy matching — teraz jest
  dokładne powiązanie z 11 assetów, nie wolno go zastąpić zgadywaniem.
- Nie dopisywać rozstawień z innych misji, żeby „uzupełnić” 91 PPtr.
- Nie twierdzić, że kolejność literałów Lua lub 668 liniowych zakresów grafów
  to chronologia wywołań zdarzeń.
- Nie wykorzystywać `samples-b080-2026-10-27.zip` (inny projekt).
- Nie ogłaszać pełnego wydania bez zwrotu tłumacza i bez testu runtime.
