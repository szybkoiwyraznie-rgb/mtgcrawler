#!/usr/bin/env python3
"""Render a reviewed reading-edition plan; never modify translation/game inputs."""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import html
import json
from pathlib import Path
import re

from reading_script_source import HEADINGS, PROSE, ReadingSource

READING_NOTE = (
    "> **Reading note:** Blockquoted dialogue is conditional or situational. "
    "Those exchanges are grouped for reading, not as a guaranteed sequence of gameplay events. "
    "No exact HP, turn, or other trigger is claimed where the text export does not establish it. "
    "Failure outcomes are marked separately. The epilogues follow source order; "
    "alternative source versions are presented separately, not as events after the first ending."
)
VARIANT_NOTE = (
    "*These passages belong to an alternative source version of this mission, not to a later "
    "event or an additional playthrough. Each excerpt includes surrounding dialogue for context; "
    "unchanged passages between excerpts are not repeated. Some excerpts also reflect passages "
    "absent from this version. No unlock condition is inferred.*"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def escape(text: str) -> str:
    text = re.sub(r"([\\`*_\[\]#])", r"\\\1", html.escape(text, quote=False))
    text = re.sub(r"^([-+]) ", r"\\\1 ", text)
    return re.sub(r"^(\d+)([.)]) ", r"\1\\\2 ", text)


def section_at(scene: dict, order: int) -> dict:
    sections = scene["sections"]
    return sections[bisect_right([s["at"] for s in sections], order) - 1]


def validate_plan(plan: dict, source: ReadingSource) -> None:
    if plan.get("schema_version") != 1 or plan.get("reviewed") is not True:
        raise ValueError("A reviewed schema-1 plan is required")
    if type(plan.get("context_entries")) is not int or not 1 <= plan["context_entries"] <= 20:
        raise ValueError("Variant context must be 1–20 whole entries")
    if [(s["seq"], s["id"]) for s in plan["scenes"]] != [(s["seq"], s["id"]) for s in source.scenes]:
        raise ValueError("Plan must cover every source scene, in source order")
    prior = {}
    chapters = []
    for scene in plan["scenes"]:
        if scene.get("reviewed") is not True:
            raise ValueError(f"Unreviewed scene: {scene['seq']}")
        mode = scene.get("mode")
        if mode not in ("full", "variant", "alias"):
            raise ValueError("Unknown scene mode")
        if mode in ("alias", "variant"):
            if scene.get("of") not in prior:
                raise ValueError("Alias/variant must reference an earlier scene")
            base = prior[scene["of"]]
            if source.title(base["id"])[1] != source.title(scene["id"])[1]:
                raise ValueError("Cannot alias/compare different missions")
        if mode == "full":
            chapters.append(scene["chapter"])
        if mode == "variant" and scene.get("label") != source.scene_by_id[scene["id"]].get("variant"):
            raise ValueError("Variant label does not match source index")
        if mode != "alias":
            sections = scene.get("sections", [])
            starts = [s["at"] for s in sections]
            orders = {e.order for e in source.entries[scene["id"]]}
            if not starts or starts[0] != 1 or starts != sorted(set(starts)) or not set(starts) <= orders:
                raise ValueError("Bad editorial boundaries")
            for section in sections:
                if section["mode"] not in ("story", "conditional", "failure"):
                    raise ValueError("Unknown editorial mode")
                heading = section.get("heading")
                if heading is not None and (not isinstance(heading, str) or not heading.strip()
                                             or "\n" in heading):
                    raise ValueError("Bad editorial heading")
                if section["mode"] != "story" and not heading:
                    raise ValueError("Conditional/failure exchanges need an explicit label")
        prior[scene["seq"]] = scene
    if chapters != list(range(1, len(chapters) + 1)):
        raise ValueError("Main chapters must be consecutive")


def render_entry(entry, mode: str, heading_level: int) -> str:
    if entry.kind in HEADINGS:
        if len(entry.text) != 1:
            raise ValueError(f"Multparagraph heading needs review: {entry.id}")
        return "#" * heading_level + " " + escape(entry.text[0])
    paras = [escape(p) for p in entry.text]
    if entry.speaker is not None:
        paras[0] = f"**{escape(entry.speaker)}:** " + paras[0]
    body = "\n\n".join(paras)
    if mode != "story":
        body = "\n".join("> " + line if line else ">" for line in body.split("\n"))
    return body


def build(source: ReadingSource, plan: dict) -> tuple[str, dict]:
    validate_plan(plan, source)
    pieces = []
    blocks = []
    coverage = {}
    alignments = {}
    position = 0

    def add(content: str, **metadata):
        nonlocal position
        content += "\n\n"
        block = {**metadata, "start": position, "end": position + len(content)}
        blocks.append(block)
        pieces.append(content)
        position += len(content)
        return len(blocks) - 1

    def literal(content: str):
        add(content, kind="literal", text=content)

    def show(entry, mode, level):
        previous = coverage.get(entry.id)
        if previous and previous["status"] == "shown":
            raise ValueError(f"Repeated source entry inside one version: {entry.id}")
        index = add(render_entry(entry, mode, level), kind="entry", row=entry.id,
                    mode=mode, heading_level=level)
        coverage[entry.id] = {"status": "shown", "block": index}

    literal(f"# Super Robot Wars OE — Episode {plan['episode']:02d}")
    literal("*English reading script*")
    literal(READING_NOTE)
    previous = {}
    for scene in plan["scenes"]:
        sid = scene["id"]
        entries = source.entries[sid]
        title = escape(source.title(sid)[0])
        for row in source.rows[sid]:
            if row["kind"] not in PROSE | HEADINGS:
                coverage[row["id"]] = {"status": "technical", "kind": row["kind"]}
        if scene["mode"] == "alias":
            base_scene = previous[scene["of"]]
            base = source.entries[base_scene["id"]]
            if [e.identity for e in entries] != [e.identity for e in base]:
                raise ValueError(f"Unsafe whole-scene alias: {scene['seq']}")
            for entry, target in zip(entries, base):
                coverage[entry.id] = {"status": "alias", "target": target.id}
            label = source.scene_by_id[sid].get("variant", "parallel")
            base_label = source.scene_by_id[base_scene["id"]].get("variant")
            target = f"version {base_label}" if base_label else "the main version"
            literal(f"*Source-variant note: version {label} of {title} has the same reading text, "
                    f"speaker identities and headings as {target}; it is not repeated.*")
        else:
            literal("---")
            if scene["mode"] == "full":
                literal(f"## Episode {plan['episode']:02d}-{scene['chapter']}: {title}")
                starts = {s["at"]: s for s in scene["sections"]}
                for entry in entries:
                    section = section_at(scene, entry.order)
                    if entry.order in starts and section.get("heading"):
                        level = 3 if section["mode"] == "story" else 4
                        literal("#" * level + " " + escape(section["heading"]))
                    show(entry, section["mode"], 3)
            else:
                base_scene = previous[scene["of"]]
                base = source.entries[base_scene["id"]]
                matcher = SequenceMatcher(None, [e.identity for e in base],
                                          [e.identity for e in entries], autojunk=False)
                # get_grouped_opcodes modifies the cached first/last equal opcodes;
                # keep a separate copy of the COMPLETE alignment for coverage.
                opcodes = list(matcher.get_opcodes())
                alignments[sid] = [list(op) for op in opcodes]
                if all(op[0] == "equal" for op in opcodes):
                    raise ValueError("Identical scene should be a whole-scene alias")
                for tag, a, b, c, d in opcodes:
                    if tag == "equal":
                        for entry, target in zip(entries[c:d], base[a:b]):
                            coverage[entry.id] = {"status": "alias", "target": target.id}
                literal(f"## Alternative text — {title}, version {scene['label']}")
                literal(VARIANT_NOTE)
                for number, group in enumerate(matcher.get_grouped_opcodes(plan["context_entries"]), 1):
                    start, end = group[0][3], group[-1][4]
                    if start == end:
                        raise ValueError("Deletion-only excerpt has no surrounding context")
                    heading = next((e.text[0] for e in reversed(entries[:start + 1])
                                    if e.kind in HEADINGS), source.title(sid)[0])
                    literal(f"### {escape(heading)} — variant passage {number}")
                    current_section = None
                    for entry in entries[start:end]:
                        section = section_at(scene, entry.order)
                        # Re-state the editorial context at each excerpt's beginning.
                        if (section["at"] != current_section and section.get("heading")
                                and (section["mode"] != "story" or entry.order == section["at"])):
                            literal("#### " + escape(section["heading"]))
                        current_section = section["at"]
                        show(entry, section["mode"], 4)
        previous[scene["seq"]] = scene

    if set(coverage) != set(source.by_id):
        raise ValueError("Incomplete source coverage")
    for rowid, disposition in coverage.items():
        if disposition["status"] == "alias":
            target = disposition["target"]
            seen = {rowid}
            while coverage[target]["status"] == "alias":
                if target in seen:
                    raise ValueError("Alias cycle")
                seen.add(target)
                target = coverage[target]["target"]
            if coverage[target]["status"] != "shown":
                raise ValueError("Alias does not lead to displayed text")
    metrics = Counter()
    for rowid, disposition in coverage.items():
        kind = source.by_id[rowid]["kind"]
        family = "prose" if kind in PROSE else "metadata" if kind in HEADINGS else "technical"
        metrics[family + "_source"] += 1
        metrics[family + "_" + disposition["status"]] += 1
        if disposition["status"] == "shown" and family == "prose":
            mode = blocks[disposition["block"]]["mode"]
            metrics["prose_" + mode] += 1
    text = "".join(pieces)
    audit = {"schema_version": 1, "offset_unit": "unicode_codepoints", "episode": plan["episode"],
             "source_sha256": source.hashes, "output_sha256": sha(text.encode("utf-8")),
             "output_bytes": len(text.encode("utf-8")), "metrics": dict(sorted(metrics.items())),
             "blocks": blocks, "coverage": coverage, "alignments": alignments}
    return text, audit


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args(argv)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    manifest_path = args.plan.parent / plan["source_manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = ReadingSource(args.package, plan["episode"])
    if source.inventory() != manifest:
        raise ValueError("Source inventory/hash changed; review and update the plan first")
    if args.out.resolve() == args.audit.resolve():
        raise ValueError("Markdown and audit must have different paths")
    for path in (args.out, args.audit):
        if (path.resolve().is_relative_to(args.package.resolve()) or
                path.resolve() in {args.plan.resolve(), manifest_path.resolve()}):
            raise ValueError("Refusing to overwrite inputs")
    text, audit = build(source, plan)
    audit["plan_sha256"] = sha(args.plan.read_bytes())
    audit["source_manifest_sha256"] = sha(manifest_path.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(text.encode("utf-8"))
    args.audit.write_bytes((json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: v for k, v in audit.items() if k not in ("blocks", "coverage", "alignments")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
