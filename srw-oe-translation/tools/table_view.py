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

import export_strings as ES      # noqa: E402  (display_width -> the width the game draws)
import translation_check as TC   # noqa: E402  (fixed_slot_limit -> the measured slot sizes)
import translation_import as TI   # noqa: E402  (render_markers -> markers_for)

#: the width the game itself never exceeds on one line, and the width a typical line has
#: (measured on every dialogue, quote and narration line of the package, 2026-10-12)
WIDEST_LINE = ES.GAME_WIDEST["dialogue"]   # 52 - the hard limit of a dialogue line
TYPICAL_LINE = ES.TYPICAL_LINE             # 46 - what most of the game's lines stay within


def limit_note(view: str, element: List[dict], widest: Dict[str, int]) -> str:
    """What the translator may write for one element, in one line.

    Three cases, and the note always says which one it is:

    * ``slot`` rows sit in a fixed span (mission titles and other menu records) - the number is a
      hard budget in bytes, and the writer refuses anything longer;
    * dialogue and battle quotes are drawn in the game's text box, so the limit is a width per line
      plus the shape of the original;
    * everything else is a string in a table the writer rebuilds, so the length is free - and the
      note gives the longest original in that category as a guide, so the translator stays in the
      game's own proportions.
    """
    rows = element
    first = rows[0]
    budgets = []
    for row in rows:
        if row.get("mode") != "slot":
            continue
        budget = row.get("max_bytes")
        # the measured fixed-stride slot (mission title 39 B, map name 31, background 23, group
        # 31) caps whatever the row says - an older export carried the whole record there
        fixed = TC.fixed_slot_limit(row)
        if fixed is not None and (not isinstance(budget, int) or fixed < budget):
            budget = fixed
        if budget:
            budgets.append(int(budget))
    if budgets:
        return f"limit: {min(budgets)} B (stała szerokość — dłuższe się nie zmieści)"
    category = first.get("category") or ""
    lines = max((len((row.get("jp") or "").split("\n")) for row in rows), default=1)
    if category in ("dialogue", "battle_quote"):
        hard = ES.box_limit(first.get("kind") or category)
        return (f"limit: {TYPICAL_LINE} jedn. na linię (twardy limit {hard} jedn. — tyle gra sama "
                f"rysuje w tym miejscu); oryginał: {lines} linii")
    part = str(first.get("part"))
    longest = widest.get(part)
    guide = (f" — trzymaj się długości oryginału (najdłuższy w tej kategorii: {longest} jedn.)"
             if longest else " — trzymaj się długości oryginału")
    return f"limit: bez twardego limitu (pole rośnie){guide}"

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
    ("01_battle_quotes.jsonl", "quote"): "Kwestia",
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
    ("01_battle_quotes.jsonl", "cytaty.md", "cytaty bitewne", "Mówca"),
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
    if row.get("category") == "battle_quote":
        return f"speaker:{(row.get('speaker') or {}).get('id')}"
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


def group_label(view: str, rows: List[dict], first: dict, characters: Dict[object, dict]) -> str:
    """The heading of a group: what the translator sees above the fields."""
    if view == "cytaty.md":
        key = (first.get("speaker") or {}).get("id")
        known = characters.get(key) or {}
        name = (first.get("speaker") or {}).get("jp") or known.get("name")
        return f" — {name}" if name else f" — ID {key}"
    if view in ("postacie.md", "mechy.md", "przedmioty.md", "umiejetnosci.md"):
        name = next((row["jp"] for row in rows if row.get("part") in ("name", "name_display")), "")
        return f" — {name}" if name else ""
    return f" — {first.get('category') or ''}"


def context_lines(view: str, rows: List[dict], characters: Dict[object, dict]) -> List[str]:
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
    if view == "cytaty.md":
        key = (rows[0].get("speaker") or {}).get("id")
        known = characters.get(key) or {}
        series = known.get("series")
        if series:
            lines.append(f"- seria: {series}")
        if not (rows[0].get("speaker") or {}).get("jp") and not known.get("name"):
            lines.append("- mówca bez nazwy w grze — w grze widać, kto to mówi; w tekście zostaw "
                         "neutralny ton")
        return lines
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


def character_context(rows_by_file: Dict[str, List[dict]]) -> Dict[object, dict]:
    """``{character key: {"name": …, "series": …}}`` from ``07_names_characters.jsonl``.

    It gives a battle quote its speaker (the quote rows carry only the id of the character) and the
    series the character comes from.
    """
    found: Dict[object, dict] = {}
    for row in rows_by_file.get("07_names_characters.jsonl", []):
        if row.get("part") not in ("name", "series") or row.get("jp") in (None, "", "NoData"):
            continue
        found.setdefault(row.get("key"), {})[row["part"]] = row["jp"]
    return found


def groups(view: str, rows: List[dict], characters: Dict[object, dict] = None) -> List[dict]:
    """``[{label, context, rows}]`` - the groups of one view, in file order of their first row."""
    characters = characters or {}
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
        found.append({"label": group_label(view, group_rows, group_rows[0], characters),
                      "context": context_lines(view, group_rows, characters),
                      "elements": elements})
    return found


def render_markers(text: str) -> str:
    """The visible marker of every invisible character (the same as in the scene view)."""
    for marker, control in TI.MARKERS:
        text = text.replace(control, marker)
    return text


def widest_by_part(rows: List[dict]) -> Dict[str, int]:
    """``{part: the widest original line of that part}`` in display units, for the limit notes."""
    found: Dict[str, int] = {}
    for row in rows:
        text = row.get("jp") or ""
        if not text:
            continue
        width = max(ES.display_width(line) for line in text.split("\n"))
        part = str(row.get("part"))
        found[part] = max(found.get(part, 0), width)
    return found


def render(view: str, rows: List[dict], characters: Dict[object, dict] = None,
           lang: str = "en") -> str:
    """The whole ``*.md`` view of one table file."""
    found = groups(view, rows, characters or {})
    widest = widest_by_part(rows)
    if lang == "pl":
        intro = ("Pod każdym elementem jest linia `limit:` (ile wolno napisać), linia `EN:` — "
                 "gotowe tłumaczenie angielskie (kontekst i terminologia — NIE zmieniaj jej) — "
                 "i linia `PL:` — tam wpisuje się tłumaczenie polskie. Elementy bez linii `PL:` "
                 "dziedziczą tłumaczenie z elementu, który ma ten sam tekst — nic tam nie wpisuj. "
                 "Gotowy plik wraca do pakietu jednym poleceniem "
                 "`tools/translation_import.py --lang pl`.")
    else:
        intro = ("Pod każdym elementem jest linia `limit:` (ile wolno napisać) i linia `EN:` — tam "
                 "wpisuje się tłumaczenie. Elementy bez linii `EN:` dziedziczą tłumaczenie z "
                 "elementu, który ma ten sam tekst — nic tam nie wpisuj. Gotowy plik wraca do "
                 "pakietu jednym poleceniem `tools/translation_import.py`.")
    lines = [f"# {TITLES[view]}", "", intro, ""]
    for index, group in enumerate(found, start=1):
        word = GROUP_WORD[view]
        lines.append(f"## {word} {index}/{len(found)}{group['label']}")
        lines.extend(group["context"])
        lines.append("")
        for number, element in enumerate(group["elements"], start=1):
            row = element[0]
            text = render_markers(row["jp"]).replace("\n", "\n   ")
            lines.append(f"{number}. [{element_label(view, row)}] {text}")
            if all(item.get("copy_of") for item in element):
                lines.append("   (ten sam tekst co wcześniej — tłumaczenie dziedziczy się "
                             "automatycznie, nic tu nie wpisuj)")
                continue
            lines.append(f"   limit: {limit_note(view, element, widest)}"
                         .replace("limit: limit: ", "limit: "))
            lines.append(f"   EN: {render_markers(row.get('en') or '').replace(chr(10), chr(10) + '   ')}".rstrip())
            if lang == "pl":
                lines.append(f"   PL: {render_markers(row.get('pl') or '').replace(chr(10), chr(10) + '   ')}".rstrip())
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
    characters = character_context(rows_by_file)
    plan: Dict[str, List[List[List[dict]]]] = {}
    for source, view, _, _ in FILES:
        plan[view] = [group["elements"]
                      for group in groups(view, rows_by_file.get(source, []), characters)]
    return plan


def lookup(package: Path) -> Dict[str, List[List[List[dict]]]]:
    """``{view file: [[[row, ...], ...], ...]}`` - the plan of every view of a package on disk."""
    return plan_from({source: load(package, source) for source, _, _, _ in FILES})


def write_views(package: Path, out: Path, force: bool = False, lang: str = "en") -> Dict[str, object]:
    """Write the six table views into ``out`` (a view with unsaved work is left alone).

    ``lang="pl"`` renders the Polish views: the English block as a read-only reference and
    the ``PL:`` slot filled from the package's ``pl`` field.
    """
    out.mkdir(parents=True, exist_ok=True)
    plan = lookup(package)
    counts: Dict[str, object] = {"files": {}, "skipped": []}
    for source, view, _, _ in FILES:
        rows = load(package, source)
        if not rows:
            continue
        text = render(view, rows, character_context({source: load(package, source)
                                                     for source, _, _, _ in FILES}), lang)
        target = out / view
        if not force and target.exists():
            edited = 0
            marker = "PL:" if lang == "pl" else "EN:"
            for line in target.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith(marker) and line.split(marker, 1)[1].strip():
                    edited += 1
            if edited:
                counts["skipped"].append(f"{view} ({edited} linii {lang.upper()} do zaimportowania)")
                continue
        target.write_text(text, encoding="utf-8")
        counts["files"][view] = sum(len(group) for group in plan[view])
    return counts


def make_zip(out: Path, archive: Path) -> int:
    files = sorted(out.glob("*.md")) + sorted(out.glob("*.txt"))   # views + the instruction
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        for path in files:
            handle.write(path, path.name)
    return len(files)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--out", type=Path, default=Path("local/translation/widoki"))
    parser.add_argument("--lang", choices=("en", "pl"), default="en",
                        help="pl = Polish views: EN block as reference + the PL: slot to fill")
    parser.add_argument("--zip", action="store_true", help="also pack the views into widoki[_PL].zip")
    parser.add_argument("--force", action="store_true",
                        help="overwrite views that still hold untransferred translations")
    args = parser.parse_args(argv)

    counts = write_views(args.package, args.out, force=args.force, lang=args.lang)
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    if args.zip:
        archive = args.out.parent / ("widoki_PL.zip" if args.lang == "pl" else "widoki.zip")
        print(f"zip: {make_zip(args.out, archive)} files -> {archive}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
