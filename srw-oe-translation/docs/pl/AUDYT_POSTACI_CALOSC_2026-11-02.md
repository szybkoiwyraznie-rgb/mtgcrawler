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
- Prosta zamiana tekstów na odpowiedniki imenu zwiększyłaby łączną długość napisów w **184 z 188** rekordów w numerach 01–07/10–15 (bez 00 i 19). To samo w sobie nie dowodzi crasha, lecz wyklucza ogólną bezstratną podmianę tekstów w rekordzie o niezmienionym rozmiarze bez dalszego rozwiązania układu lub skrótów.

W izolowanym pliku odtworzonym po eksperymencie Dancougi zawartość rekordu Alana nie zmieniła się, ale przesunął się jego początek w słowniku z offsetu 12672 na 12718 (+46 bajtów); przesunięto początki 17/73 rekordów. To pokazuje możliwy efekt uboczny przebudowy, nie dowodzi, że był przyczyną regresji na komputerze właściciela. Nie znamy adresów, cache ani plików jego rzeczywistej instalacji.

## Narzędzie

`tools/audit_character_viewer.py --left <config> --right <imenu>` porównuje fizyczne słowniki i podaje liczniki, przesunięcia oraz numer rekordu; nie zapisuje plików gry i nie wypisuje tekstu z gry. Może także porównać dwie wersje tego samego kontenera. Obsługuje powtórzone ID, nie paruje rekordów samym kluczem i przerywa przy innej sekwencji kluczy. Rozpoznanie japońskich znaków jest heurystyką, nie walidacją tłumaczenia. `tests/test_audit_character_viewer.py` pokrywa przesunięcia, powtórzone klucze, niezgodność kolejności, puste pule oraz polski kodek.

## Otwarte zagrożenia

Historyczne v12A i v14 przy zmianach słowników powodowały zgłoszone awarie; korelacja nie identyfikuje konkretnego slotu ani mechanizmu. Sukces czterech pól Dancougi i sukces Masakiego w config19 nie zapewniają bezpieczeństwa setek innych zmian. Przed wydaniem zbiorczej poprawki trzeba znaleźć i sprawdzić przyczynę awarii oraz wyeliminować skutki relokacji lub wykazać, że są bezpieczne. Odmowa właściciela dalszych testów oznacza, że nie wolno ich wymagać ani pozorować ich wykonania. Binaria i wyniki lokalne nie należą do Git.
