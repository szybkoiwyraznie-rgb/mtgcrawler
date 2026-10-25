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

## Interpretacja (hipoteza, nie fakt)

- Tabele na język to ~940 kB na 24 tabele. Dla 55 misji głównych + 104 opcjonalnych
  + 112 DLC to **za mało na tekst fabularny** → **dialogi siedzą w plikach
  `.lua.txt`**, a tabela `dialog_text` obsługuje raczej krótkie komunikaty i UI.
- Sprawdzenie tego kosztuje dwa pliki (patrz niżej) i jedną komendę — dlatego
  **nie podaję jeszcze żadnej liczby znaków do przetłumaczenia**.

## Czego potrzebuję, żeby to potwierdzić

Dwa bundle z `SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64\`
(razem **6 531 163 B, ~6,2 MiB**; instrukcja dla właściciela:
`docs/OWNER_STEPS_S2.md`):

| bundle | rozmiar | po co |
|---|---|---|
| `1cc7e02ee5711c6ba87a0e364f62198c.bundle` | 940 012 B | wszystkie tabele japońskie → format tabel, liczba stringów, obecność polskich znaków w czcionce |
| `1c12bbab8ed0f62ff22f808ce0138bc1.bundle` | 5 591 151 B | 678 skryptów scenariuszy → prawdziwy tekst fabuły, objętość, znaczniki Lua |

Opcjonalnie (później, do kolumny referencyjnej): `2d69c099…` 948 652 B — tabele
angielskie.

## Odtworzenie

```bash
python3 tools/scan_catalog.py --catalog catalog.json            # surowe adresy
python3 tools/map_catalog.py --catalog catalog.json \
        --listing listing_sizes.txt --out mapping.json          # adres → bundle
```

`mapping.json` zostaje w `local/` (ignorowane) — do repo idą tylko liczby i nazwy
bundli, nigdy zawartość gry.

## Ograniczenia tej analizy

- Mapowanie opiera się na `dependencyKeyIndex` wpisu: adres assetu → klucz bundla
  → ścieżka bundla. Zweryfikowane rozmiarami z listingu właściciela (wszystkie
  19 160 bundli istnieje poza jedną syntetyczną kotwicą), ale to wciąż
  rekonstrukcja formatu, nie oficjalna dokumentacja.
- Katalog bazowy opisuje grę bazową. Teksty dodatków są w osobnych katalogach
  (`Dlc1`, `Dlc2`, `ExpansionPack`, `AnniversaryExpansionPack`, …) i będą
  potrzebne dopiero po potwierdzeniu metody na bazie.
- Niczego nie uruchamiałem w grze: `runtime_tested` pozostaje `false`.
