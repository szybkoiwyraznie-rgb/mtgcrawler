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
| 3 | v2.6/v2.7-PL4 (2026-10-20) | ui-six, ui-seven, ui-robot-type-captions, ui-zaku-*, mission titles inventario | | W TOKU |
| 4 | v2.7-PL5/PL6 + v3.0 (2026-10-21) | ui-clipboard, ui-eldran-skills, ui-five-screens | | W TOKU |
| 5 | v4.0 (2026-10-23) | brak zmian wierszowych (wydanie) | — | ZIELONY |
| 6 | v4.1 (2026-10-23) | etykiety Pilot/Owned (10/7 komórek), Kallen vs Karen, intsys_04 | EN już zgodny (patrz) | ZIELONY |
| 7 | v4.2 (2026-10-24, para) | geometria TXCL wszystkich podpisów UI (PL+EN) | współdzielone specs `ui_labels/*.json` | ZIELONY |
| 8 | v4.3 (2026-10-24) | język fabuły ep. 00–34 | pominięte (językowe) | POMINIĘTE |
| 9 | v4.4 (2026-10-24) | język fabuły extra/simulator | pominięte (językowe) | POMINIĘTE |
| 10 | v4.5 (2026-10-24) | tytuły misji ≤32 komórki (24 menu + 24 notki) | | W TOKU |
| 11 | v4.6 (2026-10-26) | proza nie-dialogowa: panel masy (język., brak), sysmes (węższe linie), 43897/44013 (treść EN błędna!) | | W TOKU |
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
- **v4.1:** `sysmes …21488` = `Main Pilot` (10 = limit), `21500` = `Sub Pilot`,
  `31988`/`46264` — do sprawdzenia pełnej treści (patrz etap 6);
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
