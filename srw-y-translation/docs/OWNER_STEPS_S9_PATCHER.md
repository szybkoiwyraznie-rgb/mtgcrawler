# PATCHER — jeden klik, jak w SRW OE

## Gdzie go znajdziesz

Ten sam folder na Drive, plik **`SRW_Y_PATCHER_v2.zip`** (2,864,321 B):

<https://drive.google.com/file/d/14_Ymoh6osiABK0gquZqBBMf_St1Zl-aP/view>

SHA-256 `e44f71ffe11401aaaa4382a4a8b91435514c9ef76891e37a0e3854ca79015e29`
— jeśli po pobraniu skrót się zgadza, plik jest w całości.
Stara wersja `SRW_Y_PATCHER.zip` z menu 1/2/3 jest nieaktualna — do kosza.

## Co się zmieniło względem pierwszej wersji

Było: menu `1/2/3/0` i trzeba było wybrać instalację. Doszedłeś do tego słusznie —
w OE nie ma menu, jest dwuklik i robota zrobiona. Teraz jest tak samo:

```text
SRW_Y_PATCHER_v2.zip
├── PATCHER.bat     ← dwuklik: instaluje polskie pliki
├── COFNIJ.bat      ← dwuklik: przywraca oryginały
├── PATCHER.ps1     ← robota: kopiowanie, skróty SHA-256, kopie .bak
├── MANIFEST.txt    ← 13 plików: skrót oryginału i skrót wersji polskiej
├── CZYTAJ_TO.md    ← instrukcja
└── pliki/          ← gotowe polskie pliki (13, z testu 6)
```

Żadnego wyboru, żadnych pytań poza jednym: **jeśli gra nie znajdzie się sama**, patcher
poprosi o folder gry i zapamięta go w `sciezka.txt`. Można też przeciągnąć folder gry
na `PATCHER.bat` — wtedy pytań nie ma wcale.

## Jak to działa

1. Szuka gry: `sciezka.txt` → `D:\Games\SUPER ROBOT WARS Y` → typowe miejsca
   (`Gry`, `SteamLibrary\steamapps\common`, `Program Files (x86)\Steam\...`)
   na wszystkich dyskach stałych → pyta.
2. Sprawdza, czy **gra nie jest uruchomiona** — Windows trzyma wtedy pliki otwarte
   i kopiowanie i tak by się nie udało.
3. Dla każdego pliku liczy SHA-256 tego, co leży w grze i porównuje z manifestem:

   | skrót w grze | reakcja |
   |---|---|
   | równy oryginałowi | kopiuje `.bak`, wgrywa polską wersję |
   | równy wersji polskiej | nic, pisze `JUŻ POLSKI` |
   | **inny niż oba** | **nie rusza pliku**, pisze `INNA WERSJA` |

   Trzeci przypadek chroni przed patchem z innej wersji gry. Wcześniejsze testy umiały
   tylko sprawdzić „czy skopiowałem”, więc „nic się nie zmieniło” i „kopiowanie nie doszło”
   wyglądały identycznie.
4. Kopiuje przez plik `.nowy` i przenosi go na miejsce — przerwane kopiowanie nie zostawia
   w grze połowy bundla. Błąd (antywirus, brak uprawnień) jest łapany i opisany, a nie
   wywala okna.
5. Po każdym kopiowaniu liczy skrót **jeszcze raz**: `OK` znaczy, że w grze jest dokładnie
   ten plik, który zbudowałem.
6. Podsumowanie na ekranie (`GOTOWE — uruchom grę normalnie`) i **`RAPORT_PATCHERA.txt`**
   na Pulpicie: data, godzina, wersja Windows i PowerShell, każdy plik, wynik.

## Cofnięcie

**`COFNIJ.bat`** — przywraca `.bak` i też weryfikuje skrótem. Kopie powstają wyłącznie
z oryginałów (nigdy z już podmienionego pliku), więc cofnięcie wraca do stanu sprzed
patchera nawet po kilku instalacjach pod rząd.

Podgląd bez zmieniania czegokolwiek: `PATCHER.bat sprawdz` (z listy plików pokaże,
co jest polskie, co oryginalne, a czego w grze nie ma).

## Co jest sprawdzone, a co nie

Nie mam tu Windows ani PowerShell, więc **skryptu nie uruchomiłem**. Sprawdzone statycznie
i testami (`tests/test_patcher.py`, 16 testów):

- **gramatyka PowerShell** — cały `.ps1` parsuje się bez błędu (`tree-sitter-powershell`);
  to wyłapuje klasę błędów, która 2026-10-25 wywaliła zbieraczkę DLC bez komunikatu
  (przecinek przed `)`);
- `PATCHER.bat` i `COFNIJ.bat` są czystym ASCII + CRLF (konsola psuje polskie znaki
  w `.bat`), a `.ps1` ma BOM UTF-8 + CRLF (PowerShell 5.1 czyta plik bez BOM jako ANSI);
- brak menu, brak `Read-Host` poza pytaniem o folder gry;
- manifest ↔ `pliki/` ↔ oryginały w `local/`: skróty się zgadzają, żaden „polski” plik
  nie jest identyczny z oryginałem;
- paczka jest kompletna i sprawdza się sama: gdy brakuje `pliki/`, patcher mówi
  „paczka niekompletna”, a nie „13 plików brak w grze”;
- ten sam wsad daje **bit w bit to samo zip** (stałe znaczniki czasu), więc podany wyżej
  SHA-256 zostanie aktualny także po przebudowaniu paczki z tych samych bundli.

Czego testy nie zastąpią: prawdziwego uruchomienia na Twoim dysku. Jeśli po dwukliku coś
pójdzie nie tak, wyślij mi `RAPORT_PATCHERA.txt` z Pulpitu — tam jest każdy krok z godziną.

## Wydanie finalne

Podmienia się **tylko** `pliki/` i `MANIFEST.txt`. Skrypty, kopie `.bak`, weryfikacja
skrótów i raport zostają te same — dokładnie tak, jak w OE.
