# SRW Y - 38 bundli scenariusza z darmowej latki (na Pulpit; nic nie jest usuwane)
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'srw_y_s6e_log.txt'
Start-Transcript -Path $log -Force | Out-Null

try {
    $aa  = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
    $dst = Join-Path $desk 'srw_y_free_patch'
    $zip = Join-Path $desk 'srw_y_free_patch.zip'

    "folder gry : $aa"
    "na pulpit  : $dst"
    if (-not (Test-Path $aa)) { throw "Nie ma folderu: $aa" }
    New-Item -ItemType Directory -Force -Path $dst | Out-Null

    $pliki = @(
    '0d4da62848b000a01b923ae084a6b5d0.bundle',
    '141beb454fb44e3a272f5552bb6611e7.bundle',
    '1cdd8e59c3948d121d648b119d250431.bundle',
    '1e7237b067180a084a41813d725b206c.bundle',
    '24589bf8af43622440136450ebc8f659.bundle',
    '251b193b2f5eb700ee4630f384392af2.bundle',
    '29bcf7970261ce0994d3941e0cdcaea4.bundle',
    '2ca4f140dc737f2e3052e019a8378599.bundle',
    '3ff7231ca08573b470a794283c1d5c15.bundle',
    '6ed33d795cbd7fa0e61a577bcee0fbac.bundle',
    '76d2c892f39485bfea780ed27394adba.bundle',
    '83d6b36d01cf4c373cde7d5b68a1c95a.bundle',
    '8a1d95393391e5fe652090f59d2a09e0.bundle',
    '937bc61e8968b32d98ebb248f8620124.bundle',
    '97087a594607743728c740e5bfafc598.bundle',
    '9b7b9187c8666a7921c30b9a1783ac3e.bundle',
    '9f1ff4c36b11d456e9c43fd495d3ef6a.bundle',
    'de838ab8c5065210c5038b9f88ce3041.bundle',
    'f1add4a1bc8a4355ca5e6d5aef52685a.bundle',
    '05ac40cd8b0d0c560e37b9a43f643c14.bundle',
    '14bb3de6c1d6f272abd381e3822a90a5.bundle',
    '154bdbe91a60bc343c9bcd84e69a7e9f.bundle',
    '18593b7af33eb3ce73264f6e33fc3450.bundle',
    '26216ce79427f69751a05f49a93519c8.bundle',
    '33ff0406dd30f1c392fcf6e952aab74b.bundle',
    '3c1b09a99bb76c0116a4886321d0d668.bundle',
    '3d24a0ef475075fe52f3a6765c113c9f.bundle',
    '401421c9cbe7836dab9456090c20dff0.bundle',
    '45e7a190e4cb11cf2cf79e8ffa4aa345.bundle',
    '4903c1e92ad1f05d42ada5d72747089f.bundle',
    '4ec51514db6c85d1167ce46836350bde.bundle',
    '5f432593aaa6866379f58cabd1897552.bundle',
    '670349f8f0d391fbe1171eb4e742806a.bundle',
    '72418e5d483d4794a75beba4f6df7461.bundle',
    '84d156259997cddfed298f754e3041a4.bundle',
    '867d0e134ea7bfe1c59c6829da3a2836.bundle',
    '908ad98cd52f0e3a1015a387a16d164b.bundle',
    'e5e77bc4623e60c89b0b87ab2bf27b40.bundle'
    )

    $brak = @()
    $suma = 0
    foreach ($f in $pliki) {
        $src = Join-Path $aa $f
        if (Test-Path $src) {
            Copy-Item $src (Join-Path $dst $f) -Force
            $suma += (Get-Item $src).Length
        } else {
            $brak += $f
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
    "GOTOWE"
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
