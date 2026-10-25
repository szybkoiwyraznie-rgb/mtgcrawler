# SRW Y - krok S3: klucz i podmiana plikow (jeden plik, ~5 minut)

Cel: wyciagnac z dzialajacej gry klucz, ktorym sa zaszyfrowane pliki `.bundle`,
a potem **odszyfrowac prawdziwy plik** i pokazac, ze wraca do gry bez zmiany
rozmiaru. To pierwsza polowa tego, co robi zestaw OE: podmiana tekstu w plikach.

Zmiany po nieudanym KROKU 0: nie ma juz zadnego pobierania z GitHuba (blad
SSL/TLS w PowerShell 5.1), nic nie jest zapisywane na `C:\` - wszystko idzie na
**Pulpit**, tak jak dotychczas. Jest tez **jeden** plik zamiast dwoch.

Skrypt czyta pamiec gry tylko do odczytu (`PROCESS_VM_READ`): nie zmienia gry, nie
instaluje modow, nie rusza zapisow.

Wersja do sprawdzenia: `srw_y_key 2026-10-26.2`.

## KROK 0 - folder na Pulpicie i pobranie skryptu z Drive

1. W przegladarce wejdz na swoje Google Drive, folder `SRW` -> `SRWY`, i pobierz
   plik `srw_y_key` (skrypt Pythona, jeden plik, kilkadziesiat kB). Laduje w
   `Pobrane`.
2. Uruchom PowerShell **jako administrator** i wklej caly blok. Tworzy folder
   `srwytool` na Pulpicie i przenosi do niego swiezo pobrany plik.

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
New-Item -ItemType Directory -Force -Path $work | Out-Null
$ext = [char]46 + "py"
$src = Get-ChildItem (Join-Path $env:USERPROFILE "Downloads") -File |
    Where-Object { $_.Extension -eq $ext -and $_.Name -like "*key*" } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $src) {
    Write-Host "BRAK PLIKU w Pobrane - pobierz go z Drive i uruchom blok jeszcze raz"
} else {
    Copy-Item $src.FullName $work -Force
    $tool = Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1
    Write-Host ("skrypt: " + $tool.FullName)
    Write-Host ("rozmiar: " + $tool.Length + " B")
}
```

`rozmiar` musi byc wiekszy od 10 000 B. Jesli jest `BRAK PLIKU`, plik nie trafil
do `Pobrane` - pobierz go z Drive jeszcze raz i powtorz blok.

## KROK 1 - biblioteka AES i test skryptu (bez gry)

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
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
$tool = (Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1).FullName
Set-Location $work
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

`proba:` musi wskazac istniejacy plik. Jesli jest puste, ten plik ma inna nazwe -
wtedy odeslij mi wynik tego polecenia i przejdziemy dalej.

Skrypt wypisuje postep (`scanned ... GB`) i na koncu jedna z dwoch rzeczy:

- `hits: 1 (verified: 1)` oraz `FOUND stream: key ... iv ...` - klucz jest;
- `hits: 0` - w pamieci nie bylo w tym momencie zadnego `byte[]` z kluczem.

Przy `hits: 0` nie zgadujemy: zrob w grze dwie-trzy akcje z tekstem (dialog, menu
jednostki) i uruchom KROK 3 jeszcze raz. Nadal zero - odeslij
`key_report.json`, to tez jest wynik.

## KROK 4 - dowod: odszyfrowanie prawdziwego pliku

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
$tool = (Get-ChildItem $work -Filter "*key*" -File | Select-Object -First 1).FullName
Set-Location $work
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
unity: 2022.3.44f1, size 940,012 B
wrote ...\decrypted.bundle (940,012 B)
```

To jest moment, w ktorym wiadomo, ze pliki da sie podmieniac: ten sam plik, ten
sam rozmiar, w srodku normalny naglowek Unity. Linia `mode:` mowi, jakiego szyfru
uzywa gra - bez tego nie da sie zapisac tlumaczenia z powrotem.

## Co odeslac

1. `key_report.json` z folderu `srwytool` na Pulpicie - zawiera tylko liczby i
   klucz, zadnego tekstu z gry.
2. Skopiowany tekst (albo zrzut ekranu) z KROKU 1, 3 i 4.

## Czego ten krok jeszcze nie robi

Nie podmienia tekstu i nie tlumaczy - najpierw musi byc znany klucz i sposob
szyfrowania. Gdy KROK 4 pokaze `mode:` i plik sie otworzy, nastepny krok to
wyciagniecie tekstu z odszyfrowanych bundle, tlumaczenie w miejscu i zapis z
powrotem tym samym kluczem - czyli model zestawu OE: podmienione pliki, bez
uruchamiania czegokolwiek razem z gra.
