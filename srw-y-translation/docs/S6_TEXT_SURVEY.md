# S6 — gdzie w SRW Y jest cały tekst (inwentarz pod pakiet dla tłumacza)

Stan: **2026-10-25**. Cel: zbudować `plik_dla_tłumacza.zip` w formie sprawdzonej
w OE (osobno `sceny/` z misjami i kontekstem, osobno `widoki/` z tabelami), z tekstem
japońskim, angielskim jako odniesieniem i miejscem na polski.

Wszystko poniżej jest **zmierzone na katalogu Addressables właściciela**
(`google_drive/catalog.json`, 41 543 062 B) przez `tools/map_catalog.py` oraz na
czterech bundlach, które już mam (`local/s4/`). Nie ma tu zgadywania.

## 1. Cały tekst to 42 pliki `.bundle`, 33,1 MB

| rodzina | adresy w katalogu | bundli | bajtów | mam |
|---|---|---|---|---|
| tabele Unity Localization, `ja-JP` | 144 | 6 | 1 162 795 | 1 (`1cc7e02e…`) |
| tabele Unity Localization, `en-US` | 144 | 6 | 1 249 645 | 1 (`2d69c099…`) |
| skrypty scenariusza `Assets/Datas/Scenario/jp` | — | część z 30 | — | 1 (`8939a711…`, 605 skryptów) |
| skrypty scenariusza `Assets/Datas/Scenario/en` | — | część z 30 | — | 1 (`1c12bbab…`, 678 skryptów) |
| razem skrypty scenariusza | 4 131 | 30 | 32 267 543 | 2 |

Reszta `StreamingAssets` (20 GB+) to audio CriWare, wideo, tekstury i modele —
sprawdzone po adresach katalogu: nie ma tam tekstu do tłumaczenia.

**Do zbudowania pakietu brakuje 38 plików (21,4 MB).** Lista i skrypt zbierający:
[`OWNER_STEPS_S6_TEXT_UPLOAD.md`](OWNER_STEPS_S6_TEXT_UPLOAD.md) oraz
`tools/collect_text_bundles.ps1` (generowane przez `tools/build_text_upload_request.py`).

## 2. Scenariusz: dwa języki w osobnych bundlach [confirmed]

Rozwiązanie adresów katalogu (`map_catalog.py`) daje jednoznaczny podział:

| bundle | adresy | prefiks |
|---|---|---|
| `8939a711c0d8a8fc00dee03e1013ecdb.bundle` | 605 | `Assets/Datas/Scenario/jp/…` |
| `1c12bbab8ed0f62ff22f808ce0138bc1.bundle` | 678 | `Assets/Datas/Scenario/en/…` |

Czyli **para JP + EN dla jednej misji leży w dwóch różnych plikach** — dlatego
potrzebne są oba zestawy (30 bundli), a nie 15.

W środku bundle to 605–678 `TextAsset`-ów o nazwach
`cse20_<numer>_<kod>_<typ>.lua`, gdzie typ to `dlgev` (dialogi) albo `sdemo`
(scenki/dema). Każdy skrypt to wygenerowany z C++ Lua: najpierw ~3 000 linii
stałych silnika (`pid_*`, `Inst_*`, `SE_*`, `FDMode_*` — **nie tekst**), potem dane.

**Tekst dialogu jest w środku skryptu jako `[[ … ]]`**, a mówca jest w komentarzu
przy rekordzie — to jest gotowy kontekst dla tłumacza:

```lua
  [[アニーナ
「$c各機、展開」]],
   0, NULL, NULL},  -- <srw-tag=speakEE>(エチカ)<srw-tag=string-id>(344.0)
```

- `<srw-tag=speakEE>` + nazwa w nawiasie = mówca (`エチカ` = Echika),
- `<srw-tag=string-id>` = identyfikator kwestii (do powtórzeń i do patcha),
- `$c` = kolor/kontrolka gry, `「」` = japoński cudzysłów — do zachowania lub zamiany
  na polski odpowiednik według jednej reguły w całym pakiecie.

Liczby z jednego bundla (`8939a711…`, 605 skryptów, `jp`): 5 587 linii z japońskim
poza komentarzami. Pełny wolumen policzę po otrzymaniu wszystkich 30 bundli.

## 3. Tabele językowe: 37 obiektów w jednym bundlu [confirmed]

`2d69c099…` (en-US) i `1cc7e02e…` (ja-JP) zawierają po **37 `MonoBehaviour`** —
24 tabele z S2 plus warianty DLC, `font`, `battle_voice`, `_search` itd. Nazwy są
z sufiksem języka (`prologue_en-US` / `prologue_ja-JP`), więc parę JP↔EN dostaje się
przez samą nazwę.

Surowy układ obiektu (bez typetree — ten jest w tym pliku bezużyteczny):

```
offset 0   12 × 0x00
+12        int32 = 1
+16        int32 = 1
+20        8 B hash
+28        int32 nazwa_długość · nazwa (UTF-8)
           padding do 4
           int32 język_długość · język ("en-US" / "ja-JP")
           padding do 4
           int32 = 2 · 8 B hash · int32 = 0 · int32 liczba_rekordów
           rekordy: { int32 klucz, int32 x, int32 długość, tekst UTF-8, ogon }
```

**32 z 37 tabel** (w obu językach) przechodzą ten układ rekord po rekordzie **do
ostatniego bajtu obiektu** — m.in. `spirit_command` 123, `mission_title` 378,
`pilot_name` 680, `battle_voice` 28 283, `prologue` 24, `dic_text_robot` 271,
`dic_text_pilot` 550.

**5 tabel ma zmienny ogon rekordu** (`system_text`, `ICE_operation`, `assist_text`,
`weapon_name`, `dialog_text`, `robot_name`): między tekstem a następnym kluczem jest
4–6 bajtów, inaczej niż w pozostałych. To ostatnia rzecz do rozpracowania przed
generatorem `widoki/`; nie wpływa na samą treść, tylko na bezbłędne przypisanie
rekordu do wiersza.

**Klucze są niezależne od języka** — dowód: `spirit_command` ma 123 rekordy w en
i 123 w ja, ze **123 wspólnymi kluczami**, więc parowanie JP↔EN po kluczu jest
pewne i nie zależy od kolejności. `prologue`: 18 wspólnych kluczy z 19/19
(jeden rekord różni się ogonem — ten sam problem z ogonem, nie z treścią).

## 4. Co jeszcze trzeba zmierzyć

- pełna liczba kwestii dialogowych i znaków po odebraniu wszystkich 30 bundli;
- czy `battle_voice` (28 283 rekordy, 1,48 MB) to cytaty bojowe do tłumaczenia,
  czy mapa identyfikatorów głosu;
- ile znaków ma każda komórka tabel — budżety (`limit:`) policzę z długości
  oryginału JP, tak jak w OE, ale limit szerokości **linii** wymaga danych
  o okienkach; w Y mamy teksty o stałej długości pola (tabele) i teksty w oknach
  (dialog), więc reguła będzie inna niż w OE;
- czy polski font obsłuży znaki w *tych* bundlach — potwierdzone jest tylko dla
  narracji otwarcia (S5b), więc to trzeba będzie sprawdzić osobnym testem.

## 5. Kolejność pracy

1. **Teraz:** właściciel wrzuca 38 bundli (21,4 MB) — arkusz S6.
2. Parser tabel (domknięcie 5 ogonów) + parser skryptów Lua → jeden wewnętrzny JSONL
   (id, kategoria, jp, en, budżet, mówca, źródło).
3. Generator widoków: `sceny/NNN-*.md` (misja = tytuł + uczestnicy + serie + kwestie
   po kolei), `spis-scen.md`, `widoki/*.md` (nazwy, umiejętności, duchy, interfejs,
   opisy misji) — dokładnie w formacie OE: `JP`, `EN:`, `PL:`, `limit:`.
4. `plik_dla_tłumacza.zip` + instrukcja PL (co wolno zmieniać, jak liczyć budżet,
   jak odesłać pracę, jak dziedziczą się powtórzenia).
5. Import zwrotny i patch — ta sama metoda, która zadziałała w S5b
   (`srw_y_fit_patch.py`, ten sam rozmiar pliku).
