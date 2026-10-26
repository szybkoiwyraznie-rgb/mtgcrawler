#!/usr/bin/env python3
"""Rebuild a bundle when the text gets longer — the write mode that was never proven.

The proven write mode so far is *same size*: pad the new text to the old byte length and
the file keeps its length (the Polish opening shipped that way). That caps a translation
at the length of the English it replaces, and English is already longer than Japanese in
19.8% of the table rows, so Polish cannot fit everywhere.

This module rebuilds instead:

1. decrypt the bundle, read the container, decompress every block into the serialized file;
2. let UnityPy re-emit that serialized file after the objects are given new raw bytes —
   it recomputes the object table, which is what actually has to change when an object's
   size changes;
3. pack a fresh container around it: blocks re-tiled at 128 KiB and compressed with the
   game's own encoder settings, block table and file entry rewritten, header size fixed;
4. encrypt and write, then **verify by reading the result back**: every object must be
   byte-identical to the original except the ones we meant to change.

The last point is the point: if the rebuild corrupts a neighbouring object, the check
fails and no file is written.

    python3 tools/srw_y_rebuild.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import lz4.block  # noqa: E402
import UnityPy  # noqa: E402

from lz4_block_map import decompress_blocks, parse_container  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402

BLOCK = 0x20000          # 128 KiB, the tiling the game itself uses
LEVEL = 12               # LZ4 high-compression level that reproduces the original blocks
FLAG_LZ4HC = 0x40        # compression type 3 (LZ4HC) with the high-compression bit


def compress_block(chunk: bytes) -> bytes:
    return lz4.block.compress(chunk, mode='high_compression', compression=LEVEL,
                              store_size=False)


def build_info(hash16: bytes, blocks, files, flags: int) -> bytes:
    out = bytearray(hash16)
    out += struct.pack('>i', len(blocks))
    for usize, csize in blocks:
        out += struct.pack('>IIH', usize, csize, flags)
    out += struct.pack('>i', len(files))
    for offset, size, fflags, name in files:
        out += struct.pack('>qqI', offset, size, fflags)
        out += name.encode() + b'\x00'
    return bytes(out)


def pack(lay, info_compressed: bytes, info_size: int, chunks) -> bytes:
    out = bytearray()
    out += b'UnityFS\x00'
    out += struct.pack('>I', lay['version'])
    out += lay['player'].encode() + b'\x00'
    out += lay['engine'].encode() + b'\x00'
    out += struct.pack('>qIII', 0, len(info_compressed), info_size, lay['flags'])
    out += b'\x00' * (64 - len(out))
    out += info_compressed
    out += b'\x00' * (((len(out) + 15) // 16 * 16) - len(out))
    for chunk in chunks:
        out += chunk
    struct.pack_into('>q', out, 30, len(out))     # total file size in the header
    return bytes(out)


def tile(blob: bytes) -> list[tuple[int, int]]:
    return [(start, min(BLOCK, len(blob) - start))
            for start in range(0, len(blob), BLOCK)]


def objects_of(blob: bytes) -> list[tuple[str, bytes]]:
    """(name, raw bytes) of every object, in file order, for the verification step."""
    with tempfile.NamedTemporaryFile(suffix='.assets', delete=False) as handle:
        handle.write(blob)
        path = handle.name
    env = UnityPy.load(path)
    found = []
    for obj in env.objects:
        name = obj.peek_name() or f'class_{obj.type.name}_{obj.path_id}'
        found.append((name, obj.get_raw_data()))
    return found


def rebuild_plain(stem: str, plain: bytes, edits: dict[str, bytes]) -> tuple[bytes, dict]:
    """Rebuild an already-decrypted bundle; return the new plaintext and a report.

    `edits` maps an object name to its complete new raw bytes; the length may differ.
    Every other object is verified to come back byte for byte, otherwise this raises.
    """
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    before = objects_of(blob)

    with tempfile.NamedTemporaryFile(suffix='.assets', delete=False) as handle:
        handle.write(blob)
        path = handle.name
    env = UnityPy.load(path)
    applied = []
    for obj in env.objects:
        name = obj.peek_name()
        if name in edits:
            obj.set_raw_data(edits[name])
            applied.append(name)
    missing = sorted(set(edits) - set(applied))
    if missing:
        raise ValueError(f'not found in {stem}: {missing}')
    new_blob = env.file.save()

    chunks, meta = [], []
    for start, size in tile(new_blob):
        piece = new_blob[start:start + size]
        compressed = compress_block(piece)
        chunks.append(compressed)
        meta.append((size, len(compressed)))
    header_hash = plain[layout['info_offset']:layout['info_offset'] + 16]
    # one file entry per bundle: same offset/name, new size (the container is monolithic)
    first = layout['files'][0]
    files = [(first[0], len(new_blob), first[2], first[3])]
    info_plain = build_info(header_hash, meta, files,
                            layout['blocks'][0][2] if layout['blocks'] else FLAG_LZ4HC)
    info_compressed = compress_block(info_plain)
    packed = pack(layout, info_compressed, len(info_plain), chunks)

    # verify: decompress what we just packed, compare every object
    check_layout = parse_container(packed)
    check_blob = b''.join(part[2] for part in decompress_blocks(packed, check_layout))
    if len(check_blob) != len(new_blob):
        raise ValueError(f'{stem}: rebuilt data is {len(check_blob)} B, expected {len(new_blob)}')
    after = objects_of(check_blob)
    if len(after) != len(before):
        raise ValueError(f'{stem}: {len(before)} objects became {len(after)}')
    changed = []
    for (name_before, raw_before), (name_after, raw_after) in zip(before, after):
        if name_before != name_after:
            raise ValueError(f'{stem}: object order changed at {name_before}')
        if raw_before == raw_after:
            continue
        if name_before not in edits:
            raise ValueError(f'{stem}: {name_before} changed without being edited')
        changed.append(name_before)
    report = {
        'stem': stem,
        'original_size': len(plain),
        'size': len(packed),
        'data_before': len(blob),
        'data_after': len(new_blob),
        'blocks_before': len(layout['blocks']),
        'blocks_after': len(meta),
        'edited': sorted(applied),
        'changed_objects': sorted(changed),
        'sha256': hashlib.sha256(packed).hexdigest(),
    }
    return packed, report


def rebuild(stem: str, original: bytes, edits: dict[str, bytes]) -> tuple[bytes, dict]:
    """Rebuild an encrypted bundle; return the re-encrypted bundle plus a report.

    `edits` maps an object name to its complete new raw bytes; the length may differ.
    """
    plain = decrypt(f'{stem}.bundle', original)
    new_plain, report = rebuild_plain(stem, plain, edits)
    cipher = encrypt(f'{stem}.bundle', new_plain)
    if decrypt(f'{stem}.bundle', cipher) != new_plain:
        raise ValueError(f'{stem}: cipher roundtrip does not reproduce the bundle')
    report['original_size'] = len(original)
    report['size'] = len(cipher)
    report['sha256'] = hashlib.sha256(cipher).hexdigest()
    return cipher, report


def selftest() -> int:
    """Grow one table string and check the result reads back — and that nothing else moved."""
    from s6_tables import table_header, walk_records
    from s6_write import encode_table

    stem = '2d69c099bfdf0e252dabe84dbbba11df'
    path = HERE / 'local' / 's4' / f'{stem}.bundle'
    if not path.is_file():
        print('brak pliku testowego — najpierw rozpakuj dane gry do local/s4')
        return 2
    original = path.read_bytes()
    plain = decrypt(f'{stem}.bundle', original)
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    target = 'system_text_en-US'
    env = UnityPy.load(tempfile.NamedTemporaryFile(suffix='.assets', delete=False).name)
    del env
    raw = None
    for name, data in objects_of(blob):
        if name == target:
            raw = data
    if raw is None:
        print(f'{target} nie znaleziony')
        return 2
    start, count = table_header(raw, target)
    rows, _ = walk_records(raw, start, count)
    key = rows[0]['key']
    marker = ' — test przebudowy, tekst celowo dłuższy niż angielski'
    new_raw = encode_table(raw, {key: rows[0]['text'] + marker})
    cipher, report = rebuild(stem, original, {target: new_raw})

    plain2 = decrypt(f'{stem}.bundle', cipher)
    layout2 = parse_container(plain2)
    blob2 = b''.join(part[2] for part in decompress_blocks(plain2, layout2))
    for name, data in objects_of(blob2):
        if name == target:
            s, c = table_header(data, target)
            r, _ = walk_records(data, s, c)
            ok = r[0]['text'].endswith(marker)
            print(f'{target}: pierwszy wpis {"OK" if ok else "NIE"} — {r[0]["text"]!r}')
            if not ok:
                return 1
    print(f'rozmiar {report["original_size"]:,} B -> {report["size"]:,} B '
          f'(dane {report["data_before"]:,} -> {report["data_after"]:,} B)')
    print(f'bloków {report["blocks_before"]} -> {report["blocks_after"]}, '
          f'zmienione obiekty: {report["changed_objects"]}')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    parser.print_help()
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
