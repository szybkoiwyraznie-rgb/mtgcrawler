# S2 — gdzie jest tekst (wynik odczytu katalogu Addressables)

Stan: **2026-10-25**. Wejście: `catalog.json` od właściciela (Drive `SRW/SRWY`,
plik `1cSFIutg4pfL_KGimi4tab4_j29uC3s7N`), **41 543 062 B**, SHA-256
`12c17bf97478eca66f2aa6066c0a14974639443d0e9d79af3355abdd895273b4`,
build hash `4a04a7429fecea239c5f81685d298368`. To **indeks nazw assetów**, nie
treść gry — żadnego dialogu w nim nie ma.

## Co mówi katalog

| | |
|---|---|
| locator | `AddressablesMainContentCatalog` |
| adresy (klucze) | **187 039** |
| z tego klucze bundli | 82 872 (każdy bundle ma po kilka aliasów: ścieżka, nazwa, hash) |
| adresy assetów rozwiązane do bundla | **104 118** |
| różnych bundli obsługujących assety | **19 160** |
| nierozwiązane | 49 — to assety wbudowane Unity i biblioteki CriMana na inne platformy (`Color Gradient Presets/…`, `CriMana/Android/…`), nie zawartość gry |
| wpisy bez tekstu | 2 (klucze o typie, którego nie zgadujemy) |
| walidacja | wszystkie rozwiązane bundle istnieją w listingu właściciela **poza jednym**: `cri_addressables_anchor_group_assets_cri_addressables_dummy_anchor.bundle` — to syntetyczna „kotwica” CriWare, nie plik z treścią |

Providery w katalogu: `CriWare.Assets.CriResourceProvider`,
`Com.BBStudio.SRTeam.Data.CustomAssetBundleProvider`,
`BundledAssetProvider`, `LegacyResourcesProvider`. Czyli tekst nie jest
w CriWare — audio i filmy są.

## Dwa systemy tekstu

### 1. Tabele Unity Localization (UI, system, nazwy)

24 tabele × 6 języków = **144 adresy na język**. Tabele:
`dialog_text`, `mission_title`, `mission_detail`, `mission_outline`, `prologue`,
`system_text`, `tutorial_text`, `stgmemory`, `dic_text_name/pilot/robot/word`,
`pilot_name`, `robot_name`, `weapon_name`, `ip_name`, `voiceactor`,
`spirit_command`, `skill_active`, `skill_program`, `active_ability`,
`power_parts`, `custom_bonus`, `ace_bonus`, `assist_text`, `battle_voice`,
`option_parts`, `strategypart_pilotmess`, `landscape_name`, `areapoints`,
`text_EndMessTitle`, `font`, `ICE_operation`.

Bundel na język (język japoński i angielski; pozostałe analogicznie):

| język | bundle | rozmiar | co zawiera |
|---|---|---|---|
| ja-JP | `1cc7e02ee5711c6ba87a0e364f62198c.bundle` | 940 012 B | `dialog_text_ja-JP`, `mission_title`, `mission_detail`, `mission_outline`, `prologue`, `system_text`, `tutorial_text`, `stgmemory` |
| ja-JP | `08b8a348…` / `af95e769…` / `cfc11e93…` / `59feeef1…` | 80 790 / 78 413 / 61 099 / 40 230 B | tabele dodatków DLC3 / DLC4 / DLC1 / DLC2 |
| ja-JP | `a1afc008…` | 2 251 B | zaślepka łatki |
| en-US | `2d69c099bfdf0e252dabe84dbbba11df.bundle` | 948 652 B | analogiczny zestaw po angielsku |
| en-US | `403cc7e0…` / `da72de49…` / `12f735c0…` / `70bda235…` / `f1ba80f5…` | 79 102 / 79 000 / 58 520 / 42 098 / 2 273 B | DLC3 / DLC4 / DLC1 / DLC2 / zaślepka |

### 2. Skrypty scenariuszy (`.lua.txt`)

Pod `Assets/Datas/Scenario/{jp,en,cn,…}/` jest **4 131 plików** typu
`cse20_0001_0000310a_dlgev.lua.txt` w **30 bundlach**, razem **32 267 543 B**.
Sześć największych bundli ma po 605–678 plików i 4,7–5,6 MB.

## Blokada: bundle są zaszyfrowane

Oba bundle dotarły (Drive `SRW/SRWY`), rozmiary zgadzają się co do bajtu z
listingiem:

| bundle | bajty | SHA-256 |
|---|---|---|
| `1cc7e02ee5711c6ba87a0e364f62198c.bundle` | 940 012 | `a209190e…a9c1` |
| `1c12bbab8ed0f62ff22f808ce0138bc1.bundle` | 5 591 151 | `5ee05187…9a0d` |

**Nie zawierają nagłówka `UnityFS`.** Dowody z samych plików:

- brak sygnatury `UnityFS` / `UnityWeb` / `CAB-` w całym pliku;
- entropia **8,0 bita/bajt w każdym oknie 64 KiB**, wszystkie 256 wartości
  bajtów występują;
- **zero powtórzonych bloków 16-bajtowych** (wyklucza ECB);
- XOR obu plików daje entropię 7,997 (0,43 % zer) → **każdy plik ma własny
  strumień klucza**, więc to nie jest stały XOR ani stały keystream;
- brak czytelnych fragmentów (`cse20`, `dialog_text`, `Localization`, japoński
  UTF-8) — nic.

`UnityPy` otwiera pliki bez błędu i widzi **0 obiektów**, co jest zgodne z
powyższym. W katalogu jest własny provider
`Com.BBStudio.SRTeam.Data.CustomAssetBundleProvider` — czyli Bandai zaszyfrowało
całe bundle i odszyfrowuje je we własnym kodzie przy ładowaniu. Nie jest to
UnityCN (ten zaczyna się od `#$unity3dchina!@`, a nasze pliki są losowe od
pierwszego bajtu), nie jest to CPK/Blowfish z SRW 30/V.

**Skutek:** dopóki szyfrowanie nie zostanie zdjęte, nie da się policzyć znaków
ani przygotować łatki na plikach. To nie jest drobiazg — to główne ryzyko całego
projektu.

## Mechanizm szyfrowania — zidentyfikowany [confirmed]

`GameAssembly.dll` dotarł (74 865 152 B, SHA-256 `d96e91f5…68bb`) i jest to
typowy obraz IL2CPP: sekcje `.text`, `il2cpp` (50 MB kodu), `.rdata`, `.data`.
Nazwy z kodu gry siedzą w metadanych, więc to tam szukałem śladów — i są:

| ślad | co znaczy |
|---|---|
| `Assets\Scripts\Addressable\SeekableAesStreamcs.cs` | własna klasa **strumienia AES z możliwością przewijania** („seekable”) — dokładnie to, czego trzeba, by grać bundle bez rozpakowywania całości |
| pola tej klasy: `baseStream`, `password`, `salt`, `buffer`, `count`, `streamPos`, `Cipher`, `aes`, `encryptor` | klucz **nie jest stałą** — jest wyprowadzany z **hasła i soli** |
| `Com.BBStudio.SRTeam.Encryption|EnctyptionInfo` z polami `KeySize`, `BlockSize`, `Mode`, `IV`, `Padding` | konfiguracja AES (rozmiar klucza, tryb, IV, dopełnianie) |
| `Rfc2898` / `PasswordDeriveBytes` w metadanych | standardowe .NET-owe KDF-y są w grze obecne, czyli PBKDF2 jest realną drogą wyprowadzenia klucza |
| `AES_KEY`, `IV_SIZE`, `ClassSalt`, `salt`, `password` jako nazwy symboli | potwierdzają obraz: klucz + sól + IV |
| `Assets\Scripts\Addressable\CustomAssetBundleProvider.cs` | klasa, która podmienia standardowe ładowanie bundli — stąd własne szyfrowanie zamiast `UnityFS` |

To wyjaśnia wszystko, co zmierzyłem wcześniej: brak nagłówka `UnityFS`, entropię
8,0, brak powtarzalnego strumienia i brak trafienia przy testowaniu literałów
jako **kluczy** — bo literały to nie klucze, tylko (być może) hasło i sól, z
których klucz dopiero powstaje.

**Konsekwencja praktyczna:** żeby odczytać bundle bez gry, trzeba znać **parę
hasło + sól** oraz tryb AES. To zawęża atak, ale nie czyni go łatwym: hasło
i sól mogą być równie dobrze tablicami bajtów w kodzie, jak i napisami.

## Czego już próbowałem (i co to wyklucza)

Wszystko offline, na dwóch prawdziwych bundlach. **Każda próba zakończona
negatywnie — ale negatywny wynik też jest wiedzą: wyklucza całe klasy rozwiązań.**

| próba | skala | wynik |
|---|---|---|
| literały z `global-metadata.dat` jako klucze | **2 249 429** kandydatów × 13 konstrukcji (AES-ECB, CBC z IV zerowym / z pliku / z klucza, CTR w czterech układach licznika, RC4, ChaCha20 w dwóch układach, XOR) | brak trafienia (`UnityFS` się nie pojawia), 9 min 41 s |
| klucz jako skrót literału (MD5 / SHA-1 / SHA-256, też hex) | **3 836 487** kandydatów na bundlu tabel japońskich | brak trafienia, 8 min 20 s |
| proste maskowanie nagłówka | 256 × XOR, 256 × dodawanie, 256 × odejmowanie, zamiana półbajtów, odwrócenie bitów, odwrócenie pliku, negacja | brak `UnityFS` |
| kompresja / kontener pod spodem | zlib, gzip, bz2, xz/LZMA, LZ4, zstd — każdy offset w pierwszych 4096 B | nic nie dekompresuje się do `UnityFS`/`CAB-` |
| powtarzający się strumień klucza | współczynnik równych bajtów dla przesunięć 1…4096 | maks. 0,0049 przy losowym 0,0039 → **brak powtarzalności**, strumień jest ciągły |
| klucz jako tablica bajtów w `GameAssembly.dll` | **61 201 575** okien 16/24/32 B, **każde przesunięcie** (bez zaokrągleń) w sekcjach `.rdata`, `.data`, `.pdata`, `.fptable`, `.reloc` (16,6 MB danych) | brak trafienia, 15 min 34 s |
| klucz wyprowadzony z nazwy bundla (PBKDF2 i skróty) | 4712 kombinacji: nazwa/hash jako hasło lub sól × 12 stałych projektu × iteracje 1/1000/10 000 × SHA-1/SHA-256 × 16/32 B | brak trafienia |

Wniosek po wszystkich próbach: to nie jest maskowanie, kompresja ani szyfr z
powtarzalnym kluczem. Klucz **nie jest** też ani literałem, ani skrótem literału,
ani gotową tablicą bajtów leżącą w sekcjach danych `GameAssembly.dll`. Zostaje
dokładnie to, co wynika z identyfikacji mechanizmu: **para hasło + sól** (lub
hasło + sól same będące tablicami budowanymi w kodzie) i konkretny tryb AES.
Statycznie tego nie rozwiązałem i nie będę udawał, że jest blisko.

## Co zostaje — droga runtime, zbudowana

Skoro klucza nie ma w plikach, sięgamy po to, co gra **musi** mieć: odszyfrowany
tekst w pamięci. Właściciel potwierdził Pythona 3.12.9, więc nie potrzebujemy
kompilatora C#.

- `tools/mem_carve.py` — **bez żadnych bibliotek** (tylko `ctypes`), **tylko do
  odczytu** (`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`): przegląda pamięć
  procesu, szuka nagłówków `UnityFS` i `CAB-`, parsuje je, wycina dokładnie tyle
  bajtów, ile deklaruje nagłówek, i **ponownie parsuje wynik**, żeby nie nazwać
  sukcesem czegoś, co się nie otwiera. Raport zawiera **tylko liczby i nazwy**
  plików — bez treści gry, więc można go wysłać.
- `tools/read_carve.py` — otwiera wycięte pliki (UnityPy) i mierzy tekst:
  znaki, linie, znaki japońskie, znaki zastępcze (dowód złego kodowania).
- Instrukcja dla właściciela: `docs/OWNER_STEPS_S3.md`.

**Uczciwie:** narzędzie przeszło self-test i przebieg na zsyntetyzowanym zrzucie
(18 testów na parsowaniu i wycinaniu), ale **nie było jeszcze uruchomione na
prawdziwej grze** — to wymaga komputera właściciela. Jeśli okaże się, że gra nie
trzyma w pamięci całych bundli (tylko bloki), raport to pokaże liczbami, a wtedy
zostaje podpięcie się do funkcji odszyfrowującej.

## Interpretacja (hipoteza, nie fakt)

- Tabele na język to ~940 kB na 24 tabele. Dla 55 misji głównych + 104 opcjonalnych
  + 112 DLC to **za mało na tekst fabularny** → **dialogi siedzą w plikach
  `.lua.txt`**, a tabela `dialog_text` obsługuje raczej krótkie komunikaty i UI.
- Sprawdzenie tego kosztuje dwa pliki (patrz niżej) i jedną komendę — dlatego
  **nie podaję jeszcze żadnej liczby znaków do przetłumaczenia**.

## Czego potrzebuję teraz

**Żadnych plików gry.** Wszystko, co da się wyczytać z plików, jest już
wyczytane. Potrzebny jest **jeden przebieg na komputerze właściciela**, przy
działającej grze: `docs/OWNER_STEPS_S3.md` (self-test → odczyt na ekranie
tytułowym → odczyt z dialogiem na ekranie → dwa małe raporty JSON).

## Odtworzenie

```bash
python3 tools/scan_catalog.py --catalog catalog.json            # surowe adresy
python3 tools/map_catalog.py --catalog catalog.json \
        --listing listing_sizes.txt --out mapping.json          # adres → bundle
```

`mapping.json` zostaje w `local/` (ignorowane) — do repo idą tylko liczby i nazwy
bundli, nigdy zawartość gry.

Próby złamania szyfrowania (wszystkie na plikach z `local/`, nic nie trafia do
repo):

```bash
python3 tools/keyhunt.py --bundle local/bundles/*.bundle \
        --candidates local/meta/global-metadata.dat --derive
python3 tools/probe_assembly.py --dll local/meta/GameAssembly.dll \
        --bundle local/bundles/1cc7e02e*.bundle --alignment 16
```

## Ograniczenia tej analizy

- Mapowanie opiera się na `dependencyKeyIndex` wpisu: adres assetu → klucz bundla
  → ścieżka bundla. Zweryfikowane rozmiarami z listingu właściciela (wszystkie
  19 160 bundli istnieje poza jedną syntetyczną kotwicą), ale to wciąż
  rekonstrukcja formatu, nie oficjalna dokumentacja.
- Katalog bazowy opisuje grę bazową. Teksty dodatków są w osobnych katalogach
  (`Dlc1`, `Dlc2`, `ExpansionPack`, `AnniversaryExpansionPack`, …) i będą
  potrzebne dopiero po potwierdzeniu metody na bazie.
- Niczego nie uruchamiałem w grze: `runtime_tested` pozostaje `false`.

## S3 — the first real run on the owner's machine (2026-10-25)

Two live scans with `tools/mem_carve.py`, game running, read-only access. Raw
reports (with the carved files) are the owner's; the numbers below are from those
reports and from opening every carved file with UnityPy here.

| | run 1 — title screen | run 2 — dialogue on screen |
|---|---|---|
| image / pid | `SUPER ROBOT WARS Y.exe` / 63044 | `SUPER ROBOT WARS Y.exe` / 63044 |
| memory scanned | 1,834,594,304 B in 1,013 regions | 2,190,172,160 B in 973 regions |
| `UnityFS` markers | 571 | 795 |
| `CAB-` markers | 8,971 | 14,019 |
| `cse20_` (scenario names) | 580 | 641 |
| `dialog_text` (localisation) | 27 | 27 |
| `StandaloneWindows64` | 70 | 57 |
| kana (UTF-16LE runs) | 91,846 runs · **628,553 chars** · longest 192 | 93,277 runs · **636,764 chars** · longest 192 |
| carved files | 244 bundles · 2,210,644 B · largest 28,151 B | 348 files · 3,575,972 B · largest 275,626 B |
| incomplete carves | 0 | 0 |

**The carver works.** Every carved file re-parsed before being claimed, and the
sizes are sane.

**Whole-bundle carving does not reach the text.** Opening all 592 carved files
with UnityPy: 587 `AssetBundle`, 826 `MonoBehaviour`, 1,310 `MonoScript`, 266
`Texture2D`, 317 `Sprite`, 49 `Material`, 35 `Shader`, 30 `AnimationClip`, 10
`AnimatorController`, 4 files unreadable — and **zero `TextAsset`s, zero
characters of Japanese**. What is resident in memory as a whole bundle is the
small UI/prefab bundles (2 KB – 275 KB). The bundles that carry text (the 940,012 B
ja-JP localisation table, the 33.5 MB of scenario scripts) are streamed through
`SeekableAesStream` in blocks and are never contiguous in memory, so a
whole-bundle carver cannot see them.

**The text itself is in memory**, though: 628,553 kana characters at the title
screen and 636,764 in a dialogue scene, in 91,846 and 93,277 runs. That is the
number to build on — it says the Japanese is plaintext in the process and only
needs harvesting, not a key.

**A real bug found by the run:** the reports list bundle sizes of 4,294,967,141 B,
4,294,967,129 B, … Those are false `UnityFS` headers in random bytes that passed
validation (`size <= 8 GiB` was far too generous). Because `carve_plan` skips any
hit that starts before the previous hit's declared end, one false header swallowed
**every subsequent hit in that 8 MB chunk** — which is why 14,019 `CAB-` headers
produced exactly **zero** carved serialized files. The header parse now requires a
plausible editor revision (`2021.3.0f1`) and caps a bundle at 512 MB.

**New in `tools/mem_carve.py`:** a string harvest that runs alongside the carve.
It decodes each chunk as UTF-16LE and as UTF-8 (only when kana lead bytes are
present, which keeps the cost down), anchors on kana runs, grows each run over
kanji/kana/full-width/ASCII neighbours up to 400 characters, deduplicates, and
writes `strings_utf16.txt` and `strings_utf8.txt` into the output folder. The
report keeps **counts only** (`unique`, `chars`, `truncated`); the text itself
never enters the report. `--no-text` turns the harvest off.

Next run therefore answers the volume question directly: how many unique Japanese
strings, and how many characters, the running game holds.

## S3, second run: the strings are real, the containers are not

`carve2.zip` (12,704,151 B) — same two scans, now with the string harvest.

| | run 1 — title screen | run 2 — dialogue scene |
|---|---|---|
| memory scanned | 1.68 GB in 980 regions | 2.09 GB in 946 regions |
| `UnityFS` / `CAB-` | 560 / 7,836 | 803 / 13,628 |
| kana in memory | 90,671 runs, 613,502 chars | 92,413 runs, 623,507 chars |
| **UTF-16 strings** | **17,035 unique, 308,982 chars** | **17,931 unique, 340,375 chars** |
| **UTF-8 strings** | **9,131 unique, 625,119 chars** | **8,769 unique, 639,501 chars** |
| carved | 246 files, 19,221,592 B | 351 files, 11,715,387 B |

**The harvested text is genuine game text**, and it is exactly what a translator
needs: pilot-ability descriptions (`ユニットコマンド「パーツ」で使用すると…`),
spirit commands, tutorial paragraphs, UI labels, voice-cast credits
(`… 斎藤千和　モコナ …`), Unity UI draw commands (`{Inst_BG_PlaceWindowDraw, 261,
0, BgSizeHeightx2, …}`). Median string length is 14–16 characters, the longest
harvested line is 400 (the cap).

**What the runs also proved is a limit:** four carved `.assets` files (8.1, 8.3,
4.8 and 4.1 MB) have **invalid** `CAB-` headers — garbage instead of the 16-hex
name, version 0 — so they are false hits, not serialized files. They were
nevertheless 8 MB of memory containing thousands of kana runs: real text, wrong
container. And even the genuine hits are stubs: `file_size` says 33,554,496 B
while only 8,087,127 B were carved, i.e. **the object always ends outside the 8 MB
chunk that held its header**.

Both problems are fixed in `tools/mem_carve.py`:

- **`read_pieces` / `read_process`:** carving no longer slices the chunk — it
  reads the declared size straight from the process address, in 1 MB pieces,
  across region boundaries. A file bigger than the chunk now arrives whole, and a
  genuinely unreadable tail shows up as `complete: false` with `size` <
  `declared_size` instead of silently looking fine.
- **Strict `CAB-` validation:** the 16 bytes after the marker must be hex, version
  must be 1–32, `data_offset >= 48`, `metadata_size >= 32`. The four garbage
  blobs would now be rejected.
- **Duplicate suppression by SHA-256**, so a header seen in two overlapping
  chunks is written once.
- **Rich region dumps:** a chunk holding ≥ 2,000 kana characters is written out
  whole (`region_NN_XXXXXXXX.bin`, at most four) because that is the closest thing
  to a decompressed text file — it shows the structure around the strings (Lua
  code, keys, indices) that a flat string list loses.

Tests **99/99** (piece assembly, short-read truncation, non-hex and hex `CAB-`
names).

## The unfinished half of S3: how a translation gets back in

Reading is solved in principle — the text is plaintext in memory and can be
harvested. **Writing is not.** The bundles on disk are AES-encrypted by
`SeekableAesStream` and the key (password + salt through `Rfc2898`) has not been
recovered: 61.2 M candidate keys from `GameAssembly.dll` and 4,712 name-derived
KDF combinations all failed. Without the key a re-encrypted bundle cannot be
produced, so the install path has to be one of:

1. **key recovery** (then a normal bundle patch, identical in shape to the OE and
   SRW Z kits),
2. **runtime text replacement** — an external companion that patches the loaded
   strings in place while the game runs (no key, but the target string must not
   grow, which JP→PL violates),
3. **an IL2CPP mod** — needs a .NET toolchain on the owner's machine, which the
   owner does not have.

This is the decision the next measurement has to inform, and it is why rich region
dumps matter: they show whether full scenario scripts (with their `lua.txt` name
and structure) ever exist contiguously, which decides between (1) and (2).
