"""Key-hunt tests: AES vectors plus a synthetic encrypted bundle.

No game data: the "bundle" is built here by encrypting a fake UnityFS header.
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import keyhunt as K  # noqa: E402

PLAINTEXT = b"UnityFS" + bytes(range(26)) * 4      # 134 bytes, enough for two blocks


def to_blocks(data: bytes) -> list[bytes]:
    data = data + bytes((-len(data)) % 16)
    return [data[i:i + 16] for i in range(0, len(data), 16)]


def ecb_encrypt(key: bytes, data: bytes) -> bytes:
    return b"".join(K.encrypt_block(key, block) for block in to_blocks(data))


def ctr_encrypt(key: bytes, data: bytes, start: int = 0) -> bytes:
    out = bytearray()
    for index, block in enumerate(to_blocks(data)):
        out += K._xor(block, K.encrypt_block(key, K._counter_block(start + index)))
    return bytes(out)


class AesVectorTests(unittest.TestCase):
    """FIPS-197 appendix C vectors — the tool's AES must be right or nothing counts."""

    def test_aes128(self):
        key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
        block = bytes.fromhex("00112233445566778899aabbccddeeff")
        self.assertEqual(K.encrypt_block(key, block).hex(), "69c4e0d86a7b0430d8cdb78070b4c55a")
        self.assertEqual(K.decrypt_block(key, K.encrypt_block(key, block)), block)

    def test_aes192(self):
        key = bytes.fromhex("000102030405060708090a0b0c0d0e0f1011121314151617")
        block = bytes.fromhex("00112233445566778899aabbccddeeff")
        self.assertEqual(K.encrypt_block(key, block).hex(), "dda97ca4864cdfe06eaf70a0ec0d7191")

    def test_aes256(self):
        key = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
        block = bytes.fromhex("00112233445566778899aabbccddeeff")
        self.assertEqual(K.encrypt_block(key, block).hex(), "8ea2b7ca516745bfeafc49904b496089")

    def test_example_from_the_standard(self):
        key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
        block = bytes.fromhex("6bc1bee22e409f96e93d7e117393172a")
        self.assertEqual(K.encrypt_block(key, block).hex(), "3ad77bb40d7a3660a89ecaf32466ef97")


class StreamCipherVectorTests(unittest.TestCase):
    """Known-answer vectors: RC4 (RFC 6229-style) and ChaCha20 (RFC 8439)."""

    def test_rc4_keystream_rfc_vector(self):
        # key "Key", plaintext "Plaintext" -> ciphertext BBF316E8D940AF0AD3 (classic vector)
        stream = K.rc4_keystream(b"Key", 9)
        plain = b"Plaintext"
        self.assertEqual(bytes(a ^ b for a, b in zip(stream, plain)).hex().upper(),
                         "BBF316E8D940AF0AD3")

    def test_chacha20_block_rfc8439(self):
        key = bytes(range(32))
        nonce = bytes.fromhex("000000090000004a00000000")   # RFC 8439 layout
        block = K.chacha20_block(key, nonce, counter=1)
        self.assertEqual(block[:16].hex(), "10f1e7e4d13b5915500fdd1fa32071c4")

    def test_chacha20_rejects_wrong_key_size(self):
        with self.assertRaises(ValueError):
            K.chacha20_block(b"short")


class CandidateTests(unittest.TestCase):
    def test_printable_and_hex_candidates(self):
        blob = (b"\x00\x01" + b"0123456789abcdef" + b"\x00" + b"a" * 40 + b"\x00"
                + b"3132333435363738393031323334353637383930313233343536373839303132")
        keys = K.candidates_from_blob(blob)
        self.assertIn(b"0123456789abcdef", keys)          # 16 ASCII chars
        self.assertIn(b"12345678901234567890123456789012", keys)   # 32 bytes from hex
        self.assertTrue(all(len(key) in (16, 24, 32) for key in keys))

    def test_substrings_of_longer_runs(self):
        blob = b"x" + b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" + b"x"
        keys = K.candidates_from_blob(blob)
        self.assertIn(b"ABCDEFGHIJKLMNOP", keys)
        self.assertIn(b"QRSTUVWXYZ012345", keys)
        self.assertIn(b"ABCDEFGHIJKLMNOPQRSTUVWXYZ012345", keys)   # 32

    def test_literals_and_derived_keys(self):
        import hashlib
        blob = b"\x00MySecretPassphrase\x00" + b"x" * 100
        runs = K.literals_from_blob(blob)
        self.assertIn(b"MySecretPassphrase", runs)
        derived = K.derive_keys(b"MySecretPassphrase")
        self.assertIn(hashlib.md5(b"MySecretPassphrase").digest(), derived)
        self.assertIn(hashlib.sha256(b"MySecretPassphrase").digest(), derived)
        self.assertTrue(all(len(key) in (16, 24, 32) for key in derived))

    def test_word_list(self):
        words = K.candidates_from_words("short\n0123456789abcdef\n" + "z" * 32 + "\n")
        self.assertEqual(words, [b"0123456789abcdef", b"z" * 32])


class HuntTests(unittest.TestCase):
    def _bundle(self, tmp: Path, data: bytes, name: str = "x.bundle") -> Path:
        path = tmp / name
        path.write_bytes(data)
        return path

    def test_finds_aes_ecb_key(self):
        key = b"0123456789abcdef"
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = self._bundle(tmp, ecb_encrypt(key, PLAINTEXT))
            result = K.hunt([bundle], [b"nope0123456789xy", key])
            self.assertEqual(len(result["found"]), 1)
            self.assertIn("aes-ecb", result["found"][0]["schemes"])
            self.assertEqual(result["found"][0]["key_repr"], "0123456789abcdef")

    def test_finds_aes_ctr_key(self):
        key = b"fedcba9876543210"
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = self._bundle(tmp, ctr_encrypt(key, PLAINTEXT))
            result = K.hunt([bundle], [key])
            self.assertIn("aes-ctr-0", result["found"][0]["schemes"])

    def test_finds_xor_key(self):
        key = b"ABCDEFGHIJKLMNOP"
        data = K._xor(PLAINTEXT, (key * 4)[:len(PLAINTEXT)])
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = self._bundle(tmp, data)
            result = K.hunt([bundle], [key])
            self.assertIn("xor-repeat", result["found"][0]["schemes"])

    def test_no_false_positive_on_random_data(self):
        import os
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = self._bundle(tmp, os.urandom(512))
            keys = [os.urandom(16) for _ in range(50)]
            result = K.hunt([bundle], keys)
            self.assertEqual(result["found"], [])

    def test_missing_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(ValueError):
                K.hunt([Path(raw) / "missing.bundle"], [b"0123456789abcdef"])


class CliTests(unittest.TestCase):
    def test_end_to_end(self):
        key = b"0123456789abcdef"
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "meta.dat").write_bytes(b"\x00noise\x00" + key + b"\x00more noise")
            (tmp / "x.bundle").write_bytes(ecb_encrypt(key, PLAINTEXT))
            out = tmp / "out.json"
            import subprocess
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/keyhunt.py"),
                 "--bundle", str(tmp / "x.bundle"),
                 "--candidates", str(tmp / "meta.dat"),
                 "--out", str(out)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("MATCH", result.stdout)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
