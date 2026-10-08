# Next local test: candidate text dump

The user has not run this test yet. It is intended to read one local extracted file and write candidate text blocks to the desktop; it does **not** modify the game file.

## Purpose

The current hex sample suggests candidate text may follow `FF FF`, be CP932, and end at `00 00`. This script tests that heuristic on one small event BIN. It is not a verified parser and must not be used for insertion.

## Run

1. Make sure the extracted file exists at `%USERPROFILE%\Desktop\eventP01\DL102_20.bin` (or update `$p` below).
2. Paste the whole block into PowerShell and press Enter.
3. Report the number of blocks found and whether the output file contains the known Japanese substring `自衛隊の軍用レイバー相手に`. Do not paste the entire extracted script into chat or Git.

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
                $results.Add(('{0:X4}`t{1}' -f $start, $text))
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

## Interpretation

- If the known Japanese line appears, record that the heuristic succeeds on this sample only.
- If no blocks are found, or output contains malformed/gibberish text, record the exact result and do not alter the BIN. The marker or termination assumption may be wrong, or the .NET CP932 decoder may need adjustment.
- Even a successful dump does not prove safe text reinsertion. The event record structure, control data, length rules, and game acceptance must still be reverse-engineered and tested.
