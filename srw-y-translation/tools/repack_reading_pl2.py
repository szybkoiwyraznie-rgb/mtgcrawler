#!/usr/bin/env python3
"""Repack the PL2 reading edition from the Markdown in this repository.

`tools/build_reading_pl2.py` builds the edition from the private S6 corpus, which is
not in the repository. When the only change is in the Markdown (layout repairs from
`tools/fix_reading_pl2_layout.py`), the archive can be rebuilt from the committed
files alone — same three members, same fixed entry time, so the ZIP is reproducible.

    python tools/repack_reading_pl2.py --version v13 \
        --output docs/reading/pl2-oe-format/SRW_Y_CZYTANKI_PL2_POPRAWIONE_v13.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
EDITION = HERE / 'docs' / 'reading' / 'pl2-oe-format'
MEMBERS = ('README.md', 'srwy_mission_deployments.md', 'srwy_scenariusz_PL.md')


def build(output: Path, edition: Path = EDITION) -> dict:
    import sys
    sys.path.insert(0, str(HERE / 'tools'))
    from build_reading_y import archive_bytes

    files = {name: (edition / name).read_text(encoding='utf8') for name in MEMBERS}
    archive = archive_bytes(files)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive)
    return {'zip': str(output), 'bytes': len(archive),
            'sha256': hashlib.sha256(archive).hexdigest(),
            'members': {name: len(text.encode('utf8')) for name, text in files.items()}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--version', default='v13')
    parser.add_argument('--edition', type=Path, default=EDITION)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    output = args.output or (args.edition / f'SRW_Y_CZYTANKI_PL2_POPRAWIONE_{args.version}.zip')
    print(json.dumps(build(output, args.edition), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
