#!/usr/bin/env python3
"""Spis tekstur gry — narzędzie tylko czytające, część paczki dla właściciela.

Ekran Database rysuje mechy i postacie na tle wnętrza A. Adventu. To tło jest
**teksturą**, nie tekstem, więc żeby je zastąpić czernią, trzeba najpierw znać
jej nazwę. Ten skrypt przechodzi bundel po bundlu w kopii gry użytkownika i
wypisuje każdą `Texture2D`: nazwę, rozmiar, format i strumień, a duże obrazy
zapisuje dodatkowo jako podglądy PNG (zmniejszone), żeby dało się je rozpoznać
na oko.

Nic nie jest zmieniane: pliki gry są tylko czytane, a wynik (raport + podglądy)
ląduje w jednym ZIP-ie na Pulpicie.

    python spis_tekstur.py --game "D:\\...\\SUPER ROBOT WARS Y"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import srw_y_bundle_crypt as cipher  # noqa: E402

GAME_DATA = 'SUPER ROBOT WARS Y_Data'
AA = Path('StreamingAssets') / 'aa' / 'StandaloneWindows64'
#: A texture cannot live in a few kilobytes of bundle; the text and scene bundles
#: are all below this, and skipping them keeps the scan short.
MIN_BUNDLE = 64 * 1024
#: Pictures at least this big are treated as screen backgrounds and get a preview.
FULLSCREEN = (1280, 720)
PREVIEW_WIDTH = 480
NAME_HINT = re.compile(r'(db|data_?base|library|zukan|back|bg|haikei)', re.I)


def find_game() -> Path:
    """The same search the patcher does, so the owner never types a path."""
    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
        for suffix in ('Games/SUPER ROBOT WARS Y', 'Gry/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SRWY',
                       'Program Files/Steam/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SUPER ROBOT WARS Y',
                       'Program Files/Steam/steamapps/common/SUPER ROBOT WARS Y'):
            candidate = Path(f'{letter}:/{suffix}')
            if (candidate / GAME_DATA).is_dir():
                print(f'Znaleziono gre: {candidate}')
                return candidate
    return Path(input('Podaj folder gry SUPER ROBOT WARS Y: ').strip().strip('"'))


def decrypt_bundle(name: str, data: bytes) -> bytes:
    """The bundle cipher, but with the XOR done by pycryptodome instead of a loop.

    `srw_y_bundle_crypt.decrypt` XORs byte by byte, which is fine for a handful of
    bundles and far too slow for a whole game; the keystream and the AES calls are
    the same, only the XOR moves into C.
    """
    try:
        from Crypto.Cipher import AES
        from Crypto.Util import strxor
    except ImportError:  # pragma: no cover - the kit installs pycryptodome
        return cipher.decrypt(name, data)
    key = cipher.key_for(name)
    blocks = (len(data) + 15) // 16
    ecb = AES.new(key, AES.MODE_ECB)
    chunks = []
    for start in range(1, blocks + 1, 4096):
        stop = min(start + 4096, blocks + 1)
        chunks.append(ecb.encrypt(b''.join(cipher.nonce(i) for i in range(start, stop))))
    stream = b''.join(chunks)
    padded = data + b'\x00' * (len(stream) - len(data))
    return strxor.strxor(padded, stream)[:len(data)]


def plain_of(path: Path) -> bytes:
    data = path.read_bytes()
    return data if data[:7] == b'UnityFS' else decrypt_bundle(path.name, data)


def textures_of(path: Path) -> list[dict]:
    """Every Texture2D in one bundle, read from the typetree (no pixel decoding)."""
    import UnityPy

    found = []
    env = UnityPy.load(plain_of(path))
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        tree = obj.read_typetree()
        stream = tree.get('m_StreamData') or {}
        found.append({'object': obj,
                      'bundle': path.name,
                      'name': str(tree.get('m_Name', '')),
                      'width': int(tree.get('m_Width') or 0),
                      'height': int(tree.get('m_Height') or 0),
                      'format': int(tree.get('m_TextureFormat') or 0),
                      'stream': str(stream.get('path') or ''),
                      'bytes': int(stream.get('size') or 0)})
    return found


def is_fullscreen(row: dict) -> bool:
    return row['width'] >= FULLSCREEN[0] and row['height'] >= FULLSCREEN[1]


def preview(row: dict, target: Path) -> str:
    """Save a small PNG of one texture; failures are reported, never fatal."""
    try:
        image = row['object'].read().image
    except Exception as error:
        return f'BLAD podgladu: {type(error).__name__}: {error}'
    try:
        image = image.convert('RGB')
        image.thumbnail((PREVIEW_WIDTH, PREVIEW_WIDTH))
        image.save(target)
    except Exception as error:
        return f'BLAD podgladu: {type(error).__name__}: {error}'
    return ''


def shortlists(rows: list[dict]) -> dict:
    order = lambda row: (-(row['width'] * row['height']), row['bundle'], row['name'])
    return {'fullscreen': sorted((row for row in rows if is_fullscreen(row)), key=order),
            'named': sorted((row for row in rows if NAME_HINT.search(row['name'])), key=order)}


def report_text(rows: list[dict], scanned: int, failed: list[dict], empty: int = 0) -> str:
    lines = ['# SRW Y - spis tekstur (narzedzie tylko czyta, nic nie zmienia)',
             f'# bundli w katalogu: {scanned}; odczytanych tekstur: {len(rows)}; '
             f'bundli nieodczytanych: {len(failed)}; bundli bez obiektow: {empty}',
             '# nr\tbundle\ttekstura\trozmiar\tformat\tpodglad']
    for number, row in enumerate(sorted(rows, key=lambda r: (r['bundle'], r['name'])), 1):
        lines.append('\t'.join([str(number), row['bundle'], row['name'],
                                f"{row['width']}x{row['height']}",
                                str(row['format']), row.get('preview', '')]))
    lists = shortlists(rows)
    for title, key in (('NAJWIEKSZE OBRAZY (>= %dx%d)' % FULLSCREEN, 'fullscreen'),
                       ('NAZWY MOGA BYC TLEM MENU/BAZY', 'named')):
        lines += ['', '# ' + title]
        for row in lists[key][:80]:
            lines.append('\t'.join([str(row.get('number', '')), row['bundle'], row['name'],
                                    f"{row['width']}x{row['height']}", str(row['format']),
                                    row.get('preview', '')]))
        if not lists[key]:
            lines.append('# (brak)')
    for item in failed:
        lines.append(f"# NIEODCZYTANY {item['bundle']}: {item['error']}")
    return '\n'.join(lines) + '\n'


def scan(streaming: Path, out_dir: Path, previews: bool = True, limit: int = 0) -> dict:
    """Walk the bundles once; previews are made on the spot so no bundle is kept open."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    folder = out_dir / 'PODGLADY'
    if previews:
        folder.mkdir(parents=True, exist_ok=True)
    bundles = sorted(p for p in streaming.rglob('*.bundle') if p.stat().st_size >= MIN_BUNDLE)
    if limit:
        bundles = bundles[:limit]
    rows, failed, empty = [], [], 0
    started = time.time()
    for index, bundle in enumerate(bundles, 1):
        try:
            found = textures_of(bundle)
        except Exception as error:  # one odd bundle must not stop the whole scan
            failed.append({'bundle': str(bundle.relative_to(streaming)),
                           'error': f'{type(error).__name__}: {error}'})
            found = []
        if not found:
            empty += 1
        for row in found:
            row['preview'] = ''
            if previews and is_fullscreen(row):
                safe = re.sub(r'[^A-Za-z0-9_.-]', '_', row['name'])
                name = f'{len(rows) + 1:04d}_{safe}_{row["width"]}x{row["height"]}.png'
                error = preview(row, folder / name)
                if error:
                    failed.append({'bundle': row['bundle'],
                                   'error': f'{row["name"]}: {error}'})
                else:
                    row['preview'] = name
            row.pop('object', None)      # never hold a whole bundle alive for a row
            rows.append(row)
        if index % 20 == 0 or index == len(bundles):
            print(f'{index}/{len(bundles)} bundli, tekstur: {len(rows)}, '
                  f'{time.time() - started:.0f} s', flush=True)
    report = report_text(rows, len(bundles), failed, empty)
    (out_dir / 'RAPORT_TEKSTUR.txt').write_text(report, encoding='utf8')
    lists = shortlists(rows)
    return {'bundles': len(bundles), 'textures': len(rows), 'failed': len(failed),
            'empty_bundles': empty,
            'fullscreen': len(lists['fullscreen']), 'named': len(lists['named']),
            'seconds': round(time.time() - started),
            'report': str(out_dir / 'RAPORT_TEKSTUR.txt')}


def zip_result(out_dir: Path, zip_path: Path) -> dict:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(out_dir))
    return {'zip': str(zip_path), 'zip_size': zip_path.stat().st_size}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Spis tekstur SRW Y (tylko czyta).')
    parser.add_argument('--game', type=Path, help='folder gry (ten z SUPER ROBOT WARS Y.exe)')
    parser.add_argument('--out', type=Path, default=HERE, help='gdzie zapisac raport i podglady')
    parser.add_argument('--zip', type=Path, help='gdzie zapisac ZIP z wynikiem')
    parser.add_argument('--no-previews', action='store_true', help='bez podgladow PNG')
    parser.add_argument('--limit', type=int, default=0, help='tylko pierwsze N bundli (test)')
    args = parser.parse_args(argv)
    try:
        game = args.game or find_game()
        streaming = game / GAME_DATA / AA
        if not streaming.is_dir():
            print(f'BLAD: nie ma folderu {streaming}', file=sys.stderr)
            return 1
        result = scan(streaming, args.out, previews=not args.no_previews, limit=args.limit)
        if args.zip:
            result |= zip_result(args.out, args.zip)
        print('GOTOWE.')
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f'BLAD: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
