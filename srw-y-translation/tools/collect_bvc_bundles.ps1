# SRW Y - zbieram kontenery glosu (tabele przypisan mowcow)
# 310 plikow, okolo 1.2 MB. Skrypt NICZEGO nie zmienia w grze - tylko kopiuje.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_BVC_log.txt'
$dst  = Join-Path $desk 'SRW_Y_BVC'
$zip  = Join-Path $desk 'SRW_Y_BVC.zip'

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
    @{ d='aa/StandaloneWindows64'; f='00ca78c58b197aaa6684007eaa68a12b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='017ad2aedcd4541d9d8fee75e442fd85.bundle' },
    @{ d='aa/StandaloneWindows64'; f='02ac558b8ca454b53d6375d2ef4d4a4c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='02de42cd35f3579e24a2fa61f175151b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='02f801e3a8d19ae2e1462815f6347a5e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='04296ae07e63f918970de647e5658b67.bundle' },
    @{ d='aa/StandaloneWindows64'; f='048fb7139a781a28fb267d89d832b2e1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0691e03167ace3e37f0f2777ffeb2237.bundle' },
    @{ d='aa/StandaloneWindows64'; f='069a39b30afd9714989c50da5107cc89.bundle' },
    @{ d='aa/StandaloneWindows64'; f='070c7acb2cf7358d9fe3b513d9e97a42.bundle' },
    @{ d='aa/StandaloneWindows64'; f='07e0de0ad0134457dcf68b20c5c786cc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='07e90eac9a9e860634a8caeca656f35f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0886ef80c6702c5a5f531786124c018a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='089d8fd642be3eff00fc3d154b95d022.bundle' },
    @{ d='aa/StandaloneWindows64'; f='091b9e3a8be3b78c046760d11edd8fa2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='09d0cab66dd2b81b7f59a9b18c6c656e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0a5262a03d6b09d9a5cb83859dfd70d0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0a6a6a7eec3b99946755dffafeb41c53.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0b49d9d6212d643987caa05caf8cd29d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0b7273e458e872a6beb6d3684926fc81.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0c8b76ebd83305ae9a73fef0e3db21d3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0d6e3a89643d928e1da1ec6a536f9805.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0dececdb05874eef63eb1d0ce54269bf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0e0beafc26361b80752e528785c572ff.bundle' },
    @{ d='aa/StandaloneWindows64'; f='0e2dd756d1f028b576605f5a5e6a011e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='106c7b8835bc89105f63c81c3341e2f0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1116f41416c27785871cb94984b979b2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='124ad57b789dc6c6e1c2cd7dbd576879.bundle' },
    @{ d='aa/StandaloneWindows64'; f='124fe787797a01671085b33bd726cca5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1319e2485afddb7ab9c6c43bc4a7b42c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='13a3b41f01d194ef5757cb17d95d2818.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1439b48b7afe87a2aa4d9af152e0a155.bundle' },
    @{ d='aa/StandaloneWindows64'; f='16f9939edb8181d3c44dd53ed5823ca2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='170cfc3d2d57dea88ec4dfa8cc6453ed.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1796277c3b1b08bfd514fb4faad8cb3c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='17d53714e6ebcd7e96cdb43801e7afc1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='195ad58ad90604d149e41ead4a94b4a6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='19bde6c242ac205eef47d2e4fafd972c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1a829df3bc9284648673e760c297e44f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1b263ce947f2a5e0b932fa84053160b7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1b28fdd402a6c200f00a5b75412b7885.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1b569990270649739d92ee11b8a36018.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1c444aa75189865ab75d8efea4acc106.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1cdfa823cecdcd79b7e842a1d2718eac.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1ee748cf0114f3078cf513ee7beac9c3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='1fb0e14e4b5388627273e61353792c68.bundle' },
    @{ d='aa/StandaloneWindows64'; f='20b6101a0ad93741c2adf363a4cfe4ac.bundle' },
    @{ d='aa/StandaloneWindows64'; f='21f394acc629e58222d3061e1071047f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='239cb92b3f793070d25b21314e9b4a42.bundle' },
    @{ d='aa/StandaloneWindows64'; f='23b2303d8b53cd9b43aedf39bb0ab5d5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='23c7338cfde3b869a5bd388fa5dae96a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='25b73768a41da6546b22e9c8afe469ba.bundle' },
    @{ d='aa/StandaloneWindows64'; f='27645c4ddb561e149d6a0030bec49d45.bundle' },
    @{ d='aa/StandaloneWindows64'; f='276daad37e8ce45394440d18074fa6b5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='27932e7d83537fa42ec6da92faaa799a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='27fe3619900d86fb82301a22d6c5618d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2997c945dbde12ce715ff0331480f328.bundle' },
    @{ d='aa/StandaloneWindows64'; f='299f74b246354744e46293e1a1f4e1b6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='29be4d7ca53f1295c30148bbeebf83c9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2a176e4963adfe3dabf8497efe5acf1f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2a6fb5122d0fcec2cf520c05b3fc74e8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2ab8dcb439e0c2f8c0b598eb2998f9a1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2d308e690cf180d3e54439f37b0f17a0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2e4a8bb64d91ca768c91235167c36610.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2e7153479fc5351e3cae69bbf17227f2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='2fe149ce85a31c7e046535e2d8ba70cc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3077f7d207b7bf299f0d84de834271f5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3078ffe5a7e103123adaf4c0d2c19133.bundle' },
    @{ d='aa/StandaloneWindows64'; f='309a7ec04143750222b57aec8ca3e177.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3117a1293a7f032583d0ce983fd311a1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3122e54ba0cb13d9b6453399150f0e58.bundle' },
    @{ d='aa/StandaloneWindows64'; f='312723f2a07384cf9ef317d13678bead.bundle' },
    @{ d='aa/StandaloneWindows64'; f='31acfb38cbe91d084cbaa4bb0d9f0a3c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='34bd7f44c16c4b937b4060abab010d4c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='35a5f5a27c65871062d5148d7e86618d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='36cc6c7f620c2e9968af59bbe268b775.bundle' },
    @{ d='aa/StandaloneWindows64'; f='37a3fa2a88f657aa96c82c2ed0a480a3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='380d4f3e1540a02c2d348a684d3024da.bundle' },
    @{ d='aa/StandaloneWindows64'; f='397f18cc1af0b9fbfef0245f8e6bc2f7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='39f46bc90be7439ea3249fdf95946f00.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3d4d268843495a549d1b1988321f3211.bundle' },
    @{ d='aa/StandaloneWindows64'; f='3ec1b3ae9a58695c66d528eda0662325.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4056c2d68c11c0c559766c76900c3cd3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='416ed1508ea24f50c61db0a167ec69f1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='41f2c779703449dc1eb1977cdee29133.bundle' },
    @{ d='aa/StandaloneWindows64'; f='424269a81b5f3268a3fd5a8feb2032c4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='426357db25a1b93b5c1288bb7273cb7c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='427085c0815ae255bf4c8f5df5f06e20.bundle' },
    @{ d='aa/StandaloneWindows64'; f='447b443aee51cf58b0bc5f500d7caaac.bundle' },
    @{ d='aa/StandaloneWindows64'; f='44bb4685becf3220db47323f7bd1d4c2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='452346884447fc6225ac6956d7dee77f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4684253b1e6cbf9c240aca15615d3b14.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4707a849977287c1d56c958f0ea981a2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='487b742dadd3d329a34a6c3dadf93e53.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4898ef21af74dad84f0dc1b0194b333a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='49d33d0510755d1f1bccf0d596849411.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4a07ac8180aba1c4807e5cc257d79c23.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4a4009ca1b20c98ca8298f7a4948af5b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4ab73a797f5df51084def28e108c4330.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4ac06de5dbdc71be9b8b2f69774ba762.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4b14a7b5ff54f5cd1b0aeaefd84a6bac.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4d78454c9ccdd5454cd762ac154d5e85.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4e6f06e5637c81a09755e5024864e1fd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4e8ba99716ab8fa358f0b7f320b955ef.bundle' },
    @{ d='aa/StandaloneWindows64'; f='4eec05445de8496e4fd8a3b2f9593e41.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5071de09b2e4718e4218cdce0ad53ad0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='50cca5bf1b62f1cfae1ca283bf49c1b0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='515a9b41d1e72419dcb31d1bcf0a7b4f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='51e0143be0625f2ac770c1ab8d1399ca.bundle' },
    @{ d='aa/StandaloneWindows64'; f='548d3f81153565e314f18f183670be58.bundle' },
    @{ d='aa/StandaloneWindows64'; f='559997aa474dd244bad34d353aa65cd7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5653724352bcb946ea39bf526806c6f2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='56572506b180b75a553be5ab0435478a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5708484a204e3f603b874d8aadbb2ff0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='57e34950687b7ba18e26c0878ea02f67.bundle' },
    @{ d='aa/StandaloneWindows64'; f='590fa637a6305a0a9570b207dd0e8298.bundle' },
    @{ d='aa/StandaloneWindows64'; f='59171c81d0ffbdfb4e42f68448de7591.bundle' },
    @{ d='aa/StandaloneWindows64'; f='59ce463967d9493ea921d60863a418d7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5a0a3c89b349b87af08d25366a258676.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5cd7b0e1c7dfa85a22eb8dd1b4c4e9e3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5d320a7a198221fea96ca44f6d59c95b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='5eab9aef0e9ea43f22270bac889a4349.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6015c0f7495122f3758799de122c89b6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='60e344c763c9dc62fa01fd9668d1fcd8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6240cf9b1416c664e0ca55eb8bd9ccef.bundle' },
    @{ d='aa/StandaloneWindows64'; f='633dfcda5872cb3b644cb5207eb8fc5e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='64c7cf6718bcfd407df79e38e5d6855b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='670c829edfd7500627f778d8badbe764.bundle' },
    @{ d='aa/StandaloneWindows64'; f='68b8c9f6d7c95389f78cedb2e39a26ba.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6a61c452df492c97040a9d1f5057d42e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6acc92517c5470c75ce274854aa2cd27.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6bea05dafbc6092b957bfe4fb832def1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='6cfc312028dd27ae664986351eed9809.bundle' },
    @{ d='aa/StandaloneWindows64'; f='70f9a08840d907cc50a3f478a855bae8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7122c4302c5e3d1899474f2d9983b26f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='716beac9e10a124051c14dddd92b25d9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7181738e46ea5901ac8aeadeae26ca0f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='71b80d42453699cd868d80db0ddd75f0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='73ec6c90df23caafd2cfd5c0b0b6d017.bundle' },
    @{ d='aa/StandaloneWindows64'; f='745a6dd7e63699f57bf2de53f1b031c4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='759a32cb33a1d98108de16653174df97.bundle' },
    @{ d='aa/StandaloneWindows64'; f='75aab3b4d03f2c8914c4ddf967e03b4a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='766aece0a641e39a419e0c0130d6d93d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='77f0b13bdf4eaae112793f8e45c6b8e6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='784da113e4e987b7feed9aa814f19fea.bundle' },
    @{ d='aa/StandaloneWindows64'; f='785a3b37fe11742a3ac6aaebb3ce3f47.bundle' },
    @{ d='aa/StandaloneWindows64'; f='79ae6877a213634925e5ca19950d1401.bundle' },
    @{ d='aa/StandaloneWindows64'; f='79c48b013a3b0affd26436ca57235228.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7a299865ea3a49fc575a61630cb47d81.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7b003e1142de495f94da83be0cb43905.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7bdc955b25f6400e457ee174a3e467ce.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7cd620053d18a6fa7c8a03ef4670fa41.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7f5aa93b22ec2258a00cdbaf91034a84.bundle' },
    @{ d='aa/StandaloneWindows64'; f='7fcbc5c34c3c1c516ac7976395dd7284.bundle' },
    @{ d='aa/StandaloneWindows64'; f='807d239a11e5d75cbd830a191f9fb15d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='809732b260897384bbf68079ca6b1943.bundle' },
    @{ d='aa/StandaloneWindows64'; f='831dd1c0e63d460041e0d936aac21029.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8375c1e6ada48f94a1bb181ad4786ec9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='837eeb3554a73b5d136bc75690abfe81.bundle' },
    @{ d='aa/StandaloneWindows64'; f='83bf0a2d0455581756a3748c29563d91.bundle' },
    @{ d='aa/StandaloneWindows64'; f='845eb58dc585c720dbdabc2245ffeeea.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8513dbef12677e973f9b6a9f1650fb1d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='85987786387f93f975cd2cced0e46393.bundle' },
    @{ d='aa/StandaloneWindows64'; f='87c3ad9885ff965e163d30b3f7b6c629.bundle' },
    @{ d='aa/StandaloneWindows64'; f='885ae7c9f773d97a898a0d2ab5e0e2c8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8956f85e06b40ee7b6771f43937eaca2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8ac211eb5aabcd5c08351f0278b7759f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8aef7f097f11f256d848d7bb66479a14.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8b4d8065d5315ced804603e160a045d1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8c2f1f8aa54da62aec20f21f2ad08c78.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8c65946e751d4cfc57ac297815dfc7e5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8c9ab9751118e3cdbe0aa1ff5a9045c2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8d8aa088c0da1d07d145a332c2ae5de0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8e18a0e9d390b5d8c5471ce35bbf7ed7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8f16d787d45e9898f8274d018fc62026.bundle' },
    @{ d='aa/StandaloneWindows64'; f='8f4e8331f168a27dc1b38954523cd99a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='91b5c927cfaa2a285cee1ea829f526f0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='92e7197e8b1fd76ec742d3b506edf44f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='946460749ef5a9177af92534e461d30c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='947585c9fa38a3438eeb5cf9fae5b543.bundle' },
    @{ d='aa/StandaloneWindows64'; f='94aab63746f35a0f91118f367b23164c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='95cba55918a06a957d8286250175fdce.bundle' },
    @{ d='aa/StandaloneWindows64'; f='95efeef7803a73b954e3e1c252d5593e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='96e48d9721d16cbbb40196437c4e944e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='971bb16c7f524efe348c1f65fa554ef7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='97a6a173dd1fbcbbac1ad484f33f6cbd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='98d556b8cf5044868d12cc330e81a024.bundle' },
    @{ d='aa/StandaloneWindows64'; f='99118ee8c185453cdf44c1416648bd9d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='99896957616410a9c63e67087e7f12a1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9ab35915ab7322e8a4932c43a609af82.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9b5b077ff5c227d7a271175809e45613.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9e3cbf1ce2805aec1c68f55201845a49.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9f7f5de0fbd04b5ecee08eaa8420a2ff.bundle' },
    @{ d='aa/StandaloneWindows64'; f='9ff4738370e401388a9a8b3d1dcea762.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a22938be73b605e84f98892195476142.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a52addd3f655c34a16108a9b72fb3cdf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a57e7b70e88acdb036d7c6d2c356d2bf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a5ae80e5507531b13231bb79a571f4ae.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a5d675ac4edf9e31bb757bd80a1d851b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a6bd2c15991c0c4096d19ec5585a1712.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a8a9d01ad28fda2f0c81931c9c7a791e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a966d2e73cf44620e4b4886c2cba21b2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='a9e9bc66f17cbbcd34d5983c7950dd24.bundle' },
    @{ d='aa/StandaloneWindows64'; f='aad55d1a8da9adce022bc017cbfe7657.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ab6612ad7a721d2cf6f4de55937adfa7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='abe89dcfb15653adc53e89b258db67c1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ad76b7772d1d680a060280e7717a339f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='af7c5932bd1b88458aa7893425778f81.bundle' },
    @{ d='aa/StandaloneWindows64'; f='aff35e28358d85b0febd1c090891a47c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b0d8980e32fe1cb6c2ba0343669b3e81.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b182044242487bf9964f65329dc84af9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b2194c459bd3dd8251ca1573c8fad6df.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b3ad58b12f373888ec58aa40cd598aa4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b4befca799f9df594746da4b0ac03c46.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b5604f9895e9acc5e5db66b3b2f27e5e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b5e050100db3a712edcf579b3b6f5ce4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b63996b630f1238e742b2ebae6bee98e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b7f48b882f737e54c39557e1e8308f95.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b8cd79f4f4a74ab3313b26bd52175a86.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b8e7cf37940dbeeccc9498269fe6b74e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b8ebe12ee63a71e80d3e47504ec26d56.bundle' },
    @{ d='aa/StandaloneWindows64'; f='b8f30b8b6f0efa0496b9d89f93182c63.bundle' },
    @{ d='aa/StandaloneWindows64'; f='bb22805cd6069287ebdcf7cf0baf3463.bundle' },
    @{ d='aa/StandaloneWindows64'; f='bf74fc4fafe1b159ba82e2574d8ec4c5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='bffbf80782b0e3ba281bdfc2216ad05c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c0aa0ab9d35cabc47cee52d8ebcff378.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c12c34be4aa61649a3d3802cc93a9297.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c15d42296a1610ccf613f57e3362df61.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c2703119ec61e1b387debed1e04a6fec.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c2dfa8a23fa2d64972d326ee5edb137a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c34b7abb362696340dc4dfe9c6c3be45.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c4cb84cc63596ecd3808ea6a7423d9db.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c7130642ea306d0f4ae73fedf4dcdfd9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c7f2557ca2668096d9bc72dcc8afafb9.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c86fa85a1df7d85862603905f0b63ac3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c870aed952cd591497dd5db1cfa154d2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='c9e8ea95d55e42a3b8c40368c3090854.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ca4df331ccedc934c2bc3341eafe07e8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cbdd772402024130077a3cccf84fce27.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cc1074e4651073b4d03c1e02c4af3f67.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cc1241eb4b77242b592a3af54ed5d75d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cd2b576be663b0d8f03a156d994226fd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cec56f8ff116f8475f738137ba238b03.bundle' },
    @{ d='aa/StandaloneWindows64'; f='cf42adcc75eaf6e56efb2485053c05a3.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d082863d1f006e0bc4009e942b10677c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d15e0d4ed11b6d0a30cfc434c618307c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d2401470d622b52c1e2177b64c065e60.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d37a6b74c4a192611a6a9f171f76859f.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d3cf49d586fac5906cd1f34805b3cc3a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d5357f5a2a42a8c9ff52d0f39789cd39.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d6aa34270fd3e7ec849c97eab071ac75.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d6b2448c445e3220a9819a6695d83e61.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d6cef115f6d87c79554a9a2950997fc2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d899950892f5fe72583d97bc49dc3cdb.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d994153ac7bd135afba7f2556df48e28.bundle' },
    @{ d='aa/StandaloneWindows64'; f='d9b7a57aaac9ea65846b4e562f7fdc92.bundle' },
    @{ d='aa/StandaloneWindows64'; f='da3ff3673e2671e0d94af54fff1df501.bundle' },
    @{ d='aa/StandaloneWindows64'; f='dd0cd317fa3250bab35c115a27bfeb62.bundle' },
    @{ d='aa/StandaloneWindows64'; f='de1f4235b5105c2818e88b28c95c8a92.bundle' },
    @{ d='aa/StandaloneWindows64'; f='de23294353fe9172561db52904fcccb4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='df802829cca60c3f15a9ba0d67e694d6.bundle' },
    @{ d='aa/StandaloneWindows64'; f='df8b1416a110936fc894ed70e8740ea8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e06493d361aa8cd6068fdf7d1bb61a6a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e18402fca38696a96eea5a8ccdc4de0b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e1e002884ce0eda42df20c45fddf3c23.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e3964164279216ed6574d4d343b0b444.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e506e7b9f8ffb1e6f3840d3bdd1d78b5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e56fe160873860458923fe787a2c5dfc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e5f8be22ad3252aaec99f9925e2325b1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e702781eb305ed0dd1632216b51869cf.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e71fb0e67cd2b582bb2f8f0bd2f7f207.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e76fa07edec348670960a853b55ab2e2.bundle' },
    @{ d='aa/StandaloneWindows64'; f='e8fd6fcf136645ff7f8f22da77c717e5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ea9712726adde4732769b8adc71c5e02.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ea993ab015aa746a6e1085bac51f33a7.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ea9a76b586578b4bde15fb2b880efd14.bundle' },
    @{ d='aa/StandaloneWindows64'; f='eaf6f4d3120d534c2d3b72a9accb0ea1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ebbad0123f0e1ccab9b173a3c53ebfcd.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ebe7409a6bbe7c3c4b0647e4354565ca.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ecb1ccd875c32d73a5a53a0b84d6f4b0.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ecbf1dcf08d98285b78785709c322ce1.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ecdd742dd3fe39e72284f5535cbd4661.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ed0c66b70243751cebb6cb0968771acc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ee216276611c4a635937b2601440eba4.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ee7096acd8fec1736816e42e55fb24ab.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ef0f7e7b16fc25d48a6e5f364365455a.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ef24450456a29344df7ba393e1d1514b.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ef4e7549c47cd7ac89930ce18479f146.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f0de62623199bee63e1d1c8901abcdc5.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f0f1da9c1bdb5dbc58acd7a0b81ce536.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f16a18ea70d21c1e93704da4b47ffced.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f2db19caf8f3bfff76bedb45a97dd638.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f355093b43624184bf4ff2d134168b69.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f3d6c3282c5df08ad968090b97b08b92.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f3f1acec04ceb84641f7aaff03e1533d.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f49e857b8cb485db944ebf3996cb9446.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f59858dde2b806eb39925f7c4f9fbc80.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f6717302a49807f9fc74bd30c9765761.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f72d4259aebf3eaa16290c945a352eda.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f7d889b868205a646e78f6243c651d35.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f8349336640f145e38cebdf5bf33e36e.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f86504aa2239be986b80db57c9fe15e8.bundle' },
    @{ d='aa/StandaloneWindows64'; f='f9dc186c21bc5cdf50425dc828dcea76.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fb639b982667e16390067585dedbea32.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fda7cee0065279ed1219ecf1cd9f7866.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fdc64bd4c5d7e9039442c13a6e629c45.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fdeda0e436362b65563bb0a4f683877c.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fe0c6c1a63655d9e02899dc32e81b008.bundle' },
    @{ d='aa/StandaloneWindows64'; f='fea2eb95ce1e1fdf5b59b018655cc2cc.bundle' },
    @{ d='aa/StandaloneWindows64'; f='ff43942f025d02edc78fb9b9bdf60533.bundle' }
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
    Write-Host "Wgraj SRW_Y_BVC.zip na Drive (ten sam folder projektu) i napisz, ze jest."
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
