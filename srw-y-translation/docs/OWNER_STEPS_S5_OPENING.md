# SRW Y - krok S5: polskie otwarcie gry (2 pliki, 3 minuty)

Wersja arkusza: 2026-10-25.1

## Co to jest

**Polski tekst narracji otwierajacej gre** - te 24 ekrany, ktore leca na starcie
(pierwszy z nich zaczyna sie od "The Earth."). Przetlumaczone z **japonskiego**,
nie z angielskiego.

Podmienione sa dwa pliki - tabela tekstu angielskiego i tabela tekstu japonskiego,
wiec zadziala niezaleznie od tego, w jakim jezyku masz ustawiona gre:

```
2d69c099bfdf0e252dabe84dbbba11df.bundle    958 140 B   tekst angielski
1cc7e02ee5711c6ba87a0e364f62198c.bundle    950 862 B   tekst japonski
```

Jak to zrobione: plik jest odszyfrowywany kluczem z gry (klucz zlamany w S3),
tekst jest podmieniany w tabeli, plik jest zapisywany i **szyfrowany z powrotem
tym samym kluczem**. Wszystko na dysku - gra nie musi byc uruchomiona, nic nie
jest czytane z pamieci.

Jedna roznica, ktora zobaczysz w rozmiarach: pliki sa o ok. 10 kB wieksze od
oryginalow (948 652 -> 958 140 i 940 012 -> 950 862). To normalne - polski tekst
ma inna dlugosc niz angielski. Gra nie porownuje rozmiaru pliku.

## KROK 1 - pobierz i rozpakuj (Pulpit)

Pobierz z Dysku Google `srw_y_pl_otwarcie_v1.zip` na **Pulpit**, potem wklej:

```powershell
$desk = [Environment]::GetFolderPath("Desktop")
$dst  = Join-Path $desk "srw_y_pl"
Expand-Archive -Path (Join-Path $desk "srw_y_pl_otwarcie_v1.zip") -DestinationPath $dst -Force
Get-ChildItem $dst -File | ForEach-Object { "{0}  {1:N0} B" -f $_.Name, $_.Length }
```

Maja wyjsc trzy pozycje: `958 140 B`, `950 862 B` i `CZYTAJ_TO.txt`.

## KROK 2 - kopia zapasowa i podmiana (gra zamknieta)

Zamknij gre. Wklej **caly** blok:

```powershell
$aa     = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$desk   = [Environment]::GetFolderPath("Desktop")
$src    = Join-Path $desk "srw_y_pl"
$backup = Join-Path $desk "srw_y_backup_otwarcie"
New-Item -ItemType Directory -Force -Path $backup | Out-Null

$plan = @(
    @{ f = '2d69c099bfdf0e252dabe84dbbba11df.bundle';
       old = 'ce764acecf93a0f0d4d341195e9a69b9e5f42b6414c4401e9d977817db775b79';
       new = 'e62ba6e39b5e4e0ce13c4bbd773bf48138141d6ef23006ba5424006d6fd04a7e' },
    @{ f = '1cc7e02ee5711c6ba87a0e364f62198c.bundle';
       old = 'a209190eeac1ec32bd6f0979dbf8ff53d0960b7cdc8818d94604f9979bb1a9c1';
       new = 'c5dc63ebb3f70af5a23646119dfae02250b5050392c881d3864a3c7caed2e294' }
)

foreach ($p in $plan) {
    $game = Join-Path $aa $p.f
    $pat  = Join-Path $src $p.f
    if (-not (Test-Path $game)) { Write-Host ("BRAK W GRZE: " + $p.f); continue }
    if (-not (Test-Path $pat))  { Write-Host ("BRAK W PACZCE: " + $p.f); continue }
    $hOld = (Get-FileHash $game -Algorithm SHA256).Hash.ToLower()
    $hNew = (Get-FileHash $pat  -Algorithm SHA256).Hash.ToLower()
    if ($hOld -ne $p.old) { Write-Host ("INNY PLIK W GRZE: " + $p.f + " (kto inny go zmienil?)"); continue }
    if ($hNew -ne $p.new) { Write-Host ("USZKODZONA PACZKA: " + $p.f); continue }
    Copy-Item $game (Join-Path $backup $p.f) -Force
    Copy-Item $pat  $game -Force
    $hAfter = (Get-FileHash $game -Algorithm SHA256).Hash.ToLower()
    if ($hAfter -eq $p.new) { Write-Host ("OK  " + $p.f.Substring(0,8)) }
    else { Write-Host ("BLAD PODMIANY: " + $p.f) }
}
```

Na koncu maja byc dwie linie `OK`: `OK  2d69c099` i `OK  1cc7e02e`.
Oryginaly leza w `Pulpit\srw_y_backup_otwarcie`.

## KROK 3 - uruchom gre i powiedz, co widzisz

Uruchom gre i dojdz do narracji otwierajacej. Napisz mi trzy rzeczy:

1. czy tekst jest **po polsku**,
2. czy widac **wszystkie ogonki** (a c e l n o s z z - pelny zestaw),
3. czy ktoras linia wychodzi za ramke albo sie urywa.

## Cofniecie zmiany

```powershell
$aa     = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$backup = Join-Path ([Environment]::GetFolderPath("Desktop")) "srw_y_backup_otwarcie"
Copy-Item (Join-Path $backup '*.bundle') $aa -Force
"przywrocone"
```

## Stany, o ktore pytasz przy kazdej paczce

| pytanie | odpowiedz |
|---|---|
| podmieniac ISO? | **NIE** - to wersja PC, nie ma ISO |
| przerabiac DLC? | **NIE** - te dwa pliki sa z podstawki |
| PBOOT? | **NIE** - to nie PSP |

Nie uruchamiaj "sprawdz pliki" w kliencie gry i nie aktualizuj gry przed testem -
jedno i drugie nadpisze podmienione pliki.

## Czego jeszcze nie wiem (mowie wprost)

- **Nie wiem, czy gra sprawdza sume kontrolna pliku** z katalogu Addressables.
  Jesli gra zignoruje podmiane (zobaczysz angielski tekst), to bedzie wlasnie to
  i wtedy trzeba bedzie podmienic takze wpis w katalogu - tez sie da, bo katalog
  jest odszyfrowany.
- **Nie wiem, czy czcionka ma polskie znaki.** To pierwsza rzecz, ktora zobaczysz.
- Tego bloku nie uruchamialem u siebie - w piaskownicy nie ma PowerShella ani gry.
  Skrypt jest napisany pod PowerShell 5.1 i nie uzywa niczego, czego ta wersja
  nie ma.
