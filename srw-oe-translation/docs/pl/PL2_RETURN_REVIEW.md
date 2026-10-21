# PL2 — audyt zwrotu tłumacza, 2026-10-18

## Wynik najważniejszy

Sprawdzono dokładnie dostarczony `PL2.zip` (1958693 B), nie deklarowany stan
roboczy. **Pula fragmentów jest gotowa rozmiarowo, ale Skill00 nadal przekracza
normalny limit o 686 B.** Nie wyłączono zabezpieczeń i nie przygotowano kolejnej
próby za dużego pliku. Tekstu tłumacza nie przeredagowano.

| Pomiar                                                  |              Poprzedni PL.zip |           PL2.zip |    Limit |
| ------------------------------------------------------- | ----------------------------: | ----------------: | -------: |
| Skill00, rzeczywisty układ writera                      |                      224678 B |      **217454 B** | 216768 B |
| Nadmiar Skill00                                         |                        7910 B |         **686 B** |      0 B |
| Pula z ogona Skill00 jako osobny kontener — projekcja   |                       17386 B |           15382 B |  15638 B |
| Fizyczne pule DLC Skill01–08, normalny builder + odczyt | nie mierzono w tym porównaniu | **15331 B każda** |  15638 B |

Zwykły builder potwierdził odmowę `config00.cpk` przy 217454 B. Osobno sprawdzono
writer z nadal aktywną bramką: ten sam wynik. Odmówiony config00 nie trafia do
wyniku nawet jako potajemna częściowa podmiana. Wynik nie jest gotowym patchem PL.

Oszczędność binarna Skill00 wynosi **7224 B**, nie deklarowane 10234 B:
5219 B tekstów rekordów + 1 B efektu wyrównania + 2004 B puli. MD umiejętności
i MD teksty-config mogą wskazywać ten sam fizyczny tekst — nie wolno sumować
wszystkich takich wystąpień. Nie odtworzono dokładnego rachunku tłumacza;
powyższy rozkład pochodzi z fizycznych planów writera tej konkretnej paczki.

Potrzeba jeszcze co najmniej **686 B oszczędności w wynikowym Skill00**.
Warto celować w około 1–1,5 kB dalszych skrótów w nazwach/opisach umiejętności,
a potem ponowić pomiar; liczba znaków MD nie jest gwarancją wyniku po wyrównaniu.
Pula jest już poniżej limitu — nie trzeba jej skracać na siłę. Nie usuwać spacji
fragmentów, tokenów, kontroli ani istotnych podziałów linii. Jeżeli opisany stan
roboczy jest nowszy od spakowanych MD, najpierw wyeksportować go ponownie.

## Import i początkowe spacje

- 10 MD, **36161 zaakceptowanych elementów**, 7580 kopii; 0 odmów, obcych
  elementów i duplikatów. Kontrola pakietu: 0 błędów; ostrzeżenia układu/długości
  pozostają miękkimi ostrzeżeniami, nie dowodem sprawdzenia wszystkich ekranów.
- **Wszystkie 634 niepuste pola zaczynające się od spacji zachowują dokładny
  prefiks** w zaimportowanym JSONL i kodeku PL. Jedna spacja po `PL:` jest
  separatorem MD; następna należy już do tekstu. Importer nie był poprawiany,
  ponieważ już zachowywał te spacje. Dodano kontrolę i regresję także dla dwóch
  początkowych oraz jednej końcowej spacji.
- 28 pustych pól config nadal to dane binarne: 18 poza pięcioma polami tekstu,
  10 ItemDrop. Nie wypełniać ich tekstem. 8040 pustych cytatów to natomiast
  nieukończone sloty PL, nie dane binarne.
- Źródłowy EN/JP, metadane, oryginały i archiwa bez zmian; import tylko do kopii
  prywatnej. Skryptów tłumacza ze zagnieżdżonego stanu nie wykonywano.

## Złożenia i słownik

Odtworzono **1421** pól według rzeczywistych czterech indeksów przy rekordzie +28,
jednoprzebiegowego `%s`/`%%`, bez automatycznego dodawania spacji. Wszystkie
**33 poprzednio wskazane pola** mają zmieniony wynik; detektor błędnego sklejenia
`roń` ma teraz 0 trafień. W 1421 złożeniach brak `::` i podwójnych spacji.
To kontrola formatu i porównanie, nie nowa redakcja literacka ani render gry.

Jedno zakończenie linii `"Okręt-matka": ` pozostało w rekordzie 288/effect;
było też w poprzednim eksporcie. Nie uznano go automatycznie za nowy błąd.
Słownik ma 263 klucze i jeden klucz z dwiema formami PL (pełna/skrócona forma
Potencjału). To sygnał do sprawdzenia kontekstu, nie blocker importu; celowe
warianty pełne/interfejsowe są dopuszczalne. Pięciu zgłoszonych przez tłumacza
starszych niespójności nie poprawiano za niego.

## Cytaty — rozbieżność eksportu

W **dostarczonym** `PL/widoki/cytaty.md` jest **11801 / 19841** niepustych pól PL
(8040 pustych). Zgadza się niezależne liczenie surowych linii `PL:` i parser.
To o **1659 mniej** niż podane 13460. Nie jest to utrata przez importer.
Prośba do tłumacza: do następnego zwrotu spakować najnowszy eksport MD;
nie deklarować obecnego ZIP-a jako zawierającego 13460 gotowych cytatów.

## Kontrola buildera

- Na oryginalnych config01–08 zbudowano wszystkie osiem DLC normalną ścieżką:
  po naprawie opisanej niżej 0 problemów, każda pula 720 fragmentów/15331 B,
  307 B marginesu. Odczytano wszystkie 696 żądanych zmian na każdą pulę,
  w tym 82 zaczynające się od spacji. Brak twierdzenia, że pule są identyczne
  bajtowo między wszystkimi rozdziałami lub z ogonem Skill00.
- Przy okazji wykryto stary błąd kontroli rozdziału 4: poprawne polskie bajty
  tytułów odczytywano CP932. Naprawiono kontrolę na kodek aktywnego języka;
  oba tytuły, opis i tożsamość DLC nadal obowiązkowo sprawdzane. Nie wyłączono
  kontroli. Checker PL nie ma fallbacku do domyślnych oczekiwań angielskich.
- Bezpośredni writer EBOOT: 399 pól bez odmów, odczyt zgodny. Zwykły builder
  filtruje dwa pola identyczne z JP: faktycznie zapisuje 397 bez odmów.
- Końcowy zestaw: **1626 testów OK, 27 pominiętych** (28.127 s).
  Pierwszy pełny przebieg po nowej regresji PL ujawnił brak resetu kodeka
  w teście; dodano tearDown, bez zmiany zabezpieczeń produkcyjnych.
- Miniaturowy ISO zawiera rzeczywiste kontenery do testu ścieżki wejściowej,
  ale **nie jest grywalnym ISO**. Nie ma nowego runtime QA ani prośby o
  ponowne A/B/font/Masaki. Pełna kontrola wszystkich rozdziałów pozostaje otwarta.

Prywatna paczka audytu zawiera odpowiedź do tłumacza, adresy i porównanie 33 pól,
1421 złożeń, kontrolę spacji, metryki pól i aktualizator narzędzi EN/PL. Aktualizator
nie zawiera przekładów ani plików gry; nie omija pozostałych 686 B. Do GitHub
trafiają wyłącznie narzędzia/testy, ustalenia i manifest, nie binaria ani prywatny PL.

## Dostawa

[PL2_AUDYT_DLA_TLUMACZA.zip](https://drive.google.com/file/d/17pn6ak1zEeXQNAKpQRlI5Zw0uDlF1mhU/view)
— 454888 B / 16 plików, raporty/TSV i zagnieżdżony aktualizator narzędzi.
Ponownie pobrano: bajtowo identyczny, CRC obu ZIP-ów i wszystkie hashe raportów
oraz narzędzi zgodne. Udostępniania nie zmieniano.
[Manifest](pl2-return-review-delivery.json).

Wyodrębniony aktualizator sprawdzono w izolacji, poza ścieżką modułów repo:
CLI EN na oryginalnych kontenerach — 0 problemów; CLI PL — tylko oczekiwana
odmowa +686 B, poprawna kontrola i zapis DLC4. To nie nowy kompletny kit PL.
