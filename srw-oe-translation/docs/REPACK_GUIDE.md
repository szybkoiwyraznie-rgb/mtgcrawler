# REPACK — instrukcja krok po kroku (na Twoim PC, po polsku)

Cel: zbudować z rozpakowanego drzewa dysku (`SRW_OE_1.08`) nowy obraz ISO, który PPSSPP
uruchomi — najpierw **bez zmian** (test, że repack w ogóle działa), potem **z podmienionym
plikiem** (test, że Twoja zmiana trafia do gry).

Czego potrzebujesz na dysku:
- oryginał: `SRW OE 1.08.iso`,
- rozpakowane drzewo: katalog `SRW_OE_1.08` (z `PSP_GAME/...` w środku),
- świeże repo (gałąź `arena/c656a5df-mtgcrawler`) — są w nim `REPACK_ISO.bat` i `tools/iso_pack.py`,
- Python w PATH (masz go — uruchamiasz nim pipeline).

## KROK 1 — test tożsamości (bez patchy)

To sprawdza, czy spakowany obraz w ogóle startuje. **Nie pomijaj go.**

1. Otwój wiersz poleceń w katalogu repo (`srw-oe-translation`). **Najpewniej użyj Pythona
   wprost** (działa w PowerShell i w cmd, bez pułapek cytowania):

   ```
   python tools\iso_pack.py repack "D:\SRWOE\SRW_OE_1.08" "D:\SRWOE\repacked.iso" "D:\SRWOE\SRW OE 1.08.iso"
   ```

   - arg1 = rozpakowane drzewo, arg2 = nowy obraz, arg3 = oryginalne ISO (skrypt sam weźmie
     z niego pierwsze 32 KiB — region bootowy). Brak arg4 = brak patchy.
   - Jeśli wolisz `.bat`: w **PowerShell** wywołaj go przez operator `&`
     (`& .\REPACK_ISO.bat "..." "..." "..."`) albo uruchom w **cmd**. Samo
     `".\REPACK_ISO.bat" ...` w PowerShell daje błąd „Unexpected token" — to pułapka powłoki,
     nie skryptu.
3. Poczekaj (kilkadziesiąt sekund; nie trzyma 660 MB w RAM).
4. Podmień w PPSSPP oryginalne ISO na `repacked.iso` i uruchom.
5. **Oczekiwany wynik:** gra startuje i zachowuje się identycznie jak oryginał.
   Jeśli się wysypie — nie przechodź dalej, tylko wyślij mi objawy; to znaczy, że writer ISO
   wymaga poprawki (to jedyny nieprzetestowany na prawdziwym dysku element).

## KROK 2 — test z podmianą

1. Zrób katalog patchy, np. `D:\...\patch`, i odtwórz w nim ścieżkę względem drzewa:
   `D:\...\patch\PSP_GAME\USRDIR\eventP00.cpk` — to Twój zmodyfikowany plik
   (np. z nałożonym tłumaczeniem; na razie możesz użyć pliku testowego).
2. Uruchom (4. argument = katalog patchy; każdy plik w nim nadpisuje odpowiadający mu plik
   drzewa):

   ```
   python tools\iso_pack.py repack "D:\SRWOE\SRW_OE_1.08" "D:\SRWOE\repacked.iso" "D:\SRWOE\SRW OE 1.08.iso" "D:\SRWOE\patch"
   ```
3. Uruchom `repacked.iso` w PPSSPP i sprawdź, czy zmiana jest widoczna.

## Uwagi

- Rozdziały 2–8 (DLC) **nie potrzebują repacku** — PPSSPP czyta je luzem z
  `memstick/PSP/GAME/NPJH50521`; wystarczy podmienić pojedynczy `.EDAT`.
- Repack służy tylko do rozdziału 1 (dysk) i do walidacji procesu.
- Narzędzie nigdy nie dotyka oryginału — czyta drzewo i ISO tylko do odczytu, wynik pisze do
  nowego pliku.
