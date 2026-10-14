#!/usr/bin/env python3
"""Refresh the story rows of the package from the event containers (adds what the reader missed).

Why this exists: the reader used to skip every non-dialogue record inside a wrapper, so the scene
prose a player reads before a battle was missing from the package entirely (measured: 41 of 44
narration records in ``eventP00.cpk`` alone).  The reader is fixed now; this tool brings the package
up to it **without rebuilding anything**: every existing row keeps its id, its English and its
speaker (matched by container, member, byte offset and kind), the rows the reader now finds are
inserted where the game has them, and the element order inside each scene is renumbered by offset.

Only the members that are in front of it are touched - a container that is not in ``--dir`` keeps its
rows exactly as they are, so a half-filled directory refreshes half the story and says so.

Usage:
    python3 tools/event_refresh.py --package local/translation --dir local/events [--check]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import event_dialogue as ED  # noqa: E402
import speaker_map as SM  # noqa: E402

#: kinds that come from the reader itself; the ``embedded`` rows (parameter tables) are kept as
#: they are, because the reader has not changed there
TYPED = ("dialogue",)


def row_of(container: str, member: str, item: dict) -> dict:
    """One package row from one reader item (the shape ``translator_export`` writes)."""
    is_dialogue = item["kind"] == "dialogue"
    return {
        "id": f"dlg:{container}/{member}:{item['text_offset']}",
        "category": "dialogue",
        "part": "dialogue" if is_dialogue else "other",
        "jp": item["text"],
        "en": "",
        "bytes": item["bytes"],
        "mode": "grow",
        "max_bytes": None,
        "speaker": ({"id": item.get("key"), "jp": None, "source": None} if is_dialogue
                    else {"id": None, "jp": None, "source": None}),
        "kind": item["kind"],
        "source": {"container": container, "member": member, "offset": item["text_offset"]},
    }


def refresh_member(container: str, member: str, blob: bytes, existing: List[dict]) -> Tuple[List[dict], dict]:
    """The rows of one member as the fixed reader sees them; existing rows keep their English.

    Returns (rows in reading order, report).  The report counts what was added and what was kept.
    """
    found = ED.extract_member(blob, container, member)
    items = list(found["dialogue"]) + list(found["other"])
    items.sort(key=lambda item: item["text_offset"])
    old = {(int(row["source"]["offset"]), row.get("kind")): row for row in existing}
    fresh_keys = set()
    rows: List[dict] = []
    report = {"added": 0, "kept": 0, "kinds": collections.Counter(),
              "added_by_kind": collections.Counter()}
    for item in items:
        key = (int(item["text_offset"]), item["kind"])
        previous = old.get(key)
        if previous is not None:
            fresh_keys.add(key)
            row = previous                                   # id, en, speaker stay untouched
            row["jp"] = item["text"]
            row["bytes"] = item["bytes"]
            report["kept"] += 1
        else:
            row = row_of(container, member, item)
            report["added"] += 1
            report["added_by_kind"][item["kind"]] += 1
        report["kinds"][item["kind"]] = report["kinds"].get(item["kind"], 0) + 1
        rows.append(row)
    for row in existing:                                     # table texts: keep, do not re-read them
        if row.get("kind") == "embedded":
            rows.append(row)
    rows.sort(key=lambda row: int(row["source"]["offset"]))
    for order, row in enumerate(rows, start=1):
        row["order"] = order
        row["scene"] = f"{container}/{member}"
    return rows, report


def refresh_scene_metadata(scene: dict, rows: List[dict]) -> None:
    """Bring the fields of a ``06_scenes`` row in line with the rows that scene now has."""
    counts = collections.Counter(row.get("kind") for row in rows)
    scene["counts"] = dict(sorted(counts.items()))
    scene["rows"] = len(rows)
    scene["jp_bytes"] = sum(int(row.get("bytes") or 0) for row in rows)
    scene["first_row"] = rows[0]["id"] if rows else None
    scene["last_row"] = rows[-1]["id"] if rows else None
    scene["sections"] = [{"order": row["order"], "kind": row.get("kind"), "row": row["id"],
                          "jp": row["jp"]}
                         for row in rows if row.get("kind") == "location"]


def refresh(package: Path, directory: Path, check: bool = False) -> dict:
    """Refresh every scene whose container is in ``directory``; write the package back."""
    story = Path(package) / "00_dialogue.jsonl"
    scenes_path = Path(package) / "06_scenes.jsonl"
    rows = [json.loads(line) for line in story.read_text(encoding="utf-8").splitlines() if line.strip()]
    scenes = [json.loads(line) for line in scenes_path.read_text(encoding="utf-8").splitlines()
              if line.strip()]
    by_scene: Dict[str, List[dict]] = collections.defaultdict(list)
    for row in rows:
        by_scene[str(row.get("scene"))].append(row)

    report: dict = {"containers": {}, "added": 0, "scenes": 0, "skipped": [],
                    "kinds": collections.Counter(), "added_by_kind": collections.Counter()}
    refreshed: Dict[str, List[dict]] = {}
    seen_containers = set()
    for path in sorted(Path(directory).iterdir()):
        if not path.name.lower().endswith((".cpk", ".edat")):
            continue
        if not (path.name.lower().startswith("eventp") or path.name.lower().startswith("evept")):
            continue
        seen_containers.add(path.name)
        try:
            members = SM.read_members(path)
        except Exception as error:                            # unreadable container: say so, go on
            report["skipped"].append(f"{path.name}: {type(error).__name__}: {error}")
            continue
        container_report = {"members": 0, "added": 0, "missing_scenes": []}
        for member, blob in members:
            key = f"{path.name}/{member}"
            if key not in by_scene:
                # the same container also holds mission notes (_ext.dat) and entry tables, which are
                # not scenes; only a member that looks like a scene is worth reporting
                lowered = member.lower()
                if lowered.endswith(".bin") and not any(tag in lowered
                                                        for tag in ("_ext", "_edit", "_entry")):
                    container_report["missing_scenes"].append(key)
                continue
            new_rows, member_report = refresh_member(path.name, member, blob, by_scene[key])
            refreshed[key] = new_rows
            container_report["members"] += 1
            container_report["added"] += member_report["added"]
            report["added"] += member_report["added"]
            for kind, count in member_report["kinds"].items():
                report["kinds"][kind] += count
            for kind, count in member_report["added_by_kind"].items():
                report["added_by_kind"][kind] += count
        report["containers"][path.name] = container_report

    if not refreshed:
        report["note"] = "nie znalazłem żadnego kontenera scen, pakiet bez zmian"
        return report

    # scenes keep their order; a scene whose container is absent keeps its rows untouched
    new_scene_rows: List[dict] = []
    for scene in scenes:
        key = str(scene.get("id"))
        if key in refreshed:
            rows_of_scene = refreshed[key]
            refresh_scene_metadata(scene, rows_of_scene)
            new_scene_rows.extend(rows_of_scene)
            report["scenes"] += 1
        else:
            new_scene_rows.extend(by_scene.get(key, []))
    known = {str(scene.get("id")) for scene in scenes}
    for key, rows_of_scene in refreshed.items():              # a scene the package did not know
        if key not in known:
            report["skipped"].append(f"{key}: wiersze bez sceny w 06_scenes.jsonl")
            new_scene_rows.extend(rows_of_scene)

    report["rows_before"] = len(rows)
    report["rows_after"] = len(new_scene_rows)
    if not check:
        story.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in new_scene_rows),
                         encoding="utf-8")
        scenes_path.write_text("".join(json.dumps(scene, ensure_ascii=False) + "\n" for scene in scenes),
                               encoding="utf-8")
    report["written"] = not check
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--dir", type=Path, required=True, help="folder with the event containers")
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    report = refresh(args.package, args.dir, args.check)
    print(json.dumps(report, ensure_ascii=False, indent=1, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
