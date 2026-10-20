# TEST_PL v5 — polskie litery dopasowane do oryginalnego fontu

W zrzutach v4 widać działające polskie napisy, ale litery z Roboto są pełniejsze,
a korpusy części małych liter niższe od znaków gry. **V5 nie używa już Roboto.**

Podczas budowy kopiuje oryginalne `a/c/e/l/n/o/s/z` (i wielkie odpowiedniki) z Twojego
fontu i dodaje tylko ogonki, kreski oraz kropki. Korpusy zachowują oryginalne piksele,
wysokość, położenie i krycie. Nie są skalowane ani pogrubiane. Font i pochodne bitmapy
nie są dołączone do paczki — bazę pobiera ona z Twojego własnego ISO.

## Jak sprawdzić — ten sam tekst co w v4

1. Rozpakuj **cały ZIP do nowego folderu**. Uruchom **`TEST_PL.bat`** i wybierz
   swoje **oryginalne ISO SRW OE 1.08**, nie wynik poprzedniego patchowania.
2. Otwórz nowe **`output\patched.iso`** w PPSSPP od zimnego startu i wybierz
   **New Game**. Nie wczytuj save state i nie kasuj zwykłych zapisów.
3. Wystarczy screenshot pierwszej planszy **`PL V5`** lub pierwszego dialogu:

```text
(Łączność działa. Słychać mnie wyraźnie?
Chcę dziś dokończyć próbę osłony.)
```

Porównaj grubość i wysokość **ą/ę/ć/ś/ń/ó/ł** ze zwykłymi literami obok nich.
Na kolejnej planszy pozostają wielkie litery i `Zażółć gęślą jaźń`.
Naturalne zdania z v4 są bez zmian; zmieniły się tylko glify i etykiety wersji.
Nie trzeba szukać niczego w menu ani dochodzić do listy broni. To nadal wymyślone
próbki techniczne, **nie tłumaczenie japońskiego scenariusza**.

## Co kontroluje automat

Po budowie narzędzie czyta wynikowe ISO i tworzy **`output\PL_VERIFY.json`**:

- 18 fizycznych komórek fontu i dokładne zachowanie korpusów poza maską diakrytyku;
- oryginalne krycie oraz niezmienione litery ASCII i pozostałe człony fontu;
- 16 wpisów początku misji, pole tytułu i 19 prób nazw jednostek/broni.

W razie błędu nie zgłasza gotowego testu. Kontrola plików i lokalny podgląd bitmap
przeszły; **v5 nie uruchomiono tutaj w PPSSPP**. Zrzuty właściciela potwierdzają
wcześniejsze v4, nie nowy wygląd v5.

Zmienia tylko `font.cpk`, `eventP00.cpk` i `config00.cpk`. Nie wymaga DLC,
nie zmienia EBOOT, tekstur ani zapisów. Oryginalne ISO pozostaje nietknięte.
Wymagany Python 3; Pillow ani inne biblioteki graficzne nie są potrzebne.
Pakiet nie zawiera plików gry. W razie błędu budowy prześlij komunikat oraz
`build_report.json` lub `PL_VERIFY.json` — nie rób kolejnych prób w ciemno.
