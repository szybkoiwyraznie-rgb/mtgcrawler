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
