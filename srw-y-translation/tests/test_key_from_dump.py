"""Offline candidate analysis: finds the key in a dump without the game."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import key_from_dump as K  # noqa: E402
import srw_y_key as S  # noqa: E402

try:
    from Crypto.Cipher import AES  # noqa: F401
    HAVE_CRYPTO = True
except Exception:  # pragma: no cover
    HAVE_CRYPTO = False

KEY = bytes(range(32))
STATE = bytes([0x3B]) + bytes(range(0x41, 0x4F)) + bytes([0x3B])
NAME = "1cc7e02ee5711c6ba87a0e364f62198c"


class VersionTests(unittest.TestCase):
    def test_version_matches_the_tool(self):
        self.assertEqual(K.SCRIPT_VERSION, S.SCRIPT_VERSION)


class StateTests(unittest.TestCase):
    def test_name_variants_are_offered(self):
        states = K.states_from_name(NAME)
        self.assertIn(bytes.fromhex(NAME), states)
        self.assertIn(bytes.fromhex(NAME)[::-1], states)
        self.assertIn("zeros", states.values())

    def test_state_shapes(self):
        self.assertEqual(K.state_shape(b"\x00" * 12 + b"abcd"), "nonce12-zero")
        self.assertEqual(K.state_shape(b"abcdefghijkl" + b"\x00" * 4),
                         "counter32-zero")
        self.assertIsNone(K.state_shape(bytes(range(16))))


class EndToEndTests(unittest.TestCase):
    def test_finds_the_key_and_the_constant_iv(self):
        bundle_name = NAME + ".bundle"
        cipher = S.encrypt(KEY, "ctr-le", STATE, S._synthetic(4096))
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / bundle_name
            bundle.write_bytes(cipher)
            dump = tmp / "candidates.bin"
            S.write_dump(dump, [(32, bytes(32)), (32, KEY)])
            store = tmp / "fake.dll"
            store.write_bytes(b"\x00" * 64 + STATE + b"\x00" * 64)
            out = tmp / "report.json"
            code = K.main([str(dump), str(bundle), "--dll", str(store),
                           "--out", str(out)])
            self.assertEqual(code, 0)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["hits"][0]["key_hex"], KEY.hex())
            self.assertEqual(len(report["constant_hits"]), 1)
            self.assertEqual(report["constant_hits"][0]["offset"], 64)

    def test_no_key_means_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / (NAME + ".bundle")
            bundle.write_bytes(S.encrypt(KEY, "ctr-le", STATE, S._synthetic(4096)))
            dump = tmp / "candidates.bin"
            S.write_dump(dump, [(32, bytes(32))])
            code = K.main([str(dump), str(bundle), "--out", str(tmp / "r.json")])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
