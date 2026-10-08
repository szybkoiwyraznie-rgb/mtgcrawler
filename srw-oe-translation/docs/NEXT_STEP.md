# Next step: classify candidate text output

The read-only candidate scanner has now been run once against `DL102_20.bin`. It produced 215 lines and included the known Japanese substring. Some lines also contain control/binary-looking characters. This is a useful partial success, not a verified extraction format.

## What to do next

Open `%USERPROFILE%\Desktop\DL102_20_text_candidates.txt` and send only:

1. One candidate line that is clearly readable Japanese, including its offset prefix.
2. One candidate line that looks noisy/control-like, including its offset prefix.

Do not paste the whole dump or modify any game file. These two examples should help determine whether apparent junk is an embedded event/control token inside a valid string or a false-positive block.

## About the offset separator

The first output may show a literal backtick followed by the letter t between the offset and text (for example, offset 0464 followed by those two characters and then the candidate text). This is from the PowerShell script's single-quoted format string, not a game-data byte. If rerunning, use the double-quoted formatter shown below.

## Reproducible scanner used for the first test

This is a **candidate-only** scanner based on the observed `FF FF ... 00 00` pattern. Do not use it to insert or edit strings.

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

Even if the output looks clean, the event record structure, control data, length rules, and in-game acceptance still need to be reverse-engineered and tested.
