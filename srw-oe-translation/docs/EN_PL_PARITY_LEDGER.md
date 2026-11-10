# EN↔PL parity — etapy portu poprawek PL do EN (ledger)

Utworzony 2026-11-10 na polecenie właściciela: **angielski patcher ma
dostarczać grę na tym samym poziomie tłumaczenia co polski (warstwa
techniczna)**. Każda nowa wersja patchera polskiego = jeden etap. Kolejność:
chronologicznie od najstarszej wersji. Poprawki czysto językowe (gramatyka
PL) nie są portowane.

EN bazuje na **`5aefd043` (2026-10-16, import EN)** + dołączone później
commity EN na PR #33 (y `cb3cbed` – zapora w generatorze opisów, `dffa764` +
`a290eff` + `c7a6c09` – #31/#30). Wszystkie poprawki PL po 2026-10-16 domyślnie
**nie są w EN** i zostały tu sprawdzone etap po etapie.

## Metoda i reguły

1. **Reguła długości (decyzja właściciela 2026-11-10):** poprawka EN =
   skrócenie tekstu do długości maksymalnej, jaką ostatecznie uzyskała PL w
   danym slocie/typie danych (PL była sprawdzona w grze; alfabet łaciński ten
   sam). Jeśli sensownego angielskiego nie da się zmieścić obok tej granicy,
   stosujemy najkrótsze EN **nieprzekraczające pojemności JP (komórki gry)**,
   a każde takie odstępstwo jest tu jawnie wypisane. Nigdy nie przekraczamy
   pojemności JP.
2. **Niezmienniki:** ta sama liczba linii, te same tokeny sterujące (`＠n`,
   `%s`, `\x0f*…\x0f…`, pełnoszerokie `％`), tekst CP932-enkodowalny, zero
   NUL. Wymuszane fail-closed przez `tools/en_ui_corrections.py`.
3. **Zakres:** poprawki techniczne (długość/układ/slot, braki w danych,
   uszkodzone wiązania, bramki buildera, tekstury UI). Poprawki czysto
   językowe PL (fabuła, dialogi) — poza zakresem.
4. **`bytes`** w wierszach pakietu to długość JP w bajtach — zostaje
   nietknięta.
5. **Weryfikacja po każdym etapie:** `python3 tools/translation_check.py
   --package pakiet_EN --field en --strict` (0 błędów), `python3
   tools/label_fit.py --package pakiet_EN --check`, oraz zestawienie
   komórek EN vs limit z planu (wypis wyjątków w tym ledgerze).
6. **Brak testu PPSSPP** — `runtime_tested` wszędzie `false`.

## Decyzje właściciela / wyłączenia

- **Boot title card** — zostaje (właściciel, 2026-11-10: jeśli w PL też
  zostały). Dotyczy #30 (logodata GIM, poza wierszami tekstu).
- **`story-language-*` (dialogi/fabuła, v4.3/v4.4)** — nie portowane:
  poprawki gramatyczne PL, nie techniczne. Limit linii dialogu to
  odpowiedzialność buildera, nie treść pakietu; EN wypuszczone i grywalne.
- **Panel danych jednostki (`Weight －－－` → `Masa －－－`)** — poprawka PL była
  językowa (kolumna angielska obok polskiego panelu); EN jest jednorodnie
  angielskie, więc klasy błędu w EN **nie ma**. Skrócenie EN `Weight` →
  `Wt.` oznaczające 9 znaków byłoby kosmetyką bez dowodu na przesyt
  (EN-panel wypuszczony i grywalny). **Otwarte pytanie do właściciela**
  (sekcja na końcu).
- **6 komunikatów dialogowych czcionki systemowej PSP** (39944/39967/40006/
  40068/44704 + warianty) — pozostają w tym samym angielskim brzmieniu
  (mandat właściciela z v4.5/v4.9 dla PL; EN i tak je ma).
- **`43894`/`44010`** (osierocone `の`) — EN zostawia `of` (tak jak PL
  zostawił `of`).
- **103 puste wiersze `config_dlc_id`** — bez zmian (nazwy własne/ID DLC).
- **`sysmes:29165`** — JP i EN wewnętrznie niespójne; PL bez rozstrzygnięcia
  też nie ruszył; czeka na właściciela.
- **Śmieciowe jednokanji wiersze** (`牾`,`珱`…) — artefakt ekstrakcji, PL też
  zostawia; właściciel ma zdecydować, czy czyścić.

## Tabela etapów (kolejność PL)

| # | Etap PL (data) | Zakres techniczny | Weryfikacja EN | Status |
|---|---|---|---|---|
| 1 | PL3 (2026-10-19) | fizyczna pula Skill00 (dzielenie, marginy), 8 pul DLC | narzędzia dzielenia są w builderze (współdzielone EN/PL) | ZIELONY |
| 2 | v2.6 / v3.0-era 2026-10-19 | ui-qa, ui-third, ui-followup, ui-mech-viewer, ui-qa-executable | `translation_check --strict` 0 błędów; `label_fit --check` rows 0; plan `config/en/v26-ui-2026-10-19-en-port*.json` | NASTAWIONY (commit 040878e) |
| 3 | v2.6/v2.7-PL4 (2026-10-20) | ui-six, ui-seven, ui-robot-type-captions, ui-zaku-*, mission titles inventario | `v270-ui-2026-10-20-en-port.json` 30/30 w pakiecie (już było); 40 `leftover:` wierszy RoboDictionary = co do litery z `source_en`; 10/10 `mission_note …title` niepuste; `translation_check --strict` 0 błędów | ZIELONY (weryfikacja 2026-11-10) |
| 4 | v2.7-PL5/PL6 + v3.0 (2026-10-21) | ui-clipboard, ui-eldran-skills, ui-five-screens | `translation_check --strict` 0 błędów; `label_fit --check` bez zmian (15 legacy); plany `config/en/*-2026-10-21-en-port.json` | ZIELONY (commits 2e65ce7, 40c301b, 3558074) |
| 5 | v4.0 (2026-10-23) | brak zmian wierszowych (wydanie) | — | ZIELONY |
| 6 | v4.1 (2026-10-23) | etykiety Pilot/Owned (10/7 komórek), Kallen vs Karen, intsys_04 | EN już zgodny (patrz) | ZIELONY |
| 7 | v4.2 (2026-10-24, para) | geometria TXCL wszystkich podpisów UI (PL+EN) | współdzielone specs `ui_labels/*.json` | ZIELONY |
| 8 | v4.3 (2026-10-24) | język fabuły ep. 00–34 | pominięte (językowe) | POMINIĘTE |
| 9 | v4.4 (2026-10-24) | język fabuły extra/simulator | pominięte (językowe) | POMINIĘTE |
| 10 | v4.5 (2026-10-24) | tytuły misji ≤32 komórki (24 menu + 24 notki) | **EN: ZIELONY (odnowienie, 2026-11-10)** — właściciel wybrał opcję (a): 57 tytułów `title` skrócone do ≤32c/linię (527/527 wierszy title OK); `english-reference` (25 epizodów) i baseline zaksięgowane; `validate_source_bindings` akceptuje port przez zaksięgowany audyt `undo_en_mission_title_port`; `reference_sha256` w 25 `polish/episode_*.json` re-pinowany; CI zielone | ZIELONY (2026-11-10) |
| 11 | v4.6 (2026-10-26) | proza nie-dialogowa: panel masy (język., brak), sysmes (węższe linie), 43897/44013 (treść EN błędna!) | **EN: 4 wiersze** — 43894/43897/44010/44013 poprawiona treść („Download the full version.”); 39944/39967/40006 BEZ zmian (bajt-w-bajt mandat, `test_pl_nondialogue`); robonote 348 wierszy NIE portować | ZIELONY (e6beef4 + revert rewrap 2026-11-10) |
| 12 | v4.7 (2026-10-29) | podpisy pilotów robot-viewer (63 wiersze) | EN ma komplet | ZIELONY |
| 13 | v4.8 (2026-10-29) | bramki czcionki systemowej PSP (ASCII) | EN = angielski ASCII, bramka w builderze (wspólna) | ZIELONY |
| 14 | v4.9 (2026-10-29) | przywrócenie dokładnych angielskich komunikatów PSP | EN = te same wiersze | ZIELONY |
| 15 | v4.10 (2026-10-29) | Gai podpis exe (`Pilot: Gai`) | EN ma `Pilot: Gai` | ZIELONY |
| 16 | v4.11 (2026-11-02) | Alana/listy: długie pełne nazwy, znaczniki (Ally), etykieta aktora exe (14 B) | EN zgodny (patrz) | ZIELONY |

## Stan weryfikacji „zielonych” etapów (2026-11-10)

- **v4.7 podpisy pilotów:** wszystkie 63 wiersze z
  `config/pl/ui-robot-pilot-captions-2026-10-29.json` istnieją i mają w EN
  identyczną treść (np. `Pilot: Keroro` … `Pilot: Naomi`).
- **v4.8/v4.9:** komunikaty PSP w EN są po angielsku w brzmieniu z v4.5
  (mandat właściciela dotyczy PL-kitu; EN i tak je ma).
- **v4.10:** `exe:PBOOT.PBP/DATA.PSP:0x08bf4848` = `Pilot: Gai` (14 B ≤ 15).
- **v4.11:** `exe …0x08bf43a0` = `CV:Koji Totani` (14 B = slot);
  35/35 wierszy `charalist-ally-marker` w EN ≤ `max_cells`;
  oba wiersze z `charalist-long-full-names` są w EN kompletne
  (`Rudolph Gerhardt Zeppelin III` 38 B ≤ 43, `Karl Lichten Schubaltz (Ally)`).
- **v4.1:** `sysmes …21488` = `Main Pilot` (10 = limit), `21500` = `Sub Pilot`
  (9 ≤ 10), `31988` = `Owned` (5 ≤ 7) i `46264` = `＠4Owned` (7 = limit) —
  zweryfikowane 2026-11-10, pasują do slotów; zmiany PL były czysto
  językowe (`Główny pilot` → `Pilot gł.`), EN bez zmian;
  podział `char:2320` (Kallen) vs `1409` (Karen) obecny w EN ze wskazaniem
  `copy_of` na właściwe cele.
- **v4.0:** wydanie bez zmian wierszowych.
- **v3.0/PL3 (pula Skill00):** limity rozmiaru członów są pilnowane przez
  wspólny builder (`SKILL_TOTAL_LIMIT`, margins); dotyczą EN z definicji.
- **v4.2:** geometria intsys/mensys w `ui_labels/*.json` wspólna.

## Wyjątki długościowe EN (EN > PL-final, ≤ JP) — do akceptacji właściciela

| Wiersz | EN (po portzie) | Komórki EN | Limit PL | Limit JP | Uwagi |
|---|---|---|---|---|---|
| sysmes:…27276 | `Missions:` | 9 | 6 | 12 | Panel statystyk profilu gracza; pojemność JP = 12; jednowyrazowy skrót niemożliwy |
| exe …0x08bf7198 | `Ally` | 4 | 3 | 4 | Emblemat sprzymierzenia w kolejce jednostek; `Sw.` = slang PL, nie angielski |
| exe …0x08bf6b0c | `End layout change?` | 18 | 17 | 24 | EN mieści się w pojemności JP (24); PL-final 17 komórek |

## Etap 4 (2026-10-21 PL → EN) — szczegóły portu (2026-11-10)

Plany: `config/en/clipboard-2026-10-21-en-port.json` (4 zmiany),
`config/en/eldran-2026-10-21-en-port.json` (11),
`config/en/v300-ui-2026-10-21-en-port.json` (96). Zastosowane narzędziem
`tools/en_ui_corrections.py` (binding: file+id+exact `before`; fail-closed
na tokeny/linie/CP932/`max_cells`; zapis atomowy; wiersze o tym samym `id`
z innym `en` nietknięte). Commity: 2e65ce7 (clipboard), 40c301b (eldran),
3558074 (five-screens).

### Co portowaliśmy (tylko techniczne)

- **clipboard** — brak spacji przed tokenem `%` w 4 wierszach (`sysmes`
  11644/11647/11672/11675: `Damage＠230％…` → `Damage ＠230％…`,
  analogicznie `Evade bonus`). EN-19c ≤ PL-final (20/27c).
- **Eldran** — `Eldoran` → `Eldran` w 11 wierszach (`03_skills`
  r219:effect, lustro `04_config_text` 36904, tail-pool `193328` + DLC
  `config01–08` 11210/11230), zgodnie z resztą EN.
- **five-screens** — Bind linie skrócone (46–47 → 32/33c ≤ PL-final
  36–37c); trait tagi z odstępem przed tokenem (`<Bind%s1>` → `<Bind %s1>`,
  jak PL); Coord. Atk / Stun / Detonate trimowane ku szerokości PL-final;
  Slow linie: `, foe Eva-` → `, Eva-` (30/31c = pojemność JP, ≤ PL-final
  33/34c); sysmes help-bar / status-banner wiersze skrócone lub
  przezawinięte do slotów JP (16176/17096/20968/21132/22676/22832/23000/
  23520/24016/38568/38684/38744/41808/42024/42244/42288);
  `exe 0x08bf828c…82d8` skrócone do zweryfikowanych slotów pixelowych
  (`A/H`, `Sur.`, `Link Atk`, `Full`, `Pin`, `Lone`); `sysmes 10096`
  (Captured-banner) przepisany kompaktowo — `＠4Captured:  ＠0A/H/E＠1%+3d%%
  ＠0CritT＠1%+3d%%＠0` (22c = PL-final, ≤ JP 24c; skróty à la PL `A/C/U`,
  `O.kr.`); `sysmes 50984` `Action Cmds` (11c) → `Actions` (7c — patrz korekta
  właściciela 2026-11-10 poniżej); lustra `04_config_text` dla trait-linii (31 luster, match po
  exact `en`).

**Wynik audytu planu v300 po portzie:** dokładnie **1** wiersz powyżej
PL-final-u (50984; dodany do tabeli wyjątków, **domknięty 2026-11-10**:
`Actions` → `Acts`). Wszystkie pozostałe edycje
mieszczą się w PL-final albo w JP (np. Slow = 30/31c = JP, zrozumiany
wyjątek: nazwa "Eva" zamiast pełnego "foe Eva").

### Czego NIE portowaliśmy (i czemu)

- **spirit tail-pool fragment reorder** (clipboard, `HP` → ` Odnawia `) —
  szyk zdania PL, nie techniczny; EN składa te linie poprawnie as-is.
- **46 wierszy map-terrain** (clipboard) — PL przywracało znaki
  diakrytyczne; EN nazwy terenu = ASCII, max 12c, już mieści się w slocie.
- **wiersz spirit `14364`** — szyk PL; EN nietknięty.
- **spacing kosmetyczny `%s NN%%`** z PL — nie portować (powiększałby
  szerokość bez zysku technicznego; tokeny bez zmian).
- **wyjątki > JP z pierwszej iteracji** (Slow `foe Eva-` 34/35c = JP+4c;
  `10096` `Captured:` 32c = JP+8c; `0x08bf82b4` `All SR` 6c > PL-final
  5c) — **przeplanowane do wersji ≤ JP / ≤ PL-final**, zanim plan wszedł do
  pakietu. Reguła "nigdy ponad JP" utrzymana.

### Do właściciela — ZAMKNIĘTE 2026-11-10

1. ~~**`Eldoran` ×4 w `00_dialogue.jsonl`**~~ — właściciel: „Eldran powinno
   być nie Eldoran.” Poprawione (plan `config/en/eldran-dialogue-2026-11-10.json`):
   `Eldoran` → `Eldran` w 4 wierszach dialogu (DL518_12, ep. 18), spójnie
   z PL i z portem umiejętności; EN reference (ep. 18) zaksięgowany
   1:1 z pakietem.
2. ~~**`sysmes:…50984 Actions`**~~ — właściciel: „zrób tak, żeby było dobrze.
   Czyli działało bez crasha i było przetłumaczone. Jeśli skracaliśmy PL bo
   się nie mieściło to musisz też skrócić EN.” Skrócone do **`Acts`**
   (4c ≤ PL-final 5c ≤ JP 12c); `config/label_fit_rules.tsv` (wiersz
   `行動コマンド`) i `pakiet_EN/04_config_text.jsonl` spójne; plan
   `config/en/sysmes-50984-2026-11-10.json`.

## Etap 3 (2026-10-20 PL → EN) — weryfikacja (2026-11-10)

Zamknięcie audytem zamiast portu — pakiet EN już zawiera wszystkie zmiany
techniczne z PL4. Dowody:

- **ui-six / ui-seven** — plan `config/en/v270-ui-2026-10-20-en-port.json`
  (30 edycji, etap2-label w polu `stage` — artefakt historyczny, opis zgodny):
  porównanie (file,id,before→after) z pakietem wykazało **30/30 wierszy
  już zaszytych** w `pakiet_EN` (spirit 1522/… `Bullseye→Focus`,
  `Tailwind→Wind`, sloty difficulty/jednostki, `Unit Stats→Stats`,
  full-recovery ≤34c). Ponowny `--dry-run` zgłasza „stale" — oczekiwane,
  plan jest rekordem, nie do ponownego apply.
- **ui-robot-type-captions / ui-zaku-*** — 40 rekordów `operation: add`
  (`leftover:config0x|imenu0x …RoboDictionary*.bin`): wszystkie 40 obecne w
  `pakiet_EN/04_config_text.jsonl`, treść EN **identyczna** z `source_en`
  z planów (0 mismatchy).
- **ui-mission-titles-2026-10-20** — 10 brakujących base-title slotów:
  wszystkie 10 niepuste w `pakiet_EN/05_mission_text.jsonl` (dosypale z
  backfillu `config/en/mission-note-backfill-2026-11-10.json`, a290eff).
- **mission-title-inventory-2026-10-20** — wyłącznie audyt hashów/liczników
  po stronie PL; bez akcji EN.
- `translation_check --strict` po etapie 4: 0 błędów.

## Etap 10 (v4.5) — szczegóły EN (2026-11-10)

**Wykonane (a) — odnowienie reference + baseline, 2026-11-10.** Właściciel
zdecydował: „Oczywiście trzeba odnowić czyli (a).” (2026-11-10).

- **Skrócone tytuły:** 57 wierszy `title` w `pakiet_EN/05_mission_text.jsonl`
  (plan `config/en/mission-titles-2026-10-24-en-port.json`, przywrócony z c0b1850):
  prefiks `Episode→Ep.` gdzie pomaga, sens zachowany; identyczne edycje
  `mission_note …:title` (*_ext.dat kopie) jak w menu. Każda linia każdego
  z 527 wierszy `title` ma ≤32 komórki (`C.TOKEN_RE` + CP932 długość).
- **`english-reference` odnowiony:** 25 plików (epizody
  01,02,03,04,07,09,10,11,12,13,15,16,18,19,20,21,22,23,25,26,27,29,30,31,33) —
  każdy string z planu skrótów zastąpiony tym samym before→after w nagłówkach
  (`## `), poza body; 0 wystąpień przed-krótkich ciągów poza nagłówkami
  (zweryfikowano). `references.json` przeliczony bajt-w-bajt (35/35
  bytes+sha256 OK), `date` → 2026-11-10, provenance dopisana; README
  (sekcja provenance) opisuje odnowienie.
- **Plan-piny re-pinowane:** `reference_sha256` w 25
  `docs/reading-script/polish/episode_NN.json` (chirurgiczna zamiana hasha,
  diff 2-liniowy; pozostałe 10 epizodów nietkniętych).
- **Audyt source-bindings rozszerzony audytowo:** nowa funkcja
  `undo_en_mission_title_port` w `tools/polish_reading_script.py` (wzorzec jak
  `undo_en_backfill`): odtwarza dokładnie 57 zaksięgowanych zmian (wymaga
  `en == after` w zaksięgowanym wierszu; odtworzony plik musi bajt-w-bajt
  przejść przez `undo_en_backfill` do baseline'u `aaa121d3…`).
  `tests/test_reading_script_episode34.py` zaktualizowany analogicznie
  (frozen finale baseline akceptuje oba audytowane kroki). Do dotychczasowych
  pinów `english_source_sha256` nic nie zmieniono — baseline `aaa121d3…`
  pozostaje.
- **Przywrócenie po revercie:** e79dc85 wycofał transakcję c0b1850 po zapadnięciu CI; 2026-11-10 owner zlecił (a) i port został zastosowany ponownie
  w pełnej synchronizacji reference + baseline. `test_pl_ui_six` 12/12,
  `test_reading_archive_carry` 8/8, `test_polish_reading` 17/17,
  `test_polish_reading_zero` 6/6, `test_reading_script_episode34` 20/20,
  `test_pl_reading_series` OK, `test_pl_nondialogue` OK.
- **Nie ruszamy:** mandat PSP (39944/39967/40006) — jak mandatował właściciel.

**Pozostaje do właściciela:** nic. `Eldoran` → `Eldran` (dialogi) i
`50984` `Actions` → `Acts` domknięte 2026-11-10 (patrz „Korekty właściciela”
poniżej).

## Etap 11 (v4.6) — szczegóły EN (2026-11-10)

- **43894/43897/44010/44013** — EN twierdziło: `Super Robot Wars Operation
  Extend.` (nazwa gry), JP: `製品版をダウンロードします。` („pobierze wersję
  pełną”). Błąd treściowy zgłoszony w scope etapu → poprawione na
  `Download the full version.` (26c ≤ JP 28c). Wędrujące `of` w 43894/44010
  zachowane (ledger: jak PL).
- **39944/39967/40006** — mandat właściciela: ta sama angielska fraza
  (PSP system font), bajt-w-bajt także w przewijaniu linii — widać to w
  `test_pl_nondialogue.test_reviewed_system_dialogs_remain_english`
  (assert `row['en'] == <oryginał>`). Pierwsza iteracja (przezawinięcie do
  ≤35c) złamała ten test i **została wycofana 2026-11-10**. EN zostaje
  z 44c przy JP 38/36c — tak jest w wydaniu i **to jest stan mandatowany**.
- **40068/44704** — 24c = slot. Bez zmian.
- **348 robonote weight/length** — PL tłumaczyło EN→PL („Weight 32,000t" →
  „Masa 32 000 t”); EN zostaje angielskie. Sprawdzone: 343/348 wierszy to
  niezmieniony EN; 5 wierszy (np. `robonote:2200:length` `Len. 14.53m (15.59m
  incl. head lasers)`) różni się od `before` w planie PL formatowaniem liczb
  (kropka vs przecinek) — bez wpływu na EN-pakiet.

## Korekty właściciela (2026-11-10) — dialogi Eldran + sysmes 50984

Właściciel rozstrzygnął dwa otwarte punkty z sekcji „Do właściciela":

1. **`Eldoran` ×4 w `00_dialogue.jsonl`** — dialogi (DL518_12, epizod 18,
   strażnik planety): „Eldran powinno być nie Eldoran.” Zastosowane
   `Eldoran` → `Eldran` w 4 wierszach dialogu
   (`config/en/eldran-dialogue-2026-11-10.json`), dokładnie jak w PL
   (`Eldran`) i jak w porcie umiejętności v2.7-PL6. Spójnie:
   `docs/reading-script/english-reference/srwoe_episode_18.md` (4 wystąpienia),
   `references.json` (bytes+sha256, provenance), `reference_sha256`
   w `polish/episode_18.json`, oraz nowy audyt
   `tools/polish_reading_script.py: undo_en_eldran_dialogue`
   (validate_source_bindings akceptuje odnowiony `00_dialogue.jsonl`
   wyłącznie gdy odwraca się do zaksięgowanego baseline'u bajt-w-bajt);
   `tests/test_reading_script_episode34.py` analogicznie (zamrożony finale:
   legalny jest tylko wynik odwracania zaksięgowanych promocji). Piny
   `english_source_sha256` i `episode_34_sources.json` nietknięte.
2. **`sysmes:…50984 Actions`** — „zrób tak, żeby było dobrze. Czyli działało
   bez crasha i było przetłumaczone. Jeśli skracaliśmy PL bo się nie mieściło
   to musisz też skrócić EN.” PL zostało skrócone do `Akcje` (5c) w v4.5
   (przycisk „Komendy akcji” wchodził na zderzak ekranu). EN
   `Actions` (7c) → **`Acts`** (4c ≤ PL-final 5c ≤ JP 12c) — wiersz
   `行動コマンド	Acts` w `config/label_fit_rules.tsv` i
   `pakiet_EN/04_config_text.jsonl` spójne
   (`config/en/sysmes-50984-2026-11-10.json`). `mode=grow` (pula stringów,
   realokacja wskaźników przy runtime) — krótszy string nie może zawiesić
   odczytu; zmiana dotyka tylko układu paska. `test_label_fit` 22/22 OK.

## Publikacja wydania EN+PL — awaria przebiegu 448 i poprawka (2026-11-10)

Port parity z etapów 1–16 **był już w pakiecie EN** i workflow zbudował oba
kity poprawnie, ale wydanie **nie powstało**: przebieg 448
(`76f8471d`, scalenie PR #33) skończył się `building: success`,
`publish: failure`.

**Przyczyna (potwierdzona, nie hipoteza).** W jobie `publish` krok
`Checkout (release notes live in the repository)` stał **po** kroku
`Download the verified pair`. `actions/checkout@v4` domyślnie wykonuje
`git clean -ffdx && git reset --hard HEAD` w `$GITHUB_WORKSPACE`
(wejście `clean`, domyślnie `true`), więc pobrany chwilę wcześniej katalog
`release/` był kasowany, a `test -f "$EN"` przerywał krok komunikatem
`Process completed with exit code 1` (adnotacja wskazała linię 38 kroku —
`set -euo pipefail` w skrypcie publikacji). Artefakt przebiegu
`patchers-en-pl-448-76f8471d` był kompletny; brakowało wyłącznie publikacji.

**Poprawka.** `release.yml`: najpierw checkout (opis wydania z repozytorium),
potem pobranie zweryfikowanej pary; w miejscu zmiany komentarz z powodem
i numerem przebiegu, żeby kolejność nie została „uporządkowana” z powrotem.
`tests/test_release_pair.py` dostał dwa strażniki: kolejność
checkout → download-artifact w jobie `publish` (sprawdzone, że na starym
układzie test **pada**) oraz istnienie pliku opisu dopisywanego przez
workflow (`docs/release-notes/2026-11-en-additions.md`).

**Stan wydania.** Ostatnie opublikowane wydanie EN+PL to
`patch-build-432-127b7cb9` (z 2026-11-09). Wydanie z przebiegu 448 nie
istnieje; po scaleniu tej poprawki workflow na `main` zbuduje i opublikuje
parę ponownie. Do tego czasu GitHub Releases **nie** zawiera EN z opisami
z tego PR-a — nie twierdzić inaczej w odpowiedziach dla graczy.

**Czego to nie zmienia.** Poprawki tekstu EN są w `pakiet_EN` od scalenia
#33; sprawdzone lokalnie: 4 wiersze „Download the full version.”, `Acts`
w `sysmes:…50984`, `Eldran` w 4 dialogach, 57 tytułów misji ≤ 32 komórek.
To błąd dostarczania, nie treści — i dlatego naprawiony w workflow, a nie
przez ręczne wrzucanie plików na wydanie.
