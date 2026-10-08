# Next step: compare clean candidate endings

The candidate scanner was run once against `DL102_20.bin`; it produced 215 rows and included known Japanese text. The user reviewed readable rows at offsets `0x158C` and `0x1D68`, plus coherent but noisy rows at `0x14E8` and `0x25A8`.

## What the noisy-row hex showed

The first `00 00` after candidate `0x14E8` is at `0x151E`; the 16-byte window was:

```text
E8-82-DC-82-B5-82-BD-81-48-00-76-01-00-00-10-00
```

The first `00 00` after candidate `0x25A8` is at `0x25DE`; the window was:

```text
A6-97-CD-82-B7-82-E9-81-42-00-22-02-00-00-10-00
```

Both show Japanese-looking bytes followed by one `00`, then `76 01` or `22 02`, then the `00 00` pair where the candidate scanner stops, and finally `10 00`. The earlier guess that a literal space byte `20` preceded those code-like bytes was wrong; the raw byte there is `00`. The scanner stops only at a pair of zeros, so it includes the single zero and following bytes in its decoded candidate. A single `00` may terminate the Japanese text, but that is not yet proven; `76 01`, `22 02`, and the later bytes are not understood. Preserve them.

## Read-only comparison on the clean rows

Run this in PowerShell to capture the same short window around the first `00 00` after the clean candidate starts `0x158C` and `0x1D68`. It only reads the BIN and does not modify it. The scanner's offsets are candidate-start offsets (the first byte after `FF FF`).

```powershell
$p = Join-Path $env:USERPROFILE 'Desktop\eventP01\DL102_20.bin'
$b = [IO.File]::ReadAllBytes($p)

foreach ($start in @(0x158C, 0x1D68)) {
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

Paste just the two output lines. We want to see whether the clean examples also have a single `00` after the visible text followed by other bytes, or whether their first `00 00` directly follows the text.

## Offset-separator note

The original scanner output may show a literal backtick followed by `t` between offset and text. That is a formatting bug from a single-quoted PowerShell string, not game data. No rerun of the text scanner is needed for this comparison.

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
