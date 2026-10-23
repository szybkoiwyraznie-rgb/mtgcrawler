#!/usr/bin/env python3
"""Read-only sources/review for an English *reading edition*, not a game patch.

Only game line wraps/CRLF and outer whitespace are normalized. Paragraph breaks,
punctuation, speaker identity and meaningful metadata participate in comparisons.
No source text is written into Git; keep review output under ignored local/.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re

SOURCE_FILES = ("00_dialogue.jsonl", "05_mission_text.jsonl", "06_scenes.jsonl",
                "07_names_characters.jsonl")
PROSE = frozenset(("dialogue", "narration"))
HEADINGS = frozenset(("location", "scene_title", "label"))
TECHNICAL = frozenset(("help", "condition_victory", "condition_defeat"))
EMPTY_STRUCTURAL_IDS = frozenset((
    "dlg:eventP01.EDAT/DL105_40.bin:696",
    "dlg:eventP08.EDAT/DL833_60.bin:432",
))
PREFIXES = {"＃？？？": "???", "＃???": "???"}


def paragraphs(value: str) -> tuple[str, ...]:
    """Join soft wraps, not paragraphs. Do not collapse spaces inside a line."""
    value = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not value:
        return ()
    return tuple(" ".join(line.strip() for line in paragraph.splitlines())
                 for paragraph in re.split(r"\n[ \t]*\n(?:[ \t]*\n)*", value))


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def explicit_prefix(text: str) -> str | None:
    first = text.splitlines()[0] if text else ""
    if first.startswith(("＃", "#")):
        if first not in PREFIXES:
            raise ValueError(f"Unreviewed speaker prefix: {first!r}")
        return PREFIXES[first]
    return None


@dataclass
class Entry:
    row: dict
    speaker: str | None
    text: tuple[str, ...]
    identity: tuple

    @property
    def id(self) -> str:
        return self.row["id"]

    @property
    def order(self) -> int:
        return self.row["order"]

    @property
    def kind(self) -> str:
        return self.row["kind"]


class ReadingSource:
    def __init__(self, package: Path, episode: int):
        language = getattr(self, "language", "en")
        self.package = Path(package)
        self.hashes = {name: hashlib.sha256((self.package / name).read_bytes()).hexdigest()
                       for name in SOURCE_FILES}
        raw_scenes = [s for s in jsonl(self.package / "06_scenes.jsonl")
                      if s.get("series") == "story" and s.get("episode") == episode]
        if not raw_scenes:
            raise ValueError(f"No story scenes for episode {episode}")
        if [s["seq"] for s in raw_scenes] != sorted({s["seq"] for s in raw_scenes}):
            raise ValueError("Scene index is not strictly ordered")
        fixed_scenes = []
        last_base = None
        for s in raw_scenes:
            sc = dict(s)
            if not sc.get("variant"):
                last_base = sc["id"]
            elif not sc.get("variant_of"):
                sc["variant_of"] = last_base
            fixed_scenes.append(sc)
        self.scenes = fixed_scenes
        self.scene_by_id = {s["id"]: s for s in self.scenes}
        if len(self.scene_by_id) != len(self.scenes):
            raise ValueError("Duplicate scene ID")
        self.names = defaultdict(lambda: defaultdict(set))
        for row in jsonl(self.package / "07_names_characters.jsonl"):
            if row.get("key") is not None and row.get(language):
                self.names[row["key"]][row.get("part")].add(row[language].strip())
        self.missions = {}
        for row in jsonl(self.package / "05_mission_text.jsonl"):
            if row["id"] in self.missions:
                raise ValueError(f"Duplicate mission ID: {row['id']}")
            self.missions[row["id"]] = row
        self.rows = {s["id"]: [] for s in self.scenes}
        self.entries = {s["id"]: [] for s in self.scenes}
        self.by_id = {}
        for row in jsonl(self.package / "00_dialogue.jsonl"):
            scene = row.get("scene")
            if scene not in self.rows:
                continue
            if row["id"] in self.by_id:
                raise ValueError(f"Duplicate row ID: {row['id']}")
            if row.get("kind") not in PROSE | HEADINGS | TECHNICAL:
                raise ValueError(f"Unreviewed entry kind: {row['id']}")
            if row["id"] not in EMPTY_STRUCTURAL_IDS:
                if not isinstance(row.get(language), str) or not row[language].strip():
                    label = "English" if language == "en" else f"Missing {language}"
                    raise ValueError(f"Empty {label}: {row['id']}")
            self.rows[scene].append(row)
            self.by_id[row["id"]] = row
        for scene, rows in self.rows.items():
            if not rows or [r["order"] for r in rows] != sorted({r["order"] for r in rows}):
                raise ValueError(f"Missing or unordered source rows: {scene}")
            if len(rows) != self.scene_by_id[scene]["rows"]:
                raise ValueError(f"Scene row count disagrees with source index: {scene}")
        self.prepare_speakers()
        for scene, rows in self.rows.items():
            self.entries[scene] = [
                self.make_entry(r) for r in rows
                if r["kind"] in PROSE | HEADINGS
                and not (r["id"] in EMPTY_STRUCTURAL_IDS and not (r.get(language) or "").strip())
            ]

    def prepare_speakers(self) -> None:
        """Disambiguate shared short names, using only the package's full names."""
        groups = defaultdict(set)
        for rows in self.rows.values():
            for row in rows:
                if row["kind"] == "dialogue":
                    key = (row.get("speaker") or {}).get("id")
                    groups[self.name(key)].add(key)
        self.display_names = {}
        for short, keys in groups.items():
            full = {}
            for key in keys:
                values = self.names[key]["name_full"] or self.names[key]["name"] or {short}
                if len(values) != 1:
                    raise ValueError(f"Conflicting full names: {key}")
                full[key] = next(iter(values))
            if len(set(full.values())) > 1:
                self.display_names.update(full)

    def name(self, key: int) -> str:
        for part in ("nickname", "name_short", "name", "name_full"):
            values = self.names[key][part]
            if len(values) > 1:
                raise ValueError(f"Conflicting English names: {key}/{part}")
            if values:
                value = next(iter(values))
                if value == "NoData":
                    raise ValueError(f"Placeholder name: {key}/{part}")
                return value
        raise ValueError(f"Missing English speaker: {key}")

    def make_entry(self, row: dict) -> Entry:
        en = row["en"]
        speaker = None
        raw_speaker = row.get("speaker") or {}
        override = None
        if row["kind"] == "dialogue":
            jp_override = explicit_prefix(row.get("jp", ""))
            en_override = explicit_prefix(en)
            if en_override and jp_override and en_override != jp_override:
                raise ValueError(f"Conflicting inline speaker: {row['id']}")
            override = en_override or jp_override
            key = raw_speaker.get("id")
            speaker = override or getattr(self, "display_names", {}).get(key) or self.name(key)
            if en_override:
                en = en.split("\n", 1)[1] if "\n" in en else ""
        elif row["kind"] in HEADINGS:
            en = en.removeprefix("＃")
        # These are display-only defaults. Never edit the source/game's dynamic tokens.
        if "＜主人公名＞" in en:
            en = en.replace("＜主人公名＞", self.name(4501))
        if re.search(r"[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f＜＞＃\x00-\x08\x0b\x0c\x0e-\x1f]", en):
            raise ValueError(f"Unreviewed token/JP/control text: {row['id']}")
        text = paragraphs(en)
        if not text:
            raise ValueError(f"No readable text left: {row['id']}")
        # Physical offsets/containers do not identify a speaker. The original ID,
        # name, explicit override and *raw EN* do: even punctuation-only changes survive.
        identity = (row["kind"], raw_speaker.get("id"), raw_speaker.get("jp"),
                    override, speaker, paragraphs(row["en"]))
        return Entry(row, speaker, text, identity)

    def title(self, scene: str) -> tuple[str, str]:
        seen = set()
        while scene not in seen:
            seen.add(scene)
            metadata = self.scene_by_id[scene]
            key = metadata.get("mission_row")
            if key:
                text = self.missions[key]["en"].strip()
                # Mission title cards carry the episode label on a separate first line.
                lines = text.splitlines()
                if len(lines) > 1 and re.fullmatch(r"(?:Episode\s+)?\d+(?:話)?", lines[0].strip()):
                    lines = lines[1:]
                return " ".join(line.strip() for line in lines), key
            scene = metadata.get("variant_of")
            if scene not in self.scene_by_id:
                break
        raise ValueError("No sourced English mission title")

    def alignment(self, base: str, variant: str) -> list[tuple]:
        return SequenceMatcher(None, [e.identity for e in self.entries[base]],
                               [e.identity for e in self.entries[variant]],
                               autojunk=False).get_opcodes()

    def inventory(self) -> dict:
        scenes = []
        for scene in self.scenes:
            sid = scene["id"]
            item = {"seq": scene["seq"], "id": sid, "title": self.title(sid)[0],
                    "rows": len(self.rows[sid]),
                    "prose": sum(e.kind in PROSE for e in self.entries[sid]),
                    "metadata": sum(e.kind in HEADINGS for e in self.entries[sid]),
                    "kinds": dict(Counter(r["kind"] for r in self.rows[sid]))}
            base = scene.get("variant_of")
            if base:
                changed = [e for tag, _, _, begin, end in self.alignment(base, sid)
                           if tag != "equal" for e in self.entries[sid][begin:end]]
                item.update(variant_of=base,
                            changed_prose=sum(e.kind in PROSE for e in changed),
                            changed_metadata=sum(e.kind in HEADINGS for e in changed))
            prior = next((s["id"] for s in self.scenes if s["seq"] < scene["seq"]
                          and [e.identity for e in self.entries[s["id"]]] ==
                              [e.identity for e in self.entries[sid]]), None)
            if prior:
                item["exact_reading_alias_of"] = prior
            scenes.append(item)
        return {"source_sha256": self.hashes, "scenes": scenes,
                "prose": sum(s["prose"] for s in scenes)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--episode", type=int, default=34)
    parser.add_argument("--review", type=int, help="Scene seq; print FULL English, never clip entries")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=10**9)
    parser.add_argument("--changed", action="store_true", help="Changed variant entries only")
    parser.add_argument("--against", type=int, help="Review against this scene seq instead of the base")
    args = parser.parse_args(argv)
    source = ReadingSource(args.package, args.episode)
    if args.review is None:
        print(json.dumps(source.inventory(), indent=2, ensure_ascii=False))
        return 0
    scene = next(s for s in source.scenes if s["seq"] == args.review)
    entries = source.entries[scene["id"]]
    if args.changed:
        base = (next(s["id"] for s in source.scenes if s["seq"] == args.against)
                if args.against is not None else scene["variant_of"])
        entries = [e for tag, _, _, begin, end in source.alignment(base, scene["id"])
                   if tag != "equal" for e in entries[begin:end]]
    for entry in entries:
        if args.start <= entry.order <= args.end:
            print(f"{entry.order:4} [{entry.kind}] {entry.speaker or ''}: "
                  + " /PARAGRAPH/ ".join(entry.text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
