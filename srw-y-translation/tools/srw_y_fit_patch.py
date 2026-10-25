"""Minimal-invasion text patch: the file keeps its exact length and header.

The first delivery rebuilt the bundle through UnityPy: the serialized file got a
new header and a shifted object table and the bundle grew by 9.5 KiB - and the
game refused to start. This module removes every one of those differences:

* the serialized file is the owner's own file, decompressed block by block, and
  **only the text fields inside one object are rewritten**, each padded with
  spaces to the byte length it had before. The serialized file therefore keeps
  its size, its header, its object table and every other object byte for byte;
* blocks are recompressed with the encoder setup the game itself used (LZ4 high
  compression, level 12 - it reproduces all 18 original blocks of
  `2d69c099…` bit for bit), so blocks that hold no text come back identical;
* the block that holds the text grows by ~750 B, which does not fit. Instead of
  growing the file, the two blocks around the text are merged into one 256 KiB
  block, which compresses *better* than the pair did (-2.6 KiB). The leftover is
  written as zero padding at the end of the file, so the bundle ends up with
  **exactly the original length** - what the catalog records still matches.

So the delivered file has the same size and a byte-identical head, and differs
only from the block that carries the narration.

    python3 tools/srw_y_fit_patch.py
    python3 tools/srw_y_fit_patch.py --locale en-US
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lz4.block  # noqa: E402
import UnityPy  # noqa: E402
from lz4_block_map import decompress_blocks, parse_container  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402
from srw_y_text_patch import BUNDLES, find_blocks  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
LOCAL = HERE / 'local'
TRANS = HERE / 'translations' / 'opening_pl.json'
BUILD = HERE / 'build' / 'v3'
LEVEL = 12
MERGE_AT = 4          # the merged pair starts at the block that holds the text
MERGE_COUNT = 2


def compress_block(chunk: bytes) -> bytes:
    return lz4.block.compress(chunk, mode='high_compression', compression=LEVEL,
                              store_size=False)


def pad(text: str, size: int) -> bytes:
    data = text.encode('utf-8')
    if len(data) > size:
        raise ValueError(f'{len(data)} B > {size} B: {text[:40]!r}')
    return data + b' ' * (size - len(data))


def object_raw(plain: bytes, object_name: str) -> bytes:
    env = UnityPy.load(plain)
    for obj in env.objects:
        if obj.type.name == 'MonoBehaviour' and obj.peek_name() == object_name:
            return obj.get_raw_data()
    raise SystemExit(f'{object_name} not found')


def tiling(lay):
    """(start, size) of every block: the original tiling with one merge."""
    out, pos = [], 0
    sizes = [b[0] for b in lay['blocks']]
    k = 0
    while k < len(sizes):
        if k == MERGE_AT:
            size = sum(sizes[k:k + MERGE_COUNT])
            out.append((pos, size))
            pos += size
            k += MERGE_COUNT
        else:
            out.append((pos, sizes[k]))
            pos += sizes[k]
            k += 1
    return out


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


def pack(lay, info_compressed: bytes, info_usize: int, chunks) -> bytes:
    out = bytearray()
    out += b'UnityFS\x00'
    out += struct.pack('>I', lay['version'])
    out += lay['player'].encode() + b'\x00'
    out += lay['engine'].encode() + b'\x00'
    out += struct.pack('>qIII', 0, len(info_compressed), info_usize, lay['flags'])
    out += b'\x00' * (64 - len(out))
    out += info_compressed
    out += b'\x00' * (((len(out) + 15) // 16 * 16) - len(out))
    for chunk in chunks:
        out += chunk
    struct.pack_into('>q', out, 30, len(out))
    return bytes(out)


def build_one(locale: str, texts, out_dir: Path) -> dict:
    stem, object_name = BUNDLES[locale]
    cipher = (LOCAL / 's4' / f'{stem}.bundle').read_bytes()
    plain = decrypt(stem, cipher)
    lay = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, lay))
    info_off = lay['info_offset']
    info_raw = lz4.block.decompress(plain[info_off:info_off + lay['csize']], lay['usize'])

    raw = object_raw(plain, object_name)
    base = blob.find(raw)
    if base < 0 or blob.find(raw, base + 1) >= 0:
        raise SystemExit(f'{stem}: object not uniquely locatable')
    blocks = find_blocks(raw)
    if len(blocks) != len(texts):
        raise SystemExit(f'{stem}: {len(blocks)} strings, {len(texts)} translations')

    new_raw = bytearray(raw)
    for (offset, size, _old), text in zip(reversed(blocks), reversed(texts)):
        new_raw[offset + 4:offset + 4 + size] = pad(text, size)
    new_blob = blob[:base] + bytes(new_raw) + blob[base + len(raw):]
    if len(new_blob) != len(blob):
        raise SystemExit(f'{stem}: serialized file length changed')

    chunks, meta = [], []
    for start, size in tiling(lay):
        piece = new_blob[start:start + size]
        comp = compress_block(piece)
        chunks.append(comp)
        meta.append((size, len(comp)))
    files = [(off, fsize, fflags, name) for off, fsize, fflags, name in lay['files']]
    info_plain = build_info(info_raw[:16], meta, files, lay['blocks'][0][2])
    info_out = compress_block(info_plain)
    out = pack(lay, info_out, len(info_plain), chunks)

    if len(out) > len(cipher):
        raise SystemExit(f'{stem}: rebuilt {len(out):,} B > original {len(cipher):,} B')
    padding = len(cipher) - len(out)
    out += b'\x00' * padding
    out = bytearray(out)
    struct.pack_into('>q', out, 30, len(out))
    out = bytes(out)

    new_cipher = encrypt(stem, out)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'{stem}.bundle'
    path.write_bytes(new_cipher)

    old_conf = [b[1] for b in lay['blocks']]
    return {
        'locale': locale, 'stem': stem, 'object': object_name, 'path': str(path),
        'original_size': len(cipher), 'size': len(new_cipher),
        'blocks': len(meta), 'padding': padding,
        'data_bytes': len(new_blob),
        'compressed': sum(c for _u, c in meta),
        'original_compressed': sum(old_conf),
        'prefix_same': 224 + sum(old_conf[:MERGE_AT]),
        'sha256': hashlib.sha256(new_cipher).hexdigest(),
    }


def build(trans_path: Path = TRANS, out_dir: Path = BUILD, only=None) -> list[dict]:
    trans = json.loads(Path(trans_path).read_text(encoding='utf-8'))
    texts = [b['pl'] for b in trans['blocks']]
    return [build_one(locale, texts, out_dir)
            for locale in BUNDLES if not only or locale == only]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trans', type=Path, default=TRANS)
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--locale', default=None)
    args = parser.parse_args(argv)
    for row in build(args.trans, args.out_dir, args.locale):
        print(f'{row["locale"]}: {row["path"]}')
        print(f'  rozmiar {row["original_size"]:,} B -> {row["size"]:,} B '
              f'(ten sam: {row["original_size"] == row["size"]})')
        print(f'  blokow {row["blocks"]}, dane {row["data_bytes"]:,} B, '
              f'skompresowane {row["compressed"]:,} vs {row["original_compressed"]:,}, '
              f'ogon {row["padding"]:,} B')
        print(f'  identyczny poczatek: {row["prefix_same"]:,} B')
        print(f'  sha256 {row["sha256"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
