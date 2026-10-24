# Korekta językowa fabuły PL od epizodu 3 (2026-10-24)

Dokument rejestruje kolejne przeglądy epizodów wykonywane po audycie 0–2. Każdy epizod jest skanowany w kolejności scen, a potwierdzone problemy są od razu poprawiane osobnym, źródłowo powiązanym planem `config/pl/story-language-epNN-2026-10-24.json`. Plik planu jest autorytatywną listą dokładnych zmian „przed/po”; ten dokument opisuje zakres, klasy ustaleń i walidację.

## Metoda

Dla każdego epizodu sprawdzane są:

- pełny tekst scen fabularnych i wypowiedzi warunkowych;
- wszystkie grupy z pytaniem oraz poprzedzającą i dwiema kolejnymi kwestiami;
- kandydatury z kontrolowanych skanów leksykalnych: tagi pytajne, nominalizacje, kalki, formy zwracania się, zaimki otwierające, niespójności interpunkcji między JP/EN/PL oraz odpowiedzi `tak/nie`;
- zgodność każdej podejrzanej kwestii z JP, EN i kontekstem sceny.

Plan jest następnie nakładany narzędziem `tools/pl_story_corrections.py`, cały pakiet PL jest materializowany od zera, wszystkie teksty z planu są asertywnie porównywane z materializacją, a testy `test_pl_story_corrections` i `test_pl_v4_0_consistency` muszą przejść przed commitem.

## Epizod 3

- **Zakres:** 994 wpisy — 731 fabularnych i 263 warunkowe; 238 grup z pytaniami (179 fabularnych, 59 warunkowych).
- **Poprawki:** 30 kwestii wskazanych w przeglądzie; plan zawiera 33 zmiany źródłowe po dołączeniu jawnych kopii `copy_of`.
- **Potwierdzone klasy błędów:** odwrotna odpowiedź („Ani trochę” zamiast potwierdzenia), niezrozumiała komparacja przeciwników, niepełny wniosek celowy, rozjechana rola syndykatu finansującego piratów, fałszywe znaczenie alarmu, kalki „wygodne” i „przekrój czasoprzestrzeni”, błędny szyk wiązki naprowadzającej, niepoprawny zwrot „rozwoju” oddziału oraz kilka oderwanych/refleksyjnych tagów i sztywnych konstrukcji sprawozdawczych.
- **Świadomie zachowane fałszywe alarmy:** komediowe `MAX` Keroro, źródłowe `ludzie typu pekopońskiego`, dosłownie obecny w JP `układ Frontier` oraz tagi pytajne rzeczywiście skierowane do rozmówcy.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `fffa694322f42aeeb7652a9a70305fea3332d1ce81b9d096eceb83b7ae7a1bc1` → `fda6c27086af862b315cf50cd7f6a23d0298eb889554fc98596ac4ddc399e6c1`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 4

- **Zakres:** 660 wpisów — 560 fabularnych i 100 warunkowych; 135 grup z pytaniami (114 fabularnych, 21 warunkowych).
- **Poprawki:** 30 kwestii wskazanych w przeglądzie; plan zawiera 49 zmian źródłowych po dołączeniu jawnych kopii `copy_of`.
- **Potwierdzone klasy błędów:** błędny przypadek `zostawić mnie`, zdanie bez rzeczownika `pytanie`, niepełny dopełniacz ładunku bramy, sztuczne `zgubiliśmy pościg`, rozbity warunek `nie tylko walki`, zbędny tag w kanonicznym `Kręcimy się w kółko, prawda?`, odwrócona składnia Killy’ego, `z rebeliantów`, narzędnik Macross Cannona oraz narracyjne `zapłaciła czystką`.
- **Uwaga walidacyjna:** pierwsza próba zastosowania planu została poprawnie odrzucona przez limit szerokości dialogu (linia 53 przy limicie 52); po skróceniu frazy o zwiadowcach cała ścieżka przeszła.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `fda6c27086af862b315cf50cd7f6a23d0298eb889554fc98596ac4ddc399e6c1` → `b3671f043b3203f9d45011bd8ee6cfa9867a430699466cdea4b9cbaf163097e9`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 5

- **Zakres:** 1 257 wpisów — 1 095 fabularnych i 162 warunkowe; 284 grupy z pytaniami (251 fabularnych, 33 warunkowe).
- **Poprawki:** 48 kwestii wskazanych w przeglądzie; żadna nie wymagała jawnej kopii `copy_of`, więc plan zawiera 48 zmian źródłowych.
- **Potwierdzone klasy błędów:** twarda gramatyka (`Jestem major`, `pracę umysłową zostawcie mnie`), odwrócona biegunowość potwierdzenia Monskara, błędna agencja przy przedstawianiu mieszkańców wioski, podmiot głos w `Leci tutaj?`, niejednoznaczne `posiłki` zamiast drugiej fali, sprzeczność `wytępić i zagnać pod ziemię`, dziewczyna nazwana `pułapką` zamiast przynęty oraz rządy i nominalizacje przy zabezpieczaniu odwrotu, płatności, liczeniu klientom i wyszukiwaniu śladów DG.
- **Świadomie zachowane fałszywe alarmy:** `dyrektor Douglas` (Suol Douglas), `Pan Lordgenome` jako forma czci Virala, poprawne powiedzenie `pozostawianie Chirico samemu sobie`, bezpośrednie tagi pytajne oraz formy grzecznościowe Suzaku wynikające z japońskich form uprzejmych.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `b3671f043b3203f9d45011bd8ee6cfa9867a430699466cdea4b9cbaf163097e9` → `6464d12792574e213d31b636b01b58a326995de5bda1e18de40d0d2ff1dc96d8`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 6

- **Zakres:** 804 wpisy — 655 fabularnych i 149 warunkowych; 178 grup z pytaniami (147 fabularnych, 31 warunkowych).
- **Poprawki:** 44 kwestie wskazane w przeglądzie; plan zawiera 57 zmian źródłowych po dołączeniu 13 jawnych kopii DLC.
- **Potwierdzone klasy błędów:** powtarzający się błędny przypadek `zostaw to/ich/resztę mnie`, mianownik `Jestem pułkownik`, odwrócona rola adresata przy dokowaniu, rząd `czekamy z raportem`, termin `walka kołowa` zamiast manewrowej, maszyna jako podmiot kapitulacji oraz zagmatwana fizyka jednostronnego pierścienia warp wraz z bezpodmiotowym warunkiem zajęcia placu budowy.
- **Świadomie zachowane fałszywe alarmy:** techniczny i JP-potwierdzony `przekrój warpu`, forma `Dzięki za fatygę`, komediowe inwokacje kulturalne oraz bezpośrednie tagi pytajne.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `6464d12792574e213d31b636b01b58a326995de5bda1e18de40d0d2ff1dc96d8` → `3c6f89b0b2f5987fcb2002fafb0652c92945fdb609eeb0d4b8388dce4f12d87e`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 7

- **Zakres:** 1 463 wpisy — 1 240 fabularnych i 223 warunkowe; 271 grup z pytaniami (235 fabularnych, 36 warunkowych).
- **Poprawki:** 56 kwestii wskazanych w przeglądzie; plan zawiera 87 zmian źródłowych po dołączeniu 31 jawnych kopii.
- **Potwierdzone klasy błędów:** odwrócona osoba celująca u Naomi, błędny celownik `Zostaw to mnie`, doczepianie wojny do ISTO przez zaimek `jego`, biernik/mianownik po `Imperium potrzebuje`, błędne ujęcie twierdzy w dopełniaczu po `bronić się`, generalskie „danie twierdzy”, `zaminowano pułapkami`, strona czynna przy zasypanych oddziałach oraz zagubiony podmiot Fiony po kilku dniach narracji.
- **Świadomie zachowane fałszywe alarmy:** źródłowe `Poniekąd zasłużył na śmierć`, dosłowne „cud natury” wypowiedziane żartem, frontowe bezpośrednie tagi, `Bracie` dla `aniki`, komedia o łagodnych gorylach i powtórzenie `wrócić... wrócić` tam, gdzie JP rozdziela warunek od dumnego powrotu.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `3c6f89b0b2f5987fcb2002fafb0652c92945fdb609eeb0d4b8388dce4f12d87e` → `615493273f199867e0e79899f97e20bfede4ee9871ee8a3f2516d5adbd9f67c3`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; wszystkie 87 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 8

- **Zakres:** 981 wpisów — 832 fabularne i 149 warunkowych; 210 grup z pytaniami (180 fabularnych, 30 warunkowych).
- **Poprawki:** 19 kwestii wskazanych w przeglądzie; plan zawiera 19 zmian źródłowych (brak jawnych kopii wymagających rozszerzenia).
- **Potwierdzone klasy błędów:** Adeu dowiadujący się „o tym kosmosie” zamiast o locie w kosmos, oddział Mrocznego Smoka błędnie przypisany Galdenowi, niezgodność rodzaju przy ostatnich statkach, wadliwy podmiot przy `fatygować się`, brak narzędnika przy Gurren Lagann, niejednoznaczny zaimek odsyłający do żołnierzy zamiast metali, błędny kierunek transferu warp oraz `ochrona przestrzeni` zamiast patrolowania sektora.
- **Świadomie zachowane fałszywe alarmy:** poprawne wojskowe `posiłki`, dowcip `początek/KONIEC-t`, `Bracie` dla `aniki`, terminologiczny „anomalny ocalały” oraz żart o robactwie przyczepiającym się do Adeu.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `615493273f199867e0e79899f97e20bfede4ee9871ee8a3f2516d5adbd9f67c3` → `a3dbd758f5470577e8f197c391f3a7c9e39c2a8e39cd3c1952d8461c007f22a9`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; wszystkie 19 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 9

- **Zakres:** 1 080 wpisów — 960 fabularnych i 120 warunkowych; 171 grup z pytaniami (152 fabularne, 19 warunkowych).
- **Poprawki:** 16 kwestii wskazanych w przeglądzie; plan zawiera 19 zmian źródłowych po dołączeniu 3 jawnych kopii.
- **Potwierdzone klasy błędów:** `przymusowy zwiad` zamiast przeforsowania badań Connect Force, niejednoznaczna `przestrzeń planety`, żołnierze `rozmieszczeni samotnie`, hybrydowe `nie pachnie powitaniem`, niepełne `jakby dla dobicia`, `stracił krwi` bez określenia ilości, sztywne `to rangą generał`, formalny rozkaz Buda `Pan się nie boi`, `kwestia zasady` zamiast JP-owskiej kwestii odczuć, Amuro zatrzymany **w** pracy zamiast powstrzymany od pracy, `zwycięstwo wartego rozejmu`, brakujące `temu` po `dałam początek`, niezgodność orzeczenia przy obrońcach Ziemi oraz `odpierać w dwie maszyny`.
- **Świadomie zachowane fałszywe alarmy:** wojskowe pozostawienie okrętu `na straży`, żart o kanibalizmie Red Shoulder, dosłowne oddanie tytułu przez Chara, bezokolicznikowa refleksja Zechsa oraz metafora zarodka/ziarna konfliktu u Setsuny.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `a3dbd758f5470577e8f197c391f3a7c9e39c2a8e39cd3c1952d8461c007f22a9` → `e289dc2e2a70b95eb2a36ecccc176fd5af67561ca9c9b5d6d453579f7c1c386d`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; wszystkie 19 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 10

- **Zakres:** 954 wpisy — 785 fabularnych i 169 warunkowych; 191 grup z pytaniami (160 fabularnych, 31 warunkowych).
- **Poprawki:** 10 kwestii wskazanych w przeglądzie; plan zawiera 10 zmian źródłowych (brak jawnych kopii wymagających rozszerzenia).
- **Potwierdzone klasy błędów:** bezpodmiotowe wyzwanie Kena `Dawać tu`, przysłówek zamiast przymiotnika w `Szybko jesteście`, mylące potwierdzenie po pytaniu o pozostałych wrogów, kolokacja `poznał wiedzę`, ataki synchronizowane wyłącznie „z spustem” bez jasnej relacji, niepełne `ciągle ci dokładam`, żołnierze, których nie można `ruszyć otwarcie`, nominalizacyjne `zaradzenie temu`, odwrócona relacja między informacjami a zeznaniami Wisemana oraz błędny rząd w `Pospieszcie konserwację`.
- **Świadomie zachowane fałszywe alarmy:** dosłowna metafora Chara o patrzeniu na rzeczywistość, luksusowy „problem do pozazdroszczenia” Himari, wojskowe potwierdzenie `Tak jest!` po pytaniu o Big Zama oraz eliptyczna odpowiedź Garcii o prowizorycznej naprawie.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `e289dc2e2a70b95eb2a36ecccc176fd5af67561ca9c9b5d6d453579f7c1c386d` → `6098604da3928842d13b87b04bfdc4eb67ec6b1e64a35127176454e7d1159a2d`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów; wszystkie 10 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 11

- **Zakres:** 739 wpisów — 594 fabularne i 145 warunkowych; 99 grup z pytaniami (81 fabularnych, 18 warunkowych).
- **Poprawki:** 4 kwestie wskazane w przeglądzie; plan zawiera 7 zmian źródłowych po dołączeniu 3 jawnych kopii (`story-language-ep11-2026-10-24.json`, SHA-256 `545f48789e9511834d40b0fd7e71adee93c60c06e8d0ad4e6ea2559c79cab777`).
- **Potwierdzone klasy błędów:** warunek Kikaishina `przeżyjecie to miejsce` zastąpiony wyrażeniem `wyjdziecie stąd żywi`, niezgodność `każde przejęte dane`, błędny przypadek w `Zostaw to mnie` oraz raport `zgubiliśmy pościg` wymagający podmiotu ścigających.
- **Świadomie zachowane fałszywe alarmy:** techniczne `zoptymalizowane na danych uczenia`, `masz głowę martwić się o innych`, `nie mogę tego darować`, taktyczne rozwijanie Mobile suitów oraz skrót o krytycznej energii Solar Raya.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `6098604da3928842d13b87b04bfdc4eb67ec6b1e64a35127176454e7d1159a2d` → `8ef7c6891790fa1db8daf773aef8dfd00d97477e9cec98e2b5ce8a0426540c9c`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; wszystkie 7 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 12

- **Zakres:** 799 wpisów — 661 fabularnych i 138 warunkowych; 139 grup z pytaniami (117 fabularnych, 22 warunkowe).
- **Poprawki:** 2 kwestie wskazane w przeglądzie; plan zawiera 2 zmiany źródłowe (`story-language-ep12-2026-10-24.json`, SHA-256 `5770cbd7809a669ff13cb35cfe74e12753108752f06d428feb9bb5f39ef1afef`).
- **Potwierdzone klasy błędów:** oderwany tag `co?` w monologu Lamunessa, który Tama-Q wprost nazywa gadaniem do siebie, oraz zniekształcony frazeologizm Violi `ruszasz się jak na dłoni` zamiast widocznych jak na dłoni ruchów przeciwnika.
- **Świadomie zachowane fałszywe alarmy:** Setsuny „możliwości przewyższają moje dane” jako techniczna ocena wobec danych, metafora Heero o byciu częścią maszyny, humorystyczna „data przydatności” informacji Rosso, dehumanizujące „obie rzeczy” Ravena oraz JP-potwierdzone bezpośrednie tagi Ravena i Lamunessa skierowane do rozmówców.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `8ef7c6891790fa1db8daf773aef8dfd00d97477e9cec98e2b5ce8a0426540c9c` → `8401bb6996f333bdf539514d07839841aead78e670a357ce6c2a950b702afc52`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; oba teksty zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.
