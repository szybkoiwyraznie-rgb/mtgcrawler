"""Synthetic tests for the read-only boundary-evidence probe (tools/boundary_probe.py).

The fixtures build small event-like BIN files with a known layout (a length field before the
marker, a pointer table, fixed gaps, short suffixes), so each measurement can be checked against
the structure that produced it. No game file is used and no text is decoded.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import boundary_probe  # noqa: E402

NAME = "ev01.bin"
TEXTS = [
    "日本語のテキストです".encode("cp932"),
    "別の行です".encode("cp932"),
    "三番目の行です".encode("cp932"),
    "四番目".encode("cp932"),
]


def synthetic_bin(
    texts: list[bytes],
    *,
    pad: int = 16,
    suffixes: list[bytes] | None = None,
    pointer_table: bool = False,
) -> bytes:
    """One unit per text: pad, u16 LE text length, 2 pad bytes, FF FF, text, [suffix], 00 00."""
    body = bytearray()
    starts: list[int] = []
    for index, text in enumerate(texts):
        body += bytes(pad)
        starts.append(len(body) + 6)  # the text start: header (4) + marker (2)
        body += int(len(text)).to_bytes(2, "little")
        body += b"\x00\x00"
        body += b"\xff\xff"
        body += text
        if suffixes:
            body += suffixes[index]
        body += b"\x00\x00"
    if pointer_table:
        table = b"".join(start.to_bytes(4, "little") for start in starts)
        assert len(table) <= pad, "the fixture writes the table over the leading pad bytes"
        body[: len(table)] = table
    return bytes(body)


def marker_offsets(data: bytes) -> list[int]:
    offsets = []
    index = data.find(b"\xff\xff")
    while index >= 0:
        offsets.append(index)
        index = data.find(b"\xff\xff", index + 2)
    return offsets


def build_units(data: bytes) -> list[dict]:
    """Unit records in the exporter's shape, read back from the fixture's bytes."""
    units = []
    for marker in marker_offsets(data):
        start = marker + 2
        pair = data.index(b"\x00\x00", start)
        body = data[start:pair]
        first_nul = body.find(b"\x00")
        prefix = body if first_nul < 0 else body[:first_nul]
        suffix = b"" if first_nul < 0 else body[first_nul:]
        units.append(
            {
                "unit_id": f"{NAME}@{marker:08X}",
                "file": NAME,
                "source_text": prefix.decode("cp932"),
                "marker_offset": marker,
                "start_offset": start,
                "text_end_offset": start + len(prefix),
                "pair_offset": pair,
                "prefix_raw_hex": prefix.hex(),
                "suffix_raw_hex": suffix.hex() or None,
                "tokens": [],
                "flags": [],
            }
        )
    return units


def probe(units: list[dict], files: dict[str, bytes]) -> dict:
    acc = boundary_probe.Evidence()
    boundary_probe.add_units(acc, "pkg", units, files)
    result = boundary_probe.summarize(acc)
    result["status"] = "ok" if acc.units else "no_units"
    return result


class LengthPrefixTest(unittest.TestCase):
    def test_finds_the_length_field_and_beats_its_control(self):
        data = synthetic_bin(TEXTS)
        result = probe(build_units(data), {NAME: data})
        self.assertEqual(result["totals"]["units"], len(TEXTS))
        best = result["length_prefix"]["best"][0]
        # A u32 LE at marker-4 covers the u16 length plus the two pad bytes of the fixture.
        self.assertEqual((best["delta"], best["width"], best["endian"]), (4, 4, "le"))
        self.assertEqual(best["by_target"], {"prefix": len(TEXTS)})
        self.assertEqual(best["rate"], 1.0)
        self.assertLess(best["expected_rate"], best["rate"])
        # The null is conservative on four units (its own field values feed the value pool).
        self.assertGreater(best["lift"], 0.5)
        self.assertGreater(best["ratio"], 2)
        field = next(
            row
            for row in result["length_prefix"]["rows"]
            if (row["delta"], row["width"], row["endian"]) == (4, 2, "le")
        )
        self.assertEqual(field["hits"], len(TEXTS))
        self.assertEqual(field["by_target"], {"prefix": len(TEXTS)})
        self.assertLess(field["expected_rate"], field["rate"])
        # Every configuration is reported with its null, not only the winner.
        self.assertEqual(len(result["length_prefix"]["rows"]), len(boundary_probe.LENGTH_DELTAS) * 3 * 2)
        for row in result["length_prefix"]["rows"]:
            self.assertLessEqual(row["hits"], row["eligible"])
            self.assertGreaterEqual(row["expected_hits"], 0.0)

    def test_the_null_absorbs_chance_hits_in_unstructured_bytes(self):
        # Text units separated by pseudo-random bytes: no length field exists, so the observed hit
        # rate must stay at the expectation instead of showing a lift.
        import random

        rng = random.Random(11)
        units = []
        parts = []
        position = 0
        for index in range(400):
            gap = bytes(rng.getrandbits(8) for _ in range(24))
            parts.append(gap)
            position += len(gap)
            text = "文章%dです" .format(index).encode("cp932")
            parts.append(b"\xff\xff")
            marker = position
            position += 2
            parts.append(text)
            position += len(text)
            parts.append(b"\x00\x00")
            pair = position
            position += 2
            units.append(
                {
                    "unit_id": f"{NAME}@{marker:08X}",
                    "file": NAME,
                    "marker_offset": marker,
                    "start_offset": marker + 2,
                    "text_end_offset": pair,
                    "pair_offset": pair,
                    "prefix_raw_hex": text.hex(),
                    "suffix_raw_hex": None,
                }
            )
        data = b"".join(parts)
        result = probe(units, {NAME: data})
        self.assertEqual(result["totals"]["units"], len(units))
        rows = result["length_prefix"]["rows"]
        self.assertGreater(sum(row["hits"] for row in rows), 0, "the scan should still find chance hits")
        self.assertLess(max(row["lift"] for row in rows), 0.05)
        self.assertTrue(any("no 1/2/4-byte field" in line for line in boundary_probe.report_lines(result)))

    def test_pointer_table_lifts_the_start_offsets(self):
        with_table = synthetic_bin(TEXTS, pointer_table=True)
        without = synthetic_bin(TEXTS)
        lifted = probe(build_units(with_table), {NAME: with_table})
        plain = probe(build_units(without), {NAME: without})

        def row_for(result, measure, width, endian="le"):
            return next(
                row
                for row in result["pointer_references"]["rows"]
                if row["measure"] == measure and row["width"] == width and row["endian"] == endian
            )

        # The fixture's table stores text-start offsets (marker + 2) as u32 LE, 4-aligned.
        table_le = row_for(lifted, "occurrences", 4)
        plain_le = row_for(plain, "occurrences", 4)
        self.assertGreaterEqual(table_le["counts"]["start"], len(TEXTS))
        self.assertGreater(table_le["counts"]["start"], plain_le["counts"]["start"])
        self.assertEqual(table_le["targets"], table_le["counts"]["marker"] + table_le["counts"]["start"])
        self.assertLess(table_le["controls"], table_le["counts"]["start"])
        aligned = row_for(lifted, "occurrences_aligned", 4)
        self.assertGreaterEqual(aligned["counts"]["start"], len(TEXTS))
        # Matches are localized by eighth of the file: the table sits at the very start.
        positions = next(
            row
            for row in lifted["pointer_references"]["positions"]
            if row["width"] == 4 and row["endian"] == "le" and row["kind"] == "start"
        )
        self.assertEqual(sum(positions["by_eighth"].values()), table_le["counts"]["start"])
        self.assertGreater(positions["by_eighth"][0], 0)

    def test_u16_offsets_are_found_by_the_aligned_scan(self):
        # u16 is measured by the aligned scan only: a per-value search over the whole file costs too
        # much for a width whose offsets mostly do not fit their own file (see POINTER_UNALIGNED_WIDTHS)
        data = bytearray(synthetic_bin(TEXTS, pad=16))
        units = build_units(bytes(data))
        self.assertTrue(all(unit["start_offset"] % 2 == 0 for unit in units))
        table = b"".join(unit["start_offset"].to_bytes(2, "little") for unit in units)
        data[: len(table)] = table
        result = probe(units, {NAME: bytes(data)})
        row = next(
            row
            for row in result["pointer_references"]["rows"]
            if row["measure"] == "occurrences_aligned" and row["width"] == 2 and row["endian"] == "le"
        )
        self.assertGreaterEqual(row["counts"]["start"], len(TEXTS))

    def test_repeated_payloads_are_counted_not_printed(self):
        data = synthetic_bin([TEXTS[0], TEXTS[0], TEXTS[1]])
        result = probe(build_units(data), {NAME: data})
        repeats = result["repetition"]
        self.assertEqual(repeats["distinct_payloads"], 2)
        self.assertEqual(repeats["payloads_repeated"], 1)
        self.assertEqual(repeats["units_with_repeated_payload"], 2)
        self.assertEqual(repeats["max_multiplicity"], 2)
        self.assertEqual(repeats["repeated_units_at_least_8_bytes"], 2)
        self.assertEqual(repeats["repeated_payload_len_min"], len(TEXTS[0]))
        self.assertEqual(repeats["repeated_payload_len_max"], len(TEXTS[0]))


class ContextTest(unittest.TestCase):
    def test_suffix_profile_separates_structure_from_data(self):
        suffixes = [b"\x00\x11\x21", b"\x00\x22\x22", b"\x00\x11\x23", b"\x00\x22\x24"]
        data = synthetic_bin(TEXTS, suffixes=suffixes)
        result = probe(build_units(data), {NAME: data})
        self.assertEqual(result["totals"]["units"], len(TEXTS))
        self.assertEqual(result["totals"]["units_with_suffix"], len(TEXTS))
        self.assertEqual([row["key"] for row in result["suffix_lengths"]], [3])
        profile = result["suffix_profile"][0]
        self.assertEqual(profile["suffix_len"], 3)
        self.assertEqual([position["units"] for position in profile["positions"]], [4, 4, 4])
        self.assertEqual(profile["positions"][0]["distinct_values"], 1)
        self.assertEqual(profile["positions"][0]["top_value"], "00")
        self.assertEqual(profile["positions"][1]["distinct_values"], 2)
        self.assertEqual(profile["positions"][2]["distinct_values"], 4)
        self.assertEqual(len(result["suffix_patterns"]), 4)

    def test_gap_and_pitch_counts_follow_the_layout(self):
        data = synthetic_bin(TEXTS)
        result = probe(build_units(data), {NAME: data})
        gaps = result["gaps_between_units"]
        # 16 pad bytes plus the next unit's 4-byte length header.
        self.assertEqual(gaps["min"], 20)
        self.assertEqual(gaps["median"], 20)
        self.assertEqual(gaps["max"], 20)
        self.assertEqual(gaps["gaps_above_exact_max"], 0)
        self.assertEqual(gaps["multiple_of_4"], {"0": len(TEXTS) - 1})
        self.assertEqual(sum(row["count"] for row in result["pitch_between_starts"]), len(TEXTS) - 1)
        self.assertEqual(
            sum(sum(counts.values()) for counts in result["start_alignment"].values()),
            len(TEXTS) * 3,
        )

    def test_post_and_pre_marker_patterns_are_reported_as_hex(self):
        data = synthetic_bin(TEXTS)
        result = probe(build_units(data), {NAME: data})
        self.assertTrue(all(row["key"].startswith("0000") for row in result["post_text_patterns"]))
        self.assertEqual(sum(row["count"] for row in result["post_text_patterns"]), len(TEXTS))
        self.assertEqual(sum(row["count"] for row in result["pre_marker_patterns"]), len(TEXTS))


class IntegrityTest(unittest.TestCase):
    def test_mismatched_records_are_counted_not_measured(self):
        data = synthetic_bin(TEXTS)
        units = build_units(data)
        broken_marker = dict(units[0], marker_offset=units[0]["marker_offset"] + 1)
        broken_prefix = dict(units[1], prefix_raw_hex="00" * (units[1]["text_end_offset"] - units[1]["start_offset"]))
        missing = dict(units[2], file="absent.bin")
        result = probe([broken_marker, broken_prefix, missing, units[3]], {NAME: data})
        self.assertEqual(result["totals"]["marker_mismatches"], 1)
        self.assertEqual(result["totals"]["offset_problems"], 0)
        self.assertEqual(result["totals"]["prefix_mismatches"], 1)
        self.assertEqual(result["totals"]["missing_files"], 1)
        self.assertEqual(result["totals"]["units"], 1)

    def test_report_lines_say_when_no_length_field_beats_its_control(self):
        data = bytearray(synthetic_bin(TEXTS))
        for marker in marker_offsets(bytes(data)):
            data[marker - 4 : marker - 2] = b"\x00\x00"  # blank the fixture's length fields
        result = probe(build_units(bytes(data)), {NAME: bytes(data)})
        self.assertEqual(result["totals"]["units"], len(TEXTS))
        lines = boundary_probe.report_lines(result)
        self.assertTrue(any("no 1/2/4-byte field" in line for line in lines), lines)
        self.assertTrue(any("pointer scan: no unit offset occurs" in line for line in lines), lines)
        self.assertTrue(all(row["hits"] == 0 for row in result["length_prefix"]["rows"]))

    def test_empty_input_reports_no_units(self):
        result = probe([], {})
        self.assertEqual(result["status"], "no_units")
        self.assertEqual(result["totals"]["units"], 0)
        self.assertEqual(result["length_prefix"]["best"], [])
        self.assertTrue(boundary_probe.report_lines(result)[0].startswith("  boundary probe:"))


class OutputTest(unittest.TestCase):
    def test_probe_is_deterministic_and_holds_no_decoded_text(self):
        data = synthetic_bin(TEXTS)
        units = build_units(data)
        first = json.dumps(probe(units, {NAME: data}), sort_keys=True, ensure_ascii=False)
        second = json.dumps(probe(units, {NAME: data}), sort_keys=True, ensure_ascii=False)
        self.assertEqual(first, second)
        self.assertTrue(first.isascii(), "the probe output must not contain decoded text")
        for unit in units:
            self.assertNotIn(unit["source_text"], first)
            self.assertNotIn(unit["prefix_raw_hex"], first)
        for line in boundary_probe.report_lines(probe(units, {NAME: data})):
            self.assertTrue(line.isascii())

    def test_merged_evidence_matches_one_pass_over_everything(self):
        data_a = synthetic_bin(TEXTS)
        data_b = synthetic_bin(list(reversed(TEXTS)))
        combined = boundary_probe.Evidence()
        boundary_probe.add_units(combined, "a", build_units(data_a), {NAME: data_a})
        boundary_probe.add_units(combined, "b", build_units(data_b), {NAME: data_b})
        separate = boundary_probe.Evidence()
        boundary_probe.add_units(separate, "a", build_units(data_a), {NAME: data_a})
        other = boundary_probe.Evidence()
        boundary_probe.add_units(other, "b", build_units(data_b), {NAME: data_b})
        separate.merge(other)

        def measured(acc):
            summary = boundary_probe.summarize(acc)
            summary["pointer_references"].pop("budgets")  # the leftover budget depends on the pass order
            return json.dumps(summary, sort_keys=True)

        self.assertEqual(measured(combined), measured(separate))
        self.assertEqual(boundary_probe.summarize(combined)["totals"]["packages"], 2)


class NestingAndCoverageTest(unittest.TestCase):
    def test_inner_marker_followed_by_japanese_is_counted(self):
        inner = "内側の文章".encode("cp932")
        outer = "外側".encode("cp932")
        body = bytearray()
        body += bytes(16)
        marker = len(body)
        body += b"\xff\xff" + outer + b"\xff\xff" + inner + b"\x00\x00"
        data = bytes(body)
        pair = len(data) - 2
        units = [
            {
                "unit_id": f"{NAME}@{marker:08X}",
                "file": NAME,
                "marker_offset": marker,
                "start_offset": marker + 2,
                "text_end_offset": pair,
                "pair_offset": pair,
                "prefix_raw_hex": data[marker + 2 : pair].hex(),
                "suffix_raw_hex": None,
            }
        ]
        result = probe(units, {NAME: data})
        nested = result["nested_markers"]
        self.assertEqual(nested["units_with_inner_marker"], 1)
        self.assertEqual(nested["inner_markers"], 1)
        self.assertEqual(nested["inner_markers_wide_script"], 1)
        self.assertEqual(nested["inner_markers_ascii_only"], 0)
        self.assertTrue(any("nested FF FF inside a unit: 1 units" in line for line in boundary_probe.report_lines(result)))

    def test_manifest_totals_are_summed_into_the_coverage_section(self):
        data = synthetic_bin(TEXTS)
        units = build_units(data)
        acc = boundary_probe.Evidence()
        boundary_probe.add_units(acc, "p001", units, {NAME: data}, source="eventP01.EDAT")
        boundary_probe.add_manifest(
            acc,
            {
                "totals": {
                    "files": 1,
                    "units": len(units),
                    "bytes_by_kind": {"gap": 60, "text_unit": 100, "unterminated_tail": 7},
                    "unit_flags": {"nested_ff_ff_marker": 2, "single_nul_suffix": 1},
                    "tokens_by_reason": {"control_token": 3, "pua_token": 1},
                }
            }
        )
        coverage = boundary_probe.summarize(acc)["text_coverage"]
        self.assertEqual(coverage["exports_read"], 1)
        self.assertEqual(coverage["bytes_total"], 167)
        self.assertEqual(coverage["bytes_by_kind"]["text_unit"], 100)
        self.assertEqual(coverage["exports_with_unterminated_tail"], 1)
        self.assertEqual(coverage["unit_flags"]["nested_ff_ff_marker"], 2)
        self.assertEqual(coverage["tokens_by_reason"]["control_token"], 3)


class CompanionTest(unittest.TestCase):
    def test_dat_run_found_in_a_bin_is_counted_by_class(self):
        payload = b"\x82\xa0\x82\xa2\x82\xa4\x82\xa6"  # eight bytes, no NUL inside
        ext = b"\x00\x00" + payload + b"\x00" + b"\x01\x02" + b"\x00"  # one long run, one too short
        entry = b"\x00" + b"\xaa" * 8 + b"\x00"
        acc = boundary_probe.Evidence()
        boundary_probe.add_companions(
            acc, {"SM001_ext.dat": ext, "SM001_Entry.dat": entry}, {"DL102_20.bin": b"junk" + payload + b"junk"}
        )
        cross = boundary_probe.summarize(acc)["companion_dat_cross_check"]
        self.assertEqual(cross["files"], {"entry": 1, "ext": 1})
        self.assertEqual(cross["runs_searched"], {"entry": 1, "ext": 1})
        self.assertEqual(cross["runs_found_in_bins"], {"ext": 1})
        self.assertEqual(cross["occurrences"], {"ext": 1})
        self.assertEqual(cross["distinct_payloads_found"], 1)
        self.assertEqual(cross["payload_len_min"], len(payload))
        self.assertEqual(cross["payload_len_max"], len(payload))
        lines = boundary_probe.report_lines(
            {**boundary_probe.summarize(acc), "status": "ok", "totals": {"units": 0, "files": 0, "packages": 0,
             "offset_problems": 0, "marker_mismatches": 0, "prefix_mismatches": 0, "missing_files": 0}}
        )
        self.assertTrue(any("found in a BIN: ext 1" in line for line in lines), lines)

    def test_runs_are_capped_per_package(self):
        dat = b"\x00" + b"\x00".join(b"\xaa" * 8 for _ in range(boundary_probe.COMPANION_RUNS_PER_PACKAGE + 5))
        acc = boundary_probe.Evidence()
        boundary_probe.add_companions(acc, {"a_ext.dat": dat}, {"a.bin": b"\x00" * 16})
        cross = boundary_probe.summarize(acc)["companion_dat_cross_check"]
        self.assertEqual(cross["runs_searched"]["ext"], boundary_probe.COMPANION_RUNS_PER_PACKAGE)
        self.assertEqual(cross["packages_capped_at_run_limit"], 1)


class RunFolderDiscoveryTest(unittest.TestCase):
    """RUN_PROBE.bat has to find the run folder the pipeline wrote, without being told where it is."""

    def _output_with_runs(self, root: Path) -> Path:
        out = root / "out"
        for name in ("20261009-222046", "20261010-142640"):
            (out / name).mkdir(parents=True)
            (out / name / "registry.json").write_text("{}", encoding="utf-8")
        (out / "not-a-run").mkdir()
        return out

    def test_the_config_key_the_pipeline_writes_is_the_one_the_probe_reads(self):
        import run_pipeline  # the writer RUN_PIPELINE.bat uses; the two must not drift apart

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self._output_with_runs(root)
            config = root / "local-workflow.ini"
            run_pipeline.save_settings(
                config,
                run_pipeline.Settings(
                    input_root=root / "in", output_base=out, tool_path=None, expected_tool_sha256=None
                ),
            )
            self.assertIn("output_root =", config.read_text(encoding="utf-8"))
            found, why = boundary_probe.find_latest_run_folder(config)
            self.assertEqual(found, (out / "20261010-142640").resolve())
            self.assertIn("output_root", why)

    def test_a_relative_output_root_resolves_from_the_config_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self._output_with_runs(root)
            config = root / "local-workflow.ini"
            config.write_text("[local]\noutput_root = out\n", encoding="utf-8")
            self.assertEqual(boundary_probe.latest_run_folder(config), (out / "20261010-142640").resolve())

    def test_a_missing_or_incomplete_config_says_what_it_looked_for(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing, why = boundary_probe.find_latest_run_folder(root / "nope.ini")
            self.assertIsNone(missing)
            self.assertIn("no config file", why)
            empty = root / "empty.ini"
            empty.write_text("[local]\ninput_root = C:/games\n", encoding="utf-8")
            missing, why = boundary_probe.find_latest_run_folder(empty)
            self.assertIsNone(missing)
            self.assertIn("no output_root", why)
            out = self._output_with_runs(root)
            (out / "20261010-142640" / "registry.json").unlink()
            (out / "20261009-222046" / "registry.json").unlink()
            bare = root / "bare.ini"
            bare.write_text(f"[local]\noutput_root = {out}\n", encoding="utf-8")
            missing, why = boundary_probe.find_latest_run_folder(bare)
            self.assertIsNone(missing)
            self.assertIn("no subfolder", why)

    def test_a_run_folder_or_its_parent_can_both_be_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self._output_with_runs(root)
            run = out / "20261010-142640"
            self.assertEqual(boundary_probe.resolve_run_dir(run)[0], run.resolve())
            self.assertEqual(boundary_probe.resolve_run_dir(out)[0], run.resolve())
            self.assertIn("newest run folder", boundary_probe.resolve_run_dir(out)[1])
            self.assertIn("not a folder", boundary_probe.resolve_run_dir(root / "nope")[1])
            empty = root / "empty"
            empty.mkdir()
            self.assertIn("no registry.json", boundary_probe.resolve_run_dir(empty)[1])

    def test_the_command_line_says_why_it_found_nothing(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = boundary_probe.main(["--out", str(root / "b.json"), str(root / "missing")])
            self.assertEqual(code, 2)
            message = err.getvalue()
            self.assertIn("is not a folder", message)
            self.assertIn("drag it onto RUN_PROBE.bat", message)


class CohortTest(unittest.TestCase):
    """The probe must not pool the event script with the binary data that surrounds it."""

    KANA = ["ｱｲｳ", "ｴｵｶ", "ｷｸｹ"]  # half-width katakana: no wide-script codepoints

    def _run_folder(self, root: Path) -> dict:
        registry_packages = []
        for package_id, texts, flags, source in (
            ("p001", TEXTS, {}, "NPJH50521/eventP01.EDAT"),
            ("p002", [kana.encode("cp932") for kana in self.KANA],
             {"halfwidth_katakana_only_match": len(self.KANA)}, "NPJH50521/bacb01.EDAT"),
        ):
            package_dir = root / "packages" / package_id
            package_dir.mkdir(parents=True)
            data = synthetic_bin(list(texts))
            (package_dir / NAME).write_bytes(data)
            export = root / "text" / package_id
            export.mkdir(parents=True)
            units = build_units(data)
            (export / "units.jsonl").write_text(
                "".join(json.dumps(unit, ensure_ascii=False) + "\n" for unit in units), encoding="utf-8"
            )
            (export / "manifest.json").write_text(
                json.dumps(
                    {
                        "totals": {
                            "files": 1,
                            "units": len(units),
                            "bytes": len(data),
                            "bytes_by_kind": {"text_unit": len(data), "gap": 0},
                            "unit_flags": flags,
                            "tokens_by_reason": {},
                        }
                    }
                ),
                encoding="utf-8",
            )
            registry_packages.append(
                {
                    "package_id": package_id,
                    "output_dir": f"packages/{package_id}",
                    "text": {"export_dir": f"text/{package_id}"},
                    "source_path": source,
                }
            )
        registry = {"packages": registry_packages}
        (root / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
        return registry

    def test_exports_are_split_into_text_and_binary_cohorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            result = boundary_probe.probe_packages(registry["packages"], root)
        self.assertEqual(result["totals"]["units"], len(TEXTS) + len(self.KANA))
        self.assertEqual(result["cohorts"]["text"]["totals"]["units"], len(TEXTS))
        self.assertEqual(result["cohorts"]["binary"]["totals"]["units"], len(self.KANA))
        self.assertEqual(result["cohorts"]["text"]["text_share"], 1.0)
        self.assertEqual(result["cohorts"]["binary"]["text_share"], 0.0)
        # each cohort carries its own manifest coverage, not the pooled one
        self.assertEqual(result["cohorts"]["text"]["text_coverage"]["exports_read"], 1)
        self.assertEqual(result["cohorts"]["binary"]["text_coverage"]["exports_read"], 1)
        self.assertEqual(result["cohorts"]["text"]["totals"]["files"], 1)

    def test_every_export_is_ranked_with_its_own_text_share(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            result = boundary_probe.probe_packages(registry["packages"], root)
        rows = {row["export"]: row for row in result["per_export"]}
        self.assertEqual(set(rows), {"p001", "p002"})
        self.assertEqual(rows["p001"]["text_share"], 1.0)
        self.assertEqual(rows["p001"]["source"], "NPJH50521/eventP01.EDAT")
        self.assertEqual(rows["p002"]["text_share"], 0.0)
        self.assertEqual(rows["p002"]["units"], len(self.KANA))
        # the fixture stores a u16 length two bytes before the marker; the two pad bytes are zero,
        # so a u32 at marker-4 matches too, and ties go to the widest field
        self.assertEqual(rows["p001"]["best_length_width"], 4)
        self.assertEqual(rows["p001"]["best_length_delta"], 4)

    def test_the_report_names_both_cohorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            result = boundary_probe.probe_packages(registry["packages"], root)
        text = "\n".join(boundary_probe.report_lines(result))
        self.assertIn("by cohort", text)
        self.assertIn("cohort text: 1 exports, 4 units", text)
        self.assertIn("cohort binary: 1 exports, 3 units", text)
        self.assertIn("export p001: 4 units", text)

    def test_the_command_line_prints_the_cohort_section_and_the_json_path(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = boundary_probe.main([str(root)])
            printed = out.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("by cohort", printed)
            self.assertIn("cohort text: 1 exports, 4 units", printed)
            self.assertIn(str(root / boundary_probe.PROBE_NAME), printed)
            written = json.loads((root / boundary_probe.PROBE_NAME).read_text(encoding="utf-8"))
            self.assertEqual(written["schema"], boundary_probe.SCHEMA)
            self.assertIn("cohorts", written)
        self.assertEqual(registry["packages"][0]["package_id"], "p001")

    def test_a_per_record_offset_field_is_localized_at_a_fixed_distance(self):
        # Each record carries its own text offset in a u32 exactly 10 bytes before the text, so
        # every match sits at the same distance from the value it encodes. This is the shape the
        # real text cohort's start-offset matches have to be tested against.
        texts = [text.encode("cp932") for text in ("日本語のテキストです", "別の行です", "三番目の行です", "四番目")]
        starts = []
        position = 0
        for text in texts:
            starts.append(position + 10)  # u32 (4) + filler (4) + FF FF (2)
            position += 10 + len(text) + 2
        body = bytearray()
        for start, text in zip(starts, texts):
            body += start.to_bytes(4, "little") + b"\x00\x00\x00\x00" + b"\xff\xff" + text + b"\x00\x00"
        data = bytes(body)
        units = build_units(data)
        self.assertEqual([unit["start_offset"] for unit in units], starts)
        result = probe(units, {NAME: data})
        row = next(
            row
            for row in result["pointer_references"]["deltas"]
            if row["kind"] == "start" and row["width"] == 4 and row["endian"] == "le"
        )
        self.assertEqual(row["top"][0]["delta"], "-10")
        self.assertEqual(row["top"][0]["count"], len(texts))
        self.assertEqual(row["distinct_deltas"], 1)  # one fixed distance, not a spread
        self.assertIn("target-10 x4", "\n".join(boundary_probe.report_lines(result)))

    @staticmethod
    def _records_with_a_field(values: list[int] | None, texts: list[bytes]) -> tuple[bytes, list[int]]:
        """Records of `u32 field + 4 filler + FF FF + text + 00 00`, so the field is at marker-8."""
        starts = []
        position = 0
        for text in texts:
            starts.append(position + 10)
            position += 10 + len(text) + 2
        body = bytearray()
        for index, (start, text) in enumerate(zip(starts, texts)):
            value = start if values is None else values[index]
            body += value.to_bytes(4, "little") + b"\x00\x00\x00\x00" + b"\xff\xff" + text + b"\x00\x00"
        return bytes(body), starts

    def test_a_self_referential_record_field_is_attributed_to_its_own_record(self):
        texts = [text.encode("cp932") for text in ("日本語のテキストです", "別の行です", "三番目の行です", "四番目")]
        data, starts = self._records_with_a_field(None, texts)
        result = probe(build_units(data), {NAME: data})
        owner = result["pointer_references"]["owner_attribution"]
        self.assertEqual(owner["hits"], len(texts))
        # the field is 8 bytes before its own FF FF, and a record's header belongs to that record,
        # not to the one before it
        self.assertEqual(owner["position_in_record"][0], {"key": "-8", "count": len(texts)})
        # every record stores its own string's offset, so the relation to its own start is 0
        self.assertEqual(owner["stored_value_vs_record_start"][0], {"key": "0", "count": len(texts)})
        lines = "\n".join(boundary_probe.report_lines(result))
        self.assertIn("position marker-8 x4", lines)
        self.assertIn("own start+0 x4", lines)

    def test_a_chain_to_the_next_record_is_attributed_to_the_record_that_holds_it(self):
        # The distance from a match to the value it encodes means nothing for a cross-reference, so
        # the same matches have to be readable by who holds them and what they point at.
        texts = [text.encode("cp932") for text in ("日本語のテキストです", "別の行です", "三番目の行です", "四番目")]
        _data, starts = self._records_with_a_field(None, texts)
        values = [*starts[1:], starts[0]]  # each record stores the next record's start
        data, _ = self._records_with_a_field(values, texts)
        result = probe(build_units(data), {NAME: data})
        owner = result["pointer_references"]["owner_attribution"]
        self.assertEqual(owner["position_in_record"][0], {"key": "-8", "count": len(texts)})
        relations = {row["key"]: row["count"] for row in owner["stored_value_vs_record_start"]}
        pitch = starts[1] - starts[0]
        self.assertNotEqual(starts[2] - starts[1], pitch)  # the fixture's pitches differ, so this is not one bucket
        self.assertEqual(relations[str(pitch)], 1)
        self.assertEqual(relations[str(starts[0] - starts[-1])], 1)  # the wrap-around record

    def test_repeated_references_to_one_offset_are_counted_separately_from_a_line_table(self):
        texts = [text.encode("cp932") for text in ("日本語のテキストです", "別の行です", "三番目の行です", "四番目")]
        _data, starts = self._records_with_a_field(None, texts)
        values = [starts[1]] * len(texts)  # every record points at the same line
        data, _ = self._records_with_a_field(values, texts)
        result = probe(build_units(data), {NAME: data})
        owner = result["pointer_references"]["owner_attribution"]
        self.assertEqual(owner["distinct_values_matched"], 1)
        self.assertEqual(owner["most_matched_value_hits"], len(texts))
        self.assertEqual(owner["values_matched_more_than_once"], 1)
        self.assertIn("cover 1 distinct offsets", "\n".join(boundary_probe.report_lines(result)))

    def test_the_aligned_scan_counts_a_file_once_not_once_per_width_and_endian(self):
        data = synthetic_bin(TEXTS)
        result = probe(build_units(data), {NAME: data})
        coverage = result["pointer_references"]["coverage"]
        self.assertEqual(coverage["aligned_bytes_scanned"], len(data))
        per_pass = [
            row["counts"]["all"]
            for row in result["pointer_references"]["rows"]
            if row["measure"] == "bytes_scanned_aligned"
        ]
        self.assertEqual(len(per_pass), 4)  # u32/u16 x le/be each read the file once
        self.assertEqual(sum(per_pass), 4 * len(data))

    def test_an_unsearched_offset_is_reported_as_truncated_not_as_a_negative(self):
        data = synthetic_bin(TEXTS)
        units = build_units(data)
        original = boundary_probe.POINTER_UNALIGNED_FILE_BUDGET
        boundary_probe.POINTER_UNALIGNED_FILE_BUDGET = 1  # no value fits, so nothing is searched
        try:
            acc = boundary_probe.Evidence()
            boundary_probe.add_units(acc, "pkg", units, {NAME: data})
        finally:
            boundary_probe.POINTER_UNALIGNED_FILE_BUDGET = original
        self.assertEqual(acc.budgets.files_truncated, 1)
        self.assertEqual(acc.pointer_offsets[("available", 4)], len(TEXTS))
        self.assertEqual(acc.pointer_offsets[("searched", 4)], 0)

    def test_pointer_offsets_are_sampled_evenly_and_coverage_is_reported(self):
        self.assertEqual(boundary_probe._sample(list(range(10)), 4), [0, 2, 5, 7])
        self.assertEqual(boundary_probe._sample([1, 2, 3], 10), [1, 2, 3])
        self.assertEqual(boundary_probe._sample([1, 2, 3], 0), [])
        data = synthetic_bin(TEXTS)
        result = probe(build_units(data), {NAME: data})
        coverage = result["pointer_references"]["coverage"]
        self.assertEqual(coverage["offsets_available_unaligned"], {"4": len(TEXTS)})
        self.assertEqual(coverage["offsets_searched_unaligned"], {"4": len(TEXTS)})
        self.assertEqual(coverage["offsets_too_large_for_width"], {"4": 0, "2": 0})
        self.assertEqual(coverage["aligned_files_scanned"], 1)
        self.assertEqual(coverage["aligned_files_skipped_over_budget"], 0)
        lines = "\n".join(boundary_probe.report_lines(result))
        self.assertIn("u32: 4/4 offsets searched unaligned", lines)


class RunFolderTest(unittest.TestCase):
    def _run_folder(self, root: Path) -> dict:
        package_dir = root / "packages" / "p001"
        package_dir.mkdir(parents=True)
        data = synthetic_bin(TEXTS)
        (package_dir / NAME).write_bytes(data)
        export = root / "text" / "p001"
        export.mkdir(parents=True)
        units = build_units(data)
        (export / "units.jsonl").write_text(
            "".join(json.dumps(unit, ensure_ascii=False) + "\n" for unit in units), encoding="utf-8"
        )
        registry = {
            "packages": [
                {"package_id": "p001", "output_dir": "packages/p001", "text": {"export_dir": "text/p001"}}
            ]
        }
        (root / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
        return registry

    def test_probe_packages_reads_the_exports_and_the_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            payload = TEXTS[0]
            (root / "packages" / "p001" / "SM001_ext.dat").write_bytes(b"\x00" + payload + b"\x00")
            result = boundary_probe.probe_packages(registry["packages"], root)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["exports_probed"], 1)
            self.assertEqual(result["totals"]["units"], len(TEXTS))
            self.assertEqual(result["length_prefix"]["best"][0]["delta"], 4)
            cross = result["companion_dat_cross_check"]
            self.assertEqual(cross["files"], {"ext": 1})
            self.assertEqual(cross["runs_found_in_bins"], {"ext": 1})

    def test_probe_run_writes_the_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._run_folder(root)
            result = boundary_probe.build_probe(root)
            path = Path(result["json"])
            self.assertEqual(path.name, boundary_probe.PROBE_NAME)
            self.assertEqual(path.parent, root)
            on_disk = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(on_disk["totals"]["units"], len(TEXTS))
            self.assertIn("scope_note", on_disk)

    def test_hidden_exports_are_probed_from_the_hidden_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            hidden_dir = root / "hidden" / "p001"
            hidden_dir.mkdir(parents=True)
            data = synthetic_bin(TEXTS[:2])
            (hidden_dir / "00001_collide.bin").write_bytes(data)
            units = [dict(unit, file="00001_collide.bin") for unit in build_units(data)]
            export = root / "text" / "p001-hidden"
            export.mkdir(parents=True)
            (export / "units.jsonl").write_text(
                "".join(json.dumps(unit, ensure_ascii=False) + "\n" for unit in units), encoding="utf-8"
            )
            registry["packages"][0]["hidden_entries"] = {"text": {"export_dir": "text/p001-hidden"}}
            result = boundary_probe.probe_packages(registry["packages"], root)
            self.assertEqual(result["exports_probed"], 2)
            self.assertEqual(result["totals"]["units"], len(TEXTS) + 2)
            self.assertEqual(result["totals"]["packages"], 2)

    def test_units_are_grouped_under_the_top_level_source_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            data = synthetic_bin(TEXTS[:2])
            nested_dir = root / "packages" / "p001" / "sub"
            nested_dir.mkdir(parents=True)
            (nested_dir / "inner.bin").write_bytes(data)
            export = root / "text" / "p002"
            export.mkdir(parents=True)
            units = [dict(unit, file="inner.bin") for unit in build_units(data)]
            (export / "units.jsonl").write_text(
                "".join(json.dumps(unit, ensure_ascii=False) + "\n" for unit in units), encoding="utf-8"
            )
            registry["packages"][0]["source_path"] = "eventP01.EDAT"
            registry["packages"].append(
                {
                    "package_id": "p002",
                    "output_dir": "packages/p001/sub",
                    "parent_package": "p001",
                    "source_path": "eventP01.EDAT/sub/inner.cpk",
                    "text": {"export_dir": "text/p002"},
                }
            )
            result = boundary_probe.probe_packages(registry["packages"], root)
            per_source = {row["key"]: row["count"] for row in result["units_per_source"]}
            self.assertEqual(per_source, {"eventP01.EDAT": len(TEXTS) + 2})

    def test_latest_run_folder_uses_the_configured_output_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "out"
            newest = out / "20261010-101010"
            newest.mkdir(parents=True)
            (newest / "registry.json").write_text("{}", encoding="utf-8")
            older = out / "20261009-090909"
            older.mkdir()
            (older / "registry.json").write_text("{}", encoding="utf-8")
            (out / "not-a-run").mkdir()
            config = root / "local-workflow.ini"
            config.write_text(f"[local]\noutput_base = {out}\n", encoding="utf-8")
            self.assertEqual(boundary_probe.latest_run_folder(config), newest)
            self.assertIsNone(boundary_probe.latest_run_folder(root / "missing.ini"))

    def test_missing_source_files_are_reported_as_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self._run_folder(root)
            (root / "packages" / "p001" / NAME).unlink()
            result = boundary_probe.probe_packages(registry["packages"], root)
            self.assertEqual(result["status"], "no_units")
            self.assertEqual(result["totals"]["missing_files"], len(TEXTS))
            self.assertTrue(any(NAME in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
