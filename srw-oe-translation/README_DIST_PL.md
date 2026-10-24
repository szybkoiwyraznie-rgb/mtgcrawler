# Super Robot Wars OE — pełny polski patcher (v4.4 — korekta językowa scen dodatkowych)

Paczka buduje kompletny polski patch na **Twoim oryginalnym japońskim ISO 1.08** i
odszyfrowanym DLC `NPJH50521`. Nie zawiera plików gry ani gotowego ISO.

## Sceny dodatkowe i symulator — v4.4 (2026-10-24)

Dokończenie przeglądu językowego poza wydaniem do czytania: sceny z kontenerów
`evept101`–`evept108` (dodatkowe misje/symulator) oraz wiersze `eventP*`
leżące poza blokami epizodów 0–34 — 16 725 wierszy dialogów, których v4.3 nie
obejmowało.

- **22 poprawione wiersze**, każdy zweryfikowany wobec japońskiego oryginału
  i angielskiej bazy oraz wobec przyjętego już polskiego przekładu tej samej
  linii japońskiej w korpusie epizodów: brakujące orzeczenie („No...
  przeszkadza.”), zdanie zamienione w pytanie („Nie przegramy, prawda?”),
  strona bierna bez podmiotu („GoShogun nie wyrzuciło…” — trzy kopie DLC),
  brak narzędnika („To ja Gurren Lagann wydobędę…”), odwrócony podmiot i
  dopełnienie („Okręt przyspiesza wiązka naprowadzająca…”), kalka
  „pokonuje nietknięta przekrój czasoprzestrzeni” oraz szyk i odmiana
  („Brak wam czujności, wszystkim.”, „siedziba na cały Układ Słoneczny”,
  „Ten alarm chyba nie to oznacza, co?”, „Nie, to nie jest aż tak wygodne.”).
- **Bez zmian pokrycia i interfejsu:** 108 805 / 109 176 wypełnionych wierszy,
  371 świadomie pustych, 0 błędów, 4 176 ostrzeżeń; UI, font PL i geometria
  podpisów tekstur jak w v4.2.
- **Wersja tekstu:** `pakiet_PL/snapshot.json` — 108 794 wpisów,
  `data_sha256 = da2ad33f3c9ad813cd3601ca1a3400586a0ec24cd087dbd0cbe09e5bfc303e1f`,
  `partial = false`.

Aktualizacja z dowolnej starszej wersji przebiega jak zwykła instalacja
(sekcja „Pełne wydanie PL — v4.0” niżej): spatchuj od nowa **czyste**
japońskie ISO, wgraj świeże `patched.iso` i cały katalog `DLC\`, a zapis
wczytaj normalnie po zimnym starcie (nie dawny save-state).

## Korekta językowa fabuły — v4.3 (2026-10-24)

Pełny przegląd językowy polskiej prozy fabularnej, przeprowadzony epizod po
epizodzie (0–34) z weryfikacją każdej zmiany wobec tekstu japońskiego
i angielskiego, oraz domykający przegląd całej bazy:

- **658 zmienionych wpisów** (30 planów źródłowych: 453 dialogi i 205 odzywek
  bojowych): odpowiedzi niedopasowane do pytań, niezgodności rodzaju
  mówiących i adresatów, kalki składniowe oraz błędny przypadek zaimka
  w formule „Zostaw to mi” (JP ～にまかせ) — ta ostatnia poprawiona w całej
  grze (239 wpisów, po korekcie 0 pozostałych wystąpień).
- **Bez zmian pokrycia i interfejsu:** 108 805 / 109 176 wypełnionych wierszy,
  371 świadomie pustych, 0 błędów, 4 176 ostrzeżeń; UI, font PL i geometria
  podpisów tekstur jak w v4.2.
- **Wersja tekstu:** `pakiet_PL/snapshot.json` — 108 794 wpisów,
  `data_sha256 = e54562d803f8e011987b801c5439c2ee02dbe21d77775b9fe93c82386bc69262`,
  `partial = false`.

Aktualizacja z dowolnej starszej wersji przebiega jak zwykła instalacja
(sekcja „Pełne wydanie PL — v4.0” niżej): spatchuj od nowa **czyste**
japońskie ISO, wgraj świeże `patched.iso` i cały katalog `DLC\`, a zapis
wczytaj normalnie po zimnym starcie (nie dawny save-state).

## Geometria napisów na teksturach — v4.2 (2026-10-24)

Ta sama poprawka co polski `Postęp` z v4.1, domknięta dla pozostałych podpisów
rysowanych na teksturach przeglądu/ulepszeń. Komórki TXCL zweryfikowano jako
identyczne we wszystkich trzech kontenerach gry (`IM1000`/`IM3000`/`IM9000`):

- **Ekran ulepszeń (`intsys_03`, podpisy wspólne z wersją EN):** `Unit / Pilot`,
  `Upgrades`, `Linked Units`, `Support` i wstęga `Upgrade Limit Break` rysują się
  teraz w całości w swoich komórkach — wcześniej dolne części liter były ucinane
  albo wyciekały do sąsiednich podpisów, a przy wstęze zostawał ślad japońskiego
  glifu.
- **Znaczek `LNK` (`intsys_01`):** nie wystaje już o 1 px poza swoją komórkę.
- **Wersja angielska (para EN):** wszystkie podpisy `intsys_04` (m.in. pełne
  `Convert` i `Progress`) wyrównane tak samo jak polskie w v4.1.
- **Bez zmian:** treść przekładu i liczby pokrycia jak w v4.1; polskie podpisy
  `intsys_04` z v4.1 renderują się bajt w bajt identycznie.

## Poprawki interfejsu — v4.1 (2026-10-23)

Wydanie naprawia trzy ekrany zgłoszone po testach v4.0 w PPSSPP (treść przekładu
bez zmian; pokrycie i liczby jak w v4.0 poniżej):

- **Zakładka pilota (Lista Jednostek):** napis pod portretem nie wychodzi już na
  kolumnę statystyk — `Pilot gł.` (główny) i `Współpilot` (pomocniczy) mieszczą
  się w ramce.
- **Ekran „Wyniki i części”, pasek nagłówka:** `Postęp` wyświetla się w całości
  (wcześniej ostatnie „p” było ucięte), zniknął obcy znak „|” po `Premii`,
  a skróty `Masz` / `Wym.` nie są już przycinane. Przyczyna: gra przycina podpisy
  tekstur do własnych prostokątów komórek TXCL — polskie podpisy są teraz
  rysowane dokładnie w tych komórkach.
- **Ten sam ekran, stopka:** etykieta posiadanych części to teraz `Masz` —
  koniec najeżdżania na liczniki `Lv1 × 0 Lv2 × 0 Lv3 × 0`.
- **Wersja tekstu:** `pakiet_PL/snapshot.json` — `108 794` wpisów,
  `data_sha256 = e730f18027e876edd1cc466831bc9cbda6370b7e542a1ad6d9c9bf9e5272de1b`
  (16 planów poprawek właściciela, `1 525` wiązań), `partial = false`.

Aktualizacja z v4.0 przebiega tak samo jak zwykła instalacja (sekcja niżej):
spatchuj od nowa **czyste** japońskie ISO, wgraj świeże `patched.iso` i cały
katalog `DLC\`, a zapis wczytaj normalnie po zimnym starcie (nie dawny
save-state).

## Pełne wydanie PL — v4.0 (2026-10-23)

Wydanie domyka **100% prac redakcyjnych**: rozdziały 0–8 (od prologu po finał
`DL834_13` i epilogi), pakiety DLC `evept101`–`evept108`, pełny plik tekstów misji
(`05_mission_text.jsonl`) oraz audyt spójności całego korpusu (`109 176` wierszy).

- **Pokrycie pakietu:** **108 805 / 109 176** wypełnionych wierszy, **371** świadomie
  pustych slotów strukturalnych, **0 błędów twardych**, `4 176` miękkich ostrzeżeń
  długości/układu (kontrola statyczna — nie jest to runtime QA).
- **Zakres merytoryczny v4.0:** rozdzielenie skróconej nazwy **Kallen** Kozuki
  i **Karen** Joshua, zgody rodzajowe mówiących i adresatów w rozdziałach 0–8,
  krótkie repliki po pytaniach, kalki składniowe, nazwy pomocniczych pilotów
  (`SI sterująca`, `Żołnierz Posaydala`), ujednolicone `Saurersi / Saurersów`,
  nieodmienny `Mucus Gate`, męski/bezrodzajowy `Connect Force`, poprawki finału
  (`Tak... Van wygrał!`, `jedną z naaas`, `profesjonalistką`, `Shiden Swordem`)
  oraz nazwy celów misji (`Demon Goburiki`, `Transport Ark Ship`,
  `64_Mapa ataku 10 (mrok pustki)`).
- **Zachowane 100% (`1 385 / 1 385`)** wcześniejszych wiązań właściciela: poprawek
  UI, schowka, Eldrana, Duchów, umiejętności, 32 tytułów/notatek misji, kodu naprawy
  bufora nazw (`8 -> 32 B`) oraz natywnego fontu PL v5 (18 znaków diakrytycznych),
  wraz z `"Matchless"`, znacznikami `(Ally)` / `/Ally` i dynamicznym tokenem
  `＜主人公名＞`.
- **Wersja tekstu:** `pakiet_PL/snapshot.json` — `108 794` wpisów,
  `data_sha256 = 8cb37fb30f8c1551083a2e1c050abb645ed561c706a1515cbc8152cc32a6269c`,
  `partial = false`. `translation/PL_COVERAGE.json` w paczce zawiera pochodzenie
  i dokładne liczby.

**Instalacja / aktualizacja (wymagane i `patched.iso`, i cały katalog `DLC\`):**
1. Rozpakuj paczkę do nowego folderu i uruchom `PATCH.bat`.
2. Wskaż czyste, oryginalne japońskie ISO **SRW OE 1.08** oraz pełny folder
   odszyfrowanego DLC (`NPJH50521`) — **nie nakładaj patcha na wcześniej spatchowane ISO**.
3. Podmień w PPSSPP zarówno wygenerowane `output\patched.iso`, jak i wszystkie
   wygenerowane pliki z `output\DLC\` w `memstick\PSP\GAME\NPJH50521\`.
   Zachowaj swoje zwykłe zapisy gry (wczytuj normalny zapis po zimnym starcie gry,
   nie stary save-state).

---

## Historia: wydanie v3.0 (`PL5.zip`, 2026-10-21)

Zintegrowano kompletny zwrot tłumacza `PL5.zip`: wszystkie 36 plików scen
(`epizod-00`–`epizod-34` oraz `simulator`), pełne `cytaty.md` (**19 841** kwestii
bitewnych), spójność imion, tytułów misji i terenu, przy zachowaniu **1 385**
wiązań poprawek UI/Duchów/schowka i fontu PL v5. Wydanie **v4.0** powyżej dokłada
**342** poprawki redakcyjne rozdziałów 0–8, DLC i tekstów misji oraz audyt
spójności całego korpusu.

## Historia wcześniejszych wydań częściowych — import PL4 (v2.7, 2026-10-20)

Paczka patchera **v2.7-PL4** zawiera 91 plików; po pobraniu sprawdź hash
z przekazania wydania.

Zintegrowano zwrot tłumacza PL4: wszystkie dziewięć widoków oraz fabuła
**epizodów 00–21**. Odczyt sprawdził 28 078/28 079 elementów; jedyny pusty
slot to biały znak strukturalny, nie dialog. Pełny pakiet ma 87 794/109 176
wypełnionych wierszy. Walidator zgłosił 0 twardych błędów, ale pozostaje
25 165 miękkich ostrzeżeń długości/układu — to nie jest runtime QA. Epizody
22–34 i symulator są nadal nieukończone.

Wszystkie **1 283** wiązania naszych wcześniejszych skrótów i poprawek UI
zachowano; wróciły też wszystkie 32 osobne tytuły/uwagi misji. 57 trwałych
poprawek pamięci tłumaczeń sprawdzono względem zwrotu. Imię protagonisty nie
jest wpisane na sztywno w polskim wierszu epizodu 13. Skrypty z archiwum
stanu tłumacza nie były uruchamiane.

**Przyrost PL4 dotyczy 25 plików DLC `.EDAT`:**
`eventP01.EDAT`, `eventP02.EDAT`, `eventP03.EDAT`, `eventP04.EDAT`,
`eventP05.EDAT`, `eventP06.EDAT`, `eventP13.EDAT`, `eventP20.EDAT`,
`eventP21.EDAT`, `eventP22.EDAT`, `eventP23.EDAT`, `eventP24.EDAT`,
`eventP25.EDAT`, `eventP26.EDAT`, `eventP27.EDAT`, `eventP28.EDAT`,
`eventP29.EDAT`, `evept101.EDAT`, `evept102.EDAT`, `evept103.EDAT`,
`evept104.EDAT`, `evept105.EDAT`, `evept106.EDAT`, `evept107.EDAT`,
`evept108.EDAT`. Dla aktualizacji z v2.6 nie oczekujemy zmian ISO ani PBOOT;
nowe teksty wymagają tych DLC. To zakres ustalony z metadanych źródła — w tym
sandboxie nie ma pełnego oryginalnego ISO/DLC, więc builder nie wykonał
fizycznego odczytu wyjść. Po lokalnym uruchomieniu kopiuj tylko pliki pokazane
w jego raporcie. Wydanie nie zawiera ISO/DLC gry. Szczegóły:
[`docs/pl/PL4_RETURN_REVIEW.md`](docs/pl/PL4_RETURN_REVIEW.md).

## Poprzednia poprawka siedmiu zrzutów — v2.6-PL3-UI

**Aktualizacja z v2.5 na Twoim PPSSPP 1.20.4: ISO — TAK; DLC — NIE.**
Przebuduj z oryginałów i podmień tylko `patched.iso`. Zostaw obecne DLC;
nie kopiuj ponownie `PBOOT.PBP`. To zakres tej aktualizacji w używanej przez
Ciebie ścieżce uruchamiania z ISO, nie instrukcja pierwszej instalacji.

- Krótsze nagłówki: **Tr.:**, **OK**, **Sort**, **Łącz**, **Str.**
  (`Łącz` to łączenie jednostek, nie powiększenie obrazu).
- Przycisk przejścia dalej w wynikach: **OK** zamiast ucinanego „Dalej”.
- Ostrzeżenie terenowe: **Ląd: zakaz** — jednostka nie może wejść na ląd.
- Uzupełnione osobne kopie tytułów w dziesięciu misjach podstawowych,
  m.in. **Na ratunek White Base**. Kontrola wszystkich **527 pól tytułów**
  w menu i danych misji, także DLC; nie tylko misji 2.
- Przejrzane wszystkie **20 komend ducha / 60 rekordów poziomów**.
  Długie nazwy skrócone, m.in. **Wiatr**, **Celny**, **Duch**, **Błog.**;
  większość nazw mieści się w 3–7 literach/znakach. Pełne, zaakceptowane
  **Skupienie** pozostaje. Opisy działania nie zostały skrócone.
- Działający bufor nazw, kod naprawy pamięci i font pozostają bez zmian.

To poprawki danych/tekstu. Nowe dopasowanie napisów wymaga potwierdzenia
w grze — testy offline nie zastępują widoku w PPSSPP. Wystarczy jedna
przebudowa ISO, bez osobnego testu fontu czy kolejnego eksperymentu z buforem.

## Co zawiera ten przekład

- Kompletny przekład fabuły **epizodów 00–34** (w tym finał `DL834_13` i epilogi)
  oraz wszystkich pakietów DLC `evept101`–`evept108`; wypełniono
  **108 805 / 109 176** wierszy pakietu (`371` pustych slotów to wyłącznie
  strukturalne artefakty binarne i literały silnika bez fallbacku do EN).
- Pełne kwestie bitewne, nazwy postaci/jednostek/broni, encyklopedie z biogramami,
  teksty misji, przedmioty, umiejętności, ekrany pomocy oraz całe menu i UI.
- `translation/PL_COVERAGE.json` zawiera pochodzenie i dokładne liczby aktualnego
  pakietu. Pełne pokrycie widocznych slotów nie oznacza przetłumaczenia każdego
  tekstu silnika, odkrycia wszystkich zasobów ani sprawdzenia wszystkich ekranów.
- Poprawka Masaki/Shiro/Kuro działa automatycznie w normalnym builderze.
- Font v5 dodaje polskie akcenty do rodzimych jednobajtowych komórek `ank.fta`
  podczas budowania na Twoim ISO. Litera PL zajmuje jedną celę, jak ASCII.
  Nie trzeba osobno wgrywać fontu. Wygląd zaakceptowano na pokazanych ekranach
  początkowych; nie jest to deklaracja QA całej gry.

## Poprawki z 10 zrzutów — paczka UI z 19.10.2026

- Krótsze etykiety: **Statystyki**, **R. 1–R. 8**, **Strona**, **Kr.**,
  **Jedn.**, **Razem**, **Nagroda:** i **1. raz:**; krótsza pomoc „Wyniki i części”.
- Panel statusu: **Pokład**, **Sw.**, **Kr.**; nagłówki **Zwycięstwo** i **Porażka**
  z polskimi znakami, bez zmiany zaakceptowanego wyglądu fontu.
- Uzupełniony polski komunikat o stałym składzie w misjach początkowych;
  dodatkowa informacja o sojuszniczym NPC Medea nie została usunięta.
- Pełne **Skupienie** zostaje. Naprawa powiększa zbyt małe pole nazwy w menu,
  zamiast skracać nazwę. Zapis wskaźnika grafiki nie nadpisuje już jej końcówki
  w sprawdzonym teście kodu MIPS. Builder odmawia tej zmiany dla innego niż
  rozpoznany pliku wykonywalnego, zamiast zgadywać adresy.

To jedna zbiorcza poprawka. Kontrola bajtów i test kodu nie zastępują próby w grze:
**potwierdzenie tych ekranów w PPSSPP nadal jest potrzebne**. Nie trzeba wykonywać
osobnego testu fontu ani budować osobnego ISO dla każdej etykiety.

## Poprawka po kolejnych 4 zrzutach — v2.3-PL3-UI

- Zastępuje wadliwą poprawkę v2.2, która powodowała crash przy wejściu do
  szczegółów Duchów. **Skupienie** pozostaje pełne. Nowe miejsce na nazwę jest
  na końcu obiektu; dotychczasowe pola i wskaźniki nie są przesuwane.
- Test odtwarza odczyt błędnego adresu `0x6D` ze starej poprawki, a nowy kod
  przechodzi ten sam odcinek wejścia do szczegółów i cztery odcinki aktualizacji.
  To test pamięci/kodu MIPS z częścią funkcji zastąpionych atrapami, **nie PPSSPP**.
- Krótsze podpowiedzi przycisków: **Ulepsz**, **Widok**.
- Polskie znaki w ostrzeżeniu zapisu i innych napisach silnika: m.in. **nośnika**,
  **wyłączaj**, **Osłona**, **Okrążenie**, **Części**, komunikaty błędów.
  Zmieniono wyłącznie pisownię, bez powiększania tych napisów w pamięci.
- Dwa opisy w systemowej liście zapisów nadal mają pisownię ASCII. Używają
  innego, systemowego fontu UTF-8; nie wstawiamy tam niezweryfikowanych glifów PL.

Rozpakuj do nowego folderu i przebuduj z oryginałów. Nie nakładaj nowego kodu
na wcześniej spatchowane ISO. Po zimnym starcie wczytaj normalny zapis, wejdź do
podglądu maszyny Seishiro i otwórz szczegóły Duchów. Sprawdź nazwę i poziomy,
zmień zaznaczony Duch, wyjdź i otwórz ponownie. Potwierdź też zapis i oba paski
przycisków. Nie usuwaj zapisów ani oryginałów.

## Kolejna partia UI — v2.4-PL3-UI

**Instalacja po v2.3 na Twoim PPSSPP: ISO — TAK; DLC — NIE.**
Zostaw obecne DLC. Builder może odbudować również `PBOOT.PBP`, ale używana przez
Ciebie ścieżka PPSSPP uruchamia program z ISO. Nie trzeba go ponownie kopiować.

- Skupienie i wejście do szczegółów Duchów zostały już potwierdzone w grze;
  zaakceptowana poprawka pamięci pozostaje bez zmian.
- Systemowy komunikat startowy jest po angielsku: ten ekran PSP używa innego
  fontu, nie polskich komórek bitmapowych gry. Tak samo zabezpieczono cztery inne
  prześledzone systemowe ostrzeżenia. Nie zmieniono zaakceptowanego fontu gry.
- Odstępy w opisach Duchów i umiejętności: kontrola wszystkich 120/1985
  wypełnionych pól opisów i skrótów z fizycznie odbudowanych tabel. Poprawki
  dotyczą składania fragmentów, nie nowego przekładu ani zmiany działania zdolności.
  W ciasnych napisach silnika użyto `L1`–`L5` i `Obr.:`, aby zmieścić odstęp.
- Krótsze pola Wyników, **Szansa części+** i podpowiedź **Szk.** w wąskiej
  ramce przycisku. Wyczyszczony i spolszczony atlas nagłówka części.
- Usunięto zbędną informację o foncie z normalnego przebiegu launchera;
  kontrola poprawnego wejściowego ISO nadal działa.

Kontrola bajtów/obrazów nie zastępuje oględzin w PPSSPP. Po przebudowie wystarczy
jedna próba: komunikat startowy, opis Skupienia/umiejętności i wskazane ekrany
Wyników/części/przerwy. Zimny start i zwykły zapis, nie stary save-state.

## Widok oglądania mechów — v2.5-PL3-UI

Wąskie podpowiedzi przycisków z tego ekranu są krótsze:
**Zmień jedn.**, **Obr.**, **Ukryj**. SELECT nadal przełącza widoczność napisów;
„Ukryj” nazywa czynność dostępną, gdy te podpowiedzi są widoczne. Zmieniają się
wyłącznie trzy etykiety (cztery źródłowe wpisy, bo zmiana jednostki ma dwie kopie).
Pozostałe poprawki v2.4, font i zaakceptowana poprawka Skupienia bez zmian.

**Po v2.4 na Twojej obecnej konfiguracji PPSSPP: ISO — TAK; DLC — NIE.**
Przebuduj i podmień `patched.iso`, pozostaw obecne DLC. Nowej kopii `PBOOT.PBP`
nie trzeba przenosić przy używanym przez Ciebie uruchamianiu z ISO. Nie jest to
ogólna zasada dla innych loaderów. Oględziny w grze nadal są potrzebne — testy
bajtów nie stanowią potwierdzenia układu napisów w PPSSPP.

## Uruchomienie

Potrzebne: Windows10/11, Python3.10+ (zalecany3.12), Pillow, PPSSPP i kilka GB
wolnego miejsca. Launcher próbuje zainstalować brakującego Pythona/Pillow.

1. Rozpakuj **cały ZIP** do nowego folderu. Nie nakładaj go na starszy kit.
2. Uruchom **PATCH.bat**, wybierz oryginalne ISO i odszyfrowany folder DLC
   (albo Anuluj, jeśli budujesz tylko płytę).
3. Wynik w `output/`:
   - `patched.iso` — otwórz w PPSSPP, zawiera również font PL;
   - `DLC/` — pliki ze środka nałóż na istniejący kompletny folder
     `memstick/PSP/GAME/NPJH50521/`, nie jako dodatkowy podfolder;
   - `build_report.json` — zachowaj; opisuje zapisane pola i ewentualne odmowy.
4. **Nie instaluj wyniku z komunikatem Build FAILED.** Podeślij raport zamiast
   uruchamiać częściowe pliki z nieudanego przebiegu.
5. Uruchom PPSSPP na zimno i wczytaj zwykły zapis z gry, nie stary save-state.
   Nie usuwaj zapisów. Zachowaj kopie oryginalnego ISO/DLC i save'ów.

Buduj na oryginałach, nie na wcześniej spatchowanym ISO ani mieszance starych
wyników z nowymi. Oryginały wejściowe pozostają nietknięte. Obecność zachowanych
nieprzetłumaczonych zasobów w wynikowym ISO jest normalna dla częściowego patcha.

`CHECK_DLC.bat` to opcjonalna kontrola tylko do odczytu: sprawdza dwa zgłaszane
wcześniej tytuły DLC rozdziału4 i opis względem bieżącego **PL**. Nie modyfikuje
gry/save'ów i nie dowodzi, co emulator trzyma w starym stanie RAM.

## Znane ograniczenia — nie ukrywamy ich w wydaniu

- Tłumacz zgłosił możliwy **zły rodzaj gramatyczny w niektórych cytatach**;
  kompletność19841 pól nie oznacza zakończonej korekty językowej. Poprawki rodzaju
  w scenach zostały zachowane przy imporcie, ale nie przeprowadzono ręcznej korekty
  wszystkich mówców.
- Pozostało **158 zgłoszonych wcześniej uwag do złożeń**, głównie odstępów
  po dwukropkach, np. `Po aktyw.:Obraż.`. To nie jest liczba błędów łamania
  linii. Nie naprawialiśmy tych złożeń automatycznie za tłumacza.
- Miękkie ostrzeżenia o długości/layoutach nadal istnieją. Sprawdzanie limitów
  bajtów i celi nie zastępuje oglądania tekstów w grze; zalecenie46 celi jest
  czymś innym niż twardy limit danej ramki.
- Umiejętności mieszczą się w normalnych bramkach rozmiaru po skrótach PL3.
  Nie ma obejścia limitów z historycznych testów A/B. Build zatrzyma wysyłkę
  kontenera, jeśli kolejna wersja znowu przekroczy budżet.
- Napisy w grafikach są osobnymi specyfikacjami `ui_labels/`: część może nadal
  używać EN, jeśli nie ma podpisu PL. Ten fallback nie dotyczy tekstowego pola PL.
- Nie przeprowadzono tu gry na pełnym autentycznym ISO. Próby na rzeczywistych
  kontenerach w miniaturowym ISO sprawdzają bajty/pipeline, nie grywalność całości.

## Automatyczne wydania

Po scaleniu do main workflow buduje **EN i PL z jednego commita**, sprawdza oba
ZIP-y i publikuje razem z sumami SHA256. PR-y dostają artefakty do kontroli,
ale nie publikują wydania. Polski tekst pochodzi z wersjonowanego snapshotu,
nie z plików na czyimś dysku ani z dostępności Drive w czasie działania CI.

To niekomercyjny projekt fanowski, niezwiązany z Bandai Namco. Wymagana jest
własna legalna kopia gry. Nie rozpowszechniaj wynikowego ISO ani plików DLC.
