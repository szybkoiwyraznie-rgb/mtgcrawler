# Audyt 479 odrzuconych grup PL1

Zadanie właściciela: przeanalizować każdy z 479 odrzuconych slotów i wszystkie
ich powtórzenia, rozdzielić błędy narzędzi od rzeczywistych problemów,
przygotować informację dla tłumacza i patch ze 100% pokryciem otrzymanych
wypełnionych PL. Nie używać „100%” jako synonimu kompletnego tłumaczenia gry.

Pierwsze sprawdzenie oryginalnego `QUARANTINE.json`: **479 slotów, 531
zarejestrowanych diagnostyk**; każda diagnostyka jest przypisana do konkretnego
źródłowego slotu i docelowego elementu. Liczba diagnostyk nie jest liczbą
niezależnych błędów — jeden slot może mieć wiele odrzuconych powtórzeń.

Wykryte błędy warsztatu wymagające poprawy i testów:

- Parser tokenów chwytał `$kwb` razem z następującym polskim słowem, np.
  `$kwbVAL`, podczas gdy źródłowy znacznik to `$kwb` i tekst to `VAL`. To
  generuje dziesiątki fałszywych błędów; tłumacz zachował znacznik.
- Parser uznawał zwykłe `[Elita]` lub `[Auto]` za tokeny, mimo że zmierzone
  tokeny zastępcze mają postać `[p1:]`, `[r1:]`, `[i:]`, `[protagonist]`.
- Jedno z „pustych źródeł” ma puste JP, ale niepusty EN; to samo dotyczy
  wszystkich **140** diagnostyk tej kategorii. Nie wolno traktować ich jak
  pustych w obu językach. Należy obsłużyć istnienie/brak każdego klucza w
  docelowym języku oraz jawnie opisać, skąd pochodzi tekst referencyjny.
- Liczba **260 diagnostyk U+201C** oznacza niezatwierdzony przez narzędzie
  cudzysłów typograficzny, a nie udowodniony brak znaku w fontach gry.

To historyczne ustalenia przed poprawkami. Szczegóły i stan po audycie znajdują
się poniżej; renderowanie, czcionka i działanie w grze nadal wymagają testu.

## Naprawione przyczyny narzędziowe

Importer rozpoznaje `$kwb`/`$kwe` także bez spacji przed łacińskim tekstem;
nie rozpoznaje zwykłych `[Elita]` jako placeholdera, a nazwane placeholdery
`[i:]`/`[r1:]` mogą zmieniać kolejność (nadal wymagają dokładnej treści i
liczby). Kolejność pozycyjnych `%s`/`%d` i znaczników sterujących nadal jest
kontrolowana. `％` to interpunkcja, nie token printf. Znak `“`, `×`, `・`,
strzałki i `★` dopuszczono po sprawdzeniu ich występowania w oryginalnym
korpusie gry — to **nie dowód renderowania na każdym ekranie**. Dla pustego JP,
ale niepustego EN importer używa EN do walidacji tokenów i układu, zachowując
rzeczywistą tożsamość i pusty JP w planie; nie wymyśla tłumaczenia.
`＜シンギュラポイント＞` w dokładnym źródle `ゴジラ S.P＜シンギュラポイント＞` to
japoński zapis wymowy w nazwie serii, a nie dowiedziony token sterujący; wyjątek
jest ograniczony do dokładnego źródła. Inne nawiasy `＜…＞` są nadal chronione.

Po tych zmianach pierwsza walidacja zgłaszała 23 diagnostyki dla 20 grup,
a po wyjątku nazwy Godzilli pozostaje 19 grup (limity powtórzeń i dwa nowe
`$n`). Pozostałych wartości nie należy bezkrytycznie zaakceptować; wymagają
oddzielnych, kontekstowych korekt. Pierwotne 479 i raport pozostają zachowane.

## Wynik i decyzje dla każdego elementu

`translations/pl1/AUDIT_479.json` zawiera **479 grup, 550 celów, 531 dawnych
zgłoszeń**: dla każdego celu identyfikator, JP/EN, limit, dawne zgłoszenia,
wynik PL i ewentualną korektę oryginał → zamiana. Audyt ponownie wiąże teksty
ze źródłem, waliduje wszystkie wpisy i sprawdza **każdy niepusty slot i każde
powtórzenie** względem planu. `QUARANTINE.json` zachowuje pierwotny stan.

Wynik: **26 279/26 279 wypełnionych slotów**, **29 873 wystąpienia** łącznie
z powtórzeniami, **0 grup w kwarantannie**. Pozostałe **20 529 pustych** PL
nie zostały wypełnione ani przetłumaczone automatycznie. To pokrycie zwrotki,
nie całej gry. Plan ma 25 444 klucze tabel oraz 4 429 wystąpień scen.

W `translations/pl1/CORRECTIONS.json` jawnie zapisano **22 lokalne korekty**:
20 to krótsze wersje wyłącznie dla docelowych powtórzeń z mniejszym limitem,
bez skracania głównego slotu; dwie dotyczą sceny 0 (elementy 3494–3495),
gdzie tłumaczenie dodało `$n`, choć nie było go w danym JP. Sprawdzono
kontekst: poprzednie kwestie rzeczywiście mówią o `$n`, ale te dwie oryginalne
kwestie odnoszą się do tej postaci bez znacznika. Zastąpiono go neutralnymi
sformułowaniami, zamiast dopisywać niesprawdzony token. Referencja EN mówi o
„NINJA friend” i „that idiot”; kontekst tłumaczenia pozostaje ten sam.
Wpisy tłumacza w `PL/` nie są modyfikowane. Każda korekta jest związana z
hashami całej zwrotki, identyfikatorem celu i hashem oczekiwanego tekstu;
przy innej zwrotce albo celu importer przerywa, a nie stosuje jej w ciemno.
Korekty są ponownie poddane wszystkim zwykłym kontrolom. Właściciel może
przejrzeć ich redakcję w pliku JSON, a dalsze testy mogą wymagać zmian.

140 przypadków pustego JP miało niepusty EN; w oryginalnych tablicach klucz
JP **istnieje jako pusty ciąg**. Patcher sprawdza i wstawia PL dla tego klucza
w JP oraz odpowiadający EN. Oddzielny przypadek 141 kluczy niewystępujących w
EN pozostaje obsługiwany jako brak, a nie puste źródło. Test syntetyczny i
przebudowa rzeczywistych danych sprawdziły oba języki, lecz nie wyświetlanie.

Test instalacji z rozpakowanego ZIP-a na kopiach wszystkich 12 oryginalnych
bundli: 25 444 zapisów tabel JP, 25 303 EN; po 4 429 scen JP/EN. Wszystkie
zapisy były odczytane i sprawdzone przez builder; po instalacji skontrolowano
12/12 wyników i backupów, a po cofnięciu 12/12 oryginalnych hashy. To test
**offline w Linuksie, nie test Windows, czcionki ani uruchomionej gry**.
Limit znaków i układ wierszy pozostają przybliżeniem, nie pomiarem pikseli.
