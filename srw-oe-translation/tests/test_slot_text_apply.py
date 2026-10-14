#!/usr/bin/env python3
"""Tests for tools/slot_text_apply.py, on synthetic data (no game data).

The slot kinds are fixed-width cells, so the rules being tested are the opposite of the record
writer's: a translation must fit the room it was given, the NUL padding has to come back, and
nothing outside the written slots may move by a single byte.  A container that is rebuilt without
changes must also come back identical, because that is what tells us a PAC/CPK round trip is safe.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import configst_pack as CP  # noqa: E402
import cpk_write  # noqa: E402
import slot_text_apply as S  # noqa: E402
from test_configst_pack import make_pac  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402

STRIDE = 128
SLOT = 10


def synthetic_milst(count: int = 3) -> bytes:
    """A member with the measured mission-title shape: 128-byte cells, text at +10."""
    out = bytearray()
    for index in range(count):
        cell = bytearray(STRIDE)
        text = f"ミッション{index}".encode("cp932")
        cell[SLOT:SLOT + len(text)] = text
        out += cell
    return bytes(out)


class SlotTest(unittest.TestCase):
    def setUp(self):
        self.blob = synthetic_milst()
        self.spec = S.spec_for("mission_title")

    def test_the_layout_comes_from_the_measured_table(self):
        self.assertEqual((self.spec["stride"], self.spec["slot"]), (STRIDE, SLOT))
        self.assertEqual(S.records(self.blob, self.spec), 3)

    def test_reading_a_slot_gives_its_text(self):
        self.assertEqual(S.read_slot(self.blob, self.spec, 0), "ミッション0")
        self.assertEqual(S.read_slot(self.blob, self.spec, 2), "ミッション2")

    def test_the_room_of_a_slot_is_its_measured_field(self):
        # the title field is 40 bytes: an ASCII field follows it at +50 (mission_text)
        start, end = S.slot_span(self.blob, self.spec, 1)
        self.assertEqual((start, end), (STRIDE + SLOT, STRIDE + SLOT + 40))

    def test_writing_fits_the_text_and_pads_with_nuls(self):
        out, report = S.write_slots(self.blob, self.spec, {0: "Basic Training"})
        self.assertEqual(S.read_slot(out, self.spec, 0), "Basic Training")
        self.assertEqual(out[:SLOT], self.blob[:SLOT])                 # the header is untouched
        self.assertEqual(out[SLOT + len("Basic Training")], 0)         # at least one NUL
        self.assertEqual(len(out), len(self.blob))
        self.assertEqual(S.read_slot(out, self.spec, 1), "ミッション1")  # the next cell is untouched
        self.assertEqual(report, [f"record 0: {len('Basic Training'.encode('cp932'))} bytes "
                                  f"into 39"])

    def test_a_text_that_does_not_fit_is_refused(self):
        with self.assertRaises(S.SlotError) as caught:
            S.write_slots(self.blob, self.spec, {0: "x" * 40})
        self.assertIn("the text is", str(caught.exception))
        # the old span (to the record end) must not be writable any more: binary follows +50
        with self.assertRaises(S.SlotError):
            S.write_slots(self.blob, self.spec, {0: "x" * 60})

    def test_a_character_the_game_cannot_show_is_refused(self):
        with self.assertRaises(S.SlotError) as caught:
            S.write_slots(self.blob, self.spec, {0: "An em dash — here"})
        self.assertIn("codec", str(caught.exception))

    def test_a_cell_that_does_not_exist_is_refused(self):
        with self.assertRaises(S.SlotError):
            S.write_slots(self.blob, self.spec, {9: "Nowhere"})

    def test_verification_sees_a_change_outside_a_slot(self):
        out, _ = S.write_slots(self.blob, self.spec, {0: "Basic Training"})
        damaged = bytearray(out)
        damaged[2 * STRIDE + SLOT] = 0x41            # a byte in the next cell
        problems = S.verify(self.blob, bytes(damaged), self.spec, {0: "Basic Training"})
        self.assertTrue(any("outside the slots" in problem for problem in problems))

    def test_verification_sees_a_slot_that_does_not_read_back(self):
        out, _ = S.write_slots(self.blob, self.spec, {0: "Basic Training"})
        problems = S.verify(self.blob, out, self.spec, {0: "Something else"})
        self.assertTrue(any("does not read back" in problem for problem in problems))

    def test_a_clean_write_verifies_without_problems(self):
        out, _ = S.write_slots(self.blob, self.spec, {1: "Basic Training", 2: "Ep. 1: Ramage"})
        self.assertEqual(S.verify(self.blob, out, self.spec,
                                  {1: "Basic Training", 2: "Ep. 1: Ramage"}), [])

    def test_an_unknown_kind_or_slot_is_reported(self):
        with self.assertRaises(S.SlotError):
            S.spec_for("no_such_kind")
        with self.assertRaises(S.SlotError):
            S.spec_for("mission_title", role="note_a")


class ContainerTest(unittest.TestCase):
    """The whole path a mission title travels: CPK -> PAC subfile -> slot -> back."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)
        self.member = synthetic_milst()
        pac = make_pac([("milstP00.bin", self.member), ("other.bin", b"\x07" * 200)])
        self.container = self.area / "config-synthetic.cpk"
        self.container.write_bytes(build_synthetic_cpk(
            [{"dir": "", "name": "config00.pac", "data": pac, "id": 0}]))
        self.out = self.area / "config-out.cpk"

    def edits(self, text="Basic Training"):
        return {0: text}

    def test_a_rebuild_without_changes_gives_the_file_back(self):
        path = self.area / "untouched.cpk"
        S.apply_container(self.container, path, "mission_title", "milstP00.bin", {})
        self.assertEqual(path.read_bytes(), self.container.read_bytes())

    def test_writing_a_title_keeps_the_container_the_same_size(self):
        report = S.apply_container(self.container, self.out, "mission_title", "milstP00.bin",
                                   self.edits())
        self.assertEqual(report["applied"], 1)
        self.assertEqual(report["member_delta"], 0)
        self.assertEqual(report["container_delta"], 0)
        self.assertTrue(report["verified"])

    def test_the_written_title_is_inside_the_container_that_was_written(self):
        S.apply_container(self.container, self.out, "mission_title", "milstP00.bin", self.edits())
        cpk = cpk_write.load(self.out)
        pac = CP.parse_pac(cpk.members[0].blob)
        subfile = {sub["name"]: sub["data"] for sub in pac["subs"]}
        self.assertEqual(S.read_slot(subfile["milstP00.bin"], S.spec_for("mission_title"), 0),
                         "Basic Training")
        self.assertEqual(subfile["other.bin"], b"\x07" * 200)          # the neighbour is untouched
        self.assertEqual(len(subfile["milstP00.bin"]), len(self.member))

    def test_a_subfile_that_is_not_there_is_reported(self):
        with self.assertRaises(S.SlotError):
            S.apply_container(self.container, self.out, "mission_title", "nope.bin", self.edits())

    def test_a_title_that_does_not_fit_is_refused_before_anything_is_written(self):
        with self.assertRaises(S.SlotError):
            S.apply_container(self.container, self.out, "mission_title", "milstP00.bin",
                              {0: "x" * 200})
        self.assertFalse(self.out.exists())

    def test_the_rows_of_the_package_say_which_slot_to_write(self):
        import json
        (self.area / "05_mission_text.jsonl").write_text("\n".join(json.dumps(row) for row in [
            {"id": "mission_title:x:0", "category": "mission_title", "jp": "ミッション0", "en": "Basic Training",
             "source": {"container": self.container.name, "member": "milstP00.bin", "offset": SLOT}},
            {"id": "mission_title:x:1", "category": "mission_title", "jp": "ミッション1", "en": "",
             "source": {"container": self.container.name, "member": "milstP00.bin",
                        "offset": STRIDE + SLOT}},
            {"id": "mission_title:x:9", "category": "mission_title", "jp": "別のもの", "en": "Other",
             "source": {"container": "other.cpk", "member": "milstP00.bin", "offset": SLOT}},
        ]), encoding="utf-8")
        rows = S.rows_of_package(self.area, self.container.name, "mission_title")
        self.assertEqual([row["id"] for row in rows], ["mission_title:x:0"])   # only filled rows
        edits = S.edits_for_member(self.member, S.spec_for("mission_title"), rows, "milstP00.bin")
        self.assertEqual(edits, {0: "Basic Training"})

    def test_a_row_whose_slot_holds_something_else_is_refused(self):
        rows = [{"id": "x", "category": "mission_title", "jp": "inna treść", "en": "Other",
                 "source": {"container": self.container.name, "member": "milstP00.bin",
                            "offset": SLOT}}]
        with self.assertRaises(S.SlotError):
            S.edits_for_member(self.member, S.spec_for("mission_title"), rows, "milstP00.bin")


if __name__ == "__main__":
    unittest.main()
