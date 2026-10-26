"""PE probing tests — a synthetic PE image, no game files."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import probe_assembly as P  # noqa: E402


def build_pe(sections):
    """Minimal x86-64 PE with the given [(name, file bytes, executable)]."""
    headers = bytearray(0x400)
    headers[0:2] = b"MZ"
    e_lfanew = 0x80
    headers[0x3C:0x40] = (e_lfanew).to_bytes(4, "little")
    headers[e_lfanew:e_lfanew + 4] = b"PE\x00\x00"
    coff = e_lfanew + 4
    headers[coff:coff + 2] = (0x8664).to_bytes(2, "little")      # machine
    headers[coff + 2:coff + 4] = (len(sections)).to_bytes(2, "little")
    headers[coff + 16:coff + 18] = (0xF0).to_bytes(2, "little")  # optional size
    optional = coff + 20
    headers[optional:optional + 2] = (0x20B).to_bytes(2, "little")   # PE32+
    headers[optional + 24:optional + 32] = (0x140000000).to_bytes(8, "little")

    body = bytearray()
    table = optional + 0xF0
    raw_ptr = 0x400
    for index, (name, blob, executable) in enumerate(sections):
        entry = table + index * 40
        headers[entry:entry + 8] = name.encode("latin-1").ljust(8, b"\x00")
        headers[entry + 8:entry + 12] = len(blob).to_bytes(4, "little")
        headers[entry + 12:entry + 16] = (0x1000 * (index + 1)).to_bytes(4, "little")
        headers[entry + 16:entry + 20] = len(blob).to_bytes(4, "little")
        headers[entry + 20:entry + 24] = raw_ptr.to_bytes(4, "little")
        flags = 0x40000000 | (0x20000000 if executable else 0) | (0x00000040)
        headers[entry + 36:entry + 40] = flags.to_bytes(4, "little")
        body += blob
        raw_ptr += len(blob) + 0x200 - (len(blob) % 0x200)
        body += b"\x00" * (0x200 - (len(blob) % 0x200))
    return bytes(headers) + bytes(body)


class PeTests(unittest.TestCase):
    def test_sections_and_machine(self):
        data = build_pe([(".text", b"\x90" * 64, True), (".rdata", b"K" * 64, False)])
        pe = P.parse_pe(data)
        self.assertEqual(pe["machine"], "x86-64")
        self.assertEqual([s["name"] for s in pe["sections"]], [".text", ".rdata"])
        self.assertTrue(pe["sections"][0]["executable"])
        self.assertFalse(pe["sections"][1]["executable"])

    def test_not_a_pe(self):
        with self.assertRaises(P.PeError):
            P.parse_pe(b"not a pe file at all")

    def test_keyword_search_ascii_and_utf16(self):
        blob = b"\x00AES\x00" + "CreateDecryptor".encode("utf-16-le") + b"\x00CAB-\x00"
        hits = P.find_keywords(blob)
        self.assertIn("AES", hits)
        self.assertIn("CreateDecryptor", hits)
        self.assertIn("CAB-", hits)
        self.assertNotIn("Rijndael", hits)

    def test_candidate_windows_are_unique_and_sized(self):
        blob = bytes(range(64))
        windows = P.candidate_windows(blob, alignment=16)
        self.assertTrue(all(len(w) in (16, 24, 32) for w in windows))
        self.assertEqual(len(windows), len(set(windows)))


class ScanTests(unittest.TestCase):
    def test_scan_finds_a_key_hidden_in_rdata(self):
        key = b"0123456789abcdef"
        rdata = b"\xa5" * 32 + key + b"\x5a" * 32
        dll = build_pe([(".text", b"\xcc" * 128, True), (".rdata", rdata, False)])
        plain = b"UnityFS" + bytes(range(26)) * 4
        plain += bytes((-len(plain)) % 16)          # AES works on whole blocks
        encrypted = b"".join(P.K.encrypt_block(key, plain[i:i + 16])
                             for i in range(0, len(plain), 16))
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "GameAssembly.dll").write_bytes(dll)
            (tmp / "x.bundle").write_bytes(encrypted)
            report = P.scan(tmp / "GameAssembly.dll", [tmp / "x.bundle"])
            self.assertIsNotNone(report["hit"], report)
            self.assertEqual(report["hit"]["key_hex"], key.hex())

    def test_scan_reports_nothing_when_no_key(self):
        dll = build_pe([(".text", b"\xcc" * 128, True), (".rdata", bytes(range(64)), False)])
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "GameAssembly.dll").write_bytes(dll)
            (tmp / "x.bundle").write_bytes(bytes(range(256)) * 2)
            report = P.scan(tmp / "GameAssembly.dll", [tmp / "x.bundle"])
            self.assertIsNone(report["hit"])
            self.assertGreater(report["candidates"]["total"], 0)

    def test_missing_inputs_are_rejected(self):
        with self.assertRaises(P.PeError):
            P.scan(Path("/nonexistent/GameAssembly.dll"), [Path("/nonexistent/x.bundle")])


if __name__ == "__main__":
    unittest.main()
