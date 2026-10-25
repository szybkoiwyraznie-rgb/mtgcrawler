# SRW Y - krok S3: klucz i podmiana plikow (jeden plik, ~5 minut)

Cel: wyciagnac z dzialajacej gry klucz, ktorym sa zaszyfrowane pliki `.bundle`,
a potem **odszyfrowac prawdziwy plik** i pokazac, ze wraca do gry bez zmiany
rozmiaru. To pierwsza polowa tego, co robi zestaw OE: podmiana tekstu w plikach.

Co sie zmienilo po nieudanym KROKU 0:

- nie ma juz dwoch plikow - jest **jeden** (`srw_y_key`, wersja `2026-10-26.2`);
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
if ($f -and $f.Length -gt 15000) {
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
$sha  = "ad6286e9cee40bb81a313883446195931dbd7527"
$url  = "https" + [char]58 + "//raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/" + $sha + "/srw-y-translation/tools/" + $name
Remove-Item (Join-Path $work $name) -ErrorAction SilentlyContinue
try {
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile (Join-Path $work $name) -ErrorAction Stop
} catch {
    Write-Host ("pierwsza proba nie dala rady: " + $_.Exception.Message)
    curl.exe -L -o (Join-Path $work $name) $url
}
$f = Get-Item (Join-Path $work $name) -ErrorAction SilentlyContinue
if ($f -and $f.Length -gt 15000) {
    Write-Host ("OK  skrypt: " + $f.FullName + "  " + $f.Length + " B")
} else {
    Write-Host "BRAK PLIKU - skopiuj mi caly ten wynik"
}
```

W obu drogach musi pojawic sie `OK  skrypt: ...Desktop\srwytool\...` z rozmiarem
powyzej 15 000 B (plik ma ok. 23 kB). Jesli nie - odeslij mi wynik, to nie jest
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
srw_y_key 2026-10-26.2
  key test        ok
  byte[] scan     ok
  ctr-le        ok
  ctr-be        ok
  cfb128        ok
  ofb           ok
  cbc           ok
selftest: PASS
```

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
$sample = Get-ChildItem $bundles -Filter *.bundle | Where-Object { $_.Length -eq 940012 } |
    Select-Object -First 1
if (-not $sample) {
    $sample = Get-ChildItem $bundles -Filter *.bundle |
        Where-Object { $_.Length -gt 200000 -and $_.Length -lt 2000000 } |
        Sort-Object Length -Descending | Select-Object -First 1
}
if (-not $sample) { Write-Host "BRAK KANDYDATA - odeslij mi ten wynik"; return }
Write-Host ("proba: " + $sample.FullName + "  (" + $sample.Length + " B)")
python $tool key --bundle $sample.FullName --report (Join-Path $work "key_report.json")
```

Skrypt wypisuje postep (`scanned ... GB`) i na koncu jedna z dwoch rzeczy:

- `hits: 1 (verified: 1)` oraz `FOUND stream: key ... iv ...` - klucz jest;
- `hits: 0` - w pamieci nie bylo w tym momencie zadnego `byte[]` z kluczem.

Przy `hits: 0` nie zgadujemy: zrob w grze dwie-trzy akcje z tekstem (dialog, menu
jednostki) i uruchom KROK 3 jeszcze raz. Nadal zero - odeslij `key_report.json`,
to tez jest wynik.

## KROK 4 - dowod: odszyfrowanie prawdziwego pliku

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
Set-Location $work
$tool = (Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1).FullName
$bundles = "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64"
$sample = Get-ChildItem $bundles -Filter *.bundle | Where-Object { $_.Length -eq 940012 } |
    Select-Object -First 1
if (-not $sample) {
    $sample = Get-ChildItem $bundles -Filter *.bundle |
        Where-Object { $_.Length -gt 200000 -and $_.Length -lt 2000000 } |
        Sort-Object Length -Descending | Select-Object -First 1
}
if (-not $sample) { Write-Host "BRAK KANDYDATA - odeslij mi ten wynik"; return }
python $tool decrypt --in $sample.FullName --out (Join-Path $work "decrypted.bundle") --report (Join-Path $work "key_report.json")
```

Oczekiwane:

```
srw_y_key 2026-10-26.2
mode: <jedna z nazw: ctr-le, ctr-be, cfb128, ofb>
unity: 2022.3.44f1, size <rozmiar tego pliku> B
wrote ...\decrypted.bundle (<ten sam rozmiar> B)
```

To jest moment, w ktorym wiadomo, ze pliki da sie podmieniac: ten sam plik, ten
sam rozmiar, w srodku normalny naglowek Unity. Linia `mode:` mowi, jakiego szyfru
uzywa gra - bez tego nie da sie zapisac tlumaczenia z powrotem.

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
