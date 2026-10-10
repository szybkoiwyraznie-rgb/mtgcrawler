"""Prepare a small, uploadable bundle from a large PSP ISO, run on the user's PC.

The ISO (~660 MB) is too big to move whole. This tool extracts only what the remote
pipeline needs to validate and continue the process:

* ``inventory.json`` -- the ISO9660 directory inventory (paths, LBAs, sizes, signatures);
* ``system_area.bin`` -- the first 32 KiB (sectors 0..15), the UMD boot region a repacked
  disc must preserve;
* ``files/`` -- the small text-bearing members (event packages ``eventP*.EDAT`` /
  ``evept*.EDAT`` and ``PARAM.SFO``), each a few hundred KiB.

Everything is zipped so the user can upload a few MiB instead of the whole image. The ISO is
opened strictly read-only.

Usage (on the machine holding the ISO)::

    python tools/iso_prep.py prep <path-to-iso> [out_dir]

A companion ``repack`` mode rebuilds a full ISO from an unpacked tree; it is intentionally
streaming-friendly in a separate step once the inventory is available.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import iso9660

SYSTEM_AREA_BYTES = iso9660.BLOCK_SIZE * 16

# Small, text-bearing members worth bundling for the remote pipeline.
WANT_RE = re.compile(r"(eventP\d+\.EDAT|evept\d+\.EDAT|PARAM\.SFO)$", re.IGNORECASE)


def prep(iso_path: Path, out_dir: Path) -> dict:
    iso_path = Path(iso_path)
    out_dir = Path(out_dir)
    files_dir = out_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    info = iso9660.inspect_iso9660(iso_path)
    (out_dir / "inventory.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )

    with open(iso_path, "rb") as fh:
        system_area = fh.read(SYSTEM_AREA_BYTES)
    (out_dir / "system_area.bin").write_bytes(system_area)

    selected = [f for f in info["files"] if WANT_RE.search(f["path"])]
    iso9660.extract_members(iso_path, selected, files_dir)

    summary = {
        "iso": str(iso_path),
        "image_bytes": info["image_bytes"],
        "file_count": info["file_count"],
        "bundled": [f["path"] for f in selected],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")

    zip_path = out_dir.with_suffix(".zip") if out_dir.suffix != ".zip" else out_dir
    zip_path = out_dir.parent / (out_dir.name + ".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out_dir.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(out_dir.parent))
    summary["zip"] = str(zip_path)
    summary["zip_bytes"] = zip_path.stat().st_size
    return summary


def main(argv: Optional[list[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args or args[0] != "prep" or len(args) < 2:
        print("usage: iso_prep.py prep <path-to-iso> [out_dir]")
        return 2
    iso_path = Path(args[1])
    out_dir = Path(args[2]) if len(args) > 2 else Path("iso_prep_out")
    summary = prep(iso_path, out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
