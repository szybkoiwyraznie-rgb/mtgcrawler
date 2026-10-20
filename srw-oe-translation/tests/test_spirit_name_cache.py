"""Synthetic instruction words, never a copy of the game's executable."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import spirit_name_cache as S


class CacheTests(unittest.TestCase):
    def fixture(self):
        offset = 160
        raw = bytearray(max(a for a,_,_ in S.PATCHES)+offset+16)
        for address, old, _ in S.PATCHES:
            struct.pack_into('<I',raw,offset+address,old)
        return bytes(raw),offset

    def test_exact_atomic_instruction_edits_only(self):
        raw,offset = self.fixture()
        patched = S.patch_words(raw,offset)
        self.assertEqual(len(raw),len(patched))
        restored = bytearray(patched)
        for address,old,new in S.PATCHES:
            self.assertEqual(struct.unpack_from('<I',patched,offset+address)[0],new)
            struct.pack_into('<I',restored,offset+address,old)
        self.assertEqual(bytes(restored),raw)
        self.assertEqual(len(S.PATCHES),14)
        self.assertEqual(len({a for a,_,_ in S.PATCHES}),14)

    def test_mismatch_truncation_and_repeat_refused(self):
        raw,offset = self.fixture()
        for image in (bytes(len(raw)),raw[:100],S.patch_words(raw,offset)):
            with self.assertRaisesRegex(ValueError,'unexpected instruction'):
                S.patch_words(image,offset)
        with self.assertRaisesRegex(ValueError,'unreviewed executable'):
            S.apply(raw)

    def test_tail_allocation_and_four_name_addresses_stay_consistent(self):
        allocations=0
        for addr,old,new in S.PATCHES:
            if old==0x34050028:
                self.assertEqual(new,0x34050048)
                allocations+=1
            else:
                self.assertEqual(old>>16,new>>16)
                self.assertEqual(old&65535,0x0c)
                self.assertEqual(new&65535,S.NAME_OFFSET)
                self.assertLess(new&65535,S.OBJECT_BYTES)
        self.assertEqual(allocations,10)
        self.assertEqual(S.NAME_OFFSET,40)
        self.assertEqual(S.NAME_OFFSET+S.NAME_BYTES,S.OBJECT_BYTES)
        self.assertEqual(len(S.cheat_lines()),14)
        self.assertIn('_L 0x201A8A48 0x26130028',S.cheat_lines())

    def test_existing_fields_and_all_known_details_consumers_are_untouched(self):
        addresses={a for a,_,_ in S.PATCHES}
        for address in (0x1509ec,0x1509f8,0x1a209c,0x1a1d80,0x1a3574,
                        0x1a6ccc,0x1a7008,0x1a4b30):
            self.assertNotIn(address,addresses)
        allocations={a for a,old,_ in S.PATCHES if old==0x34050028}
        self.assertEqual(len(allocations),10)
        name_refs={a for a,old,_ in S.PATCHES if old!=0x34050028}
        self.assertEqual(name_refs,{0x1a4870,0x1a48d0,0x1a495c,0x1a4a48})

    def test_record_writer_refuses_names_beyond_the_repaired_cache(self):
        import item_skill_write as W
        import item_skill_records as R
        import text_codec
        from test_item_skill_write import build_record, build_member
        raw=build_member('spirit',[build_record('spirit',1,'Name','Effect')])
        row=R.parse_member(raw,'spirit')['records'][0]
        text_codec.set_lang('pl');self.addCleanup(text_codec.set_lang,'en')
        W.rebuild_record(row,{'name':'A'*31})
        with self.assertRaisesRegex(W.WriteError,'repaired menu cache'):
            W.rebuild_record(row,{'name':'A'*32})

    def test_original_suffix_overwrite_and_new_layout(self):
        text=b'Skupienie\0'
        for pointer in (0x004a5ad7,0x0012d738):
            old=bytearray(40);old[12:12+len(text)]=text
            struct.pack_into('<I',old,20,pointer)
            self.assertNotEqual(bytes(old[12:]).split(b'\0')[0],text[:-1])
            new=bytearray(S.OBJECT_BYTES);new[S.NAME_OFFSET:S.NAME_OFFSET+len(text)]=text
            struct.pack_into('<I',new,20,pointer)
            self.assertEqual(bytes(new[S.NAME_OFFSET:]).split(b'\0')[0],text[:-1])


if __name__=='__main__':unittest.main()
