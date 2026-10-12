"""Synthetic tests for tools/item_skill_records.py (no game data)."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import item_skill_records as ISR  # noqa: E402


def build_record(kind, key, name, effect, extra="", linked=None, tail=(1, 2), level=1,
                 padding_extra=0):
    """One convention-B record: u16 header, three NUL-padded slots, numeric tail."""
    header = [0] * 20
    header[0] = key
    if kind == "item":
        header[1] = header[2] = linked if linked is not None else key
    else:
        header[0] = key if level == 0 else 1        # family
        header[1] = key if level == 0 else 1
        header[2] = key                              # unique record id
    header[3] = level
    head = struct.pack("<%dH" % len(header), *header)
    slots = bytearray()
    spans = []
    start = ISR.SPAN_TABLE + 4 * ISR.SPAN_PAIRS      # the span table sits between header and slots
    for text in (name, effect, extra):
        raw = text.encode("cp932")
        slots += raw + b"\x00" + b"\x00" * padding_extra
        end = start + len(raw) + 1 + padding_extra
        spans.append((start, end))
        start = end
    table = struct.pack("<6H", *[v for pair in spans for v in pair])
    record = head[:ISR.SPAN_TABLE] + table + bytes(slots)
    record += b"".join(struct.pack("<H", v) for v in tail)
    return record


def build_member(kind, records, pool_runs=(), tail_padding=0):
    """Convention B member: tail_offset, count, offsets, records, tail pool."""
    table_size = 8 + 4 * len(records)
    offsets = []
    position = table_size
    for record in records:
        offsets.append(position)
        position += len(record)
    tail_offset = position + tail_padding
    pool = b"".join(run.encode("cp932") + b"\x00" for run in pool_runs)
    return (struct.pack("<2I", tail_offset, len(records))
            + b"".join(struct.pack("<I", o) for o in offsets)
            + b"".join(records) + b"\x00" * tail_padding + pool)


def build_pool_member(strings):
    """Convention C pool: u32 table_start, u32 0, offsets, strings."""
    table_start = 8
    table_end = table_start + 4 * len(strings)
    payload = b"".join(s.encode("cp932") + b"\x00" for s in strings)
    offsets = []
    position = table_end
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

    def test_three_slots_with_roles_and_sizes(self):
        row = ISR.parse_member(self.member(), "item")["records"][0]
        self.assertEqual(row["name"], "改造制限解除")
        self.assertEqual(row["effect"], "%s20%s\n%s")
        self.assertEqual(row["extra"], "")
        self.assertEqual(row["name_padding"], 0)
        self.assertEqual(row["extra_slot"], 1)         # a lone NUL = an empty slot
        self.assertEqual(len(row["name"].encode("cp932")), row["name_slot"] - 1)

    def test_tail_pool_is_split_into_runs(self):
        parsed = ISR.parse_member(self.member(), "item")
        self.assertEqual(parsed["tail_pool"], ["最大SP+", "回のみ使用可"])

    def test_linked_id_mismatch_is_reported(self):
        record = bytearray(build_record("item", 10000, "A", "B"))
        struct.pack_into("<H", record, 4, 7)            # corrupt the second copy
        blob = build_member("item", [bytes(record)])
        self.assertTrue(any("linked id copies" in e for e in ISR.parse_member(blob, "item")["errors"]))

    def test_slot_without_terminator_is_reported(self):
        record = bytearray(build_record("item", 10000, "A", "B"))
        record[40 + 2:40 + 4] = struct.pack("<H", 40 + 1)   # slot 0 = [40, 41) -> no room
        record[40:40 + 2] = struct.pack("<H", 40)
        blob = build_member("item", [bytes(record)])
        self.assertTrue(ISR.parse_member(blob, "item")["errors"])


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

    def test_extra_slot_can_carry_a_label(self):
        blob = build_member("skill", [build_record("skill", 670, "底力", "%s", extra="開始気力:全")])
        self.assertEqual(ISR.parse_member(blob, "skill")["records"][0]["extra"], "開始気力:全")


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
        skills = build_member("skill", [build_record("skill", 7, "C", "D")])
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
