# Cel projektu (stały, od użytkownika). Nie zmieniać bez polecenia użytkownika.

## Cel końcowy
1. **100% przygotowanego tekstu** ma być przetłumaczone na angielski i ponownie wstawione (reinject), czyli:
   - **Sceny fabularne**: każda linijka dialogu z imieniem mówiącego.
   - **Battle quotes**: każda z imieniem osoby wypowiadającej.
   - **Imiona** zmapowane na postacie, z opisami z encyklopedii (bio/opisy postaci).
   - **Nazwy mechów** powiązane z **nazwami broni** (mech → jego bronie).
   - **Nazwy itemów** z **opisem działania**.
   - **Helpy** oraz wszystkie **elementy UI** (prawdopodobnie stała szerokość).
   - Wszystko poza UI i (być może) imionami/nazwami: te w modelu „grow” (rozszerzanie tekstu tam, gdzie kontener na to pozwala).

2. **100% kluczy** do każdego rodzaju danych: szukać w różnych plikach i na przecięciach (np. klucz postaci łączy dialog, battle quote, dictionary, unit_list i encyklopedię; ID mecha łączy unit_list, RoboDictionary i wp_list).

## Zasady stałe (skrót; pełne w STATUS.md / AGENTS.md)
- Nie tłumaczyć, dopóki konfiguracja nie obejmuje 100% kategorii tekstu.
- Grow tam, gdzie kontener pozwala; stała szerokość tylko tam, gdzie struktura na to nie pozwala.
- Nie używać skryptu Akurasu jako źródła.
- Oryginalnych plików gry nie modyfikować; pliki gry, dane i pełne skrypty tylko w `local/` i `google_drive/` (gitignore).
- Etykiety: `[ZWERYFIKOWANE]` vs `[HIPOTEZA]`.
- Dokumentacja i komunikacja z użytkownikiem po polsku; użytkownik nie zna heksów, więc podawać liczby dziesiętne.
- Logować wszystko w `docs/EXPERIMENT_LOG.md`.
