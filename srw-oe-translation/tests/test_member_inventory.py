#!/usr/bin/env python3
"""Tests for tools/member_inventory.py and the sequential CPK member layout it relies on.

All fixtures are synthetic bytes: no game file is read.  The layout under test is the
"ITOC blob" CPK variant (entries without offsets, members laid out sequentially on the
alignment boundary) measured on the disc-side packages on 2026-10-12.
"""
from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import cpk_table  # noqa: E402
import member_inventory as MI  # noqa: E402
import speaker_map as SM  # noqa: E402


def sequential_table(content_offset=0x1000, content_size=0x2000, align=2048, sizes=(100, 300, 4096)):
    """A read_cpk_table-shaped dict for the offset-less (ITOC blob) layout."""
    return {
        "header": {"content_offset": content_offset, "content_size": content_size, "align": align},
        "entries": [
            {
                "name": f"ID{index:05d}",
                "file_size": size,
                "extract_size": size,
                "absolute_offset": None,
                "compressed": False,
            }
            for index, size in enumerate(sizes)
        ],
    }


def build_pac(subfiles, index_end=0x800):
    """A PAC index blob: entries of (u32 offset, u32 size, 0x20-byte name) from 0x10."""
    blob = bytearray(index_end)
    offset = index_end
    for base, (name, data) in zip(range(0x10, index_end, 0x28), subfiles):
        struct.pack_into("<2I", blob, base, offset, len(data))
        blob[base + 8:base + 8 + len(name)] = name.encode("ascii")
        blob.extend(data)
        offset += len(data)
    return bytes(blob)


class MemberOffsetsTest(unittest.TestCase):
    def test_offsetless_entries_are_sequential_and_aligned(self):
        table = sequential_table(content_offset=0x1000, sizes=(100, 300, 4096))
        offsets = SM.member_offsets(None, table)
        # 0x1000 is already aligned; each next member starts on the 2048 boundary.
        self.assertEqual(offsets, [0x1000, 0x1000 + 2048, 0x1000 + 2048 + 2048])

    def test_offsetless_entries_ignore_non_default_alignment(self):
        table = sequential_table(content_offset=0x1000, align=16, sizes=(100, 300))
        self.assertEqual(SM.member_offsets(None, table), [0x1000, 0x1000 + 112])

    def test_offset_entries_keep_their_offsets_and_move_the_cursor(self):
        table = sequential_table(content_offset=0x1000, align=16, sizes=(10, 20, 30))
        table["entries"][0]["absolute_offset"] = 0x5000
        self.assertEqual(SM.member_offsets(None, table), [0x5000, 0x5010, 0x5030])

    def test_overrun_beyond_the_content_region_fails_closed(self):
        table = sequential_table(content_offset=0x1000, content_size=0x400, align=2048, sizes=(100, 100))
        with self.assertRaises(cpk_table.CpkTableError):
            SM.member_offsets(None, table)

    def test_content_region_without_size_skips_the_overrun_check(self):
        table = sequential_table(content_offset=0x1000, content_size=None, align=2048, sizes=(100, 100))
        self.assertEqual(len(SM.member_offsets(None, table)), 2)


class SubfileRowTest(unittest.TestCase):
    def test_pac_index_yields_names_and_sizes(self):
        blob = build_pac([("bg2dlist.bin", b"A" * 40), ("unit_index_list.bin", b"BB")])
        rows = MI.subfile_rows(blob)
        self.assertEqual([row["subfile"] for row in rows], ["bg2dlist.bin", "unit_index_list.bin"])
        self.assertEqual([row["size"] for row in rows], [40, 2])

    def test_non_pac_bytes_yield_nothing(self):
        self.assertEqual(MI.subfile_rows(b"\x00" * 4096), [])
        self.assertEqual(MI.subfile_rows(b""), [])

    def test_pac_index_with_a_shorter_member_is_rejected(self):
        blob = build_pac([("a.bin", b"A" * 64)])
        self.assertEqual(len(MI.subfile_rows(blob)), 1)
        self.assertEqual(MI.subfile_rows(blob[:-1]), [])  # last subfile no longer fits


class ClassifyTest(unittest.TestCase):
    def test_claimed_names_win_over_every_rule(self):
        claimed = {"srwDL_Skill00.bin": "text_tables", "DL100_01.bin": "event_dialogue"}
        self.assertEqual(MI.classify("srwDL_Skill00.bin", "config00.cpk", claimed), "text_tables")
        # The claim wins over the container rule, so a reader output's list stays authoritative.
        self.assertEqual(MI.classify("DL100_01.bin", "mesbtl00.cpk", claimed), "event_dialogue")

    def test_marker_and_container_rules_then_the_unread_default(self):
        self.assertEqual(MI.classify("srwDL_CharaDictionary00.bin", "imenu00.cpk", {}),
                         "chara_dictionary")
        self.assertEqual(MI.classify("srw_DL_RoboDictionary00.bin", "imenu00.cpk", {}),
                         "robo_dictionary")
        self.assertEqual(MI.classify("DL100_01_ext.dat", "eventP00.cpk", {}), "mission_notes")
        self.assertEqual(MI.classify("DL100_01.bin", "eventP00.cpk", {}), "event_dialogue")
        self.assertEqual(MI.classify("DL100_01.bin", "evept101.EDAT", {}), "event_dialogue")
        self.assertEqual(MI.classify("battle.bin", "mesbtl00.cpk", {}), "battle_quotes")
        self.assertEqual(MI.classify("r0001/0000_000.pac", "robo00.cpk", {}), "unread")
        self.assertEqual(MI.classify("DL100_01_Entry.dat", "eventP00.cpk", {}), "unread")


class ReaderNamesTest(unittest.TestCase):
    def test_names_are_harvested_from_keys_and_values_of_every_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "text_tables").mkdir()
            (root / "text_tables" / "summary.json").write_text(
                json.dumps({"members": {"srwDL_Skill00.bin": {"container": "config00.cpk"}}}),
                encoding="utf-8",
            )
            (root / "item_skill_summary.json").write_text(
                json.dumps({"pools": {"srwDL_Item01.bin": 76}, "note": "not a file name"}),
                encoding="utf-8",
            )
            (root / "member_inventory.json").write_text(
                json.dumps({"files": [{"member": "should_not_be_claimed.bin"}]}), encoding="utf-8"
            )
            claimed = MI.reader_names([root])
        self.assertEqual(claimed.get("srwDL_Skill00.bin"), "text_tables")
        self.assertEqual(claimed.get("srwDL_Item01.bin"), "item_skill")
        self.assertNotIn("should_not_be_claimed.bin", claimed)


if __name__ == "__main__":
    unittest.main()
