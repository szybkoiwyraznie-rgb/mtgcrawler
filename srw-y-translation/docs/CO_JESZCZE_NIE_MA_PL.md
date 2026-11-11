# Co jeszcze nie ma polskiego tekstu — i co da się domknąć bez tłumacza

Stan na wydanie **PL9** (`translations/current_release.json`). Wszystkie liczby
w tym dokumencie pochodzą z repozytorium i odtwarza je jedno polecenie:

```bash
python tools/deliver_remaining_text.py --check          # paczka dla tłumacza + transfer
python tools/rehearse_remaining_text.py --check         # próba generalna przez bramkę importu
```

Jeśli któryś `--check` zgłosi `ROZJAZD`, dane w repo są starsze niż narzędzia i
trzeba je przeliczyć (`--write`), a nie „poprawić” dokument.

## Dwie liczby, które trzeba rozróżniać

| co | ile | skąd |
| --- | ---: | --- |
| elementy wzorca v8 | 138 735 | sloty `PL:` we wzorcu |
| wiersze planu PL9 (wypełnione) | 85 610 | `PLAN_PL9.json` |
| elementy wzorca z wypełnionym `PL:` | 74 777 | wzorzec v8 |
| **elementy bez polskiego tekstu** | **61 810** | plan odjęty od wzorca po adresach wierszy |
| — w plikach, które wróciły w PL9 | 23 218 | tłumacz je ma i zostawił puste |
| — w plikach, które nie wróciły nigdy | 38 592 | 22 pliki wzorca poza zwrotką PL9 |
| w tym **do przeniesienia bez tłumacza** | **2 148** | identyczne zdanie japońskie, jedno brzmienie w planie |
| **do napisania przez tłumacza** | **59 662** | reszta |

`138 735` (sloty wzorca) i `61 810` (puste wiersze planu) **nie są tą samą
wielkością** i nie mogą się dodawać do 100 %: wzorzec ma elementy, które w planie
występują pod innym adresem albo są powtórzeniem dziedziczącym tekst, a plan ma
wiersze spoza wzorca (m.in. `odcinek-99-dodatek.md`). Dlatego narzędzia liczą
puste wiersze **po adresach wierszy w planie**, a nie po numerach elementów
wzorca, i dlatego `tools/translator_gap_report.py` (75 073 brakujące linie
scenariusza) podaje inną liczbę niż ten dokument (61 810 wierszy planu): pierwszy
liczy linie korpusu scen, drugi wiersze planu (sceny **i** tabele). Obie liczby są
poprawne, ale nie wolno ich mieszać w jednym zdaniu.

## Paczka dla tłumacza — `translations/pl-remaining/`

- `sceny/*.md` (29 plików) i to samo w `sceny.zip` — **tylko elementy bez
  polskiego tekstu**, z zachowaną numeracją, kluczami i `limit:` z wzorca v8.
  Tłumacz wraca te pliki tą samą drogą co poprzednie zwrotki
  (`tools/one_click_patch.py`), więc tokeny, limity, układ i dozwolone znaki
  sprawdza ta sama bramka.
- `transfer.json` — brakujące linie, którym można dać brzmienie już napisane
  przez tłumacza (to samo zdanie japońskie, dokładnie jedno brzmienie).
- `CORRECTIONS.json` — ten sam transfer w formacie, który czyta
  `one_click_patch.py`: japoński oryginał, suma, powód. Dzięki temu widać
  w audycie, że żadne brzmienie tłumacza nie zostało zmienione.
- `README.md` — tabela powodów, dla których element został dla tłumacza.

### Dlaczego to nie jest tłumaczenie

Narzędzie **nie pisze nowego tekstu**. Przenosi wyłącznie brzmienie, które
tłumacz już napisał dla **identycznego co do znaku** zdania japońskiego, i tylko
wtedy, gdy w wydanym planie to zdanie ma **jedno** brzmienie. Zostają dla
tłumacza:

- zdania bez polskiego odpowiednika w planie (59 662 elementy),
- zdania z kilkoma brzmieniami (1 780) — np. 「うん…」 → 「Ano…」/「Dobrze…」/
  「Mhm…」; wybór zależy od mówcy i sceny, więc nie da się go przenieść,
- zdania, których polskie brzmienie jest identyczne z japońskim (25) — to nie
  jest przekład,
- wiersze planu, których nie ma w tym miejscu wzorca (0 obecnie).

## Próba generalna — `data/remaining_text_rehearsal.json`

`tools/rehearse_remaining_text.py` bierze **zwrotkę, z której powstał PL9**
(znajdowaną po sumach `input_sha256` z planu, nie po ścieżce), wpisuje
przeniesione brzmienia w ich własne `PL:` i przepuszcza wynik przez
`bind_all` → `import_batch` → `merge` — czyli przez tę samą bramkę co każda
zwrotka tłumacza. Wynik ostatniego przebiegu:

| kontrola | wynik |
| --- | --- |
| przeniesione linie | 2 148 |
| linie dopisane do planu przez transfer | 679 |
| wiersze, którym transfer **zmienił** brzmienie | **0** |
| wiersze zmienione poza transferem | **0** |
| wiersze utracone | **0** |
| transfery, które nie weszły do planu | **0** |

Czyli: przeniesienie tekstu przechodzi bramkę importu i nie rusza ani jednego
wiersza tłumacza. To wynik **offline**; nie jest to potwierdzenie działania
w grze (PL9 nadal nie ma potwierdzenia runtime poza misją 1-1C z PL8).

## Złożenie zwrotki — `tools/merge_remaining_return.py`

Paczka zawiera tylko brakujące elementy, a numer elementu zaczyna się od nowa w
każdej scenie, więc nie da się jej odesłać jako zwrotki. Wypełnioną paczkę
składa się z powrotem w pełny wzorzec:

```bash
python tools/merge_remaining_return.py --package <wypełniony katalog> --out <katalog>
python tools/merge_remaining_return.py --transfer translations/pl-remaining/transfer.json \
    --out build/pl-remaining-return
```

Pierwsza forma dopasowuje elementy **po nagłówku i scenie** (nie po numerze) i
przerywa pracę, jeśli w paczce zostanie cokolwiek niedopasowanego. Druga wpisuje
przeniesione brzmienia **po pozycji elementu** — to jest adres, którego używa
`pl_import`, więc nic nie jest zgadywane.

Złożona zwrotka jest **częściowa**: `one_click_patch` wymaga 100 % wierszy tabel, a
44 184 wierszy tabel nie ma polskiego tekstu. Złożenie służy więc sprawdzeniu
bramki i przyszłej zwrotce, nie wydaniu patcha.

## Jak to się ma do liczby 61 810

`deliver_remaining_text.py` dzieli 61 810 na dwie części, bo to dwie różne
sytuacje: **23 218** elementów leży w plikach, które tłumacz już dostał i odesłał
(po prostu zostawił je puste), a **38 592** — w 22 plikach wzorca, których nie ma
w żadnej zwrotce (`PL9` ma sumy 27 z 49 plików). Ta sama liczba 23 218 wychodzi z
próby generalnej (`elements_left_blank_in_return`), co jest jedynym sensownym
sprawdzeniem, że oba narzędzia liczą to samo.
