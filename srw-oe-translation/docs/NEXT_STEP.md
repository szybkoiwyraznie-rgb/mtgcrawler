# Next step: inspect candidate suffix bytes

The read-only candidate scanner was run once against `DL102_20.bin`; it produced 215 rows and included the known Japanese text. The user reviewed four examples:

- Readable Japanese candidates at offsets `0x158C` and `0x1D68`.
- Coherent Japanese candidates at `0x14E8` and `0x25A8`, followed respectively by a space + `v` + U+0001, and a space + ASCII double quote + U+0002.

The two noisy rows are not wholly gibberish. The suffixes may be inline control codes, trailing record metadata, or bytes included because the candidate span is too long. Do not strip them. The raw bytes and `00 00` boundary have not yet been checked. The offsets printed by the scanner are candidate-start offsets (the first byte after `FF FF`).

## Read-only hex check

Run this in PowerShell. It reads the extracted BIN, finds the first `00 00` after each candidate start, and prints a short hex window (12 bytes before the pair, the pair, and up to two bytes after). It does not modify the file.

```powershell
$p = Join-Path $env:USERPROFILE 'Desktop\eventP01\DL102_20.bin'
$b = [IO.File]::ReadAllBytes($p)

foreach ($start in @(0x14E8, 0x25A8)) {
    $j = $start
    while ($j -lt $b.Length - 1 -and
           -not ($b[$j] -eq 0 -and $b[$j + 1] -eq 0)) {
        $j++
    }

    if ($j -ge $b.Length - 1) {
        Write-Output ("candidate 0x{0:X4}: no 00 00 found" -f $start)
        continue
    }

    $from = [Math]::Max(0, $j - 12)
    $count = [Math]::Min(16, $b.Length - $from)
    $hex = [BitConverter]::ToString($b, $from, $count)
    Write-Output ("candidate 0x{0:X4}, first 00 00 at 0x{1:X4}: {2}" -f $start, $j, $hex)
}
```

Paste just the two output lines. This will let us confirm whether the displayed suffixes correspond to bytes like `20 76 01` and `20 22 02`, and whether they sit immediately before the suspected delimiter. The presence of a `00 00` pair alone still does not prove its format meaning.

## Offset-separator note

The original scanner output may show a literal backtick followed by `t` between offset and text. That is a formatting bug from a single-quoted PowerShell string, not game data. No rerun of the text scanner is needed for the hex check above.

## Previously used candidate scanner

This is retained for reproducibility. It is a **candidate-only** heuristic based on the observed `FF FF ... 00 00` pattern; do not use it to insert or edit strings.

```powershell
$p = Join-Path $env:USERPROFILE 'Desktop\eventP01\DL102_20.bin'
$b = [IO.File]::ReadAllBytes($p)
$enc = [Text.Encoding]::GetEncoding(932)
$results = New-Object 'System.Collections.Generic.List[string]'

for ($i = 0; $i -lt $b.Length - 1; $i++) {
    if ($b[$i] -eq 255 -and $b[$i + 1] -eq 255) {
        $start = $i + 2
        $j = $start
        while ($j -lt $b.Length - 1 -and
               -not ($b[$j] -eq 0 -and $b[$j + 1] -eq 0)) {
            $j++
        }

        if ($j -gt $start -and $j -lt $b.Length - 1) {
            $text = $enc.GetString($b[$start..($j - 1)])
            if ($text -match '[ぁ-んァ-ヶ一-龯]') {
                $text = $text -replace "`n", ' / '
                $results.Add(("{0:X4}`t{1}" -f $start, $text))
            }
        }
        $i = $j + 1
    }
}

$out = Join-Path $env:USERPROFILE 'Desktop\DL102_20_text_candidates.txt'
$results | Set-Content -LiteralPath $out -Encoding UTF8
"Znalezione bloki: $($results.Count)"
"Plik wynikowy: $out"
```

Even if output looks clean, the event record structure, control data, length rules, and in-game acceptance still need to be reverse-engineered and tested.
