"""Tests for tools/rewrite_units.py — the equal-length write-back."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import extract_event_text  # noqa: E402
import rewrite_units  # noqa: E402

HEADER = b"\x01\x00\x00\x00\x00\x00"
TEXTS = [b"first line of text", b"second line", b"third line here"]


def build(texts: list[bytes]) -> bytes:
    body = bytearray()
    for text in texts:
        body += HEADER + b"\xff\xff" + text + b"\x00\x00"
    return bytes(body)


def rows_for(name: str, texts: list[bytes], targets: list[str | None]) -> list[dict[str, str]]:
    """CSV rows whose unit_ids and source views are derived from the real file layout."""
    rows = []
    offset = 0
    for text, target in zip(texts, targets):
        start = offset + len(HEADER) + 2
        source = extract_event_text.to_view(text)
        rows.append(
            {
                "unit_id": f"{name}@{start:04X}",
                "package_id": "p001-test",
                "file": name,
                "source_text": source,
                "target_text": source if target is None else target,
                "budget_bytes": str(len(text)),
                "status": "",
                "note": "",
            }
        )
        offset += len(HEADER) + 2 + len(text) + 2
    return rows


class UnitIdTest(unittest.TestCase):
    def test_unit_id_carries_the_file_and_the_offset(self):
        self.assertEqual(rewrite_units.parse_unit_id("a.bin@001A"), ("a.bin", 0x1A))

    def test_a_file_name_containing_at_is_split_on_the_last_one(self):
        self.assertEqual(rewrite_units.parse_unit_id("we@ird.bin@0100"), ("we@ird.bin", 0x100))

    def test_a_bad_unit_id_is_refused(self):
        with self.assertRaises(rewrite_units.RewriteError):
            rewrite_units.parse_unit_id("no-offset-here")


class RewriteBytesTest(unittest.TestCase):
    def setUp(self):
        self.original = build(TEXTS)

    def test_an_equal_length_translation_is_written_and_the_file_size_never_moves(self):
        rows = rows_for("a.bin", TEXTS, ["FIRST LINE OF TEXT", None, None])
        out, stats = rewrite_units.rewrite_bytes(self.original, rows)
        self.assertEqual(stats["rewritten"], 1)
        self.assertEqual(len(out), len(self.original))
        self.assertIn(b"FIRST LINE OF TEXT", out)
        # every other unit is untouched, byte for byte
        self.assertIn(TEXTS[1] + b"\x00\x00", out)
        self.assertIn(TEXTS[2] + b"\x00\x00", out)

    def test_a_shorter_translation_is_padded_to_the_exact_slot(self):
        rows = rows_for("a.bin", TEXTS, ["short", None, None])
        out, stats = rewrite_units.rewrite_bytes(self.original, rows)
        self.assertEqual(stats["padded"], 1)
        self.assertEqual(len(out), len(self.original))
        self.assertEqual(out.count(b"short"), 1)
        # the padding is spaces, so no new 00 00 stop can appear
        self.assertEqual(out.count(b"\x00\x00"), self.original.count(b"\x00\x00"))

    def test_the_unit_count_survives_the_rewrite(self):
        rows = rows_for("a.bin", TEXTS, ["FIRST LINE OF TEXT", "second line", "third line here"])
        out, _stats = rewrite_units.rewrite_bytes(self.original, rows)
        before = extract_event_text.select_envelopes(self.original)[0]
        after = extract_event_text.select_envelopes(out)[0]
        self.assertEqual(len(before), len(after))
        self.assertEqual(
            [(e.marker_offset, e.start_offset, e.pair_offset) for e in before],
            [(e.marker_offset, e.start_offset, e.pair_offset) for e in after],
        )

    def test_an_over_budget_translation_is_refused_and_the_bytes_untouched(self):
        rows = rows_for("a.bin", TEXTS, ["second line", None, None])
        rows[0]["target_text"] = "this is far too long for the slot"
        out, stats = rewrite_units.rewrite_bytes(self.original, rows)
        self.assertEqual(stats["rewritten"], 0)
        self.assertEqual(len(stats["refused"]), 1)
        self.assertEqual(out, self.original)

    def test_a_stale_source_view_is_refused_rather_than_written_blind(self):
        rows = rows_for("a.bin", TEXTS, ["FIRST LINE OF TEXT", None, None])
        rows[0]["source_text"] = "not what is in the file"
        out, stats = rewrite_units.rewrite_bytes(self.original, rows)
        self.assertEqual(out, self.original)
        self.assertIn("stale", stats["refused"][0][1][0])

    def test_a_dropped_control_token_is_refused(self):
        original = build([b"A\x01B", b"other"])
        rows = rows_for("a.bin", [b"A\x01B", b"other"], ["AB", None])
        out, stats = rewrite_units.rewrite_bytes(original, rows)
        self.assertEqual(out, original)
        self.assertEqual(len(stats["refused"]), 1)

    def test_blank_and_unchanged_rows_are_skipped(self):
        rows = rows_for("a.bin", TEXTS, ["", None, "THIRD LINE HERE"])
        out, stats = rewrite_units.rewrite_bytes(self.original, rows)
        self.assertEqual(stats["skipped_empty"], 1)
        self.assertEqual(stats["skipped_same"], 1)  # the row left as its own source
        self.assertEqual(stats["rewritten"], 1)
        self.assertEqual(len(out), len(self.original))
        self.assertIn(TEXTS[0], out, "the blank row must not touch its unit")
        self.assertIn(b"THIRD LINE HERE", out)

    def test_a_zero_pad_byte_is_refused_because_it_would_end_the_string(self):
        with self.assertRaises(rewrite_units.RewriteError):
            rewrite_units.rewrite_bytes(self.original, rows_for("a.bin", TEXTS, ["short", None, None]), 0)


class ResolveFileTest(unittest.TestCase):
    def test_an_ambiguous_name_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "one").mkdir()
            (root / "two").mkdir()
            (root / "one" / "a.bin").write_bytes(b"x")
            (root / "two" / "a.bin").write_bytes(b"y")
            with self.assertRaises(rewrite_units.RewriteError):
                rewrite_units.resolve_file(root, "a.bin")

    def test_a_unique_basename_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pkg").mkdir()
            path = root / "pkg" / "a.bin"
            path.write_bytes(b"x")
            self.assertEqual(rewrite_units.resolve_file(root, "a.bin"), path)


class RewriteTreeTest(unittest.TestCase):
    def test_the_extracted_file_is_never_modified_and_the_copy_goes_to_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            extracted = root / "extracted"
            (extracted / "pkg").mkdir(parents=True)
            source = extracted / "pkg" / "a.bin"
            original = build(TEXTS)
            source.write_bytes(original)

            csv_path = root / "units.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows_for("a.bin", TEXTS, [None])[0]))
                writer.writeheader()
                writer.writerows(rows_for("a.bin", TEXTS, ["FIRST LINE OF TEXT", None, None]))

            out_root = root / "out"
            result = rewrite_units.rewrite_tree(csv_path, extracted, out_root)
            self.assertEqual(result["totals"]["rewritten"], 1)
            self.assertEqual(source.read_bytes(), original, "the extracted original was modified")
            written = (out_root / "pkg" / "a.bin").read_bytes()
            self.assertEqual(len(written), len(original))
            self.assertIn(b"FIRST LINE OF TEXT", written)

    def test_the_report_says_how_much_was_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            extracted = root / "extracted"
            extracted.mkdir()
            (extracted / "a.bin").write_bytes(build(TEXTS))
            csv_path = root / "units.csv"
            rows = rows_for("a.bin", TEXTS, ["way too long for this slot at all", None, None])
            with csv_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            result = rewrite_units.rewrite_tree(csv_path, extracted, root / "out")
            text = "\n".join(rewrite_units.report_lines(result))
            self.assertIn("1 refused", text)
            self.assertIn("left in Japanese", text)

    def test_a_missing_input_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = rewrite_units.main(
                ["--csv", str(Path(tmp) / "nope.csv"), "--extracted", str(Path(tmp)), "--out", str(Path(tmp) / "o")]
            )
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
