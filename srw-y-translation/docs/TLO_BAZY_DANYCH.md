# SRW Y — tło ekranu Database

## O co chodzi

W ekranie **Database** (mechy i postacie) gra rysuje model na tle wnętrza
A. Adventu. Tło jest osobną **teksturą**, nie tekstem, którego dotyczy patch —
dlatego nie zmienia go żaden z dotychczasowych planów. Cel: jednolite czarne tło,
żeby screeny były czyste.

## Czego brakuje

W repozytorium nie ma **żadnych plików gry** (ani jednego bundla), więc nie mogę
nazwać tej tekstury. Nazwa musi wyjść z kopii właściciela. Wysyłanie bundli nie
jest potrzebne: paczka robi na jego komputerze **spis tekstur** i jeden mały ZIP.

## Paczka dla właściciela

`SRW_Y_SPIS_TEKSTUR.zip` (Drive `1plOEQSWn2bjV0aNLyylUiDYC-2YRV5t2`, 11 019 B,
SHA-256 `cb9b5a31…d0f11`), zbudowana przez `tools/build_scan_kit.py`:

```
SRW_Y_SPIS_TEKSTUR/
  CZYTAJ_TO.md            instrukcja po polsku
  SKANUJ.bat              dwuklik: szuka gry, stawia .venv, skanuje, pakuje wynik
  narzedzia/
    spis_tekstur.py       silnik: czyta bundel po bundlu, nic nie zapisuje w grze
    srw_y_bundle_crypt.py cipher bundli (ten sam, co w patcherze)
    requirements.txt      UnityPy==1.25.4, pycryptodome==4.2.0, lz4==4.4.5,
                          texture2ddecoder, Pillow
```

BAT jest wzorowany na `PATCH_PL.bat` z kitów patcha: szuka `py -3`/`python`,
zakłada osobne `.venv`, przy pierwszym uruchomieniu dociąga zależności, a jeśli
gry nie znajdzie w typowych miejscach, przyjmuje folder przeciągnięty na plik.

Efekt: na Pulpicie `SPIS_TEKSTUR.zip` z `RAPORT_TEKSTUR.txt` (każda `Texture2D`:
nazwa, `WxH`, format, bundel) oraz `PODGLADY/` — zmniejszone PNG **wszystkich
obrazów ≥ 1280×720**, numerowane tak samo jak w raporcie.

## Jak działa skan (i dlaczego jest szybki)

- Pomija bundle mniejsze niż 64 KiB — tabele tekstu i scen mają kilka kilobajtów,
  więc odpada ~90% plików bez ich otwierania.
- Deszyfruje cipher strumieniowy tak samo jak `srw_y_bundle_crypt`, ale XOR robi
  `Crypto.Util.strxor` (C) zamiast pętli po bajtach: ~60 MB/s zamiast ~1 MB/s.
- Czyta tylko typetree `Texture2D` (bez dekodowania pikseli); piksele dekoduje
  wyłącznie dla podglądów, natychmiast po odczytaniu bundla, żeby nie trzymać
  w pamięci całych plików.
- Każdy bundel w `try/except`: nieczytelny plik trafia do raportu, nie przerywa
  skanu. Nagłówek raportu podaje liczbę bundli, tekstur, błędów i bundli bez
  obiektów — po tym poznam, czy gra ma inną wersję, niż zakładam.

## Co będzie dalej

1. Właściciel odsyła `SPIS_TEKSTUR.zip`.
2. Rozpoznaję wnętrze A. Adventu na podglądach (numer → bundel + nazwa tekstury).
3. Podmiana pikseli na czarne w tym samym formacie i rozmiarze, przebudowa
   bundla na jego kopii, odczyt zwrotny i `COFNIJ.bat` — tą samą drogą, co atlas
   menu (`tools/build_pl_ui_atlas.py`), ale na jego plikach, nie na moich.

## Czego to nie obiecuje

- Nie wiem, czy ekran rysuje tło wyłącznie z tekstury — jeśli część tła to
  geometria 3D, podmiana da czarną plamę tylko w miejscu obrazu. Rozstrzygnie to
  pierwszy test na screenie.
- Nadal `runtime_tested: false` po naszej stronie: sprawdzenie robi właściciel.

## Runda 2: paczka podmieniająca tło (2026-11-08)

Właściciel odesłał `RAPORT_TEKSTUR.txt` i wskazał na podglądach
`22869_BG_DataBase_01_1920x1080.png` jako tło ekranu Database: tekstura
**`BG_DataBase_01`, 1920×1080**. Podglądów (1 GB) nie wysyłał i nie musi —
wystarczyła nazwa.

Dlatego nie prosimy już o żaden plik gry. Nowa paczka
**`SRW_Y_TLO_BAZY_DANYCH.zip`** (Drive `1m4hsMm1yUjzTmclIpa7fEBLE6fV7oZ1E`,
22 322 B, SHA-256 `19e2203b…47f3c`, dwa przebiegi bajtowo identyczne) robi całą
robotę na kopii właściciela:

- `PATCH_TLO.bat` → `narzedzia/tlo_bazy.py install`:
  1. znajduje grę (albo dostaje folder przeciągnięty na plik),
  2. przegląda bundle ≥ 64 KiB, deszyfruje i **dekompresuje bloki**, żeby znaleźć
     te, które w ogóle wymieniają nazwę `BG_DataBase_01` (nazwa siedzi w pliku
     serializowanym, więc sam plaintext bundla to za mało — bloki bywają LZ4),
  3. dla każdego kandydata `db_black.patch_plain()`: sprawdza rozmiar tekstury
     (1920×1080), format, i czy slot w strumieniu `.resS` ma dokładnie tyle
     bajtów, ile wymaga format,
  4. koduje jednolitą czerń **w tym samym formacie** (BC7/DXT1/DXT5 na etcpak,
     BC4/BC5 oraz RGBA32/RGB24/ARGB32/BGRA32 jako surowe piksele),
  5. dekoduje zakodowane bloki z powrotem i wymaga czerni + krycia
     (BC7 kwantyzuje alfę do 7 bitów, więc próg to 250, nie 255),
  6. przebudowuje bundle (`srw_y_rebuild`), sprawdza, że **każdy inny obiekt jest
     bajt w bajt taki sam** i że strumień wrócił,
  7. zapisuje plik dopiero po tych testach, obok zostawia
     `*.srwy-tlo-original.bak`, a stan w `narzedzia/STAN_TLO.json`;
- `COFNIJ.bat` → `restore`: kopiuje oryginały z `.bak` i sprawdza hashe.

Raport `narzedzia/RAPORT_TLO.txt` ma linię na każdy bundle: znaleziona tekstura,
format, liczba zmienionych bajtów, czy czerń przeszła weryfikację.

### Czego ta paczka nie wie

- Formatu tekstury nie znamy z góry — kod rozpoznaje go w bundlu i odmawia
  roboty, jeśli to format, którego nie potrafimy zapisać (np. ASTC/ETC). Wtedy
  raport poda nazwę formatu i dopiszę obsługę.
- Czy tło to wyłącznie ta tekstura, czy także geometria 3D — to rozstrzygnie
  pierwszy screen z gry.

## Runda 3: bez przeszukiwania dysku (2026-11-08)

Właściciel zgłosił, że `PATCH_TLO.bat` z rundy 2 wisiał godzinę na komunikacie
„Szukam tekstury BG_DataBase_01 1920x1080 w bundlach…”, i zapytał, po co skrypt
szuka tekstury, skoro `RAPORT_TEKSTUR.txt` podawał, w którym pliku co siedzi.
Miał rację: to był mój błąd, nie ograniczenie danych. Raport nigdy nie był
odczytany w warsztacie (zapisany tylko jako plik na Drive), więc paczka szukała
nazwy w **9 892 bundlach**, deszyfrując i dekompresując każdy — godzina pracy
komputera zamiast kilku sekund.

**Co jest w raporcie (odczytane, 3 159 408 B, 36 997 tekstur, 0 bundli
nieodczytanych):** tekstura `BG_DataBase_01` 1920×1080, format **25 (BC7)**,
występuje w **16 bundlach**:

```
9ed026a1fc86446a7b96c863f449293e.bundle   ← podgląd 22869_…, który wskazał właściciel
1b5da0ef65aef8e3db19c7f1b4a62ad2.bundle   1c6bae8333d43883715cd3c80e6b06a8.bundle
21483b8c72946df172995fc28fe8513c.bundle   22ac8fb334093afc874a670d95b01504.bundle
24389cf9b6ff0c69440a0054b07a0a9b.bundle   2fcd1b5e54f206a6ecf97a71c74dcd81.bundle
36f12b4c38f68ad8811ade71945010c9.bundle   3de1bf33b35e63e87abb86acc029004f.bundle
77a2edfda00011ae81b0d44829865614.bundle   77c28b41bf3d3714c686eafb475fc32a.bundle
819fcfa52c97d0420146203b181e38cf.bundle   89807f3be3a7048e8e26f7e8edccb6da.bundle
90eb8d46b646d92973b36bac119ca271.bundle   9e56e5c953cea02a1e42b2ed1dba787f.bundle
cea16a719b85736215c37206de071b72.bundle
```

**Paczka v2** (`SRW_Y_TLO_BAZY_DANYCH_v2.zip`, Drive
`1BBOCU8MyiQeZJiIq5ycbsLVxB8S-VyK3`, 24 085 B, SHA-256 `c3dc2fab…d786a`,
MD5 `b4b5d7f7e9b459f2ca1b2728040f859e`; dwa przebiegi dają identyczne bajty —
wpisy w ZIP-ie mają stały czas) ma tę
listę **wpisaną na stałe** w `narzedzia/tlo_bazy.py` (`BUNDLES`) i podmienia
wszystkie 16 plików, które są w kopii gry — bez `rglob`, bez deszyfrowania
plików po kolei, bez czekania. Pierwszy na liście jest ten, którego podgląd
właściciel wskazał; `--tylko-rozpoznany` ogranicza robotę do niego samego,
a `--skanuj` (awaryjnie, gdyby gra była innej wersji) robi dawny przebieg —
teraz z postępem co 500 plików, więc widać, że coś się dzieje.

Testy `tests/test_db_pinned_bundles.py` pilnują trzech rzeczy: lista to 16
unikalnych nazw `[0-9a-f]{32}.bundle` z rozpoznanym bundle'em na czele,
`pinned_paths()` **nie woła `rglob`** (podstawiona pułapka wywala test), a gdy
w grze nie ma żadnego pliku z listy, `install` **odmawia** i pisze o tym wprost,
zamiast po cichu zaczynać przeszukiwanie.

Czego to nie dowodzi: nie wiem, który z 16 bundli gra wczytuje na ekranie
Database, dlatego podmieniamy wszystkie — dlatego też po instalacji zostaje 16
kopii `*.srwy-tlo-original.bak`. Jeśli ekran rysuje tło także z geometrii 3D,
czarna tekstura zasłoni tylko jej część.

## Wynik u właściciela (2026-11-08)

Paczka v2 zadziałała: **„background Adventa już nie ma”**. Została tylko delikatna
siatka-animacja rysowana na tym ekranie — właściciel ocenił ją jako mało
agresywną i **zaakceptował** („pewnie trudno byłoby ją usunąć, więc jak dla mnie
jest ok”). To pierwszy element tego projektu potwierdzony w samej grze;
z naszej strony nadal `runtime_tested: false`, bo test zrobił właściciel.

Co to znaczy dla danych:

- podmiana pikseli `BG_DataBase_01` na czerń **wystarczyła**, żeby zniknęło tło
  wnętrza A. Adventu — czyli ekran rysuje je z tej tekstury, a nie z geometrii 3D;
- siatka to **osobna warstwa**: albo druga tekstura, albo efekt (shader/particle)
  rysowany na wierzchu. W `RAPORT_TEKSTUR.txt` są kandydaci o takich nazwach —
  `GRIDKT_000_B` / `GRIDKT_050_B` / `GRIDKT_051_B` / `GRIDKT_100_B`
  (1280×1280, format 25 = BC7), `GRIDKT_000_F` / `GRIDKT_100_F` (400×400, BC7),
  `GRID_KT_000_Full` (1080×1080, format 12 = DXT5) oraz warianty `KGRIDKT_*`
  i `KZLGRID_KT_*` — ale **nie wiemy**, która z nich trafia na ten ekran; nazwa
  nie dowodzi użycia.
- Skoro właściciel to zaakceptował, **nie ruszamy tego**. Gdyby kiedyś chciał
  czystą czerń, droga jest ta sama co tutaj: podmiana pikseli na czarne w tych
  teksturach (albo sprawdzenie, czy siatka nie jest czasem shaderem, czego
  podmiana tekstury nie zmieni).

`COFNIJ.bat` z tej samej paczki nadal przywraca oryginały: w grze leżą kopie
`*.srwy-tlo-original.bak` obok 16 podmienionych bundli, a lista z hashami jest
w `narzedzia/STAN_TLO.json`.

## Runda 4: siatka też na czarno (2026-11-09)

Właściciel wrócił do tematu: pulsująca siatka, którą wcześniej zaakceptował,
jednak przeszkadza — i **znalazł jej teksturę**: `22866_BG_DataBase_02_1920x1080.png`,
czyli **`BG_DataBase_02`**, 1920×1080.

Sprawdzone w jego `RAPORT_TEKSTUR.txt` (3 159 408 B, 37 157 wierszy):

- `BG_DataBase_02` występuje w **tych samych 16 bundlach** co `BG_DataBase_01`
  — zbiory są identyczne (`d1 == d2`, bez różnic w obie strony),
- obie mają 1920×1080 i format **25 (BC7)**.

Dlatego nie trzeba ani nowego spisu, ani przeszukiwania dysku: to ta sama robota
z inną nazwą tekstury. Nowa paczka **`SRW_Y_TLO_BAZY_DANYCH_v3.zip`**
(24 627 B, SHA-256 `28b68b785b1bf12a57684ed94f5cf46c023b2a499a3e8140ec8cd973a1c640de`,
dwa przebiegi bajtowo identyczne; Drive `17diBeQf8zcKDNK66S5-TymHmNDI2DZCT`)
budowana przez `tools/build_db_kit2.py`, narzędzie `tools/tlo_bazy2.py`:

- `PATCH_TLO2.bat` → `tlo_bazy2.py install`: ta sama lista 16 bundli wpisana na
  stałe, `db_black.patch_plain()` zamienia piksele `BG_DataBase_02` na czerń
  w tym samym formacie i rozmiarze, bundle jest przebudowywany i sprawdzany
  (inne obiekty bajt w bajt, czerń dekodowana z powrotem, slot w strumieniu),
- `COFNIJ2.bat` → `tlo_bazy2.py restore`,
- stan w `narzedzia/STAN_TLO2.json`, raport w `narzedzia/RAPORT_TLO2.txt`
  — osobne pliki, żeby `COFNIJ.bat` z v2 nadal działał na swoim zapisie.

### Jedna rzecz, którą trzeba było poprawić w logice cofania

Kopie `*.srwy-tlo-original.bak` przy plikach gry powstały przy pierwszej
podmianie i trzymają **oryginał gry**, a nie stan sprzed tej rundy. Stara logika
`restore` porównywała przywrócony plik z hashem stanu *sprzed* podmiany, więc by
odmówiła. Teraz `install` zapisuje dodatkowo `sha256_backup` (hash pliku kopii)
i to on jest sprawdzany, a raport mówi wprost: przy tych plikach `COFNIJ2.bat`
przywraca oryginał, czyli **cofa obie podmiany**. Pilnują tego
`tests/test_db_grid_bundles.py` (6 testów, m.in. restauracja z kopii starszej
rundy i odmowa przy kopii o złym hashu).

### Czego to nie dowodzi

Siatka może być rysowana shaderem albo cząsteczkami, a nie tą teksturą —
podmiana pikseli nic wtedy nie zmieni. To pierwszy test na ekranie właściciela.

## Runda 5: v4 — oba obrazy naraz i na plikach z moda 4K (2026-11-13)

Właściciel zainstalował mod **4K Visual Overhaul**, który podmienia wszystkie
assety 2D na upscalowane, i zapytał, czy v2/v3 w ogóle jeszcze zadziałają i
w jakiej kolejności je instalować. Odpowiedź: **nie zakładać, że zadziałają** —
obie paczki sprawdzały grę 1.4.0 (sumy plików, `1920×1080` w schemacie), a mod
zmienia i piksele, i rozmiar slotu. Kolejność też przestała mieć sens: v2 i v3
ruszają **te same 16 bundli**, więc każda z nich widzi efekt poprzedniej.

**Paczka v4** (`SRW_Y_TLO_BAZY_DANYCH_v4.zip`, budowana przez
`tools/build_db_kit4.py`, narzędzie `tools/tlo_bazy4.py`) jest jedną paczką,
która robi 2 w 1:

| problem po modzie 4K | co robi v4 |
|---|---|
| plik nie jest już wersją 1.4.0 (sumy nie pasują) | **nie sprawdza sum** — czyta zawartość: czy w bundlu jest tekstura o nazwie i czy slot pasuje do formatu |
| tekstura ma inny rozmiar (np. 3840×2160) | rozmiar, format i slot bierze **z bundla w grze**, więc 4K wyczerni w 4K |
| kolejność v2 → v3 | oba obrazy w **jednym przebiegu**, jedna kopia zapasowa, jedno cofnięcie |
| mod mógł przebudować bundle i zmienić nazwy plików | `--skanuj` szuka nazw tekstur po zawartości całej gry |

Jak to jest zrobione: `blacken_streams()` to czysta funkcja na bajtach —
dostaje strumienie bundla i sloty (`stream`, `offset`, `size`) obu tekstur,
zwraca nowe strumienie. Dzięki temu „2 w 1” jest sprawdzalne bez gry: obie
tekstury w jednym strumieniu, w dwóch różnych strumieniach, jedna już czarna,
slot niezgodny z formatem, format nieobsługiwany, brak strumienia — każdy
przypadek ma test (`tests/test_tlo_bazy4.py`, 13 testów). Dopiero potem
`blacken()` robi jedno `rebuild_plain`, jedno sprawdzenie „inne obiekty bajt
w bajt” i jedno sprawdzenie, że czerń wróciła z przebudowy.

Stan i raport są osobne (`STAN_TLO4.json`, `RAPORT_TLO4.txt`), żeby cofnięcia
v2/v3 dalej działały na swoich zapisach. `SPRAWDZ4.bat` liczy to samo i **nic
nie zapisuje** — a `restore()` odmawia pracy na stanie z tego trybu, żeby nie
„cofnąć” czegoś, czego nigdy nie zmieniono.

### Czego v4 nie dowodzi — i co to zamyka

Nie mam **żadnego** bundla z teksturami po modzie: `RAPORT_TEKSTUR.txt` jest
ze spisu z 1.4.0, a moda nie da się pobrać w tej sesji (Nexus, 0.3–16.7 GB).
Dlatego v4 nie zakłada, że nazwy plików i rozmiary są te same — sprawdza to
na miejscu i mówi o każdym pliku w raporcie. Pierwszy przebieg u właściciela
jest więc testem na prawdziwych danych, a nie na moim założeniu.

Dodatkowo jest **zbieracz** (`SRW_Y_ZBIERACZ_TLO.zip`, `tools/zbieracz_tlo.py`):
jedno kliknięcie pakuje te bundle (z listy **i** znalezione po zawartości) do
`SRW_Y_ZBIORCZE_TLO.zip` na Pulpicie, z raportem rozmiarów i formatów. Jeśli
właściciel go odeśle, da się potwierdzić v4 na plikach po modzie przed
uruchomieniem patchera — bez wypisywania mu ścieżek do ręcznego kopiowania.

### Paczki z tej rundy (na Dysku, suma sprawdzona po odczycie z powrotem)

| paczka | co to | ID na Dysku | B | SHA-256 |
|---|---|---|---|---|
| `SRW_Y_TLO_BAZY_DANYCH_v4.zip` | patch tła: oba obrazy naraz, działa z modem 4K | `1bZ_fNXZSerpSDHjRbKh5UYlB9UI2qipR` | 27 742 | `5ad28d6f…e0817f` |
| `SRW_Y_ZBIERACZ_TLO.zip` | zbieracz: pakuje bundle z tłem do jednego ZIP-a, nic nie zmienia | `1lPAC9R28kin_6rL9jhFXLXl-omIy4isK` | 13 490 | `48bce752…14b4e1` |

Oba pliki pobrane z Dysku po wgraniu: bajt w bajt zgodne z tym, co zbudowałem
(`cmp` bez różnic), ZIP-y przechodzą test CRC. v4 zbudowana dwa razy — identyczna.

## Runda 6: v5 — piksele bywają w obiekcie, nie w strumieniu (2026-11-13)

### Co się stało u właściciela

v4 na grze **po modzie 4K** wypisała, na każdym z 16 plików z listy:

```
POMIJAM BG_DataBase_0X: nie ma strumienia (brak)
BLAD: zaden bundle nie ma BG_DataBase_01 ani BG_DataBase_02
```

Czyli paczka zrobiła dokładnie nic — a raport wyglądał, jakby gra nie miała tych
tekstur. Nie o to chodziło: tekstury są, tylko **zapisane inaczej**.

### Dlaczego: dwa tryby zapisu tekstury

Unity trzyma piksele tekstury na dwa sposoby i oba są w tej grze:

| tryb | gdzie piksele | jak to wygląda w typetree | kto tak robi |
|---|---|---|---|
| `stream` | w osobnym pliku `.resS` w tym samym bundlu | `m_StreamData = {offset, size, path}` | gra 1.4.0 |
| `inline` | **w samym obiekcie tekstury** | `image data` = bajty, `m_StreamData` puste | mod 4K (przepakował assety) |

v2/v3/v4 znały tylko `stream`: `texture_slots()` szukało `m_StreamData.path`
i bez niego mówiło „nie ma strumienia”. Po modzie **wszystkie 16 plików** jest
w trybie `inline`, więc v4 odrzuciła wszystkie 16. To nie był problem z modem
ani z listą plików — to był błąd założenia w narzędziu.

### Co robi v5

1. `texture_slots()` czyta z typetree **oba** pola i wybiera tryb tak samo, jak
   `Texture2D.get_image_data()`: jeśli obiekt niesie `image data`, to on jest
   obrazkiem; `m_StreamData` jest używane tylko wtedy, gdy pikseli w obiekcie nie ma.
2. `inline` zapisuje się **nowym typetree obiektu** (`save_typetree` →
   `m_CompleteImageSize` + `image data`), a `stream` — jak dotąd, podmianą slotu
   w strumieniu. Oba tryby mogą być w jednym pliku i idą w **jednym**
   `rebuild_plain`.
3. Po przebudowaniu sprawdzany jest **każdy** poziom mipmapy osobno
   (`verify_black_chain`). Mipmapy nie są ozdobą: 4K ma ich kilkanaście, gra
   rysuje z nich miniaturę, a slot tekstury obejmuje cały łańcuch — wyczernienie
   tylko poziomu 0 zostawiłoby widoczny obrazek, a urwany łańcuch zepsułby rozmiar.
4. Poziomy mniejsze niż 4×4 (2×2 i 1×1 na końcu łańcucha) też się kodują: format
   BC zajmuje cały blok 4×4, więc koder dostaje obrazek dopełniony. etcpak sam
   odmawia („width or height not multiple of 4”) — to wyszło w teście.

### Skąd wiem, że to działa — bez plików gry

Nie mam ani jednego bundla po modzie 4K (`RAPORT_TEKSTUR.txt` jest ze spisu
1.4.0, moda nie da się pobrać w tej sesji). Zamiast wierzyć, że „się uda”:

* **prawdziwe pliki gry, które mam, przechodzą zapis bajt w bajt.** `SerializedFile.save()`
  na strumieniu z `1c12bbab…bundle` (33 835 864 B) i `2d69c099…bundle` daje
  **identyczne bajty** — czyli biblioteka nie zmienia niczego po drodze, więc
  podmiana jednego obiektu tekstury jest bezpieczna strukturalnie;
* **syntetyczny bundle** (`tools/bundle_fixture.py`) buduje SerializedFile
  z typetree z TPK, wkłada tekstury w obu trybach (także oba w jednym pliku)
  i pakuje w kontener UnityFS z blokami LZ4 — na nim `blacken()` przechodzi
  całą drogę: odczyt → czerń → zapis obiektu → przebudowa → odczyt z powrotem.
  To są testy `tests/test_tlo_bazy5.py`; nie zależą od żadnego pliku gry;
* **symulacja całej gry po modzie**: 16 bundli, każdy z teksturą 3840×2160
  w trybie `inline` → `install()` wyczernia **16 z 16**, 0 pominiętych, ~98 s;
  `restore()` przywraca każdy plik bajt w bajt.

Czego to nadal nie dowodzi: że mod 4K trzyma **dokładnie te dwie** tekstury pod
tymi nazwami. Dlatego `SPRAWDZ5.bat` nic nie zmienia i wypisuje dla każdego pliku
tryb, rozmiar, format i liczbę mipmap, a `--skanuj` szuka nazw po zawartości,
gdyby pliki przestały się zgadzać.

### Drugi błąd tej samej rundy: zbieracz nie działał wcale

`SRW_Y_ZBIERACZ_TLO.zip` (v1) kończył każdą zbiórkę wyjątkiem:

```
NameError: name 'log' is not defined
```

`zbieracz_tlo.py` **wołał** `log(lines, …)` w ośmiu miejscach, ale nigdy jej nie
zdefiniował — brakowało funkcji, którą ma bliźniacze `tlo_bazy4.py`. Do tego
`textures_named()` podawało UnityPy cały kontener zamiast rozwiniętego strumienia
bloków LZ4, więc nawet po naprawie `log` raport zawsze mówiłby „brak naszych
tekstur”. Oba błędy naprawione; raport podaje teraz tryb zapisu, liczbę mipmap
i rozmiar pikseli — czyli to, po co zbieracz jedzie do właściciela.

### Paczki z tej rundy (na Dysku, suma sprawdzona po odczycie z powrotem)

| paczka | co to | ID na Dysku | B | SHA-256 |
|---|---|---|---|---|
| `SRW_Y_TLO_BAZY_DANYCH_v5.zip` | patch tła: oba obrazy, **oba tryby zapisu**, mipmapy | `1exOLqP0xtMF3yC0JYiWZAeZvMOiBuib3` | 31 126 | `75e14fe0…5028bd0` |
| `SRW_Y_ZBIERACZ_TLO_v2.zip` | zbieracz po naprawie `log()` i odczytu bloków | `13HO38MaOP23Wb7YqVOieAzsbjZefOBYK` | 14 265 | `c800e550…3e6ac8bb8` |

Oba pliki pobrane z Dysku po wgraniu: `cmp` bez różnic, ZIP-y przechodzą test
CRC. Każda paczka zbudowana dwa razy — identyczna bajt w bajt (`build()` ma stały
znacznik czasu, więc SHA-256 z logu i z Dysku znaczy to samo).
