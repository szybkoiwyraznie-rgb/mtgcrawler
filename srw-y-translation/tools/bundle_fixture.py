#!/usr/bin/env python3
"""Syntetyczny bundle z teksturami — do testów, które muszą widzieć prawdziwy zapis.

Po co to jest (2026-11-13). Mod 4K trzyma piksele **w obiekcie** tekstury
(`Texture2D.image_data`), a gra 1.4.0 w osobnym strumieniu `.resS`. Paczka v5
musi obsłużyć oba tryby, a żaden test nie może zależeć od plików gry
(`tests/conftest.py` zabrania skipów i prywatnych katalogów). Ten moduł buduje
więc w pamięci komplet: SerializedFile z typetree z TPK, tekstury w obu trybach,
kontener UnityFS z blokami LZ4 — na którym `tlo_bazy6.blacken()` może przejść
całą drogę zapisu i odczytu, bez ani jednego bajtu z gry.

    python tools/bundle_fixture.py --selftest

Moduł nie jest częścią paczki dla właściciela: importuje UnityPy, ale woła go
tylko wtedy, gdy test tego potrzebuje.
"""
from __future__ import annotations

import sys

UNITY_VERSION = '2022.3.44f1'
#: Ten sam zestaw flag, co w bundlach gry: informacja na początku, bloki LZ4HC.
CONTAINER_FLAGS = 0x243
#: Tabela plików: format, którym gra oznacza „w tym pliku są dane gry”.
FILE_FLAGS = 4


def _class_ids():
    return {'texture': 28, 'text': 49}


def build_serialized_file(textures=(), texts=(), stream_textures=(),
                          stream_name: str = 'CAB-fixture.resS',
                          version: str = UNITY_VERSION) -> bytes:
    """SerializedFile (wersja 22) z podanymi teksturami i tekstami.

    `textures` to `[(nazwa, piksele, format, szerokość, wysokość, mipmapy)]`,
    `texts` — `[(nazwa, treść)]`. Piksele trafiają **do obiektu** (`image data`),
    czyli w tryb, w którym po modzie 4K trzyma je gra.

    `stream_textures` to `[(nazwa, format, szerokość, wysokość, mipmapy, offset,
    rozmiar)]` — tekstury, których piksele leżą **poza** plikiem, w strumieniu
    `.resS` (tak trzyma je gra 1.4.0). Obiekt dostaje tylko `m_StreamData`.
    """
    from UnityPy.enums import BuildTarget, ClassIDType
    from UnityPy.files.ObjectReader import ObjectReader
    from UnityPy.files.SerializedFile import SerializedFile, SerializedType
    from UnityPy.helpers.Tpk import get_typetree_node
    from UnityPy.helpers.TypeTreeHelper import write_typetree
    from UnityPy.helpers.UnityVersion import UnityVersion
    from UnityPy.streams import EndianBinaryReader, EndianBinaryWriter

    class_ids = _class_ids()
    unity_version = UnityVersion.from_str(version)

    def node_for(class_id: int):
        node = get_typetree_node(class_id, unity_version)
        # TPK nie niesie dwóch pól, których wymaga zapis typetree do pliku.
        for item in node.traverse():
            if item.m_TypeFlags is None:
                item.m_TypeFlags = 0
            if getattr(item, 'm_RefTypeHash', None) is None:
                item.m_RefTypeHash = 0
        return node

    # 1. nagłówek i metadane pustego pliku — dokładnie tyle, ile UnityPy czyta
    head = EndianBinaryWriter(endian='<')
    head.write_u_int(0)
    head.write_u_int(0)
    head.write_u_int(22)
    head.write_u_int(0)
    head.write_boolean(False)
    head.write(b'\x00' * 3)
    head.write_u_int(0)
    head.write_long(0)
    head.write_long(0)
    head.write_long(0)
    head.write_string_to_null(version)
    head.write_int(BuildTarget.StandaloneWindows64.value)
    head.write_boolean(True)
    for _ in range(5):                      # typy, obiekty, skrypty, externals, ref types
        head.write_int(0)
    head.write_string_to_null('')
    assets = SerializedFile(EndianBinaryReader(head.bytes, endian='<'))

    # 2. jeden wpis typu na klasę, którą faktycznie wkładamy
    def add_type(class_id: int):
        entry = SerializedType.__new__(SerializedType)
        entry.class_id = class_id
        entry.is_stripped_type = False
        entry.script_type_index = -1
        entry.script_id = None
        entry.old_type_hash = b'\x00' * 16
        entry.node = node_for(class_id)
        entry.type_dependencies = ()
        entry.type_tree_content_hash = None
        entry.type_tree_serialized_size = None
        assets.types.append(entry)
        return entry, len(assets.types) - 1

    def add_object(entry, type_id: int, class_id: int, path_id: int, tree: dict):
        writer = EndianBinaryWriter(endian='<')
        write_typetree(tree, entry.node, writer, assets)
        obj = ObjectReader(assets_file=assets, reader=assets.reader, path_id=path_id,
                           type_id=type_id, serialized_type=entry, class_id=class_id,
                           type=ClassIDType(class_id), byte_start=0,
                           byte_size=len(writer.bytes), is_destroyed=None,
                           is_stripped=None)
        obj.data = writer.bytes
        assets.objects[path_id] = obj
        return obj

    texture_type = texture_id = None
    if textures:
        texture_type, texture_id = add_type(class_ids['texture'])
    text_type = text_id = None
    if texts:
        text_type, text_id = add_type(class_ids['text'])

    path_id = 1
    for name, pixels, fmt, width, height, mips in textures:
        add_object(texture_type, texture_id, class_ids['texture'], path_id,
                   texture_tree(name, pixels, fmt, width, height, mips))
        path_id += 2
    for name, fmt, width, height, mips, offset, size in stream_textures:
        add_object(texture_type, texture_id, class_ids['texture'], path_id,
                   texture_tree(name, b'', fmt, width, height, mips,
                                stream=(stream_name, offset, size)))
        path_id += 2
    for name, script in texts:
        add_object(text_type, text_id, class_ids['text'], path_id,
                   {'m_Name': name, 'm_Script': script, 'm_PathID': 0})
        path_id += 2
    assets.mark_changed()
    return assets.save()


def texture_tree(name: str, pixels: bytes, fmt: int = 10, width: int = 4,
                 height: int = 4, mips: int = 1,
                 stream: tuple[str, int, int] | None = None) -> dict:
    """Typetree tekstury z pikselami **w środku** (`image data`), jak po modzie 4K.

    `stream=(nazwa, offset, rozmiar)` przestawia ją na tryb strumienia: piksele
    są wtedy poza plikiem, a obiekt niesie tylko `m_StreamData`.
    """
    path, offset, size = stream if stream else ('', 0, 0)
    return {
        'm_Name': name, 'm_ForcedFallbackFormat': 0, 'm_DownscaleFallback': False,
        'm_IsAlphaChannelOptional': False, 'm_Width': width, 'm_Height': height,
        'm_CompleteImageSize': len(pixels), 'm_MipsStripped': 0,
        'm_TextureFormat': fmt, 'm_MipCount': mips, 'm_IsReadable': False,
        'm_IsPreProcessed': False, 'm_IgnoreMipmapLimit': False,
        'm_MipmapLimitGroupName': '', 'm_StreamingMipmaps': False,
        'm_StreamingMipmapsPriority': 0, 'm_ImageCount': 1, 'm_TextureDimension': 2,
        'm_TextureSettings': {'m_FilterMode': 1, 'm_Aniso': 1, 'm_MipBias': 0.0,
                              'm_WrapU': 0, 'm_WrapV': 0, 'm_WrapW': 0},
        'm_LightmapFormat': 0, 'm_ColorSpace': 0, 'm_PlatformBlob': [],
        'image data': pixels,
        'm_StreamData': {'offset': offset, 'size': size, 'path': path},
    }


def container(assets: bytes, side_stream: bytes = b'') -> bytes:
    """UnityFS wokół strumienia serializowanego, z blokami LZ4 dokładnie jak w grze.

    `side_stream` to zawartość `.resS` — tryb, w którym tekstury trzyma gra 1.4.0.
    """
    from srw_y_rebuild import build_info, compress_block, pack, tile

    files = [(0, len(assets), FILE_FLAGS, 'CAB-fixture')]
    blob = assets
    if side_stream:
        files.append((len(assets), len(side_stream), FILE_FLAGS, 'CAB-fixture.resS'))
        blob += side_stream
    chunks, meta = [], []
    for start, size in tile(blob):
        piece = blob[start:start + size]
        compressed = compress_block(piece)
        chunks.append(compressed)
        meta.append((size, len(compressed)))
    info = build_info(b'\x11' * 16, meta, files, 3)   # 3 = LZ4HC, tak jak w grze
    layout = {'version': 8, 'player': '5.x.x', 'engine': UNITY_VERSION,
              'flags': CONTAINER_FLAGS}
    return pack(layout, compress_block(info), len(info), chunks)


def bundle_with_textures(specs, texts=(), stream_specs=(), stream_pixels=b'') -> bytes:
    """Najprostsza droga: bundle z teksturami inline i/lub w strumieniu `.resS`."""
    assets = build_serialized_file(textures=specs, texts=texts,
                                   stream_textures=stream_specs)
    return container(assets, side_stream=stream_pixels)


def selftest() -> int:
    import hashlib

    import UnityPy

    from lz4_block_map import decompress_blocks, parse_container

    pixels = bytes(range(8))
    bundle = bundle_with_textures([('BG_DataBase_01', pixels, 10, 4, 4, 1)])
    layout = parse_container(bundle)
    blob = b''.join(part[2] for part in decompress_blocks(bundle, layout))
    env = UnityPy.load(blob)
    found = {}
    for obj in env.objects:
        if obj.type.name == 'Texture2D':
            tree = obj.read_typetree()
            found[str(tree['m_Name'])] = bytes(tree['image data'])
    assert found == {'BG_DataBase_01': pixels}, found
    print(f'OK {len(bundle):,} B, sha256 {hashlib.sha256(bundle).hexdigest()[:16]}')
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]:
        raise SystemExit(selftest())
    print(__doc__)
