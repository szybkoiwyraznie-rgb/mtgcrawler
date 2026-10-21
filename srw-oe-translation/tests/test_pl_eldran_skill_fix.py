"""Tests for the 2026-10-21 Polish 'Eldoran' -> 'Eldran' 11-field skill fix (v2.7-PL6)."""
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(TOOLS_DIR / "archive"))

import inline_names as IA
import item_skill_records as ISR
import pl_release_package as R
import pl_text
import speaker_map as SMF
import table_view as TV
import translation_check as C
import translation_import as TI


class EldranSkillFixTests(unittest.TestCase):
    def test_exact_eleven_translator_view_fields_and_minus_one_byte_budget(self):
        plan_json = json.loads(
            (ROOT / "config" / "pl" / "ui-eldran-skills-2026-10-21.json").read_text(encoding="utf-8")
        )
        self.assertEqual(plan_json["schema"], 1)
        self.assertEqual(len(plan_json["changes"]), 11)

        with tempfile.TemporaryDirectory() as td:
            mat_dir = Path(td) / "pakiet_PL"
            cov = R.materialize(ROOT / "pakiet_EN", ROOT / "pakiet_PL", mat_dir)
            self.assertEqual(cov["totals"]["errors"], 0)

            rows, by_file = TI.load_rows(mat_dir)
            view_plan = TV.plan_from(by_file, lang="pl")

            expected_locations = [
                ("umiejetnosci.md", 220, 3, False, "＠4%s0 Warunek: roboty Eldran x4\n%s Nie do wsparcia ataku", 57),
                ("teksty-config.md", 17, 683, False, "＠4%s0 Warunek: roboty Eldran x4\n%s Nie do wsparcia ataku", 57),
                ("teksty-config.md", 17, 3971, True, " Warunek: roboty Eldran x", 25),
            ] + [
                ("teksty-config.md", g, 384, True, " Warunek: roboty Eldran x", 25)
                for g in range(18, 26)
            ]

            for view_name, grp_no, elem_no, has_leading_space, expected_pl, expected_bytes in expected_locations:
                elem = view_plan[view_name][grp_no - 1][elem_no - 1]
                self.assertEqual(len(elem), 1)
                row = elem[0]
                self.assertEqual(row["pl"], expected_pl)
                encoded = pl_text.encode(row["pl"])
                self.assertEqual(len(encoded), expected_bytes)
                if has_leading_space:
                    self.assertTrue(row["pl"].startswith(" "))
                    self.assertTrue(encoded.startswith(b" "))
                errors, _ = C.check_row(row, field="pl")
                self.assertEqual(errors, [])

            # No remaining 'Eldoran' anywhere in skill or config text tables.
            for fname in ("03_skills.jsonl", "04_config_text.jsonl"):
                for r in by_file[fname]:
                    self.assertNotIn("Eldoran", r.get("pl") or "")

    def test_physical_skill_containers_patch_and_readback_when_present(self):
        containers_dir = ROOT / "google_drive"
        names = ["config00.cpk"] + [f"config0{i}.EDAT" for i in range(1, 9)]
        if not all((containers_dir / nm).exists() for nm in names):
            self.skipTest("Original config00..08 containers not staged in google_drive/")

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            mat_dir = td_path / "pakiet_PL"
            R.materialize(ROOT / "pakiet_EN", ROOT / "pakiet_PL", mat_dir)
            in_dir = td_path / "in"
            out_dir = td_path / "out"
            in_dir.mkdir()
            for nm in names:
                (in_dir / nm).symlink_to((containers_dir / nm).resolve())
            res = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "build_translation_patch.py"),
                    "--dlc", str(in_dir),
                    "--package", str(mat_dir),
                    "--out", str(out_dir),
                    "--lang", "pl",
                    "--no-exe",
                    "--no-ui-textures",
                    "--only", *names,
                ],
                check=False,
            )
            build_report = json.loads((out_dir / "build_report.json").read_text(encoding="utf-8"))
            self.assertEqual(build_report["problems"], ["font: NOT written: no ISO given"])
            self.assertEqual(res.returncode, 1)
            for idx, nm in enumerate(names):
                target_member = f"srwDL_Skill0{idx}.bin"
                patched_blob = None
                for cm, cb in SMF.read_members(out_dir / "DLC" / nm):
                    sub = IA.pac_subfiles(cb) if cm.lower().endswith(".pac") else [(cm, cb)]
                    for sub_name, sub_data in sub:
                        if sub_name == target_member:
                            patched_blob = sub_data
                            break
                self.assertIsNotNone(patched_blob, target_member)
                parsed = ISR.parse_member(patched_blob, "skill", target_member)
                _, pool = ISR.parse_tail_pool(patched_blob, parsed["tail_offset"])
                decoded_pool = [pl_text.decode(p) for p in pool]
                self.assertIn(" Warunek: roboty Eldran x", decoded_pool)
                self.assertFalse(any("Eldoran" in s for s in decoded_pool))
                if idx == 0:
                    rec219 = parsed["records"][219]
                    raw_rec = patched_blob[rec219["offset"] : rec219["offset"] + rec219["length"]]
                    str_offs = struct.unpack_from("<6H", raw_rec, 40)
                    eff_raw = patched_blob[rec219["offset"] + str_offs[2] :].split(b"\0", 1)[0]
                    self.assertEqual(
                        pl_text.decode(eff_raw),
                        "＠4%s0 Warunek: roboty Eldran x4\n%s Nie do wsparcia ataku",
                    )


if __name__ == "__main__":
    unittest.main()
