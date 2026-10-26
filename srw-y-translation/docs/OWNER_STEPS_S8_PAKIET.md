# Paczka dla tłumacza — gotowa i wysłana

## Gdzie ją znajdziesz

Ten sam folder na Drive, plik **`plik_dla_tlumacza.zip`** (9,629,651 B):

<https://drive.google.com/file/d/1ux0Da1NXSwvtCwA9y2enPanT2RqB73Yg/view>

SHA-256 `b221008e1e10ba15dce3379a88fc34d9e89a94b6005089febdd10d3b4542b783`
— jeśli po pobraniu skrót się zgadza, plik jest w całości.

**Tego pliku nie podmieniasz w grze.** To paczka do wysłania tłumaczowi. Instalowanie
do gry to osobny plik (`PATCHER.bat`, robię go teraz).

## Co jest w środku

```text
plik_dla_tlumacza.zip
├── README.md      instrukcja dla tłumacza (6 KB, układ jak w SRW OE)
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

- **sceny**: liczba linii (okno mieści 3 — ani japoński, ani angielski nigdy nie mają
  więcej), szerokość japońskiego w celach, pojemność okna (3 linie) i najszersza kwestia,
  jaką gra wyświetla w tym typie sceny (do 240 celi);
- **tabele jednorodne** (nazwy broni, imiona pilotów, nazwy misji): **jeden limit dla
  całego typu danych** — najdłuższy tekst tego rodzaju, jaki gra pokazuje, w obu językach;
- **tabele mieszane** (np. `system_text`: etykieta `Traits`, jej dwie wartości, potem
  `Hobbies` i jego wartości): **każde pole ma własny limit**, a wiersz `limit:` wymienia
  teksty, które w tym polu stoją.

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
