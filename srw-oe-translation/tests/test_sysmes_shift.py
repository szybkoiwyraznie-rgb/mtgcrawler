"""sysmes_shift._grow moves the pool and rewrites pointers (strictly-after only)."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import sysmes_shift as ss  # noqa: E402
from sysmes_pack import POOL_MIN  # noqa: E402


def make_sm(strings):
    pool = bytearray(); offs = []
    for s in strings:
        offs.append(POOL_MIN + len(pool))
        b = s.encode("cp932") + b"\x00"
        pool += b + b"\x00" * ((-len(b)) % 4)
    sm = bytearray(POOL_MIN + len(pool))
    sm[:4] = b"SMES"; struct.pack_into("<I", sm, 4, len(sm))
    struct.pack_into("<I", sm, 0x100, offs[0])   # pointer to string 0
    struct.pack_into("<I", sm, 0x104, offs[1])   # pointer to string 1
    sm[POOL_MIN:] = pool
    return bytes(sm), offs


class SysmesShiftTests(unittest.TestCase):
    def test_grow_shifts_later_pointer_keeps_own(self):
        sm, offs = make_sm(["ライブラリー", "リファレンス"])
        new = ss._grow(sm, offs[0], "LIBRARY")
        delta = len(new) - len(sm)
        self.assertLess(delta, 0)  # LIBRARY is shorter -> pool shrinks
        # own pointer (== offs[0]) must NOT move; later pointer shifts by delta
        self.assertEqual(struct.unpack_from("<I", new, 0x100)[0], offs[0])
        self.assertEqual(struct.unpack_from("<I", new, 0x104)[0], offs[1] + delta)
        self.assertEqual(struct.unpack_from("<I", new, 4)[0], len(new))
        # second string still readable at its new offset
        i = offs[1] + delta
        self.assertEqual(new[i:i + len("リファレンス".encode("cp932"))],
                         "リファレンス".encode("cp932"))


if __name__ == "__main__":
    unittest.main()
