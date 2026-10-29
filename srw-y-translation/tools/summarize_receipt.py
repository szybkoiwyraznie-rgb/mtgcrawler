#!/usr/bin/env python3
"""Publish a compact, deterministic receipt summary next to the reading files.

The full `receipt.json` carries every missing address (several MB) and stays in
the private build directory / owner zip. The committed summary keeps verifiable
hashes, counts and the new encyclopedia/graph measurements, but omits the long
lists so `docs/reading/` stays reviewable.

Usage:
    python tools/summarize_receipt.py \
      --receipt local/reading-research/final-edition/receipt.json \
      --out docs/reading/pl-2026-10-27/receipt-summary.json
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))
from pl_import import atomic_write  # noqa: E402

KEEP = ('schema', 'runtime_tested', 'polish_only', 'translated_scenes_only', 'source_sha256',
        'index_sha256', 'dictionary_evidence_sha256', 'dictionary_links_sha256',
        'graph_evidence_sha256', 'preset_evidence_sha256',
        'final_preset_evidence_sha256',
        'dictionary_stats', 'plan_sha256',
        'source_rows', 'translated_rows_in_plans', 'rendered_unique_addresses',
        'index_stats', 'ordering', 'files', 'zip_sha256',
        'encyclopedia_links', 'script_graphs', 'preset_resolution',
        'final_preset_resolution')


def summarize(receipt: dict, note: str | None = None) -> dict:
    result = {key: receipt[key] for key in KEEP if key in receipt}
    result['counts'] = {
        'scene_rows_without_japanese_source': len(receipt['scene_rows_without_japanese_source']),
        'untranslated_or_unlinked': len(receipt['untranslated_or_unlinked']),
        'unused_translations': len(receipt['unused_translations']),
        'verified_script_order': len(receipt['verified_script_order']),
        'event_registries': len(receipt['event_registries']),
        'mission_protagonists': len(receipt['mission_protagonists']),
        'structural_issues': len(receipt['structural_issues']),
    }
    result['note'] = note or (
        'Wydanie wylacznie polskie: braki sa jawnymi znacznikami [BRAK PL]. '
        'Pelną wersję receipt.json i deterministyczny srwy_reading_PL.zip '
        'zawiera paczka na Drive.')
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--note', default=None)
    args = p.parse_args(argv)
    receipt = json.loads(args.receipt.read_text(encoding='utf-8'))
    atomic_write(args.out, summarize(receipt, args.note))
    print(json.dumps({'schema': receipt['schema'],
                      'files': len(receipt['files'])}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
