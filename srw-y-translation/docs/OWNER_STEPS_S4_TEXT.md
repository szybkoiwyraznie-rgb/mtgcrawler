# SRW Y - krok S4: cztery pliki z tekstem (kopiowanie, 2 minuty)

Wersja arkusza: 2026-10-27.1

## Co sie zmienilo (najwazniejsze od poczatku projektu)

**Klucz jest zlamany.** Pliki `.bundle` w grze sa zaszyfrowane haslem, ktore siedzi
w danych gry; znalazlem je i sprawdzilem na **276 plikach** - kazdy odszyfrowuje sie
co do bajtu. Czyli:

- nie trzeba juz zadnego przebiegu gry ani grzebania w pamieci,
- pliki mozna odkodowac, podmienic tekst i zakodowac z powrotem **na dysku**,
- to dziala takze na duzych plikach z tekstem i scenariuszem, ktorych wczesniej nie
  mialem jak odczytac.

Czego jeszcze brakuje: **samych plikow z poczatkiem gry**. Mam liste wszystkich
plikow gry (nazwy i rozmiary), ale nie ich tresc. Stad ten krok - cztery kopie.

## KROK 1 - skopiuj cztery pliki na Pulpit

Uruchom PowerShell (Win+R -> `powershell` -> Enter) i wklej **caly** blok naraz.
Gra nie musi byc uruchomiona. Nic nie jest zmieniane w grze - to tylko kopiowanie.

```powershell
$src = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$out = Join-Path ([Environment]::GetFolderPath("Desktop")) "srw_y_text"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$files = @(
    '2d69c099bfdf0e252dabe84dbbba11df.bundle',
    '1cc7e02ee5711c6ba87a0e364f62198c.bundle',
    '1c12bbab8ed0f62ff22f808ce0138bc1.bundle',
    '8939a711c0d8a8fc00dee03e1013ecdb.bundle'
)
foreach ($f in $files) {
    $p = Join-Path $src $f
    if (-not (Test-Path $p)) { Write-Host ("BRAK: " + $f); continue }
    Copy-Item $p (Join-Path $out $f) -Force
    $len = (Get-Item $p).Length
    Write-Host ("{0}  {1:N0} B" -f $f.Substring(0,8), $len)
}
Get-ChildItem $out -File | Measure-Object -Property Length -Sum |
    ForEach-Object { "plikow: {0}   razem: {1:N0} B" -f $_.Count, $_.Sum }
Compress-Archive -Path "$out\*" -DestinationPath (Join-Path ([Environment]::GetFolderPath("Desktop")) "srw_y_text.zip") -Force
"zip: srw_y_text.zip"
```

Ma wyjsc (kolejno):

```
2d69c099   948,652 B
1cc7e02e   940,012 B
1c12bbab   5,591,151 B
8939a711   4,740,401 B
plikow: 4   razem: 12,220,216 B
zip: srw_y_text.zip
```

Jesli ktoras linia pokaze `BRAK:` - napisz mi ktora; znaczy, ze gra ma inna wersje
pliku i wtedy dobiorę inny (mam pelna liste rozmiarow z Twojego folderu).
Jesli pierwsza linia zglasza blad sciezki - popraw `$src` na wlasciwa i wklej blok
jeszcze raz.

## KROK 2 - wyslij mi `srw_y_text.zip`

Plik lezy na Pulpicie i ma ok. 12 MB. Wrzuc go na Dysk Google do folderu `SRW/SRWY`
albo dolacz do rozmowy.

## Co z tego bedzie

1. Odszyfruje oba pliki z tekstem i oba ze scenariuszem.
2. Znajde w nich **te narracje z poczatku** (te o wojnie miedzygwiezdnej 60 lat temu)
   - razem z wersja japonska, bo tlumacze z japonskiego, nie z angielskiego.
3. Podmienie tekst na polski, zakoduje z powrotem i wysle Ci **gotowe pliki .bundle**
   plus komende podmiany z kopia zapasowa (tak jak przy poprzednich probach, tylko
   ze dzialajacym tekstem na poczatku gry).

W tym kroku w grze nic nie podmieniamy: podmiana bedzie osobnym, krotkim krokiem.
Plikow nie zmieniasz i nie zmieniasz nazw - kopiujesz dokladnie te cztery.
