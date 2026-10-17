"""Synthetic tests for the read-only resource search used during screenshot QA."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from text_resource_probe import encodings, find_all, leaves, probe


class TextResourceProbeTests(unittest.TestCase):
    def test_reports_every_overlapping_match(self):
        self.assertEqual(find_all(b"aaaa", b"aa"), [0, 1, 2])

    def test_empty_needle_refused(self):
        with self.assertRaises(ValueError):
            find_all(b"x", b"")

    def test_encoded_character_values(self):
        values = encodings("宇")
        raw = "宇".encode("cp932")
        self.assertEqual(values["cp932-u16le"], raw[::-1])
        self.assertEqual(values["utf-16le"], "宇".encode("utf-16le"))

    def test_non_pac_leaf_is_not_interpreted(self):
        self.assertEqual(list(leaves("test.bin", b"fixture")), [("test.bin", b"fixture")])

    def test_plain_file_is_read_only_and_reports_offsets(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.bin"
            data = b"HEAD" + "宇宙".encode("cp932") + b"\0TAIL"
            path.write_bytes(data)
            result = probe(path, ["宇宙"])
            self.assertEqual(path.read_bytes(), data)
            hit = next(m for m in result["matches"] if m["encoding"] == "cp932")
            self.assertEqual(hit["offsets"], [4])
            self.assertEqual(result["leaves_scanned"], 1)


if __name__ == "__main__":
    unittest.main()
