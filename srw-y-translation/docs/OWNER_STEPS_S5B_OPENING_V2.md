# SRW Y - krok S5b: polskie otwarcie, wersja 2 (po crashu)

Wersja arkusza: 2026-10-25.2

## Co poszlo nie tak i co zmienilem

Poprzednia paczka (`srw_y_pl_otwarcie_v1.zip`) wysypala gre przy starcie. Powod:
zbudowalem wtedy **caly** plik od nowa - pliki byly wieksze o ok. 10 kB, mialy inny
naglowek i poprzesuwane offsety. Gra tego nie przyjela.

Wersja 2 jest zrobiona inaczej - **nie przebudowuje pliku**:

- rozmiar jest **co do bajta taki sam** jak oryginalu (948 652 B i 940 012 B),
- naglowek i uklad blokow sa zachowane,
- **cala reszta pliku jest nietknieta** - zmienia sie wylacznie ten fragment,
  w ktorym siedzi tabela tekstu narracji (5 116 bajtow),
- tekst jest dopelniony spacjami do tej samej dlugosci, zeby nic sie nie przesunelo
  (spacje na koncu linii sa niewidoczne).

## KROK 0 - najpierw przywroc oryginaly

```powershell
$aa     = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$backup = Join-Path ([Environment]::GetFolderPath("Desktop")) "srw_y_backup_otwarcie"
if (Test-Path $backup) {
    Copy-Item (Join-Path $backup '*.bundle') $aa -Force
    "przywrocone z " + $backup
} else {
    "brak kopii zapasowej - nie ruszam niczego"
}
```

## KROK 1 - pobierz i rozpakuj wersje 2

Pobierz z Dysku Google `srw_y_pl_otwarcie_v2.zip` na **Pulpit**, potem:

```powershell
$desk = [Environment]::GetFolderPath("Desktop")
$dst  = Join-Path $desk "srw_y_pl2"
Expand-Archive -Path (Join-Path $desk "srw_y_pl_otwarcie_v2.zip") -DestinationPath $dst -Force
Get-ChildItem $dst -File | ForEach-Object { "{0}  {1:N0} B" -f $_.Name, $_.Length }
```

Maja wyjsc: `948 652 B`, `940 012 B` i `CZYTAJ_TO.txt`.

## KROK 2 - podmiana (gra zamknieta)

```powershell
$aa     = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$desk   = [Environment]::GetFolderPath("Desktop")
$src    = Join-Path $desk "srw_y_pl2"
$backup = Join-Path $desk "srw_y_backup_otwarcie"
New-Item -ItemType Directory -Force -Path $backup | Out-Null

$plan = @(
    @{ f = '2d69c099bfdf0e252dabe84dbbba11df.bundle';
       old = 'ce764acecf93a0f0d4d341195e9a69b9e5f42b6414c4401e9d977817db775b79';
       new = '08bc13517dd7c354da2b6956ca0ec3ec51d8ab63c3e8e65fded11714e40879c5' },
    @{ f = '1cc7e02ee5711c6ba87a0e364f62198c.bundle';
       old = 'a209190eeac1ec32bd6f0979dbf8ff53d0960b7cdc8818d94604f9979bb1a9c1';
       new = 'c92c8764e6a62025d60870c4b648106f90a7874aa6f1017025d45b12a48f7672' }
)

foreach ($p in $plan) {
    $game = Join-Path $aa $p.f
    $pat  = Join-Path $src $p.f
    if (-not (Test-Path $game)) { Write-Host ("BRAK W GRZE: " + $p.f); continue }
    if (-not (Test-Path $pat))  { Write-Host ("BRAK W PACZCE: " + $p.f); continue }
    $hOld = (Get-FileHash $game -Algorithm SHA256).Hash.ToLower()
    $hNew = (Get-FileHash $pat  -Algorithm SHA256).Hash.ToLower()
    if ($hNew -ne $p.new) { Write-Host ("USZKODZONA PACZKA: " + $p.f); continue }
    if ($hOld -ne $p.old) { Write-Host ("UWAGA: w grze jest inny plik niz oryginal (" + $p.f.Substring(0,8) + ") - nadpisuje, kopia do backupu") }
    if (-not (Test-Path (Join-Path $backup $p.f))) { Copy-Item $game (Join-Path $backup $p.f) -Force }
    Copy-Item $pat $game -Force
    $hAfter = (Get-FileHash $game -Algorithm SHA256).Hash.ToLower()
    if ($hAfter -eq $p.new) { Write-Host ("OK  " + $p.f.Substring(0,8)) }
    else { Write-Host ("BLAD PODMIANY: " + $p.f) }
}
```

Maja wyjsc dwie linie `OK`.

## KROK 3 - uruchom gre

Jesli dziala: napisz, czy tekst jest po polsku i czy widac ogonki.

**Jesli nadal sie wysypuje** - potrzebuje logu gry, on mowi dokladnie, co sie stalo:

```powershell
$desk = [Environment]::GetFolderPath("Desktop")
$log = Get-ChildItem "$env:USERPROFILE\AppData\LocalLow" -Recurse -Filter "Player.log" -ErrorAction SilentlyContinue |
       Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($log) {
    Copy-Item $log.FullName (Join-Path $desk "srw_y_Player.log") -Force
    "skopiowane: " + $log.FullName
} else { "nie znalazlem Player.log" }
```

Wtedy wyslij mi `srw_y_Player.log` z Pulpitu (to zwykly plik tekstowy, kilka kB).

## COFNIECIE - jak zwykle

KROK 0 powyzej przywraca oryginaly z `Pulpit\srw_y_backup_otwarcie`.

## Stany

| pytanie | odpowiedz |
|---|---|
| podmieniac ISO? | **NIE** (wersja PC) |
| przerabiac DLC? | **NIE** (te pliki sa z podstawki) |
| PBOOT? | **NIE** |

## Czego nie wiem

- czy gra sprawdza sume kontrolna pliku z katalogu Addressables; jesli tak, zadna
  podmiana tekstu nie przejdzie bez podmiany katalogu - log z KROKU 3 powie to wprost
- czy czcionka ma polskie znaki
- paczki nie moglem uruchomic u siebie (brak PowerShella i gry w srodowisku, w ktorym
  pracuje); sprawdzilem tylko, ze plik daje sie odszyfrowac, ma ten sam rozmiar,
  ten sam naglowek i te same obiekty co oryginal
