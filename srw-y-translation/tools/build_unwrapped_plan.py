#!/usr/bin/env python3
"""Create a source-verified plan without EN UI wrapping for layout comparison only."""
import argparse
import json
from pathlib import Path
import pl_import as pi


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--corrections', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    dest = a.output.resolve()
    if (dest in {a.manifest.resolve(), a.corrections.resolve()}
            or dest.is_relative_to(a.input.resolve())
            or dest.is_relative_to(a.source_dir.resolve())):
        raise pi.ImportFailure('wynik nie może nadpisać wejścia')
    load = lambda p: json.loads(p.read_text(encoding='utf-8'))
    original = pi.uses_en_wrap
    try:
        pi.uses_en_wrap = lambda row: False
        result = pi.import_batch(load(a.manifest), pi.read_returns(a.input),
                                 source_dir=a.source_dir, overrides=load(a.corrections))
    finally:
        pi.uses_en_wrap = original
    pi.atomic_write(a.output, result)
    print(f"Plan porównawczy bez łamania UI: {a.output}")

if __name__ == '__main__':
    main()
