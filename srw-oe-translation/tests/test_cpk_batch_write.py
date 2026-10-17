"""Multiple CPK replacements without repeated archive rebuilds; synthetic only."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpk_write as cw
import cpk_table as ct
from test_cpk_table import build_synthetic_cpk


class BatchCpkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.original = self.root / "input.cpk"
        self.entries = [{"dir": "", "name": f"m{i}.bin", "data": bytes([65+i])*n, "id": i}
                        for i, n in enumerate((100, 5000, 96, 64))]
        self.original.write_bytes(build_synthetic_cpk(self.entries))

    def readback(self, blob, changes):
        path = self.root / "output.cpk"
        path.write_bytes(blob)
        parsed = cw.load(path)
        reference = ct.read_cpk_table(path)["entries"]
        self.assertEqual([m.name for m in parsed.members], [e["name"] for e in self.entries])
        for m, e, original in zip(parsed.members, reference, self.entries):
            want = changes.get(m.name, (original["data"], len(original["data"])))
            self.assertEqual(m.blob, want[0])
            self.assertEqual((m.file_size, m.extract_size), (len(want[0]), want[1]))
            self.assertEqual(e["file_size"], len(want[0]))
        physical = sorted(reference, key=lambda e: e["absolute_offset"])
        for a,b in zip(physical, physical[1:]):
            self.assertLessEqual(a["absolute_offset"] + a["file_size"], b["absolute_offset"])

    def test_empty_batch_exact_identity(self):
        self.assertEqual(cw.rebuild_many(cw.load(self.original), {}), self.original.read_bytes())

    def test_mixed_growth_shrink_and_same_size(self):
        changes = {"m0.bin": (b"X"*4500, 4500), "m1.bin": (b"Y"*13, 13), "m2.bin": (b"Z"*96, 96)}
        self.readback(cw.rebuild_many(cw.load(self.original), changes), changes)

    def test_order_of_change_dictionary_does_not_change_layout(self):
        changes = {"m0.bin": (b"X"*3000, 3000), "m3.bin": (b"Y"*4000, 4000)}
        original = cw.load(self.original)
        self.assertEqual(cw.rebuild_many(original, changes), cw.rebuild_many(original, dict(reversed(list(changes.items())))))

    def test_same_size_changes_preserve_all_other_bytes(self):
        c = cw.load(self.original)
        changes = {"m0.bin": (b"X"*100, 100), "m2.bin": (b"Z"*96, 96)}
        out = cw.rebuild_many(c, changes)
        restored = bytearray(out)
        for m in c.members:
            if m.name in changes:
                at = c.data_base + m.relative_offset
                restored[at:at+m.file_size] = m.blob
        self.assertEqual(bytes(restored), self.original.read_bytes())

    def test_batch_matches_sequential_physical_order_for_growth(self):
        changes = {"m0.bin": (b"X"*3000, 3000), "m2.bin": (b"Z"*4000, 4000)}
        sequential = self.original.read_bytes()
        path = self.root / "step.cpk"
        for name, (data, size) in changes.items():
            path.write_bytes(sequential)
            sequential = cw.rebuild(cw.load(path), (name, data, size))
        self.assertEqual(cw.rebuild_many(cw.load(self.original), changes), sequential)

    def test_unknown_member_refused(self):
        with self.assertRaisesRegex(ValueError, "not a member"):
            cw.rebuild_many(cw.load(self.original), {"missing": (b"X", 1)})

    def test_original_is_not_written(self):
        before = self.original.read_bytes()
        cw.rebuild_many(cw.load(self.original), {"m0.bin": (b"X", 1)})
        self.assertEqual(self.original.read_bytes(), before)

    def test_legacy_optional_extract_size(self):
        c = cw.load(self.original)
        self.assertEqual(cw.rebuild(c, ("m0.bin", b"X", None)), cw.rebuild(c, ("m0.bin", b"X")))


if __name__ == "__main__":
    unittest.main()
