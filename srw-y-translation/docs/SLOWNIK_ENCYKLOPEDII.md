# Słownik encyklopedii: czego brakuje, żeby pokazywać wpisy po odblokowaniu

## Pytanie właściciela (2026-11-09)

„Czemu tabele wpisów słownika nigdy nie wróciły? Powiedz, co mam ci wgrać, to ci
wgram. Masz zresztą pełny inwentarz gry.”

## Odpowiedź w dwóch zdaniach

Mam **spis** (nazwy, rozmiary, klasy zasobów), nie mam **plików**: bundli z tymi
tabelami nie było w żadnym archiwum, które do tej pory wgrałeś. Do zebrania ich
z Twojej kopii gry jest gotowy zestaw `SRW_Y_ZBIERZ_SLOWNIK.zip`.

## Co dokładnie jest potrzebne

11 plików z `…\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64\`,
łącznie **58 461 B**:

| # | Plik | Rozmiar | Zasób |
|--:|------|--------:|-------|
| 1 | `285818855b5de73d830691acc66152df.bundle` | 14 394 B | `PilotDictionaryEntryTable` |
| 2 | `f623b6c79ecfcad1039e29cce87e8373.bundle` | 2 617 B | `PilotDictionaryEntryTable_D1` |
| 3 | `29eda1d3638745a1e3e0805db5933b86.bundle` | 2 376 B | `PilotDictionaryEntryTable_D2` |
| 4 | `8da124fa5a1a155373e562aed4ad403d.bundle` | 5 315 B | `PilotDictionaryEntryTable_D3` |
| 5 | `dfc36f738dca6ee278a43abf034fb04b.bundle` | 4 872 B | `PilotDictionaryEntryTable_D4` |
| 6 | `a1537bb970d7f23aec670f2f54ff616b.bundle` | 11 334 B | `RobotDictionaryEntryTable` |
| 7 | `37540e8d50756baf681c32a7eba5fdc1.bundle` | 2 325 B | `RobotDictionaryEntryTable_D1` |
| 8 | `7c18bc903c6f67a6a59ba8d807c22f2a.bundle` | 2 340 B | `RobotDictionaryEntryTable_D2` |
| 9 | `a78e44ccb19568678e44b9706e5982db.bundle` | 4 086 B | `RobotDictionaryEntryTable_D3` |
| 10 | `50fa37a7a150b36b8cce0103ad6a5ff3.bundle` | 6 294 B | `RobotDictionaryEntryTable_D4` |
| 11 | `9e46587dfa2b6e15792a39f4d40519ed.bundle` | 2 508 B | `WordDictionaryEntryTable` |

Nazwy i rozmiary pochodzą z Twojego `listing_sizes.txt`, sprawdzone z katalogiem
Addressables (`data/dictionary_owner_assets.json`, pole
`present_in_recovered_inputs: false` przy każdym z 11).

## Jak je zebrać

[`SRW_Y_ZBIERZ_SLOWNIK.zip`](https://drive.google.com/file/d/1TbMgWXhasj-udvyR3YZnmW-_HLQks2iN/view)
(Drive `1TbMgWXhasj-udvyR3YZnmW-_HLQks2iN`, 3 789 B):

1. rozpakuj w dowolnym miejscu,
2. kliknij `ZBIERZ_SLOWNIK.bat` (jeśli gra nie stoi w typowym miejscu —
   przeciągnij na BAT folder z `SUPER ROBOT WARS Y.exe`),
3. na Pulpicie pojawi się `SLOWNIK_ENCYKLOPEDII.zip`,
4. wgraj go na Drive.

Zestaw nic nie zmienia w grze: kopiuje 11 plików i pakuje je w ZIP.

## Wynik odczytu (2026-11-09): tabele przyszły, warunku w nich nie ma

`SLOWNIK_ENCYKLOPEDII.zip` (60 232 B, SHA-256
`f04a1fa3ff22166d8f829de2ad41c103afa07dba59a776e36db6fe8dfa0a666d`) zawierał
wszystkie 11 bundli. Zaszyfrowane tym samym szyfrem co reszta gry; po odszyfrowaniu
każdy bundel to jedna tabela `MonoBehaviour` z listą wpisów. Odczyt zapisuje
`tools/read_dictionary_entries.py` do `data/dictionary_entries_y.json`
(635 300 B, SHA-256 `381327c9…cb85`) — bez ani jednego znaku tekstu gry.

| Rodzina tabeli | Wiersze | `TextID` | Pola rekordu |
|---|---:|---:|---|
| `PilotDictionaryEntryTable` (+`_D1…_D4`) | 786 | 419 | `BaseID`, `TextID`, `FaceID`, `VoiceActorID`, `Face[4]`, `Voice[4]`, `order`, `pkg`, `Option` |
| `RobotDictionaryEntryTable` (+`_D1…_D4`) | 1 220 | 294 | `BaseID`, `TextID`, `HeightStr`, `WeightStr`, `HeightNumStr`, `WeightNumStr`, `HeightUnit`, `WeightUnit`, `Direction`, `pkg`, `Option` |
| `WordDictionaryEntryTable` | 78 | 78 | `TextID`, `ProductID`, `pkg`, `Option` |

Trzy rzeczy, które z tego wynikają:

1. **Warunku odblokowania nie ma.** Żadnego pola flagi, misji, numeru części ani
   warunku; `Option` jest pusty we **wszystkich 2 084 wierszach**. Reguła
   „po czym pokazuje się druga część wpisu” nie jest zapisana w danych.
2. **Słownik jest kompletny w tym, co już mamy** — 419 `TextID` pilotów,
   294 maszyn i 78 haseł to dokładnie te same zbiory, co w
   `data/dictionary_links.json` (zero różnic w obie strony). Czyli czytanki nie
   pomijają żadnego wpisu encyklopedii.
3. **Jest `pkg`** — numer pakietu: 0 (podstawka) 1 531 wpisów, 10: 62, 20: 51,
   30: 88, 40: 352. To jedyny ślad „kiedy”: część wpisów pochodzi z dodatków.
   Do pokazywania po misji to za mało.

## Następny krok: pliki kodu gry

Skoro reguły nie ma w tabelach, siedzi w kodzie. Nowy zestaw
[`SRW_Y_ZBIERZ_KOD.zip`](https://drive.google.com/file/d/1SsR9TpflFF3ngk9Yz4NkAo4oOsaDXV7u/view)
(Drive `1SsR9TpflFF3ngk9Yz4NkAo4oOsaDXV7u`, 3 810 B, SHA-256 `eabbfb7d…b847`)
zbiera to, co istnieje w instalacji:

- `…_Data\Managed\Assembly-CSharp.dll` (+`Assembly-CSharp-firstpass.dll`) —
  wersja Mono,
- `…_Data\il2cpp_data\Metadata\global-metadata.dat` + `GameAssembly.dll` —
  wersja IL2CPP,
- **`spis.txt`** z wykazem `…_Data`, `Managed` i `il2cpp_data\Metadata`
  (powstaje zawsze, nawet gdy plików nie ma — od razu pokaże układ instalacji).

Pliki > 250 MB są pomijane. Po odczytaniu kodu sprawdzę, jak gra decyduje
o odsłonięciu dalszej części wpisu, i powiem wprost: albo reguła da się odczytać
(i wtedy części pojadą pod właściwe misje), albo jest zaszyta w sposób, którego
nie da się odtworzyć — wtedy zostaje mapa od właściciela.

## Co z tego wyjdzie

Klasy zasobów (`Com.BBStudio.SRTeam.Data.PilotDicEntryList`,
`RobotDicEntryList`, `WordDicEntryList`) to listy wpisów słownika. Po odczytaniu
sprawdzę, czy w rekordach jest warunek odblokowania (`flag`, `openCondition`,
numer misji, `stgmemory`). Możliwe wyniki:

- **jest warunek** → części wpisów staną pod właściwymi misjami i zniknie pytanie
  „kiedy to się pokaże”;
- **nie ma warunku** (np. odblokowanie siedzi w kodzie gry) → powiem to wprost
  i zostaje wybór: mapa od Ciebie albo dzisiejszy układ bez spojlerów.

Do tego czasu nic nie zgaduję: dalsze części wpisów zostają w jednej sekcji na
końcu dokumentu.
