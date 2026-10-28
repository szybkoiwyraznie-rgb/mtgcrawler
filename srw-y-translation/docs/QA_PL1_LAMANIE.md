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
