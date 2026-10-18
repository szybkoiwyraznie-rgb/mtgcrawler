# TEST_PL — mały test polskich liter w grze (SRW OE)

To **nie jest pełny patch tłumaczenia** — to próba techniczna, która wstawia do ISO
wyłącznie trzy pliki i pokazuje na własne oczy, że polskie litery działają w grze:
i w napisach, i w nazwach broni/mecha.

## Co robi

`TEST_PL.bat` patchuje **tylko**:

| plik w ISO | co się zmienia |
|---|---|
| `font.cpk` | gra dostaje 18 polskich glifów: ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż |
| `eventP00.cpk` | początek misji 0-0: narracja otwierająca (elementy 1–6), tytuł lokacji, dialogi Seishiro i Himari — z tekstem próbnym `TEST PL 1/4: ąćęłńóśźż...` |
| `config00.cpk` | ekran mecha **Exart**: nazwa (`Zażółć`), nazwa ekranowa oraz nazwy i skróty jego 8 broni (`TEST W1: ąćęłńóśźż`, `T1 ąćęł`...) |

Wszystkie inne teksty zostają japońskie — puste pola `pl` w pakiecie są pomijane
(oryginalne bajty nietknięte). DLC nie jest potrzebne, tekstury UI nie są ruszane.

## Jak uruchomić

1. Rozpakuj ten folder gdziekolwiek (Windows).
2. Uruchom `TEST_PL.bat` (podwójny klik). Wymagany Python 3 (bat sam go znajdzie).
3. Wybierz swoje ISO gry (SRW OE 1.08).
4. Po chwili powstanie `output\patched.iso`.
5. Otwórz go w PPSSPP i **zacznij nową grę** (New Game).

## Co sprawdzić w grze

1. **Narracja otwierająca** (czarny ekran z tekstem przed pierwszą sceną) — linie
   `TEST PL 1/4: ęłńóśźżĄĆĘŁŃÓ...` itd. Wszystkie małe i wielkie polskie litery
   powinny się wyświetlać jako litery, nie krzaki/kwadraty.
2. **Dialogi** Seishiro („(…") i Himari („TEST PL 1/1: żĄĆĘŁŃÓŚŹŻąćę") oraz
   linia z tokenem `＜主人公名＞` (imię bohatera wstawiane przez grę — token musi
   zadziałać, tzn. zamiast niego ma być imię).
3. **Ekran mecha Exart** (jednostka bohatera): nazwa `Zażółć`, opis ekranowy
   `TEST PL: Zażółć gęślą jaźń`, a na liście broni — `TEST W1: ...` do `TEST W8: ...`
   wraz ze skrótami `T1 ąćęł` ... `T8 źżĄĆ`.
4. **Tytuł misji** na briefingu: `TEST PL: Zażółć`.

Jeśli któraś litera NIE wyświetla się poprawnie — zanotuj którą i gdzie
(napisy / nazwa broni / wielkość liter). To jedyna informacja, której potrzebuje
osoba budująca patch, żeby poprawić font.

## Jak wrócić do zwykłej gry

Test niczego nie nadpisuje: twój oryginalny plik ISO zostaje nietknięty,
a `output\patched.iso` to osobna kopia — usuń ją albo trzymaj obok.
Pełny patch i tak buduje się od zera z oryginału.

## Co dalej (po udanym teście)

Pełny patch polski (`PATCH.bat` z pakietu `srw-oe-translation-pl-vN.zip`) robi to
samo, ale na wszystkich kontenerach i z prawdziwym tłumaczeniem z pola `pl`
pakietu tłumaczeniowego.
