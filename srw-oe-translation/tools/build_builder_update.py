#!/usr/bin/env python3
"""Build a shared EN/PL tools-only update; never replace user's translation/ or launchers."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))
import build_distribution
import build_translation_patch as B


def build(out):
    deps=build_distribution._resolve(HERE,('build_translation_patch',))
    hashes={f'tools/{stem}.py':hashlib.sha256((HERE/f'{stem}.py').read_bytes()).hexdigest() for stem in sorted(deps)}
    manifest={'kind':'shared EN/PL tools-only Character19 update','tools_stamp':B.TOOLS_STAMP,
              'languages':['en','pl'],'translation_files_included':False,'launchers_replaced':False,
              'game_binaries_included':False,'sha256_by_file':hashes}
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED)as z:
        for name in hashes:
            z.write(HERE/(Path(name).name),name)
        z.write(HERE.parent/'README_BUILDER_UPDATE.md','README_BUILDER_UPDATE.md')
        z.writestr('BUILDER_TOOLS.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(out)as z:
        if z.testzip() is not None or len(z.namelist())!=len(set(z.namelist())):
            raise ValueError('bad ZIP')
        for name in hashes:
            compile(z.read(name),name,'exec')
    return {'name':out.name,'bytes':out.stat().st_size,'files':len(hashes)+2,
            'md5':hashlib.md5(out.read_bytes()).hexdigest(),
            'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'tools_stamp':B.TOOLS_STAMP,
            'translation_files_included':False,'launchers_replaced':False,'game_binaries_included':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.out),indent=2))
