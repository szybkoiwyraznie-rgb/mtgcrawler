#!/usr/bin/env python3
"""Compare a return with a saved, checksummed translator template, without S6.

Only PL values may differ. A successful comparison does NOT validate translation
content, target bindings, original game data, layout or runtime behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

from pl_import import SLOT, ImportFailure, canonical, read_returns

DEFAULT_TEMPLATE = Path(__file__).resolve().parents[1] / 'translations' / 'template-v8'
SHA_LINE = re.compile(r'^([0-9a-f]{64})  (.+)$')


def load_template(root: Path) -> dict[str, str]:
    lines = (root / 'SHA256SUMS').read_text(encoding='utf-8').splitlines()
    expected = {}
    for line in lines:
        match = SHA_LINE.fullmatch(line)
        if not match:
            raise ImportFailure('nieprawidłowy SHA256SUMS')
        sha, name = match.groups()
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or name in expected or not name.endswith('.md'):
            raise ImportFailure('nieprawidłowa lub powtórzona ścieżka wzorca')
        expected[name] = sha
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*.md') if p.is_file()}
    if not expected or actual != set(expected):
        raise ImportFailure('brak lub nadmiar plików wzorca')
    files = {}
    for name, sha in sorted(expected.items()):
        path = root / name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root.parent):
            raise ImportFailure(f'{name}: dowiązania we wzorcu są niedozwolone')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != sha:
            raise ImportFailure(f'{name}: błędna suma wzorca')
        if PurePosixPath(name).parts[0] not in ('sceny', 'widoki'):
            continue
        basename = path.name
        if basename in files:
            raise ImportFailure(f'{basename}: zduplikowana nazwa wzorca')
        files[basename] = canonical(data.decode('utf-8-sig'))
    return files


def compare(template: dict[str, str], returned: dict[str, str]) -> dict:
    problems = []
    for name, text in sorted(returned.items()):
        if name not in template:
            problems.append({'file': name, 'error': 'brak we wzorcu'})
        elif SLOT.sub('   PL:', canonical(text)) != template[name]:
            problems.append({'file': name, 'error': 'zmieniona struktura lub tekst poza PL'})
    return {'kind': 'template_comparison_only', 'bindings_verified': False,
            'files_checked': len(returned), 'problems': problems}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Plik .md, katalog lub płaski ZIP .md')
    parser.add_argument('--template', type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args(argv)
    try:
        result = compare(load_template(args.template), read_returns(args.input))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f'Nie można porównać: {exc}')
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['problems'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
