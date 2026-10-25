"""Locating the bundle behind a line of text in a running game's memory.

Everything here runs without Windows and without the game: the memory reader is
replaced by a buffer, and the tests use bundles carved from the owner's memory.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import srw_y_find_text as M  # noqa: E402

TEXT = "Sixty years ago, interstellar war ravaged our planet"
CARVED = sorted((ROOT / "local" / "owner_carve4").rglob("*.bundle")) \
    if (ROOT / "local" / "owner_carve4").exists() else []


class HoleySource(M.BufferSource):
    """Separate chunks, like a process: reads outside a chunk return nothing."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.regions = [(base, len(data)) for base, data in chunks]

    def read(self, address, size):
        for base, data in self.chunks:
            if base <= address < base + len(data):
                start = address - base
                return data[start:start + size]
        return b""


def memory_with(bundle, before=50_000, after=20_000):
    """One chunk of noise, then the bundle, then more noise."""
    base = 0x10000000
    noise = bytes((i * 31) & 0xFF for i in range(before))
    tail = bytes((i * 17) & 0xFF for i in range(after))
    return HoleySource([(base, noise), (base + len(noise), bundle),
                        (base + len(noise) + len(bundle), tail)])


class VersionTests(unittest.TestCase):
    def test_version_is_pinned(self):
        self.assertEqual(M.SCRIPT_VERSION, "2026-10-26.12")


class NeedleTests(unittest.TestCase):
    def test_variants_cover_both_encodings(self):
        variants = M.needle_variants(TEXT)
        self.assertIn(b"Sixty years ago", variants["utf-8"])
        self.assertEqual(variants["utf-16-le"][:2], b"S\x00")

    def test_fragments_start_with_the_whole_text(self):
        parts = M.candidate_needles(TEXT + ". " + TEXT.replace("Sixty", "Fifty"))
        self.assertEqual(parts[0], TEXT + ". " + TEXT.replace("Sixty", "Fifty"))
        self.assertTrue(all(len(p) >= 24 for p in parts))

    def test_short_text_yields_nothing(self):
        self.assertEqual(M.candidate_needles("short"), [])

    def test_fragments_are_unique(self):
        parts = M.candidate_needles(TEXT + ". " + TEXT)
        self.assertEqual(len(parts), len(set(parts)))


class HeaderTests(unittest.TestCase):
    def test_accepts_a_self_consistent_header(self):
        blob = M._fake_bundle(b"x" * 100)
        header = M.parse_header(blob)
        self.assertEqual(header["revision"], "2022.3.44f1")
        self.assertEqual(header["declared_size"], len(blob))

    def test_rejects_other_data(self):
        self.assertIsNone(M.parse_header(b"not a bundle, just text" * 4))
        self.assertIsNone(M.parse_header(b"UnityFS\x00" + b"\xff" * 60))


class SegmentTests(unittest.TestCase):
    def test_holes_are_skipped_and_addresses_kept(self):
        source = HoleySource([(0x1000, b"aaaa"), (0x2000, b"bbbb")])
        segments = M.read_segments(source, 0xF00, 0x2100)
        self.assertEqual([(addr, data) for addr, data in segments],
                         [(0x1000, b"aaaa"), (0x2000, b"bbbb")])
        self.assertEqual(M.read_span(source, 0xF00, 0x2100), b"aaaabbbb")


class LocateTests(unittest.TestCase):
    def test_finds_the_bundle_in_front_of_the_hit(self):
        bundle = M._fake_bundle(TEXT.encode("utf-8"))
        source = memory_with(bundle)
        hit = source.chunks[1][0] + 40
        found = M.locate_bundle(source, hit, len(TEXT), lookback=1 << 20)
        self.assertIsNotNone(found)
        self.assertEqual(found["blob"], bundle)

    def test_a_decoy_signature_is_skipped(self):
        payload = b"UnityFS\x00" + b"\xff" * 8 + TEXT.encode("utf-8")
        bundle = M._fake_bundle(payload)
        source = memory_with(bundle)
        hit = source.chunks[1][0] + bundle.find(TEXT.encode("utf-8"))
        found = M.locate_bundle(source, hit, len(TEXT), lookback=1 << 20)
        self.assertIsNotNone(found)
        self.assertEqual(found["blob"], bundle)

    def test_no_header_nearby(self):
        source = memory_with(TEXT.encode("utf-8"))
        self.assertIsNone(M.locate_bundle(source, source.chunks[1][0] + 3,
                                          len(TEXT), lookback=1 << 20))

    @unittest.skipUnless(CARVED, "no carved bundles in local/")
    def test_a_real_carved_bundle_is_recognised(self):
        for path in CARVED[-3:]:
            blob = path.read_bytes()
            header = M.parse_header(blob)
            self.assertIsNotNone(header, path)
            self.assertEqual(header["declared_size"], len(blob), path)


class ScanTests(unittest.TestCase):
    def test_writes_the_bundle_and_a_report(self):
        bundle = M._fake_bundle(TEXT.encode("utf-8"))
        source = memory_with(bundle)
        with tempfile.TemporaryDirectory() as raw:
            report = M.scan(source, TEXT.encode("utf-8"), Path(raw), lookback=1 << 20)
            self.assertEqual(len(report["bundles"]), 1)
            row = report["bundles"][0]
            self.assertEqual((Path(raw) / row["file"]).read_bytes(), bundle)
            saved = json.loads((Path(raw) / "find_report.json").read_text())
            self.assertEqual(saved["hits_found"], 1)
            self.assertEqual(saved["script_version"], M.SCRIPT_VERSION)

    def test_a_context_window_is_saved_when_no_bundle_exists(self):
        source = memory_with(TEXT.encode("utf-8"))
        with tempfile.TemporaryDirectory() as raw:
            report = M.scan(source, TEXT.encode("utf-8"), Path(raw), lookback=1 << 20)
            self.assertEqual(report["bundles"], [])
            self.assertEqual(len(report["contexts"]), 1)
            self.assertTrue((Path(raw) / report["contexts"][0]["file"]).exists())

    def test_the_same_bundle_is_carved_once(self):
        # one bundle whose payload holds the text twice: two hits, one carve
        payload = TEXT.encode("utf-8") + b" and later " + TEXT.encode("utf-8")
        bundle = M._fake_bundle(payload)
        with tempfile.TemporaryDirectory() as raw:
            report = M.scan(HoleySource([(0x1000, bundle)]), TEXT.encode("utf-8"),
                            Path(raw), lookback=1 << 20)
            self.assertEqual(report["hits_found"], 2)
            self.assertEqual(len(report["bundles"]), 1)


def fake_sized(total: int, payload: bytes) -> bytes:
    """A bundle whose declared size is exactly `total` (to match a known size)."""
    head = (M.UNITYFS + (8).to_bytes(4, "big") + b"5.x.x\x00"
            + b"2022.3.44f1\x00" + total.to_bytes(8, "big")
            + (65).to_bytes(4, "big") + (91).to_bytes(4, "big")
            + (0x243).to_bytes(4, "big"))
    return head + payload + b"\x00" * (total - len(head) - len(payload))


class KnownSizeTests(unittest.TestCase):
    def test_only_known_sizes_are_taken_and_named(self):
        known = fake_sized(2273, b"ja table")
        stranger = fake_sized(9999, b"not wanted")
        source = HoleySource([(0x1000, known + stranger)])
        with tempfile.TemporaryDirectory() as raw:
            carved = M.carve_sizes(source, Path(raw))
            self.assertEqual(len(carved), 1)
            row = carved[0]
            self.assertEqual(row["size"], 2273)
            self.assertEqual(row["file"],
                             "known_f1ba80f5694d96485b7f8c5402dd18c9.bundle")
            self.assertEqual((Path(raw) / row["file"]).read_bytes(), known)

    def test_the_same_bundle_twice_is_carved_once(self):
        known = fake_sized(2273, b"ja table")
        source = HoleySource([(0x1000, known), (0x8000, known)])
        with tempfile.TemporaryDirectory() as raw:
            self.assertEqual(len(M.carve_sizes(source, Path(raw))), 1)

    def test_the_byte_limit_is_respected(self):
        source = HoleySource([(0x1000, fake_sized(2273, b"a")),
                              (0x8000, fake_sized(58520, b"b"))])
        with tempfile.TemporaryDirectory() as raw:
            carved = M.carve_sizes(source, Path(raw), byte_limit=3000)
            self.assertEqual([row["size"] for row in carved], [2273])

    def test_the_default_table_covers_the_text_files(self):
        self.assertIn(948652, M.KNOWN_BUNDLES)   # en-US large table
        self.assertIn(940012, M.KNOWN_BUNDLES)   # ja-JP large table
        self.assertIn(5591151, M.KNOWN_BUNDLES)  # scenario scripts


class CappedSource(M.BufferSource):
    """Pretends to be ReadProcessMemory: never returns more than 1 MB per call."""

    def read(self, address, size):
        return super().read(address, min(size, 1 << 20))


class LargeRegionTests(unittest.TestCase):
    def test_a_region_larger_than_one_read_is_fully_scanned(self):
        """ProcessSource.read caps at 1 MB, so the scan has to chunk by itself."""
        filler = bytes((i * 7) & 0xFF for i in range(3 << 20))
        bundle = M._fake_bundle(TEXT.encode("utf-8"))
        source = CappedSource(filler + bundle)
        source.regions = [(source.base, len(filler) + len(bundle))]
        with tempfile.TemporaryDirectory() as raw:
            report = M.scan(source, TEXT.encode("utf-8"), Path(raw),
                            lookback=1 << 20)
            self.assertEqual(len(report["bundles"]), 1)
            self.assertEqual(report["bytes_scanned"], len(filler) + len(bundle))


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "tools" / "srw_y_find_text.py"),
                               *args], capture_output=True, text=True, cwd=ROOT)

    def test_selftest_passes(self):
        result = self.run_cli("selftest")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selftest: PASS", result.stdout)

    def test_from_file_carves_the_bundle(self):
        bundle = M._fake_bundle(TEXT.encode("utf-8"))
        with tempfile.TemporaryDirectory() as raw:
            dump = Path(raw) / "dump.bin"
            dump.write_bytes(b"\x00" * 4096 + bundle + b"\x00" * 4096)
            out = Path(raw) / "opening"
            result = self.run_cli("scan", "--from-file", str(dump),
                                  "--needle", TEXT, "--out", str(out),
                                  "--lookback", "0x100000")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            carved = [p for p in out.glob("*.bundle") if not p.name.startswith("known_")]
            self.assertEqual(len(carved), 1)
            self.assertEqual(carved[0].read_bytes(), bundle)

    def test_a_short_needle_is_refused(self):
        result = self.run_cli("scan", "--needle", "short", "--out", "/tmp/x")
        self.assertEqual(result.returncode, 2)

    def test_absent_text_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as raw:
            dump = Path(raw) / "dump.bin"
            dump.write_bytes(b"\x00" * 8192)
            result = self.run_cli("scan", "--from-file", str(dump),
                                  "--needle", TEXT, "--out", str(Path(raw) / "o"))
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
