#!/usr/bin/env python3
"""Turn one texture into solid black inside the owner's own bundle.

The Database screen draws its mecha and pilots over a picture of the A. Advent
interior (`BG_DataBase_01`, 1920x1080). That picture lives in the bundle's `.resS`
stream, outside the serialized file, so it cannot be replaced through the object
table: the pixels are cut out of the stream at the texture's own offset and put
back in the same format, at the same size, byte for byte. The bundle is then
rebuilt with `srw_y_rebuild`, every other object is verified untouched, and the
black blocks are decoded back to prove they are black before anything is written.

Nothing here knows the game path: `tools/tlo_bazy.py` is the owner-side wrapper
that finds the bundle, writes the file and keeps the `.bak`.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

BC7, BC1, BC3, BC4, BC5 = 25, 10, 12, 26, 27
RGBA32, RGB24, ARGB32, BGRA32 = 4, 3, 5, 14

#: Format -> (etcpak encoder, bytes per 4x4 pixel block). All one or two bytes a pixel.
COMPRESSED = {BC7: ('compress_bc7', 16), BC1: ('compress_bc1', 8),
              BC3: ('compress_bc3', 16), BC4: ('compress_bc4', 8), BC5: ('compress_bc5', 16)}
#: Format -> (bytes per pixel, one black pixel as the game stores it).
RAW = {RGBA32: (4, b'\x00\x00\x00\xff'), RGB24: (3, b'\x00\x00\x00'),
       ARGB32: (4, b'\xff\x00\x00\x00'), BGRA32: (4, b'\x00\x00\x00\xff')}
#: Formats whose decoder returns BGRA, so "black and opaque" can be checked.
VERIFIABLE = {BC7: 'decode_bc7', BC1: 'decode_bc1', BC3: 'decode_bc3'}
#: BC7 stores alpha in seven bits, so a 255 encodes and decodes back as 254; that is
#: still opaque for every practical purpose, and the check must not call it a failure.
ALPHA_MIN = 250


def format_name(fmt: int) -> str:
    names = {BC7: 'BC7', BC1: 'DXT1/BC1', BC3: 'DXT5/BC3', BC4: 'BC4', BC5: 'BC5',
             RGBA32: 'RGBA32', RGB24: 'RGB24', ARGB32: 'ARGB32', BGRA32: 'BGRA32'}
    return names.get(fmt, f'format {fmt}')


def is_supported(fmt: int) -> bool:
    return fmt in COMPRESSED or fmt in RAW


def expected_size(fmt: int, width: int, height: int) -> int:
    if fmt in COMPRESSED:
        per_block = COMPRESSED[fmt][1]
        return ((width + 3) // 4) * ((height + 3) // 4) * per_block
    per_pixel, _pixel = RAW[fmt]
    return width * height * per_pixel


def black_bytes(fmt: int, width: int, height: int) -> bytes:
    """Solid-black pixels in the texture's own format, never larger than the slot."""
    if fmt in COMPRESSED:
        import etcpak

        encoder = getattr(etcpak, COMPRESSED[fmt][0])
        image = b'\x00\x00\x00\xff' * (width * height)
        data = encoder(image, width, height)
        if len(data) != expected_size(fmt, width, height):
            raise ValueError(f'{format_name(fmt)}: koder dał {len(data)} B, '
                             f'oczekiwano {expected_size(fmt, width, height)} B')
        return data
    if fmt in RAW:
        per_pixel, pixel = RAW[fmt]
        return pixel * (width * height)
    raise ValueError(f'{format_name(fmt)}: nieobsługiwany format — nie umiem zapisać '
                     f'czerni w tym formacie')


def verify_black(fmt: int, data: bytes, width: int, height: int) -> bool | None:
    """Decode the encoded blocks and check they are black and opaque.

    `None` means "not checked": the format has no decoder we trust (BC4/BC5 are
    single/double channel, so an alpha check would be meaningless).
    """
    if fmt in RAW:
        per_pixel, _pixel = RAW[fmt]
        if fmt in (RGBA32, ARGB32, BGRA32):
            alpha = data[3::4]
            return not any(data[i] for i in range(len(data)) if i % 4 != 3) \
                and all(byte >= ALPHA_MIN for byte in alpha)
        return not any(data)
    decoder_name = VERIFIABLE.get(fmt)
    if decoder_name is None:
        import etcpak  # noqa: F401  (keep the import error honest)

        return None
    from texture2ddecoder import decode_bc1, decode_bc3, decode_bc7

    decoder = {BC7: decode_bc7, BC1: decode_bc1, BC3: decode_bc3}[fmt]
    decoded = decoder(data, width, height)
    if any(decoded[i] for i in range(len(decoded)) if i % 4 != 3):
        return False
    return all(decoded[i] >= ALPHA_MIN for i in range(3, len(decoded), 4))


def streams_of(plain: bytes) -> tuple[dict, list[bytes]]:
    """Container layout plus every stream in it, in file-table order."""
    from lz4_block_map import decompress_blocks, parse_container

    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    return layout, [blob[off:off + size] for off, size, _f, _n in layout['files']]


def find_texture(env, name: str, size: tuple[int, int] | None = None):
    """(object, typetree) of the Texture2D called `name`; `size` rejects a namesake."""
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        tree = obj.read_typetree()
        if str(tree.get('m_Name')) != name:
            continue
        if size and (tree.get('m_Width'), tree.get('m_Height')) != size:
            continue
        return obj, tree
    return None, None


def patch_plain(stem: str, plain: bytes, texture: str,
                size: tuple[int, int] | None = None) -> tuple[bytes, dict]:
    """Replace one texture's pixels with black; return the new plaintext and a report.

    Raises if the texture is missing, its format is unsupported, the slot is not
    exactly what the format implies, the black blocks do not decode to black, or
    the rebuild changes any object or stream that was not meant to change.
    """
    import UnityPy

    from srw_y_rebuild import objects_of, rebuild_plain
    from lz4_block_map import decompress_blocks, parse_container

    layout, streams = streams_of(plain)
    workdir = Path(tempfile.mkdtemp())
    for (_off, _size, _f, name), data in zip(layout['files'], streams):
        (workdir / name).write_bytes(data)
    env = UnityPy.load(str(workdir / layout['files'][0][3]))
    obj, tree = find_texture(env, texture, size)
    if obj is None:
        raise ValueError(f'{stem}: nie ma tekstury {texture}'
                         + (f' {size[0]}x{size[1]}' if size else ''))

    fmt = int(tree['m_TextureFormat'])
    width, height = int(tree['m_Width']), int(tree['m_Height'])
    if not is_supported(fmt):
        raise ValueError(f'{stem}: {texture} ma {format_name(fmt)}, '
                         f'czerni w tym formacie nie zapiszę')
    channel = tree.get('m_StreamData') or {}
    offset, slot = int(channel.get('offset') or 0), int(channel.get('size') or 0)
    stream_name = str(channel.get('path') or '').rsplit('/', 1)[-1]
    index = next((i for i, entry in enumerate(layout['files']) if entry[3] == stream_name), None)
    if index is None:
        raise ValueError(f'{stem}: nie ma strumienia {stream_name or "(brak)"}')
    want = expected_size(fmt, width, height)
    if slot != want:
        raise ValueError(f'{stem}: {texture} {format_name(fmt)} zajmuje {slot} B, '
                         f'a format każe {want} B — nie ruszam')

    black = black_bytes(fmt, width, height)
    verified = verify_black(fmt, black, width, height)
    if verified is False:
        raise ValueError(f'{stem}: zakodowana czerń nie dekoduje się na czerń')

    data = bytearray(streams[index])
    before = bytes(data[offset:offset + slot])
    data[offset:offset + slot] = black
    new_plain, report = rebuild_plain(stem, plain, {}, {index: bytes(data)})

    check_layout, check_streams = streams_of(new_plain)
    if check_streams[index] != bytes(data):
        raise ValueError(f'{stem}: strumień {stream_name} nie wrócił z przebudowy')
    after = check_streams[index][offset:offset + slot]
    if after == before:
        raise ValueError(f'{stem}: piksele {texture} się nie zmieniły')
    if verify_black(fmt, after, width, height) is False:
        raise ValueError(f'{stem}: po przebudowie piksele {texture} nie są czarne')
    if objects_of(b''.join(part[2] for part in decompress_blocks(new_plain, check_layout))) != \
            objects_of(b''.join(part[2] for part in decompress_blocks(plain, parse_container(plain)))):
        raise ValueError(f'{stem}: obiekty zmieniły się przy podmianie tekstury')

    return new_plain, {'stem': stem, 'texture': texture, 'width': width, 'height': height,
                       'format': format_name(fmt), 'slot': slot, 'stream': stream_name,
                       'black_verified': verified, 'changed_objects': report['changed_objects'],
                       'original_size': len(plain), 'size': len(new_plain),
                       'bytes_changed': sum(1 for a, b in zip(before, after) if a != b)}
