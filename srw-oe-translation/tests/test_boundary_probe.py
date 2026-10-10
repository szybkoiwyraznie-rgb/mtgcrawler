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

        def occurrences(result, endian="le"):
            return next(
                row
                for row in result["pointer_references"]["rows"]
                if row["measure"] == "occurrences_unaligned" and row["endian"] == endian
            )

        table_le = occurrences(lifted)
        plain_le = occurrences(plain)
        self.assertGreaterEqual(table_le["candidate"], len(TEXTS))
        self.assertGreater(table_le["candidate"], table_le["control"])
        self.assertGreater(table_le["candidate"], plain_le["candidate"])
        # The aligned scan sees the same table.
        aligned = next(
            row
            for row in lifted["pointer_references"]["rows"]
            if row["measure"] == "occurrences_aligned" and row["endian"] == "le"
        )
        self.assertGreaterEqual(aligned["candidate"], len(TEXTS))

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
        self.assertTrue(any("pointer scan: no unit start occurs" in line for line in lines), lines)
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
            result = boundary_probe.probe_packages(registry["packages"], root)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["exports_probed"], 1)
            self.assertEqual(result["totals"]["units"], len(TEXTS))
            self.assertEqual(result["length_prefix"]["best"][0]["delta"], 4)

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
