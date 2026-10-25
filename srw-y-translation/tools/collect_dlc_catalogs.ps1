# SRW Y - indeksy DLC (na Pulpit; nic nie jest usuwane)
$sa    = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets'
$desk  = [Environment]::GetFolderPath('Desktop')
$dst   = Join-Path $desk 'srw_y_dlc_catalog'
$zip   = Join-Path $desk 'srw_y_dlc_catalog.zip'
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$pliki = @(
    @{ d='AnniversaryExpansionPack'; f='catalog_anniversaryexpansionpack.json' },
    @{ d='AnniversaryExpansionPack'; f='catalog_anniversaryexpansionpack.hash' },
    @{ d='BonusMission'; f='catalog_bonusmission.json' },
    @{ d='BonusMission'; f='catalog_bonusmission.hash' },
    @{ d='DeluxeEdition'; f='catalog_deluxeedition.json' },
    @{ d='DeluxeEdition'; f='catalog_deluxeedition.hash' },
    @{ d='Dlc1'; f='catalog_dlc1.json' },
    @{ d='Dlc1'; f='catalog_dlc1.hash' },
    @{ d='Dlc2'; f='catalog_dlc2.json' },
    @{ d='Dlc2'; f='catalog_dlc2.hash' },
    @{ d='EarlyPurchase'; f='catalog_earlypurchase.json' },
    @{ d='EarlyPurchase'; f='catalog_earlypurchase.hash' },
    @{ d='ExpansionPack'; f='catalog_expansionpack.json' },
    @{ d='ExpansionPack'; f='catalog_expansionpack.hash' },
    @{ d='PremiumSound'; f='catalog_premiumsound.json' },
    @{ d='PremiumSound'; f='catalog_premiumsound.hash' },
    @{ d='SeasonPassBonus'; f='catalog_seasonpassbonus.json' },
    @{ d='SeasonPassBonus'; f='catalog_seasonpassbonus.hash' },
    @{ d='UltimateEdition'; f='catalog_ultimateedition.json' },
    @{ d='UltimateEdition'; f='catalog_ultimateedition.hash' },
)

$brak = @(); $suma = 0
foreach ($p in $pliki) {
    $src = Join-Path (Join-Path $sa $p.d) $p.f
    if (Test-Path $src) {
        $out = Join-Path $dst ($p.d + '_' + $p.f)
        Copy-Item $src $out -Force
        $suma += (Get-Item $src).Length
    } else { $brak += ($p.d + '\' + $p.f) }
}

"skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count
"razem bajtow: " + $suma.ToString('N0')
if ($brak.Count -gt 0) { "BRAKUJE (moze nie masz tej czesci):"; $brak }

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
$i = Get-Item $zip
"zip: " + $i.FullName
"zip bajtow: " + $i.Length.ToString('N0')
"zip sha256: " + (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
