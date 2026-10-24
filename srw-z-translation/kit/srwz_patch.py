#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SRW Z PL font TEST patcher (P3). Patches a COPY of the owner's
SLPS-25887 ISO: half-width renderer+font hooks with Polish glyphs in
the ELF, one Polish pangram dialogue in STAGE.BIN. Never writes to
the input image. Aborts unless the source extents hash to the exact
values this test was built against.

Run via PATCH_TEST.bat (or: python srwz_patch.py [path-to-iso]).
Kit layout (relative to this file): tools/, vendor/retro-trans/tools/,
atlas_pl.bin.
"""
import hashlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

KIT = os.path.dirname(os.path.abspath(__file__))
VTOOLS = os.path.join(KIT, 'vendor', 'retro-trans', 'tools')
TOOLS = os.path.join(KIT, 'tools')
ATLAS = os.path.join(KIT, 'atlas_pl.bin')
LOG = os.path.join(KIT, 'srwz_patch_log.txt')

SECTOR = 2048
ELF_LBA, ELF_SIZE = 455, 3471624
STAGE_LBA, STAGE_SIZE = 1651029, 3910128
ELF_SHA256 = '6c4c81c4e5aa3db1f52d70b8183ce11c01fc6b265ae4d53fa4d6a657c5019b50'
STAGE_SHA256 = '9c56d42f96df7b409ccf468b24412322ed627b9cbbd656864818a404d89240dc'
ELF_PL_SHA256 = '7bfc9a205a888a461abe6d9c96b16d276d5357011db757e100a71f6c1323b7ba'
STAGE_SAMPLE_SHA256 = 'c1ca930ef044c07a2b92134fa1b134552357c3041a9d9c1cb7182962e169cc63'

PL = list('ĄĆĘŁŃÓŚŹŻąćęłńóśźż')
RESERVED = ['@', '#', '&', '*', '+', '<', '=', '>', '[', '\\', ']',
            '^', '_', '`', '{', '|', '}', '~']
ENC = dict(zip(PL, RESERVED))
SAMPLE_REC, SAMPLE_OFF = 0, 129008
SAMPLE_BODY = ['Zażółć gęślą jaźń!', 'ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż']

_logf = open(LOG, 'w', encoding='utf-8')


def log(msg=''):
    print(msg)
    _logf.write(str(msg) + '\n')
    _logf.flush()


def extent_sha256(path, lba, size):
    with open(path, 'rb') as f:
        f.seek(lba * SECTOR)
        return hashlib.sha256(f.read(size)).hexdigest()


def run(cmd):
    log('+ ' + ' '.join(os.path.basename(c) if c.endswith('.py') else c for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    for line in (r.stdout or '').splitlines():
        log('  ' + line)
    if r.returncode != 0:
        log('STDERR:\n' + (r.stderr or ''))
        raise SystemExit('FAILED: %s (see log)' % cmd[1])
    return r.stdout or ''


def pick_iso():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args:
        return os.path.abspath(args[0])
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw()
        p = filedialog.askopenfilename(
            title='Wybierz ISO SRW Z (SLPS-25887)',
            filetypes=[('Obrazy dysku', '*.iso *.bin *.chd'), ('Wszystkie', '*.*')])
        root.destroy()
        return p
    except Exception:
        return input('Sciezka do ISO SRW Z: ').strip().strip('"')


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    no_copy = '--no-copy' in sys.argv   # developer sandbox test only
    iso = pick_iso()
    if not iso or not os.path.isfile(iso):
        raise SystemExit('Brak pliku ISO.')
    log('SRW Z PL font TEST patcher (P3)')
    log('input : %s (%d B)' % (iso, os.path.getsize(iso)))

    log('verify source extents...')
    e = extent_sha256(iso, ELF_LBA, ELF_SIZE)
    s = extent_sha256(iso, STAGE_LBA, STAGE_SIZE)
    log('  ELF    sha256 %s' % e)
    log('  STAGE  sha256 %s' % s)
    if e != ELF_SHA256 or s != STAGE_SHA256:
        raise SystemExit('STOP: obraz nie pasuje do oczekiwanej edycji '
                         'SLPS-25887 (hash extentow inny niz testowy). '
                         'Przeslij log: ' + LOG)

    if no_copy:
        out = iso
        log('!! --no-copy (test sandbox): patching the given file directly')
    else:
        base, ext = os.path.splitext(iso)
        out = base + '_PLTEST' + ext
        log('copy  -> %s (oryginal nietkniety)' % out)
        shutil.copyfile(iso, out)

    tmp = tempfile.mkdtemp(prefix='srwz_')
    elf = os.path.join(tmp, 'elf.bin')
    elf_r = os.path.join(tmp, 'elf_r.bin')
    elf_pl = os.path.join(tmp, 'elf_pl.bin')
    with open(out, 'rb') as f:
        f.seek(ELF_LBA * SECTOR)
        open(elf, 'wb').write(f.read(ELF_SIZE))
    run([sys.executable, os.path.join(VTOOLS, 'patch_renderer.py'), elf, elf_r])
    run([sys.executable, os.path.join(TOOLS, 'patch_hwfont_pl.py'), elf_r, elf_pl, ATLAS])
    assert os.path.getsize(elf_pl) == ELF_SIZE
    with open(out, 'r+b') as f:
        f.seek(ELF_LBA * SECTOR)
        f.write(open(elf_pl, 'rb').read())
    log('ELF patched extent sha256: %s (expected %s)'
        % (extent_sha256(out, ELF_LBA, ELF_SIZE), ELF_PL_SHA256))

    script = os.path.join(tmp, 'script.json')
    run([sys.executable, os.path.join(VTOOLS, 'extract_script.py'), out, script])
    doc = json.load(io.open(script, encoding='utf-8'))
    hit = None
    for r in doc['rows']:
        if r['rec'] == SAMPLE_REC and r['off'] == SAMPLE_OFF:
            speaker = r['text'].split('\n')[0]
            enc = lambda s: ''.join(ENC.get(c, c) for c in s)
            r['text'] = (speaker + '\n「' + enc(SAMPLE_BODY[0]) + '\n'
                         + enc(SAMPLE_BODY[1]) + '」')
            hit = r
            break
    if hit is None:
        raise SystemExit('STOP: nie znaleziono wiersza probki rec=%d off=%d'
                         % (SAMPLE_REC, SAMPLE_OFF))
    log('sample row set (speaker kept from your copy):\n' + hit['text'])
    json.dump(doc, io.open(script, 'w', encoding='utf-8'), ensure_ascii=False)
    run([sys.executable, os.path.join(VTOOLS, 'apply_script.py'), out, script, '--write'])
    v = run([sys.executable, os.path.join(VTOOLS, 'verify_pointers.py'), out, '--min', '85'])
    log('STAGE patched extent sha256: %s (sandbox reference %s)'
        % (extent_sha256(out, STAGE_LBA, STAGE_SIZE), STAGE_SAMPLE_SHA256))
    log('')
    log('GOTOWE: %s' % out)
    log('Uruchom ten obraz w PCSX2: nowa gra -> pierwsza scena dialogowa;')
    log('kwestia Henkena zawiera polski pangram. Zrob screeny okna dialogu')
    log('i przeslij je razem z tym logiem: %s' % LOG)


if __name__ == '__main__':
    main()
