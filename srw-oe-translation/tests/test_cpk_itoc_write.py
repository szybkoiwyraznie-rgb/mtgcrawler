#!/usr/bin/env python3
"""Tests for tools/cpk_itoc_write.py on synthetic ITOC-only (CpkMode 0) containers.

Shape copied from the measured disc-side UI containers (``system.cpk`` …): header packet at
0, ITOC packet at 2048 with one row whose ``DataL``/``DataH`` cells reference nested @UTF
tables (ID / FileSize / ExtractSize), members from ``ContentOffset`` 4096 in ID order, each on
an ``Align`` boundary, file ending right after the last member.  The gate is byte identity of
a no-change rebuild; the replacement tests check what identity cannot see.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_itoc_write  # noqa: E402
import cpk_table  # noqa: E402
import crilayla  # noqa: E402
import speaker_map  # noqa: E402
from test_cpk_table import build_cpk_packet, build_utf_table  # noqa: E402

ALIGN = 2048


def _pad(blob: bytes, align: int) -> bytes:
    return blob + b"\x00" * (-len(blob) % align)


def build_itoc_only_cpk(members, *, align: int = ALIGN, header_extra=None) -> bytes:
    """``members``: list of (id, blob, extract_size); all land in DataH (u32 sizes)."""
    members = sorted(members, key=lambda m: m[0])
    data_l = build_utf_table("CpkItocL", [("ID", 0x52), ("FileSize", 0x52), ("ExtractSize", 0x52)], [])
    data_h = build_utf_table(
        "CpkItocH", [("ID", 0x52), ("FileSize", 0x54), ("ExtractSize", 0x54)],
        [{"ID": mid, "FileSize": len(blob), "ExtractSize": extract} for mid, blob, extract in members])
    itoc_table = build_utf_table(
        "CpkItocInfo",
        [("FilesL", 0x54), ("FilesH", 0x54), ("DataL", 0x5B), ("DataH", 0x5B)],
        [{"FilesL": 0, "FilesH": len(members), "DataL": (0, len(data_l)), "DataH": (len(data_l), len(data_h))}],
        data=data_l + data_h)
    itoc_packet = build_cpk_packet(b"ITOC", itoc_table)
    content = bytearray()
    pos = 2 * align
    for _mid, blob, _extract in members:
        aligned = -(-pos // align) * align
        content.extend(b"\x00" * (aligned - pos))
        content.extend(blob)
        pos = aligned + len(blob)
    footprint = pos - 2 * align
    columns = [("ContentOffset", 0x56), ("ContentSize", 0x56), ("ItocOffset", 0x56), ("ItocSize", 0x56),
               ("EnabledPackedSize", 0x56), ("EnabledDataSize", 0x56), ("Files", 0x54), ("Align", 0x52),
               ("CpkMode", 0x54)]
    row = {"ContentOffset": 2 * align, "ContentSize": -(-footprint // align) * align, "ItocOffset": align,
           "ItocSize": len(itoc_table), "EnabledPackedSize": sum(m[2] for m in members),
           "EnabledDataSize": sum(len(m[1]) for m in members), "Files": len(members), "Align": align,
           "CpkMode": 0}
    row.update(header_extra or {})
    header_packet = build_cpk_packet(b"CPK ", build_utf_table("CpkHeader", columns, [row]))
    if len(header_packet) > align or len(itoc_packet) > align:
        raise AssertionError("synthetic tables too large for the fixed layout")
    return _pad(header_packet, align) + _pad(itoc_packet, align) + bytes(content)


PACKED_A = crilayla.compress(b"A" * 9000)      # a real CRILAYLA member (FileSize < ExtractSize)
PACKED_C = crilayla.compress(bytes(range(256)) * 8 + b"C" * 2000)


class ItocWriteTests(unittest.TestCase):
    MEMBERS = [(0, PACKED_A, 9000), (1, b"B" * 100, 100), (2, PACKED_C, 4048)]

    def write(self, members=None, **kw):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "synthetic.cpk"
        path.write_bytes(build_itoc_only_cpk(members if members is not None else self.MEMBERS, **kw))
        return path, path.read_bytes()

    def test_fixture_is_readable_by_the_trusted_reader(self):
        path, _ = self.write()
        table = cpk_table.read_cpk_table(path)
        self.assertEqual([e["id"] for e in table["entries"]], [0, 1, 2])
        self.assertEqual([e["file_size"] for e in table["entries"]], [len(PACKED_A), 100, len(PACKED_C)])
        offsets = speaker_map.member_offsets(path, table)
        second = 4096 + -(-len(PACKED_A) // ALIGN) * ALIGN
        self.assertEqual(offsets, [4096, second, second + ALIGN])
        members = dict(speaker_map.read_members(path))
        self.assertEqual(members["ID00000"], b"A" * 9000)
        self.assertEqual(members["ID00002"][-2000:], b"C" * 2000)

    def test_no_change_rebuild_is_byte_identical(self):
        path, original = self.write()
        ok, message = cpk_itoc_write.verify_identity(path)
        self.assertTrue(ok, message)
        self.assertEqual(cpk_itoc_write.rebuild(cpk_itoc_write.load(path)), original)

    def test_single_member_identity(self):
        path, original = self.write([(0, b"Z" * 777, 777)])
        self.assertEqual(cpk_itoc_write.rebuild(cpk_itoc_write.load(path)), original)

    def test_refuses_a_container_with_a_toc(self):
        from test_cpk_table import build_synthetic_cpk
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "toc.cpk"
        path.write_bytes(build_synthetic_cpk([{"dir": "", "name": "a.bin", "data": b"A" * 10, "id": 0}]))
        with self.assertRaises(cpk_itoc_write.ItocWriteError):
            cpk_itoc_write.load(path)

    def _roundtrip(self, path, replacements):
        rebuilt = cpk_itoc_write.rebuild(cpk_itoc_write.load(path), replacements)
        out = path.with_name("rebuilt.cpk")
        out.write_bytes(rebuilt)
        return out, rebuilt

    def test_grown_stored_member_shifts_followers_and_updates_the_index(self):
        path, _ = self.write()
        grown = b"X" * 5000   # stored: FileSize == ExtractSize, as the UI build writes it
        out, rebuilt = self._roundtrip(path, {"ID00000": (grown, 5000)})
        table = cpk_table.read_cpk_table(out)
        self.assertEqual([(e["file_size"], e["extract_size"]) for e in table["entries"]],
                         [(5000, 5000), (100, 100), (len(PACKED_C), 4048)])
        members = dict(speaker_map.read_members(out))
        self.assertEqual(members["ID00000"], grown)
        self.assertEqual(members["ID00001"], b"B" * 100)
        self.assertEqual(members["ID00002"][-2000:], b"C" * 2000)
        fields = table["header"]["fields"]
        # footprint: 5000 -> pad to 6144, +100 -> pad to 8192, + len(PACKED_C), rounded up
        footprint = 8192 + len(PACKED_C)
        self.assertEqual(fields["ContentSize"], -(-footprint // ALIGN) * ALIGN)
        self.assertEqual(fields["EnabledPackedSize"], 5000 + 100 + 4048)
        self.assertEqual(fields["EnabledDataSize"], 5000 + 100 + len(PACKED_C))
        self.assertEqual(len(rebuilt), 4096 + footprint)

    def test_recompressed_member_round_trips(self):
        path, _ = self.write()
        packed = crilayla.compress(b"new content " * 700)
        out, _ = self._roundtrip(path, {0: (packed, 8400)})
        members = dict(speaker_map.read_members(out))
        self.assertEqual(members["ID00000"], b"new content " * 700)
        self.assertEqual(members["ID00001"], b"B" * 100)

    def test_shrunk_member_pulls_followers_back(self):
        path, _ = self.write()
        out, rebuilt = self._roundtrip(path, {0: (b"s" * 10, 10)})
        members = dict(speaker_map.read_members(out))
        self.assertEqual(members["ID00000"], b"s" * 10)
        self.assertEqual(members["ID00002"][-2000:], b"C" * 2000)
        self.assertEqual(len(rebuilt), 4096 + 2048 + 2048 + len(PACKED_C))

    def test_stored_bigger_than_extract_is_refused(self):
        path, _ = self.write()
        with self.assertRaises(cpk_itoc_write.ItocWriteError):
            cpk_itoc_write.rebuild(cpk_itoc_write.load(path), {0: (b"x" * 50, 10)})

    def test_unknown_member_is_refused(self):
        path, _ = self.write()
        with self.assertRaises(KeyError):
            cpk_itoc_write.rebuild(cpk_itoc_write.load(path), {"ID00042": (b"x", 1)})

    def test_header_fields_outside_the_measured_rule_are_left_alone(self):
        # EnabledPackedSize that does not equal sum(ExtractSize) is a convention we do not know:
        # it must survive untouched instead of being "corrected".
        path, _ = self.write(header_extra={"EnabledPackedSize": 123456})
        out, _ = self._roundtrip(path, {1: (b"Q" * 300, 300)})
        fields = cpk_table.read_cpk_table(out)["header"]["fields"]
        self.assertEqual(fields["EnabledPackedSize"], 123456)
        self.assertEqual(fields["EnabledDataSize"], len(PACKED_A) + 300 + len(PACKED_C))

    def test_cli_verify_identity(self):
        path, _ = self.write()
        self.assertEqual(cpk_itoc_write.main(["verify-identity", str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
