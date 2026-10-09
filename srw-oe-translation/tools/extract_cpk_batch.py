#!/usr/bin/env python3
"""Batch CPK listing/extraction through a locally supplied YACpkTool.

Only files beginning with the CPK signature are selected; `.EDAT` is treated
as a filename hint, not a format test. The default mode only plans the batch.
Pass --execute to invoke YACpkTool. This tool extracts; it does not repack, edit,
or process an ISO.
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from inventory_local_inputs import inventory_path

CHUNK_SIZE = 1024 * 1024
TOOL_NAME = "YACpkTool.exe"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _candidate_tool_paths(input_root: Path) -> list[Path]:
    search_directories = [Path(__file__).resolve().parent, input_root]
    candidates: dict[str, Path] = {}
    for directory in search_directories:
        if not directory.is_dir():
            continue
        try:
            for child in directory.iterdir():
                if child.is_file() and child.name.casefold() == TOOL_NAME.casefold():
                    resolved = child.resolve()
                    candidates[str(resolved).casefold()] = resolved
                elif child.is_dir() and child.name.casefold() == "yacpktool":
                    for nested in child.iterdir():
                        if nested.is_file() and nested.name.casefold() == TOOL_NAME.casefold():
                            resolved = nested.resolve()
                            candidates[str(resolved).casefold()] = resolved
        except OSError:
            continue
    return sorted(candidates.values(), key=lambda path: str(path).casefold())


def resolve_tool(tool_argument: Path | None, input_root: Path) -> Path | None:
    """Resolve a configured YACpkTool or discover one in bounded locations."""
    if tool_argument is not None:
        tool = tool_argument.expanduser().resolve(strict=True)
        if not tool.is_file():
            raise ValueError(f"Converter path is not a file: {tool_argument}")
        return tool

    candidates = _candidate_tool_paths(input_root)
    if len(candidates) > 1:
        paths = ", ".join(str(path) for path in candidates)
        raise ValueError(
            "Multiple YACpkTool.exe files found; choose one with --tool: " + paths
        )
    return candidates[0] if candidates else None


def _validate_paths(input_root: Path, output_root: Path, json_path: Path | None) -> None:
    input_root = input_root.resolve(strict=True)
    output_root = output_root.expanduser().resolve(strict=False)
    if not input_root.is_dir():
        raise ValueError("Batch input must be a directory")
    if _is_within(output_root, input_root) or _is_within(input_root, output_root):
        raise ValueError("Output directory must be separate from the input tree")
    if output_root.exists() and any(output_root.iterdir()):
        raise ValueError("Output directory already exists and is not empty; choose a fresh path")

    if json_path is not None:
        json_path = json_path.expanduser().resolve(strict=False)
        if _is_within(json_path, input_root) or _is_within(json_path, output_root):
            raise ValueError("JSON report must be outside both input and extraction output")
        if json_path.exists():
            raise ValueError("JSON report already exists; choose a fresh path")
        if json_path.exists():
            raise ValueError("JSON report already exists; choose a fresh path")


def _source_path(input_root: Path, relative_name: str) -> Path:
    return input_root.joinpath(*PurePosixPath(relative_name).parts)


def _target_path(output_root: Path, relative_name: str, source_hash: str) -> Path:
    relative = PurePosixPath(relative_name)
    parent = output_root.joinpath(*relative.parent.parts) if relative.parent.parts else output_root
    return parent / f"{relative.name}.contents-{source_hash[:12]}"


def _make_plan(
    input_root: Path, output_root: Path, inventory: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    plans = []
    unresolved_edat = []
    for entry in inventory["entries"]:
        relative_name = entry["path"]
        if entry["content_type"] == "cpk_signature":
            if entry["size_bytes"] is None or entry["sha256"] is None:
                continue
            source = _source_path(input_root, relative_name)
            destination = _target_path(output_root, relative_name, entry["sha256"])
            plans.append(
                {
                    "source": str(source),
                    "relative_path": relative_name,
                    "source_sha256": entry["sha256"],
                    "output_directory": str(destination),
                    "list_command": ["-L", "-i", str(source)],
                    "extract_command": ["-X", "-i", str(source), "-o", str(destination)],
                }
            )
        elif (entry["extension_hint"] or "").casefold() == ".edat":
            unresolved_edat.append(
                {
                    "relative_path": relative_name,
                    "size_bytes": entry["size_bytes"],
                    "sha256": entry["sha256"],
                    "content_type": entry["content_type"],
                }
            )
    return plans, unresolved_edat


def _decode_process_output(raw: bytes | None) -> str:
    return (raw or b"").decode("utf-8", errors="replace")


def _count_and_check_extracted_files(root: Path) -> int:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Extractor did not create the requested output directory")
    file_count = 0
    for current_root, directory_names, file_names in os.walk(
        root, topdown=True, followlinks=False
    ):
        current = Path(current_root)
        for directory_name in directory_names:
            if (current / directory_name).is_symlink():
                raise ValueError("Extractor created a symlink in its output")
        for file_name in file_names:
            file_path = current / file_name
            if file_path.is_symlink():
                raise ValueError("Extractor created a symlink in its output")
            if file_path.is_file():
                file_count += 1
    if file_count == 0:
        raise ValueError("Extractor produced no regular files")
    return file_count


def _run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        check=False,
        shell=False,
    )


def run_batch(
    input_root: Path,
    output_root: Path,
    tool_path: Path | None,
    execute: bool = False,
) -> dict[str, Any]:
    input_root = input_root.expanduser().resolve(strict=True)
    output_root = output_root.expanduser().resolve(strict=False)
    _validate_paths(input_root, output_root, None)
    inventory = inventory_path(input_root)
    if inventory["errors"]:
        details = "; ".join(
            f"{item['path']}: {item['error']}" for item in inventory["errors"]
        )
        raise ValueError("Input inventory has read/walk errors: " + details)

    plans, unresolved_edat = _make_plan(input_root, output_root, inventory)
    tool = resolve_tool(tool_path, input_root)
    if execute and plans and tool is None:
        raise ValueError(
            f"YACpkTool.exe was not found next to the script or in {input_root}; "
            "provide its path with --tool"
        )

    report: dict[str, Any] = {
        "schema_version": 1,
        "mode": "execute" if execute else "dry_run",
        "input_root": str(input_root),
        "output_root": str(output_root),
        "converter_path": str(tool) if tool else None,
        "converter_sha256": _sha256(tool) if tool else None,
        "input_file_count": inventory["readable_file_count"],
        "content_type_counts": inventory["content_type_counts"],
        "signature_counts_by_extension": inventory["signature_counts_by_extension"],
        "iso_candidate_count": inventory["content_type_counts"].get(
            "iso9660_pvd_signature", 0
        ),
        "cpk_candidate_count": len(plans),
        "unresolved_edat_count": len(unresolved_edat),
        "unresolved_edat": unresolved_edat,
        "input_inventory_errors": inventory["errors"],
        "results": [],
    }

    if not execute:
        report["plans"] = plans
        return report

    if output_root.exists() and any(output_root.iterdir()):
        raise ValueError("Output directory became nonempty before extraction")
    output_root.mkdir(parents=True, exist_ok=True)
    for plan in plans:
        source = Path(plan["source"])
        destination = Path(plan["output_directory"])
        result: dict[str, Any] = {
            "relative_path": plan["relative_path"],
            "source_sha256": plan["source_sha256"],
            "output_directory": str(destination),
            "status": "failed",
        }
        try:
            if _sha256(source) != plan["source_sha256"]:
                raise ValueError("Source changed after inventory; refusing to process it")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise ValueError("Extraction destination already exists")

            list_command = [str(tool), *plan["list_command"]]
            list_result = _run_command(list_command, destination.parent)
            result["list_returncode"] = list_result.returncode
            result["list_output"] = _decode_process_output(list_result.stdout)[-4000:]
            result["list_error"] = _decode_process_output(list_result.stderr)[-4000:]
            if _sha256(source) != plan["source_sha256"]:
                raise ValueError("Source changed during listing; investigate the converter")
            if list_result.returncode != 0:
                raise ValueError(f"YACpkTool -L failed with exit code {list_result.returncode}")

            extract_command = [str(tool), *plan["extract_command"]]
            extract_result = _run_command(extract_command, destination.parent)
            result["extract_returncode"] = extract_result.returncode
            result["extract_output"] = _decode_process_output(extract_result.stdout)[-4000:]
            result["extract_error"] = _decode_process_output(extract_result.stderr)[-4000:]
            if _sha256(source) != plan["source_sha256"]:
                raise ValueError("Source changed during extraction; investigate the converter")
            if extract_result.returncode != 0:
                raise ValueError(
                    f"YACpkTool -X failed with exit code {extract_result.returncode}"
                )
            result["extracted_file_count"] = _count_and_check_extracted_files(destination)
            result["status"] = "extracted"
        except (OSError, ValueError) as error:
            result["error"] = str(error)
        report["results"].append(result)

    report["extracted_count"] = sum(
        result["status"] == "extracted" for result in report["results"]
    )
    report["failed_count"] = sum(
        result["status"] != "extracted" for result in report["results"]
    )
    return report


def write_json_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_path, output_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def load_local_config(config_path: Path) -> dict[str, Path | None]:
    """Load one-time Windows input/output/tool paths from a local INI file.

    Relative paths are resolved relative to the INI file, not the current
    working directory. Empty tool_path means use bounded auto-discovery.
    """
    config_file = config_path.expanduser().resolve(strict=True)
    config = configparser.ConfigParser(interpolation=None)
    try:
        with config_file.open("r", encoding="utf-8-sig") as stream:
            config.read_file(stream)
    except configparser.Error as error:
        raise ValueError(f"Invalid local INI config: {error}") from error
    if not config.has_section("local"):
        raise ValueError("Config must contain a [local] section")

    section = config["local"]

    def configured_path(key: str, required: bool) -> Path | None:
        raw_value = section.get(key, "").strip()
        if not raw_value:
            if required:
                raise ValueError(f"Config [local] requires {key}")
            return None
        path = Path(raw_value).expanduser()
        if not path.is_absolute():
            path = config_file.parent / path
        return path.resolve(strict=False)

    return {
        "input_root": configured_path("input_root", required=True),
        "output_root": configured_path("output_root", required=True),
        "tool_path": configured_path("tool_path", required=False),
    }


def _print_summary(report: dict[str, Any]) -> None:
    print(f"Mode: {report['mode']} (CPK extraction only)")
    print(f"Readable inputs inventoried: {report['input_file_count']}")
    print(f"ISO9660 PVD signatures (not processed here): {report['iso_candidate_count']}")
    print(f"CPK-signature inputs: {report['cpk_candidate_count']}")
    print(f"Unresolved `.EDAT` inputs: {report['unresolved_edat_count']}")
    if report["converter_path"]:
        print(f"Converter: {report['converter_path']}")
        print(f"Converter SHA-256: {report['converter_sha256']}")
    else:
        print("Converter: not configured (dry-run only)")
    if report["mode"] == "dry_run":
        print("No files were extracted or modified. Pass --execute to run the batch.")
    else:
        print(f"Extracted: {report['extracted_count']}")
        print(f"Failed: {report['failed_count']}")
    if report["unresolved_edat_count"]:
        print("Some `.EDAT` files do not have a recognized CPK signature; they were not extracted.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Plan or batch-extract files with a CPK signature using a local "
            "YACpkTool. Default mode is a no-write dry run."
        )
    )
    parser.add_argument(
        "input_root",
        nargs="?",
        type=Path,
        help="directory containing EDATs and/or an ISO (or set it in --config)",
    )
    parser.add_argument("--output", type=Path, help="separate extraction output root")
    parser.add_argument(
        "--tool",
        type=Path,
        help="path to YACpkTool.exe; overrides config and bounded auto-discovery",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="local INI file with one-time input_root, output_root, and optional tool_path",
    )
    parser.add_argument("--execute", action="store_true", help="invoke the converter (default is dry-run)")
    parser.add_argument("--json-out", type=Path, help="optional local report path outside input/output")
    arguments = parser.parse_args(argv)

    try:
        config: dict[str, Path | None] = {}
        if arguments.config:
            config = load_local_config(arguments.config)
        input_root = arguments.input_root or config.get("input_root")
        output_root = arguments.output or config.get("output_root")
        tool_path = arguments.tool or config.get("tool_path")
        if input_root is None:
            parser.error("provide input_root or set it in --config")
        if output_root is None:
            parser.error("provide --output or set output_root in --config")

        _validate_paths(input_root, output_root, arguments.json_out)
        report = run_batch(
            input_root,
            output_root,
            tool_path,
            execute=arguments.execute,
        )
        if arguments.json_out:
            report_path = arguments.json_out.expanduser().resolve(strict=False)
            write_json_report(report, report_path)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    _print_summary(report)
    if arguments.json_out:
        print(f"JSON report: {arguments.json_out}")
    if report["mode"] == "execute" and (
        report.get("failed_count", 0) or report["unresolved_edat_count"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
