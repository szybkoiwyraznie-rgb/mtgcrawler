"""configst_pack PAC parse/rebuild: byte-identical round-trip + offset shift on growth."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import configst_pack as cp  # noqa: E402


def make_pac(subs):
    data_base, name_len = 0x800, 32
    layout = []
    running = data_base
    for name, data in subs:
        off = (running + 0x7FF) & ~0x7FF
        layout.append((name, data, off))
        running = off + len(data)
    out = bytearray(struct.pack("<III", data_base, len(subs), name_len))
    out += b"\x00" * (0x10 - len(out))
    for name, data, off in layout:
        out += struct.pack("<II", off, len(data)) + name.encode().ljust(name_len, b"\x00")
    out += b"\x00" * (data_base - len(out))
    for name, data, off in layout:
        out += b"\x00" * (off - len(out)) + data
    out += b"\x00" * (((len(out) + 0x7FF) & ~0x7FF) - len(out))
    return bytes(out)


class ConfigstPackTests(unittest.TestCase):
    def test_round_trip_identical(self):
        pac = make_pac([("a.bin", b"\x01" * 100), ("srwDL_Item.bin", b"\x02" * 5000),
                        ("sysmes.bin", b"\x03" * 300)])
        parsed = cp.parse_pac(pac)
        self.assertEqual([s["name"] for s in parsed["subs"]],
                         ["a.bin", "srwDL_Item.bin", "sysmes.bin"])
        self.assertEqual(parsed["subs"][1]["data"], b"\x02" * 5000)
        self.assertEqual(cp.rebuild_pac(parsed), pac)

    def test_grow_shifts_later_offsets(self):
        pac = make_pac([("a.bin", b"\x01" * 100), ("b.bin", b"\x02" * 100)])
        parsed = cp.parse_pac(pac)
        off_b_before = parsed["subs"][1]["offset"]
        parsed["subs"][0]["data"] = b"\x01" * (100 + 4096)  # grow a.bin past one align block
        rebuilt = cp.rebuild_pac(parsed)
        reparsed = cp.parse_pac(rebuilt)
        self.assertEqual(reparsed["subs"][0]["data"], b"\x01" * (100 + 4096))
        self.assertGreater(reparsed["subs"][1]["offset"], off_b_before)
        self.assertEqual(reparsed["subs"][1]["data"], b"\x02" * 100)

    def test_tail_align_trims_only_the_trailing_pad(self):
        """tail_align=0x10 strips the zeros after the last sub-file; offsets stay put."""
        pac = make_pac([("a.bin", b"\x01" * 100), ("b.bin", b"\x02" * 5000)])
        parsed = cp.parse_pac(pac)
        trimmed = cp.rebuild_pac(parsed, tail_align=0x10)
        self.assertLessEqual(len(trimmed), len(pac))
        a, b = cp.parse_pac(pac), cp.parse_pac(trimmed)
        self.assertEqual([(s["name"], s["offset"], s["size"]) for s in a["subs"]],
                         [(s["name"], s["offset"], s["size"]) for s in b["subs"]])
        self.assertEqual([s["data"] for s in a["subs"]], [s["data"] for s in b["subs"]])
        # and a pac WITH a tail pad shrinks (the default keeps the full pad)
        padded = make_pac([("a.bin", b"\x01" * 100), ("b.bin", b"\x02" * 100)]) + b"\x00" * 1500
        self.assertLess(len(cp.rebuild_pac(cp.parse_pac(padded), tail_align=0x10)),
                        len(cp.rebuild_pac(cp.parse_pac(padded))))

    def test_tail_align_must_be_power_of_two(self):
        parsed = cp.parse_pac(make_pac([("a.bin", b"\x01")]))
        with self.assertRaises(ValueError):
            cp.rebuild_pac(parsed, tail_align=100)


if __name__ == "__main__":
    unittest.main()
