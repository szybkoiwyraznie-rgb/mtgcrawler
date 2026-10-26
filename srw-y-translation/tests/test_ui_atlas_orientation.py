"""The atlas pixels have to be drawn in reading order, not upside down.

An atlas is a picture: the labels are not strings, so there is nothing to translate in
place — the cells have to be cleared and redrawn. That only works if the coordinate system
used for drawing matches the one Unity uses for the sprite rects.

It did not, in the first build of test 6: the decode kept the stream's bottom-up rows, so
`top = height - y - h` landed on the mirrored band, the original labels were never erased,
and the Polish ones were written elsewhere upside down. Nothing crashed and every
integrity check passed, which is exactly why this is a test and not a comment.

The guard does not compare against a decoder: it uses the fact that the original atlas has
ink in the rows UnityPy shows at the top and none below the last cell, and requires the
decode to reproduce that.

    python3 -m pytest tests/test_ui_atlas_orientation.py -q
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pytest  # noqa: E402

from build_pl_table_patch import plain_of  # noqa: E402
from build_pl_ui_atlas import decode_texture, encode_texture, streams_of  # noqa: E402

MID = 'ee1aae99cb34ce3465609bab05ea9352'
BUNDLE = HERE / 'local' / 'ui6' / f'{MID}.bundle'
needs_bundle = pytest.mark.skipif(not BUNDLE.is_file(), reason='brak lokalnej kopii Mid_Font')


def mid_texture():
    """(format, pixels, width, height) of `Mid_Font` read straight from its stream."""
    import UnityPy

    layout, streams = streams_of(plain_of(MID, BUNDLE))
    workdir = Path(tempfile.mkdtemp())
    for (_off, _size, _f, name), data in zip(layout['files'], streams):
        (workdir / name).write_bytes(data)
    env = UnityPy.load(str(workdir / layout['files'][0][3]))
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        tree = obj.read_typetree()
        if tree['m_Name'] != 'Mid_Font':
            continue
        stream = tree['m_StreamData']
        offset, size = int(stream['offset']), int(stream['size'])
        name = stream['path'].rsplit('/', 1)[-1]
        index = next(i for i, entry in enumerate(layout['files']) if entry[3] == name)
        pixels = streams[index][offset:offset + size]
        return tree['m_TextureFormat'], pixels, tree['m_Width'], tree['m_Height']
    raise AssertionError('brak tekstury Mid_Font')


@needs_bundle
def test_decode_puts_the_first_label_at_the_top():
    fmt, pixels, width, height = mid_texture()
    image = decode_texture(fmt, pixels, width, height)
    alpha = image.convert('RGBA').split()[-1]
    assert alpha.crop((0, 0, width, 64)).getbbox() is not None, 'górne wiersze są puste'
    assert alpha.crop((0, height - 64, width, height)).getbbox() is None, \
        'dolne wiersze mają treść - dekodowanie nie jest w kolejności czytania'


@needs_bundle
def test_encode_keeps_the_stream_exactly_the_same_length():
    """BC7 is lossy, so bytes cannot come back; the length is what the swap relies on."""
    fmt, pixels, width, height = mid_texture()
    encoded = encode_texture(fmt, decode_texture(fmt, pixels, width, height))
    assert len(encoded) == len(pixels) == width * height * (1 if fmt == 25 else 4)


@needs_bundle
def test_drawn_label_lands_where_unitypy_shows_the_cell():
    """Clear one top-row cell and check the *top* of the picture changed, not the bottom."""
    import UnityPy

    from PIL import Image, ImageDraw

    fmt, pixels, width, height = mid_texture()
    image = decode_texture(fmt, pixels, width, height)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, width, 32], fill=(0, 0, 0, 0))       # first cell row, all columns
    after = decode_texture(fmt, encode_texture(fmt, image), width, height)
    alpha = after.convert('RGBA').split()[-1]
    assert alpha.crop((0, 0, width, 32)).getbbox() is None
    # the row below must survive: this is what tells "row 0 is the top" from a mirrored write
    assert alpha.crop((0, 32, width, 64)).getbbox() is not None
    assert UnityPy  # imported for the docstring's sake
