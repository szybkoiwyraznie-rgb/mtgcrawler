# SRW Y - krok S6b: indeksy DLC (13 MB, nie całe DLC)

Wersja arkusza: 2026-10-25.1

## Dobra uwaga - miałeś rację

W arkuszu S6 policzyłem tekst tylko z **podstawki** (`aa\catalog.json`). Tymczasem
obok `aa` jest **10 osobnych zestawów DLC**, a każdy ma **własny indeks**
(`catalog_<nazwa>.json`) i **własne bundle** - razem 6 576 plików `.bundle` i 3,6 GB:

| folder obok `aa` | indeks | rozmiar indeksu |
|---|---|---|
| `AnniversaryExpansionPack` | `catalog_anniversaryexpansionpack.json` | 5,308,249 B |
| `BonusMission` | `catalog_bonusmission.json` | 416,490 B |
| `DeluxeEdition` | `catalog_deluxeedition.json` | 15,054 B |
| `Dlc1` | `catalog_dlc1.json` | 1,640,455 B |
| `Dlc2` | `catalog_dlc2.json` | 1,593,357 B |
| `EarlyPurchase` | `catalog_earlypurchase.json` | 68,160 B |
| `ExpansionPack` | `catalog_expansionpack.json` | 3,031,427 B |
| `PremiumSound` | `catalog_premiumsound.json` | 103,933 B |
| `SeasonPassBonus` | `catalog_seasonpassbonus.json` | 1,148,607 B |
| `UltimateEdition` | `catalog_ultimateedition.json` | 15,072 B |

Katalog podstawki tych bundli **nie opisuje**, więc bez tych indeksów nie mogę
powiedzieć, które bundle DLC zawierają tekst. Same indeksy to **13,341,124 B
(12.7 MB)** - i po nich wskażę dokładnie te bundle DLC, które
trzeba skopiować. Podejrzewam, że będzie to kilka MB: np. cały `BonusMission` to
274 bundle i tylko 3,6 MB.

## KROK 1 - zbierz indeksy

Skopiuj **cały** blok poniżej do PowerShella:

```powershell
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
```

Ma wyjść `skopiowanych plików: 20 z 20`
i `razem bajtow: 13,341,124`. Jeśli pokaże się `BRAKUJE` - dopisz mi, których,
to znaczy, że tej części nie masz zainstalowanej.

> Ten blok **nie był u mnie uruchamiany** (brak PowerShella i gry w tym środowisku);
> napisany pod PowerShell 5.1, nic nie usuwa - tylko kopiuje i pakuje.

## KROK 2 - wrzuć na Dysk

Wrzuć `srw_y_dlc_catalog.zip` z Pulpitu do tego samego folderu na Dysku co
`srw_y_tekst.zip`. Potem dostaniesz ode mnie **drugą, krótką listę** - już tylko
te bundle DLC, w których faktycznie jest tekst.

## Czego nie potrzebuję

- całych folderów DLC (3,6 GB) - tylko indeksy i potem garść bundli z tekstem,
- `PremiumSound` to głównie audio (163 MB) - z indeksu wyjdzie, czy jest tam
  lista tytułów do tłumaczenia,
- podmiany ISO / PBOOT - **nie**, to wersja PC.
