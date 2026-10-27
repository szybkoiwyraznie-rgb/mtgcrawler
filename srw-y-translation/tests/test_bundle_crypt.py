"""File patching: decrypt/identify/re-encrypt must be involution-exact."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import bundle_crypt as B  # noqa: E402

try:
    from Crypto.Cipher import AES  # noqa: F401
    HAVE_CRYPTO = True
except Exception:  # pragma: no cover
    HAVE_CRYPTO = False

CARVES = ROOT / "local" / "owner_carve4"
KEY = bytes(range(32))
IV = bytes(range(0xF0, 0x100))
STREAM_MODES = ("ctr-le", "ctr-be", "cfb128", "ofb")


class SelfCheckTests(unittest.TestCase):
    def test_every_mode_round_trips(self):
        self.assertTrue(all(B.self_check().values()))

    def test_cli_selfcheck(self):
        result = subprocess.run([sys.executable,
                                 str(ROOT / "tools" / "bundle_crypt.py"),
                                 "--selfcheck"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ctr-le", result.stdout)
        self.assertIn(B.SCRIPT_VERSION, result.stdout)


class RoundTripTests(unittest.TestCase):
    def test_stream_modes_preserve_odd_length(self):
        plain = B._synthetic(8203)
        for mode in STREAM_MODES:
            cipher = B.encrypt(KEY, IV, plain, mode)
            self.assertEqual(len(cipher), len(plain), mode)
            self.assertNotEqual(cipher[:16], plain[:16], mode)
            self.assertEqual(B.decrypt(KEY, IV, cipher, mode), plain, mode)

    def test_identify_returns_the_mode_used(self):
        plain = B._synthetic(8203)
        for mode in STREAM_MODES:
            found = B.identify(KEY, IV, B.encrypt(KEY, IV, plain, mode))
            self.assertIsNotNone(found, mode)
            self.assertEqual(found[0], mode)
            self.assertEqual(found[1], plain)

    def test_identify_rejects_wrong_key(self):
        plain = B._synthetic(8203)
        cipher = B.encrypt(KEY, IV, plain, "ctr-le")
        self.assertIsNone(B.identify(bytes(range(32, 64)), IV, cipher))

    def test_cbc_needs_block_alignment(self):
        plain = B._synthetic(8192)
        cipher = B.encrypt(KEY, IV, plain, "cbc")
        self.assertEqual(B.identify(KEY, IV, cipher)[1], plain)
        assert B.identify(KEY, IV, cipher)[0] == "cbc"
        odd = cipher[:-4]
        self.assertIsNone(B.identify(KEY, IV, odd))

    def test_xor_requires_equal_length(self):
        with self.assertRaises(ValueError):
            B.xor(b"abc", b"abcd")


class CliTests(unittest.TestCase):
    def write_report(self, path: Path, mode: str = "stream") -> None:
        path.write_text(json.dumps({"verified": [{"mode": mode,
                                                  "key_hex": KEY.hex(),
                                                  "iv_hex": IV.hex()}]}),
                        encoding="utf-8")

    def test_decrypt_then_encrypt_restores_the_file(self):
        plain = B._synthetic(8203)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            encrypted = tmp / "in.bundle"
            decrypted = tmp / "out.bundle"
            restored = tmp / "back.bundle"
            report = tmp / "key_report.json"
            encrypted.write_bytes(B.encrypt(KEY, IV, plain, "ctr-be"))
            self.write_report(report)

            first = subprocess.run([sys.executable, str(ROOT / "tools" / "bundle_crypt.py"),
                                    "--report", str(report), "--decrypt",
                                    str(encrypted), str(decrypted)],
                                   capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertIn("mode: ctr-be", first.stdout)
            self.assertEqual(decrypted.read_bytes(), plain)

            second = subprocess.run([sys.executable, str(ROOT / "tools" / "bundle_crypt.py"),
                                     "--report", str(report), "--mode", "ctr-be",
                                     "--encrypt", str(decrypted), str(restored)],
                                    capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(restored.read_bytes(), encrypted.read_bytes())

    def test_refuses_a_bad_key(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bad = tmp / "key_report.json"
            bad.write_text(json.dumps({"verified": [{"key_hex": (b"x" * 32).hex(),
                                                      "iv_hex": IV.hex()}]}),
                           encoding="utf-8")
            encrypted = tmp / "in.bundle"
            encrypted.write_bytes(B.encrypt(KEY, IV, B._synthetic(8203), "ctr-le"))
            result = subprocess.run([sys.executable, str(ROOT / "tools" / "bundle_crypt.py"),
                                     "--report", str(bad), "--decrypt",
                                     str(encrypted), str(tmp / "out.bundle")],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no construction", result.stderr)


if __name__ == "__main__":
    unittest.main()
