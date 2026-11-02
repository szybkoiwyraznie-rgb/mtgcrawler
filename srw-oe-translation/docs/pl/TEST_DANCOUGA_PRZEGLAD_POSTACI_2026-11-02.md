# OE PL — przegląd postaci: Dancouga (test eksperymentalny)

## Zgłoszenie i fizyczna reprodukcja

Na zrzucie właściciela przy Shinobu widoczne są japońskie etykiety pseudonimu i aktora oraz japońskie nazwisko aktora, mimo łacińskiego imienia postaci. Oficjalny ZIP v4.10 (`df36b6036e075f6b71dc3ef3bcf5a59bc5e79e2b1c51eeb0c25538a58574613f`) rozpakowano i uruchomiono jego własny `build_translation_patch.build` na zweryfikowanych oryginałach `config01.EDAT` (`1c2213b700d32963ed79d903b10f234bb365094b3f755ab2241d4a7bb7a38431`) i `imenu01.EDAT` (`d1bf9c4d6f222efaa0115f1162c3c0dc88bb725289127f7656d61004b9025325`). Izolowana budowa **nie jest czystym pełnym buildem**: bez ISO sygnalizuje brak czcionki, a każda kopia zgłasza po 8 problemów dotyczących obcych kluczy słownika robotów. Fizyczne wartości w powstałym słowniku postaci można jednak odczytać niezależnie od tych ostrzeżeń.

Wynik `srwDL_CharaDictionary01.bin`: 73 rekordy. W wyniku `config01` pole 4 (pseudonim) i 5 (aktor) zawierają japońskie znaki w 73/73 rekordach; odpowiednie pola w wyniku `imenu01` mają 0/73 takich wystąpień. Dla Shinobu: config `愛称：Shinobu` i `声優：矢尾一樹`, imenu `Pseudonim: Shinobu` i `Głos: Kazuki Yao`. Ten config odpowiada treści zrzutu; to silna przesłanka, **nie ślad wykonania ani potwierdzenie dokładnie użytego pliku**. Nazwiska pozostałych pilotów Dancougi istnieją w polskim pakiecie. Przyczyna w kodzie budowy to ostrożna blokada kategorii dla configNN; dla config19 jest oddzielny, wcześniej zaakceptowany przez właściciela wyjątek.

## Dlaczego tylko eksperyment

Historyczne testy v12A i v14 na `config01–08` po szerokiej zmianie słowników kończyły się awarią; dokładnego winnego pola nie wyizolowano. Nie zdejmować blokady globalnie i nie obiecywać stabilności z samego odczytu. To nie jest brak tłumaczenia u tłumacza. Zob. `docs/QA_MASAKI_V17.md` i wcześniejszy log.

`tools/dancouga_viewer_experiment.py` jest **osobnym, nieautomatycznym testem**, nie jest częścią normalnej budowy. Przyjmuje aktywny zbudowany `config01.EDAT` oraz zmaterializowane tłumaczenia PL; weryfikuje poprzednie wartości i zmienia tylko istniejące pola 4/5 czterech rekordów 3301/3305/3308/3311. Nie zmienia pól 1/11, innych rekordów ani innych członów kontenera; zawartość tych członów i słownika jest sprawdzana po ponownym odczycie. Tworzy plik wynikowy i kopię wejścia w **nowym folderze**, nigdy nie nadpisuje aktywnego pliku. Jeśli wejście nie pasuje, odmawia. Nie służy do stosowania bezpośrednio na czystym oryginale.

Na lokalnej, izolowanej bazie v4.10: 8 komórek zmienionych, dokładnie odpowiadają istniejącym tłumaczeniom z imenu (8/8); 19 pozostałych członów bez zmian, słownik 15710 → 15756 B, cały kontener 247936 → 247936 B. Bazowe i testowe binaria pozostają prywatne. To nie dowód stabilności, zgodności graficznej ani potwierdzenie stanu instalacji właściciela.

`tools/build_dancouga_experiment.py` buduje opcjonalny ZIP z repozytorium, bez plików gry. Posiada BAT ze wskazaniem pliku przez okno i instrukcję wykonania kopii, podmiany jednego pliku oraz powrotu do poprzedniego; nie instaluje zmian automatycznie. Po wyniku właściciela można rozważyć zakres i bezpieczny sposób poprawy innych postaci, ale test czterech nie potwierdza pozostałych ani wszystkich rozdziałów.

## Opcjonalny pakiet testowy

[Wyłącznie eksperymentalny ZIP](https://drive.google.com/file/d/1aBmG-Zgsqi8bYLsrMk26p6HZtZ14KKgd/view), 213386 B, SHA-256 `131c0bd49d1047915c6a4c2143fa3e6290c1bcaa9f954cf5a9fae4dac57718bd`. Suma Drive i pobrana kopia zgodne bajtowo. Reprodukcja z repo: `python3 tools/build_dancouga_experiment.py --out local/.../srw-oe-dancouga-test.zip`; 28 członów, bez binariów gry, manifest hashów i CRC sprawdzone. Uruchomiono skrypt wyciągnięty z gotowego ZIP na lokalnej bazie z v4.10, sprawdzono odczyt, zgodność wyniku i kopii wejściowej; wynik bajtowo taki sam jak z repozytoryjnego skryptu. Brak testu BAT pod Windows, pełnej budowy ISO i gry w PPSSPP.

## Wynik właściciela i osobny test Alana

Właściciel zgłosił, że po wąskim teście gra działa bez crasha, a Shinobu, Sara, Ryo i Masato mają polskie podpisy. To potwierdza te widoczne pola i zgłoszony przebieg, nie wszystkie misje i pozostałe rekordy. Na zrzucie dla Alana imię na liście pozostało japońskie; jego dwa podpisy również są japońskie. Poprzedni test nie modyfikował rekordu 3315. Niezależny odczyt izolowanej bazy v4.10 oraz odtworzonego testu pokazał w obu: slot 11 `アラン`, slot 4 `愛称：Alan`, slot 5 `声優：田中秀幸`. Nie dysponujemy zrzutem Alana sprzed testu, więc nie twierdzimy, kiedy po raz pierwszy widniało japońskie imię na liście. W imenu01 zapisano już `Alan`, `Pseudonim: Alan`, `Głos: Hideyuki Tanaka`.

Osobny `tools/alan_viewer_experiment.py` wymaga aktywnego pliku **po pierwszym teście**, sprawdza komplet dotychczas poprawionych wartości czterech postaci i rusza tylko istniejące trzy pola Alana (4/5/11). Pozostałe rekordy i człony weryfikuje, tworzy kopię wejścia, nie podmienia pliku gry. Komórka 11 config01 nie była objęta poprzednim pozytywnym testem — cały wariant nadal wymaga osobnego potwierdzenia w grze.

Na odtworzonej lokalnie bazie z pierwszego testu: 3/3 poprawione pola odpowiadają istniejącym wpisom imenu01; 19 pozostałych członów niezmienionych, słownik 15756 → 15766 B, kontener 247936 → 247936 B. Oryginalna baza była budowana w izolacji z ograniczeniami opisanymi powyżej. Własnego pliku aktywnego właściciela nie porównano i niczego mu nie nadpisano. Nie wykonano testu PPSSPP/Windows.
