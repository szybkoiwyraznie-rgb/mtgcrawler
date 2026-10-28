# SRW Y - zbieram 11 danych wlasnosci encyklopedii (biografie i opisy mechow)
# 11 plikow, okolo 0.1 MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_ENCYKLOPEDIA_log.txt'
$dst  = Join-Path $desk 'SRW_Y_ENCYKLOPEDIA'
$zip  = Join-Path $desk 'SRW_Y_ENCYKLOPEDIA.zip'

Start-Transcript -Path $log -Force | Out-Null
try {
    $gry = @(
        'D:\Games\SUPER ROBOT WARS Y',
        'C:\Games\SUPER ROBOT WARS Y',
        'E:\Games\SUPER ROBOT WARS Y',
        'C:\Program Files (x86)\Steam\steamapps\common\SUPER ROBOT WARS Y',
        'D:\SteamLibrary\steamapps\common\SUPER ROBOT WARS Y',
        'E:\SteamLibrary\steamapps\common\SUPER ROBOT WARS Y'
    )
    $root = $null
    foreach ($g in $gry) {
        if (Test-Path (Join-Path $g 'SUPER ROBOT WARS Y_Data\StreamingAssets')) {
            $root = $g
            break
        }
    }
    if (-not $root) {
        $root = Read-Host 'Nie znalazlem gry. Wklej folder gry (ten z SUPER ROBOT WARS Y.exe)'
    }
    $sa = Join-Path $root 'SUPER ROBOT WARS Y_Data\StreamingAssets'
    if (-not (Test-Path $sa)) { throw ("Nie ma folderu: " + $sa) }

    Write-Host ("folder gry : " + $sa) -ForegroundColor Cyan
    Write-Host ("na pulpit  : " + $dst) -ForegroundColor Cyan

    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    New-Item -ItemType Directory -Path $dst | Out-Null

    $pliki = @(
    @{ d='aa/StandaloneWindows64'; f='285818855b5de73d830691acc66152df.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f623b6c79ecfcad1039e29cce87e8373.bundle' },
    @{ d='aa/StandaloneWindows64'; f='29eda1d3638745a1e3e0805db5933b86.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8da124fa5a1a155373e562aed4ad403d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='dfc36f738dca6ee278a43abf034fb04b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a1537bb970d7f23aec670f2f54ff616b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='37540e8d50756baf681c32a7eba5fdc1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7c18bc903c6f67a6a59ba8d807c22f2a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a78e44ccb19568678e44b9706e5982db.bundle' },
    @{ d='aa/StandaloneWindows64'; f='50fa37a7a150b36b8cce0103ad6a5ff3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9e46587dfa2b6e15792a39f4d40519ed.bundle' }
    )

    $brak = @()
    $suma = 0
    foreach ($p in $pliki) {
        $src = Join-Path (Join-Path $sa $p.d) $p.f
        if (Test-Path $src) {
            $sub = Join-Path $dst $p.d
            if (-not (Test-Path $sub)) { New-Item -ItemType Directory -Force -Path $sub | Out-Null }
            Copy-Item $src (Join-Path $sub $p.f) -Force
            $suma += (Get-Item $src).Length
            Write-Host ("  ok   " + $p.f)
        } else {
            Write-Host ("  BRAK " + $p.f) -ForegroundColor Yellow
            $brak += ($p.d + '/' + $p.f)
        }
    }

    Write-Host ""
    Write-Host ("skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count)
    Write-Host ("razem bajtow: " + $suma.ToString('N0'))
    if ($brak.Count -gt 0) {
        Write-Host "BRAKUJE:" -ForegroundColor Yellow
        $brak | ForEach-Object { Write-Host ("  " + $_) -ForegroundColor Yellow }
        Write-Host "Wyslij zip mimo to - po nazwach dojde, czego szukac dalej." -ForegroundColor Yellow
    }

    if (Test-Path $zip) { Remove-Item $zip -Force }
    Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
    $i = Get-Item $zip
    $sha = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()

    Write-Host ""
    Write-Host ("Gotowe: " + $zip) -ForegroundColor Green
    Write-Host ("rozmiar: " + $i.Length.ToString('N0') + " bajtow") -ForegroundColor Green
    Write-Host ("sha256 : " + $sha) -ForegroundColor Green
    Write-Host ""
    Write-Host "Wgraj SRW_Y_ENCYKLOPEDIA.zip na Drive (ten sam folder projektu) i napisz, ze jest."
}
catch {
    Write-Host ""
    Write-Host ("BLAD: " + $_.Exception.Message) -ForegroundColor Red
    if ($_.InvocationInfo) { Write-Host ("linia: " + $_.InvocationInfo.ScriptLineNumber) }
    Write-Host ("Pelny opis: " + $log) -ForegroundColor Red
}
finally {
    Stop-Transcript | Out-Null
}

Read-Host "Nacisnij Enter, aby zamknac"
