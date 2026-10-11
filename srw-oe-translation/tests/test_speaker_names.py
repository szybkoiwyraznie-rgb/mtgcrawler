import struct
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import speaker_names as SN  # noqa: E402


def _slot(name_cp932: bytes, key: int, marker: bool) -> bytes:
    """Build a 0x14-byte name slot followed by u32 key (rule: key at slot+0x14)."""
    blob = bytearray(0x40)
    blob[0:len(name_cp932)] = name_cp932
    struct.pack_into("<I", blob, 0x14, key)
    if marker:
        struct.pack_into("<H", blob, 0x14 + SN.MARK_OFF, SN.MARK)
    return bytes(blob)


class SpeakerNameRuleTests(unittest.TestCase):
    def setUp(self):
        SN.CLEAN = SN._clean_re()

    def test_decode_slot_halfwidth_katakana(self):
        blob = b"\xbe\xb2\xbc\xdb\xb3\x00" + b"\x00" * 10
        self.assertEqual(SN.decode_slot(blob, 0), SN.unicodedata.normalize("NFKC", "ｾｲｼﾛｳ"))

    def test_scan_finds_key_at_plus_0x14(self):
        blob = b"\x00" * 0x10 + _slot("連邦兵".encode("cp932"), 0x4B6, marker=True)
        res = SN.scan(blob)
        self.assertIn(0x4B6, res)
        self.assertEqual(res[0x4B6][0]["name"], "連邦兵")
        self.assertEqual(res[0x4B6][0]["confidence"], "marker")

    def test_scan_marks_unconfirmed_as_slot(self):
        blob = _slot("自衛隊員".encode("cp932"), 0xEC0, marker=False)
        res = SN.scan(blob)
        self.assertEqual(res[0xEC0][0]["confidence"], "slot")

    def test_scan_rejects_junk_and_zero_keys(self):
        blob = _slot(b"\x01\x02\x03", 0x1234, marker=False)  # non-clean bytes
        self.assertNotIn(0x1234, SN.scan(blob))
        blob = _slot("連邦兵".encode("cp932"), 0, marker=False)
        self.assertNotIn(0, SN.scan(blob))


if __name__ == "__main__":
    unittest.main()
