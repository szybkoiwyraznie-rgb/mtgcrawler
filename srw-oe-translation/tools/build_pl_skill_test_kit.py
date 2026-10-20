#!/usr/bin/env python3
"""Package intact returned PL skills as a private, game-binary-free A/B test kit."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
import sys

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))
import build_distribution
import pl_skill_size_test as T

ROOT=HERE.parent


def build(package,out,engine_map=ROOT/'docs/mech-catalog/engine-map.json'):
    mapping=json.loads(engine_map.read_text())
    offsets={r['file_offset'] for r in mapping['selections'] if r.get('pointer')}
    if len(offsets)!=20:
        raise ValueError('unreviewed executable override map')
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        raise ValueError('refusing to overwrite a delivered kit')
    with tempfile.TemporaryDirectory() as tmp:
        target=Path(tmp)/'translation'
        counts=T.select_package(package,target,offsets)
        snapshot={'kind':T.ACK,'source':'intact PL.zip partial return reviewed 2026-10-18',
                  'source_return_sha256':'f26a97af0c2b7bd5d8d73e24cb84835509983c0a5d04d4844e922a887b8a538b',
                  'filled_selected':counts,'exe_override_offsets':sorted(offsets),
                  'no_shrinking_or_fragment_repairs':True,
                  'package_sha256':{p.name:T.file_sha(p) for p in target.iterdir()}}
        (target/'SKILL_TEST_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
        deps=build_distribution._resolve(HERE,('pl_skill_size_test','pick_path'))
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            for stem in sorted(deps):
                z.write(HERE/f'{stem}.py',f'tools/{stem}.py')
            z.write(ROOT/'TEST_UMIEJETNOSCI_PL.bat','TEST_UMIEJETNOSCI_PL.bat')
            z.write(ROOT/'README_TEST_UMIEJETNOSCI_PL.md','CZYTAJ.md')
            for path in sorted(target.iterdir()):
                z.write(path,'translation/'+path.name)
            z.writestr('KIT_VERSION.txt','PL_SKILLS_FULL_AB_v1 / 2026-10-18 / experimental only\n')
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None or len(z.namelist())!=len(set(z.namelist())):
            raise ValueError('ZIP verification failed')
        forbidden={'.iso','.cpk','.bin','.edat','.pbp','.dat','.png','.jpg','.fta'}
        if any(Path(n).suffix.lower() in forbidden for n in z.namelist()):
            raise ValueError('proprietary game file in kit')
        files=len(z.namelist())
    return {'name':out.name,'bytes':out.stat().st_size,'sha256':T.file_sha(out),
            'md5':hashlib.md5(out.read_bytes()).hexdigest(),'files':files,'snapshot':snapshot,
            'scope':'tools + translator text only; no game binaries; builds A/B on user ISO',
            'runtime_tested':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.package,a.out),ensure_ascii=False,indent=2))
