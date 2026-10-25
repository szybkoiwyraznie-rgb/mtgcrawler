"""KDF hunt tests — derived keys, synthetic bundle, no game data."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import kdf_hunt as D  # noqa: E402
import keyhunt as K  # noqa: E402

PLAINTEXT = b"UnityFS" + bytes(range(26)) * 4


def ecb_encrypt(key: bytes, data: bytes) -> bytes:
    data = data + bytes((-len(data)) % 16)
    return b"".join(K.encrypt_block(key, data[i:i + 16]) for i in range(0, len(data), 16))


def ctr_encrypt(key: bytes, data: bytes) -> bytes:
    data = data + bytes((-len(data)) % 16)
    out = b""
    for index in range(len(data) // 16):
        out += K._xor(data[index * 16:(index + 1) * 16],
                      K.encrypt_block(key, index.to_bytes(16, "big")))
    return out


class DeriveTests(unittest.TestCase):
    def test_pbkdf2_matches_hashlib(self):
        expected = hashlib.pbkdf2_hmac("sha1", b"pw", b"salt", 1000, 16)
        self.assertEqual(D.derive(b"pw", b"salt", 1000, "sha1", 16), expected)

    def test_digest_choice_changes_key(self):
        a = D.derive(b"pw", b"salt", 10, "sha1", 16)
        b = D.derive(b"pw", b"salt", 10, "sha256", 16)
        self.assertNotEqual(a, b)
        self.assertEqual(len(a), 16)
        self.assertEqual(len(b), 16)


class HuntTests(unittest.TestCase):
    def _bundle(self, tmp: Path, data: bytes) -> Path:
        path = tmp / "x.bundle"
        path.write_bytes(data)
        return path

    def test_finds_pbkdf2_key_in_ecb(self):
        key = D.derive(b"SRWY", b"BBStudio", 1000, "sha1", 16)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = self._bundle(tmp, ecb_encrypt(key, PLAINTEXT))
            result = D.hunt([b"nope", b"SRWY"], [b"BBStudio"], [1000], ["sha1"], [16],
                            [("x.bundle", bundle.read_bytes()[:512])])
            self.assertEqual(len(result["found"]), 1, result)
            self.assertEqual(result["found"][0]["password"], "SRWY")

    def test_finds_pbkdf2_key_in_ctr(self):
        key = D.derive(b"pw", b"pepper", 10, "sha256", 32)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = self._bundle(tmp, ctr_encrypt(key, PLAINTEXT))
            result = D.hunt([b"pw"], [b"pepper"], [10], ["sha256"], [32],
                            [("x.bundle", bundle.read_bytes()[:512])])
            self.assertTrue(result["found"], result)

    def test_wrong_iterations_do_not_match(self):
        key = D.derive(b"pw", b"salt", 1000, "sha1", 16)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = self._bundle(tmp, ecb_encrypt(key, PLAINTEXT))
            result = D.hunt([b"pw"], [b"salt"], [1], ["sha1"], [16],
                            [("x.bundle", bundle.read_bytes()[:512])])
            self.assertEqual(result["found"], [])

    def test_word_material(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "words.txt"
            path.write_text("alpha\n\nbeta\n", encoding="utf-8")
            self.assertEqual(D.words_from_file(path), [b"alpha", b"beta"])
            blob = Path(raw) / "blob.bin"
            blob.write_bytes(b"\x00SRWY\x00BBStudio\x00SRWY\x00")
            mined = D.words_from_blob(blob, 10)
            self.assertIn(b"SRWY", mined)
            self.assertEqual(len(mined), len(set(mined)))


if __name__ == "__main__":
    unittest.main()
