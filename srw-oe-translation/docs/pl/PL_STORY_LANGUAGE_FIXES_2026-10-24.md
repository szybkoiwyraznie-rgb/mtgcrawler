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

## Epizod 13

- **Zakres:** 1 040 wpisów — 801 fabularnych i 239 warunkowych; 201 grup z pytaniami (137 fabularnych, 64 warunkowych).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 1 zmianę źródłową (`story-language-ep13-2026-10-24.json`, SHA-256 `e88d8aa8fa524c94fc93be8ed9ce0085cccf239b8eb94c5e9738d4a3fbbfbf8d`).
- **Potwierdzone klasy błędów:** błędny przypadek zaimka w bojowej uwadze Shiro „osłonę zostaw mnie” zamiast „osłonę zostaw mi”.
- **Świadomie zachowane fałszywe alarmy:** formalne „powinien był zostać rozwiązany” Rudolpha, „wedrze się lukami” jako droga przez luki w obronie, techniczne „zasymulowałem” Zera, Van „stanę się jednym z Blade Ligerem”, podwójnie grzeczne „proszę pana” Chum (bezpośrednio wyśmiane przez Dona Harumage) oraz bezpośrednie tagi w odprawach i rozmowach grupowych.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `8401bb6996f333bdf539514d07839841aead78e670a357ce6c2a950b702afc52` → `23e5b39106fd4a4f2e45e38b15eb77de228d18a6a570d981617ed91e152b7b87`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; zmieniony tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 14

- **Zakres:** 1 213 wpisów — 944 fabularne i 269 warunkowych; 246 grup z pytaniami (184 fabularne, 62 warunkowe).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 1 zmianę źródłową (`story-language-ep14-2026-10-24.json`, SHA-256 `5d43890b068304740792cc58d048018cca1ac66fdc9f9ac6ab696effd05a8008`).
- **Potwierdzone klasy błędów:** błędny przypadek zaimka w „Zostaw to mnie” zamiast „Zostaw to mi”.
- **Świadomie zachowane fałszywe alarmy:** dworska liczba mnoga Gablae wobec Lady Nei, „wiesz?” Himari skierowane wprost do Seishiro, „prowadzić od frontu”, techniczne „dotrzeć” nową maszynę, JP-potwierdzone ukryte znaczenie `skrywacie ducha walki`, bezpośrednie tagi w rozmowach oraz poprawnie funkcjonujący porządek OVS w objaśnieniu wiązek łączących szlaki handlowe.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `23e5b39106fd4a4f2e45e38b15eb77de228d18a6a570d981617ed91e152b7b87` → `edb18709c876739d32ed0998fe31b829c5ac1dee6d24950d1c6add8d03366bcd`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; zmieniony tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 15

- **Zakres:** 910 wpisów — 639 fabularnych i 271 warunkowych; 124 grupy z pytaniami (77 fabularnych, 47 warunkowych).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 1 zmianę źródłową (`story-language-ep15-2026-10-24.json`, SHA-256 `88d34c524eb8df44c55e7ffa52191c8c0adddd195f352afd2b2e8ffff057dd3e`).
- **Potwierdzone klasy błędów:** błędny przypadek zaimka w „Zostawcie to mnie” zamiast „Zostawcie to mi”.
- **Świadomie zachowane fałszywe alarmy:** bezpośrednie tagi w dyskusji mostkowej i dialogu Jeffrey–Haman, „Daliśmy się złapać w intrygę”, żołnierskie elipsy rozkazów, „chłopiec z Gundama” jako pilot wewnątrz maszyny, archaiczna „strawa” aury Czarnego Rycerza oraz JP-potwierdzone metafory strategiczne Haman.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `edb18709c876739d32ed0998fe31b829c5ac1dee6d24950d1c6add8d03366bcd` → `f8253586c1f6180a977aa975a32bee5d70f5fc84d1ee079af96813ee8c28a78f`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; zmieniony tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 16

- **Zakres:** 800 wpisów — 661 fabularnych i 139 warunkowych; 161 grup z pytaniami (132 fabularne, 29 warunkowych).
- **Poprawki:** 5 kwestii wskazanych w przeglądzie; plan zawiera 5 zmian źródłowych (`story-language-ep16-2026-10-24.json`, SHA-256 `0d2092107d6f8dbe1f61a576c1c6e0fb9f4cb2fdc42e22a470f640cba3112ca7`).
- **Potwierdzone klasy błędów:** dwukrotnie błędny przypadek zaimka w „Zostaw to mnie” zamiast „Zostaw to mi” (Gary Godan, Kochak); wisząca kalka „Och, nie wolno nam!” bez dopełnienia zamiast „O nie, nie wolno do tego dopuścić!” (Puffy); odwrócony sens narracji „Oddział pozorujący Chirico” zamiast oddziału pozorującego, w którym służył Chirico; kalka „Tacy podejmują takie decyzje” zamiast „Ten oddział potrafi podjąć taką decyzję” (Chirico).
- **Świadomie zachowane fałszywe alarmy:** złowróżbne „grób to dla ciebie za wiele” Czarnego Rycerza, „roztopione substancje pewnie reagują chemicznie” Seishiro (JP-potwierdzone topniejące po downburście substancje), „krew dopłynie do palców AT” jako metafora płynu Polymer Ringer, zdublowana narracja o rozkazie dla oddziału Barcoffa (dwa odrębne wiersze źródłowe), zdobywanie przez Guardian Force doświadczenia przeciwko ISTO w walce z Balarantem oraz bezpośrednie tagi w rozmowach grupowych i rozkazach.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `f8253586c1f6180a977aa975a32bee5d70f5fc84d1ee079af96813ee8c28a78f` → `ffff3a1a5a8abbeb20afa2ce8e1cde50322ef5b7446697e517e3d4ac4ef00449`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; wszystkie 5 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 17

- **Zakres:** 1 051 wpisów — 890 fabularnych i 161 warunkowych; 185 grup z pytaniami (164 fabularne, 21 warunkowych).
- **Poprawki:** 4 kwestie wskazane w przeglądzie; plan zawiera 6 zmian źródłowych, bo kwestia Eijiego występuje w 3 wierszach (`story-language-ep17-2026-10-24.json`, SHA-256 `aec1fb67ea8a443c0e201b147ed3292eda0d0378f7dbd29e7dd7b9a590373d33`).
- **Potwierdzone klasy błędów:** błędny przypadek zaimka w „Zostawcie to mnie” zamiast „Zostawcie to mi” (Naomi); archaiczno-kulinarne „Gotuj się, Gosterro!” zamiast „Szykuj się” (Eiji, 3 wiersze); urwana kalka „to tylko dwa!” bez rzeczownika zamiast „to tylko dwa w jednym!” (Kenichi); chroma kolokacja „ogień przeciwlotniczy z czujnikami” zamiast ognia sprzężonego z czujnikami (Schubaltz).
- **Świadomie zachowane fałszywe alarmy:** „osłona tej trzysetki” jako określenie 300-osobowej jednostki, groźba Godana „przeżyje tylko jako pies”, żołnierskie „ile jeszcze, aż żołnierze wejdą na pokład?”, dosłowna metafora Naomi o robakach zmieniających się w muchy, zdublowana kwestia żołnierza Balarantu (dwa odrębne wiersze źródłowe) oraz bezpośrednie tagi w rozmowach grupowych.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `ffff3a1a5a8abbeb20afa2ce8e1cde50322ef5b7446697e517e3d4ac4ef00449` → `3e33d9b7b37d8f18d986fb582b5f600cd32fb3f77e8848f4215fd9cd463e42b7`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; wszystkie 6 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 18

- **Zakres:** 913 wpisów — 693 fabularne i 220 warunkowych; 142 grupy z pytaniami (107 fabularnych, 35 warunkowych).
- **Poprawki:** 3 kwestie wskazane w przeglądzie; plan zawiera 4 zmiany źródłowe, bo kwestia Ozmy ma jawny alias kopii (`story-language-ep18-2026-10-24.json`, SHA-256 `2955270a9177666832954cc9ae2f7a6cdbf11f8b1e615e5f728f9b1bca2d1e46`).
- **Potwierdzone klasy błędów:** dwukrotnie błędny przypadek zaimka w „Zostawcie/Zostaw to mnie” zamiast „Zostawcie/Zostaw to mi” (Ozma, Vanilla); faktyczne „Celujecie tylko we mnie” zamiast żądania „Waszym celem jestem tylko ja” (Chirico).
- **Świadomie zachowane fałszywe alarmy:** wyzywająca enumeracja Kenichiego „Niewybitni, barbarzyńscy, mniejsza z tym — to my!”, techniczne „krytyczne usterki konserwacyjne” okrętu, dworski rejestr przemówień Le Caina, „babrając się w robocie jak przy czyszczeniu ścieków” Vanilli, Vanilla zwracanie się per „kochaniutki” oraz bezpośrednie tagi w rozmowach grupowych.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `3e33d9b7b37d8f18d986fb582b5f600cd32fb3f77e8848f4215fd9cd463e42b7` → `321098b4d7156329ab52b98bf741cf7ac21f616cc7172e29bef12262b3dcacfc`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; wszystkie 4 teksty zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 19

- **Zakres:** 829 wpisów — 608 fabularnych i 221 warunkowych; 110 grup z pytaniami (75 fabularnych, 35 warunkowych).
- **Poprawki:** 2 kwestie wskazane w przeglądzie; plan zawiera 2 zmiany źródłowe (`story-language-ep19-2026-10-24.json`, SHA-256 `469a176d7c49563626774cab48e4abee1ba5665d2d6528c8c470b1636dbecaa0`).
- **Potwierdzone klasy błędów:** błędny przypadek zaimka w „Zostaw to mnie” zamiast „Zostaw to mi” (Judau); kalka „przekroczę ciebie” zamiast „przewyższę cię” (Setsuna).
- **Świadomie zachowane fałszywe alarmy:** kanoniczne „Jesteś ogonem tego Hitlera” Degwina, eliptyczne „Moc Exii... jest większa niż to!” Setsuny, dziecięce bezpośrednie tagi Ple, wojskowe „pilnujcie nas porządnie, jasne?” Karen oraz teatralny rejestr Mr. Bushido.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `321098b4d7156329ab52b98bf741cf7ac21f616cc7172e29bef12262b3dcacfc` → `6cd0389732a833a81e0bfeaf62bccf87bf53affb90fb8b4768628465bd5b3194`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; oba teksty zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 20

- **Zakres:** 974 wpisy — 726 fabularnych i 248 warunkowych; 145 grup z pytaniami (100 fabularnych, 45 warunkowych).
- **Poprawki:** 7 kwestii wskazanych w przeglądzie; plan zawiera 7 zmian źródłowych (`story-language-ep20-2026-10-24.json`, SHA-256 `a27e002217e6aa1fedc945f373213c4e84983f775e1d3efb9f803e92d6eeb733`).
- **Potwierdzone klasy błędów:** sześć kolejnych błędów celownika w „Zostaw mi/mi zostawcie” (Himari ×3, Koji, Ryoma, Lamuness); niepełna fraza „stawiając życie” zamiast „Ryzykując życiem” (Zechs).
- **Świadomie zachowane fałszywe alarmy:** samurajskie „Zetnę cię... bez przeprosin!” (斬り捨て御免), celowa komedia „u Pana Boga za klatą” z natychmiastową korektą Kallen, metażarty Da Cidera o PD i czasie antenowym, bezpośrednie tagi w scenach zbiorowych oraz żart z itashą Noa.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `6cd0389732a833a81e0bfeaf62bccf87bf53affb90fb8b4768628465bd5b3194` → `5a3319f106da80067496664181d96b0dbaac821398ccfe3f5f696942721b6112`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; wszystkie 7 tekstów zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 21

- **Zakres:** 801 wpisów — 538 fabularnych i 263 warunkowych; 103 grupy z pytaniami (68 fabularnych, 35 warunkowych).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 1 zmianę źródłową (`story-language-ep21-2026-10-24.json`, SHA-256 `1599d4b795ace20a0aab32a9818cf88c70d4744a5e42ddebcb3350b840991c73`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka w „Zostaw to mnie” zamiast „Zostaw to mi” (Kallen).
- **Świadomie zachowane fałszywe alarmy:** przekomarzanie „karaluch czy mszyca” drużyny Ganba, długie żartobliwe tytuły Da Cidera, bezpośrednie tagi w kierowanych wymianach oraz demoniczne przechwałki Goburikiego.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `5a3319f106da80067496664181d96b0dbaac821398ccfe3f5f696942721b6112` → `9ecf7f96412d20938da364bd540f55104a7df3cffc66956de56c6951e86ebed2`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 22

- **Zakres:** 851 wpisów — 616 fabularnych i 235 warunkowych; 114 grup z pytaniami (82 fabularne, 32 warunkowe).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 1 zmianę źródłową (`story-language-ep22-2026-10-24.json`, SHA-256 `99c0a62dc589e1ca9934f507f6caf5c4a1f6ac41b440770018a173935721e8b9`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka w „Zostaw to mnie, Fiono” zamiast „Zostaw to mi, Fiono” (Van).
- **Świadomie zachowane fałszywe alarmy:** żołnierskie „Gero gero gero” Keroro, samo-adresatywne „Znaczy, ...?” Angol Mois, szkolne przekomarzanie uczniów Eldrana oraz bezpośrednie tagi w scenach zbiorowych.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `9ecf7f96412d20938da364bd540f55104a7df3cffc66956de56c6951e86ebed2` → `af299852a00bbca1bc4532e30009ef8ba4268c315db68a5c010ad1bdc07c7faa`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 23

- **Zakres:** 819 wpisów — 486 fabularnych i 333 warunkowych; 99 grup z pytaniami (53 fabularne, 46 warunkowych).
- **Poprawki:** 0 — pełne przeczytanie i adjudikacja kandydatur nie wykazały defektów wymagających zmiany; planu nie tworzono, snapshot bez zmian.
- **Świadomie zachowane fałszywe alarmy:** poprawne „to wszystko nie ma sensu” Zera, kierowane tagi pytające (C.C., Simon, Haman), żołnierskie „to blisko, więc pewnie pojedzie Connect Force” oraz ceremonialny rejestr Gihrena.
- **Snapshot:** bez zmian — 108 794 wpisy; SHA-256 `polish.jsonl` nadal `af299852a00bbca1bc4532e30009ef8ba4268c315db68a5c010ad1bdc07c7faa`.
- **Walidacja:** świeża materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 24

- **Zakres:** 502 wpisy — 392 fabularne i 110 warunkowych; 83 grupy z pytaniami (65 fabularnych, 18 warunkowych).
- **Poprawki:** 0 — wszystkie kandydatury odrzucono jako fałszywe alarmy; planu nie tworzono, snapshot bez zmian.
- **Świadomie zachowane fałszywe alarmy:** kierowany tag Virala „Żaden z nas nie chce już tracić czasu, prawda?”, kolokwialne wezwania Kaminy oraz emocjonalne rozdzielenie zdania Seishiro na dwa wpisy.
- **Snapshot:** bez zmian — 108 794 wpisy; SHA-256 `polish.jsonl` nadal `af299852a00bbca1bc4532e30009ef8ba4268c315db68a5c010ad1bdc07c7faa`.
- **Walidacja:** świeża materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 25

- **Zakres:** 838 wpisów — 503 fabularne i 335 warunkowych; 146 grup z pytaniami (87 fabularnych, 59 warunkowych).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 2 zmiany źródłowe, bo rząd ma jedną jawną kopię (`story-language-ep25-2026-10-24.json`, SHA-256 `4ec8479745801730508869fe58dbf08238d7814ea1ef74e3298ae0b69c31a1ad`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka w cytowanym haśle „Zostawcie to mnie” zamiast „Zostawcie to mi” (Kenichi).
- **Świadomie zachowane fałszywe alarmy:** poprawny biernik w „to mnie wybrał ten świat” Drago, żartobliwe „jakmutam” Kaminy, znaczniki ukrytego mówcy „＃???” oraz żarty o „wyprzedaży bogów”.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `af299852a00bbca1bc4532e30009ef8ba4268c315db68a5c010ad1bdc07c7faa` → `761a8bb5c878de1b1ba839155239c9647a8c272f309c69a227e20ba9f650a2c5`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; oba teksty zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 26

- **Zakres:** 830 wpisów — 679 fabularnych i 151 warunkowych; 139 grup z pytaniami (111 fabularnych, 28 warunkowych).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 3 zmiany źródłowe, bo rząd ma jawne kopie (`story-language-ep26-2026-10-24.json`, SHA-256 `7af634fa1d4111566104f35a613af4dc4e8286123e0ae4e7f6331aa24dd1a765`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka „To zostawcie mnie” zamiast „To zostawcie mi” (Moonbay); skaner wzorców tego zdania nie wychwycił (szyk „zostawcie mnie” bez „to”).
- **Świadomie zachowane fałszywe alarmy:** poprawny biernik „i to mnie wkurza” Leenon, znaczniki „＃???” oraz kolokwialne „Ale urwanie głowy!” Moonbay.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `761a8bb5c878de1b1ba839155239c9647a8c272f309c69a227e20ba9f650a2c5` → `2e020dc914caff970afe0ec57b7039b5659b3d8fbed792ed06e70da049fb1d38`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; wszystkie 3 teksty zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 27

- **Zakres:** 895 wpisów — 616 fabularnych i 279 warunkowych; 123 grupy z pytaniami (78 fabularnych, 45 warunkowych).
- **Poprawki:** 2 kwestie; plan zawiera 2 zmiany źródłowe (`story-language-ep27-2026-10-24.json`, SHA-256 `ea4671d298a662cd3ef6f92088a4b330fbc140d2c5c67513696a85c7e96943a5`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka w formułach „zostawić to mnie” (Keroro) i „zostawcie mnie” (Zero) zamiast „…to mi / zostawcie mi”.
- **Świadomie zachowane fałszywe alarmy:** pytanie „Wchodzę, dobrze?” Seishiro (odpowiedź to zmiana sceny), repetycje „He, he, he” Kikaishina oraz żart o „wyprzedaży bogów” Masakiego.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `2e020dc914caff970afe0ec57b7039b5659b3d8fbed792ed06e70da049fb1d38` → `1550d30d4a57850a0d0e12f7d1807012bc767216b7a7e20ccbbed72c27de7afb`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; oba teksty zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 28

- **Zakres:** 1072 wpisy — 703 fabularne i 369 warunkowych; 179 grup z pytaniami (108 fabularnych, 71 warunkowych).
- **Poprawki:** 0 — wszystkie kandydatury odrzucono jako fałszywe alarmy; planu nie tworzono, snapshot bez zmian.
- **Świadomie zachowane fałszywe alarmy:** poprawny biernik „to mnie mdli” Bymana, JP-identyczny duplikat linijki Hiryu (źródło samo się powtarza) oraz celowy nonszalancki ton Gostero.
- **Snapshot:** bez zmian — 108 794 wpisy; SHA-256 `polish.jsonl` nadal `1550d30d4a57850a0d0e12f7d1807012bc767216b7a7e20ccbbed72c27de7afb`.
- **Walidacja:** świeża materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 29

- **Zakres:** 539 wpisów — 404 fabularne i 135 warunkowych; 70 grup z pytaniami (50 fabularnych, 20 warunkowych).
- **Poprawki:** 0 — wszystkie kandydatury odrzucono jako fałszywe alarmy; planu nie tworzono, snapshot bez zmian.
- **Świadomie zachowane fałszywe alarmy:** kolokwialne „No no” Ryomy, poprawne „Więc to to zniszczyło flotę” Brighta oraz kierowany tag Stingera „będziecie się szamotać, prawda?”.
- **Snapshot:** bez zmian — 108 794 wpisy; SHA-256 `polish.jsonl` nadal `1550d30d4a57850a0d0e12f7d1807012bc767216b7a7e20ccbbed72c27de7afb`.
- **Walidacja:** świeża materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 30

- **Zakres:** 1142 wpisy — 832 fabularne i 310 warunkowych; 176 grup z pytaniami (124 fabularne, 52 warunkowe).
- **Poprawki:** 1 kwestia wskazana w przeglądzie; plan zawiera 2 zmiany źródłowe, bo rząd ma jedną jawną kopię (`story-language-ep30-2026-10-24.json`, SHA-256 `699ee4ac0be7db6cac0450993260df920bf5df9aeeb01faaac36647350a76b82`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka „Zostaw to mnie” zamiast „Zostaw to mi” (Irvine).
- **Świadomie zachowane fałszywe alarmy:** poprawny biernik „że to mnie zatrzyma” Ravena, poprawne „to to samo” Hiltza oraz warianty warunkowe Go-Saurer/King Go-Saurer (oddzielne wpisy JP).
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `1550d30d4a57850a0d0e12f7d1807012bc767216b7a7e20ccbbed72c27de7afb` → `ce7636174e1f2afdf1066355e99c255614e8f7cafaccc270cf3723e3f76e7e85`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; oba teksty zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 31

- **Zakres:** 606 wpisów — 330 fabularnych i 276 warunkowych; 81 grup z pytaniami (36 fabularnych, 45 warunkowych).
- **Poprawki:** 0 — wszystkie kandydatury odrzucono jako fałszywe alarmy; planu nie tworzono, snapshot bez zmian.
- **Świadomie zachowane fałszywe alarmy:** poprawne „to to samo co ewolucja” Cowena, nazwa własna „Doki Doki Space” (fałszywy „podwójny wyraz”) oraz poprawny zwrot Adeu „Włożę w ten miecz…”.
- **Snapshot:** bez zmian — 108 794 wpisy; SHA-256 `polish.jsonl` nadal `ce7636174e1f2afdf1066355e99c255614e8f7cafaccc270cf3723e3f76e7e85`.
- **Walidacja:** świeża materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 32

- **Zakres:** 399 wpisów — 275 fabularnych i 124 warunkowe; 40 grup z pytaniami (31 fabularnych, 9 warunkowych).
- **Poprawki:** 2 zmiany źródłowe (`story-language-ep32-2026-10-24.json`, SHA-256 `14bcce2bffb03a1f7f1a1cdc368a8154a8869e6be3c55d31ca07c1e42ac87f52`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka „Zostaw to mnie” zamiast „Zostaw to mi” (Lamuness).
- **Świadomie zachowane fałszywe alarmy:** poprawny zwrot Adeu „W ten sposób nie da się podejść” oraz znaczniki mówców „＃Żołnierz Pentagony / ＃Oficer Pentagony”.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `ce7636174e1f2afdf1066355e99c255614e8f7cafaccc270cf3723e3f76e7e85` → `f0c3a628963273ec871ca92bcdf5adc411d26d4db97ddfc1d7910a9b23b5f295`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 33

- **Zakres:** 677 wpisów — 584 fabularne i 93 warunkowe; 88 grup z pytaniami (79 fabularnych, 9 warunkowych).
- **Poprawki:** 1 zmiana źródłowa (`story-language-ep33-2026-10-24.json`, SHA-256 `ac934320d51cf9b7b97f41006be1ba336751a12e06a3e274f38928118d8a1e2c`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka „To zostawcie mnie” zamiast „To zostawcie mi” (Zero).
- **Świadomie zachowane fałszywe alarmy:** poprawny zwrot Himari „w ten sposób uratujemy też samych Mucus” oraz dialogowe wielokropki na początku kolejnych okien.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `f0c3a628963273ec871ca92bcdf5adc411d26d4db97ddfc1d7910a9b23b5f295` → `17b2fea2564e2ec5af24e1c4ca9d807afc99b1b0d4c1afb945af1b61c4e9db15`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

## Epizod 34

- **Zakres:** 2023 wpisy — 1693 fabularne i 330 warunkowych; 338 grup z pytaniami (301 fabularnych, 37 warunkowych).
- **Poprawki:** 5 poprawek logicznych, 6 zmian źródłowych (`story-language-ep34-2026-10-24.json`, SHA-256 `8a73069ac0d05233ce86bc0956abbe70076ae9398e20091e5de098614fdf5b83`).
- **Potwierdzona klasa błędu:** błędny przypadek zaimka w formule „zostawić to komuś” — „Zostaw to mi” (Himari ×2, Shinobu), „zostawcie to mi” (Bobby) oraz „Proszę zostawić to mi” (Ohta).
- **Świadomie zachowane fałszywe alarmy:** poprawny bierny przypadek „to mnie jeszcze bardziej nakręca” Buda, nazwa własna „Doki Doki Space”, poprawne zwroty „w ten sposób”, dopełnieniowe „mnie” w „po to mnie pan wezwał” oraz zwroty do rozmówców z „prawda?”.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `17b2fea2564e2ec5af24e1c4ca9d807afc99b1b0d4c1afb945af1b61c4e9db15` → `bd61253ea31142b6f53a1107a5d2c54ca1903fea7d3bf9456735466bfeb2b1a1`.
- **Walidacja:** materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; tekst zweryfikowano po materializacji; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.
- **Uwaga:** epizod 34 to ostatni epizod wydania do czytania (`docs/reading-script/polish/episode_00.json`–`episode_34.json`), więc przegląd fabularnych dialogów w tej kolejności dobiegł końca.

## Domknięcie: przegląd całej bazy pod kątem klasy „zostaw to mi”

Po epizodzie 34 przeskanowano cały snapshot (dialogi i odzywki bojowe) pod kątem powtarzającej się klasy błędu — błędnego biernika „mnie” zamiast celownika „mi” w formule „zostawić coś komuś” (JP ～にまかせ).

- **Zakres:** 245 wpisów-kandydatów (106 różnych tekstów). Każdy zweryfikowano programowo wobec JP/EN: formuły まかせ/まっかせ/やらせろ oraz ここは自分が・あとは俺が (EN „Leave … to me”).
- **Poprawki:** 239 zmian źródłowych — 34 w dialogach i 205 w odzywkach bojowych (`story-language-sweep-zostaw-mi-2026-10-24.json`, SHA-256 `18313ff5314931237b8f53b8f3da0969dd2b10998f2436128baf88ff510a002f`). Objął też warianty plików spoza kolejności wydania do czytania (m.in. dodatkowe wersje DL834_13).
- **Świadomie zachowane poprawne bierniki (6 wpisów):** „Zostawiono mnie na asteroidzie”, „Zostawiłeś mnie samą”, „zostaw mnie, skup się na wrogu”, „nie zostawią na mnie ani jednej rysy”, „zostawisz u mnie”. Sprawdzono też inne zaimki („zostawimy ich na śmierć”, „Zostaw nas w spokoju”) — poprawne, bez zmian.
- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`: `bd61253ea31142b6f53a1107a5d2c54ca1903fea7d3bf9456735466bfeb2b1a1` → `e54562d803f8e011987b801c5439c2ee02dbe21d77775b9fe93c82386bc69262`.
- **Walidacja:** po materializacji zweryfikowano wszystkie 239 tekstów i **0 pozostałych trafień** wadliwego wzorca w dialogach i odzywkach; materializacja 109 176 wierszy, 108 805 wypełnionych, 371 pustych, 0 błędów i 4176 ostrzeżeń; przeszły 4 testy narzędzia korekt i 5 testów spójności. Brak testu PPSSPP.

Przegląd epizodów 0–34 wraz z tym domknięciem kończy bieżący zakres skanowania językowego fabuły.
