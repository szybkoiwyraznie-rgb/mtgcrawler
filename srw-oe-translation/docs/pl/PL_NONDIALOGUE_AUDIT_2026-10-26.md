# Audyt prozy nie-dialogowej (2026-10-26)

Zakres: teksty polskie, których żaden wcześniejszy przegląd językowy nie objął —
pliki `02_items`, `03_skills`, `04_config_text`, `05_mission_text` oraz część
prozy `07_names_*`/`08_names_*`. Razem **28 431 wierszy PL** (po odsianiu
nazw własnych, serii i aktorów: **17 724 wiersze prozy = 5 846 unikalnych
tekstów**).

Plan zmian: `config/pl/nondialogue-unit-data-sysmes-2026-10-26.json`,
SHA-256 `e2f1e0604c192a450c7da5b7ef050a4abbfced9980a1d383155c210eb339934d`,
**357 wierszy**. Zastosowany przez `tools/pl_ui_corrections.py` (zapis
źródłowo powiązany: plik + niezmienny hash wiersza źródłowego + ID + dokładny
tekst „przed”; odmowa przy nieaktualnym wierszu, zmianie tokenów, zmianie
liczby przejść do nowej linii, znakach sterujących i przekroczeniu limitu
komórek).

Snapshot `polish.jsonl`: `788ab91c…62` → `321d22bd…f8` (18. wpis w
`owner_ui_corrections`), 108 794 wpisy. Walidacja świeżej materializacji:
**108 805 / 109 176** wypełnionych, **371** pustych, **0 błędów**,
4 176 ostrzeżeń — bez zmian względem v4.5.

## Co poprawiono

### 1. Panel danych jednostki — 348 wierszy (`08_names_units_weapons`, `weight`/`length`)

Pole było **w połowie nietłumaczone**: 186 wierszy `weight` i 162 wiersze
`length` trzymały nadal kolumnę **angielską**, choć przetłumaczone wiersze
tego samego pola używają już `Masa 54,0 t` / `Dł. 25,0 m`. Gracz widział więc
w panelu danych mecha mieszankę `Weight 2250 zusshiri` / `Masa 54,0 t`.

Przyjęte konwencje (zgodne z już przyjętymi wierszami tego pola):

| Przed (EN) | Po (PL) | Wiersze |
| --- | --- | --- |
| `Weight －－－` | `Masa －－－` | 166 |
| `Len. －－－` | `Dł. －－－` | 151 |
| `Empty Wt. 8,450kg` | `Masa własna 8,45 t` | 8 |
| `Dry Weight 4.4 rufton` / `8.6 rufton` | `Masa sucha 4,4 rufton` / `8,6 rufton` | 2 |
| `Weight 32,000t` | `Masa 32 000 t` | 1 |
| `Weight 1,021.2t` | `Masa 1 021,2 t` | 1 |
| `Weight 8.103kg` | `Masa 8103 kg` | 1 |
| `Weight 6387kg` / `7639kg` / `8089kg` | `Masa 6387 kg` itd. | 3 |
| `Weight 2250/3077/2040 zusshiri` | `Masa … zusshiri` | 3 |
| `Len. 485/628/462 shin` | `Dł. … shin` | 3 |
| `Len. 6.9 mett` / `8.8 mett` | `Dł. 6,9 mett` / `8,8 mett` | 2 |
| `Len. approx. 13 mett` / `6.9 mett` | `Dł. ok. 13 mett` / `6,9 mett` | 2 |
| `Dł. 14,53 m (15.59m incl. head lasers)` | `Dł. 14,53 m (15,59 m z działkami)` | 2 |
| `Masa 36,8 t (loaded)` | `Masa 36,8 t (pełna)` | 1 |
| `Dł. 440 m (294m)` | `Dł. 440 m (294 m)` | 1 |
| `Dł. 19,4 m (land)` | `Dł. 19,4 m (ląd)` | 1 |

Zasady: polski przecinek dziesiętny i spacja przed jednostką (`Masa 54,0 t`),
spacja jako separator tysięcy (`32 000 t`), **jednostki fikcyjne/żartobliwe
zostają w romaji** (`shin`, `zusshiri`, `mett`, `rufton` — brak polskich
odpowiedników, a `メット` to nie „metr", lecz uniwersum Gundam), etykiety
pozostają zgodne z przyjętym `Masa`/`Dł.`, `b.d.` dla `未設定` bez zmian.

`Weight 8.103kg` (Berserga WP) odczytano jako **8103 kg**, nie 8,103 kg
[hipoteza]: sąsiednie AT z tej samej serii mają `6387 kg` (Scopedog) i
`8089 kg` (Fatty), a jednostka o masie 8 kg jest niemożliwa; JP notuje tam
kropkę jako separator tysięcy, tak jak w `空重量 8,450kg`. Gdyby właściciel
uznał inaczej, wiersz wraca do `Masa 8,103 kg` jedną linią planu.

### 2. Komunikaty systemowe — 9 wierszy (`04_config_text`, `config_sysmes`)

* `39944`, `40068`, `44704` — **monity o nieudanym zapisie były po angielsku**
  (`Save failed. Continue without saving?`) — jedyne nietłumaczone zdania
  widoczne dla gracza w całym audytowanym zakresie:
  * `39944` → `Zapis nie powiódł się. / Po "Starcie gry" z ekranu tytułowego /
    gra ruszy od poprzedniego zapisu. / Czy na pewno?`
  * `40068`, `44704` → `Zapis nie powiódł się. / Kontynuować bez zapisu?`
* `39967`, `40006` — warianty nakładających się napisów tego samego dialogu
  ujednolicono do tej samej treści (wcześniej dłuższa linia miała 49 komórek;
  teraz najdłuższa ma 36).
* `43897`, `44013` — napis `製品版をダウンロードします。` („Pobierz pełną wersję
  gry") zawierał **tytuł gry** zamiast treści → `Pobierz pełną wersję gry.`
* `43894`, `44010` — wariant z osieroconą partykułą `の` → `- / Pobierz pełną
  wersję gry.` (EN zostawia `of`; PL używa kreski jak przy innych urwanych
  wariantach).

Limity szerokości: reguła audytu = **nowa szerokość ≤ max(dotychczasowa
szerokość wiersza, szerokość JP + 4 komórki)**. Dla jednowierszowych etykiet
`sysmes` (≤16 bajtów JP) obowiązuje dodatkowo zmierzona reguła z
`config/label_fit_rules.tsv` (nie szersze niż japoński) — wszystkie zmienione
wiersze ją spełniają.

## Czego sprawdzono i nie zmieniono

Skany klas kontrolowanych na 5 846 unikalnych tekstach prozy (poza dialogami,
które przeszły przegląd w v4.3/v4.4):

* **Braki diakrytyków** — 0 rzeczywistych trafień po odsianiu poprawnych słów.
* **Podwojone wyrazy** — 1 trafienie: `komend/komend` w `sysmes:29165`, ale to
  **nie błąd tłumaczenia**: napis źródłowy (JP) to fragment puli nakładających
  się napisów, a wiersz EN ma ten sam defekt (`using commands`). Pozycja do
  decyzji właściciela (patrz niżej).
* **Spacje/przecinki** — po odsianiu tokenów `%s`/`＠n`: 0 rzeczywistych.
  `Trudność   :`, `Obszar     :` itd. to **wyrównanie kolumn** w tabelach
  statystyk, nie błąd.
* **CJK w PL tekstach** — 11 wierszy z jednym znakiem kanji (`牾`, `珱`, `淫`,
  `珖`, `炻`, `踴`, `需`) w `04_config_text`; **EN jest identyczne**, więc to
  artefakt ekstrakcji (śmieciowe 2-bajtowe pozostałości), nie brak tłumaczenia.
  Nie ruszane — patrz pytania.
* **Nietłumaczone angielskie zdania** — poza poprawionymi monitami o zapisie
  żadne nie zostało: 142 trafienia skanu to nazwy przycisków (`SELECT`) i
  nazwy własne. Kalibracja: `PL == EN` w 3 345 wierszach dotyczy niemal
  wyłącznie nazw własnych, serii, broni i skrótów (`EN-10`, `EC x2`, `Lv3`).
* **Terminologia** — spójna: skróty `Atk 1007 · Cel 989 · Unik 961 · Obr 929 ·
  Kryt 684` (UI) i `Atk 350 · Cel 317 · Kryt 256 · Obr 251` (efekty); pełne
  formy (`Celność`, `Obrażenia`) występują tylko tam, gdzie pasują
  gramatycznie. `Morale`, `PD`, `EN`, `SP` używane konsekwentnie.
* **Strony pomocy `config_reference`** (77 unikalnych), **notki misji**
  (`mission_note`, 13 unikalnych tekstów), **osiągnięcia** (`config_achievement`,
  75), **nazwy tła/map/grup** — przejrzane w całości; bez błędów językowych.
  Skróty w wąskich polach (`wzg.`, `czerw.`, `ziel.`) są świadome i spójne.
* **`Pilot: Black Tri-Stars (Gaia, Ortega, Mash)`** — zostawione: `Pilot` jest
  poprawnym słowem polskim, a `Black Tri-Stars` jest w przyjętym korpusie
  nieodmieniane (28 wystąpień).

## Pytania do właściciela (nierozstrzygnięte, bez zmian w tekście)

1. **Cyfry pełnej szerokości** w 9 wierszach `config_status_change`
   (`１ tura  Unik -５０％  Celność -５０％`) pochodzą z JP, EN też je zostawił.
   Zmiana na `1 tura  Unik -50%  Cel` jest kosmetyczna, ale dotyka pola o
   potencjalnie stałej szerokości — czeka na zgodę.
2. **Śmieciowe wiersze z jednym kanji** (11) — czy wyczyścić je do pustego
   napisu, czy zostawić (EN też je ma)?
3. **`sysmes:29165`** — JP i EN są tam wewnętrznie niespójne (`using commands`
   w treści o przerywnikach); wymaga ustalenia, który offset jest naprawdę
   wyświetlany, zanim tekst PL zostanie przepisany.
4. **Jednostki żartobliwe** (`shin`, `zusshiri`, `mett`, `rufton`) — obecnie
   romaji; jeśli mają być spolszczone, potrzebna decyzja o formie.
5. **Wiersze EN z tym samym błędem** `43897`/`44013` (tytuł gry zamiast
   „Download the full version.") — poprawka należy do zestawu EN, poza
   zakresem tej zmiany PL.

## Ograniczenia

Bez plików gry w sandboxie: brak przebudowy fizycznego ISO/DLC i brak testu
w PPSSPP. `runtime_tested = false`. Widoczność w grze: panel danych jednostki
(dokumentacja mecha) oraz okno monitu o nieudanym zapisie.
