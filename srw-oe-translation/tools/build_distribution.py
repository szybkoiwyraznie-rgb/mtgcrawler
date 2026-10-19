#!/usr/bin/env python3
"""Build the standalone distribution zip for end users.

Run from the repository root::

    python3 tools/build_distribution.py                # English kit (pakiet_EN)
    python3 tools/build_distribution.py --lang pl      # Polish kit (tracked pakiet_PL snapshot)

Produces: ``local/release/srw-oe-translation[-pl]-v<VERSION>.zip``

What goes in the zip:
  PATCH.bat              — one-click launcher (PATCH.bat for EN, PATCH_PL.bat for PL;
                           both land as PATCH.bat inside the kit)
  README.md              — user instructions (README_DIST.md / README_DIST_PL.md)
  translation/           — the JSONL package files + tokeny.tsv
  tools/                 — build_translation_patch.py + all its transitive deps + pick_path.py
  ui_labels/, assets/    — UI texture caption specs and fonts (EN kit also carries
                           docs/translator/, the translator reference material)
"""
from __future__ import annotations

import ast
import json
import shutil
import hashlib
import tempfile
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# ── tool dependency graph ──────────────────────────────────────────────

TOOL_STEMS: set[str] = set()  # filled by _resolve

TOOLS_TO_ALWAYS_INCLUDE = {"pick_path.py"}  # not in build chain but needed by .bat

def _resolve(tools_dir: Path, entry_points=("build_translation_patch",)) -> set[str]:
    """BFS from entry points through local imports (including function-local imports)."""
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

    queue = list(entry_points)
    needed = set(queue)
    while queue:
        cur = queue.pop(0)
        for dep in local_deps(cur + ".py"):
            if dep not in needed:
                needed.add(dep)
                queue.append(dep)
    needed |= {s.replace(".py", "") for s in TOOLS_TO_ALWAYS_INCLUDE}
    return needed


# ── main ───────────────────────────────────────────────

def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Build the standalone one-click distribution zip.")
    ap.add_argument("--package", metavar="DIR",
                    help="translation package dir (default: pakiet_EN/, then local staging)")
    ap.add_argument("--lang", choices=("en", "pl"), default="en",
                    help="kit language: pl ships PATCH.bat with --lang pl, the PL README, "
                         "and materializes the tracked pakiet_PL snapshot by default")
    ap.add_argument("--version", metavar="V", help="version label for the zip name (default: from CO_NOWEGO)")
    ap.add_argument("--out", metavar="DIR", help="output dir for the zip (default: local/release)")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent  # srw-oe-translation/
    tools_dir = repo / "tools"
    pl = args.lang == "pl"

    # version from the latest CO_NOWEGO
    version = args.version
    if version is None:
        version = "1" if pl else "9"
        co_files = list(repo.glob("pakiet_EN/CO_NOWEGO_v*.txt")) \
            + list(repo.glob("local/pakiet_v*/pakiet_EN_*/CO_NOWEGO_v*.txt"))
        import re as _re
        co_files.sort(key=lambda p: (lambda m: int(m.group(1)) if m else 0)(_re.search(r"v(\d+)", p.name)), reverse=True)
        if co_files and not pl:
            # extract version number from filename
            import re
            m = re.search(r"v(\d+)", co_files[0].name)
            if m:
                version = m.group(1)

    out_dir = Path(args.out) if args.out else repo / "local" / "release"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_name = (f"srw-oe-translation-pl-v{version}.zip" if pl
                else f"srw-oe-translation-v{version}.zip")
    zip_path = out_dir / zip_name

    # Resolve tool deps
    needed_stems = _resolve(tools_dir)
    print(f"Tools needed: {len(needed_stems)} files")

    # Find the translation package: the committed pakiet_EN/ first, then local staging
    if args.package:
        pkg_dir = Path(args.package)
        if not pkg_dir.is_dir():
            print(f"ERROR: package dir not found: {pkg_dir}")
            sys.exit(1)
    elif pl:
        import pl_release_package
        staging = tempfile.TemporaryDirectory(prefix="srwoe-pl-release-")
        pkg_dir = Path(staging.name) / "translation"
        pl_release_package.materialize(repo / "pakiet_EN", repo / "pakiet_PL", pkg_dir)
    elif (repo / "pakiet_EN").is_dir() and not pl:
        pkg_dir = repo / "pakiet_EN"
    else:
        pkg_dirs = sorted(
            [d for d in repo.glob("local/pakiet_v*/pakiet_EN_*") if d.is_dir()],
            reverse=True,
        )
        if not pkg_dirs:
            print("ERROR: No translation package found (use --package DIR)")
            sys.exit(1)
        pkg_dir = pkg_dirs[0]
    print(f"Package: {pkg_dir.name} (lang={args.lang})")

    # Distribution is never allowed to hide invalid/missing active-language text.
    import translation_import
    import translation_check
    import token_map
    rows, _ = translation_import.load_rows(pkg_dir)
    checked = translation_check.check_rows(rows, field=args.lang,
        token_map=token_map.load_map(pkg_dir / "tokeny.tsv") if (pkg_dir / "tokeny.tsv").exists() else {})
    if checked["totals"]["errors"] or not checked["totals"]["filled"]:
        raise ValueError("Invalid/empty active-language release: " + str(checked["errors"][:5]))
    for required in ("PATCH_PL.bat" if pl else "PATCH.bat", "CHECK_DLC.bat", "ui_labels", "assets"):
        if not (repo / required).exists():
            raise ValueError("Required distribution input missing: " + required)

    # Build zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # PATCH.bat (the PL kit ships the Polish launcher under the same name)
        patch_bat = repo / ("PATCH_PL.bat" if pl else "PATCH.bat")
        if patch_bat.exists():
            zf.write(patch_bat, "PATCH.bat")
        else:
            print(f"WARNING: {patch_bat.name} not found")

        # Read-only check of the actually installed DLC folder, useful when a
        # correct build differs from what the game has loaded.
        checker_bat = repo / "CHECK_DLC.bat"
        if checker_bat.exists():
            checker = checker_bat.read_bytes()
            if pl:
                marker = b'--package "translation"'
                if checker.count(marker) != 1:
                    raise ValueError("Unrecognized CHECK_DLC launcher")
                checker = checker.replace(marker, marker + b' --lang pl')
            zf.writestr("CHECK_DLC.bat", checker)

        # README.md (use README_DIST_PL.md / README_DIST.md if available, else README.md)
        candidates = [repo / "README_DIST_PL.md", repo / "README_DIST.md", repo / "README.md"] \
            if pl else [repo / "README_DIST.md", repo / "README.md"]
        readme = next(p for p in candidates if p.exists())
        zf.write(readme, "README.md")

        # Translation package files
        for f in sorted(pkg_dir.iterdir()):
            if f.is_file():
                if f.suffix.lower() not in {".jsonl", ".json", ".tsv", ".txt", ".md"}:
                    raise ValueError("Unexpected file in translation package: " + f.name)
                zf.write(f, f"translation/{f.name}")

        # UI texture caption specs + fonts (the icon pipeline reads both;
        # their absence is why earlier dists "brakowaly plikow do ikon")
        for extra in ("ui_labels", "assets"):
            src_dir = repo / extra
            if src_dir.is_dir():
                for f in sorted(src_dir.rglob("*")):
                    if f.is_file():
                        zf.write(f, str(f.relative_to(repo)))
            else:
                print(f"WARNING: {extra}/ missing - icon captions will not build")

        # Tools
        for stem in sorted(needed_stems):
            p = tools_dir / f"{stem}.py"
            if p.exists():
                zf.write(p, f"tools/{stem}.py")

        # Data files are runtime dependencies too, invisible to the AST import graph.
        for data in sorted((tools_dir / "data").glob("*.json")):
            zf.write(data, f"tools/data/{data.name}")

        # Docs/translator (the English kit carries the translator reference material;
        # the Polish kit ships only the end-user README - the translator material went
        # out separately in pakiet_PL.zip)
        translator_dir = repo / "docs" / "translator"
        if translator_dir.exists() and not pl:
            for f in sorted(translator_dir.rglob("*")):
                if f.is_file():
                    rel = f.relative_to(repo)
                    zf.write(f, str(rel))

    with zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED) as zf:
        provenance = dict(language=args.lang, version=version, partial=pl,
                          validation=checked["totals"], game_data_included=False,
                          sha256_by_file={n: hashlib.sha256(zf.read(n)).hexdigest() for n in zf.namelist()})
        if pl and (pkg_dir / "PL_COVERAGE.json").exists():
            provenance["source_return"] = json.loads((pkg_dir / "PL_COVERAGE.json").read_text(encoding="utf-8"))["source_return"]
        zf.writestr("RELEASE_MANIFEST.json",json.dumps(provenance,ensure_ascii=False,indent=2)+"\n")

    with zipfile.ZipFile(zip_path) as zf:
        if zf.testzip() is not None or len(zf.namelist()) != len(set(zf.namelist())):
            raise ValueError("Invalid distribution ZIP")
        forbidden = {".iso", ".cso", ".cpk", ".edat", ".bin", ".dat", ".pbp", ".sav", ".fta"}
        if any(Path(n).suffix.lower() in forbidden for n in zf.namelist()):
            raise ValueError("Game data in distribution")

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