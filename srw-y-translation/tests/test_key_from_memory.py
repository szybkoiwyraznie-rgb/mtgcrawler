"""Key recovery: known-prefix logic, array scanning, and an end-to-end fake run."""
import ctypes
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import key_from_memory as K  # noqa: E402
import mem_carve as M  # noqa: E402

try:
    from Crypto.Cipher import AES
    HAVE_CRYPTO = True
except Exception:  # pragma: no cover - pycryptodome is in the venv
    HAVE_CRYPTO = False


def fake_encrypted_bundle(path: Path, key: bytes, iv: bytes) -> None:
    """Write a file that a stream cipher would produce from a real bundle."""
    ecb = AES.new(key, AES.MODE_ECB)
    prefix = K.BUNDLE_PREFIX + b"\x00" * 64
    cipher = bytes(a ^ b for a, b in zip(prefix, ecb.encrypt(iv) * 4))
    path.write_bytes(cipher[:96])


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class PrefixTests(unittest.TestCase):
    def test_keystream_is_the_xor_of_prefix(self):
        key = hashlib.sha256(b"k").digest()
        iv = hashlib.md5(b"i").digest()
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "x.bundle"
            fake_encrypted_bundle(path, key, iv)
            stream = K.known_keystream(path)
            expected = AES.new(key, AES.MODE_ECB).encrypt(iv)
            self.assertEqual(stream, expected)

    def test_prefix_matches_a_real_bundle_header(self):
        # the prefix is taken from bundles carved out of memory; keep it pinned
        self.assertTrue(K.BUNDLE_PREFIX.startswith(b"UnityFS\x00"))
        self.assertIn(b"2022.3.44f1", K.BUNDLE_PREFIX)


class ArrayScanTests(unittest.TestCase):
    def heap(self, *payloads: bytes) -> bytes:
        klass = (0x1F1803285D0).to_bytes(8, "little")
        blob = b"\x00" * 32
        for payload in payloads:
            blob += klass + b"\x00" * 8 + struct.pack("<i", len(payload)) + payload
            blob += b"\x00" * ((8 - len(blob) % 8) % 8)
        return blob

    def test_finds_sixteen_and_thirty_two_byte_arrays(self):
        iv = bytes(range(16))
        key = bytes(range(32))
        found = K.scan_arrays(self.heap(iv, key))
        self.assertEqual(sorted(len(payload) for _k, _a, payload in found), [16, 32])

    def test_constant_payloads_ignored(self):
        self.assertEqual(K.scan_arrays(self.heap(b"\x00" * 32)), [])

    def test_rejects_non_pointer_class(self):
        blob = b"\x00" * 32 + b"\x01" * 8 + b"\x00" * 8 + struct.pack("<i", 16) + b"x" * 16
        self.assertEqual(K.scan_arrays(blob), [])


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class KeyTestTests(unittest.TestCase):
    def test_finds_key_and_iv_from_the_pool(self):
        key = hashlib.sha256(b"selftest").digest()
        iv = hashlib.md5(b"iv").digest()
        ecb = AES.new(key, AES.MODE_ECB)
        keystream = ecb.encrypt(iv)
        hits = K.test_keys([("heap", key)], {iv}, K.BUNDLE_PREFIX[:16],
                           bytes(a ^ b for a, b in zip(keystream,
                                                       K.BUNDLE_PREFIX[:16])))
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["mode"], "stream")
        self.assertEqual(hits[0]["iv_hex"], iv.hex())

    def test_cbc_iv_found_through_the_target_set(self):
        key = hashlib.sha256(b"cbc").digest()
        iv = hashlib.md5(b"cbc-iv").digest()
        plain = K.BUNDLE_PREFIX[:16]
        cipher = AES.new(key, AES.MODE_ECB).encrypt(
            bytes(a ^ b for a, b in zip(plain, iv)))
        hits = K.test_keys([("heap", key)], {iv}, plain, cipher)
        self.assertEqual([hit["mode"] for hit in hits], ["cbc"])

    def test_wrong_key_gives_nothing(self):
        key = hashlib.sha256(b"selftest").digest()
        iv = hashlib.md5(b"iv").digest()
        wrong = hashlib.sha256(b"other").digest()
        keystream = AES.new(key, AES.MODE_ECB).encrypt(iv)
        cipher = bytes(a ^ b for a, b in zip(keystream, K.BUNDLE_PREFIX[:16]))
        self.assertEqual(K.test_keys([("heap", wrong)], {iv},
                                     K.BUNDLE_PREFIX[:16], cipher), [])


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class SelfTestTests(unittest.TestCase):
    def test_selftest_passes(self):
        self.assertTrue(K.self_test()["ok"])

    def test_selftest_cli(self):
        result = subprocess.run([sys.executable,
                                 str(ROOT / "tools" / "key_from_memory.py"),
                                 "--selftest"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("self-test: PASS", result.stdout)
        self.assertIn(K.SCRIPT_VERSION, result.stdout)


class FakeKernel:
    def __init__(self, regions):
        self.regions = regions
        VirtualQueryEx = ctypes.CFUNCTYPE(
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(M.MEMORY_BASIC_INFORMATION), ctypes.c_size_t)
        ReadProcessMemory = ctypes.CFUNCTYPE(
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))
        CloseHandle = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)
        OpenProcess = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_uint32,
                                       ctypes.c_int, ctypes.c_uint32)
        self.VirtualQueryEx = VirtualQueryEx(self._query)
        self.ReadProcessMemory = ReadProcessMemory(self._read)
        self.CloseHandle = CloseHandle(lambda handle: 1)
        self.OpenProcess = OpenProcess(lambda access, inherit, pid: 0x1234)

    def _query(self, handle, address, mbi_ptr, size):
        address = address or 0
        for start, data in self.regions:
            if start + len(data) > address:
                mbi = mbi_ptr.contents
                mbi.BaseAddress = start
                mbi.RegionSize = len(data)
                mbi.State = M.MEM_COMMIT
                mbi.Protect = 0x04
                return 1
        return 0

    def _read(self, handle, address, buffer, size, read_ptr):
        address = address or 0
        for start, data in self.regions:
            if start <= address < start + len(data):
                chunk = data[address - start:address - start + size]
                ctypes.memmove(buffer, chunk, len(chunk))
                read_ptr[0] = len(chunk)
                return 1
        read_ptr[0] = 0
        return 0


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class CollectTests(unittest.TestCase):
    def test_collect_finds_arrays_in_a_region(self):
        key = hashlib.sha256(b"collect").digest()
        iv = hashlib.md5(b"collect-iv").digest()
        klass = (0x1F1803285D0).to_bytes(8, "little")
        heap = b"\x00" * 16
        for payload in (iv, key):
            heap += klass + b"\x00" * 8 + struct.pack("<i", len(payload)) + payload
            heap += b"\x00" * ((8 - len(heap) % 8) % 8)
        kernel = FakeKernel([(0x10000000, heap)])
        keys, ivs, stats = K.collect(kernel, 1)
        self.assertEqual(len(ivs), 1)
        self.assertEqual([payload for _origin, payload in keys], [key])
        self.assertEqual(stats["regions"], 1)

    def test_main_reports_a_verified_key(self):
        key = hashlib.sha256(b"main").digest()
        iv = hashlib.md5(b"main-iv").digest()
        klass = (0x1F1803285D0).to_bytes(8, "little")
        heap = b"\x00" * 16
        for payload in (iv, key):
            heap += klass + b"\x00" * 8 + struct.pack("<i", len(payload)) + payload
            heap += b"\x00" * ((8 - len(heap) % 8) % 8)
        kernel = FakeKernel([(0x10000000, heap)])

        with tempfile.TemporaryDirectory() as raw:
            bundle = Path(raw) / "x.bundle"
            fake_encrypted_bundle(bundle, key, iv)
            report = Path(raw) / "key_report.json"
            with mock.patch.object(M, "win_api", lambda: kernel), \
                    mock.patch.object(M, "process_pid", lambda name: 7), \
                    mock.patch.object(K.sys, "platform", "win32"):
                code = K.main(["--bundle", str(bundle), "--report", str(report)])
            self.assertEqual(code, 0)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(len(data["verified"]), 1)
            self.assertEqual(data["verified"][0]["key_hex"], key.hex())


if __name__ == "__main__":
    unittest.main()
