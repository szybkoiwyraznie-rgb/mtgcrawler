#!/usr/bin/env python3
"""Owner-side tool: make the Database background black, and put it back.

The owner never sends game files, so the bundle is patched where it lives. His
own texture inventory (`RAPORT_TEKSTUR.txt`) already names every bundle that
carries `BG_DataBase_01` (1920x1080), so the list is shipped in this script and
nothing is searched: each path is opened directly, `db_black` replaces the
pixels with solid black, rebuilds the bundle and checks the result, then the
file is written and a `.srwy-tlo-original.bak` stays next to it. `restore`
copies the originals back.

    python tlo_bazy.py install
    python tlo_bazy.py restore

Both actions write `RAPORT_TLO.txt` next to this file and store what they changed
in `STAN_TLO.json`, so an interrupted install can still be undone.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cipher_fast import decrypt_bundle, plain_of  # noqa: E402
from db_black import patch_plain  # noqa: E402
from srw_y_bundle_crypt import encrypt  # noqa: E402

GAME_DATA = 'SUPER ROBOT WARS Y_Data'
AA = Path('StreamingAssets') / 'aa' / 'StandaloneWindows64'
TEXTURE = 'BG_DataBase_01'
SIZE = (1920, 1080)
#: Every bundle that carries the texture, copied from the owner's own
#: `RAPORT_TEKSTUR.txt` (2026-11-08: 16 bundles, all `BG_DataBase_01` 1920x1080).
#: The first one is the bundle whose preview the owner pointed at (`22869_...png`).
#: Scanning his 9,892 bundles is what made the first kit hang for an hour: with
#: this list the whole job is 16 files, opened by name.
BUNDLES = (
    '9ed026a1fc86446a7b96c863f449293e.bundle',
    '1b5da0ef65aef8e3db19c7f1b4a62ad2.bundle',
    '1c6bae8333d43883715cd3c80e6b06a8.bundle',
    '21483b8c72946df172995fc28fe8513c.bundle',
    '22ac8fb334093afc874a670d95b01504.bundle',
    '24389cf9b6ff0c69440a0054b07a0a9b.bundle',
    '2fcd1b5e54f206a6ecf97a71c74dcd81.bundle',
    '36f12b4c38f68ad8811ade71945010c9.bundle',
    '3de1bf33b35e63e87abb86acc029004f.bundle',
    '77a2edfda00011ae81b0d44829865614.bundle',
    '77c28b41bf3d3714c686eafb475fc32a.bundle',
    '819fcfa52c97d0420146203b181e38cf.bundle',
    '89807f3be3a7048e8e26f7e8edccb6da.bundle',
    '90eb8d46b646d92973b36bac119ca271.bundle',
    '9e56e5c953cea02a1e42b2ed1dba787f.bundle',
    'cea16a719b85736215c37206de071b72.bundle',
)
#: Text and scene bundles are a few kilobytes; a 1920x1080 picture is megabytes.
MIN_BUNDLE = 64 * 1024
BACKUP_SUFFIX = '.srwy-tlo-original.bak'
STATE = HERE / 'STAN_TLO.json'
REPORT = HERE / 'RAPORT_TLO.txt'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def log(lines: list[str], text: str) -> None:
    print(text, flush=True)
    lines.append(text)


def check_game_stopped() -> None:
    if os.name != 'nt':
        return
    result = subprocess.run(['tasklist', '/fo', 'csv', '/nh'], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('nie można sprawdzić uruchomionych procesów; zamknij grę i spróbuj ponownie')
    for row in csv.reader(result.stdout.splitlines()):
        if row and 'super robot wars y' in row[0].lower():
            raise ValueError('gra jest uruchomiona — zamknij ją przed podmianą lub cofnięciem')


def find_game() -> Path:
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


def mentions(plain: bytes, wanted: bytes) -> bool:
    """Does this bundle mention the name at all?

    The name sits in the serialized file, which the container may hold LZ4-compressed,
    so the raw plaintext is not enough: decompress the blocks and look there. That is
    still far cheaper than asking UnityPy to parse thousands of bundles.
    """
    if wanted in plain:
        return True
    try:
        from lz4_block_map import decompress_blocks, parse_container

        layout = parse_container(plain)
        blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    except Exception:            # not a container we understand — not our bundle
        return False
    return wanted in blob


def pinned_paths(streaming: Path) -> list[Path]:
    """The listed bundles that exist in this copy of the game, in list order."""
    return [streaming / name for name in BUNDLES if (streaming / name).is_file()]


def candidates(streaming: Path, name: str = TEXTURE, log=None) -> list[Path]:
    """Fallback only: bundles that mention the texture name, biggest first.

    This walks thousands of files and takes minutes, so it runs only when none of
    the BUNDLES names exists — a different game version, not the normal path.
    """
    wanted = name.encode('ascii')
    found = []
    paths = sorted(p for p in streaming.rglob('*.bundle') if p.stat().st_size >= MIN_BUNDLE)
    for index, path in enumerate(paths, 1):
        if log is not None and index % 500 == 0:
            log(f'   przeszukane {index}/{len(paths)} plikow, trafien: {len(found)}')
        try:
            if not mentions(plain_of(path), wanted):
                continue
        except (OSError, ValueError):
            continue
        found.append(path)
    return sorted(found, key=lambda p: -p.stat().st_size)


def install(game: Path, lines: list[str], scan: bool = False,
            identified_only: bool = False) -> dict:
    streaming = game / GAME_DATA / AA
    if not streaming.is_dir():
        raise ValueError(f'nie ma folderu {streaming}')
    paths = pinned_paths(streaming)
    if identified_only:
        paths = [path for path in paths if path.name == BUNDLES[0]]
    if paths:
        log(lines, f'Lista z Twojego spisu tekstur: {len(BUNDLES)} plikow z {TEXTURE} '
                   f'{SIZE[0]}x{SIZE[1]}; w grze jest {len(paths)}. Nie przeszukuje dysku.')
    elif scan:
        log(lines, 'Zadnego pliku z listy nie ma w grze — przeszukuje bundle '
                   '(to potrwa kilka minut, w raporcie widac postep)...')
        paths = candidates(streaming, log=lambda text: log(lines, text))
        log(lines, f'Bundli, ktore wymieniaja nazwe: {len(paths)}')
    else:
        raise ValueError(f'w grze nie ma zadnego z {len(BUNDLES)} plikow, ktore wedlug Twojego '
                         f'spisu tekstur zawieraja {TEXTURE} {SIZE[0]}x{SIZE[1]} — '
                         f'masz inna wersje gry niz ta, z ktorej robilem spis? '
                         f'Wyslij mi RAPORT_TLO.txt, albo uruchom PATCH_TLO.bat drugi raz '
                         f'z opcja --skanuj, zeby poszukal tekstury w calym katalogu.')
    for path in paths:
        log(lines, f'   {path.relative_to(streaming)} ({path.stat().st_size:,} B)')
    started = time.time()
    entries, skipped = [], []
    for index, path in enumerate(paths, 1):
        stem = path.name
        log(lines, f'[{index}/{len(paths)}] {stem} ...')
        try:
            plain = plain_of(path)
            new_plain, info = patch_plain(stem, plain, TEXTURE, SIZE)
        except ValueError as error:
            skipped.append(f'{stem}: {error}')
            log(lines, f'POMIJAM {error}')
            continue
        cipher = encrypt(stem, new_plain)
        if decrypt_bundle(stem, cipher) != new_plain:
            raise ValueError(f'{stem}: szyfrowanie nie odtwarza pliku')
        backup = path.parent / (path.name + BACKUP_SUFFIX)
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        before_hash = sha256(path.read_bytes())
        path.write_bytes(cipher)
        after = path.read_bytes()
        if sha256(after) != sha256(cipher):
            raise ValueError(f'{stem}: zapisany plik nie zgadza sie z przebudowanym')
        if decrypt_bundle(stem, after) != new_plain:
            raise ValueError(f'{stem}: odczyt zapisanego pliku nie daje przebudowanego bundla')
        entries.append({'bundle': str(path.relative_to(streaming)), 'path': str(path),
                        'sha256_before': before_hash, 'sha256_after': sha256(after),
                        'backup': str(backup), 'info': info})
        log(lines, f'OK   {path.relative_to(streaming)} — {TEXTURE} '
                   f'{info["width"]}x{info["height"]} {info["format"]}, '
                   f'zmnienionych bajtow: {info["bytes_changed"]}, '
                   f'czern sprawdzona: {info["black_verified"]}')
    if not entries:
        detail = f' Powody pominiecia: {"; ".join(skipped[:5])}' if skipped else ''
        raise ValueError(f'nie znalazłem tekstury {TEXTURE} {SIZE[0]}x{SIZE[1]} — '
                         f'gra ma inną wersję niż ta, z której robilem spis?{detail}')
    state = {'schema': 1, 'texture': TEXTURE, 'size': list(SIZE),
             'when': time.strftime('%Y-%m-%d %H:%M:%S'), 'bundles': entries,
             'skipped': skipped}
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf8')
    log(lines, f'GOTOWE. Zmienione bundle: {len(entries)}. '
               f'Cofniecie: COFNIJ.bat. Czas: {time.time() - started:.0f} s.')
    return state


def restore(lines: list[str]) -> int:
    if not STATE.is_file():
        raise ValueError(f'nie ma pliku {STATE.name} — nie wiem, co przywrócić; '
                         f'uruchom ten plik z tego samego folderu, w ktorym robiles podmiane')
    state = json.loads(STATE.read_text(encoding='utf8'))
    restored = 0
    for entry in state['bundles']:
        path = Path(entry['path'])
        backup = Path(entry['backup'])
        if not backup.is_file():
            raise ValueError(f'brakuje kopii {backup} — nie ruszam {path}')
        data = backup.read_bytes()
        if sha256(data) != entry['sha256_before']:
            raise ValueError(f'kopia {backup} nie zgadza sie z zapisanym hashem — nie ruszam')
        path.write_bytes(data)
        if sha256(path.read_bytes()) != entry['sha256_before']:
            raise ValueError(f'{path}: po przywroceniu hash sie nie zgadza')
        restored += 1
        log(lines, f'OK   przywrocono {entry["bundle"]}')
    state['restored'] = time.strftime('%Y-%m-%d %H:%M:%S')
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf8')
    log(lines, f'GOTOWE. Przywrocone bundle: {restored}.')
    return restored


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Tlo ekranu Database: czern i cofniecie.')
    parser.add_argument('action', choices=('install', 'restore'))
    parser.add_argument('--game', type=Path)
    parser.add_argument('--skanuj', action='store_true',
                        help='awaryjnie: szukaj tekstury w calym katalogu, gdy lista plikow nie pasuje')
    parser.add_argument('--tylko-rozpoznany', action='store_true',
                        help='podmien tylko ten bundle, ktory wskazal wlasciciel na podgladzie')
    args = parser.parse_args(argv)
    lines: list[str] = [f'RAPORT TLO BAZY DANYCH — {time.strftime("%Y-%m-%d %H:%M:%S")}',
                        f'akcja: {args.action}']
    try:
        check_game_stopped()
        if args.action == 'install':
            game = args.game or find_game()
            install(game, lines, scan=args.skanuj, identified_only=args.tylko_rozpoznany)
        else:
            restore(lines)
        code = 0
    except (OSError, ValueError, KeyError) as error:
        log(lines, f'BLAD: {error}')
        code = 1
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf8')
    print(f'Szczegoly: {REPORT}')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
