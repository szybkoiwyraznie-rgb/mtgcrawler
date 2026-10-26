# Powrót tłumaczeń — co jest gotowe, a czego brakuje

Audyt na 2026-10-26, przed oddaniem pakietu tłumaczowi. Pytanie brzmiało: czy mamy
wszystko sprawdzone na powrót tłumaczeń, łącznie z odpowiednikiem `PATCH.bat` z OE.
Odpowiedź: **nie wszystko** — poniżej dokładnie co i dlaczego.

## 1. Stan po kolei

| etap | stan | dowód |
|---|---|---|
| odczyt tabel językowych | **gotowe** | 144 tabele × 2 języki, 44 344 wpisy, chodzenie po rekordach kończy się na terminatorze w każdym obiekcie |
| odczyt scenariuszy | **gotowe** | 601 scen, 119 151 linii z 1 883 plików Lua |
| zapis tabel (sama treść) | **gotowe** | 288/288 obiektów odtwarza się **bajt w bajt** — `tools/s6_write.py --verify` |
| zapis scenariuszy (sama treść) | **gotowe** | 4 614/4 614 plików odtwarza się **bajt w bajt** (662 313 literałów) |
| import zwrotki tłumacza (`.md` → dane) | **brak** | trzeba napisać walidator: numeracja, japoński bez zmian, tokeny, liczba linii, limit |
| przebudowa bundla przy zmianie rozmiaru | **brak — i to jest ryzyko** | w grze sprawdzony jest tylko patch o **tym samym** rozmiarze (polskie otwarcie v2) |
| instalacja i cofnięcie (odpowiednik `PATCH.bat`) | **brak** | |

Enkoder treści jest więc sprawdzony: podmiana napisu to jedyna różnica między plikiem
oryginalnym a naszym — reszta bajtów zostaje nietknięta. To jest warunek konieczny
i został udowodniony offline, bez gry.

## 2. Czego dokładnie brakuje

### 2a. Import zwrotki (walidator)

Musi odrzucać całą partię, jeśli cokolwiek się nie zgadza — tak jak `translation_import.py`
w OE:

- numeracja elementów bez zmian (przesunięty numer = błąd, nie „prawie dobrze”),
- linia japońska nad `PL:` **nienaruszona** (po niej narzędzia znajdują miejsce w grze),
- tokeny zachowane (`$c`, `$n`, `$kwe`, `$kwb`, `%s`, `＃`, `{0}`, `＜…＞`),
- liczba przejść do nowej linii jak w oryginale,
- limit: linie i cele (sceny) oraz cele (tabele),
- znaki spoza obsługiwanego zestawu (polskie diakrytyki są OK — potwierdzone w grze).

### 2b. Zapis do bundla przy zmienionym rozmiarze

Dwa tryby, opisane w `docs/LIMITY_Y.md` §3:

- **tryb A** — podmiana w miejscu, ten sam rozmiar; sprawdzony w grze. Wymusza jednak
  twardy limit na **długość tekstu**, a 19,8% napisów w tabelach ma angielski dłuższy niż
  japoński, więc polski (≈ angielski + 10%) się w to nie zmieści wszędzie.
- **tryb B** — przebudowa, rozmiar może się zmienić; **niesprawdzony**. Pierwsza próba
  (v1) przebudowywała bundle przez UnityPy, plik urósł o 9,5 KiB i gra nie wystartowała.

Bez rozstrzygnięcia A/B nie można tłumaczowi obiecać limitów — dlatego w paczce są liczby
zmierzone (co gra wyświetla), ale nie ma jeszcze zdania „tyle się zmieści”.

### 2c. Instalacja i cofnięcie

Odpowiednik `PATCH.bat` z OE: jeden plik `.bat` u właściciela, który podmienia pliki
w folderze gry, robi kopię zapasową i potrafi przywrócić stan pierwotny. Dla SRW Y
oznacza to listę bundli do podmiany + kopię oryginałów + sumy kontrolne.

## 3. Kolejność, którą proponuję

1. **Test w grze, mały** (jeden bundle, jedna scena DLC + jedna nazwa w tabeli):
   polski tekst **dłuższy** od angielskiego. To rozstrzyga tryb B.
   → dopiero potem limity w paczce dostają brzmienie „twarde” albo „miękkie”.
2. **Import + walidator** (`tools/pl_import.py`) — na sztucznych danych, z testami,
   zanim tłumacz odeśle pierwszą partię.
3. **Builder patcha** (`tools/build_pl_patch.py`) + `PATCH_PL.bat` i `COFNIJ.bat`
   dla właściciela, wzorowane na OE.
4. **Pilot**: pierwsza scena w całości po polsku, w grze, przed oddaniem paczki tłumaczowi.

Punkty 2–4 są po naszej stronie i nie wymagają niczego od właściciela. Punkt 1 wymaga
jednego testu w grze.

## 4. Czego nie twierdzę

- Nie twierdzę, że patch z dłuższym tekstem zadziała — to jest właśnie do sprawdzenia.
- Nie twierdzę, że limity są ostateczne — są zmierzone z danych gry, ale nie potwierdzone
  na ekranie w polskiej wersji.
- Nie twierdzę, że pakiet jest gotowy do wysłania tłumaczowi: brakuje 19 scen z darmowej
  łatki (`docs/OWNER_STEPS_S6E_FREE_PATCH.md`) i rozstrzygnięcia z punktu 1.
