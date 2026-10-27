# Handoff — czytanki SRW Y, 2026-10-27

## Punkt wznowienia

**Zadanie nie jest zakończone.** Działają generatory częściowych czytanek, ale
właściwe biografie/opisy przy pierwszym wystąpieniu, 91 powiązań presetów oraz
chronologia wywołań zdarzeń nadal wymagają źródłowego potwierdzenia.
Nie dostarczono pełnego wydania czytanek PL ani dowodu runtime.

- Repo: `szybkoiwyraznie-rgb/mtgcrawler`.
- Jedyna gałąź robocza: `arena/77d28fec-mtgcrawler`; nie przełączać ani nie zmieniać nazwy.
- Otwarty **draft PR #27**: https://github.com/szybkoiwyraznie-rgb/mtgcrawler/pull/27.
- Stan kodu przed zapisem tego handoffu: `68fa808aa3456e2581407439f300334c47960b1d`.
- Ostatnie testy kodu: **169 passed, 1 skipped, 57 subtests passed**.
- Ostatni prywatny build diagnostyczny bez PL: **964/964** renderowalne pliki Lua
  przeszły sprawdzenie tekstu, kolejności literałów i kontekstu zdarzeń.
- `runtime_tested=false`. OE nietknięte; jest ukończonym punktem odniesienia, nie
  projektem do dalszego rozwijania w tym zadaniu.

Przed pracą przeczytać root `AGENTS.md`, instrukcje Y oraz `docs/READING_Y.md`.
Poniższy stan jest nowszy niż wcześniejsze checkpointy z 29/35/38 testami czytanek.
Każdy spójny etap commitować i wypychać do istniejącego PR; nie kończyć na lokalnym
commicie. Nie commitować źródeł gry, prywatnych indeksów, zrzutów ani buildów.

## Wiążące decyzje właściciela — nie otwierać ponownie

1. Jeden protagonista na **całą misję**: domyślnie mężczyzna; kobieta tylko gdy
   misja ma wariant żeński i nie ma męskiego. Linie wspólne zostają.
2. Cytaty bitewne są **poza zakresem czytanek**. Nie mieszać ich dawnych braków
   identyfikacji mówców z odnośnikami presetów.
3. Deployment może listować uczestników bez momentów wejścia do bitwy.
4. Pierwsze wystąpienie każdej nowej postaci i mecha ma dostać właściwą biografię
   lub opis encyklopedii. Sam znacznik braku albo osobny indeks tekstów nie spełnia
   tego wymagania.
5. Kolejność scen/tekstów musi być sprawdzona i potwierdzona. Kolejność literałów
   Lua nie dowodzi chronologii wywołań warunkowych zdarzeń.
6. Nie uznawać 91 PPtr za dowód brakujących plików u właściciela. Nie przygotowywać
   kolejnej prośby o presety na tej podstawie; najpierw badać dostarczone dane.
7. Wykorzystywać lekcje niezawodności importera OE. Powiązania po rzeczywistych ID,
   bez fuzzy matching i bez nieoznaczonego fallbacku EN/JP.

## Co jest już zaimplementowane

- `tools/reading_index.py`: graf misji/presetów, dokładne CAB + PathID, zakresy DLC,
  pełne klucze Shared Data; fizyczne warianty Lua z tekstem, tabelą, PID i gałęzią.
  Zachowuje `serifuOnly`, `source_index` i surowy `preset_pointer`.
- `tools/build_reading_y.py`: częściowy PL z zaakceptowanych, źródłowo związanych
  planów importu; wybór protagonisty dla całej misji; obowiązkowa kontrola źródła
  przed filtrem płci; deterministyczne MD/ZIP i receipt; publikacja do nowego
  katalogu przez staging, bez nadpisywania wejść lub starszego wydania.
- Deployment: jawne uczestnictwo w presetach, subpiloci, deduplikacja; referencje
  runtime tylko przez jawne przypisania BasisID z tej samej misji, nie po nazwie.
- Osobny dział postaci dialogów: dokładne PID → definicja pilota/facial setting,
  z tym samym filtrem protagonisty. Postać przemawiająca **nie jest** przez to
  dopisywana jako jednostka bojowa. Wspólna tożsamość po facial ID, nie imieniu.
- Pierwsze wystąpienia są wykrywane, ale właściwe biografie **nie są przypisane**:
  obecne znaczniki braku są świadomym ograniczeniem, nie ukończoną funkcją.
- `tools/reading_events.py`: konserwatywny statyczny odczyt rejestru `t_tbl`, bez
  wykonywania Lua. Oddzielne bloki zdarzeń w czytankach. ID rejestru nie jest czasem.
- `tools/reading_audit.py`: audyt dokładnych kluczy/typów katalogu i dostarczonych
  obiektów; zachowuje zakres katalogu, deduplikuje alias GUID przez wpis główny,
  hashuje wejścia. Nie zgaduje nazw presetów ani nie podmienia odnośników.

## Co zrobić dalej — priorytety i warunki zamknięcia

### A. Biografie i opisy przy pierwszym wystąpieniu

**Ustalone:** katalog wskazuje 10 assetów: `PilotDictionaryEntryTable` oraz
`RobotDictionaryEntryTable`, każdy base + D1…D4. Typy:
`Com.BBStudio.SRTeam.Data.PilotDicEntryList` / `RobotDicEntryList`.
W zrzutach przekazanych do obecnego audytu nie znaleziono ich obiektów źródłowych.
To ograniczenie badanego zestawu, nie dowód nieobecności we wszystkich archiwach
lub w grze właściciela. Wcześniejsze celowane wyszukiwanie nazw na Drive niczego
nie zwróciło; nie dowodzi to braku w inaczej nazwanym archiwum.

**Do wykonania:**
- Ustalić zawartość właściwych rekordów i źródłowe związki właściciela wpisu,
  wariantu/odblokowania oraz kluczy opisu. Nie odgadywać schematu z nazwy klasy.
- Zweryfikować mapowanie na facial ID postaci i tożsamość/model mecha, z wariantami
  technicznymi i zakresem DLC. Nie dopasowywać po imieniu ani prefiksie `dic_pilot_*`.
- Wstawić właściwy zaakceptowany tekst PL przy pierwszym wystąpieniu. Zachować
  jawne braki PL/powiązania, jeśli dany fragment nie jest jeszcze przetłumaczony.
- Dodać regresje wariantów wpisów, zakresów DLC, konfliktów i powtarzających się
  tożsamości. Sprawdzić NPC/dialogue-only, nie tylko pilotów z presetów.

**Zamknięcie:** rzeczywiste źródłowe powiązania z pochodzeniem danych oraz opis
przy pierwszej misji danej tożsamości w uzgodnionym porządku czytanki.

### B. 91 nierozwiązanych PPtr presetów

**Ustalone:** 91 odnośników; rozkład według kolekcji: D1 16, D2 20, D3 28,
Bn 14, B3 9, Er 2, Sz 2. Brak problemów tej kategorii w podstawowej `MissionData`.
Dokładnych celów CAB/PathID nie znaleziono w zrzutach audytu; nie znaleziono też
samych PathID w innych CAB-ach. Taki alternatywny PathID i tak nie byłby dowodem
powiązania. Sprawdzono również wspólne ID misji + dokładny `script_file` w innych
kolekcjach: brak rozwiązanego presetu zastępczego dla tych odnośników.

**Do wykonania:** wyjaśnić źródłowe powiązania, zakres pakietu/rewizji i ewentualne
nadpisania na podstawie istniejących danych. Zachować CAB, PathID, właściciela,
kompozycję i pochodzenie. Nie zastępować presetu po podobnej nazwie, numerze misji
czy samym PathID. Nie nazywać tego brakiem mówców cytatów bitewnych.

**Zamknięcie:** dokładny cel każdego rzeczywiście potrzebnego odnośnika lub
udowodnione źródłowo wyłączenie/alias/nadpisanie. Obecnie przyczyna jest otwarta.

### C. Chronologia scen i wywołań zdarzeń

**Ustalone:** wszystkie 4652 fizyczne warianty Lua w odtworzonych sześciu archiwach
mają statycznie poprawny rejestr `t_tbl`. Kontrola 964 renderowalnych plików dotyczy
literałów i kontekstu, nie wykonania gry. `composition.script_file` wskazuje na
`Unity.VisualScripting.ScriptGraphAsset` (`Unity.VisualScripting.Flow`), nie kolejny Lua.

Z 589 odnośników składników: 368 ma dokładny wpis katalogu typu ScriptGraphAsset;
218 bez wpisu katalogu ma `serifuOnly=1`; 3 nie mają ani wpisu, ani tej flagi.
Te trzy to końcowy składnik czteroczęściowej misji anniversary i dwa wpisy podstawki.
Nie udowodniono ich nieaktywności. Nie nazywać wszystkich 221 brakującymi grafami
bitewnymi. W zrzutach audytu brak odpowiadających im źródłowych obiektów grafów.

**Do wykonania:**
- Zbadać właściwe grafy i wywołania sdemo/dlgev: ID zdarzeń, przeplatanie scen,
  warunki, alternatywy i ewentualne powtórzenia. Nie wyprowadzać tego z `execNo`,
  numeru tabeli, nazwy pliku ani kolejności wpisów rejestru.
- Sprawdzić porządek misji; obecne sortowanie rozdział/kolekcja/ID jest porządkiem
  edycji, nie potwierdzoną chronologią. `source_index` zachowuje miejsce w tablicy
  źródłowej, ale samo w sobie także nie dowodzi chronologii gry.
- Uzgodnić reprezentację alternatywnych zdarzeń/ścieżek bez udawania jednej liniowej
  rozgrywki. Powiązać porządek z kontrolowanym źródłem i dodać testy regresyjne.

**Zamknięcie:** źródłowo potwierdzone wywołania/warunki oraz porządek edycji.
Obecny receipt uczciwie ma `literal_order_verified=true`,
`conditional_event_order_verified=false`, `mission_chronology_verified=false`.

### D. Pozostałe ograniczenia przed pełnym wydaniem

- 116 różnych PID postaci dialogów jest nierozwiązanych — badać dokładne definicje,
  nie imiona. 679 to liczba unikalnych już powiązanych tożsamości dialogów.
  662 tożsamości występują poza pilotami presetów w co najmniej jednej misji;
  **nie jest to liczba unikalnych NPC**.
- 4609 wierszy scen bez źródła JP pozostaje wykazanych w receipt, bez tłumaczenia
  z EN. Nie ukrywać ich przez oznaczenie wydania jako pełnego.
- Odtworzone S6: 120665 wierszy scen, 144 tabele / 44344 wiersze tabel. Historyczny
  pakiet miał 143 tabele / 44340 wierszy; nie zakładać identyczności v7/v8.
- Zweryfikować rzeczywiste zaakceptowane zwrotki PL, kompletną przebudowę i zgodność
  hashy planów czytanek z planami patcha. Nie deklarować integracji z instalacją
  gry ani runtime bez dowodów. Testy syntetyczne nie zastępują tych etapów.

## Ważna poprawka ekstraktora — nie cofać

`s6_scenario.resolve_variants` kopiował tabelę/PID/gałąź siostry, choć dowód
identycznego tekstu EN uzasadniał tylko dopasowanie JP. Poprawiono: kontekst jest
rodzimy dla pliku docelowego; kontekst JP siostry trafia do `jp_sibling_context`.
Regeneracja nie zmieniła żadnego JP/EN, ale zmieniła 4610 numerów tabel: 4609
wcześniej pozbawionych kontekstu wierszy EN-only i jeden błędny numer ze siostry.
Dobór wersji Lua uwzględnia teraz tekst **oraz** tabelę/PID/gałąź, a dopiero potem
preferencję JP. Stare indeksy bez tych pól nie zapewniają nowej kontroli.

**Nigdy nie przepisywać pieczęci starego manifestu na nowy hash.** Po regeneracji
źródła odtworzyć manifest/pakiet i ponownie zweryfikować zwrotki. Nie uruchamiać
prywatnych skryptów historycznych tylko dlatego, że istnieją w `local/`.

## Pliki lokalne i narzędzia do wznowienia

Wszystkie ścieżki poniżej względem repo, chyba że wskazano inaczej.

- `srw-y-translation/docs/READING_Y.md`: szczegóły, intake, Drive ID/hash wejść,
  historia badań i ograniczenia. `docs/EXPERIMENT_LOG.md`: wyniki checkpointów.
- `srw-y-translation/local/reading-research/context-index.json`: najnowszy indeks
  z trybem misji, surowymi PPtr oraz PID/gałęzią jednostek Lua.
- `.../prerequisite-mode-audit.json`: najnowszy audyt katalogów i trybów misji.
- `.../s6/{scenario,tables}.jsonl`: odtworzony korpus po poprawce kontekstu.
- `.../diagnostic-story-participants-final/`: ostatni diagnostyczny build bez PL,
  receipt i ZIP. **Nie wydawać go jako polskiej czytanki.**
- `.../{complete-objects,base-text-objects,extra-objects}.json`: starsze prywatne
  zrzuty źródeł do audytu obecności; nie mają wszystkich nowszych metadanych Lua.
- `.../{SRW_Y_MISSION,SRW_Y_GLOSY,srw_y_text,srw_y_tekst,srw_y_dlc_bundle,
  srw_y_free_patch}`: sześć odtworzonych katalogów wejściowych ostatniego indeksu.
- `.../srw_y_dlc_catalog/`: dziesięć katalogów DLC. Bazowy katalog:
  `google_drive/catalog.json`. Oryginalne ZIP-y także w ignorowanym `google_drive/`.
- `.../restore_s6.py`: prywatny skrypt odtworzenia; zapisuje ponownie lokalne S6.
  Najpierw sprawdzić ścieżki i hashe, zachować istotne stare snapshoty.
- Interpreter: `.venv/bin/python` (UnityPy, pycryptodome, pytest, Pillow).

Przykładowe odtworzenie indeksu (uruchamiać z katalogu repo):

```sh
r=srw-y-translation/local/reading-research
.venv/bin/python srw-y-translation/tools/reading_index.py \
  --bundles "$r/SRW_Y_MISSION" "$r/SRW_Y_GLOSY" \
    "$r/srw_y_text" "$r/srw_y_tekst" "$r/srw_y_dlc_bundle" "$r/srw_y_free_patch" \
  --out "$r/context-index-next.json"
```

Audyt ma CLI w `tools/reading_audit.py`; przykład użycia w `READING_Y.md`.
Nowy build kierować do **nowego katalogu**, nigdy nad istniejącą czytankę.

## Testy do ponownego uruchomienia po zmianach kodu

```sh
.venv/bin/python -m pytest -q \
  srw-y-translation/tests/test_reading_y.py \
  srw-y-translation/tests/test_reading_events.py \
  srw-y-translation/tests/test_scenario_context.py \
  srw-y-translation/tests/test_reading_audit.py \
  srw-y-translation/tests/test_pl_import.py \
  srw-y-translation/tests/test_pl_import_oe_regressions.py \
  srw-y-translation/tests/test_translator_package.py \
  srw-y-translation/tests/test_pl_patch.py
```

Ostatni wynik: **169 passed, 1 skipped, 57 subtests passed**.
Workflow `.github/workflows/srw-y-import.yml` obejmuje te regresje.
Pełny historyczny zestaw Y miał też testy wymagające innych prywatnych wejść;
nie opisywać powyższego wyniku jako zaliczenia wszystkich testów projektu.

## Pierwszy krok następnego agenta

Sprawdzić stan gałęzi/PR i dostępność powyższych lokalnych danych. Następnie
kontynuować **źródłowe** badanie A–C. Nie regenerować po raz kolejny tych samych
statystyk i nie tworzyć kolejnego audytu zamiast brakującego dowodu powiązań.
Jeśli potrzebna zawartość nadal nie jest dostępna, jasno wskazać ten konkretny
brak dowodowy — nie udawać zamknięcia zadania i nie stawiać diagnozy, że właściciel
nie dostarczył kompletnych presetów. Bez dowodu nie dołączać encyklopedii po nazwie
ani nie ogłaszać chronologii na podstawie kolejności literałów.
