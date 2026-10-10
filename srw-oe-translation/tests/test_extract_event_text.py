import contextlib
import io
import random
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from audit_event_candidates import scan_bin_with_stats  # noqa: E402
from extract_event_text import (  # noqa: E402
    build_export,
    extract_file,
    from_view,
    main,
    read_export,
    select_envelopes,
    to_view,
    to_view_items,
    verify_records,
)

LOCAL_SAMPLE = Path(__file__).resolve().parents[1] / "local" / "eventP01.zip"


def synthetic_bin() -> bytes:
    """A small invented BIN that covers each segment kind (no game data)."""
    return (
        b"EDAT\x00\x00\x00\x00"
        + b"\xff\xff" + "日本語".encode("cp932") + b"\x00\x76\x01" + b"\x00\x00"
        + b"\x10\x20"
        + b"\xff\xff" + "テスト\r\n".encode("cp932") + b"\x00\x00"
        + b"\xff\xff" + b"ABC" + b"\x00\x00"
        + b"\xff\xff\x00\x00"
        + b"\xff\xff\x82\x20\xff\xff" + "あ".encode("cp932") + b"\x01" + b"\x00\x00"
        + b"\xff\xff" + b"AB"
    )


def manifest_for(file_record: dict) -> dict:
    return {"files": [file_record]}


class CodecTests(unittest.TestCase):
    def test_ascii_and_line_breaks_stay_literal(self):
        self.assertEqual(to_view(b"AB\r\nC~ "), "AB\r\nC~ ")

    def test_braces_and_controls_are_tokens(self):
        self.assertEqual(to_view(b"{\x01\x7f"), "{7B}{01}{7F}")
        self.assertEqual(from_view("{7B}{01}{7F}"), b"{\x01\x7f")

    def test_cp932_text_and_halfwidth_katakana_stay_readable(self):
        raw = "日本語ｱｲｳ".encode("cp932")
        self.assertEqual(to_view(raw), "日本語ｱｲｳ")

    def test_private_use_and_nonroundtrip_pairs_become_tokens(self):
        self.assertEqual(to_view(b"\xf0\x40"), "{F040}")
        self.assertEqual(to_view(b"\xa0\xfd\xfe\xff"), "{A0}{FD}{FE}{FF}")
        # 0x8790 decodes to U+2252, which re-encodes to 0x81E0 rather than 0x8790.
        self.assertEqual(to_view(b"\x87\x90"), "{8790}")
        self.assertEqual(to_view(b"\xfa\x40"), "{FA40}")

    def test_invalid_lead_byte_does_not_consume_the_next_byte(self):
        self.assertEqual(to_view(b"\x82A"), "{82}A")
        self.assertEqual(to_view(b"\x82"), "{82}")

    def test_token_reasons_are_reported(self):
        reasons = [item.reason for item in to_view_items(b"\x80\xa0\x82\x20\x87\x90\x01")]
        self.assertEqual(reasons, ["control", "pua", "invalid", "ascii", "nonroundtrip", "control"])

    def test_every_single_byte_and_byte_pair_round_trips(self):
        for value in range(256):
            raw = bytes([value])
            self.assertEqual(from_view(to_view(raw)), raw)
        for first in range(256):
            for second in range(256):
                raw = bytes([first, second])
                self.assertEqual(from_view(to_view(raw)), raw, msg=raw.hex())

    def test_views_never_leak_raw_controls_or_private_use_characters(self):
        import unicodedata

        for first in range(256):
            for second in range(256):
                for char in to_view(bytes([first, second])):
                    if char in "\r\n":
                        continue
                    self.assertNotIn(unicodedata.category(char), {"Cc", "Co", "Cs", "Cn"})

    def test_random_sequences_round_trip(self):
        rng = random.Random(1234)
        pool = [0x00, 0x0A, 0x0D, 0x7B, 0x7D, 0x81, 0x82, 0x9F, 0xA0, 0xDF, 0xE0, 0xFC, 0xFD, 0xFF, 0x40, 0x7E]
        for _ in range(3000):
            raw = bytes(
                rng.choice(pool) if rng.random() < 0.6 else rng.randrange(256)
                for _ in range(rng.randint(0, 40))
            )
            self.assertEqual(from_view(to_view(raw)), raw, msg=raw.hex())

    def test_from_view_rejects_malformed_or_unescaped_input(self):
        # Characters outside CP932, raw controls, private use, and malformed tokens.
        for bad in ["{ZZ}", "{7}", "{7B", "{123}", "\x01", "\ue000", "\u00e9", "\U00020000"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                from_view(bad)


class EnvelopeTests(unittest.TestCase):
    def test_walk_matches_candidate_scanner_on_synthetic_bin(self):
        data = synthetic_bin()
        envelopes, tail = select_envelopes(data)
        candidates, stats = scan_bin_with_stats("SYN01.bin", data)
        self.assertEqual(len(envelopes), stats["spans_with_double_nul"])
        self.assertEqual(stats["consumed_ff_ff_markers"], len(envelopes) + (tail is not None))
        # Five selected envelopes (one is empty); the nested FF FF inside the
        # fifth is not a separate envelope.
        self.assertEqual([env.marker_offset for env in envelopes], [8, 23, 35, 42, 46])
        self.assertEqual(tail, len(data) - len(b"\xff\xffAB"))
        self.assertEqual(
            [candidate.start for candidate in candidates],
            [env.start_offset for env in envelopes if env.marker_offset in (8, 23, 46)],
        )


class ExtractFileTests(unittest.TestCase):
    def test_partitions_every_byte_and_exports_stable_units(self):
        data = synthetic_bin()
        file_record, segments, units = extract_file("SYN01.bin", data)

        self.assertEqual(
            [segment["kind"] for segment in segments],
            ["gap", "text_unit", "gap", "text_unit", "marker_span", "marker_span", "text_unit", "unterminated_tail"],
        )
        self.assertEqual(
            [unit["unit_id"] for unit in units],
            ["SYN01.bin@000A", "SYN01.bin@0019", "SYN01.bin@0030"],
        )
        self.assertEqual(file_record["size"], len(data))
        self.assertEqual(verify_records(manifest_for(file_record), units, segments), [])

        first, second, third = units
        self.assertEqual(first["source_text"], "日本語")
        self.assertEqual(first["suffix_raw_hex"], "00 76 01")
        self.assertEqual(first["suffix_view"], "{00}{76}{01}")
        self.assertEqual(first["flags"], ["single_nul_suffix"])
        self.assertEqual(first["tokens"], [])

        self.assertEqual(second["source_text"], "テスト\r\n")
        self.assertIsNone(second["suffix_raw_hex"])
        self.assertEqual(
            [(line["at"], line["offset"], line["raw_hex"]) for line in second["line_breaks"]],
            [(3, 31, "0D"), (4, 32, "0A")],
        )

        self.assertEqual(third["source_text"], "{82} {FF}{FF}あ{01}")
        self.assertEqual(
            [(token["at"], token["offset"], token["reason"]) for token in third["tokens"]],
            [(0, 48, "invalid"), (5, 50, "pua"), (9, 51, "pua"), (14, 54, "control")],
        )
        self.assertEqual(
            third["flags"],
            ["nested_ff_ff_marker", "single_japanese_codepoint", "invalid_cp932_token", "pua_token", "control_token"],
        )

    def test_unit_ids_and_raw_bytes_agree_with_the_candidate_scanner(self):
        data = synthetic_bin()
        _, _, units = extract_file("SYN01.bin", data)
        candidates, _ = scan_bin_with_stats("SYN01.bin", data)
        self.assertEqual(
            [unit["unit_id"] for unit in units],
            [f"SYN01.bin@{candidate.start:04X}" for candidate in candidates],
        )
        for unit, candidate in zip(units, candidates):
            self.assertEqual(bytes.fromhex(unit["prefix_raw_hex"]), candidate.text_bytes)
            self.assertEqual(unit["pair_offset"], candidate.pair_offset)

    def test_unterminated_tail_is_preserved_as_opaque_bytes(self):
        data = b"\x00\x01" + b"\xff\xff" + "日本".encode("cp932")
        file_record, segments, units = extract_file("TAIL.bin", data)
        self.assertEqual(units, [])
        self.assertEqual([segment["kind"] for segment in segments], ["gap", "unterminated_tail"])
        self.assertEqual(verify_records(manifest_for(file_record), units, segments), [])

    def test_empty_file_has_no_segments(self):
        file_record, segments, units = extract_file("EMPTY.bin", b"")
        self.assertEqual((segments, units), ([], []))
        self.assertEqual(verify_records(manifest_for(file_record), units, segments), [])

    def test_random_inputs_partition_and_match_the_candidate_walk(self):
        rng = random.Random(20261009)
        pool = [b"\xff", b"\xff\xff", b"\x00", b"\x00\x00", b"\x82", b"\xa0", b"A", b"\x76", b"\x01",
                b"\x81\x40", b"\x88\x9f", b" ", b"\n", b"\r", b"{"]
        for _ in range(300):
            data = b"".join(rng.choice(pool) for _ in range(rng.randint(0, 60)))
            with self.subTest(data=data.hex()):
                file_record, segments, units = extract_file("RND.bin", data)
                self.assertEqual(verify_records(manifest_for(file_record), units, segments), [])
                candidates, _ = scan_bin_with_stats("RND.bin", data)
                self.assertEqual(len(units), len(candidates))


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.data = synthetic_bin()
        self.file_record, self.segments, self.units = extract_file("SYN01.bin", self.data)
        self.manifest = manifest_for(self.file_record)

    def test_detects_altered_unit_text(self):
        units = [dict(unit) for unit in self.units]
        units[0]["source_text"] = "日本"
        self.assertTrue(verify_records(self.manifest, units, self.segments))

    def test_detects_altered_segment_bytes(self):
        segments = [dict(segment) for segment in self.segments]
        segments[0]["raw_hex"] = "45 44 41 54 00 00 00 01"
        self.assertTrue(verify_records(self.manifest, self.units, segments))

    def test_detects_missing_segment(self):
        self.assertTrue(verify_records(self.manifest, self.units, self.segments[1:]))

    def test_malformed_record_is_reported_not_raised(self):
        segments = [dict(segment) for segment in self.segments]
        segments[0]["raw_hex"] = "ZZ"
        errors = verify_records(self.manifest, self.units, segments)
        self.assertTrue(any("malformed export record" in error for error in errors), msg=errors)

    def test_detects_manifest_count_mismatch(self):
        manifest = {"files": [dict(self.file_record, units=99)]}
        self.assertTrue(verify_records(manifest, self.units, self.segments))


class ExportTests(unittest.TestCase):
    def _make_zip(self, directory: Path) -> Path:
        archive = directory / "sample.zip"
        with zipfile.ZipFile(archive, "w") as handle:
            handle.writestr("SYN01.bin", synthetic_bin())
        return archive

    def test_export_round_trips_and_verifies_from_disk(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            archive = self._make_zip(temp_path)
            export_dir = temp_path / "export"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(archive), "--export-dir", str(export_dir)])

            self.assertEqual(code, 0)
            printed = output.getvalue()
            self.assertNotIn("日本語", printed)
            self.assertNotIn("テスト", printed)
            self.assertIn("Verification passed (in-memory records)", printed)
            self.assertIn("Verification passed (exported files read back)", printed)
            for name in ("manifest.json", "units.jsonl", "segments.jsonl"):
                self.assertTrue((export_dir / name).is_file())

            manifest, units, segments = read_export(export_dir)
            self.assertEqual(manifest["totals"]["units"], 3)
            self.assertEqual(manifest["input"]["kind"], "zip")
            self.assertEqual(verify_records(manifest, units, segments), [])

    def test_repeated_exports_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            archive = self._make_zip(temp_path)
            for run in ("first", "second"):
                with contextlib.redirect_stdout(io.StringIO()):
                    main([str(archive), "--export-dir", str(temp_path / run)])
            for name in ("manifest.json", "units.jsonl", "segments.jsonl"):
                self.assertEqual(
                    (temp_path / "first" / name).read_bytes(),
                    (temp_path / "second" / name).read_bytes(),
                )

    def test_export_inside_input_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            input_dir = Path(temp) / "input"
            input_dir.mkdir()
            (input_dir / "SYN01.bin").write_bytes(synthetic_bin())
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main([str(input_dir), "--export-dir", str(input_dir / "out")])
            self.assertEqual(raised.exception.code, 2)

    def test_single_bin_input_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            bin_path = temp_path / "SYN01.bin"
            bin_path.write_bytes(synthetic_bin())
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([str(bin_path)])
            self.assertEqual(code, 0)


@unittest.skipUnless(LOCAL_SAMPLE.is_file(), "local/eventP01.zip is not present in this checkout")
class LocalSampleRegressionTests(unittest.TestCase):
    def test_restored_sample_matches_documented_counts(self):
        manifest, units, segments = build_export(LOCAL_SAMPLE)
        self.assertEqual(manifest["totals"]["files"], 22)
        self.assertEqual(manifest["totals"]["bytes"], 333732)
        self.assertEqual(manifest["totals"]["units"], 3277)
        self.assertEqual(manifest["totals"]["segments"], 6826)
        self.assertEqual(verify_records(manifest, units, segments), [])


if __name__ == "__main__":
    unittest.main()
