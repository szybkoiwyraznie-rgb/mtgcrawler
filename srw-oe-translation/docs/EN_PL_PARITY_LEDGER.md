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
| 10 | v4.5 (2026-10-24) | tytuły misji ≤32 komórki (24 menu + 24 notki) | **EN: ZABLOKOWANE / do decyzji właściciela** — CI/reading-script: tytuły EN są wiązane z angielskim reference i baseline'em `episode_*.json` (`validate_source_bindings`, fail-closed; także tożsamość tytułu z reference w `validate_plan`). Audyt znalazł 50 menu `mission_title` > 32c; gotowa łatka 57 wierszy w historii gita (commit c0b1850, wycofany). Potrzebny przegląd reference albo decyzja: skrócić EN tytuły | ZABLOKOWANE (revert 2026-11-10) |
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
| sysmes:…50984 | `Actions` | 7 | 5 | 12 | Przycisk komend akcji; jednowyrazowy skrót niemożliwy; PL-final 5 ('Akcje') |

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
  `O.kr.`); `sysmes 50984` `Action Cmds` (11c) → `Actions` (7c — wyjątek,
  ≤ JP 12c); lustra `04_config_text` dla trait-linii (31 luster, match po
  exact `en`).

**Wynik audytu planu v300 po portzie:** dokładnie **1** wiersz powyżej
PL-final-u (50984; dodany do tabeli wyjątków). Wszystkie pozostałe edycje
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

### Do właściciela (otwarte)

1. **`Eldoran` ×4 w `00_dialogue.jsonl`** — dialogi (warstwa językowa);
   wg zasad nie ruszamy. Czy poprawić na `Eldran` także w dialogach?
2. **`sysmes:…50984 Actions`** (7c > PL-final 5c, ≤ JP 12c) — zaakceptować
   jako wyjątek czy skrócić do `Acts`/`Cmds` (4c ≤ PL-final)?

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

**Wycofany.** Pierwszy port (commit c0b1850, 57 wierszy `title` w
`05_mission_text.jsonl` skrócone do ≤32c, plan
`config/en/mission-titles-2026-10-24-en-port.json`) został wycofany po tym,
jak CI `Test tools` (`python -m unittest discover -s tests`) zpadł na
`test_pl_ui_six.BatchTests.test_reading_rebase_accepts_only_exact_en_empty_bound_append`:
`validate_source_bindings` fail-closed wiąże cały `05_mission_text.jsonl`
z baseline'm zapisanym w `docs/reading-script/polish/episode_*.json`
(`english_source_sha256`) i dopuszcza wyłącznie jawnie zaksięgowane
promocje (#30 backfill, 10 promowanych tytułów z
`ui-mission-titles-2026-10-20.json`). Zmiana treści 57 tytułów jest poza
tymi promocjami, więc strażnik słusznie odrzuca plik. Dodatkowo EN tytuły
są wiązane z treścią **angielskiego reference** (`validate_plan`:
`title == reference_blocks[...]`) — skrócone EN tytuły by to zepsuły.

Plik przywrócony do bajtowo-identycznego stanu z commita 2068be7
(test znów przechodzi). Gotowe remedium czeka w historii gita (c0b1850):
pełna lista 57 skrótów + identyczne edycje w 7 wierszach `mission_note …:title`.

**Do właściciela:** czy EN tytuły mają zostać skrócone do slotu 32c
(wtedy konieczny przegląd/odnowienie `english-reference` + baseline w
`episode_*.json`, tak jak zrobił to backfill #30/#31), czy EN zostaje
ze stanu zastosowanego? Decyzja jest poza agendą techniczną — dotyka
łańcucha audytu reading-scriptu.

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
