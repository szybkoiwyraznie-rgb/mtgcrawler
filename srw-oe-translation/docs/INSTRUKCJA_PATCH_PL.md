# Jak nałożyć angielskie tłumaczenie SRW OE — instrukcja (stan 2026-10-15 wieczór)

To jest instrukcja dla osoby, która ma **własne** japońskie pliki gry (ISO rozdziału 1 w wersji
1.08, 679 243 152 bajty, i odszyfrowane pliki DLC rozdziałów 2–8) i chce zobaczyć na nich angielski
tekst. Nic z oryginałów nie jest ruszane: ISO i DLC są tylko czytane, wynik ląduje w osobnym folderze.

Uczciwie o stanie: **to nie jest skończone tłumaczenie i pełny zestaw nie był jeszcze ani razu
uruchomiony bez crasha.** W grze sprawdzone są tylko dwa pliki (`config00.cpk` + `configst.cpk`
z budowy #14: Loading, nowa gra, sejw z 2. rozdziału — działają). Pozostałe 94 pliki (trzy z ISO:
`eventP00`, `mesbtl00`, `imenu00`, oraz 91 DLC) po poprawkach pisarzy jeszcze **nigdy nie
przeszły przez grę** — ostatnia próba pełnego zestawu (2026-10-15) padła na ekranie „Loading”.
Dlatego ta instrukcja ma trzy części: zbudować, **sprawdzić co się zbudowało i co jest wgrane**
(`DIAGNOZA.bat`), i gdy pada — **podzielić problem na pół** dwoma testami bez budowania.

Zasada stała: żaden plik `.bat` nie każe wpisywać ścieżek — zawsze otwiera okno wyboru pliku/folderu.

---

## Co jest na Dysku (folder DELIVERY) — stan 2026-10-15 wieczór

| plik | do czego |
|---|---|
| `pakiet_EN_2026-10-15_v3.zip` | **jedyny aktualny pakiet tłumaczenia** (rozpakować do `srw-oe-translation\pakiet_EN\`) |
| `RUNDA8_build14.zip` | `config00.cpk` + `configst.cpk` z budowy #14 — jedyne pliki sprawdzone w grze (do folderu DLC emulatora) |
| `KIT_build15_2026-10-15.zip` | pliki z budowy #15 (= #14 + reszta ISO + `config01–08.EDAT`) do testów bez budowania: `USRDIR_build15\` (5 plików do ISO), `ISO_B_imenu00\`, `ISO_C_mesbtl00\`, `ISO_D_eventP00\` (pojedyncze pliki do bisekcji przez `WGRAJ_DO_ISO.bat`), `DLC_config01-08\` |
| `INSTRUKCJA_PL.md` | ten tekst |
| `_STARE_NIE_UZYWAC\…` | wszystko z 14–15.10 sprzed poprawki `+52` (pakiet v1, `DLC_EN_2026-10-14`, `USRDIR_EN_2026-10-14b`, `WGRAJ_build10–13`, rundy 2–7, stara instrukcja). **Te pliki padają — nie kopiować.** |

Jak odróżnić pliki: `config00.cpk` z poprawnej budowy ma **936 064 B, md5 `71d9fcafa37c21513b97c14d1dff8f33`**,
`configst.cpk` **372 864 B, md5 `6cfe245d5f6ec6dfffd2a829b778a4d7`**. Każdy inny md5 = stare
narzędzia albo stary pakiet (`DIAGNOZA.bat` sprawdza to za ciebie i rozpoznaje stare buildy po md5).

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
2. **Pakiet v3.** Ściągnij z Dysku `pakiet_EN_2026-10-15_v3.zip` i rozpakuj tak, żeby plik
   `00_dialogue.jsonl` leżał **bezpośrednio** w `srw-oe-translation\pakiet_EN\` (w zipie jest
   folder `pakiet_EN_2026-10-15_v3\` — jego zawartość, nie on sam). Żadnych innych `*.jsonl` obok.
3. **`HOKUS_POKUS.bat`** (dwuklik). Dwa okna wyboru: (1) plik `SRW OE 1.08.iso`;
   (2) **folder z odszyfrowanymi plikami DLC** (zestaw FULL_DLC). Czekaj na „Gotowe”
   (~4 min budowy + przepisanie ISO 680 MB).
4. **Wynik** w `srw-oe-translation\srw-oe-patch\`: `patched.iso`, `DLC\…` (91 plików `*.EDAT` +
   `config00.cpk`, `configst.cpk`), `build_report.json`.
5. **Zanim cokolwiek skopiujesz — `DIAGNOZA.bat`** (część 2). Dopiero gdy raport mówi
   „pakiet v3 — AKTUALNY”, „`+52` TAK” i „config00 = BUILD14”, kopiuj.
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
2. który pakiet leży w `pakiet_EN\` (v1 z 14.10 / v2 / v3 — po md5 plików `03`/`04`) i czy nie
   jest rozpakowany o jeden folder za głęboko;
3. co zbudował HOKUS_POKUS (`build_report.json`: odmowy zapisu, brakujące kontenery; md5 plików w
   `patched.iso` i w `DLC\`, rozpoznane po tabeli znanych buildów);
4. co **naprawdę** leży w folderze DLC emulatora: identyczne z budową / inne niż budowa /
   oryginał / stary build (#6–#13 rozpoznawane po md5);
5. co jest w ISO uruchamianym w PPSSPP (5 plików USRDIR: oryginał / build #14 / inny).

Na końcu sekcja **WNIOSKI** — automatyczne zdania typu „config00.cpk w folderze DLC to build #12
(stary)”. Jeżeli WNIOSKI są puste, instalacja jest taka, jak ma być, i crash to sprawa plików
samych w sobie — wtedy część 3.

---

## Część 3 — gdy pełny zestaw pada: dwa testy bez budowania (po 2 minuty)

Oba testy wymagają tylko kopiowania plików. Zanotuj dla każdego: **działa** (ekran tytułowy po
„Loading”) / **crash** (jaki ekran, zrzut PPSSPP z adresem). Pliki do testów masz po budowie
w `srw-oe-patch\` albo w `KIT_build15_2026-10-15.zip` z Dysku (te same bajty).

**Test X — tylko ISO zmienione.** Folder DLC emulatora = **w całości oryginalny** (przywróć
z `_ORYGINAL`, łącznie z oryginalnymi `config00.cpk`/`configst.cpk`). W PPSSPP uruchom
`patched.iso`. Gra bierze `config00`/`configst` z folderu DLC, więc X sprawdza wyłącznie trzy
pliki z ISO: `eventP00`, `mesbtl00`, `imenu00`.

**Test Y — tylko DLC zmienione.** W PPSSPP uruchom **oryginalne** `SRW OE 1.08.iso`. Folder DLC
emulatora = oryginał + **wszystkie** pliki z `srw-oe-patch\DLC\` (91 `*.EDAT` + `config00.cpk`
+ `configst.cpk` z budowy #14). Y sprawdza 91 plików EDAT (config #14 w tej konfiguracji już
przechodziło).

| X | Y | wniosek | następny krok |
|---|---|---|---|
| crash | działa | winny jeden z trzech plików ISO | `WGRAJ_DO_ISO.bat` ×3 z folderami `ISO_B_imenu00`, `ISO_C_mesbtl00`, `ISO_D_eventP00` z KIT-u (okno 1: oryginalne ISO, okno 2: folder); każde `srw-oe-wgrane\<folder>\patched.iso` uruchom z **oryginalnym DLC + config #14** w folderze DLC |
| działa | crash | winny któryś EDAT | `BISEKCJA.bat` literą `H` (tylko EDAT z dialogami) i `I` (EDAT bez dialogów): oryginalne ISO + `srw-oe-bisekcja\<litera>\DLC\` |
| crash | crash | dwa różne problemy albo wspólny (np. budżet pamięci przy starcie) | prześlij oba zrzuty + `DIAGNOZA.txt` |
| działa | działa | pełny zestaw padał przez stare/pomieszane pliki | `DIAGNOZA.bat` na pełnym zestawie pokaże, co było nie tak |

---

## Gdy okno `.bat` miga i znika

Każdy `.bat` otwiera się ponownie w trybie, w którym okno **nie zamyka się** po błędzie. Jeśli
mimo to znika: otwórz folder `srw-oe-translation` w Eksploratorze, kliknij w pasek adresu, wpisz
`cmd`, Enter; w czarnym oknie wpisz nazwę pliku (np. `DIAGNOZA`) i Enter. Niebieskie „System
Windows ochronił ten komputer” → „Więcej informacji” → „Uruchom mimo to” (plik z pobranego zipa).

## Powrót do oryginału

W PPSSPP wskaż z powrotem swoje ISO, przywróć folder DLC z kopii `_ORYGINAL`, usuń
`srw-oe-patch\`. Żaden oryginalny plik nie był modyfikowany.

## Co dokładnie jest w pakiecie v3 (liczby z budowy #15, 2026-10-15)

- Pakiet: 108 135 wierszy, 77 106 z angielskim + 3 686 identycznych (znaki, liczby); kontrola
  pakietu `translation_check`: 0 błędów. Dialogi fabularne: rozdziały 1–3 w całości, rozdział 4
  ~59 %, rozdziały 5–8 jeszcze po japońsku.
- Zmienione człony kontenerów są zapisywane **bez kompresji** (oryginał używa CRILAYLA), stąd
  pliki rosną: `mesbtl00.cpk` 348 888 → 994 008 B, `eventP00.cpk` 162 264 → 260 568 B,
  `imenu00.cpk` 34 984 → 57 512 B; rozpakowana zawartość rośnie najwyżej o ~6 %. Czy gra to
  udźwignie przy starcie — **nie wiadomo** (test X to sprawdza).

## Czego ten pakiet NIE robi

- Nie dotyka grafik (logo, przyciski w teksturach) — tylko tekst w plikach danych.
- Nie tłumaczy komunikatu o autozapisie po starcie — siedzi w programie gry (`EBOOT.BIN`).
- Nie zawiera żadnych plików gry: wszystko powstaje z twojego ISO i twoich DLC.
- Nie działa na zaszyfrowanych plikach DLC ani na ISO innej wersji niż 1.08.
