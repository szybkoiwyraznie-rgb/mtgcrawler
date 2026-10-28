# Czytanki Y — wzór OE i zakres poprawki (w trakcie)

Właściciel wskazał `srwoe_reading_PL_00-34.zip` z Dysku jako wzór. Archiwum zawiera `srwoe_episode_00_PL.md` oraz `srwoe_mission_deployments.md`. Pierwszy jest czytelnym scenariuszem: tytuł, ostrzeżenie o dialogach warunkowych, nagłówki scen, akapity narracji, wypowiedzi `**Imię:** tekst`, cytowane bloki warunkowe, bez technicznych identyfikatorów przy każdej linijce. Drugi grupuje dane pod każdą misją: listy jednostek według stron oraz szczegółowe profile maszyn i postaci, w tym parametry, umiejętności i komendy ducha. Żądane wydanie Y ma taki sam układ i dodatkowo opisy z encyklopedii.

W `MissionData` pierwsza zwrotka obejmuje prolog `m0000_0000300` oraz siedem kompletnie przetłumaczonych misji `m0001_0000310`–`m0007_0000320`; późniejsze misje mają tylko pojedyncze przetłumaczone wiersze i nie są częścią tego wydania. Wariant `m0002_0000311` ma warunek otwarcia `M000B_FHERO`; jest misją dla bohaterki, równoległą wobec `m0001_0000310` z `M000A_MHERO`, a nie następną sceną po jej zakończeniu. W poprzednim generatorze wybór wyłącznie na podstawie obecności linii męskich daje tam błędny wynik, ponieważ w plikach są również dwie męskie kwestie. W nowym wydaniu należy uwzględnić warunek misji i zachować bohaterkę oraz kwestie wspólne. Kolejność wywołań zdarzeń i fale nie są udowodnione; nie wolno udawać, że numery tabel są chronologią bitwy.

Wzór OE pochodzi z Drive `1zEOrnN0mwgRQv4Y1T-hBlXMxTmt_yKjv`; w repo nie zmieniamy ukończonego projektu OE. Wartości gry oraz dopasowania pobieramy z istniejącego tekstowego indeksu, planu PL1 v5 i sprawdzonych powiązań encyklopedii. Zakres i dokładność tabel zostaną udokumentowane po ukończeniu.

## Gotowe wydanie

`docs/reading/pl1-oe-format/` zawiera `srwy_episode_00_PL.md` (prolog), siedem osobnych misji `01`–`07`, `srwy_mission_deployments.md` i krótkie README. Porównanie ze źródłem PL1 v5 wykazało **3586/3586** wybranych wierszy scen (61 + 342 + 389 + 508 + 582 + 579 + 535 + 590), bez braków tłumaczenia w tym zakresie. Misja 2 wybiera bohaterkę na podstawie jawnego warunku misji; dwie kwestie oznaczone jako męskie są pominięte zgodnie z zasadą wariantu. Pozostałe misje wybierają bohatera, chyba że brak jego wariantu. Imiona bohaterów i usunięcie znaczników sterujących są objaśnione w czytankach.

Dokument rozmieszczeń zawiera tylko 7 misji (bez prologu): osobne listy pól gracza, pozostałe grupy w kodach źródła, oddzielny rejestr `Entry`, karty jednostek i postaci ze statystykami, bronią, umiejętnościami, komendami ducha i opisami encyklopedii przy pierwszym wystąpieniu. Rozmieszczenie łączone jest wyłącznie po jawnych referencjach w tym samym presecie; rejestr nie dowodzi, że jednostka faktycznie wyszła na mapę. Nieznane wartości, hasła i referencje są jawne. `allyGroup` nie jest odgadywane jako wróg lub sojusznik. Nie są też dopowiadane fale ani momenty wejścia.

Opisy zdolności i duchów są pobrane z odpowiednich tabel lokalizacji. W 78 hasłach `WordDictionaryEntryTable` nie znaleziono dokładnych zgodności z ID rekordów umiejętności mechów, pilotów ani duchów, dlatego nie są sztucznie podpinane po podobieństwie nazw. Powiązanie encyklopedii pilotów i mechów pochodzi z istniejącego dowodu 11 assetów. Powtórzone identyczne części tego samego hasła pokazano raz.

Dla lektury bloki zdarzeń w ramach tej samej kompozycji przeplatane są według źródłowych numerów tekstu, z zachowaniem oryginalnego porządku wewnątrz każdego bloku. Jest to **układ redakcyjny**, nie dowód kolejności wykonywania warunkowych zdarzeń; przejście od scen do bitewnych cytatów i z powrotem ułatwia lekturę, ale nie rozstrzyga wyzwalaczy. Nie dopisano narracji i nie przetłumaczono brakujących tekstów.

## Odtworzenie

Najpierw odtwórz i zweryfikuj `local/pl1-reading/v5-plan.json` według `docs/CZYTANKI_PL1_V5.md`, następnie z katalogu `srw-y-translation/`:

```sh
python tools/build_reading_oe_style.py --source-dir data/s6-full \
  --index data/reading-index-sourcebound.json \
  --translations local/pl1-reading/v5-plan.json \
  --links data/dictionary_links.json --out local/pl1-reading/oe-style
```

Katalog wyjściowy nie może istnieć. ZIP `srwy_reading_PL1_OE_style.zip` ma SHA-256 `8d4041d076111840721e38ce4688b19b38bf1cbcd9e65e44a4fd8c115475696d`; dwa niezależne przebiegi dały identyczne bajty. ZIP sprawdzono CRC i porównano z plikami Markdown w repo. Testy całego warsztatu: **639 testów i 4558 subtestów**. To nie jest nowy patch gry ani dowód wykonania misji w grze.
