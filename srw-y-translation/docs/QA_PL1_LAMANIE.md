# PL1 — zgłoszenie łamania tekstu w grze

## Obserwacja od właściciela

Po instalacji v3 gra uruchamia się; siedem screenów pokazuje niepożądane
łamanie opisów, okien i pomocy oraz pusty wiersz wewnątrz zdania. To jest
rzeczywisty test określonych ekranów, nie dowód poprawności całej gry, fontu ani
wszystkich sposobów zawijania. Screeny pozostają poza repozytorium.

## Przyczyna i decyzja

Importer rozdzielał polski tekst na tyle fragmentów, ile niepustych wierszy
zawierało JP (ewentualnie EN), dzieląc go na równe części; dodatkowo bez
rozumienia znaczenia kopiował śródtekstowe puste wiersze. Zapisany wynik dla
trybu średniego faktycznie zawierał `poziomie\n\ntrudności`, dla dialogu
potwierdzającego `Rozpocząć\ngrę w\ntrybie {0}?`, a dla opisu pilota
cięcia po około 127 znakach. Odpowiada to pozycjom widocznym na screenach.
To błąd naszego narzędzia, nie tłumacza. Na widocznym ekranie opisu silnik
łamie także dłuższy wiersz samodzielnie; sposób wyświetlania *każdego innego*
widgetu nie został dowiedziony.

Zmiana eksperymentalna v4: dla **wszystkich tabel** nie wstawiamy wewnątrz PL
podziałów ani pustych wierszy z JP/EN. Pozostawiamy istniejącą obsługę
separatorów na brzegach źródła, których ewentualne znaczenie jest nieznane.
Teksty scen Lua i ich poprzedni sposób łamania pozostają bez zmian; narracja
w tabeli `prologue` jest objęta nową regułą. Oznacza to również usunięcie
niektórych potencjalnie znaczących wewnętrznych podziałów, np. między akapitami
lub punktami: ich odtworzenie semantycznie wymaga osobnego formatowania, a nie
zgadywania po indeksie japońskiego wiersza. Wszelkie nieprzetestowane ekrany,
w szczególności narracja, zdolności, listy punktowane i napisy bitewne, wymagają
kontroli w grze. Nie twierdzimy, że wszędzie gra zawija tekst lub że się zmieści.

Odtworzony z repo plan v3 jest bajtowo identyczny z planem pobranym z wysłanej
paczki v3. Porównanie z v4: 3 582 rekordy tabel różnią się wyłącznie położeniem
separatorów (7 129 usuniętych przejść wiersza), te same słowa i tokeny, identyczne
źródła JP/EN i klucze; **4 429 wystąpień scen bez zmian**. Nadal 26 279
wypełnionych slotów, 29 873 wystąpienia oraz te same 22 korekty kontekstowe.
To porównanie nie jest testem układu w grze.

## Weryfikacja i paczka v4

- Regresje obejmują dokładne rekordy wszystkich siedmiu zgłoszonych screenów
  oraz przykład narracji. Sprawdzają zapisany tekst, **nie** to, jak gra go zawija.
- Pełne testy: **622 passed, 4 558 subtests passed**.
- Instalacja v3 → próba instalacji v4 bez cofnięcia → cofnięcie v3 → instalacja
  v4 → cofnięcie v4 na kopiach 12 oryginalnych bundli: v4 bez cofnięcia
  poprawnie odmówiła, oba cofnięcia odtworzyły oryginały, 12/12 plików i
  backupów przeszło weryfikację SHA-256. W v4 odczytano i zweryfikowano 25 444
  rekordy tabel JP, 25 303 EN i po 4 429 wystąpień scen JP/EN. Test offline
  na Linuksie; nie jest to test v4 w grze ani na Windows.
- Niezależne odtworzenie wiązania, planu, audytu i paczki: identyczne bajtowo.
  `tools/compare_pl_layout.py` sprawdza tylko zmianę separatorów i tożsamość scen.
- `SRW_Y_PATCH_PL1_v4.zip` (2 570 923 B), SHA-256
  `53182f27a01082703eabb85fe8c1405c5b2805a99b3656f7d4c2c43b7e4ca818`, Drive
  `1dLRCueGdsPOik9cybU8xmB2IRgwRkoK_`. Pobranie zwrotne identyczne bajtowo,
  CRC ZIP poprawne. Pack zawiera kod i polski plan, nie bundle gry.

**Test właściciela po instalacji:** prosimy ponownie obejrzeć te same okna, opis
pilota, help oraz narrację, a także przykładowy opis zdolności, tekst misji i
cytat bitewny. Zwrócić uwagę na brak zawijania, przycięcie, przewijanie i
wygląd list punktowanych; te zachowania nie są dowiedzione offline.

## Zgłoszenie po v4 i podejście v5

Właściciel uruchomił v4 w grze. Potwierdził, że opisy zdolności, postaci i
encyklopedia zawijają się poprawnie; równocześnie pokazał overflow w UI wyboru
trybu, opisie postaci na ekranie wyboru i narracji otwierającej oraz zgłosił
niewidoczny w całości komunikat o automatycznym zapisie. Potwierdzenie dotyczy
v4 i tych obserwacji, a nie automatycznie kolejnej wersji czy całej gry.

V5 pozostawia niezmienione potwierdzone pola opisów i wszystkie sceny Lua.
Stosuje regułę opartą o długość najdłuższej niepustej linii EN w tym samym
rekordzie w rozpoznanych rekordach systemowego UI (zapisywanie, wybór
trybów/postaci, powiązane DLC i kilka komunikatów), `dialog_text` oraz
`prologue`. Dla pojedynczych linii EN o długości co najmniej 25 znaków
przyjęto minimum 35 znaków jako **szacunkowy** zapas; dla wieloliniowych
minimum 16. Nie jest to pomiar szerokości fontu, a znaki nie są jednakowo
szerokie. Przełamania wyłącznie na granicach wyrazów, z zachowaniem tokenów;
`「 」` z komunikatu zapisu traktowane jest jako niepodzielna całość.
Modele list punktowanych powstają wyłącznie wtedy, gdy liczby znaczników listy
w EN i PL się zgadzają; wstęp oddziela się od listy semantycznie, nigdy w
środku zdania. Dane z `mission_detail`/`mission_outline` pozostały jak w v4:
nie potwierdzono ich zachowania, więc nie wnioskujemy o widgetach z samych
nazw tabel. Bez EN, z nieobsłużonymi tagami, lub przy bardzo krótkim pojedynczym
EN algorytm nie zgaduje szerokości.

Porównanie z rzeczywistym planem v4: **117 rekordów**, tylko separatory,
bez zmian słów, tokenów, JP/EN, kluczy, liczników, powtórzeń i scen. Raport
`translations/pl1/LAYOUT_V5_REVIEW.json` pokazuje każde z nich i ostrzeżenia:
**16 rekordów** ma więcej niepustych linii niż EN, w tym opisy trybu Trudnego
oraz Elity. Nie wiadomo, czy zmieszczą się pionowo; żadna treść nie została
skrócona ani ukryta. Pojedynczy długi wyraz lub token może przekroczyć szerokość
szacunkową, a podstawiane zmienne mogą zwiększyć faktyczną szerokość. To nadal
wymaga testu w grze; nie uznajemy, że v5 poprawia wszystkie ekrany.

Patcher v5 ma w głównym katalogu tylko `PATCH_PL.bat`, `COFNIJ.bat` i
`CZYTAJ_TO.md`; skrypty, zależności, plan, `STAN_PATCHA.json`, raport i
środowisko `.venv` są w `narzedzia/`. Cofnięcie starszej v4 wymaga jej własnego
`COFNIJ.bat` z jej folderu, dopiero potem instalacja v5 z nowego folderu.

Offline przeprowadzono v4 → odmowa instalacji v5 na aktywnej v4 → cofnięcie v4
→ instalacja i cofnięcie v5 na 12 rzeczywistych oryginalnych bundlach; 12/12
wyników, backupów i przywróconych oryginałów przeszło kontrolę hashy. Sprawdzono
również, że po pracy w katalogu głównym nie powstały dodatkowe pliki. BAT-y nie
były uruchomione na Windows. **628 testów i 4 558 subtestów passed**. Powtórne
wygenerowanie planu, raportów i ZIP było identyczne bajtowo.

`SRW_Y_PATCH_PL1_v5.zip`: 2 571 726 B, SHA-256
`be1a2a337719e4bcb0d644c01268ada2cb26b3af79ea0c4d4dde898e0554997d`, Drive
`1rVVwDm9pHITtjeuVePMrmt0FRDcvvvLO`. Ponowne pobranie identyczne bajtowo;
CRC ZIP poprawne. Paczka nie zawiera plików gry.
