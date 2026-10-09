import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import extract_cpk_batch  # noqa: E402
from inventory_local_inputs import inventory_path  # noqa: E402
from iso9660 import BLOCK_SIZE, Iso9660Error, inspect_iso9660  # noqa: E402


def _both_endian(value, width):
    return value.to_bytes(width, "little") + value.to_bytes(width, "big")


def _record(extent_lba, byte_length, flags, identifier, *, continues=False):
    identifier = bytes(identifier)
    record_length = 33 + len(identifier) + (len(identifier) % 2 == 0)
    record = bytearray(record_length)
    record[0] = record_length
    record[2:10] = _both_endian(extent_lba, 4)
    record[10:18] = _both_endian(byte_length, 4)
    record[25] = flags | (0x80 if continues else 0)
    record[28:32] = _both_endian(1, 2)
    record[32] = len(identifier)
    record[33 : 33 + len(identifier)] = identifier
    return bytes(record)


def _put_records(image, lba, records):
    data = b"".join(records)
    if len(data) > BLOCK_SIZE:
        raise AssertionError("synthetic directory does not fit in one sector")
    start = lba * BLOCK_SIZE
    image[start : start + len(data)] = data


def _synthetic_iso():
    """Build a tiny PVD-only ISO fixture; it contains no game data."""
    volume_blocks = 26
    image = bytearray(volume_blocks * BLOCK_SIZE)

    pvd = bytearray(BLOCK_SIZE)
    pvd[0] = 1
    pvd[1:6] = b"CD001"
    pvd[6] = 1
    pvd[80:88] = _both_endian(volume_blocks, 4)
    pvd[128:132] = _both_endian(BLOCK_SIZE, 2)
    root_record = _record(20, BLOCK_SIZE, 0x02, b"\x00")
    pvd[156 : 156 + len(root_record)] = root_record
    image[16 * BLOCK_SIZE : 17 * BLOCK_SIZE] = pvd

    terminator = bytearray(BLOCK_SIZE)
    terminator[0] = 255
    terminator[1:6] = b"CD001"
    terminator[6] = 1
    image[17 * BLOCK_SIZE : 18 * BLOCK_SIZE] = terminator

    _put_records(
        image,
        20,
        [
            _record(20, BLOCK_SIZE, 0x02, b"\x00"),
            _record(20, BLOCK_SIZE, 0x02, b"\x01"),
            _record(21, BLOCK_SIZE, 0x02, b"DATA"),
        ],
    )
    _put_records(
        image,
        21,
        [
            _record(21, BLOCK_SIZE, 0x02, b"\x00"),
            _record(20, BLOCK_SIZE, 0x02, b"\x01"),
            _record(22, 6, 0, b"ARCHIVE.CPK;1"),
            _record(23, 2, 0, b"SPLIT.BIN;1", continues=True),
            _record(24, 2, 0, b"SPLIT.BIN;1"),
            _record(25, 6, 0, b"OTHER.BIN;1"),
        ],
    )
    image[22 * BLOCK_SIZE : 22 * BLOCK_SIZE + 6] = b"CPK \x01\x02"
    image[23 * BLOCK_SIZE : 23 * BLOCK_SIZE + 2] = b"CP"
    image[24 * BLOCK_SIZE : 24 * BLOCK_SIZE + 2] = b"K "
    image[25 * BLOCK_SIZE : 25 * BLOCK_SIZE + 6] = b"ABCD\x00\x00"
    return image


class Iso9660InventoryTests(unittest.TestCase):
    def test_indexes_pvd_members_and_detects_signatures_across_extents(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            image_path = Path(temporary_directory) / "synthetic.iso"
            image_path.write_bytes(_synthetic_iso())

            inventory = inspect_iso9660(image_path)
            files = {member["path"]: member for member in inventory["files"]}

            self.assertEqual(inventory["status"], "indexed")
            self.assertEqual(inventory["logical_block_size"], BLOCK_SIZE)
            self.assertEqual(inventory["file_count"], 3)
            self.assertEqual(inventory["directory_count"], 2)
            self.assertEqual(inventory["cpk_signature_count"], 2)
            self.assertEqual(files["DATA/ARCHIVE.CPK;1"]["content_type"], "cpk_signature")
            self.assertEqual(files["DATA/ARCHIVE.CPK;1"]["size_bytes"], 6)
            self.assertEqual(
                files["DATA/ARCHIVE.CPK;1"]["extents"][0]["offset_bytes"],
                22 * BLOCK_SIZE,
            )
            self.assertEqual(files["DATA/SPLIT.BIN;1"]["content_type"], "cpk_signature")
            self.assertEqual(files["DATA/SPLIT.BIN;1"]["extent_count"], 2)
            self.assertEqual(files["DATA/SPLIT.BIN;1"]["size_bytes"], 4)
            self.assertEqual(files["DATA/OTHER.BIN;1"]["content_type"], "other_signature")

    def test_inventory_local_inputs_embeds_iso_metadata_without_extracting(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image_path = root / "disc.iso"
            original = _synthetic_iso()
            image_path.write_bytes(original)

            report = inventory_path(root)
            entry = report["entries"][0]

            self.assertEqual(entry["content_type"], "iso9660_pvd_signature")
            self.assertEqual(entry["iso_inventory"]["status"], "indexed")
            self.assertEqual(entry["iso_inventory"]["cpk_signature_count"], 2)
            self.assertEqual(image_path.read_bytes(), original)

    def test_batch_dry_run_reports_nested_iso_candidates_without_staging(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root = root / "mixed input"
            input_root.mkdir()
            image_path = input_root / "base game.iso"
            image_path.write_bytes(_synthetic_iso())
            output_root = root / "staging"

            report = extract_cpk_batch.run_batch(
                input_root, output_root, tool_path=None, execute=False
            )

            self.assertEqual(report["mode"], "dry_run")
            self.assertEqual(report["cpk_candidate_count"], 0)
            self.assertEqual(report["iso_member_cpk_candidate_count"], 2)
            self.assertEqual(
                {candidate["member_path"] for candidate in report["iso_member_cpk_candidates"]},
                {"DATA/ARCHIVE.CPK;1", "DATA/SPLIT.BIN;1"},
            )
            self.assertFalse(output_root.exists())
            self.assertEqual(len(image_path.read_bytes()), 26 * BLOCK_SIZE)

    def test_rejects_inconsistent_both_endian_volume_size(self):
        image = bytearray(_synthetic_iso())
        image[16 * BLOCK_SIZE + 84] ^= 1
        with tempfile.TemporaryDirectory() as temporary_directory:
            image_path = Path(temporary_directory) / "bad-volume.iso"
            image_path.write_bytes(image)

            with self.assertRaisesRegex(Iso9660Error, "Mismatched both-endian volume-space size"):
                inspect_iso9660(image_path)

    def test_rejects_extent_beyond_declared_volume(self):
        image = bytearray(_synthetic_iso())
        # The PVD root record starts at byte 156; its extent LBA begins at +2.
        image[16 * BLOCK_SIZE + 156 + 2 : 16 * BLOCK_SIZE + 156 + 6] = (99).to_bytes(4, "little")
        image[16 * BLOCK_SIZE + 156 + 6 : 16 * BLOCK_SIZE + 156 + 10] = (99).to_bytes(4, "big")
        with tempfile.TemporaryDirectory() as temporary_directory:
            image_path = Path(temporary_directory) / "bad-extent.iso"
            image_path.write_bytes(image)

            with self.assertRaisesRegex(Iso9660Error, "extent extends beyond"):
                inspect_iso9660(image_path)

    def test_inventory_keeps_signature_only_iso_as_unsupported_not_fatal(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image = bytearray(17 * BLOCK_SIZE)
            image[16 * BLOCK_SIZE : 16 * BLOCK_SIZE + 7] = b"\x01CD001\x01"
            image_path = root / "signature-only.iso"
            image_path.write_bytes(image)

            report = inventory_path(image_path)

            self.assertEqual(report["entries"][0]["content_type"], "iso9660_pvd_signature")
            self.assertEqual(report["entries"][0]["iso_inventory"]["status"], "unsupported")
            self.assertIn("terminator", report["entries"][0]["iso_inventory"]["error"])
            self.assertEqual(report["errors"], [])


class Iso9660MutationTests(unittest.TestCase):
    def test_corrupted_images_raise_only_iso_errors(self):
        """A damaged image may be rejected, but the parser must not raise any other exception."""
        base = bytes(_synthetic_iso())
        rng = random.Random(20261009)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "corrupted.iso"
            for _ in range(500):
                data = bytearray(base)
                for _ in range(rng.randint(1, 40)):
                    data[rng.randrange(len(data))] = rng.randrange(256)
                path.write_bytes(bytes(data))
                try:
                    inspect_iso9660(path)
                except (Iso9660Error, OSError):
                    pass


if __name__ == "__main__":
    unittest.main()
