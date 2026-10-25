"""The single-file tool the owner runs: selftest, key, decrypt, encrypt."""
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

import srw_y_key as S  # noqa: E402

try:
    from Crypto.Cipher import AES  # noqa: F401
    HAVE_CRYPTO = True
except Exception:  # pragma: no cover
    HAVE_CRYPTO = False

CARVES = ROOT / "local" / "owner_carve4"
SCRIPT = str(ROOT / "tools" / "srw_y_key.py")
KEY = bytes(range(32))
IV = bytes(range(0xF0, 0x100))


class FakeKernel:
    """A process whose heap is exactly the bytes we hand it."""

    def __init__(self, regions):
        self.regions = regions
        VirtualQueryEx = ctypes.CFUNCTYPE(
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(S.MEMORY_BASIC_INFORMATION), ctypes.c_size_t)
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
                mbi.State = S.MEM_COMMIT
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


def heap_with(*payloads: bytes) -> bytes:
    klass = (0x1F1803285D0).to_bytes(8, "little")
    blob = b"\x00" * 32
    for payload in payloads:
        blob += klass + b"\x00" * 8 + struct.pack("<i", len(payload)) + payload
        blob += b"\x00" * ((8 - len(blob) % 8) % 8)
    return blob


class VersionTests(unittest.TestCase):
    def test_version_is_pinned(self):
        self.assertEqual(S.SCRIPT_VERSION, "2026-10-26.2")

    def test_cli_version(self):
        result = subprocess.run([sys.executable, SCRIPT, "--version"],
                                capture_output=True, text=True)
        self.assertEqual(result.stdout.strip(), S.SCRIPT_VERSION)


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class SelfTestTests(unittest.TestCase):
    def test_selftest_function(self):
        self.assertTrue(S.selftest())

    def test_selftest_cli(self):
        result = subprocess.run([sys.executable, SCRIPT, "selftest"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("selftest: PASS", result.stdout)
        self.assertIn("ctr-le", result.stdout)


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class KeyCommandTests(unittest.TestCase):
    def run_key(self, kernel, bundle: Path, extra=()):
        with mock.patch.object(S, "win_api", lambda: kernel), \
                mock.patch.object(S, "process_pid", lambda name: 7):
            return S.main(["key", "--bundle", str(bundle), *extra])

    def test_finds_the_key_and_writes_the_report(self):
        plain = S._synthetic(4096)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "x.bundle"
            bundle.write_bytes(S.encrypt(KEY, IV, plain, "ctr-le"))
            report = tmp / "key_report.json"
            kernel = FakeKernel([(0x10000000, heap_with(IV, KEY))])
            code = self.run_key(kernel, bundle, ("--report", str(report)))
            self.assertEqual(code, 0)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(len(data["verified"]), 1)
            self.assertEqual(data["verified"][0]["key_hex"], KEY.hex())
            self.assertEqual(data["script_version"], S.SCRIPT_VERSION)

    def test_reports_failure_when_the_heap_has_no_key(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "x.bundle"
            bundle.write_bytes(S.encrypt(KEY, IV, S._synthetic(4096), "ctr-le"))
            report = tmp / "key_report.json"
            kernel = FakeKernel([(0x10000000, heap_with(hashlib.md5(b"no").digest()))])
            code = self.run_key(kernel, bundle, ("--report", str(report)))
            self.assertEqual(code, 1)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["verified"], [])

    def test_missing_process_is_a_clean_error(self):
        with tempfile.TemporaryDirectory() as raw:
            bundle = Path(raw) / "x.bundle"
            bundle.write_bytes(b"\x00" * 64)
            with mock.patch.object(S, "process_pid", lambda name: None):
                self.assertEqual(S.main(["key", "--bundle", str(bundle)]), 2)

    def test_missing_bundle_is_a_clean_error(self):
        with tempfile.TemporaryDirectory() as raw:
            code = self.run_key(FakeKernel([]), Path(raw) / "nope.bundle")
            self.assertEqual(code, 2)


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class CryptCommandTests(unittest.TestCase):
    def test_decrypt_then_encrypt_round_trips(self):
        plain = S._synthetic(8203)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            encrypted = tmp / "in.bundle"
            decrypted = tmp / "out.bundle"
            restored = tmp / "back.bundle"
            report = tmp / "key_report.json"
            encrypted.write_bytes(S.encrypt(KEY, IV, plain, "ctr-be"))
            report.write_text(json.dumps({"verified": [{"key_hex": KEY.hex(),
                                                        "iv_hex": IV.hex()}]}),
                              encoding="utf-8")

            first = S.main(["decrypt", "--in", str(encrypted), "--out",
                            str(decrypted), "--report", str(report)])
            self.assertEqual(first, 0)
            self.assertEqual(decrypted.read_bytes(), plain)

            second = S.main(["encrypt", "--in", str(decrypted), "--out",
                             str(restored), "--report", str(report),
                             "--mode", "ctr-be"])
            self.assertEqual(second, 0)
            self.assertEqual(restored.read_bytes(), encrypted.read_bytes())

    def test_decrypt_with_explicit_key_and_mode(self):
        plain = S._synthetic(8203)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            encrypted = tmp / "in.bundle"
            encrypted.write_bytes(S.encrypt(KEY, IV, plain, "ofb"))
            out = tmp / "out.bundle"
            code = S.main(["decrypt", "--in", str(encrypted), "--out", str(out),
                           "--key", KEY.hex(), "--iv", IV.hex(), "--mode", "ofb"])
            self.assertEqual(code, 0)
            self.assertEqual(out.read_bytes(), plain)


@unittest.skipUnless(HAVE_CRYPTO and CARVES.exists(), "no carved bundles here")
class RealBundleTests(unittest.TestCase):
    def test_single_file_tool_round_trips_a_real_bundle(self):
        source = next(CARVES.rglob("*.bundle"))
        plain = source.read_bytes()
        self.assertIsNotNone(S.parse_unityfs(plain[:S.PROBE]))
        for mode in ("ctr-le", "ctr-be", "cfb128", "ofb"):
            found = S.identify(KEY, IV, S.encrypt(KEY, IV, plain, mode))
            self.assertEqual(found[0], mode, source.name)
            self.assertEqual(found[1], plain, source.name)


if __name__ == "__main__":
    unittest.main()
