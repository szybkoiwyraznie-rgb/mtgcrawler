"""The line-break fix: row list, table edit, and the kit the owner double-clicks."""
import json
import struct
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_lamanie_kit  # noqa: E402
import lamanie_opisow  # noqa: E402

ROWS = ROOT / 'data' / 'lamanie_linii_rows.json'
BUNDLES = ROOT / 'data' / 'ja_table_bundles.json'


def align4(value: int) -> int:
    return (value + 3) // 4 * 4


def make_table(name: str, records: list[tuple[str, str]]) -> bytes:
    """A table object in the game's layout, as `s6_tables` reads it.

    Same header the game writes: 28 zero bytes, name, locale, `u32 2`, 8-byte hash,
    `u32 0`, record count, then `[low][high][length][text][pad4][0]` per row and the
    8-byte terminator.
    """
    out = bytearray(b'\x00' * 28 + struct.pack('<I', len(name)) + name.encode())
    out += bytes(-len(out) % 4)
    locale = b'ja-JP'
    out += struct.pack('<I', len(locale)) + locale
    out += bytes(-len(out) % 4)
    out += struct.pack('<I', 2) + bytes(8) + struct.pack('<I', 0)
    out += struct.pack('<I', len(records))
    for key, text in records:
        high, low = (int(part, 16) for part in key.split(':'))
        encoded = text.encode('utf-8')
        out += struct.pack('<III', low, high, len(encoded)) + encoded
        out += bytes(-len(out) % 4) + bytes(4)
    out += struct.pack('<II', 2, 0)
    return bytes(out)


def test_the_row_list_matches_the_bundles_the_owner_sent():
    payload = json.loads(ROWS.read_text(encoding='utf8'))
    expected = {item['bundle']: item['size']
                for item in json.loads(BUNDLES.read_text(encoding='utf8'))['bundles']}
    assert payload['counts']['elements'] == 804
    assert payload['counts']['rows'] == 1042
    assert set(payload['bundles']) == set(expected)
    for name, entry in payload['bundles'].items():
        assert entry['size'] == expected[name]
        assert len(entry['sha256']) == 64


def test_no_row_changes_the_text_only_the_breaks():
    """A space becomes a newline: the record keeps its characters, so `limit:` holds."""
    payload = json.loads(ROWS.read_text(encoding='utf8'))
    assert all('\n' in row['pl'] for row in payload['rows'])
    assert all(row['pl'].replace('\n', ' ') == row['flat'] for row in payload['rows'])
    assert all(row['jp'] and row['key'] for row in payload['rows'])


def test_a_flat_row_gets_the_broken_text():
    row = {'bundle': 'x.bundle', 'table': 'skill_active_ja-JP', 'key': '00000001:00000002',
           'jp': '出撃時、気力＋１０。\nＨＰ３０％以下で「命中」＋１０。',
           'flat': 'Morale startowe +10. Przy HP do 30％: Celność +10.',
           'pl': 'Morale startowe +10.\nPrzy HP do 30％: Celność +10.'}
    raw = make_table('skill_active_ja-JP', [(row['key'], row['flat'])])
    new_raw, counts, conflicts = lamanie_opisow.table_edits('skill_active_ja-JP', raw, [row])
    assert counts['poprawione'] == 1 and not conflicts
    from s6_tables import table_header, walk_records

    start, count = table_header(new_raw, 'skill_active_ja-JP')
    records, _ = walk_records(new_raw, start, count)
    assert [record['text'] for record in records] == [row['pl']]
    assert count == 1


def test_japanese_original_is_accepted_too():
    row = {'bundle': 'x.bundle', 'table': 't_ja-JP', 'key': '00000001:00000002',
           'jp': '日本語', 'flat': 'Polski tekst.', 'pl': 'Polski\ntekst.'}
    raw = make_table('t_ja-JP', [(row['key'], row['jp'])])
    new_raw, counts, conflicts = lamanie_opisow.table_edits('t_ja-JP', raw, [row])
    assert counts['poprawione'] == 1 and not conflicts and new_raw != raw


def test_an_already_fixed_row_is_left_alone():
    row = {'bundle': 'x.bundle', 'table': 't_ja-JP', 'key': '00000001:00000002',
           'jp': '日本語', 'flat': 'Polski tekst.', 'pl': 'Polski\ntekst.'}
    raw = make_table('t_ja-JP', [(row['key'], row['pl'])])
    new_raw, counts, conflicts = lamanie_opisow.table_edits('t_ja-JP', raw, [row])
    assert new_raw is raw and counts['juz_poprawne'] == 1 and not conflicts


def test_foreign_text_is_reported_never_overwritten():
    row = {'bundle': 'x.bundle', 'table': 't_ja-JP', 'key': '00000001:00000002',
           'jp': '日本語', 'flat': 'Polski tekst.', 'pl': 'Polski\ntekst.'}
    raw = make_table('t_ja-JP', [(row['key'], 'coś zupełnie innego')])
    new_raw, counts, conflicts = lamanie_opisow.table_edits('t_ja-JP', raw, [row])
    assert new_raw is raw and not counts['poprawione']
    assert conflicts and conflicts[0]['problem'] == 'inny tekst w grze'


def test_a_missing_row_is_a_conflict_not_a_crash():
    row = {'bundle': 'x.bundle', 'table': 't_ja-JP', 'key': '00000009:00000009',
           'jp': '日本語', 'flat': 'Polski tekst.', 'pl': 'Polski\ntekst.'}
    raw = make_table('t_ja-JP', [('00000001:00000002', '日本語')])
    _, counts, conflicts = lamanie_opisow.table_edits('t_ja-JP', raw, [row])
    assert not counts['poprawione'] and conflicts[0]['problem'] == 'brak wiersza'


def test_the_kit_carries_tools_and_rows_but_no_game_files(tmp_path):
    result = build_lamanie_kit.build(tmp_path / 'SRW_Y_LAMANIE_OPISOW.zip')
    assert result['members'] == ['COFNIJ.bat', 'CZYTAJ_TO.md', 'POPRAW.bat',
                                 'narzedzia/cipher_fast.py', 'narzedzia/lamanie_opisow.py',
                                 'narzedzia/lamanie_rows.json', 'narzedzia/lz4_block_map.py',
                                 'narzedzia/requirements.txt', 'narzedzia/s6_scenario.py',
                                 'narzedzia/s6_tables.py', 'narzedzia/s6_write.py',
                                 'narzedzia/srw_y_bundle_crypt.py',
                                 'narzedzia/srw_y_rebuild.py']
    with zipfile.ZipFile(result['zip']) as archive:
        fix = archive.read('POPRAW.bat').decode('ascii')
        undo = archive.read('COFNIJ.bat').decode('ascii')
        readme = archive.read('CZYTAJ_TO.md').decode('utf8')
        rows = json.loads(archive.read('narzedzia/lamanie_rows.json').decode('utf8'))
    assert 'lamanie_opisow.py install' in fix and 'lamanie_opisow.py restore' not in fix
    assert 'lamanie_opisow.py restore' in undo
    assert 'COFNIECIE LAMANIA OPISOW' in undo
    assert '1042' in readme and '804' in readme
    assert 'Przywracam pliki z kopii' in undo
    assert 'dysk nie jest przeszukiwany' in fix
    assert rows['counts']['rows'] == 1042


def test_the_kit_is_byte_reproducible(tmp_path):
    first = build_lamanie_kit.build(tmp_path / 'a.zip')
    second = build_lamanie_kit.build(tmp_path / 'b.zip')
    assert first['sha256'] == second['sha256']


def test_the_owner_side_tool_imports_only_what_the_kit_ships():
    """The kit must be self-contained: every import resolves inside `narzedzia/`."""
    source = (ROOT / 'tools' / 'lamanie_opisow.py').read_text(encoding='utf8')
    for module in ('cipher_fast', 's6_tables', 's6_write', 'srw_y_bundle_crypt',
                   'srw_y_rebuild'):
        assert f'from {module} import' in source
        assert (ROOT / 'tools' / f'{module}.py').is_file()
    shipped = set(build_lamanie_kit.FILES)
    assert {'cipher_fast.py', 's6_tables.py', 's6_write.py', 'srw_y_bundle_crypt.py',
            'srw_y_rebuild.py', 'lamanie_opisow.py'} <= shipped
