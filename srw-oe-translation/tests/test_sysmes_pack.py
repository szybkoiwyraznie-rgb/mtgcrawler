"""sysmes_pack grows a pool string and rewrites the pointer table + SMES size."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import sysmes_pack as sp  # noqa: E402


def make_sm(strings):
    pool_off = sp.POOL_MIN
    pool = bytearray()
    offs = []
    for s in strings:
        offs.append(pool_off + len(pool))
        b = s.encode("cp932") + b"\x00"
        pool += b + b"\x00" * ((-len(b)) % 4)
    sm = bytearray(pool_off + len(pool))
    sm[:4] = b"SMES"
    struct.pack_into("<I", sm, 4, len(sm))
    struct.pack_into("<I", sm, 8, len(strings))
    # one pointer word in the table referencing the first string
    struct.pack_into("<I", sm, 0x100, offs[0])
    sm[pool_off:pool_off + len(pool)] = pool
    return bytes(sm), offs


class SysmesPackTests(unittest.TestCase):
    def test_grow_fixes_pointer_and_size(self):
        sm, offs = make_sm(["ライブラリー", "クレジット"])
        new = sp.grow_one(sm, offs[0], "LIBRARY AND MORE")
        # pointer to the grown string shifted by delta
        delta = len(new) - len(sm)
        self.assertEqual(struct.unpack_from("<I", new, 0x100)[0], offs[0] + delta)
        # size field updated
        self.assertEqual(struct.unpack_from("<I", new, 4)[0], len(new))
        # the second string moved after the grown one and still reads back
        i = new.find("クレジット".encode("cp932"))
        self.assertEqual(i, offs[1] + delta)
        # new text present, NUL-terminated
        j = new.find(b"LIBRARY AND MORE")
        self.assertEqual(j, offs[0])
        self.assertEqual(new[j + len(b"LIBRARY AND MORE")], 0)

    def test_apply_edits_exact_match_only(self):
        sm, offs = make_sm(["ライブラリー", "ライブラリーを閲覧できます。"])
        new = sp.apply_edits(sm, {"ライブラリー": "LIBRARY"})
        self.assertIn(b"LIBRARY", new)
        # the longer string that merely CONTAINS the term is untouched
        self.assertIn("ライブラリーを閲覧できます。".encode("cp932"), new)


if __name__ == "__main__":
    unittest.main()
