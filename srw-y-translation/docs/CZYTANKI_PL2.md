# SRW Y — poprawione czytanki misji PL2

[SRW_Y_CZYTANKI_PL2_POPRAWIONE_v14.zip na Drive](https://drive.google.com/file/d/1p_LK-GJAM755nYis88bNnC0UG3FY-zo6/view)
(`1p_LK-GJAM755nYis88bNnC0UG3FY-zo6`) **powstaje w całości z plików repozytorium**: korpus S6
(`data/s6-full/`), indeks źródłowy, powiązania słownikowe, fazy scen, plan PL2
(`translations/pl2/PLAN_PL2.json`) i jego audyt. Markdown jest bajt w bajt ten
sam co w v13 (README różni się tylko tym, że notę o układzie dopisuje już
generator, a nie ręka). ZIP ma **1 542 817 B** i SHA-256
`230b219e077a96c9ff5b37357cb293a7e0ca06519924feff6342232209f502cc`.
Od teraz nie trzeba żadnego `.zip`-a od właściciela: `python3
tools/rebuild_reading_pl2.py --check` buduje wydanie od zera i porównuje je
z plikami w `docs/reading/pl2-oe-format/`.

[SRW_Y_CZYTANKI_PL2_POPRAWIONE_v13.zip na Drive](https://drive.google.com/file/d/1xn3b-ygVI6moaGqY2AcKGqLhXwI01Dxn/view)
(`1xn3b-ygVI6moaGqY2AcKGqLhXwI01Dxn`) poprawia **układ** zgłoszony przez
właściciela na zrzucie z 2026-11-09: długie opisy umiejętności pilota i efekty
komend Ducha są łamane na **dwa wiersze tabeli** (dalszy ciąg w wierszu bez numeru
slotu, pozostałe komórki puste), więc wiersz nie wychodzi za szerokość okna
w Notepad++ — ta sama zasada, co przy tabeli uzbrojenia w v12. Z wpisów encyklopedii
usunięto akapit powtarzający początek dłuższego opisu (Forte Tsukinowa i jedna
maszyna). Treść, kolejność i numeracja tekstów bez zmian. ZIP ma **1 542 819 B**
i SHA-256 `7ab648e68cb8a2eec13e7e582d9e5573e2bfc304cc89196e4cb5083fcc8d1992`;
złożony z plików w repozytorium (`archive_bytes`, więc dwie budowy dają ten sam
plik). Poprawkę naniesiono `tools/fix_reading_pl2_layout.py` na wydane `.md`,
a generator `tools/build_reading_oe_style.py` ma obie poprawki na przyszłość.
Wtedy sądziłem, że wydania nie da się przeliczyć od zera, bo „źródeł S6 nie ma
w repozytorium” — to było nieprawdziwe: korpus leżał w `data/s6-full/`, brakował
tylko planu przekładu, który jeździł w zestawach patchy. v14 zamyka tę lukę.

[SRW_Y_CZYTANKI_PL2_POPRAWIONE_v12.zip na Drive](https://drive.google.com/file/d/123qj9F7LCQzZ1nAndYcPjqqmXXNdn8wg/view)
(`123qj9F7LCQzZ1nAndYcPjqqmXXNdn8wg`) robi tabelę uzbrojenia **dokładnie jak
w czytance SRW OE, którą przysłał właściciel**: każda właściwość broni stoi
w osobnym wierszu kontynuacji tabeli (puste komórki w kolumnach 1–9, treść tylko
w „Zdolności — opisy bazowe”), więc plik `.md` czyta się jak tabela — bez `<br>`
i bez sklejania w jednej linii. ZIP ma **1 516 984 B** i SHA-256
`daa7b35ac349cc6cf095230c2c6395b445a4d0ac5a048d4386d4445b4dcbdec6`
(MD5 `f905ce0c35577b00a306b6f1b5f113f9`); dwa przebiegi dały identyczny plik.
Wydanie v11 (wszystko w jednej linii, rozdzielone ` · `) jest zastąpione;
zostaje jako ślad po tym, co właściciel odrzucił na zrzucie z 2026-11-09.

[SRW_Y_CZYTANKI_PL2_POPRAWIONE_v11.zip na Drive](https://drive.google.com/file/d/1V3XKiKLvf352cl22D2qRt7a2Z2-SH88m/view)
(`1V3XKiKLvf352cl22D2qRt7a2Z2-SH88m`) usuwał `<br>` z tabeli uzbrojenia, ale
sklejał właściwości w jednej linii — nieczytelne, więc zastąpione przez v12.

[SRW_Y_CZYTANKI_PL2_POPRAWIONE_v10.zip na Drive](https://drive.google.com/file/d/1AIdRsKzvZlU6z7hxGZiiV75xyaZef670/view)
(`1AIdRsKzvZlU6z7hxGZiiV75xyaZef670`) to wydanie z 2026-11-09, w którym zestawienie jednostek dostało
poprawki z rundy 10 (patrz niżej), a układ plików został ten sam co w v9. ZIP ma
**1 514 234 B** i SHA-256
`4d1b498a4ba77d95200828cc0c34760ac84c90db19b08e2f93c1e326a451b0c4`
(MD5 `8ad8375246dae6d1156f4983703881cb`); dwa niezależne przebiegi dały
identyczny plik. Poprzednie wydanie
[`SRW_Y_CZYTANKI_PL2_POPRAWIONE_v9.zip`](https://drive.google.com/file/d/1pPVuW5Qoa5rgbma3np31hG1sL2dnDy38/view)
(`1pPVuW5Qoa5rgbma3np31hG1sL2dnDy38`) to wydanie v8 w układzie, o który poprosił
właściciel 2026-11-08: **cały scenariusz w jednym pliku**
(`srwy_scenariusz_PL.md`), a zestawienie jednostek osobno
(`srwy_mission_deployments.md`). Treść misji jest ta sama — 52 sekcje misji,
26 251 wierszy scen, zero braków PL. ZIP ma **1 594 817 B** i SHA-256
`210289ee028a6ab859386be0b82bc2c758051e677f87ad67e932c811f7779aa7`
(MD5 `d1124af853723dfcab84ce06a46e8736`); dwa niezależne przebiegi dały
identyczny plik.

Poprzednie wydanie
[`SRW_Y_CZYTANKI_PL2_POPRAWIONE_v8.zip`](https://drive.google.com/file/d/1q7TE58d-y4Uvm2jaYL4JJsIffBsduJbN/view)
(`1q7TE58d-y4Uvm2jaYL4JJsIffBsduJbN`, 1 698 185 B, SHA-256 `90a6b075…c2aa5`)
usuwało znacznik cytatu `> ` sprzed dialogów i opisów. Wydanie v7
(`1HJmaSuBfaUBjd8qho6CyHAOxZ1vn4ea6`, SHA-256 `ab3c3f30…f3ebd`) dodało pod
każdą misją hasła encyklopedii i opisy serii. Wydanie v6 (`1OxgtVNj…`) zostaje
jako zaakceptowany układ czytanek, a v3 (`1_w1e-zvO1r8FxTVdzk7dklzTFyTlhC3R`)
jako poprzedni układ.

## Co zmienia v10 (2026-11-08/09): same fakty z gry, bez premii i bez spojlerów

Właściciel poprosił o pięć rzeczy w zestawieniu jednostek
(`srwy_mission_deployments.md`); scenariusz (`srwy_scenariusz_PL.md`) jest
bajtowo ten sam co w v9.

1. **Premie znikają.** Z kart usunięto „Premia Asa” (pilot) i „Bonus
   modyfikacji” (maszyna) — to informacje o modyfikacjach, nie o stanie z gry.
2. **Opisy encyklopedii tylko w pierwszej części.** Wpisy maszyn, postaci,
   **serii** i haseł słownika mają w grze kilka części; kolejne odsłaniają
   wydarzenia fabularne. Karty pokazują wyłącznie część pierwszą (`_00_0`),
   pozostałe trafiły do jednej sekcji **„Teksty encyklopedii, których gra jeszcze
   nie pokazuje”** na końcu dokumentu — bez przypisywania do misji, bo danych
   gry nie da się z nich odczytać (tabele wpisów słownika nigdy nie wróciły
   z kopii gry).
3. **Seria na każdej karcie.** Karta maszyny bierze `ipnameId` z rekordu,
   karta postaci z rekordu `listFacialSettingData` (postacie go nie mają),
   postacie dialogowe — z rekordu twarzy. Tytuł pochodzi z tabeli `ip_name`.
4. **Zdolności broni.** Tabela uzbrojenia ma kolumnę „Zdolności — opisy
   bazowe”: nazwy właściwości i ich bazowe opisy pochodzą wprost z tabeli
   `system_text` (`00000019:`, indeksy 79–117) — użycie po ruchu, wiązka, kontra,
   penetracja barier, ignorowanie rozmiaru, osłabienia (EN/pancerz/zwrotność/
   celownik/morale/SP/parametry/paraliż) i broń MAP. Właściwość „wiązka” bierzemy
   z pola `powerType` = 1; to jedyne miejsce, gdzie opieramy się na powiązaniu
   odczytanym z nazw broni, i tak jest opisane w legendzie dokumentu.
5. **Opisy serii bez wiersza w indeksie.** Odzyskany indeks słownika nie ma
   wierszy dwóch serii, choć gra oznacza je jako mające hasło
   (`onDictionaryExist: 1`): **SSSS.DYNAZENON** (`DYNZNN`) i **New Story of AURA
   BATTLER Dunbine** (`DBOVA`). Ich tekst jest w `dic_text_name`: wiersze tej
   tabeli idą w kolejności serii z Encyklopedii, a każda seria ma tam dwa wiersze
   (tak pokazuje 16 serii obecnych w indeksie). Przypisanie wynika więc
   z kolejności i liczby wierszy — stosowane tylko wtedy, gdy liczba wierszy
   zgadza się co do jednego — a nie z podobieństwa tekstu. Dzięki temu pod misją,
   po której właściciel widzi ten wpis w grze, stoi pełny polski opis
   („Yomogi Asanaka, uczeń publicznego liceum Fujiyokidai…”). Serie bez hasła
   w grze (`onDictionaryExist: 0`, m.in. Original, M-MSV, Macross Δ, Code Geass
   Ⅲ) są oznaczone wprost, zamiast zostawiać puste miejsce.

Testy: `tests/test_reading_unlocked_parts.py` (5 przypadków) pilnuje pierwszej
części, dorozumianego przypisania serii i kolumny zdolności broni; cały zestaw to
**707 testów / 4558 podtestów**.

## Kiedy pokazują się dalsze części wpisów? Nie wiemy — i dlatego ich nie przypisujemy

Pytanie właściciela z 2026-11-09: „na jakiej podstawie ustaliłeś, kiedy mają się
pokazywać dalsze elementy opisu mechów/postaci/serii?”. Odpowiedź jest krótka:
**nie ustaliłem żadnego momentu.** W wydaniu v10/v11 dalsze części nie pojawią się
pod żadną misją — także po odblokowaniu w grze. Leżą wyłącznie w sekcji „Teksty
encyklopedii, których gra jeszcze nie pokazuje” na końcu dokumentu.

Dlaczego nie da się tego odczytać z danych:

- w tabelach tekstowych gry wpis ma części `_00_0`, `_00_1`, … ale **żadne pole
  nie mówi, co je odsłania**; tabele wpisów słownika (`RobotDictionaryEntryTable`,
  `PilotDictionaryEntryTable` itd.) nie wróciły w odzyskanych bundlach, więc
  warunku (`flag`, `mission_open_cond`, numer misji) po prostu nie ma w danych;
- jedyny sygnał, jaki mamy, to **w której tabeli leży część**: 1 307 dalszych
  części rozkłada się na tabele podstawowe (688: `dic_text_pilot` 348,
  `dic_text_robot` 243, `dic_text_word` 81, `dic_text_name` 16) i na tabele
  dodatków (619: głównie `dic_text_pilot-DLC4` 459). To wskazuje na zależność od
  zawartości dodatków, a nie od numeru misji — i tylko dla części wpisów;
- `stgmemory`, `mission_open_cond` i `listGlobalFlag` istnieją, ale nie mają
  powiązania z identyfikatorami wpisów słownika, więc dopasowanie byłoby
  zgadywaniem.

Co można z tym zrobić (do wyboru przez właściciela):

1. **Zostawić jak jest** — bez spojlerów, ale dalsze części nigdy nie staną przy
   misji.
2. **Pokazać wszystko** — tak robiło v9; wraca problem spojlerów.
3. **Bundli słownika od właściciela** — gra trzyma warunek odblokowania w 11
   bundlach `*DictionaryEntryTable*` (łącznie 58 461 B); spis zna ich nazwy
   i rozmiary, ale pliki nigdy nie wróciły w żadnym archiwum
   (`data/dictionary_owner_assets.json`, `present_in_recovered_inputs: false`).
   Do ich zebrania jest zestaw **`SRW_Y_ZBIERZ_SLOWNIK.zip`**
   (Drive `1TbMgWXhasj-udvyR3YZnmW-_HLQks2iN`): rozpakować, kliknąć
   `ZBIERZ_SLOWNIK.bat`, wgrać `SLOWNIK_ENCYKLOPEDII.zip` z Pulpitu. Szczegóły:
   `docs/SLOWNIK_ENCYKLOPEDII.md`. Po odczytaniu tych tabel albo warunek będzie
   znany, albo będzie wiadomo, że go tam nie ma — w obu przypadkach bez zgadywania.
4. **Mapa od właściciela** — wystarczy, że powie „wpis X pokazuje się po misji N”
   (albo „po rozdziale N”) dla wpisów, które go interesują; wtedy dopiszemy małą
   tabelę `entry → misja` w narzędziach i część 2 pojedzie pod tę misję. To jedyny
   sposób, żeby „po odblokowaniu” zadziałało naprawdę — bez zgadywania.

## Jeden plik scenariusza (v9, 2026-11-08)

Właściciel: „nie rozbijaj mi treści skryptu na osobne pliki per epizod — umieść
je wszystkie w jednym pliku, deployment osobno”. Od v9 wydanie ma **cztery
pliki** zamiast 55:

- `srwy_scenariusz_PL.md` — cały scenariusz: prolog i 51 misji w kolejności
  numerów, każda misja zaczyna się własnym nagłówkiem `# Super Robot Wars Y — …`
  i kończy sekcją **Uwagi redakcyjne** (ta sama treść co wcześniej, tylko
  w jednym dokumencie); na początku pliku stoi krótki wstęp z zakresem wydania,
  brakami numerów i wskazaniem pliku zestawienia;
- `srwy_mission_deployments.md` — zestawienie jednostek, profili, haseł
  encyklopedii i serii, bez zmian względem v8 (bajtowo ten sam plik);
- `README.md` i `receipt.json` — spis misji (numer, tytuł) i liczniki wydania.

Weryfikator nie został osłabiony: dzieli dokument na sekcje misji po nagłówkach
(`episode_documents`) i sprawdza każdą misję tak jak wcześniej — obecność
26 251 wierszy scen, umiejscowienie 35 tekstów narracji, brak znaków japońskich
i brak markerów braku. `receipt.json` dostaje `markdown_files: 3`.

## Układ zaakceptowany przez właściciela (v6, 2026-11-08): bloki dialogów i kolejność wymian

Właściciel zgłosił trzy rzeczy w czytaniu scen: podwójne łamania w dialogach,
nagłówki strukturalne (`## Sceny fabularne`, `### Wymiana sytuacyjna`) oraz
wymiany sytuacyjne wmieszane w dialogi bitewne. Po dwóch odrzuconych próbach
(odwrócona reguła łamań, potem za długi blok wymian) właściciel podał wzór dla
misji 1; v6 trzyma się go linia w linię i **został zaakceptowany („no i teraz
jest idealnie :)”):**

* **Jedna tabela dialogowa = jeden blok.** Kwestie w bloku (scena `**…**` albo
  wymiana `> …`) stoją w kolejnych liniach rozdzielonych **pojedynczym** `\n` —
  tak w scenach, jak i w wymianach. Wewnętrzne podwójne łamanie tłumacza
  zwijamy do `\n`; własnego zawijania nie dokładamy.
* **`\n\n` oddziela bloki** — kolejną tabelę dialogową, następną scenę
  i znacznik miejsca.
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

## Bez znacznika cytatu (v8, 2026-11-08)

Właściciel: „żebyś we wszystkich czytankach (w tym deployment) usunął taki ciąg
znaków sprzed dialogów/opisów, w ogóle wszędzie: `> `”. Znacznik `> ` był
przedrostkiem bloku cytatu w Markdownie; w wydaniu zniknął wszędzie — przed
kwestiami dialogów sytuacyjnych, przed opisami encyklopedii maszyn i postaci,
przed hasłami słownika, przed opisami serii i przed uwagami redakcyjnymi.
Tekst kwestii i akapitów się nie zmienił: generator po prostu nie dokleja
przedrostka (`build_reading_oe_style.py`), a weryfikator porównuje wiersze bez
niego (`verify_reading_pl2.py`). Trzy wiersze polskiego tekstu zaczynają się od
liczby z kropką (np. „99. i jedyny cesarz…”) — w podglądzie Markdowna czytnik
może pokazać je jako element listy, ale treść i numer pozostają bez zmian.
Test `test_published_pl2_uses_the_owner_reading_layout` pilnuje, że w wydaniu
nie ma ani jednego wiersza zaczynającego się od `> ` ani ciągu `&gt;`.

## Hasła encyklopedii i serie pod każdą misją (v7, 2026-11-08)

Właściciel poprosił, żeby na końcu opisu każdej misji w
`srwy_mission_deployments.md` stanęły dwie rzeczy: **hasła z Encyklopedii gry,
które pojawiły się w dialogach tej misji** (bez postaci i mechów) oraz **opisy
serii, których reprezentanci wystąpili w misji**.

- **Hasła.** Dopasowanie jest tekstowe: tytuł japoński hasła z tabeli
  `dic_text_word` szukany w japońskich kwestiach misji (zgodnie z zasadą
  warsztatu tekst źródłowy służy do dopasowania, nigdy do druku). Kolejność
  haseł to kolejność pierwszego wystąpienia w dialogach. Hasła jednoliterowe
  pomijamy jako nierozstrzygalne, a odmiana tytułu w kwestii może hasło
  pominąć — to ograniczenie metody, nie brak danych. Wyszło **47 haseł**
  w **308** wystąpieniach; jedna misja (nr 36) nie ma ani jednego hasła.
- **Podział haseł.** Tabela `dic_text_word` miesza terminy, osoby i maszyny
  (78 identyfikatorów, 81 tytułów), a dane tekstowe nie niosą kategorii.
  Dlatego `data/dictionary_word_kinds.json` zawiera **ręczną klasyfikację**
  18 postaci i 4 mechów, z uzasadnieniem przy każdym tytule; wszystko poza tymi
  listami jest terminem i tylko terminy wchodzą do zestawienia. Klasyfikacja
  jest sprawdzana testem: każdy wymieniony tytuł musi istnieć jako hasło
  `dic_text_word`.
- **Serie.** Numer serii (`ipnameId`) pochodzi z **rekordów gry** — mech z
  `listRobotBaseData`, pilot przez swój wpis `listFacialSettingData`; tytuł
  z tabeli `ip_name`, opis z tabeli `dic_text_name` encyklopedii. Wyszły
  **22 serie**. To, że jednostka jest w presecie misji, nie dowodzi, że
  występuje w każdej fali — zestawienie opisuje preset, nie przebieg walki.
- **Zakres plików.** Zmienił się wyłącznie `srwy_mission_deployments.md`;
  scenariusz i `receipt.json` opisują ten sam zestaw danych co v6 (weryfikator:
  6 276 tabel / 47 160 wierszy, 26 251 wierszy scen, 0 braków PL, 0 znaków
  japońskich w wydaniu). Wydanie PL1 w `docs/reading/pl1-oe-format/`
  zostaje w wersji opublikowanej — generator dodałby tam te sekcje dopiero przy
  przebudowie, a PL1 nie było zamawiane ponownie.

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

* otwiera prolog (w v9 początek `srwy_scenariusz_PL.md`) sekcją
  **Narracja otwierająca** —
  11 akapitów od „Ziemia…” do „…kończę dziś czternaście lat.”, czyli dokładnie
  przed pierwszymi scenami misji 1;
* kończy ostatnią misję rozdziału sekcją **Narracja kończąca rozdział N** —
  misja 7 (rozdział 1), 35 (rozdział 2) i 52 (rozdział 3);
* umieszcza `Epilog_END` i teksty dodatków na końcu ostatniej misji
  (w v9: koniec `srwy_scenariusz_PL.md`) w sekcji **Narracje poza tym wydaniem**,
  z podziałem
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
python3 tools/rebuild_reading_pl2.py --check     # buduje od zera i porównuje z repo
python3 tools/rebuild_reading_pl2.py --out /tmp/pl2-edition --version v14
python3 tools/verify_reading_pl2.py --source-dir data/s6-full \
  --index data/reading-index-sourcebound.json \
  --translations translations/pl2/PLAN_PL2.json \
  --links data/dictionary_links.json --edition /tmp/pl2-edition
```

Nic więcej nie jest potrzebne: żadnego pliku od właściciela gry, żadnego katalogu
`local/`. Źródła wydania i ich rola:

| plik w repozytorium | co wnosi |
| --- | --- |
| `data/s6-full/scenario.jsonl`, `data/s6-full/tables.jsonl` | teksty gry JP/EN (korpus S6) |
| `data/reading-index-sourcebound.json` | indeks źródeł; pieczęć zgodna z hashami korpusu |
| `data/dictionary_links.json` | powiązania słownikowe |
| `data/scene_phases_y.json` | fazy scen (start / po oczyszczeniu pola) |
| `translations/pl2/PLAN_PL2.json` | przekład PL2 — **tekst**, którym wydanie się wypełnia |
| `translations/pl2/AUDIT_PL2.json` | audyt tego planu (`plan_sha256`) |

`data/limits_y.json` i `data/s6-derived/groups.json` to pliki pochodne
(limit szerokości pól, grupowanie tabel), liczone z korpusu przez
`tools/s6_limits.py` i `tools/s6_groups.py`; `tools/prepare_local_sources.py`
podstawia je do `local/s6/`, żeby dało się złożyć zestaw dla tłumacza. Banki
głosów i skrypty misji (`voice_map.json`, `voice_groups.json`,
`mission_map.json`, `pilots.json`, `voice_bank_ip.json`) pochodzą z dodatkowych
zrzutów gry i są opcjonalne: wydanie do czytania ich nie używa, a zestaw patcha
powstaje bez nich (`docs/PATCH_PL2.md`, `tests/test_patch_pipeline_repo.py`).

Plan PL2 jest w repozytorium jako gotowy tekst. Starsza droga
(`translations/pl2/PL` → `bind_v8_return` → `audit_full_return`) opisuje, jak
powstał: pliki w `translations/pl2/PL` pisano pod starszy kształt zestawu dla
tłumacza, więc ponowny import na dzisiejszym manifeście ich nie przyjmie —
autorytetem jest `PLAN_PL2.json` wraz z `AUDIT_PL2.json`.

`tests/test_reading_rebuild.py` pilnuje tego układu: sprawdza zgodność planu
z audytem, pieczęć korpusu i to, że przebudowa daje bajt w bajt te same pliki
Markdown, które leżą w `docs/reading/pl2-oe-format/`.

Wydanie zawiera trzy pliki Markdown i `receipt.json`; ZIP w katalogu
`edition` nazywa się `SRW_Y_CZYTANKI_PL2_POPRAWIONE_v14.zip`. Bez `--phases`
generator zachowuje czysty porządek źródłowy (bez przenoszenia wymian po
wygranej) — dane faz `data/scene_phases_y.json` są w repozytorium i wiążą się
hashem z indeksem źródłowym oraz katalogiem grafów.

Katalog `edition` nie może istnieć. Archiwum odtwarza się z oryginalnych tekstów w repozytorium; nie są potrzebne pliki binarne gry. Generator kontroluje pieczęć korpusu i zgodność planu z audytem PL2, a wszystkie źródła scen wiąże z konkretną wersją i kolejnością pliku. Zakres opiera się na zachowanym indeksie, nie na niezweryfikowanych hipotezach o zdarzeniach w grze.

Pełny zestaw testów warsztatu po zapisaniu dokumentów: **707 testów i 4558 subtestów**, wszystkie pozytywne. Weryfikator wydania raportuje `markdown_files: 54`, `narration_rows: 35`, `scene_rows: 26251`, `tables: 6276` / `table_rows: 48394` (wiersze kontynuacji właściwości broni z v12).
