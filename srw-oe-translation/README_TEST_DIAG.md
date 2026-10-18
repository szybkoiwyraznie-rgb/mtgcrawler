# TEST_DIAG — diagnostyka liter w grze (SRW OE)

Nie do grania normalnie. Cel: ustalić, skąd gra czyta katakany.

## Co zrobić
1. Rozpakuj cały pakiet obok **oryginalnego** ISO SRW OE 1.08 (nie `patched.iso`).
2. Uruchom `TEST_DIAG.bat` (dwuklik). Wybierz ISO w oknie.
3. Powstanie `output\diag.iso`.
4. W PPSSPP: załaduj `diag.iso`, nowa gra, zimny start.
5. Wejdź w misję 0-0 i zrób zrzut ekranu z tekstem (F12 w PPSSPP — [NIEZWERYFIKOWANE]).

## Co sprawdzam na zrzucie
- Litera `e` w napisach angielskich: czy jest czarnym blokiem?
- Katakany (np. japońskie napisy UI): czy są blokami, czy wyglądają jak dotąd?

Wynik: `e` blok + katakany bez zmian → gra czyta katakany z innej tablicy.
Katakany blokami → zapis działa, błąd w poprzednim pakiecie.
Brak zmian → gra nie czyta tego font.cpk.
