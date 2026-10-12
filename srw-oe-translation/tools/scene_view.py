#!/usr/bin/env python3
"""Render the translation package as a readable script: one file per episode, scene by scene.

The JSONL files are what the game reads back; this view is for the person (or the assistant)
translating, so that the context of a scene is visible instead of a flat line-by-line list:

    ## Scena 12/293 — 試作レイバー暴走事件
    - odcinek: １話 メインミッション (episode 1)
    - miejsce: ジオン軍基地／オデッサ (element 74)
    - uczestnicy:
      - シロー・アマダ — 機動戦士ガンダム 第０８ＭＳ小隊
      - アイナ・サハリン — 機動戦士ガンダム 第０８ＭＳ小隊

    T1. [Tytuł misji] 試作レイバー暴走事件
       EN:
    1. [Narracja] 西暦２０５０年……
       EN:
    2. [Dialog - シロー・アマダ] ここは……
       EN:

The header carries only what helps the translation: the episode, the place the scene happens in
(also an element of the list, so it gets translated) and **who takes part** - the Japanese name of
every speaker in order of appearance plus the series the character comes from, so that a name is
never translated blind.  ``[kopia]`` elements repeat a line of another scene: their English is
filled by ``tools/translation_copy.py``, so they carry no ``EN:`` line.

The scene is identified by its number (``## Scena 8/293``), which is the ``seq`` of
``06_scenes.jsonl`` - the name of the game file stays out of the translator's way.

Usage:
    python tools/scene_view.py --package local/translation --out local/translation/sceny [--zip]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import translation_import as TI

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

KIND_LABEL = {
    "dialogue": "Dialog",
    "narration": "Narracja",
    "location": "Miejsce",
    "scene_title": "Nagłówek miejsca",
    "help": "Pomoc",
    "label": "Etykieta",
    "condition_victory": "Warunek zwycięstwa",
    "condition_defeat": "Warunek porażki",
    "embedded": "Tekst misji",
}


def load_package(package: Path) -> dict:
    """Everything the view needs from the package (all four files are optional except 00 and 06).

    * ``rows`` - ``00_dialogue.jsonl``, the text of the scenes,
    * ``scenes`` - ``06_scenes.jsonl``, the scene index (number, episode, mission, place),
    * ``series`` - ``{character key: series}`` from ``07_names_characters.jsonl``, the game's own
      character table, so every participant of a scene can be listed with the series it comes from,
    * ``mission`` - ``{row id: row}`` of ``05_mission_text.jsonl``, the mission title and notes a
      scene introduces (they are translated in the scene that introduces them, see below).
    """
    rows = [json.loads(line) for line in
            (package / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    scenes = [json.loads(line) for line in
              (package / "06_scenes.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    series: Dict[object, str] = {}
    names = package / "07_names_characters.jsonl"
    if names.exists():
        for line in names.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("category") == "character_series" and row.get("jp") not in (None, "", "NoData"):
                series[row.get("key")] = row["jp"]
    mission: Dict[str, dict] = {}
    mission_file = package / "05_mission_text.jsonl"
    if mission_file.exists():
        for line in mission_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                mission[row.get("id")] = row
    return {"rows": rows, "scenes": scenes, "series": series, "mission": mission}


def label(row: dict) -> str:
    """``Dialog - セイシロウ・クサナギ`` / ``[kopia] Narracja`` for one element."""
    kind = KIND_LABEL.get(row.get("kind") or "", row.get("kind") or "?")
    if row.get("kind") == "dialogue":
        speaker = (row.get("speaker") or {})
        who = speaker.get("jp") or (f"ID {speaker['id']}" if speaker.get("id") is not None else "?")
        kind = f"{kind} - {who}"
    return f"{'[kopia] ' if row.get('copy_of') else ''}{kind}"


def participants(rows: List[dict], series: Dict[object, str]) -> List[Tuple[str, Optional[str]]]:
    """``[(name, series)]`` of every speaker of the scene, in order of first appearance."""
    seen: Dict[object, str] = {}
    for row in rows:
        if row.get("kind") != "dialogue":
            continue
        speaker = row.get("speaker") or {}
        key = speaker.get("id")
        if key is None or key in seen:
            continue
        seen[key] = speaker.get("jp") or f"ID {key}"
    found: List[Tuple[str, Optional[str]]] = []
    seen_names = set()
    for key, name in seen.items():
        if name in seen_names:          # two characters can share a generic name; the translator
            continue                    # needs the name once
        seen_names.add(name)
        found.append((name, series.get(key)))
    return found


def mission_elements(scene: dict, mission: Dict[str, dict]) -> List[Tuple[str, str, dict]]:
    """``[(token, label, row)]`` of the mission title and notes of one scene.

    The tokens are unique inside the scene (the importer keys on the scene number and the token):
    the title that another scene of the same mission repeats is marked as shared, so it is
    translated once, in the scene that introduces it.
    """
    found: List[Tuple[str, str, dict]] = []
    title = mission.get(scene.get("mission_row"))
    if title is not None:
        if scene.get("mission_inherited"):
            found.append(("T1", "Tytuł misji (wspólny z inną sceną — tłumaczy się raz, tam gdzie jest "
                                "wprowadzony)", title))
        else:
            found.append(("T1", "Tytuł misji", title))
    notes = []
    for row_id in scene.get("mission_notes") or []:
        row = mission.get(row_id)
        if row is not None:
            notes.append(row)
    if notes:
        merged = len(notes) > 1 and all(row.get("jp") == notes[0].get("jp") for row in notes)
        tokens = ["N1"] if merged else [f"N{index}" for index in range(1, len(notes) + 1)]
        label = "Uwaga do misji (pole powtarzane w grze — jeden tekst)" if merged \
            else "Uwaga do misji"
        for token, row in zip(tokens, notes):
            found.append((token, label, row))
    return found


def element_line(row: dict) -> List[str]:
    """The Japanese text of one element plus the ``EN:`` line to fill (or the note for a copy)."""
    text = row["jp"].replace("\r", "⏎").replace("\x0f", "<0x0F>").replace("\n", "\n   ")
    lines = [f"{row['order']}. [{label(row)}] {text}"]
    if row.get("copy_of"):
        lines.append("   (tłumaczenie dziedziczone automatycznie — nie wpisuj tu nic)")
        return lines
    english = (row.get("en") or "").replace("\r", "⏎").replace("\x0f", "<0x0F>")
    lines.append(f"   EN: {english.replace(chr(10), chr(10) + '   ')}".rstrip())
    return lines


def render_scene(scene: dict, rows: List[dict], package: dict) -> str:
    mission = (scene.get("mission") or "(bez tytułu)").replace("\n", " ")
    lines = [f"## Scena {scene['seq']}/{scene.get('total', '?')} — {mission}"]
    if scene.get("episode") is not None:
        label_text = scene.get("episode_label") or f"odcinek {scene['episode']}"
        lines.append(f"- odcinek: {label_text} (episode {scene['episode']})")
    else:
        lines.append("- odcinek: misje treningowe (Simulator)")
    for section in scene.get("sections") or []:
        lines.append(f"- miejsce: {section['jp']} (element {section['order']})")
    lines.append("- limit: dialog — 46 jedn. na linię (gra sama używa do 52), narracja — do 50 jedn.; "
                 "liczbę linii zostaw jak w oryginale (okno gry pokazuje 3 naraz)")
    people = participants(rows, package["series"])
    if people:
        lines.append("- uczestnicy:")
        for name, origin in people:
            lines.append(f"  - {name} — {origin}" if origin else f"  - {name}")
    seq_by_id = package.get("seq_by_id") or {}
    if scene.get("duplicate_of"):
        source = seq_by_id.get(scene["duplicate_of"], scene["duplicate_of"])
        lines.append(f"- cała scena powtarza scenę nr {source} — nic do tłumaczenia "
                     "(angielski dziedziczy się automatycznie)")
    elif scene.get("variant_of"):
        source = seq_by_id.get(scene["variant_of"], scene["variant_of"])
        lines.append(f"- wariant sceny nr {source} — wiersze `[kopia]` dziedziczą tłumaczenie "
                     "automatycznie")
    lines.append("")

    elements = mission_elements(scene, package["mission"])
    for token, name, row in elements:
        text = row["jp"].replace("\r", "⏎").replace("\x0f", "<0x0F>").replace("\n", "\n   ")
        lines.append(f"{token}. [{name}] {text}")
        english = (row.get("en") or "").replace("\r", "⏎").replace("\x0f", "<0x0F>")
        lines.append(f"   EN: {english.replace(chr(10), chr(10) + '   ')}".rstrip())
    if lines[-1] != "":
        lines.append("")

    for row in sorted(rows, key=lambda item: item["order"]):
        lines.extend(element_line(row))
    lines.append("")
    lines.append("_koniec sceny_")
    lines.append("")
    return "\n".join(lines)


def render_index(scenes: List[dict]) -> str:
    lines = ["# Spis scen", "",
             "Widok do czytania i do pracy: pod każdym elementem jest linia `EN:` — tam wpisuje się",
             "tłumaczenie. Gotowe pliki wracają do pakietu jednym poleceniem "
             "`tools/translation_import.py`.", "",
             "Kolejność jest kolejnością gry: odcinek, misja, wariant (DLC). "
             "Numer sceny w nagłówku (`## Scena 12/293`) to numer wiersza w `06_scenes.jsonl`.", "",
             "| # | odcinek | misja | miejsce | uwaga |",
             "|---|---------|-------|--------|-------|"]
    seq_by_id = {scene["id"]: scene["seq"] for scene in scenes}
    for scene in scenes:
        place = "; ".join(section["jp"].replace("\n", " ") for section in scene.get("sections") or [])
        mission = (scene.get("mission") or "—").replace("\n", " ")
        note = ""
        if scene.get("duplicate_of"):
            note = f"kopia sceny nr {seq_by_id.get(scene['duplicate_of'], '?')} — bez pracy"
        elif scene.get("variant_of"):
            note = f"wariant sceny nr {seq_by_id.get(scene['variant_of'], '?')}"
        episode = scene.get("episode_label") or (f"episode {scene['episode']}"
                                                 if scene.get("episode") is not None else "Simulator")
        lines.append(f"| {scene['seq']} | {episode.replace(chr(10), ' ')} | {mission} | "
                     f"{place} | {note} |")
    return "\n".join(lines) + "\n"


def write_views(package: Path, out: Path, force: bool = False) -> Dict[str, object]:
    """Write ``spis-scen.md`` plus one script file per episode into ``out``.

    A view file that already carries English a translator typed (``EN:`` lines that the package does
    not know yet) is **left alone**, so regenerating the list can never throw the work away; use
    ``force`` to overwrite it anyway.
    """
    data = load_package(package)
    rows, scenes = data["rows"], data["scenes"]
    lookup = TI.scene_lookup(rows)
    data["seq_by_id"] = {scene["id"]: scene["seq"] for scene in scenes}
    out.mkdir(parents=True, exist_ok=True)
    by_scene: Dict[str, List[dict]] = collections.defaultdict(list)
    for row in rows:
        by_scene[row["scene"]].append(row)
    for scene in scenes:
        scene["total"] = len(scenes)
    (out / "spis-scen.md").write_text(render_index(scenes), encoding="utf-8")

    groups: Dict[str, List[dict]] = collections.defaultdict(list)
    for scene in scenes:
        if scene.get("episode") is not None:
            key = f"epizod-{scene['episode']:02d}.md"
        elif scene.get("series") == "simulator":
            key = "simulator.md"
        else:
            key = "inne.md"
        groups[key].append(scene)
    counts: Dict[str, object] = {"files": {"spis-scen.md": 1}, "skipped": []}
    for name, group in sorted(groups.items()):
        body = [f"# {name.replace('.md', '').replace('-', ' ')}", ""]
        for scene in sorted(group, key=lambda item: item["seq"]):
            body.append(render_scene(scene, by_scene.get(scene["id"], []), data))
        text = "\n".join(body)
        target = out / name
        if not force and target.exists():
            edited = 0
            for (scene_key, token), value in TI.parse_view(target.read_text(encoding="utf-8")).items():
                row = TI.resolve(lookup, scene_key, token)
                if row is None or (row.get("en") or "") != value:
                    edited += 1
            if edited:
                counts["skipped"].append(f"{name} ({edited} linii EN do zaimportowania)")
                continue
        target.write_text(text, encoding="utf-8")
        counts["files"][name] = 1
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
    parser.add_argument("--out", type=Path, default=Path("local/translation/sceny"))
    parser.add_argument("--zip", action="store_true", help="also pack the view into sceny.zip")
    parser.add_argument("--force", action="store_true",
                        help="overwrite view files that still hold untransferred English")
    args = parser.parse_args(argv)

    counts = write_views(args.package, args.out, force=args.force)
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    if args.zip:
        archive = args.out.parent / "sceny.zip"
        print(f"zip: {make_zip(args.out, archive)} files -> {archive}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
