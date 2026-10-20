# Test pełnych umiejętności PL — bez skracania, wariant A/B

**Eksperyment na prośbę właściciela, 2026-10-18. Nie wydanie gotowego patcha.**
Paczka nie zawiera ISO ani binariów gry. Tak jak przy teście fontu, tworzy obrazy
lokalnie z Twojego oryginalnego ISO OE 1.08. Potrzebny Python 3, bez dodatkowych bibliotek.

## Uruchomienie

1. Rozpakuj **cały ZIP do nowego folderu**. Uruchom `TEST_UMIEJETNOSCI_PL.bat`.
2. Wybierz **oryginalne, działające ISO 1.08**, nie obraz po wcześniejszym patchowaniu.
3. Poczekaj na komunikat o zgodnym zapisie/odczycie. Powstaną dwa obrazy:
   - `output/A_PELNE_PL/A_PELNE_UMIEJETNOSCI_PL.iso` — właściwy test **A**;
   - `output/B_KONTROLA_ROZMIARU/B_JP_TEN_SAM_ROZMIAR.iso` — kontrolny **B**.
4. Uruchom **A od zimnego startu PPSSPP**, bez save state. Wybierz **New Game**,
   dojdź do początku misji 0-0. Nie musisz szukać konkretnych umiejętności w menu.
5. Jeżeli A się wywali, uruchom już gotowe **B** w ten sam sposób. Użyj tego samego
   folderu DLC i tych samych ustawień. Nie podmieniaj DLC między próbami.

**Nie kasuj zwykłych zapisów.** Test nie wymaga zapisywania gry ani nadpisywania sejwu.
Dwa obrazy zajmują łącznie około dwukrotność rozmiaru ISO. Ponowna budowa wymaga nowego
folderu/rozpakowania — narzędzie nie nadpisuje poprzedniego testu.

## Co dokładnie jest w A

- Pełne teksty `srwDL_Skill00.bin` z przekazanego `PL.zip`: **4932 wypełnione pola
  rekordów** i powiązane tłumaczenia config/puli, bez skracania, bez poprawiania
  błędów składania fragmentów, bez reguł angielskich skrótów. Rozmiar **224 678 B**.
- **20 opisów bazowych umiejętności z EBOOT** z tego samego przekładu (inaczej gra
  nadpisywałaby te opisy tekstem programu). Kod wykonywalny nie jest modyfikowany.
- Font PL w zaakceptowanym stylu v5: oryginalne litery ASCII z dodanymi diakrytykami.

Pozostałe człony config00, przedmioty, mechy, sceny, tytuły, tekstury, teksty programu
inne niż owe 20 opisów oraz wszystkie pliki DLC pozostają nietknięte. Początek misji
jest oryginalny, nie zawiera wcześniejszych wymyślonych dialogów testu fontu. To nie
jest jeszcze integracja całego częściowego przekładu.

## Co dokładnie jest w B

Oryginalna japońska tabela umiejętności powiększona **wyłącznie końcowymi spacjami
w opisach** do **tego samego rozmiaru 224 678 B**. Zachowuje oryginalną pulę fragmentów,
wartości liczbowe i liczbę rekordów. Wskaźniki są przeliczane aktualnym writerem
(w tym +52, którego brakowało w dawnych eksperymentach). Font i owe 20 opisów EBOOT
są identyczne jak w A — nie stanowią różnicy między wariantami.

B służy do kontroli ładowania, nie do czytania japońskich napisów: font PL zajmuje
część znaków katakany. Równy rozmiar całego pliku nie oznacza równego rozkładu
rozmiarów rekordów/puli — kontrola pomaga, ale nie dowodzi dokładnego mechanizmu alokacji.

## Co mi odpisać

Wystarczy:

- **A działa** — dociera do początku misji, bez crasha; opcjonalnie jeden screenshot;
- albo **A crash na …; B działa / B crash na …** — przy crashu screenshot komunikatu
  PPSSPP; dołącz `output/TEST_VERIFY.json`, jeśli jest.

Nie traktujemy samego crasha A jako dowodu, że wyłącznie wielkość jest winna.
Jeżeli A i B padają w tym samym miejscu, mocniej wskazuje to problem rozmiaru/układu
lub wspólnej pamięci. Jeśli A pada, a B działa, trzeba badać treść/strukturę A zamiast
od razu skracać. Jeśli A działa, obecna bramka była zbyt zachowawcza dla tego testu,
ale pozostaje jeszcze kontrola innych ekranów, zapisów i DLC.

## Zabezpieczenia i odczyt po zapisie

Tylko ten eksperymentalny skrypt pomija bramkę **216 768 B** dla Skill00; nie zmienia
jej w standardowym builderze i przywraca ją także po wyjątku. Nie ignoruje odmów
walidacji, nie psuje wskaźników i nie poprawia po cichu tłumaczenia.

`output/TEST_VERIFY.json` potwierdza odczyt polskich pól i puli, parametry i wskaźniki,
18 glifów fontu, 20 pól EBOOT, zakres zmienionych plików ISO oraz SHA256 obu obrazów.
Porównuje też oryginalne ISO przed/po budowie. Gdy budowa/kontrola zawiedzie, **nie
uruchamiaj częściowych obrazów**; prześlij komunikat i raport z folderu A.

Ta kontrola plików nie zastępuje uruchomienia w PPSSPP. Lokalny test na małym ISO
z oryginalnymi kontenerami jest sprawdzeniem writerów, nie bootowalnym obrazem gry.
