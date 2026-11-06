#!/usr/bin/env python3
"""Compare a private ISO9660 image with a private unpacked directory tree.

Read-only: compare the exact case-sensitive set of regular file paths and each
file's SHA-256. Does not compare metadata, UMD system-area bytes, empty
folders, ISO ordering, executable behaviour or media outside the given tree.
Symlinks inside the input tree are refused. The report may contain private filenames; do not
commit reports containing game assets to version control.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import iso9660

CHUNK = 1024 * 1024


def _source_files(root: Path) -> dict[str, Path]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('tree must be a directory')
    result: dict[str, Path] = {}
    def scan(directory: Path) -> None:
        for item in sorted(directory.iterdir()):
            if item.is_symlink():
                raise ValueError(f'symlink is not allowed: {item.relative_to(root)}')
            if item.is_dir():
                scan(item)
            elif item.is_file():
                result[item.relative_to(root).as_posix()] = item
            else:
                raise ValueError(f'non-regular file is not allowed: {item.relative_to(root)}')
    scan(root)
    return result


def verify(image: Path, root: Path) -> dict:
    files = _source_files(root)
    inventory = iso9660.inspect_iso9660(image)
    if inventory['warnings']:
        raise ValueError('ISO inventory has warnings; inspect before comparison')
    entries = inventory['files']
    paths = [item['path'] for item in entries]
    if len(set(paths)) != len(paths):
        raise ValueError('duplicate ISO paths')
    iso_paths = set(paths)
    only_tree = sorted(set(files) - iso_paths)
    only_iso = sorted(iso_paths - set(files))
    mismatched: list[str] = []
    compared = 0
    with image.open('rb') as iso:
        for item in entries:
            name = item['path']
            if name not in files:
                continue
            source = files[name]
            if source.stat().st_size != item['size_bytes']:
                mismatched.append(name)
                continue
            h1, h2 = hashlib.sha256(), hashlib.sha256()
            with source.open('rb') as stream:
                while part := stream.read(CHUNK):
                    h1.update(part)
            for extent in item['extents']:
                remaining = extent['length_bytes']
                iso.seek(extent['offset_bytes'])
                while remaining:
                    part = iso.read(min(CHUNK, remaining))
                    if not part:
                        raise ValueError(f'truncated extent: {name}')
                    h2.update(part)
                    remaining -= len(part)
            compared += 1
            if h1.digest() != h2.digest():
                mismatched.append(name)
    return {'matches': not (only_tree or only_iso or mismatched),
            'iso_files': len(entries), 'tree_files': len(files), 'hashes_compared': compared,
            'only_in_tree': only_tree, 'only_in_iso': only_iso, 'mismatched': mismatched,
            'checks_gameplay': False, 'checks_system_area_or_metadata': False}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso', type=Path, required=True)
    p.add_argument('--tree', type=Path, required=True)
    args = p.parse_args()
    result = verify(args.iso, args.tree)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['matches'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
