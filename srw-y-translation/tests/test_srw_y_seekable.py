"""The game's seekable AES stream: derivation, counter layout, and the oracle."""
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import srw_y_seekable as S  # noqa: E402


class DerivationTests(unittest.TestCase):
    def test_pbkdf1_first_iteration_is_sha1_of_password_and_salt(self):
        self.assertEqual(S.password_derive_bytes(b"pw", b"salt", 16, 1),
                         hashlib.sha1(b"pwsalt").digest()[:16])

    def test_iterations_chain(self):
        one = S.password_derive_bytes(b"pw", b"salt", 16, 1)
        two = S.password_derive_bytes(b"pw", b"salt", 16, 2)
        # PBKDF1 chains the full 20-byte digest and truncates only at the end.
        self.assertEqual(two, hashlib.sha1(hashlib.sha1(b"pwsalt").digest()).digest()[:16])
        self.assertNotEqual(two, hashlib.sha1(one).digest()[:16])

    def test_output_lengths(self):
        self.assertEqual(len(S.password_derive_bytes(b"pw", b"s", 16)), 16)
        self.assertEqual(len(S.password_derive_bytes(b"pw", b"s", 32)), 20)  # SHA-1

    def test_iterations_must_be_positive(self):
        with self.assertRaises(ValueError):
            S.password_derive_bytes(b"pw", b"s", 16, 0)

    def test_rfc2898_matches_hashlib(self):
        self.assertEqual(S.rfc2898_bytes(b"pw", b"salt", 16, 1000),
                         hashlib.pbkdf2_hmac("sha1", b"pw", b"salt", 1000, 16))


class StreamTests(unittest.TestCase):
    KEY = bytes(range(16))

    def test_nonce_is_le32_at_offset_zero(self):
        self.assertEqual(S.counter_nonce(1), b"\x01\x00\x00\x00" + b"\x00" * 12)
        self.assertEqual(S.counter_nonce(258), struct.pack("<i", 258) + b"\x00" * 12)

    def test_keystream_is_the_counter_mode(self):
        from Crypto.Cipher import AES

        ecb = AES.new(self.KEY, AES.MODE_ECB)
        stream = S.keystream(self.KEY, 48)
        self.assertEqual(stream[:16], ecb.encrypt(S.counter_nonce(1)))
        self.assertEqual(stream[16:32], ecb.encrypt(S.counter_nonce(2)))
        self.assertEqual(stream[32:48], ecb.encrypt(S.counter_nonce(3)))

    def test_round_trip(self):
        data = b"UnityFS\x00" + bytes(range(200))
        self.assertEqual(S.decrypt(self.KEY, S.encrypt(self.KEY, data)), data)

    def test_matches_only_its_own_key(self):
        stream = S.keystream(self.KEY, 48)
        self.assertTrue(S.matches(self.KEY, stream))
        self.assertFalse(S.matches(bytes(16), stream))
        # A truncated sample is still long enough to decode the first two blocks.
        self.assertTrue(S.matches(self.KEY, stream[:-1]))
        # The oracle looks at exactly 32 bytes, so a bad byte there must fail.
        self.assertFalse(S.matches(self.KEY, b"\x00" + stream[1:]))
        self.assertFalse(S.matches(self.KEY, stream[:31]))

    def test_name_salts_cover_the_name(self):
        salts = dict(S.name_salts("1cc7e02ee5711c6ba87a0e364f62198c.bundle", 940012))
        self.assertEqual(salts["name"],
                         b"1cc7e02ee5711c6ba87a0e364f62198c.bundle")
        self.assertEqual(salts["stem-hex"],
                         bytes.fromhex("1cc7e02ee5711c6ba87a0e364f62198c"))
        self.assertEqual(salts["size-ascii"], b"940012")
        self.assertIn("md5(name)", salts)


class PairTests(unittest.TestCase):
    def test_load_pairs_pairs_by_unique_size(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pair_dir, plain_dir = root / "pairs", root / "plain"
            pair_dir.mkdir()
            plain_dir.mkdir()
            head = (b"UnityFS\x00" + (8).to_bytes(4, "big") + b"5.x.x\x00"
                    + b"2022.3.44f1\x00")
            body = head + b"\x00" * 60
            payload = head + (len(body)).to_bytes(8, "big") + b"\x00" * 52
            (plain_dir / "carved.bundle").write_bytes(payload)
            (pair_dir / "abc.bundle").write_bytes(
                bytes(a ^ 0x5A for a in payload))
            pairs = S.load_pairs(pair_dir, plain_dir)
            self.assertEqual(len(pairs), 1)
            self.assertEqual(pairs[0]["name"], "abc.bundle")
            self.assertTrue(all(b == 0x5A for b in pairs[0]["keystream"]))

    def test_a_size_shared_by_two_plaintexts_is_ambiguous(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pair_dir, plain_dir = root / "pairs", root / "plain"
            pair_dir.mkdir()
            plain_dir.mkdir()
            blob = b"UnityFS\x00" + b"\x00" * 60
            (plain_dir / "a.bundle").write_bytes(blob)
            (plain_dir / "b.bundle").write_bytes(blob[:-1] + b"\x01")
            (pair_dir / "abc.bundle").write_bytes(blob)
            self.assertEqual(S.load_pairs(pair_dir, plain_dir), [])


class CliTests(unittest.TestCase):
    def test_selftest_cli_passes(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools" /
                                                    "srw_y_seekable.py"),
                                 "selftest"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selftest: PASS", result.stdout)

    def test_stream_command_prints_a_keystream(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools" /
                                                    "srw_y_seekable.py"),
                                 "stream", "--password", "pw", "--salt", "x"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("keystream", result.stdout)


if __name__ == "__main__":
    unittest.main()
