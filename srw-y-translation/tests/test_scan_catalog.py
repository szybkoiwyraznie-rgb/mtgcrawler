"""Catalogue scanner tests — synthetic catalogues only, no game files."""
import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import scan_catalog as C  # noqa: E402

BUNDLE_A = "2e1c004184c62d08997e13aed13a1004.bundle"
BUNDLE_B = "543dcfca980ee913ad786fd13cf848e1.bundle"


def synthetic_catalog(marker: str = "Assets/GameData/Text/English/Scenario001_Text.asset") -> dict:
    """A miniature Addressables catalogue with one binary key section."""
    key_blob = b"".join([
        marker.encode() + b"\x00",
        b"Assets/GameData/UI/Layout_MainMenu.asset\x00",
        b"Assets/GameData/Units/MS_Gundam.asset\x00",
        BUNDLE_A.encode() + b"\x00",
        b"Assets/GameData/Text/Japanese/Scenario001_Text.asset\x00",
        BUNDLE_B.encode() + b"\x00",
        b"MS_Gundam_Text\x00",
    ])
    bucket_blob = b"\x00\x01\x02" + BUNDLE_A.encode() + b"\x00"
    return {
        "m_LocatorId": "AddressablesMainContentCatalog",
        "m_BuildResultHash": "0123456789abcdef",
        "m_InstanceProviderData": {"m_Id": "Assembly-CSharp", "m_ObjectType": {"m_ClassName": "AssetBundleProvider"}},
        "m_InternalIds": [
            "{UnityEngine.AddressableAssets.Addressables.RuntimePath}/StandaloneWindows64/" + BUNDLE_A,
            "{UnityEngine.AddressableAssets.Addressables.RuntimePath}/StandaloneWindows64/" + BUNDLE_B,
        ],
        "m_ProviderIds": ["UnityEngine.ResourceManagement.ResourceProviders.AssetBundleProvider"] * 2,
        "m_BucketDataString": base64.b64encode(bucket_blob).decode(),
        "m_KeyDataString": base64.b64encode(key_blob).decode(),
        "m_EntryDataString": base64.b64encode(b"\x01\x02\x03" * 8).decode(),
        "m_ExtraDataString": base64.b64encode(b"MS_Gundam_Text\x00").decode(),
    }


def write(tmp: Path, data: dict, name: str = "catalog.json") -> Path:
    path = tmp / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class ClassificationTests(unittest.TestCase):
    def test_bundle_and_asset_and_hint(self):
        self.assertEqual(C.classify(BUNDLE_A), "bundle")
        self.assertEqual(C.classify("aaaa1111bbbb2222cccc3333dddd4444"), "bundle")
        self.assertEqual(C.classify("Assets/GameData/Units/MS_Gundam.asset"), "asset_path")
        self.assertEqual(C.classify("Scenario001_Text"), "text_hint")
        self.assertEqual(C.classify("UnityEngine.ResourceManagement"), "other")

    def test_base64_detection_is_conservative(self):
        self.assertFalse(C.is_base64_blob("short"))
        self.assertFalse(C.is_base64_blob("Assets/GameData/Not Base64!"))
        self.assertFalse(C.is_base64_blob("A" * 63))          # not a multiple of 4
        self.assertTrue(C.is_base64_blob(base64.b64encode(b"x" * 64).decode()))

    def test_string_scan_reads_utf8_including_polish(self):
        blob = (b"Assets/Text/Hello.asset\x00"
                + "Assets/Text/Zażółć_gęślą.asset".encode("utf-8") + b"\x00"
                + b"\x00\x01\x02binary\x00")
        found = C.scan_strings(blob)
        self.assertIn("Assets/Text/Hello.asset", found)
        self.assertIn("Assets/Text/Zażółć_gęślą.asset", found)
        self.assertIn("binary", found)


class ScanTests(unittest.TestCase):
    def test_recovers_addresses_from_binary_section(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write(Path(raw), synthetic_catalog())
            report = C.scan(path)
            hints = report["candidate_text_addresses"]
            self.assertIn("Assets/GameData/Text/English/Scenario001_Text.asset", hints)
            self.assertIn("Assets/GameData/Text/Japanese/Scenario001_Text.asset", hints)
            self.assertIn("MS_Gundam_Text", hints)
            self.assertEqual(report["counts"]["bundles"], 2)  # distinct bundle names, not per occurrence
            self.assertGreaterEqual(report["counts"]["asset_paths"], 3)
            self.assertEqual(report["identity"]["m_LocatorId"], "AddressablesMainContentCatalog")

    def test_heuristic_pairs_address_with_nearby_bundle(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write(Path(raw), synthetic_catalog())
            report = C.scan(path)
            pairs = report["text_address_to_bundle_heuristic"]
            self.assertIn("Assets/GameData/Text/English/Scenario001_Text.asset", pairs)
            self.assertIn(BUNDLE_A, pairs["Assets/GameData/Text/English/Scenario001_Text.asset"])
            self.assertIn(BUNDLE_B, pairs["Assets/GameData/Text/Japanese/Scenario001_Text.asset"])

    def test_report_is_deterministic_and_contains_no_binary(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write(Path(raw), synthetic_catalog())
            first = json.dumps(C.scan(path), sort_keys=True)
            second = json.dumps(C.scan(path), sort_keys=True)
            self.assertEqual(first, second)
            self.assertNotIn("\\u0000", first)
            self.assertNotIn("m_KeyDataString\x00", first)

    def test_missing_or_broken_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            with self.assertRaises(SystemExit):
                C.scan(tmp / "nope.json")
            broken = tmp / "broken.json"
            broken.write_text("not json at all", encoding="utf-8")
            with self.assertRaises(SystemExit):
                C.scan(broken)

    def test_cli_writes_summary(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            path = write(tmp, synthetic_catalog())
            out = tmp / "summary.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/scan_catalog.py"),
                 "--catalog", str(path), "--out", str(out), "--print-candidates", "5"],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("text-ish addrs", result.stdout)
            summary = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(summary["schema"], C.SCHEMA)
            self.assertIn("Assets/GameData/Text/English/Scenario001_Text.asset",
                          summary["candidate_text_addresses"])


if __name__ == "__main__":
    unittest.main()
