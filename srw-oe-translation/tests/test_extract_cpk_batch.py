import hashlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import extract_cpk_batch  # noqa: E402


class BatchCpkExtractionTests(unittest.TestCase):
    def _input_tree(self, root: Path) -> tuple[Path, list[Path]]:
        input_root = root / "input files"
        nested = input_root / "DLC pack"
        nested.mkdir(parents=True)
        first = input_root / "event P01.EDAT"
        second = nested / "unit data.EDAT"
        first.write_bytes(b"CPK " + b"first fake archive")
        second.write_bytes(b"CPK " + b"second fake archive")
        (input_root / "not a CPK.EDAT").write_bytes(b"unknown wrapper")
        iso = bytearray(17 * 2048)
        iso[16 * 2048 : 16 * 2048 + 7] = b"\x01CD001\x01"
        (input_root / "base game.iso").write_bytes(iso)
        return input_root, [first, second]

    def test_dry_run_batches_signature_matched_edat_without_writing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root, cpk_files = self._input_tree(root)
            output_root = root / "extract outputs"

            report = extract_cpk_batch.run_batch(
                input_root, output_root, tool_path=None, execute=False
            )

            self.assertEqual(report["mode"], "dry_run")
            self.assertEqual(report["cpk_candidate_count"], 2)
            self.assertEqual(report["unresolved_edat_count"], 1)
            self.assertEqual(report["iso_candidate_count"], 1)
            self.assertFalse(output_root.exists())
            planned_sources = {Path(plan["source"]) for plan in report["plans"]}
            self.assertEqual(planned_sources, set(cpk_files))
            self.assertTrue(
                all(plan["extract_command"][0] == "-X" for plan in report["plans"])
            )

    def test_execute_uses_arg_list_and_extracts_all_detected_archives(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root, cpk_files = self._input_tree(root)
            output_root = root / "outputs"
            tool_directory = root / "Converter Folder"
            tool_directory.mkdir()
            tool = tool_directory / "YACpkTool.exe"
            tool.write_bytes(b"fake converter executable")
            commands = []

            def fake_run(command, **kwargs):
                commands.append((command, kwargs))
                self.assertIsInstance(command, list)
                self.assertFalse(kwargs["shell"])
                if "-X" in command:
                    output_directory = Path(command[command.index("-o") + 1])
                    output_directory.mkdir(parents=True)
                    (output_directory / "member.bin").write_bytes(b"fake extracted member")
                return extract_cpk_batch.subprocess.CompletedProcess(
                    command, 0, b"fake listing", b""
                )

            before_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in cpk_files}
            with patch.object(extract_cpk_batch.subprocess, "run", side_effect=fake_run):
                report = extract_cpk_batch.run_batch(
                    input_root, output_root, tool_path=tool, execute=True
                )

            self.assertEqual(report["extracted_count"], 2)
            self.assertEqual(report["failed_count"], 0)
            self.assertEqual(len(commands), 4)
            self.assertEqual(report["converter_path"], str(tool.resolve()))
            self.assertEqual(
                report["converter_sha256"], hashlib.sha256(tool.read_bytes()).hexdigest()
            )
            self.assertEqual(
                {result["relative_path"] for result in report["results"]},
                {path.relative_to(input_root).as_posix() for path in cpk_files},
            )
            for path in cpk_files:
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before_hashes[path])
            self.assertEqual(len(list(output_root.rglob("member.bin"))), 2)

    def test_list_failure_does_not_start_extraction(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root, _ = self._input_tree(root)
            output_root = root / "outputs"
            tool = root / "YACpkTool.exe"
            tool.write_bytes(b"fake converter")
            commands = []

            def fake_run(command, **kwargs):
                commands.append(command)
                return extract_cpk_batch.subprocess.CompletedProcess(
                    command, 7, b"", b"list failed"
                )

            with patch.object(extract_cpk_batch.subprocess, "run", side_effect=fake_run):
                report = extract_cpk_batch.run_batch(
                    input_root, output_root, tool_path=tool, execute=True
                )

            self.assertEqual(len(commands), 2)
            self.assertTrue(all("-L" in command for command in commands))
            self.assertEqual(report["extracted_count"], 0)
            self.assertEqual(report["failed_count"], 2)
            self.assertTrue(all(result["status"] == "failed" for result in report["results"]))

    def test_source_mutation_during_listing_blocks_extraction(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root, cpk_files = self._input_tree(root)
            output_root = root / "outputs"
            tool = root / "YACpkTool.exe"
            tool.write_bytes(b"fake converter")
            first_source = cpk_files[0]
            commands = []

            def fake_run(command, **kwargs):
                commands.append(command)
                if "-L" in command and Path(command[command.index("-i") + 1]) == first_source:
                    first_source.write_bytes(b"modified by fake tool")
                return extract_cpk_batch.subprocess.CompletedProcess(command, 0, b"", b"")

            with patch.object(extract_cpk_batch.subprocess, "run", side_effect=fake_run):
                report = extract_cpk_batch.run_batch(
                    input_root, output_root, tool_path=tool, execute=True
                )

            first_result = next(
                result for result in report["results"]
                if result["relative_path"] == first_source.relative_to(input_root).as_posix()
            )
            self.assertIn("Source changed during listing", first_result["error"])
            self.assertFalse(any("-X" in command and str(first_source) in command for command in commands))

    def test_output_may_not_overlap_source_tree(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root, _ = self._input_tree(root)

            with self.assertRaisesRegex(ValueError, "separate from the input tree"):
                extract_cpk_batch._validate_paths(
                    input_root, input_root / "extracted", None
                )
            with self.assertRaisesRegex(ValueError, "separate from the input tree"):
                extract_cpk_batch._validate_paths(
                    input_root, input_root.parent, None
                )

    def test_report_paths_are_outside_inputs_outputs_and_new(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root, _ = self._input_tree(root)
            output_root = root / "outputs"

            with self.assertRaisesRegex(ValueError, "outside both input"):
                extract_cpk_batch._validate_paths(
                    input_root, output_root, input_root / "report.json"
                )
            with self.assertRaisesRegex(ValueError, "outside both input"):
                extract_cpk_batch._validate_paths(
                    input_root, output_root, output_root / "report.json"
                )

            existing_report = root / "old-report.json"
            existing_report.write_text("old", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "already exists"):
                extract_cpk_batch._validate_paths(
                    input_root, output_root, existing_report
                )

    def test_ini_config_resolves_paths_relative_to_itself_and_cli_overrides_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            config_directory = root / "Desktop config folder"
            input_root = root / "Game files"
            output_from_config = root / "Configured output"
            output_from_cli = root / "CLI output"
            tool_directory = root / "Converter folder"
            config_directory.mkdir()
            input_root.mkdir()
            (input_root / "eventP01.EDAT").write_bytes(b"CPK " + b"fixture")
            tool_directory.mkdir()
            tool = tool_directory / "YACpkTool.exe"
            tool.write_bytes(b"fake converter")
            config_path = config_directory / "paths.ini"
            config_path.write_text(
                "[local]\n"
                "input_root = ../Game files\n"
                "output_root = ../Configured output\n"
                "tool_path = ../Converter folder/YACpkTool.exe\n",
                encoding="utf-8",
            )

            settings = extract_cpk_batch.load_local_config(config_path)
            self.assertEqual(settings["input_root"], input_root.resolve())
            self.assertEqual(settings["output_root"], output_from_config.resolve())
            self.assertEqual(settings["tool_path"], tool.resolve())

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = extract_cpk_batch.main(
                    ["--config", str(config_path), "--output", str(output_from_cli)]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("CPK-signature inputs: 1", output.getvalue())
            self.assertIn(str(tool.resolve()), output.getvalue())
            self.assertFalse(output_from_cli.exists())
            self.assertFalse(output_from_config.exists())

    def test_ini_config_requires_local_section_and_input_output_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            no_section = root / "no-section.ini"
            no_section.write_text("[other]\ninput_root = x\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"\[local\] section"):
                extract_cpk_batch.load_local_config(no_section)

            missing_output = root / "missing-output.ini"
            missing_output.write_text("[local]\ninput_root = .\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requires output_root"):
                extract_cpk_batch.load_local_config(missing_output)

    def test_converter_auto_discovery_is_limited_to_input_root_and_script_dir(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            input_root = root / "game files"
            input_root.mkdir()
            tool_directory = input_root / "YACpkTool"
            tool_directory.mkdir()
            tool = tool_directory / "YACpkTool.exe"
            tool.write_bytes(b"fake converter")

            self.assertEqual(
                extract_cpk_batch.resolve_tool(None, input_root), tool.resolve()
            )

            another_tool = input_root / "YACpkTool.exe"
            another_tool.write_bytes(b"another fake converter")
            with self.assertRaisesRegex(ValueError, "Multiple YACpkTool.exe"):
                extract_cpk_batch.resolve_tool(None, input_root)


if __name__ == "__main__":
    unittest.main()
