# Pakiet dla tłumacza SRW Y — stan i forma

Forma jest **taka sama jak przy SRW OE**: jedno archiwum, w środku instrukcja i dwa zipy
z plikami `.md` do tłumaczenia. Różnica wynika tylko z języka docelowego — w OE
tłumacz wpisywał angielski po `EN:`, tutaj polski po `PL:`, a `EN:` jest gotowym
odniesieniem.

```text
plik_dla_tlumacza_v6.zip
├── README.md      instrukcja (polski, ten sam układ co w OE) + odpowiedzi 1–6
├── sceny.zip      spis-scen.md + 37 plików scen (611 scen, 120 665 linii)
└── widoki.zip     9 plików tabel (44 340 elementów; tabela `font` nie jest wysyłana)
```

Element ma układ z OE:

```text
14. [Dialog - ちせ] 「ん…？」
   limit: do 270 znaków
   tokeny: zachowaj dokładnie: $c
   EN: "Huh?"
   PL:
```

Grupy plików: `odcinek-NN[_x].md` dla podstawki (numeracja z nazw scenariuszy) oraz
`dlc-<Pakiet>[_x].md` dla dodatków; plik dzieli się na części `_a`, `_b`, … powyżej
8 000 linii. `spis-scen.md` listuje wszystkie 611 scen z grupą, mówcami i liczbą linii.

## Co jest w środku (zmierzone, 2026-10-25)

| część | elementy | sloty `PL:` | źródło |
|---|---|---|---|
| sceny | 116 056 | 97 514 | 611 scen z 946 plików Lua jp podstawki, DLC i darmowej łatki |
| widoki | 44 340 | 41 222 | 143 tabele × 2 języki (bez `font`) |
| razem | 160 396 | **138 736** | |

Pozostałe 21 565 elementów to powtórzenia w obrębie pliku — mają znacznik
`(powtórzenie elementu N)`, tłumaczenie dziedziczy się automatycznie, tak jak kopie w OE.

## Kompletność

- podstawka: 605 plików jp + 678 en (z tego 605 par; 73 to starsze wersje angielskie),
- DLC: 601 bundli (323 jp / 278 en), w tym `Dlc1` bez angielskiego,
- **darmowa łatka** (`DLC_EXP/FreePatch`) jest w pakiecie: 38 bundli, 363 847 B
  (`srw_y_free_patch.zip`) — 1 514 linii; wcześniej brakowało 19 scen i to była
  jedyna przeszkoda, żeby wysłać paczkę.

## Odtworzenie

```text
python3 tools/s6_tables.py
python3 tools/s6_scenario.py
python3 tools/build_translator_package.py
```

Dane wejściowe: `local/s6/tables.jsonl`, `local/s6/scenario.jsonl` (oba poza repozytorium,
bo zawierają tekst gry), skrypty w `local/s4_plain/` i `local/s6/plain/`.

## Limity w paczce (wersja poprawiona, 2026-10-26)

Każdy element ma **jedną** linię `limit:` z liczbą polskich znaków, policzoną z danych
gry (`tools/s6_limits.py`, `local/s6/limits.json`, opis w `docs/LIMITY_Y.md`):

```text
14. [Dialog - ちせ] 「ん…？」
   limit: do 270 znaków

7. [Nazwa broni] ゴッドミサイル
   limit: do 50 znaków

3. [Tekst interfejsu] 冷酷非情
   limit: do 14 znaków

98. [Tekst interfejsu] 敵から攻撃を仕掛けられた際、…
   limit: do 91 znaków
```

- **sceny**: okno mieści 3 linie; najdłuższa linia, jakiej używa angielska wersja gry,
  ma 137 znaków, a polski jest od angielskiego dłuższy — budżet to 90 znaków na linię,
  czyli **270 na kwestię**. Tyle się mieści, bo łamaniem linii zajmuje się nasze narzędzie.
- **tabele**: `do N znaków`, gdzie N = najdłuższy tekst, jaki gra wyświetla **w tym samym
  polu** (japoński liczony jako 2 znaki, polski jako 1).

W wersji 3 (2026-10-26) zniknęło też `(3 linie po 90)` i `(2 linie)`: tłumacz pisze
**jedną linią**, więc liczba linii jest naszą sprawą przy składaniu, a nie jego limitem.
W paczce zostaje wyłącznie liczba znaków, którą można policzyć.

Wersja z 2026-10-25 podawała w `limit:` cele japońskie, liczbę linii oryginału i najszerszą
kwestię w grze — właściciel to odrzucił jako nieczytelne i nieprzydatne dla tłumacza
(„czemu podajesz jakieś cele zamiast ilości liter”). Cała metodologia pomiaru została
w README paczki i tutaj, a w plikach do tłumaczenia jest tylko liczba, którą można
policzyć.

**Limit jest na pole, nie na pojedyncze słowo** (decyzja właściciela, 2026-10-26):
- tabela z jednym rodzajem danych (nazwy broni, imiona pilotów, nazwy misji) → **jeden
  limit dla wszystkich wpisów**, równy najdłuższemu tekstowi tego rodzaju w grze;
- tabela mieszana (`system_text` trzyma etykietę `Traits`, jej wartości, potem `Hobbies`
  i jego wartości) → **każde pole ma własny limit**.

Granice pól wyznacza `tools/s6_groups.py` (`local/s6/groups.json`) z samych tekstów gry:
nowe pole zaczyna się, gdy długość skacze o więcej niż 1,6x albo zmienia się liczba linii.
Tabele jednorodne dostają jedno pole na całość. Sprawdzone w grze: `Chłodny, bezwzględny`
(20 znaków) nachodził na etykietę `Charakter`, której pole mieści 14 znaków.

Który limit jest twardy, zależy od trybu zapisu — patrz `docs/POWROT_TLUMACZEN.md`.

### Tekst widziany przez tłumacza

Linie japońskie i `EN:` są podane **tak, jak gra je rysuje**, ale bez tego, czego nie widać:
`\r`, `\t`, znaczniki kierunku (U+200E/U+200F), spacje ideograficzne (U+3000) i puste
linie formatujące są usuwane, a każda linia gry to osobna linia pliku. Powód: edytor
właściciela pokazywał U+3000 jako czarne prostokąty z napisem `IDSP`, co wyglądało jak
uszkodzony plik. Wcięcia i łamanie linii odtwarzamy sami przy składaniu tekstu, więc
`PL:` to zawsze jedna linia tekstu.

## Wersja 4 (2026-10-26) — odpowiedzi na pytania tłumacza

Tłumacz zwrócił sześć pytań (cytaty bez mówcy, wiersze hex, fala `～`, mapa
scena → rozdział, `鋼鉄ジーグ`, płeć bohatera w `$n`/`$c`). Odpowiedzi z dowodami:
[`ODPOWIEDZI_TLUMACZOWI_Y.md`](ODPOWIEDZI_TLUMACZOWI_Y.md); w skrócie:

| pytanie | rozstrzygnięcie | zmiana w paczce |
|---|---|---|
| 1. mówca cytatów bitewnych | nazw **nie ma w danych** (0/34 317 cytatów występuje w fabule, żadna tabela nie dzieli kluczy) | numer grupy `[głos N/39]` + 339 kwestii pilotów przeniesione z „pozostałych” |
| 2. wiersze szesnastkowe | to tabela `font`, nie tekst | tabela **wyrzucona** z paczki |
| 3. fala `～` | EN nie używa jej ani raz | reguła w README (sekcja 4): `-` albo nic |
| 4. scena → rozdział | powiązania **nie ma w danych** | `spis-scen.md` z podsumowaniem grup |
| 5. `鋼鉄ジーグ` | dane poprawne, 1901 to powtórzenie 732 | wyraźniejsze oznaczenie powtórzeń |
| 6. płeć bohatera | **dwie wersje w grze**: `cmd_BranchProtagonist 0/1`, `pid_MHERO`/`pid_FHERO` | 9 034 linie `(wariant: bohater)`, 8 623 `(wariant: bohaterka)` |

Do tego: pełne odtworzenie danych w tym przebiegu z `srw_y_dlc_bundle.zip` i
`srw_y_free_patch.zip` — **0 brakujących bundli** (wcześniej raport miał 639 wpisów
„bundle missing on disk”, bo dodatków nie było na dysku). Numeracja elementów w plikach
scen jest **identyczna z v3** (37 plików różni się tylko dodanymi znacznikami), więc praca
zaczęta na v3 przenosi się przez numer elementu.

## Wysłane (2026-10-26)

Wersja bieżąca — **`plik_dla_tlumacza_v6.zip`** (sekcja 7 przepisana po danych, które
właściciel odesłał tego samego dnia: **bank głosów = jedna seria**, dowiedzione dla
11 z 39 banków; druga prośba o kontenery głosu — `SRW_Y_BVC_PROSBA.zip`; treść plików
do tłumaczenia **bez zmian** względem v5 — ta sama numeracja, te same elementy):

| | |
|---|---|
| plik | **`plik_dla_tlumacza_v6.zip`** |
| rozmiar | 8,283,635 B |
| SHA-256 | `e19d8505d6cbab34d31fcada5a46398b27a5158b113699a47720099a2056aa93` |
| Drive | folder `1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`, id `1tnXKRYzt93u2Arjb_UJj0c8pJW8sjMYh` |
| w środku | `README.md` (15,958 B), `sceny.zip` (6,195,930 B), `widoki.zip` (2,079,401 B) |
| sprawdzenie | pobrane z Drive z powrotem, SHA-256 zgodne, bajt w bajt **identyczne** |
| treść do tłumaczenia | `sceny.zip` i `widoki.zip` — **te same rozmiary co w v4/v5**; zmienił się tylko `README.md` w paczce (sekcja 7 i 9) |

Poprzednia wersja — **`plik_dla_tlumacza_v5.zip`** (sekcja 7 o cytatach bitewnych
przepisana na język danych: czym jest grupa głosu, co wiemy o kluczach i jak domkniemy
mówców; treść plików do tłumaczenia **bez zmian** względem v4 — ta sama numeracja, te
same elementy):

| | |
|---|---|
| plik | **`plik_dla_tlumacza_v5.zip`** |
| rozmiar | 8,283,398 B |
| SHA-256 | `d765c481f1eb5ec18f4e506552c33d85e8e3496443cb24e70582137bf8491611` |
| Drive | folder `1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`, id `1U-gZS-LfEZq2h9tAZgl_R_WA2bsivdU4` |
| w środku | `README.md` (15,449 B), `sceny.zip` (6,195,930 B), `widoki.zip` (2,079,401 B) |
| sprawdzenie | pobrane z Drive z powrotem, SHA-256 zgodne, bajt w bajt **identyczne** |
| treść do tłumaczenia | `sceny.zip` 6,195,930 B i `widoki.zip` 2,079,401 B — **te same rozmiary co w v4**, generator jest deterministyczny, więc numeracja i elementy są identyczne; zmienił się tylko `README.md` w paczce (sekcja 7) |

Wersja z rana 2026-10-26 — **`plik_dla_tlumacza_v4.zip`** (ta sama treść do tłumaczenia,
starsza sekcja 7):

| | |
|---|---|
| plik | `plik_dla_tlumacza_v4.zip` |
| rozmiar | 8,282,791 B |
| SHA-256 | `235bee7a9b0ed352e3af077ed65f6cd51bb5687ff507544b1de6e3c09a0e80bf` |
| Drive | folder `1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`, id `1tWR6mafmm-MHRyJZmbfflTzy5a0SPzLc` |

Poprzednia wersja — **`plik_dla_tlumacza_v3.zip`** (nieaktualna, bez znaczników płci
i z tabelą `font`):

| | |
|---|---|
| plik | **`plik_dla_tlumacza_v3.zip`** |
| rozmiar | 8,208,973 B |
| SHA-256 | `fbcd8631f8b15ef9ac345c7639464b537657d982078a4158ec3969da65843989` |
| Drive | folder `1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`, id `1PB1GVocO1zYWJx6H6xaarvan2LF_hiGA` |
| w środku | `README.md` (6 675 B), `sceny.zip` (6,152,141 B), `widoki.zip` (2,052,713 B) |

Nieaktualne: `plik_dla_tlumacza.zip` (id `1ux0Da1NXSwvtCwA9y2enPanT2RqB73Yg`, cele
japońskie i surowe znaki formatowania) oraz `plik_dla_tlumacza_v2.zip`
(id `1x27QLGJkSXFOQTeapgMLsDm6ueTMAu3a`, `limit` z liczbą linii).

Zmierzona treść v5: **611 scen w 37 plikach, 120 665 linii**, `spis-scen.md`
z podsumowaniem grup, mówcami i liczbą linii każdej sceny; **9 plików tabel,
44 340 elementów**. Slotów `PL:` razem **138 736** (sceny 97 514, widoki 41 222).
Pozostałe elementy to powtórzenia w obrębie pliku (tłumaczenie dziedziczy się
automatycznie).

Dane wejściowe tej wersji (wszystkie z Drive właściciela):

| zip | bundli | rola |
|---|---|---|
| `srw_y_text.zip` | 4 | podstawka: scenariusze jp/en + tabele jp/en |
| `srw_y_tekst.zip` | 38 | tabele DLC i łatki w obu językach |
| `srw_y_dlc_bundle.zip` | 601 | scenariusze DLC (10 paczek) |
| `srw_y_free_patch.zip` | 38 | scenariusze darmowej łatki |

Kolejność odtworzenia: rozpakować powyższe do `local/s4_plain`,
`local/s6/plain/{tekst,dlc/<Pakiet>,fp}`, odszyfrować (`srw_y_bundle_crypt.decrypt`),
potem `tools/s6_tables.py`, `s6_scenario.py`, `s6_limits.py`, `s6_groups.py`,
`build_translator_package.py`.
