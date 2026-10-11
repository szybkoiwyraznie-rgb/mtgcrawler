"""Collect everything needed to diagnose a run into one ZIP, without the game binaries.

Included: REPORT.txt, registry.json, inputs.csv, packages.csv, boundary_probe.json (counts only), translation/template_report.txt (counts only), logs/ (converter call logs),
and text/<package>/manifest.json (the text export manifests). Excluded: packages/, iso/,
staging/, gates/, _cache/, and the unit/segment files, which are large and reproducible.
Every included file is listed with its size and SHA-256 in BUNDLE_INDEX.txt.

Usage: python tools/diagnostic_bundle.py <run folder> [--out <zip path>]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path
from typing import Optional

TOP_LEVEL_FILES = (
    "REPORT.txt",
    "registry.json",
    "inputs.csv",
    "packages.csv",
    "boundary_probe.json",
    "layout_probe.zip",
    "translation/template_report.txt",
)
INDEX_NAME = "BUNDLE_INDEX.txt"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _collect(run_dir: Path) -> list[Path]:
    files = [run_dir / name for name in TOP_LEVEL_FILES if (run_dir / name).is_file()]
    logs = run_dir / "logs"
    if logs.is_dir():
        files += sorted(p for p in logs.rglob("*") if p.is_file() and not p.is_symlink())
    text = run_dir / "text"
    if text.is_dir():
        files += sorted(p for p in text.glob("*/manifest.json") if p.is_file() and not p.is_symlink())
    return files


def write_bundle(run_dir: Path, out: Optional[Path] = None) -> Path:
    """Write the diagnostic ZIP for `run_dir` and return its path."""
    run_dir = run_dir.expanduser().resolve(strict=True)
    if not (run_dir / "registry.json").is_file():
        raise FileNotFoundError(f"not a finished run folder (no registry.json): {run_dir}")
    out = out or run_dir / f"diagnostics_{run_dir.name}.zip"
    files = _collect(run_dir)
    index_lines = ["# Files in this bundle: size in bytes, SHA-256, path inside the ZIP", ""]
    for path in files:
        arcname = path.relative_to(run_dir).as_posix()
        index_lines.append(f"{path.stat().st_size}\t{_sha256(path)}\t{arcname}")
    index_text = "\n".join(index_lines) + "\n"
    staging = out.with_name(out.name + ".partial")
    with zipfile.ZipFile(staging, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, arcname=path.relative_to(run_dir).as_posix())
        archive.writestr(INDEX_NAME, index_text)
    staging.replace(out)
    return out


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path, help="run folder (the one containing registry.json)")
    parser.add_argument("--out", type=Path, help="ZIP path (default: inside the run folder)")
    args = parser.parse_args(argv)
    try:
        print(write_bundle(args.run_dir, args.out.expanduser().resolve() if args.out else None))
    except (OSError, FileNotFoundError) as error:
        print(f"Could not write the bundle: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
