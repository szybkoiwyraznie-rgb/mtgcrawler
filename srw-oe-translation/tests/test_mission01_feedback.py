"""Regression contracts for mission 0-1 feedback (2026-10-17).

Synthetic binaries + the committed translation rows only; no game files or screenshots.
Screen budgets are conservative limits from the screenshots, not an emulator render test.
"""
from __future__ import annotations

import copy
import json
import struct
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))

import exe_strings as X
import slot_apply as SLA
import table_write as TW
import translation_check as TC
from exe_fixtures import Builder, cp932
from test_exe_strings import _row
from test_table_write import make_pool, make_record

# (DLC chapter container, both measured title offsets, expected English).
# The two fields are distinct even when they carry identical Japanese.
DLC_TITLES = [
    (1, (102, 114), "Chapter 2 Main Story"),
    (1, (424, 436), "Chapter 3 Main Story"),
    (1, (746, 758), "Chapter 4 Main Story"),
    (1, (1070, 1082), "Chapter 5 Main Story"),
    (1, (1398, 1410), "Chapter 6 Main Story"),
    (1, (1734, 1746), "Chapter 7 Main Story"),
    (1, (2054, 2066), "Chapter 8 Main Story"),
    (1, (2374, 2395), "Lelouch of the Rebellion"),
    (1, (2760, 2773), "The White Knight"),
    (1, (3102, 3128), "New Unit: Cybuster"),
    (2, (70, 89), "Rare Metal Mining"),
    (2, (446, 465), "The 30 Bunch Incident"),
    (3, (70, 94), "Operation Stop the Solar Ray"),
    (3, (446, 459), "The Nighthawk's Dream"),
    (4, (70, 95), "Return of the Goburiki Army"),
    (4, (450, 467), "The Bandits' Tragedy"),
    (5, (70, 83), "Trap on the Moon"),
    (5, (410, 439), "A New Knightmare Frame"),
    (6, (70, 89), "Unearthing the Sirbine"),
    (6, (446, 471), "Tactical Simulator Alpha"),
    (7, (66, 91), "Tactical Simulator Beta"),
]
NAME_MARKERS = ("＜主人公姓＞", "＜主人公名＞", "＜主人公愛称＞", "＜＜主人公名フルネーム＞＞")


def package_rows(name):
    with (ROOT / "pakiet_EN" / name).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


class EngineLiteralTests(unittest.TestCase):
    def test_export_preserves_name_marker_keys(self):
        b = Builder()
        for i, text in enumerate(NAME_MARKERS):
            b.ref_pair(b.string(str(i), cp932(text)), reg=4)
        rows, _ = X.extract_rows(X.Elf(b.build()))
        self.assertEqual({r["jp"] for r in rows}, set(NAME_MARKERS))
        for row in rows:
            self.assertEqual(row["en"], row["jp"])

    def test_rejects_translated_markers_and_punctuation(self):
        for text in NAME_MARKERS + ("・", "「", "　", "」"):
            with self.subTest(text=text):
                encoded, why = X.check_en(_row(text, "X"))
                self.assertIsNone(encoded)
                self.assertIn("engine literal", why)
                encoded, why = X.check_en(_row(text, text))
                self.assertIsNone(why)
                self.assertEqual(encoded, cp932(text))

    def test_checker_catches_old_package_even_though_it_fits_the_slot(self):
        errors, _ = TC.check_row(_row("＜主人公名＞", "<Hero Name>", slack=3))
        self.assertTrue(any("engine literal" in error for error in errors))

    def test_writer_and_cheat_refuse_translated_marker_without_changing_bytes(self):
        b = Builder()
        b.ref_pair(b.string("hero", cp932("＜主人公名＞")), reg=4)
        blob = b.build()
        rows, _ = X.extract_rows(X.Elf(blob))
        rows[0]["en"] = "<Hero Name>"
        after, report = X.apply_rows(blob, rows)
        self.assertEqual(after, blob)
        self.assertEqual(report["applied"], 0)
        self.assertEqual(len(report["skipped"]), 1)
        lines, _ = X.cheat_lines(blob, rows)
        self.assertEqual(lines, [])

    def test_safe_identity_does_not_modify_neighbouring_bytes(self):
        row = _row("＜主人公名＞", "＜主人公名＞", slack=3)
        row["source"]["offset"] = 4
        blob = b"HEAD" + cp932(row["jp"]) + b"\0" * 4 + b"TAIL"
        after, report = X.apply_rows(blob, [row])
        self.assertEqual(after, blob)
        self.assertEqual(report["skipped"], [])

    def test_does_not_freeze_visible_hero_menu_labels(self):
        encoded, why = X.check_en(_row("主人公名変更", "Rename Hero"))
        self.assertIsNone(why)
        self.assertTrue(encoded.startswith(b"Rename Hero"))


class ScreenBudgetTests(unittest.TestCase):
    CASES = (
        ("0x08bf7190", "敵", "Foe", "F."),
        ("0x08bf7194", "他", "Oth", "O."),
        ("0x08bf8598", "移動後", "Post-Mv", "P-Mv"),
    )

    def test_storage_slack_does_not_override_screen_limits(self):
        for addr, jp, old, new in self.CASES:
            with self.subTest(addr=addr):
                row = _row(jp, old, slack=1)
                row["source"]["vaddr"] = addr
                self.assertIn("too wide for the UI", X.check_en(row)[1])
                self.assertTrue(TC.check_row(row)[0])
                row["en"] = new
                encoded, why = X.check_en(row)
                self.assertIsNone(why)
                self.assertEqual(encoded.rstrip(b"\0"), new.encode("ascii"))
                self.assertEqual(len(encoded), len(cp932(jp)) + 1)

    def test_other_enemy_labels_keep_their_separate_budget(self):
        row = _row("敵", "Foe", slack=1)
        row["source"]["vaddr"] = "0x08bf8594"
        self.assertEqual(X.check_en(row), (b"Foe", None))


class PackageFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe = package_rows("09_executable.jsonl")
        cls.config = {r["id"]: r for r in package_rows("04_config_text.jsonl")}
        cls.missions = {r["id"]: r for r in package_rows("05_mission_text.jsonl")}

    def test_package_preserves_all_engine_literals(self):
        by = {r["jp"]: r for r in self.exe}
        for text in NAME_MARKERS:
            self.assertEqual(by[text]["en"], text)
        by_address = {r["source"]["vaddr"]: r for r in self.exe}
        for address in ("0x08bf9fbc", "0x08bf9fc0", "0x08bf9fc4", "0x08bf9fc8"):
            row = by_address[address]
            self.assertEqual(row["en"], row["jp"])
        # Other copies of the full-width space are deliberately unfilled: the writer skips
        # them and keeps the original bytes. Never collapse those distinct rows by jp.
        for row in self.exe:
            if row["jp"] in X.ENGINE_LITERALS:
                self.assertIn(row["en"], ("", row["jp"]))

    def test_himari_line_still_uses_player_name_not_a_hardcoded_default(self):
        with (ROOT / "pakiet_EN/00_dialogue.jsonl").open(encoding="utf-8") as handle:
            row = next(r for r in map(json.loads, handle)
                       if r["id"] == "dlg:eventP00.cpk/DL100_01.bin:2872")
        self.assertEqual(row["en"], "＜主人公名＞, can you hear me?")

    def test_package_screen_labels_fit_and_other_foe_labels_are_unchanged(self):
        by = {r["source"]["vaddr"]: r for r in self.exe}
        for addr, _, _, new in ScreenBudgetTests.CASES:
            self.assertEqual(by[addr]["en"], new)
            self.assertIsNone(X.check_en(by[addr])[1])
        self.assertEqual(by["0x08bf8594"]["en"], "Foe")

    def test_all_21_dlc_titles_have_both_copies_and_consistent_copy_of(self):
        for chapter, offsets, english in DLC_TITLES:
            for offset in offsets:
                key = f"dlc_id:config{chapter:02}.EDAT/srwDL_DLC_ID{chapter:02}.bin:{offset}"
                with self.subTest(key=key):
                    row = self.config[key]
                    self.assertEqual(row["en"], english)
                    self.assertEqual(TC.check_row(row)[0], [])
                    if row.get("copy_of"):
                        self.assertEqual(row["en"], self.config[row["copy_of"]]["en"])

    def test_dlc_title_writes_keep_description_ids_flags_and_other_fields(self):
        for chapter, offsets, english in DLC_TITLES:
            with self.subTest(chapter=chapter, offsets=offsets):
                name = f"srwDL_DLC_ID{chapter:02}.bin"
                rows = [copy.deepcopy(self.config[f"dlc_id:config{chapter:02}.EDAT/{name}:{off}"])
                        for off in offsets]
                fields = [cp932(rows[0]["jp"])] * 2 + [cp932("説明"), b"", b"TEST-CONTENT-ID", b"", b"", b""]
                extra = struct.pack("<6I", 5000, 73, 1, 2, 200, 4) + b"\0\0"
                blob = make_pool([make_record(fields, extra=extra, nptr=8)])
                family = TW.family_of(name)
                self.assertEqual(TW.rebuild_pool(blob, family), blob)
                record = TW.parse_pool(blob, family)[0]
                start = TW.record_spans(blob)[0][0]
                for slot, row in enumerate(rows):
                    row["source"]["offset"] = start + record.pointers[slot]
                after, report = TW.apply_member(blob, name, rows)
                self.assertEqual(report["problems"], [])
                self.assertEqual(report["refused"], [])
                self.assertEqual(report["edits"], 2)
                result = TW.parse_pool(after, family)[0]
                self.assertEqual(result.strings[:2], [english.encode("ascii")] * 2)
                self.assertEqual(result.strings[2:], fields[2:])
                self.assertEqual(result.prefix[32:], record.prefix[32:])

    def test_training_menu_and_title_card_are_separate_translated_targets(self):
        menu = self.missions["mission_title:config00.cpk/milstP00.bin:r1:title"]
        card = self.missions["mission_note:eventP00.cpk/DL100_01_ext.dat:r0:title"]
        self.assertEqual(menu["en"], "Basic Training")
        self.assertEqual(card["en"], menu["en"])
        self.assertEqual(card["max_bytes"], 39)
        self.assertEqual(card["source"]["offset"], 344)
        blob = bytearray(b"\0" * 388)
        blob[344:352] = cp932(card["jp"])
        blob[384:] = struct.pack("<HH", 3, 2)
        after, report = SLA.apply_member(bytes(blob), [card])
        self.assertEqual(report["refused"], [])
        self.assertEqual(report["applied"], 1)
        self.assertEqual(len(after), 388)
        self.assertEqual(after[:344], blob[:344])
        self.assertEqual(after[344:384].split(b"\0")[0], b"Basic Training")
        self.assertEqual(after[384:], blob[384:])


if __name__ == "__main__":
    unittest.main()
