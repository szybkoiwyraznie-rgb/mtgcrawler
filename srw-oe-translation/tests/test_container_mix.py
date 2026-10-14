"""container_mix: sub-file recombination of an original and a built container (bisection)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import configst_pack as CSP  # noqa: E402
import container_mix as CM  # noqa: E402
import cpk_write  # noqa: E402
from test_configst_pack import make_pac  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402


def container(subs) -> bytes:
    pac = make_pac(subs)
    return build_synthetic_cpk([{"dir": "", "name": "config00.pac", "data": pac, "id": 0}])


ORIGINAL = [("a.bin", b"\x01" * 100), ("srwDL_DLC_ID00.bin", b"\x02" * 500),
            ("srwDL_Skill00.bin", b"\x03" * 3000), ("unit_list00.bin", b"\x04" * 384)]
BUILT = [("a.bin", b"\x01" * 100), ("srwDL_DLC_ID00.bin", b"\x05" * 480),
         ("srwDL_Skill00.bin", b"\x06" * 5000), ("unit_list00.bin", b"\x07" * 384)]


class ContainerMixTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.original = self.root / "orig.cpk"
        self.built = self.root / "built.cpk"
        self.original.write_bytes(container(ORIGINAL))
        self.built.write_bytes(container(BUILT))

    def subs_of(self, data: bytes) -> dict:
        path = self.root / "probe.cpk"
        path.write_bytes(data)
        _cpk, members, pac = CM.members_of(path)
        self.assertEqual(pac, "config00.pac")
        return members

    def test_nothing_taken_is_the_original_verbatim(self):
        out, report = CM.mix(self.original, self.built, [], [])
        self.assertEqual(out, self.original.read_bytes())
        self.assertEqual(report["taken"], [])
        self.assertEqual(report["changed_by_build"],
                         ["srwDL_DLC_ID00.bin", "srwDL_Skill00.bin", "unit_list00.bin"])

    def test_everything_taken_reproduces_the_build(self):
        out, report = CM.mix(self.original, self.built, ["*"], [])
        self.assertEqual(self.subs_of(out), self.subs_of(self.built.read_bytes()))
        self.assertEqual(len(report["taken"]), 3)

    def test_one_member_taken_keeps_the_rest_original(self):
        out, report = CM.mix(self.original, self.built, ["srwDL_DLC_ID00.bin"], [])
        subs = self.subs_of(out)
        self.assertEqual(subs["srwDL_DLC_ID00.bin"], b"\x05" * 480)
        self.assertEqual(subs["srwDL_Skill00.bin"], b"\x03" * 3000)
        self.assertEqual(subs["unit_list00.bin"], b"\x04" * 384)
        self.assertEqual(report["taken"], ["srwDL_DLC_ID00.bin"])
        self.assertEqual([r["source"] for r in report["members"]],
                         ["original", "built", "original", "original"])

    def test_keep_wins_over_take(self):
        out, report = CM.mix(self.original, self.built, ["*"], ["srwDL_Skill*"])
        subs = self.subs_of(out)
        self.assertEqual(subs["srwDL_Skill00.bin"], b"\x03" * 3000)
        self.assertEqual(subs["srwDL_DLC_ID00.bin"], b"\x05" * 480)
        self.assertEqual(report["taken"], ["srwDL_DLC_ID00.bin", "unit_list00.bin"])

    def test_pad_only_keeps_content_and_matches_the_built_size(self):
        out, report = CM.mix(self.original, self.built, [], [], pad_only=True)
        subs = self.subs_of(out)
        self.assertEqual(subs, self.subs_of(self.original.read_bytes()))
        built_pac = CSP.parse_pac(cpk_write.decompressed(
            cpk_write.load(self.built).members[0].blob))["orig_len"]
        self.assertEqual(report["pac_size"], built_pac)
        self.assertEqual(report["taken"], [])
        self.assertTrue(report["pad_only"])

    def test_cli_writes_the_container_and_a_report(self):
        out = self.root / "V1" / "config00.cpk"
        rc = CM.main(["--original", str(self.original), "--built", str(self.built),
                      "--take", "unit_list00.bin", "--out", str(out)])
        self.assertEqual(rc, 0)
        self.assertTrue(out.exists())
        report = json.loads(out.with_name("config00.cpk.mix.json").read_text(encoding="utf-8"))
        self.assertEqual(report["taken"], ["unit_list00.bin"])
        self.assertEqual(self.subs_of(out.read_bytes())["unit_list00.bin"], b"\x07" * 384)

    def test_mismatched_containers_are_refused(self):
        other = self.root / "other.cpk"
        other.write_bytes(container(ORIGINAL[:3]))
        with self.assertRaises(CM.MixError):
            CM.mix(self.original, other, ["*"], [])


if __name__ == "__main__":
    unittest.main()
