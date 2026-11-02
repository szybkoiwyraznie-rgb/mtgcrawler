#!/usr/bin/env python3
"""Make a PRIVATE scratch set of configNN containers with experimental strings.

Research only: suffix-sharing pointers are outside the supported writer format.
Do not install, distribute, use on real saves or infer that other consumers are
safe. Supply explicit matching already-built configNN/imenuNN pairs. The
existing production config gate is NOT changed. All inputs remain untouched;
all resulting game data and reports must remain outside Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

import character_packing_research as PACK
import container_mix as CM
import member_variants as MV
import probe_character_packing_physical as CHECK


def build(pairs: list[tuple[Path, Path]], out: Path) -> dict:
    out = out.resolve()
    if out.exists():
        raise ValueError('output already exists')
    if not pairs:
        raise ValueError('at least one config/imenu pair is required')
    resolved = [(a.resolve(strict=True), b.resolve(strict=True)) for a, b in pairs]
    seen: set[str] = set()
    for config, imenu in resolved:
        a = re.fullmatch(r'config(\d\d)\.edat', config.name, re.I)
        b = re.fullmatch(r'imenu(\d\d)\.edat', imenu.name, re.I)
        if not a or not b or a[1] != b[1] or a[1] in seen:
            raise ValueError('pairs must have unique matching configNN.EDAT / imenuNN.EDAT names')
        if (out == config or out == imenu or out in config.parents or out in imenu.parents or
                config.parent == out or config.parent in out.parents or
                imenu.parent == out or imenu.parent in out.parents):
            raise ValueError('output must be separate from input directories')
        seen.add(a[1])

    # Validate every pair before publishing anything; the temporary files stay
    # private and are removed on error. The destination is a new directory.
    out.parent.mkdir(parents=True, exist_ok=True)
    reports = []
    with tempfile.TemporaryDirectory(prefix='.character-experiment-', dir=out.parent) as temp:
        stage = Path(temp) / 'result'
        stage.mkdir()
        for config, imenu in resolved:
            verified = CHECK.verify(config, imenu)
            _, left, _ = CM.members_of(config)
            _, right, _ = CM.members_of(imenu)
            name = verified['member']
            candidate, packing = PACK.prototype(left[name], right[name], name)
            generated, _ = MV.with_member(config, name, candidate)
            digest = hashlib.sha256(generated).hexdigest()
            if digest != verified['sha256_candidate'] or packing != verified['prototype']:
                raise ValueError('scratch candidate differs from validated candidate')
            target = stage / config.name
            target.write_bytes(generated)
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError('staged container readback differs')
            reports.append(verified)
        summary = {'experimental_only': True, 'runtime_safety_verified': False,
                   'config_gate_changed': False, 'pairs': len(reports), 'results': reports}
        (stage / 'report.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        # os.rename refuses an existing non-empty directory but may replace an
        # empty one. Check again; this is not a defence against hostile races.
        if out.exists():
            raise ValueError('output appeared during build')
        stage.rename(out)
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pair', action='append', nargs=2, required=True, type=Path,
                   metavar=('CONFIG', 'IMENU'))
    p.add_argument('--out', type=Path, required=True, help='new PRIVATE directory outside source inputs')
    a = p.parse_args()
    result = build([tuple(x) for x in a.pair], a.out)
    print(json.dumps({'pairs': result['pairs'], 'experimental_only': True,
                      'runtime_safety_verified': False}, indent=2))


if __name__ == '__main__':
    main()
