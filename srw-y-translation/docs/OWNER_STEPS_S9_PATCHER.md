# PATCHER — jeden plik do instalacji, sprawdzenia i cofnięcia

Plik: **`SRW_Y_PATCHER.zip`** (2,862,356 B, SHA-256
`aeffef8572f7fb7657c4bc01251d4097722097b65d4a15bd761307b511a517cc`)
w tym samym folderze na Drive.

## Co to jest

Do tej pory każdy test miał własny `PATCH_PL.bat` ze wpisaną na sztywno listą plików.
`PATCHER.bat` jest **jeden na zawsze**: lista plików leży w `MANIFEST.txt`, pliki
w `pliki/`, a skrypty się nie zmieniają. Do wydania finalnego podmieniam tylko zawartość
tych dwóch rzeczy.

```text
SRW_Y_PATCHER.zip
├── PATCHER.bat     ← to klikasz (dwuklik)
├── PATCHER.ps1     ← robota: kopiowanie, skróty SHA-256, cofanie
├── MANIFEST.txt    ← 13 plików: skrót oryginału i skrót wersji polskiej
├── CZYTAJ_TO.md    ← instrukcja
└── pliki/          ← gotowe polskie pliki (13)
```

## Menu (pokazuje się przy każdym uruchomieniu)

```text
1 - zainstaluj polskie pliki
2 - sprawdź, co jest teraz w grze
3 - cofnij do oryginału (z kopii .bak)
0 - wyjście
```

## Co robi, zanim cokolwiek podmieni

Dla każdego pliku liczy SHA-256 tego, co leży w grze, i porównuje z manifestem:

| skrót w grze | reakcja |
|---|---|
| równy oryginałowi | robi `.bak` i wgrywa polską wersję |
| równy wersji polskiej | nic, pisze `JUŻ POLSKI` |
| **inny niż oba** | **nie rusza pliku**, pisze `INNA WERSJA` |

Ten trzeci przypadek jest najważniejszy: gdyby patch był zbudowany z innej wersji gry,
patcher nie rozwali instalacji po cichu — powie, który plik się nie zgadza.
Wcześniejsze testy umiały tylko sprawdzić „czy skopiowałem”, więc „nic się nie zmieniło”
i „kopiowanie nie doszło” wyglądały identycznie.

Po każdym kopiowaniu liczy skrót **jeszcze raz** i porównuje z manifestem: `OK` znaczy,
że w grze jest dokładnie ten plik, który zbudowałem. Cała sesja trafia do
**`RAPORT_PATCHERA.txt`** na Pulpicie (data, godzina, każdy plik).

## Cofnięcie

Opcja **3** przywraca `.bak` i też sprawdza wynik skrótem. Kopie powstają wyłącznie
z oryginałów (nigdy z już podmienionego pliku), więc cofnięcie wraca do stanu sprzed
patchera nawet po kilku instalacjach pod rząd.

## Gdzie szuka gry

Najpierw `sciezka.txt` (zapamiętana przy poprzednim uruchomieniu), potem
`D:\Games\SUPER ROBOT WARS Y`, a jeśli tam nie ma gry — pyta o ścieżkę i zapamiętuje ją.
Sprawdza, czy w środku jest `SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64`.

## Stan tej wersji

To jest **mechanizm docelowy, wypełniony plikami z testu 6** (13 plików: tabele, prefaby,
atlasy menu i pojęć). Możesz go użyć zamiast `PATCH_PL.bat` z testu 6 — efekt ten sam,
ale z weryfikacją każdego pliku i cofaniem. Jeśli test 6 jest już zainstalowany, opcja 1
napiszе `JUŻ POLSKI` przy każdym pliku i nic nie zmieni.

## Czego nie mogłem sprawdzić

Nie mam tu PowerShell ani Windows, więc skryptu nie uruchomiłem. Sprawdziłem go inaczej:

- **gramatyka PowerShell** (`tree-sitter-powershell`) parsuje cały plik bez błędu —
  to wyłapuje właśnie takie rzeczy, jak przecinek przed `)`, który 2026-10-25 wywalił
  zbieraczkę DLC bez żadnego komunikatu;
- `PATCHER.bat` jest czystym ASCII (konsola psuje polskie znaki w `.bat`),
  a `PATCHER.ps1` ma BOM UTF-8 + CRLF (PowerShell 5.1 czyta plik bez BOM jako ANSI);
- `tests/test_patcher.py` (8 testów) sprawdza skład paczki, bilans nawiasów, brak
  przecinka przed `)`, zgodność manifestu z `pliki/` i to, że żaden „polski” plik nie jest
  identyczny z oryginałem.

Jeśli po dwukliku coś się nie uruchomi, wyślij mi `RAPORT_PATCHERA.txt` z Pulpitu —
tam jest każdy krok z godziną.
