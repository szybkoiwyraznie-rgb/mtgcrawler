# SRW Y - krok S3 (wariant awaryjny): klucz z pamieci gry

**Nie uruchamiaj tego teraz.** Aktualny krok to pary plikow (arkusz
`OWNER_STEPS_S3_PAIRS.md`) - nie wymaga klucza ani uprawnien administratora.
Ten arkusz zostaje na wypadek, gdyby droga z parami sie zatrzymala.

Cel: wyciagnac z dzialajacej gry klucz, ktorym sa zaszyfrowane pliki `.bundle`,
a potem **odszyfrowac prawdziwy plik** i pokazac, ze wraca do gry bez zmiany
rozmiaru. To pierwsza polowa tego, co robi zestaw OE: podmiana tekstu w plikach.

Co sie zmienilo po nieudanym KROKU 0:

- nie ma juz dwoch plikow - jest **jeden** (`srw_y_key`, wersja `2026-10-26.8`);
- pobieranie ustawia TLS 1.2 (PowerShell 5.1 sam negocjuje 1.0/1.1 i GitHub tego
  nie przyjmuje) i ma zapasowe wyjscie przez `curl.exe`;
- nic nie jest zapisywane na `C:\` - wszystko idzie na **Pulpit**, jak dotychczas;
- w bloczkach nie ma nazw plikow z rozszerzeniem ani gotowych adresow, bo klient
  czatu zamienial je na linki i do PowerShell trafial link zamiast nazwy pliku.
  Nazwy sa skladane z kawalkow, a skrypt znajdowany jest maska `*key*`.

Skrypt czyta pamiec gry tylko do odczytu (`PROCESS_VM_READ`): nie zmienia gry, nie
instaluje modow, nie rusza zapisow.

## KROK 0 - folder na Pulpicie i skrypt w nim

**Droga A (najprostsza, bez PowerShell):** w czacie dostajesz bezposredni link do
pliku. Klikasz go w przegladarce, plik laduje w `Pobrane` - dalej robi to bloczek
ponizej (utworzy folder `srwytool` na Pulpicie i przeniesie tam swiezo pobrany
plik). PowerShell uruchom **jako administrator**, bo pozniej czyta pamiec gry.

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
New-Item -ItemType Directory -Force -Path $work | Out-Null
$ext = [char]46 + "py"
$src = Get-ChildItem (Join-Path $env:USERPROFILE "Downloads") -File |
    Where-Object { $_.Extension -eq $ext -and $_.Name -like "*key*" } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($src) { Copy-Item $src.FullName $work -Force }
$f = Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1
if ($f -and $f.Length -gt 30000) {
    Write-Host ("OK  skrypt: " + $f.FullName + "  " + $f.Length + " B")
} elseif ($f) {
    Write-Host ("plik jest, ale maly (" + $f.Length + " B) - pobierz go jeszcze raz")
} else {
    Write-Host "BRAK PLIKU - uzyj drogi B nizej"
}
```

**Droga B (gdy przegladarka nie pobierze):** ten bloczek pobiera plik sam, z
wymuszonym TLS 1.2 (PowerShell 5.1 sam negocjuje 1.0/1.1 i GitHub tego nie
przyjmuje) oraz z zapasem przez `curl.exe`.

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
New-Item -ItemType Directory -Force -Path $work | Out-Null
Set-Location $work
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$name = "srw_y_key" + [char]46 + "py"
$sha  = "c6a093edcabcdff98ac8f2a4d2cd98af464de29f"
$url  = "https" + [char]58 + "//raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/" + $sha + "/srw-y-translation/tools/" + $name
Remove-Item (Join-Path $work $name) -ErrorAction SilentlyContinue
try {
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile (Join-Path $work $name) -ErrorAction Stop
} catch {
    Write-Host ("pierwsza proba nie dala rady: " + $_.Exception.Message)
    curl.exe -L -o (Join-Path $work $name) $url
}
$f = Get-Item (Join-Path $work $name) -ErrorAction SilentlyContinue
if ($f -and $f.Length -gt 30000) {
    Write-Host ("OK  skrypt: " + $f.FullName + "  " + $f.Length + " B")
} else {
    Write-Host "BRAK PLIKU - skopiuj mi caly ten wynik"
}
```

W obu drogach musi pojawic sie `OK  skrypt: ...Desktop\srwytool\...` z rozmiarem
powyzej 30 000 B (plik ma ok. 35 kB). Jesli nie - odeslij mi wynik, to nie jest
problem po Twojej stronie.

## KROK 1 - biblioteka AES i test skryptu (bez gry)

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
Set-Location $work
$tool = (Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1).FullName
python -m pip install --upgrade pycryptodome
python $tool selftest
```

Oczekiwane (dokladnie te linie, bez bledow):

```
srw_y_key 2026-10-26.8
  ctr-le          ok
  ctr-be          ok
  ctr-le-byte     ok
  ctr-be-byte     ok
  ctr-le-xoridx   ok
  ctr-be-xoridx   ok
  ctr-le-xorbyte  ok
  ctr-be-xorbyte  ok
  ctr32le         ok
  ctr32be         ok
  ofb             ok
  cfb128          ok
  cfb8            ok
  cbc             ok
  ecb             ok
  wrong key       ok
  byte[] scan     ok
  patch + enc     ok
selftest: PASS
```

**Wazne:** pierwsza linia musi brzmiec `srw_y_key 2026-10-26.8`. Jesli widzisz
starszy numer, to jest plik z poprzedniej proby i KROK 3 znow sie wywali -
powtorz KROK 0, zeby go nadpisac.

Jesli `python` nie jest rozpoznany, uzyj `py` zamiast `python`.

## KROK 2 - uruchom gre i wczytaj scene z tekstem

1. Uruchom `SUPER ROBOT WARS Y` normalnie.
2. Wczytaj **zapis** albo zacznij misje tak, zeby na ekranie byly dialogi. To nie
   formalnosc: klucz i odszyfrowane bundle sa w pamieci tylko wtedy, gdy gra juz
   ich uzywa.
3. Zostaw gre wlaczona i wroc do PowerShell (dalej jako administrator).

## KROK 3 - szukanie klucza (1-3 minuty)

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
Set-Location $work
$tool = (Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1).FullName
$bundles = "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64"
$sample = Get-ChildItem $bundles -Filter *.bundle -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -eq 940012 } | Select-Object -First 1
if (-not $sample) {
    $sample = Get-ChildItem $bundles -Filter *.bundle -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -gt 200000 -and $_.Length -lt 2000000 } |
        Sort-Object Length -Descending | Select-Object -First 1
}
if (-not $sample) { Write-Host "BRAK PLIKU PROBKI - odeslij mi ten wynik"; return }
Write-Host ("proba: " + $sample.FullName + "  (" + $sample.Length + " B)")
python $tool key --bundle $sample.FullName --passes 2 --wait 15 --report (Join-Path $work "key_report.json") --dump (Join-Path $work "candidates.bin")
```

Skrypt skanuje pamiec dwa razy (15 s przerwy), zeby zlapac klucz, ktory istnieje
tylko przez chwile. Wypisuje postep i na koncu jedna z trzech rzeczy:

- `FOUND ...: key ...` i `hits: 1 (verified: 1)` - klucz jest, lec do KROKU 4;
- `candidates by length: 32: 12 345, ...` ale `hits: 0` - skan widzi tablice
  w pamieci, tylko zaden kandydat nie pasuje. To konkretna informacja;
- `candidates by length: none` - w pamieci nie ma zadnych tablic 16/24/32 B.

**Sprawdz w raporcie linie `passes`:** musi byc `2`. Jesli jest `1`, to znaczy, ze
skrypt przeskanowal pamiec tylko raz i klucz mogl sie nie zalapac.

W obu przypadkach bez klucza odeslij mi `key_report.json` oraz (jesli sie zmiesci)
`candidates.bin` - to zrzut wszystkich sprawdzonych kandydatow, o ok. 15 MB. Dzieki
niemu sprawdzam nowe hipotezy u siebie, bez kolejnych przebiegow u Ciebie. Na tej podstawie wybieram nastepny ruch;
mam tez plan B, ktory w ogole nie potrzebuje klucza (opisany nizej).

## KROK 4 - dowod: odszyfrowanie prawdziwego pliku

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
Set-Location $work
$tool = (Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1).FullName
$bundles = "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64"
$sample = Get-ChildItem $bundles -Filter *.bundle -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -eq 940012 } | Select-Object -First 1
if (-not $sample) {
    $sample = Get-ChildItem $bundles -Filter *.bundle -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -gt 200000 -and $_.Length -lt 2000000 } |
        Sort-Object Length -Descending | Select-Object -First 1
}
if (-not $sample) { Write-Host "BRAK PLIKU PROBKI - odeslij mi ten wynik"; return }
python $tool decrypt --in $sample.FullName --out (Join-Path $work "decrypted.bundle") --report (Join-Path $work "key_report.json")
```

Oczekiwane:

```
srw_y_key 2026-10-26.8
mode: <jedna z nazw: ctr-le, ctr-be, cfb128, ofb>
unity: 2022.3.44f1, size <rozmiar tego pliku z przecinkiem> B
wrote ...\decrypted.bundle (<ten sam rozmiar> B)
```

To jest moment, w ktorym wiadomo, ze pliki da sie podmieniac: ten sam plik, ten
sam rozmiar, w srodku normalny naglowek Unity. Linia `mode:` mowi, jakiego szyfru
uzywa gra - bez tego nie da sie zapisac tlumaczenia z powrotem.

## Plan B, gdyby klucza nie bylo

Nie zalezy od klucza: skoro gra musi odszyfrowac bundle, zeby dzialac, to jej
pamiec zawiera **gotowy tekst** tych bundle (mamy ich juz 597 z poprzednich
przebiegow). Mamy tez zaszyfrowane pliki na dysku. Jesli rozmiar odszyfrowanego
bundle jest unikalny na dysku (276 takich rozmiarow), to para plaintext/ciphertext
jest wymuszona - a z pary wychodzi strumien szyfru, ktorym mozna podmienic tekst
bez znajomosci klucza. Do sprawdzenia tej drogi potrzebowalbym 2-3 **malych**
plikow `.bundle` z dysku (kilka kB kazdy) - powiem dokladnie ktore.

## Co odeslac

1. `key_report.json` z folderu `srwytool` na Pulpicie - zawiera tylko liczby i
   klucz, zadnego tekstu z gry.
2. Skopiowany tekst (albo zrzut ekranu) z KROKU 0, 1, 3 i 4.

## Czego ten krok jeszcze nie robi

Nie podmienia tekstu i nie tlumaczy - najpierw musi byc znany klucz i sposob
szyfrowania. Gdy KROK 4 pokaze `mode:` i plik sie otworzy, nastepny krok to
wyciagniecie tekstu z odszyfrowanych bundle, tlumaczenie w miejscu i zapis z
powrotem tym samym kluczem - czyli model zestawu OE: podmienione pliki, bez
uruchamiania czegokolwiek razem z gra.
