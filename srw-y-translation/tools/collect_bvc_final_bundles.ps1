# SRW Y - zbieram ostatnie kontenery glosu (wspolne i bez numeru)
# 145 plikow, okolo 0.5 MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_BVC4_log.txt'
$dst  = Join-Path $desk 'SRW_Y_BVC4'
$zip  = Join-Path $desk 'SRW_Y_BVC4.zip'

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
    @{ d='AnniversaryExpansionPack'; f='01dcdfefae8d50bbf938690b661f13dd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='05fd4bf0546fd7f1874e450fd2eddce7.bundle' },
    @{ d='Dlc1'; f='06a32abc775cd613d4d9fbd83f5369a8.bundle' },
    @{ d='AnniversaryExpansionPack'; f='06e63a6780d9aadf05bc95d927ff1197.bundle' },
    @{ d='aa/StandaloneWindows64'; f='07a3b868b3cd8ad78ceea0eca2156ced.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0c7a76a688ce50ae7fe5480e1df4017b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='10968f0dbb2c190c0b19e8ba491daffc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='10ca8b6a3265f196136125aa8158ee11.bundle' },
    @{ d='aa/StandaloneWindows64'; f='13111d92accc064d74ebb08488e90918.bundle' },
    @{ d='aa/StandaloneWindows64'; f='144b9abec2d3755888f0a679c81eb723.bundle' },
    @{ d='aa/StandaloneWindows64'; f='14861b0125428426a94cd4878bfbea57.bundle' },
    @{ d='AnniversaryExpansionPack'; f='15d42c59491c83d11dde7e31aad1ffbd.bundle' },
    @{ d='AnniversaryExpansionPack'; f='19acaf2f970f7860a94da892f35d062c.bundle' },
    @{ d='AnniversaryExpansionPack'; f='1afaebe1ab671f97ced06bd2b2d5e678.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1b03615efb00283a4387979da0b82a87.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1bdd728308129b24b80216a2a7d103a0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1c2350e8ac8c2b5044a311c3b4668264.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1d51d77f40370e899b40f1c7d5d4c064.bundle' },
    @{ d='Dlc2'; f='1ed020be7f8f190dfe056691adb8269b.bundle' },
    @{ d='Dlc1'; f='1fd41d1f241b2b745001459f5611da27.bundle' },
    @{ d='AnniversaryExpansionPack'; f='20c1905577ece10242a6dfc68d773b0d.bundle' },
    @{ d='AnniversaryExpansionPack'; f='25a5a69b59b960b0957e684970ee6d99.bundle' },
    @{ d='aa/StandaloneWindows64'; f='26d2ef1671e0c9b3bc2d4d5c94f7c08a.bundle' },
    @{ d='AnniversaryExpansionPack'; f='272e52642457db78394b9fef3aa41b1d.bundle' },
    @{ d='AnniversaryExpansionPack'; f='288431f7b7c47a5bfda704bd9279e89c.bundle' },
    @{ d='Dlc2'; f='2a4d5150274a42f3d4aaa81bc4b4a1d6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2d08cc304581de0b430d23bc28948d67.bundle' },
    @{ d='AnniversaryExpansionPack'; f='2d5a70b494ba9e896b556e5ae366c1a2.bundle' },
    @{ d='AnniversaryExpansionPack'; f='2f842d892f6608c388b2b680472595f4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='311f933d92895403ecfcea8447496e10.bundle' },
    @{ d='aa/StandaloneWindows64'; f='32cad6ef268ca70b79852702e0699471.bundle' },
    @{ d='Dlc2'; f='370539a953ea03a646a696b4885e1a83.bundle' },
    @{ d='ExpansionPack'; f='37dddd3aead2977839f8c1d479871047.bundle' },
    @{ d='ExpansionPack'; f='3949c91300d7a3ae93242dd1db1331b9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3f24a85cd8fe2f9ceba94894c53e79b4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3ff8a988b02be5ff0fb4f7381f3516f6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='404a1e9f8795a734d3d1de4944b5c9d8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4060412c47e1dc46ed79f0df89b86b7b.bundle' },
    @{ d='ExpansionPack'; f='446f505ce515805e948f2162970f45b6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='467d14dd7ba8b89b6968d0c40cc91597.bundle' },
    @{ d='aa/StandaloneWindows64'; f='47064802de38598e9b5e7f530a50fee4.bundle' },
    @{ d='AnniversaryExpansionPack'; f='48c102faf26604f94764d5f2ed5c83b7.bundle' },
    @{ d='SeasonPassBonus'; f='4920096e460ce583284dd2e0555c15ca.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4a2cf3ee96e3709f5743780e3c78ebdf.bundle' },
    @{ d='AnniversaryExpansionPack'; f='4d506cfa5d5208dde3365bd83c0e0786.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4dbe4b8237ca175aa0b33bc5382cfa89.bundle' },
    @{ d='Dlc1'; f='4f4aba2023128f2f9a6cd6a2eaaa4f19.bundle' },
    @{ d='Dlc2'; f='50906d8ae0d8dfe3b1fda5b7894da1ad.bundle' },
    @{ d='aa/StandaloneWindows64'; f='50b3a2900e6a7e8ca30297f248c20ccd.bundle' },
    @{ d='Dlc2'; f='5331915d1d5cc9d26a13c9126ba38f15.bundle' },
    @{ d='aa/StandaloneWindows64'; f='53923604049c8574569167a62eb49a5d.bundle' },
    @{ d='AnniversaryExpansionPack'; f='53cca5f72b6fb8187a6d08501044d0f7.bundle' },
    @{ d='Dlc1'; f='53d6b78f1fb5e30dfdff94fd4c483bf9.bundle' },
    @{ d='AnniversaryExpansionPack'; f='55032cc4a182bfaf800f20d33df2a3a9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5614efe28966fb84d1bbf633827216ac.bundle' },
    @{ d='Dlc2'; f='579ace128976cb5b3c058462aba9857a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='58c5727531c64834e4ce92308c70d43d.bundle' },
    @{ d='AnniversaryExpansionPack'; f='58ee0022a11964ee79a2e88ea6d827d1.bundle' },
    @{ d='Dlc1'; f='5db224813ad12a8e32a1214cf2cc8d69.bundle' },
    @{ d='ExpansionPack'; f='617d3d881ccc19a71fd349b48a72a8db.bundle' },
    @{ d='AnniversaryExpansionPack'; f='61908de908a179b96b38b9279c8a70c5.bundle' },
    @{ d='AnniversaryExpansionPack'; f='62d4ca3e7b18d11173a83c91e628a810.bundle' },
    @{ d='Dlc1'; f='62fe637f187375c1b6913ec5d14b4270.bundle' },
    @{ d='Dlc2'; f='63a9659090f74ad65a95719359d5cae2.bundle' },
    @{ d='Dlc1'; f='64bb327f7f6cde9c334c9e00fa17a2db.bundle' },
    @{ d='AnniversaryExpansionPack'; f='66cc4a57534b3bc993bc04ad1d9ede6d.bundle' },
    @{ d='Dlc2'; f='66e53945af0801c414fdbb9f1a18c4d4.bundle' },
    @{ d='AnniversaryExpansionPack'; f='677ea1eb536d9c8005ba9319f1579ac6.bundle' },
    @{ d='AnniversaryExpansionPack'; f='68002563f1862a9d4d3394f3d665b298.bundle' },
    @{ d='AnniversaryExpansionPack'; f='6a667650bbe8d443ddd5a0c522711f0f.bundle' },
    @{ d='Dlc1'; f='6aa5b8c9dfad9465de69786ebb1ef539.bundle' },
    @{ d='AnniversaryExpansionPack'; f='6ee946cfa458da23aa96bafc32fcd042.bundle' },
    @{ d='SeasonPassBonus'; f='7101d22dc9fb5b273c239cf85934bdda.bundle' },
    @{ d='AnniversaryExpansionPack'; f='72af95f6f9420bea7f60949b6544434e.bundle' },
    @{ d='ExpansionPack'; f='74a7fe2d4eff210a05cca3111cdfe569.bundle' },
    @{ d='Dlc1'; f='7a721c649312dd07cef1a0bb0ee6d210.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7b3db9d38eda6016efca6a418ff98cfc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7d0296539237e470a4daa66d12bdc3a0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7d456eb506a254396b70a95f72ad83ff.bundle' },
    @{ d='aa/StandaloneWindows64'; f='879704b91275e3fe7eacde332d240f0b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='87bb423152b16b68f2b052b7d50284b9.bundle' },
    @{ d='ExpansionPack'; f='89655cf56361bb01f22a75fb1f078e29.bundle' },
    @{ d='ExpansionPack'; f='897dfddb42cb2ad9362e08a03bdc3dd2.bundle' },
    @{ d='Dlc1'; f='89a18443e792a3aa725dabed0ff20ca1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8ab3b1963aff4eda35f02d49fc3e48e0.bundle' },
    @{ d='AnniversaryExpansionPack'; f='8b889277a80060c11275ea6256dfd364.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8cd0ebd898e533fea721ed4ef1bd7384.bundle' },
    @{ d='AnniversaryExpansionPack'; f='8f26b03aa1cb2f65e04f3dfc6f73fcd2.bundle' },
    @{ d='AnniversaryExpansionPack'; f='91216edb50c75ff64ec3e48224f4e3ba.bundle' },
    @{ d='ExpansionPack'; f='93d2c7547b467d32b61feaf531ec2fd9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9763ff174797987f45d050abae30075e.bundle' },
    @{ d='AnniversaryExpansionPack'; f='980f374d68f07b5e77fa4e0af3d1bded.bundle' },
    @{ d='ExpansionPack'; f='98c7460650eb14f75388e61068044f83.bundle' },
    @{ d='AnniversaryExpansionPack'; f='993b5d5532bba288fbbc20b9af7d8354.bundle' },
    @{ d='aa/StandaloneWindows64'; f='995db78963ea5ddaa0c395ef66ca314c.bundle' },
    @{ d='Dlc1'; f='9be668f5b0f1651dc6974b3e14ac315b.bundle' },
    @{ d='Dlc2'; f='a46d41eceb5d27a75692fb82c6cae61d.bundle' },
    @{ d='AnniversaryExpansionPack'; f='a46e131103f9d98e1b26b94a6a7fa0a8.bundle' },
    @{ d='SeasonPassBonus'; f='a5386f563a93960a6d3b4de476bbb7de.bundle' },
    @{ d='ExpansionPack'; f='a8a40efb09e20aeaf6740e9dc7491b02.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a930279887474e6d733fb0b1e8c1b6a3.bundle' },
    @{ d='AnniversaryExpansionPack'; f='a9531e9f6671f468b5bd1280878fb1cf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ab2d2208999e802953a3a496a0603ee6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ad474361da09473d2edf15de05c4b079.bundle' },
    @{ d='AnniversaryExpansionPack'; f='ad4b951a95af204e218cebe3c7f5ef17.bundle' },
    @{ d='AnniversaryExpansionPack'; f='b2861e5cc2aa3517dbfb5d4bcad8dc5b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b8bed713b33447cfb1d225e96427c7cb.bundle' },
    @{ d='AnniversaryExpansionPack'; f='ba3b05bea576e901a036cb6defe795d3.bundle' },
    @{ d='AnniversaryExpansionPack'; f='bb901ad251afa3bc99f811094f925ed7.bundle' },
    @{ d='AnniversaryExpansionPack'; f='bf48c5a0a38c8020233f3144538ef662.bundle' },
    @{ d='AnniversaryExpansionPack'; f='c2013f7153dd73ef853ed718d4874d75.bundle' },
    @{ d='Dlc1'; f='c374c60767ab2cbedbd8e6c24d6322c5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c3a74b8569014fb689245ec4ff00fd6e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c6211fcd84f88b8b3de6d0afe113cf94.bundle' },
    @{ d='AnniversaryExpansionPack'; f='c667708c97848b47f252ea629f1477e2.bundle' },
    @{ d='ExpansionPack'; f='c6884adde93d084e79107c72949b5aae.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c69d3b7b4287d17175a9b92192ca86b7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c891d68ed024f63cf33fdb913289b786.bundle' },
    @{ d='AnniversaryExpansionPack'; f='c8e981cae046546066790f0678e3efb4.bundle' },
    @{ d='Dlc2'; f='c91f9e8ce43b5c2739f1a9f9d86f8040.bundle' },
    @{ d='AnniversaryExpansionPack'; f='cad8562c77d3c1c12c072a211346706e.bundle' },
    @{ d='AnniversaryExpansionPack'; f='ce25b256c91234e07517acd62c2f16bc.bundle' },
    @{ d='AnniversaryExpansionPack'; f='d0f6586a51c2c5538b3f1d07e89bd0b4.bundle' },
    @{ d='SeasonPassBonus'; f='d39d5b0bc6c641fdf13d61ad24b46f4d.bundle' },
    @{ d='AnniversaryExpansionPack'; f='d6b3f70e0ae48b570fd00cea9c559bf7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d707efac31a1be3563e0f09a49b94476.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d72df5df2764bf8a1e050bf5a2cf9542.bundle' },
    @{ d='AnniversaryExpansionPack'; f='d885a22644d6cfbbac6020c06d471fb5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='daf14a75f81fcca795dda6b2b6d2732d.bundle' },
    @{ d='Dlc2'; f='dd0e31a880a4254bf5557565a7d38fa7.bundle' },
    @{ d='AnniversaryExpansionPack'; f='dd2990d1ae9c8b46671cf82a6581be77.bundle' },
    @{ d='ExpansionPack'; f='ddd940376facdd6e1f5d22620d3afde3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='dea27d40a1051ba84b54940a9579c019.bundle' },
    @{ d='ExpansionPack'; f='e0ccd215eac03c0ba3163210e64b4daa.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e24a5b87bbd623a93802396727256c5d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e4b3a92d205ac3efbba4021f2bfb6c82.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e80672b5cb31c832dda7ad1321de79ac.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e81d03bb1f52da2813d1e93f21160c2f.bundle' },
    @{ d='AnniversaryExpansionPack'; f='ee8d0fc87984fcbe14cd5a479a24aa80.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ef80917af3814389c7a591aa5fa233b3.bundle' },
    @{ d='AnniversaryExpansionPack'; f='efb9e9c34b095649e7f1f6fc6bdb8259.bundle' },
    @{ d='AnniversaryExpansionPack'; f='f210ff97f166bab38fea80a43ac6cf8f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f4b891403c7aad2d7c228aeb7503e356.bundle' },
    @{ d='AnniversaryExpansionPack'; f='f4cc05913ddf8f4a708e167e6e34e21a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fb62b35440b697b3291c2da4e7754ccb.bundle' }
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
    Write-Host "Wgraj SRW_Y_BVC4.zip na Drive (ten sam folder projektu) i napisz, ze jest."
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
