# SRW Y — pakiet dla tłumacza (japoński → polski), wersja 8

To jest cały tekst fabularny i cały tekst nazw tej gry, w jednej paczce w formacie
identycznym z pakietem do SRW OE. Tłumaczy się **tekst w plikach `.md`**, wpisując
polski po znaczniku `PL:`. Nie trzeba znać JSON-ów ani żadnych narzędzi.

Wersja 8 domyka **pytanie 4 — mapę scena → misja → rozdział**. Wcześniejsza odpowiedź
(„takiego powiązania nie ma w danych”) była błędna: dane misji gry wymieniają pliki każdej
misji, więc **588 z 611 scen** ma teraz numer misji i rozdział, a cały flow fabuły jest
w nowym pliku **`spis-misji.md`** (sekcja 8, pytanie 4). Mówcy w cytatach bitewnych
zostają jak w wersji 7: **94,4% cytatów ma imię z danych gry**, reszta numer grupy
`??? NNN` (sekcja 7). Wykaz zmian w sekcji 9.

## 0. W skrócie

1. Rozpakowujesz **`sceny.zip`** — fabuła: 611 scen, 120,665 linii dialogu
   i narracji, w kolejności plików gry. Do wpisania: **97,514 linii `PL:`**.
   Każda scena ma w nagłówku **numer misji i rozdział**, a `spis-misji.md` w tym samym
   zipie pokazuje cały flow: rozdział 1 → 7, misje po kolei, z tytułami i scenami
   (sekcja 8, pytanie 4).
2. Rozpakowujesz **`widoki.zip`** — nazwy i tabele: postacie, roboty i bronie, cytaty
   bitewne, umiejętności, przedmioty, interfejs, teksty misji, teren. Do wpisania:
   **41,222 linii `PL:`** (razem w całym pakiecie **138,736**).
3. Pod każdym japońskim tekstem są linie `EN:` (gotowe tłumaczenie angielskie jako odniesienie)
   i `PL:` — **polski wpisujesz po `PL:`**.
4. Odsyłasz pliki **tak jak są** (może być zip). Nie zmieniasz nazw plików, numerów ani
   linii japońskich.

## 1. Jak wygląda jeden element

```text
14. [Dialog - $n (wariant: bohater)] 「ん…？」
   limit: do 270 znaków
   tokeny: zachowaj dokładnie: $c
   EN: "Huh?"
   PL:
```

- Pierwsza linia: numer, kto mówi (`[Dialog - imię]`, `[Narracja]`, `[Nazwa broni]`…)
  i tekst japoński. Jeśli japoński ma kilka linii, kolejne linie są **wcięte trzema
  spacjami** — tak samo wygląda wtedy wersja angielska.
- `(wariant: bohater)` / `(wariant: bohaterka)` — mówi, w której wersji płci bohatera ta
  kwestia występuje w grze. Szczegóły w sekcji 6; jeśli znacznika nie ma, kwestia jest
  wspólna dla obu wersji.
- `limit:` — ile polskich znaków mieści się w grze (patrz punkt 3). Jedna liczba.
- `tokeny:` — kody gry, które zostają nietknięte.
- `EN:` — angielska wersja gry. Pomaga w nazwach i terminach, ale tłumaczymy z japońskiego.
- `PL:` — tu wpisujesz polski, w tej samej linii co znacznik.

## 2. Zasady

1. **Piszesz tylko po `PL:`.** Linia japońska nad `PL:` jest nienaruszalna — po niej
   narzędzia znajdują miejsce w grze.
2. **Nie zmieniasz numerów ani kolejności elementów** (`1.`, `2.`, `3.`).
3. **Cały tekst jednej kwestii wpisujesz w jednej linii po `PL:`** — nie łamiesz linii
   i nie liczysz, gdzie wypada przejście do następnej. Łamaniem i wcięciami zajmują się
   narzędzia. Liczysz tylko znaki: `limit:` podaje, ile ich wolno.
4. **Nie tłumaczysz tokenów gry** — zostają dokładnie takie, jakie są: `$c`, `$n`,
   `$kwe`, `$kwb`, `$F`, `$l`, `[p1:]`, `[r1:]`, `[i:]`, `[protagonist]`, `％`, `＃`,
   `{0}`, `{1}`, `＜…＞`. Wiersz `tokeny: zachowaj dokładnie: [...]` pod elementem
   wylicza je wszystkie. `$n` to imię bohatera wpisywane przez grę, `$c` — jego skrócona
   forma, `$F` — pełne imię i nazwisko; w obu wersjach płci podstawia je gra, więc tokeny
   nie mają rodzaju — rodzaj ma dopiero polskie zdanie wokół nich (sekcja 6).
   `[p1:]` to nazwa jednostki gracza, `[r1:]` — jednostki wroga, `[i:]` — przedmiot.
5. **Jedna nazwa — jedna pisownia** w całym pakiecie. Imiona i nazwy ustalasz w plikach
   `00_postacie.md`, `01_roboty_i_bronie.md` i tam ich potem używacie w dialogach.
6. Tekst japoński pokazujemy **bez znaków, których nie widać**: bez wcięć, bez pustych
   linii, bez znaczników formatowania. To, jak tekst jest ustawiony na ekranie,
   odtwarzają narzędzia — Ty piszesz sam tekst. Niczego to nie psuje przy składaniu:
   miejsce w grze znajdujemy po numerze elementu i nazwie sceny, a wcięcia i łamanie
   linii bierzemy z danych gry, nie z tego pliku. W linii japońskiej możesz więc czytać
   tylko słowa.

## 3. Limity — jedna liczba, którą można policzyć

`limit:` podaje **liczbę polskich znaków, jaka mieści się w grze**. Liczy się każda
litera i każdy znak interpunkcji; polska litera (`ą`, `ł`, `ż`) to jeden znak, znak
japoński — dwa. Nie ma tu żadnych innych jednostek ani tabel pomiarowych.

- **Dialogi i narracja (`sceny.zip`): `do 270 znaków`.** Tyle mieści się w oknie
  dialogowym: ma ono trzy linie, angielska wersja gry używa najdłużej 137 znaków
  w jednej linii, a polski jest od angielskiego o kilkanaście procent dłuższy —
  3 × 90 = 270 zostawia zapas. To jeden budżet na całą kwestię, nie „270 na każdą linię”.
- **Nazwy i tabele (`widoki.zip`): `do N znaków`.** `N` to długość najdłuższego tekstu,
  jaki gra wyświetla **w tym samym polu** — nie w całej tabeli i nie w tym jednym
  elemencie. Dlatego w tabeli trzymającej jeden rodzaj danych (nazwy broni, imiona
  pilotów, tytuły misji) wszystkie wpisy mają ten sam limit, a w tabeli mieszającej pola
  (np. `system_text`) każde pole ma własny limit. Przy wątpliwości wybierz krótszy
  wariant — za długi napis nachodzi na sąsiednie pole, co widać w grze.
- **Skąd te liczby:** z pomiaru tekstów, które gra sama wyświetla (`docs/LIMITY_Y.md`).
  To dobre przybliżenie, nie pomiar w pikselach. Jeśli któraś linia okaże się za długa,
  dostaniesz poprawioną paczkę z nowym `limit:`, a nie uwagę „skróć, bo tak wyszło”.

## 4. Polskie znaki i interpunkcja

`ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż` działają — polskie otwarcie gry zostało
sprawdzone w grze z tymi znakami i wyświetla się poprawnie. Poza nimi nie używaj innych
znaków spoza zwykłego ASCII i japońskiej interpunkcji, którą widzisz w `EN:`
(`―`, `…`, `‘ ’ “ ”`, `♪`, `×`). Zamiast myślnika `—` pisz `-`.

**Fala `～` (odpowiedź na pytanie 3).** Japoński używa `～` w dwóch rolach: jako zakres
(„A～B”) i jako przeciągnięcie w mowie („は～い”). Angielska wersja gry **nie używa go
ani razu** (0 z 120 tys. linii fabuły, 0 z 44 tys. elementów tabel) — więc i polski go nie
używa. Zasada: **nigdy nie wpisuj `～` ani `〜`**, zamiast tego `-` (zakres, np. „1-3”)
albo nic (przeciągnięcie: „Tak… no jasne”). W nagłówkach typu `～エーアデント ブリッジ～`
tyldy po prostu znikają: `A. Advent — mostek`.

## 5. Elementy bez `PL:`

Element oznaczony `(powtórzenie elementu N — nie wpisuj tu nic)` powtarza tekst, który
już jest w tym samym pliku. Tłumaczenie dziedziczy się samo — nic tam nie pisz.

Element z `EN: (brak wersji angielskiej w grze)` nie ma angielskiego odpowiednika
(w grze jest tylko japoński) — tłumaczysz z japońskiego, tak jak resztę.

## 6. Dwie wersje bohatera — odpowiedź na pytanie 6

**Bohater nie jest jednej płci. W grze są dwie wersje — męska i żeńska — i obie mają
pełny tekst.** Gracz wybiera jedną na początku, ale scenariusze zawierają oba warianty,
a paczka zawiera oba, bo oba są w grze i oba trzeba przetłumaczyć.

Skąd to wiemy z danych, a nie z domysłów:

- skrypty scen mają jawne znaczniki gałęzi: `{Cmd_BranchProtagonist_Begin, 0}` to
  komentarz `男Ａ分岐開始` („początek gałęzi: bohater A”, mężczyzna),
  `{Cmd_BranchProtagonist_Begin, 1}` to `女Ａ分岐開始` (bohaterka), z odpowiadającymi
  `_End`;
- w każdym zdaniu mówca ma identyfikator: `pid_MHERO` (bohater) i `pid_FHERO` (bohaterka)
  — **żadna kwestia bohatera nie jest bez identyfikatora** (7,992 kwestii);
- kwestie innych postaci w tych samych blokach też różnią się między wariantami
  (np. „Mister $F” / „Miss $F” w angielskim), a całe bloki odpowiedzi są rozdzielone;
- część wariantów leży w osobnych blokach tej samej sceny: blok, w którym mówi bohater,
  może być pokazany tylko na jego trasie, więc wszystkie jego linie są jednego wariantu.

Dlatego **9,034 linii** ma znacznik `(wariant: bohater)`, **8,623 linii**
`(wariant: bohaterka)`, a reszta (103,008) jest wspólna dla obu
wersji — tego nie ruszamy.

Co to znaczy dla polskiego:

1. **Linia ze znacznikiem** — pisz tak, jak wymaga tego podana płeć: `(wariant: bohater)`
   → „powiedziałem, gotów, sam”, `(wariant: bohaterka)` → „powiedziałam, gotowa, sama”.
   Dotyczy to także kwestii *innych* postaci: skoro blok jest z bohaterem, to zwracają się
   do mężczyzny („pan”, „zrobiłeś”) i odwrotnie.
2. **Linia bez znacznika** — jest wspólna, więc jeśli polskie zdanie wymaga rodzaju
   (a w czasie przeszłym prawie zawsze wymaga), **wybierz formę neutralną**: czas
   teraźniejszy („Nie wierzę”, „Idziemy”), stronę bierną, rzeczownik zamiast imiesłowu,
   albo konstrukcję bezosobową („Trzeba iść”, „Udało się”). Wtedy obie trasy czytają się
   poprawnie. Nie zgaduj płci — błędny rodzaj jest gorszy niż zdanie neutralne.
3. **Zwroty do bohatera bez znacznika** (np. „$F…さん…” → „panno/panie $F”) pisz bez
   rodzaju: „poznać $F”, „z $F”, „u $F”. To jedyne miejsce, gdzie naprawdę trzeba się
   nagimnastykować — i dlatego lepiej unikać formy „pan/pani”, niż strzelać.
4. `$n`, `$c`, `$F` są **bezrodzajowe** — gra podstawia imię, skrót i pełne nazwisko
   niezależnie od płci. Rodzaj nosisz w słowach wokół tokenu, nie w tokenie.

## 7. Cytaty bitewne — odpowiedź na pytanie 1 (i zmiana etykiet)

Tabela `battle_voice` ma **34 317 kwestii w 39 bankach** (31 w podstawce, 8 w dodatkach)
i nie ma w niej kolumny z mówcą. Wniosek „mówcy nie da się ustalić” był błędny — dane gry
to ustalają i zostało to odczytane. Łańcuch jest taki:

```text
wiersz battle_voice  (klucz 01999dc9:15e0b000)
  -> battle_voice Shared Data   (m_Id -> m_Key, np. F069_002)
  -> kontener głosu             (WaveId -> nameText: imię, które gra wypisuje nad kwestią)
```

Skąd pewność: sprawdzone na okrzykach, o których wiadomo, kto je wykrzykuje —
`イデオンソード` wraca z mówcą **コスモ** (pilot, nie robot イデオン), `ダ・ガーン` z **星史**,
`ゲッタービーム` z **拓馬**, `ブライ・ソード` z **キッド**. Nic nie jest zgadywane z treści:
etykieta to pole `nameText` z pliku gry.

**Co się zmieniło w plikach.** Etykieta cytatu nie jest już numerem banku, tylko mówcą:

```text
2541. [Cytat bitewny — アムロ (Amuro), m] 「当たれっ！」
2542. [Cytat bitewny — シャア (Char), m] 「遅い！」
2543. [Cytat bitewny — ??? 012] 「いいだろう！」
```

- **`m` = mężczyzna, `k` = kobieta, `miesz.` = głos zbiorowy lub mieszany** (chórek, „oni”).
  Płeć pochodzi z tabeli pilotów, nie z domysłu o tekście.
- W nawiasie jest **angielska wersja imienia z gry**; gdy gra jej nie ma, zostaje samo imię
  japońskie.
- **`??? NNN`** to cytat, którego zestawu głosu **nie ma w wydanym buildzie** — wiersz
  w tabeli jest, pliku z nagraniem nie ma (sprawdzone na wszystkich plikach gry). Takich
  kwestii jest **1 915 (5,6%)** i właściciel projektu zdecydował, że **przekładamy je
  mimo to** — lepszy polski bez imienia niż angielski.

### Co zrobić z `??? NNN`

`widoki.zip` ma osobny plik **`09_grupy_bez_mowcy.md`** — indeks wszystkich 138 grup:
ile kwestii, z jakiej tabeli, z jakiej serii (gdy dowiedziona) i **podpowiedź mówcy**
tam, gdzie da się ją uzasadnić.

1. **Jeden numer = jedna postać.** W obrębie numeru trzymaj **jeden rodzaj gramatyczny**.
   Zmiana rodzaju w środku numeru to błąd; między numerami — to różne postacie, więc
   rodzaj może się różnić.
2. **Podpowiedź nie jest etykietą.** Dla 1 870 z 1 915 kwestii w tej samej rodzinie głosu
   są już kwestie z imieniem i wszystkie mają jednego mówcę — to dobra podpowiedź płci.
   Ale jeśli japoński tekst sam mówi o płci (`俺` / `私` / `あたし`, formy żeńskie),
   **wierzymy tekstowi japońskiemu**.
3. **Gdy nie wiadomo nic** — pisz bez rodzaju: czas teraźniejszy, tryb rozkazujący,
   bezosobowo („Trzeba się wycofać”). To ta sama zasada, co w sekcji 6 dla linii wspólnych
   bohatera.

Dlaczego nie ma tam imion: rodzina głosu bywa wielomówcza (w jednym banku mówi nawet
40 postaci), a treść bywa myląca — te same nazwy robotów padają w cudzych kwestiach.
Błędne imię albo błędny rodzaj w paczce jest gorszy niż numer grupy.

## 8. Pozostałe odpowiedzi

**Pytanie 2 — wiersze szesnastkowe w `08_*.md`.** Tabela `font` (4 wiersze z kluczami
typu `a1b2c3…`) to nie tekst, tylko wewnętrzne nazwy zasobów czcionek. W paczce
**nie ma jej w paczce w ogóle** — nie ma tam czego tłumaczyć ani czego zostawiać
pustego. Plik `08_pokrewne.md` zawiera teraz tylko `prolog` (24 krótkie teksty
wprowadzające). Jeśli w przyszłości zobaczysz klucz złożony z samych cyfr i liter
`a-f` bez sensownego tekstu obok — to ten sam przypadek; zgłoś, wytniemy.

**Pytanie 4 — scena → rozdział / misja. ODPOWIEDŹ: mapa jest i jest w tej paczce.**
Wcześniejsza odpowiedź („nie ma powiązania”) była **za szeroka i była błędna**. Nie ma go
w *skryptach scen* — to prawda, tytuły misji nie występują w treści żadnej sceny. Ale nie
trzeba go szukać w tekście: **dane misji gry same wymieniają pliki każdej misji**.

```text
missionRomList[]   (MissionData, MissionD1Data … MissionUlData — 15 tabel, 533 misje)
  -> id:          m0001_0000310        numer misji
  -> chapterNo:   1                     rozdział (0 = poza rozdziałami)
  -> name:        "m0001_0000310：花と忍と誕生日"   tytuł misji
  -> composition: sdemo_file / dlgev_file / script_file   pliki scen tej misji
```

Skrypt sceny nazywa się tak samo jak plik w `composition`, więc połączenie jest
**dokładnym porównaniem nazwy pliku**, nie domysłem:

```text
scena  cse20_0001_0000310a  ->  composition.sdemo_file "cse20_0001_0000310a"
       ->  misja m0001_0000310, rozdział 1, tytuł 花と忍と誕生日
```

**Skuteczność — policzona, nie zadeklarowana:**

| co | ile | jak |
|---|---|---|
| scen w grze | **611** | wszystkie pliki scen z podstawki i dodatków |
| scen przypisanych do misji | **588** | 580 po nazwie pliku + 8 po kluczach presetów |
| misji w danych | **533** | z 15 tabel `Mission*Data` |
| misji z rozdziałem 1–7 | **144** | `chapterNo` > 0 |
| scen z rozdziałem 1–7 | **188** | reszta to dodatki, bonusy i misje poboczne |
| scen bez wpisu misji | **23** | wypisane wprost jako `brak wpisu misji w danych` |

Te 8 scen z presetów to scenki zdarzeń, których nazwa pliku różni się o jedną literę od
wpisu misji; znajdują je klucze `ICE_OP_ADVICE_*` w presetach (198 presetów ma takie
klucze, 15 trafia w scenę). Celowo **nie zgaduję** dla pozostałych 23 scen — są to
rodziny `cse20_0900_*` (samouczek), `cse20_095x_0999900` (ekrany systemowe) i kilka
`cse20_0041/0047/0059/0024`, których nie ma w żadnym wpisie misji ani w żadnym kluczu
presetu. W plikach widzisz wtedy `misja: brak wpisu misji w danych` i to jest cała
prawda o tej scenie — nic nie zostało dopisane „na oko”.

**Co z tego masz w plikach:**

1. **`spis-scen.md`** — 611 scen, a przy każdej: `misja` (np. `m0001_0000310`),
   `rozdział` (1–7 albo `—`), plik `.md`, mówcy, liczba linii. `—` znaczy „ta misja nie
   ma numeru rozdziału w danych”, nie „nie wiadomo”.
2. **`spis-misji.md`** — cały flow fabuły: rozdział 1 … 7, w każdym misje po numerze,
   z tytułem japońskim, liczbą scen i liczbą linii; na końcu misje spoza rozdziałów
   w podziale na paczki (dodatek rocznicowy, DLC, bonusy, sezon pass, przedpremiera).
3. **nagłówek każdej sceny w plikach `odcinek-*`/`dlc-*`** — dwie nowe linie:
   `- misja: m0001_0000310, rozdział 1` i `- tytuł misji: 花と忍と誕生日`. Czytasz scenę
   i od razu wiesz, w którym miejscu scenariusza jesteś.
4. **`06_teksty_misji.md`** — przy każdym tytule misji linia `misja: …` z tym samym
   numerem i rozdziałem. Tytuł, scena i plik zawsze do siebie pasują.

Numeracja elementów, klucze i linie `PL:` **się nie zmieniły** — mapa to wyłącznie nowe
linie informacyjne, więc tego, co już przetłumaczone, nie trzeba ruszać.

**Pytanie 5 — `鋼鉄ジーグ` i „Getter Robot – The Jet-Black Drifters”.** To nie jest
błąd danych. W `00_postacie.md`:

- element **732** `[Imię pilota (DLC2)] 鋼鉄ジーグ` → EN: **Kotetsu Jeeg** — poprawnie;
- element **1901** `[Nazwa serii (DLC2)] 鋼鉄ジーグ` jest **powtórzeniem elementu 732**
  („nie wpisuj tu nic”) — stąd wzięło się wrażenie, że ta sama nazwa ma dwie różne
  angielskie wersje;
- angielskie „Dynamic Planning Original (Getter Robot – The Jet-Black Drifters)” należy
  do **elementu 1902** `ダイナミック企画オリジナル（ゲッターロボ 漆黒の漂流者）`, czyli do
  innej serii.

Czyli: `鋼鉄ジーグ` = „Kotetsu Jeeg” (albo „Jeeg z Kotetsu”, jeśli wolisz tłumaczyć),
a Getter to osobna pozycja. W wersji 4 powtórzenia są oznaczone wyraźniej.

## 9. Co się zmieniło w wersji 8

1. **Mapa scena → misja → rozdział.** Nowe linie w nagłówku każdej sceny (`misja:`,
   `tytuł misji:`), nowe kolumny w `spis-scen.md` i nowy plik **`spis-misji.md`**.
   Powiązanie pochodzi z danych misji gry (nazwa pliku w `composition`), nie z domysłu:
   **588 z 611 scen** przypisanych, 23 wprost oznaczone jako bez wpisu misji.
2. **`06_teksty_misji.md`** — przy każdym tytule misji linia `misja: m…, rozdział N`.
3. **Nic, co już przetłumaczone, nie wymaga zmian** — numeracja elementów, klucze i linie
   `PL:` są identyczne jak w wersji 7; doszły tylko linie informacyjne.

### Co się zmieniło w wersji 7 (poprzednia)

1. **Etykiety cytatów bitewnych: numer banku → mówca.** `[głos N/39]` zniknął;
   **94,4% cytatów** ma imię i płeć z danych gry, reszta numer grupy `??? NNN`.
   Pliki do tłumaczenia mają **te same elementy i tę samą numerację** — zmienił się tylko
   tekst w nawiasie kwadratowym. Tego, co już przetłumaczone, nie trzeba przerabiać.
2. **Nowy plik `09_grupy_bez_mowcy.md`** — indeks 138 grup `??? NNN` z liczbą kwestii,
   tabelą, serią i podpowiedzią mówcy/płci. Bez tekstu gry, tylko spis.
3. **Płeć mówcy** w etykiecie (`m`, `k`, `miesz.`) — z tabeli pilotów (`PilotBasicDatas`),
   dla 28 763 z 32 402 nazwanych cytatów. Reszta bez oznaczenia płci.
4. Każda kwestia bohatera i każda kwestia z bloku jednego wariantu płci ma znacznik
   `(wariant: bohater)` / `(wariant: bohaterka)`; nagłówek sceny podaje, ile linii ma
   każdy wariant (sekcja 6).
5. Pełne dane dodatków — 611 scen i 120,665 linii, tyle ile w grze.
6. Tabela `font` (klucze szesnastkowe) nie jest wysyłana.
7. Nowe zasady: `～` (sekcja 4), rodzaj bohatera (sekcja 6), cytaty `???` (sekcja 7).

## 10. Co odesłać

Te same pliki `.md` (może być zip), z wypełnionymi liniami `PL:`. Zapis w UTF-8,
nazwy plików bez zmian. Można partiami — np. po jednym `odcinek-*.md`.
