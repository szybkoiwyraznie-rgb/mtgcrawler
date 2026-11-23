# Etykiety „Efekt umiejętności” w sysmes.bin — skrócenie do 18 komórek (2026-11-22)

## Zgłoszenie właściciela

Podczas gry na ekranie widać za długi tekst `Efekt umiejętności/części`.
Właściciel wybrał skróconą formę **„Efekt umiejętności”** (pełna forma, bez końcówki „/części”).

## Pomiar

| Element | Wartość |
| --- | --- |
| Docelowy napis PL (bez tokenów) | `Efekt umiejętności` |
| Szerokość nowego napisu (komórki ramki 8x14) | **18** |
| Szerokość starego napisu (bez tokenów) | 25 |
| Napis JP bez tokenów (`特殊ｽｷﾙ・\u000f0ｰﾂ効果`) | 17 komórek (17 bajtów CP932) |
| Tokeny | `＠4` (czworo wersetów: 2 wiersze z tokenem + 2 bez) |
| Granica pikselowa | **NIE zmierzona** — nie ma zrzutu ze skróconą etykietą; limit 18 komórek mierzy plan, nie ekran |

Zakres obejmuje wyłącznie cztery wiersze `sysmes.bin` z tą samą etykietą w polskim pakiecie (`pakiet_PL/polish.jsonl`): `50348` i `50444` z tokenem `＠4`, `50351` i `50447` bez niego.

## Plan

`config/pl/ui-skill-effect-label-2026-11-22.json` (SHA-256 `b00f1945…`), **4 zmiany**, wszystkie powiązane ze źródłem przez `source_sha256`:

| # | ID | Przed | Po |
| --- | --- | --- | --- |
| 1 | `sysmes:configst.cpk/sysmes.bin:50348` | `＠4Efekt umiejętności/części` | `＠4Efekt umiejętności` |
| 2 | `sysmes:configst.cpk/sysmes.bin:50351` | `Efekt umiejętności/części` | `Efekt umiejętności` |
| 3 | `sysmes:configst.cpk/sysmes.bin:50444` | `＠4Efekt umiejętności/części` | `＠4Efekt umiejętności` |
| 4 | `sysmes:configst.cpk/sysmes.bin:50447` | `Efekt umiejętności/części` | `Efekt umiejętności` |

Tokeny, liczba linii i długość pola zachowane (2 wiersze z `＠4` zachowane tokeny bez zmian, 2 bez tokenów); `max_cells: 18` na każdą zmianę.

## Zmiany i weryfikacja

- Powiązane źródłowo, nakładane przez `tools/pl_ui_corrections.py` (asertywnie: pliki + hash + ID + tekst „przed”).
- Snapshot PL: `data_sha256` `66775517…` → `642ad41e…` (28. wpis `owner_ui_corrections`, `runtime_tested: false`); diff w `polish.jsonl` to **dokładnie 4 linie**; `entries` pozostaje 108 929.
- Materializacja od zera (`R.materialize`) po nałożeniu: 4 wiersze wyglądają jako `＠4Efekt umiejętności` / `Efekt umiejętności`; żaden inny wiersz w pakiecie nie zawiera dłuższej formy (AUDYT: `grep "Efekt umiejętności/części"` → 0 trafień w pakiecie PL).
- `tests/test_pl_skill_effect_label.py` (plan i status snapshota).
- **Brak testu PPSSPP** — nie ma zrzutu ekranu; `runtime_tested` pozostaje `false`.
- Żaden inny wiersz pakietu PL nie został zmieniony; pole `EN_LENGTH_EXCEPTIONS.md` o nadwyżkach (postój w wierszach tabeli) nie jest dotknięte — etykieta ekranowa jako `sysmes.bin` nie ma własnego zmierzonego slot-boardu w tym dokumencie.

## Ryzyko szczątkowe

Ekran, na którym `Efekt umiejętności` ma się zmieścić, nie został zmierzony. Limit planu (18 komórek = szerokość nowego napisu) nie zagwarantuje pojemności ekranu; jeśli na ekranie etykieta nadal wykracza poza pole, należy obniżyć ją w kolejnym planie (pomiar na zrzucie ekranu) — mechanizm i test już istnieją.

## Regresja CI po wdrożeniu planu (naprawiona 2026-11-23)

Plan v4.14 dodał 4 edycje istniejących wierszy, ale nie trafił na listę
cofanych w `tests/pl_history.py`. Przez to `test_gai_pilot_label` i
`test_missing_charalist_full_names` (odtwarzają starsze snapshoty PL) padały
na skrótach `6517ec17…`≠`32d914cd…` i `d3c4b167…`≠`a5537ab7…`, a krok CI
`Test tools` był czerwony na `main` (run `45283102550`) i w PR #42.
Naprawa: plan `ui-skill-effect-label-2026-11-22.json` dopisany do
`REWIND_EDITS`; pakiet, snapshoty i ten plan pozostają bez zmian.
