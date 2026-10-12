#!/usr/bin/env python3
"""Tests for tools/iso_test_patch.py, end to end on synthetic data.

The tool exists so that the repository can hand out a working test disc without carrying any game
data.  These tests therefore build the whole chain out of invented parts -- a synthetic event
member with the measured framing, a synthetic container, a synthetic ISO -- and then check the two
things a user cares about: the lines in the spec are English in the ISO that comes out, and nothing
else in that ISO moved.  The hashes are the safety gate, so a wrong hash and an offset that lands
on nothing must both stop the run.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import event_text_apply as ETA  # noqa: E402
import iso_pack  # noqa: E402
import iso_test_patch  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402
from test_event_text_apply import member as synthetic_member  # noqa: E402

MEMBER = "DL100_01.bin"
CONTAINER_IN_ISO = "PSP_GAME/USRDIR/eventP00.cpk"
KEEP_IN_ISO = "PSP_GAME/USRDIR/keep.bin"
KEEP = b"nie ruszaj mnie"


def spec_for(container: bytes, member: bytes, lines) -> dict:
    return {
        "container": CONTAINER_IN_ISO,
        "member": MEMBER,
        "md5_container": hashlib.md5(container).hexdigest(),
        "md5_member": hashlib.md5(member).hexdigest(),
        "lines": lines,
    }


class IsoTestPatchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)

        self.lines = ["最初の行です。".encode("cp932"), "二番目の行です。".encode("cp932"),
                      "三番目の行です。".encode("cp932")]
        self.blob, self.offsets, _ = synthetic_member(self.lines, speakers=[7, 7, 7])
        self.container = build_synthetic_cpk([
            {"dir": "", "name": MEMBER, "data": self.blob, "id": 0},
            {"dir": "", "name": "other.bin", "data": b"Z" * 300, "id": 1},
        ])
        self.iso = self.area / "synthetic.iso"
        self.iso.write_bytes(iso_pack.build_iso({
            "PSP_GAME": {"USRDIR": {"eventP00.cpk": self.container, "keep.bin": KEEP},
                         "SYSDIR": {"EBOOT.BIN": b"boot"}},
            "UMD_DATA.BIN": b"DATA",
        }))
        self.iso_original = self.iso.read_bytes()
        self.out = self.area / "test.iso"
        self.spec = spec_for(self.container, self.blob, [
            {"offset": self.offsets[0], "text": "The first line."},
            {"offset": self.offsets[1], "text": "The second line."},
        ])
        self.spec_path = self.area / "spec.json"
        self.spec_path.write_text(json.dumps(self.spec, ensure_ascii=False), encoding="utf-8")

    def read_back(self):
        """The event member as a player's game would see it in the ISO we wrote."""
        container = iso_pack.read_member(self.out, CONTAINER_IN_ISO)
        return container, ETA.parse_block_records(container)[0]

    def test_the_lines_in_the_spec_are_english_in_the_written_iso(self):
        report = iso_test_patch.apply_test_patch(self.iso, self.out, self.spec)
        self.assertEqual(report["apply"]["applied"], 2)
        self.assertEqual(report["changed_members"], [MEMBER])
        self.assertEqual(report["written"], str(self.out))
        container = iso_pack.read_member(self.out, CONTAINER_IN_ISO)
        texts = [ETA.text_of(container, record) for record in ETA.parse_block_records(container)[0]
                 if record["type"] == ETA.RECORD_TEXT]
        self.assertEqual(texts[0], b"The first line.")
        self.assertEqual(texts[1], b"The second line.")
        self.assertEqual(texts[2], self.lines[2])                 # untouched line stays Japanese

    def test_only_the_event_container_and_nothing_else_changes_in_the_iso(self):
        before_keep = iso_pack.read_member(self.iso, KEEP_IN_ISO)
        iso_test_patch.apply_test_patch(self.iso, self.out, self.spec)
        self.assertEqual(iso_pack.read_member(self.out, KEEP_IN_ISO), before_keep)
        self.assertEqual(self.iso.read_bytes(), self.iso_original)   # the input ISO is read-only
        with open(self.out, "rb") as written:
            self.assertTrue(iso_pack._walk_record_offsets(written))

    def test_the_written_iso_holds_every_member_the_original_held(self):
        iso_test_patch.apply_test_patch(self.iso, self.out, self.spec)
        with open(self.iso, "rb") as before, open(self.out, "rb") as after:
            original = iso_pack._walk_record_offsets(before)
            written = iso_pack._walk_record_offsets(after)
        self.assertEqual(sorted(original), sorted(written))

    def test_a_container_from_another_edition_stops_the_run(self):
        spec = dict(self.spec, md5_container="0" * 32)
        with self.assertRaises(ValueError) as caught:
            iso_test_patch.apply_test_patch(self.iso, self.out, spec)
        self.assertIn("inna wersja gry", str(caught.exception))
        self.assertFalse(self.out.exists())

    def test_a_member_from_another_edition_stops_the_run(self):
        spec = dict(self.spec, md5_member="0" * 32)
        with self.assertRaises(ValueError) as caught:
            iso_test_patch.apply_test_patch(self.iso, self.out, spec)
        self.assertIn("inna wersja gry", str(caught.exception))
        self.assertFalse(self.out.exists())

    def test_an_offset_that_lands_on_nothing_stops_the_run(self):
        spec = dict(self.spec, lines=[{"offset": 4, "text": "Nowhere."}])
        with self.assertRaises(ValueError) as caught:
            iso_test_patch.apply_test_patch(self.iso, self.out, spec)
        self.assertIn("no dialogue record starts at 4", str(caught.exception))
        self.assertFalse(self.out.exists())

    def test_a_line_too_wide_for_the_box_stops_the_run(self):
        spec = dict(self.spec, lines=[{"offset": self.offsets[0], "text": "x" * 200}])
        with self.assertRaises(ValueError) as caught:
            iso_test_patch.apply_test_patch(self.iso, self.out, spec)
        self.assertIn("wtrysk nie wyszedl czysto", str(caught.exception))
        self.assertFalse(self.out.exists())

    def test_a_dry_run_checks_everything_and_writes_nothing(self):
        report = iso_test_patch.apply_test_patch(self.iso, self.out, self.spec, dry_run=True)
        self.assertEqual(report["apply"]["applied"], 2)
        self.assertIsNone(report["written"])
        self.assertFalse(self.out.exists())
        self.assertEqual(len(report["replaced"]), 2)

    def test_the_report_names_the_lines_it_replaced(self):
        report = iso_test_patch.apply_test_patch(self.iso, self.out, self.spec)
        self.assertEqual([jp for _offset, jp, _en in report["replaced"]],
                         ["最初の行です。", "二番目の行です。"])
        self.assertEqual([en for _offset, _jp, en in report["replaced"]],
                         ["The first line.", "The second line."])

    def test_the_shipped_spec_is_well_formed_and_carries_no_japanese(self):
        shipped = iso_test_patch.load_spec(iso_test_patch.DEFAULT_SPEC)
        self.assertEqual(shipped["member"], MEMBER)
        self.assertEqual(shipped["container"], CONTAINER_IN_ISO)
        self.assertEqual(len(shipped["lines"]), 6)
        self.assertTrue(all(len(line["text"]) <= 200 for line in shipped["lines"]))
        raw = iso_test_patch.DEFAULT_SPEC.read_text(encoding="utf-8")
        self.assertFalse(any(ord(character) > 0x7F and ord(character) not in (0x2019,)
                             for character in raw), "the spec must stay ASCII")

    def test_the_test_iso_lands_next_to_the_disc_you_picked(self):
        self.assertEqual(iso_test_patch.default_out_path(Path("D:/gry/SRW OE 1.08.iso")),
                         Path("D:/gry/SRW OE 1.08-test.iso"))
        self.assertNotEqual(iso_test_patch.default_out_path(self.iso), self.iso)

    def test_the_cli_writes_the_default_output_next_to_the_input(self):
        code = iso_test_patch.main([str(self.iso), "--spec", str(self.spec_path)])
        self.assertEqual(code, 0)
        self.assertTrue(iso_test_patch.default_out_path(self.iso).is_file())

    def test_the_cli_asks_for_the_disc_and_gives_up_when_there_is_no_answer(self):
        import io
        original_stdin, original_choose = sys.stdin, iso_test_patch.choose_iso
        sys.stdin = io.StringIO("\n")
        iso_test_patch.choose_iso = lambda initial=None: None     # brak okna (np. bez Tk)
        self.addCleanup(setattr, sys, "stdin", original_stdin)
        self.addCleanup(setattr, iso_test_patch, "choose_iso", original_choose)
        self.assertEqual(iso_test_patch.main([]), 2)

    def test_a_dialog_that_cannot_open_is_not_an_error(self):
        # Tk is present in CI but there is no display: the picker must return None, not raise
        self.assertIn(iso_test_patch.choose_iso(), (None, Path("")))

    def test_a_work_directory_keeps_the_intermediate_containers(self):
        work = self.area / "work"
        iso_test_patch.apply_test_patch(self.iso, self.out, self.spec, work=work)
        self.assertTrue((work / "original.cpk").is_file())
        self.assertTrue((work / "patched.cpk").is_file())
        self.assertNotEqual((work / "original.cpk").read_bytes(),
                            (work / "patched.cpk").read_bytes())


if __name__ == "__main__":
    unittest.main()
