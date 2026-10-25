# SRW Y - poczatek gry: wyciecie tekstu z pamieci (jeden przebieg, ~5 minut)

Wersja arkusza: 2026-10-26.11

## Po co to jest

Pliki z tekstem sa zaszyfrowane, a klucza nie ma. Zeby podmienic tekst bez klucza,
potrzebuje **odszyfrowanej** wersji tego konkretnego pliku - i jedyne miejsce, gdzie
ona istnieje, to pamiec uruchomionej gry, ktora ten tekst wlasnie wyswietla.

Twoje zdanie z ekranu jest latarka: skrypt szuka go w pamieci gry i wycina **caly
plik**, w ktorym on lezy. Przy okazji zabiera tabele tekstow (angielska i japonska)
oraz skrypty scenariuszy, wiec kolejne napisy bede mogl podmieniac bez nastepnych
przebiegow.

Nic nie jest zapisywane do gry. Skrypt tylko czyta pamiec (`PROCESS_VM_READ`).

## KROK 0 - skrypt na Pulpit

PowerShell uruchom **jako administrator** (skrypt czyta pamiec innego procesu).
Wklej caly blok:

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
New-Item -ItemType Directory -Force -Path $work | Out-Null
Set-Location $work
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$name = "srw_y_find_text" + [char]46 + "py"
$sha  = "297b3bedd568b0d0039a5a21a7b6885c24b197dd"
$url  = "https" + [char]58 + "//raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/" + $sha + "/srw-y-translation/tools/" + $name
Remove-Item (Join-Path $work $name) -ErrorAction SilentlyContinue
try {
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile (Join-Path $work $name) -ErrorAction Stop
} catch {
    Write-Host ("pierwsza proba nie dala rady: " + $_.Exception.Message)
    curl.exe -L -o (Join-Path $work $name) $url
}
$f = Get-Item (Join-Path $work $name) -ErrorAction SilentlyContinue
if ($f -and $f.Length -gt 25000) {
    Write-Host ("OK  skrypt: " + $f.FullName + "  " + $f.Length + " B")
} else {
    Write-Host "BRAK PLIKU - skopiuj mi caly ten wynik"
}
```

Ma wyjsc `OK  skrypt: ...\Desktop\srwytool\srw_y_find_text.py` z rozmiarem
powyzej 25 000 B (plik ma ok. 26 kB).

## KROK 1 - doprowadz gre do tekstu z poczatku

1. Uruchom `SUPER ROBOT WARS Y` i dojdz do ekranu z narracja, ktora wkleiles
   (ta o wojnie miedzygwiezdnej 60 lat temu).
2. **Zostaw ten tekst na ekranie** i nie klikaj dalej - skrypt szuka go w pamieci
   wlasnie wtedy, gdy gra go trzyma.
3. Wroc do PowerShella (dalej jako administrator).

## KROK 2 - skan pamieci (ok. 1 minuty)

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
Set-Location $work
$needle = @'
Sixty years ago, interstellar war ravaged our planet
'@
Set-Content -Path (Join-Path $work "needle.txt") -Value $needle -Encoding UTF8
$tool = (Get-ChildItem $work -Filter "*find*" -File | Select-Object -First 1).FullName
python $tool "scan" --process "SUPER ROBOT WARS Y.exe" --needle-file (Join-Path $work "needle.txt") --out (Join-Path $work "opening")
```

Jesli `python` nie jest rozpoznany, uzyj `py` zamiast `python`.

Co powinno pojawic sie na koncu (liczby moga byc inne):

```
hits: 1, bundles: 1, contexts: 0, scanned 1.80 GB
  bundle    948,652 B  bundle_0x..._....bundle
  en-US text table (large)   known_2d69c099....bundle  948,652 B
  ja-JP text table (large)   known_1cc7e02e....bundle  940,012 B
report: ...\Desktop\srwytool\opening\find_report.json
send me the whole folder - it is small
```

Wazne sa dwie rzeczy: `hits:` wieksze od zera oraz lista `known_` - to tabele tekstow.

## KROK 3 - spakuj i wyslij

```powershell
$work = Join-Path ([Environment]::GetFolderPath("Desktop")) "srwytool"
Compress-Archive -Path (Join-Path $work "opening\*") -DestinationPath (Join-Path $work "srw_y_opening.zip") -Force
Get-Item (Join-Path $work "srw_y_opening.zip") | ForEach-Object { "zip: " + $_.FullName + "  " + $_.Length + " B" }
```

Wyslij `srw_y_opening.zip` na Dysk Google tak jak poprzednio. Folder moze miec od
kilku do kilkunastu MB - to normalne, bo w srodku sa tabele tekstow.

## Jesli `hits: 0`

Napisz mi to i odeslij `find_report.json` (jest w folderze `opening`). Najczestsze
przyczyny i co wtedy zrobic:

- **tekst nie jest na ekranie** - skrypt musi byc uruchomiony, gdy napis jest widoczny;
- **tekst jest skladany z kilku kawalkow** - wtedy uruchom jeszcze raz, podmieniajac
  w bloczkach KROKU 2 linie `$needle` na krotszy fragment, np. `Sixty years ago`;
- **gra trzyma tekst inaczej** - w folderze `opening` pojawi sie plik `context_...bin`;
  jego tez wyslij, pokaze mi format.

## Co z tego dostaniesz

Jeden podmieniony plik z polskim poczatkiem gry plus bloczek, ktory go wgrywa i
(cofa). Polski tekst musi zmiescic sie w tej samej liczbie **bajtow** co angielski
(326), bo plik musi zachowac rozmiar - mam juz dwie wersje tlumaczenia: wierna
(338 B) i krotsza (255 B, zawsze wchodzi). Ktora pojdzie, okaze sie po obejrzeniu
pliku.

Potem kolejne napisy: wklejasz tekst z ekranu, ja podmieniam i odsylam plik - bez
nastepnych przebiegow, dopoki wszystkie potrzebne tabele sa w tym zipie.
