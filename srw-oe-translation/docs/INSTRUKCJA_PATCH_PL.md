# Jak nałożyć angielskie tłumaczenie SRW OE — instrukcja krok po kroku (stan 2026-10-14)

To jest instrukcja dla osoby, która ma **własne** japońskie pliki gry (ISO rozdziału 1 w wersji
1.08 i odszyfrowane pliki DLC rozdziałów 2–8) i chce zobaczyć na nich angielski tekst.
Nic z oryginałów nie jest ruszane: ISO i DLC są tylko czytane, wynik ląduje w osobnym folderze.

Uczciwie o stanie: **to nie jest skończone tłumaczenie.** Menu, przedmioty, umiejętności,
nazwy, teksty bitewne i opisy misji są wpisane w całości; fabuła (dialogi scen) jest wpisana
tam, gdzie tłumacz już ją oddał — rozdziały 1–3 w całości, rozdział 4 w ~59 %, rozdziały 5–8
jeszcze po japońsku (szczegóły niżej). Wygląd w grze (szerokość linii 47–52 jednostek, 1 MB
`mesbtl00` zapisany bez kompresji) nie był jeszcze sprawdzony na całości — to jest właśnie
to, co ten pakiet ma umożliwić.

---

## Co dostajesz (folder na Dysku „SRW OE - PATCH 2026-10-14 (EN2)”)

| plik | do czego |
|---|---|
| `DLC_EN_2026-10-14.zip` | **gotowe pliki DLC** (91 plików `*.EDAT`) — rozdziały 2–8, menu i teksty, które gra czyta z DLC; do skopiowania do folderu DLC emulatora |
| `pakiet_EN_2026-10-14.zip` | pakiet tłumaczenia z wpisanym angielskim (pliki `00_dialogue.jsonl` … `08_…`, `tokeny.tsv`) — **potrzebny do zbudowania ISO** rozdziału 1 |
| `USRDIR_EN_2026-10-14.zip` | 5 plików z wnętrza ISO (`config00.cpk`, `configst.cpk`, `eventP00.cpk`, `imenu00.cpk`, `mesbtl00.cpk`) już po podmianie tekstu — do włożenia do KOPII ISO przez `WGRAJ_DO_ISO.bat` (okno 1: oryginalne ISO, okno 2: folder z tymi plikami; wynik `srw-oe-wgrane\<folder>\patched.iso`); **HOKUS_POKUS robi to samo automatycznie z pakietu** |
| `md5sums.txt` | sumy kontrolne wszystkich plików wynikowych |
| `build_report.json`, `spot_check.json`, `missing.txt` | raport z budowy: co wpisane, co odmówione i dlaczego |
| `DO_ZROBIENIA_2.md` | lista dla tłumacza (10 tytułów misji skróconych prowizorycznie — do potwierdzenia) |
| `INSTRUKCJA_PL.md` | ten tekst |

---

## Droga A — tylko DLC (bez budowania ISO, 5 minut)

Daje angielski wszędzie tam, gdzie gra czyta tekst z plików DLC: rozdziały 2–8 (fabuła tam,
gdzie przetłumaczona), menu i listy DLC, teksty bitewne, opisy misji DLC. Rozdział 1 i wspólne
menu z dysku (`config00`, `configst`, `mesbtl00`) zostają japońskie — do nich potrzebna jest droga B.

1. Zrób **kopię zapasową** swojego folderu DLC (tego, z którego PPSSPP czyta DLC, np.
   `…\NPJH50521`). Najprościej: skopiuj cały folder obok i dopisz `_ORYGINAL`.
2. Rozpakuj `DLC_EN_2026-10-14.zip`. W środku są 91 pliki `config01.EDAT … mesbtl19.EDAT`.
3. Skopiuj je do swojego folderu DLC, **nadpisując** pliki o tych samych nazwach.
   (Pliki są odszyfrowane, tak jak zestaw FULL_DLC — PPSSPP czyta takie bez różnicy, co
   sprawdziliśmy wcześniej na `eventP02.EDAT`.)
4. Uruchom grę w PPSSPP jak zwykle.

Powrót do japońskiego = skopiowanie plików z kopii `_ORYGINAL` z powrotem.

---

## Droga B — całość: ISO rozdziału 1 + DLC (jeden `.bat`, 10–15 minut)

Potrzebne raz: **Python 3.9 lub nowszy** na Windows — <https://www.python.org/downloads/>,
przy instalacji zaznacz **„Add python.exe to PATH”**. Nic więcej (żadnych bibliotek).

1. **Ściągnij repozytorium** jako ZIP i rozpakuj gdziekolwiek (np. `D:\SRWOE\patch\`):
   na stronie repozytorium wybierz gałąź `arena/c0e5c9d1-mtgcrawler` → zielony przycisk
   **Code** → **Download ZIP** (bezpośredni link:
   `https://github.com/szybkoiwyraznie-rgb/mtgcrawler/archive/refs/heads/arena/c0e5c9d1-mtgcrawler.zip`).
   Po rozpakowaniu interesuje cię podfolder `srw-oe-translation\`.
2. **Ściągnij z Dysku `pakiet_EN_2026-10-14.zip`** i rozpakuj go **do folderu
   `srw-oe-translation\pakiet_EN\`** — tak, żeby plik `00_dialogue.jsonl` leżał bezpośrednio
   w `pakiet_EN\` (a nie w kolejnym podfolderze). Ten folder jest w `.gitignore`, więc nic
   z niego nie trafi do repozytorium.
3. **Uruchom `srw-oe-translation\HOKUS_POKUS.bat`** (dwuklik). Skrypt widzi `pakiet_EN\`
   i otwiera **dwa okna wyboru** — niczego nie wpisujesz z palca:
   - pierwsze okno: wskaż plik **`SRW OE 1.08.iso`** (679 243 152 bajtów);
   - drugie okno: wskaż **folder z odszyfrowanymi plikami DLC** (ten sam zestaw, który jest na
     Dysku jako `FULL_DLC`). Jeżeli w folderze emulatora masz pliki zaszyfrowane, wskaż
     folder FULL_DLC, a nie folder emulatora.
   Zamknięcie okna bez wyboru = skrypt kończy, nic nie zapisuje. Okna można pominąć,
   przeciągając ISO na plik `.bat` albo podając ścieżki z wiersza poleceń:
   `HOKUS_POKUS.bat "D:\gry\SRW OE 1.08.iso" "D:\SRWOE\FULL_DLC"`.
4. **Czekaj.** Napis „Buduje patch… (to potrwa kilka minut)” — u nas 96 kontenerów zajęło
   ~3,5 minuty bez ISO; z ISO dochodzi przepisanie obrazu 680 MB (kilka minut na HDD).
   Na końcu skrypt wypisuje „Gotowe” albo „Cos odmowilo” i czeka na klawisz.
5. **Wynik** w `srw-oe-translation\srw-oe-patch\`:
   - `patched.iso` — nowy obraz (większy od oryginału o ok. 2,7 MB: pięć zmienionych plików jest
     dopisanych na końcu obrazu, reszta bajt w bajt jak w oryginale);
   - `DLC\…\*.EDAT` — te same 91 plików co w `DLC_EN_2026-10-14.zip` (zbudowane u ciebie);
   - `build_report.json` — raport.
6. **W PPSSPP** uruchom `patched.iso` zamiast swojego ISO. Pliki z `srw-oe-patch\DLC\`
   skopiuj do folderu DLC emulatora tak jak w drodze A (kopia zapasowa najpierw!).

Jeśli zamiast „Gotowe” jest „Cos odmowilo”: nie kasuj niczego, prześlij `build_report.json`
i treść okna konsoli (albo zrzut ekranu). Oryginały są nietknięte, skrypt można puścić ponownie.

### Czego się spodziewać / co sprawdzić w grze

- Ekran tytułowy, menu, sklep, lista jednostek, opisy przedmiotów i umiejętności, cytaty
  bitewne, tytuły i opisy misji — po angielsku.
- Fabuła: rozdziały 1–3 po angielsku, rozdział 4 częściowo (scenki wpisane w całości albo wcale,
  nie w połowie), rozdziały 5–8 i scenki poboczne od `eventP27` wzwyż — po japońsku, do czasu
  aż tłumacz je odda. Następny pakiet dopisze je bez żadnej zmiany w sposobie nakładania.
- **Na co patrzeć:** linie dialogów szersze niż 46 jednostek (jest ich ~300, dopuściliśmy do 52
  na podstawie najszerszych linii samej gry) — czy nic nie jest ucięte przy prawej krawędzi
  okna; rozdział 1 (`mesbtl00` i `eventP00` zapisane bez kompresji) — czy bitwy i scenki
  ładują się bez zacięć; menu DLC (`DLC_ID`) — czy pozycje listy wyglądają normalnie.
  Zrzut ekranu + nazwa scenki/menu wystarczą, żeby to naprawić.

### Gdy okno `.bat` miga i znika

Od wersji z 2026-10-14 (noc) `HOKUS_POKUS.bat` i `BISEKCJA.bat` same otwierają się ponownie w trybie,
w którym okno **nie zamyka się** po błędzie — zostaje tekst do zrzutu ekranu (pierwsze linie: folder,
wersja Windows). Jeśli mimo to okno znika w ułamku sekundy: otwórz folder `srw-oe-translation` w
Eksploratorze, kliknij w pasek adresu, wpisz `cmd`, Enter; w czarnym oknie wpisz `HOKUS_POKUS` i Enter —
komunikat zostanie na ekranie. Jeśli po dwukliku pojawia się niebieskie „System Windows ochronił ten
komputer" — „Więcej informacji" → „Uruchom mimo to" (plik pochodzi z pobranego zipa).

### Gdy gra się wywala — `BISEKCJA.bat` (szukanie winnego pliku)

Build z 2026-10-14 wieczorem padał na ekranie „Loading" (niebieski ekran PPSSPP `Read Word at
00000000`). Przyczyna znaleziona offline (plik `sysmes.bin` z komunikatami systemowymi był składany
złym narzędziem) jest naprawiona w tym wydaniu, ale **czy była jedyna — pokaże dopiero gra**. Jeśli
nowy `HOKUS_POKUS.bat` dalej daje crash, uruchom `srw-oe-translation\BISEKCJA.bat`:

1. Te same okna co w HOKUS_POKUS (ISO, folder DLC; pakiet bierze z `pakiet_EN\`).
2. Trzecie okno — lista wariantów. W każdym tłumaczony jest **tylko jeden kawałek gry**, reszta
   zostaje oryginalna:
   `A` configst.cpk (menu/teksty systemowe) · `B` config00.cpk (nazwy, umiejętności, przedmioty, lista DLC) ·
   `C` eventP00.cpk (dialogi rozdz. 1) · `D` mesbtl00.cpk (kwestie bitewne) · `E` imenu00.cpk (menu
   intermisji) · `F` całe ISO przetłumaczone, DLC oryginalne · `G` tylko DLC, ISO oryginalne ·
   `H` tylko DLC z dialogami · `I` tylko DLC bez dialogów.
3. Wynik ląduje w `srw-oe-bisekcja\<litera>\` (`patched.iso` i/lub `DLC\...`). Dla wariantów A–F
   uruchom `patched.iso` z tego folderu **z oryginalnym DLC**; dla G–I uruchom **oryginalne ISO**
   z podmienionym DLC z tego folderu.
4. Zapisz dla każdej litery „działa / crash (jaki ekran)". Zacznij od `F` i `G` (dzieli problem na
   ISO vs DLC), potem litery z tej połowy, która pada. Każda litera to osobny folder — nic się nie
   nadpisuje; foldery można kasować.

### Powrót do oryginału

Usuń folder `srw-oe-patch\`, w PPSSPP wskaż z powrotem swoje ISO, przywróć folder DLC z kopii
`_ORYGINAL`. Żaden oryginalny plik nie był modyfikowany.

---

## Co dokładnie jest w tym wydaniu (liczby z budowy 2026-10-14)

- Pakiet: 108 123 wiersze tekstu, 80 780 z angielskim (27 343 puste — wszystkie to dialogi
  fabularne, których tłumacz jeszcze nie oddał). Kontrola pakietu: 0 błędów.
- Budowa: 96 kontenerów (5 z ISO + 91 DLC), wszystkie zmienione; kontrola po budowie
  (odczyt z gotowych plików): 80 075 wierszy odnalezionych w plikach wynikowych, 72 odmówione
  (z tego 32 resztki tablic, 13 liczników menu DLC i 11 pustych rekordów umiejętności to śmieci
  ze starego eksportu, nie teksty; 6 osiągnięć, 2 przydomki postaci i 8 tytułów misji — patrz
  `DO_ZROBIENIA_2.md`), 633 za krótkie, by je odnaleźć automatycznie (1–2 znaki, np. „A”, „+1”).
- Fabuła wg kontenerów: eventP00–03 100 %, eventP04 59 %, eventP05–08 0 %, scenki poboczne
  eventP09/13/20–26 95–100 %, eventP27–32 0 %, evept101–102 100 %, evept103–108 9–71 %.

## Czego ten pakiet NIE robi

- Nie dotyka grafik (logo, przyciski w teksturach) — tylko tekst w plikach danych.
- Nie tłumaczy komunikatu o autozapisie wyświetlanego zaraz po starcie („本ゲームはオートセーブ…"):
  ten napis siedzi w programie gry (`EBOOT.BIN`), nie w plikach danych — osobne zadanie.
- Nie zawiera żadnych plików gry: wszystko powstaje z twojego ISO i twoich DLC.
- Nie działa na zaszyfrowanych plikach DLC ani na ISO innej wersji niż 1.08 (inne offsety).
