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
Potem skopiuj **cały** blok poniżej, wklej do PowerShella i naciśnij Enter.

> **Trzecia poprawka — najważniejsza.** Poprzedni blok pobierał plik tylko
> wtedy, gdy go nie było, więc nieudane pobranie zostawiało **stary** skrypt i
> błąd wyglądał identycznie jak błąd w programie. Teraz blok: (1) **kasuje** stary
> plik, (2) pobiera wersję przypiętą do konkretnego commita (`$sha`), więc nie ma
> czego zcache'ować, (3) **sprawdza numer wersji** w pliku i bez zgodności nic nie
> uruchamia. Poprawny skrypt wypisuje na starcie `mem_carve 2026-10-25.5` — jeśli
> tej linii nie ma, to znaczy, że pobrało się coś innego.
>
> Przypomnienie: w bloku nie ma ani jednego adresu ani nazwy pliku, bo komunikator
> zamienia je w linki — adres składa się z kawałków (`[char]58` to dwukropek,
> `[char]46` to kropka). Jeśli w konsoli widzisz `>>`, naciśnij **Ctrl+C** i wklej
> od nowa.

```powershell
$py = Join-Path $env:USERPROFILE ("Desktop\mem_carve" + [char]46 + "py")
$want = "2026-10-25" + [char]46 + "7"
$sha = "f27d2b68ec09473ac42b9d1adc775a4b3ce6358e"
$u1 = "https" + [char]58 + "//raw" + [char]46 + "githubusercontent" + [char]46 + "com/szybkoiwyraznie-rgb/mtgcrawler/" + $sha + "/srw-y-translation/tools/mem_carve" + [char]46 + "py"
$u2 = "https" + [char]58 + "//github" + [char]46 + "com/szybkoiwyraznie-rgb/mtgcrawler/raw/" + $sha + "/srw-y-translation/tools/mem_carve" + [char]46 + "py"
Remove-Item -LiteralPath $py -ErrorAction SilentlyContinue
python -c "import urllib.request,sys;urllib.request.urlretrieve(sys.argv[1],sys.argv[2])" $u1 $py
if (-not (Test-Path $py)) { python -c "import urllib.request,sys;urllib.request.urlretrieve(sys.argv[1],sys.argv[2])" $u2 $py }
if (-not (Test-Path $py)) { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri $u2 -OutFile $py }
$ok = (Test-Path $py) -and (Select-String -LiteralPath $py -Pattern $want -Quiet)
if (-not (Test-Path $py)) { Write-Host "POBRANIE NIE UDALO SIE - napisz mi to" -ForegroundColor Red }
if ((Test-Path $py) -and -not $ok) { Write-Host "POBRAL SIE STARY PLIK - napisz mi to" -ForegroundColor Red; Remove-Item $py }
if ($ok) { python $py --selftest }
if ($ok) { Read-Host "KROK 1: gra na ekranie tytulowym - nacisnij Enter" }
if ($ok) { python $py --out "$env:USERPROFILE\Desktop\srw_y_carve_1" }
if ($ok) { Read-Host "KROK 2: wejdz w misje, poczekaj az pojawi sie KUBA dialogu z tekstem - nacisnij Enter" }
if ($ok) { python $py --watch 120 --out "$env:USERPROFILE\Desktop\srw_y_carve_2" }
if ($ok) { explorer "$env:USERPROFILE\Desktop\srw_y_carve_1" }
if ($ok) { explorer "$env:USERPROFILE\Desktop\srw_y_carve_2" }
```

> Jeśli wisisz teraz na `KROK 1: ... nacisnij Enter` z poprzedniej próby -
> naciśnij **Ctrl+C** i wklej blok od nowa.

Co się będzie działo po kolei:

1. Plik `mem_carve.py` trafi na pulpit (pobiera go Python; jeśli się nie uda,
   PowerShell z TLS 1.2).
2. Skrypt sam się przetestuje — musi pojawić się `self-test: PASS`.
3. Zatrzyma się na `KROK 1: ...` — **naciśnij Enter**. Odczyt potrwa **1–3
   minuty** (okno może wyglądać na zawieszone, nie zamykaj go).
4. Zatrzyma się na `KROK 2: ...` — przełącz się do gry, wejdź w misję tak, żeby
   **ukazał się dialog z tekstem**, wróć i naciśnij Enter. Potem **szybko wróć do
   gry i przez 2 minuty przechodź dialogi** (klikaj dalej). Skrypt w tym czasie
   czyta pamięć i zapisuje to, co się pojawia.
5. Otworzą się dwa foldery: `srw_y_carve_1` i `srw_y_carve_2`.

## Druga runda — ta sama wklejka, bez zmian

Pierwsza runda dała wynik i pokazała, czego brakuje: skrypt wyciąga całe pliki, a
tych z tekstem gra trzyma w pamięci pocięte na kawałki. Dlatego **ten sam blok
robi teraz więcej**: obok plików zapisuje też zebrane stringi (dwa pliki
`strings_utf16.txt` i `strings_utf8.txt`, w tych samych folderach) i liczy, ile
japońskiego tekstu ma gra.

Blok się nie zmienił — skrypt sam się podmienia przy każdym uruchomieniu.

Piąta runda ma dwie zmiany i obie są ważne:

1. **KROK 2 to teraz 2 minuty nagrywania.** Skrypt nie robi jednego przebiegu,
   tylko przez 2 minuty w kółko czyta pamięć. W tym czasie **przechodź dialogi** —
   klikaj dalej, żeby kolejne kwestie się pojawiały. Tekst fabuły istnieje w
   pamięci tylko przez chwilę, więc trzeba go „przyłapać".
2. **Plik `strings_objects.tsv` będzie teraz kompletny** (poprzednio ucinał się na
   8 MB). Wgraj go **razem z raportami** — może mieć kilkanaście MB.

Poprzednia poprawka: skrypt czyta teraz
**całe** pliki z pamięci, także takie, które nie mieszczą się w jednym kawałku
(poprzednio zawsze ucinał je na 8 MB), odrzuca fałszywe nagłówki i zapisuje w
folderach po kilka surowych fragmentów pamięci (`region_..bin`) tam, gdzie jest
najwięcej japońskiego. Te pliki też możesz zostawić u siebie — do raportów nie są
potrzebne.
Wystarczy powtórzyć te same kroki (gra na ekranie tytułowym, potem scena z
dialogiem) i wgrać **dwa nowe raporty**. Pliki `strings_*` zostaw u siebie;
poproszę o nie, jeśli będą potrzebne.

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
| `Nie można utworzyć bezpiecznego kanału SSL/TLS` | to był stary blok; nowy pobiera przez Pythona — wklej go od nowa |
| `can't open file ... mem_carve.py` | plik się nie pobrał; nowy blok sam sprawdza, czy plik jest |
| `POBRANIE NIE UDALO SIE` | obie drogi zawiodły — użyj drogi z przeglądarki (niżej) i wklej blok jeszcze raz |
| `POBRAL SIE STARY PLIK` | pobrało się coś innego niż wersja 2026-10-25.5 — napisz mi to |
| brak linii `mem_carve 2026-10-25.5` na starcie | to stary skrypt; wklej blok jeszcze raz |

## Jeśli pobieranie nie wyjdzie (droga z przeglądarki)

Przeglądarka ma nowsze TLS niż stary PowerShell, więc ta droga działa zawsze:

1. Otwórz w przeglądarce:
   `https://github.com/szybkoiwyraznie-rgb/mtgcrawler/raw/arena/6906ed6b-mtgcrawler/srw-y-translation/tools/mem_carve.py`
2. W przeglądarce powinien pokazać się kod. Naciśnij **Ctrl+S** i zapisz plik
   **dokładnie** jako `mem_carve.py` **na Pulpicie** (typ: wszystkie pliki; jeśli
   przeglądarka dopisze `.txt`, usuń to końcówkę).
3. Wróć do PowerShella i wklej ten sam blok — zobaczy, że plik już jest, i pójdzie
   dalej bez pobierania.

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
