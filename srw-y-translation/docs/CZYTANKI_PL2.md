# SRW Y — poprawione czytanki misji PL2

[SRW_Y_CZYTANKI_PL2_POPRAWIONE_v5.zip na Drive](https://drive.google.com/file/d/1XxCsJwHzNZRDG6oW4n2MIP4VduibdEMm/view)
(`1XxCsJwHzNZRDG6oW4n2MIP4VduibdEMm`) jest wersją poprawioną wydania
`SRW_Y_CZYTANKI_PL2_POPRAWIONE.zip`, w układzie zaakceptowanym w
`SRW_Y_CZYTANKI_7_MISJI_PL_POPRAWIONE.zip`. Ma **1 267 677 B** i SHA-256
`693809c5afb2b9880cc3b271b29f3b23c7e70ee52982db6073779d3b27b9d0f3`
(MD5 `6d636a1df28f73346e13e6da73d362d9`); dwa niezależne przebiegi dały
identyczny ZIP, a przebudowa od zera — po skasowanym katalogu `local/`
(manifest → audyt → wydanie) — odtworzyła ten sam plik i bajtowo te same
dokumenty. Poprzednie wydanie `SRW_Y_CZYTANKI_PL2_POPRAWIONE_v3.zip`
(`1_w1e-zvO1r8FxTVdzk7dklzTFyTlhC3R`) zostaje w historii jako poprzedni układ
scen. To **54 pliki Markdown** i `receipt.json`, bez bundli gry; komplet
dokumentów tekstowych i szczegółowa recepta są również w
`docs/reading/pl2-oe-format/`.

## Czwarta wersja (2026-11-06): układ scen i kolejność wymian

Właściciel zgłosił trzy rzeczy w czytaniu scen: podwójne łamania w dialogach,
nagłówki strukturalne (`## Sceny fabularne`, `### Wymiana sytuacyjna`) oraz
wymiany sytuacyjne wmieszane w dialogi bitewne. Wszystkie trzy poprawiono
strukturalnie, nie ręcznie:

* **Scena fabularna czyta się ciągiem:** kolejne kwestie stoją w kolejnych
  liniach, rozdzielone **pojedynczym** `\n` (wcześniej `\n\n`). Wewnętrzne
  podwójne łamanie tłumacza zwijamy do `\n`; własnego zawijania nie dokładamy.
* **Wymiana sytuacyjna ma każdą kwestię jako osobny akapit:** `>` i pusta
  linia między kwestiami (`\n\n`), tak jak w zaakceptowanym układzie PL1.
* **Nagłówki strukturalne zniknęły.** Zostały wyłącznie znaczniki miejsca
  w świecie gry (`### Rezydencja Franburnettów`) i sekcje narracji.
* **Kolejność wymian oparto na grafach scenariusza**, które właściciel
  udostępnił w `SRW_Y_GRAFY.zip` (12 726 061 B, SHA-256
  `8c6451349ef1e80037a648af9f4ee34287086d5e800fc549c59405a4c8563156`;
  plik nie jest w repozytorium). Z 219 grafów odczytano 4 157 tabel dialogowych:
  **995 startowych** (`MapStartUnit`/`MapInitUnit`), **2 375 zdarzeniowych**
  i **787 w bloku oczyszczenia pola** (`StageClearUnit`/`MapClearUnit`).
  Jedna tabela jest w dwóch różnych blokach i celowo została bez przypisania.
  Kolejność zmieniamy **tylko wewnątrz jednej nieprzerwanej serii wymian**
  w danej kompozycji: najpierw rozmowy startowe, potem zdarzeniowe, a blok
  oczyszczenia pola na końcu serii. Sceny zostają na swoich miejscach
  źródłowych. Dzięki temu rozmowa po wygranej (np. Gauma/Cross o wstrząsach)
  stoi bezpośrednio przed sceną rezydencji, a nie w środku dialogów bitewnych.
  Nie twierdzimy, że znamy warunki wejścia pozostałych wymian.

Przykład właściciela z misji 1 jest teraz odtworzony dokładnie: wymiana Gaumy
i Crossa o wstrząsach (`cse20_0001_0000310a_dlgev`, tabela 12) jest w grafie
**w bloku oczyszczenia pola**, więc stoi na końcu serii wymian — bezpośrednio
przed sceną `### Rezydencja Franburnettów` (`…_sdemo`, tabela 2), która startuje
w bloku mapy. Wcześniej ta rozmowa była w środku dialogów bitewnych
Zero/Cross/Lumenus i to było „pomieszanie”. `receipt.json`:
`phase_attribution: true`, `clear_tables_moved: 241`, `chronology_verified:
false` — potwierdzone jest przypisanie do bloku startu i oczyszczenia pola,
nie pełna chronologia ani warunki zdarzeń.

**Co było nowe w v3 (2026-11-07):** poprawka układu
narracji, na którą wskazał właściciel. Wszystkie **35 tekstów narracji** z tabel
`prologue` (24) i `prologue-DLC1`…`prologue-DLC4` (2 + 2 + 3 + 4) są teraz
**w plikach misji, w miejscu, w którym gra je odtwarza**: otwarcie gry na
początku prologu, epilogi rozdziałów na końcu ostatniej misji rozdziału, a teksty
rozdziałów i dodatków nieobjętych wydaniem na końcu ostatniego pliku. Osobny plik
`srwy_narracja_PL.md` i numerowanie `**12.**` zostały usunięte. Sceny, misje,
zestawienie i liczniki pozostały bez zmian (`26 251` wierszy scen, `6 276` tabel /
`47 160` wierszy).

Zawiera **prolog i 51 misji**: numery 1–35 oraz 37–52. Numer 36 jest poza główną listą `MissionData`, pojawia się w innych kolekcjach i brak w zwrotce jego scen; nie dopisujemy jej. Misje 1 i 2 to alternatywne początki. Przyjęto męskiego protagonistę, poza misją jawnie przeznaczoną dla bohaterki lub sytuacjami bez wariantu męskiego. Pozostałe są wariantami, a nie pewną chronologią rozgrywki.

Dobór to początkowy ciąg głównej listy, zakończony przed pierwszą misją z niepełnymi rozpoznanymi dialogami. W misji 53 jest 20 z 377 wybranych wierszy, dlatego jej i dalszych wyrywkowych scen nie przedstawiono jako pełnej czytanki. W wybranych misjach **26 251/26 251 rozpoznanych wierszy wybranego wariantu** znajduje się w zweryfikowanym planie PL2 i w plikach; inne warianty bohatera są celowo pominięte. To pokrycie rozpoznanych wierszy, nie dowód kompletności całej gry.

Dwa powiązania plików scen z misji prologu i misji 47 nie występują w dostępnym korpusie ani w indeksie obiektów tekstowych. Nie potwierdzono, czy te wskazania oznaczają istniejący tekst gry. Są jawnie zastrzeżone w README; ich brak nie jest dowodem, że coś zostało przetłumaczone. Nie ma polskich braków w rozpoznanym materiale, ale nie dowodzi to chronologii scen lub faktycznych warunków wywołania. Szczegóły per misja w `receipt.json`.

## Gdzie trafiła narracja (2026-11-07)

Właściciel zauważył, że gra zaczyna się monologiem („Ziemia…”, „Sześćdziesiąt
lat temu…”), a czytanka zaczynała się od prologu misji. Przyczyna nie leżała w
tłumaczeniu: te teksty to **tabela `prologue`**, a nie scena Lua. Są
przetłumaczone w PL2 i trafiają do planu patchera (`PATCH_PL2.md`), więc gra
pokazuje je po polsku. Brakowało ich tylko w generatorze czytanek.

Przypisanie do misji odczytano z nazw kluczy w tabelach gry, a nie z numeracji
tabeli. `Prologue_1x`/`Prologue_2x` to wstawki otwarcia, `Epilog_<rozdział><część>`
to epilog rozdziału, `Epilog_END` to zakończenie gry, a tabele DLC mają własne
prefiksy. Dlatego wydanie:

* otwiera prolog (`srwy_episode_00_PL.md`) sekcją **Narracja otwierająca** —
  11 akapitów od „Ziemia…” do „…kończę dziś czternaście lat.”, czyli dokładnie
  przed pierwszymi scenami misji 1;
* kończy ostatnią misję rozdziału sekcją **Narracja kończąca rozdział N** —
  misja 7 (rozdział 1), 35 (rozdział 2) i 52 (rozdział 3);
* umieszcza `Epilog_END` i teksty dodatków na końcu ostatniego pliku
  (`srwy_episode_52_PL.md`) w sekcji **Narracje poza tym wydaniem**, z podziałem
  na rozdziały 4–6, zakończenie gry i dodatki 1–4. Rozdziały 2–7 są w tym
  wydaniu niepełne (brak m.in. misji 53+), więc ich epilogi nie mają do czego
  przylgnąć; nic nie zgadujemy i nie podpinamy ich pod przypadkową misję.

Numeracja akapitów (`**12.**`, `**13.**`…) została usunięta — nie niosła treści.
Niezależny weryfikator (`tools/verify_reading_pl2.py`) sprawdza, że każdy
przetłumaczony wiersz tabeli narracji występuje w wydaniu dokładnie raz, w pliku
wskazanym przez klucz gry, w kolejności gry, że otwarcie stoi przed
pierwszą sceną prologu i że liczniki w `receipt.json`
(`narration.opening/chapters/appendix/rows`) się zgadzają.

## Zestawienie, nazwy i kontrola

`srwy_mission_deployments.md` zachowuje format poprzedniej poprawki: strony, rejestr, bazowe profile mechów, broni, pilotów, umiejętności, rozkazów i opisy encyklopedii przy pierwszym wystąpieniu. Źródłowe numery scen są porządkowane redakcyjnie, nie dowodzą kolejności wydarzeń. Dynamika jednostek i faktyczny stan zapisu pozostają nieustalone.

Nowe misje ujawniły odniesienia do twarzy/postaci zamiast rekordu parametrów pilota. Nazwy odczytano z dokładnych rekordów `listFacialSettingData`, bez przypisywania niepotwierdzonych statystyk. Różne jawne rekordy dla tej samej referencji rozpisano jako warianty „lub”, a nie wybrano jednego; lista nie wyklucza innych stanów gry. Dwa rekordy rejestru nie podają pilota — oznaczono to bez zgadywania. Ostatecznie **zero** oznaczeń braku tłumaczenia, nierozpoznanej postaci lub jednostki; w indeksie mogą jednak istnieć inne nieudowodnione zależności.

Misja 10 zawiera w danych odwołanie do nieistniejącego klucza tytułu. Etykieta w zatwierdzonym szablonie v8 wiąże ją z unikalnym japońskim tytułem (metoda `mission_map.join_titles`); ścisła poprawka w generatorze sprawdza adres, JP i EN tego wiersza i używa przekładu „Zagadka Campbellian”. Nie jest to dopasowanie po podobieństwie numerów.

Niezależny weryfikator sprawdził 26 251 wierszy względem planu, CRC i identyczność członów ZIP, **6 276 wyrównanych tabel / 47 160 wierszy tabel**, zero japońskich/chińskich znaków, zero surowych backslashy w zestawieniu, zero braków PL. 8/8 poprzednich scenariuszy ma **ten sam zestaw kwestii** co zaakceptowana zwrotka PL1; zmienił się tylko układ (bez nagłówków strukturalnych, pojedyncze łamania, przeniesione wymiany po wygranej), więc test porównuje kwestie, nie bajty. Są to kontrole danych, nie test w grze. Tekst może zawierać nazwy własne i angielskie frazy pozostawione przez tłumacza.

## Odtwarzanie i kontrola

W katalogu `srw-y-translation/`, Python 3.10+ (zależności warsztatu jak w `docs/PATCH_PL2.md`):

```sh
mkdir -p local/pl2-reading
python tools/bind_v8_return.py --input translations/pl2/PL --output local/pl2-reading/manifest.json
python tools/audit_full_return.py --manifest local/pl2-reading/manifest.json --input translations/pl2/PL --source-dir data/s6-full --corrections translations/pl2/CORRECTIONS.json --historical-quarantine translations/pl2/QUARANTINE_PRECHECK.json --return-label PL2 --output-plan local/pl2-reading/plan.json --output-report local/pl2-reading/audit.json
cmp local/pl2-reading/audit.json translations/pl2/AUDIT_PL2.json
python tools/build_scene_phases.py --archive /ścieżka/SRW_Y_GRAFY.zip --out data/scene_phases_y.json  # opcjonalnie: dane faz są w repo
python tools/build_reading_pl2.py --source-dir data/s6-full --index data/reading-index-sourcebound.json --translations local/pl2-reading/plan.json --audit translations/pl2/AUDIT_PL2.json --links data/dictionary_links.json --phases data/scene_phases_y.json --out local/pl2-reading/edition
python tools/verify_reading_pl2.py --source-dir data/s6-full --index data/reading-index-sourcebound.json --translations local/pl2-reading/plan.json --links data/dictionary_links.json --edition local/pl2-reading/edition
```

Wydanie zawiera teraz 54 pliki Markdown i `receipt.json`; ZIP w katalogu
`edition` nazywa się `SRW_Y_CZYTANKI_PL2_POPRAWIONE_v5.zip`. Bez `--phases`
generator zachowuje czysty porządek źródłowy (bez przenoszenia wymian po
wygranej) — dane faz `data/scene_phases_y.json` są w repozytorium i wiążą się
hashem z indeksem źródłowym oraz katalogiem grafów.

Katalog `edition` nie może istnieć. Archiwum odtwarza się z oryginalnych tekstów w repozytorium; nie są potrzebne pliki binarne gry. Generator kontroluje pieczęć korpusu i zgodność planu z audytem PL2, a wszystkie źródła scen wiąże z konkretną wersją i kolejnością pliku. Zakres opiera się na zachowanym indeksie, nie na niezweryfikowanych hipotezach o zdarzeniach w grze.

Pełny zestaw testów warsztatu po zapisaniu dokumentów: **668 testów i 4558 subtestów**, wszystkie pozytywne. Weryfikator wydania raportuje `markdown_files: 54`, `narration_rows: 35`, `scene_rows: 26251`, `tables: 6276` / `table_rows: 47160`.
