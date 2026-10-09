#!/usr/bin/env python3
"""Read-only inventory of local SRW OE inputs; no extraction or repacking.

This first automation layer recursively hashes files and probes a small set of
container signatures. A recognized signature is not proof that the corresponding
format is fully supported. Filename extensions are reported only as hints and
never determine the content type.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

CHUNK_SIZE = 1024 * 1024
ISO9660_SECTOR_SIZE = 2048
ISO9660_PVD_SECTOR = 16

ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")


def _content_type(path: Path, size: int) -> str:
    """Identify a few top-level signatures without trusting the suffix."""
    with path.open("rb") as stream:
        header = stream.read(8)
        if header.startswith(b"CPK "):
            return "cpk_signature"
        if header.startswith(b"\x00PBP"):
            return "pbp_signature"
        if header.startswith(b"\x00PSF"):
            return "psf_sfo_signature"
        if any(header.startswith(signature) for signature in ZIP_SIGNATURES):
            return "zip_signature"
        if size >= (ISO9660_PVD_SECTOR + 1) * ISO9660_SECTOR_SIZE:
            stream.seek(ISO9660_PVD_SECTOR * ISO9660_SECTOR_SIZE)
            pvd_prefix = stream.read(7)
            if pvd_prefix == b"\x01CD001\x01":
                return "iso9660_pvd_signature"
    return "unknown_signature"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def inventory_path(input_path: Path) -> dict[str, Any]:
    """Inventory one file or every regular file below a directory.

    Symlink entries are reported but not followed. Permission/read errors are
    included in the report and do not cause the remaining tree to be skipped.
    """
    root = input_path.expanduser().resolve(strict=True)
    if not (root.is_dir() or root.is_file()):
        raise ValueError(f"Input is not a regular file or directory: {input_path}")

    entries: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    def add_file(path: Path, relative_path: str) -> None:
        try:
            if path.is_symlink():
                entries.append(
                    {
                        "path": relative_path,
                        "size_bytes": None,
                        "sha256": None,
                        "content_type": "symlink_not_followed",
                        "extension_hint": path.suffix.lower() or None,
                        "duplicate_of": None,
                    }
                )
                return
            stat = path.stat(follow_symlinks=False)
            if not path.is_file():
                entries.append(
                    {
                        "path": relative_path,
                        "size_bytes": None,
                        "sha256": None,
                        "content_type": "non_regular_file_skipped",
                        "extension_hint": path.suffix.lower() or None,
                        "duplicate_of": None,
                    }
                )
                return
            content_type = _content_type(path, stat.st_size)
            sha256 = _sha256(path)
            entries.append(
                {
                    "path": relative_path,
                    "size_bytes": stat.st_size,
                    "sha256": sha256,
                    "content_type": content_type,
                    "extension_hint": path.suffix.lower() or None,
                    "duplicate_of": None,
                }
            )
        except OSError as error:
            errors.append({"path": relative_path, "error": str(error)})

    if root.is_file():
        add_file(root, root.name)
    else:
        def on_walk_error(error: OSError) -> None:
            raw_path = Path(error.filename) if error.filename else root
            try:
                relative_path = _relative(raw_path, root)
            except ValueError:
                relative_path = str(raw_path)
            errors.append({"path": relative_path, "error": str(error)})

        for current_root, directory_names, file_names in os.walk(
            root, topdown=True, followlinks=False, onerror=on_walk_error
        ):
            current = Path(current_root)
            kept_directories = []
            for directory_name in sorted(directory_names):
                directory_path = current / directory_name
                if directory_path.is_symlink():
                    add_file(directory_path, _relative(directory_path, root))
                else:
                    kept_directories.append(directory_name)
            directory_names[:] = kept_directories
            for file_name in sorted(file_names):
                file_path = current / file_name
                add_file(file_path, _relative(file_path, root))

    entries.sort(key=lambda entry: entry["path"])

    first_path_by_hash: dict[str, str] = {}
    for entry in entries:
        file_hash = entry["sha256"]
        if file_hash is None:
            continue
        entry["duplicate_of"] = first_path_by_hash.setdefault(
            file_hash, entry["path"]
        )
        if entry["duplicate_of"] == entry["path"]:
            entry["duplicate_of"] = None

    by_type: Counter[str] = Counter(entry["content_type"] for entry in entries)
    by_extension_and_type: dict[str, Counter[str]] = {}
    for entry in entries:
        extension = entry["extension_hint"] or "[no extension]"
        by_extension_and_type.setdefault(extension, Counter())[entry["content_type"]] += 1
    readable_files = [entry for entry in entries if entry["size_bytes"] is not None]
    return {
        "schema_version": 1,
        "input_root": str(root),
        "file_count": len(entries),
        "readable_file_count": len(readable_files),
        "total_size_bytes": sum(entry["size_bytes"] for entry in readable_files),
        "content_type_counts": dict(sorted(by_type.items())),
        "signature_counts_by_extension": {
            extension: dict(sorted(type_counts.items()))
            for extension, type_counts in sorted(by_extension_and_type.items())
        },
        "errors": errors,
        "entries": entries,
        "scope_note": (
            "Signatures and hashes only: this inventory does not validate, "
            "extract, modify, or rebuild any file."
        ),
    }


def write_json_report(report: dict[str, Any], output_path: Path, input_root: Path) -> None:
    """Write a JSON report atomically, refusing to place it inside the input."""
    destination = output_path.expanduser().resolve(strict=False)
    root = input_root.expanduser().resolve(strict=True)
    if root.is_dir():
        try:
            destination.relative_to(root)
        except ValueError:
            pass
        else:
            raise ValueError("JSON report path must be outside the inventoried input")
    elif destination == root:
        raise ValueError("JSON report path must be outside the inventoried input")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def _summary_lines(report: dict[str, Any]) -> list[str]:
    lines = [
        f"Inventoried {report['readable_file_count']}/{report['file_count']} readable files.",
        f"Total readable size: {report['total_size_bytes']} bytes.",
        "Content signatures (inventory only):",
    ]
    if report["content_type_counts"]:
        lines.extend(
            f"  {content_type}: {count}"
            for content_type, count in report["content_type_counts"].items()
        )
    else:
        lines.append("  (none)")
    lines.append("Signature counts grouped by extension hint (suffix is not detection):")
    for extension, type_counts in report["signature_counts_by_extension"].items():
        details = ", ".join(
            f"{content_type}={count}"
            for content_type, count in type_counts.items()
        )
        lines.append(f"  {extension}: {details}")
    duplicate_count = sum(
        entry["duplicate_of"] is not None for entry in report["entries"]
    )
    lines.append(f"Identical-content duplicate paths: {duplicate_count}.")
    lines.append(f"Read/walk errors: {len(report['errors'])}.")
    lines.append("No files were extracted, renamed, modified, or repacked.")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recursively inventory local game inputs by content signature and "
            "SHA-256. This is read-only; it does not unpack or rebuild files."
        )
    )
    parser.add_argument("input", type=Path, help="one file or a directory to inventory")
    parser.add_argument(
        "--json-out",
        type=Path,
        help="optional JSON report path; it must be outside the inventoried input",
    )
    arguments = parser.parse_args(argv)

    try:
        report = inventory_path(arguments.input)
        if arguments.json_out:
            write_json_report(report, arguments.json_out, arguments.input)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print("\n".join(_summary_lines(report)))
    if arguments.json_out:
        print(f"JSON report: {arguments.json_out}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
