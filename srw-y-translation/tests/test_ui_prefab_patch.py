"""Polish written into UI prefabs — the text that is not in any table.

The title screen keeps `Press Any Key` as a TextMeshPro field inside a `MonoBehaviour`,
so it is patched by re-serialising that object rather than by rewriting a table. Two
things have to be true before that is safe, and both are checked here on the real
bundle when it is present locally:

1. the writer reproduces an *unchanged* typetree byte for byte — otherwise the object is
   not edited, it is overwritten with a slightly different one;
2. the rebuilt container keeps every other object and the `.resS` stream that follows the
   serialized file inside the same bundle. Dropping that stream is silent corruption: the
   objects still verify, the textures are gone.

    python3 -m pytest tests/test_ui_prefab_patch.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pytest  # noqa: E402

from build_pl_table_patch import plain_of  # noqa: E402
from build_pl_ui_patch import build, load_objects, text_of  # noqa: E402
from lz4_block_map import decompress_blocks, parse_container  # noqa: E402
from srw_y_bundle_crypt import decrypt  # noqa: E402
from srw_y_rebuild import objects_of  # noqa: E402

TITLE = 'ec293019eef6338eba241eaf3314c9f3'
BUNDLE = HERE / 'local' / 'ui' / f'{TITLE}.bundle'
needs_title = pytest.mark.skipif(not BUNDLE.is_file(),
                                 reason='brak lokalnej kopii bundle z ekranem tytułowym')


def files_of(plain: bytes):
    """[(name, bytes)] of every stream in the container, in order."""
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    return layout, [(name, blob[off:off + size]) for off, size, _f, name in layout['files']]


@needs_title
def test_writer_reproduces_an_unchanged_object_byte_for_byte():
    """`get_raw_data()` never changes; the proof has to compare `obj.data`."""
    env, temp_path, _blob = load_objects(plain_of(TITLE, BUNDLE))
    try:
        checked = 0
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            raw = obj.get_raw_data()
            obj.save_typetree(obj.read_typetree())
            assert obj.data == raw, f'{obj.path_id} nie zapisuje się wiernie'
            checked += 1
        assert checked
    finally:
        temp_path.unlink(missing_ok=True)


@needs_title
def test_patch_changes_only_the_wanted_strings_and_keeps_the_streams(tmp_path):
    original = plain_of(TITLE, BUNDLE)
    layout_before, files_before = files_of(original)
    assert len(files_before) == 2, 'ten bundle ma plik serializowany i strumień .resS'

    rows = build(out_dir=tmp_path)
    title = next(row for row in rows if row['stem'] == TITLE)
    assert [item['pl'] for item in title['strings']] == ['Naciśnij klawisz\n'] * 2

    rebuilt = decrypt(f'{TITLE}.bundle', Path(title['path']).read_bytes())
    layout_after, files_after = files_of(rebuilt)
    assert len(files_after) == len(files_before)
    assert [name for name, _ in files_after] == [name for name, _ in files_before]
    # the stream that follows the serialized file must come back untouched
    for (_name, before), (_name2, after) in zip(files_before[1:], files_after[1:]):
        assert before == after

    before = objects_of(b''.join(
        part[2] for part in decompress_blocks(original, layout_before)))
    after = objects_of(b''.join(
        part[2] for part in decompress_blocks(rebuilt, layout_after)))
    assert len(before) == len(after)
    changed = [right for left, right in zip(before, after) if left[2] != right[2]]
    assert len(changed) == 2
    assert all(b'Press Any Key' not in raw for _id, _name, raw in changed)

    env, temp_path, _blob = load_objects(rebuilt)
    try:
        texts = [text_of(obj.read_typetree()) for obj in env.objects
                 if obj.type.name == 'MonoBehaviour']
        assert texts.count('Naciśnij klawisz\n') == 2
    finally:
        temp_path.unlink(missing_ok=True)


def test_translation_file_covers_every_wanted_string():
    """Each entry must say what it replaces — a patch matched by position is a bug."""
    import json
    data = json.loads((HERE / 'translations' / 'ui_test_pl.json').read_text(encoding='utf-8'))
    for stem, spec in data['bundles'].items():
        assert len(stem) == 32 and all(c in '0123456789abcdef' for c in stem)
        for row in spec['strings']:
            assert row['old'] and row['pl']
            assert row['old'] != row['pl']
            # the replacement is a UI label; a line break belongs to the original only
            assert row['pl'].endswith('\n') == row['old'].endswith('\n')
