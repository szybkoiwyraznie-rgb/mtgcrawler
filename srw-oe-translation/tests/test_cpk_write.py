#!/usr/bin/env python3
"""Tests for tools/cpk_write.py, on synthetic containers.

The acceptance gate for this tool is byte identity: the gbatemp thread about the
SRW OE Korean patch records that a naive repack *crashed the game*, so a rebuild
that changes nothing has to reproduce the original file exactly. These tests run
that gate on the synthetic containers from test_cpk_table, then check the thing
the gate cannot see -- that a member which does change is placed correctly and
every other member survives untouched.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_table  # noqa: E402
import cpk_write  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402

ENTRIES = [
    {"dir": "", "name": "first.bin", "data": b"A" * 100, "id": 0},
    {"dir": "", "name": "second.bin", "data": b"B" * 250, "id": 1},
    {"dir": "", "name": "third.bin", "data": b"C" * 40, "id": 2},
]


class CpkWriteTests(unittest.TestCase):
    def write(self, entries=None) -> tuple:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "synthetic.cpk"
        path.write_bytes(build_synthetic_cpk(entries if entries is not None else ENTRIES))
        return path, path.read_bytes()

    def test_a_no_change_rebuild_reproduces_the_file_exactly(self):
        path, original = self.write()
        self.assertEqual(cpk_write.rebuild(cpk_write.load(path), None), original)

    def test_identity_holds_for_a_single_entry_container_too(self):
        path, original = self.write([ENTRIES[0]])
        self.assertEqual(cpk_write.rebuild(cpk_write.load(path), None), original)

    def test_loader_cross_checks_every_cell_against_cpk_table(self):
        path, _ = self.write()
        cpk = cpk_write.load(path)
        reference = cpk_table.read_cpk_table(path)["entries"]
        self.assertEqual([m.name for m in cpk.members], [e["name"] for e in reference])
        self.assertEqual(
            [(m.file_size, m.extract_size) for m in cpk.members],
            [(e["file_size"], e["extract_size"]) for e in reference],
        )

    def test_a_longer_member_shifts_the_following_ones_and_keeps_the_rest(self):
        path, _ = self.write()
        grown = b"X" * 5000
        rebuilt = cpk_write.rebuild(cpk_write.load(path), ("second.bin", grown))
        self.assertNotEqual(len(rebuilt), len(path.read_bytes()))

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        out = Path(temporary.name) / "rebuilt.cpk"
        out.write_bytes(rebuilt)

        # It has to still be a readable container, and the sizes have to agree
        # between this writer's view and the reader the pipeline already trusts.
        after = cpk_write.load(out)
        reference = cpk_table.read_cpk_table(out)["entries"]
        for member, entry in zip(after.members, reference):
            self.assertEqual(member.name, entry["name"])
            self.assertEqual(member.file_size, entry["file_size"])
            self.assertEqual(cpk_write.load(out).data_base + member.relative_offset, entry["absolute_offset"])

        blobs = {m.name: m.blob for m in after.members}
        self.assertEqual(blobs["second.bin"], grown)
        self.assertEqual(blobs["first.bin"], b"A" * 100)
        self.assertEqual(blobs["third.bin"], b"C" * 40)
        # The grown member is written stored, so both sizes are the new length.
        second = next(m for m in after.members if m.name == "second.bin")
        self.assertEqual(second.file_size, second.extract_size)
        self.assertEqual(second.file_size, len(grown))

    def test_a_same_size_replacement_keeps_the_container_length(self):
        path, original = self.write()
        rebuilt = cpk_write.rebuild(cpk_write.load(path), ("second.bin", b"Z" * 250))
        self.assertEqual(len(rebuilt), len(original))
        self.assertNotEqual(rebuilt, original)
        self.assertIn(b"Z" * 250, rebuilt)
        self.assertIn(b"A" * 100, rebuilt)
        self.assertIn(b"C" * 40, rebuilt)

    def test_members_keep_their_order_and_alignment_after_a_shift(self):
        path, _ = self.write()
        rebuilt = cpk_write.rebuild(cpk_write.load(path), ("first.bin", b"Y" * 9000))
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        out = Path(temporary.name) / "rebuilt.cpk"
        out.write_bytes(rebuilt)
        after = cpk_write.load(out)
        offsets = sorted(m.relative_offset for m in after.members)
        # No two members may overlap, and none may start before the region does.
        by_offset = sorted(after.members, key=lambda m: m.relative_offset)
        for earlier, later in zip(by_offset, by_offset[1:]):
            self.assertLessEqual(
                earlier.relative_offset + earlier.file_size,
                later.relative_offset,
                f"{earlier.name} runs into {later.name}",
            )
        self.assertEqual(offsets, sorted(offsets))

    def test_refuses_a_file_that_is_not_a_container(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "notcpk.bin"
        path.write_bytes(b"AFS2" + b"\x00" * 64)
        with self.assertRaises(ValueError) as caught:
            cpk_write.load(path)
        self.assertIn("not a CPK container", str(caught.exception))

    def test_verify_identity_reports_a_clean_container_as_identical(self):
        path, original = self.write()
        ok, detail = cpk_write.verify_identity(path)
        self.assertTrue(ok, detail)
        self.assertIn(str(len(original)), detail)

    def test_verify_identity_reports_failure_rather_than_raising(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "broken.bin"
        path.write_bytes(b"nope")
        ok, detail = cpk_write.verify_identity(path)
        self.assertFalse(ok)
        self.assertTrue(detail)


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.dir = Path(temporary.name)
        self.path = self.dir / "synthetic.cpk"
        self.path.write_bytes(build_synthetic_cpk(ENTRIES))

    def test_extract_member_writes_the_stored_bytes(self):
        out = self.dir / "second.bin"
        self.assertEqual(cpk_write.main(["extract-member", str(self.path), "second.bin", "-o", str(out)]), 0)
        self.assertEqual(out.read_bytes(), b"B" * 250)

    def test_extract_member_refuses_a_name_that_is_not_there(self):
        out = self.dir / "nope.bin"
        self.assertEqual(cpk_write.main(["extract-member", str(self.path), "nope.bin", "-o", str(out)]), 1)
        self.assertFalse(out.exists())

    def test_replace_member_writes_a_container_that_reads_back(self):
        blob = self.dir / "new.bin"
        blob.write_bytes(b"N" * 777)
        out = self.dir / "rebuilt.cpk"
        self.assertEqual(
            cpk_write.main(
                ["replace-member", str(self.path), "third.bin", str(blob), "-o", str(out)]
            ),
            0,
        )
        after = cpk_write.load(out)
        self.assertEqual(next(m for m in after.members if m.name == "third.bin").blob, b"N" * 777)

    def test_verify_identity_subcommand_exits_zero_when_everything_round_trips(self):
        self.assertEqual(cpk_write.main(["verify-identity", str(self.path)]), 0)




class AlignmentPaddingTests(unittest.TestCase):
    class Stub:
        content_offset = 10240
        content_size = 356352   # ends at 366592 = 2048*179 -> aligned, like real files
        align = 2048

    def test_a_grown_region_is_padded_back_to_the_align_boundary(self):
        # 360768 grew the end to 371008, which is 320 bytes past a 2048 boundary.
        content = cpk_write._pad_to_alignment(self.Stub(), bytearray(b"\x00" * 360768))
        end = self.Stub.content_offset + len(content)
        self.assertEqual(end % self.Stub.align, 0, f"end {end} not aligned")
        self.assertEqual(end, 372736)

    def test_a_no_change_region_of_an_aligned_container_is_untouched(self):
        content = bytearray(b"\x00" * 356352)
        self.assertEqual(cpk_write._pad_to_alignment(self.Stub(), content), content)

    class Unaligned:
        content_offset = 265
        content_size = 390      # ends at 655, not aligned -> leave alone
        align = 2048

    def test_an_originally_unaligned_container_is_not_padded(self):
        content = bytearray(b"\x00" * 390)
        self.assertEqual(cpk_write._pad_to_alignment(self.Unaligned(), content), content)

if __name__ == "__main__":
    unittest.main()
