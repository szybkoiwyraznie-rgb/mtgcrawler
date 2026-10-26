# Test 6 — polskie napisy w panelach (pilot, mech, broń, bitwa) + poprawka błędów rysowania

Plik: **`TEST6_UI_PELNY.zip`** (2,860,676 B, SHA-256
`01257a6aede712c11a9175d589f9ace446cdf546e98d7ae816da4fbb99f1066c`)
w tym samym folderze na Drive. 13 plików `.bundle`.

## Co robi ten test

Dwie rzeczy naraz.

### 1. Poprawka błędu, który psuł wszystkie atlasy do tej pory

Narzędzie `build_pl_ui_atlas.py` dekodowało BC7 w kolejności strumienia (od dołu), a prostokąty
sprite'ów są liczone od dołu obrazu — więc `top = H - y - h` trafiało w **lustrzane** pasy.
Skutek: oryginalne napisy nie były zamazywane, a polskie lądowały w złych wierszach i do góry
nogami. Wszystkie kontrole integralności przechodziły, bo piksele zmieniały się „w ogóle”.

Dowód, że to był prawdziwy błąd, a nie teoria: pierwsze zbudowanie testu 6 dało atlas
`Mid_Font`, w którym **oryginalne** `必要気力 Required Morale` nadal było na górze, a polskie
napisy pojawiły się jako lustrzane resztki na dole (`/tmp/chk_Mid_Font_d.png` → po poprawce
wszystkie 5 kolumn czyta się normalnie).

Poprawka: `decode_texture()` / `encode_texture()` — jedno miejsce, jawne odwrócenie wierszy
w obie strony, dla BC7 **i** dla nieskompresowanego RGBA32 (`TacticalPart_Font` ma format 4).

**To znaczy, że atlasy z testów 4 i 5 (`TOP_Font`, `DataBase_Font`, `OptionMenuButton_Font`)
były zbudowane błędnie.** Właściciel do tych ekranów nie dotarł, więc tego nie zobaczył.
W teście 6 wszystkie trzy są zbudowane ponownie, już poprawnie.

### 2. Nowe atlasy z plików `SRW_Y_UI6.zip`

Osiem atlasów pojęć, wszystkie przerysowane po polsku w **pięciu kolumnach** językowych
(język gry nie ma znaczenia). Kolejność wierszy odczytana z obrazków, nie zgadywana —
kontrola: kolumna `en` pocięta prostokątami sprite'ów i złożona w arkusz `/tmp/sheets/a-d.png`.

| bundle | atlas | zawartość |
|---|---|---|
| `888af64b` | `Pilot_Font` 480×480, 70 komórek | WRĘCZ, DYST, OBR, CELN, UNIK, UMIEJ, SP, Morale, Punkty, Nast., Poz., KRYT, Efekt, Cel |
| `49e9a7cb` | `Robot_Font` 720×544, 85 | Pancerz, Zwrotność, Widoczność, Poziom ulepsz., Rozmiar, Ruch, Pełna nazwa, Broń, Ulepsz. mecha, Ulepsz. broni, Modyf. obrony, Modyf. uniku, Regen. HP, Regen. EN, Info o terenie, Wym. morale, Wym. umiej. |
| `ee1aae99` | `Mid_Font` 740×640, 60 | Wym. morale, Wym. umiej., Nazwa broni, Siła ataku, Zasięg, Koszt EN, Amunicja, CELN, KRYT, Cechy, Misja, Miejsce |
| `b8d33782` | `Long_Font` 1100×640, 70 | Zalec. ranga, Stałe wyjścia, Nagrody, Adaptacja terenu, Morale startowe, Maks. morale, Maks. SP, Suma kredytów, Suma punktów, Utracone jedn., Zdobyte części, Zdobyte umiej. (×2) |
| `6311c54b` | `Short_Font` 300×320, 35 | HP, EN, Pow, Zie, Wod, Kos, Teren |
| `e17590ff` | `StatusBuff_Font` 1200×200, 25 | Statystyki +, Statystyki −, Umiejętność aktywna, Zdolność aktywna, Unieruchomiony |
| `ef1c821e` | `TacticalPart_Font` 1090×80, 10 | FAZA GRACZA, FAZA WROGA (format 4 = RGBA32, ścieżka bez kompresji) |
| `6a727783` | `TacticalPart02_Font` 320×40, 10 | TURA, JEDN. |

Reguła długości zachowana: rysowanie zmniejsza czcionkę, aż napis wejdzie w komórkę oryginału
i nigdy nie wychodzi za nią (`pad` per atlas, bo chip 60×32 nie może mieć tego samego marginesu
co komórka 352×64).

### 3. Znacznik `PL6` — żeby przestać zgadywać o ekranie tytułowym

W prefabie `Title` (`ec293019`) numer wersji `30` jest zamieniony na **`PL6`**. Ten prefab był
już podmieniany w testach 3–5 (skrypt potwierdzał SHA-256 w folderze gry), a napis
`Press Any Key` się nie zmieniał. Teraz wiadomo, co to znaczy:

| co widać w rogu ekranu | wniosek |
|---|---|
| `PL6` | prefab **jest** rysowany; `Press Any Key` pochodzi z innego assetu → szukamy napisu, nie prefabu |
| `30` (bez zmian) | prefab **nie** jest tym, co widać; ekran tytułowy rysuje inny plik |

To rozstrzygnięcie kosztuje jedno spojrzenie i zamyka cztery testy domysłów.

## Kroki dla właściciela

1. Rozpakuj `TEST6_UI_PELNY.zip` na Pulpit.
2. Kliknij dwa razy **`PATCH_PL.bat`**.
3. Poczekaj — na końcu każdego pliku ma być **`OK`**, a na Pulpicie powstaje `RAPORT.txt`.
4. Uruchom grę i sprawdź: numer wersji na ekranie tytułowym (**`PL6`** czy `30`).
5. Wejdź w nową grę, do ekranu pilota / mecha.

Cofnięcie: **`COFNIJ.bat`** (pliki `.bak` powstały przy pierwszym patchu).

## Czego ten test NIE rozstrzyga

- Czy ekran tytułowy da się przetłumaczyć — to zależy od punktu 3 powyżej.
- Czy atlasy pojęć są w ogóle widoczne bez zapisu gry: ekran pilota/mecha jest dostępny
  z nowej gry, ale panel podsumowania misji (`Long_Font`) dopiero po misji.

## Pliki w repo

- `tools/build_pl_ui_atlas.py` — `decode_texture` / `encode_texture`, obsługa formatu 4, `pad`
- `tools/build_pl_table_patch.py` — `PLAIN_ROOTS` obejmuje teraz `local/ui6`
- `translations/ui_atlas_term_pl.json` — osiem atlasów pojęć i ich polskie napisy
- `translations/ui_test_pl.json` — dopisany znacznik `30` → `PL6`
- `tests/test_ui_atlas_orientation.py` — trzy testy pilnujące orientacji i długości strumienia
- `tests/test_ui_prefab_patch.py` — oczekuje trzech zmienionych obiektów (dwa napisy + znacznik)
