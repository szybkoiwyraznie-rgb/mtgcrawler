# Audyt językowy PL — epizody 0–2 (2026-10-24)

**Status:** raport z przeglądu. Na polecenie właściciela **nie poprawiano w tej partii żadnych tekstów tłumaczenia**.

## Zakres i metoda

- Źródło: aktualny zmaterializowany pakiet PL (`pakiet_EN` + `pakiet_PL`), kolejność kwestii z `docs/reading-script/polish/episode_00.json` … `episode_02.json`.
- Korpus audytu: **2 701 wpisów** (2 346 `story` + 355 `conditional`; puste PL: 0).
- Kontrola pytanie–odpowiedź: odczytano wszystkie **565 dialogów z pytaniem** (503 `story` + 62 `conditional`) wraz z dwiema następującymi kwestiami. Misję **1_5 (`DL101_50`)** przeczytano dodatkowo w całości; pozostały tekst przeszukano pod kątem kalk, rządu czasownika, nominalizacji i form adresatywnych, a kandydatury zweryfikowano wobec JP/EN i szerszego kontekstu.
- Uwaga metodologiczna: bloki `conditional` są wyzwalane zdarzeniami bitewnymi, więc ich sąsiedztwo w edycji czytelniczej nie zawsze jest kolejnością rozmowy. Nie zgłaszano jako błędów typowych przerywań komicznych ani wieloosobowych wtrąceń, jeżeli identyczny układ wynikał z JP.

## Misja 1_5 (`DL101_50`) — znaleziska najważniejsze dla zgłoszenia właściciela

### 1. Zaproszenie na symulator brzmi jak pytanie, a odpowiedź prosi o pozwolenie — wyraźna niezgodność wymiany

**ID:** `dlg:eventP00.cpk/DL101_50.bin:2212` (Chris) → `:2296` (Shiro)

> Chris: „Spróbuj na symulatorze, to zobaczysz. **Może się przekonasz?**"
> Shiro: „**Naprawdę mogę?** Bardzo chętnie!"

JP `ちょっと試してみたら？` znaczy „dlaczego nie spróbujesz?" / „może spróbuj?", czyli **zaproszenie**. Polskie „Może się przekonasz?" pyta raczej o efekt („może zmienisz zdanie?"), więc Shiro odpowiada tak, jakby dostał ofertę/pozwolenie, której w poprzedniej kwestii nie ma. To najczystszy przykład zgłoszonego wrażenia, że odpowiedź nie pasuje do pytania.

### 2. Koniec walki — odpowiedź przeskakuje z dźwięku odwrotu od razu do podsumowania

**ID:** Eledore `dlg:eventP00.cpk/DL101_50.bin:10612` (kontekst); Michel `:10688` → Shiro `:10732`

> Eledore: „Dźwięk się oddala... Chyba już nie zamierzają atakować."
> Michel: „Dowódco, **słyszał pan?**"
> Shiro: „**Tak, jakoś wytrzymaliśmy.**"

Wymianę da się obronić („tak" odpowiada na pytania, a reszta podsumowuje walkę), ale po kwestii Michela czytelnik spodziewa się raczej reakcji na odsłuchany odwrót. JP ma tę samą elipsę (`聞こえましたか？` → `ああ、なんとか持ちこたえたな`), więc jest to elipsa źródłowa, która po polsku brzmi jednak jak zmiana tematu. To drugi prawdopodobny punkt z odczucia właściciela.

### 3. Stopień + imię („pani porucznik Chris") i „proszę spokojnie wsiadać"

**ID:** `dlg:eventP00.cpk/DL101_50.bin:2508`; powtórzenie formy: `:8932`

> „**Pani porucznik Chris, proszę spokojnie wsiadać.**"
> „Nikt nie tknie wahadłowca **pani porucznik Chris**!"

To kalka JP `クリス中尉` (imię + stopień). W Wojsku Polskim zwrot jest nienaturalny: stopień łączy się z nazwiskiem albo występuje sam. Dodatkowo JP `安心して…乗ってください` znaczy „proszę wsiąść bez obaw / spokojnie [o resztę]", a polskie zdanie sugeruje raczej upominanie o spokojny sposób wsiadania.

### 4. „Maszyna trzyma pani życie w rękach" + „niedoczulona"

**ID:** `dlg:eventP00.cpk/DL101_50.bin:1892` (Shiro)

> „Na polu bitwy **maszyna trzyma pani życie w rękach**. Lepiej, żeby była nadwrażliwa niż **niedoczulona**."

JP mówi o **powierzeniu życia maszynie** (`機体に命を預ける`). Metafora „trzyma życie w rękach" pochodzi z EN („your life's in its hands") i silniej personifikuje maszynę. „Niedoczulona" jest tworem analogicznym; dla układów sterowania naturalniejsze jest mówienie o zbyt małej czułości, a nie o „niedoczulonej" maszynie.

### 5. „Dziękujemy za waszą służbę!" — formuła amerykańska

**ID:** `dlg:eventP00.cpk/DL101_50.bin:10916` (Oficer Federacji)

> „Dobra robota. Dzięki wam kontener jest już załadowany. **Dziękujemy za waszą służbę!**"

JP `貴官らの働きに感謝する` = „dziękuję za waszą robotę/działanie". Polska formuła przypomina amerykańskie *thank you for your service* i przesuwa sens z wykonanego konkretnego zadania na ogólną służbę wojskową.

### 6. Ta sama para w jednej scenie kilkakrotnie przełącza rejestr pan/pani ↔ ty

Przykłady: `dlg:eventP00.cpk/DL101_50.bin:1704` („Twierdzi **pan**…?") → `:2212` („Spróbuj… zobaczysz") → `:2508` („Pani porucznik…") → `:11064` („**Mów mi po prostu Shiro, Chris.**").

JP jest tu rzeczywiście swobodne, ale polski system pan/pani uwidacznia skoki, których w JP prawie nie widać. Nie jest to błąd jednej kwestii; raczej decyzja o stabilności rejestru w scenie — szczególnie że Chris jest oficerem wyższego stopnia niż Shiro, a „Mów mi… Chris" wychodzi od podwładnego.

### 7. Drobne elipsy i szyk w liniach bitewnych

- `dlg:eventP00.cpk/DL101_50.bin:7772` (Karen): „**Głów już nie było**." — JP/EN: nie było już części/zapasowych głów; po polsku zdanie bez dopowiedzenia brzmi egzystencjalnie („nie było głów").
- `dlg:eventP00.cpk/DL101_50.bin:8148` (Steiner): „**Dalej siłą się nie przebijemy**…" — sens jasny, ale szyk jest kalkowy; „siłą" wisi przed „się".

## Pozostałe epizody 1–2 — logika wymiany i sens zdania

### 8. Zapalnik pocisku: brakuje przesłanki „typ poznamy dopiero po starcie"

**ID:** `dlg:eventP00.cpk/DL101_30.bin:2080` (Bright) → `:2180` (Sayla)

> „Znając typ pocisku, z danych ujawnionych w ramach traktatu ustalimy położenie zapalnika."
> „Czyli dopóki go nie odpalą, nie dowiemy się, gdzie jest zapalnik..."

Wniosek Sayli zakłada niedopowiedziany krok: typ będzie można rozpoznać dopiero po odpaleniu/zobaczenie pocisku. JP jest równie eliptyczne, ale polska wersja — pewna forma „ustalimy" — jeszcze silniej sugeruje sprzeczność z następną kwestią.

### 9. „Maszyna ma swój potencjał" może znaczyć odwrotnie niż wymaga spór

**ID:** `dlg:eventP01.EDAT/DL102_30.bin:8844` (Seishiro)

> Shinobu: „To walcz, jakby od tego zależało twoje życie!"
> Seishiro: „Ale **maszyna ma swój potencjał!**"

Seishiro protestuje jako racjonalista: maszyna ma **skończone możliwości / limit osiągów**. Polskie „potencjał" jest zwykle pozytywne („stać ją na więcej"), więc replika może czytać się odwrotnie. EN ratuje zapożyczenie JP `ポテンシャル`, dodając „limits"; w Polskiej wersji zostało samo słowo „potencjał".

### 10. Refleksyjne powtórzenie zamienione w pytanie „…co?"

**ID:** `dlg:eventP01.EDAT/DL102_30.bin:14348` (Shinobu) → `:14428` (Seishiro)

> „…to chyba jesteś najsilniejszy, co?"
> „Spokojny, a zarazem pełen zapału... **co?**"

JP `…か` jest tu namysłem („hm…"), nie pytaniem. Shinobu dlatego nie odpowiada i zmienia temat. Znacznik `?` rodzi pozorne pytanie bez odpowiedzi.

### 11. Zdanie Mirai o pewności siebie brzmi jak sprzeczność

**ID:** `dlg:eventP00.cpk/DL101_20.bin:14640` (Mirai)

> „**Nie możemy być zbyt pewni siebie, ale powinniśmy bardziej w siebie wierzyć.**"

JP odróżnia `過信` (nadmierna pewność/ zarozumiałość) od `自信` (wiara we własne siły). Polskie „pewni siebie" i „wierzyć w siebie" są niemal synonimiczne, przez co zdanie brzmi jak „nie X, ale bardziej X".

### 12. Pytanie o syna komendanta zostaje bez jawnego „tak"

**ID:** `dlg:eventP01.EDAT/DL102_30.bin:4004` (Kanuka) → `:4060` (Alan)

> „Czy pan jest synem komendanta Igora...?"
> „Alan Igor."

Odpowiedź jest eliptyczna już w JP (podanie nazwiska ma być potwierdzeniem), ale po polsku jest słabsza tym bardziej, że „Igora" czyta się łatwo jako imię ojca, a nie wspólne nazwisko. Efekt: niepełna odpowiedź, po której rozmowa po prostu idzie dalej.

## Kalki, frazeologia, gramatyka i szyk poza misją 1_5

| ID | Kwestia | Diagnoza |
|---|---|---|
| `dlg:eventP00.cpk/DL101_11.bin:8956` (Kanuka) | „Przy dzisiejszym **poziomie broni** na pewno tak." | JP `新兵器の水準`, EN „today's new weapons". „Poziom broni" to nienaturalna kolokacja; mówi się raczej o poziomie techniki wojskowej / uzbrojenia. |
| `dlg:eventP00.cpk/DL101_20.bin:3156` (Szef Suol) | „No, **ręka rękę myje**." | JP `持ちつ持たれつ` = wzajemne wspieranie się / układ coś za coś. Po polsku idiom najczęściej sugeruje tuszowanie nadużyć / kolesiostwo — mocniejsza, podejrzana konotacja (choć może pasować do śliskiego Szefa). |
| `dlg:eventP00.cpk/DL101_20.bin:11128` (Gaia) | „**Źle wybrać chwilę odwrotu** przez głupią dumę **to cecha** drugorzędnych pilotów!" | Nominalizacja po JP/EN. Wrzask w boju brzmi jak zdanie z wykładu; „cecha" zamienia działanie na stałą właściwość. |
| `dlg:eventP00.cpk/DL101_60.bin:2868` (Sanders) | „Pewnie Doppy **ją** przekazały..." | Poprzednia kwestia mówi o **trasie lotu Medei**; „ją" może wskazywać Medeę, trasę albo informację. Nieostry zaimek. |
| `dlg:eventP00.cpk/DL101_80.bin:16332` (Goto) | „**ogłosi się to** jako bezpłatną aktualizację…" | Bezpodmiotowe „ogłosi się to" z biernego JP/EN zamiast konstrukcji osobowej lub „zostanie ogłoszone". |
| `dlg:eventP00.cpk/DL102_11.bin:23380` (Seishiro) | „**Zostawicie swoją sprawę w rękach Connect?**" | JP `処遇` = status / co się z wami będzie działo. „Swoją sprawę" jest biurokratycznie nieostre; „zostawicie" brzmi jak stwierdzenie przyszłości, nie propozycja. |
| `dlg:eventP00.cpk/DL102_11.bin:22008` (Himari) | „**z jakiej oni są organizacji?**" | Szyk pytania rozerwany jak w EN („what organization are they from"); naturalniej trzymałby frazę „z jakiej organizacji" w całości. |
| `dlg:eventP00.cpk/DL102_11.bin:26508` (Gai) | „Choćby te **pojawienia się** Invaderów..." | Rzeczownik odczasownikowy w liczbie mnogiej — kalka nominalnej frazy JP/EN („Invader sightings"). |
| `dlg:eventP01.EDAT/DL102_20.bin:3804` (Kanuka) | „Albo po prostu **skąpią na dodatek** za ryzyko." | Błędny rząd czasownika: „skąpić czegoś" (dopełniacz) / „żałować na coś". Najbardziej jednoznaczny drobny błąd gramatyczny poza misją 1_5. |
| `dlg:eventP01.EDAT/DL102_20.bin:8568` (Seishiro) | „**Pędziliśmy ekspresem**." | JP `超特急で駆けつけた` jest metaforyczne („pędziliśmy co sił"); dosłownie brzmi, jakby przybyli Ekspresem-pociągiem. |
| `dlg:eventP01.EDAT/DL102_90.bin:2356` (Kotaro) | „**Nie, Rikiya?**" | Samodzielna końcówka `なぁ` („prawda?"), oderwana od zdania. W osobnej bańce „Nie" czyta się najpierw jako odpowiedź „nie" skierowaną do Rikiyi. |
| `dlg:eventP00.cpk/DL102_11.bin:7492` (Elly) | „**Profesorko**, czy to nowy gatunek mechabestii?" | Forma gramatycznie dopuszczalna, ale w zwrocie dziecka do autorytetu naukowego jest nacechowana; to raczej pytanie o politykę feminatywów niż błąd. |

## Wzorce systemowe (nie pojedyncze błędy)

1. **Końcowe znaczniki potwierdzające z JP.** W korpusie jest **41 wpisów** kończących się schematem „, prawda? / nie? / tak? / co?". Większość jest po polsku możliwa w mowie potocznej, ale są bezpośrednim nośnikiem partykuł typu `ね` / `だろ` / `か`. Problem pojawia się, gdy stają w osobnej bańce („Nie, Rikiya?") albo przerabiają namysł na pytanie („…co?") — wtedy powstaje wymiana, która wygląda na pozbawioną odpowiedzi.
2. **Nominalny, „briefingowy" tok zdań.** Formy typu „pojawienia się", „Źle wybrać chwilę odwrotu to cecha…", „ogłosi się to", „swoją sprawę" zachowują rzeczownikową składnię JP/EN. Pojedynczo są zrozumiałe; razem sprawiają, że ekspozycje Connect i wojskowe odprawy brzmią bardziej jak tłumaczenie niż mowa.
3. **Japońskie formy adresatywne przeniesione wprost.** Poza „pani porucznik Chris": **15× „Bracie"** Simon → Kamina (`aniki`, bez pokrewieństwa) — jest to utrwalona konwencja fanowska wokół *Gurren Lagann*, więc zgłaszam tylko jako świadoma decyzja stylu, nie jako błąd. Podobnie „Profesorko".
4. **Epizod 0.** Nie znalazłem równie wyraźnego rozjazdu pytanie–odpowiedź jak w misji 1_5. Kilka wymian Seishiro/Himari (przerywane „Rozumiem…", dokładanie wyjaśnień w kolejnej bańce) układa się zgodnie z JP i po przeczytaniu następnej kwestii nie zostawia luki.

## Sprawdzone, ale niezgłoszone jako defekty

- Wielokrotne pozorne nieodpowiadanie Himari/Seishiro oraz bohaterów `DL101_40`–`DL101_80` wynika z celowych przerywań i wieloosobowych rozmów; kolejna postać zwykle domyka sens pytania.
- `DL102_11` („Przybyliście nam na pomoc?" → „Wyjaśnijcie mi sytuację.") to wojskowe przejęcie inicjatywy, nie błąd logiczny; odpowiedź na pytanie Gaja wynika z dalszych rozkazów Seishiro.
- Wątki kanoniczne (`Bracie`, kokpitowe okrzyki, fandomowe nazwy zespołów) pozostawiono bez oceny jako konwencje franczyz.

## Podsumowanie nasilenia

- **Najbardziej odczuwalne:** pkt 1 (misja 1_5), 9 („potencjał") i 8 (zapalnik) — wpływają na logikę kolejnych kwestii.
- **Wyraźnie nienaturalne, ale sensownego toku nie łamią:** pkt 3–5, 10–11, „skąpią na dodatek".
- **Reszta:** lokalne kalki/szyk i decyzje rejestru; w większości nie utrudniają zrozumienia, ale składają się na zgłoszone wrażenie „coś tu zgrzyta".

Żadna linia `pakiet_PL/polish.jsonl` nie została w tej partii zmieniona.
