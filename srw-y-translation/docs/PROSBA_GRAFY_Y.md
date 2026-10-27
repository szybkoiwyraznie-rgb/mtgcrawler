# PROŚBA — 366 bundli grafów zdarzeń (`SRW_Y_GRAFY_PROSBA.zip`)

Dokumenty powiązane: [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md),
[`PROSBA_ENCYKLOPEDIA_Y.md`](PROSBA_ENCYKLOPEDIA_Y.md). To **osobny, drugi kit** —
pierwszy zbiera 11 assetów właścicielskich encyklopedii i nie ma z tym nic wspólnego.

## Po co to

Dwa otwarte punkty czytanek mają jedno źródło:

1. **91 nierozwiązanych wskaźników PPtr** (82 misje) — w `deployment.md` brakuje
   rozstawień jednostek. Pomiar: 91/91 takich kompozycji ma `script_file`
   typu `Unity.VisualScripting.ScriptGraphAsset`. Te grafy leżą w
   **89 bundlach (2,618,505 B)**, których nie ma
   w żadnej z dotychczasowych paczek; żaden z 91 docelowych plików CAB ani
   PathID-ów nie występuje w 716 odzyskanych bundlach.
2. **Chronologia wywołań zdarzeń** — receipt ma
   `conditional_event_order_verified: false` i
   `mission_chronology_verified: false`. Potrzebne są też grafy pozostałych
   misji: łącznie **366 bundli, 12,650,148 B**
   (ok. 12.1 MB).

**To nie jest prośba o presety.** Wszystkie te pliki istnieją w Twojej grze —
są w `listing_sizes.txt` (SHA-256 `74854bf01f759f45c7a0ea16021e88f7cdad26b91966a677330c6f5ae20c0cba`), a nazwy bundli
pochodzą z `catalog.json` (SHA-256 `12c17bf97478eca66f2aa6066c0a14974639443d0e9d79af3355abdd895273b4`) i dziesięciu
katalogów DLC. Po prostu żadna wcześniejsza paczka ich nie zawierała. Nie
wysyłaj całej gry, audio, scen ani `GameAssembly.dll`.

## Co jest w paczce

| folder w `StreamingAssets` | plików | w tym priorytet (91 PPtr) |
|---|---:|---:|
| `AnniversaryExpansionPack` | 50 | 0 |
| `BonusMission` | 16 | 14 |
| `Dlc1` | 16 | 16 |
| `Dlc2` | 20 | 20 |
| `EarlyPurchase` | 2 | 2 |
| `ExpansionPack` | 28 | 28 |
| `SeasonPassBonus` | 2 | 2 |
| `aa/StandaloneWindows64` | 232 | 7 |

`data/script_graph_bundles.json` w repozytorium ma pełną listę 366 nazw z
rozkładem na foldery, rozmiarami, adresami `script_file`, katalogami źródłowymi
i znacznikiem `resolves_pptr`. Skrypt zbiera je w tej samej kolejności:
najpierw 89 priorytetowych, potem reszta.

## Co uruchomić

**`SRW_Y_GRAFY_PROSBA.zip`** — w folderze projektu na Drive
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`), w środku `URUCHOM_TO.bat`, `ZBIERZ_GRAFY.ps1`,
`CZYTAJ_TO.txt`. Format identyczny jak `SRW_Y_MISSION_PROSBA.zip`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_GRAFY.zip`** — wgraj go na ten sam folder
   Drive i daj znać.

Skrypt niczego nie zmienia w grze: szuka gry w typowych folderach Steam,
kopiuje pliki z ośmiu podfolderów `StreamingAssets`, pakuje je i wypisuje
rozmiar + SHA-256. Jeśli czegoś nie znajdzie, wypisze `BRAK` i mimo to zrobi
zip — wyślij go razem z logiem `SRW_Y_GRAFY_log.txt`.

## Co zrobię po otrzymaniu

1. Odszyfruję bundl e i sprawdzę **dokładnie**, czy zawierają 91 docelowych
   CAB-ów i PathID-ów. Jeśli tak — uzupełnię `deployment.md` o brakujące
   rozstawienia, bez dopisywania presetów z innych misji.
2. Zrzucę grafy zdarzeń z proweniencją i spróbuję potwierdzić kolejność
   wywołań warunkowych. Jeśli się nie da, receipt pozostanie z `false`
   i opiszę dlaczego — bez zgadywania.
3. Zaktualizuję czytanki oraz `receipt.json`. Pliki pozostaną w 100% po polsku.
