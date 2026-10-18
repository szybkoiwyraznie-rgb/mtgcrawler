#!/usr/bin/env python3
"""Build the reproducible, game-data-free PL v3 batch font-test kit."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_distribution
import test_pl_package

ROOT = Path(__file__).resolve().parent.parent


def build(out: Path, package: Path = ROOT / "pakiet_EN") -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    tools = ROOT / "tools"
    deps = build_distribution._resolve(tools, ("build_translation_patch", "verify_pl_test"))
    with tempfile.TemporaryDirectory() as tmp:
        probes = Path(tmp) / "translation"
        counts = test_pl_package.build(package, probes)
        wanted = {"dialogue_rows": 16, "mission_rows": 1, "unit_rows": 3, "weapon_rows": 16}
        if any(counts[k] != v for k, v in wanted.items()):
            raise ValueError(f"unexpected source probe coverage: {counts}")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(ROOT / "TEST_PL.bat", "TEST_PL.bat")
            zf.write(ROOT / "README_TEST_PL.md", "README_TEST_PL.md")
            for stem in sorted(deps):
                zf.write(tools / f"{stem}.py", f"tools/{stem}.py")
            zf.write(tools / "data/pl_glyphs_8x14.json", "tools/data/pl_glyphs_8x14.json")
            # Only package data, no local reports, release notes, fonts or game containers.
            for path in sorted(probes.iterdir()):
                if path.suffix in (".jsonl", ".tsv"):
                    zf.write(path, f"translation/{path.name}")
            zf.writestr("KIT_VERSION.txt", "PL font batch test v3 / 2026-10-18\n")
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP members")
    return {"name": out.name, "bytes": out.stat().st_size,
            "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
            "files": len(names), "probe_counts": counts,
            "scope": "patch tools and probe package only; no game files"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path,
                    default=ROOT / "local/release/srw-oe-test-pl-v3.zip")
    ap.add_argument("--package", type=Path, default=ROOT / "pakiet_EN")
    args = ap.parse_args()
    print(json.dumps(build(args.out, args.package), indent=2))


if __name__ == "__main__":
    main()
