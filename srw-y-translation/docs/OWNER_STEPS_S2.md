# Krok S2 — odczyt bundli zatrzymał się na szyfrowaniu (dla właściciela)

Oba bundle dotarły w całości (rozmiary zgadzają się co do bajtu), ale **gra
wysyła je zaszyfrowane**. To nie jest problem z plikami — pliki są dobre, tylko
całe zaszyfrowane, a klucz siedzi w kodzie gry. Szczegóły techniczne:
`docs/S2_FINDINGS.md`, sekcja „Blokada”.

Co to znaczy praktycznie: dopóki nie zdejmiemy szyfrowania, **nie umiem policzyć
znaków ani przygotować łatki na plikach**. Dlatego pytam teraz o inny plik — i to
ostatni, o jaki proszę na tym etapie.

## Co jest potrzebne

```
D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\il2cpp_data\Metadata\global-metadata.dat
```

rozmiar **18 909 544 B** (18,0 MiB).

To metadane kodu gry: **nazwy klas, metod i teksty wpisane w kod** (literały).
Nie zawiera assetów, grafik, dźwięków ani dialogów. Jeśli klucz do bundli jest
zapisany w kodzie jako tekst, jest właśnie tutaj — a wtedy odczyt tekstu rusza
od razu i w całości po mojej stronie.

Wgraj do **`SRW/SRWY`**, tak jak poprzednie pliki. Folder otworzysz tak:

```powershell
explorer "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\il2cpp_data\Metadata"
```

**Jeśli nazwa `global-metadata.dat` jest dla Ciebie myląca** — to nie są dane
gry, tylko „spis” nazw z kodu (18 MB). Nie zawiera niczego, czym da się grać.

## Opcjonalnie, razem z tym (małe, pomaga)

Z folderu `…_Data\StreamingAssets\aa\`:

- `settings.json` — **1 604 B**
- `AddressablesLink\link.xml` — **99 045 B** (lista klas używanych przez grę;
  może wprost wskazać klasę od szyfrowania)

Razem ~18,1 MB — czyli mniej niż poprzedni `catalog.json`.

## Jeśli ten trop nie zadziała

Wtedy zostaje droga runtime: gra sama odszyfrowuje bundle w pamięci, więc
wtyczka do MelonLoadera może zrzucić tekst bez znajomości klucza. Uprzedzam
uczciwie: **w moim środowisku nie ma kompilatora C#**, więc ta droga wymaga
najpierw rozwiązania problemu po mojej stronie — nie obiecuję jej na dziś.
Napisałem to też w `docs/STATUS.md`, żeby nie zniknęło.

## Czego nie trzeba robić

- Nie wysyłaj `GameAssembly.dll` (74,9 MB) — jeszcze nie teraz; sens miałby
  dopiero, gdyby metadane nie wystarczyły.
- Nie ruszaj niczego w folderze gry.
- Nie szukaj „klucza” samodzielnie — to nie jest plik, który gdzieś leży.

## Co dalej

1. Ja: przeszukuję literały z metadanych jako kandydatów na klucz i sprawdzam
   każdy na prawdziwym bundlu (jeśli odszyfrowanie da nagłówek `UnityFS`, mamy
   klucz — to dowód, nie zgadywanie).
2. Jeśli klucz się znajdzie: odczyt wszystkich tabel tekstowych i skryptów
   scenariuszy → **uczciwa liczba znaków** i decyzja go/no-go.
3. Jeśli nie: wracam do drogi runtime i melduję, co jest realne.
