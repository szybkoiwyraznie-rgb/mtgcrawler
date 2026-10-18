# Polskie litery: plan zmiany fontu (checkpoint 2026-10-18)

**Najnowsze v5 (2026-10-18):** v4 potwierdzony w grze, ale właściciel zgłosił
zbyt grube i nieco za niskie polskie litery. [V5](https://drive.google.com/file/d/13tWWoHO6nBSmEVGFj4y46BtDIV2kz3uD/view)
kopiuje oryginalne korpusy ASCII i dodaje tylko maski diakrytyków; nie rasteruje
Roboto i nie przechowuje bitmap gry w repo/kit. [Styl i dowody](PL_FONT_STYLE.md),
[manifest](test-v5-delivery.json). 1569 unittest OK (25 skipped), isolated kit
read-back + niezależny audyt natywnych korpusów OK; **runtime v5 niepotwierdzony**.
Dalsze sekcje są historią.

**Najnowsze (2026-10-18):** właściciel przesłał dwa zrzuty v3 i ocenił wygląd
pozytywnie. Na jego prośbę [v4](https://drive.google.com/file/d/1ic0N5bx0PMF_3xnu2ZWhlG0e3nOQRc-U/view)
zawiera naturalne próbki w pierwszym dialogu, bez zmiany fontu/kodeka.
[Manifest](test-v4-delivery.json); 1558 unittest OK (25 skipped), offline read-back
wydanego ZIP sprawdzony. V4 nie jest tłumaczeniem i nie ma jeszcze potwierdzenia
runtime; poprzednie v3 ma potwierdzenie otwierającej sceny. Dalsze sekcje są historią.

**Aktualizacja po PR #19 (2026-10-18, PR #20):** naprawiono dwie przyczyny:
indeks katakany to `bajt − 0x40`, a lewy piksel jest w młodszym nibblu bajtu.
[Dowody i granice](PL_FONT_MAPPING.md), [manifest TEST_PL v3](test-v3-delivery.json).
[V3 na Drive](https://drive.google.com/file/d/16mPAOMpab8aSFbuqv1LSxMWyStEQmn_K/view)
ma wszystkie 18 liter + ASCII + odstępy na pierwszej planszy misji 0-0;
automatyczny odczyt ISO po budowie. 1553 testy OK (25 skipped), offline/extracted-kit
sprawdzone; **potwierdzenie obrazu w PPSSPP nadal oczekiwane**. Poniżej historia.

Status historyczny (2026-10-18, po commicie 8497268): implementacja gotowa, testy jednostkowe 1535 OK.
Pakiet testowy **srw-oe-test-pl-v2.zip** na Dysku (`1GheEOtFzQm4pHv_VlOJqfs0hsFdiEazi`).
**Nic nie jest jeszcze potwierdzone w grze** - czeka na test PPSSPP właściciela.

## Wynik testu v1 (zrzuty właściciela)
- Gra się uruchamia, brak crasha.
- Polskie litery mają szerokość dwóch liter ASCII (dwubajtowy kod -> komórka 14 px).
- Znaki diakrytyczne są przypadkowymi plamkami (ręcznie dorysowane 3-4 px, stałe pozycje).
  [ZWERYFIKOWANE na zrzutach]

## Decyzja
1. Każda z 18 liter PL = **jeden bajt** z zakresu półszerokich katakan 0xA1-0xDF
   (szerokość 1 jednostki, jak ASCII).
2. Przydział (najmniej używane w pakiecie JP, bez 0xDE/0xDF (znaki łączące) i 0xA1-0xA5 (interpunkcja)):
   D5 DB D0 D8 D6 D1 D3 D9 DA D2 D7 B2 A7 CA AC B8 CE AE
   [ZWERYFIKOWANE: w pakiecie EN 0 wystąpień tych bajtów poza katakaną JP;
   katakana w EN nieużywana w ogóle]
3. Glify w `ank.fta` (8x14, 4 bpp) rasteryzowane z Roboto Medium ~11-12 px
   (`assets/fonts/Roboto-Medium.ttf`) zamiast ręcznych plamek. [HIPOTEZA do testu w grze]
4. Szerokość w budżetach PL = 1 jednostka na literę (jak ASCII). [HIPOTEZA do testu w grze]

## Ryzyka
- Każdy wiersz pakietu PL musi być przetłumaczony, inaczej zostanie japońska katakana
  wyświetlona jako polska litera. Pakiet PL nie może zostawiać JP (walidator).
- Katakana w `ank.fta` może być używana poza tekstem pakietu (grafika/ikony) - do sprawdzenia w grze.

## Wykonane (2026-10-18)
- `tools/font_pl.py`: zapis 18 glifów do `ank.fta` pod bajty PL_BYTES (kanji nietknięte).
- `tools/data/pl_glyphs_8x14.json`: glify wygenerowane przez `tools/make_pl_glyphs.py`
  (Roboto Medium, linia bazowa jak w grze, wysokość wielkich liter jak 'H' w grze).
- `tools/pl_text.py`: kodek jednobajtowy; half-width katakana w tekście PL = błąd.
- `tests/`: 1535 OK. Pakiet testowy v2 sprawdzony `translation_check --field pl`: 0 błędów.
- Dokumentacja tłumacza (`docs/translator_pl/INSTRUKCJA_PL.md` §2, §2a, §4): szerokość 1.
- Nieprzetestowane w grze: kształty ł/Ż i szerokość (hipoteza), walidacja w PPSSPP.

## Wynik testu v2 (2026-10-18, zrzuty właściciela) - BŁĘDNE ZAŁOŻENIE
- Nowy `patched.iso` nie pokazuje polskich liter: w grze bajty katakany (0xA1-0xDF) rysują się
  **oryginalnymi katakanami** (np. Ó=0xAC pokazuje się jako katakana, a nie jako litera PL).
  [ZWERYFIKOWANE na zrzutach]
- Założenie „bajt katakany = komórka `ank.fta` pod indeksem bajt-0x20” NIE zostało potwierdzone
  i wygląda na błędne lub niekompletne. Przesłanki:
  - w oryginalnym `ank.fta` komórki pod bajtami katakany mają tusz (57 z 63), więc gra mogłaby
    czytać je stamtąd, ale nadpisane komórki nie zmieniły wyglądu w grze;
  - komórka pod 0xDA (ż) jest w oryginale pusta, a w grze widać katakanę, więc glif nie pochodzi z tej komórki.
  [ZWERYFIKOWANE w pliku; przyczyna NIEZNANA]
- Hipotezy do sprawdzenia (w kolejności): (1) gra czyta katakany z innej tablicy (`kanji21`/`kanji22`
  albo inny indeks); (2) patched.iso nie zawiera zmienionego `font.cpk` (sprawdzić md5 w ISO
  względem `local/font_pl.cpk`); (3) silnik ma cache/kopię fontu.
- Następny krok: `build_report.json` z `output\` oraz diagnostyczny test (solidny blok w ASCII 'Q'
  i w katakanie 0xD5), żeby rozdzielić (1) i (2).

## Wynik testu diagnostycznego (2026-10-18, zrzut właściciela) [ZWERYFIKOWANE ze zrzutu]
- W misji 0-0 litera ASCII `e` w nazwach (np. „Seishiro”, nazwa jednostki u góry ekranu) jest pełnym
  czarnym blokiem. Zmiana w `ank.fta` działa dla ASCII.
- Katakany NIE sprawdzone: w misji 0-0 nie ma napisów z katakaną. Wynik dla katakany pozostaje
  nierozstrzygnięty; potrzebny ekran z katakaną (np. japońskie napisy UI).
- Pakiet diagnostyczny v2 (`srw-oe-test-diag-v2.zip`) zawiera pełne `tools/` i `TEST_DIAG.bat`
  z wyborem ISO (commit 8cad3e3). Poprzedni v1 był złożony ręcznie i nie działał.
