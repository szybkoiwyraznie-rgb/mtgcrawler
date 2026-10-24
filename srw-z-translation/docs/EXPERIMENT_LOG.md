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

## 2026-10-24 — czcionka najpierw (decyzja), wejścia lokalne, dowód STAGE w sandboxie, landmarki renderera

**Decyzja właściciela:** zaczynamy od czcionek, ambitnie — polskie znaki
tej samej (półszerokiej) szerokości co angielskie, budowane na korpusach
liter łacińskich z ogonkami; bez półśrodków (pełnoszeroki remap nie jest
docelową drogą). Projekt: `docs/FONT_RESEARCH.md`.

**Potwierdzone (pobranie plików właściciela z Drive do ignorowanego
`local/inputs/`; checkout sandboxa najpierw zresynchronizowano do
`origin/arena/7bb0f98d-mtgcrawler` = `e50e502`):**

- `SLPS_258.87` (Drive `1p4ek8vUsC5ukrHWeZSopO6ehhWEo1q4y`): 3 471 624 B,
  SHA-256 `6c4c81c4e5aa3db1f52d70b8183ce11c01fc6b265ae4d53fa4d6a657c5019b50`.
- `stage.bin` (Drive `1dG_w3QBS3AEE_HJaolVV0HjskpaJYRDd`): 3 910 128 B,
  SHA-256 `9c56d42f96df7b409ccf468b24412322ed627b9cbbd656864818a404d89240dc`.
  Oba pliki pokryte `.gitignore` (`git check-ignore` OK), poza repo.

**Potwierdzone (sandbox, rzadki obraz wirtualny: `stage.bin` pod
offsetem 1651029×2048 = 3 381 307 392; narzędzia vendora uruchamiane z
kopii w `local/work/tools_run/`, niemodyfikowane):**

- `extract_script.py`: **119 837 wierszy** (95 627 z japońskim, 24 210
  tylko łacińskich), JSON 15 778 893 B w `local/`; ~3,7 s.
- `apply_script.py --write` niezmienionego JSON na kopii obrazu:
  119 837 unchanged / 0 to write / 0 REJECTED; extent po apply
  **bajt-identyczny** (ta sama SHA-256). Uwaga: to dowód no-op;
  test zapisu *zmienionego* wiersza należy do prototypu P2.
- `verify_pointers.py` (obraz dziewiczy): 205 rekordów, 131 976
  wskaźników, 121 382 (91,97%) trafia na początek stringa; najsłabsze
  rec61 82,1%, rec20 82,2%, rec88 82,8% — linia bazowa pod porównania.

**Potwierdzone (ELF właściciela vs `RENDERER.md`):** mapowanie PT_LOAD
`vaddr 0x100000 ↔ plik 0x1A80` (readelf); 5/5 słów kontrolnych zgodnych:
`0x22137C=0x28410080`, `0x13A390=0x92820000`, `0x13A608=0x00441025`,
`0x13A6C0=0x3401827A`, `0x13A6F8=0x340182F2`; tablica banków `0x433E30`
= `13A7D8 13A7F8 13A818 13A838 13A898 13A898 13A858 13A878`.

**Potwierdzone (inwentaryzacja znaków w wyekstrahowanym skrypcie JP,
2 448 170 znaków):** `$` = prefiks placeholderów (6 396×: `$n` 4 398,
`$c` 912, `$Y` 738, `$v` 115, `$F` 72…) — **nie do ruszenia**; pełno-
szerokie `％` 35× i `＆` 10× to prawdziwy tekst. Banki SJIS `0x84`,
`0x85`, `0x86`: **0 wystąpień** (histogram: 0x81: 422 471, 0x82:
925 119, 0x83: 407 596, 0x87: 79, 0x88: 13 121) — prywatne kody
upstream `0x8540..0x85C9` niczego nie nadpisują, a za nimi jest 54
wolnych kodów do `0x85FF` i całe banki dalej. Wniosek: **nie trzeba
przerabiać drukowalnych „specjali"** — polskie znaki dostaną własne
prywatne kody i stemple komórek jak angielskie.

**Audyt narzędzi fontowych upstream (ten sam pinned commit):**
`patch_hwfont.py` 21 887 B (stdlib), `patch_renderer.py` 19 463 B
(stdlib), `patch.py` 3 908 B (→ `patch_hwfont`); `ast.parse` OK ×3,
ścieżki osobiste: brak. Zaimportowane jako batch 2 do vendora (razem
22 pliki / 225 346 B). Mechanizm v2: stemplowanie 12-px liter w komórki
czcionki głównej w RAM (komórka 24×24 4bpp, 288 B; `HW_MAP` ASCII →
`0x8540..`, 69 artów regular + bold = 138 kodów). Sprzeczność w docs
(`CUSTOM_FONT.md`: dostawa pełnoszeroka vs CHANGELOG 0.9.57+: poprawki
half-width w buildach) rozstrzygnie test P3 u właściciela.

Brak wyników runtime; żaden plik w `local/` nie jest dystrybuowany.

## 2026-10-24 — P1/P2: atlas PL, ELF baseline i PL, próbka dialogu; P3: kit testowy

**Potwierdzone (sandbox; szczegóły `docs/FONT_RESEARCH.md`):**

- `tools/gen_pl_atlas.py` (DejaVu Sans, em 20, linia bazowa w rzędzie
  20 komórki 12×24, supersampling 4×, 4 poziomy alfa): atlas 87 glifów
  × 72 B = 6 264 B, SHA-256 `38ec24bd…44202` (wycinek 69: `17d68def…a4add`).
  Tusz PL: wielkie z kreską rzędy 1..20; ogonkowe (Ą Ę ą ę) do rzędu 23 —
  bez przycięć. Waga kroju raczej ciężka; descensory blisko dołu komórki
  (strojenie po screenach P3).
- Problem miejsca rozwiązany bez ruszania vendora: cave 6 320 B przy
  `0x78A070` to plikowe bajty `0x34D770..` (tablica sekcji ELF,
  `e_shoff=0x34D770`, 215×40 B do EOF — loader jej nie używa); sterta
  przesunięta na `0x78CD00` (luka 12 288 B). Nasz `tools/patch_hwfont_pl.py`
  (fork-przez-import vendora) rozszerza PT_LOAD do 8 192 B (koniec pliku
  `0x34F770` ≤ EOF `0x34F908`; koniec vaddr `0x78C070` < `0x78CD00`),
  NART 69→87, NGLYPH 138→174, wpisy tabeli setText dla 18 zarezerwowanych
  bajtów ASCII (`@ # & * + < = > [ \ ] ^ _ \` { | } ~`; `$` nigdy) →
  kody PL `0x8585..0x8596` (bold +87).
- P1 (niemodyfikowany vendor na ELF właściciela): rozmiar bez zmian,
  e_phnum 209→210, **3 847 B** różnic tylko w: nagłówki PT/argumenty
  sterty (`0x1001D9`, `0x3F3FB5`), miejsca hooków (`0x13A7A0`,
  `0x13AB68..`, `0x13B304`, setText `0x20C9B0`), region cave od
  `0x34D770`. `elf_r` SHA-256 `8878af89…ca97`, `elf_p1` `fd54e556…9194`.
- ELF PL vs P1: tylko **879 B** dalej (pola PT_LOAD, stałe w hookach,
  wpisy tabeli, ogon atlasu PL `0x34F018..0x34F524`); vs oryginał
  4 680 B; SHA-256 `7bfc9a20…b7ba`. Rozmiar pliku niezmieniony.
- P2 próbka: wiersz idx 632 (rec 0, off 129008, slot 112 B), mówca
  ヘンケン zachowany; treść = zakodowane bajtami zapasowymi
  „Zażółć gęślą jaźń! / ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż” (105→51 B). Apply:
  1 zapisany / 0 odrzuconych; ponowna ekstrakcja = tekst zamierzony
  co do znaku; `verify_pointers` 121 383/131 977 (91,97%). Diff extentu
  54 538 B w jednym zakresie `0xD..0xD85F` (rekompresja rekordu);
  stage po próbce SHA-256 `c1ca930e…cc63`.
- P3 kit (`tools/build_test_kit.py`, `kit/`): zip 14 plików, 43 748 B,
  SHA-256 `7040ca98…38a4`; test end-to-end w sandboxie na łączonym
  obrazie wirtualnym (ELF@455 + STAGE@1651029, tryb `--no-copy`):
  hashe extentów po patchu = referencje co do bajta (`7bfc9a20…`,
  `c1ca930e…`), ~93 s. Wgrany na Drive `SRWZ`:
  `srwz-pl-font-test-p3.zip` (`1PMiZXRKJWvL9z0ETRGq-3lpENPvhJRAN`,
  43 748 B). Patcher przerywa przy niezgodnych hashach źródła i pisze
  wyłącznie kopię `*_PLTEST`.

**Oczekuje na właściciela:** przebieg bata na prawdziwym ISO + screeny
PCSX2 (okno dialogu z pangramem, menu) + `srwz_patch_log.txt`. Nadal
**brak twierdzeń runtime** — ghost/zawijanie/czytelność ogonków oceni
dopiero dowód z emulatora (P4: strojenie i zamrożenie kodów).

## 2026-10-24 — projekt ZAWIESZONY (decyzja właściciela)

Właściciel zawiesza projekt SRW Z do odwołania („może kiedyś go
wznowimy”); zespół wraca do SRW OE. Stan zaparkowania: wszystko
scommitowane i wypchnięte (przez `e6ac62b`), kit testowy na Drive,
test właściciela niewykonany, brak nierozliczonych zmian lokalnych —
artefakty sandboxa (`local/`: wejścia z hashami, obrazy wirtualne, dist)
są jednorazowe i odtwarzalne z Drive + repo wg `docs/STATUS.md`
(sekcja wznowienia) i `docs/FONT_RESEARCH.md`. Nie kontynuować prac nad
SRW Z bez nowej decyzji właściciela.
