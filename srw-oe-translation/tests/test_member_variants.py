"""member_variants: bisection inside one convention-B member (size / records / pool / names / effects)."""
from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import container_mix as CM  # noqa: E402
import item_skill_records as ISR  # noqa: E402
import item_skill_write as ISW  # noqa: E402
import member_variants as MV  # noqa: E402
from test_configst_pack import make_pac  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402
from test_item_skill_write import build_member, build_record  # noqa: E402

MEMBER = "srwDL_Skill00.bin"


def container(skill_blob: bytes) -> bytes:
    pac = make_pac([("a.bin", b"\x01" * 100), (MEMBER, skill_blob), ("z.bin", b"\x02" * 50)])
    return build_synthetic_cpk([{"dir": "", "name": "config00.pac", "data": pac, "id": 0}])


class MemberVariantsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        records = [build_record("skill", 1000 + i, f"技{i}", f"効果{i}", name_level=f"技{i} Lv1",
                                effect_brief=f"短{i}") for i in range(4)]
        self.original = build_member("skill", records, ["気力", "命中"])
        edits = {i: {"name": f"Skill number {i}", "name_level": f"Skill number {i} Lv1",
                     "effect": f"A much longer English effect text {i}", "effect_brief": f"Brief {i}"}
                 for i in range(4)}
        grown, _ = ISW.rebuild_member(self.original, "skill", edits, MEMBER)
        parsed = ISR.parse_member(grown, "skill", MEMBER)
        self.built = grown[:parsed["tail_offset"]] + ISR.build_tail_pool(
            parsed["tail_offset"], [b"Will", b"Hit"])
        self.orig_path = self.root / "orig.cpk"
        self.built_path = self.root / "built.cpk"
        self.orig_path.write_bytes(container(self.original))
        self.built_path.write_bytes(container(self.built))

    def fields(self, blob):
        parsed = ISR.parse_member(blob, "skill", MEMBER)
        return [MV.field_bytes(blob, row) for row in parsed["records"]]

    def pool(self, blob):
        parsed = ISR.parse_member(blob, "skill", MEMBER)
        return ISR.parse_tail_pool(blob, parsed["tail_offset"])[1]

    def test_every_variant_changes_only_what_it_says(self):
        fo, fb = self.fields(self.original), self.fields(self.built)
        po, pb = self.pool(self.original), self.pool(self.built)
        out = {name: MV.make_variant(name, self.original, self.built, "skill", MEMBER) for name in MV.VARIANTS}
        self.assertEqual(out["pad"], self.original + b"\x00" * (len(self.built) - len(self.original)))
        self.assertEqual(self.fields(out["rec_en_pool_jp"]), fb)
        self.assertEqual(self.pool(out["rec_en_pool_jp"]), po)
        self.assertEqual(self.fields(out["rec_jp_pool_en"]), fo)
        self.assertEqual(self.pool(out["rec_jp_pool_en"]), pb)
        for i, f in enumerate(self.fields(out["names_only"])):
            self.assertEqual((f["name"], f["name_level"]), (fb[i]["name"], fb[i]["name_level"]))
            self.assertEqual((f["effect"], f["effect_brief"], f["label"]),
                             (fo[i]["effect"], fo[i]["effect_brief"], fo[i]["label"]))
        for i, f in enumerate(self.fields(out["effects_only"])):
            self.assertEqual((f["name"], f["name_level"]), (fo[i]["name"], fo[i]["name_level"]))
            self.assertEqual(f["effect"], fb[i]["effect"])
        self.assertEqual(self.fields(out["half_a"]), fb[:2] + fo[2:])
        self.assertEqual(self.fields(out["half_b"]), fo[:2] + fb[2:])
        for name in MV.VARIANTS:
            if name != "pad":
                self.assertEqual(self.pool(out[name]), pb if name == "rec_jp_pool_en" else po)
                parsed = ISR.parse_member(out[name], "skill", MEMBER)
                self.assertEqual(ISW.pool_pointer_faults(out[name], parsed), [], name)

    def test_containers_differ_from_the_original_only_in_the_member(self):
        reports = MV.build_all(self.orig_path, self.built_path, MEMBER, self.root / "out")
        self.assertEqual([r["label"] for r in reports], ["S1", "S2", "S3", "S4", "S5", "S6", "S7"])
        _c, orig_members, _p = CM.members_of(self.orig_path)
        for report in reports:
            path = self.root / "out" / report["label"] / "orig.cpk"
            _c, members, _p = CM.members_of(path)
            self.assertEqual(members["a.bin"], orig_members["a.bin"])
            self.assertEqual(members["z.bin"], orig_members["z.bin"])
            self.assertEqual(len(members[MEMBER]), report["member_variant"]["size"])
            self.assertTrue(path.with_name("orig.cpk.variant.json").exists())
        self.assertEqual(reports[0]["member_variant"]["size"], len(self.built))

    def test_identical_members_are_refused(self):
        with self.assertRaises(MV.VariantError):
            MV.build_all(self.orig_path, self.orig_path, MEMBER, self.root / "x")

    def test_cli_prints_sizes_only(self):
        rc = MV.main(["--original", str(self.orig_path), "--built", str(self.built_path),
                      "--member", MEMBER, "--out-dir", str(self.root / "cli"), "--variants", "pad", "names_only"])
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / "cli" / "S1" / "orig.cpk").exists())
        self.assertTrue((self.root / "cli" / "S2" / "orig.cpk").exists())

    def test_grow_with_spaces_adds_only_trailing_spaces_to_effects(self):
        size = len(self.original)
        grown = MV.grow_with_spaces(self.original, "skill", MEMBER, size + 8, max_field=64, max_line=64)
        self.assertEqual(len(grown), size + 8)
        fo, fg = self.fields(self.original), self.fields(grown)
        for i, (a, b) in enumerate(zip(fo, fg)):
            for role in ISR.FIELDS:
                if role == "effect":
                    self.assertTrue(b[role].startswith(a[role]))
                    self.assertEqual(b[role][len(a[role]):], b" " * (4 if i < 2 else 0), i)
                else:
                    self.assertEqual(a[role], b[role], (i, role))
        self.assertEqual(self.pool(grown), self.pool(self.original))
        parsed = ISR.parse_member(grown, "skill", MEMBER)
        self.assertEqual(ISW.pool_pointer_faults(grown, parsed), [])
        # the parameter pointer (+52) moved with the grown effects (Y3 -> Y5, 2026-10-15)
        self.assertEqual(ISW.parameter_pointer_faults(grown, parsed), [])
        po = ISR.parse_member(self.original, "skill", MEMBER)
        for a, b in zip(po["records"], parsed["records"]):
            delta_a = struct.unpack_from("<H", self.original, a["offset"] + 52)[0] - a["boundaries"][-1]
            delta_b = struct.unpack_from("<H", grown, b["offset"] + 52)[0] - b["boundaries"][-1]
            self.assertEqual(delta_a, delta_b)
        # round robin keeps every effect under the caps; a cap that is already full refuses
        # (each 5-byte effect has room for 8 spaces under a 16-byte cap: 4 records x 8 = 32)
        big = MV.grow_with_spaces(self.original, "skill", MEMBER, size + 32, max_field=16, max_line=16)
        self.assertEqual([len(f["effect"]) for f in self.fields(big)], [13] * 4)
        with self.assertRaises(MV.VariantError):
            MV.grow_with_spaces(self.original, "skill", MEMBER, size + 6, max_field=64, max_line=64)
        with self.assertRaises(MV.VariantError):
            MV.grow_with_spaces(self.original, "skill", MEMBER, size + 8)   # own maximum: no room
        with self.assertRaises(MV.VariantError):
            MV.grow_with_spaces(self.original, "skill", MEMBER, size + 4000, max_field=16, max_line=16)

    def test_build_ladder_writes_one_container_per_size_with_other_members_untouched(self):
        size = len(self.original)
        out = self.root / "ladder"
        reports = MV.build_ladder(self.orig_path, MEMBER, [size + 8, size + 16], out, max_field=64, max_line=64)
        self.assertEqual([r["label"] for r in reports], ["T1", "T2"])
        _c, orig_members, _p = CM.members_of(self.orig_path)
        for report, want in zip(reports, (size + 8, size + 16)):
            path = out / report["label"] / "orig.cpk"
            self.assertTrue(path.exists())
            self.assertTrue(path.with_name("orig.cpk.variant.json").exists())
            _c2, members, _p2 = CM.members_of(path)
            self.assertEqual(len(members[MEMBER]), want)
            self.assertEqual(report["member_variant"]["size"], want)
            for name, data in orig_members.items():
                if name != MEMBER:
                    self.assertEqual(members[name], data, name)


if __name__ == "__main__":
    unittest.main()
