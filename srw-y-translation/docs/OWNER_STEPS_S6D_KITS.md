# SRW Y - krok S6d: dwie paczki do zebrania tekstu (kliknij i gotowe)

Wersja arkusza: 2026-10-25.3

## Co się stało i co zmieniłem

Pierwsze podejście się wywaliło, bo w skrypcie był **przecinek po ostatnim wpisie
listy** - PowerShell 5.1 nie przyjmuje takiego zapisu (`Missing expression after ','`).
Poprawione; dodatkowo w repo jest test, który tego pilnuje, więc to nie wróci.
Nic nie zostało przez to skopiowane ani zmienione w grze - błąd był na etapie
czytania skryptu.

## Co masz zrobić (2 paczki, po 4 kroki każda)

Na Dysku są dwa pliki:

| paczka | co zbiera | ile |
|---|---|---|
| `SRW_Y_ZBIERZ_TEKST.zip` | 38 bundli z tekstem podstawki (tabele językowe + scenariusz) | ok. 22 MB |
| `SRW_Y_ZBIERZ_DLC.zip` | 601 bundli DLC ze scenariuszem | ok. 7 MB |

Dla **każdej** z nich:

1. pobierz i **rozpakuj na Pulpit** (wszystkie pliki do jednego folderu),
2. kliknij dwa razy **`URUCHOM_TO.bat`**,
3. poczekaj do końca - okno **zostanie otwarte** i pokaże wynik,
4. wrzuć na Dysk Google zip, który pojawi się na Pulpicie
   (`srw_y_tekst.zip` / `srw_y_dlc_bundle.zip`).

Kolejność dowolna. Na końcu każdego okna powinno być `GOTOWE` oraz linia
`skopiowanych plikow: N z N` i `razem bajtow:`:

- tekst: `38 z 38`, `22 459 767`
- DLC: `601 z 601`, `7 032 042`

## Jeśli znowu będzie błąd

Okno się **nie zamknie**. W nim będzie `BLAD: ...` z numerem linii, a ten sam opis
zapisze się w pliku na Pulpicie:

- `srw_y_tekst_log.txt` (paczka tekstowa)
- `srw_y_dlc_log.txt` (paczka DLC)

Wyślij mi ten plik (albo zdjęcie okna) - wtedy naprawiam dokładnie to, co widać,
bez zgadywania.

## Czego nie potrzebuję

| pytanie | odpowiedź |
|---|---|
| całe `StreamingAssets` (20 GB) | **NIE** |
| całe foldery DLC (3,6 GB) | **NIE** - tylko 601 bundli z tekstem |
| audio, wideo, tekstury, modele | **NIE** - nie ma tam tekstu |
| podmieniać ISO | **NIE** - wersja PC |
| PBOOT | **NIE** |

## Co dalej (po Twoim uploadzie)

1. Odczytam oba zipy, złożę pełny inwentarz tekstu: tabele (24 + DLC) i scenariusz
   (podstawka 30 bundli + 601 bundli DLC), jp + en.
2. Wygeneruję `plik_dla_tłumacza.zip` w formacie OE: instrukcja + `spis-scen.md` +
   `sceny/` (misja z tytułem, mówcami, uczestnikami, seriami) + `widoki/`
   (nazwy, bronie, piloci, duchy, umiejętności, interfejs, opisy misji),
   każdy element z `JP`, `EN:`, `PL:` i `limit:`.
3. Osobno dostaniesz krótki raport: ile elementów, ile znaków, gdzie limity są ciasne.

> Paczki są napisane pod PowerShell 5.1 i **nie były u mnie uruchamiane** - w moim
> środowisku nie ma PowerShella, Windowsa ani gry. Dlatego są tak zbudowane, żeby
> każdy błąd zostawił ślad w pliku na Pulpicie, a nie zniknął z oknem.
