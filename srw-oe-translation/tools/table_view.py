#!/usr/bin/env python3
"""Render the name and table categories of the package as readable views for the translator.

The scene views (``tools/scene_view.py``) cover the story.  The other categories are tables, and a
translator should not have to read JSON:  this tool renders them as ``*.md`` files in which every
element is followed by an ``EN:`` line, exactly like the scene views, and every group carries the
context a name needs - the series it comes from, the unit it belongs to, the item it describes::

    # mechy

    ## Jednostka 12/393 — ライジンオー
    - seria: 絶対無敵ライジンオー

    1. [Nazwa] ライジンオー
       EN:
    2. [Nazwa na ekranie] ライジンオー
       EN:
    3. [Seria] 絶対無敵ライジンオー
       EN:
    ...
    7. [Broń 1 — nazwa] ライジンクロー
       EN:

An element is addressed by the number of its group (``## Jednostka 12/393``) and its own number
(``3.``); ``tools/translation_import.py`` reads the English back into the package JSONL the same way
it reads the scenes.  Files:

    postacie.md           <- 07_names_characters.jsonl     (jedna grupa na postać)
    mechy.md              <- 08_names_units_weapons.jsonl  (jedna grupa na jednostkę + jej bronie)
    przedmioty.md         <- 02_items.jsonl                (jedna grupa na przedmiot)
    umiejetnosci.md       <- 03_skills.jsonl               (jedna grupa na umiejętność)
    teksty-config.md      <- 04_config_text.jsonl          (grupa na kategorię)
    teksty-misji.md       <- 05_mission_text.jsonl         (grupa na kategorię)

Usage:
    python tools/table_view.py --package local/translation --out local/translation/widoki [--zip]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import translation_import as TI   # noqa: E402  (render_markers -> markers_for)

# the label of every field, as the translator sees it in the view
PART_LABEL = {
    ("02_items.jsonl", "name"): "Nazwa",
    ("02_items.jsonl", "effect"): "Opis efektu",
    ("03_skills.jsonl", "name"): "Nazwa",
    ("03_skills.jsonl", "name_level"): "Nazwa z poziomem",
    ("03_skills.jsonl", "effect"): "Opis efektu",
    ("03_skills.jsonl", "effect_brief"): "Opis skrócony",
    ("03_skills.jsonl", "label"): "Etykieta",
    ("07_names_characters.jsonl", "name"): "Imię w grze",
    ("07_names_characters.jsonl", "name_short"): "Imię krótkie (lista)",
    ("07_names_characters.jsonl", "name_full"): "Imię pełne (dialogi)",
    ("07_names_characters.jsonl", "name_narrow"): "Imię wąskie (półszerokie znaki)",
    ("07_names_characters.jsonl", "nickname"): "Przezwisko",
    ("07_names_characters.jsonl", "series"): "Seria",
    ("07_names_characters.jsonl", "voice_actor"): "Aktor głosowy",
    ("07_names_characters.jsonl", "entry"): "Tekst w księdze",
    ("08_names_units_weapons.jsonl", "name"): "Nazwa",
    ("08_names_units_weapons.jsonl", "name_display"): "Nazwa na ekranie",
    ("08_names_units_weapons.jsonl", "series"): "Seria",
    ("08_names_units_weapons.jsonl", "length"): "Długość",
    ("08_names_units_weapons.jsonl", "weight"): "Masa",
    ("08_names_units_weapons.jsonl", "name_short"): "Skrót (półszerokie znaki)",
    ("04_config_text.jsonl", "text"): "Tekst",
    ("05_mission_text.jsonl", "text"): "Tekst",
    ("05_mission_text.jsonl", "title"): "Tytuł",
    ("05_mission_text.jsonl", "name"): "Nazwa",
    ("05_mission_text.jsonl", "series"): "Seria",
    ("05_mission_text.jsonl", "title_narrow"): "Tytuł (półszerokie znaki)",
    ("05_mission_text.jsonl", "note_a"): "Uwaga A",
    ("05_mission_text.jsonl", "note_b"): "Uwaga B",
}

# the six table files: what the view file is called, what it is titled and how it is grouped
FILES = (
    ("07_names_characters.jsonl", "postacie.md", "postacie", "Postać"),
    ("08_names_units_weapons.jsonl", "mechy.md", "mechy", "Jednostka"),
    ("02_items.jsonl", "przedmioty.md", "przedmioty", "Przedmiot"),
    ("03_skills.jsonl", "umiejetnosci.md", "umiejetnosci", "Umiejętność"),
    ("04_config_text.jsonl", "teksty-config.md", "teksty config", "Sekcja"),
    ("05_mission_text.jsonl", "teksty-misji.md", "teksty misji", "Sekcja"),
)
VIEW_TO_FILE = {view: source for source, view, _, _ in FILES}
FILE_TO_VIEW = {source: view for source, view, _, _ in FILES}
TITLES = {view: title for _, view, title, _ in FILES}
GROUP_WORD = {view: word for _, view, _, word in FILES}


def head(row: dict) -> str:
    """``char:1244`` / ``unit:12`` / ``weapon:12:3`` / ``item:…:r0`` - the id without its field."""
    parts = str(row.get("id") or "").split(":")
    return ":".join(parts[:-1]) if len(parts) > 1 else str(row.get("id") or "")


def group_key(row: dict) -> str:
    """The identity of the group a row belongs to (one character, one unit, one item, one category)."""
    prefix = str(row.get("id") or "").split(":")[0]
    if prefix == "weapon":                      # weapons live under their unit
        parts = str(row["id"]).split(":")
        return f"unit:{parts[1]}"
    if prefix in ("unit", "robonote"):
        return f"unit:{str(row['id']).split(':')[1]}"
    if prefix == "char":
        return f"char:{str(row['id']).split(':')[1]}"
    if prefix in ("item", "skill"):
        return head(row)
    return f"category:{row.get('category')}"    # 04 / 05: a group per category


def group_label(view: str, rows: List[dict], first: dict) -> str:
    """The heading of a group: what the translator sees above the fields."""
    if view in ("postacie.md", "mechy.md", "przedmioty.md", "umiejetnosci.md"):
        name = next((row["jp"] for row in rows if row.get("part") in ("name", "name_display")), "")
        return f" — {name}" if name else ""
    return f" — {first.get('category') or ''}"


def context_lines(view: str, rows: List[dict]) -> List[str]:
    """The ``- klucz: wartość`` lines that give the group its context (a series, a voice actor)."""
    def value(*parts: str, unit: Optional[str] = None) -> Optional[str]:
        for row in rows:
            if unit is not None and f":{unit}:" not in row["id"] and not row["id"].startswith(
                    f"weapon:{unit}:"):
                continue
            if row.get("part") in parts and row.get("jp") not in (None, ""):
                return row["jp"]
        return None

    lines: List[str] = []
    if view == "postacie.md":
        series = value("series")
        actor = value("voice_actor")
        if series:
            lines.append(f"- seria: {series}")
        if actor:
            lines.append(f"- głos: {actor}")
    elif view == "mechy.md":
        series = value("series")
        if series:
            lines.append(f"- seria: {series}")
        length, weight = value("length"), value("weight")
        if length:
            lines.append(f"- długość: {length}")
        if weight:
            lines.append(f"- masa: {weight}")
    return lines


def weapon_label(row: dict) -> str:
    """``Broń 3 — nazwa`` / ``Broń 3 — skrót`` for a weapon field."""
    parts = str(row["id"]).split(":")
    slot = int(parts[2]) + 1
    what = "nazwa" if row.get("part") == "name" else "skrót"
    return f"Broń {slot} — {what}"


def element_key(view: str, row: dict) -> str:
    """The identity of one element inside its group.

    The game reads the same field of the same character (or unit) from several chapter tables, so a
    group holds those rows as **one** element (as long as the Japanese text is the same too): the
    translator writes the text once and every row of the element gets it.  The flat ``text``
    categories (04, 05) have no fields - there every single row is an element of its own.
    """
    if view in ("teksty-config.md", "teksty-misji.md"):
        return str(row.get("id"))
    if view == "mechy.md" and str(row.get("id") or "").startswith("weapon:"):
        parts = str(row["id"]).split(":")
        return f"weapon:{parts[2]}:{row.get('part')}"
    return str(row.get("part"))


def element_label(view: str, row: dict) -> str:
    if view == "mechy.md" and str(row.get("id") or "").startswith("weapon:"):
        return weapon_label(row)
    return PART_LABEL.get((VIEW_TO_FILE.get(view, ""), row.get("part")), "") or \
        (row.get("part") or "Tekst")


def groups(view: str, rows: List[dict]) -> List[dict]:
    """``[{label, context, rows}]`` - the groups of one view, in file order of their first row."""
    order: List[str] = []
    by_key: Dict[str, List[dict]] = collections.defaultdict(list)
    for row in rows:
        if "jp" not in row or "en" not in row:
            continue
        key = group_key(row)
        if key not in by_key:
            order.append(key)
        by_key[key].append(row)
    found = []
    for key in order:
        group_rows = by_key[key]
        elements: List[List[dict]] = []
        index: Dict[tuple, List[dict]] = {}
        for row in group_rows:
            # rows are one element only when they carry the *same* field and the *same* Japanese
            # text; the same offset can hold two different strings, and then both are elements
            element_id = (element_key(view, row), row.get("jp"))
            if element_id not in index:
                index[element_id] = []
                elements.append(index[element_id])
            index[element_id].append(row)
        found.append({"label": group_label(view, group_rows, group_rows[0]),
                      "context": context_lines(view, group_rows), "elements": elements})
    return found


def render_markers(text: str) -> str:
    """The visible marker of every invisible character (the same as in the scene view)."""
    for marker, control in TI.MARKERS:
        text = text.replace(control, marker)
    return text


def render(view: str, rows: List[dict], total: Optional[int] = None) -> str:
    """The whole ``*.md`` view of one table file."""
    found = groups(view, rows)
    lines = [f"# {TITLES[view]}", "",
             "Pod każdym elementem jest linia `EN:` — tam wpisuje się tłumaczenie. "
             "Gotowy plik wraca do pakietu jednym poleceniem `tools/translation_import.py`.", ""]
    for index, group in enumerate(found, start=1):
        word = GROUP_WORD[view]
        lines.append(f"## {word} {index}/{len(found)}{group['label']}")
        lines.extend(group["context"])
        lines.append("")
        for number, element in enumerate(group["elements"], start=1):
            row = element[0]
            text = render_markers(row["jp"]).replace("\n", "\n   ")
            lines.append(f"{number}. [{element_label(view, row)}] {text}")
            english = render_markers(row.get("en") or "").replace("\n", "\n   ")
            lines.append(f"   EN: {english}".rstrip())
        lines.append("")
    return "\n".join(lines)


def load(package: Path, source: str) -> List[dict]:
    path = Path(package) / source
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def plan_from(rows_by_file: Dict[str, List[dict]]) -> Dict[str, List[List[List[dict]]]]:
    """The plan of every view built from rows that are already loaded (they are the package rows).

    Both the renderer and the importer build the plan with this function, so the numbers of a view
    always mean the same rows on both sides.  One element can hold several package rows (the same
    field read from several chapter tables); all of them carry the same text.
    """
    plan: Dict[str, List[List[List[dict]]]] = {}
    for source, view, _, _ in FILES:
        plan[view] = [group["elements"] for group in groups(view, rows_by_file.get(source, []))]
    return plan


def lookup(package: Path) -> Dict[str, List[List[List[dict]]]]:
    """``{view file: [[[row, ...], ...], ...]}`` - the plan of every view of a package on disk."""
    return plan_from({source: load(package, source) for source, _, _, _ in FILES})


def write_views(package: Path, out: Path, force: bool = False) -> Dict[str, object]:
    """Write the six table views into ``out`` (a view with unsaved English is left alone)."""
    out.mkdir(parents=True, exist_ok=True)
    plan = lookup(package)
    counts: Dict[str, object] = {"files": {}, "skipped": []}
    for source, view, _, _ in FILES:
        rows = load(package, source)
        if not rows:
            continue
        text = render(view, rows)
        target = out / view
        if not force and target.exists():
            edited = 0
            for line in target.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("EN:") and line.split("EN:", 1)[1].strip():
                    edited += 1
            if edited:
                counts["skipped"].append(f"{view} ({edited} linii EN do zaimportowania)")
                continue
        target.write_text(text, encoding="utf-8")
        counts["files"][view] = sum(len(group) for group in plan[view])
    return counts


def make_zip(out: Path, archive: Path) -> int:
    files = sorted(out.glob("*.md"))
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        for path in files:
            handle.write(path, path.name)
    return len(files)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--out", type=Path, default=Path("local/translation/widoki"))
    parser.add_argument("--zip", action="store_true", help="also pack the views into widoki.zip")
    parser.add_argument("--force", action="store_true",
                        help="overwrite views that still hold untransferred English")
    args = parser.parse_args(argv)

    counts = write_views(args.package, args.out, force=args.force)
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    if args.zip:
        archive = args.out.parent / "widoki.zip"
        print(f"zip: {make_zip(args.out, archive)} files -> {archive}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
