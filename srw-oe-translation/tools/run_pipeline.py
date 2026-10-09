#!/usr/bin/env python3
"""One-click local run: unpack CPK containers, export and verify event text, write reports.

Entry points: RUN_PIPELINE.bat (Windows, double-click) or `python tools/run_pipeline.py`.
After a one-time folder setup, every stage runs automatically:

  1. setup: read config/local-workflow.ini; ask for folders with dialogs only when missing
  2. inventory: content-based SHA-256 and signature inventory of the input folder
  3. preflight: converter identity, output-path safety, free space, overlap checks
  4. probe: find a converter mode that extracts the smallest CPK. The original file name is
     tried first; a `.cpk` alias is made only inside the disposable staging folder and only
     if the original name is rejected. Captured and console I/O are both tried.
  5. extract: every unique CPK (and nested CPKs up to MAX_NESTED_DEPTH) into a fresh run folder
  6. text: export and verify event text for every BIN in each extracted package
  7. gate: repack the smallest package and check that its member hashes reproduce
  8. report: registry.json, inputs.csv, packages.csv, REPORT.txt, and logs

Safety rules: the input folder is never written (before/after tree snapshot); source hashes are
checked before and after each converter call; ISO images are reported but not processed;
the registry and report never contain decoded game text; nothing is inserted or repacked
into the game. The converter's exit code is not trusted alone because YACpkTool reports
many errors as plain console text with exit code 0.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import struct
import subprocess
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

TOOLS_DIR = Path(__file__).resolve().parent
SRW_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

import extract_cpk_batch  # noqa: E402  (converter discovery, shared with the dry-run driver)
import extract_event_text  # noqa: E402  (text export, verification, read-back)
from inventory_local_inputs import inventory_path  # noqa: E402

RUN_SCHEMA = "srw-oe-local-run/1"
DEFAULT_CONFIG = SRW_ROOT / "config" / "local-workflow.ini"
CHUNK_SIZE = 1024 * 1024
TOOL_TIMEOUT_SECONDS = 1800
MAX_NESTED_DEPTH = 2
PROBE_CANDIDATE_LIMIT = 3
PROBE_ORDER = (
    ("original_name", "captured"),
    ("original_name", "console"),
    ("cpk_alias", "captured"),
    ("cpk_alias", "console"),
)
FREE_SPACE_FACTOR = 3
FREE_SPACE_MARGIN_BYTES = 512 * 1024 * 1024
MAX_PATH_CHARS = 200
ERROR_LINE_RE = re.compile(r"^\s*Error:", re.IGNORECASE | re.MULTILINE)
CRASH_RE = re.compile(r"unhandled exception|System\.[A-Za-z.]*Exception", re.IGNORECASE)
FINISHED_TEXT = "Process finished"
WINDOWS_EXIT_CODE_LABELS = {0xE0434352: "unhandled .NET (CLR) exception"}
WINDOWS_SAFE_PATH_RE = re.compile(r"[A-Za-z]:\\(?:[A-Za-z0-9._~-]+\\)*[A-Za-z0-9._~-]*")
POSIX_SAFE_PATH_RE = re.compile(r"/(?:[A-Za-z0-9._~-]+/)*[A-Za-z0-9._~-]*")
SHA256_RE = re.compile(r"[0-9a-f]{64}")

KNOWN_GAPS = (
    "ISO adapter: not implemented; ISO images are reported (PVD facts) but never unpacked.",
    "Repack and write-back: disabled; the repack gate only checks CPK member round trips.",
    "Completeness: extracted files are not yet compared with each package's listing (-L); a partial "
    "extraction that exits 0 without an Error: line is not detected.",
    "Event text boundaries: unvalidated; units are heuristic candidates, not confirmed strings.",
    "Translation insertion: not implemented; no translated text is produced or applied.",
    "In-game verification: not performed; nothing here is a playable patch.",
)


class SetupError(Exception):
    """Configuration or environment problem that stops the run before any work starts."""


class UnsafePathError(ValueError):
    """A path that YACpkTool's output-path validation would reject."""


@dataclass
class Settings:
    input_root: Optional[Path] = None
    output_base: Optional[Path] = None
    tool_path: Optional[Path] = None
    expected_tool_sha256: Optional[str] = None


@dataclass
class Candidate:
    relpath: str
    path: Path
    name: str
    size: int
    sha256: str


@dataclass
class ConverterCall:
    label: str
    io_mode: str
    command: list[str]
    returncode: Optional[int]
    timed_out: bool
    output: Optional[str]
    error: Optional[str]
    seconds: float


@dataclass
class WorkItem:
    path: Path
    display_path: str
    name: str
    sha256: str
    size: int
    depth: int
    parent_package: Optional[str]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_stem(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).stem).strip("._")
    return cleaned[:40] or "cpk"


def _is_converter_safe(text: str) -> bool:
    return bool(WINDOWS_SAFE_PATH_RE.fullmatch(text) or POSIX_SAFE_PATH_RE.fullmatch(text))


def _windows_short_name(path: Path) -> Optional[str]:
    """Return the 8.3 form of an existing Windows path (ASCII, no spaces), if available."""
    if os.name != "nt":
        return None
    import ctypes

    buffer = ctypes.create_unicode_buffer(32768)
    length = ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, len(buffer))  # type: ignore[attr-defined]
    if 0 < length < len(buffer):
        return buffer.value
    return None


def converter_argument_path(
    path: Path, short_name: Callable[[Path], Optional[str]] = _windows_short_name
) -> str:
    """Return a path string that YACpkTool's `-o` validation accepts.

    YACpkTool checks output paths with Uri.IsWellFormedUriString, which rejects spaces and
    non-ASCII characters. Input paths are not checked. When the planned output path is not
    safe, the 8.3 short name of its nearest existing ancestor is used instead.
    """
    text = str(path)
    if _is_converter_safe(text) and len(text) <= MAX_PATH_CHARS:
        return text
    existing = path
    tail: list[str] = []
    while not existing.exists() and existing.parent != existing:
        tail.insert(0, existing.name)
        existing = existing.parent
    short = short_name(existing) if existing.exists() else None
    if short:
        candidate = str(Path(short, *tail))
        if _is_converter_safe(candidate) and len(candidate) <= MAX_PATH_CHARS:
            return candidate
    raise UnsafePathError(
        "path cannot be passed to the converter: it must be a local drive path (e.g. C:\\SRW_OE_out) "
        "without spaces, non-ASCII letters, or UNC share names, and must be short enough: "
        f"{path}"
    )


def _leaf_name(member_path: str) -> str:
    """Last component of a forward-slash member path from the registry or the input inventory."""
    return member_path.rsplit("/", 1)[-1]


def _free_bytes(path: Path) -> int:
    probe = path
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    return shutil.disk_usage(probe).free


def _tree_snapshot(root: Path) -> dict[str, tuple]:
    """Names, types, sizes, and mtimes below root; used to prove the input was not written."""
    snapshot: dict[str, tuple] = {".": ("dir", root.stat().st_mtime_ns)}
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in sorted(directory_names + file_names):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            try:
                info = path.lstat()
            except OSError:
                snapshot[relative] = ("unreadable",)
                continue
            if stat.S_ISLNK(info.st_mode):
                snapshot[relative] = ("symlink", info.st_mtime_ns)
            elif stat.S_ISDIR(info.st_mode):
                snapshot[relative] = ("dir", info.st_mtime_ns)
            else:
                snapshot[relative] = ("file", info.st_size, info.st_mtime_ns)
    return snapshot


def _snapshot_changes(before: dict[str, tuple], after: dict[str, tuple]) -> list[str]:
    changed = set(before) ^ set(after)
    changed.update(key for key in before if key in after and before[key] != after[key])
    return sorted(changed)


def _has_regular_files(folder: Path) -> bool:
    if not folder.is_dir():
        return False
    for current, _directory_names, file_names in os.walk(folder, followlinks=False):
        for name in file_names:
            path = Path(current, name)
            if not path.is_symlink() and path.is_file():
                return True
    return False


def describe_exit_code(code: int) -> str:
    """Exit code as text. Windows crash codes are large unsigned numbers, so they also get hex."""
    value = code & 0xFFFFFFFF if code < 0 else code
    if value < 0x80000000:
        return str(value)
    label = WINDOWS_EXIT_CODE_LABELS.get(value, "Windows exception or error code")
    return f"{value} (0x{value:08X}, {label})"


def converter_failure(call: ConverterCall, *, expect_finished: bool) -> Optional[str]:
    """Judge one converter call. Exit code 0 is not enough: YACpkTool prints `Error:` lines."""
    if call.error:
        return f"could not start converter: {call.error}"
    if call.timed_out:
        return "converter timed out"
    if call.returncode != 0:
        return f"converter exit code {describe_exit_code(call.returncode)}"
    if call.output is not None:
        if ERROR_LINE_RE.search(call.output):
            return "converter printed an Error: line"
        if CRASH_RE.search(call.output):
            return "converter printed an unhandled exception"
        if expect_finished and FINISHED_TEXT not in call.output:
            return "converter did not reach its final message"
    return None


def _member_entries(folder: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    inventory = inventory_path(folder)
    members = [
        {
            "path": entry["path"],
            "size_bytes": entry["size_bytes"],
            "sha256": entry["sha256"],
            "content_type": entry["content_type"],
        }
        for entry in inventory["entries"]
        if entry["sha256"] is not None
    ]
    return members, inventory["errors"]


def _iso_summary(facts: dict[str, Any]) -> str:
    if not facts.get("primary_volume_descriptor_found"):
        return f"container: {facts.get('container')}; no ISO 9660 primary volume descriptor at sector 16"
    text = (
        f"container: {facts['container']}; volume id: {facts.get('volume_identifier') or '(empty)'}; "
        f"size matches descriptor: {'yes' if facts.get('size_matches_descriptor') else 'no'}"
    )
    if not facts.get("size_matches_descriptor"):
        text += f" (descriptor {facts.get('descriptor_bytes')} bytes, file {facts.get('file_bytes')} bytes)"
    return text


def _iso_facts(path: Path, size: int) -> dict[str, Any]:
    """Read-only ISO 9660 primary-volume facts for the report. No ISO is unpacked."""
    facts: dict[str, Any] = {"container": "unknown", "primary_volume_descriptor_found": False}
    with path.open("rb") as stream:
        head = stream.read(4)
        if head == b"CISO":
            facts["container"] = "ciso (compressed ISO)"
        stream.seek(16 * 2048)
        descriptor = stream.read(2048)
    if descriptor[:7] == b"\x01CD001\x01" and len(descriptor) == 2048:
        facts["container"] = "iso9660" if facts["container"] == "unknown" else facts["container"]
        facts["primary_volume_descriptor_found"] = True
        facts["volume_identifier"] = descriptor[40:72].decode("ascii", errors="replace").strip()
        blocks = struct.unpack_from("<I", descriptor, 80)[0]
        block_size = struct.unpack_from("<H", descriptor, 128)[0]
        facts["volume_space_blocks"] = blocks
        facts["logical_block_size"] = block_size
        facts["descriptor_bytes"] = blocks * block_size
        facts["file_bytes"] = size
        facts["size_matches_descriptor"] = blocks * block_size == size
    return facts


# ---------------------------------------------------------------------------
# Setup: configuration and one-time folder prompts
# ---------------------------------------------------------------------------


def load_settings(config_path: Path) -> Settings:
    if not config_path.is_file():
        return Settings()
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with config_path.open("r", encoding="utf-8-sig") as stream:
            parser.read_file(stream)
    except (OSError, configparser.Error) as error:
        raise SetupError(f"cannot read config {config_path}: {error}") from error
    if not parser.has_section("local"):
        raise SetupError(f"config {config_path} must contain a [local] section")
    section = parser["local"]

    def configured(key: str) -> Optional[Path]:
        raw_value = section.get(key, "").strip()
        if not raw_value:
            return None
        path = Path(raw_value).expanduser()
        if not path.is_absolute():
            path = config_path.parent / path
        return path.resolve(strict=False)

    expected = section.get("expected_tool_sha256", "").strip().lower() or None
    if expected is not None and not SHA256_RE.fullmatch(expected):
        raise SetupError("expected_tool_sha256 must be 64 lowercase hexadecimal characters")
    return Settings(
        input_root=configured("input_root"),
        output_base=configured("output_root"),
        tool_path=configured("tool_path"),
        expected_tool_sha256=expected,
    )


def save_settings(config_path: Path, settings: Settings) -> None:
    lines = [
        "# Written by RUN_PIPELINE.bat on first use. Private to this PC; ignored by git.",
        "# Absolute paths are fine. Relative paths resolve from this file's folder.",
        "",
        "[local]",
    ]
    if settings.input_root is not None:
        lines.append(f"input_root = {settings.input_root}")
    if settings.output_base is not None:
        lines.append(f"output_root = {settings.output_base}")
    if settings.tool_path is not None:
        lines.append(f"tool_path = {settings.tool_path}")
    if settings.expected_tool_sha256 is not None:
        lines.append(f"expected_tool_sha256 = {settings.expected_tool_sha256}")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _prompt_directory(title: str, initial: Optional[Path]) -> Optional[Path]:
    try:
        import tkinter
        from tkinter import filedialog
    except ImportError as error:
        raise SetupError(
            "Python was built without Tk, so folder dialogs are unavailable. Reinstall Python from "
            "python.org with the default options, or run with --input, --output, and --tool."
        ) from error
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        chosen = filedialog.askdirectory(
            title=title,
            initialdir=str(initial) if initial is not None and initial.is_dir() else None,
            mustexist=True,
        )
    finally:
        root.destroy()
    return Path(chosen) if chosen else None


def _prompt_converter(initial: Optional[Path]) -> Optional[Path]:
    try:
        import tkinter
        from tkinter import filedialog
    except ImportError as error:
        raise SetupError("Tk is unavailable; run with --tool or reinstall Python with Tcl/Tk.") from error
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        chosen = filedialog.askopenfilename(
            title="Choose YACpkTool.exe (keep CpkMaker.dll in the same folder)",
            initialdir=str(initial.parent) if initial is not None and initial.parent.is_dir() else None,
            filetypes=[("YACpkTool", "YACpkTool.exe"), ("Programs", "*.exe"), ("All files", "*.*")],
        )
    finally:
        root.destroy()
    return Path(chosen) if chosen else None


def output_folder_problem(output_base: Path, input_root: Optional[Path]) -> Optional[str]:
    """Return why an output folder cannot be used, or None when it is fine."""
    if input_root is not None:
        resolved = output_base.resolve(strict=False)
        resolved_input = input_root.resolve(strict=False)
        if resolved == resolved_input or resolved_input in resolved.parents or resolved in resolved_input.parents:
            return "the output folder must not be inside the input folder or contain it"
    try:
        converter_argument_path(output_base / "run")
    except UnsafePathError:
        return (
            f"YACpkTool rejects paths with spaces or non-ASCII letters ({output_base}); "
            "use a folder such as C:\\SRW_OE_out"
        )
    return None


def complete_settings(
    settings: Settings,
    *,
    gui: bool,
    reconfigure: bool,
    prompt_directory: Callable[[str, Optional[Path]], Optional[Path]] = _prompt_directory,
    prompt_converter: Callable[[Optional[Path]], Optional[Path]] = _prompt_converter,
) -> tuple[Settings, set[str]]:
    """Fill in missing folders, asking with dialogs only when allowed.

    Returns the settings and the names of the fields that were asked for, so that only
    those answers are saved. A converter found by bounded discovery is used but not saved.
    """
    prompted: set[str] = set()

    def ask_directory(field_name: str, title: str, initial: Optional[Path], what: str) -> Path:
        if not gui:
            raise SetupError(f"{what} is not configured; pass it on the command line or run without --no-gui")
        chosen = prompt_directory(title, initial)
        if chosen is None:
            raise SetupError(f"setup cancelled: no {what} chosen")
        prompted.add(field_name)
        return chosen

    def ask_converter(initial: Optional[Path]) -> Path:
        if not gui:
            raise SetupError("converter is not configured; pass --tool or run without --no-gui")
        chosen = prompt_converter(initial)
        if chosen is None:
            raise SetupError("setup cancelled: no converter chosen")
        prompted.add("tool_path")
        return chosen

    if reconfigure or settings.input_root is None or not settings.input_root.is_dir():
        settings.input_root = ask_directory(
            "input_root", "Choose the folder with the SRW OE files (EDAT, CPK, ISO)", settings.input_root, "input folder"
        )
    # In GUI mode a saved output folder that YACpkTool cannot use is asked for again, so a
    # double-click never stays blocked on a stale setting. Without GUI the preflight reports it.
    saved_output_problem = (
        output_folder_problem(settings.output_base, settings.input_root)
        if gui and settings.output_base is not None and settings.input_root is not None
        else None
    )
    if reconfigure or settings.output_base is None or saved_output_problem is not None:
        if saved_output_problem is not None:
            print(f"Saved output folder is not usable: {saved_output_problem}. Please choose another folder.")
        initial = settings.output_base
        while True:
            chosen = ask_directory(
                "output_root",
                "Choose an output folder. Prefer a path without spaces or Polish letters, e.g. C:\\SRW_OE_out",
                initial,
                "output folder",
            )
            problem = output_folder_problem(chosen, settings.input_root)
            if problem is None:
                settings.output_base = chosen
                break
            if not gui:
                raise SetupError(problem)
            print(f"Not usable: {problem}. Please choose another folder.")
            initial = chosen.parent
    if reconfigure or (settings.tool_path is not None and not settings.tool_path.is_file()):
        settings.tool_path = ask_converter(settings.tool_path)
    elif settings.tool_path is None:
        try:
            found = extract_cpk_batch.resolve_tool(None, settings.input_root)
        except ValueError as error:
            if not gui:
                raise SetupError(str(error)) from error
            found = None
        if found is not None:
            settings.tool_path = found  # used for this run only: it is not in `prompted`, so not saved
        else:
            settings.tool_path = ask_converter(None)
    return settings, prompted


# ---------------------------------------------------------------------------
# One run
# ---------------------------------------------------------------------------


class Run:
    """State and stage functions for one pipeline run."""

    def __init__(
        self,
        *,
        tool: Path,
        input_root: Path,
        run_dir: Path,
        timeout_seconds: float,
        say: Callable[[str], None],
    ) -> None:
        self.tool: Optional[Path] = tool
        self.input_root = input_root
        self.run_dir = run_dir
        self.logs_dir = run_dir / "logs"
        self.staging_dir = run_dir / "staging"
        self.packages_dir = run_dir / "packages"
        self.text_dir = run_dir / "text"
        self.gates_dir = run_dir / "gates"
        self.timeout_seconds = timeout_seconds
        self.say = say
        self.naming_mode: Optional[str] = None
        self.io_mode: Optional[str] = None
        self.calls: list[dict[str, Any]] = []
        self._call_counter = 0

    # -- paths and logging -------------------------------------------------

    def redact(self, text: str) -> str:
        """Replace local absolute paths so the registry can be shared without user folder names."""
        pairs = [(str(self.input_root), "<input>"), (str(self.run_dir), "<run>")]
        if self.tool is not None:
            pairs.append((str(self.tool), "<converter>"))
        for value, placeholder in pairs:
            if value and value not in (".", os.sep):
                text = text.replace(value, placeholder)
        return text

    # -- converter calls ---------------------------------------------------

    def call(self, arguments: list[str], *, label: str, io_mode: str) -> ConverterCall:
        if self.tool is None:
            raise RuntimeError("converter is not resolved")
        self._call_counter += 1
        slug = f"{self._call_counter:04d}-{re.sub(r'[^A-Za-z0-9_-]+', '-', label)}"
        command = [str(self.tool), *arguments]
        started = time.monotonic()
        returncode: Optional[int] = None
        timed_out = False
        output: Optional[str] = None
        error: Optional[str] = None
        try:
            if io_mode == "captured":
                completed = subprocess.run(
                    command,
                    cwd=str(self.run_dir),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=self.timeout_seconds,
                    check=False,
                )
                returncode = completed.returncode
                output = completed.stdout.decode("utf-8", errors="replace") if completed.stdout else ""
            else:
                # Console mode: inherit the console so YACpkTool's progress output works even
                # when its progress loop cannot run with redirected output. Its errors are then
                # judged from the output folder only.
                completed = subprocess.run(
                    command,
                    cwd=str(self.run_dir),
                    stdin=subprocess.DEVNULL,
                    timeout=self.timeout_seconds,
                    check=False,
                )
                returncode = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
        except OSError as exc:
            error = str(exc)
        call = ConverterCall(
            label=label,
            io_mode=io_mode,
            command=command,
            returncode=returncode,
            timed_out=timed_out,
            output=output,
            error=error,
            seconds=round(time.monotonic() - started, 2),
        )
        self._write_call_log(slug, call)
        self.calls.append(
            {
                "label": label,
                "io_mode": io_mode,
                "arguments": [self.redact(argument) for argument in arguments],
                "exit_code": returncode,
                "timed_out": timed_out,
                "start_error": self.redact(error) if error else None,
                "seconds": call.seconds,
                "log": f"logs/converter/{slug}.txt",
            }
        )
        return call

    def _write_call_log(self, slug: str, call: ConverterCall) -> None:
        folder = self.logs_dir / "converter"
        folder.mkdir(parents=True, exist_ok=True)
        header = [
            f"label: {call.label}",
            f"io_mode: {call.io_mode}",
            "command: " + " ".join(f'"{part}"' if " " in part else part for part in call.command),
            f"exit_code: {call.returncode}",
            f"timed_out: {call.timed_out}",
            f"start_error: {call.error}",
            f"seconds: {call.seconds}",
        ]
        body = call.output if call.output is not None else "(console mode: output was not captured)"
        (folder / f"{slug}.txt").write_text("\n".join(header) + "\n\n" + body, encoding="utf-8", errors="replace")

    def _make_alias(self, source: Path, expected_sha256: str, alias_path: Path) -> Path:
        """Copy into staging under a `.cpk` name. The original file is never renamed."""
        alias_path.parent.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(source, alias_path)
        if _sha256_file(alias_path) != expected_sha256:
            raise RuntimeError("staging copy does not match the source hash")
        return alias_path

    def _extraction_failure(self, call: ConverterCall, output_dir: Path) -> Optional[str]:
        reason = converter_failure(call, expect_finished=True)
        if reason is None and not _has_regular_files(output_dir):
            reason = "converter produced no files"
        return reason

    # -- probe -------------------------------------------------------------

    def probe(self, candidates: list[Candidate]) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        for candidate in candidates[:PROBE_CANDIDATE_LIMIT]:
            for naming, io_mode in PROBE_ORDER:
                probe_dir = self.staging_dir / f"probe-{len(attempts) + 1:02d}"
                probe_dir.mkdir(parents=True)
                reason: Optional[str]
                try:
                    if naming == "original_name":
                        source = candidate.path
                    else:
                        source = self._make_alias(
                            candidate.path,
                            candidate.sha256,
                            probe_dir / "alias" / f"{safe_stem(candidate.name)}.cpk",
                        )
                    output_dir = probe_dir / "out"
                    call = self.call(
                        ["-X", "-i", str(source), "-o", converter_argument_path(output_dir)],
                        label=f"probe-{naming}-{io_mode}",
                        io_mode=io_mode,
                    )
                    reason = self._extraction_failure(call, output_dir)
                finally:
                    shutil.rmtree(probe_dir, ignore_errors=True)
                source_unchanged = _sha256_file(candidate.path) == candidate.sha256
                attempts.append(
                    {
                        "candidate": candidate.relpath,
                        "naming_mode": naming,
                        "io_mode": io_mode,
                        "ok": reason is None and source_unchanged,
                        "reason": reason or ("" if source_unchanged else "source changed during probe"),
                    }
                )
                if not source_unchanged:
                    return {"status": "blocked", "reason": "source changed during probe", "attempts": attempts}
                if reason is None:
                    self.naming_mode = naming
                    self.io_mode = io_mode
                    return {
                        "status": "passed",
                        "candidate": candidate.relpath,
                        "naming_mode": naming,
                        "io_mode": io_mode,
                        "attempts": attempts,
                    }
                self.say(f"  probe {candidate.relpath}: {naming}/{io_mode} rejected ({reason})")
        return {
            "status": "blocked",
            "reason": "no converter mode extracted any probe CPK",
            "attempts": attempts,
        }

    # -- extraction --------------------------------------------------------

    def extract_all(self, top_level: list[WorkItem]) -> list[dict[str, Any]]:
        queue: deque[WorkItem] = deque(top_level)
        packages: list[dict[str, Any]] = []
        by_sha: dict[str, dict[str, Any]] = {}
        while queue:
            item = queue.popleft()
            existing = by_sha.get(item.sha256)
            if existing is not None:
                existing["aliases"].append(
                    {"path": item.display_path, "sha256": item.sha256, "reason": "same content as package"}
                )
                self.say(f"  {item.display_path}: same content as {existing['package_id']} (not extracted again)")
                continue
            package = self._new_package(len(packages) + 1, item)
            packages.append(package)
            by_sha[item.sha256] = package
            if item.depth > MAX_NESTED_DEPTH:
                package["status"] = "not_processed"
                package["error"] = f"nested depth above the limit of {MAX_NESTED_DEPTH}"
                self.say(f"  {item.display_path}: {package['error']}")
                continue
            self.say(f"  extracting {package['package_id']} ({item.size} bytes)")
            nested = self._extract_package(item, package)
            queue.extend(nested)
        return packages

    def _new_package(self, sequence: int, item: WorkItem) -> dict[str, Any]:
        package_id = f"p{sequence:03d}" + (f"-n{item.depth}" if item.depth else "") + f"-{safe_stem(item.name)}-{item.sha256[:12]}"
        return {
            "package_id": package_id,
            "depth": item.depth,
            "parent_package": item.parent_package,
            "source_path": item.display_path,
            "source_sha256": item.sha256,
            "source_size_bytes": item.size,
            "aliases": [],
            "status": "pending",
            "error": None,
            "list_ok": None,
            "output_dir": f"packages/{package_id}",
            "members": [],
            "member_count": 0,
            "total_member_bytes": 0,
            "text": {"status": "not_run"},
        }

    def _extract_package(self, item: WorkItem, package: dict[str, Any]) -> list[WorkItem]:
        package_id = package["package_id"]
        output_dir = self.packages_dir / package_id
        alias_root = self.staging_dir / package_id
        reason: Optional[str] = None
        nested: list[WorkItem] = []
        try:
            if _sha256_file(item.path) != item.sha256:
                raise RuntimeError("source changed before extraction")
            source = item.path
            if self.naming_mode == "cpk_alias":
                source = self._make_alias(item.path, item.sha256, alias_root / "alias" / f"{safe_stem(item.name)}.cpk")
            listing = self.call(["-L", "-i", str(source)], label=f"list-{package_id}", io_mode="captured")
            package["list_ok"] = converter_failure(listing, expect_finished=False) is None
            call = self.call(
                ["-X", "-i", str(source), "-o", converter_argument_path(output_dir)],
                label=f"extract-{package_id}",
                io_mode=self.io_mode or "captured",
            )
            reason = self._extraction_failure(call, output_dir)
            if _sha256_file(item.path) != item.sha256:
                reason = "source changed during extraction"
        except Exception as exc:  # noqa: BLE001 - one package must not stop the other packages
            reason = f"{type(exc).__name__}: {str(exc)[:200]}"
        finally:
            shutil.rmtree(alias_root, ignore_errors=True)

        if reason is not None:
            shutil.rmtree(output_dir, ignore_errors=True)
            package["status"] = "failed"
            package["error"] = self.redact(reason)
            self.say(f"  FAILED {package_id}: {reason}")
            return nested

        members, inventory_errors = _member_entries(output_dir)
        if inventory_errors:
            package["status"] = "failed"
            package["error"] = f"{len(inventory_errors)} output entries could not be read"
            self.say(f"  FAILED {package_id}: {package['error']}")
            return nested
        package["status"] = "extracted"
        package["members"] = members
        package["member_count"] = len(members)
        package["total_member_bytes"] = sum(member["size_bytes"] for member in members)
        for member in members:
            if member["content_type"] == "cpk_signature":
                nested.append(
                    WorkItem(
                        path=output_dir / member["path"],
                        display_path=f"packages/{package_id}/{member['path']}",
                        name=_leaf_name(member["path"]),
                        sha256=member["sha256"],
                        size=member["size_bytes"],
                        depth=item.depth + 1,
                        parent_package=package_id,
                    )
                )
        package["text"] = self.export_text(package_id, output_dir)
        return nested

    # -- text --------------------------------------------------------------

    def export_text(self, package_id: str, package_dir: Path) -> dict[str, Any]:
        bin_count = sum(
            1
            for current, _names, file_names in os.walk(package_dir)
            for name in file_names
            if name.lower().endswith(".bin") and not Path(current, name).is_symlink()
        )
        if bin_count == 0:
            return {"status": "not_applicable", "bin_files": 0}
        export_dir = self.text_dir / package_id
        try:
            manifest, units, segments = extract_event_text.build_export(package_dir)
            checks = [
                ("in-memory records", extract_event_text.verify_records(manifest, units, segments)),
            ]
            extract_event_text.write_export(export_dir, manifest, units, segments)
            checks.append(
                (
                    "exported files read back",
                    extract_event_text.read_back_errors(export_dir, manifest, units, segments),
                )
            )
        except Exception as exc:  # noqa: BLE001 - a malformed BIN fails only its own package
            message = f"{type(exc).__name__}: {str(exc)[:200]}"
            self.say(f"  text FAILED {package_id}: {message}")
            return {"status": "failed", "bin_files": bin_count, "error": message}
        totals = manifest["totals"]
        errors_total = sum(len(errors) for _label, errors in checks)
        status = "exported_verified" if errors_total == 0 else "verification_failed"
        self.say(
            f"  text {package_id}: {totals['files']} BIN files, {totals['units']} units, "
            + ("verified" if errors_total == 0 else f"{errors_total} verification problem(s)")
        )
        return {
            "status": status,
            "bin_files": totals["files"],
            "bytes": totals["bytes"],
            "segments": totals["segments"],
            "units": totals["units"],
            "export_dir": f"text/{package_id}",
            "checks": [{"label": label, "errors": len(errors)} for label, errors in checks],
            "verification_errors": [error[:200] for _label, errors in checks for error in errors[:20]],
            "manifest_sha256": _sha256_file(export_dir / "manifest.json"),
            "units_sha256": _sha256_file(export_dir / "units.jsonl"),
            "segments_sha256": _sha256_file(export_dir / "segments.jsonl"),
        }

    # -- repack gate -------------------------------------------------------

    def repack_gate(self, package: dict[str, Any]) -> dict[str, Any]:
        package_id = package["package_id"]
        gate_dir = self.gates_dir / package_id
        packed = gate_dir / "roundtrip.cpk"
        unpacked = gate_dir / "unpacked"
        gate_dir.mkdir(parents=True)
        package_dir = self.run_dir / package["output_dir"]
        before = {member["path"]: member["sha256"] for member in package["members"]}
        result: dict[str, Any] = {"package_id": package_id, "member_count": len(before)}
        try:
            pack = self.call(
                ["-P", "-i", str(package_dir), "-o", converter_argument_path(packed)],
                label=f"pack-{package_id}",
                io_mode=self.io_mode or "captured",
            )
            reason = converter_failure(pack, expect_finished=True)
            if reason is None and not (packed.is_file() and packed.stat().st_size > 0):
                reason = "packed file is missing or empty"
            if reason is None:
                result["packed_size_bytes"] = packed.stat().st_size
                result["packed_sha256"] = _sha256_file(packed)
                unpack = self.call(
                    ["-X", "-i", str(packed), "-o", converter_argument_path(unpacked)],
                    label=f"unpack-check-{package_id}",
                    io_mode=self.io_mode or "captured",
                )
                reason = self._extraction_failure(unpack, unpacked)
            if reason is None:
                after_entries, errors = _member_entries(unpacked)
                if errors:
                    reason = f"{len(errors)} round-trip entries could not be read"
                else:
                    after = {member["path"]: member["sha256"] for member in after_entries}
                    missing = sorted(set(before) - set(after))
                    extra = sorted(set(after) - set(before))
                    changed = sorted(path for path in set(before) & set(after) if before[path] != after[path])
                    result.update(
                        {
                            "round_trip_member_count": len(after),
                            "missing_count": len(missing),
                            "extra_count": len(extra),
                            "hash_mismatch_count": len(changed),
                            "missing_examples": missing[:10],
                            "extra_examples": extra[:10],
                            "hash_mismatch_examples": changed[:10],
                        }
                    )
                    result["status"] = "passed" if not (missing or extra or changed) else "failed"
        except Exception as exc:  # noqa: BLE001 - report the gate as an error, keep the run
            reason = f"{type(exc).__name__}: {str(exc)[:200]}"
        finally:
            shutil.rmtree(gate_dir, ignore_errors=True)
        if reason is not None:
            result["status"] = "error"
            result["error"] = self.redact(reason)
        result.setdefault("status", "error")
        self.say(f"  repack gate {package_id}: {result['status']}")
        return result


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class RunResult:
    status: str
    exit_code: int
    run_dir: Optional[Path]
    report_path: Optional[Path]
    registry_path: Optional[Path]


def _classify_input(entry: dict[str, Any]) -> str:
    content_type = entry["content_type"]
    if content_type == "cpk_signature":
        return "cpk"
    if content_type == "iso9660_pvd_signature":
        return "iso_not_processed"
    if content_type == "zip_signature":
        return "zip_not_processed"
    if content_type in ("pbp_signature", "psf_sfo_signature"):
        return "metadata_not_processed"
    if content_type == "unknown_signature":
        return "unknown_not_processed"
    return "skipped_symlink_or_not_regular"


def _format_bytes(count: int) -> str:
    return f"{count / (1024 * 1024):.1f} MiB"


def _default_run_id(base: Path, now: Optional[dt.datetime] = None) -> str:
    stamp = (now or dt.datetime.now()).strftime("%Y%m%d-%H%M%S")
    candidate, counter = stamp, 2
    while (base / candidate).exists():
        candidate = f"{stamp}-{counter}"
        counter += 1
    return candidate


def run_pipeline(
    settings: Settings,
    *,
    preflight_only: bool = False,
    run_id: Optional[str] = None,
    timeout_seconds: float = TOOL_TIMEOUT_SECONDS,
    free_bytes: Callable[[Path], int] = _free_bytes,
    say: Callable[[str], None] = print,
) -> RunResult:
    if settings.input_root is None or settings.output_base is None:
        raise SetupError("input and output folders are required")
    input_root = settings.input_root.expanduser().resolve(strict=True)
    base = settings.output_base.expanduser().resolve(strict=False)
    if not input_root.is_dir():
        raise SetupError(f"input folder does not exist: {input_root}")
    if base == input_root or input_root in base.parents or base in input_root.parents:
        raise SetupError("output folder must be separate from the input folder (neither inside the other)")

    say("Stage 1/8 setup: folders chosen")
    say("Stage 2/8 inventory: hashing and classifying every input file (read-only)")
    inventory = inventory_path(input_root)
    entries = inventory["entries"]
    before_snapshot = _tree_snapshot(input_root)
    cpk_entries = [entry for entry in entries if entry["content_type"] == "cpk_signature"]
    unique_cpk: dict[str, dict[str, Any]] = {}
    for entry in sorted(cpk_entries, key=lambda item: item["path"]):
        unique_cpk.setdefault(entry["sha256"], entry)
    cpk_total_bytes = sum(entry["size_bytes"] for entry in unique_cpk.values())
    iso_count = sum(entry["content_type"] == "iso9660_pvd_signature" for entry in entries)
    say(
        f"  {inventory['file_count']} files; {len(cpk_entries)} CPK signatures "
        f"({len(unique_cpk)} unique); ISO images: {iso_count}"
    )

    run_id = run_id or _default_run_id(base)
    run_dir = base / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    run = Run(tool=None, input_root=input_root, run_dir=run_dir, timeout_seconds=timeout_seconds, say=say)
    for folder in (run.logs_dir, run.staging_dir, run.packages_dir, run.text_dir, run.gates_dir):
        folder.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now().astimezone()

    failures: list[str] = []
    warnings: list[str] = []
    converter_info: dict[str, Any] = {}
    probe: dict[str, Any] = {"status": "not_run", "reason": "no CPK signatures found"}
    packages: list[dict[str, Any]] = []
    gate: dict[str, Any] = {"status": "not_run", "reason": "not reached"}
    status = "completed" if not preflight_only else "preflight_passed"
    blocked_reason: Optional[str] = None

    try:
        say("Stage 3/8 preflight: converter, output path, free space")
        tool_path = settings.tool_path
        if tool_path is None:
            try:
                tool_path = extract_cpk_batch.resolve_tool(None, input_root)
            except ValueError as error:
                raise SetupError(str(error)) from error
        if tool_path is None:
            raise SetupError(f"{extract_cpk_batch.TOOL_NAME} was not found next to the scripts or in the input folder")
        tool = tool_path.expanduser().resolve(strict=True)
        run.tool = tool
        digest = _sha256_file(tool)
        expected = settings.expected_tool_sha256
        converter_info = {
            "file_name": tool.name,
            "sha256": digest,
            "size_bytes": tool.stat().st_size,
            "expected_sha256_matched": None if expected is None else digest == expected,
            "companion_dll_present": (tool.parent / "CpkMaker.dll").is_file(),
        }
        if expected is not None and digest != expected:
            failures.append("converter SHA-256 differs from expected_tool_sha256; refusing to run it")
        if not converter_info["companion_dll_present"]:
            warnings.append("CpkMaker.dll was not found beside the converter; extraction will likely fail")
        needed = (FREE_SPACE_FACTOR * cpk_total_bytes + FREE_SPACE_MARGIN_BYTES) if cpk_total_bytes else 0
        free = free_bytes(base)
        if free < needed:
            failures.append(
                f"not enough free space on the output drive: {_format_bytes(free)} free, "
                f"about {_format_bytes(needed)} needed"
            )
        try:
            converter_argument_path(run_dir)
        except UnsafePathError as error:
            if cpk_entries:
                failures.append(str(error))
            else:
                warnings.append(str(error))
        if failures:
            raise SetupError("; ".join(failures))

        if preflight_only:
            say("Preflight only: no converter call was made; nothing was extracted.")
            probe = {"status": "not_run", "reason": "preflight only"}
            gate = {"status": "not_run", "reason": "preflight only"}
        elif cpk_entries:
            say("Stage 4/8 probe: finding a converter mode that extracts the smallest CPK")
            candidates = [
                Candidate(
                    relpath=entry["path"],
                    path=input_root.joinpath(*entry["path"].split("/")),
                    name=_leaf_name(entry["path"]),
                    size=entry["size_bytes"],
                    sha256=entry["sha256"],
                )
                for entry in sorted(unique_cpk.values(), key=lambda item: (item["size_bytes"], item["path"]))
            ]
            probe = run.probe(candidates)
            if probe["status"] != "passed":
                raise SetupError("converter probe failed: " + probe["reason"])
            naming_text = "original .EDAT name" if probe["naming_mode"] == "original_name" else "staged .cpk copy"
            output_text = "captured output" if probe["io_mode"] == "captured" else "console output"
            say(f"  probe passed: {naming_text}, {output_text}")
            say("Stage 5/8 extract: unique CPKs and nested CPKs into the run folder")
            top_level = [
                WorkItem(
                    path=input_root.joinpath(*entry["path"].split("/")),
                    display_path=entry["path"],
                    name=_leaf_name(entry["path"]),
                    sha256=entry["sha256"],
                    size=entry["size_bytes"],
                    depth=0,
                    parent_package=None,
                )
                for entry in sorted(cpk_entries, key=lambda item: item["path"])
            ]
            packages = run.extract_all(top_level)
            say("Stage 6/8 text: export and verify event text for each extracted package")
            say("Stage 7/8 gate: repack the smallest extracted package and compare member hashes")
            gate_candidates = sorted(
                (package for package in packages if package["status"] == "extracted" and package["member_count"]),
                key=lambda package: (package["total_member_bytes"], package["package_id"]),
            )
            gate = run.repack_gate(gate_candidates[0]) if gate_candidates else {
                "status": "not_run",
                "reason": "no extracted package with members",
            }
        else:
            say("Stage 4/8 probe: skipped (no CPK signatures)")
            say("Stage 5-7/8: nothing to extract, export, or repack")
    except SetupError as error:
        blocked_reason = str(error)
        status = "blocked"
        say(f"BLOCKED: {error}")
    except KeyboardInterrupt:
        status = "interrupted"
        say("Interrupted by user; partial outputs are kept in the run folder for inspection.")
    except Exception as error:  # noqa: BLE001 - report every unexpected failure, then fail closed
        status = "error"
        failures.append(f"unexpected error: {type(error).__name__}: {str(error)[:200]}")
        say(f"Unexpected error: {type(error).__name__}: {error}")
    finally:
        shutil.rmtree(run.staging_dir, ignore_errors=True)
        try:
            run.gates_dir.rmdir()  # only removed when empty; gate artifacts are deleted after each check
        except OSError:
            pass

    say("Stage 8/8 report: registry, CSV files, and REPORT.txt")
    changes = _snapshot_changes(before_snapshot, _tree_snapshot(input_root))
    input_unchanged = not changes
    if changes:
        status = "error"
        failures.append(f"input folder changed during the run ({len(changes)} entries); names are in the registry")

    for package in packages:
        if package["status"] == "failed":
            failures.append(f"{package['package_id']}: extraction failed ({package['error']})")
        if package["text"].get("status") in ("failed", "verification_failed"):
            failures.append(f"{package['package_id']}: text export {package['text']['status']}")
    if gate.get("status") in ("failed", "error"):
        failures.append(f"CPK repack gate {gate['status']}: the round trip did not reproduce the members")

    not_processed: list[str] = []
    input_rows: list[dict[str, Any]] = []
    package_by_sha = {package["source_sha256"]: package for package in packages}
    for entry in entries:
        category = _classify_input(entry)
        iso_facts = None
        if category == "iso_not_processed":
            iso_facts = _iso_facts(input_root.joinpath(*entry["path"].split("/")), entry["size_bytes"])
            not_processed.append(f"{entry['path']}: ISO image not processed (no validated ISO adapter); {_iso_summary(iso_facts)}")
        elif category == "zip_not_processed":
            not_processed.append(f"{entry['path']}: ZIP archive not processed by this pipeline")
        elif category == "metadata_not_processed":
            not_processed.append(f"{entry['path']}: metadata container not processed")
        elif category == "unknown_not_processed":
            not_processed.append(f"{entry['path']}: unrecognized signature; not processed")
        pipeline_status = category
        if category == "cpk":
            package = package_by_sha.get(entry["sha256"])
            if package is None:
                pipeline_status = "not_processed"
            elif package["source_path"] == entry["path"]:
                pipeline_status = package["status"]
            else:
                pipeline_status = f"same_content_as:{package['package_id']}"
        input_rows.append(
            {
                "path": entry["path"],
                "size_bytes": entry["size_bytes"],
                "sha256": entry["sha256"],
                "content_type": entry["content_type"],
                "extension_hint": entry["extension_hint"],
                "pipeline_status": pipeline_status,
                "iso_facts": iso_facts,
            }
        )
    for package in packages:
        if package["status"] == "not_processed":
            not_processed.append(f"{package['source_path']}: {package['error']}")
    if iso_count > 1:
        not_processed.append(
            f"{iso_count} ISO images found: base-image selection is not implemented, so none was chosen"
        )

    if run.io_mode == "console":
        warnings.append(
            "converter output was not captured (console mode): YACpkTool's error lines were not checked; "
            "a package counts as extracted when the converter exits 0 and writes files"
        )
    if status == "completed" and failures:
        status = "completed_with_failures"
    finished = dt.datetime.now().astimezone()
    registry = {
        "schema": RUN_SCHEMA,
        "run": {
            "id": run_id,
            "started": started.isoformat(timespec="seconds"),
            "finished": finished.isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "platform": platform.system() + " " + platform.release(),
            "mode": "preflight_only" if preflight_only else "full",
        },
        "status": status,
        "blocked_reason": blocked_reason,
        "converter": {**converter_info, "naming_mode": run.naming_mode, "io_mode": run.io_mode},
        "input": {
            "file_count": inventory["file_count"],
            "readable_file_count": inventory["readable_file_count"],
            "total_size_bytes": inventory["total_size_bytes"],
            "content_type_counts": inventory["content_type_counts"],
            "inventory_errors": inventory["errors"],
            "unchanged": input_unchanged,
            "changed_entries": changes[:50],
            "cpk_unique_count": len(unique_cpk),
            "cpk_total_bytes_unique": cpk_total_bytes,
        },
        "probe": probe,
        "inputs": input_rows,
        "packages": packages,
        "gate": gate,
        "not_processed": not_processed,
        "failures": failures,
        "warnings": warnings,
        "known_gaps": list(KNOWN_GAPS),
        "converter_calls": run.calls,
        "summary": _summary(packages, gate, probe),
        "scope_note": (
            "Inventory, extraction, text exports, and CPK round-trip checks only. Nothing here "
            "is a translation, a patch, or a verified in-game result."
        ),
    }
    registry_path = run_dir / "registry.json"
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_csvs(run_dir, input_rows, packages)
    report_path = run_dir / "REPORT.txt"
    report_path.write_text(_render_report(registry), encoding="utf-8")
    exit_code = 0 if status in ("completed", "preflight_passed") else 1
    say(f"Status: {status}. Report: {report_path}")
    return RunResult(status=status, exit_code=exit_code, run_dir=run_dir, report_path=report_path, registry_path=registry_path)


def _summary(packages: list[dict[str, Any]], gate: dict[str, Any], probe: dict[str, Any]) -> dict[str, Any]:
    extracted = [package for package in packages if package["status"] == "extracted"]
    text_units = sum(package["text"].get("units", 0) for package in packages)
    return {
        "packages_total": len(packages),
        "packages_extracted": len(extracted),
        "packages_failed": sum(package["status"] == "failed" for package in packages),
        "packages_not_processed": sum(package["status"] == "not_processed" for package in packages),
        "member_files_extracted": sum(package["member_count"] for package in extracted),
        "text_packages_verified": sum(package["text"].get("status") == "exported_verified" for package in packages),
        "text_packages_failed": sum(
            package["text"].get("status") in ("failed", "verification_failed") for package in packages
        ),
        "text_units_total": text_units,
        "aliases_total": sum(len(package["aliases"]) for package in packages),
        "probe_status": probe.get("status"),
        "gate_status": gate.get("status"),
    }


def _write_csvs(run_dir: Path, input_rows: list[dict[str, Any]], packages: list[dict[str, Any]]) -> None:
    with (run_dir / "inputs.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["path", "size_bytes", "sha256", "content_type", "extension_hint", "pipeline_status"])
        for row in input_rows:
            writer.writerow(
                [
                    row["path"],
                    row["size_bytes"],
                    row["sha256"],
                    row["content_type"],
                    row["extension_hint"],
                    row["pipeline_status"],
                ]
            )
    with (run_dir / "packages.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "package_id",
                "depth",
                "parent_package",
                "source_path",
                "source_sha256",
                "status",
                "member_count",
                "total_member_bytes",
                "text_status",
                "text_units",
                "aliases",
                "error",
            ]
        )
        for package in packages:
            writer.writerow(
                [
                    package["package_id"],
                    package["depth"],
                    package["parent_package"] or "",
                    package["source_path"],
                    package["source_sha256"],
                    package["status"],
                    package["member_count"],
                    package["total_member_bytes"],
                    package["text"].get("status", ""),
                    package["text"].get("units", ""),
                    len(package["aliases"]),
                    package["error"] or "",
                ]
            )


def _probe_rejection_lines(registry: dict[str, Any]) -> list[str]:
    """Show every rejected probe attempt, so a converter crash in one mode stays visible."""
    return [
        f"  rejected probe: {attempt.get('naming_mode')}/{attempt.get('io_mode')} on "
        f"{attempt.get('candidate')}: {attempt.get('reason')}"
        for attempt in registry["probe"].get("attempts", [])
        if not attempt.get("ok")
    ]


def _extraction_notes(registry: dict[str, Any]) -> list[str]:
    notes = []
    if registry["converter"].get("io_mode") == "console":
        notes.append(
            "  error lines: not checked (console output is not captured); a package counts as "
            "extracted when the converter exits 0 and writes files"
        )
    listed = [package for package in registry["packages"] if package.get("list_ok") is not None]
    if listed:
        listed_ok = sum(1 for package in listed if package["list_ok"])
        notes.append(f"  listing (-L) without error: {listed_ok} of {len(listed)} packages")
    return notes


def _render_report(registry: dict[str, Any]) -> str:
    summary = registry["summary"]
    converter = registry["converter"]
    lines = [
        "SRW OE one-click run report",
        "===========================",
        f"Run: {registry['run']['id']} ({registry['run']['mode']})",
        f"Status: {registry['status']}",
    ]
    if registry["blocked_reason"]:
        lines.append(f"Blocked: {registry['blocked_reason']}")
        if registry["status"] == "blocked":
            lines += [
                "What to check, for the reason above:",
                "  - failed probe: the probe-* files in logs/converter/; CpkMaker.dll beside YACpkTool.exe",
                "  - output path: no spaces or non-ASCII letters, and not inside the input folder",
                "  - converter hash: YACpkTool.exe must match expected_tool_sha256 in your settings",
                "  - free space: the output drive needs about three times the CPK size plus 512 MiB",
                "Share REPORT.txt if you need help.",
            ]
    lines += [
        "",
        "Converter",
        f"  file: {converter.get('file_name', 'not found')}",
        f"  sha256: {converter.get('sha256', 'n/a')}",
        f"  probe: {registry['probe'].get('status')} "
        f"(name mode: {converter.get('naming_mode') or 'n/a'}, output mode: {converter.get('io_mode') or 'n/a'})",
        *_probe_rejection_lines(registry),
        "",
        "Input",
        f"  files: {registry['input']['file_count']} (readable: {registry['input']['readable_file_count']}), "
        f"unchanged during run: {'yes' if registry['input']['unchanged'] else 'NO'}",
        f"  CPK signatures: {registry['input']['content_type_counts'].get('cpk_signature', 0)} "
        f"(unique content: {registry['input']['cpk_unique_count']})",
        "",
        "Extraction",
        f"  packages: {summary['packages_total']} (extracted {summary['packages_extracted']}, "
        f"failed {summary['packages_failed']})",
        f"  member files extracted: {summary['member_files_extracted']}",
        f"  duplicates skipped (same content): {summary['aliases_total']}",
        *_extraction_notes(registry),
        "",
        "Event text (heuristic units, verified for round trip only)",
        f"  packages with BIN files verified: {summary['text_packages_verified']} "
        f"(failed: {summary['text_packages_failed']})",
        f"  text units: {summary['text_units_total']}",
        "",
        "CPK repack round trip (smallest package)",
        f"  status: {registry['gate'].get('status')}",
    ]
    if registry["gate"].get("reason"):
        lines.append(f"  reason: {registry['gate']['reason']}")
    if registry["failures"]:
        lines += ["", "Failures"] + [f"  - {item}" for item in registry["failures"]]
    if registry["warnings"]:
        lines += ["", "Warnings"] + [f"  - {item}" for item in registry["warnings"]]
    if registry["not_processed"]:
        lines += ["", "Not processed"] + [f"  - {item}" for item in registry["not_processed"]]
    lines += ["", "Known gaps (not done by this run)"] + [f"  - {item}" for item in registry["known_gaps"]]
    lines += [
        "",
        "Outputs (inside this run folder)",
        "  registry.json, inputs.csv, packages.csv, REPORT.txt",
        "  packages/   extracted CPK contents (one folder per unique package)",
        "  text/       event text exports (manifest, units, segments) for packages with BIN files",
        "  logs/       converter logs (captured or console mode noted per call)",
        "",
        "This report contains file names and hashes only; it contains no decoded game text.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _apply_overrides(args: argparse.Namespace, settings: Settings) -> Settings:
    if args.input is not None:
        settings.input_root = args.input.expanduser().resolve(strict=False)
    if args.output is not None:
        settings.output_base = args.output.expanduser().resolve(strict=False)
    if args.tool is not None:
        settings.tool_path = args.tool.expanduser().resolve(strict=False)
    return settings


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="private INI file (ignored by git)")
    parser.add_argument("--input", type=Path, help="input folder for this run only (not saved)")
    parser.add_argument("--output", type=Path, help="output folder for this run only (not saved)")
    parser.add_argument("--tool", type=Path, help="converter path for this run only (not saved)")
    parser.add_argument("--no-gui", action="store_true", help="never open dialogs; fail if a path is missing")
    parser.add_argument("--reconfigure", action="store_true", help="ask for the folders and converter again")
    parser.add_argument("--preflight-only", action="store_true", help="check everything; make no converter call")
    args = parser.parse_args(argv)

    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required. Install Python 3.11 or newer from python.org.")
        return 2
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")

    try:
        saved = load_settings(args.config)
        # A second load: the overrides mutate their argument, and they must never reach `saved`.
        effective = _apply_overrides(args, load_settings(args.config))
        effective, prompted = complete_settings(
            effective, gui=not args.no_gui, reconfigure=args.reconfigure
        )
        if prompted:
            for field_name in prompted:
                attribute = {"input_root": "input_root", "output_root": "output_base", "tool_path": "tool_path"}[field_name]
                setattr(saved, attribute, getattr(effective, attribute))
            save_settings(args.config, saved)
            print(f"Saved your folder choices to {args.config}")
        result = run_pipeline(effective, preflight_only=args.preflight_only)
    except SetupError as error:
        print(f"Setup error: {error}")
        return 2
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return 2
    print(f"Done. Open {result.report_path} for the summary.")
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
