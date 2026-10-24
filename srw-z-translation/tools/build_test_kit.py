#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble the owner-side P3 font test kit (zip) in local/dist/.

Mirrors the layout srwz_patch.py expects:
  PATCH_TEST.bat, srwz_patch.py, README_TEST_PL.txt, atlas_pl.bin
  tools/patch_hwfont_pl.py
  vendor/retro-trans/{LICENSE,PROVENANCE.md,tools/<subset>}
The atlas is copied from local/work/font/atlas_pl.bin and hash-pinned:
regenerating the font without updating the expected hashes in
kit/srwz_patch.py must fail loudly here, not on the owner's PC.
"""
import hashlib
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'local' / 'dist' / 'srwz-pl-font-test-p3'
ZIP = ROOT / 'local' / 'dist' / 'srwz-pl-font-test-p3.zip'
ATLAS = ROOT / 'local' / 'work' / 'font' / 'atlas_pl.bin'
ATLAS_SHA256 = '38ec24bd41ca23e5d6c0d8a2f62279c415ca089abe0c45954624d23c25644202'
VENDOR_SUBSET = ['extract_script.py', 'apply_script.py', 'verify_pointers.py',
                 'banlz.py', 'rewrap_dialogue.py', 'patch_renderer.py',
                 'patch_hwfont.py']


def main():
    assert ATLAS.is_file(), 'run tools/gen_pl_atlas.py first'
    got = hashlib.sha256(ATLAS.read_bytes()).hexdigest()
    assert got == ATLAS_SHA256, 'atlas drift: %s != pinned %s' % (got, ATLAS_SHA256)

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / 'tools').mkdir(parents=True)
    (DIST / 'vendor' / 'retro-trans' / 'tools').mkdir(parents=True)

    for name in ['PATCH_TEST.bat', 'srwz_patch.py', 'README_TEST_PL.txt']:
        shutil.copy2(ROOT / 'kit' / name, DIST / name)
    shutil.copy2(ROOT / 'tools' / 'patch_hwfont_pl.py',
                 DIST / 'tools' / 'patch_hwfont_pl.py')
    for name in VENDOR_SUBSET:
        shutil.copy2(ROOT / 'vendor' / 'retro-trans' / 'tools' / name,
                     DIST / 'vendor' / 'retro-trans' / 'tools' / name)
    for name in ['LICENSE', 'PROVENANCE.md']:
        shutil.copy2(ROOT / 'vendor' / 'retro-trans' / name,
                     DIST / 'vendor' / 'retro-trans' / name)
    shutil.copy2(ATLAS, DIST / 'atlas_pl.bin')

    if ZIP.exists():
        ZIP.unlink()
    members = []
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DIST.rglob('*')):
            if p.is_file():
                arc = p.relative_to(DIST.parent)
                z.write(p, arc)
                members.append(str(arc))
    print('kit: %s' % ZIP)
    print('  %d members, %d B, sha256 %s'
          % (len(members), ZIP.stat().st_size,
             hashlib.sha256(ZIP.read_bytes()).hexdigest()))
    for m in members:
        print('   ', m)


if __name__ == '__main__':
    main()
