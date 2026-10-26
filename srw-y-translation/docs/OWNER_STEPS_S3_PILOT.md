# SRW Y - krok S3, test mechaniki: 3 podmienione pliki (ok. 3 minuty)

Wersja arkusza: 2026-10-26.10

## Co to jest, a co nie jest

To **nie jest tlumaczenie**. To sprawdzenie jednej rzeczy: czy plik `.bundle`,
ktory odszyfrowalismy w pamieci gry, podmienilismy w nim tekst i **zaszyfrowalismy
z powrotem bez znajomosci klucza**, jest przez gre przyjmowany.

Dlaczego to dziala bez klucza: dla kazdego z 276 plikow mamy dwie wersje tego
samego pliku - zaszyfrowana z dysku i odszyfrowana z pamieci gry. Roznica miedzy
nimi to strumien szyfru, ktory zalezy tylko od klucza i od danego pliku, a nie od
tresci. Wiec podmieniamy tekst, dopelniamy do **dokladnie tego samego rozmiaru**
i przepuszczamy przez ten sam strumien.

Trzy podmienione pliki (nazwy sa takie same jak na dysku, rozmiary bez zmian):

```
a74bb2064bfce43f2d6f0f77b93c062e.bundle   11 469 B   tytuly muzyki (BGM)
f547a4144fd374dcf0ccdcbbdfa11267.bundle    7 201 B   opisy zdolnosci broni
cd75854d1b55ad6dde2d3c915cf5b5f4.bundle   14 420 B   ekran przekazania danych
```

Tekst polski jest dopelniony spacjami do tej samej liczby bajtow, wiec w grze
moze wygladac nierowno (spacje na koncu). To celowe - dzieki temu plik ma ten sam
rozmiar i nic w nim nie przesuwa sie.

## KROK 1 - rozpakuj paczke na Pulpit

Pobierz z Dysku Google plik `srw_y_pilot.zip` i zapisz go na **Pulpicie**
(3 pliki, 33 090 B po rozpakowaniu). Potem wklej:

```powershell
$desk  = [Environment]::GetFolderPath("Desktop")
$pilot = Join-Path $desk "srw_y_pilot"
New-Item -ItemType Directory -Force -Path $pilot | Out-Null
Expand-Archive -Path (Join-Path $desk "srw_y_pilot.zip") -DestinationPath $pilot -Force
Get-ChildItem $pilot -File | Measure-Object -Property Length -Sum |
    ForEach-Object { "plikow: {0}   razem: {1:N0} B" -f $_.Count, $_.Sum }
```

Ma wyjsc `plikow: 3` i `razem: 33 090 B`.

## KROK 2 - kopia zapasowa i podmiana

```powershell
$aa     = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$desk   = [Environment]::GetFolderPath("Desktop")
$pilot  = Join-Path $desk "srw_y_pilot"
$backup = Join-Path $desk "srw_y_backup"
New-Item -ItemType Directory -Force -Path $backup | Out-Null
$files = @(
    'a74bb2064bfce43f2d6f0f77b93c062e.bundle',
    'f547a4144fd374dcf0ccdcbbdfa11267.bundle',
    'cd75854d1b55ad6dde2d3c915cf5b5f4.bundle'
)
foreach ($f in $files) {
    $src = Join-Path $aa $f
    if (-not (Test-Path $src)) { Write-Host ("BRAK PLIKU: " + $src); continue }
    Copy-Item $src (Join-Path $backup $f) -Force
    $before = (Get-Item $src).Length
    Copy-Item (Join-Path $pilot $f) $src -Force
    $after = (Get-Item $src).Length
    Write-Host ("{0}  {1:N0} B -> {2:N0} B" -f $f, $before, $after)
}
Write-Host ("kopie zapasowe: " + $backup)
```

Kazda linia musi pokazac **ten sam rozmiar przed i po** (11 469 / 7 201 / 14 420).

## KROK 3 - uruchom gre i sprawdz, co widac

Gra musi wystartowac normalnie. Szukaj polskiego tekstu w trzech miejscach:

1. **Biblioteka muzyki / BGM** (ekran z lista utworow): tytuly `POLSKI
   AKCELERATOR`, `Monolog w kolorach`, `POLSKA TEQUILA 1.0`, `TYTUL 1.0!`,
   `juz nie ustanie`, `MAKSYMALNY 3.5!`, `OSTATNIE WRAZEN`.
2. **Opis zdolnosci broni** (szczegoly jednostki/broni): slowa `Pancerz`,
   `Zwrotn.`, `Regen. HP`, `Mentalne`, `Spadek mor.`, `wlas. BEAM`,
   `Po ruchu: uzyc OK!!`.
3. **Ekran przekazania danych** (po ukonczeniu gry / import danych): `Przekaz.`,
   `Zdobyte do konca gry`, `Zestrzelenia pilotow`, `Limit ulepszen`.

Jesli widzisz polski tekst - mechanika dziala i mozna nia tlumaczyc cala gre.
Jesli gre masz ustawiona na inny jezyk, czesc z tych napisow moze sie nie
pokazac (kazdy jezyk ma swoja tabele) - napisz, w jakim jezyku grasz.

## KROK 4 - cofniecie zmian (do zrobienia zawsze po tescie)

```powershell
$aa     = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$backup = Join-Path ([Environment]::GetFolderPath("Desktop")) "srw_y_backup"
Get-ChildItem $backup -Filter *.bundle -File | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $aa $_.Name) -Force
    Write-Host ("przywrocono: " + $_.Name)
}
```

## Co odeslac

Jedno zdanie: czy polski tekst jest widoczny, i w ktorym z trzech miejsc. Jesli
gra sie nie uruchomila albo cos zniknelo z ekranu - tez napisz, to znaczy, ze
zaszyfrowana wersja jest zla i wracamy do szukania klucza.
