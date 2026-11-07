# SRW Y — poprawione czytanki misji PL2

[SRW_Y_CZYTANKI_PL2_POPRAWIONE_v2.zip na Drive](https://drive.google.com/file/d/12LPkwwEAxxkFmOmQdn6h7my1CQnqM4bz/view) jest wersją
poprawioną wydania `SRW_Y_CZYTANKI_PL2_POPRAWIONE.zip`, w układzie
zaakceptowanym w `SRW_Y_CZYTANKI_7_MISJI_PL_POPRAWIONE.zip`. Ma **1 271 370 B** i
SHA-256 `d7d5b0d7e91ba6483f5c5a79865a35c05f6d427a6d220659b331712be5cc115e`
(MD5 `f9a1b21a707dd4dfc2b06d3a2d791c07`); dwa niezależne przebiegi dały
identyczny ZIP, a pobranie zwrotne z Drive ma ten sam MD5 i rozmiar. Poprzednie
wydanie (`1AVkLyHkQFrRX4V-TBUPfRMg2YOs2N7Wy`) jest w koszu. **55 członów Markdown** i `receipt.json`,
bez bundli gry; komplet dokumentów tekstowych i szczegółowa recepta są również w
`docs/reading/pl2-oe-format/`.

**Co jest nowe względem poprzedniej wersji (2026-11-07):** plik
`srwy_narracja_PL.md` — **35 tekstów narracji** z tabel `prologue` (24) oraz
`prologue-DLC1`…`prologue-DLC4` (2 + 2 + 3 + 4). Sceny, misje, zestawienie i
liczniki pozostały bez zmian (`26 251` wierszy scen, `6 276` tabel / `47 160`
wierszy), więc poprzednie wydanie nie różniło się treścią misji, tylko brakiem
narracji.

Zawiera **prolog i 51 misji**: numery 1–35 oraz 37–52. Numer 36 jest poza główną listą `MissionData`, pojawia się w innych kolekcjach i brak w zwrotce jego scen; nie dopisujemy jej. Misje 1 i 2 to alternatywne początki. Przyjęto męskiego protagonistę, poza misją jawnie przeznaczoną dla bohaterki lub sytuacjami bez wariantu męskiego. Pozostałe są wariantami, a nie pewną chronologią rozgrywki.

Dobór to początkowy ciąg głównej listy, zakończony przed pierwszą misją z niepełnymi rozpoznanymi dialogami. W misji 53 jest 20 z 377 wybranych wierszy, dlatego jej i dalszych wyrywkowych scen nie przedstawiono jako pełnej czytanki. W wybranych misjach **26 251/26 251 rozpoznanych wierszy wybranego wariantu** znajduje się w zweryfikowanym planie PL2 i w plikach; inne warianty bohatera są celowo pominięte. To pokrycie rozpoznanych wierszy, nie dowód kompletności całej gry.

Dwa powiązania plików scen z misji prologu i misji 47 nie występują w dostępnym korpusie ani w indeksie obiektów tekstowych. Nie potwierdzono, czy te wskazania oznaczają istniejący tekst gry. Są jawnie zastrzeżone w README; ich brak nie jest dowodem, że coś zostało przetłumaczone. Nie ma polskich braków w rozpoznanym materiale, ale nie dowodzi to chronologii scen lub faktycznych warunków wywołania. Szczegóły per misja w `receipt.json`.

## Dlaczego brakowało monologu otwierającego (2026-11-07)

Właściciel zauważył, że gra zaczyna się monologiem („Ziemia…”, „Sześćdziesiąt
lat temu…”), a czytanka zaczynała się od prologu misji. Przyczyna nie leżała w
tłumaczeniu: te teksty to **tabela `prologue`**, a nie scena Lua. Są w pakiecie
tłumacza jako `widoki/08_pokrewne.md` i **są przetłumaczone w PL2** — wszystkie
24 elementy tabeli głównej i 11 elementów dodatków. Trafiły też do planu patchera
(`PATCH_PL2.md`), więc gra pokazuje je po polsku.

Brakowało ich w generatorze czytanek: wydanie chodziło po misjach i ich plikach
scen (`sdemo_file`/`dlgev_file`) oraz po zestawieniu jednostek, a tabeli
`prologue` nie odwiedzało w ogóle. Poprawka dodaje `narration_document()` w
`tools/build_reading_pl2.py`, który czyta wiersze tabel `prologue*` w kolejności
gry i wypisuje wyłącznie kolumnę `PL`. Kolejność w tabeli to kolejność gry;
**potwierdzone przez właściciela są tylko elementy 1–2** (start gry), dlatego
wydanie dzieli narrację na „Początek gry” (1–2), „Ciąg dalszy narracji
otwierającej” (3–11) i „Narracje późniejsze” (12–24, przypisanie do rozdziałów
niepotwierdzone) oraz „Wprowadzenia dodatków” z podziałem na DLC1–DLC4.
Niezależny weryfikator (`tools/verify_reading_pl2.py`) sprawdza, że każdy
przetłumaczony wiersz tabeli występuje dokładnie raz, że liczniki w `receipt.json`
się zgadzają i że dwa pierwsze teksty stoją na początku pliku.


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

Wydanie zawiera teraz 55 plików Markdown i `receipt.json`; ZIP w katalogu
`edition` nazywa się `SRW_Y_CZYTANKI_PL2_POPRAWIONE_v2.zip`.

Katalog `edition` nie może istnieć. Archiwum odtwarza się z oryginalnych tekstów w repozytorium; nie są potrzebne pliki binarne gry. Generator kontroluje pieczęć korpusu i zgodność planu z audytem PL2, a wszystkie źródła scen wiąże z konkretną wersją i kolejnością pliku. Zakres opiera się na zachowanym indeksie, nie na niezweryfikowanych hipotezach o zdarzeniach w grze.

Pełny zestaw testów warsztatu po zapisaniu dokumentów: **659 testów i 4558 subtestów**, wszystkie pozytywne. Weryfikator wydania raportuje `markdown_files: 55`, `narration_rows: 35`, `scene_rows: 26251`, `tables: 6276` / `table_rows: 47160`.
