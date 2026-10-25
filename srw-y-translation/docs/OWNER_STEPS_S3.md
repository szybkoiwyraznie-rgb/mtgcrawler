# Krok S3 — odczyt tekstu z pamięci gry (dla właściciela)

Dziękuję za wersję Pythona (**3.12.9**) — to wystarcza. Nie potrzebuję już
żadnego pliku gry. Potrzebuję jednego przebiegu **na Twoim komputerze**, przy
działającej grze.

## Idea w jednym akapicie

Bundli na dysku nie da się odczytać, bo gra je szyfruje własnym strumieniem AES
(hasło + sól). Ale gra **musi** je odszyfrować, żeby działać — więc przez chwilę
odszyfrowany tekst istnieje w jej pamięci. Zamiast zgadywać hasło, czytamy tę
pamięć. Skrypt niczego nie zmienia: otwiera proces **tylko do odczytu**.

## Krok 1 — sprawdź, że skrypt działa u Ciebie (10 sekund, bez gry)

Wklej do PowerShella:

```powershell
$u = "https://raw.githubusercontent.com/szybkoiwyraznie-rgb/mtgcrawler/arena/6906ed6b-mtgcrawler/srw-y-translation/tools/mem_carve.py"
Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile "$env:USERPROFILE\Desktop\mem_carve.py"
python "$env:USERPROFILE\Desktop\mem_carve.py" --selftest
```

Powinno wypisać `self-test: PASS` i `carved: [...]`. Jeśli tak — skrypt działa
na Twoim Pythonie i nic więcej nie trzeba instalować (żadnych bibliotek).

## Krok 2 — pierwszy odczyt (gra na ekranie tytułowym)

1. Uruchom grę normalnie i **zostań na ekranie tytułowym** (nie klikaj dalej).
2. Otwórz **drugie** okno PowerShella (gra ma działać dalej) i wklej:

```powershell
python "$env:USERPROFILE\Desktop\mem_carve.py" --out "$env:USERPROFILE\Desktop\srw_y_carve_1"
```

Odczyt potrwa od kilku sekund do około minuty (zależy od rozmiaru pamięci gry).
Na końcu zobaczysz kilka linii, m.in. `markers: {...}`, `carved files: N`,
`kana runs: ...`, oraz `report: ...carve_report.json`.

## Krok 3 — drugi odczyt (z fabułą na ekranie)

1. W grze wejdź w scenariusz, w którym **widać dialogi** (dowolna misja z
   rozmową; wystarczy pierwsza scena).
2. W tym samym oknie PowerShella wklej:

```powershell
python "$env:USERPROFILE\Desktop\mem_carve.py" --out "$env:USERPROFILE\Desktop\srw_y_carve_2"
```

## Krok 4 — co wgrać

Wgraj do **`SRW/SRWY`** dwa małe pliki raportów:

- `srw_y_carve_1\carve_report.json`
- `srw_y_carve_2\carve_report.json`

To raporty z **liczbami** (ile znaleziono nagłówków bundli, ile plików
odszyfrowanych w pamięci, ile tekstu japońskiego) — bez treści gry, więc można je
wysłać bez obaw. Foldery z odzyskanymi plikami **zostaw u siebie**; po raportach
powiem dokładnie, które pliki (jeśli w ogóle) warto przesłać.

## Czego ten skrypt nie robi

- **Nie zmienia** gry, plików ani zapisów — dostęp tylko do odczytu pamięci.
- **Nie wysyła** niczego do internetu; wszystko zostaje na Twoim dysku.
- **Nie wymaga** uprawnień administratora (gdyby jednak wyskoczył błąd
  `OpenProcess failed`, uruchom PowerShell jako administrator i powtórz).
- **Nie zawiera** żadnej treści gry w raporcie.

## Jeśli coś nie zadziała

Wklej mi dokładnie to, co wypisała konsola (albo zrzut ekranu). Najczęstsze
przypadki: gra nie działa (skrypt powie `process not found`), gra działa pod
inną nazwą (sprawdzimy `tasklist`), albo pamięć jest większa niż domyślny limit
— wtedy dodam parametr `--max-scan`.

## Co będzie dalej

1. Z raportów odczytam, czy odszyfrowane bundle/pliki w ogóle pojawiają się w
   pamięci i w jakiej liczbie.
2. Jeśli tak — poproszę o konkretne pliki z `srw_y_carve_2`, otworzę je naszymi
   narzędziami i **policzę znaki**. To jest liczba, której brakuje do decyzji
   go/no-go.
3. Jeśli nie — powiem to wprost i przejdziemy na wariant z podpięciem do funkcji
   odszyfrowującej (trudniejszy, ale nie wymaga zgadywania hasła).
