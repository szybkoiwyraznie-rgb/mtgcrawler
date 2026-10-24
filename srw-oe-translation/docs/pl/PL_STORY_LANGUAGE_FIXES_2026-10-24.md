# Korekta językowa fabuły PL od epizodu 3 (2026-10-24)

Dokument rejestruje kolejne przeglądy epizodów wykonywane po audycie 0–2. Każdy epizod jest skanowany w kolejności scen, a potwierdzone problemy są od razu poprawiane osobnym, źródłowo powiązanym planem `config/pl/story-language-epNN-2026-10-24.json`. Plik planu jest autorytatywną listą dokładnych zmian „przed/po”; ten dokument opisuje zakres, klasy ustaleń i walidację.

## Metoda

Dla każdego epizodu sprawdzane są:

- pełny tekst scen fabularnych i wypowiedzi warunkowych;
- wszystkie grupy z pytaniem oraz poprzedzającą i dwiema kolejnymi kwestiami;
- kandydatury z kontrolowanych skanów leksykalnych: tagi pytajne, nominalizacje, kalki, formy zwracania się, zaimki otwierające, niespójności interpunkcji między JP/EN/PL oraz odpowiedzi `tak/nie`;
- zgodność każdej podejrzanej kwestii z JP, EN i kontekstem sceny.

Plan jest następnie nakładany narzędziem `tools/pl_story_corrections.py`, cały pakiet PL jest materializowany od zera, wszystkie teksty z planu są asertywnie porównywane z materializacją, a testy `test_pl_story_corrections` i `test_pl_v4_0_consistency` muszą przejść przed commitem.

## Epizod 3

- **Zakres:** 994 wpisy — 731 fabularnych i 263 warunkowe; 238 grup z pytaniami (179 fabularnych, 59 warunkowych).
- **Poprawki:** 30 kwestii wskazanych w przeglądzie; plan zawiera 33 zmiany źródłowe po dołączeniu jawnych kopii `copy_of`.
- **Potwierdzone klasy błędów:** odwrotna odpowiedź („Ani trochę” zamiast potwierdzenia), niezrozumiała komparacja przeciwników, niepełny wniosek celowy, rozjechana rola syndykatu finansującego piratów, fałszywe znaczenie alarmu, kalki „wygodne” i „przekrój czasoprzestrzeni”, błędny szyk wiązki naprowadzającej, niepoprawny zwrot „rozwoju” oddziału oraz kilka oderwanych/refleksyjnych tagów i sztywnych konstrukcji sprawozdawczych.
- **Świadomie zachowane fałszywe alarmy:** komediowe `MAX` Keroro, źródłowe `ludzie typu pekopońskiego`, dosłownie obecny w JP `układ Frontier` oraz tagi pytajne rzeczywiście skierowane do rozmówcy.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `fffa694322f42aeeb7652a9a70305fea3332d1ce81b9d096eceb83b7ae7a1bc1` → `fda6c27086af862b315cf50cd7f6a23d0298eb889554fc98596ac4ddc399e6c1`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 4

- **Zakres:** 660 wpisów — 560 fabularnych i 100 warunkowych; 135 grup z pytaniami (114 fabularnych, 21 warunkowych).
- **Poprawki:** 30 kwestii wskazanych w przeglądzie; plan zawiera 49 zmian źródłowych po dołączeniu jawnych kopii `copy_of`.
- **Potwierdzone klasy błędów:** błędny przypadek `zostawić mnie`, zdanie bez rzeczownika `pytanie`, niepełny dopełniacz ładunku bramy, sztuczne `zgubiliśmy pościg`, rozbity warunek `nie tylko walki`, zbędny tag w kanonicznym `Kręcimy się w kółko, prawda?`, odwrócona składnia Killy’ego, `z rebeliantów`, narzędnik Macross Cannona oraz narracyjne `zapłaciła czystką`.
- **Uwaga walidacyjna:** pierwsza próba zastosowania planu została poprawnie odrzucona przez limit szerokości dialogu (linia 53 przy limicie 52); po skróceniu frazy o zwiadowcach cała ścieżka przeszła.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `fda6c27086af862b315cf50cd7f6a23d0298eb889554fc98596ac4ddc399e6c1` → `b3671f043b3203f9d45011bd8ee6cfa9867a430699466cdea4b9cbaf163097e9`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 5

- **Zakres:** 1 257 wpisów — 1 095 fabularnych i 162 warunkowe; 284 grupy z pytaniami (251 fabularnych, 33 warunkowe).
- **Poprawki:** 48 kwestii wskazanych w przeglądzie; żadna nie wymagała jawnej kopii `copy_of`, więc plan zawiera 48 zmian źródłowych.
- **Potwierdzone klasy błędów:** twarda gramatyka (`Jestem major`, `pracę umysłową zostawcie mnie`), odwrócona biegunowość potwierdzenia Monskara, błędna agencja przy przedstawianiu mieszkańców wioski, podmiot głos w `Leci tutaj?`, niejednoznaczne `posiłki` zamiast drugiej fali, sprzeczność `wytępić i zagnać pod ziemię`, dziewczyna nazwana `pułapką` zamiast przynęty oraz rządy i nominalizacje przy zabezpieczaniu odwrotu, płatności, liczeniu klientom i wyszukiwaniu śladów DG.
- **Świadomie zachowane fałszywe alarmy:** `dyrektor Douglas` (Suol Douglas), `Pan Lordgenome` jako forma czci Virala, poprawne powiedzenie `pozostawianie Chirico samemu sobie`, bezpośrednie tagi pytajne oraz formy grzecznościowe Suzaku wynikające z japońskich form uprzejmych.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `b3671f043b3203f9d45011bd8ee6cfa9867a430699466cdea4b9cbaf163097e9` → `6464d12792574e213d31b636b01b58a326995de5bda1e18de40d0d2ff1dc96d8`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.
