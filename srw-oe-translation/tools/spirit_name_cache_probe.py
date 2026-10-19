"""Optional read-only MIPS cache reproduction; requires unicorn, no emulator/gameplay."""
import argparse
import sys,json,struct,hashlib
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
    
    def execute(image,name,ctor,level):
     m=U.Uc(U.UC_ARCH_MIPS,U.UC_MODE_MIPS32|U.UC_MODE_LITTLE_ENDIAN);m.mem_map(0,0x600000)
     for address,_,data in M.allocated_sections(image):m.mem_write(address,data)
     for addr in (0x700000,0x800000,STOP):m.mem_map(addr,0x10000)
     calls=[]
     def hook(m,pc,size,user):
      if pc not in external:return
      if pc==0x20f364:
       a=m.reg_read(UC_MIPS_REG_A1);text=bytes(m.mem_read(a,64)).split(b'\0')[0];calls.append(text)
      result={0x1a4654:7,0xe7804:DATA,0xe5a54:INPUT,0xe59b0:level}.get(pc,POINTER)
      m.reg_write(UC_MIPS_REG_V0,result);m.reg_write(UC_MIPS_REG_PC,m.reg_read(UC_MIPS_REG_RA))
     m.hook_add(U.UC_HOOK_CODE,hook)
     def run(addr,params):
      for reg,val in [(UC_MIPS_REG_SP,STACK),(UC_MIPS_REG_RA,STOP),*zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3,UC_MIPS_REG_T0),params)]:m.reg_write(reg,val)
      m.emu_start(addr,STOP,count=20000)
      assert m.reg_read(UC_MIPS_REG_PC)==STOP,hex(m.reg_read(UC_MIPS_REG_PC))
     m.mem_write(OBJ,b'\0'*64+b'GUARD'*4);m.mem_write(INPUT,name+b'\0');m.mem_write(DATA+12,struct.pack('<II',7,level))
     if ctor==0x1a4830:params=(OBJ,19,0,0,0)
     elif ctor==0x1a48b8:params=(OBJ,0,INPUT,level,0)
     else:params=(OBJ,0,DATA,0,0)
     run(ctor,params)
     before=bytes(m.mem_read(OBJ+12,32)).split(b'\0')[0]
     run(0x1a4a30,(OBJ,0))
     after=bytes(m.mem_read(OBJ+12,32)).split(b'\0')[0]
     assert bytes(m.mem_read(OBJ+64,20))==b'GUARD'*4
     return before,after,calls
    results=[]
    for ctor in (0x1a4830,0x1a48b8,0x1a4938):
     before,after,calls=execute(raw,b'Skupienie',ctor,1)
     assert before==b'Skupienie' and after!=b'Skupienie' and calls==[after],(hex(ctor),before,after,calls)
     results.append(dict(constructor=hex(ctor),old_suffix_hex=after.hex(),original_overwrite_reproduced=True))
     for index,name in enumerate(names):
      before,after,calls=execute(fixed,name,ctor,1+index%3)
      assert before==after==name and calls==[name],(hex(ctor),name,before,after,calls)
     for name in (b'A'*31,b'Skupienie'):
      before,after,calls=execute(fixed,name,ctor,1);assert before==after==name and calls==[name]
    report.update(scope='Memory-only execution of original/patched cache constructors, strcpy and draw method; external UI/getter callees stubbed, NOT PPSSPP',unicorn=U.__version__,constructors=results,physical_names=len(names),maximum_physical_name_bytes=max(map(len,names)),fixed_cases=3*(len(names)+2),original_corrupt_cases=3,guard_bytes_unchanged=True,full_focus_name_preserved=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
