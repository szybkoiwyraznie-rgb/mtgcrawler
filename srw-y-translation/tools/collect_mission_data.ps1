# SRW Y - zbieram dane misji gry (powiazanie sceny z rozdzialem i tytulem)
# 18 plikow, okolo 0.7 MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_MISSION_log.txt'
$dst  = Join-Path $desk 'SRW_Y_MISSION'
$zip  = Join-Path $desk 'SRW_Y_MISSION.zip'

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
    @{ d='AnniversaryExpansionPack'; f='18d9aa7b616172ff969cacaa3bbc8fb6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2ae449b50d5ee774f49556f66d5d7036.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3cfebf6f7d071c6ae21004ff9be631cf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1db1e0cdf166614b272df50279a55bbb.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9e536edb099109e3b6d01d041fef9755.bundle' },
    @{ d='BonusMission'; f='bf1c6879f562b70d563bb278abf79039.bundle' },
    @{ d='Dlc1'; f='ad6b59435451f01b6243560a6111e092.bundle' },
    @{ d='Dlc2'; f='57cd1059a40c94c0d5b348c8e6e9dc37.bundle' },
    @{ d='ExpansionPack'; f='1be53a6a89633ed22f13e1cd6c918772.bundle' },
    @{ d='AnniversaryExpansionPack'; f='bd23fe63ba02716607805bd8bfe8154e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2a1bccdc130b8ca6171f2bc2bb11baaa.bundle' },
    @{ d='DeluxeEdition'; f='a4adc6ce4d63eb4e3fe4d8559839f413.bundle' },
    @{ d='EarlyPurchase'; f='72f42f58ef7988401088311f3fba114e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='dc1faaa3dba2af45460df444e798d32d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6a89a2c0d5a5827034772d49fa16b7e5.bundle' },
    @{ d='PremiumSound'; f='25637835e5d8c7ebf69300a66bb3bf28.bundle' },
    @{ d='SeasonPassBonus'; f='99cf42ef07d3a0e87e504cff166201c7.bundle' },
    @{ d='UltimateEdition'; f='07bdc514ee51a9bce61aee0d5e051366.bundle' }
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
    Write-Host "Wgraj SRW_Y_MISSION.zip na Drive (ten sam folder projektu) i napisz, ze jest."
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
