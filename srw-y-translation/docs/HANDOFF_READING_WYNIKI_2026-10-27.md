# SRW Y — czytanki: wyniki obu zwrotów właściciela i co zostało (2026-10-27)

Aktualny handoff. Poprzedni — [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md)
— opisuje stan **przed** odesłaniem zipów i pozostaje jako historia decyzji.
Gałąź `arena/ff68be19-mtgcrawler`, draft PR #28
(`https://github.com/szybkoiwyraznie-rgb/mtgcrawler/pull/28`).

Decyzje właściciela nadal obowiązują: czytanki **w 100% po polsku** (bez kolumn
JP/EN), protagonista domyślnie mężczyzna (żeński tylko w misjach bez wariantu
męskiego, linie wspólne zostają), encyklopedia w `deployment.md` jest kluczowa.

> **AKTUALNY STAN (§11): właściciel odesłał `SRW_Y_PRESETY3.zip`.**
> Trzy bundli znalezione po wewnętrznej nazwie CAB domknęły ostatnie 3 PPtr:
> **91/91 po dokładnej parze (CAB, PathID)**, `unresolved_preset_links: 0`,
> `structural_issues: 0`. Wydanie czytanek ma **schema 5**,
> `final_preset_evidence_sha256` i 115 407 jawnych braków PL. Wszystkie liczby
> w §2–§5 i §9 opisują wcześniejsze etapy i są zachowane jako historia pomiarów.
> Nadal brakuje zwrotu tłumacza, dowodu chronologii i testu runtime.

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

To są bundli adresowane przez `script_file`; 91 wskaźników dotyczy `preset_file`.
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
**commitowany** `tools/restore_s6_full.py`: czyta bundli z archiwów Drive,
język każdego assetu Lua bierze z adresu w 11 katalogach Addressables,
a tabele lokalizacyjne z obiektów `*_ja-JP`/`*_en-US`. Wynik:
**120 794 wiersze scen, 614 scen, 144 tabele, 44 344 wiersze tabel** —
zgodne z poprzednim wydaniem. `tables.jsonl` ma identyczną sumę SHA-256;
`scenario.jsonl` ma nową (`03455b67…`), bo:

- adresy `…lua.txt_Patch` / `_Patch2` są jawnie obsłużone (poprawia 1 linię
  `cse20_2010_0201710a_sdemo.lua/103.1#1`),
- deklarowane `/en/…_Patch` bundli zawierają japoński dialog i są pomijane,
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
.venv/bin/python tools/reading_index.py \
  --bundles local/reading-research/{SRW_Y_MISSION,SRW_Y_GLOSY,srw_y_text,\
srw_y_tekst,srw_y_dlc_bundle,srw_y_free_patch,PRESETY} \
  --out local/reading-research/context-index-presets.json
.venv/bin/python tools/restore_s6_full.py \
  --bundles local/reading-research/{srw_y_text,srw_y_tekst,srw_y_dlc_bundle,\
srw_y_free_patch} \
  --catalog ../google_drive/catalog.json \
  --dlc-catalogs local/reading-research/srw_y_dlc_catalog \
  --out local/reading-research/s6-full
.venv/bin/python tools/build_dictionary_links.py \
  --bundles local/reading-research/ENCYKLOPEDIA \
  --index local/reading-research/context-index-presets.json \
  --archive ../google_drive/SRW_Y_ENCYKLOPEDIA.zip --out data/dictionary_links.json
.venv/bin/python tools/build_graph_evidence.py \
  --bundles local/reading-research/GRAFY \
  --index local/reading-research/context-index-presets.json \
  --archive ../google_drive/SRW_Y_GRAFY.zip \
  --catalog ../google_drive/catalog.json \
  --dlc-catalogs local/reading-research/srw_y_dlc_catalog \
  --listing ../google_drive/listing_sizes.txt \
  --targets-index local/reading-research/context-index-next.json \
  --out data/script_graph_evidence.json
.venv/bin/python tools/build_preset_evidence.py \
  --bundles local/reading-research/PRESETY \
  --before-index local/reading-research/context-index-next.json \
  --after-index local/reading-research/context-index-presets.json \
  --archive ../google_drive/SRW_Y_PRESETY.zip --out data/preset_evidence.json
.venv/bin/python tools/build_reading_y.py \
  --source-dir local/reading-research/s6-full \
  --index local/reading-research/context-index-presets.json \
  --evidence data/dictionary_owner_assets.json \
  --links data/dictionary_links.json \
  --graph-evidence data/script_graph_evidence.json \
  --preset-evidence data/preset_evidence.json \
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

## 9. Zwrot `SRW_Y_PRESETY.zip` — 88/91 PPtr rozwiązanych, 3 zostały

Paczka: 1 014 402 B, SHA-256
`0abd10565f9beab99447a0a9aed8c743a89f479f816740e35fea9de3e3560fe8`,
id Drive `12LIh0fZSXcXgD2FoXoqfPEshD188YYYA`. Zawiera dokładnie **109 bundli /
994 215 B** — tyle, ile prosił trzeci kit; lokalna suma zgodna z Drive.

Prywatne `local/`, `google_drive/` i `build/` wygasły między sesjami, więc całe
środowisko odtworzono z Drive. Stary indeks (6 katalogów bundli) wyszedł bajt w
bajt identyczny z poprzednim (`8dd21bf5…`), a korpus S6 również
(`03455b67…` / `45e15696…`) — dzięki commitowanemu `tools/restore_s6_full.py`.

Po dołączeniu 109 bundli `reading_index.py` daje:

| | przed | po |
|---|---:|---:|
| nierozwiązane PPtr | 91 | **3** |
| rozwiązane linki presetów | 276 | **364** |
| obiekty presetów | 277 | **380** |
| misje / piloci / mechy / tabele Shared Data | 533 / 683 / 1 198 / 144 | bez zmian |

Sekcje `shared`, `records`, `scenario_order`, `scenario_texts` i
`scenario_variants` są **identyczne** przed i po — nowe bundli dodały wyłącznie
rozstawienia. `data/dictionary_links.json` i `data/script_graph_evidence.json`
przeliczono na nowym indeksie: ich grupy/klucze/pomiary są bez zmian, zmieniły
się tylko pieczęcie indeksu. W `build_graph_evidence.py` dodano
`--targets-index`, żeby historyczny pomiar 0/91 w 366 grafach nie skurczył się
przez późniejsze rozwiązanie wskaźników.

Nowy dowód: `data/preset_evidence.json` (`tools/build_preset_evidence.py`) —
**88 dokładnych par (CAB, PathID)**, 109 bundli / 109 CAB-ów / 109 obiektów
presetów, 79 misji. `build_reading_y.py` dostał `--preset-evidence`; recepcik ma
`schema: 4`, `preset_evidence_sha256`, `preset_resolution`, `structural_issues: 3`.
`deployment.md` wypisuje przy każdej z 3 pozostałych misji dokładny brakujący
CAB i PathID, a w nagłówku 88/91. Bez zgadywania i bez podkładania presetów
z innych misji.

**Pozostałe 3** to dokładnie misje z wariantami `_Normal`/`_Hard`:

| misja | brakujący CAB | PathID |
|---|---|---:|
| `m4003_0202500` | `CAB-58e9cd9947154ef535126db225215ad0` | -3378871923023034847 |
| `m4020_0200230` | `CAB-79ddf87b4d63e5a85be58e6e5bdadfe8` | -713082379541291897 |
| `m5003_0107330` | `CAB-cd5151f08eae3cb61aecc23bad1bd323` | -6070146337825874469 |

Katalogi dla tych trzech misji mają wyłącznie adresy `_Normal` i `_Hard`; oba
bundli są w zwróconej paczce, ale ich wewnętrzne nazwy plików
(`CAB-4266ee…`, `CAB-c799f1…`, `CAB-d0e6eb…`, `CAB-ab9cbe…`, `CAB-0dbd01…`,
`CAB-ac2b04…`) i PathID-y **nie są** celami wskaźników. Żadna z 91 docelowych
par nie występuje też w żadnym wcześniejszym archiwum. Zamknięcie ostatnich 3
wymagałoby więc czwartego, celowanego zestawu bundli (skan po wewnętrznej
nazwie pliku w grze) — na razie są jawnie wykazane, nie „domknięte na siłę”.

**Chronologia bez zmian:** `conditional_event_order_verified: false`,
`mission_chronology_verified: false`. Presety niosą rozstawienia, nie harmonogram
zdarzeń.

**Nowe wydanie czytanek:** `docs/reading/pl-2026-10-27/` (14 plików `.md`,
0 znaków CJK/kana), `receipt-summary.json` schema 4, 115 369 jawnych braków,
112 692 użytych adresów, `polish_only: true`, `runtime_tested: false`.
Pierwsze wystąpienia po rozszerzeniu rosteru: 579 postaci z powiązaniem,
943 mechów z powiązaniem. Paczka na Drive została podmieniona.

Pozostałe braki (bez zmian): zwrot tłumacza, 3 PPtr, dowód chronologii,
weryfikacja importera na prawdziwym zwrocie v8, test runtime.

## 10. Czwarty, celowany kit + czystka testów (2026-10-27)

**`SRW_Y_PRESETY3_PROSBA.zip`** (generator `tools/build_final_preset_request.py`,
skrypt `tools/collect_final_presets.ps1`, opis
[`PROSBA_PRESETY3_Y.md`](PROSBA_PRESETY3_Y.md)) zamyka ostatnie 3 PPtr bez
zgadywania nazw plików. Skrypt w PowerShellu 5.1 (bez Pythona):

- czyta pierwsze **512 B każdego** `.bundle` w `StreamingAssets`,
- odszyfrowuje je znanym szyfrem `SeekableAesStream` (PBKDF1-SHA1 × 100 →
  AES-128-ECB, licznik od 1, XOR) — wewnętrzna nazwa `CAB-…` leży na pozycji 92,
- porównuje z trzema dosłownymi napisami z `data/preset_evidence.json`,
- kopiuje trafione bundli + `manifest.txt` do `SRW_Y_PRESETY3.zip`.

Ma wbudowany **samotest szyfru** ze znanym szyfrogramem; jeśli port .NET jest
błędny, skrypt zatrzymuje się z czerwonym komunikatem zamiast odesłać pusty zip.
Wektor i algorytm są sprawdzane w `tests/test_final_preset_kit.py`, a składnię
wszystkich 14 skryptów `.ps1` sprawdza prawdziwy parser `tree-sitter-powershell`
(wymieniony w CI).

**Czystka testów (decyzja właściciela).** Usunięto wszystkie testy wyciszone
oraz wszystkie zależne od plików spoza repo: całe pliki
`test_patcher.py`, `test_mission_request.py`, `test_ui_atlas_orientation.py`,
pojedyncze testy w `test_bundle_crypt.py`, `test_srw_y_key.py`,
`test_srw_y_find_text.py`, `test_pl_patch.py`, `test_ui_atlas.py` i
`test_ui_prefab_patch.py`. `test_ps_kits.py` przepisano tak, by lintował
wyłącznie commitowane `tools/collect_*.ps1` i generatory czytające commitowane
metadane. Usunięto też dekoratory `skipUnless(HAVE_CRYPTO)` — `pycryptodome`
jest jawną zależnością CI. Dodano `tests/conftest.py`, który **przerywa sesję
z kodem 1, jeśli cokolwiek zostanie pominięte**, oraz naprawiono prawdziwy
błąd (końcowy przecinek) w `collect_dlc_catalogs.ps1` i jego generatorze.

Wynik: pełny `pytest -q` w symulacji czystego checkoutu (bez `local/`,
`build/`, `google_drive/`) → **561 passed, 0 skipped, 4 552 subtests**.
CI wykonuje teraz cały zestaw jedną komendą `python -m pytest -q -rs`.

---

## 11. Zwrot `SRW_Y_PRESETY3.zip` — 91/91 PPtr, `structural_issues: 0`

Właściciel uruchomił czwarty, celowany kit i odesłał **`SRW_Y_PRESETY3.zip`**:
id Drive `1b6OHFzKoq0ysZZoSSQp6DkKWFcEwl4Ja`, **28 023 B**, SHA-256
`92de45977a54fcd3d10b688131214ec635c3da3c37b21ae6c2b5ecf888261b36`
(lokalnie = na Drive). ZIP ma **3 bundli / 27 206 B** i `manifest.txt`:

| plik (hash bundla) | wewnętrzny CAB | PathID celu | obiekt presetu | ścieżka w grze |
|---|---|---:|---|---|
| `906048a7c794a067f9fd269c9a37bd10.bundle` | `CAB-58e9cd9947154ef535126db225215ad0` | -3378871923023034847 | `m4003_0200500a_preset` | `ExpansionPack\` |
| `a7a4c234679672036f4358d34d8086bc.bundle` | `CAB-79ddf87b4d63e5a85be58e6e5bdadfe8` | -713082379541291897 | `m4020_0202300a_preset` | `ExpansionPack\` |
| `e5aff4d5c30c0e1f4589c10ebc0303c2.bundle` | `CAB-cd5151f08eae3cb61aecc23bad1bd323` | -6070146337825874469 | `m5003_0107320a_preset` | `aa\StandaloneWindows64\` |

**Wszystkie 3 dokładne pary (CAB, PathID) trafiają w obiekty `MonoBehaviour`
`*_preset`.** Uwaga: nazwa obiektu nie pokrywa się z ID misji (np.
`m4003_0200500a_preset` dla misji `m4003_0202500`) — właśnie dlatego czwarty
kit skanował nagłówki po wewnętrznej nazwie CAB, a nie zgadywał plików po
nazwie misji. Samotest szyfru w skrypcie PS zadziałał.

Środowisko znowu wygasło (`local/`, `build/`, `.venv/`), więc odtworzono je z
Drive. Stary indeks z 6 katalogów wyszedł identycznie (`8dd21bf5…`), korpus S6
także (`03455b67…` / `45e15696…`). `reading_index.py` z 6 katalogami +
`PRESETY` (109) + `PRESETY3` (3):

| | 6 katalogów | +109 presetów | **+3 presety (finalny)** |
|---|---:|---:|---:|
| `unresolved_preset_links` | 91 | 3 | **0** |
| `preset_links` | 276 | 364 | **367** |
| `presets` | 277 | 380 | **383** |
| misje / piloci / mechy / tabele | 533 / 683 / 1 198 / 144 | bez zmian | bez zmian |

Indeks finalny: SHA-256
`b1b1c368212296123842d17079f314fd0e0330e249dcf0973c15901ea20ab478`.
Sekcje `shared`, `records`, `record_origins`, `scenario_order`,
`scenario_texts`, `scenario_variants` i `system_entries` są **identyczne** przed
i po — 3 nowe pliki dodały wyłącznie rozstawienia. `issues` zeszły z 3 do 0.

### Nowe artefakty w repo

- `data/final_preset_evidence.json` — `tools/build_final_preset_evidence.py`:
  proweniencja archiwum + `manifest.txt`, SHA/rozmiary/CAB-y 3 bundli, 3
  dokładne złączenia (CAB, PathID), diff indeksów, `total_resolved: 91`,
  `total_remaining: 0`, `remaining: []`. Historyczny
  `data/preset_evidence.json` **zostaje bez zmian** (88/91, 3 cele) jako dowód
  tamtego pomiaru i jako wejście czwartego kita.
- `tools/build_reading_y.py` dostał `--final-preset-evidence`: `deployment.md`
  i `README.md` wypisują teraz `88/91` (pierwsza paczka), `3/3` (druga) i
  `razem 91/91`, `Pozostaje 0 misji bez rozstawienia`. Recepcik ma **schema 5**,
  `final_preset_evidence_sha256` i `final_preset_resolution`.
- `tools/summarize_receipt.py` przepisuje oba nowe pola do skróconego recepciku.
- `tools/build_reading_package.py` — deterministyczny ZIP dla właściciela
  (17 członów, stały znacznik czasu i tryb; 14 `.md` + skrócony recepcik +
  pełny `receipt.json` + `srwy_reading_PL.zip`).
- `tests/test_final_preset_evidence.py` — 13 testów: proweniencja, 3 dokładne
  pary, 91/91, diff indeksów, parser `manifest.txt`, schema 5, 100% PL,
  recepcik i determinizm paczki. **Wszystkie wejścia są w repo** — zero skippów.

`data/dictionary_links.json` i `data/script_graph_evidence.json` przeliczono
na finalnym indeksie (z `--targets-index` dla historycznego 0/91 w grafach):
grupy, klucze i pomiary bez zmian, zmieniły się tylko pieczęcie indeksu.

### Wydanie (schema 5)

`docs/reading/pl-2026-10-27/` — 14 plików `.md` + `receipt-summary.json`.
Skan: **0 znaków CJK/kana, 0 wielojęzycznych nagłówków kolumn** (`EN` w
`mechy.md` to statystyka energii mecha, nie kolumna języka). Recepcik:
`polish_only: true`, `runtime_tested: false`, `structural_issues: 0`,
**115 407 jawnych braków** `[BRAK PL]` / `[BRAK WPISU ENCYKLOPEDII]`,
112 692 użytych adresów, 4 607 wierszy scen bez japońskiego źródła,
`literal_order_verified: true`, `conditional_event_order_verified: false`,
`mission_chronology_verified: false`. Protagonista bez zmian (566 `M` / 1 `F`).

Paczka na Drive: **`SRW_Y_CZYTANKI_PL_2026-10-27.zip`**,
id `1DXBz0q9Nk9suXpIL1Ju9sVQm3KYpGPCV`, **3 103 804 B**, SHA-256
`8bb038fc4b4f3439990d717c5212bb9d0cb8941c795561d47c4383d5175cf877`.
Wewnętrzny `srwy_reading_PL.zip`: `cb4e0619c332…`. Poprzednie paczki o tej
samej nazwie (id `1xS3k-6TMq1KYLKKR_4rTLnXUQIYAiEDd`,
`1m59pW6irvyU8BJbEnLKiHyK6M28vdAzL`, `1gdLuAcKxuudIG8BWnWSLX5D4pGH9Fr0W`)
przeniesione do kosza Drive.

### Odtworzenie (prywatne wejścia z Drive)

```sh
.venv/bin/python tools/reading_index.py \
  --bundles local/reading-research/{SRW_Y_MISSION,SRW_Y_GLOSY,srw_y_text,srw_y_tekst,srw_y_dlc_bundle,srw_y_free_patch,PRESETY,PRESETY3} \
  --out local/reading-research/context-index-final.json
.venv/bin/python tools/build_final_preset_evidence.py \
  --bundles local/reading-research/PRESETY3 \
  --before-index local/reading-research/context-index-presets.json \
  --after-index local/reading-research/context-index-final.json \
  --preset-evidence data/preset_evidence.json \
  --archive ../google_drive/SRW_Y_PRESETY3.zip \
  --out data/final_preset_evidence.json
.venv/bin/python tools/build_reading_y.py \
  --source-dir local/reading-research/s6-full \
  --index local/reading-research/context-index-final.json \
  --evidence data/dictionary_owner_assets.json \
  --links data/dictionary_links.json \
  --graph-evidence data/script_graph_evidence.json \
  --preset-evidence data/preset_evidence.json \
  --final-preset-evidence data/final_preset_evidence.json \
  --out local/reading-research/final-edition
.venv/bin/python tools/summarize_receipt.py \
  --receipt local/reading-research/final-edition/receipt.json \
  --out docs/reading/pl-2026-10-27/receipt-summary.json
.venv/bin/python tools/build_reading_package.py \
  --docs docs/reading/pl-2026-10-27 \
  --receipt local/reading-research/final-edition/receipt.json \
  --reading-zip local/reading-research/final-edition/srwy_reading_PL.zip \
  --out build/SRW_Y_CZYTANKI_PL_2026-10-27.zip
```

### Co zostało (bez zmian)

Strukturalne powiązania presetów są domknięte, ale **wydanie nadal nie jest
pełne**: brak zwrotu tłumacza z wypełnionymi `PL:` (115 407 jawnych braków),
brak dowodu chronologii wywołań zdarzeń, brak weryfikacji importera na
prawdziwym zwrocie i brak testu runtime. Nie wolno ogłaszać pełnego wydania.
`SRW_Y_PRESETY3_PROSBA.zip` pozostaje na Drive jako opis metody; nie jest już
potrzebny do dalszej pracy.
