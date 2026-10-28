# SRW Y — trwałe zaplecze importu i patchowania

Stan audytu: 2026-10-28, prace w toku.

## Punkt wyjścia

- Pierwsza zwrotka tłumacza jest w `translations/pl1/PL/` jako źródło, nie jako patch gry.
- `tools/pl_import.py` i generowanie manifestu istnieją, ale `docs/IMPORTER_Y.md` wymaga odtworzenia prywatnego manifestu z danych S6 i porównania go z wysłanym pakietem v8. Manifestu i S6 nie ma w repozytorium.
- Ten sam dokument stwierdza, że nie istnieje jeszcze zbiorczy orchestrator import → wszystkie sceny i tabele → patch. Nie należy przedstawiać pojedynczych skryptów ani patchera v2 jako dowodu, że cały proces dla rzeczywistej zwrotki jest ukończony.
- Katalog `local/` i `build/` jest ignorowany. Same narzędzia są w repozytorium, ale ignorowanie całego obszaru roboczego nie gwarantuje zachowania manifestów i innych danych niebinarnych potrzebnych kolejnej sesji.

## Cel

Odzyskać i utrwalić w repozytorium reużywalny warsztat i niebinarne wejścia potrzebne do walidacji i przygotowania kolejnych zwrotek, a oryginalne i zmodyfikowane binarne assety gry pozostawić poza repozytorium. Nie zakładać, że patchowanie istniejących bundli jest możliwe bez dostępu do oryginalnych bajtów: ustalić zakres operacji offline i wykonywanych u właściciela. Nie pomijać kontroli tożsamości źródeł ani nie publikować niezweryfikowanego patcha.

Dalszy audyt i wyniki rzeczywistej walidacji zostaną zapisane tutaj.
