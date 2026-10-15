# Jak nałożyć angielskie tłumaczenie SRW OE — instrukcja (stan 2026-10-15 wieczorem: pakiet v5 / KIT 18, grafiki interfejsu UI_TEST3 i w HOKUS_POKUS)

To jest instrukcja dla osoby, która ma **własne** japońskie pliki gry (ISO rozdziału 1 w wersji
1.08, 679 243 152 bajty, i odszyfrowane pliki DLC rozdziałów 2–8) i chce zobaczyć na nich angielski
tekst. Nic z oryginałów nie jest ruszane: ISO i DLC są tylko czytane, wynik ląduje w osobnym folderze.

Uczciwie o stanie: **to nie jest skończone tłumaczenie.** Od 2026-10-15 (testy Y4a / Y4 / Z4) pełny
zestaw z pakietu v4 — `patched.iso` + cały folder DLC z `HOKUS_POKUS.bat` — **działa w grze**: Loading,
nowa gra, sejw z 2. rozdziału, ekrany statusu i umiejętności. Pierwsze zrzuty z grania pokazały dwa
błędy tekstu, poprawione w **pakiecie v5 / KIT 18** (jeszcze nie sprawdzonym w grze): nazwy jednostek
dłuższe niż 14 znaków wchodziły w liście na kolumnę pilota, a opis umiejętności „Coord. Atk” pokazywał
„Group4” (szczegóły w `CO_NOWEGO_v5.txt`). Czego w nim brakuje: (1) dialogi
rozdziałów 5–8 są w pakiecie w większości bez angielskiego (tłumaczenie trwa), (2) **etykiety
systemowe na ekranach statusu / broni / umiejętności / intermisji (攻撃 防御 命中, 能力 改造 武器 機体,
特殊能力・スキル, 気力, 援護 …) nie są tekstem, tylko obrazkami** — pierwszy zestaw (`UI_TEST1`) **działa
w grze** (test z 15.10), komplet 26 tekstur (walka, opcje, części, ulepszenia, ikony z 2-literowymi kodami,
sceny nawigacji) jest w `UI_TEST3.zip` i od tej wersji narzędzi `HOKUS_POKUS.bat` wmalowuje je sam (część 4
niżej); po japońsku zostają tylko ikony `mensys_12` (czekam na zrzut, gdzie je widać); (3) komunikaty
z programu gry (autozapis) — poza zasięgiem.
Drobny znany błąd układu: pasek podpowiedzi w słowniku nachodzi na zakładkę „Pilot”.

Zasada stała: żaden plik `.bat` nie każe wpisywać ścieżek — zawsze otwiera okno wyboru pliku/folderu.

---

## Co jest na Dysku (folder DELIVERY) — stan 2026-10-15 wieczorem, pakiet v5 + UI_TEST3

| plik | do czego |
|---|---|
| `pakiet_EN_2026-10-15_v5.zip` | **jedyny aktualny pakiet tłumaczenia** (rozpakować do `srw-oe-translation\pakiet_EN\`); = v4 + 124 poprawione wiersze, lista w `POPRAWKI_v5.tsv`, opis w `CO_NOWEGO_v5.txt` |
| `KIT_build18_2026-10-15.zip` | pliki z budowy #18 (pakiet v5) do testów bez budowania: `USRDIR_build18\` (5 plików do ISO dla `WGRAJ_DO_ISO.bat`), `DLC_build18_config\` (10 plików do folderu DLC: `config00.cpk`, `configst.cpk`, `config01–08.EDAT`), `CZYTAJ.txt`. Pełny efekt v5 (nazwy jednostek rozdziałów 9+, pilot Kuro) daje dopiero `HOKUS_POKUS.bat` z pakietem v5 — KIT pokrywa rozdziały 1–8 |
| `RUNDA8_build14.zip` | `config00.cpk` + `configst.cpk` z budowy #14 — para sprawdzona w grze z oryginalnym DLC (odniesienie) |
| `UI_TEST3.zip` | **grafiki interfejsu, komplet 26 tekstur** (zastępuje `UI_TEST2`; pierwszy zestaw `UI_TEST1` wariant A działał w grze): `system.cpk`, `tacsys.cpk`, `IM1000.cpk`, `IM3000.cpk`, `IM9000.cpk`, `navisys.cpk` z angielskimi napisami wmalowanymi w tekstury (walka: Attack / Defend / Evade / Counter, bannery, Unit Info, Start Battle, Your turn / Enemy turn…; opcje dźwięku; części; ulepszenia; **ikony z 2-literowymi kodami**: teren GR / AI / SP, cechy broni BR / AR / PU / TH / CO, kule ducha VA BU AC FL FO PE WA GA FR DI, badge SR / DH; sceny nawigacji Battle / Evade / Confirm / Cancel / Enemy Sighted). Wgrywa się `WGRAJ_DO_ISO.bat` (**aktualne narzędzia** — starsze nie znają `navisys.cpk`) **na `patched.iso` z pakietu (v5 lub v4), które NIE ma jeszcze wgranego UI_TEST1/2** (wskazać folder `UI_TEST3`). Przy budowie od nowa `HOKUS_POKUS.bat` robi to sam. Legenda kodów i instrukcja w `CZYTAJ_UI_TEST3.txt` w środku |
| `INSTRUKCJA_PL.md` | ten tekst |
| `_STARE_NIE_UZYWAC\…` | pakiet v4 i `KIT_build17` (działały w grze, ale z dwoma błędami tekstu — zastąpione przez v5/KIT 18), `UI_TEST1` (wariant A działał) i `UI_TEST2` (zastąpione przez `UI_TEST3`), pakiet v3 i `KIT_build15` (ich `config01–08.EDAT` padają na Loading — test Y), oraz wszystko z 14–15.10 sprzed poprawki `+52`. **Nie kopiować.** |

Jak odróżnić pliki: `config00.cpk` z budowy #18 (pakiet v5) ma **936 064 B, md5
`5c43cf343b9fafde62c3c53c3a6c1e78`**; z budowy #17 (pakiet v4, sprawdzony w grze) ten sam rozmiar, md5
`80b8fae61b858fb91db35532c4680c6f`; z budowy #14 / pakietu v3 md5 `71d9fcafa37c21513b97c14d1dff8f33`.
`configst.cpk` **372 864 B, md5 `6cfe245d5f6ec6dfffd2a829b778a4d7`** (bez zmian od #14). `config01.EDAT`
z v5 ma **247 936 B (rozmiar oryginału), md5 `8db9f78108b829526ef5a7176847c5fd`** (z v4:
`7c6459fa7377b585a5176b5859361da2`; z v3 miał 249 984 B). Każdy inny md5 = stare narzędzia albo
stary pakiet (`DIAGNOZA.bat` sprawdza to za ciebie i rozpoznaje buildy #15/#17/#18/pulaJP po md5).

---

## Część 1 — budowa (jeden `.bat`, 10–15 minut)

Potrzebne raz: **Python 3.9 lub nowszy** — <https://www.python.org/downloads/>, przy instalacji
zaznacz **„Add python.exe to PATH”**. Nic więcej (żadnych bibliotek).

1. **Świeże narzędzia.** Ściągnij repozytorium jako ZIP: strona repozytorium → gałąź
   `arena/c0e5c9d1-mtgcrawler` → zielony przycisk **Code** → **Download ZIP** (bezpośredni link:
   `https://github.com/szybkoiwyraznie-rgb/mtgcrawler/archive/refs/heads/arena/c0e5c9d1-mtgcrawler.zip`).
   Rozpakuj do **nowego, pustego** folderu — nie nadpisuj starego rozpakowania (stary folder może
   mieć stare `tools\*.py` i stary `pakiet_EN\`). Interesuje cię podfolder `srw-oe-translation\`.
   Świeży zestaw poznasz po tym, że obok `HOKUS_POKUS.bat` leży **`DIAGNOZA.bat`**.
2. **Pakiet v5.** Ściągnij z Dysku `pakiet_EN_2026-10-15_v5.zip` i rozpakuj tak, żeby plik
   `00_dialogue.jsonl` leżał **bezpośrednio** w `srw-oe-translation\pakiet_EN\` (w zipie jest
   folder `pakiet_EN_2026-10-15_v5\` — jego zawartość, nie on sam). Żadnych innych `*.jsonl` obok
   (stary v4/v3 usuń w całości).
3. **`HOKUS_POKUS.bat`** (dwuklik). Dwa okna wyboru: (1) plik `SRW OE 1.08.iso`;
   (2) **folder z odszyfrowanymi plikami DLC** (zestaw FULL_DLC). Czekaj na „Gotowe”
   (~4 min budowy + przepisanie ISO 680 MB).
4. **Wynik** w `srw-oe-translation\srw-oe-patch\`: `patched.iso`, `DLC\…` (91 plików `*.EDAT` +
   `config00.cpk`, `configst.cpk`), `build_report.json`.
5. **Zanim cokolwiek skopiujesz — `DIAGNOZA.bat`** (część 2). Dopiero gdy raport mówi
   „pakiet v5 — AKTUALNY”, „`+52` TAK”, „budżet pul DLC TAK” i „config00 = BUILD18”, kopiuj.
   W `build_report.json` jest teraz też pole `skill_total` (Skill00 + 8 pul; ma być ≤ 342 194 B,
   z v5 wychodzi 340 074 B).
6. **Wgranie:** kopia zapasowa folderu DLC emulatora (cały folder obok, z dopiskiem `_ORYGINAL`),
   potem wszystkie pliki z `srw-oe-patch\DLC\` do folderu DLC emulatora (nadpisać). W PPSSPP
   uruchom `srw-oe-patch\patched.iso`.

Jeśli zamiast „Gotowe” jest „Cos odmowilo”: nie kasuj niczego, prześlij `build_report.json`
i `DIAGNOZA.txt`.

---

## Część 2 — `DIAGNOZA.bat`: co jest zbudowane i co jest wgrane (nic nie zmienia)

Uruchom `srw-oe-translation\DIAGNOZA.bat`. Dwa okna wyboru: (1) **folder DLC, z którego czyta
PPSSPP** (`…\PSP\GAME\NPJH50521` albo twoja lokalizacja); (2) **ISO, które uruchamiasz w PPSSPP**
(`patched.iso`; Anuluj = bez części o ISO). Resztę (narzędzia, `pakiet_EN\`, `srw-oe-patch\`) skrypt
znajduje sam obok siebie. Wynik: `DIAGNOZA.txt` (otwiera się w Notatniku) — **ten plik prześlij**.

Raport zawiera tylko nazwy, rozmiary i sumy md5 (żadnych bajtów gry) i odpowiada na pytania:

1. czy narzędzia obok `.bat` to świeża gałąź (markery poprawek `+32`, `+36`, `+52`, budżet Skill00);
2. który pakiet leży w `pakiet_EN\` (v1 z 14.10 / v2 / v3 / v4 / v5 — po md5 plików `03`/`04`) i czy nie
   jest rozpakowany o jeden folder za głęboko;
3. co zbudował HOKUS_POKUS (`build_report.json`: odmowy zapisu, brakujące kontenery; md5 plików w
   `patched.iso` i w `DLC\`, rozpoznane po tabeli znanych buildów);
4. co **naprawdę** leży w folderze DLC emulatora: identyczne z budową / inne niż budowa /
   oryginał / stary build (#6–#13 rozpoznawane po md5; `config01–08.EDAT` rozpoznawane jako
   build #15 / build #17 / wariant pulaJP);
5. co jest w ISO uruchamianym w PPSSPP (5 plików USRDIR: oryginał / build #14 / #17 / inny).

Na końcu sekcja **WNIOSKI** — automatyczne zdania typu „config00.cpk w folderze DLC to build #12
(stary)”. Jeżeli WNIOSKI są puste, instalacja jest taka, jak ma być, i crash to sprawa plików
samych w sobie — wtedy część 3.

---

## Część 3 — runda testów pakietu v4 (ZALICZONA 2026-10-15: Y4a, Y4 i Z4 działają)

Ta runda jest już za nami — zostawiam opis, bo te same kroki służą do odtworzenia stanu „działa”
po każdej kolejnej zmianie (dla pakietu v5 podstaw `KIT_build18` / `DLC_build18_config` /
`USRDIR_build18` — układ plików jest ten sam; v5 w grze jeszcze nie sprawdzony). Wyniki X/Y z 2026-10-15 (X działa, Y pada) były jej podstawą. Za każdym razem **zacznij od
przywrócenia folderu DLC emulatora z kopii `_ORYGINAL`**; ISO = **oryginalne** `SRW OE 1.08.iso`,
chyba że napisano inaczej. Pliki do kopiowania: `KIT_build17_2026-10-15.zip` z Dysku (te same
bajty co twoja budowa z pakietem v4). Zanotuj: **działa** (tytuł po „Loading”) / **crash** (zrzut PPSSPP).

**Y4a — tylko config.** Oryginalny folder DLC + 10 plików z `DLC_build17_config\` (nadpisać:
`config00.cpk`, `configst.cpk`, `config01–08.EDAT`). To jest dokładnie to, co w teście Y padało,
tyle że z pulami ≤ oryginału.

**Y4 — cały zestaw DLC.** Jak Y4a + **wszystkie** 91 `*.EDAT` z twojej budowy `srw-oe-patch\DLC\`
(HOKUS_POKUS z pakietem v4; pozostałe 83 pliki są identyczne z budową #15).

**Z4 — pełny patch.** ISO = `srw-oe-patch\patched.iso` (albo `srw-oe-wgrane\USRDIR_build17\patched.iso`
z `WGRAJ_DO_ISO.bat` i folderem `USRDIR_build17\`) + folder DLC z testu Y4. Potem: sejw z 2. rozdziału,
nowa gra, lista umiejętności pilota w rozdziale 2 (tam są teksty z pul).

**Y3 — tylko gdy Y4a padł.** Oryginalny folder DLC + `config00.cpk` i `configst.cpk`
z `DLC_build17_config\` + 8 plików z `DLC_pulaJP_config01-08\` (pule japońskie, reszta po angielsku).

| wynik | wniosek | następny krok |
|---|---|---|
| Y4a działa | pule były winne (budżet trzyma) | Y4 |
| Y4a crash, Y3 działa | gra nie toleruje zmienionych pul nawet ≤ oryginału (treść, nie rozmiar) | prześlij zrzut; wrócę z pulami bajt-w-bajt tej samej długości |
| Y4a crash, Y3 crash | problem poza pulami: słowniki/Item/DLC_ID w `config01–08` albo `config00` v4 | prześlij oba zrzuty + `DIAGNOZA.txt`; następna runda = `config00` v4 sam |
| Y4 crash (po Y4a OK) | winny któryś z 83 pozostałych EDAT | `BISEKCJA.bat` literą `H` (EDAT z dialogami), potem `I` |
| Z4 działa | pełny patch działa — pierwszy raz | graj; zbieraj zrzuty błędów tekstu (np. pasek podpowiedzi w słowniku nachodzi na zakładkę „Pilot” — znany, do poprawki) |

Po każdym teście `DIAGNOZA.bat` (okno 1: folder DLC emulatora, okno 2: ISO) i prześlij
`DIAGNOZA.txt` + zrzut PPSSPP przy crashu. Przy Y4/Z4 dołącz też `srw-oe-patch\build_report.json`.

## Część 4 — grafiki interfejsu: `UI_TEST3.zip` (szybki test) albo `HOKUS_POKUS.bat` (od tej wersji sam)

Napisy systemowe na ekranach statusu / broni / umiejętności, zakładki intermisji, napisy w walce (okno
reakcji, bannery, nagłówki tur), ikony i przyciski scen nawigacji są obrazkami w sześciu plikach ISO:
`system.cpk`, `tacsys.cpk`, `IM1000.cpk`, `IM3000.cpk`, `IM9000.cpk`, `navisys.cpk`. Pierwszy zestaw
(`UI_TEST1`, wariant A = dane bez kompresji) **działa w grze** (zrzuty z 15.10) — komplet 26 tekstur w tej
samej technice to `UI_TEST3.zip` (26 tekstur, 137 napisów / kodów; podgląd przed/po w `podglad\`). Nic
z UI_TEST2/UI_TEST3 nie było jeszcze w grze. Ikony z pojedynczym kanji mają teraz **2-literowe kody**
(w środku ikony jest ~10×10 px — 3 litery się nie mieszczą, a 1 litera myliłaby się z rangami S/A/B/C/D
obok): teren **GR** Ground / **AI** Air / **SP** Space; cechy broni **BR** Break, **AR** Arc Shot, **PU** Push,
**TH** Throw (z „karbem” = Pull Throw), **CO** Combination (M i B zostają); badge **SR** Surround, **DH** Direct
Hit; kule ducha **VA** Valor, **BU** Bullseye, **AC** Accel, **FL** Flash, **FO** Focus, **PE** Persist, **WA** Wall,
**GA** Gain, **FR** Fortune, **DI** Disrupt. Nawigacja: Battle / Evade / Musai / Confirm / Cancel / Enemy Sighted.

Droga A — szybki test na gotowym `patched.iso` (nic nie buduje):

1. Rozpakuj `UI_TEST3.zip` (folder `UI_TEST3\` z sześcioma `.cpk` na wierzchu). Pobierz też aktualny ZIP
   gałęzi z GitHub — starszy `WGRAJ_DO_ISO.bat` nie zna `navisys.cpk` i odmówi.
2. `WGRAJ_DO_ISO.bat` → okno ISO: **`patched.iso` z pakietu v5 (lub v4), do którego NIE wgrywałeś
   UI_TEST1/UI_TEST2** (narzędzie zna md5 oryginalnych plików i odmówi: „system.cpk w tym ISO nie jest
   oryginalny”; w razie czego zbuduj `patched.iso` od nowa albo weź kopię sprzed UI_TEST1) → okno
   folderu: **`UI_TEST3`**. Wynik: `srw-oe-wgrane\UI_TEST3\patched.iso`.
3. Uruchom w PPSSPP z tym samym folderem DLC co dotąd. Sprawdź walkę: okno reakcji (Attack / Defend /
   Evade / Counter), bannery (Counter / Attack / Defend / Critical / Evade), ekran przed walką (Unit Info,
   Start Battle, Support Setup), nagłówek tury (Your turn / Enemy turn), Units Ready, wynik walki
   (Level Up!, Spirit Cmd, Skill, Get!); poza walką: opcje dźwięku, ekran części / konwersji (Parts List,
   Convert, Equip, Team), ekran ulepszeń (Upgrades, Linked Units, Upgrade Limit Break); ikony: teren
   GR / AI / SP przy rangach, cechy broni BR AR PU TH CO obok M / B, kule ducha nad jednostką, scena
   nawigacji (Battle / Evade / Confirm / Cancel / Enemy Sighted). Zrzuty napisów uciętych, nachodzących
   lub za małych — szczególnie Counter, Critical, Team, Equip, Spec./Mat. i **czy kody na ikonach da się
   przeczytać przy twoim skalowaniu PPSSPP** (to najmniejsze napisy w patchu, 7–9 px).

Droga B — przy budowie od nowa: po pobraniu aktualnych narzędzi (ZIP gałęzi z GitHub) `HOKUS_POKUS.bat`
po wstawieniu tekstu **sam** czyta te sześć plików z twojego ISO, wmalowuje napisy i wstawia je do
`patched.iso` (krok „Tekstury UI”; w `build_report.json` klucz `ui_textures`, każdy plik z md5). Jeśli
któryś napis się nie zmieści, budowa jest przerwana z komunikatem — nic nie jest wstawiane „na pół”.
Wyłączenie (tylko tekst): `python tools\build_translation_patch.py … --no-ui-textures`.
`DIAGNOZA.bat` z ISO pokazuje teraz blok „tekstury UI” — oryginał / UI_TEST1 / UI_TEST2 / UI_TEST3 / nieznany.

| wynik | wniosek | następny krok |
|---|---|---|
| wszystko czytelne | technika potwierdzona na walce | poprawki pojedynczych napisów ze zrzutów |
| crash / czarne pola w walce | `tacsys.cpk` inaczej buforowany niż `system.cpk` | zrzut + moment; `WGRAJ_DO_ISO` z samym `system.cpk`+`IM*` (skopiuj je do osobnego folderu) |
| napis ucięty / nachodzi | komórka węższa niż założona | napisz który — skracam/ściskam konkretny napis |
| kody na ikonach nieczytelne | 7–9 px to za mało przy twoim skalowaniu | zamieniam na piktogramy / jednoliterowe kody w innym kolorze — do decyzji |

Świadomie po japońsku zostają: ikony `mensys_12` (連 持 特 防 突 早 狙 回 — nie wiem na pewno, gdzie gra je
pokazuje; prześlij zrzut z taką ikoną, dopiszę kody), 6-pikselowe znaczniki „連” w `intsys_01` (za małe)
i nagłówki 用 / 名 (kontekst niepotwierdzony).

---

## Gdy okno `.bat` miga i znika

Każdy `.bat` otwiera się ponownie w trybie, w którym okno **nie zamyka się** po błędzie. Jeśli
mimo to znika: otwórz folder `srw-oe-translation` w Eksploratorze, kliknij w pasek adresu, wpisz
`cmd`, Enter; w czarnym oknie wpisz nazwę pliku (np. `DIAGNOZA`) i Enter. Niebieskie „System
Windows ochronił ten komputer” → „Więcej informacji” → „Uruchom mimo to” (plik z pobranego zipa).

## Powrót do oryginału

W PPSSPP wskaż z powrotem swoje ISO, przywróć folder DLC z kopii `_ORYGINAL`, usuń
`srw-oe-patch\`. Żaden oryginalny plik nie był modyfikowany.

## Co dokładnie jest w pakiecie v5 (liczby z budowy #18, 2026-10-15 w nocy)

- Pakiet: 108 135 wierszy, 77 106 z angielskim + 3 686 identycznych (znaki, liczby); kontrola
  pakietu `translation_check`: 0 błędów. Dialogi fabularne: rozdziały 1–3 w całości, rozdział 4
  ~59 %, rozdziały 5–8 jeszcze po japońsku. Względem v3: 231 tekstów umiejętności skróconych
  (lista w `SKROCENIA_Skill00_v4_tier4_i_pule.tsv`), pule rozdziałów 2–8 = teksty Skill00.
- Względem v4 (po zrzutach z grania, lista w `POPRAWKI_v5.tsv`): 106 nazw jednostek w listach
  skróconych do ≤ 14 znaków (np. „Strike Freedom Gundam” → „Strike Freedom”, „VF-25F Messiah B” →
  „VF-25F (B)”, „/Movie” → nazwa bazowa; pełne nazwy na ekranie statusu bez zmian), 5 krótkich nazw
  pilotów-sojuszników (np. „Da Cider (Ally)” → „Da Cider/Ally”), 8 opisów „Coord. Atk” / „Group (GR)”
  bez zbędnej czwórki po „Group” (japoński bajt po `%s` był drugą połową glifu kana ﾌﾟ), pilot Kuro
  (miał cudzy angielski). Nowe reguły kontroli pakietu pilnują tych trzech rzeczy.
- Budżety rozmiaru pilnowane przez narzędzia: `srwDL_Skill00.bin` ≤ 216 768 B (zmierzone w grze),
  każda pula `srwDL_Skill01–08.bin` ≤ 15 638 B (= oryginał; przyjęte po teście Y), suma ≤ 342 194 B.
- Zmienione człony kontenerów są zapisywane **bez kompresji** (oryginał używa CRILAYLA), stąd
  pliki rosną: `mesbtl00.cpk` 348 888 → 994 008 B, `eventP00.cpk` 162 264 → 260 568 B,
  `imenu00.cpk` 34 984 → 57 512 B; rozpakowana zawartość rośnie najwyżej o ~6 %. Test X
  (2026-10-15) pokazał, że gra startuje z tymi trzema plikami i oryginalnym DLC.

## Czego ten pakiet NIE robi

- Pakiet tekstowy nie dotyka grafik. Etykiety systemowe w teksturach (ekrany statusu, broni,
  umiejętności, zakładki intermisji, pasek 気力/援護, walka, opcje, części) maluje osobny krok
  (`UI_TEST3.zip` albo aktualny `HOKUS_POKUS.bat`, część 4); pierwszy zestaw działał w grze, komplet —
  jeszcze nie sprawdzony. Po japońsku zostają tylko ikony `mensys_12` (czekam na zrzut).
- Nie tłumaczy komunikatu o autozapisie po starcie — siedzi w programie gry (`EBOOT.BIN`).
- Nie zawiera żadnych plików gry: wszystko powstaje z twojego ISO i twoich DLC.
- Nie działa na zaszyfrowanych plikach DLC ani na ISO innej wersji niż 1.08.
