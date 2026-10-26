# SRW Y - zbieram pozostale kontenery glosu (nazwy mowcow cytatow)
# 311 plikow, okolo 2.0 MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_BVC3_log.txt'
$dst  = Join-Path $desk 'SRW_Y_BVC3'
$zip  = Join-Path $desk 'SRW_Y_BVC3.zip'

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
    @{ d='aa/StandaloneWindows64'; f='0001072104cecafc8b3a8d49a22b5d71.bundle' },
    @{ d='aa/StandaloneWindows64'; f='00865751030fa68b80974b2eefd29aa4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='00f8a71ef114dd09eba741504b5b7811.bundle' },
    @{ d='aa/StandaloneWindows64'; f='018552a0eb1b4c0437d90d8a99437595.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0365d8da31ddc266619e6bba93b29de3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='03a5ce04bcf50e9f4473bea4604abbdc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='04270a38d3ea76785d2726af081cb0e7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='042ac72077be167f58fb4e26f3b8fb5a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='051f65b19eb127351d3a5f574995fbb4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='052989fff12416d123ddacafe6bda953.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0539a13e25d531d052a1bc8d70600772.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0553f866f55f257415a8ff2b4de94ea3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='05561d378153862c9cb07660de8a8062.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0657565ded7ccb2950e04f0e01a7e3f1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='06c58c921c451dd8cf4cc1ae68754d35.bundle' },
    @{ d='aa/StandaloneWindows64'; f='071362d44fa89a3bf486e177d796bd21.bundle' },
    @{ d='aa/StandaloneWindows64'; f='077c694e8a5c63a64cb3615b05bc574f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='077ff1648fe7241bb84161812f303ac8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0780f67fa082221baf2073789cf757d4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0857a0531e86420285aa1a61a7dc7785.bundle' },
    @{ d='aa/StandaloneWindows64'; f='08e32b521f9ae899e9a2450d1a41be96.bundle' },
    @{ d='aa/StandaloneWindows64'; f='094b33e4432b69ad6d2f86dfbebe9ef9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0a7640b42171ed79f98215da882d4126.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0c17ee3bbda8a3a9adc1f0c116fe9e38.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0d04873906d793f4273b81341ca25161.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0d630118d7d05e34756e9e7891ce0dd5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0dbee1b9c7cdace7f964b75cfb6bc436.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0dd76929d7ccf867b35179fd14e20ce0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0f684ea533c459aade7cdb92f891484d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='105d2f7fecaa86870050c1111e650efd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='11ba8a16bda1de22d6ea3ca1bfbd7d3e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1339d89457114cf48782204c762edb00.bundle' },
    @{ d='aa/StandaloneWindows64'; f='14538de80c46b244fe193723a07bc8d5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='166af9388a3c3883bb1622e2c6a8b02d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='168707434aeaf9071c789a0185da53df.bundle' },
    @{ d='aa/StandaloneWindows64'; f='16b6378593665d40b71831713babd623.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1751c641edcd9ed19f320ca62e0ee545.bundle' },
    @{ d='aa/StandaloneWindows64'; f='184d6d6affa9e5193c8db8849a96f396.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1887a505527cc3dbc3ebd26fd0ae1cd5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1941d1453863aff22027496ff29c80f1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1945f6087c306fca37ae74b0e3109614.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1a3712aa2a3324d0454112560977fb7f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1a430c012b5015bbfcda0575951cd12d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1b0d4db832631b9285ef7845ebb18a09.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1b46e3cc46dbddbd2a3b37abbf12c926.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1c3c7189c24c148c0e8e9b112147bf60.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1e179ca656ad132d3ef798701ccd37da.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1ea6dc8e1a160d348f473432bd1928f8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='20513bd6120ab0de17ea8ba1c89acff2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='206ba9e36a5daad50eabeec766edfc96.bundle' },
    @{ d='aa/StandaloneWindows64'; f='210b4b5aad914862cdc18e10c03b6bcd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='21a28e704248488ec7081593258433db.bundle' },
    @{ d='aa/StandaloneWindows64'; f='21b8edaf66c6dbc0f60705597e8fbe23.bundle' },
    @{ d='aa/StandaloneWindows64'; f='225ec43e1a2b0e47d4608736f97d8955.bundle' },
    @{ d='aa/StandaloneWindows64'; f='227d471de100f9d2ef5f73c31d99bd2c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='230e310e5a080dd38a8971058dca36d3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='230ea63d56d51465b1b2a14aa37994e0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2444590b523249c8f9e6415e371965ae.bundle' },
    @{ d='aa/StandaloneWindows64'; f='24ebf9d417fbeb5a384fb92fdc325bf8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='25d67d08bcdf2890af95ddecb7aee3a4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='281ef337345052c39a976ae7ce859eb4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='29127bc2a07b404ec2d6c6a803884508.bundle' },
    @{ d='aa/StandaloneWindows64'; f='29ee8742e5afe4c6c72cd8552dffa836.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2c543e2631cd210cece9f44776514913.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2c94c6850b0ae109823ee9ee10d27ac9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2c9aa3f3e28b75bdc1abfbac1652d742.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2c9e3b2e8706b8ceb761edc03060cbc2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2d460689a3e834561c282971004c93d6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2d92d69c23aeaffad94e01ee34417577.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2f61dcc53ea578ecf6b35ad8f9f49114.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2fbf74a02cb43a667a6070dc460eb92a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='30786cd594de377c15f3aa17ede03ea2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3164fdad4b0f57ae2be622ee7dabda4e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='321a5dfc109b347d967b46c0f0e801cc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='328d42f4d49b99c2fca7ca7a6689598a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='32beac2ea3923191932369f8b1c2e8e4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='33d434ae27f6ac9a1d2f3bdf661ad789.bundle' },
    @{ d='aa/StandaloneWindows64'; f='36b444b1859af78f651bb2aec332b859.bundle' },
    @{ d='aa/StandaloneWindows64'; f='36daf577d77912fb63d7cd650277167c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='395f8097bd71f76156c2b67e74515124.bundle' },
    @{ d='aa/StandaloneWindows64'; f='39786640a5bb981c8b0adbb2141a480f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='39c0c61f7961ad0236c03283948f9aa7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3ac77fb853552eb0255cff7d9e1483c5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3b5f6704ab7c2129c0c274cac363ae41.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3cc78f3e0183d9e7f90a6f65b3cd84d0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3d78c08dfafcd9bac85bbde794a3e724.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3d9df76b2c6c8d524eca96bc6c3becae.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3e570bd1a80879df92ff3dd9aa150a41.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3ef43fd1b6fcae23f55a8ab6f2d223e8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3fa5758ad53e7bcb038d236601221f0c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3fb416bf6e5a82a01ca0e8423f6c9c0a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='402a897ef768a1bb0ff7bbc511acef9a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='40d0734695faa02f3997e5c43e093f1b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='40ff3703ffaef9b73bcd410f05baf395.bundle' },
    @{ d='aa/StandaloneWindows64'; f='41466b33a1747f395e67c45cb2f3b903.bundle' },
    @{ d='aa/StandaloneWindows64'; f='440be0ff5890ac7423d0eb44b637d54e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='44762766f569ee2803c99c7534aa80ca.bundle' },
    @{ d='aa/StandaloneWindows64'; f='45dd27a24a555930f732b0ad61aa92e2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='47727012e6dd066e83431fecd5a69a21.bundle' },
    @{ d='aa/StandaloneWindows64'; f='485206cd24583208f5d344041f2d61e0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4add7eb5f923047770c1a834135aca00.bundle' },
    @{ d='aa/StandaloneWindows64'; f='513e2e2d3328b7699146159ac1338207.bundle' },
    @{ d='aa/StandaloneWindows64'; f='515a735edc7a8c173f16a1ff37575e15.bundle' },
    @{ d='aa/StandaloneWindows64'; f='52b074d94510cf5ba67b99a8ec23470b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='53240185486f54f9bc4e2c9b26b9e04e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5373faef1e1177e62c9aa7a76b477cbe.bundle' },
    @{ d='aa/StandaloneWindows64'; f='543fb096a73b1613a825bd77b6359e37.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5647f65260586835b324b3b07feb3b6d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='573d48adf74abdc4491db8f195df94e3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='573dd39580f986654771a97ce4f058ab.bundle' },
    @{ d='aa/StandaloneWindows64'; f='577fd2aa289ef89caa0ff13c6f551710.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5886f53844d26a8b6aec55cfa0960687.bundle' },
    @{ d='aa/StandaloneWindows64'; f='592253b4e95f70cec9da9a076b4cb67f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='59e7d7bce038d5e8a914ae31fed55632.bundle' },
    @{ d='aa/StandaloneWindows64'; f='59fa3bd770686388fdb9419562466325.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5b6cedf51726df866086430752ed7519.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5b9d90b9e0c0d43a489fd9404ae813f2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5cc987f0c88818bb83a8606038c08534.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5d0af41016389b6a01af6288cc65c8d5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5dde012cd0182d9391a9b76aa08a149f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5df7ceb76e5132a448a58cafd09bf86e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5ed36dd1d37a6b0f7fd8bd167c1d98b1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6075e74d99199373a26d11a115db8a3d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='60dfd4519968f9bb7f51d183b8fdf470.bundle' },
    @{ d='aa/StandaloneWindows64'; f='625b26bb60e1c81fab47e668d0037a12.bundle' },
    @{ d='aa/StandaloneWindows64'; f='66c8bfdc0d210c30a9c61fc3884735b0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='67e59628f446d99d5e16a78974593beb.bundle' },
    @{ d='aa/StandaloneWindows64'; f='685023e9ea5fd36f67bb214ca13acd8d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='68cb5a83d966f9a18869dd26f5a60e59.bundle' },
    @{ d='aa/StandaloneWindows64'; f='69d030d10a8a71533e547c9df8da2a52.bundle' },
    @{ d='aa/StandaloneWindows64'; f='69dac88d05506ebf0c80a48fd4fe08f8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6bee690b6eab841adc47729b98a620ee.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6d240572629ebc4752ab56e4f2a6d517.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6d4ae4e6ce8676928acf67ec6516ecc2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6e63cdeb37f5701123fff02668a7857f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6feb7b8cd5237b38383ad6686db06b44.bundle' },
    @{ d='aa/StandaloneWindows64'; f='717ed71cc608a7230c575cba956491a2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7252150a2f23bc62f0c8f2c82e5aae70.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7261ce53b7debf57dcc113f061521d51.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7369d126cec61bf012689d6824bd658a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='748b52b8782b97c5ad435709c5393d24.bundle' },
    @{ d='aa/StandaloneWindows64'; f='74f274c39dc0e96468d6cfb323a454ee.bundle' },
    @{ d='aa/StandaloneWindows64'; f='78fabf211f43502bc6412b7965359c6a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='793a64e744ad485ab54f68ab70ee5607.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7a1abfe57e7ac93c6403d4e64fcba062.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7a5453b443cd53d05902ae9ca9ea4e68.bundle' },
    @{ d='SeasonPassBonus'; f='7adb52a419ad060ad7d9992744fe5dda.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7cd64f1ebb709e22cb8d76ed87dea044.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7d22f9d67c28bddf066dab848d0ab9af.bundle' },
    @{ d='aa/StandaloneWindows64'; f='80ea8f89a0611a0d4b48716651d876b1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='81f4c3bd0e44e0f2ec85ec5db553704f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='82866266bb7669bdb0e42e126994b2f5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='836d096c6a2d8171a52a8610361e8782.bundle' },
    @{ d='aa/StandaloneWindows64'; f='84fe85005e5520a6732a0a6965fef013.bundle' },
    @{ d='aa/StandaloneWindows64'; f='86a3ba7265a03eb04838ed74b4eaa0df.bundle' },
    @{ d='aa/StandaloneWindows64'; f='88140f126ec4895e850a4965b44188cd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='885d056fd634cf799e3dc300cd7affab.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8a6df77afaf1b50e02fba1caccf73496.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8a80b8e102bc86d129e18db58cb6e94d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8b38255ef9527330a9de62dff0e4a3e2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8c17a34ff740daf1264e7cbe8498a48c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8c681fdd36899a66622d1d8e176a4d22.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8d2a278cbb07c0e10e5a5a1255bf8074.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8dcbab7f9ed80f51523f628f057c717f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8ed74f780a7ea95ecd75975d924fc52a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='910a56420949dbc5185ab7985f112055.bundle' },
    @{ d='aa/StandaloneWindows64'; f='921dd7db2abe8b1ded1c337d16583360.bundle' },
    @{ d='aa/StandaloneWindows64'; f='92355a6459eb0c55a6d77f5140903419.bundle' },
    @{ d='aa/StandaloneWindows64'; f='93d430718db2d04c30c80e574cb828b9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9429bb10024469baa355f73f018fdeb8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='947e31b1bc78eb7d4cdf2a26773ae85e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='948eed53519fe957604375ae9926f524.bundle' },
    @{ d='aa/StandaloneWindows64'; f='94936474344a5edd037940d0d1e55167.bundle' },
    @{ d='aa/StandaloneWindows64'; f='94e3a79283e675ab24eb448b65fdfff6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='95248b33b048a4add8cde2d15cbad48a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='965df0ac4bddbc9585e1c8ee7297d44a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='96dee2434c02f50fc2ad95905d8d23d1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='97f49fc21a9442b1150255f314b47488.bundle' },
    @{ d='aa/StandaloneWindows64'; f='985d059f1771a3a3e5e0242be338c351.bundle' },
    @{ d='aa/StandaloneWindows64'; f='990b6353b51fa3b32d9176d43535c0d9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='993de57e8392c8d2ae02c31359466259.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9a3cd047f9bbf70b01e1190662cbb4b8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9aaba13de7d9f37a59c1acc9b91d23b6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9b6bba5fbac95551ce38af352a7368a6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9cee11c1fce089eefe9ed2397af02657.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9d143a272c7405bc76724ad2fae0324c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9d98b12635a43299fc869dcc96869629.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9da4a9a9a4fc3d631ac4529e97ae5c4f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9f6774028365039cba50dc91a2988fbd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a00fa55c8f5bf46e8ed22b56ff9c119e.bundle' },
    @{ d='SeasonPassBonus'; f='a1bbfddd738d1c24708f986ccff8775c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a2859c1163c81dcc557bcc09ef49e8ad.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a2ce66396ae8e0cc776cc74cfb2cd94c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a36321639acba0b9c94a2ead11a3a765.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a41bbeee4700aa17bf2ab147c0cf6558.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a45b9ec548dd0c46eb8da0d46957f0fb.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a4a6c951b9f78d10e311775677a11bd7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a4f62eec7866a1a27de1cc474416a29b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a501453a3fbf50f03adcaf00dcc662e2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a505961921d85ada3411ca9dfa39bf4f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a6195be5d18d833c309862903c6a61b1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a6469511c5b77ebe61675fa1fc669b83.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a7be97591bef3115bd0a98644a230841.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a7ed7ada848d2418c6c94e612549230a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a8e3b163ef338fdbefe1bb6bc6d614fd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a8e86061c4fe642047e4648a7783b9f2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a933ceac5008b0630ceae260991947a3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a9fbef3754d9564579411d804567e180.bundle' },
    @{ d='aa/StandaloneWindows64'; f='aaacd5d2a77f6d4c9cbf8d8580cf6d98.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ada7fe6686d0ba06de5472b4cec26769.bundle' },
    @{ d='aa/StandaloneWindows64'; f='afb871d04156ffd08964ecbcbdc277e6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b013033671b4089a393e1d068eca40d1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b03a10389e35a933ec1b0b3699f62c89.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b22b951020ce9fff4bb60d491bf9b78e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b2652fb13e362a0f80eff397c8a76fba.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b2905f55391da7babd47457804a3ea53.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b327d3b6ac2f6ebed99527d75bac985e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b3ee87d97a754f6656dc78f755f5c2cf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b59bc28bef99c63b7eb117a0ea58f6c4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b6247967ccb0cb00c77ec01c2c6570f8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b70161feca832f03e23166a8c50e519a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='bac2e4cb3e158887bc3428b21d9d3b0a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='bbbdbc9bc24733529bcd2346361f4f18.bundle' },
    @{ d='aa/StandaloneWindows64'; f='bbd09f2a190080e74b6db0ab57968eec.bundle' },
    @{ d='aa/StandaloneWindows64'; f='bcdc06799dee5791ee5d0c4d9c369bd2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='be3575edb8817d00b42ae3660670cafa.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c16c49c6fff69a7b20b239c99eb04fb7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c1a953ef19f2d6f465ae04f1243ae574.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c220645fed9bf13b2b9947f3d536386e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c2235b1a57db85aeac41634fccd96743.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c2534f51b9ac15318062beb56683f457.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c2ea474d315dc807d645e00d6ec42927.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c38c0580129e546eeeedfc8f1d97b570.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c3dde1e9165e6a48a6fbe8b656063304.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c52e38f49db0570b3abee068c384f308.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c5a36b5df56948a609874050af2dcf7e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c5c5cdb10fdde67556f95b83e209f654.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c7a1a28138ed8c4d906ebd174a03731f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c7d3fa4b6864dca28ba10bfca0205cea.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c89b8716439a7f5e7198492e5afe1bb7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c983322b77389bb5f3341de9c507da11.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c984479c320a8986891539fdee2b3683.bundle' },
    @{ d='aa/StandaloneWindows64'; f='caeaa0abb6f1a85eb3af3ff3b4957cf1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cb61140b887275c2356e86ce271d63ec.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cbe9c7ab103f62da945d54f62dffc4b6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cc18c6981d70a14fc44c08f5f64b6ae8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cc46a5e8712bb148ca895c6f57c08049.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cce81a230203c172bd82fd5da6b3a82d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ccfd7acb45de3711677477c7693bbfc7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cdb70dc7f52ecfeea0a42b2f740418bc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cdb9a008fa9d07607c71982e1a68a3de.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ce41e12840f7d1357cb57ba9486c9ffb.bundle' },
    @{ d='SeasonPassBonus'; f='ce576fe79c9bbbf2e54c9fb74cd8b705.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cf1a9e7a0217c42196210aaced2d5c1f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d008633ba49e277ee2d2e1599c9b45c1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d09938dfc3eb4511ac16edd791727ace.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d17dc2a7dc1454291b9e0723f942409b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d2fceeac21adc469d3b3a972cbf99f28.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d493d9e9130a28675fb2a8587131fa06.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d4f9503e77839cb4e38f1a6dbf000ea3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d58316252a3ad167277be6e6d880dd5c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d61b3a13359dcea95a3160ad8d7dbd41.bundle' },
    @{ d='SeasonPassBonus'; f='d6fea41486093275f82921e80c382577.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d710896e1fc6721682dc8192296cc79b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d75db14dc907bfa97f1285d8386c0dd4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d7b9aa0ad865aa607e7d71401a2f0340.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d7d9b848b8e2b1e03996b59229937c21.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d9080e7018782fedee2055e16d2cebf1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d90dc44090d97be76cd11c1bc23219d1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d92f61f480738b73e9dab95946d2d450.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d95b9326013ecbeab6cd4fa19aa05df5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='dada655ef368eaa1ccf84561804f7275.bundle' },
    @{ d='aa/StandaloneWindows64'; f='dd666835629f094ae195c00504c74d6f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='dd6b3966de0d7b736e8f90eed148bfcc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ddcdf02e8871aa63d7bd6703983e5409.bundle' },
    @{ d='aa/StandaloneWindows64'; f='de8aaaecc1e4bd7b64c66a96e704b53e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='df144c17bcdfd6454a4ec44d813901b2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='df667731befd0f0263ef696af6780c52.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e0590f7ca050b66e567269194fc943cd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e0a099c3f4a52df33e510102d7e19d4a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e16ffdd4edab9418433d7918d8e78e6b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e2467cf8d831b2d201171a6959a0b648.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e4f36bba49151095e3127cd644c5b9ba.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e528e8f4af7e2511631beb5f70b50df5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e562f483d3b214650076679035af1f5a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e6976758159e97a48b4315b16b67336d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e949371adafe0e5bab79635b668382ca.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ea05a205dd92f9a3becc572761854b31.bundle' },
    @{ d='aa/StandaloneWindows64'; f='eb77e5182164069bb9ceaff19dc610a4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ebd03a367eaae2843b517fdfdb05e32a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ec1dd6a9dbbefcf7cdc3874c77b2a147.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ecda4ff2a8cce0a1449d6331606c8242.bundle' },
    @{ d='aa/StandaloneWindows64'; f='eced74b6a674ea7c9192988990db4caf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f06c3b0388089503c540f51255657123.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f172365c4a63a183929ec44ef6320129.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f28ca27f4092862a39d34cf9957110b9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f2db45cafc686fef5003352df3a077ac.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f30dfc14b8f918b7af86efcca4a32d69.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f3fab2d681c70152f87ba5e41e9890c5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f671e5cf6b16ac47d435f277e7a97401.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f6ec6bdf993547edc684b67bbd2c0518.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f8229142bc7bb73d6cf7a2316901a98e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f9625a4813702c50d42e820c35cffb15.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f9f3c0735af13ca1b0cc64a7f2038ee1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fa6fc03b08d8a604142f798b00b1b6c8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='faa4a4c7f3292f63397bc4fae0ac9eeb.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fc3aaaad5a459db8f3683da99e91bf54.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fd1a3571659dcc9e76f5eadda990c96a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fd839765a0e8519fcfc1c99732304ef6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ff29a3fd04d74e7442565f61d1516ae0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ff2ba29b7ce5a338a13f4a8dd781def8.bundle' }
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
    Write-Host "Wgraj SRW_Y_BVC3.zip na Drive (ten sam folder projektu) i napisz, ze jest."
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
