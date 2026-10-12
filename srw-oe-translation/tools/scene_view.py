#!/usr/bin/env python3
"""Render the translation package as a readable script: one file per episode, scene by scene.

The JSONL files are what the game reads back; this view is for the person (or the assistant)
translating, so that the context of a scene is visible instead of a flat line-by-line list:

    ## Scena 12/293 - 試作レイバー暴走事件
    - odcinek: 1話 メインミッション
    - plik gry: eventP00.cpk / DL101_11.bin
    - miejsce: ジオン軍基地／オデッサ        (z elementu 12)
    1. [Narracja] ...
    2. [Dialog - セイシロウ・クサナギ] ...
    _koniec sceny_

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
from typing import Dict, List, Tuple

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


def load_package(package: Path) -> Tuple[List[dict], List[dict]]:
    """Rows of ``00_dialogue.jsonl`` and the scene index of ``06_scenes.jsonl``."""
    rows = [json.loads(line) for line in
            (package / "00_dialogue.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    scenes = [json.loads(line) for line in
              (package / "06_scenes.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows, scenes


def label(row: dict) -> str:
    """``Dialog - セイシロウ・クサナギ`` / ``[kopia] Narracja`` for one element."""
    kind = KIND_LABEL.get(row.get("kind") or "", row.get("kind") or "?")
    if row.get("kind") == "dialogue":
        speaker = (row.get("speaker") or {})
        who = speaker.get("jp") or (f"ID {speaker['id']}" if speaker.get("id") is not None else "?")
        kind = f"{kind} - {who}"
    return f"{'[kopia] ' if row.get('copy_of') else ''}{kind}"


def render_scene(scene: dict, rows: List[dict]) -> str:
    lines = [f"## Scena {scene['seq']}/{scene.get('total', '?')} — {scene.get('mission') or '(bez tytułu)'}"]
    if scene.get("episode") is not None:
        label_text = scene.get("episode_label") or f"odcinek {scene['episode']}"
        lines.append(f"- odcinek: {label_text} (episode {scene['episode']})")
    else:
        lines.append("- odcinek: misje treningowe (Simulator)")
    lines.append(f"- plik gry: {scene['container']} / {scene['member']}")
    if scene.get("mission_row"):
        lines.append(f"- tytuł misji do przetłumaczenia: `{scene['mission_row']}`")
    if scene.get("mission_notes"):
        lines.append(f"- uwagi do misji: {', '.join('`' + row + '`' for row in scene['mission_notes'])}")
    if scene.get("duplicate_of"):
        lines.append(f"- **kopia sceny** `{scene['duplicate_of']}` — tłumaczenie dziedziczone "
                     "(patrz `tools/translation_copy.py`)")
    elif scene.get("variant_of"):
        lines.append(f"- **wariant sceny** `{scene['variant_of']}` — ta sama scena w innym DLC, "
                     "część linii jest identyczna (wiersze `[kopia]`)")
    counts = ", ".join(f"{KIND_LABEL.get(kind, kind)}: {count}" for kind, count in
                       sorted((scene.get("counts") or {}).items()))
    lines.append(f"- elementów: {scene['rows']} ({counts})")
    for section in scene.get("sections") or []:
        lines.append(f"- miejsce (element {section['order']}): {section['jp']}")
    lines.append("")
    for row in rows:
        # the JSONL keeps the raw bytes; the view makes the invisible control characters visible
        text = row["jp"].replace("\r", "⏎").replace("\x0f", "<0x0F>").replace("\n", "\n   ")
        lines.append(f"{row['order']}. [{label(row)}] {text}")
    lines.append("")
    lines.append("_koniec sceny_")
    lines.append("")
    return "\n".join(lines)


def render_index(scenes: List[dict]) -> str:
    lines = ["# Spis scen", "",
             "Kolejność jest kolejnością gry: odcinek, misja, wariant (DLC). "
             "Plik `00_dialogue.jsonl` ma wiersze w tej samej kolejności.", "",
             "| # | odcinek | misja | scena (plik gry) | elementów | miejsce | uwaga |",
             "|---|---------|-------|------------------|-----------|--------|-------|"]
    for scene in scenes:
        place = "; ".join(section["jp"] for section in scene.get("sections") or []) or ""
        note = ""
        if scene.get("duplicate_of"):
            note = f"kopia `{scene['duplicate_of']}`"
        elif scene.get("variant_of"):
            note = f"wariant `{scene['variant_of']}`"
        episode = scene.get("episode_label") or (f"episode {scene['episode']}"
                                                 if scene.get("episode") is not None else "Simulator")
        lines.append(f"| {scene['seq']} | {episode} | {scene.get('mission') or '—'} | "
                     f"{scene['container']}/{scene['member']} | {scene['rows']} | {place} | {note} |")
    return "\n".join(lines) + "\n"


def write_views(package: Path, out: Path) -> Dict[str, int]:
    """Write ``spis-scen.md`` plus one script file per episode into ``out``."""
    rows, scenes = load_package(package)
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
    counts = {"spis-scen.md": 1}
    for name, group in sorted(groups.items()):
        head = f"# {name.replace('.md', '').replace('-', ' ')}"
        body = [head, ""]
        for scene in sorted(group, key=lambda item: item["seq"]):
            body.append(render_scene(scene, sorted(by_scene.get(scene["id"], []),
                                                   key=lambda row: row["order"])))
        (out / name).write_text("\n".join(body), encoding="utf-8")
        counts[name] = 1
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
    args = parser.parse_args(argv)

    counts = write_views(args.package, args.out)
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    if args.zip:
        archive = args.out.parent / "sceny.zip"
        print(f"zip: {make_zip(args.out, archive)} files -> {archive}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
