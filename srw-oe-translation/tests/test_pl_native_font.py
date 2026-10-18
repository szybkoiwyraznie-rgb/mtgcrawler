"""Native ASCII bodies are copied exactly; only sparse diacritics may differ."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import font_pl as F
import pl_glyph_compose as C
from test_font_pl import _synthetic_container


class NativeFontTests(unittest.TestCase):
    def setUp(self):
        self.ank = F.parse_container(_synthetic_container())[0]["ank.fta"]
        self.glyphs = F.load_glyphs(self.ank)
        self.patched = F.build_ank_patch(self.ank, self.glyphs)

    def test_all_18_use_correct_native_base(self):
        self.assertEqual("".join(C.BASE_LETTERS), "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
        self.assertEqual("".join(C.BASE_LETTERS.values()), "acelnoszzACELNOSZZ")

    def test_pixels_outside_mark_mask_are_exact_not_rescaled(self):
        for letter, source in C.BASE_LETTERS.items():
            before = C.ascii_rows(self.ank, source)
            mask = C.accent_mask(letter, before)
            self.assertLessEqual(len(mask), 6)
            for y in range(14):
                for x in range(8):
                    if (x, y) not in mask:
                        self.assertEqual(self.glyphs[letter][y][x], before[y][x])

    def test_body_height_and_weight_are_identical_except_crossing_stroke(self):
        for letter, source in C.BASE_LETTERS.items():
            if letter.lower() == "ł":
                continue  # the crossing stroke must change a few body pixels
            before = C.ascii_rows(self.ank, source)
            self.assertEqual(self.glyphs[letter][3:12], before[3:12])
            # Capitals start on row 2, lowercase bodies start lower: preserve both.
            self.assertEqual(self.glyphs[letter][2][0:3], before[2][0:3])

    def test_no_peak_increase_or_pixel_removal(self):
        for letter, source in C.BASE_LETTERS.items():
            before = C.ascii_rows(self.ank, source)
            self.assertEqual(max(map(max, self.glyphs[letter])), max(map(max, before)))
            self.assertTrue(all(a >= b for r, q in zip(self.glyphs[letter], before)
                                for a, b in zip(r, q)))

    def test_new_marks_do_not_need_external_font_or_glyph_json(self):
        # Changes in original source are reflected, not ignored by a cached raster.
        modified = bytearray(self.ank)
        offset = (ord("c") - 0x20) * 56 + 9 * 4 + 1
        modified[offset] = 0x28
        actual = F.load_glyphs(bytes(modified))["ć"]
        self.assertEqual(actual[9][2:4], [8, 2])

    def test_independent_audit_accepts_original_and_marks(self):
        report = C.verify_native(self.ank, self.patched, F.pl_byte_map())
        self.assertTrue(report["ok"], report)
        self.assertEqual(len(report["letters"]), 18)
        for letter in report["letters"].values():
            self.assertEqual(letter["native_peak"], letter["output_peak"])
            self.assertGreater(letter["accent_pixels_changed"], 0)
            self.assertLessEqual(letter["accent_pixels_changed"], 6)

    def test_independent_audit_refuses_boldening_shifting_or_missing_mark(self):
        for label in ("bold", "shift", "missing_mark"):
            with self.subTest(label=label):
                rows = [r[:] for r in self.glyphs["ć"]]
                if label == "bold":
                    rows[9][1] = 15
                elif label == "shift":
                    rows = [[0] * 8] + rows[:-1]
                else:
                    rows = C.ascii_rows(self.ank, "c")
                bad = bytearray(self.patched)
                offset = (F.PL_BYTES[1] - 0x40) * 56
                bad[offset:offset + 56] = F.ank_cell(rows)
                report = C.verify_native(self.ank, bytes(bad), F.pl_byte_map())
                self.assertFalse(report["ok"])

    def test_independent_audit_refuses_changed_original_ascii(self):
        bad = bytearray(self.patched)
        bad[(ord("c") - 0x20) * 56 + 20] ^= 0xFF
        self.assertIn("ASCII source cells changed",
                      C.verify_native(self.ank, bytes(bad), F.pl_byte_map())["failures"])

    def test_missing_blank_or_invalid_source_refused(self):
        for ank in (b"", bytes(len(self.ank))):
            with self.assertRaises(ValueError):
                F.load_glyphs(ank)
        with self.assertRaises(ValueError):
            C.accent_mask("ć", [[16] * 8] * 14)
        with self.assertRaises(ValueError):
            C.accent_mask("x", [[0] * 8] * 14)

    def test_no_room_for_tail_or_acute_is_not_silently_clipped(self):
        rows = C.ascii_rows(self.ank, "a")
        rows[13][3] = 9
        with self.assertRaises(ValueError):
            C.accent_mask("ą", rows)
        rows = C.ascii_rows(self.ank, "C")
        rows[0][4] = 9
        with self.assertRaises(ValueError):
            C.accent_mask("Ć", rows)

    def test_real_original_source_and_new_body(self):
        path = ROOT.parent / "google_drive/font.cpk"
        if not path.is_file():
            self.skipTest("private font absent")
        import verify_pl_test as V
        ank = V.font_members(path.read_bytes())["ank.fta"]
        glyphs = F.load_glyphs(ank)
        patched = F.build_ank_patch(ank, glyphs)
        report = C.verify_native(ank, patched, F.pl_byte_map())
        self.assertTrue(report["ok"], report)
        for letter, source in C.BASE_LETTERS.items():
            native = C.ascii_rows(ank, source)
            if letter.lower() != "ł":
                self.assertEqual(glyphs[letter][3:12], native[3:12])
            self.assertEqual(report["letters"][letter]["output_peak"],
                             report["letters"][letter]["native_peak"])


if __name__ == "__main__":
    unittest.main()
