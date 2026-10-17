"""Synthetic tests: no game prose or derived reading edition in test fixtures."""
import collections
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from reading_script_source import ReadingSource, paragraphs  # noqa: E402


def synthetic_source():
    source = ReadingSource.__new__(ReadingSource)
    source.names = collections.defaultdict(lambda: collections.defaultdict(set))
    source.names[4501]["nickname"].add("Seishiro")
    source.names[1]["nickname"].add("Alice")
    source.names[2]["name_short"].add("Bob")
    return source


def row(text="A synthetic line.", *, key=1, kind="dialogue", jp="fixture"):
    return {"id": "synthetic:1", "order": 1, "kind": kind, "en": text, "jp": jp,
            "speaker": {"id": key, "jp": "speaker fixture"} if kind == "dialogue" else None}


class ReadingSourceTests(unittest.TestCase):
    def test_soft_wraps_and_crlf_are_not_new_dialogue(self):
        self.assertEqual(paragraphs(" First line\r\ncontinues.\r\n"), ("First line continues.",))

    def test_paragraphs_are_preserved(self):
        self.assertEqual(paragraphs("First\nparagraph.\n \nSecond.\n"),
                         ("First paragraph.", "Second."))
        self.assertNotEqual(paragraphs("One\n\nTwo"), paragraphs("One\nTwo"))

    def test_internal_spacing_and_punctuation_are_not_rewritten(self):
        self.assertEqual(paragraphs("One  two…"), ("One  two…",))
        self.assertNotEqual(paragraphs("Yes."), paragraphs("Yes!"))

    def test_unknown_inline_prefix_stops_work(self):
        with self.assertRaisesRegex(ValueError, "Unreviewed speaker prefix"):
            synthetic_source().make_entry(row("＃NewRole\nA line."))

    def test_anonymous_prefix_does_not_reveal_portrait_identity(self):
        result = synthetic_source().make_entry(row("＃???\nA line.", jp="＃？？？\nfixture"))
        self.assertEqual(result.speaker, "???")
        self.assertEqual(result.text, ("A line.",))

    def test_source_anonymity_survives_missing_en_prefix(self):
        result = synthetic_source().make_entry(row("A line.", jp="＃？？？\nfixture"))
        self.assertEqual(result.speaker, "???")

    def test_dynamic_name_is_display_only(self):
        original = row("Hello, ＜主人公名＞!")
        result = synthetic_source().make_entry(original)
        self.assertEqual(result.text, ("Hello, Seishiro!",))
        self.assertEqual(original["en"], "Hello, ＜主人公名＞!")

    def test_unreviewed_token_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Unreviewed token"):
            synthetic_source().make_entry(row("＜UNKNOWN＞"))

    def test_speaker_only_change_is_not_an_alias(self):
        source = synthetic_source()
        self.assertNotEqual(source.make_entry(row(key=1)).identity,
                            source.make_entry(row(key=2)).identity)

    def test_punctuation_only_change_is_not_an_alias(self):
        source = synthetic_source()
        self.assertNotEqual(source.make_entry(row("Yes.")).identity,
                            source.make_entry(row("Yes!")).identity)

    def test_heading_is_not_dialogue_and_keeps_its_text(self):
        source = synthetic_source()
        entry = source.make_entry(row("＃Synthetic room", kind="location"))
        self.assertEqual(entry.text, ("Synthetic room",))
        self.assertIsNone(entry.speaker)
        self.assertNotEqual(entry.identity, source.make_entry(row("Synthetic room")).identity)

    def test_short_name_fallback(self):
        self.assertEqual(synthetic_source().make_entry(row(key=2)).speaker, "Bob")

    def test_shared_short_names_use_sourced_full_names(self):
        source = synthetic_source()
        source.names[2]["name_short"] = {"Alice"}
        source.names[1]["name_full"] = {"Alice North"}
        source.names[2]["name_full"] = {"Alice South"}
        source.rows = {"scene": [row(key=1), row(key=2)]}
        source.prepare_speakers()
        self.assertEqual(source.make_entry(row(key=1)).speaker, "Alice North")
        self.assertEqual(source.make_entry(row(key=2)).speaker, "Alice South")
        self.assertEqual(source.make_entry(row(key=1, jp="＃？？？\nfixture")).speaker, "???")

    def test_duplicate_portraits_do_not_force_a_full_name(self):
        source = synthetic_source()
        source.names[2]["name_short"] = {"Alice"}
        source.names[1]["name_full"] = {"Alice North"}
        source.names[2]["name_full"] = {"Alice North"}
        source.rows = {"scene": [row(key=1), row(key=2)]}
        source.prepare_speakers()
        self.assertEqual(source.make_entry(row(key=1)).speaker, "Alice")

    def test_conflicting_names_stop_work(self):
        source = synthetic_source()
        source.names[1]["nickname"].add("Another Alice")
        with self.assertRaisesRegex(ValueError, "Conflicting English names"):
            source.make_entry(row())

    def test_empty_body_after_prefix_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, "No readable text"):
            synthetic_source().make_entry(row("＃???\n"))


if __name__ == "__main__":
    unittest.main()
