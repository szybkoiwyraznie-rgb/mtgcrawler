# SRW Y — częściowy patch PL1 (pierwsza zwrotka tłumacza)

To jest **częściowy patch** z pierwszą częścią polskiego tłumaczenia SRW Y,
odesłaną przez tłumacza jako `Y_PL1.zip` na Drive (id `1TaaVxCPfzYLwRluQLnU6QsQNXe0wFBIt`).

## Co zawiera

| plik | elementy | PL wypełnione | PL puste |
|---|---:|---:|---:|
| `PL/sceny/odcinek-00_a.md` | 7 761 | 2 701 | 2 885 |
| `PL/widoki/00_postacie.md` | 1 910 | 1 874 | 1 |
| `PL/widoki/01_roboty_i_bronie.md` | 1 248 | 1 192 | 0 |
| `PL/widoki/02_cytaty_bitewne.md` | 34 656 | 14 776 | 17 639 |
| `PL/widoki/03_umiejetnosci.md` | 2 694 | 2 150 | 0 |
| `PL/widoki/04_przedmioty_i_slowa.md` | 484 | 475 | 4 |
| `PL/widoki/05_interfejs.md` | 1 635 | 1 528 | 0 |
| `PL/widoki/06_teksty_misji.md` | 1 360 | 1 238 | 0 |
| `PL/widoki/07_swiat.md` | 318 | 310 | 0 |
| `PL/widoki/08_pokrewne.md` | 35 | 35 | 0 |
| **RAZEM** | **52 101** | **26 279** | **20 529** |

To jest **częściowy** patch: nie wszystkie elementy mają `PL:`. Puste `PL:` permanecą do uzupełnienia przez tłumacza w kolejnych zwrotkach.

## Format

Pliki są w formacie pakietu tłumacza (`plik_dla_tlumacza_v8.zip`): numerowany element, `limit:`, kolumna `EN:` (odniesienie) i wypełniona `PL:` (polski tekst). Inline tokeny (`$c`, `[p1:]`, `[r1:]`, `[p2:]`, `[i:]`, `[protagonist]`) są zachowane dokładnie.

## Jak użyć

1. Te pliki to **źródło tłumaczenia**, nie patch do gry — nie nakładać ich na bundle'y gry bezpośrednio.
2. Następnym krokiem jest import przez `tools/pl_import.py` (wymaga prywatnych źródeł S6 w `local/s6/` — poza repo).
3. Po zaimportowaniu i wyprodukowaniu patcha (bundle'y z polskim tekstem), patcher v2 (`SRW_Y_PATCHER_v2.zip`) instaluje go w grze.

## Źródło

- `Y_PL1.zip` na Drive: id `1TaaVxCPfzYLwRluQLnU6QsQNXe0wFBIt`, SHA-256 `eabb640094f076809949b4fd17c030015db1781dfc5527bb972bf768a495a9b9`, 7 794 906 B.
- Szczegóły statystyczne: `MANIFEST.txt` obok tego pliku.
