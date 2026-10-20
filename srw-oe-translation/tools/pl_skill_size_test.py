#!/usr/bin/env python3
"""EXPERIMENT ONLY: intact returned PL skills and equal-size Japanese control.

The normal builder/limits are unchanged. This entry point requires explicit unsafe-test
acknowledgement and removes only the Skill00 size guard inside a finally-restored scope.
No language edits, fragment repairs, shrink rules, DLC changes or invented probe texts.
"""
from contextlib import contextmanager
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_translation_patch as B
import exe_strings as E
import iso_pack
import item_skill_records as R
import item_skill_write as W
import member_variants as M
import pl_glyph_compose
import font_pl
import text_codec
import verify_pl_test as V

MEMBER = 'srwDL_Skill00.bin'
CONFIG = 'psp_game/usrdir/config00.cpk'
FONT = 'psp_game/usrdir/font.cpk'
EXE = 'psp_game/sysdir/eboot.bin'
ACK = 'EXPERIMENT_UNSHORTENED_PL_SKILLS'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


@contextmanager
def experimental_budget():
    """Only this isolated process/scope; restore even when a writer raises."""
    saved = W.MEMBER_SIZE_LIMITS.copy()
    try:
        W.MEMBER_SIZE_LIMITS.pop(MEMBER, None)
        yield
    finally:
        W.MEMBER_SIZE_LIMITS.clear()
        W.MEMBER_SIZE_LIMITS.update(saved)


def grow_control(original, size):
    """Native Japanese control must not run through the PL-reserved-katakana codec."""
    previous = text_codec.lang()
    try:
        text_codec.set_lang('en')
        return M.grow_with_spaces(original, 'skill', MEMBER, size)
    finally:
        text_codec.set_lang(previous)


def select_package(source, target, override_offsets):
    """Keep PL verbatim only for Skill00 and its 20 executable base overrides."""
    target.mkdir(parents=True, exist_ok=False)
    counts = {}
    for path in sorted(source.iterdir()):
        if path.suffix == '.tsv':
            shutil.copyfile(path, target / path.name)
        elif path.suffix == '.jsonl':
            result = []
            filled = 0
            for line in path.read_text(encoding='utf-8').splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                src = row.get('source') or {}
                selected = (src.get('container') == 'config00.cpk' and src.get('member') == MEMBER
                            or path.name == '09_executable.jsonl' and src.get('offset') in override_offsets)
                if not selected:
                    row['pl'] = ''
                filled += bool(row.get('pl'))
                result.append(json.dumps(row, ensure_ascii=False))
            (target / path.name).write_text('\n'.join(result)+'\n', encoding='utf-8')
            counts[path.name] = filled
    selected_exe = [r for r in B.load_rows(target, 'pl') if B.owner(r) == 'exe' and B.filled(r)]
    if {r['source']['offset'] for r in selected_exe} != set(override_offsets):
        raise ValueError('missing returned PL for executable skill overrides')
    return counts


def skill_member(config):
    members = V.event_members(config, nested=True)
    names = [n for n in members if n.rsplit('/', 1)[-1] == MEMBER]
    if len(names) != 1:
        raise ValueError('expected exactly one Skill00 member')
    return members[names[0]], members


def verify_records(original, actual, package):
    before = R.parse_member(original, 'skill', MEMBER)
    after = R.parse_member(actual, 'skill', MEMBER)
    checked = M.check(actual, 'skill', MEMBER, original)
    for a, b in zip(before['records'], after['records']):
        # Preserve key/level/argument indices plus counted list and numeric parameters.
        if original[a['offset']:a['offset']+32] != actual[b['offset']:b['offset']+32]:
            raise ValueError('record header/selectors changed')
        if original[a['offset']+a['boundaries'][-1]:a['offset']+a['length']] != actual[b['offset']+b['boundaries'][-1]:b['offset']+b['length']]:
            raise ValueError('numeric parameter tail changed')
    rows = B.load_rows(package, 'pl')
    checked_fields = 0
    for row in rows:
        if row.get('__file') != '03_skills.jsonl' or not B.filled(row):
            continue
        record = after['records'][row['record']]
        if B.identity(row):
            source_record = before['records'][row['record']]
            expected = W.field_raw(original, source_record, row['part'])
        else:
            expected = text_codec.encode(row['en'])
        if W.field_raw(actual, record, row['part']) != expected:
            raise ValueError('returned PL record did not read back exactly: '+row['id'])
        checked_fields += 1
    mapped = [r for r in rows if B.filled(r) and not B.identity(r)]
    pool_edits, refused, _ = W.plan_pool_edits(mapped, MEMBER, before, original, 'config00.cpk')
    if refused:
        raise ValueError('pool planner refused')
    _, old_pool = R.parse_tail_pool(original, before['tail_offset'])
    _, new_pool = R.parse_tail_pool(actual, after['tail_offset'])
    expected_pool = old_pool[:]
    for index, value in pool_edits.items():
        expected_pool[index] = value
    if new_pool != expected_pool:
        raise ValueError('translated pool differs or was shortened')
    return {**checked, 'returned_record_fields_read_back': checked_fields,
            'translated_pool_entries_read_back': len(pool_edits), 'numeric_tails_preserved': True}


def verify_iso_scope(original, patched, allowed):
    """Hash every logical ISO file; only explicitly allowed paths may differ."""
    with original.open('rb') as f:
        left = iso_pack._walk_record_offsets(f)
    with patched.open('rb') as f:
        right = iso_pack._walk_record_offsets(f)
    left = {k: v for k, v in left.items() if not v[3]}
    right = {k: v for k, v in right.items() if not v[3]}
    if left.keys() != right.keys():
        raise ValueError('ISO file set changed')
    changed = []
    with original.open('rb') as a, patched.open('rb') as b:
        for key, (_, lba, size, _) in left.items():
            _, other_lba, other_size, _ = right[key]
            a.seek(lba * 2048); b.seek(other_lba * 2048)
            if size != other_size:
                equal = False
            else:
                equal = True
                remaining = size
                while remaining:
                    chunk = min(1024*1024, remaining)
                    if a.read(chunk) != b.read(chunk):
                        equal = False
                        break
                    remaining -= chunk
            if not equal:
                path = key.split(';', 1)[0].strip('/').lower()
                if path not in allowed:
                    raise ValueError('unexpected changed ISO file: '+path)
                changed.append(path)
    if set(changed) != set(allowed):
        raise ValueError('expected ISO change missing')
    return {'files_checked': len(left), 'changed': sorted(changed)}


def build(iso, package, out, acknowledgement):
    if acknowledgement != ACK:
        raise ValueError('explicit experimental acknowledgement required')
    if out.exists() and any(out.iterdir()):
        raise ValueError('output must be new/empty; original ISO and old tests must not be overwritten')
    snapshot = json.loads((package/'SKILL_TEST_SNAPSHOT.json').read_text(encoding='utf-8'))
    if snapshot.get('kind') != ACK:
        raise ValueError('wrong experimental package')
    for name, digest in snapshot['package_sha256'].items():
        if Path(name).name != name or file_sha(package/name) != digest:
            raise ValueError('test package changed: '+name)
    out.mkdir(parents=True, exist_ok=True)
    input_hash = file_sha(iso)
    source_config = iso_pack.read_member(iso, CONFIG)
    source_font = iso_pack.read_member(iso, FONT)
    source_skill, source_members = skill_member(source_config)
    report = {'experiment': ACK, 'runtime_tested': False, 'input_iso_sha256': input_hash,
              'normal_budget': W.SKILL00_LIMIT, 'dlc_modified': False,
              'scope': 'Skill00 + accepted v5 PL font + 20 PL executable skill overrides; no other translation',
              'interpretation': 'A full PL, B Japanese with spaces same size; a crash of A alone does not establish a size cause'}
    old_lang = text_codec.lang()
    try:
        with experimental_budget():
            a_dir = out / 'A_PELNE_PL'
            built = B.build(iso, None, package, a_dir, only=['config00.cpk','font.cpk','EBOOT.BIN'],
                            ui_textures=False, executable=True, lang='pl')
            if built['problems']:
                raise ValueError('builder reported problems: '+str(built['problems']))
            a_iso = a_dir / 'patched.iso'
            if not a_iso.is_file():
                raise ValueError('builder produced no ISO')
            config_a = iso_pack.read_member(a_iso, CONFIG)
            full, members_a = skill_member(config_a)
            checks = verify_records(source_skill, full, package)
            changed_members = [n for n in source_members if source_members[n] != members_a.get(n)]
            if len(changed_members) != 1 or not changed_members[0].endswith('/'+MEMBER) or source_members.keys() != members_a.keys():
                raise ValueError('config changes exceed Skill00')
            font_a = iso_pack.read_member(a_iso, FONT)
            fonts_before, fonts_after = V.font_members(source_font), V.font_members(font_a)
            if fonts_before.keys() != fonts_after.keys() or any(fonts_before[n] != fonts_after[n] for n in fonts_before if n != 'ank.fta'):
                raise ValueError('font changes exceed ank.fta')
            font_check = pl_glyph_compose.verify_native(fonts_before['ank.fta'], fonts_after['ank.fta'], dict(zip(font_pl.PL_LETTERS,font_pl.PL_BYTES)))
            if not font_check['ok']:
                raise ValueError('native font read-back failed')
            # Exact executable comparison: same code/bytes except selected PL data slots.
            original_elf, _, error = B._exe_elf(iso_pack.read_member(iso, EXE))
            if error:
                raise ValueError('cannot independently read original ELF: '+error)
            exe_rows = [r for r in B.load_rows(package, 'pl') if B.owner(r) == 'exe' and B.filled(r)]
            expected_exe, exe_report = E.apply_rows(original_elf, exe_rows)
            if exe_report['skipped'] or iso_pack.read_member(a_iso, EXE) != expected_exe:
                raise ValueError('executable slot write/read-back failed')
            text_section = E.Elf(original_elf).section('.text')
            if text_section is None or original_elf[text_section.offset:text_section.offset+text_section.size] != expected_exe[text_section.offset:text_section.offset+text_section.size]:
                raise ValueError('executable code .text changed')
            exe_a = expected_exe
            scope_a = verify_iso_scope(iso, a_iso, {CONFIG,FONT,EXE})
            a_named = a_dir / 'A_PELNE_UMIEJETNOSCI_PL.iso'
            a_iso.rename(a_named)
            # Control changes no numeric data: current writer fixes +32/+36/+52 as it pads.
            control = grow_control(source_skill, len(full))
            check_b = M.check(control, 'skill', MEMBER, source_skill)
            b_parsed = R.parse_member(control,'skill',MEMBER)
            original_parsed = R.parse_member(source_skill,'skill',MEMBER)
            for a,b in zip(original_parsed['records'],b_parsed['records']):
                for role in R.FIELDS:
                    before = W.field_raw(source_skill,a,role)
                    after = W.field_raw(control,b,role)
                    if (after != before if role != 'effect' else not after.startswith(before) or after[len(before):].strip(b' ')):
                        raise ValueError('control changed more than trailing effect spaces')
                if source_skill[a['offset']+a['boundaries'][-1]:a['offset']+a['length']] != control[b['offset']+b['boundaries'][-1]:b['offset']+b['length']]:
                    raise ValueError('control numeric tail changed')
            _, control_pool = R.parse_tail_pool(control,b_parsed['tail_offset'])
            _, original_pool = R.parse_tail_pool(source_skill,original_parsed['tail_offset'])
            if control_pool != original_pool:
                raise ValueError('control pool contents changed')
            original_path = out/'work'/'config00.cpk'
            original_path.parent.mkdir(parents=True,exist_ok=True)
            original_path.write_bytes(source_config)
            config_b, _ = M.with_member(original_path,MEMBER,control)
            b_dir = out/'B_KONTROLA_ROZMIARU'; b_dir.mkdir()
            b_iso = b_dir/'B_JP_TEN_SAM_ROZMIAR.iso'
            iso_pack.patch_iso(iso,b_iso,{CONFIG:config_b,FONT:font_a,EXE:exe_a})
            if iso_pack.read_member(b_iso,CONFIG) != config_b or skill_member(config_b)[0] != control:
                raise ValueError('B ISO read-back failed')
            if iso_pack.read_member(b_iso,FONT) != font_a or iso_pack.read_member(b_iso,EXE) != exe_a:
                raise ValueError('A/B common font/executable differ')
            scope_b = verify_iso_scope(iso,b_iso,{CONFIG,FONT,EXE})
            report.update({'skill_bytes_A':len(full),'skill_bytes_B':len(control),
                           'over_guard_bytes':max(0,len(full)-W.SKILL00_LIMIT),
                           'A':{**checks,'iso':str(a_named),'sha256':file_sha(a_named),'scope':scope_a},
                           'B':{**check_b,'iso':str(b_iso),'sha256':file_sha(b_iso),'scope':scope_b,
                                'japanese_text_and_pool_preserved':True},
                           'common_font':{'ok':True,'glyphs':18,'style':'native-ascii-plus-marks-v1'},
                           'common_executable_fields':exe_report['applied'], 'executable_code_text_unchanged':True,
                           'returned_snapshot':json.loads((package/'SKILL_TEST_SNAPSHOT.json').read_text(encoding='utf-8'))})
    finally:
        text_codec.set_lang(old_lang)
    if file_sha(iso) != input_hash:
        raise ValueError('input ISO changed')
    report['original_iso_unchanged'] = True
    report['normal_guard_restored'] = W.MEMBER_SIZE_LIMITS.get(MEMBER) == W.SKILL00_LIMIT
    if not report['normal_guard_restored']:
        raise ValueError('normal guard not restored')
    (out/'TEST_VERIFY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--iso',type=Path,required=True)
    p.add_argument('--package',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--acknowledge',required=True,choices=[ACK])
    a=p.parse_args()
    try:
        print(json.dumps(build(a.iso,a.package,a.out,a.acknowledge),ensure_ascii=False,indent=2))
    except Exception as exc:
        print('TEST BUILD FAILED: '+str(exc),file=sys.stderr)
        raise SystemExit(1)


if __name__=='__main__':
    main()
