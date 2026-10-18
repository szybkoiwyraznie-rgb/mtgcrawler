# TEST_PL v3 — wszystkie litery od razu na początku misji 0-0

To mały test techniczny, nie pełne tłumaczenie. **Naprawia błędny indeks glifów
z v2:** silnik odczytuje katakanę z komórki `bajt − 0x40`, nie `bajt − 0x20`.
Ustalono to z instrukcji programu gry; wygląd w PPSSPP wymaga jeszcze potwierdzenia.

## Tylko trzy kroki

1. Rozpakuj **cały ZIP do nowego folderu** i uruchom **`TEST_PL.bat`**.
   Wybierz swoje **oryginalne ISO SRW OE 1.08**, nie wynik poprzedniego testu.
2. Otwórz nowe **`output\patched.iso`** w PPSSPP, od zimnego startu, i wybierz
   **New Game**. Nie wczytuj save state. Nie kasuj zwykłych zapisów gry.
3. Zrób screenshot **pierwszej planszy `PL V3 / 1 - FONT CHECK`**, na samym
   początku misji 0-0, i prześlij go. Nie musisz szukać niczego w menu.

Na tej jednej planszy są jednocześnie:

```text
PL V3 / 1 - FONT CHECK
A: acelnoszz ACELNOSZZ
P: ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ
G: |aąa|cćc|eęe|lłl|
```

Pozwala to ocenić wszystkie **18 liter**, małe/wielkie znaki, linię bazową,
porównanie z ASCII i odstępy. Zwykłe litery ASCII mają zostać zwykłymi literami,
nie blokami. Kolejna plansza `PL V3 / 2` zawiera dodatkowe porównanie szerokości;
jeśli łatwo ją pokazać, można dosłać drugi screenshot — **to ten sam build**.
Napisy późniejszych dialogów i nazwy Exarta/broni też zawierają próby, ale nie
trzeba do nich dochodzić, żeby ocenić podstawowy wynik.

## Co jest sprawdzane automatycznie

Po budowie skrypt ponownie czyta wynikowe ISO i tworzy **`output\PL_VERIFY.json`**:
18 glifów w fizycznych komórkach czytanych przez silnik, zachowanie pozostałych
komórek/fontów, 16 wpisów początku misji, pole tytułu i obecność 19 prób nazw
jednostek/broni. W razie błędu nie zgłasza gotowego testu. To kontrola plików,
nie symulacja renderowania w emulatorze.

Zmienia tylko `font.cpk`, `eventP00.cpk` i `config00.cpk`. Nie wymaga DLC i nie
zmienia EBOOT, tekstur ani zapisów. Oryginalne ISO pozostaje nietknięte.
Wymagany Python 3; dodatkowe biblioteki graficzne nie są potrzebne.

Jeśli budowa się nie uda, prześlij komunikat błędu oraz dostępny `build_report.json`
lub `PL_VERIFY.json`, zamiast uruchamiać kolejne próby. Pakiet nie zawiera plików gry.
