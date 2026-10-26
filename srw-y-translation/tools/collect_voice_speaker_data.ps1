# SRW Y - dane, ktore nazywaja mowcow cytatow bitewnych (17 plikow, nic nie jest usuwane)
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'srw_y_voice_log.txt'
Start-Transcript -Path $log -Force | Out-Null

try {
    $sa = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets'
    $dst = Join-Path $desk 'srw_y_voice_data'
    $zip = Join-Path $desk 'srw_y_voice_data.zip'

    "folder gry : $sa"
    "na pulpit  : $dst"
    if (-not (Test-Path $sa)) { throw "Nie ma folderu: $sa" }
    New-Item -ItemType Directory -Force -Path $dst | Out-Null

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
    $n = 0
    foreach ($p in $pliki) {
        $n++
        $src = Join-Path (Join-Path $sa $p.d) $p.f
        if (Test-Path $src) {
            $sub = Join-Path $dst $p.d
            if (-not (Test-Path $sub)) { New-Item -ItemType Directory -Force -Path $sub | Out-Null }
            Copy-Item $src (Join-Path $sub $p.f) -Force
            $suma += (Get-Item $src).Length
        } else {
            $brak += ($p.d + '\' + $p.f)
        }
    }

    ""
    "skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count
    "razem bajtow: " + $suma.ToString('N0')
    if ($brak.Count -gt 0) { "BRAKUJE:"; $brak }

    if (Test-Path $zip) { Remove-Item $zip -Force }
    Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
    $i = Get-Item $zip
    "zip: " + $i.FullName
    "zip bajtow: " + $i.Length.ToString('N0')
    "zip sha256: " + (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
    "GOTOWE - wrzuc ten zip na Drive"
}
catch {
    ""
    "BLAD: " + $_.Exception.Message
    if ($_.InvocationInfo) { "linia: " + $_.InvocationInfo.ScriptLineNumber }
    "Pelny opis powyzej zapisany w: $log"
    exit 1
}
finally {
    Stop-Transcript | Out-Null
}
