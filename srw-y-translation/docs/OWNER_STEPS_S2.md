# Krok S2 — znaleźć tekst w grze (dla właściciela)

Dzięki Twojemu listingowi wiem już, jak gra jest zbudowana — i to dobra
wiadomość: tekst jest w zwykłych plikach Unity, a nie w jednym wielkim kontenerze
CRI (jak w SRW 30/V). Szczegóły w `STATUS.md`, sekcja „S1 result”.

Teraz potrzebuję **jednego pliku-indeksu**, który mówi, co siedzi w którym
bundlu. Bez niego pliki w grze nazywają się jak
`2e1c004184c62d08997e13aed13a1004.bundle` i nie da się zgadnąć, który zawiera
dialogi.

## Co konkretnie

```
D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\catalog.json
```

rozmiar **41 543 062 B** (39,6 MiB).

To indeks Addressables: mapa „nazwa assetu → bundle”. **Nie zawiera tekstu gry
ani dialogów** — same nazwy assetów i numery bundli. Wysyłasz go raz, ja robię z
niego krótką listę kandydatów i wtedy poproszę Cię o **jeden lub dwa** bundle
(po kilka MiB), a nie o całe 20 GB.

## Wariant A — najlepszy: przeciągnij plik na Dysk Google

1. Otwórz folder z plikiem:

```powershell
explorer "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa"
```

2. Przeciągnij `catalog.json` do folderu **`SRW/SRWY`** na Dysku Google (ten sam,
   do którego trafił `listing_sizes.txt`). Możesz też użyć „Nowy → Wgranie pliku”
   i wskazać tę ścieżkę.

Nic więcej nie trzeba — nie zmieniasz niczego w grze, plik tylko się kopiuje.

## Wariant B — jeśli wolisz nie wysyłać 40 MB

Poniższy blok wyciąga z tego samego pliku **tylko listę nazw** (kilkaset KB) i
zapisuje ją na pulpicie jako `catalog_strings.txt`. Wklej całość do PowerShella:

```powershell
$src = "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\catalog.json"
$raw = Get-Content -LiteralPath $src -Raw
$out = New-Object System.Collections.Generic.List[string]
foreach ($m in [regex]::Matches($raw, '"m_[A-Za-z]+String"\s*:\s*"([A-Za-z0-9+/=]+)"')) {
  $bytes = [Convert]::FromBase64String($m.Groups[1].Value)
  $text  = [Text.Encoding]::UTF8.GetString($bytes)
  foreach ($s in ($text -split '[\x00-\x1F]+')) { if ($s.Length -ge 6) { $out.Add($s) } }
}
$dest = "$env:USERPROFILE\Desktop\catalog_strings.txt"
$out | Sort-Object -Unique | Set-Content -LiteralPath $dest -Encoding UTF8
"gotowe: " + (Get-Item -LiteralPath $dest).Length + " B -> " + $dest
```

Na końcu wypisze rozmiar pliku — powinno być od kilkuset KB w górę. Ten plik
wgraj do **`SRW/SRWY`** zamiast `catalog.json`.

> Uczciwie: tego bloku nie uruchamiałem u siebie (nie mam w moim środowisku
> PowerShella), więc jeśli coś zgrzytnie — wklej mi dokładnie to, co wypisał
> konsola, i poprawię. Wariant A nie ma tego ryzyka, bo to zwykłe kopiowanie.

## Opcjonalnie (30 sekund, pomaga)

Ten sam folder, plik `settings.json` (1 604 B) — małą konfigurację Addressables.
Jeśli wariant A już działa, dorzuć go przy okazji; jeśli nie — pomiń.

## Porządki (opcjonalne)

W folderze gry zostały dwa puste pliki po pierwszej, nieudanej próbie. Możesz je
usunąć, żeby późniejsze listy były czyste:

```powershell
Remove-Item -LiteralPath "D:\Games\SUPER ROBOT WARS Y\listing.txt","D:\Games\SUPER ROBOT WARS Y\listing_sizes.txt" -ErrorAction SilentlyContinue
```

## Czego NIE trzeba robić

- Nie kopiuj bundli „na wyczucie” — po `catalog.json` wskażę dokładnie które.
- Nie ruszaj `GameAssembly.dll`, `.exe` ani niczego w folderze gry.
- Nie wysyłaj całego `StreamingAssets` (20 GB) — nie jest potrzebne.

## Co będzie dalej

1. Ja: odczyt indeksu → lista assetów, które wyglądają na teksty (dialogi, UI,
   nazwy) + bundle, w których leżą.
2. Ty: wgrywasz **ten jeden lub dwa** bundle (kilka MiB).
3. Ja: pierwsza prawdziwa próbka tekstu → policzę znaki i powiem uczciwie, ile
   to jest roboty (S2 → S3).
