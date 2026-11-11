#!/usr/bin/env python3
"""Build the deterministic owner ZIP for a Polish reading edition.

The committed docs/reading/ directory holds the 14 `.md` files plus the compact
receipt summary.  The owner package additionally carries the full receipt.json
and the deterministic srwy_reading_PL.zip produced by build_reading_y.py.
Every member has a fixed timestamp and mode so the same inputs give the same
SHA-256.

Usage:
    python tools/build_reading_package.py \
      --docs docs/reading/pl-2026-10-27 \
      --receipt local/reading-research/final-edition/receipt.json \
      --reading-zip local/reading-research/final-edition/srwy_reading_PL.zip \
      --out build/SRW_Y_CZYTANKI_PL_2026-10-27.zip
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

STAMP = (2026, 10, 27, 0, 0, 0)
MODE = 0o100644 << 16


def package(docs: Path, receipt: Path, reading_zip: Path) -> bytes:
    members = sorted(p for p in docs.iterdir() if p.is_file())
    names = [p.name for p in members]
    if 'receipt-summary.json' not in names:
        raise ValueError('docs directory has no receipt-summary.json')
    if len([n for n in names if n.endswith('.md')]) != 14:
        raise ValueError('expected exactly 14 Polish .md files')
    if any(n in names for n in ('receipt.json', 'srwy_reading_PL.zip')):
        raise ValueError('private receipt/inner archive must not be in the docs directory')
    ordered = members + [receipt, reading_zip]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in ordered:
            name = path.name
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = MODE
            info.create_system = 3
            zf.writestr(info, path.read_bytes())
    return buffer.getvalue()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--docs', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--reading-zip', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(argv)
    data = package(args.docs, args.receipt, args.reading_zip)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(json.dumps({'name': args.out.name, 'bytes': len(data),
                      'sha256': hashlib.sha256(data).hexdigest(),
                      'members': len(list(args.docs.iterdir())) + 2}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
