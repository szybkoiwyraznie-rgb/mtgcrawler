# SRW Y — poprawione czytanki misji PL2

## Dostawa i zakres

[SRW_Y_CZYTANKI_PL2_POPRAWIONE.zip na Drive](https://drive.google.com/file/d/1AVkLyHkQFrRX4V-TBUPfRMg2YOs2N7Wy/view) jest nową wersją zaakceptowanego układu `SRW_Y_CZYTANKI_7_MISJI_PL_POPRAWIONE.zip`. Ma 1 267 844 B i SHA-256 `9d5ff8f3fc4acebfb8be66f32dcc3f827c2d2f4e5f04ba9fdc57b6039805d730`; po pobraniu z Drive jest identyczny bajtowo. Dwa niezależne przebiegi dały identyczny ZIP. 54 człony Markdown bez bundli gry; komplet dokumentów tekstowych i szczegółowa recepta są również w `docs/reading/pl2-oe-format/`.

Zawiera **prolog i 51 misji**: numery 1–35 oraz 37–52. Numer 36 jest poza główną listą `MissionData`, pojawia się w innych kolekcjach i brak w zwrotce jego scen; nie dopisujemy jej. Misje 1 i 2 to alternatywne początki. Przyjęto męskiego protagonistę, poza misją jawnie przeznaczoną dla bohaterki lub sytuacjami bez wariantu męskiego. Pozostałe są wariantami, a nie pewną chronologią rozgrywki.

Dobór to początkowy ciąg głównej listy, zakończony przed pierwszą misją z niepełnymi rozpoznanymi dialogami. W misji 53 jest 20 z 377 wybranych wierszy, dlatego jej i dalszych wyrywkowych scen nie przedstawiono jako pełnej czytanki. W wybranych misjach **26 251/26 251 rozpoznanych wierszy wybranego wariantu** znajduje się w zweryfikowanym planie PL2 i w plikach; inne warianty bohatera są celowo pominięte. To pokrycie rozpoznanych wierszy, nie dowód kompletności całej gry.

Dwa powiązania plików scen z misji prologu i misji 47 nie występują w dostępnym korpusie ani w indeksie obiektów tekstowych. Nie potwierdzono, czy te wskazania oznaczają istniejący tekst gry. Są jawnie zastrzeżone w README; ich brak nie jest dowodem, że coś zostało przetłumaczone. Nie ma polskich braków w rozpoznanym materiale, ale nie dowodzi to chronologii scen lub faktycznych warunków wywołania. Szczegóły per misja w `receipt.json`.

## Zestawienie, nazwy i kontrola

`srwy_mission_deployments.md` zachowuje format poprzedniej poprawki: strony, rejestr, bazowe profile mechów, broni, pilotów, umiejętności, rozkazów i opisy encyklopedii przy pierwszym wystąpieniu. Źródłowe numery scen są porządkowane redakcyjnie, nie dowodzą kolejności wydarzeń. Dynamika jednostek i faktyczny stan zapisu pozostają nieustalone.

Nowe misje ujawniły odniesienia do twarzy/postaci zamiast rekordu parametrów pilota. Nazwy odczytano z dokładnych rekordów `listFacialSettingData`, bez przypisywania niepotwierdzonych statystyk. Różne jawne rekordy dla tej samej referencji rozpisano jako warianty „lub”, a nie wybrano jednego; lista nie wyklucza innych stanów gry. Dwa rekordy rejestru nie podają pilota — oznaczono to bez zgadywania. Ostatecznie **zero** oznaczeń braku tłumaczenia, nierozpoznanej postaci lub jednostki; w indeksie mogą jednak istnieć inne nieudowodnione zależności.

Misja 10 zawiera w danych odwołanie do nieistniejącego klucza tytułu. Etykieta w zatwierdzonym szablonie v8 wiąże ją z unikalnym japońskim tytułem (metoda `mission_map.join_titles`); ścisła poprawka w generatorze sprawdza adres, JP i EN tego wiersza i używa przekładu „Zagadka Campbellian”. Nie jest to dopasowanie po podobieństwie numerów.

Niezależny weryfikator sprawdził 26 251 wierszy względem planu, CRC i identyczność członów ZIP, **6 276 wyrównanych tabel / 47 160 wierszy tabel**, zero japońskich/chińskich znaków, zero surowych backslashy w zestawieniu, zero braków PL. 8/8 poprzednich scenariuszy jest identycznych po pominięciu dwóch zmienionych not o wydaniu; treść scen się nie zmieniła. Są to kontrole danych, nie test w grze. Tekst może zawierać nazwy własne i angielskie frazy pozostawione przez tłumacza.

## Odtwarzanie i kontrola

W katalogu `srw-y-translation/`, Python 3.10+ (zależności warsztatu jak w `docs/PATCH_PL2.md`):

```sh
mkdir -p local/pl2-reading
python tools/bind_v8_return.py --input translations/pl2/PL --output local/pl2-reading/manifest.json
python tools/audit_full_return.py --manifest local/pl2-reading/manifest.json --input translations/pl2/PL --source-dir data/s6-full --corrections translations/pl2/CORRECTIONS.json --historical-quarantine translations/pl2/QUARANTINE_PRECHECK.json --return-label PL2 --output-plan local/pl2-reading/plan.json --output-report local/pl2-reading/audit.json
cmp local/pl2-reading/audit.json translations/pl2/AUDIT_PL2.json
python tools/build_reading_pl2.py --source-dir data/s6-full --index data/reading-index-sourcebound.json --translations local/pl2-reading/plan.json --audit translations/pl2/AUDIT_PL2.json --links data/dictionary_links.json --out local/pl2-reading/edition
python tools/verify_reading_pl2.py --source-dir data/s6-full --index data/reading-index-sourcebound.json --translations local/pl2-reading/plan.json --links data/dictionary_links.json --edition local/pl2-reading/edition
```

Katalog `edition` nie może istnieć. Archiwum odtwarza się z oryginalnych tekstów w repozytorium; nie są potrzebne pliki binarne gry. Generator kontroluje pieczęć korpusu i zgodność planu z audytem PL2, a wszystkie źródła scen wiąże z konkretną wersją i kolejnością pliku. Zakres opiera się na zachowanym indeksie, nie na niezweryfikowanych hipotezach o zdarzeniach w grze.

Pełny zestaw testów warsztatu po zapisaniu dokumentów: **657 testów i 4558 subtestów**, wszystkie pozytywne.
