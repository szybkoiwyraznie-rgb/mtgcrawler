# Polskie litery: plan zmiany fontu (checkpoint 2026-10-18)

Status: **plan + w toku. Nic nie jest jeszcze potwierdzone w grze.**

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
