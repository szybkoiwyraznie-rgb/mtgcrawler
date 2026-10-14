"""sysmes_pack: measured layout (relative pointer table, sequential pool) and its rewrite."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import sysmes_pack as sp  # noqa: E402

LABELS = ["Ａ", "表示切換", "ゲームスタート", "ライブラリー", "リファレンス", "クレジット",
          "ダウンロードリスト", "データインストール"]


class LayoutTests(unittest.TestCase):
    def test_make_and_parse_round_trip(self):
        sm = sp.make_sysmes(LABELS, ids=[2, 3, 0x28C, 0x28D, 0x28E, 0x28F, 0x2C6])
        parsed = sp.parse(sm)
        self.assertEqual(parsed.count, len(LABELS))
        self.assertEqual(parsed.base, sp.HEADER_LEN + sp.ENTRY_LEN * len(LABELS) - 4)
        self.assertEqual([s.decode("cp932") for s in parsed.strings], LABELS)
        self.assertEqual(parsed.ids, [2, 3, 0x28C, 0x28D, 0x28E, 0x28F, 0x2C6])
        self.assertEqual(sp.build(parsed, parsed.strings), sm)
        # the pool starts ON the last table word: string 0 is that word
        self.assertEqual(sm[parsed.base:parsed.base + 4], "Ａ".encode("cp932") + b"\x00\x00")
        self.assertEqual(struct.unpack_from("<I", sm, 4)[0], len(sm))

    def test_pointer_words_are_relative_sequential_offsets(self):
        sm = sp.make_sysmes(LABELS)
        parsed = sp.parse(sm)
        for k, start in enumerate(parsed.starts):
            word = struct.unpack_from("<I", sm, sp.HEADER_LEN + sp.ENTRY_LEN * k)[0]
            self.assertEqual(word, start - parsed.base)
            end = sm.index(b"\x00", start)
            self.assertEqual(sm[start:end].decode("cp932"), LABELS[k])

    def test_parse_refuses_a_table_that_does_not_match_the_pool(self):
        sm = bytearray(sp.make_sysmes(LABELS))
        struct.pack_into("<I", sm, sp.HEADER_LEN + sp.ENTRY_LEN * 3, 0x1234)
        with self.assertRaises(sp.SysmesError):
            sp.parse(bytes(sm))
        sm = bytearray(sp.make_sysmes(LABELS))
        struct.pack_into("<I", sm, 4, 7)
        with self.assertRaises(sp.SysmesError):
            sp.parse(bytes(sm))


class TranslateTests(unittest.TestCase):
    def test_grown_label_moves_every_later_entry_and_keeps_ids(self):
        sm = sp.make_sysmes(LABELS)
        edits = {"ライブラリー".encode("cp932"): b"LIBRARY OF EVERYTHING",
                 "クレジット".encode("cp932"): b"CREDITS"}
        new, report = sp.translate_bytes(sm, edits)
        self.assertEqual(sp.verify(sm, new, edits), [])
        before, after = sp.parse(sm), sp.parse(new)
        self.assertEqual(before.ids, after.ids)
        self.assertEqual(after.strings[3], b"LIBRARY OF EVERYTHING")
        self.assertEqual(after.strings[5], b"CREDITS")
        self.assertEqual(after.strings[6], "ダウンロードリスト".encode("cp932"))
        # every pointer still resolves to its own string (relative offsets rewritten)
        for k, start in enumerate(after.starts):
            self.assertEqual(struct.unpack_from("<I", new, sp.HEADER_LEN + sp.ENTRY_LEN * k)[0],
                             start - after.base)
        self.assertEqual(report["replaced"], 2)
        self.assertEqual(report["unmatched"], [])
        self.assertEqual(struct.unpack_from("<I", new, 4)[0], len(new))

    def test_equal_strings_are_replaced_everywhere_and_string_zero_never(self):
        sm = sp.make_sysmes(["Ａ", "ライブラリー", "オプション", "ライブラリー", "Ａ"])
        new, report = sp.translate_bytes(sm, {"ライブラリー".encode("cp932"): b"LIBRARY",
                                              "Ａ".encode("cp932"): b"A"})
        strings = sp.parse(new).strings
        self.assertEqual(strings, ["Ａ".encode("cp932"), b"LIBRARY", "オプション".encode("cp932"),
                                   b"LIBRARY", b"A"])
        self.assertEqual(report["replaced_entries"], 3)

    def test_apply_edits_exact_match_only(self):
        sm = sp.make_sysmes(["Ａ", "ライブラリー", "ライブラリーを閲覧できます。"])
        new = sp.apply_edits(sm, {"ライブラリー": "LIBRARY"})
        self.assertEqual(sp.parse(new).strings[1], b"LIBRARY")
        self.assertEqual(sp.parse(new).strings[2], "ライブラリーを閲覧できます。".encode("cp932"))

    def test_grow_one_by_offset(self):
        sm = sp.make_sysmes(LABELS)
        off = sp.parse(sm).starts[2]
        new = sp.grow_one(sm, off, "START GAME NOW")
        self.assertEqual(sp.parse(new).strings[2], b"START GAME NOW")
        with self.assertRaises(sp.SysmesError):
            sp.grow_one(sm, off + 2, "x")

    def test_verify_reports_foreign_changes(self):
        sm = sp.make_sysmes(LABELS)
        new = sp.apply_edits(sm, {"クレジット": "CREDITS"})
        self.assertTrue(sp.verify(sm, new, {}))
        self.assertEqual(sp.verify(sm, new, {"クレジット".encode("cp932"): b"CREDITS"}), [])
        self.assertEqual(sp.string_starts(new), sp.parse(new).starts)


if __name__ == "__main__":
    unittest.main()
