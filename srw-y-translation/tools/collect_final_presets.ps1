# SRW Y - znajduje 3 ostatnie presety po wewnetrznej nazwie pliku CAB
# Skrypt NICZEGO nie zmienia w grze. Czyta tylko pierwsze 512 B kazdego bundla.
$ErrorActionPreference = 'Stop'
$desk = [Environment]::GetFolderPath('Desktop')
$log  = Join-Path $desk 'SRW_Y_PRESETY3_log.txt'
$dst  = Join-Path $desk 'SRW_Y_PRESETY3'
$zip  = Join-Path $desk 'SRW_Y_PRESETY3.zip'

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
    if (-not (Test-Path $sa)) { throw ('Nie ma folderu: ' + $sa) }

    $needles = @(
        'CAB-58e9cd9947154ef535126db225215ad0',
        'CAB-79ddf87b4d63e5a85be58e6e5bdadfe8',
        'CAB-cd5151f08eae3cb61aecc23bad1bd323'
    )
    # Haslo i sol z odzyskanego szyfru SeekableAesStream. Tylko do odczytu.
    $password = [Text.Encoding]::UTF8.GetBytes('ComBBStudioSRTeam')

    function Get-Key([string]$file) {
        $stem = [IO.Path]::GetFileNameWithoutExtension($file)
        $salt = [Text.Encoding]::UTF8.GetBytes($stem)
        $buf = New-Object byte[] ($password.Length + $salt.Length)
        [Array]::Copy($password, 0, $buf, 0, $password.Length)
        [Array]::Copy($salt, 0, $buf, $password.Length, $salt.Length)
        $sha = [Security.Cryptography.SHA1]::Create()
        $d = $sha.ComputeHash($buf)
        for ($i = 1; $i -lt 100; $i++) { $d = $sha.ComputeHash($d) }
        $key = New-Object byte[] 16
        [Array]::Copy($d, 0, $key, 0, 16)
        return $key
    }

    function Get-Stream([byte[]]$key, [int]$blocks) {
        $nonceBlocks = New-Object byte[] ($blocks * 16)
        for ($n = 1; $n -le $blocks; $n++) {
            $b = [BitConverter]::GetBytes([int]$n)
            [Array]::Copy($b, 0, $nonceBlocks, (($n - 1) * 16), 4)
        }
        $aes = New-Object Security.Cryptography.AesManaged
        $aes.KeySize = 128
        $aes.BlockSize = 128
        $aes.Mode = [Security.Cryptography.CipherMode]::ECB
        $aes.Padding = [Security.Cryptography.PaddingMode]::None
        $zero = New-Object byte[] 16
        $aes.IV = $zero
        $aes.Key = $key
        $enc = $aes.CreateEncryptor()
        $stream = $enc.TransformFinalBlock($nonceBlocks, 0, $nonceBlocks.Length)
        $enc.Dispose()
        $aes.Dispose()
        return $stream
    }

    function Decrypt-Head([byte[]]$key, [byte[]]$head) {
        $blocks = [int][Math]::Floor($head.Length / 16)
        $stream = Get-Stream $key $blocks
        $plain = New-Object byte[] $head.Length
        for ($i = 0; $i -lt $head.Length; $i++) {
            $plain[$i] = [byte]($head[$i] -bxor $stream[$i])
        }
        return $plain
    }

    # Samotest: znany szyfrogram musi dac naglowek UnityFS.
    # Jesli nie, skrypt zatrzymuje sie, zeby nie wysylac pustego zipa.
    $selftestName = 'srw_y_selftest.bundle'
    $selftestCipher = [byte[]]@(0x35, 0x6f, 0x74, 0x16, 0x46, 0x2f, 0xf6, 0xf8, 0x0c, 0xbd, 0x8b, 0x44, 0x43, 0xa0, 0xea, 0xb5)
    $selftestKey = Get-Key $selftestName
    $selftestPlain = Decrypt-Head $selftestKey $selftestCipher
    $selftestText = [Text.Encoding]::ASCII.GetString($selftestPlain)
    if (-not $selftestText.StartsWith('UnityFS')) {
        throw 'BLAD samotestu szyfru - nie wysylaj zipa, daj znac autorowi.'
    }
    Write-Host 'samotest szyfru: OK' -ForegroundColor Green

    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    New-Item -ItemType Directory -Path $dst | Out-Null
    $manifest = @()
    $found = @{}
    $count = 0
    $plainCount = 0
    $unknown = 0
    $files = Get-ChildItem -Path $sa -Filter '*.bundle' -Recurse -File
    foreach ($file in $files) {
        $count++
        if ($count % 2000 -eq 0) { Write-Host ('  sprawdzonych: ' + $count) }
        if ($file.Length -lt 32) { continue }
        $head = New-Object byte[] 512
        $fs = [IO.File]::OpenRead($file.FullName)
        try { $read = $fs.Read($head, 0, 512) } finally { $fs.Close() }
        $usable = [int]([Math]::Floor($read / 16) * 16)
        if ($usable -lt 16) { continue }
        $slice = New-Object byte[] $usable
        [Array]::Copy($head, 0, $slice, 0, $usable)
        $raw = [Text.Encoding]::ASCII.GetString($slice)
        if ($raw.StartsWith('UnityFS')) {
            $text = $raw
            $plainCount++
        } else {
            $key = Get-Key $file.Name
            $plain = Decrypt-Head $key $slice
            $text = [Text.Encoding]::ASCII.GetString($plain)
            if (-not $text.StartsWith('UnityFS')) {
                $unknown++
                continue
            }
        }
        foreach ($needle in $needles) {
            if ($text.Contains($needle)) {
                if (-not $found.ContainsKey($file.Name)) {
                    Copy-Item -Path $file.FullName -Destination (Join-Path $dst $file.Name) -Force
                    $found[$file.Name] = $true
                }
                $rel = $file.FullName.Substring($sa.Length).TrimStart('\', '/')
                $manifest += ($rel + ' | ' + $file.Name + ' | ' + $needle)
                Write-Host ('  ZNALEZIONO ' + $file.Name + ' -> ' + $needle) -ForegroundColor Green
            }
        }
    }
    $manifest | Set-Content -Path (Join-Path $dst 'manifest.txt') -Encoding UTF8
    Write-Host ''
    Write-Host ('sprawdzonych bundli: ' + $count)
    Write-Host ('jawne UnityFS: ' + $plainCount + ', nieznane: ' + $unknown)
    Write-Host ('znaleziono plikow: ' + $found.Count)
    if ($found.Count -lt 3) {
        Write-Host 'UWAGA: mniej niz 3 bundli. Wyslij zip mimo to - log wyjasni.' -ForegroundColor Yellow
    }
    if (Test-Path $zip) { Remove-Item $zip -Force }
    Compress-Archive -Path (Join-Path $dst '*') -DestinationPath $zip -CompressionLevel Fastest
    $info = Get-Item $zip
    $sha = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
    Write-Host ''
    Write-Host ('Gotowe: ' + $zip) -ForegroundColor Green
    Write-Host ('rozmiar: ' + $info.Length.ToString('N0') + ' bajtow') -ForegroundColor Green
    Write-Host ('sha256 : ' + $sha) -ForegroundColor Green
    Write-Host 'Wgraj SRW_Y_PRESETY3.zip na Drive i napisz, ze jest.'
}
catch {
    Write-Host ''
    Write-Host ('BLAD: ' + $_.Exception.Message) -ForegroundColor Red
    if ($_.InvocationInfo) { Write-Host ('linia: ' + $_.InvocationInfo.ScriptLineNumber) }
    Write-Host ('Pelny opis: ' + $log) -ForegroundColor Red
}
finally {
    Stop-Transcript | Out-Null
}

Read-Host "Nacisnij Enter, aby zamknac"
