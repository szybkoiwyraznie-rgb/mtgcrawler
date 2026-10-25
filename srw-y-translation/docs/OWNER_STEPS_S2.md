# Krok S2 — znaleźć tekst w grze (dla właściciela)

**Krok 1 (katalog) — ZROBIONE.** `catalog.json` dotarł, 41 543 062 B,
SHA-256 `12c17bf9…73b4`. Odczyt przeszedł w całości: gra jest w Unity
Addressables, a katalog wskazuje, co siedzi w którym bundlu. Wynik:
`docs/S2_FINDINGS.md`.

Najważniejsze z odczytu:

- Tekst siedzi w **dwóch** miejscach: w tabelach Unity Localization (UI, nazwy,
  komunikaty — jeden bundle ~940 kB na język) oraz w **skryptach scenariuszy**
  `*.lua.txt` (4 131 plików w 30 bundlach) — i to tam prawie na pewno jest fabuła.
- Wszystkie bundle, o które proszę poniżej, leżą w jednym folderze. Nic nie
  trzeba szukać po całym dysku.

## Krok 2 — dwa bundle (razem 6 531 163 B, ~6,2 MiB)

Folder:

```powershell
explorer "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64"
```

Wgraj do **`SRW/SRWY`** (przeciągnij, jak katalog) dokładnie te dwa pliki:

| plik | rozmiar | po co |
|---|---|---|
| `1cc7e02ee5711c6ba87a0e364f62198c.bundle` | 940 012 B | wszystkie tabele tekstowe po japońsku — poznam format, liczbę stringów i czy czcionka ma polskie znaki |
| `1c12bbab8ed0f62ff22f808ce0138bc1.bundle` | 5 591 151 B | 678 skryptów scenariuszy — faktyczny tekst fabuły: objętość i znaczniki |

To **nie jest** zgoda na wysyłanie gry: te dwa pliki to ok. **0,03 %** zawartości
(6,2 MiB z 20,66 GiB), zostaną w moim `local/` (ignorowanym przez repo) i
posłużą tylko do zmierzenia tekstu.

Jeśli nazwy plików są zbyt długie do przepisania, możesz je wkleić do PowerShella
i skopiować na pulpit pod krótszymi nazwami:

```powershell
$src = "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64"
Copy-Item -LiteralPath "$src\1cc7e02ee5711c6ba87a0e364f62198c.bundle" "$env:USERPROFILE\Desktop\srw_y_text_ja.bundle"
Copy-Item -LiteralPath "$src\1c12bbab8ed0f62ff22f808ce0138bc1.bundle" "$env:USERPROFILE\Desktop\srw_y_scenario.bundle"
explorer "$env:USERPROFILE\Desktop"
```

…i wgraj z pulpitu `srw_y_text_ja.bundle` oraz `srw_y_scenario.bundle`.

## Opcjonalnie (później)

- `2d69c099bfdf0e252dabe84dbbba11df.bundle` (948 652 B) — tabele angielskie,
  przydadzą się jako kolumna referencyjna przy tłumaczeniu z japońskiego.
- Nie ma potrzeby wysyłać nic więcej: resztę bundli wyliczę z katalogów dodatków.

## Porządki (jeśli jeszcze nie zrobione)

```powershell
Remove-Item -LiteralPath "D:\Games\SUPER ROBOT WARS Y\listing.txt","D:\Games\SUPER ROBOT WARS Y\listing_sizes.txt" -ErrorAction SilentlyContinue
```

## Co dalej

1. Ja: otwieram oba bundle, wyciągam tekst, liczę znaki i linie per język,
   sprawdzam, czy polskie znaki mają czcionkę (S3).
2. Ty: dopiero wtedy dostaniesz **uczciwą liczbę** — ile znaków ma fabuła i ile
   to realnie pracy — oraz decyzję go/no-go.
