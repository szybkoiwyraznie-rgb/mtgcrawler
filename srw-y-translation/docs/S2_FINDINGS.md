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

## Co zostaje

**A. Statyczne — wyczerpane w tym, co tanie.** Zostałyby dwie drogi, obie drogie
i o niepewnym wyniku: (1) deasemblacja metod `SeekableAesStream`/`CustomAssetBundleResource`
w `GameAssembly.dll`, żeby zobaczyć, skąd biorą się `password` i `salt` — to
praca z deasemblerem IL2CPP, nie „jeszcze jedna próba”; (2) przesiewanie
nieczytelnych (bajtowych) obszarów metadanych jako kluczy — 56 mln okien, ~15
min, ale niska szansa, bo metadane trzymają nazwy i typy, nie sekrety.

**B. Runtime — bez klucza.** Gra sama odszyfrowuje bundle w pamięci. Zamiast
klucza można więc **przechwycić jawny tekst** w trakcie działania gry:
podpiąć się pod `SeekableAesStream.Read` (albo pod samo ładowanie bundla) i
zapisać to, co wychodzi — a potem analizować offline naszymi narzędziami.

To jest obecnie **najbardziej obiecująca droga** i jedyna, która nie zależy od
odgadnięcia hasła. Ma jednak dwa warunki: trzeba ją napisać i uruchomić na
komputerze właściciela (Windows), a ja muszę zaprojektować ją tak, żeby nie
wymagała kompilatora C# — którego w moim środowisku nie ma. Realny kandydat to
Frida (jest na PyPI, czyli w zasięgu) z mostkiem do IL2CPP, sterowana krótkim
skryptem. **Nie obiecuję, że zadziała, dopóki tego nie sprawdzę** — ale to
następna rzecz, którą zrobię, zamiast dalej zgadywać klucz.

## Interpretacja (hipoteza, nie fakt)

- Tabele na język to ~940 kB na 24 tabele. Dla 55 misji głównych + 104 opcjonalnych
  + 112 DLC to **za mało na tekst fabularny** → **dialogi siedzą w plikach
  `.lua.txt`**, a tabela `dialog_text` obsługuje raczej krótkie komunikaty i UI.
- Sprawdzenie tego kosztuje dwa pliki (patrz niżej) i jedną komendę — dlatego
  **nie podaję jeszcze żadnej liczby znaków do przetłumaczenia**.

## Czego potrzebuję teraz

**Niczego.** Wszystkie pliki, które miały sens na tym etapie, są już w `local/`:
dwa bundle (6 531 163 B), katalog (41 543 062 B), metadane (18 909 544 B) i
`GameAssembly.dll` (74 865 152 B). Dalsza praca — zaprojektowanie przechwycenia
tekstu w runtime — jest po mojej stronie i nie wymaga wysyłania kolejnych
plików gry.

Jeśli ta droga będzie wymagała uruchomienia czegoś na Twoim komputerze,
dostaniesz **osobną, gotową do wklejenia instrukcję** — tak jak poprzednie.

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
