"""Minimal-invasive text patch: same file length, same block layout, only text differs.

The first delivery (`srw_y_text_patch.py build`) rebuilt the whole bundle through
UnityPy: that rewrote the serialized file's header and object table and changed
the bundle length - and the game refused to start. This module removes all of
those differences:

* the serialized file is the original, decompressed block by block, and **only
  the text fields inside one object are rewritten** - to the same byte length,
  because every string is padded with spaces to the length it had before;
* every block is recompressed with the encoder settings the game itself used
  (LZ4 high compression, level 12, 128 KiB chunks - verified to reproduce all 18
  blocks of `2d69c099…` bit for bit), so untouched blocks come back
  byte-identical and stay at their original offsets;
* if the block holding the text compresses to a different size, the difference
  is absorbed at the end of the file, so the bundle keeps **exactly** the
  original length and the catalog's size record still matches.

So the delivered file differs from the owner's file only inside the one block
that carries the narration.

    python3 tools/srw_y_exact_patch.py
    python3 tools/srw_y_exact_patch.py --locale en-US
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
BUILD = HERE / 'build'
LEVEL = 12


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


def patched_info(info_raw: bytes, old_sizes, new_sizes) -> bytes:
    """Copy the blocks-info table with the new compressed sizes filled in."""
    out = bytearray(info_raw)
    for k, size in enumerate(new_sizes):
        if size != old_sizes[k]:
            struct.pack_into('>I', out, 16 + 4 + 10 * k + 4, size)
    return bytes(out)


def pack(lay, info_compressed: bytes, compressed_blocks) -> bytes:
    """Assemble a UnityFS container with the original header fields and layout."""
    out = bytearray()
    out += b'UnityFS\x00'
    out += struct.pack('>I', lay['version'])
    out += lay['player'].encode() + b'\x00'
    out += lay['engine'].encode() + b'\x00'
    out += struct.pack('>qIII', 0, len(info_compressed), lay['usize'], lay['flags'])
    out += b'\x00' * (64 - len(out))
    out += info_compressed
    out += b'\x00' * (((len(out) + 15) // 16 * 16) - len(out))
    for chunk in compressed_blocks:
        out += chunk
    struct.pack_into('>q', out, 30, len(out))
    return bytes(out)


def build_one(locale: str, texts, out_dir: Path) -> dict:
    stem, object_name = BUNDLES[locale]
    cipher = (LOCAL / 's4' / f'{stem}.bundle').read_bytes()
    plain = decrypt(stem, cipher)
    lay = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, lay))
    if len(blob) != sum(b[0] for b in lay['blocks']):
        raise SystemExit(f'{stem}: decompressed size mismatch')
    info_off = lay['info_offset']
    info_compressed = plain[info_off:info_off + lay['csize']]
    info_raw = lz4.block.decompress(info_compressed, lay['usize'])

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
    new_raw = bytes(new_raw)
    new_blob = blob[:base] + new_raw + blob[base + len(raw):]
    if len(new_blob) != len(blob):
        raise SystemExit(f'{stem}: serialized file length changed')

    chunks, pos = [], 0
    for size, _c, _f in lay['blocks']:
        chunks.append(new_blob[pos:pos + size])
        pos += size
    compressed = [compress_block(chunk) for chunk in chunks]
    sizes = [len(c) for c in compressed]
    old_sizes = [b[1] for b in lay['blocks']]
    changed = [k for k in range(len(sizes)) if sizes[k] != old_sizes[k]]

    if changed:
        info_out = compress_block(patched_info(info_raw, old_sizes, sizes))
    else:
        info_out = info_compressed
    out = pack(lay, info_out, compressed)
    if len(out) > len(cipher):
        raise SystemExit(f'{stem}: rebuilt bundle is {len(out):,} B, '
                         f'original {len(cipher):,} B - it does not fit')
    out += b'\x00' * (len(cipher) - len(out))

    new_cipher = encrypt(stem, out)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'{stem}.bundle'
    path.write_bytes(new_cipher)
    return {
        'locale': locale, 'stem': stem, 'object': object_name, 'path': str(path),
        'original_size': len(cipher), 'size': len(new_cipher),
        'changed_blocks': changed,
        'delta': {k: sizes[k] - old_sizes[k] for k in changed},
        'tail_padding': len(cipher) - len(out) + (len(out) - len(out)),
        'sha256': hashlib.sha256(new_cipher).hexdigest(),
        'diff_bytes': count_diff(cipher, new_cipher),
    }


def count_diff(a: bytes, b: bytes) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def build(trans_path: Path = TRANS, out_dir: Path = BUILD, only=None) -> list[dict]:
    trans = json.loads(Path(trans_path).read_text(encoding='utf-8'))
    texts = [b['pl'] for b in trans['blocks']]
    rows = []
    for locale in BUNDLES:
        if only and locale != only:
            continue
        rows.append(build_one(locale, texts, out_dir))
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trans', type=Path, default=TRANS)
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--locale', default=None)
    args = parser.parse_args(argv)
    for row in build(args.trans, args.out_dir, args.locale):
        print(f'{row["locale"]}: {row["path"]}')
        print(f'  rozmiar {row["original_size"]:,} B -> {row["size"]:,} B')
        print(f'  zmienione bloki {row["changed_blocks"]} delta {row["delta"]}')
        print(f'  roznych bajtow w calym pliku: {row["diff_bytes"]:,}')
        print(f'  sha256 {row["sha256"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
