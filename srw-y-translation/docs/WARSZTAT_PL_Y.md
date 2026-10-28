# SRW Y — trwałe zaplecze importu i patchowania

Stan audytu: 2026-10-28, prace w toku.

## Punkt wyjścia

- Pierwsza zwrotka tłumacza jest w `translations/pl1/PL/` jako źródło, nie jako patch gry.
- `tools/pl_import.py` i generowanie manifestu istnieją, ale `docs/IMPORTER_Y.md` wymaga odtworzenia prywatnego manifestu z danych S6 i porównania go z wysłanym pakietem v8. Manifestu i S6 nie ma w repozytorium.
- Ten sam dokument stwierdza, że nie istnieje jeszcze zbiorczy orchestrator import → wszystkie sceny i tabele → patch. Nie należy przedstawiać pojedynczych skryptów ani patchera v2 jako dowodu, że cały proces dla rzeczywistej zwrotki jest ukończony.
- Katalog `local/` i `build/` jest ignorowany. Same narzędzia są w repozytorium, ale ignorowanie całego obszaru roboczego nie gwarantuje zachowania manifestów i innych danych niebinarnych potrzebnych kolejnej sesji.

## Cel

Odzyskać i utrwalić w repozytorium reużywalny warsztat i niebinarne wejścia potrzebne do walidacji i przygotowania kolejnych zwrotek, a oryginalne i zmodyfikowane binarne assety gry pozostawić poza repozytorium. Nie zakładać, że patchowanie istniejących bundli jest możliwe bez dostępu do oryginalnych bajtów: ustalić zakres operacji offline i wykonywanych u właściciela. Nie pomijać kontroli tożsamości źródeł ani nie publikować niezweryfikowanego patcha.

## Pierwsza kontrola PL1 bez danych gry

`python tools/check_pl_limits.py translations/pl1/PL` kontroluje tylko wpisane
wartości względem limitów *zwróconych przez tłumacza*. Nie wymaga S6, nie
zmienia zwrotki, zwraca JSON i kod 1 przy błędach. Nie jest importerem:
nie potwierdza autentyczności limitu, źródła, numeracji, tokenów, powtórzeń,
układu ani adresów docelowych. Pełna weryfikacja źródłowa nadal jest obowiązkowa.

Wynik: 26 279 wypełnionych i 20 529 pustych slotów; jeden wpis przekracza
podany limit: `02_cytaty_bitewne.md`, element 28254, **44 / 38 znaków**.
Nie zmieniono tłumaczenia ani nie uznano tej kontroli za pełną walidację.

Testy: 4 nowe testy, pełny `pytest -q -rs`: **578 passed, 0 skipped,
4558 subtests** (1 ostrzeżenie deprecacji). Kod i wynik możliwe do odtworzenia
bez plików gry.

## Ustalenia wymagające dalszej pracy

Wcześniejsze instrukcje były niejednoznaczne: patcher v2 instaluje już
zbudowane bundle i był testowym zestawem, natomiast dokument importera wprost
mówi, że zbiorczy builder jeszcze nie powstał. Nie jest więc prawdą, że sam
patcher realizuje drogę od zwrotki do gry. Na Drive odnaleziono paczkę v8,
ale osobnych plików `scenario.jsonl`, `tables.jsonl` ani manifestu wyszukiwanie
nazw nie zwróciło. Odtworzone S6 z czytanek to inny snapshot: nie wolno go
podstawić jako v8 bez niezależnego porównania. Konieczne jest zachowanie
odpowiednich niebinarnych danych, proweniencji i procedury ich odtwarzania;
dalej należy wykonać właściwą walidację PL1 i uzupełnić brakujące etapy.

