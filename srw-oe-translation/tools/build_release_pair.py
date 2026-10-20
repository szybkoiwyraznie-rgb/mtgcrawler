#!/usr/bin/env python3
"""Build and verify the current EN + partial PL patchers together, without game data."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parent.parent


def verify_pair(out,version):
    records={}
    for lang,name in [('en',f'srw-oe-translation-v{version}.zip'),('pl',f'srw-oe-translation-pl-v{version}.zip')]:
        path=out/name
        with zipfile.ZipFile(path)as z:
            if z.testzip()is not None or len(z.namelist())!=len(set(z.namelist())):
                raise ValueError('bad ZIP: '+name)
            manifest=json.loads(z.read('RELEASE_MANIFEST.json'))
            if (manifest['language']!=lang or manifest['version']!=version or
                manifest['validation']['errors'] or not manifest['validation']['filled']):
                raise ValueError('wrong/invalid active-language manifest: '+name)
            if set(manifest['sha256_by_file']) != set(z.namelist())-{'RELEASE_MANIFEST.json'}:
                raise ValueError('incomplete artifact manifest')
            for member,digest in manifest['sha256_by_file'].items():
                if hashlib.sha256(z.read(member)).hexdigest()!=digest:
                    raise ValueError('artifact member hash mismatch: '+member)
            if lang=='pl':
                if b'--lang pl'not in z.read('PATCH.bat')or b'--lang pl'not in z.read('CHECK_DLC.bat'):
                    raise ValueError('wrong PL launcher/checker')
                coverage=json.loads(z.read('translation/PL_COVERAGE.json'))
                if not coverage['partial']or coverage['totals']['errors']:
                    raise ValueError('invalid/missing partial PL coverage')
                (out/'PL_COVERAGE.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        records[lang]=dict(name=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return records


def build(out,version):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,80}',version):
        raise ValueError('unsafe release version')
    if out.exists()and any(out.iterdir()):
        raise ValueError('release output must be empty; refusing stale/mixed assets')
    out.mkdir(parents=True,exist_ok=True)
    for lang in ('en','pl'):
        subprocess.run([sys.executable,str(ROOT/'tools/build_distribution.py'),'--lang',lang,
                        '--version',version,'--out',str(out.resolve())],cwd=ROOT,check=True)
    records=verify_pair(out,version)
    (out/'SHA256SUMS.txt').write_text(''.join(f'{r["sha256"]}  {r["name"]}\n'for r in records.values()),encoding='ascii')
    (out/'RELEASE_PAIR.json').write_text(json.dumps(dict(version=version,artifacts=records,
        PL_partial=True,game_binaries_included=False),indent=2)+'\n',encoding='utf-8')
    return records


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--version',required=True)
    a=p.parse_args();print(json.dumps(build(a.out,a.version),indent=2))
