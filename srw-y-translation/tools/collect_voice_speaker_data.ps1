# SRW Y - zbieram dane, ktore nazywaja mowcow cytatow bitewnych
# 17 plikow, okolo 2.9 MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_GLOSY_log.txt'
$dst  = Join-Path $desk 'SRW_Y_GLOSY'
$zip  = Join-Path $desk 'SRW_Y_GLOSY.zip'

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
    @{ d='aa/StandaloneWindows64'; f='ba1da373064fa4257af70cd3741c3b0e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2180d4f65e1ee3ac2fb4497c015b0395.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8fb5468b8f0e3e65eadb980949553186.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f2c0027f39ba80ee8ec5510fde91ee60.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4e2c02efe3bd247bee95c6ba792b0c9c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a0ae82c7bcb2df2b2ea1cd705dd968f6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9a86251607bab7f2a3258f2709bee213.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7a7c55b8f1d1c991651d30333ce771c4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='892215ddbcdf52f2ebf8a0bd6fec0466.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3f065218ced59059a0908b505b0a9609.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1b5da0ef65aef8e3db19c7f1b4a62ad2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='862c7887d89b02dc5798436613f93586.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fffb4d79945d10628c55ab13356efdfd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='102a157887ff8b2acf824cc6c9d110e2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9f2339313950b822bb0ffe0353ce1d10.bundle' },
    @{ d='aa/StandaloneWindows64'; f='09b2858b77e9d4103345dd38fae7c781.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4723fcb4c6dcb838cef5b3c69a661554.bundle' }
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
    Write-Host "Wgraj SRW_Y_GLOSY.zip na Drive (ten sam folder projektu) i napisz, ze jest."
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
