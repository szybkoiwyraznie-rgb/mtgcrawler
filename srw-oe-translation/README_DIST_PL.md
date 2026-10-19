# Super Robot Wars OE — częściowy patcher PL (PL3)

Paczka buduje polski patch na **Twoim oryginalnym japońskim ISO 1.08** i
odszyfrowanym DLC NPJH50521. Nie zawiera plików gry ani gotowego ISO.

## Co zawiera ten przekład

- Aktualny, sprawdzony import **PL3.zip**: widoki, **19841/19841** widocznych pól
  cytatów bitewnych i dialogi z eksportów epizodów **00–03** wraz z ich kopiami.
- Dalsza fabuła nie jest ukończona. Puste pola PL pozostają w oryginalnej grze;
  nie są automatycznie wypełniane angielską wersją tekstową.
- `translation/PL_COVERAGE.json` zawiera pochodzenie i dokładne liczby aktualnego
  pakietu. Pełne pokrycie widocznych slotów nie oznacza przetłumaczenia każdego
  tekstu silnika, odkrycia wszystkich zasobów ani sprawdzenia wszystkich ekranów.
- Poprawka Masaki/Shiro/Kuro działa automatycznie w normalnym builderze.
- Font v5 dodaje polskie akcenty do rodzimych jednobajtowych komórek `ank.fta`
  podczas budowania na Twoim ISO. Litera PL zajmuje jedną celę, jak ASCII.
  Nie trzeba osobno wgrywać fontu. Wygląd zaakceptowano na pokazanych ekranach
  początkowych; nie jest to deklaracja QA całej gry.

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
  po dwukropkach. Nie naprawialiśmy ich automatycznie za tłumacza.
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
