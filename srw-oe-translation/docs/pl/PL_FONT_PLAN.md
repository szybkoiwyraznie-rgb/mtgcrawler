# Polskie litery: plan zmiany fontu (checkpoint 2026-10-18)

Status (2026-10-18, po commicie 8497268): implementacja gotowa, testy jednostkowe 1535 OK.
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
