#!/usr/bin/env python3
"""Run the complete experimental UI-node probe over explicit chapter pairs.

This is a read-only research tool, NOT a production patch or whole-game test.
Requires unicorn==2.1.4, a private original ELF, a materialized PL package,
paired prebuilt config/imenu containers and the supplied charalist configs.
A caller must select and document the complete available inputs; no omitted
chapter is inferred or implicitly treated as covered.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import probe_character_ui_nodes_mips as PROBE


def run(elf: bytes, pairs: list[tuple[Path, Path]], configs: list[Path], rows: list[dict]) -> dict:
    if not pairs or not configs:
        raise ValueError('at least one pair and one charalist config are required')
    if (len({c.resolve() for c, _ in pairs}) != len(pairs) or
            len({m.resolve() for _, m in pairs}) != len(pairs)):
        raise ValueError('config or imenu reused in pairs')
    if len({p.resolve() for p in configs}) != len(configs):
        raise ValueError('duplicate charalist config')
    results = [PROBE.verify(elf, config, imenu, configs, rows) for config, imenu in pairs]
    members = [item['member'] for item in results]
    if len(set(members)) != len(members):
        raise ValueError('duplicate dictionary member')
    counts = ('records', 'ui_node_insertions', 'fallbacks', 'fallback_keys_not_found',
              'voice_overrides_checked')
    return {'pairs': len(results), 'charalist_configs_supplied': len(configs),
            'charalist_records': results[0]['charalist_records'],
            **{key: sum(item[key] for item in results) for key in counts},
            'null_character_paths_checked': sum(item['null_character_path_checked'] for item in results),
            'prototype_changed_records': sum(item['prototype']['changed_records'] for item in results),
            'results': results, 'render_and_full_game_tested': False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--pair', nargs=2, type=Path, action='append', required=True,
                   metavar=('CONFIG', 'IMENU'))
    p.add_argument('--charalist-config', type=Path, action='append', required=True)
    a = p.parse_args()
    rows = [json.loads(line) for line in
            (a.package / '09_executable.jsonl').read_text(encoding='utf-8').splitlines() if line]
    print(json.dumps(run(a.elf.read_bytes(), [tuple(pair) for pair in a.pair],
                         a.charalist_config, rows), indent=2))


if __name__ == '__main__':
    main()
