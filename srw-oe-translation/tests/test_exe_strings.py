# -*- coding: utf-8 -*-
"""exe_strings on a synthetic relocatable ELF (tests/exe_fixtures.py) - no game bytes.

Covers: reference discovery (HI16/LO16 pairs by register, interleaved ``lui``, ``R_MIPS_32``
pointers), run splitting into exact segments, float constants in front of a string, the trailing
level-2 kanji trim, alignment slack, text classification, English checks (budget, printf
conversions, 0x0F tokens, exact-segment padding), in-place apply with fail-closed refusal, and
the CWCheat lines.
"""
import json
import struct
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
sys.path.insert(0, str(HERE))

import exe_strings as X  # noqa: E402
from exe_fixtures import Builder, cp932  # noqa: E402


def _by_jp(rows):
    return {r["jp"]: r for r in rows}


def _fixture():
    b = Builder()
    s_after = b.string("after", cp932("移動後"))                    # 6 B + NUL + 1 pad → slack 1
    s_enemy = b.string("enemy", cp932("敵"))                        # 2 B + NUL + 1 pad → slack 1
    s_move = b.string("move", cp932("移動"), align=8)               # 4 B + NUL + 3 pad → slack 3
    s_guard = b.string("guard", cp932("ダメージ-16% 発動率12%"))
    s_pilot = b.string("pilot", cp932("パイロット：剴"))             # stray level-2 kanji tail
    # a float constant without a NUL right in front of the string
    s_float = b.raw_bytes(struct.pack("<f", 1.5))
    s_fmt = b.string("fmt", "第%d話までクリア　".encode("utf-8"))
    coord = cp932("＠4<連携攻撃 Lv1>＠0 包囲率+30% 全機が攻撃")
    s_coord = b.string("coord", coord)                              # split by a 2nd reference
    s_junk = b.string("junk", b"UUUU")                              # a float that is valid cp932
    s_data = b.string("data", cp932("未使用"), section="data")
    s_table = b.raw_bytes(cp932("攻撃"))                            # text + referenced float = table
    s_tablef = b.raw_bytes(struct.pack("<f", 1234.5678) + b"\0")
    b.addr["table"] = s_table
    s_plain = b.string("plain", b"Hello")                           # ASCII only: never a row

    b.ref_pair(s_after, reg=4)
    b.ref_interleaved(s_enemy, s_move, reg_a=4, reg_b=5)
    b.ref_pair(s_guard, reg=6)
    b.ref_pair(s_pilot, reg=7)
    b.ref_pair(s_float, reg=8)
    b.ref_pair(s_fmt, reg=9)
    b.ref_pair(s_coord, reg=4)
    b.ref_pair(s_coord + 19, reg=5)                                 # the code prints the tail too
    b.ref_pair(s_junk, reg=4)
    b.ref_pointer(s_data)
    b.ref_pair(s_table, reg=4)
    b.ref_pair(s_tablef, reg=5)
    b.ref_pair(s_plain, reg=4)
    return b, b.build()


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.b, self.blob = _fixture()
        self.elf = X.Elf(self.blob)

    def test_sections_and_segment(self):
        self.assertEqual(len(self.elf.segments), 1)
        self.assertEqual([n for n, _a, _b in self.elf.text_ranges()], [".rodata", ".data"])
        self.assertEqual(self.elf.file_offset(0x1000), 0x80 + 0x1000)
        self.assertIsNone(self.elf.file_offset(0x20000))

    def test_pairs_by_register_and_pointer(self):
        refs = self.elf.referenced()
        for key in ("after", "enemy", "move", "guard", "pilot", "fmt", "coord", "data", "table"):
            self.assertIn(self.b.addr[key], refs, key)
        self.assertEqual(refs[self.b.addr["coord"]], 1)
        self.assertEqual(refs[self.b.addr["coord"] + 19], 1)
        # naive "last lui" pairing would have invented enemy+ (move.lo - enemy.lo); it must not
        bad = self.b.addr["enemy"] + ((self.b.addr["move"] & 0xFFFF) - (self.b.addr["enemy"] & 0xFFFF))
        if bad not in self.b.addr.values():
            self.assertNotIn(bad, refs)


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.b, self.blob = _fixture()
        self.rows, self.rejects = X.extract_rows(X.Elf(self.blob), include_rejects=True)
        self.by = _by_jp(self.rows)

    def test_rows_found_and_junk_rejected(self):
        jps = set(self.by)
        for jp in ("移動後", "敵", "移動", "ダメージ-16% 発動率12%", "パイロット：", "第%d話までクリア　",
                   "未使用"):
            self.assertIn(jp, jps, jp)
        self.assertNotIn("UUUU", jps)
        self.assertNotIn("Hello", jps)
        self.assertFalse(any(r["jp"].startswith("攻撃") for r in self.rows), "constant table")
        self.assertTrue(any(r["cp932"].startswith("攻撃") for r in self.rejects))

    def test_slack_and_budget(self):
        self.assertEqual((self.by["敵"]["bytes"], self.by["敵"]["max_bytes"]), (2, 3))
        self.assertEqual(self.by["敵"]["source"]["slack"], 1)
        self.assertEqual((self.by["移動"]["bytes"], self.by["移動"]["max_bytes"]), (4, 7))
        self.assertEqual((self.by["移動後"]["bytes"], self.by["移動後"]["max_bytes"]), (6, 7))
        row = self.by["ダメージ-16% 発動率12%"]                       # 20 B + NUL → 3 pad bytes
        self.assertEqual((row["bytes"], row["max_bytes"], row["source"]["slack"]), (22, 23, 1))

    def test_trimmed_tail(self):
        row = self.by["パイロット："]
        self.assertEqual(row["source"]["trimmed_tail"], 2)
        self.assertEqual(row["bytes"], 12)
        self.assertEqual(row["max_bytes"], 11)
        self.assertNotIn("slack", row["source"])

    def test_utf8_row(self):
        row = self.by["第%d話までクリア　"]
        self.assertEqual(row["source"]["encoding"], "utf-8")
        self.assertEqual(row["bytes"], len("第%d話までクリア　".encode("utf-8")))

    def test_float_in_front_is_skipped(self):
        # the float bytes 00 00 c0 3f precede the UTF-8 string without a NUL between -
        # the UTF-8 row starts at the string, not at the float
        row = self.by["第%d話までクリア　"]
        self.assertEqual(row["source"]["offset"], 0x80 + self.b.addr["fmt"])

    def test_split_run_segments(self):
        head = [r for r in self.rows if r["source"]["offset"] == 0x80 + self.b.addr["coord"]][0]
        tail = [r for r in self.rows if r["source"]["offset"] == 0x80 + self.b.addr["coord"] + 19][0]
        self.assertTrue(head["source"]["exact"])
        self.assertEqual(head["bytes"], 19)
        self.assertEqual(head["max_bytes"], 19)
        self.assertTrue(head["jp"].endswith("＠"))
        self.assertNotIn("exact", tail["source"])
        self.assertEqual(head["jp"] + tail["jp"], "＠4<連携攻撃 Lv1>＠0 包囲率+30% 全機が攻撃")

    def test_row_schema(self):
        row = self.by["移動後"]
        self.assertEqual(row["category"], "exe")
        self.assertEqual(row["mode"], "slot")
        self.assertEqual(row["id"], "exe:PBOOT.PBP/DATA.PSP:0x%08x" % (X.LOAD_BASE + self.b.addr["after"]))
        self.assertEqual(row["source"]["container"], "PBOOT.PBP")
        self.assertEqual(row["source"]["member"], "DATA.PSP")
        self.assertEqual(row["en"], "")
        json.dumps(row, ensure_ascii=False)

    def test_data_section_pointer(self):
        row = self.by["未使用"]
        self.assertEqual(row["source"]["offset"], 0x80 + self.b.addr["data"])


class ClassifyTests(unittest.TestCase):
    def test_accepts_game_text(self):
        for text in ("＠0", "歌", "ｻﾎﾟｰﾄ", "未使用", "？？", "移動後", "回避-22%", "ＥＮ不足",
                     "\x0f*ﾒｰ\x0f&-20%", "＠4<貫通 Lv1>＠0 敵の防御-30%"):
            self.assertIsNotNone(X.classify_text(cp932(text)), text)

    def test_rejects_constants_and_ascii(self):
        for raw in (b"UUUU", cp932("囮劔"), b"\x00\x00\xc0\x3f", b"Hello", b"\x33\x33\xb3\x3f", b"A",
                    cp932("ｼG0"), b"\x0f\x00ab"):
            self.assertIsNone(X.classify_text(raw), raw)

    def test_utf8_detected(self):
        text, enc = X.classify_text("第%d話までクリア".encode("utf-8"))
        self.assertEqual((text, enc), ("第%d話までクリア", "utf-8"))

    def test_trim_tail(self):
        self.assertEqual(X.trim_tail("パイロット：剴", "cp932"), ("パイロット：", 1))
        self.assertEqual(X.trim_tail("移動後", "cp932"), ("移動後", 0))
        self.assertEqual(X.trim_tail("囮劔囮劔", "cp932")[1], 0)


def _row(jp, en, max_bytes=None, exact=False, slack=0, trimmed=0, encoding="cp932"):
    region = len(X.encode_text(jp, encoding))
    if max_bytes is None:
        max_bytes = region - 1 if trimmed else region + slack
    src = {"container": "PBOOT.PBP", "member": "DATA.PSP", "offset": 0, "vaddr": "0x08804000",
           "refs": 1, "encoding": encoding}
    if exact:
        src["exact"] = True
    if slack:
        src["slack"] = slack
    if trimmed:
        src["trimmed_tail"] = trimmed
    return {"id": "exe:x", "category": "exe", "part": "label", "jp": jp, "en": en, "bytes": region,
            "mode": "slot", "max_bytes": max_bytes, "source": src}


class CheckEnTests(unittest.TestCase):
    def test_budget(self):
        enc, why = X.check_en(_row("移動後", "Post-Mv", slack=1))
        self.assertEqual(enc, b"Post-Mv")                            # 6 + 1 slack; the old NUL follows
        enc, why = X.check_en(_row("移動後", "Post-Move", slack=1))
        self.assertIsNone(enc)
        self.assertIn("over budget", why)
        enc, why = X.check_en(_row("敵", "Foe", slack=1))
        self.assertEqual(enc, b"Foe")

    def test_padding_fills_the_slot(self):
        enc, _ = X.check_en(_row("移動", "Move", slack=3))
        self.assertEqual(enc, b"Move\0\0\0")                        # region + slack; the old NUL stays

    def test_trimmed_keeps_terminator_inside(self):
        enc, _ = X.check_en(_row("パイロット：", "Pilot:", trimmed=2))
        self.assertEqual(enc, b"Pilot:" + b"\0" * 6)
        enc, why = X.check_en(_row("パイロット：", "Pilot label!", trimmed=2))
        self.assertIsNone(enc)

    def test_format_conversions_must_match(self):
        self.assertIsNotNone(X.check_en(_row("%s ×%2d を入手しました。", "Obtained %s x%2d."))[0])
        enc, why = X.check_en(_row("%s ×%2d を入手しました。", "Obtained %2d x%s."))
        self.assertIsNone(enc)
        self.assertIn("printf", why)
        # a bare '%' in ordinary text is not a conversion
        self.assertIsNotNone(X.check_en(_row("ダメージ-16% 発動率12%", "Dmg-16% Trigger 12%"))[0])
        self.assertIsNotNone(X.check_en(_row("＠０命＠２%+3d%%", "＠０Acc＠２%+3d%%", slack=3))[0])
        self.assertIsNotNone(X.check_en(_row("%s%s%-TEXT_SPACE_ROBOs＠0", "%s%s%-TEXT_SPACE_ROBOs＠0"))[0])

    def test_kana_token_refused(self):
        enc, why = X.check_en(_row("\x0f*ﾒｰ\x0f&-20%", "\x0f*Dmg-20%"))
        self.assertIsNone(enc)
        self.assertIn("0x0F", why)
        self.assertEqual(X.check_en(_row("\x0f*ﾒｰ\x0f&-20%", "Dmg-20%"))[0], b"Dmg-20%\0\0\0")

    def test_exact_segment_space_padded_before_split_code(self):
        jp = "＠4<連携攻撃 Lv1>＠"
        enc, why = X.check_en(_row(jp, "＠4<Coord Lv1>＠", exact=True))
        self.assertIsNone(why)
        self.assertEqual(len(enc), len(cp932(jp)))
        self.assertTrue(enc.endswith(b" " + cp932("＠")))
        enc, why = X.check_en(_row(jp, "＠4<Coord Lv1>", exact=True))
        self.assertIsNone(enc)
        enc, why = X.check_en(_row(jp, "＠4<Coordinated Atk Lv1>＠", exact=True))
        self.assertIsNone(enc)

    def test_utf8_row_encodes_utf8(self):
        enc, _ = X.check_en(_row("第%d話までクリア　", "Cleared up to Ep. %d", encoding="utf-8"))
        self.assertTrue(enc.startswith(b"Cleared up to Ep. %d\0"))
        self.assertEqual(len(enc), len("第%d話までクリア　".encode("utf-8")))

    def test_empty_english(self):
        self.assertEqual(X.check_en(_row("敵", ""))[1], "empty")


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.b, self.blob = _fixture()
        self.rows, _ = X.extract_rows(X.Elf(self.blob))
        self.by = _by_jp(self.rows)

    def test_apply_in_place(self):
        self.by["敵"]["en"] = "Foe"
        self.by["移動"]["en"] = "Move"
        self.by["移動後"]["en"] = "Post-Mv"
        self.by["パイロット："]["en"] = "Pilot:"
        self.by["第%d話までクリア　"]["en"] = "Cleared up to Ep. %d"
        out, report = X.apply_rows(self.blob, self.rows)
        self.assertEqual(report["applied"], 5)
        self.assertEqual(report["skipped"], [])
        self.assertEqual(len(out), len(self.blob))
        off = 0x80 + self.b.addr["enemy"]
        self.assertEqual(out[off:off + 4], b"Foe\0")
        off = 0x80 + self.b.addr["pilot"]
        self.assertEqual(out[off:off + 12], b"Pilot:" + b"\0" * 6)
        off = 0x80 + self.b.addr["fmt"]
        self.assertTrue(out[off:].startswith(b"Cleared up to Ep. %d\0"))
        # everything outside the rows is untouched
        diff = [i for i, (x, y) in enumerate(zip(self.blob, out)) if x != y]
        owned = set()
        for key, span in (("enemy", 4), ("move", 8), ("after", 8), ("pilot", 12), ("fmt", 26)):
            owned.update(range(0x80 + self.b.addr[key], 0x80 + self.b.addr[key] + span))
        self.assertTrue(set(diff) <= owned)
        self.assertEqual(X.verify_build(self.blob, self.rows)[0], len(self.rows))

    def test_refuses_wrong_build(self):
        self.by["敵"]["en"] = "Foe"
        other = bytearray(self.blob)
        off = 0x80 + self.b.addr["enemy"]
        other[off:off + 2] = cp932("他")
        out, report = X.apply_rows(bytes(other), self.rows)
        self.assertEqual(report["applied"], 0)
        self.assertEqual(len(report["skipped"]), 1)
        self.assertIn("japanese bytes not at offset", report["skipped"][0]["reason"])
        self.assertEqual(out, bytes(other))

    def test_refuses_bad_english_without_touching(self):
        self.by["敵"]["en"] = "Enemy"
        out, report = X.apply_rows(self.blob, self.rows)
        self.assertEqual(report["applied"], 0)
        self.assertIn("over budget", report["skipped"][0]["reason"])
        self.assertEqual(out, self.blob)

    def test_refuses_when_padding_is_not_zero(self):
        row = self.by["敵"]
        row["en"] = "Foe"
        tampered = bytearray(self.blob)
        tampered[0x80 + self.b.addr["enemy"] + 3] = 0x41        # the pad byte is in use
        out, report = X.apply_rows(bytes(tampered), self.rows)
        self.assertEqual(report["applied"], 0)
        self.assertIn("padding", report["skipped"][0]["reason"])

    def test_cheat_lines(self):
        self.by["敵"]["en"] = "Foe"
        self.by["移動"]["en"] = "Move"
        lines, report = X.cheat_lines(self.blob, self.rows)
        self.assertEqual(report["applied"], 2)
        addr = X.LOAD_BASE + self.b.addr["enemy"] - X.CWCHEAT_BASE
        self.assertIn("_L 0x2%07X 0x%08X" % (addr, struct.unpack("<I", b"Foe\0")[0]), lines)
        addr = X.LOAD_BASE + self.b.addr["move"] - X.CWCHEAT_BASE
        self.assertIn("_L 0x2%07X 0x%08X" % (addr, struct.unpack("<I", b"Move")[0]), lines)
        self.assertIn("_L 0x2%07X 0x00000000" % (addr + 4), lines)
        self.assertTrue(all(line.startswith("_L 0x2") for line in lines), lines)
        text, _ = X.cheat_file(self.blob, self.rows)
        self.assertTrue(text.startswith("_S NPJH-50521\n_G "))
        self.assertIn("_C1 ", text)


if __name__ == "__main__":
    unittest.main()
