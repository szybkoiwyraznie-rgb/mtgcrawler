# Kontrola czytelności i braków zestawienia jednostek — zakończona

Właściciel zaakceptował scenariusze i wskazał błędy w `srwy_mission_deployments.md`. Poprawiono wyłącznie zestawienie i jego generator; wszystkie osiem plików scenariusza porównano bajt po bajcie z poprzednim wydaniem — są identyczne.

## Zwrotka i oryginalne tabele

- Audyt zwrotki PL1: poza `02_cytaty_bitewne.md` jest pięć pustych slotów, ale jeden to rekord bez tekstu JP i EN, cztery pozostałe to wewnętrzne identyfikatory `OptionParts_Name_*` (wypełnionych 8802 pozostałych slotów widoków). Nie są to brakujące zdania do tłumaczenia.
- Poprzednie zestawienie zawierało 60 wystąpień `[BRAK PL]`, obejmujących 50 różnych adresów encyklopedii. Sprawdzono wszystkie: żaden nie ma odpowiedniego wiersza w oryginalnej tabeli. Przykłady `dic_text_robot/014d369b:97a0b007` i `dic_text_pilot-DLC4/00633a0d:38028079` są zarezerwowanymi kluczami Shared Data, a nie wierszami z pustym tłumaczeniem.
- Niezależnie odczytano oryginalne bundle, używając `table_rows` z `tools/restore_s6_full.py`: **44 344 wiersze** są identyczne z `data/s6-full/tables.jsonl`; 288 obiektów tabel, zero problemów parsera i zero brakujących par tabel. Przebieg korzystał z binarnych katalogów `local/reading-research/{srw_y_text,srw_y_tekst,srw_y_dlc_bundle,srw_y_free_patch}`; raport lokalny `local/pl1-reading/table-source-audit.json`. Binarne materiały nie są częścią repozytorium.
- Generator najpierw sprawdza istnienie rekordu. Rezerwację klucza bez wiersza pomija; jeśli nie odczytano całej tabeli, zgłasza problem; jeśli istnieje niepusty tekst źródłowy bez PL, wyświetla `[Brak polskiego opisu]` i odnotowuje brak. Testy syntetyczne sprawdzają wszystkie te przypadki. W rzeczywiście wykorzystanym zakresie nowe wydanie ma **0 braków PL**.

## Powiązania i rzeczywisty zakres encyklopedii

- `RRAZ_G` i `ZERO_G` występują jako jawne rejestracje w jednym presecie misji 1, a potem jako referencje w drugim. Generator rozpoznaje obecnie powiązania w pozostałych presetach tej samej misji. Zbadano też 13 oryginalnych grafów siedmiu misji; nie traktujemy podobieństwa identyfikatorów jako dowodu statystyk.
- Dla referencji domyślnej generator wymaga jawnego pola `defaultReferenceId` oraz zgodności nazw wszystkich kandydatów. W przypadku kilku jawnych kandydatów z presetów również wymaga zgodności nazw; różne nazwy pozostają nierozstrzygnięte. Bazowy profil nie dowodzi faktycznego stanu, ulepszeń czy wariantu zapisanego w grze. Przy kilku rekordach o tej samej nazwie podano odrębne, ponumerowane warianty danych. Zestawienie nie ma obecnie nierozpoznanych referencji, nie dowodzi jednak kolejności fal ani wykonania zdarzeń w grze.
- Przeanalizowano wszystkie 25 starych oznaczeń braku hasła. Jedno dotyczyło Show Kamui: jego wariant twarzy ma jawne odwołanie domyślne do twarzy z hasłem i zgodne oba klucze nazwy, więc opis został podłączony. Sześć dotyczyło postaci dialogowej „Obywatel”, bez osobnego hasła. Pozostałe 18 dotyczyło rekordów niemających własnego powiązanego hasła, m.in. jednostek `CNTN`, `GTERD2`, `DYNDV`, `DYNSL`, `DYNST`, `DYNWG`, `ARKGO`, `KARNGO`, `KRIKGO` oraz generycznych postaci i SI. Część nazw jest celowo ukryta w danych gry jako `???`; nie jest to brak tłumaczenia. Bez dowodu nie dopisujemy im opisów z innych haseł.
- Tam, gdzie źródłowe powiązanie hasła nie istnieje, zestawienie podaje informację o braku osobnego opisu, a nie o braku polskiego tłumaczenia. Powtórzenia tej informacji dotyczą wielokrotnych wystąpień i dodatkowo rozpoznanych rekordów w różnych misjach. Opisy zdolności i duchów nadal pochodzą z ich własnych rekordów lokalizacyjnych; brak dowodu na ich dokładne połączenie z osobnymi hasłami słownika.

## Kontrola wydania

- Wszystkie **453 tabele, 3371 wierszy** mają wyrównane kolumny w surowym Markdown, włącznie z separatorem i wyrównaniem liczb. W dokumencie nie ma ukośników odwrotnych ani identyfikatorów zapisywanych w kodzie. Pozostawiono 25 wystąpień zwykłego ukośnika w rzeczywistych ułamkach i wzorach matematycznych, np. `1/4`.
- ZIP zawiera prolog, siedem misji, zestawienie jednostek i README. Test CRC poprawny, a pliki w archiwum są identyczne z osobnymi plikami wyjściowymi. Dwie niezależne regeneracje dały ten sam SHA-256: `1015adab3066080b2aa4abee73706a24685bc0182546d682410f1052fa3e74a4`.
- Pełny zestaw testów: **645 testów i 4558 subtestów**, wszystkie zaliczone. To wydanie czytelnicze, nie nowa poprawka gry ani wynik testu w samej grze.
