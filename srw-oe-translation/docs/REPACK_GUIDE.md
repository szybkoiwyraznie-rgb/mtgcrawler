# REPACK — instrukcja krok po kroku (na Twoim PC, po polsku)

Cel: zbudować nowy obraz ISO, który PPSSPP
uruchomi — najpierw **bez zmian** (test, że repack w ogóle działa), potem **z podmienionym
plikiem** (test, że Twoja zmiana trafia do gry).

Czego potrzebujesz na dysku:
- oryginał: `SRW OE 1.08.iso`,
- rozpakowane drzewo: katalog `SRW_OE_1.08` (z `PSP_GAME/...` w środku),
- świeże repo (gałąź `arena/c656a5df-mtgcrawler`) — są w nim `REPACK_ISO.bat` i `tools/iso_pack.py`,
- Python w PATH (masz go — uruchamiasz nim pipeline).

## WAŻNE: Twoja ekstrakcja `SRW_OE_1.08` jest NIEPEŁNA

Prawdziwy dysk ma ~672 MB danych (80 plików), a katalog rozpakowany waży ~293 MB — narzędzie
rozpakowujące **pominęło duże pliki** (`BgmSet00.awb`, `UPDATE/DATA.BIN`, `bacb00.cpk`,
`lmap.cpk`, `voice00.awb`, `mov00.cpk`, `robo00.cpk`…). Dlatego repack z drzewa dał ~300 MB i
byłby okrojony. **Używaj metody `repackiso`**, która czyta niezmienione pliki wprost z
oryginalnego ISO — nic nie może zginąć, a drzewo w ogóle nie jest potrzebne.

## KROK 1 — test tożsamości (bez patchy)

To sprawdza, czy spakowany obraz w ogóle startuje. **Nie pomijaj go.**

1. Otwórz wiersz poleceń w katalogu repo (`srw-oe-translation`). Użyj Pythona wprost (działa
   w PowerShell i w cmd):

   ```
   python tools\iso_pack.py repackiso "D:\SRWOE\SRW OE 1.08.iso" "D:\SRWOE\repacked.iso"
   ```

   - arg1 = oryginalne ISO (źródło wszystkich plików + 32 KiB bootowe), arg2 = nowy obraz.
   - Brak arg3 = brak patchy.
   - W PowerShell nie cytuj samej nazwy skryptu `.bat`; tu wywołujemy `python`, więc pułapki
     cytowania nie ma.
3. Poczekaj (kilkadziesiąt sekund; nie trzyma 660 MB w RAM).
4. Podmień w PPSSPP oryginalne ISO na `repacked.iso` i uruchom.
5. **Oczekiwany wynik:** gra startuje i zachowuje się identycznie jak oryginał.
   Jeśli się wysypie — nie przechodź dalej, tylko wyślij mi objawy; to znaczy, że writer ISO
   wymaga poprawki (to jedyny nieprzetestowany na prawdziwym dysku element).

## KROK 2 — test z podmianą

1. Zrób katalog patchy, np. `D:\...\patch`, i odtwórz w nim ścieżkę względem drzewa:
   `D:\...\patch\PSP_GAME\USRDIR\eventP00.cpk` — to Twój zmodyfikowany plik
   (np. z nałożonym tłumaczeniem; na razie możesz użyć pliku testowego).
2. Uruchom (arg3 = katalog patchy; każdy plik w nim nadpisuje odpowiadający mu plik z ISO;
   ścieżki patchy pisz małymi literami jak w drzewie, porównanie jest bez rozróżniania
   wielkości liter):

   ```
   python tools\iso_pack.py repackiso "D:\SRWOE\SRW OE 1.08.iso" "D:\SRWOE\repacked.iso" "D:\SRWOE\patch"
   ```
3. Uruchom `repacked.iso` w PPSSPP i sprawdź, czy zmiana jest widoczna.

## Uwagi

- Rozdziały 2–8 (DLC) **nie potrzebują repacku** — PPSSPP czyta je luzem z
  `memstick/PSP/GAME/NPJH50521`; wystarczy podmienić pojedynczy `.EDAT`.
- Repack służy tylko do rozdziału 1 (dysk) i do walidacji procesu.
- Narzędzie nigdy nie dotyka oryginału — czyta drzewo i ISO tylko do odczytu, wynik pisze do
  nowego pliku.
