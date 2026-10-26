"""Keystream patching: same-length text edits inside an encrypted bundle."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import keystream_patch as K  # noqa: E402


def fake_bundle(payload: bytes, size: int | None = None) -> bytes:
    """A blob that starts like a real UnityFS bundle."""
    size = size if size is not None else 0
    head = (b"UnityFS\x00" + (8).to_bytes(4, "big") + b"5.x.x\x00"
            + b"2022.3.44f1\x00" + size.to_bytes(8, "big")
            + (0x41).to_bytes(4, "big") + (0x5B).to_bytes(4, "big")
            + (0x243).to_bytes(4, "big"))
    return head + payload


class HeaderTests(unittest.TestCase):
    def test_parses_the_header_of_a_real_layout(self):
        blob = fake_bundle(b"x" * 32, 79)
        info = K.header_info(blob)
        self.assertEqual(info["unity_revision"], "2022.3.44f1")
        self.assertEqual(info["declared_size"], 79)
        self.assertEqual(info["compression"], 3)

    def test_rejects_other_files(self):
        with self.assertRaises(ValueError):
            K.header_info(b"not a bundle at all")

    def test_finds_japanese_runs(self):
        blob = fake_bundle("神と悪魔".encode("utf-8") + b"abc")
        runs = K.text_runs(blob, minimum=2)
        self.assertEqual([run for _, run in runs],
                         ["神と悪魔".encode("utf-8")])


class EditTests(unittest.TestCase):
    def test_xor_needs_equal_lengths(self):
        self.assertEqual(K.xor(b"\x00\x01", b"\x01\x01"), b"\x01\x00")
        with self.assertRaises(ValueError):
            K.xor(b"ab", b"a")

    def test_map_rejects_a_length_change(self):
        with self.assertRaises(SystemExit):
            K.parse_map(["神と悪魔=Bog"])

    def test_apply_edits_keeps_the_length_and_counts(self):
        plain = fake_bundle("神と悪魔".encode("utf-8") * 2)
        edits = [("神と悪魔".encode("utf-8"), "Bog i czart!".encode("utf-8"))]
        self.assertEqual(len(edits[0][0]), len(edits[0][1]))
        patched, count = K.apply_edits(plain, edits)
        self.assertEqual(count, 2)
        self.assertEqual(len(patched), len(plain))
        self.assertNotIn("神と悪魔".encode("utf-8"), patched)
        self.assertIn("Bog i czart!".encode("utf-8"), patched)

    def test_verify_reports_when_unitypy_cannot_read_it(self):
        before = fake_bundle(b"abc" + "神と悪魔".encode("utf-8"))
        edits = [("神と悪魔".encode("utf-8"), "Bog i czart!".encode("utf-8"))]
        after, _ = K.apply_edits(before, edits)
        report = K.verify_patch(before, after, edits)
        self.assertTrue(report["length_unchanged"])
        self.assertTrue(report["unitypy"])

    def test_a_length_change_is_refused(self):
        before = fake_bundle(b"abc")
        with self.assertRaises(AssertionError):
            K.verify_patch(before, before + b"x", [])


class StoreTests(unittest.TestCase):
    def test_save_and_load_a_keystream(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "x.ks"
            K.save_stream(path, bytes(range(32)))
            self.assertEqual(K.load_stream(path), bytes(range(32)))

    def test_foreign_file_is_refused(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "x.ks"
            path.write_bytes(b"nope")
            with self.assertRaises(ValueError):
                K.load_stream(path)

    def test_find_plain_needs_a_unique_size(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            plain = fake_bundle(b"x" * 100)
            (root / "a.bundle").write_bytes(plain)
            (root / "b.bundle").write_bytes(fake_bundle(b"y" * 100))
            self.assertIsNone(K.find_plain(root, len(plain)))
            (root / "b.bundle").unlink()
            self.assertEqual(K.find_plain(root, len(plain)), plain)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plain_dir = self.root / "plain"
        self.plain_dir.mkdir()
        text = "神と悪魔".encode("utf-8")
        self.plain = fake_bundle(b"prefix" + text + b"middle" + text + b"suffix")
        (self.plain_dir / "carved.bundle").write_bytes(self.plain)
        stream = bytes((i * 37 + 11) & 0xFF for i in range(len(self.plain)))
        self.stream = stream
        self.cipher = K.xor(self.plain, stream)
        self.bundle = self.root / "abc123.bundle"
        self.bundle.write_bytes(self.cipher)

    def tearDown(self):
        self.tmp.cleanup()

    def test_info_reports_the_pair(self):
        code = K.main(["info", "--bundle", str(self.bundle),
                       "--plain", str(self.plain_dir), "--show", "1"])
        self.assertEqual(code, 0)

    def test_plan_then_apply_round_trips(self):
        plan_path = self.root / "plan.json"
        code = K.main(["plan", "--bundle", str(self.bundle),
                       "--plain", str(self.plain_dir),
                       "--map", "神と悪魔=Bog i czart!", "--out", str(plan_path)])
        self.assertEqual(code, 0)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual(plan["plan"][0]["occurrences"], 2)

        out = self.root / "out.bundle"
        code = K.main(["apply", "--bundle", str(self.bundle),
                       "--plain", str(self.plain_dir),
                       "--plan", str(plan_path), "--out", str(out)])
        self.assertEqual(code, 0)
        patched_cipher = out.read_bytes()
        self.assertEqual(len(patched_cipher), len(self.cipher))
        patched_plain = K.xor(patched_cipher, self.stream)
        self.assertIn("Bog i czart!".encode("utf-8"), patched_plain)
        self.assertNotIn("神と悪魔".encode("utf-8"), patched_plain)

    def test_a_map_that_changes_length_is_refused(self):
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps({"bundle": "abc123.bundle", "plan": [
            {"old": "神と悪魔", "new": "Bog"}]}), encoding="utf-8")
        code = K.main(["apply", "--bundle", str(self.bundle),
                       "--plain", str(self.plain_dir),
                       "--plan", str(plan_path), "--out",
                       str(self.root / "x.bundle")])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
