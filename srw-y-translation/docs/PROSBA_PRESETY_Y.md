# PROŚBA — 109 bundli z brakującymi rozstawieniami (`SRW_Y_PRESETY_PROSBA.zip`)

Dokumenty powiązane: [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md),
[`PROSBA_GRAFY_Y.md`](PROSBA_GRAFY_Y.md). To **trzeci, osobny kit**. Dwa
wcześniejsze zwroty — `SRW_Y_ENCYKLOPEDIA.zip` (11 assetów) i
`SRW_Y_GRAFY.zip` (366 grafów) — zostały już przetworzone.

## Wynik analizy `SRW_Y_GRAFY.zip`

| pomiar | wynik |
|---|---:|
| bundli grafów | 366 / 12 650 148 B |
| obiekty `ScriptGraphAsset` | 1 570 (399 nazw) |
| jednostki `TalkStartUnit` | 7 410 |
| połączenia sterowania | 67 214 |
| rozgałęzienia `If` | 1 382 |
| zakresy z wywołaniami zdarzeń | 1 089 |
| zakresy o jednoznacznym, statycznym ciągu | 668 |
| **rozwiązane wskaźniki presetów** | **0 / 91** |
| obiekty `*_preset` | 0 |

Grafy są tym, na co wskazuje `script_file` w kompozycji misji; 91 brakujących
wskaźników to `preset_file`. Żaden z 91 docelowych plików CAB nie występuje
wśród 366 nazw plików serializowanych, żaden z 91 PathID-ów nie występuje
wśród obiektów, a zależności AssetBundle nie wskazują tych CAB-ów. **Nie
wolno z tego dopisywać rozstawień z innych misji.**

## Skąd wiemy, których plików potrzeba

Katalog Addressables ma jawne adresy presetów: `m1002_0000100a_preset`,
`m1003_0202200a_preset`, … oraz wersje `_Patch`. Trzy misje
(`m4003_0202500`, `m4020_0200230`, `m5003_0107330`) zamiast `_preset`
używają adresów `_Normal` i `_Hard`. `bundle_for` rozwiązuje każdy adres
do konkretnego bundla, a `listing_sizes.txt` podaje folder i rozmiar.
Wynik: **109 bundli, 994,215 B** (ok.
971 KB); żadnego nie ma w dziewięciu dotychczasowych
archiwach.

| folder w `StreamingAssets` | plików |
|---|---:|
| `BonusMission` | 14 |
| `Dlc1` | 16 |
| `Dlc2` | 20 |
| `EarlyPurchase` | 2 |
| `ExpansionPack` | 30 |
| `SeasonPassBonus` | 2 |
| `aa/StandaloneWindows64` | 25 |

Pełna lista z adresami i misjami leży w
`data/script_graph_evidence.json` → `missing_presets.bundles`
(pieczęć indeksu `8dd21bf55273…`, paczki grafów
`8c6451349ef1…`).

## Co uruchomić

**`SRW_Y_PRESETY_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). W środku `URUCHOM_TO.bat`, `ZBIERZ_PRESETY.ps1`,
`CZYTAJ_TO.txt`. Format identyczny jak poprzednie kity.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_PRESETY.zip`** — wgraj go na ten sam
   folder na Drive i daj znać.

## Co zrobię po otrzymaniu

1. Zweryfikuję SHA-256 paczki i rozmiary 109 plików.
2. Odszyfruję 109 bundli i sprawdzę **dokładne pary (CAB, PathID)** dla 91
   wskaźników z `reading_index.py`. Jeśli któryś pozostanie, podam jego
   liczbę zamiast zgadywania.
3. Uzupełnię rozstawienia w `deployment.md`, przebuduję czytanki i
   zaktualizuję receipt (`structural_issues` powinien spaść do zera).
4. Chronologia wywołań warunkowych pozostanie `false`, dopóki grafy nie
   dadzą pełnego dowodu — 668 jednoznacznych zakresów z 1 089 to za mało.
