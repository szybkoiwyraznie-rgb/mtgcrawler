# SRW OE — sprawdzone widoki PL, wydanie 2 (2026-10-18)

Do pracy służą **oba archiwa razem**: `sceny_PL_sprawdzone_v2.zip` i
`widoki_PL_sprawdzone_v2.zip`. Zastępują wcześniejsze `sceny_PL.zip` / `widoki_PL.zip`.
To pliki Markdown do tłumaczenia, nie patch ani gotowy polski przekład.

## Gdzie wpisywać tłumaczenie

- Zmieniaj **wyłącznie zawartość bloków `PL:`**. Pozostaw nazwy plików, numerację,
  JP, referencyjne `EN:`, `limit:`, `tokeny:` i komentarz kontrolny na początku pliku.
- Tłumacz z japońskiego, naturalną polszczyzną, uwzględniając kontekst sceny i mówcę.
  EN pomaga w interpretacji i spójności nazw; nie jest obowiązkiem kalkowania zdań.
- Kolejne linie przekładu wcięte są trzema spacjami, tak jak kolejne linie JP/EN:

  ```text
  1. [Dialog] tekst japoński
     limit: ...
     EN: English reference.
     PL: Pierwsza linia.
     Druga linia.
  ```

- Nie dopisuj drugiego `PL:` do tego samego elementu. Nie umieszczaj komentarzy,
  uzasadnień ani znaczników Markdown w przekładzie — trafiłyby do gry.
- Element **bez bloku `PL:`** jest kopią, wspólnym tytułem, pustym polem lub chronionym znacznikiem
  (`NoData` / literał silnika). Nic tam nie dopisuj; dziedziczenie wykonują narzędzia, nie tłumacz.
- `spis-scen.md`, nagłówki, uczestnicy i miejsca nad sceną są kontekstem/nawigacją.
  Tłumaczone miejsce ma własny numerowany element.
- Ten sam element może wystąpić w scenie i w tabeli misji. Wypełnij go w jednym
  miejscu, a drugie zostaw puste; jeżeli wypełnisz oba, teksty muszą być identyczne.
- Zapisuj jako **UTF-8**. Oddawaj te same pliki MD, także partiami/epizodami.

## Znaki: liczba liter, szerokość i bajty to nie zawsze to samo

- `ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż` oraz ASCII zajmują **1 celę szerokości
  i 1 bajt zapisu gry**. Dotyczy aktualnego jednobajtowego fontu PL, także v5.
  Nie licz bajtów UTF-8 pliku MD — to inne kodowanie niż wewnątrz gry.
- `…`, `“ ”`, `‘ ’`, `∞` i inne dwubajtowe znaki CP932 zajmują **2 cele i 2 bajty**.
  `...` to 3 cele/3 bajty. Spacje i interpunkcja również zużywają budżet.
- Używaj zwykłych `-`, `"`, `'`. Nie używaj `„`, `–`, `—`, emoji ani obcych
  diakrytyków typu `é`, `ü`, `ā`; aktualny kodek ich nie obsługuje.
- Nie kopiuj półszerokiej katakany (`ｱ`, `ｶ` itd.) do PL — jej zakres bajtów jest
  zarezerwowany dla fontu PL. Japońskie zmienne/kolory pozostają wyjątkami poniżej.

## Jak czytać `limit:` przy KAŻDYM elemencie

- **`maks. N B tekstu`** to twardy budżet całego pola w kodowaniu gry, bez końcowego
  NUL. Podziały linii i zakodowane kontrolki również zajmują bajty.
- **`N celi na linię`** to szerokość każdej linii osobno, a nie całego akapitu.
  Celuj w 46; granica walidatora zależy od rodzaju tekstu: dialog 52, cytat bitewny
  50, pomoc 66, miejsce 48; pozostałe wartości są podane przy elemencie.
  Narracja ma zalecenie 56 celi, nie dowód, że dowolny akapit zmieści się na ekranie.
- Dla nazw obowiązują JEDNOCZEŚNIE zapis i ekran: np. nazwa jednostki ma pole
  31 B, ale kolumna listy mieści **14 celi**. Krótkie/wąskie imię pilota:
  zalecane 14 celi; pole wąskiego imienia maks. 19 B.
- **`zalecane` / `zalecana długość`** oznacza ostrzeżenie, nie twardą granicę.
- **`pole przebudowywane; brak zmierzonego limitu UI`** NIE oznacza dowolnej długości
  na ekranie. Pisz zwięźle, blisko proporcji oryginału. Sama poprawność bajtów nie
  dowodzi, że każdy ekran poprawnie ułoży dłuższy tekst.

## Linie, kontrolki i tokeny

- Zachowuj liczbę podziałów linii i układ JP. `⏎` oznacza **CR / czyszczenie okna**,
  nie zwykły Enter. Zachowuj je w odpowiedniej części tekstu. Zwykły Enter w MD
  oznacza LF. Importer uzupełnia niewidoczne końcowe CR/LF według oryginału.
- `%s`, `%d`, `%02d`, `＠0`…`＠9`, `％…`, `＄…`, `＃`, `{XX}`,
  `＜主人公名＞`, `＜主人公姓＞` mogą być danymi/sterowaniem gry. Nie tłumacz ich.
  Wiersz **`tokeny: zachowaj kolejność i liczbę: [...]`** wylicza wymagane tokeny.
  `%%` to dosłowny procent; może przesunąć się wraz z liczbą.
- Wyjątek: część japońskich `%s` NIE jest zmienną, tylko zapisem znaku kana.
  `tokeny: usuń znaczniki japońskich głosek: [...]` wskazuje dokładne pary do usunięcia
  z PL, np. `%s*`. Nie przenoś ich do polskiego słowa. Reguła pochodzi z `tokeny.tsv`,
  nie ze zgadywania po wyglądzie `%s`.
- **`<0x0F>` wraz z bajtem dopełniającym japoński znak nie zostaje w PL.**
  To część znaku kana, a nie uniwersalny znacznik, który trzeba przepisać.
- Długość tekstu wstawionego przez `%s` / zmienne imienia zależy od gry; statyczny
  licznik nie gwarantuje braku kolizji po rozwinięciu każdej zmiennej.

## Pliki specjalne i zakres

- `program.md` (dodany w tym wydaniu): teksty programu/EBOOT, osobne limity bajtów
  i printf. **Nie używaj polskich liter** — ta ścieżka nie ma zweryfikowanego fontu PL.
  Dla tłumaczeń zalecane ASCII (`Wez`, nie `Weź`). JP/EN mogą pokazywać znaki
  w CP932 lub UTF-8; sam zapis UTF-8 nie dowodzi obsługi polskiego fontu.
  Literały oznaczone `NIE TŁUMACZ` nie mają bloku PL i pozostają bez zmian.
- `teren.md` (dodany): **wyłącznie ASCII, maks. 12 znaków/celi**.
- `06_scenes` to indeks, nie dodatkowy tekst do tłumaczenia.
- Odłożono 364 nierozpoznane `leftover:` — niepotwierdzone napisy / artefakty
  dekodowania. Zachowano 8 takich źródeł, z których dziedziczą rzeczywiste pola
  katalogu jednostek; nie wolno było usunąć ich razem z resztą. `NoData`, puste pola
  i literały silnika są tylko do odczytu. Pozostałe kategorie bazowego `pakiet_EN`
  mają pokrycie sprawdzane automatycznie.
  To nie jest twierdzenie, że ekstrakcja obejmuje każdą teksturę czy wszystkie
  niewyodrębnione napisy całej gry.

## Kontrola i późniejszy patch — dla osoby integrującej

Użyj narzędzi z audytu z 2026-10-18 lub nowszych, **nie starego patchera v1**.
Obie paczki mają ten sam odcisk bazowego pakietu; nie łącz ich z inną wersją JSONL.

```text
python tools/pl_package_build.py --package pakiet_EN --out local/pakiet_PL
python tools/translation_import.py --package local/pakiet_PL --views sceny_PL_sprawdzone_v2.zip widoki_PL_sprawdzone_v2.zip --lang pl --require-template --check
python tools/translation_import.py --package local/pakiet_PL --views sceny_PL_sprawdzone_v2.zip widoki_PL_sprawdzone_v2.zip --lang pl --require-template
python tools/translation_check.py --package local/pakiet_PL --field pl --strict
python tools/build_translation_patch.py --iso TWOJA_GRA.iso --package local/pakiet_PL --out local/patch_PL --lang pl
```

Import PL sprawdza pełny JP i odcisk źródła, kodowanie, tokeny, linie, limity oraz
jawne kopie. Błąd, nieznany element albo podwójny blok = kod wyjścia 1 i **brak zapisu
całej partii**. `--check` niczego nie zapisuje. Puste bloki nie kasują wcześniejszej pracy.
Kopie PL aktualizują się automatycznie bez zmieniania referencyjnego EN. Nie uruchamiaj
heurystycznego mirrorowania nazw bez osobnej kontroli konfliktów.

Po poprawnym imporcie pusty PL nadal oznacza „nie przetłumaczono” — nie automatyczny
angielski zamiennik. Budowanie i testy w grze są osobnym etapem: kontrola offline nie
zastępuje przeglądu układu ekranów ani oceny wyglądu fontu v5 w PPSSPP.
