# Next step: validate the suffix pattern

The read-only scanner ran once on `DL102_20.bin`, producing 215 rows and including known Japanese text. Four rows were reviewed: two readable rows (`0x158C`, `0x1D68`) and two coherent but noisy rows (`0x14E8`, `0x25A8`). Offsets printed by the scanner are candidate starts, i.e. the first byte after `FF FF`.

## Raw-hex comparison so far

Noisy candidate `0x14E8`: first `00 00` at `0x151E`:

```text
E8-82-DC-82-B5-82-BD-81-48-00-76-01-00-00-10-00
```

Noisy candidate `0x25A8`: first `00 00` at `0x25DE`:

```text
A6-97-CD-82-B7-82-E9-81-42-00-22-02-00-00-10-00
```

Readable candidate `0x158C`: first `00 00` at `0x15EC`:

```text
82-A0-82-E8-82-DC-82-B9-82-F1-81-42-00-00-00-00
```

Readable candidate `0x1D68`: first `00 00` at `0x1D8A`:

```text
82-AA-82-E9-82-CC-82-A9-81-49-81-48-00-00-C9-00
```

The readable examples have Japanese-looking bytes followed directly by `00 00`. In the noisy examples, a single `00` is followed by `76 01` or `22 02` before the `00 00` pair. The original scanner stops only at the pair, so it includes those intervening bytes in its decoded candidate. A single `00` may terminate visible text, with later bytes belonging to event/control data, but this remains a hypothesis. The earlier guess that a literal `20` space precedes `76` or `22` was wrong; the raw byte is `00`. Preserve all suffix bytes.

## Next check

Look through the local candidate output for another coherent Japanese row with a control-looking suffix besides `0x14E8` and `0x25A8`. If one exists, send its offset and the short raw-hex window produced by the helper below. If none are apparent, simply report that; do not paste the full dump or modify game files. One more example can tell us whether this suffix pattern repeats before we change the extraction heuristic.

This read-only helper prints 12 bytes before the first `00 00` after each listed candidate start, the pair itself, and up to two bytes after it. Add another candidate offset to `$starts` if you find one.

```powershell
$p = Join-Path $env:USERPROFILE 'Desktop\eventP01\DL102_20.bin'
$b = [IO.File]::ReadAllBytes($p)
$starts = @(0x14E8, 0x25A8)

foreach ($start in $starts) {
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

## Offset-separator note

The first scanner output may show a literal backtick followed by `t` between offset and text. That is a PowerShell formatting bug from a single-quoted string, not game data; no text-scanner rerun is needed for this check.

## Previously used candidate scanner

This is retained for reproducibility. It is a **candidate-only** heuristic based on `FF FF ... 00 00`; do not use it to insert or edit strings.

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
