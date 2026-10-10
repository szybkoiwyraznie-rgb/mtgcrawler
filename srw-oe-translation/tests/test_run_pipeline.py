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
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
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

sys.stdout.reconfigure(encoding="utf-8")
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


def grouped(value):
    text = str(value)
    parts = []
    while len(text) > 3:
        parts.insert(0, text[-3:])
        text = text[:-3]
    parts.insert(0, text)
    return "\ufffd".join(parts)


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
    rows = [(member["path"], len(base64.b64decode(member["data"]))) for member in members]
    if flag("FAKE_YACPK_DUPLICATE_SUBSTRING") and flag("FAKE_YACPK_DUPLICATE_SUBSTRING") in source and rows:
        rows.append(rows[0])  # a second entry with the same name, as the real bacb01 listing has
    no_id = flag("FAKE_YACPK_NO_ID_LISTING")
    no_name = flag("FAKE_YACPK_NO_NAME_LISTING")
    narrow = flag("FAKE_YACPK_NARROW_LISTING")
    print(f"CPK Filename:{Path(source).name}")
    print("File format version:Ver.7, Rev.1")
    print(f"Content files:{len(rows)}")
    print(f"Content file size:{grouped(sum(size for _name, size in rows))}")
    print("Compressed files:0")
    print()
    if no_id and no_name:
        print("No.        Filesize  Compressed       %")
    elif no_id:
        print("No.        Filesize  Compressed       %  Contents Filename")
    elif no_name:
        print("No.         ID    Filesize  Compressed       %")
    else:
        print("No.         ID    Filesize  Compressed       %  Contents Filename")
    for number, (name, size) in enumerate(rows):
        # A 0/0 percent prints as ",00", as the real converter does for empty entries.
        percent = ",00" if size == 0 else "100,00"
        if no_id and no_name:
            print(f"[{number:5d}]  {grouped(size):>9}  {grouped(size):>9}  {percent}")
        elif no_id:
            if narrow:
                print(f"[{number:5d}]  {grouped(size)} {grouped(size)}  {percent}  {name}")
            else:
                print(f"[{number:5d}]  {grouped(size):>9}  {grouped(size):>9}  {percent}  {name}")
        elif no_name:
            # Filename info disabled: the row has an ID column but no name (as the real face01).
            print(f"[{number:5d}]  {number:5d}  {grouped(size):>9}  {grouped(size):>9}  {percent} ")
        else:
            if narrow:
                # Narrow columns: the two numbers are separated by a single space, no padding.
                print(f"[{number:5d}]  {number + 1:5d}  {grouped(size)} {grouped(size)}  {percent}  {name}")
            else:
                print(f"[{number:5d}]  {number + 1:5d}  {grouped(size):>9}  {grouped(size):>9}  {percent}  {name}")
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
    no_name = flag("FAKE_YACPK_NO_NAME_LISTING")
    for index, member in enumerate(members):
        # Filename info disabled: YACpkTool writes one ID-named file per entry (ID00000, ...).
        target = out / (f"ID{index:05d}" if no_name else member["path"])
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


def grouped_number(value: int) -> str:
    """Thousands groups joined by U+FFFD, as the captured -L text shows them (synthetic values)."""
    text = str(value)
    groups = []
    while len(text) > 3:
        groups.insert(0, text[-3:])
        text = text[:-3]
    groups.insert(0, text)
    return "\ufffd".join(groups)


def synthetic_listing(entries: list) -> str:
    """Same layout as YACpkTool's -L output, with CR CR LF line ends. The entries are invented."""
    total = sum(size for _entry_id, _name, size in entries)
    lines = [
        "CPK Filename:synthetic.EDAT",
        "File format version:Ver.7, Rev.1",
        f"Content files:{len(entries)}",
        f"Content file size:{grouped_number(total)}",
        "Compressed files:0",
        "",
        "No.         ID    Filesize  Compressed       %  Contents Filename",
    ]
    for number, (entry_id, name, size) in enumerate(entries):
        lines.append(
            f"[{number:5d}]  {entry_id:5d}  {grouped_number(size):>9}  {grouped_number(size):>9}  100,00  {name}"
        )
    lines.append("Process finished (hopefully) without issues!")
    return "\r\r\n".join(lines) + "\r\r\n"


def synthetic_listing_layout(entries: list, *, drop_id: bool = False, drop_name: bool = False) -> str:
    """YACpkTool -L layout variants seen in the real run: without the ID column (Enable ID info
    off), without the filename column (Enable Filename info off), and a ",00" percent for a
    0-byte entry. The entries are invented."""
    total = sum(size for _entry_id, _name, size in entries)
    lines = [
        "CPK Filename:synthetic.EDAT",
        "File format version:Ver.7, Rev.1",
        f"Content files:{len(entries)}",
        f"Content file size:{grouped_number(total)}",
        "Compressed files:0",
        f"Enable Filename info.:{'False' if drop_name else 'True'}",
        f"Enable ID info.:{'False' if drop_id else 'True'}",
        "",
    ]
    if drop_id and drop_name:
        lines.append("No.        Filesize  Compressed       %")
    elif drop_id:
        lines.append("No.        Filesize  Compressed       %  Contents Filename")
    elif drop_name:
        lines.append("No.         ID    Filesize  Compressed       %")
    else:
        lines.append("No.         ID    Filesize  Compressed       %  Contents Filename")
    for number, (entry_id, name, size) in enumerate(entries):
        percent = ",00" if size == 0 else "100,00"
        if drop_id and drop_name:
            lines.append(f"[{number:5d}]  {grouped_number(size):>9}  {grouped_number(size):>9}  {percent}")
        elif drop_id:
            lines.append(f"[{number:5d}]  {grouped_number(size):>9}  {grouped_number(size):>9}  {percent}  {name}")
        elif drop_name:
            lines.append(f"[{number:5d}]  {entry_id:5d}  {grouped_number(size):>9}  {grouped_number(size):>9}  {percent} ")
        else:
            lines.append(
                f"[{number:5d}]  {entry_id:5d}  {grouped_number(size):>9}  {grouped_number(size):>9}  {percent}  {name}"
            )
    lines.append("Process finished (hopefully) without issues!")
    return "\r\r\n".join(lines) + "\r\r\n"


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
        self.assertEqual(len(list(result.run_dir.glob("diagnostics_*.zip"))), 1)

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
        self.assertEqual(registry["summary"]["listing_verified"], 3)
        self.assertEqual(registry["summary"]["listing_incomplete"], 0)
        self.assertEqual(registry["summary"]["listing_unverified"], 0)
        self.assertTrue(all(package["listing_check"]["status"] == "verified" for package in registry["packages"]))
        self.assertEqual(registry["summary"]["text_packages_verified"], 3)
        self.assertGreater(registry["summary"]["text_units_total"], 0)
        self.assertTrue((result.run_dir / "text" / imenu["package_id"] / "manifest.json").is_file())

        not_processed = " | ".join(registry["not_processed"])
        self.assertIn("ISO image is never rebuilt", not_processed)
        self.assertIn("volume id: SRW_OE_TEST", not_processed)
        self.assertIn("ZIP archive not processed", not_processed)
        self.assertIn("unrecognized signature", not_processed)
        self.assertEqual(registry["probe"]["naming_mode"], "original_name")
        self.assertEqual(registry["converter"]["io_mode"], "captured")
        iso_rows = [row for row in registry["inputs"] if row["content_type"] == "iso9660_pvd_signature"]
        self.assertEqual(iso_rows[0]["iso_facts"]["volume_identifier"], "SRW_OE_TEST")
        self.assertTrue(iso_rows[0]["iso_facts"]["size_matches_descriptor"])
        unknown_rows = [row for row in registry["inputs"] if row["content_type"] == "unknown_signature"]
        self.assertEqual(len(unknown_rows), 1)
        self.assertEqual(unknown_rows[0]["head_hex"], b"NOT A CONTAINER, unknown wrapper"[:32].hex(" "))
        self.assertTrue(all(row["head_hex"] is None for row in registry["inputs"] if row is not unknown_rows[0]))

        self.assertFalse((result.run_dir / "staging").exists())
        gates = result.run_dir / "gates"
        self.assertTrue(not gates.exists() or list(gates.iterdir()) == [])

    def test_boundary_probe_measures_the_text_exports_and_ships_in_the_bundle(self):
        self.write_standard_inputs()

        result, lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        boundary = registry["boundary_probe"]
        self.assertEqual(boundary["status"], "ok")
        self.assertEqual(boundary["totals"]["units"], registry["summary"]["text_units_total"])
        self.assertEqual(boundary["totals"]["offset_problems"], 0)
        self.assertEqual(boundary["totals"]["marker_mismatches"], 0)
        self.assertEqual(boundary["totals"]["prefix_mismatches"], 0)
        self.assertTrue(boundary["length_prefix"]["rows"])
        self.assertTrue(boundary["pointer_references"]["rows"])
        self.assertTrue(boundary["exports_probed"] >= registry["summary"]["text_packages_verified"])

        on_disk = json.loads((result.run_dir / "boundary_probe.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk["totals"]["units"], boundary["totals"]["units"])

        report = result.report_path.read_text(encoding="utf-8")
        self.assertIn("Boundary evidence", report)
        self.assertIn(f"units probed: {boundary['totals']['units']}", report)
        self.assertIn("no 1/2/4-byte field", report)  # the synthetic BIN stores no length prefix
        self.assertIn("boundary_probe.json", report)
        self.assertNotIn("\u65e5\u672c\u8a9e", report)  # no decoded game text in the report

        bundle = next(result.run_dir.glob("diagnostics_*.zip"))
        with zipfile.ZipFile(bundle) as archive:
            self.assertIn("boundary_probe.json", archive.namelist())
        self.assertTrue(any("Stage 8/9 boundary evidence" in line for line in lines))

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
        logs = sorted((result.run_dir / "logs" / "converter").glob("*.txt"))
        self.assertTrue(logs)
        for log in logs:
            log_text = log.read_text(encoding="utf-8")
            self.assertIn("command: ", log_text)
            self.assertNotIn(str(self.root), log_text)
            self.assertNotIn(str(self.input_root), log_text)
            self.assertNotIn(str(self.tool), log_text)
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
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("rejected probe: original_name/captured on ", report)
        self.assertIn("exit code 3", report)
        self.assertIn("error lines: not checked (console output is not captured)", report)
        self.assertIn("listing check (entries vs files): verified 3, incomplete 0, unverified 0, not checked 0", report)
        self.assertTrue(any("console mode" in warning for warning in registry["warnings"]))
        self.assertTrue(any("Completeness" in gap for gap in registry["known_gaps"]))

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

    def test_entries_that_share_a_name_fail_the_package_and_keep_no_partial_output(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_DUPLICATE_SUBSTRING": "event_P01"})

        self.assertEqual(result.status, "completed_with_failures")
        self.assertEqual(result.exit_code, 1)
        registry = self.registry(result)
        by_source = {package["source_path"]: package for package in registry["packages"]}
        event = by_source["event_P01.EDAT"]
        self.assertEqual(event["status"], "failed")
        self.assertEqual(event["listing_check"]["status"], "incomplete")
        self.assertEqual(event["listing_check"]["duplicate_entries"], 1)
        self.assertIn("listing check incomplete", event["error"])
        self.assertIn("share a name with another entry", event["error"])
        self.assertFalse((result.run_dir / event["output_dir"]).exists())
        # The fixture is a JSON stand-in, not a real @UTF CPK, so the table cannot be read here;
        # the step must record that without failing the run (see HiddenEntryTests for the real path).
        self.assertEqual(event["hidden_entries"]["status"], "unreadable_table")
        self.assertTrue((result.run_dir / "layout_probe.zip").is_file())
        self.assertEqual(self.registry(result)["summary"]["packages_failed"], 1)
        self.assertEqual(by_source["imenu01.EDAT"]["status"], "extracted")
        self.assertEqual(by_source["imenu01.EDAT"]["listing_check"]["status"], "verified")
        self.assertEqual(registry["summary"]["listing_incomplete"], 1)
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("listing check (entries vs files): verified 1, incomplete 1, unverified 0, not checked 0", report)
        self.assertIn("event_P01", " ".join(registry["failures"]))

    def test_narrow_single_space_listings_still_verify(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_NARROW_LISTING": "1"})

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertEqual(registry["summary"]["listing_verified"], 3)
        for package in registry["packages"]:
            check = package["listing_check"]
            self.assertEqual(check["status"], "verified")
            self.assertEqual(check["parse_modes"]["fallback"], check["entries"])
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("rows read with the single-space fallback:", report)

    def test_report_lists_unrecognized_inputs_by_head_bytes(self):
        self.write_standard_inputs()
        (self.input_root / "mystery2.EDAT").write_bytes(b"SECOND UNKNOWN WRAPPER")

        result, _lines = self.run_quietly()

        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("Unrecognized inputs (first 32 bytes, hex", report)
        self.assertIn(b"NOT A CONTAINER, unknown wrapper"[:32].hex(" "), report)
        self.assertIn(b"SECOND UNKNOWN WRAPPER"[:32].hex(" "), report)
        self.assertIn("unknown.EDAT", report)
        self.assertIn("mystery2.EDAT", report)

    def test_registry_copies_the_read_only_iso_inventory(self):
        self.write_standard_inputs()
        real_inventory = run_pipeline.inventory_path

        def patched_inventory(path):
            inventory = real_inventory(path)
            for entry in inventory["entries"]:
                if entry["content_type"] == "iso9660_pvd_signature":
                    entry["iso_inventory"] = {
                        "status": "indexed",
                        "file_count": 7,
                        "directory_count": 2,
                        "cpk_signature_count": 5,
                        "files": [],
                        "directories": [],
                        "warnings": [],
                    }
            return inventory

        with patch.object(run_pipeline, "inventory_path", patched_inventory):
            result, _lines = self.run_quietly()

        registry = self.registry(result)
        iso_rows = [row for row in registry["inputs"] if row["content_type"] == "iso9660_pvd_signature"]
        self.assertEqual(iso_rows[0]["iso_inventory"]["file_count"], 7)
        not_processed = " | ".join(registry["not_processed"])
        self.assertIn("read-only index: 7 files, 2 directories, 5 CPK signatures inside", not_processed)

    def test_report_notes_iso_member_extents_beyond_the_descriptor_volume(self):
        self.write_standard_inputs()
        real_inventory = run_pipeline.inventory_path

        def patched_inventory(path):
            inventory = real_inventory(path)
            for entry in inventory["entries"]:
                if entry["content_type"] == "iso9660_pvd_signature":
                    entry["iso_inventory"] = {
                        "status": "indexed",
                        "file_count": 7,
                        "directory_count": 2,
                        "cpk_signature_count": 5,
                        "extents_beyond_volume": 3,
                        "max_extent_overflow_bytes": 4096,
                        "image_bytes": 100000,
                        "volume_bytes": 90000,
                        "files": [],
                        "directories": [],
                        "warnings": [],
                    }
            return inventory

        with patch.object(run_pipeline, "inventory_path", patched_inventory):
            result, _lines = self.run_quietly()

        not_processed = " | ".join(self.registry(result)["not_processed"])
        self.assertIn(
            "3 member extents end beyond the PVD volume (max +4096 bytes; "
            "the file is 10000 bytes longer than its descriptor)",
            not_processed,
        )

    def test_report_shows_why_the_read_only_iso_index_failed(self):
        self.write_standard_inputs()
        real_inventory = run_pipeline.inventory_path

        def patched_inventory(path):
            inventory = real_inventory(path)
            for entry in inventory["entries"]:
                if entry["content_type"] == "iso9660_pvd_signature":
                    entry["iso_inventory"] = {
                        "status": "unsupported",
                        "error": "Multi-extent directories are unsupported",
                    }
            return inventory

        with patch.object(run_pipeline, "inventory_path", patched_inventory):
            result, _lines = self.run_quietly()

        not_processed = " | ".join(self.registry(result)["not_processed"])
        self.assertIn("read-only index failed: Multi-extent directories are unsupported", not_processed)

    def test_listings_without_an_id_column_verify_by_name_and_size(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_NO_ID_LISTING": "1"})

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertEqual(registry["summary"]["listing_verified"], 3)
        for package in registry["packages"]:
            check = package["listing_check"]
            self.assertEqual(check["status"], "verified")
            self.assertEqual(check["columns"][1:], ["Filesize", "Compressed", "%", "Contents Filename"])
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("listing layouts: 3 no ID column", report)

    def test_listings_without_a_filename_column_verify_by_count_and_sizes(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly({"FAKE_YACPK_NO_NAME_LISTING": "1"})

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertEqual(registry["summary"]["listing_verified"], 3)
        for package in registry["packages"]:
            check = package["listing_check"]
            self.assertEqual(check["status"], "verified")
            self.assertEqual(check["columns"][1:], ["ID", "Filesize", "Compressed", "%"])
            self.assertTrue(check["examples"]["file_name_examples"])
            self.assertTrue(all(name.startswith("ID") for name in check["examples"]["file_name_examples"]))
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("listing layouts: 3 no filename column (ID-named files)", report)

    def test_zero_byte_entries_with_comma_percent_still_verify(self):
        self.write_standard_inputs()
        (self.input_root / "hollow.EDAT").write_bytes(make_cpk({"empty.pac": b""}))

        result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        hollow = next(package for package in registry["packages"] if package["source_path"] == "hollow.EDAT")
        self.assertEqual(hollow["listing_check"]["status"], "verified")
        self.assertEqual(hollow["listing_check"]["entries"], 1)

    def test_table_check_unreadable_for_synthetic_containers_is_reported(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        for package in registry["packages"]:
            self.assertEqual(package["table_check"]["status"], "unreadable")
        self.assertEqual(registry["summary"]["table_unreadable"], 3)
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn(
            "CPK table check (TOC vs listing, report-only): agree 0, mismatch 0, unreadable 3, no listing 0",
            report,
        )
        csv_text = (result.run_dir / "packages.csv").read_text(encoding="utf-8")
        self.assertIn("table_status", csv_text.splitlines()[0])
        self.assertIn("unreadable", csv_text)

    def test_table_check_agree_results_are_recorded_and_reported(self):
        self.write_standard_inputs()

        def fake_table_check(source, listing_text):
            return {
                "status": "agree",
                "entries": 2,
                "unique_names": 2,
                "duplicate_entries": 0,
                "compressed_entries": 0,
                "header_files": 2,
                "problems": [],
            }

        with patch.object(run_pipeline, "table_check", fake_table_check):
            result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertEqual(registry["summary"]["table_agree"], 3)
        for package in registry["packages"]:
            self.assertEqual(package["table_check"]["status"], "agree")
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("agree 3, mismatch 0, unreadable 0, no listing 0", report)

    def test_table_check_mismatch_is_reported_without_failing_the_run(self):
        self.write_standard_inputs()

        def fake_table_check(source, listing_text):
            return {
                "status": "mismatch",
                "entries": 2,
                "unique_names": 2,
                "duplicate_entries": 0,
                "compressed_entries": 0,
                "header_files": 2,
                "problems": ["row 0: listing size 4 != TOC ExtractSize 3"],
            }

        with patch.object(run_pipeline, "table_check", fake_table_check):
            result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertEqual(registry["summary"]["table_mismatch"], 3)
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("CPK table check mismatches (report-only; up to 3 shown)", report)
        self.assertIn("listing size 4 != TOC ExtractSize 3", report)

    def _iso_member(self, size):
        return {
            "path": "PSP_GAME/USRDIR/disc00.cpk;1",
            "size_bytes": size,
            "content_type": "cpk_signature",
            "extent_count": 1,
            "extents": [
                {"lba": 22, "extended_attribute_blocks": 0, "offset_bytes": 22 * 2048, "length_bytes": size}
            ],
        }

    def _patched_iso_inventory(self, member):
        real_inventory = run_pipeline.inventory_path

        def patched_inventory(path):
            inventory = real_inventory(path)
            for entry in inventory["entries"]:
                if entry["content_type"] == "iso9660_pvd_signature":
                    entry["iso_inventory"] = {
                        "status": "indexed",
                        "file_count": 1,
                        "directory_count": 1,
                        "cpk_signature_count": 1,
                        "files": [member],
                        "directories": [],
                        "warnings": [],
                        "extents_beyond_volume": 0,
                        "max_extent_overflow_bytes": 0,
                        "last_extent_end_bytes": 0,
                        "trailing_bytes_after_last_extent": 0,
                        "image_bytes": 0,
                        "volume_bytes": 0,
                    }
            return inventory

        return patched_inventory

    def test_iso_cpk_members_are_extracted_read_only_and_processed(self):
        self.write_standard_inputs()
        # Distinct content, so the disc member is not deduplicated against the loose files.
        iso_cpk = make_cpk({"disc00.bin": self.bin_data, "note.txt": b"disc member"})
        member = self._iso_member(len(iso_cpk))

        def fake_extract(image, members, output_root):
            target = output_root / "PSP_GAME" / "USRDIR" / "disc00.cpk"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(iso_cpk)
            return [
                {
                    "member_path": member["path"],
                    "target": target,
                    "size_bytes": len(iso_cpk),
                }
            ]

        with patch.object(run_pipeline, "inventory_path", self._patched_iso_inventory(member)), patch.object(
            run_pipeline.iso9660, "extract_members", fake_extract
        ):
            result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        iso_packages = [p for p in registry["packages"] if p["source_path"].startswith("iso/")]
        self.assertEqual(len(iso_packages), 1)
        self.assertTrue(iso_packages[0]["source_path"].startswith("iso/base_game/"))
        self.assertTrue(iso_packages[0]["source_path"].endswith("disc00.cpk"))
        self.assertEqual(iso_packages[0]["status"], "extracted")
        self.assertEqual(iso_packages[0]["listing_check"]["status"], "verified")
        self.assertEqual(registry["summary"]["iso_members_extracted"], 1)
        self.assertEqual(registry["input"]["iso_cpk_member_count"], 1)
        report = Path(result.report_path).read_text(encoding="utf-8")
        self.assertIn("1 CPK-signature members extracted read-only into iso/", report)
        self.assertIn("ISO members extracted read-only: 1", report)
        self.assertTrue((result.run_dir / "iso").is_dir())

    def test_unsupported_iso_index_extracts_nothing_and_does_not_fail(self):
        self.write_standard_inputs()

        result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        self.assertFalse([p for p in registry["packages"] if p["source_path"].startswith("iso/")])
        self.assertEqual(registry["summary"]["iso_members_extracted"], 0)
        self.assertIn("ISO image is never rebuilt", " | ".join(registry["not_processed"]))

    def test_iso_member_extraction_failure_fails_the_run_closed(self):
        self.write_standard_inputs()
        member = self._iso_member(10)

        def broken_extract(image, members, output_root):
            raise run_pipeline.iso9660.Iso9660Error("boom")

        with patch.object(run_pipeline, "inventory_path", self._patched_iso_inventory(member)), patch.object(
            run_pipeline.iso9660, "extract_members", broken_extract
        ):
            result, _lines = self.run_quietly()

        self.assertEqual(result.status, "error")
        self.assertTrue(any("boom" in failure for failure in self.registry(result)["failures"]))

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

    def test_repack_gate_skips_packages_whose_members_are_all_empty(self):
        self.write_standard_inputs()
        (self.input_root / "hollow.EDAT").write_bytes(make_cpk({"empty.pac": b""}))

        result, _lines = self.run_quietly()

        self.assertEqual(result.status, "completed")
        registry = self.registry(result)
        hollow = next(package for package in registry["packages"] if package["source_path"] == "hollow.EDAT")
        self.assertEqual(hollow["status"], "extracted")
        self.assertEqual(hollow["total_member_bytes"], 0)
        self.assertEqual(hollow["listing_check"]["status"], "verified")
        self.assertEqual(registry["gate"]["status"], "passed")
        self.assertNotEqual(registry["gate"]["package_id"], hollow["package_id"])

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
        # A cache hit legitimately removes converter calls; compare against a fresh cache.
        shutil.rmtree(self.output_base / "_cache", ignore_errors=True)
        second, _ = self.run_quietly(run_id="second-run")
        keys = ("probe", "inputs", "packages", "gate", "not_processed", "failures", "summary")
        first_registry, second_registry = self.registry(first), self.registry(second)
        # The second run may legitimately restore packages from the first run's verified cache;
        # that flag is the only package field allowed to differ.
        for registry in (first_registry, second_registry):
            for package in registry["packages"]:
                package.pop("restored_from_cache", None)
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


class VerifiedCacheTests(PipelineFixture):
    def comparable(self, result) -> list:
        registry = self.registry(result)
        return sorted(
            (
                package["source_path"],
                package["status"],
                package["member_count"],
                (package.get("listing_check") or {}).get("status"),
                (package.get("text") or {}).get("units"),
            )
            for package in registry["packages"]
        )

    def test_second_run_restores_verified_packages_and_matches_the_first(self):
        self.write_standard_inputs()
        first, _ = self.run_quietly()
        first_calls = len(self.calls())
        second, lines = self.run_quietly()
        second_calls = len(self.calls()) - first_calls

        self.assertEqual(second.status, "completed")
        self.assertLess(second_calls, first_calls)
        self.assertTrue(any("restored from the verified cache" in line for line in lines))
        self.assertEqual(self.comparable(first), self.comparable(second))
        restored = [p for p in self.registry(second)["packages"] if p["restored_from_cache"]]
        self.assertTrue(restored)

    def test_tampered_cache_entry_is_not_used_and_the_package_is_extracted_again(self):
        self.write_standard_inputs()
        first, _ = self.run_quietly()
        cache = self.output_base / "_cache"
        victims = sorted(cache.rglob("tree/*.bin"))
        self.assertTrue(victims)
        tampered_sha = victims[0].relative_to(cache).parts[1]
        victims[0].write_bytes(b"tampered")

        second, lines = self.run_quietly()

        self.assertEqual(second.status, "completed")
        self.assertEqual(self.comparable(first), self.comparable(second))
        packages = self.registry(second)["packages"]
        tampered = [p for p in packages if p["source_sha256"] == tampered_sha]
        self.assertTrue(tampered)
        self.assertFalse(any(p["restored_from_cache"] for p in tampered))
        self.assertTrue(any(p["restored_from_cache"] for p in packages if p["source_sha256"] != tampered_sha))
        self.assertTrue(any("not used" in line or "restored" in line for line in lines))

class UnitHelperTests(unittest.TestCase):
    def test_listing_parser_reads_rows_with_u_fffd_and_space_separators(self):
        parsed = run_pipeline.parse_listing(synthetic_listing([(0, "a.acb", 5), (7, "sub/b c.acb", 187808)]))
        self.assertEqual(parsed["header_count"], 2)
        self.assertEqual(parsed["header_total"], 187813)
        self.assertEqual([(entry["id"], entry["size"], entry["name"]) for entry in parsed["entries"]],
                         [(0, 5, "a.acb"), (7, 187808, "sub/b c.acb")])
        spaced = synthetic_listing([(1, "x.acb", 1234567)]).replace("\ufffd", " ")
        self.assertEqual(run_pipeline.parse_listing(spaced)["entries"][0]["size"], 1234567)
        self.assertIsNone(run_pipeline.parse_listing(""))
        self.assertIsNone(run_pipeline.parse_listing(None))

    def test_listing_check_verifies_one_file_per_entry_and_fails_closed(self):
        def files(*names):
            return [{"path": name} for name in names]

        plain = [(0, "a.acb", 5), (1, "b.acb", 187808)]
        self.assertEqual(run_pipeline.check_listing(synthetic_listing(plain), files("a.acb", "b.acb"))["status"], "verified")
        nested = run_pipeline.check_listing(synthetic_listing([(0, "sub/c.cpk", 9)]), files("sub\\c.cpk"))
        self.assertEqual(nested["status"], "verified")

        shared = [(0, "a.acb", 5), (1, "a.acb", 5), (2, "b.acb", 187808)]
        duplicate = run_pipeline.check_listing(synthetic_listing(shared), files("a.acb", "b.acb"))
        self.assertEqual(duplicate["status"], "incomplete")
        self.assertEqual(duplicate["duplicate_entries"], 1)
        self.assertEqual(duplicate["entries"], 3)
        self.assertIn("1 of 3 entries share a name", duplicate["reason"])

        self.assertEqual(run_pipeline.check_listing(synthetic_listing(plain), files("a.acb"))["status"], "incomplete")
        extra = run_pipeline.check_listing(synthetic_listing(plain), files("a.acb", "b.acb", "c.acb"))
        self.assertEqual(extra["status"], "incomplete")
        self.assertEqual(extra["files_not_listed"], 1)

        broken_row = synthetic_listing(plain).replace(
            "Process finished", "[    2]      3  x  100,00  c.acb\r\r\nProcess finished"
        )
        unreadable = run_pipeline.check_listing(broken_row, files("a.acb", "b.acb"))
        self.assertEqual(unreadable["status"], "unverified")
        self.assertIn("1 listing rows could not be read", unreadable["reason"])
        undecoded = run_pipeline.check_listing(synthetic_listing([(0, "a\ufffd.acb", 5)]), files("a\ufffd.acb"))
        self.assertEqual(undecoded["status"], "unverified")
        self.assertIn("could not be decoded", undecoded["reason"])
        self.assertEqual(run_pipeline.check_listing(None, files("a.acb"))["status"], "unverified")
        no_header = synthetic_listing(plain).replace("Content files:2\r\r\n", "")
        self.assertEqual(run_pipeline.check_listing(no_header, files("a.acb", "b.acb"))["status"], "unverified")
        short_header = synthetic_listing(plain).replace("Content files:2", "Content files:3")
        self.assertEqual(run_pipeline.check_listing(short_header, files("a.acb", "b.acb"))["status"], "unverified")
        bad_total = synthetic_listing(plain).replace(f"Content file size:{grouped_number(187813)}", "Content file size:1")
        self.assertEqual(run_pipeline.check_listing(bad_total, files("a.acb", "b.acb"))["status"], "unverified")

    def test_listing_parser_falls_back_to_single_space_gaps_for_narrow_columns(self):
        narrow = (
            "CPK Filename:narrow.EDAT\r\r\n"
            "Content files:2\r\r\n"
            f"Content file size:{grouped_number(187813)}\r\r\n"
            "Compressed files:0\r\r\n"
            "\r\r\n"
            "No.         ID    Filesize  Compressed       %  Contents Filename\r\r\n"
            f"[    0]      1  {grouped_number(5)} {grouped_number(5)}  100,00  a.acb\r\r\n"
            f"[    1]      2  {grouped_number(187808)} {grouped_number(187808)}  100,00  b.acb\r\r\n"
            "Process finished (hopefully) without issues!\r\r\n"
        )
        parsed = run_pipeline.parse_listing(narrow)
        self.assertEqual(parsed["header_count"], 2)
        self.assertEqual(parsed["header_total"], 187813)
        self.assertEqual(parsed["unparsed_rows"], 0)
        self.assertEqual(parsed["parse_modes"], {"strict": 0, "fallback": 2})
        self.assertEqual(
            [(entry["id"], entry["size"], entry["name"]) for entry in parsed["entries"]],
            [(1, 5, "a.acb"), (2, 187808, "b.acb")],
        )
        # A row whose numbers cannot be split into two readable values stays unparsed and is kept raw.
        broken = narrow.replace(
            f"[    1]      2  {grouped_number(187808)} {grouped_number(187808)}  100,00  b.acb",
            "[    1]      2  x y  100,00  b.acb",
        )
        parsed_broken = run_pipeline.parse_listing(broken)
        self.assertEqual(parsed_broken["unparsed_rows"], 1)
        self.assertEqual(parsed_broken["unparsed_row_lines"], ["[    1]      2  x y  100,00  b.acb"])
        # Two numbers that each contain a space separator are ambiguous and stay unparsed (fail closed).
        ambiguous = narrow.replace(
            f"[    0]      1  {grouped_number(5)} {grouped_number(5)}  100,00  a.acb",
            "[    0]      1  1 234 5 678  100,00  a.acb",
        )
        self.assertEqual(run_pipeline.parse_listing(ambiguous)["unparsed_rows"], 1)

    def test_listing_check_keeps_raw_examples_for_unreadable_rows_and_missing_headers(self):
        def files(*names):
            return [{"path": name} for name in names]

        plain = [(0, "a.acb", 5), (1, "b.acb", 187808)]
        broken = synthetic_listing(plain).replace(
            "Process finished", "[    2]      3  x  100,00  c.acb\r\r\nProcess finished"
        )
        unreadable = run_pipeline.check_listing(broken, files("a.acb", "b.acb"))
        self.assertEqual(unreadable["status"], "unverified")
        self.assertEqual(unreadable["examples"]["unparsed_rows"], ["[    2]      3  x  100,00  c.acb"])
        self.assertEqual(unreadable["examples"]["listing_head"][0], "CPK Filename:synthetic.EDAT")
        no_header = synthetic_listing(plain).replace("Content files:2\r\r\n", "")
        missing = run_pipeline.check_listing(no_header, files("a.acb", "b.acb"))
        self.assertEqual(missing["status"], "unverified")
        self.assertIn("listing has no 'Content files' line", missing["reason"])
        self.assertTrue(missing["examples"]["listing_head"])
        undecoded = run_pipeline.check_listing(synthetic_listing([(0, "a\ufffd.acb", 5)]), files("a\ufffd.acb"))
        self.assertEqual(undecoded["examples"]["undecodable_names"], ["a\ufffd.acb"])

    def test_listing_parser_reads_the_three_real_column_layouts(self):
        entries = [(0, "a.acb", 5), (7, "sub/b c.acb", 187808)]
        full = run_pipeline.parse_listing(synthetic_listing_layout(entries))
        self.assertEqual(full["columns"], ["No.", "ID", "Filesize", "Compressed", "%", "Contents Filename"])
        self.assertEqual(
            [(entry["id"], entry["size"], entry["name"]) for entry in full["entries"]],
            [(0, 5, "a.acb"), (7, 187808, "sub/b c.acb")],
        )
        no_id = run_pipeline.parse_listing(synthetic_listing_layout(entries, drop_id=True))
        self.assertEqual(no_id["columns"], ["No.", "Filesize", "Compressed", "%", "Contents Filename"])
        self.assertEqual(
            [(entry["size"], entry["name"]) for entry in no_id["entries"]],
            [(5, "a.acb"), (187808, "sub/b c.acb")],
        )
        self.assertNotIn("id", no_id["entries"][0])
        no_name = run_pipeline.parse_listing(synthetic_listing_layout(entries, drop_name=True))
        self.assertEqual(no_name["columns"], ["No.", "ID", "Filesize", "Compressed", "%"])
        self.assertEqual([(entry["id"], entry["size"]) for entry in no_name["entries"]], [(0, 5), (7, 187808)])
        self.assertNotIn("name", no_name["entries"][0])
        # A 0-byte entry prints its percent as ",00" (seen in the real mesbtl09 listing).
        zero = run_pipeline.parse_listing(synthetic_listing_layout([(0, "p0000.pac", 0)]))
        self.assertEqual(zero["entries"][0]["size"], 0)
        self.assertEqual(zero["entries"][0]["percent"], ",00")
        self.assertEqual(zero["compressed_files"], 0)
        self.assertEqual(zero["filename_info"], "True")
        self.assertEqual(zero["id_info"], "True")
        # A thousands separator inside the Content files count (seen in the real robo01
        # listing: "Content files:1?711") still reads as the row count.
        grouped_count = synthetic_listing_layout([(index, f"f{index}.bin", 10) for index in range(12)]).replace(
            "Content files:12", "Content files:1\ufffd2"
        )
        parsed = run_pipeline.parse_listing(grouped_count)
        self.assertEqual(parsed["header_count"], 12)
        self.assertEqual(len(parsed["entries"]), 12)
        self.assertEqual(parsed["unparsed_rows"], 0)

    def test_listing_check_verifies_id_named_packages_by_count_and_sizes(self):
        def members(*pairs):
            return [{"path": name, "size_bytes": size} for name, size in pairs]

        entries = [(0, "a.acb", 5), (3, "b.acb", 187808)]
        listing = synthetic_listing_layout(entries, drop_name=True)
        ok = run_pipeline.check_listing(listing, members(("ID00000", 5), ("ID00003", 187808)))
        self.assertEqual(ok["status"], "verified")
        self.assertEqual(ok["entries"], 2)
        self.assertEqual(ok["examples"]["file_name_examples"], ["ID00000", "ID00003"])
        self.assertEqual(ok["examples"]["listed_id_examples"], [0, 3])
        short = run_pipeline.check_listing(listing, members(("ID00000", 5)))
        self.assertEqual(short["status"], "incomplete")
        self.assertIn("the folder holds 1 files for 2 listed entries", short["reason"])
        wrong_size = run_pipeline.check_listing(listing, members(("ID00000", 5), ("ID00003", 1)))
        self.assertEqual(wrong_size["status"], "incomplete")
        self.assertIn("the file sizes do not match the listed entry sizes", wrong_size["reason"])

    def test_listing_check_fails_a_file_whose_size_differs_and_reports_decoded_name_matches(self):
        def files(*pairs):
            return [{"path": name, "size_bytes": size} for name, size in pairs]

        plain = [(0, "a.acb", 5), (1, "b.acb", 187808)]
        wrong = run_pipeline.check_listing(synthetic_listing(plain), files(("a.acb", 5), ("b.acb", 1)))
        self.assertEqual(wrong["status"], "incomplete")
        self.assertEqual(wrong["size_mismatches"], 1)
        self.assertIn("1 files differ in size from their listed entry", wrong["reason"])
        undecoded = run_pipeline.check_listing(synthetic_listing([(0, "a\ufffd.acb", 5)]), files(("a\ufffd.acb", 5)))
        self.assertEqual(undecoded["status"], "unverified")
        self.assertIn("could not be decoded", undecoded["reason"])
        self.assertIn("1 of 1 listed names matched a file by name", undecoded["reason"])

    def test_hidden_lines_report_the_crilayla_counts_and_the_uncompressed_writes(self):
        registry = {
            "packages": [
                {
                    "package_id": "p001-bacb01",
                    "source_path": "bacb01.EDAT",
                    "hidden_entries": {
                        "status": "extracted",
                        "entries": 10,
                        "written": 4,
                        "written_bytes": 400,
                        "compressed": 5,
                        "no_offset": 1,
                        "listing_sizes_match": True,
                        "crilayla": {"attempted": 3, "decoded": 2, "failed": 1},
                        "text": {"status": "exported_verified"},
                    },
                },
                {
                    "package_id": "p002-face01",
                    "source_path": "face01.EDAT",
                    "hidden_entries": {
                        "status": "no_offsets",
                        "reason": "the table stores no data offsets (ITOC blob layout)",
                    },
                },
            ]
        }
        lines = run_pipeline._hidden_lines(registry)
        self.assertEqual(len(lines), 2)
        self.assertIn("4 of 10 uncompressed entries written (400 bytes)", lines[0])
        self.assertIn("5 compressed (2 CRILAYLA decoded, 1 failed, 2 not CRILAYLA)", lines[0])
        self.assertIn("listing sizes match: True", lines[0])
        self.assertIn("no_offsets: the table stores no data offsets", lines[1])

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
        crash = run_pipeline.converter_failure(call("", returncode=3762504530), expect_finished=True)
        self.assertIn("3762504530 (0xE0434352, unhandled .NET (CLR) exception)", crash)
        self.assertEqual(run_pipeline.describe_exit_code(-532462766), run_pipeline.describe_exit_code(3762504530))
        self.assertEqual(run_pipeline.describe_exit_code(3), "3")

    def test_iso_facts_read_the_primary_volume_descriptor_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            image = Path(temporary) / "game.iso"
            image.write_bytes(synthetic_iso())
            facts = run_pipeline._iso_facts(image, image.stat().st_size)
        self.assertTrue(facts["primary_volume_descriptor_found"])
        self.assertEqual(facts["volume_identifier"], "SRW_OE_TEST")
        self.assertEqual(facts["volume_space_blocks"], 17)
        self.assertTrue(facts["size_matches_descriptor"])
        self.assertEqual(facts["descriptor_bytes"], 17 * 2048)
        mismatch = dict(facts, size_matches_descriptor=False, file_bytes=17 * 2048 + 5)
        self.assertIn(
            f"size matches descriptor: no (descriptor {17 * 2048} bytes, file {17 * 2048 + 5} bytes)",
            run_pipeline._iso_summary(mismatch),
        )
        self.assertNotIn("bytes", run_pipeline._iso_summary(facts))

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


class ProbeLauncherTests(unittest.TestCase):
    def test_probe_launcher_reuses_the_saved_folders_and_never_calls_the_converter(self):
        path = BAT_PATH.parent / "RUN_PROBE.bat"
        self.assertTrue(path.is_file())
        lowered = path.read_text(encoding="utf-8").lower()
        self.assertIn('cd /d "%~dp0"', lowered)
        self.assertIn("py -3", lowered)
        self.assertIn("tools\\boundary_probe.py", lowered)
        self.assertIn("pause", lowered)
        self.assertIn("run_pipeline.bat", lowered)  # it points back at the full run
        self.assertNotIn("yacpktool", lowered)
        self.assertNotIn("pip install", lowered)

    def test_probe_launcher_asks_for_a_folder_when_the_probe_finds_none(self):
        # A fresh download has no config/local-workflow.ini (it is private and git-ignored), so the
        # automatic lookup finds nothing; the launcher must then ask instead of just stopping.
        text = (BAT_PATH.parent / "RUN_PROBE.bat").read_text(encoding="utf-8")
        self.assertIn('if not "%RESULT%"=="2" goto :finish', text)
        self.assertIn('set /p "RUNDIR=Run folder: "', text)
        self.assertIn("%PY% tools\\boundary_probe.py %RUNDIR%", text)
        self.assertIn("drag the run folder", text.lower())
        self.assertIn("exit /b %RESULT%", text)  # the retry's exit code is the one reported


class HiddenEntryTests(unittest.TestCase):
    """Colliding names are read from a real @UTF CPK by TOC index, so none overwrites another."""

    def test_entries_that_share_a_name_are_all_written_with_their_own_bytes(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import test_cpk_table  # noqa: E402  (synthetic CPK builder, no game data)

        blob = test_cpk_table.build_synthetic_cpk(
            [
                {"dir": "", "name": "dup.bin", "data": b"A" * 100, "id": 1},
                {"dir": "", "name": "dup.bin", "data": b"B" * 50, "id": 2},
                {"dir": "", "name": "other.txt", "data": b"C" * 10, "id": 3},
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cpk = root / "pkg.cpk"
            cpk.write_bytes(blob)
            run = run_pipeline.Run.__new__(run_pipeline.Run)
            run.run_dir = root / "run"
            run.run_dir.mkdir()
            run.text_dir = run.run_dir / "text"
            run.say = lambda *_args: None
            item = run_pipeline.WorkItem(
                path=cpk,
                display_path="pkg.cpk",
                name="pkg.cpk",
                sha256="0" * 64,
                size=len(blob),
                depth=0,
                parent_package=None,
            )
            hidden = run._extract_hidden_entries(item, "p001", None)
            written = sorted((run.run_dir / "hidden" / "p001").iterdir())
            payloads = sorted(path.read_bytes() for path in written)

        self.assertEqual(hidden["status"], "extracted", hidden)
        self.assertEqual(hidden["entries"], 3)
        self.assertEqual(hidden["written"], 3)
        self.assertEqual(hidden["written_bytes"], 160)
        self.assertEqual(hidden["compressed"], 0)
        self.assertIsNone(hidden["listing_sizes_match"])
        self.assertEqual(payloads, sorted([b"A" * 100, b"B" * 50, b"C" * 10]))
        self.assertEqual([path.name.split("_")[0] for path in written], ["00000", "00001", "00002"])


if __name__ == "__main__":
    unittest.main()
