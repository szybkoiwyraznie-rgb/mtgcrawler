import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from inventory_local_inputs import inventory_path, write_json_report  # noqa: E402


class LocalInputInventoryTests(unittest.TestCase):
    def test_signature_detection_does_not_depend_on_extension(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cpk = root / "eventP01.EDAT"
            cpk.write_bytes(b"CPK " + b"\x00" * 20)
            odd_name_cpk = root / "odd-name.data"
            odd_name_cpk.write_bytes(b"CPK " + b"\x00" * 16)
            mislabeled_edat = root / "not-a-cpk.EDAT"
            mislabeled_edat.write_bytes(b"not actually a recognized container")

            report = inventory_path(root)
            by_path = {entry["path"]: entry for entry in report["entries"]}

            self.assertEqual(by_path["eventP01.EDAT"]["content_type"], "cpk_signature")
            self.assertEqual(by_path["eventP01.EDAT"]["extension_hint"], ".edat")
            self.assertEqual(by_path["odd-name.data"]["content_type"], "cpk_signature")
            self.assertEqual(by_path["odd-name.data"]["extension_hint"], ".data")
            self.assertEqual(
                by_path["not-a-cpk.EDAT"]["content_type"], "unknown_signature"
            )
            self.assertEqual(by_path["not-a-cpk.EDAT"]["extension_hint"], ".edat")
            self.assertEqual(
                report["signature_counts_by_extension"][".edat"],
                {"cpk_signature": 1, "unknown_signature": 1},
            )
            self.assertEqual(report["file_count"], 3)

    def test_detects_iso_pvd_pbp_sfo_and_zip_signatures(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            iso = bytearray(17 * 2048)
            iso[16 * 2048 : 16 * 2048 + 7] = b"\x01CD001\x01"
            (root / "disc.img").write_bytes(iso)
            (root / "update.bin").write_bytes(b"\x00PBP" + b"\x00" * 12)
            (root / "metadata.bin").write_bytes(b"\x00PSF" + b"\x00" * 12)
            (root / "archive.dat").write_bytes(b"PK\x03\x04" + b"\x00" * 12)

            report = inventory_path(root)
            by_path = {entry["path"]: entry["content_type"] for entry in report["entries"]}

            self.assertEqual(by_path["disc.img"], "iso9660_pvd_signature")
            self.assertEqual(by_path["update.bin"], "pbp_signature")
            self.assertEqual(by_path["metadata.bin"], "psf_sfo_signature")
            self.assertEqual(by_path["archive.dat"], "zip_signature")

    def test_recurses_hashes_and_reports_duplicate_content_deterministically(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            nested = root / "PSP" / "GAME" / "NPJH50521"
            nested.mkdir(parents=True)
            (root / "first.bin").write_bytes(b"same bytes")
            (nested / "second.EDAT").write_bytes(b"same bytes")
            (nested / "third.bin").write_bytes(b"different")

            report = inventory_path(root)

            self.assertEqual(
                [entry["path"] for entry in report["entries"]],
                ["PSP/GAME/NPJH50521/second.EDAT", "PSP/GAME/NPJH50521/third.bin", "first.bin"],
            )
            # Entries are path-sorted lexically, so the first duplicate is the nested file.
            by_path = {entry["path"]: entry for entry in report["entries"]}
            self.assertIsNone(by_path["PSP/GAME/NPJH50521/second.EDAT"]["duplicate_of"])
            self.assertEqual(
                by_path["first.bin"]["duplicate_of"], "PSP/GAME/NPJH50521/second.EDAT"
            )
            self.assertEqual(report["total_size_bytes"], len(b"same bytes") * 2 + len(b"different"))
            self.assertEqual(report["file_count"], 3)

    def test_reports_symlink_without_following_it(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            outside = root / "outside.bin"
            outside.write_bytes(b"CPK " + b"\x00" * 8)
            source = root / "input"
            source.mkdir()
            try:
                (source / "linked.bin").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks are not available on this platform")

            report = inventory_path(source)

            self.assertEqual(report["file_count"], 1)
            self.assertEqual(report["entries"][0]["content_type"], "symlink_not_followed")
            self.assertIsNone(report["entries"][0]["sha256"])

    def test_json_report_is_written_outside_input_and_refuses_inside_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            source = base / "input"
            source.mkdir()
            (source / "game.bin").write_bytes(b"CPK " + b"\x00" * 8)
            report = inventory_path(source)

            output = base / "reports" / "inventory.json"
            write_json_report(report, output, source)
            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(loaded["file_count"], 1)

            with self.assertRaisesRegex(ValueError, "outside the inventoried input"):
                write_json_report(report, source / "inventory.json", source)

    def test_single_file_report_can_share_parent_but_not_overwrite_input(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "game.bin"
            source.write_bytes(b"CPK " + b"\x00" * 8)
            report = inventory_path(source)

            write_json_report(report, root / "inventory.json", source)
            self.assertTrue((root / "inventory.json").is_file())
            with self.assertRaisesRegex(ValueError, "outside the inventoried input"):
                write_json_report(report, source, source)

    def test_inventory_never_changes_input_bytes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "sample.EDAT"
            original = b"CPK " + bytes(range(64))
            source.write_bytes(original)

            inventory_path(source)

            self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
