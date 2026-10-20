"""Optional read-only MIPS cache reproduction; requires unicorn, no emulator/gameplay."""
import argparse
import sys,json,struct,hashlib,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import spirit_name_cache as S,mech_catalog_engine as M,item_skill_records as R
import unicorn as U
from unicorn.mips_const import *


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe',type=Path,required=True)
    parser.add_argument('--spirit',type=Path,required=True,help='physically rebuilt srwDL_Spirit.bin (private/local)')
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--previous-cache-module',type=Path,help='optional private copy of historical v2.2 module, to reproduce regression')
    args=parser.parse_args()
    raw=args.exe.read_bytes();fixed,report=S.apply(raw)
    spirit=args.spirit.read_bytes()
    parsed=R.parse_member(spirit,'spirit','srwDL_Spirit.bin');names=[spirit[r['offset']+r['name_offset']:].split(b'\0')[0] for r in parsed['records']]
    assert max(map(len,names))<S.NAME_BYTES
    OBJ,INPUT,DATA,STOP,STACK=0x800100,0x801000,0x802000,0x900000,0x70f000
    POINTER=0x004a5ad4
    # All external JAL targets from the bounded class; only strcpy executes outside it.
    section=S.E.Elf(raw).section('.text');words=struct.unpack('<%dI'%(section.size//4),raw[section.offset:section.offset+section.size])
    external={(w&0x3ffffff)*4 for w in words[0x1a4684//4:0x1a4fe4//4] if w>>26==3 and not 0x1a4684<=(w&0x3ffffff)*4<0x1a4fe4 and (w&0x3ffffff)*4!=0x36731c}
    
    # Execute the real details caller and callee too. Other UI/getter callees remain
    # stubbed, explicitly; this is a memory-contract test, NOT PPSSPP gameplay.
    for lo,hi in ((0x1a201c,0x1a2140),(0x210904,0x210a5c)):
     external.update((w&0x3ffffff)*4 for w in words[lo//4:hi//4] if w>>26==3)
    external.discard(0x210904)
    LIST,DETAIL,FONT=0x803000,0x804000,0x805000

    def execute(image,name,ctor,level,name_offset,object_bytes,expect_bad=False):
     m=U.Uc(U.UC_ARCH_MIPS,U.UC_MODE_MIPS32|U.UC_MODE_LITTLE_ENDIAN);m.mem_map(0,0x600000)
     for address,_,data in M.allocated_sections(image):m.mem_write(address,data)
     for addr in (0x700000,0x800000,STOP):m.mem_map(addr,0x10000)
     calls=[];detail_sources=[];bad_reads=[]
     def invalid(m,access,address,size,value,user):
      bad_reads.append(address);return False
     m.hook_add(U.UC_HOOK_MEM_READ_UNMAPPED|U.UC_HOOK_MEM_READ_INVALID,invalid)
     def hook(m,pc,size,user):
      if pc==0x210908:
       source=m.reg_read(UC_MIPS_REG_A1);detail_sources.append(source)
       if source!=POINTER:bad_reads.append(source+8)
      if pc not in external:return
      if pc==0x20f364:
       a=m.reg_read(UC_MIPS_REG_A1);text=bytes(m.mem_read(a,64)).split(b'\0')[0];calls.append(text)
      result={0x1a4654:7,0xe7804:DATA,0xe5a54:INPUT,0xe59b0:level,0x21071c:DETAIL}.get(pc,POINTER)
      m.reg_write(UC_MIPS_REG_V0,result);m.reg_write(UC_MIPS_REG_PC,m.reg_read(UC_MIPS_REG_RA))
     m.hook_add(U.UC_HOOK_CODE,hook)
     def run(addr,params,stop=STOP):
      for reg,val in [(UC_MIPS_REG_SP,STACK),(UC_MIPS_REG_RA,STOP),*zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3,UC_MIPS_REG_T0),params)]:m.reg_write(reg,val)
      m.emu_start(addr,stop,count=20000)
      assert m.reg_read(UC_MIPS_REG_PC)==stop,hex(m.reg_read(UC_MIPS_REG_PC))
     m.mem_write(OBJ,b'\0'*object_bytes+b'GUARD'*4);m.mem_write(INPUT,name+b'\0');m.mem_write(DATA+12,struct.pack('<II',7,level))
     if ctor==0x1a4830:params=(OBJ,19,0,0,0)
     elif ctor==0x1a48b8:params=(OBJ,0,INPUT,level,0)
     else:params=(OBJ,0,DATA,0,0)
     run(ctor,params)
     before=bytes(m.mem_read(OBJ+name_offset,32)).split(b'\0')[0]
     run(0x1a4a30,(OBJ,0))
     after=bytes(m.mem_read(OBJ+name_offset,32)).split(b'\0')[0]
     assert bytes(m.mem_read(OBJ+object_bytes,20))==b'GUARD'*4
     # Drawable/source pointer matches the ctor/draw stub result. Satisfy its
     # font-metrics link so the *whole*210904 function can execute, not be stubbed.
     m.mem_write(POINTER,b'\0'*0x60)
     m.mem_write(POINTER+0x28,struct.pack('<I',FONT))
     m.mem_write(FONT+0x58,struct.pack('<I',16))
     m.mem_write(DETAIL+0x14,struct.pack('<I',POINTER))
     m.mem_write(LIST,b'\0'*0x130)
     m.mem_write(LIST+0x18,struct.pack('<I',256))
     m.mem_write(LIST+0x3c,struct.pack('<I',OBJ))
     try:
      run(0x1a201c,(LIST,0))  # owner's stack:19f5c4 ->1a201c ->210904
      for start,end,registers in (
       (0x1a1d6c,0x1a1d84,{UC_MIPS_REG_S0:LIST}),
       (0x1a3560,0x1a3578,{UC_MIPS_REG_S6:LIST}),
       (0x1a6cb8,0x1a6cd0,{UC_MIPS_REG_S0:LIST}),
       (0x1a6ff0,0x1a700c,{UC_MIPS_REG_S0:0,UC_MIPS_REG_S1:LIST,UC_MIPS_REG_V0:DETAIL})):
       m.mem_write(LIST+0x18,struct.pack('<I',OBJ))
       for reg,val in registers.items():m.reg_write(reg,val)
       run(start,(DETAIL,0),end)
     except U.UcError:
      if not expect_bad:raise
      assert bad_reads==[0x6d],bad_reads
      return before,after,calls,dict(regression_read_address='0x6d',details_source=hex(detail_sources[0]))
     assert not expect_bad,'historical regression did not fail'
     assert detail_sources==[POINTER]*5,detail_sources
     assert not bad_reads,bad_reads
     assert bytes(m.mem_read(OBJ+object_bytes,20))==b'GUARD'*4
     assert bytes(m.mem_read(OBJ+name_offset,32)).split(b'\0')[0]==after
     return before,after,calls,dict(real_details_consumers=len(detail_sources))
    results=[]
    for ctor in (0x1a4830,0x1a48b8,0x1a4938):
     before,after,calls,details=execute(raw,b'Skupienie',ctor,1,12,40)
     assert before==b'Skupienie' and after!=b'Skupienie' and calls==[after],(hex(ctor),before,after,calls)
     results.append(dict(constructor=hex(ctor),old_suffix_hex=after.hex(),original_overwrite_reproduced=True))
     for index,name in enumerate(names):
      before,after,calls,details=execute(fixed,name,ctor,1+index%3,S.NAME_OFFSET,S.OBJECT_BYTES)
      assert before==after==name and calls==[name],(hex(ctor),name,before,after,calls)
     for name in (b'A'*31,b'Skupienie'):
      before,after,calls,details=execute(fixed,name,ctor,1,S.NAME_OFFSET,S.OBJECT_BYTES);assert before==after==name and calls==[name]
    regressions=[]
    if args.previous_cache_module:
     spec=importlib.util.spec_from_file_location('historical_cache',args.previous_cache_module)
     previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
     regressed,_=previous.apply(raw)
     for ctor in (0x1a4830,0x1a48b8,0x1a4938):
      *_,details=execute(regressed,b'Skupienie',ctor,1,12,64,expect_bad=True)
      regressions.append(dict(constructor=hex(ctor),**details))
    report.update(historical_v22_crash_reproduced=regressions,
                  details_consumer_offsets=['0x1a209c','0x1a1d80','0x1a3574','0x1a6ccc','0x1a7008'],
                  actual_details_callee='0x210904 (not stubbed)',
                  details_calls_per_fixed_case=5,fixed_details_calls=15*(len(names)+2),scope='Memory-only execution of original/patched constructors, strcpy, draw, full details-selection caller1a201c and callee210904 plus four external details-update call slices; other UI/getter callees stubbed, NOT PPSSPP',unicorn=U.__version__,constructors=results,physical_names=len(names),maximum_physical_name_bytes=max(map(len,names)),fixed_cases=3*(len(names)+2),original_corrupt_cases=3,guard_bytes_unchanged=True,full_focus_name_preserved=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
