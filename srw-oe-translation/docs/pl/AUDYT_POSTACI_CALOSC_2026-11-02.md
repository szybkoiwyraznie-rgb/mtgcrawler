# OE PL: zbiorczy audyt pól przeglądu postaci — praca nieukończona

## Stan

Właściciel nie chce kolejnych testów poszczególnych pilotów. Polecił poprawić wszystkie pola postaci w całej grze, także imiona na liście. Zgłosił, że Alan był na liście po polsku **przed** eksperymentem Dancougi, a po nim po japońsku. Traktujemy to jako regresję zgłoszoną w jego rzeczywistej instalacji. Odtworzony wcześniej izolowany config01 nie jest tym samym plikiem i nie dowodzi, co właściciel widział wcześniej.

Nie przygotowano bezpiecznego zbiorczego patcha. Rzeczywista przyczyna dawnych awarii przy szerokich zmianach słowników nadal nie została wyizolowana. Nie należy zdejmować globalnej blokady tylko dlatego, że statyczny odczyt daje spodziewane wyniki. Nie należy przedstawiać eksperymentu dla Alana jako spełnienia prośby. Getter-3, istniejące kopie bezpieczeństwa i angielskie komunikaty PSP pozostają bez zmian.

## Reprodukcja i zakres

Oryginalne `config00.cpk`, `imenu00.cpk`, 45 dostępnych config EDAT i 24 imenu EDAT pobrano z dotychczasowego prywatnego źródła. Z oficjalnego kitu PL v4.10 użyto jego własnego buildera i zmaterializowanego tłumaczenia. Builder uruchomiono na kopiach kontenerów, osobno dla pary 00 i DLC, z wyłączonym exe i teksturami. **Nie było pełnego ISO:** raporty zgłaszają brak czcionki, a zatem te wyniki nie są pełnym buildem ani działającym obrazem gry. Porównanie dotyczy fizycznej zawartości słowników, nie potwierdza ścieżki wykonania w PPSSPP.

Wśród 45 dostępnych `configNN.EDAT` 19 zawiera słownik postaci, z czego 13 niepustych (01–07, 10–15) i jeden niepusty 19; pozostałe słowniki są puste. `config00` także zawiera niepusty słownik. Dla wszystkich 15 niepustych numerów dostępne są odpowiadające imenu. Imenu 20, 21, 22, 24, 25, 31 i 32 zawierają pustą czterobajtową tabelę; odczytano je przez czytnik TOC, gdyż writer słusznie odmawia pracy z kolumną o stałym rozmiarze. Pozostałe niedostępne numery nie są pokryte tą inwentaryzacją. Inne struktury i wszystkie ekranowe ścieżki gry nie zostały w ten sposób wykluczone.

Dla 15 par przebadano **291 rekordów**, wszystkie sloty 0–11 oraz japońskie znaki w slotach 0, 1, 2, 3, 4, 5, 10, 11. Rekordy porównano po kolejności z kontrolą pełnej sekwencji kluczy: w oryginale niektóre klucze występują więcej niż raz (00 i 02), dlatego proste łączenie po ID gubi dane.

- W configach stwierdzono japońskie znaki: slot 1 — 143 komórki, slot 2 — 2, slot 4 — 188, slot 5 — 188, slot 10 — 1, slot 11 — 160. To liczba **komórek**, nie liczba osób. Słownik 00 i 19 nie miał takich komórek w badanych polach.
- W odpowiadających imenu w tych polach nie wykryto znaków japońskich. Sama obecność tekstu po polsku nie gwarantuje, że gra wybierze tę kopię ani że długość pasuje w każdym widoku.
- Porównanie config↔imenu pokazuje różnice również w slotach 2 i 10 (poza aktorem, pseudonimem i krótkim imieniem), dlatego naprawa ograniczona do slotów 4/5/11 nie byłaby kompletna. Ogółem różnice: slot 1 — 144, 2 — 2, 4 — 188, 5 — 188, 10 — 1, 11 — 161. Różnica bajtów nie zawsze oznacza błąd językowy.
- Prosta zamiana tekstów na odpowiedniki imenu zwiększyłaby łączną długość napisów w **184 z 188** rekordów w numerach 01–07/10–15 (bez 00 i 19). Wcześniejsze stwierdzenie, że samo to wyklucza zapis w niezmienionym rozmiarze, było błędne: rekordy zawierają też zapas zerowego wypełnienia. Po jego uwzględnieniu 136/188 pełnych zestawów napisów mieści się w rekordzie z normalnie uporządkowanymi, rozdzielnymi napisami; 52 się nie mieszczą. Wariant arytmetyczny, w którym sam tekst aktora z pola 1 współdzieli końcówkę tekstu z pola 5, mieści 186/188, zaś współdzielenie dowolnych wspólnych końcówek — 188/188. Wszystkie 188 badanych rekordów miały zerowy ogon i brak nieznanych referencji wykrywanych przez parser. **To tylko analiza pojemności, nie patch:** współdzielenie narusza niezmiennik rosnącej kolejności wskaźników obecnie wymagany przez parser; nie wykazano, że gra ani jej loader akceptują taki układ. Nie wykazano też bezpieczeństwa użycia zerowego wypełnienia. Nie wolno włączać tej metody do patchera jako bezpiecznej.

W izolowanym pliku odtworzonym po eksperymencie Dancougi zawartość rekordu Alana nie zmieniła się, ale przesunął się jego początek w słowniku z offsetu 12672 na 12718 (+46 bajtów); przesunięto początki 17/73 rekordów. To pokazuje możliwy efekt uboczny przebudowy, nie dowodzi, że był przyczyną regresji na komputerze właściciela. Nie znamy adresów, cache ani plików jego rzeczywistej instalacji.

## Narzędzie

`tools/audit_character_viewer.py --left <config> --right <imenu>` porównuje fizyczne słowniki i podaje liczniki, przesunięcia, numer rekordu oraz teoretyczną pojemność dla trzech układów tekstu; nie zapisuje plików gry i nie wypisuje tekstu z gry. Może także porównać dwie wersje tego samego kontenera. Obsługuje powtórzone ID, nie paruje rekordów samym kluczem i przerywa przy innej sekwencji kluczy. Rozpoznanie japońskich znaków jest heurystyką, nie walidacją tłumaczenia. `tests/test_audit_character_viewer.py` pokrywa przesunięcia, powtórzone klucze, niezgodność kolejności, puste pule, analizę pojemności oraz polski kodek.

## Otwarte zagrożenia

Historyczne v12A i v14 przy zmianach słowników powodowały zgłoszone awarie; korelacja nie identyfikuje konkretnego slotu ani mechanizmu. Sukces czterech pól Dancougi i sukces Masakiego w config19 nie zapewniają bezpieczeństwa setek innych zmian. Przed wydaniem zbiorczej poprawki trzeba znaleźć i sprawdzić przyczynę awarii oraz wyeliminować skutki relokacji lub wykazać, że są bezpieczne. Odmowa właściciela dalszych testów oznacza, że nie wolno ich wymagać ani pozorować ich wykonania. Binaria i wyniki lokalne nie należą do Git.

## Uzupełnienie: offline i rzeczywisty odczyt kontenerów

Zachowując bramkę, w wariancie badawczym sprawdzono fizyczny zapis i ponowny odczyt wszystkich 15 par: 291 rekordów, 188 zmienionych, 242 człony, jednakowe rozmiary kontenerów i bajtowo identyczne pozostałe człony. Rzeczywisty kod loadera i wybrane selektory 1.08 wykonano w emulatorze z kontrolowanymi atrapami; dodatkowo dla każdego rekordu wywołano bezpośrednie odczyty pól 3 i 10 oraz sprawdzono oba wyjątki zapisane w EXE. Test kończy się przed kolejnym resolverem i nie obejmuje całej gry. Na tej podstawie **nadal nie wydano zbiorczej poprawki**, bo nie zostały wyjaśnione dawne crashe ani regresja Alana, a format prototypu narusza niezmiennik normalnego parsera.

Poprawiono źródło osobnego podpisu aktora w EXE na `Głos: K.Totani` (14 bajtów, więc imię skrócono). To zmiana danych źródłowych, nie gotowe wydanie. Dotychczasowy eksperyment Dancougi tworzył `wynik-test/config01.EDAT.BACKUP`; przywrócenie tej kopii po zamknięciu PPSSPP cofa całą podmianę z tego eksperymentu, ale nie naprawia reszty pól i nie stanowi diagnozy przyczyny regresji.
