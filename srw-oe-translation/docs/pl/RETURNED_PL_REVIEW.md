# Odpowiedź po sprawdzeniu częściowego przekładu `PL.zip`

**2026-10-18.** Sprawdzono zwrócone 9 plików MD, zagnieżdżony stan pracy/słownik
oraz oryginalne `config00.cpk`, `configst.cpk` i EBOOT 1.08. Zwrot tłumacza i baza
EN pozostają bez zmian. To przegląd techniczny, nie literacka korekta całego przekładu.

## Gotowa odpowiedź dla tłumacza

Dziękuję za uwagi — zostały sprawdzone na plikach i narzędziach autora patcha.

### 1. 28 pustych pól w `teksty-config.md`

**Zostaw wszystkie te konkretne 28 pól PL puste. Nie kopiuj tam JP ani EN.**
To nie są napisy, które trzeba odtworzyć bez katakany:

- 14 trafia w nagłówki rekordów przedmiotów, na pozycji +24, poza tekstami;
- 4 trafiają w część liczbową rekordów umiejętności, również poza tekstami;
- 10 jest pozostałościami z binarnej tabeli `ItemDrop`, którą writer już odrzuca
  jako tekst.

Nie usuwaj numerowanych elementów ani nie zmieniaj JP/EN; pozostawienie pustego PL
nie patchuje tych danych. Lista adresów znajduje się w `empty-fields.tsv`.
To rozstrzygnięcie dotyczy tych 28 elementów, nie dowolnego japońskiego fragmentu.

### 2. Tokeny `＠4` / `＠6` w `program.md`

**Tak — nasz importer i writer je przyjmują. Zachowuj je dokładnie.**
„ASCII” w instrukcji dotyczy tłumaczonych słów, nie obowiązkowych kontrolek gry.
Nie zamieniaj pełnoszerokiego `＠` na zwykłe `@`, nie tłumacz cyfr kolorów.

W tej paczce jest 68 tekstów z `＠`: 63 mają pełny kod `＠` + cyfra, a 5 zawiera
rozdzielony między segmentami znacznik. Również tych końcowych, samotnych `＠`
nie wolno usuwać. Wszystkie 399 wypełnionych pól programu zapisano próbnie do
kopii oryginalnego EBOOT: **0 odrzuceń**, zgodne kontrolki i odczyt bajtów po zapisie.
Nie oznacza to testu wszystkich ekranów programu w emulatorze.

### 3. Długości umiejętności i przedmiotów

Potwierdzono **2082 ostrzeżenia w umiejętnościach i 138 w przedmiotach**, licząc
widoczne elementy MD. Są to rzeczywiście zalecenia długości pojedynczych pól,
nie polecenie skrócenia każdego tekstu do rozmiaru japońskiego.

**Jest jednak dodatkowy twardy problem całego pliku umiejętności:**

| Pomiar | Bajty zapisu gry |
|---|---:|
| Oryginalny `srwDL_Skill00.bin` | 208 958 |
| Wynik budowy z obecnymi tekstami PL | **224 678** |
| Przyjęty bezpieczny budżet buildera | **216 768** |
| Nadwyżka | **7 910** |

Builder odmówił wydania kontenera — to nie tylko potencjalne przycięcie napisu.
Budżet wynika z wcześniejszych testów ładowania gry, nie z ograniczenia ZIP-a.

Potrzebna jest zwięźlejsza wersja tekstów umiejętności: szczególnie nazw, wariantów
z poziomem i powtarzalnych opisów. Nie skracaj mechanicznie wszystkich ostrzeżeń;
wybierz sensowne, spójne skróty do UI i zapisz pełne oraz krótkie formy w słowniku.
Orientacyjnie trzeba odzyskać co najmniej około 8 kB **w kodowaniu gry**, z zapasem;
ostateczny wynik musi być ponownie zmierzony przez autora, ponieważ dochodzi
wyrównanie rekordów. Rozmiar UTF-8 pliku MD nie jest właściwą miarą.

Pula wspólnych fragmentów urosła dodatkowo o 1748 B. Dla DLC z tą samą pulą
projekcja daje 17 386 B wobec bezpiecznego budżetu 15 638 B. To wyliczenie na
fragmentach, nie test budowy rzeczywistych ośmiu EDAT-ów; pula również wymaga
skrócenia/kontroli. Nie omijamy zabezpieczeń rozmiaru.

### 4. Składane fragmenty w grupie 17

**Obawa jest zasadna: obecne złożenia zawierają rzeczywiste błędy.** Sam fakt,
że angielski urywa słowo w tym miejscu, nie gwarantuje poprawnego polskiego złożenia.

Z oryginalnych rekordów odczytano cztery indeksy fragmentów i podstawiono je do
aktualnych polskich szablonów, bez dopisywania spacji. W 33 polach wychodzi m.in.:

```text
Broń niewiązkowaroń wiązkowa
Broń wiązkowaroń wiązkowa
```

Przykład do znalezienia: `umiejetnosci.md`, **grupa 422, element 3**, korzysta
ze wspólnego fragmentu `teksty-config.md`, **grupa 17, element 3618**.
Drugi wskazany fragment, **grupa 17, element 3801**, również należy przejrzeć
w kontekście; nie ma podstaw do niezależnego dopisywania „B” do każdego wystąpienia.

Trzeba poprawić **pary: szablon + wspólny fragment**, tak aby wszystkie użycia
składały się poprawnie. Nie kopiuj podziału angielskiego słowa na polskie i nie
usuwaj `%s`, żeby ukryć problem. Zmiany równoległych zapisów w umiejętnościach
oraz config muszą pozostać zgodne. Jawne kopie DLC rozprowadza importer.

Dostarczone materiały do kontroli:

- `fragment-join-review.tsv` — 33 znalezione problematyczne pola, numery grup
  i elementów MD, referencja EN, szablon PL i złożony wynik;
- `assembled-skills.tsv` — 1421 pól tabeli po podstawieniu fragmentów, do szerszej
  kontroli kontekstu;
- `warnings.tsv` — ostrzeżenia z adresami elementów, bez domysłów co do wyglądu UI.

To podgląd formatowania z danych gry, nie screenshot. Osobne nadpisania opisów
przez EBOOT oraz ostateczny układ ekranów pozostają dodatkowym etapem kontroli.
Żaden z 33 wskazanych kluczy nie jest nadpisaniem bazowego opisu w znanej mapie 1.08.

### 5. Terminologia i dalsza praca

Przyjmujemy te ustalenia jako kanon dalszej pracy: **気力 = Morale**, polskie nazwy
Duchów, nazwy własne ataków zgodne z EN, ogólne bronie po polsku. Słownik w stanie
pracy został odczytany: **187 kluczy, bez sprzecznych powtórzeń tego samego klucza**.
To nie jest deklaracja literackiej weryfikacji każdej pozycji. Krótkie warianty UI
powinny być zapisane obok form pełnych, nie zmieniać po cichu terminologii.

Możesz kontynuować pozostałe sceny i kategorie. Przed integracją tej części trzeba
jednak skrócić umiejętności do budżetu oraz poprawić złożenia. Samo „0 błędów”
walidatora pojedynczych pól nie zamyka tych dwóch problemów.

## Uwaga autora patcha o walidatorze

Po naszej stronie znaleziono i naprawiono fałszywe rozpoznawanie tekstów typu
`50% obrażeń` jako printf `% o`. To odpowiadało za 77 początkowych odrzuceń.
Nie trzeba z tego powodu usuwać procentów ani przerabiać poprawnego przekładu.
Program nadal ma osobny, pełny walidator printf. Po poprawce cały przekazany zakres
przechodzi import: **24 360 elementów, 7580 uzupełnionych kopii PL, 0 błędów**.
W kopii pakietu jest 32 744 wypełnionych wierszy PL. Reszta pustych wierszy w pełnej
bazie obejmuje jeszcze nieoddane części; nie traktujemy jej jako regresji tłumacza.
JP, EN i metadane pozostały bez zmian. Nie wydano patcha z przekroczonym budżetem.

## Odtworzenie kontroli

```text
python tools/audit_pl_return.py --archive ../google_drive/PL.zip --package pakiet_EN --originals ../google_drive --out local/nowy_audyt_zwrotu_PL
```

Wyjście musi być nowym/pustym katalogiem. Skrypty ze stanu tłumacza nie są uruchamiane.
Dokładny SHA256 wejściowego `PL.zip`:
`f26a97af0c2b7bd5d8d73e24cb84835509983c0a5d04d4844e922a887b8a538b`.

## Dostarczona paczka dla tłumacza

[PL_audyt_i_kontekst_dla_tlumacza_2026-10-18.zip](https://drive.google.com/file/d/1PxXC3Kq_NcHWhro0bk6u0fI1wyEPzKqG/view)

Zawiera tę odpowiedź (bez niniejszego odsyłacza), czytelny Markdown z 33 przykładami,
cztery TSV oraz `review.json`. **60 597 B**, lokalna kontrola CRC wszystkich plików
ZIP OK; rozmiar i MD5 zwrócone przez Drive zgodne z lokalną paczką. Nie zmieniano
udostępniania. Nie zawiera binariów gry ani nowego tłumaczenia zastępującego pracę.
SHA256: `1cc03f74b43987fce87e0e5d2d85ce9ca7d79d6a3251a54a23010798c6f1de49`.
