<#
.SYNOPSIS
    Metadata-only inventory of an installed game folder (SRW Y project).

.DESCRIPTION
    Walks a game folder, reads the first 16 bytes of every file to recognise the
    container family, and writes ONE text report: relative path, size, magic
    family. It never copies file contents anywhere, so the report is safe to
    share - it contains no game data, and the folder prefix is stripped so it
    contains no user name either.

    Written for Windows PowerShell 5.1 (no external modules, no Python).

.PARAMETER Root
    The game folder, e.g. "D:\Games\SUPER ROBOT WARS Y".

.PARAMETER Out
    Where to write the report. Default: Desktop\srw_y_inventory.txt

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File inventory_build.ps1 -Root "D:\Games\SUPER ROBOT WARS Y"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $Root,

    [string] $Out = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'srw_y_inventory.txt')
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------- locate root
$rootItem = Get-Item -LiteralPath $Root -ErrorAction Stop
if (-not $rootItem.PSIsContainer) { throw "not a folder: $Root" }
$rootPath = $rootItem.FullName.TrimEnd('\')
$rootName = $rootItem.Name

# --------------------------------------------------------- magic-number table
# Order matters: the first matching prefix wins.
$magic = New-Object System.Collections.Specialized.OrderedDictionary
$magic.Add('CPK ',                                      'cri_cpk')
$magic.Add('UnityFS',                                   'unity_bundle')
$magic.Add('UnityWeb',                                  'unity_bundle_web')
$magic.Add('UnityRaw',                                  'unity_bundle_raw')
$magic.Add('PK' + [char]3 + [char]4,                    'zip')
$magic.Add([char]0x1f + [string][char]0x8b,             'gzip')
$magic.Add('BZh',                                       'bzip2')
$magic.Add([char]0xfd + '7zXZ' + [char]0x00,            'xz')
$magic.Add('7z' + [char]0xbc + [char]0xaf + [char]0x27 + [char]0x1c, '7z')
$magic.Add('SQLite format 3',                           'sqlite')
$magic.Add('MZ',                                        'pe_executable')
$magic.Add('BLTU',                                      'bltu_table')

function Get-MagicFamily {
    param([string] $Path, [long] $Length)

    if ($Length -lt 4) { return 'tiny' }
    $stream = $null
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        $buffer = New-Object byte[] 16
        $read = $stream.Read($buffer, 0, 16)
    } catch {
        return 'unreadable'
    } finally {
        if ($stream) { $stream.Dispose() }
    }
    if ($read -le 0) { return 'empty' }

    $head = ''
    for ($i = 0; $i -lt $read; $i++) { $head += [char]$buffer[$i] }

    foreach ($key in $magic.Keys) {
        if ($head.StartsWith($key)) { return $magic[$key] }
    }
    return ''
}

# ------------------------------------------------------------------ walk tree
Write-Host "scanning $rootPath ..."
$files = @(Get-ChildItem -LiteralPath $rootPath -Recurse -File -ErrorAction SilentlyContinue)

$flags       = @{}
$families    = @{}
$topLevel    = @{}
$rows        = New-Object System.Collections.Generic.List[string]
$totalBytes  = [long]0
$unreadable  = 0

$nameFlags = @{
    'gameassembly.dll'      = 'il2cpp_gameassembly'
    'unityplayer.dll'       = 'unity_player'
    'global-metadata.dat'   = 'il2cpp_metadata'
    'melonloader'           = 'melonloader_present'
    'bepinex'               = 'bepinex_present'
    'doorstop_config.ini'   = 'doorstop_present'
    'winhttp.dll'           = 'doorstop_proxy'
}

foreach ($file in $files) {
    $relative = $file.FullName.Substring($rootPath.Length + 1)
    $size     = $file.Length
    $totalBytes += $size

    $family = Get-MagicFamily -Path $file.FullName -Length $size
    if ($family -eq 'unreadable') { $unreadable++ }
    if ($family -and $family -ne 'unreadable') {
        if ($families.ContainsKey($family)) { $families[$family]++ } else { $families[$family] = 1 }
    }

    $top = $relative.Split('\')[0]
    if ($relative -notmatch '\\') { $top = '<root>' }
    if (-not $topLevel.ContainsKey($top)) { $topLevel[$top] = @{ files = 0; bytes = [long]0 } }
    $topLevel[$top]['files'] = $topLevel[$top]['files'] + 1
    $topLevel[$top]['bytes'] = $topLevel[$top]['bytes'] + $size

    $lower = $file.Name.ToLowerInvariant()
    foreach ($key in $nameFlags.Keys) {
        if ($lower.Contains($key)) { $flags[$nameFlags[$key]] = $relative }
    }

    $rows.Add(("{0}`t{1}`t{2}" -f $relative, $size, $family))
}

# ------------------------------------------------------------------- report
$stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('# SRW Y build inventory (metadata only: relative paths, sizes, magic numbers)')
$lines.Add("# generated: $stamp")
$lines.Add("# root_name: $rootName")
$lines.Add("# files: $($files.Count)")
$lines.Add("# bytes: $totalBytes")
$lines.Add("# unreadable_headers: $unreadable")
$lines.Add('')
$lines.Add('## flags')
if ($flags.Count -eq 0) { $lines.Add('(none)') }
foreach ($key in ($flags.Keys | Sort-Object)) { $lines.Add(("{0}`t{1}" -f $key, $flags[$key])) }
$lines.Add('')
$lines.Add('## container families')
if ($families.Count -eq 0) { $lines.Add('(none)') }
foreach ($key in ($families.Keys | Sort-Object)) { $lines.Add(("{0}`t{1}" -f $key, $families[$key])) }
$lines.Add('')
$lines.Add('## top level (files, bytes)')
foreach ($key in ($topLevel.Keys | Sort-Object)) {
    $lines.Add(("{0}`t{1}`t{2}" -f $key, $topLevel[$key]['files'], $topLevel[$key]['bytes']))
}
$lines.Add('')
$lines.Add('## files (relative path, bytes, magic family)')
foreach ($row in $rows) { $lines.Add($row) }

Set-Content -LiteralPath $Out -Value $lines -Encoding UTF8

# -------------------------------------------------------------- console recap
Write-Host ''
Write-Host ("files      : {0}" -f $files.Count)
Write-Host ("bytes      : {0}" -f $totalBytes)
Write-Host ("unreadable : {0}" -f $unreadable)
Write-Host 'container families:'
if ($families.Count -eq 0) { Write-Host '  (none)' }
foreach ($key in ($families.Keys | Sort-Object)) { Write-Host ("  {0,-20} {1}" -f $key, $families[$key]) }
if ($flags.Count -gt 0) {
    Write-Host 'flags:'
    foreach ($key in ($flags.Keys | Sort-Object)) { Write-Host ("  {0,-20} {1}" -f $key, $flags[$key]) }
}
Write-Host ''
Write-Host ("report written: {0}" -f $Out)
Write-Host ("size {0:N0} B, metadata only, no file contents" -f (Get-Item -LiteralPath $Out).Length)
