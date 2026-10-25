# SRW Y - 38 bundli z tekstem podstawki (na Pulpit; nic nie jest usuwane)
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'srw_y_tekst_log.txt'
Start-Transcript -Path $log -Force | Out-Null

try {
    $aa   = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
    $dst  = Join-Path $desk 'srw_y_tekst'
    $zip  = Join-Path $desk 'srw_y_tekst.zip'

    "folder gry : $aa"
    "na pulpit  : $dst"
    if (-not (Test-Path $aa)) { throw "Nie ma folderu: $aa" }
    New-Item -ItemType Directory -Force -Path $dst | Out-Null

    $pliki = @(
    '91fbfdfba1fd39edbe153d4bec9a32ba.bundle',
    '87aad0e5edac27a8024e0a463c337d1c.bundle',
    '65dbabff8fbeee5c6c267469446efdbf.bundle',
    '6cd6f3dc3574d603430c16f312f8127c.bundle',
    '08b8a34806d30abe7e38e3f6464d41e9.bundle',
    '403cc7e0acc5faad8d9a25e182360d08.bundle',
    'da72de49d4106a034fce2fa5974c7bcd.bundle',
    'af95e769e79a11b531fbf1629475bb58.bundle',
    'cfc11e93f1dadabea385427266e4e252.bundle',
    '12f735c027dcb1485f2fa2797fc5b364.bundle',
    '70bda2356ad71c26973532fad02804b9.bundle',
    '59feeef15e1736ef5c7166d6b4ab2740.bundle',
    '663e18dfca2a7f0b6c277f1a94ae1b74.bundle',
    'fee658ea297dfae6bc743cc0c24afa6c.bundle',
    '8cf45687fddb92db2c73391178a3c07c.bundle',
    'c5970d9efac30008d7650f1552f7561e.bundle',
    'f1fe4566f269113769deba122cc8e6b3.bundle',
    '986728319f712c6263b691ded48c3657.bundle',
    '863a8170d6c0b19f2706ab12b95fd8ca.bundle',
    '2f5af0724d7dd5583baed40295e221bb.bundle',
    'bbfd618fae051e38853d046cc3b3ad2f.bundle',
    'c993229532c7a9653d52016e4de1a0b7.bundle',
    '19786145d00f2e0619c63bc4ce5a3a94.bundle',
    'c83dd78fdcb5be1313d657d7dc18230d.bundle',
    '724bb0aa32a920a5580ed339d66e8c0b.bundle',
    '08146c82df5d3e4ab44b373cb977d1d4.bundle',
    '53af829b4e6a6d8a6e522b667d97ba3a.bundle',
    '3a7b7e4b1b4a5cdfcece5c8fa170024e.bundle',
    '4be2720be3e8934465cdfdd3aea80a65.bundle',
    '68bec2915e89403ca3003574b25af33d.bundle',
    'c5c6c3b818c0d7066ce87a5204616f51.bundle',
    '7e3386886233abd000cc410efe080c0b.bundle',
    '0b917d6b3962ca02b69a8e18a321b4b0.bundle',
    'e7ba2b8b7031f56d6b05e7cb5db371dd.bundle',
    'f2d4d1610724c20b49489757435ac136.bundle',
    '4dd4d85f742c65c9f6175a5bb9778647.bundle',
    'f1ba80f5694d96485b7f8c5402dd18c9.bundle',
    'a1afc008875b80176d4139e04773d990.bundle',
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
