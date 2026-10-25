"""Memory carver tests — synthetic images only, no game and no Windows needed."""
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mem_carve as M  # noqa: E402


def unityfs(size: int = 4096, unity_version: bytes = b"5.x.x") -> bytes:
    header = (M.SIGNATURE + struct.pack(">I", 7) + unity_version + b"\x00"
              + b"2021.3.0f1\x00" + struct.pack(">q", size)
              + struct.pack(">I", 128) + struct.pack(">I", 256)
              + struct.pack(">I", 0x43))
    return header + b"\x00" * (size - len(header))


class HeaderTests(unittest.TestCase):
    def test_parses_a_bundle_header(self):
        parsed = M.parse_unityfs(unityfs(4096))
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["version"], 7)
        self.assertEqual(parsed["size"], 4096)
        self.assertEqual(parsed["unity_revision"], "2021.3.0f1")
        self.assertEqual(parsed["uncompressed_blocks_info_size"], 256)

    def test_rejects_rubbish(self):
        self.assertIsNone(M.parse_unityfs(b"not a bundle at all, really"))
        self.assertIsNone(M.parse_unityfs(M.SIGNATURE + b"\x00" * 4))
        bad_size = (M.SIGNATURE + struct.pack(">I", 7) + b"a\x00" + b"b\x00"
                    + struct.pack(">q", -5) + b"\x00" * 12)
        self.assertIsNone(M.parse_unityfs(bad_size))

    def test_rejects_absurd_size(self):
        absurd = (M.SIGNATURE + struct.pack(">I", 7) + b"a\x00" + b"b\x00"
                  + struct.pack(">q", 1 << 40) + b"\x00" * 12)
        self.assertIsNone(M.parse_unityfs(absurd))


class ScanTests(unittest.TestCase):
    def test_finds_markers_and_bundles(self):
        image = (b"\x00" * 100 + unityfs(2048) + b"\x00" * 50 + M.CAB
                 + b"deadbeef" + b"cse20_0001_0000310a" + b"dialog_text_ja-JP")
        scan = M.scan_buffer(image)
        self.assertEqual(len(scan["bundles"]), 1)
        self.assertEqual(scan["bundles"][0][1], 2048)
        self.assertEqual(len(scan["markers"]["cab"]), 1)
        self.assertEqual(len(scan["markers"]["scenario_name"]), 1)
        self.assertEqual(len(scan["markers"]["localization"]), 1)

    def test_marker_limit_is_honoured(self):
        image = M.CAB * 500
        scan = M.scan_buffer(image, marker_limit=10)
        self.assertEqual(len(scan["markers"]["cab"]), 10)

    def test_japanese_ratio(self):
        japanese = "これはテストです".encode("utf-16-le") * 200
        self.assertGreater(M.utf16_japanese_ratio(japanese), 0.8)
        self.assertEqual(M.utf16_japanese_ratio(b"\x00" * 1000), 0.0)
        self.assertLess(M.utf16_japanese_ratio(bytes(range(256)) * 8), 0.2)


def serialized(size: int = 1024, name: bytes = b"0123456789abcdef") -> bytes:
    body = (M.CAB + name + struct.pack(">IIII", 128, size, 22, 512)
            + b"\x00" * (size - 24))
    return body


class SerializedTests(unittest.TestCase):
    def test_parses_a_serialized_file_header(self):
        parsed = M.parse_serialized_header(serialized(2048))
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["file_size"], 2048)
        self.assertEqual(parsed["data_offset"], 512)
        self.assertEqual(parsed["name"], "0123456789abcdef")

    def test_rejects_bad_sizes(self):
        bad = M.CAB + b"0123456789abcdef" + struct.pack(">IIII", 4096, 1024, 22, 0)
        self.assertIsNone(M.parse_serialized_header(bad))       # metadata > file
        huge = M.CAB + b"0123456789abcdef" + struct.pack(">IIII", 0, 1 << 31, 22, 0)
        self.assertIsNone(M.parse_serialized_header(huge))
        self.assertIsNone(M.parse_serialized_header(b"CAB-"))

    def test_carving_writes_serialized_files_too(self):
        image = b"\x00" * 64 + serialized(1024) + b"\x00" * 32 + unityfs(512)
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw)
            result = M.carve_from_buffer(image, out)
            kinds = sorted(item["kind"] for item in result["written"])
            self.assertEqual(kinds, ["assets", "bundle"])
            assets = next(item for item in result["written"] if item["kind"] == "assets")
            self.assertEqual(assets["size"], 1024)
            self.assertIsNotNone(M.parse_serialized_header(
                (out / assets["name"]).read_bytes()))


class KanaTests(unittest.TestCase):
    def test_counts_runs_without_keeping_text(self):
        text = "これはテストです。".encode("utf-16-le") * 5
        stats = M.kana_stats(text)
        self.assertGreaterEqual(stats["runs"], 5)
        self.assertGreater(stats["chars"], 20)
        self.assertGreater(stats["longest"], 5)

    def test_random_bytes_do_not_look_like_kana(self):
        stats = M.kana_stats(bytes(range(256)) * 64)
        self.assertLess(stats["runs"], 5)


class CarveTests(unittest.TestCase):
    def test_carve_plan_skips_overlaps_and_respects_budget(self):
        plan = M.carve_plan([(0, 100), (50, 100), (400, 100)], 1000, 0x1000, 250)
        self.assertEqual([task["offset"] for task in plan], [0, 400])
        self.assertEqual(plan[0]["address"], 0x1000)
        plan = M.carve_plan([(0, 400)], 1000, 0, 100)
        self.assertEqual(plan, [])

    def test_carve_writes_valid_bundles_only(self):
        image = unityfs(1024) + b"\x00" * 64 + unityfs(2048)
        with tempfile.TemporaryDirectory() as raw:
            out = Path(raw)
            result = M.carve_from_buffer(image, out)
            self.assertEqual(len(result["written"]), 2)
            sizes = sorted(item["size"] for item in result["written"])
            self.assertEqual(sizes, [1024, 2048])
            for item in result["written"]:
                data = (out / item["name"]).read_bytes()
                self.assertIsNotNone(M.parse_unityfs(data))
                self.assertEqual(len(data), item["size"])

    def test_truncated_bundle_is_flagged_incomplete(self):
        """A partial carve is kept (it may still hold text) but never claimed whole."""
        bundle = unityfs(4096)
        image = bundle[:1000]            # header promises 4096, only 1000 present
        with tempfile.TemporaryDirectory() as raw:
            result = M.carve_from_buffer(image, Path(raw))
            self.assertEqual(len(result["written"]), 1)
            item = result["written"][0]
            self.assertFalse(item["complete"])
            self.assertEqual(item["size"], 1000)
            self.assertEqual(item["declared_size"], 4096)


class CliTests(unittest.TestCase):
    def test_selftest_passes(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools/mem_carve.py"),
                                 "--selftest"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_from_file_end_to_end(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            dump = tmp / "dump.bin"
            dump.write_bytes(b"\x11" * 512 + unityfs(1024) + M.CAB + b"x" * 64)
            out = tmp / "carved"
            report = tmp / "report.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/mem_carve.py"),
                 "--from-file", str(dump), "--out", str(out),
                 "--report", str(report)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(report.is_file())
            self.assertEqual(len(list(out.glob("*.bundle"))), 1)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["counts"]["cab"], 1)
            self.assertEqual(len(payload["carved"]["written"]), 1)

    def test_live_scan_refuses_outside_windows(self):
        if sys.platform == "win32":
            self.skipTest("this test targets non-Windows hosts")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/mem_carve.py"),
             "--process", "nothing.exe", "--out", "/tmp/x"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("needs Windows", result.stderr)


if __name__ == "__main__":
    unittest.main()


class HarvestTests(unittest.TestCase):
    """String harvesting: the volume measurement that does not need a bundle."""

    SENTENCE = "\u3053\u3093\u306b\u3061\u306f\u3001\u30d1\u30a4\u30ed\u30c3\u30c8\u3002"

    def test_utf16_and_utf8_both_harvested(self):
        utf16, utf8 = set(), set()
        M.harvest_buffer(self.SENTENCE.encode("utf-16-le") + b"\x00" * 8, utf16, utf8)
        M.harvest_buffer(self.SENTENCE.encode("utf-8") + b"\x7f" * 8, utf8, utf8)
        self.assertEqual(len(utf16), 1)
        self.assertIn(self.SENTENCE, "".join(utf16))

    def test_ascii_is_not_harvested(self):
        utf16, utf8 = set(), set()
        M.harvest_buffer(b"ordinary english text, no japanese" * 10, utf16, utf8)
        self.assertEqual(utf16, set())
        self.assertEqual(utf8, set())

    def test_deduplicates(self):
        utf16, utf8 = set(), set()
        block = self.SENTENCE.encode("utf-16-le")
        M.harvest_buffer(block * 3, utf16, utf8)
        self.assertEqual(len(utf16), 1)

    def test_write_strings_caps_and_reports(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "strings.txt"
            stats = M.write_strings(path, {"\u3042" * 10, "\u3044" * 10}, cap=15)
            self.assertTrue(path.is_file())
            self.assertEqual(stats["unique"], 2)
            self.assertEqual(stats["written"], 1)
            self.assertTrue(stats["truncated"])


class StrictHeaderTests(unittest.TestCase):
    """False headers in random bytes must not swallow the rest of a chunk."""

    def test_absurd_size_rejected(self):
        # the owner's reports contained sizes of 4,294,967,141 B: false headers
        # that used to swallow every following hit in the same chunk
        self.assertIsNone(M.parse_unityfs(self._with_size(4294967141)))

    @staticmethod
    def _with_size(size: int) -> bytes:
        header = (M.SIGNATURE + struct.pack(">I", 7) + b"5.x.x\x00"
                  + b"2021.3.0f1\x00" + struct.pack(">q", size)
                  + struct.pack(">I", 128) + struct.pack(">I", 256)
                  + struct.pack(">I", 0x43))
        return header + b"\x00" * 64

    def test_bad_revision_rejected(self):
        header = (M.SIGNATURE + struct.pack(">I", 7) + b"5.x.x\x00"
                  + b"not-a-version\x00" + struct.pack(">q", 4096)
                  + struct.pack(">I", 128) + struct.pack(">I", 256)
                  + struct.pack(">I", 0x43))
        self.assertIsNone(M.parse_unityfs(header + b"\x00" * 64))


class ReadPiecesTests(unittest.TestCase):
    """Assembling a file that does not fit in one chunk."""

    def test_assembles_across_pieces(self):
        source = bytes(range(256)) * 40          # 10,240 B
        def read_fn(address, size):
            return source[address:address + size]
        data = M.read_pieces(0, len(source), read_fn, piece=1024)
        self.assertEqual(data, source)

    def test_short_read_stops_and_reports(self):
        source = b"x" * 500
        def read_fn(address, size):
            return source[address:address + size]
        data = M.read_pieces(0, 1000, read_fn, piece=256)
        self.assertEqual(len(data), 500)          # 256 + 244, then nothing left
        self.assertNotEqual(len(data), 1000)      # caller marks complete: false


class FalseSerializedHeaderTests(unittest.TestCase):
    def test_non_hex_name_rejected(self):
        # the owner's run carved four 8 MB blobs whose "CAB-" name was garbage
        header = (b"CAB-" + b"\x00\x90\x99\x04\xb1y\x02\x00\x000\x00\x00\x00\x00"
                  + struct.pack(">IIII", 240, 33554496, 0, 0))
        self.assertIsNone(M.parse_serialized_header(header + b"\x00" * 64))

    def test_hex_name_accepted(self):
        header = (b"CAB-" + b"0123456789abcdef"
                  + struct.pack(">IIII", 240, 33554496, 6, 4096))
        parsed = M.parse_serialized_header(header + b"\x00" * 64)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["file_size"], 33554496)


class StringObjectTests(unittest.TestCase):
    """IL2CPP strings: `[klass 8][monitor 8][length 4][utf-16 chars]`."""

    KLASS = bytes.fromhex("d0853280f1010000")     # ends in zeros, like real ones

    @classmethod
    def heap(cls, *texts: str) -> bytes:
        blob = b""
        for text in texts:
            raw = text.encode("utf-16-le")
            blob += cls.KLASS + b"\x00" * 8 + struct.pack("<i", len(text)) + raw
            blob += b"\x00" * ((8 - len(blob) % 8) % 8)
        return blob

    def test_finds_strings_and_their_addresses(self):
        blob = self.heap("\u30d1\u30a4\u30ed\u30c3\u30c8", "ja-JP")
        hits = M.scan_string_objects(blob)
        self.assertEqual([text for _, _, text in hits],
                         ["\u30d1\u30a4\u30ed\u30c3\u30c8", "ja-JP"])
        self.assertEqual(hits[0][1], 0)
        self.assertEqual(hits[0][0], self.KLASS)

    def test_class_pointer_ending_in_zeros_is_handled(self):
        # the klass pointer itself ends in 00 00, so the zero run starts inside
        # it; anchoring on the run start (the first attempt) found nothing
        blob = self.heap("abc")
        self.assertTrue(M.scan_string_objects(blob))

    def test_empty_and_absurd_lengths_ignored(self):
        blob = self.KLASS + b"\x00" * 8 + struct.pack("<i", 0) + b"x" * 32
        blob += self.KLASS + b"\x00" * 8 + struct.pack("<i", 99999) + b"y" * 32
        self.assertEqual(M.scan_string_objects(blob), [])


class HarvestObjectTests(unittest.TestCase):
    def test_dominant_class_kept_and_text_deduplicated(self):
        other = bytes.fromhex("1122334455667788")
        hits = [(M.KLASS if hasattr(M, "KLASS") else bytes.fromhex("d0853280f1010000"), 0, "a"),
                (bytes.fromhex("d0853280f1010000"), 32, "a"),
                (bytes.fromhex("d0853280f1010000"), 64, "b"),
                (other, 96, "c")]
        counts = {bytes.fromhex("d0853280f1010000"): 60, other: 1}
        kept = M.harvest_objects(hits, counts)
        self.assertEqual([text for _, text in kept], ["a", "b"])

    def test_no_dominant_class_means_nothing(self):
        self.assertEqual(M.harvest_objects([(b"1" * 8, 0, "a")], {b"1" * 8: 3}), [])
