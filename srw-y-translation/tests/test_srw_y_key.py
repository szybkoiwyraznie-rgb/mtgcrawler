"""The single-file tool the owner runs: selftest, key, decrypt, encrypt.

The important test here is `NoIvNeededTests`: the key must be accepted from the
ciphertext alone, because the first owner run demanded a 16-byte IV found in the
game's heap and never found one - the correct key was probably there and rejected.
"""
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
STATE = bytes(range(0x40, 0x50))
STREAM_MODES = ("ctr-le", "ctr-be", "ofb", "cfb128", "cfb8")


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
    """A heap-like blob holding each payload as a managed byte[] (layout A)."""
    klass = (0x1F1803285D0).to_bytes(8, "little")
    blob = b"\x00" * 32
    for payload in payloads:
        blob += klass + b"\x00" * 8 + struct.pack("<i", len(payload)) + payload
        blob += b"\x00" * ((8 - len(blob) % 8) % 8)
    return blob


class VersionTests(unittest.TestCase):
    def test_version_is_pinned(self):
        self.assertEqual(S.SCRIPT_VERSION, "2026-10-26.6")

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
        self.assertIn("2026-10-26.6", result.stdout)


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class NoIvNeededTests(unittest.TestCase):
    """The key is judged by the ciphertext, not by an IV that may not exist."""

    def test_check_key_recognises_each_mode_without_any_heap(self):
        for mode in S.MODES:
            plain = S._synthetic(8208 if mode in ("cbc", "ecb") else 8211)
            cipher = S.encrypt(KEY, mode, STATE, plain)
            hits = S.check_key(KEY, cipher[:48], len(plain))
            self.assertIn(mode, [hit["mode"] for hit in hits], mode)
            chosen = [hit for hit in hits if hit["mode"] == mode][0]
            self.assertEqual(S.decrypt(KEY, mode, chosen["state"], cipher), plain,
                             mode)

    def test_a_wrong_key_matches_nothing(self):
        plain = S._synthetic(8211)
        cipher = S.encrypt(KEY, "ctr-le", STATE, plain)
        self.assertEqual(S.check_key(bytes(range(32, 64)), cipher[:48], len(plain)), [])

    def test_the_state_is_recoverable_not_required(self):
        # encrypt with an IV nobody stores anywhere, then recover it from the file
        plain = S._synthetic(8211)
        for mode in STREAM_MODES:
            cipher = S.encrypt(KEY, mode, STATE, plain)
            self.assertNotIn(STATE, cipher)
            found = S.identify(KEY, cipher)
            self.assertIsNotNone(found, mode)
            self.assertEqual(found[0], mode)
            self.assertEqual(found[2], plain)


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class ScanTests(unittest.TestCase):
    def test_candidates_are_found_at_three_payload_offsets(self):
        klass = (0x1F1803285D0).to_bytes(8, "little")
        payload = bytes(range(32))
        for offset in S.PAYLOAD_OFFSETS:
            blob = (klass + b"\x00" * 8 + struct.pack("<i", 32)
                    + b"\x00" * (offset - 4) + payload)
            found = [item for item in S.scan_arrays(blob) if item[2] == payload]
            self.assertTrue(found, f"payload at +{offset} not found")

    def test_a_locked_object_still_yields_its_array(self):
        """A thin lock puts a pointer in the sync block; the array is still there."""
        klass = (0x1F1803285D0).to_bytes(8, "little")
        lock = (0x1F1C0000A00).to_bytes(8, "little")
        payload = bytes(range(32))
        blob = klass + lock + struct.pack("<i", 32) + payload
        found = [item for item in S.scan_arrays(blob) if item[2] == payload]
        self.assertTrue(found)

    def test_constant_payloads_are_ignored(self):
        klass = (0x1F1803285D0).to_bytes(8, "little")
        blob = klass + b"\x00" * 8 + struct.pack("<i", 32) + b"\x00" * 32
        self.assertEqual(S.scan_arrays(blob), [])


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class KeyCommandTests(unittest.TestCase):
    def run_key(self, kernel, bundle, extra=()):
        with mock.patch.object(S, "win_api", lambda: kernel), \
                mock.patch.object(S, "process_pid", lambda name: 7):
            return S.main(["key", "--bundle", str(bundle), *extra])

    def test_finds_a_key_when_the_heap_holds_no_iv_at_all(self):
        """The owner's six failed runs: key present, IV absent, nothing verified."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "x.bundle"
            plain = S._synthetic(940012 // 100)
            bundle.write_bytes(S.encrypt(KEY, "ctr-be", STATE, plain))
            report = tmp / "key_report.json"
            kernel = FakeKernel([(0x10000000, heap_with(KEY))])
            code = self.run_key(kernel, bundle, ("--report", str(report)))
            self.assertEqual(code, 0)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(len(data["verified"]), 1)
            hit = data["verified"][0]
            self.assertEqual(hit["key_hex"], KEY.hex())
            self.assertEqual(hit["mode"], "ctr-be")
            # the payload offset is guessed at +4/+8/+12, so a single array can
            # yield more than one candidate; what matters is that the key is among
            # them and that the heap held no IV
            self.assertGreaterEqual(data["candidates_by_length"].get("32", 0), 1)

    def test_reports_failure_when_the_heap_has_no_key(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "x.bundle"
            bundle.write_bytes(S.encrypt(KEY, "ctr-le", STATE, S._synthetic(4096)))
            report = tmp / "key_report.json"
            kernel = FakeKernel([(0x10000000, heap_with(hashlib.md5(b"no").digest()))])
            self.assertEqual(self.run_key(kernel, bundle, ("--report", str(report))), 1)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["verified"], [])
            self.assertTrue(data["candidates_by_length"])

    def test_missing_process_is_a_clean_error(self):
        with tempfile.TemporaryDirectory() as raw:
            bundle = Path(raw) / "x.bundle"
            bundle.write_bytes(b"\x00" * 64)
            with mock.patch.object(S, "process_pid", lambda name: None):
                self.assertEqual(S.main(["key", "--bundle", str(bundle)]), 2)

    def test_passes_scan_again_and_reach_the_same_candidates(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "x.bundle"
            bundle.write_bytes(S.encrypt(KEY, "ctr-le", STATE, S._synthetic(4096)))
            report = tmp / "key_report.json"
            kernel = FakeKernel([(0x10000000, heap_with(KEY))])
            with mock.patch.object(S.time, "sleep", lambda seconds: None):
                code = self.run_key(kernel, bundle,
                                    ("--report", str(report), "--passes", "2"))
            self.assertEqual(code, 0)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["passes"], 2)
            self.assertEqual(len(data["verified"]), 1)

    def test_progress_survives_many_regions(self):
        regions = [(0x10000000 + index * 0x10000, heap_with(STATE))
                   for index in range(60)]
        regions.append((0x30000000, heap_with(KEY)))
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "x.bundle"
            bundle.write_bytes(S.encrypt(KEY, "ctr-le", STATE, S._synthetic(4096)))
            report = tmp / "key_report.json"
            self.assertEqual(self.run_key(FakeKernel(regions), bundle,
                                          ("--report", str(report))), 0)


@unittest.skipUnless(HAVE_CRYPTO, "pycryptodome not installed")
class CryptCommandTests(unittest.TestCase):
    def write_report(self, path: Path, mode: str = "ctr-be") -> None:
        path.write_text(json.dumps({"verified": [{"mode": mode,
                                                  "key_hex": KEY.hex(),
                                                  "state_hex": STATE.hex()}]}),
                        encoding="utf-8")

    def test_decrypt_then_encrypt_round_trips(self):
        plain = S._synthetic(8211)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            encrypted, decrypted, restored = (tmp / "in.bundle",
                                              tmp / "out.bundle",
                                              tmp / "back.bundle")
            report = tmp / "key_report.json"
            encrypted.write_bytes(S.encrypt(KEY, "cfb128", STATE, plain))
            self.write_report(report)
            data = json.loads(report.read_text(encoding="utf-8"))
            data["verified"][0]["mode"] = "cfb128"
            report.write_text(json.dumps(data), encoding="utf-8")

            self.assertEqual(S.main(["decrypt", "--in", str(encrypted), "--out",
                                     str(decrypted), "--report", str(report)]), 0)
            self.assertEqual(decrypted.read_bytes(), plain)
            self.assertEqual(S.main(["encrypt", "--in", str(decrypted), "--out",
                                     str(restored), "--report", str(report)]), 0)
            self.assertEqual(restored.read_bytes(), encrypted.read_bytes())

    def test_explicit_key_and_state(self):
        plain = S._synthetic(8211)
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            encrypted, out = tmp / "in.bundle", tmp / "out.bundle"
            encrypted.write_bytes(S.encrypt(KEY, "ofb", STATE, plain))
            code = S.main(["decrypt", "--in", str(encrypted), "--out", str(out),
                           "--key", KEY.hex(), "--iv", STATE.hex(),
                           "--mode", "ofb"])
            self.assertEqual(code, 0)
            self.assertEqual(out.read_bytes(), plain)

    def test_refuses_without_a_report(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            bundle = tmp / "in.bundle"
            bundle.write_bytes(b"\x00" * 64)
            self.assertEqual(S.main(["decrypt", "--in", str(bundle), "--out",
                                     str(tmp / "o.bundle"),
                                     "--report", str(tmp / "nope.json")]), 2)


@unittest.skipUnless(HAVE_CRYPTO and CARVES.exists(), "no carved bundles here")
class RealBundleTests(unittest.TestCase):
    def test_real_bundle_round_trips_through_every_stream_mode(self):
        source = next(CARVES.rglob("*.bundle"))
        plain = source.read_bytes()
        self.assertIsNotNone(S.parse_unityfs(plain[:S.PROBE]))
        for mode in STREAM_MODES:
            cipher = S.encrypt(KEY, mode, STATE, plain)
            found = S.identify(KEY, cipher)
            self.assertIsNotNone(found, mode)
            self.assertEqual(found[0], mode, source.name)
            self.assertEqual(found[2], plain, source.name)
            self.assertEqual(len(cipher), len(plain), source.name)


if __name__ == "__main__":
    unittest.main()
