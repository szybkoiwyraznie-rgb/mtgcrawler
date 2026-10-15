# Jak nałożyć angielskie tłumaczenie SRW OE — instrukcja (stan 2026-10-15 późnym wieczorem: pakiet v6, napisy programu gry EXE_TEST1, grafiki interfejsu UI_TEST4 — wszystko w HOKUS_POKUS)

To jest instrukcja dla osoby, która ma **własne** japońskie pliki gry (ISO rozdziału 1 w wersji
1.08, 679 243 152 bajty, i odszyfrowane pliki DLC rozdziałów 2–8) i chce zobaczyć na nich angielski
tekst. Nic z oryginałów nie jest ruszane: ISO i DLC są tylko czytane, wynik ląduje w osobnym folderze.

Uczciwie o stanie: **to nie jest skończone tłumaczenie.** Od 2026-10-15 pełny zestaw z `HOKUS_POKUS.bat`
— `patched.iso` + cały folder DLC — **działa w grze**: pakiet v4 (testy Y4a / Y4 / Z4), a potem **build #19 =
pakiet v5 + grafiki interfejsu UI_TEST3** („wszystko śmiga”: Loading, nowa gra, sejw, status, walka, listy).
Osiem zrzutów z buildu #19 pokazało ostatnie japońskie resztki i wszystkie trzy ich źródła są już obsłużone
w **pakiecie v6** + aktualnych narzędziach (jeszcze nie sprawdzone w grze): (1) **napisy zaszyte w programie
gry** (`PBOOT.PBP` = aktualizacja 1.08 z folderu DLC): panel broni w walce (`移動後`, `TGT 敵`), komunikaty
bitewne, linie zdolności broni z 1.08 (`<貫通 Lv2>`, `<ビーム兵器 Lv2>`, `<連携攻撃 Lv2>`), efekt Guard, komendy
i menu taktyczne, komunikaty o sejwie — nowy plik pakietu `09_executable.jsonl` (397 napisów), a `HOKUS_POKUS`
pisze teraz także `DLC\PBOOT.PBP` (część 5); (2) **31 całych napisów menu** (`メインパイロット`, `サブパイロット`,
`SELECT パイロット表示変更`, Sort, Page, System Setup…), które pakiet v5 miał tylko w kawałkach; (3) komórki
grafik (`WPN名`, ucięte „RNG”, „EN Cost”, ścięte ikony części / zdolności) — `UI_TEST4` (część 4).
Czego nadal brakuje: dialogi rozdziałów 5–8 w większości bez angielskiego (tłumaczenie trwa), ikony `mensys_12`
(czekam na zrzut, gdzie je widać), pasek podpowiedzi w słowniku nachodzi na zakładkę „Pilot”.

Zasada stała: żaden plik `.bat` nie każe wpisywać ścieżek — zawsze otwiera okno wyboru pliku/folderu.

---

## Co jest na Dysku (folder DELIVERY) — stan 2026-10-15 późnym wieczorem: pakiet v6 + EXE_TEST1 + UI_TEST4

| plik | do czego |
|---|---|
| `pakiet_EN_2026-10-15_v6.zip` | **jedyny aktualny pakiet tłumaczenia** (rozpakować do `srw-oe-translation\pakiet_EN\`); = v5 (działał w grze w buildzie #19) + `09_executable.jsonl` (napisy programu gry, 408 wierszy / 397 EN) + 31 całych napisów menu + „Coord. Attack”; opis w `CO_NOWEGO_v6.txt` |
| `EXE_TEST1.zip` | **napisy programu gry bez budowania**: gotowy `PBOOT.PBP` (twój 1.08 z 397 angielskimi napisami; program poza napisami bajt w bajt ten sam) + `cheats\NPJH50521.ini` (te same zmiany jako kody CWCheat — droga zapasowa) + `lista_napisow_exe.txt` + `CZYTAJ_EXE_TEST1.txt` (część 5) |
| `UI_TEST4.zip` | **grafiki interfejsu, komplet 26 tekstur z poprawionymi komórkami** po zrzutach z #19 (zastępuje `UI_TEST3`, który działał w grze): `system.cpk`, `tacsys.cpk`, `IM1000.cpk`, `IM3000.cpk`, `IM9000.cpk`, `navisys.cpk` + `CZYTAJ_UI_TEST4.txt`; `HOKUS_POKUS.bat` z aktualnym ZIP-em gałęzi buduje dokładnie to samo |
| `RUNDA8_build14.zip` | `config00.cpk` + `configst.cpk` z budowy #14 — para sprawdzona w grze z oryginalnym DLC (odniesienie) |
| `INSTRUKCJA_PL.md` | ten tekst |
| `_STARE_NIE_UZYWAC\…` | pakiet v5, `KIT_build18` i `UI_TEST3` (wszystkie **działały w grze** w buildzie #19 — odniesienie, zastąpione przez v6 / UI_TEST4), pakiet v4 i `KIT_build17` (działały, dwa błędy tekstu), `UI_TEST1` (wariant A działał) i `UI_TEST2`, pakiety v3 i starsze (padają na Loading) |

Jak odróżnić pliki: `config00.cpk` z budowy #18 (pakiet v5) ma **936 064 B, md5
`5c43cf343b9fafde62c3c53c3a6c1e78`**; z budowy #17 (pakiet v4, sprawdzony w grze) ten sam rozmiar, md5
`80b8fae61b858fb91db35532c4680c6f`; z budowy #14 / pakietu v3 md5 `71d9fcafa37c21513b97c14d1dff8f33`.
`configst.cpk` **372 864 B, md5 `6cfe245d5f6ec6dfffd2a829b778a4d7`** (bez zmian od #14). `config01.EDAT`
z v5 ma **247 936 B (rozmiar oryginału), md5 `8db9f78108b829526ef5a7176847c5fd`** (z v4:
`7c6459fa7377b585a5176b5859361da2`; z v3 miał 249 984 B). Z pakietu v6 `config00.cpk`, `configst.cpk`
i `config01–08.EDAT` budują się na nowo (`configst.cpk` dostaje 31 nowych napisów, więc md5 się zmieni —
`DIAGNOZA.bat` opisze je jako nowe). `PBOOT.PBP`: **oryginał 1.08 = 6 194 059 B, md5
`22daece3b6fccc4363dd76ed6a7ec2fb`; z napisami EN (EXE_TEST1 = budowa #20) = 6 191 659 B, md5
`26689964d2ce4e6cddadb67c8188e923`** — `DIAGNOZA.bat` rozpoznaje oba i mówi, czy `DATA.PSP` w środku jest
„szyfrowany ~PSP” (oryginał) czy „jawny ELF” (nasz). Każdy inny md5 = stare narzędzia albo stary pakiet
(`DIAGNOZA.bat` sprawdza to za ciebie i rozpoznaje buildy #15/#17/#18/pulaJP po md5).

---

## Część 1 — budowa (jeden `.bat`, 10–15 minut)

Potrzebne raz: **Python 3.9 lub nowszy** — <https://www.python.org/downloads/>, przy instalacji
zaznacz **„Add python.exe to PATH”**. Do napisów w grafikach interfejsu (część 4) potrzebna jest
jeszcze biblioteka **Pillow** — `HOKUS_POKUS.bat` sam ją doinstalowuje (`pip install pillow`, raz,
potrzebny internet); gdyby się nie udało, buduje **sam tekst** i wyraźnie o tym pisze (wtedy ręcznie:
`python -m pip install pillow` i jeszcze raz `HOKUS_POKUS.bat`).

1. **Świeże narzędzia.** Ściągnij repozytorium jako ZIP: strona repozytorium → gałąź
   `arena/c0e5c9d1-mtgcrawler` → zielony przycisk **Code** → **Download ZIP** (bezpośredni link:
   `https://github.com/szybkoiwyraznie-rgb/mtgcrawler/archive/refs/heads/arena/c0e5c9d1-mtgcrawler.zip`).
   Rozpakuj do **nowego, pustego** folderu — nie nadpisuj starego rozpakowania (stary folder może
   mieć stare `tools\*.py` i stary `pakiet_EN\`). Interesuje cię podfolder `srw-oe-translation\`.
   Świeży zestaw poznasz po tym, że obok `HOKUS_POKUS.bat` leży **`DIAGNOZA.bat`**.
2. **Pakiet v6.** Ściągnij z Dysku `pakiet_EN_2026-10-15_v6.zip` i rozpakuj tak, żeby plik
   `00_dialogue.jsonl` leżał **bezpośrednio** w `srw-oe-translation\pakiet_EN\` (w zipie jest
   folder `pakiet_EN_2026-10-15_v6\` — jego zawartość, nie on sam). Żadnych innych `*.jsonl` obok
   (stary v5/v4 usuń w całości). W v6 jest nowy, dziesiąty plik `09_executable.jsonl` — bez niego
   napisy programu gry zostaną japońskie (`DIAGNOZA.bat` to wypisze).
3. **`HOKUS_POKUS.bat`** (dwuklik). Dwa okna wyboru: (1) plik `SRW OE 1.08.iso`;
   (2) **folder z odszyfrowanymi plikami DLC** (zestaw FULL_DLC). **Ten folder musi zawierać też
   `PBOOT.PBP`** (aktualizacja 1.08 — leży w folderze DLC emulatora obok `*.EDAT`; jeśli twój zestaw
   FULL_DLC go nie ma, skopiuj go tam z folderu emulatora). Bez niego budowa przejdzie, ale bez napisów
   programu (w raporcie `executable.container = null`). Czekaj na „Gotowe” (~4 min budowy +
   przepisanie ISO 680 MB).
4. **Wynik** w `srw-oe-translation\srw-oe-patch\`: `patched.iso` (tekst rozdziału 1 **i** napisy
   w grafikach — 6 kontenerów UI, w `build_report.json` klucz `ui_textures`), `DLC\…` (91 plików
   `*.EDAT` + `config00.cpk`, `configst.cpk` **+ `PBOOT.PBP`** z angielskimi napisami programu),
   `cheats\NPJH50521.ini` (droga zapasowa, część 5), `build_report.json` (klucz `executable`:
   `applied` 397, `verified: true`).
5. **Zanim cokolwiek skopiujesz — `DIAGNOZA.bat`** (część 2). Dopiero gdy raport mówi
   „pakiet v6 — AKTUALNY”, „`+52` TAK”, „budżet pul DLC TAK”, a przy `PBOOT.PBP` „DATA.PSP: jawny ELF”,
   kopiuj. W `build_report.json` jest też pole `skill_total` (Skill00 + 8 pul; ma być ≤ 342 194 B,
   z v5/v6 wychodzi 340 074 B).
6. **Wgranie:** kopia zapasowa folderu DLC emulatora (cały folder obok, z dopiskiem `_ORYGINAL` —
   **w tym oryginalny `PBOOT.PBP`**), potem wszystkie pliki z `srw-oe-patch\DLC\` do folderu DLC
   emulatora (nadpisać, razem z `PBOOT.PBP`). W PPSSPP uruchom `srw-oe-patch\patched.iso`. Gdyby gra
   z nowym `PBOOT.PBP` nie wystartowała (hipoteza do sprawdzenia, część 5): przywróć oryginalny
   `PBOOT.PBP` z kopii i użyj `cheats\NPJH50521.ini`.

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

## Część 4 — grafiki interfejsu: `UI_TEST4.zip` (szybki test) albo `HOKUS_POKUS.bat` (sam)

Napisy systemowe na ekranach statusu / broni / umiejętności, zakładki intermisji, napisy w walce (okno
reakcji, bannery, nagłówki tur), ikony i przyciski scen nawigacji są obrazkami w sześciu plikach ISO:
`system.cpk`, `tacsys.cpk`, `IM1000.cpk`, `IM3000.cpk`, `IM9000.cpk`, `navisys.cpk`. Pierwszy zestaw
(`UI_TEST1`, wariant A = dane bez kompresji) **działa w grze** (zrzuty z 15.10), a komplet 26 tekstur
(`UI_TEST3`) **działał w buildzie #19** („wszystko śmiga”). `UI_TEST4.zip` = ten sam komplet z poprawionymi
komórkami po twoich zrzutach: nagłówek „WPN” bez 名, „RNG” nieobcięte, „EN Cost” w swojej komórce bez
osieroconej litery, ramki nad ikonami części (nie są już ścięte w połowie), ikony zdolności nie podcięte,
„!” i „M” w wyniku misji całe. Ikony z pojedynczym kanji mają **2-literowe kody**
(w środku ikony jest ~10×10 px — 3 litery się nie mieszczą, a 1 litera myliłaby się z rangami S/A/B/C/D
obok): teren **GR** Ground / **AI** Air / **SP** Space; cechy broni **BR** Break, **AR** Arc Shot, **PU** Push,
**TH** Throw (z „karbem” = Pull Throw), **CO** Combination (M i B zostają); badge **SR** Surround, **DH** Direct
Hit; kule ducha **VA** Valor, **BU** Bullseye, **AC** Accel, **FL** Flash, **FO** Focus, **PE** Persist, **WA** Wall,
**GA** Gain, **FR** Fortune, **DI** Disrupt. Nawigacja: Battle / Evade / Musai / Confirm / Cancel / Enemy Sighted.

Droga A — szybki test na gotowym `patched.iso` (nic nie buduje):

1. Rozpakuj `UI_TEST4.zip` (folder `UI_TEST4\` z sześcioma `.cpk` na wierzchu). Pobierz też aktualny ZIP
   gałęzi z GitHub — starszy `WGRAJ_DO_ISO.bat` nie zna `navisys.cpk` i odmówi.
2. `WGRAJ_DO_ISO.bat` → okno ISO: **`patched.iso` zbudowane BEZ tekstur (`--no-ui-textures`) albo stare
   `patched.iso` z pakietu v4/v5 sprzed UI_TEST1** (narzędzie zna md5 oryginalnych plików i odmówi:
   „system.cpk w tym ISO nie jest oryginalny” — `patched.iso` z buildu #19 ma już w sobie UI_TEST3, więc
   tam nie wgrasz; prościej: Droga B) → okno folderu: **`UI_TEST4`**. Wynik: `srw-oe-wgrane\UI_TEST4\patched.iso`.
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
`DIAGNOZA.bat` z ISO pokazuje blok „tekstury UI” — oryginał / UI_TEST1 / UI_TEST2 / UI_TEST3 / UI_TEST4 / nieznany.

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

## Część 5 — napisy programu gry: `PBOOT.PBP` (EXE_TEST1 albo wynik `HOKUS_POKUS`) i droga zapasowa CWCheat

Część napisów nie leży w żadnym pliku danych, tylko w **programie gry** — a dokładnie w aktualizacji 1.08
(`PBOOT.PBP` w folderze DLC emulatora; PPSSPP uruchamia go zamiast programu z płyty, bo pasuje `DISC_ID`).
Są to: na panelu broni w walce `移動後` (→ Post-Mv) i `TGT 敵/味方/全て` (→ Foe/Ally/All); komunikaty w walce
(`回避` Evade, `援護防御` Sup. Def, `援護攻撃` Sup. Atk, `ＥＮ不足` Low EN, `射程外` OutRng, `合体攻撃` Comb.Atk,
`クリティカル` Critical, `突破攻撃` Break, `全包囲！` Surround!); linie zdolności broni dodane w 1.08
(`<貫通 Lv2> 敵の防御-35%` → `<Pierce Lv2>Foe Def-35%`, `<ビーム兵器 Lv2>…` → `<Beam Wpn Lv2>CT Dmg+6% Foe Eva-6%`,
`<連携攻撃 Lv2>…` → `<Coord. Atk Lv2>Surround+35% Whole group attacks …`, Slow, Keron, Huge…); efekt Guard
(`ダメージ-16% 発動率12%` → `Dmg-16% Trigger 12%`); komendy jednostki (Move Attack Spirit Parts Ability Wait),
menu taktyczne (Find Status Options Retire Quick Save), `【End Phase】`, komunikaty o sejwie / autozapisie /
sieci / DLC i nazwa gry w danych sejwu. Razem 408 napisów, 397 po angielsku (11 to symbole i teksty debugowe).
Angielski jest wpisany **w miejsce** japońskiego (nigdy dłuższy niż miejsce + zera wyrównania — dlatego skróty
jak „OutRng”, „Comb.Atk”, „Sng”); program poza napisami jest bajt w bajt ten sam. Jedna zmiana techniczna:
`DATA.PSP` w środku nie jest już zaszyfrowany (zaszyfrować z powrotem nie da się bez kluczy Sony) — **PPSSPP
według swojego kodu źródłowego ładuje taki nieszyfrowany moduł wprost; w grze tego jeszcze nie sprawdziliśmy
(to jest główna hipoteza tego zestawu).** Prawdziwe PSP z CFW — nie sprawdzane, poza celem.

Droga A — `EXE_TEST1.zip` (nic nie buduje, 2 minuty):

1. Kopia oryginału: `memstick\PSP\GAME\NPJH50521\PBOOT.PBP` → np. `PBOOT_ORYGINAL.PBP` **w innym folderze**
   (nie obok pod inną nazwą — PPSSPP czyta tylko `PBOOT.PBP`, ale porządek się przyda).
2. Skopiuj `PBOOT.PBP` z `EXE_TEST1\` do `memstick\PSP\GAME\NPJH50521\` (nadpisz).
3. Uruchom grę z dotychczasowego `patched.iso`. Tytuł ma nadal pokazywać wersję 1.08. Sprawdź: walka →
   panel broni (Post-Mv / TGT Foe), Guard L1 (`Dmg-16% Trigger 12%`), zdolności broni VF-25F (`<Pierce Lv2>`,
   `<Beam Wpn Lv2>`, `<Coord. Atk Lv2>`), komunikat autozapisu po starcie.
4. **Gra nie startuje / wisi na logo** → przywróć oryginalny `PBOOT.PBP` i napisz (zrzut + co było na ekranie);
   wtedy Droga C.

Droga B — przy budowie `HOKUS_POKUS.bat` (część 1): jeśli wskazany folder DLC zawiera `PBOOT.PBP`, builder
sam robi to samo i kładzie wynik w `srw-oe-patch\DLC\PBOOT.PBP` (plus `srw-oe-patch\cheats\NPJH50521.ini`).
Wyłączenie: `python tools\build_translation_patch.py … --no-exe`.

Droga C — zapasowa, bez podmiany `PBOOT.PBP` (kody CWCheat): skopiuj `cheats\NPJH50521.ini` do
`memstick\PSP\Cheats\` (jeśli plik już tam jest, dopisz zawartość na końcu). W PPSSPP: Ustawienia → System →
**Włącz cheaty**; w menu pauzy → Cheaty → zaznacz `EXE strings EN`. Te same bajty są wtedy wpisywane w pamięć
po starcie gry; oryginalny `PBOOT.PBP` zostaje.

Co z tego zestawu NIE pochodzi: „Main Pilot / Sub Pilot / Switch Pilot” i inne napisy menu (to `configst.cpk`
z pakietu v6 — potrzebna budowa) oraz poprawki grafik (część 4).

## Gdy okno `.bat` miga i znika

Każdy `.bat` otwiera się ponownie w trybie, w którym okno **nie zamyka się** po błędzie. Jeśli
mimo to znika: otwórz folder `srw-oe-translation` w Eksploratorze, kliknij w pasek adresu, wpisz
`cmd`, Enter; w czarnym oknie wpisz nazwę pliku (np. `DIAGNOZA`) i Enter. Niebieskie „System
Windows ochronił ten komputer” → „Więcej informacji” → „Uruchom mimo to” (plik z pobranego zipa).

## Powrót do oryginału

W PPSSPP wskaż z powrotem swoje ISO, przywróć folder DLC z kopii `_ORYGINAL` (razem z oryginalnym
`PBOOT.PBP`), wyłącz cheaty (jeśli włączałeś), usuń `srw-oe-patch\`. Żaden oryginalny plik nie był
modyfikowany.

## Co dokładnie jest w pakiecie v6 (2026-10-15 późnym wieczorem; = v5 + trzy rzeczy)

- 108 574 wierszy, 81 220 z angielskim; kontrola pakietu `translation_check`: 0 błędów. Nowe względem v5:
  `09_executable.jsonl` (408 napisów programu gry, 397 EN — część 5), 31 całych napisów menu w
  `04_config_text.jsonl` (`Main Pilot`, `Sub Pilot`, `Switch Pilot`, `Pilot Parts`, `System Setup 1/2`,
  `Sound Setup`, `Sort`, `Page`, `Missions Cleared:`, `[GR Mission]`, `Simulator Mission`, ` Saving...`,
  `%s is now available!` …), „Link Attack” → „Coord. Attack” w 3 opisach. Opis: `CO_NOWEGO_v6.txt`.
- Budowa z v6 w piaskownicy (#20, bez ISO): `config00.cpk` 936 064 B (Skill00 215 450 B jak v5),
  `configst.cpk` 372 864 B z 31 nowymi napisami, `PBOOT.PBP` 6 191 659 B md5 `26689964d2ce4e6cddadb67c8188e923`.

## Co było w pakiecie v5 (liczby z budowy #18, 2026-10-15 w nocy; v5 działał w grze w buildzie #19)

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
  (`UI_TEST4.zip` albo aktualny `HOKUS_POKUS.bat`, część 4); komplet `UI_TEST3` działał w grze (#19),
  poprawki `UI_TEST4` — jeszcze nie. Po japońsku zostają tylko ikony `mensys_12` (czekam na zrzut).
- Napisy programu gry (komunikat autozapisu, panel broni, komendy) są od v6 w zakresie — ale tylko przez
  podmianę `PBOOT.PBP` (nieszyfrowany `DATA.PSP`, hipoteza) albo kody CWCheat (część 5); działa to tylko
  z aktualizacją 1.08 w folderze DLC, nie z samym programem z płyty.
- Nie zawiera żadnych plików gry: wszystko powstaje z twojego ISO i twoich DLC.
- Nie działa na zaszyfrowanych plikach DLC ani na ISO innej wersji niż 1.08.
