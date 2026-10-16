"""Synthetic tests for tools/item_skill_records.py (no game data).

The fixtures rebuild the record layout measured on the real files:

    +0..+39  20 u16 parameter words
    +40..+51  six u16 field boundaries (b0 == 54 in every real record)
    +52..+53  one more parameter word
    +54..     five NUL-terminated CP932 fields: name, name_level, effect, effect_brief, label
    then      the numeric tail (u16 words up to the record end)

Container (convention B): ``u32 tail_offset``, ``u32 count``, ``count`` u32 record offsets,
the records, then the fragment pool up to EOF.
"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import item_skill_records as ISR  # noqa: E402


def build_record(kind, key, name, effect, name_level="", effect_brief="", label="",
                 linked=None, tail=(1, 2), level=1, preamble_word=100):
    """One convention-B record with all five text fields."""
    words = [0] * 20
    if kind == "item":
        words[0] = key
        words[1] = words[2] = linked if linked is not None else key
    else:
        words[0] = 10 if level > 0 else key       # family
        words[1] = 20 if level > 0 else key       # second family field
        words[2] = key                            # unique record id
    words[3] = level
    head = struct.pack("<20H", *words)
    fields = [(name, name_level, effect, effect_brief, label)]
    boundaries = [ISR.STRING_BASE]
    blob = b""
    for text in fields[0]:
        raw = text.encode("cp932") + b"\x00"
        blob += raw
        boundaries.append(boundaries[-1] + len(raw))
    record = (head + struct.pack("<%dH" % ISR.BOUNDARY_COUNT, *boundaries)
              + struct.pack("<H", preamble_word) + blob
              + b"".join(struct.pack("<H", v) for v in tail))
    return record


def build_member(kind, records, pool_runs=(), tail_padding=0, bare_pool=False):
    """Convention B member: header, offsets, records, tail pool.

    The pool is laid out as the game files have it - a u32 table of absolute string offsets,
    then the strings; ``bare_pool=True`` writes the strings without a table (the shape the first
    reading of these files assumed), for the fallback test.
    """
    table_size = 8 + 4 * len(records)
    offsets, position = [], table_size
    for record in records:
        offsets.append(position)
        position += len(record)
    tail_offset = position + tail_padding
    raws = [run.encode("cp932") for run in pool_runs]
    if bare_pool or not raws:
        pool = b"".join(raw + b"\x00" for raw in raws)
    else:
        pool = ISR.build_tail_pool(tail_offset, raws)
    return (struct.pack("<2I", tail_offset, len(records))
            + b"".join(struct.pack("<I", o) for o in offsets)
            + b"".join(records) + b"\x00" * tail_padding + pool)


def build_pool_member(strings):
    """Convention C pool (the DLC Item/Skill files): u32 table_start, u32 0, offsets, strings."""
    table_start = 8
    table_end = table_start + 4 * len(strings)
    payload = b"".join(s.encode("cp932") + b"\x00" for s in strings)
    offsets, position = [], table_end
    for s in strings:
        offsets.append(position)
        position += len(s.encode("cp932")) + 1
    return (struct.pack("<2I", table_start, 0)
            + b"".join(struct.pack("<I", o) for o in offsets) + payload)


class ParseItemTest(unittest.TestCase):
    def member(self):
        return build_member("item", [
            build_record("item", 10000, "改造制限解除", "%s20%s\n%s", tail=(2, 6, 100)),
            build_record("item", 10019, "経験値 ２倍 Lv1", "%s2倍\n5%s", linked=1015, tail=(5,)),
        ], pool_runs=("最大SP+", "回のみ使用可"))

    def test_keys_and_linked_ids(self):
        parsed = ISR.parse_member(self.member(), "item")
        self.assertEqual(parsed["errors"], [])
        rows = parsed["records"]
        self.assertEqual([r["key"] for r in rows], [10000, 10019])
        self.assertEqual(rows[0]["linked"], 10000)     # copies of the id
        self.assertEqual(rows[1]["linked"], 1015)      # a different linked id
        self.assertEqual(rows[0]["tail"], [2, 6, 100])

    def test_all_five_fields_have_roles_sizes_and_offsets(self):
        row = ISR.parse_member(self.member(), "item")["records"][0]
        self.assertEqual([row[role] for role in ISR.FIELDS],
                         ["改造制限解除", "", "%s20%s\n%s", "", ""])
        self.assertEqual(row["name_offset"], ISR.STRING_BASE)
        self.assertEqual(row["name_slot"], len("改造制限解除".encode("cp932")) + 1)
        self.assertEqual(row["name_level_slot"], 1)          # a lone NUL = an empty field
        self.assertEqual(row["label_slot"], 1)
        self.assertEqual(row["boundaries"][0], ISR.STRING_BASE)
        self.assertEqual(len(row["boundaries"]), ISR.BOUNDARY_COUNT)
        self.assertEqual([row[f"{role}_padding"] for role in ISR.FIELDS], [0] * 5)

    def test_fields_are_contiguous_and_terminated(self):
        row = ISR.parse_member(self.member(), "item")["records"][0]
        for role in ISR.FIELDS:
            start, end = row[f"{role}_offset"], row[f"{role}_offset"] + row[f"{role}_slot"]
            self.assertEqual(end - start, len(row[role].encode("cp932")) + 1)
            self.assertEqual(row[f"{role}_padding"], 0)

    def test_tail_pool_is_split_into_runs(self):
        parsed = ISR.parse_member(self.member(), "item")
        self.assertEqual(parsed["tail_pool"], ["最大SP+", "回のみ使用可"])


class TailPoolTableTest(unittest.TestCase):
    """The fragment pool starts with a u32 table of absolute string offsets (measured on all
    five pools, 2026-10-14) - the reader uses it, and round-trips the bytes."""

    def member(self, **kw):
        return build_member("item", [build_record("item", 1, "A", "B")],
                            pool_runs=("最大SP+", "%s", "回のみ使用可"), **kw)

    def test_the_table_is_read_and_the_strings_fill_the_pool(self):
        blob = self.member()
        tail = struct.unpack_from("<I", blob, 0)[0]
        pointers, strings = ISR.parse_tail_pool(blob, tail)
        self.assertEqual(pointers[0], tail + 12)
        self.assertEqual(strings, [b"\x8d\xc5\x91\xe5SP+", b"%s", "回のみ使用可".encode("cp932")])
        self.assertEqual(ISR.build_tail_pool(tail, strings), blob[tail:])

    def test_a_member_without_a_pool_is_empty_not_an_error(self):
        blob = build_member("item", [build_record("item", 1, "A", "B")])
        self.assertEqual(ISR.parse_tail_pool(blob, len(blob)), ([], []))

    def test_a_pool_without_a_table_is_refused_by_the_reader(self):
        blob = self.member(bare_pool=True)
        tail = struct.unpack_from("<I", blob, 0)[0]
        with self.assertRaises(ValueError):
            ISR.parse_tail_pool(blob, tail)
        # split_pool still lists the runs of such a region (exports never lose text)
        self.assertEqual(ISR.split_pool(blob, tail), ["最大SP+", "%s", "回のみ使用可"])

    def test_a_pointer_into_the_middle_of_a_string_is_refused(self):
        blob = bytearray(self.member())
        tail = struct.unpack_from("<I", blob, 0)[0]
        second = struct.unpack_from("<I", blob, tail + 4)[0]
        struct.pack_into("<I", blob, tail + 4, second + 1)
        with self.assertRaises(ValueError):
            ISR.parse_tail_pool(bytes(blob), tail)

    def test_build_refuses_a_nul_inside_a_string(self):
        with self.assertRaises(ValueError):
            ISR.build_tail_pool(100, [b"a\x00b"])

    def test_linked_id_mismatch_is_reported(self):
        record = bytearray(build_record("item", 10000, "A", "B"))
        struct.pack_into("<H", record, 4, 7)            # corrupt the second copy
        blob = build_member("item", [bytes(record)])
        self.assertTrue(any("linked id copies" in e for e in ISR.parse_member(blob, "item")["errors"]))

    def test_bad_boundaries_are_reported(self):
        record = bytearray(build_record("item", 10000, "A", "B"))
        struct.pack_into("<H", record, ISR.BOUNDARY_TABLE, 52)   # b0 must be 54
        blob = build_member("item", [bytes(record)])
        self.assertTrue(any("bad field boundaries" in e
                            for e in ISR.parse_member(blob, "item")["errors"]))

    def test_field_without_terminator_is_reported(self):
        record = bytearray(build_record("item", 10000, "A", "B"))
        b = list(struct.unpack_from("<6H", record, ISR.BOUNDARY_TABLE))
        record[b[1] - 1] = ord("Z")                     # overwrite the NUL of field 0
        blob = build_member("item", [bytes(record)])
        self.assertTrue(any("no terminator" in e for e in ISR.parse_member(blob, "item")["errors"]))


class ParseSkillTest(unittest.TestCase):
    def test_skill_key_is_the_unique_record_id(self):
        blob = build_member("skill", [
            build_record("skill", 1000, "対地", "地形%s6地＠0%s攻撃､命中上昇", level=0),
            build_record("skill", 1, "対地", "地形%s6地＠0%s攻撃､命中上昇", level=1),
        ])
        parsed = ISR.parse_member(blob, "skill")
        self.assertEqual(parsed["errors"], [])
        self.assertEqual([r["key"] for r in parsed["records"]], [1000, 1])
        self.assertEqual([r["level"] for r in parsed["records"]], [0, 1])

    def test_level_name_and_brief_effect_are_read(self):
        blob = build_member("skill", [
            build_record("skill", 1000, "対地", "＠4<対地%s1>＠0 地形%s6地＠0%s､%s40%% 攻撃1.3倍",
                         name_level="対地 Lv1", effect_brief="攻撃1.3倍 命中+40%", level=1)])
        row = ISR.parse_member(blob, "skill")["records"][0]
        self.assertEqual(row["name"], "対地")
        self.assertEqual(row["name_level"], "対地 Lv1")
        self.assertEqual(row["effect_brief"], "攻撃1.3倍 命中+40%")

    def test_label_field_can_carry_a_label(self):
        blob = build_member("skill", [
            build_record("skill", 670, "闘争心", "初期%s+1", name_level="闘争心 Lv1",
                         label="開始気力:全", level=1)])
        row = ISR.parse_member(blob, "skill")["records"][0]
        self.assertEqual(row["label"], "開始気力:全")
        self.assertEqual(row["name_level"], "闘争心 Lv1")


class PoolTest(unittest.TestCase):
    def test_convention_c_pool_entries(self):
        self.assertEqual(ISR.pool_entries(build_pool_member(["最大SP+", "回のみ使用可"])),
                         ["最大SP+", "回のみ使用可"])

    def test_non_pool_blob_returns_empty(self):
        self.assertEqual(ISR.pool_entries(b"\x01\x02\x03"), [])
        self.assertEqual(ISR.pool_entries(build_member("item", [build_record("item", 1, "a", "b")])), [])


class CollectTest(unittest.TestCase):
    def fake_reader(self, path):
        items = build_member("item", [build_record("item", 10000, "A", "B", tail=(1,))])
        skills = build_member("skill", [build_record("skill", 7, "C", "D", name_level="C Lv1")])
        pool = build_pool_member(["最大SP+", "other"])
        return [("srwDL_Item00.bin", items), ("srwDL_Skill00.bin", skills),
                ("srwDL_Item01.bin", pool), ("srwDL_Skill_Tag.bin", b"\x00" * 64)]

    def test_collect_reports_members_pools_and_dlc_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "config00.cpk").write_bytes(b"")
            collected = ISR.collect(Path(tmp), read_members=self.fake_reader)
        report = ISR.summary(collected)
        self.assertEqual(report["members"], 2)                     # Skill_Tag is excluded
        self.assertEqual(report["per_kind"]["item"]["keys"], 1)
        self.assertEqual(report["per_kind"]["skill"]["keys"], 1)
        self.assertEqual(report["pools"], {"srwDL_Item01.bin": 2})
        check = report["pool_checks"]["dlc"]["srwDL_Item01.bin"]
        self.assertEqual((check["entries"], check["in_base_tail_pool"], check["new"]), (2, 0, 2))

    def test_summary_counts_every_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "config00.cpk").write_bytes(b"")
            collected = ISR.collect(Path(tmp), read_members=self.fake_reader)
        skill = ISR.summary(collected)["per_kind"]["skill"]
        self.assertEqual(skill["with_name"], 1)
        self.assertEqual(skill["with_name_level"], 1)
        self.assertEqual(skill["with_label"], 0)
        self.assertEqual(skill["name_bytes"], len("C".encode("cp932")))

    def test_jsonl_rows_are_writable(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "config00.cpk").write_bytes(b"")
            collected = ISR.collect(Path(tmp), read_members=self.fake_reader)
            out = Path(tmp, "rows.jsonl")
            with out.open("w", encoding="utf-8") as handle:
                for rows in collected["merged"].values():
                    for row in rows:
                        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(sorted(r["kind"] for r in rows), ["item", "skill"])
        self.assertEqual({r["name"] for r in rows}, {"A", "C"})


if __name__ == "__main__":
    unittest.main()
