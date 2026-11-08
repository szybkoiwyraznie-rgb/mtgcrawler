#!/usr/bin/env python3
"""Find the Database background texture in the owner's own game files.

The Database viewer (mecha and characters) draws its content over a picture of
the A. Advent interior. To replace that picture with plain black we first have to
name it: nothing in the text corpus mentions a texture, and no game file lives in
this repository. This tool only *reads*: it walks the player's own bundles, lists
every `Texture2D` with its size and format, and writes a report to send back.

    python tools/find_db_background.py --game "D:\\Games\\SUPER ROBOT WARS Y\\...\\StandaloneWindows64" \
        --out RAPORT_TEKSTUR.txt

The report has one line per texture:

    bundle<TAB>texture<TAB>widthxheight<TAB>format<TAB>stream

followed by two shortlists: the largest full-screen pictures and the names that
look like a menu/library/database background. Nothing is written to the game.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

from srw_y_bundle_crypt import decrypt  # noqa: E402

#: Names worth a look before the size shortlist; the JP build calls the library
#: 図鑑 (zukan), the EN build "Database"/"Library".
NAME_HINT = re.compile(r'(db|data_?base|library|zukan|back|bg|haikei)', re.I)
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = 1280, 720


def plain(bundle: Path) -> bytes:
    data = bundle.read_bytes()
    return data if data[:7] == b'UnityFS' else decrypt(bundle.name, data)


def textures_of(bundle: Path) -> list[dict]:
    """Every Texture2D in one bundle: name, size, format, stream path."""
    found = []
    env = UnityPy.load(plain(bundle))
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        try:
            tree = obj.read_typetree()
        except Exception:  # a broken or unexpected object must not stop the scan
            continue
        stream = tree.get('m_StreamData') or {}
        found.append({'bundle': bundle.name,
                      'name': str(tree.get('m_Name', '')),
                      'width': int(tree.get('m_Width') or 0),
                      'height': int(tree.get('m_Height') or 0),
                      'format': int(tree.get('m_TextureFormat') or 0),
                      'stream': str(stream.get('path') or ''),
                      'bytes': int(stream.get('size') or 0)})
    return found


def shortlists(rows: list[dict]) -> dict:
    """Full-screen pictures and name matches, biggest first."""
    big = [row for row in rows
           if row['width'] >= FULLSCREEN_WIDTH and row['height'] >= FULLSCREEN_HEIGHT]
    named = [row for row in rows if NAME_HINT.search(row['name'])]
    order = lambda row: (-(row['width'] * row['height']), row['bundle'], row['name'])
    return {'fullscreen': sorted(big, key=order), 'named': sorted(named, key=order)}


def report_text(rows: list[dict], scanned: int, failed: list[dict]) -> str:
    lines = ['# SRW Y - spis tekstur (narzedzie tylko czyta, nic nie zmienia)',
             f'# bundli w katalogu: {scanned}; odczytanych tekstur: {len(rows)}; '
             f'bundli nieodczytanych: {len(failed)}',
             '# bundle\ttexture\trozmiar\tformat\tstrumien',
             ]
    for row in sorted(rows, key=lambda r: (r['bundle'], r['name'])):
        lines.append('\t'.join([row['bundle'], row['name'],
                                f"{row['width']}x{row['height']}",
                                str(row['format']), row['stream']]))
    lists = shortlists(rows)
    for title, key in (('NAJWIEKSZE OBRAZY (>= %dx%d)' % (FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT),
                        'fullscreen'),
                       ('NAZWY MOGAce BYC TLEM MENU/BAZY', 'named')):
        lines.append('')
        lines.append('# ' + title)
        for row in lists[key][:60]:
            lines.append('\t'.join([row['bundle'], row['name'],
                                    f"{row['width']}x{row['height']}",
                                    str(row['format'])]))
        if not lists[key]:
            lines.append('# (brak)')
    for item in failed:
        lines.append(f"# NIEODCZYTANY {item['bundle']}: {item['error']}")
    return '\n'.join(lines) + '\n'


def scan(game: Path, out: Path) -> dict:
    if not game.is_dir():
        raise SystemExit(f'nie ma katalogu: {game}')
    bundles = sorted(game.rglob('*.bundle'))
    rows, failed = [], []
    for index, bundle in enumerate(bundles, 1):
        try:
            rows.extend(textures_of(bundle))
        except Exception as error:  # record and continue: one odd file is not a failure
            failed.append({'bundle': str(bundle.relative_to(game)),
                           'error': f'{type(error).__name__}: {error}'})
        if index % 200 == 0:
            print(f'{index}/{len(bundles)} bundli, tekstur: {len(rows)}', flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report_text(rows, len(bundles), failed), encoding='utf8')
    lists = shortlists(rows)
    return {'bundles': len(bundles), 'textures': len(rows), 'failed': len(failed),
            'fullscreen': len(lists['fullscreen']), 'named': len(lists['named']),
            'report': str(out)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--game', type=Path, required=True,
                        help='katalog ze plikami .bundle (u mnie: '
                             r'...\StreamingAssets\aa\StandaloneWindows64)')
    parser.add_argument('--out', type=Path, default=Path('RAPORT_TEKSTUR.txt'))
    args = parser.parse_args(argv)
    print(json.dumps(scan(args.game, args.out), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
