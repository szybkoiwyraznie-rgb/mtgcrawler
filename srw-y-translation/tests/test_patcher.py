"""The patcher is linted, not run: there is no PowerShell here and the owner's console closes.

A syntax error in `PATCHER.ps1` would cost a round trip and look like "the patch does not
work" (2026-10-25: a trailing comma in an array literal made PS 5.1 stop with a parse error
and the window disappeared before the message could be read). So the generated files are
checked the way PowerShell 5.1 reads them:

* `PATCHER.ps1` starts with a UTF-8 BOM and uses CRLF — without the BOM 5.1 reads the file
  as ANSI and every Polish word becomes mojibake;
* `PATCHER.bat` is pure ASCII — the console code page garbles anything else;
* brackets balance outside string literals, no trailing comma before a closing paren;
* `MANIFEST.txt` agrees with `pliki/`, carries two different 64-hex hashes per file, and
  every patched bundle really differs from its original in `local/`.

    python3 -m pytest tests/test_patcher.py -q
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pytest  # noqa: E402

import build_patcher  # noqa: E402

SOURCES = [Path(p) for p in build_patcher.DEFAULT_SOURCES]


def strip_strings(source: str) -> str:
    """Drop '...' and "..." contents so bracket counting sees code only."""
    out, index = [], 0
    while index < len(source):
        char = source[index]
        if char == "'":
            end = source.find("'", index + 1)
            if end < 0:
                break
            index = end + 1
            continue
        if char == '"':
            index += 1
            while index < len(source) and source[index] != '"':
                index += 2 if source[index] == '`' else 1
            index += 1
            continue
        out.append(char)
        index += 1
    return ''.join(out)


@pytest.fixture(scope='module')
def kit(tmp_path_factory):
    if not any(Path(src).is_dir() for src in SOURCES):
        pytest.skip('brak zbudowanych plikow (build/test6)')
    bundles, originals = build_patcher.collect(SOURCES)
    out = tmp_path_factory.mktemp('patcher')
    zip_path = out / 'SRW_Y_PATCHER.zip'
    info = build_patcher.write_patcher(out / 'kit', bundles, originals, zip_path)
    return out / 'kit', zip_path, info, bundles


@pytest.mark.parametrize('name', ['PATCHER.bat', 'COFNIJ.bat'])
def test_bats_are_ascii_and_crlf(kit, name):
    _dir, _zip, _info, _b = kit
    raw = (_dir / name).read_bytes()
    assert raw.decode('ascii') is not None, f'{name} musi byc czystym ASCII'
    assert b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n', b''), f'{name}: CRLF'
    text = raw.decode('ascii')
    assert 'PATCHER.ps1' in text and 'pause' in text
    assert '-Tryb' in text and '-FolderGry' in text


def test_one_double_click_installs_without_a_menu(kit):
    """Like the OE patcher: no options, no questions - the bat says what to do."""
    _dir, _zip, _info, _b = kit
    install = (_dir / 'PATCHER.bat').read_text(encoding='ascii')
    undo = (_dir / 'COFNIJ.bat').read_text(encoding='ascii')
    assert 'set "TRYB=instaluj"' in install
    assert 'set "TRYB=cofnij"' in undo
    assert 'choice' not in install.lower()  # no menu prompt
    ps1 = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    assert '1 - zainstaluj' not in ps1
    assert "$choice = Read-Host" not in ps1


def test_ps1_has_bom_and_crlf(kit):
    _dir, _zip, _info, _b = kit
    raw = (_dir / 'PATCHER.ps1').read_bytes()
    assert raw.startswith(b'\xef\xbb\xbf'), 'brak BOM - PS 5.1 przeczyta plik jako ANSI'
    assert b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n', b''), 'PATCHER.ps1: CRLF'
    text = raw[3:].decode('utf-8')
    assert 'ą' in text or 'ę' in text, 'polskie komunikaty powinny byc w UTF-8'


def test_ps1_brackets_balance_outside_strings(kit):
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    code = strip_strings(text)
    for opening, closing in (('{', '}'), ('(', ')'), ('[', ']')):
        assert code.count(opening) == code.count(closing), f'{opening}{closing} nie bilansuja sie'
    depth = 0
    for char in code:
        depth += {'{': 1, '}': -1}.get(char, 0)
        assert depth >= 0, 'zamykajacy nawias bez otwierajacego'
    assert depth == 0


def test_ps1_has_no_trailing_comma_before_closing_paren(kit):
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    assert re.findall(r',\s*\n\s*\)', text) == [], 'PS 5.1 rejectuje przecinek przed )'


def test_ps1_contains_the_three_modes_and_a_verified_copy(kit):
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    for needle in ('function Install-All', 'function Check-All', 'function Revert-All',
                   'Get-FileHash', 'Copy-Item', 'Read-Host', 'RAPORT_PATCHERA.txt',
                   "if ($Tryb -eq 'cofnij')", "if ($Tryb -eq 'sprawdz')"):
        assert needle in text, f'brak {needle}'
    # the copy is hashed again afterwards and compared with the manifest
    assert '$after -eq $patched' in text
    # an unknown file in the game is never overwritten
    assert '$current -ne $original' in text


def test_ps1_refuses_to_patch_a_running_game(kit):
    """Windows keeps the bundles open; copying into a running game is how installs break."""
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    assert 'function Test-GameRunning' in text
    assert 'if (Test-GameRunning)' in text
    assert 'Zamknij ją całkowicie' in text


def test_ps1_copies_through_a_temporary_file(kit):
    """A crash mid-copy must not leave half a bundle in the game."""
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    assert "$temp = $target + '.nowy'" in text
    assert 'Move-Item -LiteralPath $temp -Destination $target -Force' in text


def test_manifest_rows_are_objects_not_arrays(kit):
    """A one-row manifest would unroll `@(name, hash, hash)` into three strings."""
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    assert '[pscustomobject]@{ Name = $parts[0]; Original = $parts[1]; Patched = $parts[2] }' in text
    assert '$row[0]' not in text and '$row[1]' not in text and '$row[2]' not in text


def test_ps1_notices_an_incomplete_kit(kit):
    """Owner copies the .bat only -> say so, do not report 13 missing files in the game."""
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    assert 'Paczka niekompletna' in text
    assert 'foreach ($row in $rows) {' in text


def test_ps1_finds_the_game_without_help(kit):
    """Same as OE: try the usual places first, ask only when that fails."""
    _dir, _zip, _info, _b = kit
    text = (_dir / 'PATCHER.ps1').read_bytes()[3:].decode('utf-8')
    assert 'function Find-Game' in text and 'function Ask-Game' in text
    assert '[System.IO.DriveInfo]::GetDrives()' in text
    assert 'steamapps\\common' in text
    assert 'sciezka.txt' in text  # the answer is remembered between runs


def test_manifest_matches_the_files_and_carries_two_hashes(kit):
    _dir, _zip, _info, bundles = kit
    lines = [line for line in (_dir / 'MANIFEST.txt').read_text(encoding='utf-8').splitlines()
             if line.strip() and not line.startswith('#')]
    assert len(lines) == len(bundles)
    names = set()
    for line in lines:
        name, original, patched = line.split('|')
        names.add(name)
        assert re.fullmatch(r'[0-9a-f]{64}', original)
        assert re.fullmatch(r'[0-9a-f]{64}', patched)
        assert original != patched, f'{name}: "polski" plik identyczny z oryginalem'
        assert hashlib.sha256((_dir / 'pliki' / name).read_bytes()).hexdigest() == patched
    assert names == set(bundles)
    assert {path.name for path in (_dir / 'pliki').glob('*.bundle')} == names


def test_zip_holds_the_whole_folder(kit):
    import zipfile

    _dir, zip_path, info, bundles = kit
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert {'PATCHER.bat', 'COFNIJ.bat', 'PATCHER.ps1', 'MANIFEST.txt',
            'CZYTAJ_TO.md'} <= names
    assert sum(1 for name in names if name.startswith('pliki/')) == len(bundles)
    assert info['zip_sha256'] == hashlib.sha256(zip_path.read_bytes()).hexdigest()


def test_the_same_bundles_give_the_same_zip(tmp_path):
    """Fixed timestamps: the published SHA-256 stays valid when the kit is rebuilt."""
    bundles, originals = build_patcher.collect(SOURCES)
    first = build_patcher.write_patcher(tmp_path / 'a', bundles, originals,
                                        tmp_path / 'a.zip')
    second = build_patcher.write_patcher(tmp_path / 'b', bundles, originals,
                                         tmp_path / 'b.zip')
    assert first['zip_sha256'] == second['zip_sha256']


def test_ps1_is_a_valid_powershell_document(kit):
    """Parse the script with a real PowerShell grammar, not just bracket counting.

    Needs `tree-sitter` + `tree-sitter-powershell`; skipped where they are absent, because
    the sandbox venv is not part of the repository. When present this catches the class of
    mistake that actually cost a round trip (a trailing comma in an array literal).
    """
    tree_sitter = pytest.importorskip('tree_sitter')
    grammar = pytest.importorskip('tree_sitter_powershell')
    _dir, _zip, _info, _b = kit
    source = (_dir / 'PATCHER.ps1').read_bytes()[3:]
    parser = tree_sitter.Parser(tree_sitter.Language(grammar.language()))
    tree = parser.parse(source)
    assert not tree.root_node.has_error, 'gramatyka PowerShell widzi błąd składni'
