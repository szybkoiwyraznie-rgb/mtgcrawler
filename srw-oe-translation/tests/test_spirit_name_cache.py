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
        self.assertEqual(len(S.PATCHES),69)
        self.assertEqual(len({a for a,_,_ in S.PATCHES}),69)

    def test_mismatch_truncation_and_repeat_refused(self):
        raw,offset = self.fixture()
        for image in (bytes(len(raw)),raw[:100],S.patch_words(raw,offset)):
            with self.assertRaisesRegex(ValueError,'unexpected instruction'):
                S.patch_words(image,offset)
        with self.assertRaisesRegex(ValueError,'unreviewed executable'):
            S.apply(raw)

    def test_allocation_and_member_moves_stay_consistent(self):
        allocations=0
        for addr,old,new in S.PATCHES:
            if old==0x34050028:
                self.assertEqual(new,0x34050040)
                allocations+=1
            else:
                self.assertEqual(old>>16,new>>16)
                self.assertIn(old&65535,(0x14,0x18,0x20,0x24))
                self.assertEqual((new&65535)-(old&65535),24)
                self.assertLess(new&65535,S.OBJECT_BYTES)
        self.assertEqual(allocations,10)
        self.assertEqual(S.NAME_OFFSET+S.NAME_BYTES,0x2c)
        self.assertEqual(len(S.cheat_lines()),69)
        self.assertIn('_L 0x201A8B30 0xAE02002C',S.cheat_lines())

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
            new=bytearray(S.OBJECT_BYTES);new[12:12+len(text)]=text
            struct.pack_into('<I',new,44,pointer)
            self.assertEqual(bytes(new[12:]).split(b'\0')[0],text[:-1])


if __name__=='__main__':unittest.main()
