"""Addressables catalogue mapping tests — synthetic files only.

The binary sections are built here exactly as `tools/map_catalog.py` expects
them, so the parser is exercised end to end without any game data.
"""
import base64
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import map_catalog as M  # noqa: E402

BUNDLE_JA = "1cc7e02ee5711c6ba87a0e364f62198c"
BUNDLE_EN = "2d69c099bfdf0e252dabe84dbbba11df"
BUNDLE_SCENARIO = "1c12bbab8ed0f62ff22f808ce0138bc1"

PROVIDERS = [
    "CriWare.Assets.CriResourceProvider",
    "Com.BBStudio.SRTeam.Data.CustomAssetBundleProvider",
    "UnityEngine.ResourceManagement.ResourceProviders.BundledAssetProvider",
]


def key_records(strings):
    blob = b""
    offsets = []
    for text in strings:
        offsets.append(len(blob))
        if text.startswith("utf16:"):
            payload = text[6:].encode("utf-16-le")
            blob += bytes([1]) + struct.pack("<i", len(payload)) + payload
        else:
            payload = text.encode("utf-8")
            blob += bytes([0]) + struct.pack("<i", len(payload)) + payload
    return blob, offsets


def build_catalog(keys, entries, buckets):
    """keys: list[str]; entries: list[7-tuples]; buckets: list[(keyIndex, [entryIndex])]."""
    key_blob, offsets = key_records(keys)
    bucket_blob = struct.pack("<i", len(buckets))
    for key_index, entry_indices in buckets:
        bucket_blob += struct.pack("<ii", offsets[key_index], len(entry_indices))
        bucket_blob += struct.pack("<%di" % len(entry_indices), *entry_indices)
    entry_blob = struct.pack("<i", len(entries))
    for row in entries:
        entry_blob += struct.pack("<7i", *row)
    return {
        "m_LocatorId": "AddressablesMainContentCatalog",
        "m_BuildResultHash": "0123456789abcdef",
        "m_ProviderIds": PROVIDERS,
        "m_InternalIds": [
            "{" + "UnityEngine.AddressableAssets.Addressables.RuntimePath"
            "}\\StandaloneWindows64\\" + BUNDLE_JA + ".bundle",
            "{" + "UnityEngine.AddressableAssets.Addressables.RuntimePath"
            "}\\StandaloneWindows64\\" + BUNDLE_EN + ".bundle",
            "{" + "UnityEngine.AddressableAssets.Addressables.RuntimePath"
            "}\\StandaloneWindows64\\" + BUNDLE_SCENARIO + ".bundle",
        ],
        "m_KeyDataString": base64.b64encode(key_blob).decode(),
        "m_BucketDataString": base64.b64encode(bucket_blob).decode(),
        "m_EntryDataString": base64.b64encode(entry_blob).decode(),
        "m_ExtraDataString": base64.b64encode(b"\x00").decode(),
    }


def synthetic():
    # key order matters: bundle keys first, then assets that depend on them
    keys = [
        BUNDLE_JA,
        BUNDLE_EN,
        BUNDLE_SCENARIO,
        "dialog_text_ja-JP",
        "dialog_text_en-US",
        "Assets/Datas/Scenario/jp/cse20_0001_0000310a_dlgev.lua.txt",
        "Assets/Datas/Scenario/en/cse20_0001_0000310a_dlgev.lua.txt",
        "Assets/Localization/dialog_text Shared Data.asset",
        "CriMana/Android/AndroidH264Rgb",
    ]
    entries = [
        # bundle entries: provider 1, internal id, no dependency
        (0, 1, -1, 0, 0, 0, 0),
        (1, 1, -1, 0, 0, 1, 0),
        (2, 1, -1, 0, 0, 2, 0),
        # assets: bundled provider 2, depend on the bundle key index
        (0, 2, 0, -11, -1, 3, 8),
        (1, 2, 1, -22, -1, 4, 8),
        (2, 2, 2, -33, -1, 5, 8),
        (2, 2, 2, -44, -1, 6, 8),
        (2, 2, 0, -55, -1, 7, 6),
        # built-in asset: legacy resources provider, nothing to resolve
        (8, 3, -1, 0, 1, 8, 0),
    ]
    buckets = [(index, [index]) for index in range(len(keys))]
    return build_catalog(keys, entries, buckets)


class ParserTests(unittest.TestCase):
    def test_round_trip_mapping(self):
        catalog = M.Catalog(synthetic())
        self.assertEqual(len(catalog.addresses), 9)
        self.assertEqual(catalog.bundle_for(catalog.by_address["dialog_text_ja-JP"]), BUNDLE_JA + ".bundle")
        self.assertEqual(catalog.bundle_for(catalog.by_address["dialog_text_en-US"]), BUNDLE_EN + ".bundle")
        scenario = "Assets/Datas/Scenario/jp/cse20_0001_0000310a_dlgev.lua.txt"
        self.assertEqual(catalog.bundle_for(catalog.by_address[scenario]), BUNDLE_SCENARIO + ".bundle")

    def test_bundle_key_resolves_to_itself(self):
        catalog = M.Catalog(synthetic())
        self.assertEqual(catalog.bundle_for(catalog.by_address[BUNDLE_JA]), BUNDLE_JA + ".bundle")

    def test_unresolvable_asset_is_reported_not_guessed(self):
        catalog = M.Catalog(synthetic())
        result = M.report(catalog, None)
        self.assertEqual(result["counts"]["unresolved"], 1)
        self.assertEqual(result["unresolved_sample"], ["CriMana/Android/AndroidH264Rgb"])

    def test_utf16_keys_are_decoded(self):
        blob, offsets = key_records(["plain", "utf16:zażółć"])
        keys = M.parse_keys(blob, offsets)
        self.assertEqual(keys[offsets[0]]["text"], "plain")
        self.assertEqual(keys[offsets[1]]["text"], "zażółć")

    def test_sections_size_mismatch_is_an_error(self):
        data = synthetic()
        blob = base64.b64decode(data["m_EntryDataString"]) + b"\x00\x00"
        data["m_EntryDataString"] = base64.b64encode(blob).decode()
        with self.assertRaises(M.CatalogError):
            M.Catalog(data)

    def test_missing_section_is_an_error(self):
        data = synthetic()
        del data["m_BucketDataString"]
        with self.assertRaises(M.CatalogError):
            M.Catalog(data)

    def test_not_json_is_an_error(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "catalog.json"
            path.write_text("nope", encoding="utf-8")
            with self.assertRaises(M.CatalogError):
                M.load_catalog(path)


class ValidationTests(unittest.TestCase):
    def test_listing_is_used_for_sizes_and_validation(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            catalog_path = tmp / "catalog.json"
            catalog_path.write_text(json.dumps(synthetic()), encoding="utf-8")
            listing = tmp / "listing.txt"
            listing.write_text(
                "940012\tS Y\\SUPER ROBOT WARS Y_Data\\StreamingAssets\\aa\\StandaloneWindows64\\"
                + BUNDLE_JA + ".bundle\r\n"
                "948652\tS Y\\SUPER ROBOT WARS Y_Data\\StreamingAssets\\aa\\StandaloneWindows64\\"
                + BUNDLE_EN + ".bundle\r\n",
                encoding="utf-8")
            sizes = M.read_listing(listing)
            self.assertEqual(sizes[BUNDLE_JA + ".bundle"], 940012)

            catalog = M.Catalog(M.load_catalog(catalog_path))
            result = M.report(catalog, sizes)
            self.assertTrue(result["validated_against_listing"])
            self.assertEqual(result["bundles_missing_from_listing"], [BUNDLE_SCENARIO + ".bundle"])
            self.assertEqual(result["localization_by_locale"]["ja-JP"]["bundles"][BUNDLE_JA + ".bundle"],
                             940012)

    def test_cli_writes_report(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            catalog_path = tmp / "catalog.json"
            catalog_path.write_text(json.dumps(synthetic()), encoding="utf-8")
            out = tmp / "report.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/map_catalog.py"),
                 "--catalog", str(catalog_path), "--out", str(out)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("addresses", result.stdout)
            saved = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(saved["schema"], M.SCHEMA)
            self.assertEqual(saved["counts"]["addresses"], 9)


if __name__ == "__main__":
    unittest.main()
