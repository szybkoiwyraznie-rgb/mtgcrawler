import hashlib
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from apply_y_plan import jobs_for, safe_relative, scene_edit, build_bundle


def textasset(name, data):
    raw = struct.pack('<I', len(name)) + name.encode()
    raw += bytes(-len(raw) % 4)
    raw += struct.pack('<I', len(data)) + data
    return raw + bytes(-len(raw) % 4)


def test_scene_rejects_changed_source_and_keeps_other_lines():
    script = ('[[Pilot\nHello]], -- <srw-tag=string-id>(1.0)\n'
              '[[Pilot\nBye]], -- <srw-tag=string-id>(2.0)')
    raw = textasset('a.lua', script.encode())
    rows = {'1.0#1': {'jp': 'jp', 'en': 'Hello', 'pl': 'Cześć'}}
    changed, count = scene_edit('a.lua', raw, script, rows, 'en')
    assert count == 1 and 'Cześć'.encode() in changed and b'Bye' in changed
    rows['1.0#1']['en'] = 'other'
    with pytest.raises(ValueError, match='inny tekst'):
        scene_edit('a.lua', raw, script, rows, 'en')


def test_paths_refuse_traversal_and_unsupported_locations():
    assert safe_relative('aa/StandaloneWindows64/abc.bundle')
    assert safe_relative('Dlc1/abc.bundle')
    for path in ('../x.bundle', '/x.bundle', 'aa/../x.bundle', 'Dlc1\\x.bundle',
                 'C:/x.bundle', 'x.bundle', 'a/b/c.bundle'):
        with pytest.raises(ValueError):
            safe_relative(path)


def test_index_requires_both_locales_and_exact_source_hash():
    row = {'jp': 'jp', 'en': 'en', 'pl': 'pl'}
    plan = {'schema': 1, 'tables': {}, 'scenes': {'a.lua': {'1#1': row}}}
    entry = {'sha256': hashlib.sha256(b'original').hexdigest(), 'tables': [],
             'scenes': [{'name': 'a.lua', 'lang': 'ja', 'path_id': 1}]}
    idx = {'schema': 1, 'bundles': {'aa/StandaloneWindows64/x.bundle': entry}}
    with pytest.raises(ValueError, match='brak obiektu en'):
        jobs_for(plan, idx)
    entry['scenes'].append({'name': 'a.lua', 'lang': 'en', 'path_id': 2})
    jobs = jobs_for(plan, idx)
    with pytest.raises(ValueError, match='niezgodna wersja'):
        build_bundle('aa/StandaloneWindows64/x.bundle', b'wrong', next(iter(jobs.values())), plan)


def test_table_edit_empty_jp_with_english_reference_updates_both_languages():
    from test_s6_extract import table_object
    from apply_y_plan import table_edit
    from s6_tables import table_header, walk_records
    key = '00000000:00001000'
    rows = {key: {'jp': '', 'en': 'Example', 'pl': 'Przykład'}}
    for locale, lang, initial in [('ja-JP', 'ja', ''), ('en-US', 'en', 'Example')]:
        name = 'skill_active_' + locale
        raw = table_object(name, locale, [initial, 'untouched'])
        new, n = table_edit(name, raw, rows, lang)
        start, count = table_header(new, name)
        records, _ = walk_records(new, start, count)
        assert n == 1 and [r['text'] for r in records] == ['Przykład', 'untouched']
    rows[key]['jp'] = 'different'
    with pytest.raises(ValueError, match='inny tekst'):
        table_edit('skill_active_ja-JP', table_object('skill_active_ja-JP', 'ja-JP', ['', 'untouched']), rows, 'ja')
