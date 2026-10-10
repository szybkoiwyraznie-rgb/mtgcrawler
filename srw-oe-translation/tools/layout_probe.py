"""Collect only the header and table bytes of the packages whose names collide, into one small ZIP.

Run it once on the user's PC after a run:
    python tools/layout_probe.py "<game input folder>" "<run folder>"

For each top-level package whose listing is `incomplete` (entries share a name), the ZIP gets
the bytes before the CPK content offset (the header, TOC, and ITOC tables; capped at 16 MiB, or
1 MiB when the header cannot be read), plus `layout.json` with the table layout, the entry count,
whether offsets exist, and the SHA-256 of each whole file. No entry data is copied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_table  # noqa: E402

HEADER_CAP = 16 * 1024 * 1024
FALLBACK_CAP = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _describe(path: Path) -> tuple[dict[str, Any], int]:
    """Layout facts and the number of header bytes to keep."""
    size = path.stat().st_size
    try:
        table = cpk_table.read_cpk_table(path)
    except Exception as exc:  # noqa: BLE001 - the probe must still record the file
        return {"table_error": f"{type(exc).__name__}: {str(exc)[:300]}"}, min(size, FALLBACK_CAP)
    entries = table.get("entries") or []
    header = table.get("header") or {}
    facts = {
        "table_error": None,
        "content_offset": header.get("content_offset"),
        "toc_offset": header.get("toc_offset"),
        "itoc_offset": header.get("itoc_offset"),
        "etoc_offset": header.get("etoc_offset"),
        "data_base": table.get("data_base"),
        "entries": len(entries),
        "entries_with_offsets": sum(entry.get("absolute_offset") is not None for entry in entries),
        "compressed_entries": sum(bool(entry.get("compressed")) for entry in entries),
        "distinct_names": len({entry.get("name") for entry in entries}),
    }
    cut = header.get("content_offset") or 0
    if not cut or cut > size:
        cut = min(size, FALLBACK_CAP)
    return facts, min(cut, HEADER_CAP, size)


def build_probe(input_root: Path, run_dir: Path, out: Optional[Path] = None) -> Path:
    registry = json.loads((run_dir / "registry.json").read_text(encoding="utf-8"))
    selected = [
        package
        for package in registry["packages"]
        if package.get("depth") == 0 and (package.get("listing_check") or {}).get("status") == "incomplete"
    ]
    out = out or run_dir / "layout_probe.zip"
    layout: dict[str, Any] = {"packages": [], "note": "header/table bytes only; no entry data"}
    staging = out.with_name(out.name + ".partial")
    with zipfile.ZipFile(staging, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for package in selected:
            source = input_root.joinpath(*package["source_path"].split("/"))
            record: dict[str, Any] = {
                "package_id": package["package_id"],
                "source_path": package["source_path"],
                "present": source.is_file(),
                "listing_duplicate_entries": (package.get("listing_check") or {}).get("duplicate_entries"),
                "hidden_entries_status": (package.get("hidden_entries") or {}).get("status"),
            }
            if source.is_file():
                facts, cut = _describe(source)
                record.update(facts)
                record["file_bytes"] = source.stat().st_size
                record["file_sha256"] = _sha256(source)
                record["header_bytes_kept"] = cut
                with source.open("rb") as stream:
                    head = stream.read(cut)
                archive.writestr(f"headers/{package['package_id']}.head", head)
            layout["packages"].append(record)
        archive.writestr("layout.json", json.dumps(layout, indent=2, ensure_ascii=False) + "\n")
    staging.replace(out)
    return out


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_root", type=Path, help="the game input folder used for the run")
    parser.add_argument("run_dir", type=Path, help="the run folder (contains registry.json)")
    parser.add_argument("--out", type=Path, help="ZIP path (default: layout_probe.zip in the run folder)")
    args = parser.parse_args(argv)
    try:
        out = build_probe(
            args.input_root.expanduser().resolve(strict=True),
            args.run_dir.expanduser().resolve(strict=True),
            args.out.expanduser().resolve() if args.out else None,
        )
    except (OSError, KeyError, ValueError) as error:
        print(f"Could not build the layout probe: {error}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
