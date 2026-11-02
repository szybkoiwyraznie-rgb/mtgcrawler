#!/usr/bin/env python3
"""Build a binary-free, opt-in test kit; never overwrites an existing ZIP."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import build_distribution as DIST

ROOT = Path(__file__).resolve().parent.parent


def build(out: Path) -> dict:
    if out.exists():
        raise ValueError('refusing to overwrite an existing ZIP')
    tools = ROOT / 'tools'
    entries = {
        'TEST_PILOTOW.bat': (tools / 'fixed_pilot_test_kit/TEST_PILOTOW.bat').read_bytes().replace(b'\n', b'\r\n'),
        'CZYTAJ_TO.txt': (tools / 'fixed_pilot_test_kit/CZYTAJ_TO.txt').read_bytes(),
        'narzedzia/fixed-pilot-test-v410-hashes.json': (ROOT / 'config/pl/fixed-pilot-test-v410-hashes.json').read_bytes(),
    }
    for name in sorted(DIST._resolve(tools, ('fixed_pilot_slots_test',))):
        path = tools / (name + '.py')
        if not path.is_file():
            raise ValueError('missing dependency: ' + name)
        entries['narzedzia/' + path.name] = path.read_bytes()
    hashes = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(entries.items())}
    entries['narzedzia/MANIFEST.json'] = (json.dumps({'experimental': True, 'runtime_tested': False,
        'game_binaries_included': False, 'sha256_by_file': hashes}, indent=2) + '\n').encode('utf-8')
    out.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with zipfile.ZipFile(out, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            created = True
            for name, content in sorted(entries.items()):
                info = zipfile.ZipInfo(name, (2026, 11, 2, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, content)
        with zipfile.ZipFile(out) as z:
            if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
                raise ValueError('invalid ZIP')
            if any(hashlib.sha256(z.read(name)).hexdigest() != digest for name, digest in hashes.items()):
                raise ValueError('ZIP member hash mismatch')
    except Exception:
        if created and out.exists():
            out.unlink()
        raise
    return {'path': str(out), 'bytes': out.stat().st_size,
            'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'members': len(entries)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.out), indent=2))


if __name__ == '__main__':
    main()
