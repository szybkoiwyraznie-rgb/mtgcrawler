# Audyt 479 odrzuconych grup PL1 — w toku

Zadanie właściciela: przeanalizować każdy z 479 odrzuconych slotów i wszystkie
ich powtórzenia, rozdzielić błędy narzędzi od rzeczywistych problemów,
przygotować informację dla tłumacza i patch ze 100% pokryciem otrzymanych
wypełnionych PL. Nie używać „100%” jako synonimu kompletnego tłumaczenia gry.

Pierwsze sprawdzenie oryginalnego `QUARANTINE.json`: **479 slotów, 531
zarejestrowanych diagnostyk**; każda diagnostyka jest przypisana do konkretnego
źródłowego slotu i docelowego elementu. Liczba diagnostyk nie jest liczbą
niezależnych błędów — jeden slot może mieć wiele odrzuconych powtórzeń.

Wykryte błędy warsztatu wymagające poprawy i testów:

- Parser tokenów chwytał `$kwb` razem z następującym polskim słowem, np.
  `$kwbVAL`, podczas gdy źródłowy znacznik to `$kwb` i tekst to `VAL`. To
  generuje dziesiątki fałszywych błędów; tłumacz zachował znacznik.
- Parser uznawał zwykłe `[Elita]` lub `[Auto]` za tokeny, mimo że zmierzone
  tokeny zastępcze mają postać `[p1:]`, `[r1:]`, `[i:]`, `[protagonist]`.
- Jedno z „pustych źródeł” ma puste JP, ale niepusty EN; to samo dotyczy
  wszystkich **140** diagnostyk tej kategorii. Nie wolno traktować ich jak
  pustych w obu językach. Należy obsłużyć istnienie/brak każdego klucza w
  docelowym języku oraz jawnie opisać, skąd pochodzi tekst referencyjny.
- Liczba **260 diagnostyk U+201C** oznacza niezatwierdzony przez narzędzie
  cudzysłów typograficzny, a nie udowodniony brak znaku w fontach gry.

Stan: żadnych zmian w walidatorze ani w patchu; szczegółowa klasyfikacja,
korekty, reguły fontu i weryfikacja w toku. Nie deklarować ukończenia.
