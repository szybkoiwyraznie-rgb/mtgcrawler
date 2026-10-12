# REPACK — instrukcja krok po kroku (na Twoim PC, po polsku)

Cel: zbudować nowy obraz ISO, który PPSSPP
uruchomi — najpierw **bez zmian** (test, że repack w ogóle działa), potem **z podmienionym
plikiem** (test, że Twoja zmiana trafia do gry).

Czego potrzebujesz na dysku:
- oryginał: `SRW OE 1.08.iso`,
- rozpakowane drzewo: katalog `SRW_OE_1.08` (z `PSP_GAME/...` w środku),
- świeże repo (gałąź sesji, dziś `arena/51f7d5fe-mtgcrawler`) — są w nim `REPACK_ISO.bat`, `PATCH_ISO_TEST.bat` i `tools/iso_pack.py`,
- Python w PATH (masz go — uruchamiasz nim pipeline).

## WAŻNE: Twoja ekstrakcja `SRW_OE_1.08` jest NIEPEŁNA

Prawdziwy dysk ma ~672 MB danych (80 plików), a katalog rozpakowany waży ~293 MB — narzędzie
rozpakowujące **pominęło duże pliki** (`BgmSet00.awb`, `UPDATE/DATA.BIN`, `bacb00.cpk`,
`lmap.cpk`, `voice00.awb`, `mov00.cpk`, `robo00.cpk`…). Dlatego repack z drzewa dał ~300 MB i
byłby okrojony. **Używaj metody `repackiso`**, która czyta niezmienione pliki wprost z
oryginalnego ISO — nic nie może zginąć, a drzewo w ogóle nie jest potrzebne.

## KROK 0 (najprościej) — jeden plik: `PATCH_ISO_TEST.bat`

Ten bat robi **cały** test wtrysku fabuły: bierze Twoje ISO, wyciąga z niego kontener zdarzeń,
wpisuje 6 angielskich linii prologu i zapisuje **nowe** ISO obok. Nic nie trzeba pobierać ani
rozpakowywać osobno — wystarczy całe repo i Twoje ISO.

1. Uruchom `PATCH_ISO_TEST.bat` (albo przeciągnij na niego plik ISO).
2. Podaj ścieżkę do swojej kopii ISO 1.08 (albo połóż ją jako `SRW_OE.iso` w katalogu repo —
   wtedy bat znajdzie ją sam).
3. Bat wypisze, ile linii wpisał, pokaże **wymienione linie** (japoński → angielski) i poda
   ścieżkę nowego ISO `SRW_OE-test.iso`.
4. Uruchom nowe ISO w PPSSPP, nowa gra, prolog (odcinek 1).

Zasady bezpieczeństwa, które ten bat sam pilnuje:
- Twój oryginał jest tylko **czytany** — bat nigdy nie zmienia pliku wejściowego.
- Kontener i scenka muszą zgadzać się skrótem MD5 z tym, na czym mierzyłem offsety; inna wersja
  gry **zatrzymuje** pracę z komunikatem, zamiast cicho zepsuć plik.
- Po zmianie liczy się od nowa, czy zmienił się **tylko** jeden członek (scenka z prologiem);
  gdyby ruszyło się cokolwiek więcej, wynik nie jest zapisywany.
- `--dry-run` (dopisz na końcu wywołania `python tools/iso_test_patch.py`) sprawdza wszystko,
  ale nic nie zapisuje.

Kontener zdarzeń i japoński tekst **nie leżą w repozytorium** — repo trzyma tylko offsety, skróty
MD5 i nasze angielskie linie (`test-patches/eventP00-scena1.json`). Japoński tekst jest czytany z
Twojego ISO i pokazywany na ekranie, nigdzie nie jest zapisywany.

## KROK 0 — metoda: `patchiso` (zalecana)

Zamiast przebudowywać ISO od zera (`repackiso`), używaj **`patchiso`**:
kopiuje oryginał bajt-w-bajt i zmienia TYLKO rekord katalogowy + dopisuje podmieniony plik na
końcu. Cała struktura UMD/ISO9660 oryginału zostaje nietknięta, więc obraz bootuje jak źródło.
`repackiso` (przebudowa) okazał się niewystarczający dla prawdziwego UMD (crash w PPSSPP).

## KROK 1 — test tożsamości (patch identyczny)

To sprawdza, czy spakowany obraz w ogóle startuje. **Nie pomijaj go.**

1. Otwórz wiersz poleceń w katalogu repo (`srw-oe-translation`). Użyj Pythona wprost (działa
   w PowerShell i w cmd):

   1. Zrób katalog patchy i skopiuj doń ORYGINALNY `eventP00.cpk` (patch identyczny):
      `D:\SRWOE\patch\PSP_GAME\USRDIR\eventP00.cpk`.
   2. Uruchom:
   ```
   python tools\iso_pack.py patchiso "D:\SRWOE\SRW OE 1.08.iso" "D:\SRWOE\repacked.iso" "D:\SRWOE\patch"
   ```
   - arg1 = oryginalne ISO, arg2 = nowy obraz, arg3 = katalog patchy.
   - Ma powstać obraz ~tej samej wielkości co oryginał (+kilka KB) i bootować identycznie.
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
   python tools\iso_pack.py patchiso "D:\SRWOE\SRW OE 1.08.iso" "D:\SRWOE\repacked.iso" "D:\SRWOE\patch"
   ```
3. Uruchom `repacked.iso` w PPSSPP i sprawdź, czy zmiana jest widoczna.

## Uwagi

- Rozdziały 2–8 (DLC) **nie potrzebują repacku** — PPSSPP czyta je luzem z
  `memstick/PSP/GAME/NPJH50521`; wystarczy podmienić pojedynczy `.EDAT`.
- Repack służy tylko do rozdziału 1 (dysk) i do walidacji procesu.
- Narzędzie nigdy nie dotyka oryginału — czyta drzewo i ISO tylko do odczytu, wynik pisze do
  nowego pliku.
