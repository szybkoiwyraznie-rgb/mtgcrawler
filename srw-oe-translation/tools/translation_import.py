#!/usr/bin/env python3
"""Move the English a translator typed into the scene view (``*.md``) back into the package.

The scene view (``tools/scene_view.py`` -> ``sceny/*.md``, shipped as ``sceny.zip``) is the reading
copy: every element of every scene in game order, with its place, its speaker and its Japanese text.
It is **not** sent to the game - it is a work card.  This tool reads the English out of it and writes
it into ``00_dialogue.jsonl``, which stays the single source of truth the game is built from.

The view carries an empty ``EN:`` line under every element, so the translator only types after the
colon::

    1. [Dialog - セイシロウ・クサナギ] （俺は今、宇宙貿易事業を推進する
       　民間組織『コネクト』にいる…）
       EN: (I'm now at Connect - a civilian
        organization promoting interstellar trade...)

Every following indented line belongs to the same element, so the number of line breaks stays the
same as in the Japanese text (the game draws the box around them); the two invisible characters of
the view are written back as characters (``\u23ce`` -> carriage return, ``<0x0F>`` -> the half-width
font switch), so the translator never types an invisible byte.  Lines of an element that has no
``EN:`` text are left untouched.  A text that would break the game (CP932, control tokens, line
breaks, control characters - the rules of ``tools/translation_check.py``) is **refused**, not
written, and reported, so a broken view can never clobber the package.

Usage::

    python tools/translation_import.py --views local/translation/sceny --package local/translation
    python tools/translation_import.py --views sceny.zip --package local/translation --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import translation_check as TC  # noqa: E402

MARKERS = (("\u23ce", "\r"), ("<0x0F>", "\x0f"))   # the view shows them, the game needs bytes
ELEMENT_RE = re.compile(r"^(\d+)\. \[(.*?)\] (.*)$")
EN_RE = re.compile(r"^\s*EN:\s?(.*)$")
SCENE_FILE_RE = re.compile(r"^- plik gry: (.+?) / (.+?)\s*$")


def read_views(paths: Iterable[Path]) -> Dict[Path, str]:
    """{path: text} of every ``*.md`` given, plus every ``*.md`` inside a ``*.zip``."""
    views: Dict[Path, str] = {}
    for path in paths:
        path = Path(path)
        if path.is_dir():
            for child in sorted(path.glob("*.md")):
                views[child] = child.read_text(encoding="utf-8")
        elif path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                for name in sorted(archive.namelist()):
                    if name.lower().endswith(".md"):
                        views[Path(f"{path.name}:{name}")] = archive.read(name).decode("utf-8")
        else:
            views[path] = path.read_text(encoding="utf-8")
    return views


def restore_markers(text: str) -> str:
    """Turn the visible markers of the view back into the characters the game draws with."""
    for marker, control in MARKERS:
        text = text.replace(marker, control)
    return text


def parse_view(text: str) -> Dict[Tuple[str, int], str]:
    """{(scene, order): english} for every element that has an ``EN:`` block with text."""
    found: Dict[Tuple[str, int], str] = {}
    scene: Optional[str] = None
    order: Optional[int] = None
    english: Optional[List[str]] = None

    def close() -> None:
        if scene is not None and order is not None and english is not None:
            joined = "\n".join(line.rstrip(" ") for line in english).strip("\n")
            if joined.strip():
                found[(scene, order)] = restore_markers(joined)

    for raw in text.splitlines():
        match = SCENE_FILE_RE.match(raw)
        if match:
            close()
            english, order = None, None
            scene = f"{match.group(1)}/{match.group(2)}"
            continue
        if raw.startswith("## ") or raw.startswith("- "):
            close()
            english, order = None, None
            continue
        if raw.strip() == "_koniec sceny_":
            close()
            english, order = None, None
            continue
        element = ELEMENT_RE.match(raw)
        if element:
            close()
            order = int(element.group(1))
            english = None
            continue
        if raw.strip().startswith("EN:"):
            english = [raw[raw.index("EN:") + 3:].lstrip(" ")]
            continue
        if english is not None:
            english.append(raw[3:] if raw.startswith("   ") else raw)
    close()
    return found


def load_rows(package: Path) -> Tuple[List[dict], Dict[str, List[dict]]]:
    """Every package row (``*.jsonl``) plus ``{file name: rows}``."""
    rows: List[dict] = []
    by_file: Dict[str, List[dict]] = {}
    for path in sorted(Path(package).glob("*.jsonl")):
        file_rows = [json.loads(line) for line in
                     path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in file_rows:
            row["_file"] = path.name
        by_file[path.name] = file_rows
        rows.extend(file_rows)
    return rows, by_file


def import_views(views: Dict[Path, str], package: Path, apply: bool = True) -> dict:
    """Write the English of the views into the package; ``apply=False`` only reports."""
    rows, by_file = load_rows(package)
    by_scene: Dict[Tuple[str, int], dict] = {}
    for row in rows:
        if row.get("scene") is not None and row.get("order") is not None:
            by_scene[(row["scene"], int(row["order"]))] = row

    report = {"views": len(views), "elements_with_text": 0, "imported": 0, "unchanged": 0,
              "unknown": [], "rejected": [], "written": [], "rows": len(rows)}
    touched: Dict[str, List[dict]] = {}
    for name, text in views.items():
        for (scene, order), english in sorted(parse_view(text).items()):
            report["elements_with_text"] += 1
            row = by_scene.get((scene, order))
            if row is None:
                report["unknown"].append(f"{name}:{scene}:{order}")
                continue
            if (row.get("en") or "") == english:
                report["unchanged"] += 1
                continue
            errors, _ = TC.check_row(dict(row, en=english))
            if errors:
                row_id = row.get("id", "?")
                report["rejected"].extend(f"{row_id}: {message}" for message in errors)
                continue
            row["en"] = english
            report["imported"] += 1
            touched.setdefault(row["_file"], []).append(row)
    if apply:
        for file_name, file_rows in by_file.items():
            if file_name not in touched:
                continue
            path = Path(package) / file_name
            with path.open("w", encoding="utf-8") as handle:
                for row in file_rows:
                    handle.write(json.dumps({k: v for k, v in row.items() if k != "_file"},
                                            ensure_ascii=False) + "\n")
            report["written"].append(file_name)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--views", nargs="+", type=Path, required=True,
                        help="scene view files, a folder of *.md, or a sceny.zip")
    parser.add_argument("--package", type=Path, default=Path("local/translation"),
                        help="folder with the package JSONL (the files that get written)")
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)

    views = read_views(args.views)
    report = import_views(views, args.package, apply=not args.check)
    summary = {key: value for key, value in report.items() if key not in ("unknown", "rejected")}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    for label in ("rejected", "unknown"):
        for message in report[label][:40]:
            print(f"{label[:-2]}e: {message}" if label == "rejected" else f"nieznane: {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
