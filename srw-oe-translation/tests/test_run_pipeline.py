"""Tests for the one-click run with a fake converter and invented data.

The fake converter is a small Python program that mimics the documented YACpkTool
command line, including its quirks: error messages on stdout with exit code 0, output
path validation that rejects spaces and non-ASCII characters, the `.EDAT` name rejection
path, and a crash when stdout is a pipe. The CPK container here is a synthetic JSON
format, not the CRI format. No real game file, converter, or decoded game text is used.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import run_pipeline  # noqa: E402

SRW_ROOT = Path(__file__).resolve().parents[1]
BAT_PATH = SRW_ROOT / "RUN_PIPELINE.bat"

FAKE_CONVERTER_SOURCE = r'''#!{python}
import base64
import json
import os
import re
import stat
import sys
from pathlib import Path

args = sys.argv[1:]
log_path = os.environ.get("FAKE_YACPK_LOG")
if log_path:
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(args) + "\n")


def flag(name):
    return os.environ.get(name, "")


def is_pipe(stream):
    try:
        return stat.S_ISFIFO(os.fstat(stream.fileno()).st_mode)
    except (OSError, ValueError):
        return False


def value_after(option):
    return args[args.index(option) + 1]


def load_members(path):
    data = Path(path).read_bytes()
    if not data.startswith(b"CPK "):
        return None
    return json.loads(data[4:].decode("utf-8"))["members"]


def rejected(path):
    if flag("FAKE_YACPK_REJECT_ALL"):
        return True
    return bool(flag("FAKE_YACPK_REJECT_EDAT")) and Path(path).name.lower().endswith(".edat")


def crash():
    sys.stderr.write("Unhandled Exception: System.IO.IOException: The handle is invalid.\n")
    sys.exit(3)


if not args or "-h" in args:
    print("YACpkTool fake test double (not the real tool)")
    sys.exit(0)

command = args[0]
if command == "-L":
    source = value_after("-i")
    members = None if rejected(source) else load_members(source)
    if members is None:
        print("Error: AnalyzeCpkFile returned false!")
        sys.exit(0)
    print(f"CPK information: {len(members)} members")
    print("Process finished (hopefully) without issues!")
    sys.exit(0)

if command == "-X":
    source = value_after("-i")
    destination = value_after("-o")
    if not re.fullmatch(r"[A-Za-z0-9._\-/\\:]+", destination):
        print("Error: Invalid output path specified. Exiting process.")
        sys.exit(0)
    members = None if rejected(source) else load_members(source)
    if members is None:
        print("Error: AnalyzeCpkFile returned false!")
        sys.exit(0)
    if flag("FAKE_YACPK_FAIL_SUBSTRING") and flag("FAKE_YACPK_FAIL_SUBSTRING") in source:
        print("Error: Unable to locate the specified file in the CPK")
        sys.exit(0)
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=True)
    for index, member in enumerate(members):
        target = out / member["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(member["data"]))
        if index == 0 and flag("FAKE_YACPK_CRASH_ON_PIPE") and is_pipe(sys.stdout):
            print("0% extracted...", end="")
            crash()
    print("100% extracted...")
    print("Status = Done")
    print("Process finished (hopefully) without issues!")
    if flag("FAKE_YACPK_WRITE_INTO_INPUT"):
        (Path(source).parent / "stray.txt").write_text("written by the converter", encoding="utf-8")
    if flag("FAKE_YACPK_MUTATE_SUBSTRING") and flag("FAKE_YACPK_MUTATE_SUBSTRING") in source:
        with open(source, "ab") as handle:
            handle.write(b"!")
    sys.exit(0)

if command == "-P":
    folder = Path(value_after("-i"))
    destination = value_after("-o")
    if not re.fullmatch(r"[A-Za-z0-9._\-/\\:]+", destination):
        print("Error: Invalid output path specified. Exiting process.")
        sys.exit(0)
    if not folder.is_dir() or not Path(destination).parent.is_dir():
        print("Error: Could not find the specified input folder or output folder")
        sys.exit(0)
    if flag("FAKE_YACPK_CRASH_ON_PIPE") and is_pipe(sys.stdout):
        print("0% packed...", end="")
        crash()
    names = sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())
    if flag("FAKE_YACPK_PACK_DROP_FIRST") and names:
        names = names[1:]
    members = [
        {"path": name, "data": base64.b64encode((folder / name).read_bytes()).decode("ascii")}
        for name in names
    ]
    Path(destination).write_bytes(b"CPK " + json.dumps({"members": members}, sort_keys=True).encode("utf-8"))
    print("100% packed...")
    print("Status = Done")
    print("Process finished (hopefully) without issues!")
    sys.exit(0)

print("Error: unknown command in the fake converter")
sys.exit(0)
'''


def make_cpk(members: dict) -> bytes:
    """Synthetic container for tests: 'CPK ' signature plus JSON members."""
    payload = {
        "members": [
            {"path": name, "data": base64.b64encode(data).decode("ascii")}
            for name, data in sorted(members.items())
        ]
    }
    return b"CPK " + json.dumps(payload, sort_keys=True).encode("utf-8")


def synthetic_bin() -> bytes:
    """An invented BIN with the same shape as the extractor tests (no game data)."""
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


def synthetic_iso(volume_id: bytes = b"SRW_OE_TEST") -> bytes:
    data = bytearray(17 * 2048)
    descriptor = bytearray(2048)
    descriptor[0:7] = b"\x01CD001\x01"
    descriptor[40:72] = volume_id.ljust(32, b" ")
    descriptor[80:84] = (17).to_bytes(4, "little")
    descriptor[128:130] = (2048).to_bytes(2, "little")
    data[16 * 2048 : 17 * 2048] = descriptor
    return bytes(data)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PipelineFixture(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.tool_dir = self.root / "converter"
        self.tool_dir.mkdir()
        self.tool = self.tool_dir / "YACpkTool.exe"
        self.tool.write_text(FAKE_CONVERTER_SOURCE.replace("{python}", sys.executable), encoding="utf-8")
        self.tool.chmod(0o755)
        (self.tool_dir / "CpkMaker.dll").write_bytes(b"fake companion library")
        self.calls_log = self.root / "calls.jsonl"
        self.input_root = self.root / "input files"
        self.output_base = self.root / "out"
        self.input_root.mkdir()
        self.config = self.root / "config" / "local-workflow.ini"
        self.console_calls: list[list[str]] = []
        self.console_output = self.root / "console-output.txt"
        self.bin_data = synthetic_bin()
        self.imenu_bytes = make_cpk({"srwDL_Chara.bin": self.bin_data, "readme.txt": b"plain text member"})
        self.event_bytes = make_cpk(
            {
                "event/P01.bin": self.bin_data + self.bin_data,
                "sub/inner.cpk": make_cpk({"b.bin": self.bin_data, "c.txt": b"tail"}),
            }
        )

    def tearDown(self):
        self._temporary.cleanup()

    def write_standard_inputs(self):
        (self.input_root / "imenu01.EDAT").write_bytes(self.imenu_bytes)
        (self.input_root / "zz_copy.EDAT").write_bytes(self.imenu_bytes)
        (self.input_root / "event_P01.EDAT").write_bytes(self.event_bytes)
        (self.input_root / "unknown.EDAT").write_bytes(b"NOT A CONTAINER, unknown wrapper")
        (self.input_root / "base game.iso").write_bytes(synthetic_iso())
        (self.input_root / "notes.zip").write_bytes(b"PK\x03\x04" + b"0" * 100)

    def input_hashes(self) -> dict:
        return {
            path.relative_to(self.input_root).as_posix(): sha256(path.read_bytes())
            for path in sorted(self.input_root.rglob("*"))
            if path.is_file()
        }

    def settings(self, **overrides) -> run_pipeline.Settings:
        values = {
            "input_root": self.input_root,
            "output_base": self.output_base,
            "tool_path": self.tool,
            "expected_tool_sha256": None,
        }
        values.update(overrides)
        return run_pipeline.Settings(**values)

    def run_quietly(self, env: dict | None = None, **kwargs):
        """Run the pipeline with the fake converter. console mode is simulated with a regular file."""
        environment = {"FAKE_YACPK_LOG": str(self.calls_log)}
        environment.update(env or {})
        real_run = subprocess.run

        def console_aware_run(command, **call_kwargs):
            if "stdout" not in call_kwargs:
                # Console mode: the real tool would inherit our console. A regular file stands in.
                self.console_calls.append(list(command))
                with self.console_output.open("ab") as handle:
                    call_kwargs["stdout"] = handle
                    call_kwargs["stderr"] = handle
                    return real_run(command, **call_kwargs)
            return real_run(command, **call_kwargs)

        lines: list[str] = []
        with patch.dict(os.environ, environment), patch.object(
            run_pipeline.subprocess, "run", side_effect=console_aware_run
        ):
            result = run_pipeline.run_pipeline(self.settings(), say=lines.append, **kwargs)
        return result, lines

    def calls(self) -> list[list[str]]:
        if not self.calls_log.exists():
            return []
        return [json.loads(line) for line in self.calls_log.read_text(encoding="utf-8").splitlines()]

    def registry(self, result) -> dict:
        return json.loads(result.registry_path.read_text(encoding="utf-8"))


class RunPipelineTests(PipelineFixture):
    def test_full_run_extracts_unique_packages_nested_cpk_text_and_gates(self):
        self.write_standard_inputs()
        before = self.input_hashes()

        result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.exit_code, 0)
        registry = self.registry(result)
        self.assertTrue(registry["input"]["unchanged"])
        self.assertEqual(self.input_hashes(), before)

        self.assertEqual(len(registry["packages"]), 3)
        packages = {package["source_path"]: package for package in registry["packages"] if package["depth"] == 0}
        self.assertEqual(sorted(packages), ["event_P01.EDAT", "imenu01.EDAT"])
        imenu = packages["imenu01.EDAT"]
        self.assertEqual(imenu["status"], "extracted")
        self.assertEqual(imenu["aliases"][0]["path"], "zz_copy.EDAT")
        nested = [package for package in registry["packages"] if package["depth"] == 1][0]
        self.assertTrue(nested["source_path"].endswith("/sub/inner.cpk"))
        self.assertEqual(nested["parent_package"], packages["event_P01.EDAT"]["package_id"])
        self.assertEqual(nested["text"]["status"], "exported_verified")

        for package in registry["packages"]:
            self.assertEqual(package["status"], "extracted")
            self.assertTrue((result.run_dir / package["output_dir"]).is_dir())
        self.assertEqual(registry["gate"]["status"], "passed")
        self.assertEqual(registry["gate"].get("missing_count", 0), 0)
        self.assertEqual(registry["summary"]["text_packages_verified"], 3)
        self.assertGreater(registry["summary"]["text_units_total"], 0)
        self.assertTrue((result.run_dir / "text" / imenu["package_id"] / "manifest.json").is_file())

        not_processed = " | ".join(registry["not_processed"])
        self.assertIn("ISO image not processed", not_processed)
        self.assertIn("volume id: SRW_OE_TEST", not_processed)
        self.assertIn("ZIP archive not processed", not_processed)
        self.assertIn("unrecognized signature", not_processed)
        self.assertEqual(registry["probe"]["naming_mode"], "original_name")
        self.assertEqual(registry["converter"]["io_mode"], "captured")
        iso_rows = [row for row in registry["inputs"] if row["content_type"] == "iso9660_pvd_signature"]
        self.assertEqual(iso_rows[0]["iso_facts"]["volume_identifier"], "SRW_OE_TEST")
        self.assertTrue(iso_rows[0]["iso_facts"]["size_matches_descriptor"])

        self.assertFalse((result.run_dir / "staging").exists())
        gates = result.run_dir / "gates"
        self.assertTrue(not gates.exists() or list(gates.iterdir()) == [])

    def test_converter_never_receives_r_option_and_extract_always_uses_dash_i_after_x(self):
        self.write_standard_inputs()
        self.run_quietly()
        calls = self.calls()
        self.assertTrue(calls)
        for arguments in calls:
            self.assertNotIn("-R", arguments)
            if arguments[0] == "-X":
                self.assertEqual(arguments[1], "-i")
            self.assertIn(arguments[0], ("-X", "-L", "-P"))

    def test_registry_and_reports_contain_no_decoded_game_text_or_absolute_input_paths(self):
        self.write_standard_inputs()
        result, _lines = self.run_quietly()
        registry_text = result.registry_path.read_text(encoding="utf-8")
        report_text = result.report_path.read_text(encoding="utf-8")
        csv_text = (result.run_dir / "packages.csv").read_text(encoding="utf-8") + (
            result.run_dir / "inputs.csv"
        ).read_text(encoding="utf-8")
        for text in (registry_text, report_text, csv_text):
            self.assertNotIn("日本語", text)
            self.assertNotIn("テスト", text)
            self.assertNotIn(str(self.input_root), text)
            self.assertNotIn(str(self.root), text)
        self.assertIn("Known gaps", report_text)
        self.assertIn("Repack and write-back: disabled", registry_text)

    def test_probe_falls_back_to_cpk_alias_in_staging_without_renaming_inputs(self):
        self.write_standard_inputs()
        before = self.input_hashes()

        result, _lines = self.run_quietly({"FAKE_YACPK_REJECT_EDAT": "1"})

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertEqual(registry["probe"]["naming_mode"], "cpk_alias")
        self.assertEqual(registry["probe"]["io_mode"], "captured")
        rejected_attempts = [a for a in registry["probe"]["attempts"] if not a["ok"]]
        self.assertGreaterEqual(len(rejected_attempts), 2)
        self.assertEqual(self.input_hashes(), before)
        self.assertTrue((self.input_root / "imenu01.EDAT").is_file())
        extract_inputs = [call[2] for call in self.calls() if call[0] == "-X" and "-i" in call]
        alias_inputs = [value for value in extract_inputs if value.endswith(".cpk")]
        self.assertTrue(alias_inputs)
        for value in alias_inputs:
            self.assertNotIn(str(self.input_root), value)
        self.assertEqual(registry["summary"]["packages_extracted"], 3)

    def test_crash_when_output_is_piped_falls_back_to_console_mode(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_CRASH_ON_PIPE": "1"})

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertEqual(registry["converter"]["io_mode"], "console")
        captured_probe = registry["probe"]["attempts"][0]
        self.assertEqual(captured_probe["io_mode"], "captured")
        self.assertFalse(captured_probe["ok"])
        self.assertIn("exit code 3", captured_probe["reason"])
        self.assertTrue(self.console_calls)
        self.assertTrue(all(command[1] in ("-X", "-P") for command in self.console_calls))
        self.assertEqual(registry["summary"]["packages_extracted"], 3)
        self.assertEqual(registry["summary"]["gate_status"], "passed")

    def test_blocked_when_no_mode_extracts_and_no_partial_output_is_kept(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_REJECT_ALL": "1"})

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.exit_code, 1)
        registry = self.registry(result)
        self.assertEqual(registry["probe"]["status"], "blocked")
        self.assertGreaterEqual(len(registry["probe"]["attempts"]), 4)
        self.assertEqual(registry["packages"], [])
        self.assertIn("Blocked: converter probe failed", result.report_path.read_text(encoding="utf-8"))
        self.assertFalse((result.run_dir / "packages").exists() and any((result.run_dir / "packages").iterdir()))

    def test_one_failing_package_is_isolated_and_reported(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_FAIL_SUBSTRING": "event_P01"})

        self.assertEqual(result.status, "completed_with_failures")
        self.assertEqual(result.exit_code, 1)
        registry = self.registry(result)
        by_source = {package["source_path"]: package for package in registry["packages"]}
        self.assertEqual(by_source["imenu01.EDAT"]["status"], "extracted")
        self.assertEqual(by_source["event_P01.EDAT"]["status"], "failed")
        self.assertIn("Error: line", by_source["event_P01.EDAT"]["error"])
        self.assertFalse((result.run_dir / by_source["event_P01.EDAT"]["output_dir"]).exists())
        self.assertIn("event_P01", " ".join(registry["failures"]))

    def test_source_changed_during_extraction_is_detected_and_output_removed(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_MUTATE_SUBSTRING": "event_P01"})

        registry = self.registry(result)
        by_source = {package["source_path"]: package for package in registry["packages"]}
        self.assertEqual(by_source["event_P01.EDAT"]["status"], "failed")
        self.assertIn("source changed during extraction", by_source["event_P01.EDAT"]["error"])
        self.assertFalse((result.run_dir / by_source["event_P01.EDAT"]["output_dir"]).exists())
        # The fake also changed the input file, so the whole run must fail closed.
        self.assertEqual(result.status, "error")
        self.assertFalse(registry["input"]["unchanged"])

    def test_converter_writing_into_input_folder_makes_the_run_fail_closed(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_WRITE_INTO_INPUT": "1"})

        self.assertEqual(result.status, "error")
        registry = self.registry(result)
        self.assertFalse(registry["input"]["unchanged"])
        self.assertIn("stray.txt", json.dumps(registry["input"]["changed_entries"]))
        self.assertTrue(any("input folder changed" in item for item in registry["failures"]))

    def test_repack_gate_reports_a_missing_member(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_PACK_DROP_FIRST": "1"})

        self.assertEqual(result.status, "completed_with_failures")
        gate = self.registry(result)["gate"]
        self.assertEqual(gate["status"], "failed")
        self.assertEqual(gate["missing_count"], 1)
        self.assertFalse((result.run_dir / "gates").exists() and any((result.run_dir / "gates").iterdir()))

    def test_no_cpk_inputs_means_no_converter_calls_and_reports_gaps(self):
        (self.input_root / "unknown.EDAT").write_bytes(b"unknown")
        (self.input_root / "base game.iso").write_bytes(synthetic_iso())

        result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        self.assertEqual(self.calls(), [])
        registry = self.registry(result)
        self.assertEqual(registry["probe"]["status"], "not_run")
        self.assertEqual(registry["gate"]["status"], "not_run")

    def test_preflight_only_makes_no_converter_call(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly(preflight_only=True)

        self.assertEqual(result.status, "preflight_passed")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.calls(), [])
        registry = self.registry(result)
        self.assertEqual(registry["run"]["mode"], "preflight_only")
        self.assertEqual(registry["packages"], [])
        self.assertEqual(registry["converter"]["sha256"], sha256(self.tool.read_bytes()))

    def test_free_space_shortfall_blocks_before_any_converter_call(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly(free_bytes=lambda _path: 1024)

        self.assertEqual(result.status, "blocked")
        self.assertEqual(self.calls(), [])
        self.assertIn("not enough free space", " ".join(self.registry(result)["failures"]))

    def test_output_path_with_space_is_refused_before_converter_runs(self):
        self.write_standard_inputs()
        self.output_base = self.root / "my out"

        result, _lines = self.run_quietly()

        self.assertEqual(result.status, "blocked")
        self.assertEqual(self.calls(), [])
        self.assertIn("cannot be passed to the converter", " ".join(self.registry(result)["failures"]))

    def test_expected_converter_hash_mismatch_refuses_to_run(self):
        self.write_standard_inputs()
        settings = self.settings(expected_tool_sha256="0" * 64)

        environment = {"FAKE_YACPK_LOG": str(self.calls_log)}
        with patch.dict(os.environ, environment):
            result = run_pipeline.run_pipeline(settings, say=lambda _line: None)

        self.assertEqual(result.status, "blocked")
        self.assertEqual(self.calls(), [])

    def test_output_inside_input_tree_is_rejected(self):
        self.write_standard_inputs()
        settings = self.settings(output_base=self.input_root / "out")
        with self.assertRaises(run_pipeline.SetupError):
            run_pipeline.run_pipeline(settings, say=lambda _line: None)
        self.assertEqual(self.calls(), [])

    def test_registry_is_deterministic_apart_from_run_identity_and_timing(self):
        self.write_standard_inputs()
        first, _ = self.run_quietly(run_id="first-run")
        second, _ = self.run_quietly(run_id="second-run")
        keys = ("probe", "inputs", "packages", "gate", "not_processed", "failures", "summary")
        first_registry, second_registry = self.registry(first), self.registry(second)
        self.assertEqual({key: first_registry[key] for key in keys}, {key: second_registry[key] for key in keys})
        calls_without_timing = lambda registry: [  # noqa: E731
            {key: value for key, value in call.items() if key != "seconds"} for call in registry["converter_calls"]
        ]
        self.assertEqual(calls_without_timing(first_registry), calls_without_timing(second_registry))
        self.assertNotEqual(first_registry["run"]["id"], second_registry["run"]["id"])

    def test_fresh_run_folder_is_never_reused(self):
        self.write_standard_inputs()
        first, _ = self.run_quietly(run_id="same-id")
        self.assertEqual(first.status, "completed")
        with self.assertRaises(FileExistsError):
            self.run_quietly(run_id="same-id")


class CliAndSetupTests(PipelineFixture):
    def test_cli_without_gui_and_without_config_fails_and_writes_no_config(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = run_pipeline.main(["--config", str(self.config), "--no-gui"])
        self.assertEqual(code, 2)
        self.assertIn("not configured", output.getvalue())
        self.assertFalse(self.config.exists())

    def test_cli_runs_with_config_and_overrides_do_not_overwrite_saved_values(self):
        self.write_standard_inputs()
        run_pipeline.save_settings(
            self.config,
            run_pipeline.Settings(input_root=self.input_root, output_base=self.output_base, tool_path=self.tool),
        )
        before = self.config.read_text(encoding="utf-8")
        output = io.StringIO()
        with patch.dict(os.environ, {"FAKE_YACPK_LOG": str(self.calls_log)}), redirect_stdout(output):
            code = run_pipeline.main(
                ["--config", str(self.config), "--no-gui", "--preflight-only", "--output", str(self.root / "other")]
            )
        self.assertEqual(code, 0)
        self.assertEqual(self.config.read_text(encoding="utf-8"), before)
        self.assertIn("Done. Open", output.getvalue())

    def test_config_paths_are_relative_to_the_ini_file_and_hash_is_validated(self):
        self.config.parent.mkdir(parents=True)
        self.config.write_text(
            "[local]\ninput_root = ../input files\noutput_root = ../out\ntool_path = ../converter/YACpkTool.exe\n"
            "expected_tool_sha256 = " + "a" * 64 + "\n",
            encoding="utf-8",
        )
        settings = run_pipeline.load_settings(self.config)
        self.assertEqual(settings.input_root, self.input_root.resolve())
        self.assertEqual(settings.output_base, self.output_base.resolve())
        self.assertEqual(settings.tool_path, self.tool.resolve())
        self.assertEqual(settings.expected_tool_sha256, "a" * 64)

        self.config.write_text("[local]\ninput_root = x\nexpected_tool_sha256 = nothex\n", encoding="utf-8")
        with self.assertRaises(run_pipeline.SetupError):
            run_pipeline.load_settings(self.config)

    def test_prompted_answers_are_the_only_ones_reported_and_discovery_is_not_saved(self):
        self.write_standard_inputs()
        (self.input_root / "YACpkTool.exe").write_bytes(b"not run in this test")
        asked: list[str] = []

        def fake_directory(title, initial):
            asked.append(title)
            return self.input_root if "input" in title.lower() or "files" in title.lower() else self.output_base

        settings, prompted = run_pipeline.complete_settings(
            run_pipeline.Settings(),
            gui=True,
            reconfigure=False,
            prompt_directory=fake_directory,
            prompt_converter=lambda _initial: self.fail("converter must be discovered, not asked"),
        )
        self.assertEqual(prompted, {"input_root", "output_root"})
        self.assertEqual(settings.tool_path, (self.input_root / "YACpkTool.exe").resolve())
        self.assertEqual(len(asked), 2)

    def test_unusable_output_folder_is_asked_again_before_it_is_saved(self):
        answers = iter([self.root / "my out", self.output_base])
        asked_titles: list[str] = []

        def fake_directory(title, initial):
            asked_titles.append(title)
            if "output" in title.lower():
                return next(answers)
            return self.input_root

        self.output_base.mkdir()
        with redirect_stdout(io.StringIO()):
            settings, prompted = run_pipeline.complete_settings(
                run_pipeline.Settings(tool_path=self.tool),
                gui=True,
                reconfigure=False,
                prompt_directory=fake_directory,
                prompt_converter=lambda _initial: self.fail("converter is already set"),
            )
        self.assertEqual(settings.output_base, self.output_base)
        self.assertEqual(prompted, {"input_root", "output_root"})
        self.assertEqual(sum("output" in title.lower() for title in asked_titles), 2)

    def test_saved_unusable_output_folder_is_asked_again_in_gui_mode_only(self):
        self.output_base = self.root / "my out"
        self.output_base.mkdir()
        asked: list[str] = []

        def fake_directory(title, initial):
            asked.append(title)
            return self.output_base.parent / "out"

        (self.output_base.parent / "out").mkdir()
        with redirect_stdout(io.StringIO()):
            settings, prompted = run_pipeline.complete_settings(
                run_pipeline.Settings(input_root=self.input_root, output_base=self.output_base, tool_path=self.tool),
                gui=True,
                reconfigure=False,
                prompt_directory=fake_directory,
                prompt_converter=lambda _initial: self.fail("converter is already set"),
            )
        self.assertEqual(settings.output_base, self.root / "out")
        self.assertEqual(prompted, {"output_root"})
        self.assertEqual(len(asked), 1)

        # Without GUI nothing is asked; the unusable folder stays and the preflight blocks the run.
        unchanged, prompted_no_gui = run_pipeline.complete_settings(
            run_pipeline.Settings(input_root=self.input_root, output_base=self.output_base, tool_path=self.tool),
            gui=False,
            reconfigure=False,
            prompt_directory=lambda *_args: self.fail("no dialogs without GUI"),
            prompt_converter=lambda _initial: self.fail("no dialogs without GUI"),
        )
        self.assertEqual(unchanged.output_base, self.output_base)
        self.assertEqual(prompted_no_gui, set())

    def test_output_inside_input_is_refused_by_the_same_check(self):
        problem = run_pipeline.output_folder_problem(self.input_root / "out", self.input_root)
        self.assertIn("must not be inside the input folder", problem)
        self.assertIsNone(run_pipeline.output_folder_problem(self.output_base, self.input_root))

    def test_gui_prompts_fill_missing_converter_when_discovery_is_empty(self):
        settings, prompted = run_pipeline.complete_settings(
            run_pipeline.Settings(input_root=self.input_root, output_base=self.output_base),
            gui=True,
            reconfigure=False,
            prompt_directory=lambda *_args: self.fail("folders are already set"),
            prompt_converter=lambda _initial: self.tool,
        )
        self.assertEqual(prompted, {"tool_path"})
        self.assertEqual(settings.tool_path, self.tool)

    def test_cancelled_setup_raises_without_writing(self):
        with self.assertRaises(run_pipeline.SetupError):
            run_pipeline.complete_settings(
                run_pipeline.Settings(),
                gui=True,
                reconfigure=False,
                prompt_directory=lambda *_args: None,
                prompt_converter=lambda _initial: None,
            )
        self.assertFalse(self.config.exists())

    def test_save_skips_missing_values_and_round_trips(self):
        run_pipeline.save_settings(self.config, run_pipeline.Settings(output_base=self.output_base))
        text = self.config.read_text(encoding="utf-8")
        self.assertNotIn("input_root", text)
        loaded = run_pipeline.load_settings(self.config)
        self.assertEqual(loaded.output_base, self.output_base.resolve())
        self.assertIsNone(loaded.input_root)


class UnitHelperTests(unittest.TestCase):
    def test_converter_path_keeps_safe_paths_and_uses_short_names_when_needed(self):
        safe = Path("/tmp/safe_dir/run-1")
        self.assertEqual(run_pipeline.converter_argument_path(safe, short_name=lambda _p: None), str(safe))
        with tempfile.TemporaryDirectory() as temporary:
            unsafe = Path(temporary) / "my out" / "run"
            with self.assertRaises(run_pipeline.UnsafePathError):
                run_pipeline.converter_argument_path(unsafe, short_name=lambda _p: None)
            short_parent = Path(temporary) / "my out"
            short_parent.mkdir()
            result = run_pipeline.converter_argument_path(
                unsafe, short_name=lambda path: str(Path(temporary) / "MYOUT~1") if path == short_parent else None
            )
            self.assertEqual(result, str(Path(temporary) / "MYOUT~1" / "run"))

    def test_converter_failure_judges_error_lines_crashes_and_missing_finish(self):
        def call(output, returncode=0):
            return run_pipeline.ConverterCall(
                label="t", io_mode="captured", command=[], returncode=returncode, timed_out=False,
                output=output, error=None, seconds=0.0,
            )

        self.assertIsNone(run_pipeline.converter_failure(call("x\nProcess finished (hopefully)"), expect_finished=True))
        self.assertIn("Error:", run_pipeline.converter_failure(call("Error: nope\nProcess finished"), expect_finished=True))
        self.assertIn("unhandled", run_pipeline.converter_failure(call("Unhandled Exception: System.IO.IOException"), expect_finished=True))
        self.assertIn("final message", run_pipeline.converter_failure(call("partial"), expect_finished=True))
        self.assertIn("exit code 3", run_pipeline.converter_failure(call("", returncode=3), expect_finished=True))
        self.assertIsNone(run_pipeline.converter_failure(call("listing"), expect_finished=False))

    def test_iso_facts_read_the_primary_volume_descriptor_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            image = Path(temporary) / "game.iso"
            image.write_bytes(synthetic_iso())
            facts = run_pipeline._iso_facts(image, image.stat().st_size)
        self.assertTrue(facts["primary_volume_descriptor_found"])
        self.assertEqual(facts["volume_identifier"], "SRW_OE_TEST")
        self.assertEqual(facts["volume_space_blocks"], 17)
        self.assertTrue(facts["size_matches_descriptor"])

    def test_snapshot_detects_added_changed_and_removed_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "tree"
            (root / "sub").mkdir(parents=True)
            (root / "sub" / "a.bin").write_bytes(b"one")
            before = run_pipeline._tree_snapshot(root)
            (root / "sub" / "a.bin").write_bytes(b"two two")
            (root / "new.txt").write_bytes(b"x")
            after = run_pipeline._tree_snapshot(root)
        changes = run_pipeline._snapshot_changes(before, after)
        self.assertIn("new.txt", changes)
        self.assertIn("sub/a.bin", changes)

    def test_default_run_id_skips_existing_folders(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            stamp = "20261009-120000"
            (base / stamp).mkdir()
            self.assertEqual(run_pipeline._default_run_id(base, dt_for(stamp)), stamp + "-2")


def dt_for(stamp: str):
    import datetime as dt

    return dt.datetime.strptime(stamp, "%Y%m%d-%H%M%S")


class LauncherContractTests(unittest.TestCase):
    def test_bat_launcher_finds_python_runs_the_tool_and_keeps_the_window_open(self):
        self.assertTrue(BAT_PATH.is_file())
        text = BAT_PATH.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn('cd /d "%~dp0"', lowered)
        self.assertIn("py -3", lowered)
        self.assertIn("python", lowered)
        self.assertIn("tools\\run_pipeline.py", lowered)
        self.assertIn("pause", lowered)
        self.assertIn("python.org", lowered)
        self.assertNotIn("pip install", lowered)
        self.assertNotIn("curl", lowered)
        self.assertNotIn("powershell -command download", lowered)


if __name__ == "__main__":
    unittest.main()
