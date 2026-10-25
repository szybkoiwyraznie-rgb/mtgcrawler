"""Statyczne tłumaczenie tekstu w bundle'ach SRW Y: odszyfruj → podmień → zaszyfruj.

The pipeline for one bundle is exactly the one the owner asked for, and every
step is offline:

    cipher = local/s4/<stem>.bundle
    plain  = srw_y_bundle_crypt.decrypt(stem, cipher)      # key recovered in S3
    edit   = UnityPy: replace the 24 fields of `prologue_*` with the Polish text
    plain' = env.file.save(packer='original')              # still a UniytFS bundle
    cipher'= srw_y_bundle_crypt.encrypt(stem, plain')      # same cipher, new length

`build` does that for both locales and writes `build/<stem>.bundle`; `verify`
reads the built files back through the cipher and checks the text field by field.

    python3 tools/srw_y_text_patch.py build
    python3 tools/srw_y_text_patch.py verify
    python3 tools/srw_y_text_patch.py probe local/s4_plain/<stem>.bundle
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import UnityPy  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
LOCAL = HERE / 'local'
TRANS = HERE / 'translations' / 'opening_pl.json'
BUILD = HERE / 'build'

BUNDLES = {
    'en-US': ('2d69c099bfdf0e252dabe84dbbba11df', 'prologue_en-US'),
    'ja-JP': ('1cc7e02ee5711c6ba87a0e364f62198c', 'prologue_ja-JP'),
}


# ------------------------------------------------------------------ table scanning
def is_text(data: bytes) -> bool:
    """True for the display strings this table holds (prose, no binary noise)."""
    if len(data) < 2:
        return False
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return False
    if not all(ch == '\n' or 32 <= ord(ch) < 127 or ord(ch) > 127 for ch in text):
        return False
    wide = sum(1 for ch in text if ord(ch) > 127)
    return wide >= 3 or (len(data) >= 20 and text.count(' ') >= 2)


def find_blocks(raw: bytes) -> list[tuple[int, int, bytes]]:
    """The table's strings as (offset of the int32 prefix, length, bytes)."""
    blocks, i = [], 0
    while i < len(raw) - 4:
        size = struct.unpack('<i', raw[i:i + 4])[0]
        if 2 <= size <= 8192 and i + 4 + size <= len(raw):
            data = raw[i + 4:i + 4 + size]
            if is_text(data):
                blocks.append((i, size, data))
                i += 4 + size
                continue
        i += 1
    return blocks


def replace_blocks(raw: bytes, blocks, texts) -> bytes:
    """Rebuild the object with each string replaced; lengths may change."""
    out = bytearray(raw)
    for (offset, size, _old), text in zip(reversed(blocks), reversed(texts)):
        data = text.encode('utf-8')
        out[offset:offset + 4 + size] = struct.pack('<i', len(data)) + data
    return bytes(out)


def object_raw(plain: bytes, object_name: str) -> bytes:
    env = UnityPy.load(plain)
    for obj in env.objects:
        if obj.type.name == 'MonoBehaviour' and obj.peek_name() == object_name:
            return obj.get_raw_data()
    raise SystemExit(f'{object_name} not found')


# ------------------------------------------------------------------------- building
def build_one(locale: str, texts, out_dir: Path) -> dict:
    stem, object_name = BUNDLES[locale]
    cipher = (LOCAL / 's4' / f'{stem}.bundle').read_bytes()
    plain = decrypt(stem, cipher)
    reference = (LOCAL / 's4_plain' / f'{stem}.bundle').read_bytes()
    if plain != reference:
        raise SystemExit(f'{stem}: decrypt() disagrees with the stored plaintext')

    env = UnityPy.load(plain)
    target = None
    before = {}
    for obj in env.objects:
        try:
            before[obj.path_id] = obj.get_raw_data()
        except Exception:  # noqa: BLE001 - typetree-less objects still round-trip
            before[obj.path_id] = None
        if obj.type.name == 'MonoBehaviour' and obj.peek_name() == object_name:
            target = obj
    if target is None:
        raise SystemExit(f'{stem}: {object_name} not found')

    raw = target.get_raw_data()
    blocks = find_blocks(raw)
    if len(blocks) != len(texts):
        raise SystemExit(f'{stem}: {len(blocks)} strings in the table, '
                         f'{len(texts)} translations')
    target.set_raw_data(replace_blocks(raw, blocks, texts))
    new_plain = env.file.save(packer='original')

    # ---- checks on the rebuilt plaintext
    check = UnityPy.load(new_plain)
    found = None
    for obj in check.objects:
        got = None
        try:
            got = obj.get_raw_data()
        except Exception:  # noqa: BLE001
            got = None
        if obj.path_id == target.path_id:
            found = got
        elif before.get(obj.path_id) is not None and got != before[obj.path_id]:
            raise SystemExit(f'{stem}: object {obj.path_id} changed unexpectedly')
    if found is None:
        raise SystemExit(f'{stem}: the patched object vanished')
    got_texts = [t for _o, _n, t in find_blocks(found)]
    if got_texts != [t.encode('utf-8') for t in texts]:
        raise SystemExit(f'{stem}: rebuilt table does not read back as the translation')

    new_cipher = encrypt(stem, new_plain)
    if decrypt(stem, new_cipher) != new_plain:
        raise SystemExit(f'{stem}: cipher round trip failed')

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f'{stem}.bundle'
    out.write_bytes(new_cipher)
    return {
        'locale': locale,
        'stem': stem,
        'object': object_name,
        'original_size': len(cipher),
        'patched_size': len(new_cipher),
        'original_sha256': hashlib.sha256(cipher).hexdigest(),
        'patched_sha256': hashlib.sha256(new_cipher).hexdigest(),
        'plain_size': len(new_plain),
        'path': str(out),
    }


def build(trans_path: Path = TRANS, out_dir: Path = BUILD) -> list[dict]:
    import json

    trans = json.loads(Path(trans_path).read_text(encoding='utf-8'))
    texts = [block['pl'] for block in trans['blocks']]
    return [build_one(locale, texts, out_dir) for locale in BUNDLES]


def verify(trans_path: Path = TRANS, out_dir: Path = BUILD) -> list[dict]:
    import json

    trans = json.loads(Path(trans_path).read_text(encoding='utf-8'))
    texts = [block['pl'] for block in trans['blocks']]
    rows = []
    for locale, (stem, object_name) in BUNDLES.items():
        cipher = (Path(out_dir) / f'{stem}.bundle').read_bytes()
        plain = decrypt(stem, cipher)
        raw = object_raw(plain, object_name)
        got = [t.decode('utf-8') for _o, _n, t in find_blocks(raw)]
        rows.append({
            'locale': locale, 'stem': stem, 'strings': len(got),
            'match': got == texts, 'size': len(cipher),
            'sha256': hashlib.sha256(cipher).hexdigest(),
        })
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)

    d = sub.add_parser('dump', help='print the strings of a decrypted bundle')
    d.add_argument('plain', type=Path)

    b = sub.add_parser('build')
    b.add_argument('--trans', type=Path, default=TRANS)
    b.add_argument('--out-dir', type=Path, default=BUILD)

    v = sub.add_parser('verify')
    v.add_argument('--trans', type=Path, default=TRANS)
    v.add_argument('--out-dir', type=Path, default=BUILD)

    args = parser.parse_args(argv)
    if args.cmd == 'dump':
        env = UnityPy.load(args.plain.read_bytes())
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            blocks = find_blocks(obj.get_raw_data())
            if not blocks:
                continue
            print(f'{obj.peek_name()}: {len(blocks)} strings')
            for k, (_offset, size, data) in enumerate(blocks, 1):
                print(f'  {k:3d} {size:5d} B  {data.decode("utf-8")!r}')
    elif args.cmd == 'build':
        for row in build(args.trans, args.out_dir):
            print(f'{row["locale"]}: {row["path"]}')
            print(f'  {row["original_size"]:,} B -> {row["patched_size"]:,} B '
                  f'(serialized {row["plain_size"]:,} B)')
            print(f'  {row["original_sha256"]}')
            print(f'  {row["patched_sha256"]}')
    else:
        for row in verify(args.trans, args.out_dir):
            state = 'OK' if row['match'] else 'MISMATCH'
            print(f'{row["locale"]}: {row["strings"]} strings {state}, '
                  f'{row["size"]:,} B, {row["sha256"]}')
        if not all(row['match'] for row in verify(args.trans, args.out_dir)):
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
