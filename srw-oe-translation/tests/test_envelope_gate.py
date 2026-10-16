"""DLC configNN.EDAT size envelope: helpers of the builder gate (v10, 2026-10-16).

Measured on the v9 crash (user sweep): config01 249 984 B and config02 159 872 B - each
exactly one 0x800 quantum over the original file - crashed at Loading, while every rebuild
at the original size ran (build #17, half B, config03-08).  The gate limit is therefore
align_up(original, 0x800); the ladder is trim -> drop spare viewer-slot rows -> refuse.
"""
from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_translation_patch as BTP  # noqa: E402
import configst_pack as CSP  # noqa: E402
import cpk_write  # noqa: E402
from test_configst_pack import make_pac  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402


class EnvelopeLimitTests(unittest.TestCase):
    def test_limit_is_the_original_rounded_up_to_a_sector(self):
        self.assertEqual(BTP.envelope_limit(247_936), 249_856)  # v9 config01: crashed at 249 984
        self.assertEqual(BTP.envelope_limit(157_824), 159_744)  # v9 config02: crashed at 159 872
        self.assertEqual(BTP.envelope_limit(80_000), 81_920)
        self.assertEqual(BTP.envelope_limit(249_856), 249_856)  # already on the boundary

    def test_both_v9_crashers_sat_exactly_one_quantum_over(self):
        for orig, crash in ((247_936, 249_984), (157_824, 159_872)):
            self.assertGreater(crash, BTP.envelope_limit(orig))
            self.assertEqual(crash - BTP.envelope_limit(orig), 128)


class EnvelopeDroppableTests(unittest.TestCase):
    def test_spare_viewer_slot_parts_of_dictionary_members(self):
        for member in ("srwDL_CharaDictionary02.bin", "srw_DL_RoboDictionary02.bin"):
            for part in ("voice_actor", "alt_name", "short_name", "note", "type", "name_narrow"):
                row = {"part": part, "source": {"member": member}}
                self.assertTrue(BTP.envelope_droppable(row), (member, part))

    def test_core_rows_and_other_members_stay(self):
        for member, part in (("srwDL_CharaDictionary02.bin", "name"),
                             ("srwDL_CharaDictionary02.bin", "nickname"),
                             ("srwDL_CharaDictionary02.bin", "series"),
                             ("srw_DL_RoboDictionary02.bin", "series"),
                             ("srw_DL_RoboDictionary02.bin", "length"),
                             ("srw_DL_RoboDictionary02.bin", "weight"),
                             ("srw_DL_RoboDictionary02.bin", "name"),
                             ("unit_list02.bin", "voice_actor"),
                             ("srwDL_DLC_ID02.bin", "text")):
            row = {"part": part, "source": {"member": member}}
            self.assertFalse(BTP.envelope_droppable(row), (member, part))

    def test_mirror_duplicated_rows_of_dictionary_members_are_droppable(self):
        row = {"mirrored_from": "imenu02.EDAT", "part": "text",
               "source": {"member": "srwDL_CharaDictionary02.bin"}}
        self.assertTrue(BTP.envelope_droppable(row))
        # the gate stays conservative outside the dictionary members
        row = {"mirrored_from": "imenu02.EDAT", "part": "text",
               "source": {"member": "srwDL_DLC_ID02.bin"}}
        self.assertFalse(BTP.envelope_droppable(row))


class TrimPacTailTests(unittest.TestCase):
    def _cpk_with_pac(self, subs, tail_pad: int) -> bytes:
        pac = make_pac(subs) + b"\x00" * tail_pad
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config09.EDAT"
            path.write_bytes(build_synthetic_cpk(
                [{"dir": "", "name": "config09.pac", "data": pac, "id": 0}]))
            return path.read_bytes()

    def test_trims_the_tail_and_keeps_every_sub_file(self):
        subs = [("unit_list09.bin", b"\x01" * 300), ("srwDL_Item09.bin", b"\x02" * 2100)]
        container = self._cpk_with_pac(subs, tail_pad=1500)
        trimmed = BTP.trim_pac_tail(container)
        self.assertIsNotNone(trimmed)
        self.assertLess(len(trimmed), len(container))
        before = CSP.parse_pac(struct.unpack_from("<I", container, 0) and
                               self._member_pac(container))
        after = CSP.parse_pac(self._member_pac(trimmed))
        self.assertEqual([(s["name"], s["offset"], s["size"]) for s in before["subs"]],
                         [(s["name"], s["offset"], s["size"]) for s in after["subs"]])
        self.assertEqual([s["data"] for s in before["subs"]], [s["data"] for s in after["subs"]])

    def _member_pac(self, container: bytes) -> bytes:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.cpk"
            path.write_bytes(container)
            cpk = cpk_write.load(path)
            return cpk_write.decompressed(cpk.members[0].blob)

    def test_container_without_a_pac_member_yields_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plain.cpk"
            path.write_bytes(build_synthetic_cpk(
                [{"dir": "", "name": "data.bin", "data": b"\x01" * 64, "id": 0}]))
            self.assertIsNone(BTP.trim_pac_tail(path.read_bytes()))

    def test_pac_without_a_tail_pad_yields_none(self):
        # the last sub-file ends exactly on the 0x800 boundary: nothing to reclaim
        container = self._cpk_with_pac([("a.bin", b"\x01" * 2048)], tail_pad=0)
        self.assertIsNone(BTP.trim_pac_tail(container))


if __name__ == "__main__":
    unittest.main()
