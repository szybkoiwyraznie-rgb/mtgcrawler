# TEST_PL v4 — naturalne polskie zdania w pierwszym dialogu

**V3 działa w grze:** właściciel przesłał zrzuty pokazujące polskie litery i ocenił
wygląd pozytywnie. V4 **nie zmienia fontu ani kodeka**. Zamiast ciągów alfabetu
wstawia krótkie, naturalne zdania, żeby ocenić czytelność w normalnym tekście.
To wymyślone próbki techniczne, **nie tłumaczenie japońskiego scenariusza**.

## Jak uruchomić

1. Rozpakuj **cały ZIP do nowego folderu**. Uruchom **`TEST_PL.bat`** i wybierz
   swoje **oryginalne ISO SRW OE 1.08**, nie wynik poprzedniego patchowania.
2. Otwórz **`output\patched.iso`** w PPSSPP od zimnego startu i wybierz **New Game**.
   Nie wczytuj save state i nie kasuj zwykłych zapisów.
3. Wystarczy screenshot **pierwszego okna dialogowego**. Tekst zaczyna się tak:

```text
(Łączność działa. Słychać mnie wyraźnie?
Chcę dziś dokończyć próbę osłony.)
```

W tych dwóch liniach są m.in. wszystkie wskazane znaki **ł, ś, ć, ą, ę, ń**,
a także ź i ó. Kolejne kwestie sprawdzają m.in. ż oraz imię gracza:

```text
Łączność działa. Możemy zacząć.
Słyszę cię wyraźnie. Wszystko działa.
```

Naturalne zdania są również od razu na pierwszej planszy `PL V4`, przed dialogiem.
Druga plansza zachowuje komplet wielkich liter i pangram `Zażółć gęślą jaźń`.
Pozostałe plansze skrócono: nie trzeba już przewijać dwunastu powtarzanych ciągów
alfabetu. Nie trzeba szukać niczego w menu ani dochodzić do listy broni.

## Automatyczna kontrola

Po budowie narzędzie czyta wynikowe ISO i tworzy **`output\PL_VERIFY.json`**:
sprawdza 18 fizycznych komórek fontu, pozostałe glify/człony fontu, 16 wpisów
początku misji (w tym nowe zdania), pole tytułu i 19 prób nazw jednostek/broni.
W razie błędu nie zgłasza gotowego testu. To kontrola plików; w tym środowisku
nie uruchomiono v4 w PPSSPP.

Zmienia tylko `font.cpk`, `eventP00.cpk` i `config00.cpk`. Nie wymaga DLC,
nie zmienia EBOOT, tekstur ani zapisów. Oryginalne ISO pozostaje nietknięte.
Wymagany Python 3; dodatkowe biblioteki graficzne nie są potrzebne.
Pakiet nie zawiera plików gry. W razie błędu budowy prześlij komunikat oraz
dostępny `build_report.json` lub `PL_VERIFY.json` — nie rób kolejnych prób w ciemno.
