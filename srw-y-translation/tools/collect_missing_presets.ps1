# SRW Y - zbieram 109 bundli z brakujacymi rozstawieniami misji
# 109 plikow, okolo 0.9 MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_PRESETY_log.txt'
$dst  = Join-Path $desk 'SRW_Y_PRESETY'
$zip  = Join-Path $desk 'SRW_Y_PRESETY.zip'

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
    @{ d='BonusMission'; f='01af747d4c6c94a7947b7a4235e3ac30.bundle' },
    @{ d='BonusMission'; f='09a6931dacf4a34104e6945353bd761a.bundle' },
    @{ d='BonusMission'; f='11a092974f44d6a2fa490e54e186553e.bundle' },
    @{ d='BonusMission'; f='1ad02da169c7dfd81274ca3934180da3.bundle' },
    @{ d='BonusMission'; f='712139f784aeee7052bb074bdfe6e454.bundle' },
    @{ d='BonusMission'; f='768aa8b2c7ffdc392017312e7e2099fb.bundle' },
    @{ d='BonusMission'; f='77f6c2e2d0e5af7918553f27c69e9750.bundle' },
    @{ d='BonusMission'; f='790fea047193ff493fd20bfb8f39417a.bundle' },
    @{ d='BonusMission'; f='7ea50e62f58d34c2bab98fc4eed94dfe.bundle' },
    @{ d='BonusMission'; f='cfe2cf19d5466660b4522ead28ef4c15.bundle' },
    @{ d='BonusMission'; f='e0098689688985425bbb23f143217c38.bundle' },
    @{ d='BonusMission'; f='e1bdea3910624a0a929f4322a320642b.bundle' },
    @{ d='BonusMission'; f='e6dd3c5b2bf90bf84f29f947d2da5ce2.bundle' },
    @{ d='BonusMission'; f='f438ddbcbd0bad897730eebeaffa78a3.bundle' },
    @{ d='Dlc1'; f='15e31da7f135981a25447ebcfab4c55e.bundle' },
    @{ d='Dlc1'; f='18de302e14a07ff12ca2feae843dea57.bundle' },
    @{ d='Dlc1'; f='53efb5a44eaacb0a80a5f0c9ded94492.bundle' },
    @{ d='Dlc1'; f='55327ca4dd1f439027ad87fd88e74a89.bundle' },
    @{ d='Dlc1'; f='60c5bdccdbb483f6b1c0721fecc22014.bundle' },
    @{ d='Dlc1'; f='635110e52472bc782037abf621b3e34b.bundle' },
    @{ d='Dlc1'; f='670b153a76495bdc278515ca6b63a710.bundle' },
    @{ d='Dlc1'; f='697166aace21879ebe45dffada355c1c.bundle' },
    @{ d='Dlc1'; f='a028372a95d0131939ee64fd45276739.bundle' },
    @{ d='Dlc1'; f='aef143ab97c9cdd0cefa1e6b0ad956ab.bundle' },
    @{ d='Dlc1'; f='c1fac6b9cada31bd8603ab264fb7da65.bundle' },
    @{ d='Dlc1'; f='c21f5eddb37c1c0a63f6cb979daf1b01.bundle' },
    @{ d='Dlc1'; f='cc6fe0b60c0d90a2174cdab3d15057dc.bundle' },
    @{ d='Dlc1'; f='ea2ebeaf88580547b308063a95e9ccf1.bundle' },
    @{ d='Dlc1'; f='f8b74bfeddb8db92e8c709733a3abafe.bundle' },
    @{ d='Dlc1'; f='fcb86be6d9e6b7366d97ba8a6276aef5.bundle' },
    @{ d='Dlc2'; f='1880aad3f77a08a2be66b8388bc23cab.bundle' },
    @{ d='Dlc2'; f='3c0e72273ae9e2652f296f543859bea9.bundle' },
    @{ d='Dlc2'; f='7652827edec4cdad92b25d8b0834e74e.bundle' },
    @{ d='Dlc2'; f='78e516f88d1b80109516b36e39066a14.bundle' },
    @{ d='Dlc2'; f='7fee4992f1d7b80c3a30f43d28a26f39.bundle' },
    @{ d='Dlc2'; f='884058ccb94d89d54268e6818ee3b049.bundle' },
    @{ d='Dlc2'; f='8cf6d4d62ffe99c3827e14eb9f508cc8.bundle' },
    @{ d='Dlc2'; f='a26f86e82099d78f6148278bf9a2e032.bundle' },
    @{ d='Dlc2'; f='b47e953a3384ad364ab9ee3f76e52998.bundle' },
    @{ d='Dlc2'; f='ba1f1a13b53e36d96d5c1ece912c846a.bundle' },
    @{ d='Dlc2'; f='bc17cfafa9b1c244d9e55182480a1af7.bundle' },
    @{ d='Dlc2'; f='bd511191d259180b3934946c55a7d3a2.bundle' },
    @{ d='Dlc2'; f='d1416f6807a9776eb677bb1893a2da66.bundle' },
    @{ d='Dlc2'; f='d4230c00e4921255c4526082c0a18afe.bundle' },
    @{ d='Dlc2'; f='d93d19f2bdcc832afc139fb763a2d51c.bundle' },
    @{ d='Dlc2'; f='daafa057a6108c3123d666fd5b1a2273.bundle' },
    @{ d='Dlc2'; f='e0ebe709ea178e502aa1f4eea3e3a95d.bundle' },
    @{ d='Dlc2'; f='eca2a02d7d6cd6ef4e75c1971f0bce4f.bundle' },
    @{ d='Dlc2'; f='f4a3f3993b6aa5c67bea1c35d67f9b4d.bundle' },
    @{ d='Dlc2'; f='f896eae59646522e68012f3c2c1414a5.bundle' },
    @{ d='EarlyPurchase'; f='b357986b92f32f292c2d85cffc3b3b79.bundle' },
    @{ d='EarlyPurchase'; f='de4a1a3b7eb820e9d25b999bd779d5e4.bundle' },
    @{ d='ExpansionPack'; f='1377f769a2d2e17d3cd98b6c9af463e6.bundle' },
    @{ d='ExpansionPack'; f='145f14334d0887af65ff185afbc96e69.bundle' },
    @{ d='ExpansionPack'; f='1ef1493140c5cde22e54f2447fd7e376.bundle' },
    @{ d='ExpansionPack'; f='2977e26bd30cc08bfcf1a0863a85c6f8.bundle' },
    @{ d='ExpansionPack'; f='3ff1b77af5e119fb4d52d638fcda39f8.bundle' },
    @{ d='ExpansionPack'; f='4129def7f931b950c7947b3ae96950d5.bundle' },
    @{ d='ExpansionPack'; f='4ec03efa4372912472a4e472a053dd52.bundle' },
    @{ d='ExpansionPack'; f='542fafb446a1a7fcc79b6c03cebbcd16.bundle' },
    @{ d='ExpansionPack'; f='5528d7f19377e31cc878652e9a803161.bundle' },
    @{ d='ExpansionPack'; f='65c5eccd0acbfea41b8e9ace074511a9.bundle' },
    @{ d='ExpansionPack'; f='68bf52fcc2a9570552b9192ce394c8a6.bundle' },
    @{ d='ExpansionPack'; f='6cd40a4e836a2fc227096ab399c1f68c.bundle' },
    @{ d='ExpansionPack'; f='6fe403c514e77117bc9a7ae1a659f195.bundle' },
    @{ d='ExpansionPack'; f='7586b01008f07c734677bb819581d38d.bundle' },
    @{ d='ExpansionPack'; f='78991899aff4deb5fd65dcd1bd27089e.bundle' },
    @{ d='ExpansionPack'; f='79517aee71a51c88255d81df7d96e73f.bundle' },
    @{ d='ExpansionPack'; f='89337632722ed386397d8e273dda504b.bundle' },
    @{ d='ExpansionPack'; f='8af29803aedd7b5e25e735661227471a.bundle' },
    @{ d='ExpansionPack'; f='8d0d86a5ea0a3b2217accf60d7038101.bundle' },
    @{ d='ExpansionPack'; f='97d5426fef5eb6754598be35f246bfff.bundle' },
    @{ d='ExpansionPack'; f='9c2c08e3f1d12e4b070c99e91c75169b.bundle' },
    @{ d='ExpansionPack'; f='a0227c18fe46be67cd3ad5c21608a6fd.bundle' },
    @{ d='ExpansionPack'; f='a64407cfd3c9eb39ec9ee286353b2336.bundle' },
    @{ d='ExpansionPack'; f='a7f77026108a8287e3016bc8f1e03376.bundle' },
    @{ d='ExpansionPack'; f='b5aa44aac6bbb6c4f14a4c57f1ca0342.bundle' },
    @{ d='ExpansionPack'; f='c49246a9cedba7cca998bf2d7824271b.bundle' },
    @{ d='ExpansionPack'; f='cd9175e32601d78148457530b6824664.bundle' },
    @{ d='ExpansionPack'; f='dbf3efcb9c7539ee316d878b997a39c5.bundle' },
    @{ d='ExpansionPack'; f='eafbd88ff98b2681bad341941168d5e6.bundle' },
    @{ d='ExpansionPack'; f='fb5bfe7d9e3033d9cf2f8fa667b1820f.bundle' },
    @{ d='SeasonPassBonus'; f='767759081e502fca8568b0deed12ee42.bundle' },
    @{ d='SeasonPassBonus'; f='85cb64472dbbe710dc7f4ac70f405382.bundle' },
    @{ d='aa/StandaloneWindows64'; f='10d53c180e7336ae5f6a6f4a05de1033.bundle' },
    @{ d='aa/StandaloneWindows64'; f='191f6095cd5c554d5a5b3afb1eca8b3f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='20e8633c5aa43aac5407049b8367e870.bundle' },
    @{ d='aa/StandaloneWindows64'; f='38b4bde0a8ff1a86793c2c47dba7392d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3ee00935583f71d51c81e351fe954093.bundle' },
    @{ d='aa/StandaloneWindows64'; f='421539771305dca9adf62ec95e92967b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='484bab440952733f75eac432a81d49ff.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5920eca2cd930e73e41ebd95715ebb3a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5d720017111ab1d2ebd8fd51c7e261e0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5d777408faad264bf9139e314ab52525.bundle' },
    @{ d='aa/StandaloneWindows64'; f='81201cf90adaaae1a3e5cc7bcc6f9aab.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8f68bc5b0f6ec36a948e34a14514d707.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8fd67c5f5da1748052773ae7ec6aecfc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9bbbeb4770724af232442f6bbd9c1d46.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a347c8207915208a5633ed8af09d23d2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='adce8357d0d305db008bf87df29a32ac.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b44ccc8aee2f4487c9aeb0b86ba5ae16.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b4679952f0630efc1f126cb879aa4be7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c35890ae1b819d47be6f406295cfa244.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c827b14ce8361ca18b5d8c7bfaf235fc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cd929ae6295c8537e4435f026faacbb7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d4db51b8b2ea9b41ef7147e946578aad.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e09fb30ccc09b4e3bdd866d07f99d50f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ed335109954b64f5ce45ff474edc2443.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f75d350bbfe42b386c63e1d3195852e4.bundle' }
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
    Write-Host "Wgraj SRW_Y_PRESETY.zip na Drive (ten sam folder projektu) i napisz, ze jest."
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
