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
