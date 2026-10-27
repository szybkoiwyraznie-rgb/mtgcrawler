# PROŚBA — 11 assetów właścicielskich encyklopedii Y (`SRW_Y_ENCYKLOPEDIA_PROSBA.zip`)

Nowy handoff czytanek: [`HANDOFF_READING_CONT_2026-10-27.md`](HANDOFF_READING_CONT_2026-10-27.md).

## Dlaczego to jest potrzebne

Właściciel wymaga, żeby pliki czytanek były **w 100% po polsku**, a przy
pierwszym wystąpieniu każdej postaci i mecha w `deployment.md` miały
odpowiednią **biografię/opis z encyklopedii gry**.

Mamy już komplet tekstów encyklopedii — cztery rodziny tabel
`dic_text_pilot`, `dic_text_robot`, `dic_text_name`, `dic_text_word`
(podstawka + DLC) — oraz ich klucze Shared Data i adresy wierszy S6.
**Nie mamy rekordów właścicielskich**, czyli informacji, który wariant
biografii należy do której postaci, a który opis do którego mecha. Bez nich
każde przypisanie byłoby zgadywaniem po nazwie lub prefiksie klucza, czego
właściciel wyraźnie zakazał.

Bazowy `catalog.json` (SHA-256 `12c17bf97478eca66f2aa6066c0a14974639443d0e9d79af3355abdd895273b4`) wskazuje dokładnie
**11 assetów** tych rekordów. Wszystkie leżą w jednym folderze gry
`StreamingAssets/aa/StandaloneWindows64` i ważą razem **58,461 B**
(ok. 57 KB). Żadnego z nich nie ma w dotychczasowych
paczkach źródłowych; audyt na 741 nazwanych obiektach MonoBehaviour potwierdza
0 obiektów źródłowych.

| asset | bundle | rozmiar | klasa z katalogu |
|---|---|---|---:|
| `PilotDictionaryEntryTable` | `285818855b5de73d830691acc66152df.bundle` | 14,394 B | PilotDicEntryList |
| `PilotDictionaryEntryTable_D1` | `f623b6c79ecfcad1039e29cce87e8373.bundle` | 2,617 B | PilotDicEntryList |
| `PilotDictionaryEntryTable_D2` | `29eda1d3638745a1e3e0805db5933b86.bundle` | 2,376 B | PilotDicEntryList |
| `PilotDictionaryEntryTable_D3` | `8da124fa5a1a155373e562aed4ad403d.bundle` | 5,315 B | PilotDicEntryList |
| `PilotDictionaryEntryTable_D4` | `dfc36f738dca6ee278a43abf034fb04b.bundle` | 4,872 B | PilotDicEntryList |
| `RobotDictionaryEntryTable` | `a1537bb970d7f23aec670f2f54ff616b.bundle` | 11,334 B | RobotDicEntryList |
| `RobotDictionaryEntryTable_D1` | `37540e8d50756baf681c32a7eba5fdc1.bundle` | 2,325 B | RobotDicEntryList |
| `RobotDictionaryEntryTable_D2` | `7c18bc903c6f67a6a59ba8d807c22f2a.bundle` | 2,340 B | RobotDicEntryList |
| `RobotDictionaryEntryTable_D3` | `a78e44ccb19568678e44b9706e5982db.bundle` | 4,086 B | RobotDicEntryList |
| `RobotDictionaryEntryTable_D4` | `50fa37a7a150b36b8cce0103ad6a5ff3.bundle` | 6,294 B | RobotDicEntryList |
| `WordDictionaryEntryTable` | `9e46587dfa2b6e15792a39f4d40519ed.bundle` | 2,508 B | WordDicEntryList |

## Co uruchomić

**`SRW_Y_ENCYKLOPEDIA_PROSBA.zip`** — w folderze projektu na Drive
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`), w środku `URUCHOM_TO.bat`,
`ZBIERZ_ENCYKLOPEDIA.ps1`, `CZYTAJ_TO.txt`. Format identyczny jak
`SRW_Y_MISSION_PROSBA.zip`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_ENCYKLOPEDIA.zip`** — wgraj go na ten sam
   folder na Drive i daj znać.

Skrypt niczego nie zmienia w grze: szuka gry w typowych folderach Steam,
kopiuje 11 plików i pakuje je, wypisując rozmiar i SHA-256. Jeśli któregoś
nie znajdzie, wypisze `BRAK` i mimo to zrobi zip — wyślij go razem z logiem.

## Czego NIE prosimy

- **To nie jest prośba o presety.** 91 nierozwiązanych wskaźników PPtr nie
  jest dowodem brakujących plików u właściciela i nie jest podstawą tej prośby.
- Nie potrzebujemy audio, scen, tekstów, całej gry ani `GameAssembly.dll`.
- Nie potrzebujemy 366 bundli `ScriptGraphAsset` (to osobny, późniejszy temat
  chronologii zdarzeń).

## Co zrobię po otrzymaniu

1. Odszyfruję 11 bundli tym samym, sprawdzonym sposobem (`pilot_master.decrypt`)
   i zrzucę pełne drzewa obiektów z proweniencją (bundle, CAB, PathID).
2. Odtworzę **dokładny schemat** `PilotDicEntryList`, `RobotDicEntryList`,
   `WordDicEntryList` — bez zakładania nazw pól.
3. Połączę rekord z ID postaci/mecha z kluczem `dic_text_*` po rzeczywistym ID
   i dodam polską biografię/opis przy pierwszym wystąpieniu w `deployment.md`,
   `piloci.md` i `mechy.md`. Każde powiązanie dostanie proweniencję.
4. Jeśli w środku okaże się, że pola są inne, podam liczbę i opis tego, co
   jest, zamiast dopisywać własną interpretację.
