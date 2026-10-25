# Krok S3 — najprościej: jeden blok do wklejenia

**Po co to:** gra trzyma odszyfrowany tekst w pamięci, kiedy działa. Skrypt czyta
tę pamięć (tylko do odczytu, niczego nie zmienia) i zapisuje dwa małe raporty.
Na ich podstawie policzę, ile tekstu ma gra.

**Co pobrać:** nic ręcznie. Blok poniżej sam pobiera skrypt.
**Co wgrać:** dwa pliki `carve_report.json` do folderu `SRW/SRWY` na Dysku
(tam, gdzie wcześniej wrzucałeś `catalog.json`).
**Co napisać:** nic. Naciskasz dwa razy **Enter**.

---

## Jedyny krok — wklej całość do PowerShella

Najpierw **uruchom grę** i zostań na ekranie tytułowym (gra ma działać w tle).
Potem skopiuj **cały** blok poniżej, wklej do PowerShella i naciśnij Enter:

```powershell
$py = "$env:USERPROFILE\Desktop\mem_carve.py"
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/arena/6906ed6b-mtgcrawler/srw-y-translation/tools/mem_carve.py" -OutFile $py
Write-Host "=== TEST (bez gry, powinno byc PASS) ===" -ForegroundColor Cyan
python $py --selftest
Read-Host "KROK 1: gra na ekranie tytulowym - nacisnij Enter"
python $py --out "$env:USERPROFILE\Desktop\srw_y_carve_1"
Read-Host "KROK 2: wejdz w misje tak, zeby dialog byl widoczny - nacisnij Enter"
python $py --out "$env:USERPROFILE\Desktop\srw_y_carve_2"
Write-Host "=== GOTOWE - otwieram dwa foldery z raportami ===" -ForegroundColor Green
explorer "$env:USERPROFILE\Desktop\srw_y_carve_1"
explorer "$env:USERPROFILE\Desktop\srw_y_carve_2"
```

Co się będzie działo po kolei:

1. Skrypt ściągnie się na pulpit i sam się przetestuje — zobaczysz
   `self-test: PASS`.
2. Zatrzyma się na `KROK 1: ...` — wtedy **naciśnij Enter**. Odczyt potrwa od
   kilku sekund do minuty (okno może wyglądać na „zawieszone”, to normalne).
3. Zatrzyma się na `KROK 2: ...` — przełącz się do gry, wejdź w dowolną misję
   tak, żeby **dialog był widoczny na ekranie**, wróć do PowerShella i **naciśnij
   Enter**. To drugi odczyt.
4. Otworzą się dwa foldery z pulpitowego `srw_y_carve_1` i `srw_y_carve_2`.

## Co dalej wgrać

W każdym z tych dwóch folderów jest plik **`carve_report.json`**. Przeciągnij
**oba** te pliki do folderu **`SRW/SRWY`** na Dysku Google (ten sam, w którym są
`catalog.json` i `GameAssembly.dll`).

To wszystko. Foldery z odzyskanymi plikami **zostaw u siebie** — po raportach
powiem, czy i które pliki warto przesłać.

## Jeśli coś pójdzie nie tak

Wklej mi dokładnie to, co wypisała konsola — albo zrób zrzut ekranu. Nic nie
zepsujesz: skrypt tylko czyta.

| komunikat | co zrobić |
|---|---|
| `self-test: FAIL` | napisz mi to, poprawię przed dalszymi krokami |
| `process not found` | gra musi działać w momencie odczytu; sprawdź `tasklist \| findstr /i super` i podaj mi wynik |
| `OpenProcess failed` | uruchom PowerShell jako administrator i powtórz |
| `a 64-bit Python is required` | zainstalowana jest wersja 32-bit — napisz, podam inną drogę |
| `Microsoft.PowerShell... nie można rozpoznać` | wklej jeszcze raz cały blok, od pierwszej linii |

## Czego skrypt NIE robi

- nie zmienia gry, plików, zapisów — dostęp **tylko do odczytu**;
- nie wysyła niczego do internetu;
- w raportach **nie ma treści gry** — same liczby i nazwy.

---

<details>
<summary>Więcej szczegółów (możesz pominąć)</summary>

## Dlaczego nie da się po prostu odczytać plików

Gra szyfruje bundle własnym strumieniem AES z hasłem i solą
(`SeekableAesStream` — widać to w kodzie gry). Sprawdziłem 61 mln kandydatów na
klucz i 6 mln literałów z metadanych — bez trafienia. Dlatego nie zgadujemy
hasła, tylko bierzemy tekst tam, gdzie gra już go odszyfrowała: z pamięci.

## Co dokładnie robi skrypt

1. znajduje proces gry (`tasklist`),
2. otwiera go **tylko do odczytu** (`PROCESS_VM_READ`),
3. przegląda czytelne obszary pamięci (8 MB na raz),
4. szuka nagłówków `UnityFS` (cały bundle) i `CAB-` (plik w środku bundla),
5. wycina dokładnie tyle bajtów, ile deklaruje nagłówek, i **sprawdza, że
   wycięte dane znów się otwierają**,
6. liczy obecność tekstu japońskiego (kany) — bez zapisywania treści,
7. zapisuje raport z liczbami: `carve_report.json`.

## Pliki w projekcie

- `tools/mem_carve.py` — ten skrypt (bez żadnych bibliotek, tylko standardowy
  Python),
- `tools/read_carve.py` — otwiera odzyskane pliki i mierzy tekst (używam go ja,
  nie Ty),
- `docs/S2_FINDINGS.md` — pełna analiza szyfrowania i wyników.

</details>
