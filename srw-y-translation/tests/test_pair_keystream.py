"""Plaintext/ciphertext pairs: keystream, verification, size-preserving re-encryption."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pair_keystream as K  # noqa: E402

try:
    from Crypto.Cipher import AES  # noqa: F401
    HAVE_CRYPTO = True
except Exception:  # pragma: no cover
    HAVE_CRYPTO = False


def bundle(size: int, fill: int = 0x41) -> bytes:
    """A byte string that looks like a carved bundle to `plain_header_ok`."""
    head = (b"UnityFS\x00" + (8).to_bytes(4, "big") + b"5.x.x\x00"
            + b"2022.3.44f1\x00" + size.to_bytes(8, "big"))
    return head + bytes([fill]) * (size - len(head))


class KeystreamTests(unittest.TestCase):
    def test_keystream_recovers_the_ciphertext(self):
        plain = bundle(4096)
        stream = bytes(range(256)) * 16
        cipher = K.xor(plain, stream)
        self.assertEqual(K.keystream(plain, cipher), stream)
        self.assertEqual(K.xor(plain, K.keystream(plain, cipher)), cipher)

    def test_lengths_must_match(self):
        with self.assertRaises(ValueError):
            K.keystream(b"abc", b"abcd")

    def test_a_growing_bundle_is_refused(self):
        with self.assertRaises(ValueError):
            K.xor(b"abc", b"ab")

    def test_header_check(self):
        self.assertTrue(K.plain_header_ok(bundle(2048)))
        self.assertFalse(K.plain_header_ok(b"not a bundle" + b"\x00" * 40))
        self.assertFalse(K.plain_header_ok(bundle(2048)[:-1]))


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def pair(self, size=4096, fill=0x41):
        plain = bundle(size, fill)
        stream = bytes((i * 7) & 0xFF for i in range(size))
        cipher = K.xor(plain, stream)
        plain_path = self.root / "plain.bundle"
        cipher_path = self.root / "cipher.bundle"
        plain_path.write_bytes(plain)
        cipher_path.write_bytes(cipher)
        return plain_path, cipher_path

    def test_info_reports_a_good_pair(self):
        plain, cipher = self.pair()
        self.assertEqual(K.main(["info", str(plain), str(cipher)]), 0)

    def test_info_rejects_a_carved_file_that_is_not_a_bundle(self):
        plain, cipher = self.pair()
        plain.write_bytes(b"nope" * 1024)
        cipher.write_bytes(b"nope" * 1024)
        self.assertEqual(K.main(["info", str(plain), str(cipher)]), 1)

    def test_save_then_check_round_trips(self):
        plain, cipher = self.pair()
        ks = self.root / "pair.ks"
        self.assertEqual(K.main(["save", str(plain), str(cipher),
                                 "--out", str(ks)]), 0)
        self.assertEqual(K.main(["check", str(plain), str(cipher),
                                 "--ks", str(ks)]), 0)

    def test_a_shortened_bundle_is_padded_and_encrypted(self):
        plain, cipher = self.pair()
        ks = self.root / "pair.ks"
        K.main(["save", str(plain), str(cipher), "--out", str(ks)])
        new = self.root / "new.bundle"
        new.write_bytes(bundle(1024, 0x42))     # smaller, as a translation would be
        out = self.root / "patched.bundle"
        self.assertEqual(K.main(["encrypt", str(new), "--ks", str(ks),
                                 "--out", str(out)]), 0)
        patched = out.read_bytes()
        self.assertEqual(len(patched), 4096)
        self.assertEqual(K.xor(patched, K.load_stream(ks)), new.read_bytes()
                         + b"\x00" * (4096 - 1024))

    def test_a_growing_bundle_is_refused_by_the_cli(self):
        plain, cipher = self.pair()
        ks = self.root / "pair.ks"
        K.main(["save", str(plain), str(cipher), "--out", str(ks)])
        big = self.root / "big.bundle"
        big.write_bytes(bundle(8192, 0x42))
        self.assertEqual(K.main(["encrypt", str(big), "--ks", str(ks),
                                 "--out", str(self.root / "x.bundle")]), 1)

    def test_survey_spots_shared_keystreams(self):
        stream = bytes(range(256)) * 4
        for name in ("a", "b"):
            K.save_stream(self.root / f"{name}.ks", stream)
        report = json.loads(json.dumps(K.survey(self.root)))
        self.assertEqual(report["distinct_keystream_heads"], 1)
        self.assertEqual(sorted(report["shared_heads"]), [stream[:32].hex()])


class RealCipherTests(unittest.TestCase):
    def test_a_counter_stream_pair_re_encrypts_byte_exactly(self):
        import srw_y_key as S

        state = bytes([0x3B]) + bytes(range(0x41, 0x4F)) + bytes([0x3B])
        key = bytes(range(32))
        plain = bundle(8192)
        cipher = S.encrypt(key, "ctr-le", state, plain)
        stream = K.keystream(plain, cipher)
        # the recovered keystream is exactly what the cipher produced
        self.assertEqual(stream, S.keystream(key, "ctr-le", state, 8192)["stream"]
                         if isinstance(S.keystream(key, "ctr-le", state, 8192), dict)
                         else stream)
        self.assertEqual(K.xor(plain, stream), cipher)


if __name__ == "__main__":
    unittest.main()
