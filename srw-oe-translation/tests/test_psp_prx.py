# -*- coding: utf-8 -*-
"""psp_prx: AES known answers, ~PSP header parsing, PBP sub-file round trip.

No game bytes are used; the ``~PSP`` header is synthetic and the AES vectors are FIPS-197's.
"""
import struct
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))

import psp_prx as P  # noqa: E402


class AESKnownAnswerTests(unittest.TestCase):
    KEY = bytes(range(16))
    PLAIN = bytes.fromhex("00112233445566778899aabbccddeeff")
    CIPHER = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")

    def test_fips197_c1_decrypt(self):
        self.assertEqual(P.AES128(self.KEY).decrypt_block(self.CIPHER), self.PLAIN)

    def test_cbc_zero_iv_chains_blocks(self):
        aes = P.AES128(self.KEY)
        # two identical cipher blocks: block 1 = D(c) xor 0, block 2 = D(c) xor c
        out = aes.cbc_decrypt_zero_iv(self.CIPHER * 2)
        self.assertEqual(out[:16], self.PLAIN)
        self.assertEqual(out[16:], bytes(a ^ b for a, b in zip(self.PLAIN, self.CIPHER)))

    def test_cbc_refuses_partial_block(self):
        with self.assertRaises(ValueError):
            P.AES128(self.KEY).cbc_decrypt_zero_iv(b"\0" * 20)


class PspHeaderTests(unittest.TestCase):
    def _header(self, tag=0x2E5E10F0, comp_attribute=0, mode=25):
        h = bytearray(0x150)
        struct.pack_into("<IHHBB", h, 0, P.PSP_MAGIC, 0x0200, comp_attribute, 1, 1)
        h[0x0A:0x0A + 3] = b"srw"
        struct.pack_into("<IIIIi", h, 0x28, 5531024, 5533424, 0x80, 0x3EEC70, 0x1000)
        struct.pack_into("<II", h, 0x78, 0x06060010, mode)
        struct.pack_into("<ii", h, 0xB0, 5531024, 0)
        struct.pack_into("<I", h, 0xD0, tag)
        return bytes(h)

    def test_fields(self):
        info = P.psp_header(self._header())
        self.assertEqual(info["modname"], "srw")
        self.assertEqual(info["module_version"], "1.1")
        self.assertEqual(info["tag"], 0x2E5E10F0)
        self.assertEqual(info["decrypt_mode"], 25)
        self.assertEqual(info["elf_size"], 5531024)
        self.assertFalse(info["compressed"])
        self.assertTrue(P.psp_header(self._header(comp_attribute=1))["compressed"])

    def test_rejects_non_psp(self):
        with self.assertRaises(P.PrxError):
            P.psp_header(b"\x7fELF" + b"\0" * 0x200)
        with self.assertRaises(P.PrxError):
            P.psp_header(self._header()[:0x100])

    def test_unknown_tag_fails_closed(self):
        blob = self._header(tag=0x12345678) + b"\0" * 0x100
        with self.assertRaises(P.PrxError) as ctx:
            P.decrypt_prx(blob)
        self.assertIn("12345678", str(ctx.exception).lower())


def _pbp(parts):
    header = bytearray(b"\x00PBP" + struct.pack("<I", 0x10000))
    pos = 0x28
    offs = []
    for p in parts:
        offs.append(pos)
        pos += len(p)
    header += struct.pack("<8I", *offs)
    return bytes(header) + b"".join(parts)


class PbpTests(unittest.TestCase):
    PARTS = [b"\0PSF-param", b"icon0", b"", b"", b"pic1-bytes", b"", b"~PSP-data-here", b"psar"]

    def test_entries_and_get(self):
        blob = _pbp(self.PARTS)
        ents = P.pbp_entries(blob)
        self.assertEqual([n for n, _o, _s in ents], list(P.PBP_NAMES))
        self.assertEqual([s for _n, _o, s in ents], [len(p) for p in self.PARTS])
        self.assertEqual(P.pbp_get(blob, "DATA.PSP"), b"~PSP-data-here")
        self.assertEqual(P.pbp_get(blob, "PARAM.SFO"), b"\0PSF-param")
        self.assertEqual(P.pbp_get(blob, "ICON1.PMF"), b"")

    def test_replace_round_trip(self):
        blob = _pbp(self.PARTS)
        new = P.pbp_replace(blob, "DATA.PSP", b"\x7fELF-much-longer-plain-elf-payload")
        self.assertEqual(P.pbp_get(new, "DATA.PSP"), b"\x7fELF-much-longer-plain-elf-payload")
        for name in ("PARAM.SFO", "ICON0.PNG", "PIC1.PNG", "DATA.PSAR"):
            self.assertEqual(P.pbp_get(new, name), P.pbp_get(blob, name), name)
        self.assertEqual(new[:8], blob[:8])
        back = P.pbp_replace(new, "DATA.PSP", b"~PSP-data-here")
        self.assertEqual(back, blob)

    def test_rejects_non_pbp(self):
        with self.assertRaises(P.PrxError):
            P.pbp_entries(b"\x7fELF" + b"\0" * 64)


if __name__ == "__main__":
    unittest.main()
