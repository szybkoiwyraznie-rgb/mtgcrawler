# SRW Y - krok S6: co mam Ci wrzucić (tekst do pakietu tłumacza)

Wersja arkusza: 2026-10-25.1

## Po co to

Pakiet dla tłumacza musi zawierać **cały tekst gry**: 24 tabele językowe (nazwy,
umiejętności, opisy, interfejs) oraz ~4 100 skryptów scenariusza (dialogi, narracja,
warunki misji). Tłumacz dostaje japoński oryginał + angielską wersję jako odniesienie
i pisze polski.

Nie potrzebuję całego `StreamingAssets` (tam jest 20 GB audio, wideo i tekstur).
Tekst siedzi w **42 plikach `.bundle`**, razem
**33.1 MB**, z czego część już mam. Brakuje **38 plików,
21.4 MB**.

| rodzina | co to | plików | mam | potrzebuję |
|---|---|---|---|---|
| tabele językowe `ja-JP` + `en-US` | interfejs, nazwy, opisy, DLC | 12 | 2 | 10 |
| skrypty scenariusza `jp` + `en` | dialogi i narracja misji | 30 | 2 | 28 |

## KROK 1 - zbierz pliki (nic nie jest usuwane, tylko kopiowane)

Skopiuj **cały** blok poniżej do PowerShella i wklej. Zrobi na Pulpicie folder
`srw_y_tekst` i plik `srw_y_tekst.zip`.

```powershell
# SRW Y - zbior tekstu do pakietu tlumacza (na Pulpit; nic nie jest usuwane)
$aa    = 'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'
$desk  = [Environment]::GetFolderPath('Desktop')
$dst   = Join-Path $desk 'srw_y_tekst'
$zip   = Join-Path $desk 'srw_y_tekst.zip'
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

$brak = @(); $suma = 0
foreach ($f in $pliki) {
    $src = Join-Path $aa $f
    if (Test-Path $src) {
        Copy-Item $src (Join-Path $dst $f) -Force
        $suma += (Get-Item $src).Length
    } else { $brak += $f }
}

"skopiowanych plikow: " + ($pliki.Count - $brak.Count) + " z " + $pliki.Count
"razem bajtow: " + $suma.ToString('N0')
if ($brak.Count -gt 0) { "BRAKUJE:"; $brak }

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
$i = Get-Item $zip
"zip: " + $i.FullName
"zip bajtow: " + $i.Length.ToString('N0')
"zip sha256: " + (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
```

Na końcu mają wyjść trzy linie: `skopiowanych plików: 38 z 38`,
`razem bajtow: 22,459,767` (mniej więcej) i `zip sha256: ...`.
Jeśli pokaże się `BRAKUJE:` - wklej mi tę listę, sprawdzę nazwy.

> Ten blok **nie był u mnie uruchamiany** - w środowisku, w którym pracuję, nie ma
> PowerShella ani gry. Jest napisany pod PowerShell 5.1 (żadnych poleceń, których
> 5.1 nie ma) i niczego nie usuwa: tylko kopiuje pliki na Pulpit i pakuje zip.

## KROK 2 - wrzuć na Dysk

Wrzuć `srw_y_tekst.zip` z Pulpitu do tego samego folderu na Dysku Google, w którym
leżą poprzednie paczki (SRW / SRWY), i napisz jedno słowo, że jest.

## Czego NIE potrzebuję

| pytanie | odpowiedź |
|---|---|
| całe `StreamingAssets` | **NIE** - wystarczy 38 plików z listy |
| japońskie audio / wideo / tekstury | **NIE** - w nich nie ma tekstu |
| podmieniać ISO | **NIE** - to wersja PC |
| przerabiać DLC | **NIE** - tabele DLC są w tych samych 12 bundlach, więc są na liście |
| PBOOT | **NIE** |

## Co się potem stanie

1. Wyciągam tekst z tych bundli (są zaszyfrowane naszym znanym kluczem).
2. Buduję pliki `.md` w formacie sprawdzonym w OE: japoński, `EN:` jako odniesienie,
   `PL:` do wpisania, przy każdym elemencie `limit:` z budżetem znaków.
3. Sceny dostają kontekst: tytuł misji, mówcę każdej kwestii, listę uczestników i serie.
4. Wynik: `plik_dla_tłumacza.zip` (instrukcja + `sceny/` + `widoki/`).

Do czasu, aż przyjdzie zip, pracuję na tym, co mam: 4 bundle już są u mnie
(tabele `ja-JP`/`en-US` + dwa skrypty scenariusza), więc mogę zbudować i pokazać
najpierw **próbkę dokładnie w docelowym formacie**.
