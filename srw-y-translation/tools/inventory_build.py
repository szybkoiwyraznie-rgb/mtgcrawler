#!/usr/bin/env python3
"""Inventory an installed game folder without copying anything out of it.

The report contains metadata only: relative paths, sizes, magic numbers and
SHA-256 of small files. It never contains file contents, so it is safe to hand
over as the first input of the SRW Y feasibility spike.

Usage:
    python3 tools/inventory_build.py --root "C:/Games/SRWY" --out build_report.json
    python3 tools/inventory_build.py --root . --hash-limit-mb 4 --print-paths 200

The tool is read-only: it opens files for reading only, writes nothing except the
report path given on the command line.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA = 1

# Enough of a header to recognise the container families this project cares about.
MAGIC_TABLE = (
    (b"CPK ", "cri_cpk"),
    (b"UnityFS", "unity_bundle"),
    (b"UnityWeb", "unity_bundle_web"),
    (b"UnityRaw", "unity_bundle_raw"),
    (b"PK\x03\x04", "zip"),
    (b"\x1f\x8b", "gzip"),
    (b"BZh", "bzip2"),
    (b"\xfd7zXZ\x00", "xz"),
    (b"Rar!", "rar"),
    (b"7z\xbc\xaf\x27\x1c", "7z"),
    (b"MZ", "pe_executable"),
    (b"\x7fELF", "elf"),
    (b"SQLite format 3\x00", "sqlite"),
    (b"BLTU", "bltu_table"),
    (b"KTSR", "ktsr"),
)

# Files whose presence tells us what we are looking at.
NOTABLE_NAMES = {
    "gameassembly.dll": "il2cpp_gameassembly",
    "unityplayer.dll": "unity_player",
    "global-metadata.dat": "il2cpp_metadata",
    "melonloader": "melonloader_present",
    "bepinex": "bepinex_present",
    "doorstop_config.ini": "doorstop_present",
    "winhttp.dll": "doorstop_proxy",
}

# Directory names that usually hold one language's assets in Unity games.
LANGUAGE_HINTS = {"en", "english", "ja", "jp", "japanese", "zh", "zh_cn", "zh_tw",
                  "zh-cn", "zh-tw", "ko", "korean", "kr", "sc", "tc", "lang",
                  "languages", "localization", "localisation", "text", "i18n"}

TEXT_EXTENSIONS = {".json", ".csv", ".tsv", ".txt", ".xml", ".yaml", ".yml",
                   ".po", ".resx", ".bytes", ".asset", ".strings"}


def sniff_magic(path: Path) -> str | None:
    """Return a container family name, or None when the header is unknown."""
    try:
        with path.open("rb") as handle:
            head = handle.read(16)
    except OSError:
        return None
    for magic, name in MAGIC_TABLE:
        if head.startswith(magic):
            return name
    return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human(size: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TiB"


def inventory(root: Path, hash_limit_bytes: int = 0) -> dict:
    """Walk ``root`` and build the metadata report.

    ``hash_limit_bytes`` == 0 means "do not hash anything" (fast mode); a file is
    hashed only when its size is at or below the limit.
    """
    root = root.resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    by_extension: Counter[str] = Counter()
    by_extension_bytes: Counter[str] = Counter()
    by_top: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    families: Counter[str] = Counter()
    flags: dict[str, list[str]] = defaultdict(list)
    files: list[dict] = []
    language_dirs: set[str] = set()
    total_bytes = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        current = Path(dirpath)
        rel_dir = current.relative_to(root)
        for name in dirnames:
            low = name.lower()
            if low in LANGUAGE_HINTS:
                language_dirs.add(str((rel_dir / name)).replace("\\", "/"))
            for key, flag in NOTABLE_NAMES.items():
                if key in low:
                    flags[flag].append(str((rel_dir / name)).replace("\\", "/"))
        for name in sorted(filenames):
            path = current / name
            try:
                size = path.stat().st_size
            except OSError:
                continue
            rel = str(path.relative_to(root)).replace("\\", "/")
            ext = path.suffix.lower() or "<none>"
            top = rel.split("/", 1)[0] if "/" in rel else "<root>"
            by_extension[ext] += 1
            by_extension_bytes[ext] += size
            by_top[top]["files"] += 1
            by_top[top]["bytes"] += size
            total_bytes += size

            family = sniff_magic(path)
            if family:
                families[family] += 1
            low = name.lower()
            for key, flag in NOTABLE_NAMES.items():
                if key in low:
                    flags[flag].append(rel)

            entry = {"path": rel, "bytes": size}
            if family:
                entry["magic"] = family
            if ext in TEXT_EXTENSIONS and size <= max(hash_limit_bytes, 4 << 20):
                entry["text_like"] = True
            if hash_limit_bytes and size <= hash_limit_bytes:
                entry["sha256"] = sha256(path)
            files.append(entry)

    files.sort(key=lambda entry: entry["path"])

    report = {
        "schema": SCHEMA,
        "kind": "game build inventory (metadata only, no file contents)",
        "root_name": root.name,
        "totals": {"files": len(files), "bytes": total_bytes},
        "by_top_level": {
            key: {"files": value["files"], "bytes": value["bytes"]}
            for key, value in sorted(by_top.items())
        },
        "by_extension": {
            key: {"files": by_extension[key], "bytes": by_extension_bytes[key]}
            for key in sorted(by_extension, key=lambda k: (-by_extension[k], k))
        },
        "container_families": dict(sorted(families.items())),
        "flags": {key: sorted(value) for key, value in sorted(flags.items())},
        "language_hint_dirs": sorted(language_dirs),
        "hash_limit_bytes": hash_limit_bytes,
        "files": files,
    }
    return report


def summary(report: dict, print_paths: int = 0) -> str:
    lines = [
        f"root: {report['root_name']}",
        f"files: {report['totals']['files']:,}  total: {human(report['totals']['bytes'])}",
        "",
        "top-level:",
    ]
    for name, data in report["by_top_level"].items():
        lines.append(f"  {name:<28} {data['files']:>7,} files  {human(data['bytes']):>10}")
    lines.append("")
    lines.append("container families:")
    for name, count in report["container_families"].items():
        lines.append(f"  {name:<20} {count:,}")
    if report["flags"]:
        lines.append("")
        lines.append("flags:")
        for name, paths in report["flags"].items():
            preview = ", ".join(paths[:3])
            more = f" (+{len(paths) - 3})" if len(paths) > 3 else ""
            lines.append(f"  {name:<20} {preview}{more}")
    if report["language_hint_dirs"]:
        lines.append("")
        lines.append("language-like directories: " + ", ".join(report["language_hint_dirs"][:12]))
    biggest = sorted(report["files"], key=lambda f: -f["bytes"])[:10]
    if biggest:
        lines.append("")
        lines.append("largest files:")
        for entry in biggest:
            magic = f"  [{entry['magic']}]" if "magic" in entry else ""
            lines.append(f"  {human(entry['bytes']):>10}  {entry['path']}{magic}")
    if print_paths:
        lines.append("")
        lines.append(f"first {print_paths} paths:")
        for entry in report["files"][:print_paths]:
            lines.append(f"  {human(entry['bytes']):>10}  {entry['path']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path, help="game folder to scan")
    parser.add_argument("--out", type=Path, help="write the JSON report here")
    parser.add_argument("--hash-limit-mb", type=float, default=0.0,
                        help="also hash files up to this size (default: no hashing)")
    parser.add_argument("--print-paths", type=int, default=0,
                        help="print the first N paths to stdout")
    args = parser.parse_args(argv)

    report = inventory(args.root, int(args.hash_limit_mb * (1 << 20)))
    text = summary(report, args.print_paths)
    print(text)
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(f"\nreport written: {args.out} ({args.out.stat().st_size:,} B)")
    else:
        print("\n(no --out given: report not saved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
