#!/usr/bin/env python3
"""Create a reusable hash-bound map of text bundles, names and game paths.

Input roots are the owner's already-collected files; no game binaries are written
into the index. DLC paths differ from the base Addressables directory.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import UnityPy
from pilot_master import decrypt
from restore_s6_full import bundle_metadata
from s6_tables import split_locale


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(base_roots: list[Path], dlc_root: Path, catalog: Path, dlc_catalogs: Path) -> dict:
    meta = bundle_metadata(catalog, dlc_catalogs)
    sources = []
    for root in base_roots:
        if not root.is_dir():
            raise ValueError(f'brak katalogu: {root}')
        sources.extend((p, f'aa/StandaloneWindows64/{p.name}') for p in sorted(root.glob('*.bundle')))
    if not dlc_root.is_dir():
        raise ValueError(f'brak katalogu: {dlc_root}')
    for p in sorted(dlc_root.rglob('*.bundle')):
        rel = p.relative_to(dlc_root)
        if len(rel.parts) != 2:
            raise ValueError(f'nieoczekiwana ścieżka DLC: {rel}')
        sources.append((p, rel.as_posix()))
    result = {}
    for path, rel in sources:
        raw = path.read_bytes()
        if rel in result:
            if result[rel]['sha256'] != sha(raw):
                raise ValueError(f'różne pliki dla {rel}')
            continue
        env = UnityPy.load(decrypt(path))
        entry = {'sha256': sha(raw), 'size': len(raw), 'tables': [], 'scenes': []}
        metadata = meta.get(path.name)
        for obj in env.objects:
            if obj.type.name == 'MonoBehaviour':
                try:
                    name = str(obj.read().m_Name)
                except Exception:
                    continue
                table, lang = split_locale(name)
                if table:
                    entry['tables'].append({'name': name, 'table': table,
                                            'lang': lang, 'path_id': obj.path_id})
            elif obj.type.name == 'TextAsset' and metadata:
                name = str(obj.read().m_Name)
                if name in metadata['assets']:
                    entry['scenes'].append({'name': name, 'lang': metadata['lang'],
                                            'path_id': obj.path_id,
                                            'patched_address': metadata['assets'][name]})
        if entry['tables'] or entry['scenes']:
            result[rel] = entry
    return {'schema': 1, 'scope': 'owner-srw-y-1.4.0-s6', 'bundles': dict(sorted(result.items()))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-roots', nargs='+', required=True, type=Path)
    parser.add_argument('--dlc-root', required=True, type=Path)
    parser.add_argument('--catalog', required=True, type=Path)
    parser.add_argument('--dlc-catalogs', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    index = build(args.base_roots, args.dlc_root, args.catalog, args.dlc_catalogs)
    args.output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{len(index['bundles'])} bundli w {args.output}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
