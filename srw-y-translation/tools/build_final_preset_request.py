#!/usr/bin/env python3
"""Owner kit: find the LAST 3 preset bundles by their internal CAB file name.

88 of the 91 `preset_file` PPtr targets were resolved by `SRW_Y_PRESETY.zip`.
The remaining three missions (`m4003_0202500`, `m4020_0200230`, `m5003_0107330`)
point at CAB names that have no Addressables address, so no file name can be
looked up. This kit does not guess names: it scans every `.bundle` in
`StreamingAssets`, decrypts only the first 512 bytes with the already-recovered
SeekableAesStream cipher, and looks for the three literal CAB strings. The
serialized-file name sits at offset 92 of a decrypted bundle, measured on all
109 bundles of the previous return.

PowerShell 5.1 has SHA1 and AES-128-ECB in the BCL, so no Python, no game files
are copied wholesale and nothing is modified. A built-in known-answer test
aborts the script if the cipher port is wrong, so the owner never sends an empty
zip without knowing why.

Outputs (deterministic, same shape as the earlier kits):
    build/final_preset_request/SRW_Y_PRESETY3_PROSBA.zip
    tools/collect_final_presets.ps1
    docs/PROSBA_PRESETY3_Y.md
    local/s6/final_preset_request.json

    python3 tools/build_final_preset_request.py --dry-run
    python3 tools/build_final_preset_request.py
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_voice_speaker_request as kit_base  # noqa: E402

EVIDENCE = HERE / 'data' / 'preset_evidence.json'
PS1 = HERE / 'tools' / 'collect_final_presets.ps1'
PS_NAME = 'ZBIERZ_PRESETY3.ps1'
STEM = 'SRW_Y_PRESETY3'
KIT_DIR = HERE / 'build' / 'final_preset_request'
OUT_JSON = HERE / 'local' / 's6' / 'final_preset_request.json'
DOC = HERE / 'docs' / 'PROSBA_PRESETY3_Y.md'
CAB_RE = re.compile(r'^CAB-[0-9a-f]{32}$')

# Known-answer vector for the cipher port. Plaintext is exactly
# b"UnityFS\x00" + eight zero bytes; ciphertext comes from
# srw_y_bundle_crypt.encrypt() with the name below. The PowerShell script
# recomputes it and aborts if it does not decrypt back to "UnityFS".
SELFTEST_NAME = 'srw_y_selftest.bundle'
SELFTEST_CIPHER = (0x35, 0x6f, 0x74, 0x16, 0x46, 0x2f, 0xf6, 0xf8,
                   0x0c, 0xbd, 0x8b, 0x44, 0x43, 0xa0, 0xea, 0xb5)

PS_TEMPLATE = r'''# SRW Y - znajduje 3 ostatnie presety po wewnetrznej nazwie pliku CAB
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
@@NEEDLES@@
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
    $selftestName = '@@SELFTEST_NAME@@'
    $selftestCipher = [byte[]]@(@@SELFTEST_CIPHER@@)
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
'''


def survey() -> dict:
    """Read the three remaining CAB targets from committed evidence only."""
    data = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    remaining = data['pptr']['remaining']
    cabs = [row['cab'] for row in remaining]
    if len(cabs) != 3 or len(set(cabs)) != 3 or not all(CAB_RE.match(c) for c in cabs):
        raise ValueError(f'expected exactly 3 distinct CAB targets, got {cabs!r}')
    if data['pptr']['after'] != 3 or data['pptr']['before'] != 91:
        raise ValueError('unexpected PPtr counts in preset evidence')
    return {'targets': remaining, 'cabs': cabs,
            'archive_sha256': data['archive']['sha256'],
            'evidence_sha256': __import__('hashlib').sha256(
                EVIDENCE.read_bytes()).hexdigest(),
            'selftest_name': SELFTEST_NAME,
            'selftest_cipher': list(SELFTEST_CIPHER)}


def ps_block(plan: dict) -> str:
    needles = ',\n'.join(f"        '{cab}'" for cab in plan['cabs'])
    cipher = ', '.join(f'0x{byte:02x}' for byte in plan['selftest_cipher'])
    text = (PS_TEMPLATE
            .replace('@@NEEDLES@@', needles)
            .replace('@@SELFTEST_NAME@@', plan['selftest_name'])
            .replace('@@SELFTEST_CIPHER@@', cipher))
    text.encode('ascii')  # PS 5.1 reads a BOM-less file as ANSI
    return text


def readme(plan: dict) -> str:
    rows = '\n'.join(f"  {row['mission']}  ->  {row['cab']}  (PathID {row['path_id']})"
                     for row in plan['targets'])
    return f"""SRW Y - 3 ostatnie presety (skan po wewnetrznej nazwie CAB)
===============================================================

Co zrobic (3 kroki)
-------------------
1. Rozpakuj ten zip NA PULPIT.
2. Kliknij dwa razy URUCHOM_TO.bat.
3. Na pulpicie powstanie SRW_Y_PRESETY3.zip - wgraj go na Drive
   (folder projektu SRWY) i napisz, ze jest.

Skrypt NICZEGO nie zmienia w grze. Przeglada wszystkie pliki .bundle
w StreamingAssets, odczytuje tylko pierwsze 512 B kazdego z nich i
szuka trzech dokladnych napisow CAB. Potrzebne bundl e kopiuje do
jednego zipa (razem z manifest.txt). Moze to potrwac kilka minut -
co 2000 plikow wypisuje postep.

Po co to
--------
Dziekuje za SRW_Y_PRESETY.zip - rozwiazal 88 z 91 brakujacych wskaznikow
presetow. Zostaly dokladnie 3 misje:

{rows}

Te trzy cele nie maja w katalogach gry zadnego adresu, wiec nie da sie
podac nazw plikow do skopiowania. Kazdy bundle ma zaszyfrowany naglowek,
a w srodku (na pozycji 92 po odszyfrowaniu) jest jego wewnetrzna nazwa
pliku CAB. Skrypt ja odczytuje i porownuje z powyzszymi trzema napisami.

Skrypt ma wbudowany samotest szyfru: jesli odszyfrowanie znanego
szyfrogramu nie da naglowka UnityFS, zatrzyma sie z czerwonym komunikatem.
Wtedy nie wysylaj zipa - daj znac, poprawie skrypt.

Czego NIE robic
---------------
Nie wysylaj calej gry, audio, scen, katalogow ani GameAssembly.dll.
Nie zmieniaj nazw plikow w zipie - sa potrzebne do odszyfrowania.
Wynik to maksymalnie 3 male bundl e plus manifest.txt i log.

Jesli skrypt wypisze BLAD albo znajdzie mniej niz 3
----------------------------------------------------
Wgraj zip mimo to i napisz, co wypisal. Log jest na pulpicie:
SRW_Y_PRESETY3_log.txt.
"""


def render_doc(plan: dict, kit_info: dict | None = None) -> str:
    rows = '\n'.join(
        f"| `{row['mission']}` | `{row['cab']}` | `{row['path_id']}` | "
        f"`{row['script_file']}` |" for row in plan['targets'])
    result = f"""# PROŚBA — 3 ostatnie presety (`SRW_Y_PRESETY3_PROSBA.zip`)

Dokumenty powiązane: [`HANDOFF_READING_WYNIKI_2026-10-27.md`](HANDOFF_READING_WYNIKI_2026-10-27.md) §9,
[`PROSBA_PRESETY_Y.md`](PROSBA_PRESETY_Y.md). To **czwarty, ostatni kit**.

## Dlaczego nie wystarczą nazwy plików

`SRW_Y_PRESETY.zip` (109 bundli, SHA-256 `{plan['archive_sha256'][:12]}…`)
rozwiązał **88 z 91** wskaźników `preset_file` po dokładnej parze
(CAB, PathID). Zostały trzy:

| misja | brakujący CAB | PathID | `script_file` |
|---|---|---:|---|
{rows}

Dla tych trzech misji katalogi Addressables mają wyłącznie adresy
`_Normal` i `_Hard`; oba bundl e są już w zwróconej paczce, ale ich
wewnętrzne nazwy plików i PathID-y nie są celami wskaźników. Żadna
z 91 docelowych par nie występuje też w dziewięciu wcześniejszych
archiwach. Źródłem prawdy są [`data/preset_evidence.json`](../data/preset_evidence.json)
(`pptr.remaining`, SHA-256 `{plan['evidence_sha256'][:12]}…`).

## Co robi skrypt

`ZBIERZ_PRESETY3.ps1` (BOM + CRLF + ASCII, PowerShell 5.1, bez Pythona):

1. Znajduje `StreamingAssets` w typowych folderach Steam.
2. Dla każdego `.bundle` czyta pierwsze **512 B**.
3. Odszyfrowuje je znanym szyfrem `SeekableAesStream`
   (`PasswordDeriveBytes` SHA-1 × 100 → AES-128-ECB, licznik od 1, XOR).
   Pomiar na 109 bundlach: wewnętrzna nazwa `CAB-…` leży na pozycji **92**.
4. Porównuje z trzema dosłownymi napisami; trafione bundl e kopiuje do
   `SRW_Y_PRESETY3` wraz z `manifest.txt` (ścieżka, nazwa, który CAB).
5. Pakuje `SRW_Y_PRESETY3.zip` i wypisuje rozmiar + SHA-256.

**Samotest szyfru:** w skrypcie jest znany szyfrogram
(`srw_y_selftest.bundle` → `UnityFS\\0…`). Jeśli port kryptografii w .NET
byłby błędny, skrypt zatrzyma się z czerwonym komunikatem zamiast
odesłać pusty zip. Wektor jest też sprawdzany w `tests/test_final_preset_kit.py`.

Nic nie jest modyfikowane w grze; nie są kopiowane żadne inne pliki.

## Co uruchomić

**`SRW_Y_PRESETY3_PROSBA.zip`** — na Drive w folderze projektu
(id `18xIBclTKykKOP67fvJ55UZDMotGIVZA2`, @@KIT_SIZE@@ B,
SHA-256 `@@KIT_SHA@@`). W środku `URUCHOM_TO.bat`, `ZBIERZ_PRESETY3.ps1`,
`CZYTAJ_TO.txt`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_PRESETY3.zip`** — wgraj go na ten sam
   folder na Drive i daj znać. Razem z logiem, jeśli skrypt wypisał `BLAD`
   albo znalazł mniej niż 3 pliki.

## Co zrobię po otrzymaniu

1. Zweryfikuję SHA-256 i rozmiary; odszyfruję bundl e.
2. Sprawdzę dokładne pary (CAB, PathID) z trzema pozostałymi wskaźnikami.
3. Jeśli się zgadzają — przebuduję indeks i `deployment.md`;
   `structural_issues` powinno spaść do **0**.
4. Jeśli nie — podam liczbę i opis tego, co jest, bez zgadywania.
"""
    if kit_info:
        result = result.replace('@@KIT_SIZE@@', f"{kit_info['size']:,}")
        result = result.replace('@@KIT_SHA@@', kit_info['sha256'])
    else:
        result = result.replace('@@KIT_SIZE@@', '?').replace('@@KIT_SHA@@', '?')
    return result


def write_kit(plan: dict, out_dir: Path) -> dict:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    ps_text = ps_block(plan)
    ps_path = out_dir / PS_NAME
    ps_path.write_bytes(b'\xef\xbb\xbf' + ps_text.replace('\n', '\r\n').encode('ascii'))
    (out_dir / 'URUCHOM_TO.bat').write_bytes(
        kit_base.BATCH.replace('{ps_name}', PS_NAME).replace('\n', '\r\n').encode('ascii'))
    (out_dir / 'CZYTAJ_TO.txt').write_bytes(
        b'\xef\xbb\xbf' + readme(plan).replace('\n', '\r\n').encode('utf-8'))
    zip_path = out_dir / f'{STEM}_PROSBA.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.iterdir()):
            if not path.is_file() or path.suffix not in {'.ps1', '.bat', '.txt'}:
                continue
            info = zipfile.ZipInfo(path.name, date_time=kit_base.KIT_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return {'zip': str(zip_path), 'ps1': str(ps_path), 'size': zip_path.stat().st_size}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--out-dir', type=Path, default=KIT_DIR)
    p.add_argument('--json', type=Path, default=OUT_JSON)
    p.add_argument('--doc', type=Path, default=DOC)
    p.add_argument('--ps1', type=Path, default=PS1)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args(argv)

    plan = survey()
    print(f"celow: {len(plan['cabs'])}")
    if args.dry_run:
        for cab in plan['cabs']:
            print('  ', cab)
        return 0

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n',
                         encoding='utf-8')
    kit = write_kit(plan, args.out_dir)
    args.ps1.write_bytes(Path(kit['ps1']).read_bytes())
    import hashlib
    zip_bytes = Path(kit['zip']).read_bytes()
    args.doc.write_text(render_doc(plan, {
        'size': len(zip_bytes),
        'sha256': hashlib.sha256(zip_bytes).hexdigest()}), encoding='utf-8')
    print(f"kit: {kit['zip']} ({kit['size']:,} B)")
    print(f"ps1: {args.ps1}")
    print(f"doc: {args.doc}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
