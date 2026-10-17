"""Synthetic catalogue presentation tests; no copied game text fixtures."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mech_catalog import format_description, clean_description, canonical_form_name, md, unique
from mech_catalog_sources import group_rows


class CatalogueTests(unittest.TestCase):
    def test_printf_arguments_are_not_recursive(self):
        self.assertEqual(format_description("A %s B %s", ["%s", "C"]), "A %s B C")

    def test_percent_is_unescaped_once(self):
        self.assertEqual(format_description("%s10%%", ["HP+"]), "HP+10%")

    def test_joined_fragment_word_boundaries(self):
        self.assertEqual(format_description("%s100%s", ["Energy", "or more"]), "Energy 100 or more")

    def test_colour_completion_is_not_separated(self):
        self.assertEqual(clean_description(format_description("%s6Sky＠0", ['"＠'])), '"Sky')

    def test_remove_only_the_redundant_leading_label(self):
        self.assertEqual(clean_description("＠4<Test Lv1>＠0 Atk+2\nCondition: <example>"),
                         "Atk+2\nCondition: <example>")

    def test_leftover_placeholder_is_not_hidden(self):
        with self.assertRaisesRegex(ValueError, "Unrendered"):
            clean_description("Still %s")
        with self.assertRaises(ValueError):
            format_description("%s %s", ["one"])

    def test_japanese_leftover_is_not_hidden(self):
        with self.assertRaisesRegex(ValueError, "Unrendered"):
            clean_description("未解決")

    def test_series_form_matching_keeps_pilot_qualifiers(self):
        self.assertEqual(canonical_form_name("Ｒｏｂｏ／飛行"), "Robo")
        self.assertNotEqual(canonical_form_name("Robo(Keroro)"), canonical_form_name("Robo"))

    def test_table_and_html_characters_are_escaped(self):
        self.assertEqual(md("A|B\n<tag> & *x*"), r"A\|B<br>&lt;tag&gt; &amp; \*x\*")

    def test_duplicate_keys_cannot_silently_overwrite(self):
        with self.assertRaises(ValueError):
            unique([{"id": 1}, {"id": 1}], lambda r: r["id"])

    def test_group_has_a_100_byte_record_and_explicit_count(self):
        raw = bytearray(100)
        raw[:6] = b"Group\0"
        struct.pack_into("<4H", raw, 32, 7, 2, 11, 12)
        self.assertEqual(group_rows(bytes(raw))[0]["members"], [11, 12])
        with self.assertRaises(ValueError):
            group_rows(bytes(raw[:-1]))
        struct.pack_into("<H", raw, 34, 1)
        with self.assertRaises(ValueError):
            group_rows(bytes(raw))


if __name__ == "__main__":
    unittest.main()
