#!/usr/bin/env python3
"""Build the standalone distribution zip for end users.

Run from the repository root::

    python3 tools/build_distribution.py

Produces: ``local/dist/srw-oe-translation-v<VERSION>.zip``

What goes in the zip:
  PATCH.bat              — one-click launcher
  README.md              — user instructions (copied from README_DIST.md)
  translation/           — the JSONL package files + tokeny.tsv
  tools/                 — build_translation_patch.py + all its transitive deps + pick_path.py
  docs/translator/       — glossary, voice cards, style guide, bible, briefs
"""
from __future__ import annotations

import ast
import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# ── tool dependency graph ──────────────────────────────────────────────

TOOL_STEMS: set[str] = set()  # filled by _resolve

TOOLS_TO_ALWAYS_INCLUDE = {"pick_path.py"}  # not in build chain but needed by .bat

def _resolve(tools_dir: Path) -> set[str]:
    """BFS from build_translation_patch.py through local imports."""
    tool_stems = {f.stem for f in tools_dir.glob("*.py")}

    def local_deps(fname: str) -> set[str]:
        p = tools_dir / fname
        if not p.exists():
            return set()
        tree = ast.parse(p.read_text(encoding="utf-8"))
        deps: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in tool_stems:
                        deps.add(mod)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split(".")[0]
                    if mod in tool_stems:
                        deps.add(mod)
        return deps

    queue = ["build_translation_patch"]
    needed = set(queue)
    while queue:
        cur = queue.pop(0)
        for dep in local_deps(cur + ".py"):
            if dep not in needed:
                needed.add(dep)
                queue.append(dep)
    needed |= {s.replace(".py", "") for s in TOOLS_TO_ALWAYS_INCLUDE}
    return needed


# ── main ───────────────────────────────────────────────────────────────

def main() -> None:
    repo = Path(__file__).resolve().parent.parent  # srw-oe-translation/
    tools_dir = repo / "tools"

    # version from the latest CO_NOWEGO
    version = "9"
    co_files = sorted(repo.glob("local/pakiet_v*/CO_NOWEGO_v*.txt"), reverse=True)
    if co_files:
        # extract version number from filename
        import re
        m = re.search(r"v(\d+)", co_files[0].name)
        if m:
            version = m.group(1)

    out_dir = repo / "local" / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_name = f"srw-oe-translation-v{version}.zip"
    zip_path = out_dir / zip_name

    # Resolve tool deps
    needed_stems = _resolve(tools_dir)
    print(f"Tools needed: {len(needed_stems)} files")

    # Find the latest translation package
    # Find the latest translation package (directory, not zip)
    pkg_dirs = sorted(
        [d for d in repo.glob("local/pakiet_v*/pakiet_EN_*") if d.is_dir()],
        reverse=True,
    )
    if not pkg_dirs:
        print("ERROR: No translation package found in local/pakiet_v*/")
        sys.exit(1)
    pkg_dir = pkg_dirs[0]
    print(f"Package: {pkg_dir.name}")

    # Build zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # PATCH.bat
        patch_bat = repo / "PATCH.bat"
        if patch_bat.exists():
            zf.write(patch_bat, "PATCH.bat")
        else:
            print("WARNING: PATCH.bat not found")

        # README.md (use README_DIST.md if available, else README.md)
        readme = repo / "README_DIST.md" if (repo / "README_DIST.md").exists() else repo / "README.md"
        zf.write(readme, "README.md")

        # Translation package files
        for f in sorted(pkg_dir.iterdir()):
            if f.is_file():
                zf.write(f, f"translation/{f.name}")

        # Tools
        for stem in sorted(needed_stems):
            p = tools_dir / f"{stem}.py"
            if p.exists():
                zf.write(p, f"tools/{stem}.py")

        # Docs/translator
        translator_dir = repo / "docs" / "translator"
        if translator_dir.exists():
            for f in sorted(translator_dir.rglob("*")):
                if f.is_file():
                    rel = f.relative_to(repo)
                    zf.write(f, str(rel))

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nCreated: {zip_path}")
    print(f"Size: {size_mb:.1f} MB")
    print(f"Version: v{version}")

    # Summary
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        tools_count = sum(1 for n in names if n.startswith("tools/"))
        trans_count = sum(1 for n in names if n.startswith("translation/"))
        docs_count = sum(1 for n in names if n.startswith("docs/"))
        print(f"Contents: {len(names)} files ({tools_count} tools, {trans_count} translation, {docs_count} docs)")


if __name__ == "__main__":
    main()