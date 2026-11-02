# OE PL — przegląd postaci: Dancouga (test eksperymentalny)

## Zgłoszenie i fizyczna reprodukcja

Na zrzucie właściciela przy Shinobu widoczne są japońskie etykiety pseudonimu i aktora oraz japońskie nazwisko aktora, mimo łacińskiego imienia postaci. Oficjalny ZIP v4.10 (`df36b6036e075f6b71dc3ef3bcf5a59bc5e79e2b1c51eeb0c25538a58574613f`) rozpakowano i uruchomiono jego własny `build_translation_patch.build` na zweryfikowanych oryginałach `config01.EDAT` (`1c2213b700d32963ed79d903b10f234bb365094b3f755ab2241d4a7bb7a38431`) i `imenu01.EDAT` (`d1bf9c4d6f222efaa0115f1162c3c0dc88bb725289127f7656d61004b9025325`). Izolowana budowa **nie jest czystym pełnym buildem**: bez ISO sygnalizuje brak czcionki, a każda kopia zgłasza po 8 problemów dotyczących obcych kluczy słownika robotów. Fizyczne wartości w powstałym słowniku postaci można jednak odczytać niezależnie od tych ostrzeżeń.

Wynik `srwDL_CharaDictionary01.bin`: 73 rekordy. W wyniku `config01` pole 4 (pseudonim) i 5 (aktor) zawierają japońskie znaki w 73/73 rekordach; odpowiednie pola w wyniku `imenu01` mają 0/73 takich wystąpień. Dla Shinobu: config `愛称：Shinobu` i `声優：矢尾一樹`, imenu `Pseudonim: Shinobu` i `Głos: Kazuki Yao`. Ten config odpowiada treści zrzutu; to silna przesłanka, **nie ślad wykonania ani potwierdzenie dokładnie użytego pliku**. Nazwiska pozostałych pilotów Dancougi istnieją w polskim pakiecie. Przyczyna w kodzie budowy to ostrożna blokada kategorii dla configNN; dla config19 jest oddzielny, wcześniej zaakceptowany przez właściciela wyjątek.

## Dlaczego tylko eksperyment

Historyczne testy v12A i v14 na `config01–08` po szerokiej zmianie słowników kończyły się awarią; dokładnego winnego pola nie wyizolowano. Nie zdejmować blokady globalnie i nie obiecywać stabilności z samego odczytu. To nie jest brak tłumaczenia u tłumacza. Zob. `docs/QA_MASAKI_V17.md` i wcześniejszy log.

`tools/dancouga_viewer_experiment.py` jest **osobnym, nieautomatycznym testem**, nie jest częścią normalnej budowy. Przyjmuje aktywny zbudowany `config01.EDAT` oraz zmaterializowane tłumaczenia PL; weryfikuje poprzednie wartości i zmienia tylko istniejące pola 4/5 czterech rekordów 3301/3305/3308/3311. Nie zmienia pól 1/11, innych rekordów ani innych członów kontenera; zawartość tych członów i słownika jest sprawdzana po ponownym odczycie. Tworzy plik wynikowy i kopię wejścia w **nowym folderze**, nigdy nie nadpisuje aktywnego pliku. Jeśli wejście nie pasuje, odmawia. Nie służy do stosowania bezpośrednio na czystym oryginale.

Na lokalnej, izolowanej bazie v4.10: 8 komórek zmienionych, dokładnie odpowiadają istniejącym tłumaczeniom z imenu (8/8); 19 pozostałych członów bez zmian, słownik 15710 → 15756 B, cały kontener 247936 → 247936 B. Bazowe i testowe binaria pozostają prywatne. To nie dowód stabilności, zgodności graficznej ani potwierdzenie stanu instalacji właściciela.

`tools/build_dancouga_experiment.py` buduje opcjonalny ZIP z repozytorium, bez plików gry. Posiada BAT ze wskazaniem pliku przez okno i instrukcję wykonania kopii, podmiany jednego pliku oraz powrotu do poprzedniego; nie instaluje zmian automatycznie. Po wyniku właściciela można rozważyć zakres i bezpieczny sposób poprawy innych postaci, ale test czterech nie potwierdza pozostałych ani wszystkich rozdziałów.
