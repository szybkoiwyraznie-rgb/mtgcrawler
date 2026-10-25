"""The recovered bundle cipher: password, salt, keystream, and the pair survey."""
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import srw_y_bundle_crypt as C  # noqa: E402

PAIR_NAME = "00490461b04976657673ede043b22592.bundle"
# The key the pair data produced when the exact metadata literals were tried.
KNOWN_KEY = "bb979f3e4714554a5b216229fe2b0d60"


class DerivationTests(unittest.TestCase):
    def test_password_is_the_recovered_constant(self):
        self.assertEqual(C.PASSWORD, b"ComBBStudioSRTeam")

    def test_key_matches_the_pair_proof(self):
        self.assertEqual(C.key_for(PAIR_NAME).hex(), KNOWN_KEY)

    def test_salt_is_the_file_name_without_the_extension(self):
        self.assertEqual(C.salt_for(PAIR_NAME),
                         b"00490461b04976657673ede043b22592")

    def test_a_directory_is_kept(self):
        self.assertEqual(C.salt_for("aa/bb.bundle"), b"aa/bb")

    def test_key_is_pbkdf1_sha1_with_a_hundred_rounds(self):
        digest = hashlib.sha1(b"ComBBStudioSRTeam"
                              + b"00490461b04976657673ede043b22592").digest()
        for _ in range(99):
            digest = hashlib.sha1(digest).digest()
        self.assertEqual(C.key_for(PAIR_NAME), digest[:16])

    def test_every_file_gets_its_own_key(self):
        self.assertNotEqual(C.key_for("a.bundle"), C.key_for("b.bundle"))

    def test_iterations_are_checkable(self):
        self.assertNotEqual(C.key_for("a.bundle", iterations=1), C.key_for("a.bundle"))
        with self.assertRaises(ValueError):
            C.key_for("a.bundle", iterations=0)


class StreamTests(unittest.TestCase):
    def test_nonce_layout(self):
        self.assertEqual(C.nonce(1), b"\x01\x00\x00\x00" + b"\x00" * 12)
        self.assertEqual(C.nonce(70000), struct.pack("<i", 70000) + b"\x00" * 12)

    def test_keystream_is_ecb_over_the_counter(self):
        from Crypto.Cipher import AES

        key = C.key_for(PAIR_NAME)
        ecb = AES.new(key, AES.MODE_ECB)
        stream = C.keystream(key, 48)
        self.assertEqual(stream[:16], ecb.encrypt(C.nonce(1)))
        self.assertEqual(stream[32:48], ecb.encrypt(C.nonce(3)))

    def test_round_trip_keeps_the_length(self):
        payload = b"UnityFS\x00" + bytes(range(200))
        blob = C.encrypt(PAIR_NAME, payload)
        self.assertEqual(len(blob), len(payload))
        self.assertNotEqual(blob, payload)
        self.assertEqual(C.decrypt(PAIR_NAME, blob), payload)

    def test_encryption_is_deterministic(self):
        payload = b"x" * 64
        self.assertEqual(C.encrypt(PAIR_NAME, payload), C.encrypt(PAIR_NAME, payload))

    def test_the_wrong_name_gives_the_wrong_bytes(self):
        payload = b"UnityFS\x00" + b"\x00" * 64
        self.assertNotEqual(C.decrypt("ffffffffffffffffffffffffffffffff.bundle",
                                      C.encrypt(PAIR_NAME, payload)), payload)


class VerifyTests(unittest.TestCase):
    def _store(self, root: Path, names, plain_of, cipher_of):
        pairs, plain = root / "pairs", root / "plain"
        pairs.mkdir()
        plain.mkdir()
        for name in names:
            data = plain_of(name)
            (pairs / name).write_bytes(cipher_of(name, data))
            (plain / name).write_bytes(data)
        return pairs, plain

    def test_a_pair_round_trips_through_verify(self):
        names = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.bundle",
                 "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.bundle"]
        payloads = {name: b"UnityFS\x00" + bytes(range(120)) for name in names}
        with tempfile.TemporaryDirectory() as raw:
            pairs, plain = self._store(Path(raw), names, lambda n: payloads[n],
                                       lambda n, d: C.encrypt(n, d))
            report = C.verify(pairs, plain)
            self.assertEqual(report["pairs"], 2)
            self.assertEqual(report["oracle_matches"], 2)
            self.assertEqual(report["carve_head_matches"], 2)
            self.assertEqual(report["failures"], [])

    def test_a_wrong_password_is_caught(self):
        names = ["cccccccccccccccccccccccccccccccc.bundle"]
        payload = b"UnityFS\x00" + bytes(range(120))
        with tempfile.TemporaryDirectory() as raw:
            pairs, plain = self._store(Path(raw), names, lambda n: payload,
                                       lambda n, d: C.xor_stream(d, bytes(16)))
            report = C.verify(pairs, plain)
            self.assertEqual(report["oracle_matches"], 0)

    def test_a_carve_that_is_not_a_bundle_is_ignored(self):
        names = ["dddddddddddddddddddddddddddddddd.bundle"]
        payload = b"UnityFS\x00" + b"\x00" * 96
        with tempfile.TemporaryDirectory() as raw:
            pairs, plain = self._store(Path(raw), names, lambda n: payload,
                                       lambda n, d: C.encrypt(n, d))
            (plain / "noise.bundle").write_bytes(b"not a bundle at all" + b"\x00" * 96)
            self.assertEqual(C.verify(pairs, plain)["carve_head_matches"], 1)


class CliTests(unittest.TestCase):
    def test_selftest_passes(self):
        result = subprocess.run([sys.executable,
                                 str(ROOT / "tools" / "srw_y_bundle_crypt.py"),
                                 "selftest"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selftest: PASS", result.stdout)

    def test_decrypt_writes_a_file(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            name = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.bundle"
            blob = C.encrypt(name, b"UnityFS\x00" + b"\x11" * 64)
            source = root / name
            source.write_bytes(blob)
            target = root / "out.bundle"
            result = subprocess.run([sys.executable,
                                     str(ROOT / "tools" / "srw_y_bundle_crypt.py"),
                                     "decrypt", name, str(target),
                                     "--input", str(source)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(target.read_bytes()[:7], b"UnityFS")


if __name__ == "__main__":
    unittest.main()
