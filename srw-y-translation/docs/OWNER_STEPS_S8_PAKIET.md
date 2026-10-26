# Paczka dla tłumacza — wersja 3

## Gdzie ją znajdziesz

Ten sam folder na Drive, plik **`plik_dla_tlumacza_v3.zip`** (8,208,973 B):

<https://drive.google.com/file/d/1PB1GVocO1zYWJx6H6xaarvan2LF_hiGA/view>

SHA-256 `fbcd8631f8b15ef9ac345c7639464b537657d982078a4158ec3969da65843989`
— jeśli po pobraniu skrót się zgadza, plik jest w całości.

Wersje `plik_dla_tlumacza.zip` i `plik_dla_tlumacza_v2.zip` są nieaktualne — do kosza.

**Zmiana w v3:** `limit:` to już tylko jedna liczba — `do 270 znaków` (sceny) i `do N
znaków` (tabele). Zniknęło `(3 linie po 90)` i `(2 linie)`, bo to nasza robota przy
składaniu, a nie limit tłumacza. Tłumacz pisze jedną linią i liczy znaki.

## Co poprawiłem po Twoich uwagach

1. **Dziwne znaki.** To nie były uszkodzone pliki, tylko dwa rodzaje znaków, których
   nie widać — a Twój edytor rysuje je jako czarne prostokąty z podpisem (`U+3000`
   to spacja pełnej szerokości, używana w japońskim jako wcięcie; do tego `\r`, `\t`
   i znaczniki kierunku). Wyleciały wszystkie. Każda linia gry to teraz osobna linia
   pliku, bez `\n` wpisywanych jako znaki i bez pustych linii na wcięcia.
   Element 5 z Twojego zrzutu:
   ```text
   5. [Narracja] ～皇帝ルルーシュ パレード～
      limit: do 270 znaków
      EN: Emperor Lelouch's Parade
      PL:
   ```

   Nic się przy tym nie psuje przy składaniu: **linia japońska i `EN:` są tylko do
   czytania**. Miejsce w grze znajdujemy po numerze elementu i nazwie sceny, a wcięcia,
   puste linie i łamanie bierzemy z oryginalnych danych gry (te same pliki, z których
   powstała paczka — nietknięte). Dlatego nie trzeba żadnych tagów w tekście: tłumacz
   pisze wyłącznie polskie słowa po `PL:`, a znaki formatowania wstawiamy sami.
2. **`limit:` w scenach.** Miałeś rację — liczby japońskich celi i „tyle ma japoński”
   nic tłumaczowi nie dają. Teraz jest jedna zasada dla wszystkich kwestii:
   **do 270 znaków**. Skąd: okno ma 3 linie, najdłuższa linia angielskiej wersji gry
   ma 137 znaków, polski jest dłuższy od angielskiego, więc 3 × 90 = 270 mieści się
   z zapasem. Skoro tłumacz pisze jedną linią, w paczce jest tylko ta jedna liczba —
   bez „po 90" i bez liczby linii.
3. **`limit:` w widokach.** Też racja. Zamiast całego wywodu jest `limit: do 42 znaków`.
   „Cele” zniknęły — w paczce jest wyłącznie liczba polskich znaków (polska litera = 1,
   japoński znak = 2). Wyjaśnienia przeniosłem do README paczki, gdzie czyta się je raz,
   a nie przy 160 tysiącach elementów. Dopisek `(2 linie)` pojawia się tylko tam, gdzie
   pole jest wielolinijkowe.

Przy okazji: wiersz `tokeny:` nie wymieniał kodów `[p1:]`, `[r1:]`, `[p2:]`, `[i:]`
(nazwy jednostek gracza i wroga wpisywane przez grę) — teraz je wymienia, żeby tłumacz
ich nie przetłumaczył.

**Tego pliku nie podmieniasz w grze.** To paczka do wysłania tłumaczowi. Instalowanie
do gry to osobny plik (`PATCHER.bat`, robię go teraz).

## Co jest w środku

```text
plik_dla_tlumacza.zip
├── README.md      instrukcja dla tłumacza (6,6 KB, układ jak w SRW OE)
├── sceny.zip      spis-scen.md + 37 plików scen
└── widoki.zip     9 plików tabel
```

| część | ile | do wpisania `PL:` |
|---|---|---|
| sceny | 611 scen, 120 665 linii, 37 plików `.md` | 97 514 |
| widoki | 44 344 elementy, 9 plików `.md` | 41 228 |
| razem | 160 400 elementów | **138 742** |

Pozostałe elementy to powtórzenia w obrębie pliku — tłumaczenie dziedziczy się samo,
tłumacz ich nie przepisuje (tak samo jak w OE).

## Limity — na czym stoją

Każdy element ma linię `limit:` policzoną z danych gry, **na pole, w które trafia tekst**:

- **sceny**: jedna liczba dla wszystkich kwestii — **do 270 znaków**;
- **tabele jednorodne** (nazwy broni, imiona pilotów, nazwy misji): **jeden limit dla
  całego typu danych** — najdłuższy tekst tego rodzaju, jaki gra pokazuje;
- **tabele mieszane** (np. `system_text`: etykieta `Traits`, jej dwie wartości, potem
  `Hobbies` i jego wartości): **każde pole ma własny limit**.

Granice pól wyznacza `tools/s6_groups.py` z tekstów gry (nowe pole = skok długości
ponad 1,6x albo zmiana liczby linii); tabele jednorodne dostają jedno pole na całość.
Liczby: `local/s6/limits.json` + `local/s6/groups.json`, opis w `docs/LIMITY_Y.md`.

## Czego w paczce nie ma i dlaczego

- **Nie ma obietnicy „zmieści się tyle bajtów”** — to zależy od trybu zapisu do gry
  (tryb A: ta sama długość, tryb B: przebudowa pliku). Limit w paczce jest **ekranowy**,
  bo to jest wersja, która nie zależy od trybu.
- **Nie ma zmierzonej szerokości pól w pikselach** — granice pól są odczytane z tego,
  jakie teksty gra w nich wyświetla. To przybliżenie, opisane w README paczki.
- Nie ma w paczce plików gry ani żadnych danych z Twojego repacka — tylko japoński tekst
  i angielskie odniesienie, tak jak w OE.

## Co dalej

1. Wyślij `plik_dla_tlumacza.zip` tłumaczowi (może dostać całość, niczego nie musi
   instalować).
2. Ja w tym czasie robię **`PATCHER.bat`** — jeden plik, który wkłada gotowe polskie
   pliki do gry i sam sprawdza, czy weszły.
