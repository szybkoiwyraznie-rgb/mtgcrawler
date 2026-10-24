# SRW Z (PL) — dziennik eksperymentów

Każdy test zapisujemy z dokładnymi liczbami/hashami i etykietą:
**potwierdzone** / **hipoteza** / **nieznane**. Twierdzeń o działaniu w
emulatorze nie stawiamy bez dowodów od właściciela (PCSX2).

## 2026-10-24 — rozpoznanie, decyzje właściciela, import vendora (faza 0)

**Potwierdzone (metadane Drive, bez pobierania zawartości plików gry):**

- Drzewo właściciela: Drive `SRW/SRWZ/rozpakowane ISO` (folder
  `1ujHDKXOlj_OtgY-A9i53JhS7Fuw14D1g` w `SRWZ`
  `1HnENcLdKxc_2j3k5CBewUhyvYrXFhKl0`), 16 wpisów top-level. Edycja
  **SLPS-25887**: `SLPS_258.87` 3 471 624 B (`1p4ek8vUsC5ukrHWeZSopO6ehhWEo1q4y`),
  `SYSTEM.CNF` 57 B, `vmap.dat` 3072 B, `IOPRP310.IMG` 278 353 B + 12
  katalogów danych.
- `DATA/` (13 plików): `stage.bin` **3 910 128 B**
  (`1dG_w3QBS3AEE_HJaolVV0HjskpaJYRDd`) — dokładnie rozmiar extentu z
  narzędzi upstream (LBA 1651029 × 2048, SIZE 3 910 128); `HSFC.BIN`
  250 112 B; `compdata.bn` 144 990 B; pozostałe (m.in. `vt1.bin`
  127 500 736 B) poza zakresem fazy 1.
- Wyszukiwanie Drive po `.iso/.chd/SLPS_258`: brak obrazu płyty (tylko
  folder `rozpakowane ISO` i `SLPS_258.87`) — zgodnie z decyzją modelową
  poniżej obraz **nie jest potrzebny**.

**Potwierdzone (audyt upstream, klon `--depth 1`, commit
`fed4c8b910028e964c5c6de87b2d58b3b92628b9`, licencja MIT):**

- Domknięcie zależności rdzenia pipeline'u skryptu = 7 plików /
  66 772 B (`extract_script`, `apply_script`, `verify_pointers`,
  `scan_visible_defects`, `build_compare` → `banlz`, `rewrap_dialogue`;
  poza tym tylko stdlib). Wszystkie 7 przechodzi `ast.parse`.
- Adresowanie: `rewrap_dialogue.py` — `LBA, SIZE, SECTOR = 1651029,
  3910128, 2048`; `apply_script.py` nadpisuje extent **w miejscu, ten sam
  rozmiar**. `docs/TECHNICAL.md` nazywa extent `DATA_STAGE.BIN`
  (banlz) — zgodne z `stage.bin` właściciela co do rozmiaru.
- Skan ścieżek osobistych (`C:\Users\…` itd.) po `tools/`+`docs/`:
  trafienia tylko w 3 narzędziach spoza rdzenia (`build_texture_pack.py`,
  `gen_intro_cards.py`, `zkn_deepseek.py`) — wyłączone z importu. Zbiór
  zaimportowany: **brak trafień**.
- Zaimportowano do `vendor/retro-trans/`: 19 plików / 180 088 B
  (7 narzędzi + 9 dokumentów + `LICENSE` + `TRANSLATING.md` +
  `UPSTREAM_README.md`), bez modyfikacji. Nie importowano `analysis/`
  (~26 MB) ani pozostałych ~269 narzędzi i 6 skryptów `.ps1`.

**Decyzje właściciela (2026-10-24, zapisane też w `../README.md`):**

1. Model pracy jak w SRW OE: ISO (~3,7 GB) zostaje lokalnie u
   właściciela; sandbox pracuje na rozpakowanych plikach z Drive;
   dostarczany `PATCH.bat` patchuje ISO u właściciela. Zastępuje
   wcześniejszy tego dnia pomysł wgrywania ISO na Drive.
2. Pliki tłumacza: oryginał JP + kolumna referencyjna EN (retro-trans)
   + nasz glosariusz terminologii z SRW OE; tekst PL świeży z japońskiego.
3. Najpierw dowód techniczny (round-trip ekstrakcji + prototyp polskiej
   czcionki), potem pliki tłumacza.
4. Ambicja czcionki (remap pełnoszeroki vs half-width/VWF): decyzja po
   prototypie.

**Hipoteza (plan fazy 1, jeszcze niewykonane):** rzadki (sparse) obraz
wirtualny z `stage.bin` pod offsetem 1651029 × 2048 pozwoli uruchomić
niemodyfikowane narzędzia vendora w sandboxie i udowodnić round-trip
bez ISO; zgodność bajtów rozpakowanego `stage.bin` z extentem w ISO
udowodni dopiero test no-op bata u właściciela.

**Nieznane:** hashe plików gry (żaden nie został jeszcze pobrany),
limity tekstu poza skryptem głównym, źródło glifów PL, ustawienia PCSX2
właściciela. Brak jakichkolwiek wyników runtime.

## 2026-10-24 — inwentarz powierzchni tekstowych (dokumentacja vendora) + PCSX2 właściciela

Pytanie właściciela: czy wszystkie teksty są w `stage.bin`? Odpowiedź:
**nie** — jak w SRW OE tekst jest rozproszony po kilku plikach.
Szczegóły: `docs/TEXT_SURFACES.md`.

**Potwierdzone (dokumentacja upstream w vendorze — `FINDINGS.md`,
`TECHNICAL.md` — zgodne z rozmiarami plików `DATA/` właściciela tam,
gdzie je znamy):**

- `DATA/stage.bin` = tylko scenariusz główny: 205 rekordów banlz
  (jeden scenariusz = jeden rekord, ~400–1450 wierszy; wiersz =
  zablokowana linia mówcy + treść, ramka maks. 3 linie × 34 kolumny;
  offsety stringów inline w bytecode scenariusza).
- `DATA/HSFC.BIN` (właściciel: 250 112 B) = streszczenia etapów,
  4 rekordy banlz.
- `btl/SRVC.BIN` (+ `.SEG`) = dialogi/kwestie bitewne (~1,08 mln
  znaków; wg README upstream 19 213 linii bitewnych), **bez kompresji**,
  indeksowane `.SEG`; regiony upstream 3 313 040 B + 1 416 B — rozmiary
  u właściciela jeszcze niezmierzone.
- `DATA/compdata.bn` (właściciel: 144 990 B skompresowane) = jeden
  rekord banlz → 524 032 B pod RAM `0x006D6800`: nazwy/tytuły/biogramy
  (jednostki, piloci), teksty broni/przedmiotów/zdolności, 55 opisów
  zdolności/skilli, tytuły odcinków/scenariuszy, etykiety wyboru trasy,
  UI statystyk/wyszukiwarki/bonusów; pula stringów ~3 433 wpisów na
  absolutnych wskaźnikach RAM (nie da się wydłużać w miejscu, da się
  przepakować pulę); kodowanie „menu" (ASCII `0x2E–0x3D` = kody
  sterujące). Narzędzia puli/COMPDATA **nie** są jeszcze w vendorze.
- `SLPS_258.87` (ELF, 3 471 624 B) = część UI: skille, tytuły serii,
  komunikaty systemowe (SJIS w ELF) + miejsce patcha renderera/czcionki.
  Dokładny podział UI ELF vs COMPDATA — do ustalenia.
- `MAP/MAPNAME.BIN` = 195 nazw map, SJIS, stały krok 256 B (= 49 920 B);
  rozmiar u właściciela niezmierzony. `DATA/MtVZkn*.bin`
  (29 936 / 293 696 / 185 600 B) = archiwa encyklopedii (grupa TEXT
  upstream); `DATA/MtV_ProS.BIN` 9 056 B — zawartość TBD. Teksty
  malowane w teksturach = osobna powierzchnia (poza zakresem do fazy 2+).

**Fakt od właściciela:** emulator testowy to **PCSX2 v2.9.144**
(Windows x64 Qt, `pcsx2-v2.9.144-windows-x64-Qt.7z` z GitHub Releases) —
pobrany 2026-10-24. Ustawień jeszcze nie znamy.

Żaden plik gry nie został w tym kroku pobrany ani przetworzony; brak
wyników runtime. Weryfikacja każdej powierzchni na kopii właściciela =
faza 1 (STAGE) i faza 2 (reszta).
