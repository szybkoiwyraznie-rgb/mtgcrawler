#!/usr/bin/env python3
"""Build Polish story-reading Markdown from source-bound PL package rows.

The English package is used only for immutable source bindings and scene shape.
Only ``pl`` values are rendered. All story scenes and source variants are shown
in source order; no alias is inferred and no condition/trigger is invented.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace

from build_reading_script import escape, render_entry
from mech_catalog_sources import need
from pl_release_package import binding
from reading_script_source import HEADINGS, PROSE, paragraphs, jsonl

SOURCE_FILES = ("00_dialogue.jsonl", "05_mission_text.jsonl", "06_scenes.jsonl",
                "07_names_characters.jsonl")
EMPTY_STRUCTURAL_IDS = frozenset({
    "dlg:eventP01.EDAT/DL105_40.bin:696",
    "dlg:eventP08.EDAT/DL833_60.bin:432",
})
EMPTY_STRUCTURAL_ID = "dlg:eventP01.EDAT/DL105_40.bin:696"
JP_RE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bound_map(package: Path, filename: str) -> dict:
    result = {}
    for row in jsonl(package / filename):
        key = (row["id"], binding(row))
        result.setdefault(key, []).append(row)
    return result


def unique_bound(rows: list[dict], field: str, key: tuple) -> dict:
    need(bool(rows), f"Missing source-bound {field} row: {key[0]}")
    values = {row.get(field) or "" for row in rows}
    need(len(values) == 1, f"Conflicting aliases for {field}: {key[0]}")
    return rows[0]


class PolishStorySource:
    """Read story rows by immutable EN/PL binding; never falls back to English."""
    def __init__(self, english_package: Path, polish_package: Path, episode: int):
        self.english_package = Path(english_package)
        self.package = Path(polish_package)
        self.episode = episode
        self.scenes = [s for s in jsonl(self.package / "06_scenes.jsonl")
                       if s.get("series") == "story" and s.get("episode") == episode]
        need(bool(self.scenes), f"No story scenes for episode {episode}")
        need([s["seq"] for s in self.scenes] == sorted({s["seq"] for s in self.scenes}),
             "Scene index is not strictly ordered")
        self.scene_by_id = {s["id"]: s for s in self.scenes}
        need(len(self.scene_by_id) == len(self.scenes), "Duplicate scene ID")

        self.rows = {s["id"]: [] for s in self.scenes}
        en_rows = bound_map(self.english_package, "00_dialogue.jsonl")
        pl_rows = bound_map(self.package, "00_dialogue.jsonl")
        self.by_id = {}
        self.bindings = {}
        for key, group in en_rows.items():
            row = group[0]
            scene = row.get("scene")
            if scene not in self.rows:
                continue
            target = unique_bound(pl_rows.get(key, []), "pl", key)
            need(target.get("id") == row.get("id") and target.get("scene") == scene,
                 f"Source row changed in PL package: {row['id']}")
            need(row["id"] not in self.by_id, f"Duplicate dialogue row ID: {row['id']}")
            self.rows[scene].append(target)
            self.by_id[row["id"]] = target
            self.bindings[row["id"]] = key[1]
        for scene, rows in self.rows.items():
            rows.sort(key=lambda row: row["order"])
            need(bool(rows), f"No dialogue rows for scene {scene}")
            need([r["order"] for r in rows] == sorted({r["order"] for r in rows}),
                 f"Scene rows not strictly ordered: {scene}")
            need(len(rows) == self.scene_by_id[scene]["rows"],
                 f"Scene row count differs: {scene}")

        self.names = {}
        for key, rows in bound_map(self.package, "07_names_characters.jsonl").items():
            row = unique_bound(rows, "pl", key)
            if row.get("key") is not None and (row.get("pl") or "").strip():
                self.names.setdefault(row["key"], {}).setdefault(row.get("part"), set()).add(row["pl"].strip())
        self.display_names = {}
        groups = {}
        for rows in self.rows.values():
            for row in rows:
                if row.get("kind") == "dialogue":
                    key = (row.get("speaker") or {}).get("id")
                    if key is not None:
                        groups.setdefault(self.name(key), set()).add(key)
        for short, keys in groups.items():
            full = {}
            for key in keys:
                vals = (self.names.get(key, {}).get("name_full") or
                        self.names.get(key, {}).get("name") or {short})
                need(len(vals) == 1, f"Conflicting full Polish names for speaker {key}")
                full[key] = next(iter(vals))
            if len(set(full.values())) > 1:
                self.display_names.update(full)

        self.missions = {}
        for key, rows in bound_map(self.package, "05_mission_text.jsonl").items():
            row = unique_bound(rows, "pl", key)
            self.missions[row["id"]] = row

    def name(self, key: int) -> str:
        fields = self.names.get(key, {})
        for part in ("nickname", "name_short", "name", "name_full"):
            vals = fields.get(part, set())
            if len(vals) > 1:
                raise ValueError(f"Conflicting Polish speaker names: {key}/{part}")
            if vals:
                value = next(iter(vals))
                if value == "NoData":
                    raise ValueError(f"Placeholder Polish speaker name: {key}/{part}")
                return value
        raise ValueError(f"Missing Polish speaker name: {key}")

    def make_entry(self, row: dict):
        value = row.get("pl") or ""
        kind = row.get("kind")
        speaker = None
        raw_speaker = row.get("speaker") or {}
        if kind == "dialogue":
            jp_lines = (row.get("jp") or "").splitlines()
            first = value.splitlines()[0] if value.splitlines() else ""
            has_pl_prefix = first.startswith(("＃", "#"))
            if has_pl_prefix:
                need(bool(jp_lines and jp_lines[0].startswith(("＃", "#"))),
                     f"Translated speaker prefix lacks a source prefix: {row['id']}")
                speaker = first[1:].strip()
                need(bool(speaker), f"Empty Polish speaker prefix: {row['id']}")
                need(not JP_RE.search(speaker), f"Untranslated speaker prefix: {row['id']}")
                value = value.split("\n", 1)[1] if "\n" in value else ""
            elif jp_lines and jp_lines[0] in ("＃？？？", "＃???"):
                speaker = "???"
            else:
                key = raw_speaker.get("id")
                speaker = self.display_names.get(key) or self.name(key)
        elif kind in HEADINGS:
            value = value.removeprefix("＃")

        # These are display-only substitutions. The package and game keep the
        # customizable protagonist-name tokens unchanged.
        value = value.replace("＜主人公名＞", self.name(4501))
        if "＜主人公姓＞" in value:
            full = self.names.get(4501, {}).get("name_full", set())
            need(len(full) == 1 and len(next(iter(full)).split()) == 2,
                 "Default protagonist surname needs review")
            value = value.replace("＜主人公姓＞", next(iter(full)).split()[1])
        need(not re.search(r"[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f＜＞＃]", value),
             f"Unresolved Japanese/token in PL reading row: {row['id']}")
        text = paragraphs(value)
        need(bool(text), f"Empty readable PL text: {row['id']}")
        return SimpleNamespace(row=row, speaker=speaker, text=text, kind=kind,
                               id=row["id"], order=row["order"])

    def mission_title(self, scene: dict) -> str:
        seen = set()
        while scene.get("variant_of"):
            need(scene["id"] not in seen, "Cycle in scene variant metadata")
            seen.add(scene["id"])
            scene = self.scene_by_id.get(scene["variant_of"])
            need(scene is not None, "Variant base is absent from this episode")
        row_id = scene.get("mission_row")
        if not row_id:
            return f"Scena fabularna {scene['seq']}"
        row = self.missions.get(row_id)
        need(row is not None, f"Missing source mission row: {row_id}")
        value = (row.get("pl") or "").strip()
        need(bool(value), f"Missing PL mission title: {row_id}")
        lines = value.splitlines()
        if lines and re.fullmatch(r"(?:Ep\.?\s*)?\d+(?:話)?", lines[0].strip(), re.I):
            lines = lines[1:]
        title = " ".join(line.strip() for line in lines if line.strip())
        need(bool(title), f"Empty rendered mission title: {row_id}")
        need(not JP_RE.search(title), f"Untranslated mission title: {row_id}")
        return title


def build_episode(english_package: Path, polish_package: Path, episode: int,
                  output: Path, audit_path: Path) -> dict:
    source = PolishStorySource(english_package, polish_package, episode)
    entries = {}
    technical = {}
    empty_structural = []
    expected_prose = set()
    for scene_id, rows in source.rows.items():
        for row in rows:
            kind = row.get("kind")
            if kind not in PROSE | HEADINGS:
                technical[kind] = technical.get(kind, 0) + 1
                continue
            if not (row.get("pl") or "").strip():
                if (row["id"] in EMPTY_STRUCTURAL_IDS and not (row.get("jp") or "").strip()
                        and not (row.get("en") or "").strip()):
                    empty_structural.append(row["id"])
                    continue
                raise ValueError(f"Missing Polish reading text: {row['id']}")
            entry = source.make_entry(row)
            entries[row["id"]] = entry
            if kind in PROSE:
                expected_prose.add(row["id"])

    pieces: list[str] = []
    spans: list[dict] = []
    position = 0

    def put(value: str, **meta):
        nonlocal position
        value += "\n\n"
        start = position
        pieces.append(value)
        position += len(value)
        if meta:
            spans.append({**meta, "start": start, "end": position})

    put(f"# Super Robot Wars OE — Epizod {episode:02d}")
    put("*Polski scenariusz do czytania · tekst z zaakceptowanego pakietu PL*")
    put("> **Informacja:** Dialogi i narrację pokazano w kolejności wpisów źródłowych. Wymiany mogą zależeć "
        "od przebiegu misji; kolejność w dokumencie nie oznacza, że wszystkie kwestie występują w jednej "
        "rozgrywce. Nie dopisano warunków HP/tur ani dalszych zdarzeń. Alternatywne wersje źródłowe "
        "oznaczono osobno i pokazano w całości.")
    put("---")

    shown_prose = set()
    for scene in source.scenes:
        sid = scene["id"]
        put("## " + escape(source.mission_title(scene)), scene=sid, role="scene-title")
        if scene.get("variant_of"):
            put(f"*Wersja alternatywna ({escape(scene.get('variant') or 'źródłowa')}); "
                "to nie dalszy ciąg tej misji. Pełny tekst zachowano.*",
                scene=sid, role="variant-note")
        elif scene.get("variant"):
            put(f"*Wariant źródłowy {escape(scene['variant'])}; scena zachowana osobno.*",
                scene=sid, role="variant-note")
        elif scene.get("copy_of"):
            put("*Kopia źródłowa; zachowano osobno wszystkie wpisy.*", scene=sid, role="copy-note")
        for row in source.rows[sid]:
            kind = row.get("kind")
            if kind not in PROSE | HEADINGS:
                continue
            entry = entries.get(row["id"])
            if entry is None:
                continue  # the documented whitespace-only structural row
            text = render_entry(entry, "story", 3)
            if kind in PROSE:
                text = re.sub(r"(?m)(^|\n\n)(\([^\n]*\))(?=\n\n|$)",
                              lambda m: m.group(1) + "*" + m.group(2) + "*", text)
                shown_prose.add(row["id"])
            put(text, row=row["id"], binding=source.bindings[row["id"]], scene=sid, kind=kind)

    need(shown_prose == expected_prose,
         f"PL prose coverage differs: missing={len(expected_prose-shown_prose)}, "
         f"extra={len(shown_prose-expected_prose)}")
    put("---")
    put("## Uwagi redakcyjne")
    put("- Tekst pochodzi wyłącznie z polskich pól pakietu PL; angielskie wiersze służą tylko "
        "do sprawdzania identyfikatorów i struktury. Nie ma uzupełniania braków angielskim.")
    put("- Zachowano wszystkie polskie wpisy narracji/dialogu z tego epizodu, także tekst scen "
        "alternatywnych. Nie usuwano powtórzeń między scenami.")
    put("- Pominięto techniczne pola celu/pomocy i pusty wypełniacz strukturalny; nie są narracją do czytania.")
    put(f"- Pokrycie: **{len(shown_prose)}** wpisów dialogu i narracji w **{len(source.scenes)}** scenach. "
        "Dokument nie ustala dokładnych wyzwalaczy ani kolejności kwestii warunkowych w grze.")
    put("- Znaczniki imienia/nazwiska podstawiono wyłącznie w tym dokumencie, używając domyślnej "
        "polskiej nazwy z tabel postaci; dane gry pozostają dynamiczne.")

    text = "".join(pieces)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")
    source_hashes = {name: sha((english_package / name).read_bytes()) for name in SOURCE_FILES}
    pl_hashes = {name: sha((polish_package / name).read_bytes()) for name in SOURCE_FILES}
    audit = {
        "schema": 1, "episode": episode, "source_sha256": source_hashes,
        "materialized_pl_sha256": pl_hashes, "output_sha256": sha(text.encode("utf-8")),
        "scene_count": len(source.scenes), "prose_total": len(shown_prose),
        "prose_ids": sorted(shown_prose), "rendered_blocks": spans,
        "technical_rows_omitted_by_kind": dict(sorted(technical.items())),
        "empty_structural_rows_skipped": empty_structural,
        "output_bytes": len(text.encode("utf-8")), "runtime_tested": False,
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english", type=Path, required=True)
    parser.add_argument("--polish", type=Path, required=True,
                        help="materialized PL package from the accepted PL snapshot")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--episodes", type=int, nargs="+", default=list(range(35)),
                        help="internal story episode IDs; current PL source covers 00-34")
    args = parser.parse_args(argv)
    need(args.out.resolve() not in (args.english.resolve(), args.polish.resolve()),
         "Output must be separate from both source packages")
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": 1, "kind": "PL reading edition", "episodes": [],
                "scope_note": "The source-bound PL package covers all story episodes 00-34; no text beyond that coverage is generated."}
    for episode in args.episodes:
        audit = build_episode(args.english, args.polish, episode,
                              args.out / f"srwoe_episode_{episode:02d}_PL.md",
                              args.out / f"episode_{episode:02d}_audit.json")
        manifest["episodes"].append({"episode": episode, "prose": audit["prose_total"],
                                     "scenes": audit["scene_count"], "bytes": audit["output_bytes"],
                                     "sha256": audit["output_sha256"]})
        print(f"{episode:02d}: {audit['scene_count']} scenes, {audit['prose_total']} PL prose rows, "
              f"{audit['output_bytes']} bytes, {audit['output_sha256']}")
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
