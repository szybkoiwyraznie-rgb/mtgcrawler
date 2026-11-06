#!/usr/bin/env python3
"""Build the optional Alan follow-up ZIP from repository inputs; no game files."""
from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
import build_distribution as DIST
import pl_release_package as RELEASE

ROOT = Path(__file__).resolve().parent.parent


def build(out: Path):
    if out.exists():
        raise ValueError('refusing to overwrite an existing output')
    tools = ROOT / 'tools'
    with tempfile.TemporaryDirectory(prefix='oe-alan-release-') as temp:
        package = Path(temp) / 'translation'
        coverage = RELEASE.materialize(ROOT / 'pakiet_EN', ROOT / 'pakiet_PL', package)
        if coverage['totals']['errors']:
            raise ValueError('invalid PL snapshot')
        entries = {
            'TEST_ALAN.bat': (tools / 'alan_test_kit/TEST_ALAN.bat').read_bytes().replace(b'\n', b'\r\n'),
            'CZYTAJ_TO.txt': (tools / 'alan_test_kit/CZYTAJ_TO.txt').read_bytes(),
            'translation/07_names_characters.jsonl': (package / '07_names_characters.jsonl').read_bytes(),
        }
        for name in sorted(DIST._resolve(tools, ('alan_viewer_experiment',))):
            path = tools / (name + '.py')
            if not path.is_file():
                raise ValueError('missing dependency: ' + name)
            entries['tools/' + path.name] = path.read_bytes()
        hashes = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(entries.items())}
        entries['EXPERIMENT_MANIFEST.json'] = (json.dumps({'experimental': True, 'runtime_tested': False,
            'scope': 'Alan Igor in config01, only slots 4, 5, 11; previous four unchanged',
            'game_binaries_included': False, 'sha256_by_file': hashes}, indent=2) + '\n').encode('utf-8')
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name, content in sorted(entries.items()):
                info = zipfile.ZipInfo(name, (2026, 11, 2, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, content)
        with zipfile.ZipFile(out) as z:
            if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
                raise ValueError('invalid ZIP')
            if any(hashlib.sha256(z.read(name)).hexdigest() != digest for name, digest in hashes.items()):
                raise ValueError('ZIP member hash mismatch')
        return {'path': str(out), 'bytes': out.stat().st_size,
                'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'members': len(entries)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(build(a.out), indent=2))


if __name__ == '__main__':
    main()
