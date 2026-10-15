# Jak nałożyć angielskie tłumaczenie SRW OE — instrukcja (stan 2026-10-15, pakiet v4)

To jest instrukcja dla osoby, która ma **własne** japońskie pliki gry (ISO rozdziału 1 w wersji
1.08, 679 243 152 bajty, i odszyfrowane pliki DLC rozdziałów 2–8) i chce zobaczyć na nich angielski
tekst. Nic z oryginałów nie jest ruszane: ISO i DLC są tylko czytane, wynik ląduje w osobnym folderze.

Uczciwie o stanie: **to nie jest skończone tłumaczenie i pełny zestaw nie był jeszcze ani razu
uruchomiony bez crasha.** W grze sprawdzone są: `config00.cpk` + `configst.cpk` z budowy #14
(Loading, nowa gra, sejw z 2. rozdziału) oraz — testem X z 2026-10-15 — całe zmienione ISO
(`patched.iso` z `eventP00`, `mesbtl00`, `imenu00`) z **oryginalnym** folderem DLC: działa, da się
grać do ekranu słownika. Test Y (oryginalne ISO + 91 zbudowanych plików DLC) **padł na „Loading”**
z tym samym śladem co dawny crash „Skill00 za duży”. Jedyna różnica rozmiarowa między X a Y, która
pasuje do tego śladu, to pule fragmentów umiejętności w `config01–08.EDAT` (każda urosła
15 638 → 17 396 B). **Pakiet v4** trzyma te pule poniżej oryginału (15 578 B) — to jest kandydat
do sprawdzenia w tej rundzie (część 3). Pozostałe 83 pliki EDAT po poprawkach pisarzy nadal
**nigdy nie przeszły przez grę osobno**.

Zasada stała: żaden plik `.bat` nie każe wpisywać ścieżek — zawsze otwiera okno wyboru pliku/folderu.

---

## Co jest na Dysku (folder DELIVERY) — stan 2026-10-15, pakiet v4

| plik | do czego |
|---|---|
| `pakiet_EN_2026-10-15_v4.zip` | **jedyny aktualny pakiet tłumaczenia** (rozpakować do `srw-oe-translation\pakiet_EN\`); w środku `CO_NOWEGO_v4.txt` |
| `KIT_build17_2026-10-15.zip` | pliki z budowy #17 (pakiet v4) do testów bez budowania: `USRDIR_build17\` (5 plików do ISO dla `WGRAJ_DO_ISO.bat`), `DLC_build17_config\` (10 plików do folderu DLC: `config00.cpk`, `configst.cpk`, `config01–08.EDAT`), `DLC_pulaJP_config01-08\` (wariant awaryjny), `CZYTAJ.txt` z planem testów |
| `RUNDA8_build14.zip` | `config00.cpk` + `configst.cpk` z budowy #14 — para sprawdzona w grze z oryginalnym DLC (odniesienie) |
| `INSTRUKCJA_PL.md` | ten tekst |
| `_STARE_NIE_UZYWAC\…` | pakiet v3 i `KIT_build15` (ich `config01–08.EDAT` padają na Loading — test Y), oraz wszystko z 14–15.10 sprzed poprawki `+52`. **Nie kopiować.** |

Jak odróżnić pliki: `config00.cpk` z budowy #17 (pakiet v4) ma **936 064 B, md5
`80b8fae61b858fb91db35532c4680c6f`** (z budowy #14 / pakietu v3: ten sam rozmiar, md5
`71d9fcafa37c21513b97c14d1dff8f33`); `configst.cpk` **372 864 B, md5 `6cfe245d5f6ec6dfffd2a829b778a4d7`**
(bez zmian od #14). `config01.EDAT` z v4 ma **247 936 B (rozmiar oryginału), md5
`7c6459fa7377b585a5176b5859361da2`**; z v3 miał 249 984 B. Każdy inny md5 = stare narzędzia albo
stary pakiet (`DIAGNOZA.bat` sprawdza to za ciebie i rozpoznaje buildy #15/#17/pulaJP po md5).

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
2. **Pakiet v4.** Ściągnij z Dysku `pakiet_EN_2026-10-15_v4.zip` i rozpakuj tak, żeby plik
   `00_dialogue.jsonl` leżał **bezpośrednio** w `srw-oe-translation\pakiet_EN\` (w zipie jest
   folder `pakiet_EN_2026-10-15_v4\` — jego zawartość, nie on sam). Żadnych innych `*.jsonl` obok
   (stary v3 usuń w całości).
3. **`HOKUS_POKUS.bat`** (dwuklik). Dwa okna wyboru: (1) plik `SRW OE 1.08.iso`;
   (2) **folder z odszyfrowanymi plikami DLC** (zestaw FULL_DLC). Czekaj na „Gotowe”
   (~4 min budowy + przepisanie ISO 680 MB).
4. **Wynik** w `srw-oe-translation\srw-oe-patch\`: `patched.iso`, `DLC\…` (91 plików `*.EDAT` +
   `config00.cpk`, `configst.cpk`), `build_report.json`.
5. **Zanim cokolwiek skopiujesz — `DIAGNOZA.bat`** (część 2). Dopiero gdy raport mówi
   „pakiet v4 — AKTUALNY”, „`+52` TAK”, „budżet pul DLC TAK” i „config00 = BUILD17”, kopiuj.
   W `build_report.json` jest teraz też pole `skill_total` (Skill00 + 8 pul; ma być ≤ 342 194 B,
   z v4 wychodzi 340 086 B).
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
2. który pakiet leży w `pakiet_EN\` (v1 z 14.10 / v2 / v3 / v4 — po md5 plików `03`/`04`) i czy nie
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

## Część 3 — runda testów pakietu v4 (po 2–5 minut każdy, bez budowania poza Y4)

Wyniki X/Y z 2026-10-15 (X działa, Y pada) są podstawą tej rundy. Za każdym razem **zacznij od
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

---

## Gdy okno `.bat` miga i znika

Każdy `.bat` otwiera się ponownie w trybie, w którym okno **nie zamyka się** po błędzie. Jeśli
mimo to znika: otwórz folder `srw-oe-translation` w Eksploratorze, kliknij w pasek adresu, wpisz
`cmd`, Enter; w czarnym oknie wpisz nazwę pliku (np. `DIAGNOZA`) i Enter. Niebieskie „System
Windows ochronił ten komputer” → „Więcej informacji” → „Uruchom mimo to” (plik z pobranego zipa).

## Powrót do oryginału

W PPSSPP wskaż z powrotem swoje ISO, przywróć folder DLC z kopii `_ORYGINAL`, usuń
`srw-oe-patch\`. Żaden oryginalny plik nie był modyfikowany.

## Co dokładnie jest w pakiecie v4 (liczby z budowy #17, 2026-10-15)

- Pakiet: 108 135 wierszy, 77 106 z angielskim + 3 686 identycznych (znaki, liczby); kontrola
  pakietu `translation_check`: 0 błędów. Dialogi fabularne: rozdziały 1–3 w całości, rozdział 4
  ~59 %, rozdziały 5–8 jeszcze po japońsku. Względem v3: 231 tekstów umiejętności skróconych
  (lista w `SKROCENIA_Skill00_v4_tier4_i_pule.tsv`), pule rozdziałów 2–8 = teksty Skill00.
- Budżety rozmiaru pilnowane przez narzędzia: `srwDL_Skill00.bin` ≤ 216 768 B (zmierzone w grze),
  każda pula `srwDL_Skill01–08.bin` ≤ 15 638 B (= oryginał; przyjęte po teście Y), suma ≤ 342 194 B.
- Zmienione człony kontenerów są zapisywane **bez kompresji** (oryginał używa CRILAYLA), stąd
  pliki rosną: `mesbtl00.cpk` 348 888 → 994 008 B, `eventP00.cpk` 162 264 → 260 568 B,
  `imenu00.cpk` 34 984 → 57 512 B; rozpakowana zawartość rośnie najwyżej o ~6 %. Test X
  (2026-10-15) pokazał, że gra startuje z tymi trzema plikami i oryginalnym DLC.

## Czego ten pakiet NIE robi

- Nie dotyka grafik (logo, przyciski w teksturach) — tylko tekst w plikach danych.
- Nie tłumaczy komunikatu o autozapisie po starcie — siedzi w programie gry (`EBOOT.BIN`).
- Nie zawiera żadnych plików gry: wszystko powstaje z twojego ISO i twoich DLC.
- Nie działa na zaszyfrowanych plikach DLC ani na ISO innej wersji niż 1.08.
