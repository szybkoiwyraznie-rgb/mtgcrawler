from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

SRW_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = SRW_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import pilot_catalog as PC
import verify_pilot_catalog as VPC


def _build_synthetic_charalist(
    *,
    key: int = 500,
    portrait_ref: int = 500,
    player_override_key: int = 0,
    default_level: int = 1,
    base_sp: int = 50,
    sp_growth: int = 1,
    morale_base: int = 100,
    stats: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]] = (
        (118, 20),
        (76, 10),
        (124, 20),
        (62, 10),
    ),
    spirits: list[tuple[int, int, int]] | None = None,
    skills: list[tuple[int, int, int]] | None = None,
    ace_alias: int = 571,
    paired_form_key: int = 0,
) -> bytes:
    buf = bytearray(172)
    struct.pack_into("<hHH", buf, 96, key, portrait_ref, player_override_key)
    buf[104] = default_level
    buf[105] = base_sp
    buf[106] = sp_growth
    buf[107] = morale_base
    for idx, (b, r) in enumerate(stats):
        buf[108 + 2 * idx] = b
        buf[109 + 2 * idx] = r
    for s_idx, (fam, learn_lv, step) in enumerate(spirits or []):
        buf[116 + s_idx] = fam
        buf[120 + s_idx] = learn_lv
        buf[124 + s_idx] = step
    for k_idx, (alias_id, learn_lv, step) in enumerate(skills or []):
        struct.pack_into("<h", buf, 128 + 2 * k_idx, alias_id)
        buf[136 + k_idx] = learn_lv
        buf[140 + k_idx] = step
    struct.pack_into("<hH", buf, 156, ace_alias, paired_form_key)
    return bytes(buf)


def _build_synthetic_spirit_table(families: list[int]) -> tuple[bytes, list[dict]]:
    blob = bytearray()
    records = []
    for fam in families:
        for tier in (1, 2, 3):
            off = len(blob)
            rec = bytearray(52)
            struct.pack_into("<HHh", rec, 2, fam, fam * 10 + tier, tier)
            rec[12] = 10 * tier
            blob.extend(rec)
            records.append({"offset": off, "length": 52})
    return bytes(blob), records


class SyntheticPilotCatalogTests(unittest.TestCase):
    """Pure-stdlib unit tests that always execute without external game binaries."""

    def test_sp_and_hardware_float32_stat_formulas(self) -> None:
        self.assertEqual(PC.sp_at_level(50, 1, 1), 50)
        self.assertEqual(PC.sp_at_level(50, 1, 50), 99)
        self.assertEqual(PC.sp_at_level(50, 1, 99), 148)
        self.assertEqual(PC.sp_at_level(90, 2, 99), 286)

        # Verify exact IEEE-754 binary32 0x3dcccccd rounding parity across all rates & levels.
        for rate in range(0, 45):
            for lv in range(1, 100):
                self.assertEqual(
                    PC.stat_at_level(100, rate, lv),
                    VPC.independent_f32_stat(100, rate, lv),
                )

    def test_charalist_parser_and_step_zero_unlocks(self) -> None:
        raw = _build_synthetic_charalist(
            key=3401,
            player_override_key=0,
            spirits=[(7, 1, 24), (2, 10, 0)],
            skills=[(684, 3, 9), (400, 15, 0)],
            ace_alias=578,
            paired_form_key=526,
        )
        parsed = PC.parse_charalist_record(raw)
        self.assertEqual(parsed["key"], 3401)
        self.assertEqual(parsed["ace_alias"], 578)
        self.assertEqual(parsed["paired_form_key"], 526)
        self.assertEqual(len(parsed["spirit_slots"]), 2)
        self.assertEqual(len(parsed["skill_slots"]), 2)

        # Spirit step > 0 vs step == 0
        self.assertEqual(
            [x["unlock_level"] for x in PC.spirit_unlock_schedule(1, 24)],
            [1, 25, 49],
        )
        self.assertEqual(
            [x["unlock_level"] for x in PC.spirit_unlock_schedule(10, 0)],
            [10, 10, 10],
        )

    def test_skill_selector_and_runtime_progression_evaluator(self) -> None:
        skills = [
            {"alias_id": 684, "key": 2970, "level": 65535},  # -1 header skipped
            *[
                {"alias_id": 684, "key": 2970 + lv, "level": lv}
                for lv in range(1, 10)
            ],
            {"alias_id": 685, "key": 2980, "level": 65535},
            *[
                {"alias_id": 685, "key": 2980 + lv, "level": lv}
                for lv in range(1, 10)
            ],
            {"alias_id": 400, "key": 1800, "level": 0},
            {"alias_id": 578, "key": 2100, "level": 0},
        ]
        spirit_bin, spirit_records = _build_synthetic_spirit_table([7, 2])

        enemy_raw = _build_synthetic_charalist(
            key=405,
            player_override_key=406,
            base_sp=40,
            spirits=[],
            skills=[(684, 3, 9)],
            ace_alias=0,
        )
        ally_raw = _build_synthetic_charalist(
            key=406,
            player_override_key=0,
            base_sp=60,
            spirits=[(7, 1, 24), (2, 10, 0)],
            skills=[(684, 3, 9), (400, 15, 0)],
            ace_alias=578,
        )
        by_key = {405: enemy_raw, 406: ally_raw}

        # On enemy side: stays on 405, no spirits, no Ace even with 500 kills.
        st_enemy = PC.evaluate_pilot_at_level(
            enemy_raw,
            by_key,
            skills,
            spirit_records,
            spirit_bin,
            level=20,
            is_enemy=True,
            kills=500,
        )
        self.assertEqual(st_enemy["sp"], 59)
        self.assertEqual(st_enemy["spirits"], [])
        self.assertFalse(st_enemy["ace_active"])
        self.assertEqual(st_enemy["ace_skill_record"], -1)
        self.assertEqual(skills[st_enemy["skill_records"][0]]["key"], 2972)

        # On player side: redirects to 406, unlocks all 3 tiers of step==0 spirit at lv 10,
        # upgrades 0x2ac -> 0x2ad when flag 0x461 is active, activates Ace at kills >= 300.
        st_ally_299 = PC.evaluate_pilot_at_level(
            enemy_raw,
            by_key,
            skills,
            spirit_records,
            spirit_bin,
            level=20,
            is_enemy=False,
            kills=299,
            story_flag_461=True,
        )
        self.assertFalse(st_ally_299["ace_active"])
        self.assertEqual(skills[st_ally_299["skill_records"][0]]["key"], 2982)
        self.assertEqual(skills[st_ally_299["skill_records"][1]]["key"], 1800)
        # Slot 0 has only Lv1 at lv=20; Slot 1 (step==0) has all 3 tiers at lv=20!
        self.assertEqual(len(st_ally_299["spirits"]), 4)

        st_ally_300 = PC.evaluate_pilot_at_level(
            enemy_raw,
            by_key,
            skills,
            spirit_records,
            spirit_bin,
            level=20,
            is_enemy=False,
            kills=300,
            story_flag_461=True,
        )
        self.assertTrue(st_ally_300["ace_active"])
        self.assertEqual(skills[st_ally_300["ace_skill_record"]]["key"], 2100)

    def test_base_spirit_effect_helper_strips_upgrade_tiers(self) -> None:
        raw_choice = (
            "Cel: ty Efekt: 1 tura\n"
            "Lv1 SP-15 Unik+20% Celność+25%\n"
            "Lv2 SP-20 Unik+30% Celność+35%\n"
            "Lv3 SP-25 Unik+40% Celność+45%"
        )
        self.assertEqual(
            PC._base_spirit_effect(raw_choice, 15),
            "Cel: ty Efekt: 1 tura — Unik+20% Celność+25%",
        )
        raw_growth = "Cel: ty Efekt: 1 razy\nLv1 SP-20 Ruch+3"
        self.assertEqual(
            PC._base_spirit_effect(raw_growth, 20),
            "Cel: ty Efekt: 1 razy — Ruch+3",
        )

    def test_markdown_auditor_rejects_cjk_control_codes_and_missing_sections(self) -> None:
        valid_doc = (
            "## 1. Leksykon wszystkich Komend Ducha (20 rodzin / 60 poziomów)\n"
            "## 2. Leksykon wszystkich umiejętności pilotów i Premii Asa (80 rodzin)\n"
            "## 3. Piloci grywalni — profile główne (92 profile)\n"
            "#### Jin Hyuga `[ID 500]`\n"
            "## 4. Podpiloci i załoga wsparcia (45 profili)\n"
            "## 5. Piloci wrodzy, rywale i bossowie (117 profili bojowych)\n"
            "## 6. Dodatek A — Rekordy niebojowe, portretowe i systemowe (150 rekordów)\n"
            "| 999 | Test | Seria | — |\n"
            "## 7. Pochodzenie danych i ograniczenia\n"
        )
        res = VPC.audit_markdown_document(valid_doc, [500], [999])
        self.assertEqual(res["combat_pilot_headings_verified"], 1)

        with self.assertRaisesRegex(ValueError, "CJK"):
            VPC.audit_markdown_document(valid_doc + "\n熱血\n", [500], [999])
        with self.assertRaisesRegex(ValueError, "control"):
            VPC.audit_markdown_document(valid_doc + "\n＠1Celność\n", [500], [999])
        with self.assertRaisesRegex(ValueError, "heading"):
            VPC.audit_markdown_document(valid_doc, [500, 501], [999])


class RealBinaryPilotCatalogTests(unittest.TestCase):
    """End-to-end verification tests against real 1.08 game containers when present."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.containers = SRW_ROOT / "google_drive"
        cls.elf = SRW_ROOT / "local" / "eboot_108.elf"
        cls.en_pkg = SRW_ROOT / "pakiet_EN"
        cls.pl_pkg = SRW_ROOT / "local" / "pakiet_PL"
        cls.source_manifest = SRW_ROOT / "docs" / "mech-catalog" / "source-inventory.json"
        cls.engine_map = SRW_ROOT / "docs" / "pilot-catalog" / "engine-map.json"
        if not (cls.containers.exists() and cls.elf.exists() and cls.pl_pkg.exists()):
            raise unittest.SkipTest("Local ignored game binaries not staged in workspace")

    def test_full_polish_pilot_catalog_and_independent_auditor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md_path = Path(tmp) / "srwoe_pilot_catalog_PL.md"
            model_path = Path(tmp) / "model.json"
            model = PC.build_pilot_model(
                self.containers,
                self.en_pkg,
                self.pl_pkg,
                self.elf.read_bytes(),
                json.loads(self.engine_map.read_text(encoding="utf-8")),
            )
            md_text = PC.render_polish_markdown(model)
            md_path.write_text(md_text, encoding="utf-8")
            model_path.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")

            report = VPC.verify(
                containers_dir=self.containers,
                elf_path=self.elf,
                english_package=self.en_pkg,
                polish_package=self.pl_pkg,
                source_manifest_path=self.source_manifest,
                engine_map_path=self.engine_map,
                markdown_path=md_path,
                model_json_path=model_path,
                replay_unicorn=False,
            )
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["counts"]["total_characters"], 404)
            self.assertEqual(report["counts"]["playable_total"], 92)
            self.assertEqual(report["counts"]["sub_pilot"], 45)
            self.assertEqual(report["counts"]["enemy_total"], 117)
            self.assertEqual(report["counts"]["non_combat"], 150)

            # Tampering a single stat cell must fail verification immediately.
            import re as _re
            tampered = _re.sub(r"(\|\s*\*\*Atak\*\*\s*\|\s*)120(\s*\|)", r"\g<1>999\2", md_text, count=1)
            self.assertNotEqual(tampered, md_text)
            md_path.write_text(tampered, encoding="utf-8")
            with self.assertRaises(ValueError):
                VPC.verify(
                    containers_dir=self.containers,
                    elf_path=self.elf,
                    english_package=self.en_pkg,
                    polish_package=self.pl_pkg,
                    source_manifest_path=self.source_manifest,
                    engine_map_path=self.engine_map,
                    markdown_path=md_path,
                )


if __name__ == "__main__":
    unittest.main()
