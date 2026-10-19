#!/usr/bin/env python3
"""Reproduce and verify all four private Polish reading/reference deliverables."""
import argparse
import hashlib
import json
from pathlib import Path

import mech_catalog as M
import polish_mech_catalog as C
import polish_reading_script as R
import verify_polish_reading as V
from mech_catalog_sources import PACKAGE_FILES, need


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--english', required=True, type=Path, help='Current EN package (reading plans)')
    ap.add_argument('--catalogue-english', required=True, type=Path, help='Frozen catalogue EN package')
    ap.add_argument('--polish', required=True, type=Path, help='Materialized, accepted PL3 snapshot')
    ap.add_argument('--references', required=True, type=Path, help='Delivered EN Markdown directory')
    ap.add_argument('--configs', required=True, type=Path, help='Private original config00/configst/config01–19')
    ap.add_argument('--elf', required=True, type=Path, help='Private original Japanese 1.08 ELF')
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args(argv)
    project = Path(__file__).resolve().parent.parent
    docs = project / 'docs'
    inputs = {p.resolve() for p in (args.english, args.catalogue_english, args.polish, args.references, args.configs, docs)}
    need(all(not args.out.resolve().is_relative_to(p) for p in inputs), 'Refusing output among inputs')
    need(not args.elf.resolve().is_relative_to(args.out.resolve()), 'Refusing output around original ELF')
    args.out.mkdir(parents=True, exist_ok=True)
    verification = {}
    for episode in (1, 2, 3):
        plan = json.loads((docs / f'reading-script/polish/episode_{episode:02}.json').read_bytes())
        en, pl = R.EarlyReadingSource(args.english, episode), R.EarlyReadingSource(args.polish, episode, 'pl')
        reference = (args.references / f'srwoe_episode_{episode:02}.md').read_bytes()
        text, audit = R.build(plan, en, pl, reference)
        path = args.out / f'srwoe_episode_{episode:02}_PL.md'
        path.write_text(text, encoding='utf-8')
        verification[f'episode_{episode:02}'] = V.verify_episode(path.read_text(encoding='utf-8'), audit, pl)
        (args.out / f'episode_{episode:02}_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    source = M.collect(args.configs, args.catalogue_english)
    inventory = json.loads((docs / 'mech-catalog/source-inventory.json').read_bytes())
    need(source['inputs'] == inventory['inputs'] and source['summary']['package_sha256'] ==
         inventory['summary']['package_sha256'], 'Original catalogue input snapshot changed')
    model = M.build_model(source, args.catalogue_english, args.elf.read_bytes(),
                          json.loads((docs / 'mech-catalog/engine-map.json').read_bytes()),
                          json.loads((docs / 'mech-catalog/description-errata.json').read_bytes()))
    reference = (args.references / 'srwoe_mech_catalog_v3.md').read_bytes()
    expected_sha = json.loads((docs / 'mech-catalog/presentation-v3.json').read_bytes())['output_sha256']
    need(R.sha(reference) == expected_sha and M.render(model)[0].encode() == reference,
         'English catalogue v3 was not reproduced byte-for-byte')
    polish = C.localize(model, source, args.catalogue_english, args.polish)
    path = args.out / 'srwoe_mech_catalog_v3_PL.md'
    path.write_text(C.render(polish), encoding='utf-8')
    verification['catalogue'] = V.verify_catalogue(path.read_text(encoding='utf-8'), model, polish)
    need(path.read_text(encoding='utf-8') == C.render(polish), 'Catalogue output readback differs')
    # Full source/model evidence stays private; public receipts contain counts/hashes.
    (args.out / 'catalogue_models.json').write_text(json.dumps({'en': model, 'pl': polish}, ensure_ascii=False) + '\n')
    report = {'schema': 1, 'language': 'pl', 'text_source': 'PL3', 'game_package_changed': False,
              'english_catalogue_v3_reproduced_sha256': expected_sha,
              'polish_package_sha256': {f: R.sha((args.polish / f).read_bytes()) for f in set(PACKAGE_FILES) | set(R.SOURCE_FILES)},
              'outputs': {p.name: {'bytes': p.stat().st_size, 'sha256': R.sha(p.read_bytes())}
                          for p in sorted(args.out.glob('*_PL.md'))}, 'verification': verification}
    (args.out / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
