"""Selftests of the two analysis tools that found the key: key matrix, IL2CPP modules."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import il2cpp_modules as M  # noqa: E402
import key_matrix as K  # noqa: E402


def run_selftest(name):
    return subprocess.run([sys.executable, str(TOOLS / name), "selftest"],
                          capture_output=True, text=True)


class SelftestTests(unittest.TestCase):
    def test_key_matrix_selftest(self):
        result = run_selftest("key_matrix.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selftest: PASS", result.stdout)

    def test_il2cpp_modules_selftest(self):
        result = run_selftest("il2cpp_modules.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selftest: PASS", result.stdout)


class ModuleRecordTests(unittest.TestCase):
    def test_record_layout(self):
        import struct

        blob = (struct.pack("<Q", 0x180001000) + struct.pack("<I", 37353) + b"\x00" * 4
                + struct.pack("<Q", 0x1840A46E0) + struct.pack("<I", 1269) + b"\x00" * 4
                + struct.pack("<Q", 0x180003000) + struct.pack("<Q", 0x180004000)
                + b"\x00" * 16)
        record = M.decode_module(blob)
        self.assertEqual(record["method_pointer_count"], 37353)
        self.assertEqual(record["method_pointers_rva"], 0x40A46E0)

    def test_module_name_pattern(self):
        self.assertTrue(M.MODULE_NAME.match(b"Assembly-CSharp.dll"))
        self.assertFalse(M.MODULE_NAME.match(b"Assembly-CSharp"))


class KeyMatrixTests(unittest.TestCase):
    def test_derivation_names(self):
        import hashlib

        keys = K.keys_from(b"ComBBStudioSRTeam")
        self.assertEqual(keys["md5"], hashlib.md5(b"ComBBStudioSRTeam").digest())
        self.assertEqual(len(keys["sha256-16"]), 16)
        self.assertEqual(K.keys_from(b"abc")["pad16"], b"abc" + b"\x00" * 13)
        self.assertNotIn("pad16", keys)          # 16 bytes already fill a key

    def test_layout_count(self):
        keys = K.keys_from(b"0123456789abcdef")
        self.assertEqual(len(K.layouts(keys["raw16"])), 6)

    def test_leading_zero_counters_cannot_be_told_apart(self):
        """LE32 and LE64 of the same counter agree until the counter needs 33 bits."""
        keys = K.keys_from(b"0123456789abcdef")
        layouts = K.layouts(keys["raw16"])
        self.assertEqual(layouts["le32@1"], layouts["le64@1"])
        self.assertNotEqual(layouts["le32@1"], layouts["le32@0"])


if __name__ == "__main__":
    unittest.main()
