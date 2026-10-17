#!/usr/bin/env python3
"""Verify a built v17 distribution using PRIVATE originals and a minimal ISO fixture.

This is NOT a bootable full-game build or PPSSPP test. Generated large archives
must go under ignored/excluded build/. The uploaded kit must contain no game files.
All inputs are read only. Verification compares every original/output map member
independently of terrain_names.patch_attr and the builder's own report.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import zipfile

import check_dlc_titles
import configst_pack
import cpk_table
import crilayla
import exe_strings
import iso_pack
import speaker_map

INPUTS = ("EBOOT.BIN", "eventP00.cpk", "lmap.cpk", "config04.EDAT", "imenu04.EDAT", "config26.EDAT", "config27.EDAT")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for b in iter(lambda:handle.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def members(path):
    table = cpk_table.read_cpk_table(path)
    offsets = speaker_map.member_offsets(path,table)
    with path.open("rb") as handle:
        for entry,offset in zip(table["entries"],offsets):
            handle.seek(offset);raw=handle.read(entry["file_size"])
            require(len(raw)==entry["file_size"],"truncated CPK readback")
            if crilayla.is_crilayla(raw):raw=crilayla.decompress(raw).data
            yield entry,raw


def verify_maps(original, output, package):
    rows=[json.loads(l) for l in (package/"10_map_terrain.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    expected={r["record"]:r for r in rows};require(len(expected)==111,"expected 111 terrain names")
    copies=cells=0
    # Keep no decompressed full-game dataset in memory.
    for (old_entry,old),(new_entry,new) in zip(members(original),members(output)):
        for key in ("name","id","dir_name"):
            require(old_entry.get(key)==new_entry.get(key),"map identity/directory changed")
        require(new_entry["file_size"]==new_entry["extract_size"]==len(new),"map is not stored as declared")
        old_sub=[s for s in configst_pack.parse_pac(old)["subs"] if s["name"]=="attr.par"]
        new_sub=[s for s in configst_pack.parse_pac(new)["subs"] if s["name"]=="attr.par"]
        require(len(old_sub)==len(new_sub)==1,"attr.par copy missing/duplicated")
        a,z=old_sub[0],new_sub[0]
        require((a["offset"],a["size"])==(z["offset"],z["size"]),"attr.par layout changed")
        off,size=a["offset"],a["size"]
        require(len(old)==len(new) and old[:off]==new[:off] and old[off+size:]==new[off+size:],
                "map geometry/textures/PAC directory changed")
        before,after=a["data"],z["data"]
        require(len(before)==len(after)==9284 and before[:4]==after[:4],"attribute table resized")
        require(struct.unpack_from("<I",before)[0]==145,"attribute count changed")
        for i in range(145):
            start=4+i*64
            require(before[start+32:start+64]==after[start+32:start+64],"numeric attribute modified")
            old_cell,new_cell=before[start:start+32],after[start:start+32]
            if i in expected:
                r=expected[i]
                require(old_cell==r["jp"].encode("cp932").ljust(32,b"\0"),"original label differs")
                require(new_cell==r["en"].encode("ascii").ljust(32,b"\0"),"English label missing/wrong")
                cells+=1
            else:
                require(old_cell==new_cell==bytes(32),"blank name cell modified")
        copies+=1
    require(copies==271,"not all map copies were checked")
    require(len(cpk_table.read_cpk_table(original)["entries"])==len(cpk_table.read_cpk_table(output)["entries"])==271,
            "extra or missing map entries")
    require(cells==30081,"not all terrain cells were checked")
    return {"copies":copies,"name_cells":cells,"all_numeric_and_non_name_bytes_unchanged":True,
            "output_bytes":output.stat().st_size,"output_sha256":sha(output)}



def validated_broadcast_misses(report, originals, package):
    """Allow ONLY global RoboDict rows whose IDs provably do not exist in a chapter.

    The legacy writer calls these row-level skips `refused` and samples the first
    eight into container.problems. Reconcile the ENTIRE refusal count against the
    original keyspace; do not blanket-ignore writer warnings or test only the
    top-level problems array. Any in-range/stale-JP/structural refusal still fails.
    """
    import build_translation_patch as bp
    import table_write as tw
    global_rows = [r for r in bp.load_rows(package) if bp.filled(r) and not bp.identity(r)
                   and (r.get("source") or {}).get("container") is None]
    notes = []
    for container in report['containers']:
        name = container['container']
        allowed = set()
        for step in container.get('steps',[]):
            detail = step.get('detail') or {}
            if not detail.get('refused'):
                continue
            require(step['step']=='tables' and isinstance(detail['refused'],int),
                    'unexpected non-table writer refusal')
            require(name in originals,'refusal from a container without a checked original')
            pool = {}
            for member,blob in speaker_map.read_members(originals[name]):
                subs = [(x['name'],x['data']) for x in configst_pack.parse_pac(blob)['subs']] if member.endswith('.pac') else [(member,blob)]
                pool.update(subs)
            reconciled = 0
            for member, result in detail.get('per_member',{}).items():
                require(not result.get('problems'),'member structural error')
                count = result.get('refused',0)
                if not count:
                    continue
                require(member.startswith('srw_DL_RoboDictionary') and member in pool,
                        'unexpected refused member')
                raw = pool[member];family=tw.family_of(member)
                keys={tw.record_key(raw,span,family) for span in tw.record_spans(raw)}
                absent=[r for r in global_rows if tw.member_matches(r['source'].get('member'),member)
                        and r.get('key') is not None and int(r['key']) not in keys
                        and not (bp.DLC_CONFIG_RE.match(name) and bp.config_side_spare_row(r))]
                require(len(absent)==count,'refusal count exceeds independently proven absent global IDs')
                reconciled += count
                messages={f"tables: {member}: refused: {r['id']}: no record with key {r['key']}" for r in absent}
                allowed.update(messages)
                notes.append({'container':name,'member':member,'count':count,
                              'classification':'global broadcast IDs absent from this chapter; not failed target writes'})
            require(reconciled==detail['refused'],'unreconciled table refusals')
            require(all('tables: '+msg in allowed for msg in detail.get('problems',[])),
                    'unexpected table refusal detail')
        require(all(msg in allowed for msg in container.get('problems',[])),
                'unexpected container-level writer refusal')
    return notes


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kit",type=Path,required=True)
    ap.add_argument("--originals",type=Path,required=True)
    ap.add_argument("--work",type=Path,required=True,help="Fresh ignored build/ directory")
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args(argv)
    require(a.work.resolve()!=a.originals.resolve() and a.originals.resolve() not in a.work.resolve().parents,
            "work folder must be outside original inputs")
    require(a.kit.resolve() not in a.work.resolve().parents,"work folder overlaps kit")
    require(not a.work.exists(),"use a fresh work folder to avoid stale outputs")
    require(a.report.suffix.lower()=='.json' and a.originals.resolve() not in a.report.resolve().parents
            and a.report.resolve()!=a.kit.resolve(),"report must be JSON outside original inputs")
    originals={name:a.originals/name for name in INPUTS}
    before={name:sha(path) for name,path in originals.items()}
    a.work.mkdir(parents=True)
    unpacked=a.work/"kit"
    with zipfile.ZipFile(a.kit) as archive:
        require(archive.testzip() is None,"kit ZIP CRC failure")
        for name in archive.namelist():
            p=Path(name)
            require(not p.is_absolute() and ".." not in p.parts,"unsafe ZIP path")
            require(p.suffix.lower() not in (".iso",".cpk",".edat",".bin",".pbp",".dat"),"game file in distribution")
        count=len(archive.namelist())
        archive.extractall(unpacked)
    for name in ("PATCH.bat","CHECK_DLC.bat","tools/terrain_names.py","tools/check_dlc_titles.py","translation/10_map_terrain.jsonl"):
        require((unpacked/name).is_file(),f"kit missing {name}")
    package=unpacked/"translation"
    image=a.work/"validation-fixture.iso"
    image.write_bytes(iso_pack.build_iso({"PSP_GAME":{"PARAM.SFO":b"OFFLINE TEST FIXTURE - NOT A FULL GAME", "SYSDIR":{"EBOOT.BIN":originals['EBOOT.BIN'].read_bytes()},
        "USRDIR":{n:originals[n].read_bytes() for n in ('eventP00.cpk','lmap.cpk')}}}))
    dlc=a.work/"original-dlc";dlc.mkdir()
    for name in INPUTS[3:]:
        folder=dlc/"chapter04" if name=='config04.EDAT' else dlc
        folder.mkdir(parents=True,exist_ok=True);shutil.copyfile(originals[name],folder/name)
    output=a.work/"output"
    cmd=[sys.executable,str(unpacked/'tools/build_translation_patch.py'),'--iso',str(image),'--dlc',str(dlc),
         '--package',str(package),'--out',str(output),'--only',*INPUTS,'--no-ui-textures']
    print('Running the EXTRACTED kit with a nested chapter-4 input and real 1.08 data...',flush=True)
    with (a.work/'kit-build.log').open('w',encoding='utf-8') as log:
        subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT)
    report=json.loads((output/'build_report.json').read_bytes())
    require(not report['problems'],'builder reported problems')
    broadcast_notes=validated_broadcast_misses(report,originals,package)
    require(report['terrain']['status']=='verified','terrain step absent or failed')
    for target in report.get('executable',{}).get('targets',[]):
        require(not target.get('skipped') and not target.get('problems'),'executable rows refused')
    patched_iso=output/'patched.iso'
    rebuilt_map=a.work/'map-from-iso.cpk'
    rebuilt_map.write_bytes(iso_pack.read_member(patched_iso,'PSP_GAME/USRDIR/lmap.cpk'))
    print('Independently checking all map payloads extracted from the resulting ISO...',flush=True)
    maps=verify_maps(originals['lmap.cpk'],rebuilt_map,package)
    want,exe_report=exe_strings.apply_rows(originals['EBOOT.BIN'].read_bytes(),exe_strings.load_rows(package/'09_executable.jsonl'))
    require(not exe_report['skipped'],'expected executable cannot be built')
    actual=iso_pack.read_member(patched_iso,'PSP_GAME/SYSDIR/EBOOT.BIN')
    require(actual==want,'ISO executable differs from expected build')
    old=exe_strings.Elf(originals['EBOOT.BIN'].read_bytes());new=exe_strings.Elf(actual)
    sec=old.section('.text');require(sec is not None,'text section missing')
    require(old.data[sec.offset:sec.offset+sec.size]==new.data[sec.offset:sec.offset+sec.size],'game code changed')
    event_path=a.work/'event-from-iso.cpk';event_path.write_bytes(iso_pack.read_member(patched_iso,'PSP_GAME/USRDIR/eventP00.cpk'))
    event=dict(speaker_map.read_members(event_path));require(event['DL100_01_ext.dat'][344:384].split(b'\0')[0]==b'Basic Training','v16 title-card regression')
    expected=check_dlc_titles.expectations([json.loads(l) for l in (package/'04_config_text.jsonl').read_text(encoding='utf-8').splitlines()])
    dlc_report=check_dlc_titles.inspect_folder(output/'DLC',expected)
    require(dlc_report['passed'],'output DLC title contract failed')
    require(all(p.parent==output/'DLC' for p in (output/'DLC').rglob('*') if p.is_file()),'nested deployment output')
    for r in dlc_report['files']:
        require(all(x['reported_jp_occurrences']==0 for x in r['records'].values()),'reported JP title remains in DLC catalog')
    require(before=={name:sha(path) for name,path in originals.items()},'original inputs modified')
    result={'status':'PASS','scope':'Real originals + actual extracted distribution on minimal ISO fixture; not gameplay/PPSSPP',
            'kit_name':a.kit.name,'kit_bytes':a.kit.stat().st_size,'kit_sha256':sha(a.kit),'kit_files':count,'validated_broadcast_notes':broadcast_notes,
            'input_sha256':before,'maps':maps,'dlc':dlc_report,'iso_member_readback':True,'eboot_text_unchanged':True,
            'basic_training_preserved':True,'source_files_unchanged':True,'flat_deployment_from_nested_input':True}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS — all 271 maps, 30081 name cells, DLC fields and ISO read-back verified.',flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
