# Krok S1 — inwentaryzacja folderu gry (dla właściciela)

Cel: poznać **położenie i rozmiary plików**, żeby znaleźć kontener z tekstem.
Raport zawiera tylko: ścieżki względne, rozmiary i typ pliku rozpoznany po
pierwszych bajtach. **Nie zawiera treści plików ani Twojej nazwy użytkownika**
(prefiks folderu jest obcinany), więc można go bez obaw wysłać.

Wszystko wpisuj w **PowerShellu** (konsola z `PS D:\…>`). Dwie uwagi, bo na tym
się wysypało:

- `dir /s` to składnia `cmd.exe`. W PowerShellu `dir` to alias `Get-ChildItem`,
  a `/s` jest czytane jako ścieżka — stąd `Cannot find path 'D:\s'`.
- Skrypty **nie leżą** w folderze gry. Trzeba je najpierw pobrać (poniżej), a
  nazwa pliku to dokładnie `inventory_build.py` — bez `https://` i bez nawiasów,
  które doklejło formatowanie czatu.

## Wariant A — Python 3.12 (zalecany; to narzędzie ma testy w repo)

```powershell
$u = "https://raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/arena/6906ed6b-mtgcrawler/srw-y-translation/tools/inventory_build.py"
Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile "$env:TEMP\inventory_build.py"
python "$env:TEMP\inventory_build.py" --root "D:\Games\SUPER ROBOT WARS Y" --out "$env:USERPROFILE\Desktop\build_report.json"
explorer "$env:USERPROFILE\Desktop"
```

Na konsoli zobaczysz podsumowanie (liczba plików, rodziny kontenerów), a na
pulpicie powstanie `build_report.json`.

## Wariant B — PowerShell, bez Pythona

```powershell
$u = "https://raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/arena/6906ed6b-mtgcrawler/srw-y-translation/tools/inventory_build.ps1"
Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile "$env:TEMP\inventory_build.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:TEMP\inventory_build.ps1" -Root "D:\Games\SUPER ROBOT WARS Y"
explorer "$env:USERPROFILE\Desktop"
```

Raport: `srw_y_inventory.txt`. Skrypt jest napisany pod Windows PowerShell 5.1
i nie był uruchamiany w moim środowisku (nie mam tu PowerShella), więc jeśli
cokolwiek w nim zgrzytnie — napisz, co dokładnie wypisał, i poprawię. Wariant A
jest sprawdzony testami, więc w razie wątpliwości wybierz A.

## Wariant C — bez pobierania czegokolwiek

Wystarczy lista plików z rozmiarami:

```powershell
Get-ChildItem -LiteralPath "D:\Games\SUPER ROBOT WARS Y" -Recurse -File |
  ForEach-Object { "{0}`t{1}" -f $_.Length, $_.FullName.Substring(24) } |
  Set-Content -LiteralPath "$env:USERPROFILE\Desktop\listing_sizes.txt" -Encoding UTF8
```

(`24` to długość ścieżki `D:\Games\SUPER ROBOT WARS Y`; jeśli Twoja jest inna,
podmień liczbę albo użyj wariantu A.)

## Co dalej

Wrzuć wynik (`build_report.json`, `srw_y_inventory.txt` albo `listing_sizes.txt`)
do folderu Drive **`SRW/SRWY`**
(<https://drive.google.com/drive/folders/1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr>) —
nic więcej na tym etapie nie jest potrzebne. Na tej podstawie wskażę kontener
z tekstem i poproszę o **jeden mały** plik do pomiaru, nie o całą grę.

## Czego nie robimy

- Nie wysyłasz folderu gry, nie kopiujesz `.exe`, `.dll`, kontenerów ani zapisów.
- Nic nie jest modyfikowane: narzędzia tylko czytają 16 bajtów z każdego pliku.
