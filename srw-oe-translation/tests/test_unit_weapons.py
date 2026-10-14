"""Synthetic tests for tools/unit_weapons.py (no game data).

The fixtures rebuild the record layouts measured on config00-06: 384-byte unit records with the
unit id at +84, wp_list records of 12 + 256*count bytes with the name / short name / animation at
entry +32 / +96 / +128, robo_cpkid pairs, RoboDictionary slot tables and the global unit index.
"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import unit_weapons as UW  # noqa: E402


def unit_record(name: str, display: str, unit_id: int, base_id: int = 0) -> bytes:
    rec = bytearray(384)
    nb, db = name.encode("cp932"), display.encode("cp932")
    rec[0:len(nb)] = nb
    rec[140:140 + len(db)] = db
    struct.pack_into("<H", rec, UW.UNIT_ID_OFFSET, unit_id)
    struct.pack_into("<H", rec, UW.UNIT_ID_OFFSET + 2, base_id)
    return bytes(rec)


def weapon_entry(name: str, short: str, anim: str) -> bytes:
    ent = bytearray(256)
    nb = name.encode("cp932")
    ent[UW.WP_NAME:UW.WP_NAME + len(nb)] = nb
    sb = short.encode("cp932")
    ent[UW.WP_SHORT_NAME:UW.WP_SHORT_NAME + len(sb)] = sb
    ab = anim.encode("ascii")
    ent[UW.WP_ANIM:UW.WP_ANIM + len(ab)] = ab
    struct.pack_into("<f", ent, 28, 1.0)
    return bytes(ent)


def wp_record(unit_id: int, entries) -> bytes:
    head = struct.pack("<3I", unit_id, len(entries), 0x100)
    return head + b"".join(entries)


def wp_table(records) -> bytes:
    """u32 first-offset at byte 4 (the layout inline_names.record_offsets expects)."""
    head = 4 + 4 * len(records)
    offs, body, pos = [], b"", head
    for rec in records:
        offs.append(pos)
        body += rec
        pos += len(rec)
    return struct.pack("<I", 0) + b"".join(struct.pack("<I", o) for o in offs) + body


def robo_dict(records) -> bytes:
    """records: list of (unit_id, aux, series).  Slot table of 7 u32, id pair at +28."""
    count = len(records)
    head = 4 + 4 * count
    offs, body, pos = [], b"", head
    for _ in records:
        offs.append(pos)
        pos += 0
    # build each record first, then fix offsets
    bodies = []
    for unit_id, aux, series in records:
        slots = [40, 48, 56, 64, 0, 0, 0]
        pre = struct.pack("<7I", *slots) + struct.pack("<HH", unit_id, aux)
        pre = pre.ljust(40, b"\x00")
        body_tail = b"L\x00" + b"W\x00" + b"\x00" + series.encode("cp932") + b"\x00"
        # keep slot[3] pointing at the series string inside the record
        slots[3] = 40 + len(b"L\x00") + len(b"W\x00") + 1
        rec = struct.pack("<7I", *slots) + struct.pack("<HH", unit_id, aux)
        rec = rec.ljust(40, b"\x00") + b"L\x00" + b"W\x00" + b"\x00" + series.encode("cp932") + b"\x00"
        bodies.append(rec)
    offs, body, pos = [], b"", head
    for rec in bodies:
        offs.append(pos)
        pos += len(rec)
    return struct.pack("<I", count) + b"".join(struct.pack("<I", o) for o in offs) + b"".join(bodies)


class UnitRowsTest(unittest.TestCase):
    def test_names_id_and_display(self):
        blob = unit_record("テスト", "テスト／標準", 138, 2) + unit_record("テスト改", "テスト改", 139)
        rows = UW.unit_rows(blob, "c.cpk", "unit_list00.bin")
        self.assertEqual([r["unit_id"] for r in rows], [138, 139])
        self.assertEqual(rows[0]["name"], "テスト")
        self.assertEqual(rows[0]["name_display"], "テスト／標準")
        self.assertEqual(rows[0]["base_id"], 2)
        self.assertEqual(rows[0]["fields84"][0], 138)

    def test_rejects_partial_record(self):
        self.assertEqual(UW.unit_rows(b"\x00" * 100, "c", "unit_list00.bin"), [])


class WpRowsTest(unittest.TestCase):
    def test_entry_offsets_and_token_decode(self):
        rec = wp_record(1000, [weapon_entry("ビーム・サーベル", "\x0f1ｰﾑ･ｻｰ\x0f5ﾙ", "s1000_003.bsb")])
        rows = UW.wp_rows(wp_table([rec]), "c.cpk", "wp_list00.bin")
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["unit_id"], 1000)
        self.assertEqual(row["weapon_count"], 1)
        self.assertTrue(row["size_ok"])
        ent = row["weapons"][0]
        self.assertEqual(ent["name"], "ビーム・サーベル")
        self.assertEqual(ent["name_short_raw"], "{31}ｰﾑ･ｻｰ{35}ﾙ")
        self.assertEqual(ent["name_short"], "ビｰﾑ･ｻｰベﾙ")
        self.assertEqual(ent["name_short_tokens"], [0x31, 0x35])
        self.assertTrue(ent["name_short_mapped"])
        self.assertEqual(ent["anim"], "s1000_003.bsb")

    def test_unmapped_token_is_flagged(self):
        raw, mapped, toks, fully = UW.short_name_forms(b"\x0f\xff\xb1")
        self.assertEqual(raw, "{FF}ｱ")
        self.assertFalse(fully)
        self.assertEqual(toks, [0xFF])

    def test_plain_short_form_has_no_tokens(self):
        raw, mapped, toks, fully = UW.short_name_forms("格闘".encode("cp932"))
        self.assertEqual((raw, mapped, toks, fully), ("格闘", "格闘", [], True))

    def test_size_mismatch_is_reported_not_hidden(self):
        rec = wp_record(5, [weapon_entry("Ａ", "ｱ", "s0005_001.bsb")]) + b"\x00" * 16
        rows = UW.wp_rows(wp_table([rec]), "c", "wp_list00.bin")
        self.assertFalse(rows[0]["size_ok"])


class CrossCheckTest(unittest.TestCase):
    def test_weapon_count_mismatch_is_reported(self):
        units = [
            {"unit_id": 1, "container": "c", "weapons": [1, 2, 3]},
            {"unit_id": 2, "container": "c", "weapons": [1]},
            {"unit_id": 4, "container": "c", "weapons": []},
        ]
        index = [{"unit_id": 1, "weapon_count": 3}, {"unit_id": 9, "weapon_count": 0},
                 {"unit_id": 2, "weapon_count": 2}]
        result = UW.unit_index_cross_check(units, index)
        self.assertEqual(result["matched"], 1)
        self.assertEqual(result["mismatched"], 1)
        self.assertEqual(result["missing"], 1)
        self.assertEqual(result["mismatched_units"][0]["unit_id"], 2)

    def test_offset_chain(self):
        rows = [{"weapon_count": 2, "table_offset": 1588},
                {"weapon_count": 1, "table_offset": 1588 + 12 + 512},
                {"weapon_count": 0, "table_offset": 1588 + 24 + 768}]
        self.assertTrue(UW.unit_index_offset_chain(rows))
        rows[2]["table_offset"] += 4
        self.assertFalse(UW.unit_index_offset_chain(rows))


class IdTablesTest(unittest.TestCase):
    def test_robo_cpkid_pairs(self):
        blob = struct.pack("<4H", 1, 0, 10, 33)
        self.assertEqual(UW.robo_cpkid_rows(blob), [(1, 0), (10, 33)])

    def test_robo_cpkid_rejects_odd_size(self):
        self.assertEqual(UW.robo_cpkid_rows(b"\x01\x00\x02"), [])

    def test_robo_dictionary_series_and_id(self):
        blob = robo_dict([(1, 161, "絶対無敵ライジンオー"), (10, 162, "絶対無敵ライジンオー")])
        rows = UW.robo_dictionary_rows(blob)
        self.assertEqual([r["unit_id"] for r in rows], [1, 10])
        self.assertEqual(rows[0]["series"], "絶対無敵ライジンオー")
        self.assertEqual(rows[0]["aux_id"], 161)

    def test_robo_dictionary_rejects_bad_offsets(self):
        blob = struct.pack("<I3I", 3, 16, 12, 20) + b"\x00" * 8
        self.assertEqual(UW.robo_dictionary_rows(blob), [])

    def test_unit_index_rows(self):
        body = struct.pack("<HHI", 1, 8, 1588) + struct.pack("<HHI", 10, 11, 3648)
        blob = struct.pack("<I", 2) + body
        rows = UW.unit_index_rows(blob)
        self.assertEqual(rows[0], {"row": 0, "unit_id": 1, "weapon_count": 8, "table_offset": 1588})
        self.assertEqual(rows[1]["unit_id"], 10)

    def test_unit_index_rejects_count_size_mismatch(self):
        self.assertEqual(UW.unit_index_rows(struct.pack("<I", 2) + b"\x00" * 8), [])

    def test_robolist_rows(self):
        rec = struct.pack("<4H", 1, 1, 0, 0) + b"r0001.pac".ljust(16, b"\x00")
        blob = struct.pack("<I", 1) + rec
        rows = UW.robolist_rows(blob)
        self.assertEqual(rows[0]["robolist_id"], 1)
        self.assertEqual(rows[0]["model"], "r0001.pac")


class CollectTest(unittest.TestCase):
    def test_collect_joins_weapons_series_and_model_dir(self):
        units = unit_record("テスト", "テスト", 1, 1) + unit_record("テスト二", "テスト二", 10, 0)
        wp = wp_table([wp_record(1, [weapon_entry("テスト砲", "ﾃｽﾄ砲", "s0001_001.bsb")]),
                       wp_record(10, [])])
        cpkid = struct.pack("<4H", 1, 0, 10, 33)
        rd = robo_dict([(1, 161, "テスト作品")])
        pac = _pac({"unit_list00.bin": units, "wp_list00.bin": wp,
                    "robo_cpkid00.bin": cpkid, "srw_DL_RoboDictionary00.bin": rd})

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "config00.pac").write_bytes(pac)
            data = _collect_with_fake_reader(tmp)

        self.assertEqual(data["summary"]["units"], 2)
        self.assertEqual(data["summary"]["weapons"], 1)
        self.assertEqual(data["summary"]["id_checks"][0]["ids_equal_in_order"], True)
        first = data["units"][0]
        self.assertEqual(first["weapons"][0]["name"], "テスト砲")
        self.assertEqual(first["series"], "テスト作品")
        self.assertEqual(first["model_dir"], "r0001")
        second = data["units"][1]
        self.assertEqual(second["weapons"], [])
        self.assertEqual(second["model_dir"], "r0050")


def _pac(entries) -> bytes:
    """Minimal config .pac index: entries at 0x10 stride 0x28 (u32 off, u32 size, name at +8)."""
    head = bytearray(0x800)
    body = bytearray()
    data_start = 0x2000
    for i, (name, blob) in enumerate(entries.items()):
        base = 0x10 + i * 0x28
        off = data_start + len(body)
        struct.pack_into("<2I", head, base, off, len(blob))
        nb = name.encode("ascii")
        head[base + 8:base + 8 + len(nb)] = nb
        pad = (-len(blob)) % 16
        body += blob + b"\x00" * pad
    out = bytes(head) + b"\x00" * (data_start - len(head)) + bytes(body)
    return out


class _FakeMembers:
    """Stand-in for speaker_map.read_members on a directory of .pac-only 'containers'."""

    def __init__(self, path: Path):
        self.path = path

    def __iter__(self):
        yield "config00.pac", self.path.read_bytes()


def _collect_with_fake_reader(tmp: Path) -> dict:
    import speaker_map as SM
    original = SM.read_members
    original_dirs = UW.robo_member_dirs
    SM.read_members = lambda p: _FakeMembers(p)
    UW.robo_member_dirs = lambda p: {0: "r0001", 33: "r0050"}
    try:
        return UW.collect([tmp / "config00.pac"], robo00=tmp / "robo00.cpk")
    finally:
        SM.read_members = original
        UW.robo_member_dirs = original_dirs


if __name__ == "__main__":
    unittest.main()
