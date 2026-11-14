#!/usr/bin/env python3
"""Zbieracz plików dla właściciela: pakuje **tylko wskazane bundle** do jednego ZIP-a.

Po co to jest (2026-11-13). Paczka v4 tła Encyklopedii ma działać także z modem
4K, a tego nie da się *udowodnić* bez plików z gry po modzie: nie wiem, czy mod
zostawił te 16 bundli na miejscu, czy przebudował je w inne pliki. Zamiast
wypisywać właścicielowi 16–17 ścieżek do ręcznego kopiowania (a tego nie
robimy), ten zbieracz sam je znajduje i pakuje:

* pliki z listy, jeśli są w grze,
* każdy inny bundle, który **wymienia nazwę** `BG_DataBase_01`/`BG_DataBase_02`
  (szukanie po zawartości — wolniejsze, ale nie zgaduje),
* dla każdego pliku liczy SHA-256, rozmiar i podaje, które tekstury znalazł.

Wynik: jeden mały ZIP na Pulpicie (kilkadziesiąt MB przy 16 bundlach) plus
`RAPORT_ZBIERACZA.txt`, który mówi, co leży w środku i czego nie znaleziono.

    python zbieracz.py --game "D:/.../SUPER ROBOT WARS Y" --zip "%USERPROFILE%/Desktop/ZBIORCZE.zip"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cipher_fast  # noqa: E402

GAME_DATA = 'SUPER ROBOT WARS Y_Data'
AA = Path('StreamingAssets') / 'aa' / 'StandaloneWindows64'
#: Tekstury, których dotyczy paczka v4 — zbieracz raportuje, gdzie je widzi.
TEXTURES = ('BG_DataBase_01', 'BG_DataBase_02')
#: Ta sama lista 16 bundli, co w `tlo_bazy5.py` (spis z 1.4.0).
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
MIN_BUNDLE = 64 * 1024
#: Większe pliki są pomijane w szukaniu po zawartości: bundle z teksturami
#: ekranu Database mają kilka MB, a kilkusetmegabajtowe paczki animacji nie są
#: tym, o co pytamy — inaczej zbieracz czytałby całą grę.
MAX_SCAN_BYTES = 64 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def log(lines: list[str] | None, text: str) -> None:
    """Print *and* keep the line for RAPORT_ZBIERACZA.txt.

    This was missing and every collection run died with `NameError: name 'log'
    is not defined` at the first progress line — before any file was written,
    so the owner got a crash instead of the ZIP. Same helper as `tlo_bazy5.py`.
    """
    print(text, flush=True)
    if lines is not None:
        lines.append(text)


def find_game() -> Path:
    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
        for suffix in ('SUPER ROBOT WARS Y', 'SRWY',
                       'Games/SUPER ROBOT WARS Y', 'Gry/SUPER ROBOT WARS Y',
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
    """Czy bundle wymienia nazwę (bloki bywają LZ4, więc dekompresja jest konieczna)."""
    if wanted in plain:
        return True
    try:
        from lz4_block_map import decompress_blocks, parse_container

        layout = parse_container(plain)
        blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    except Exception:
        return False
    return wanted in blob


def decompress(plain: bytes) -> bytes:
    """Strumień serializowany z kontenera (bloki bywają LZ4 — trzeba je rozwinąć).

    `UnityPy.load()` na samym kontenerze nie widzi obiektów: one są w blokach,
    a nie w nagłówku UnityFS. Bez tego raport zawsze mówiłby „brak naszych
    tekstur”, także dla plików, które je mają.
    """
    from lz4_block_map import decompress_blocks, parse_container

    layout = parse_container(plain)
    return b''.join(part[2] for part in decompress_blocks(plain, layout))


def textures_named(plain: bytes) -> list[dict]:
    """Które z naszych tekstur są w tym bundlu — z rozmiarem, formatem i trybem.

    Tryb (`inline` / `stream`) jest tu najważniejszy: mówi, **gdzie** mod 4K
    położył piksele, czyli którą drogą zapisu ma iść v5. To jest dokładnie ta
    informacja, po którą zbieracz jedzie do właściciela.
    """
    if not any(mentions(plain, name.encode('ascii')) for name in TEXTURES):
        return []
    import UnityPy

    found = []
    env = UnityPy.load(decompress(plain))
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        tree = obj.read_typetree()
        name = str(tree.get('m_Name'))
        if name not in TEXTURES:
            continue
        channel = tree.get('m_StreamData') or {}
        offset, size = int(channel.get('offset') or 0), int(channel.get('size') or 0)
        inline = tree.get('image data') or b''
        found.append({'name': name, 'width': int(tree.get('m_Width') or 0),
                      'height': int(tree.get('m_Height') or 0),
                      'format': int(tree.get('m_TextureFormat') or 0),
                      'mips': int(tree.get('m_MipCount') or 1),
                      'mode': 'stream' if (size or channel.get('path')) else 'inline',
                      'pixels': size or len(inline)})
    return found


def collect(streaming: Path, lines: list[str]) -> list[Path]:
    """Lista plików do spakowania: z listy, potem wszystko, co wymienia nazwy."""
    chosen: list[Path] = []
    for name in BUNDLES:
        path = streaming / name
        if path.is_file():
            chosen.append(path)
            print(f'z listy: {name} ({path.stat().st_size:,} B)')
    log(lines, f'Plikow z listy 1.4.0 w grze: {len(chosen)}/{len(BUNDLES)}')
    missing = [name for name in BUNDLES if not (streaming / name).is_file()]
    if missing:
        log(lines, f'Brakuje z listy: {", ".join(missing)}')
    log(lines, 'Szukam po zawartosci pozostalych bundli, ktore wymieniaja '
               f'{TEXTURES[0]} / {TEXTURES[1]} (to potrwa kilka minut)...')
    seen = set(chosen)
    paths = sorted(p for p in streaming.rglob('*.bundle')
                   if MIN_BUNDLE <= p.stat().st_size <= MAX_SCAN_BYTES)
    for index, path in enumerate(paths, 1):
        if index % 500 == 0:
            print(f'   przeszukane {index}/{len(paths)}, wybranych: {len(seen)}', flush=True)
        if path in seen:
            continue
        try:
            plain = cipher_fast.plain_of(path)
        except (OSError, ValueError):
            continue
        if any(mentions(plain, name.encode('ascii')) for name in TEXTURES):
            chosen.append(path)
            seen.add(path)
            log(lines, f'po zawartosci: {path.name} ({path.stat().st_size:,} B)')
    log(lines, f'Plikow wybranych razem: {len(chosen)}')
    return chosen


def build_zip(paths: list[Path], streaming: Path, target: Path,
              lines: list[str]) -> dict:
    entries = []
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in paths:
            data = path.read_bytes()
            rel = path.relative_to(streaming).as_posix()
            archive.writestr(zipfile.ZipInfo(rel, (2026, 11, 13, 0, 0, 0)), data)
            try:
                found = textures_named(cipher_fast.plain_of(path))
            except (OSError, ValueError):
                found = []
            entry = {'path': rel, 'bytes': len(data), 'sha256': sha256(data),
                     'textures': found}
            entries.append(entry)
            names = ', '.join(
                f'{t["name"]} {t["width"]}x{t["height"]} (format {t["format"]}, '
                f'{t["mips"]} mip., '
                f'{"w obiekcie" if t["mode"] == "inline" else "w strumieniu"}, '
                f'{t["pixels"]:,} B)' for t in found) or 'brak naszych tekstur'
            log(lines, f'{rel}: {len(data):,} B, {names}')
    return {'zip': str(target), 'bytes': target.stat().st_size,
            'sha256': sha256(target.read_bytes()), 'files': entries}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Zbierz bundli tla Database do jednego ZIP-a.')
    parser.add_argument('--game', type=Path, help='folder gry (ten z SUPER ROBOT WARS Y.exe)')
    parser.add_argument('--zip', type=Path,
                        default=Path(os.environ.get('USERPROFILE') or Path.home())
                        / 'Desktop' / 'SRW_Y_ZBIORCZE_TLO.zip')
    parser.add_argument('--out', type=Path, default=HERE, help='gdzie zapisac raport')
    args = parser.parse_args(argv)
    lines: list[str] = []
    started = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        game = args.game or find_game()
        streaming = game / GAME_DATA / AA
        if not streaming.is_dir():
            raise ValueError(f'nie ma folderu {streaming}')
        paths = collect(streaming, lines)
        if not paths:
            raise ValueError('nie znalazlem zadnego bundla z naszymi teksturami — '
                             'wyslij mi RAPORT_ZBIERACZA.txt, ustalimy nastepny krok')
        result = build_zip(paths, streaming, args.zip, lines)
        summary = (f'GOTOWE. Plik: {result["zip"]} ({result["bytes"]:,} B). '
                   f'SHA-256: {result["sha256"]}. Plikow w srodku: {len(result["files"])}.')
        print(summary, flush=True)
        lines.append(summary)
        (args.out / 'RAPORT_ZBIERACZA.json').write_text(
            json.dumps({'when': started, **result}, ensure_ascii=False, indent=1), encoding='utf8')
        exit_code = 0
    except (OSError, ValueError) as exc:
        print(f'BLAD: {exc}', flush=True)
        lines.append(f'BLAD: {exc}')
        exit_code = 1
    (args.out / 'RAPORT_ZBIERACZA.txt').write_text(
        '\n'.join([f'# SRW Y - zbieracz tla Database ({started})', ''] + lines) + '\n',
        encoding='utf8')
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
