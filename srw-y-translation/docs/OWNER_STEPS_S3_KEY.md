# SRW Y - krok S3: klucz i podmiana plikow (jeden przebieg, ~5 minut)

Cel: wyciagnac z dzialajacej gry klucz, ktorym sa zaszyfrowane pliki `.bundle`,
a potem **odszyfrowac prawdziwy plik** i pokazac, ze wraca do gry bez zmiany
rozmiaru. To jest pierwsza polowa tego, co robi zestaw OE: podmiana tekstu
w plikach. Nic tu nie jest zgadywane - skrypt sam sprawdza wynik.

Skrypt czyta pamiec gry tylko do odczytu (`PROCESS_VM_READ`). Nie zmienia gry,
nie instaluje modow, nie rusza zapisow.

Wersje do sprawdzenia: `key_from_memory 2026-10-26.1`, `bundle_crypt 2026-10-26.1`.
Plik jest przypiety do commita `e5a44657abb48408e4063a117261d6cee731bbee`, wiec
zawsze pobierze sie ta sama, przetestowana wersja.

## KROK 0 - folder roboczy i pobranie skryptow

Uruchom PowerShell **jako administrator** (skan pamieci tego wymaga) i wklej
caly blok. Tworzy `C:\srwytool` i pobiera dwa skrypty.

```powershell
$work = "C:\srwytool"
$sha  = "e5a44657abb48408e4063a117261d6cee731bbee"
$base = "https" + [char]58 + "//raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/" + $sha + "/srw-y-translation/tools/"
New-Item -ItemType Directory -Force -Path $work | Out-Null
Set-Location $work
Remove-Item .\key_from_memory.py, .\bundle_crypt.py -ErrorAction SilentlyContinue
foreach ($f in @("key_from_memory.py", "bundle_crypt.py")) {
    Invoke-WebRequest -UseBasicParsing -Uri ($base + $f) -OutFile (Join-Path $work $f)
}
foreach ($f in @("key_from_memory.py", "bundle_crypt.py")) {
    $len = (Get-Item (Join-Path $work $f)).Length
    Write-Host ("{0}  {1} B" -f $f, $len)
}
```

Oczekiwane rozmiary: `key_from_memory.py` ok. 13 300 B, `bundle_crypt.py` ok.
9 000 B. Zera albo blad 404 znacza, ze pobralo sie zly adres - przerwij i napisz.

## KROK 1 - biblioteka AES i sprawdzenie wersji

```powershell
Set-Location "C:\srwytool"
python -m pip install --upgrade pycryptodome
python .\key_from_memory.py --selftest
python .\bundle_crypt.py --selfcheck
```

Oczekiwane (dokladnie te linie, bez bledow):

```
key_from_memory 2026-10-26.1
self-test: PASS (3 arrays, 1 hits)
bundle_crypt 2026-10-26.1
  ctr-le   ok
  ctr-be   ok
  cfb128   ok
  ofb      ok
  cbc      ok
```

Jesli `python` nie jest rozpoznany, uzyj `py` zamiast `python` w calej instrukcji.

## KROK 2 - uruchom gre i wczytaj scene z tekstem

1. Uruchom `SUPER ROBOT WARS Y` normalnie (Steam lub skrot).
2. Wczytaj **zapis** albo zacznij misje tak, zeby na ekranie byly dialogi.
   To nie jest formalnosc: klucz i odszyfrowane bundle sa w pamieci tylko wtedy,
   gdy gra juz ich uzywa.
3. Zostaw gre wlaczona i wroc do okna PowerShell.

## KROK 3 - szukanie klucza (1-3 minuty)

```powershell
Set-Location "C:\srwytool"
$game = "D:\Games\SUPER ROBOT WARS Y"
$sample = Join-Path $game "SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64\1cc7e02ee5711c6ba87a0e364f62198c.bundle"
Test-Path $sample
python .\key_from_memory.py --bundle $sample --report .\key_report.json
```

`Test-Path` musi wypisac `True`. Jesli wypisze `False`, ten plik ma inna nazwe -
wtedy podaj mi wynik tego polecenia:

```powershell
Get-ChildItem "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64" -Filter *.bundle |
    Where-Object { $_.Length -eq 940012 } | Select-Object -First 3 Name, Length
```

Skrypt wypisuje postep (`scanned ... GB`) i na koncu jedna z dwoch rzeczy:

- `hits: 1 (verified: 1)` i linie `FOUND stream: key ... iv ...` - klucz jest;
- `hits: 0` - w pamieci nie bylo w tym momencie zadnego `byte[]` z kluczem.

Przy `hits: 0` nie zgadujemy dalej: przejdz do KROKU 2, zrob w grze dwie-trzy
akcje z tekstem (otworz dialog, wejdz w menu jednostki), i uruchom KROK 3 jeszcze
raz. Nadal zero - odeslij `key_report.json`, to tez jest wynik.

## KROK 4 - dowod: odszyfrowanie prawdziwego pliku

```powershell
Set-Location "C:\srwytool"
$game = "D:\Games\SUPER ROBOT WARS Y"
$sample = Join-Path $game "SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64\1cc7e02ee5711c6ba87a0e364f62198c.bundle"
python .\bundle_crypt.py --report .\key_report.json --decrypt $sample .\decrypted.bundle
```

Oczekiwane:

```
bundle_crypt 2026-10-26.1
mode: <jedna z nazw: ctr-le, ctr-be, cfb128, ofb>
unity: 2022.3.44f1, size 940,012 B
wrote ...\decrypted.bundle (940,012 B)
```

To jest moment, w ktorym wiadomo, ze pliki da sie podmieniac: ten sam plik, ten
sam rozmiar, w srodku normalny naglowek Unity. `mode:` mowi, jakiego szyfru
uzywa gra - bez tego nie da sie zapisac tlumaczenia z powrotem.

## Co odeslac

1. `key_report.json` (`C:\srwytool\key_report.json`) - male, zawiera tylko liczby
   i klucz, zadnego tekstu z gry.
2. Zrzut ekranu albo skopiowany tekst z KROKU 1, 3 i 4.

## Czego ten krok jeszcze nie robi

Nie podmienia tekstu i nie tlumaczy - najpierw musi byc znany klucz i sposob
szyfrowania. Gdy KROK 4 pokaze `mode:` i plik sie otworzy, nastepny krok to
wyciagniecie tekstu z odszyfrowanych bundle, tlumaczenie w miejscu i zapis z
powrotem tym samym kluczem, czyli dokladnie model zestawu OE: podmienione pliki,
bez uruchamiania czegokolwiek razem z gra.
