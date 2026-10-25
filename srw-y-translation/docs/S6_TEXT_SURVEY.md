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

## 6. DLC: osobne zestawy, osobne indeksy [confirmed — uwaga właściciela]

Właściciel zauważył katalogi obok `aa`. Ma rację i **poprawia to punkt 1**: liczba
„42 pliki” obejmuje **tylko podstawkę**.

Obok `aa` leży 10 osobnych zestawów Addressables, każdy z **własnym indeksem
`catalog_<nazwa>.json`** i własnymi bundlami:

| folder | indeks | indeks B | bundli | razem B |
|---|---|---|---|---|
| `AnniversaryExpansionPack` | `catalog_anniversaryexpansionpack.json` | 5 308 249 | 2 601 | 1 678 581 815 |
| `ExpansionPack` | `catalog_expansionpack.json` | 3 031 427 | 1 551 | 814 688 229 |
| `Dlc1` | `catalog_dlc1.json` | 1 640 455 | 830 | 449 111 081 |
| `Dlc2` | `catalog_dlc2.json` | 1 593 357 | 782 | 554 220 108 |
| `SeasonPassBonus` | `catalog_seasonpassbonus.json` | 1 148 607 | 418 | 270 688 509 |
| `BonusMission` | `catalog_bonusmission.json` | 416 490 | 274 | 3 583 308 |
| `PremiumSound` | `catalog_premiumsound.json` | 103 933 | 64 | 163 395 645 |
| `EarlyPurchase` | `catalog_earlypurchase.json` | 68 160 | 42 | 516 572 |
| `DeluxeEdition` | `catalog_deluxeedition.json` | 15 054 | 7 | 57 292 |
| `UltimateEdition` | `catalog_ultimateedition.json` | 15 072 | 7 | 57 321 |

Razem **6 576 bundli i 3,6 GB**, a katalog podstawki ich nie opisuje (19 160 bundli
w `aa` vs 19 923 pliki w folderze). Dlatego kolejność jest taka: **najpierw indeksy
DLC (13,3 MB)**, potem — już z resolved adresami — krótka lista bundli DLC
z tekstem. Wstępnie widać, że tekst DLC jest tani: cały `BonusMission` to 274 bundle
i 3,58 MB, `EarlyPurchase` 42 bundle i 0,5 MB.

Arkusze: [`OWNER_STEPS_S6_TEXT_UPLOAD.md`](OWNER_STEPS_S6_TEXT_UPLOAD.md) (podstawka)
i [`OWNER_STEPS_S6B_DLC_CATALOGS.md`](OWNER_STEPS_S6B_DLC_CATALOGS.md) (indeksy DLC),
generowane przez `tools/build_text_upload_request.py` i
`tools/build_dlc_catalog_request.py`.

### 6a. Wynik po odebraniu indeksów DLC [confirmed, 2026-10-25]

Indeksy doszły (`google_drive/srw_y_dlc_catalog.zip`, 2 884 114 B, rozpakowane do
`local/dlc_catalog/`, 10 × `.json` + `.hash`) i przeszły to samo rozwiązanie adresów
co podstawka (`tools/map_catalog.py`): **0 nierozwiązanych** w każdym zestawie.

Skrypty scenariusza w DLC leżą pod **dwoma** rodami adresów, nie jednym:

| ród adresów | gdzie |
|---|---|
| `Assets/Datas/Scenario/<lang>/…` | BonusMission, Dlc1, Dlc2, EarlyPurchase, SeasonPassBonus, Deluxe/Ultimate |
| `Assets/DLC_EXP{,2}/PaidContent/Scenario/<lang>/…` | AnniversaryExpansionPack (630), ExpansionPack (439) |

Gdyby patrzeć tylko na pierwszy ród, wypadłoby 269 z 601 potrzebnych plików — dlatego
filtr w `tools/build_dlc_bundle_request.py` dopasowuje parę `Scenario/<lang>/`.

**Tabele językowe:** DLC nie mają własnych. Interfejs i opisy dodatków są w tabelach
`ja-JP`/`en-US` z `aa` (12 bundli z arkusza S6, w tym cztery DLC i dwie zaślepki).

**Skrypty DLC są tanie:** każdy skrypt to osobny bundle 5–18 kB. Dla `jp` + `en`:

| zestaw | `jp` | `en` |
|---|---|---|
| AnniversaryExpansionPack | 105 | 105 |
| BonusMission | 33 | 35 |
| Dlc1 | 46 | **brak** |
| Dlc2 | 51 | 51 |
| EarlyPurchase | 5 | 5 |
| ExpansionPack | 75 | 74 |
| SeasonPassBonus | 5 | 5 |
| Deluxe / Ultimate / PremiumSound | po 1 | po 1 |

Razem **601 plików, 7 032 042 B** — i **zero wspólnych nazw** z 30 bundlami
scenariusza z podstawki (sprawdzone), więc nic się nie dubluje. Lista:
[`OWNER_STEPS_S6C_DLC_BUNDLES.md`](OWNER_STEPS_S6C_DLC_BUNDLES.md),
`tools/collect_dlc_bundles.ps1`, dane: `local/dlc_scenario_bundles.json`.

Jedyna otwarta kwestia: **`Dlc1` nie ma w indeksie ani jednego skryptu `en`**
(46 `jp`, 0 `en`). Albo tak jest w grze, albo angielski leży w innym zestawie —
w pakiecie zobaczymy to wprost (misje Dlc1 zostaną z samym jp).

---

## 7. Odkodowanie tabel i scenariuszy (2026-10-25, po paczce S6)

### 7a. Rekord tabeli — zamknięte

Obiekt tabeli (`MonoBehaviour`, np. `prologue_en-US`):

```text
+0    12 x 0x00
+12   u32 1, u32 1, 8 B hash
+28   u32 dlugosc nazwy, nazwa, pad4
      u32 dlugosc locale, locale ("ja-JP"/"en-US"), pad4
      u32 2, 8 B hash, u32 0, u32 liczba rekordow
      rekordy...
      u32 2, u32 0                     <- 8-bajtowy terminator, zawsze obecny
```

Rekord:

```text
u32   klucz dolny    \
u32   klucz gorny    /  ta sama para jest w pliku jp i en dla tego samego napisu
u32   dlugosc tekstu w bajtach
...   tekst UTF-8
      pad4
u32   zawsze 0        (wszystkie 72 436 rekordow odczytanych tu)
```

czyli `nastepny = align4(rekord + 12 + dlugosc) + 4`. Chodzenie po rekordach zgadza się
ze liczbą z nagłówka **i** kończy dokładnie na terminatorze w **144 tabelach × 2 języki**
(`tools/s6_tables.py`, twardy błąd przy niezgodności).

**Klucz jest w rekordzie — i to on łączy języki.** Parowanie po pozycji jest błędne:
`robot_name` po japońsku zaczyna się od ライディーン, a po angielsku od `Combattler V`.
Po kluczu wychodzi `ライディーン → Reideen`, `洸 → Akira`, `底力Ｌ１ → Potential L1`.
`battle_voice` ma 2 043 powtórzone klucze dolne, więc kluczem jest **para** (dolny, górny),
unikalna w obu językach.

Wynik: `local/s6/tables.jsonl` — **44 344 wiersze**, 891 094 znaki jp / 2 121 512 znaki en.
141 wierszy nie ma drugiej strony: `active_ability-DLC3` (139 — bundle en ma 18 z 157
wpisów, czyli angielski tej tabeli jest w grze niepełny) i `voiceactor` (2).

### 7b. Scenariusze — co jest linią

Plik scenariusza to skrypt Lua wygenerowany z C++. Tekst, który widzi gracz, stoi jako
literal `[[ mówca\n「kwestia」 ]]` i **tylko** on ma w komentarzu `srw-tag=string-id>`:

```text
  {WPos_c, 2, FDMode_Normal, pid_CHISE,
  [[ちせ
「ん…？」]],
   0, NULL, NULL},  -- <srw-tag=speakEE>(...)<srw-tag=string-id>(87.0)
```

W pliku kontrolnym 147 z 160 literalow miało `string-id`; pozostałe 13 to nazwy BGM,
tła i efektów (`[[Y_DEM_2]]`, `[[221\t通常サイズ<...>左下]]`) — nigdy nie są pokazywane
jako tekst. Pierwsza linia wewnątrz literal to mówca (także lokalizowany: `ちせ`/`Chise`),
a linia zaczynająca się od samej spacji ideograficznej to wcięcie podpisu, nie mówca.

Wynik: `local/s6/scenario.jsonl` — **601 scen, 119 151 linii** ze 1 883 plików
(927 ja / 956 en): 114 383 linie sparowane, 159 tylko jp (`Dlc1` nie ma angielskiego),
4 609 tylko en.

**Czego nie parujemy:** 30 plików angielskich nie ma japońskiego odpowiednika — to
starsze wersje tych samych scen (nagłówek `$Date: 2024/11/20` vs `2025/11/07` w wersji
japońskiej). Parowanie po `string-id` **jest błędne i zmierzone jako błędne**: dla
`cse20_0024_0202800a` zgodność `pid_` ze sceną jp wynosi 93/278. Dlatego te 4 609 linii
zostaje w pakiecie z `EN:` jako jedynym źródłem, z jawnym opisem.

### 7c. Czego jeszcze brakuje

`Assets/DLC_EXP/FreePatch/Scenario/{jp,en}/…` — **19 scen, 19 + 19 bundli, 357 783 B**
(`docs/OWNER_STEPS_S6E_FREE_PATCH.md`, `tools/build_free_patch_request.py`). Nie ma ich
w żadnej dotychczasowej paczce. `ba1da373` (25 tabel podstawki) jest zbędny: te same
tabele są w `2d69c099`/`1cc7e02e`.
