#!/usr/bin/env python3
"""Independent reading-edition verifier (stdlib only; imports no renderer/source helper).

Re-read the package, resolve speakers and inline anonymity, preserve paragraph
boundaries, derive a complete alignment and independently union context windows.
Parse EVERY emitted source block back into text/speaker/quotation state. Neither
a correct file hash nor a generator-supplied coverage map is sufficient to pass.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import hashlib
import html
import json
from pathlib import Path
import re

FILES = ("00_dialogue.jsonl", "05_mission_text.jsonl", "06_scenes.jsonl", "07_names_characters.jsonl")
PROSE = {"dialogue", "narration"}
META = {"location", "scene_title", "label"}
UI = {"help", "condition_victory", "condition_defeat"}
NOTE = (
    "> **Reading note:** Blockquoted dialogue is conditional or situational. "
    "Those exchanges are grouped for reading, not as a guaranteed sequence of gameplay events. "
    "No exact HP, turn, or other trigger is claimed where the text export does not establish it. "
    "Failure outcomes are marked separately. The epilogues follow source order; "
    "alternative source versions are presented separately, not as events after the first ending."
)
ALTERNATIVE = (
    "*These passages belong to an alternative source version of this mission, not to a later "
    "event or an additional playthrough. Each excerpt includes surrounding dialogue for context; "
    "unchanged passages between excerpts are not repeated. Some excerpts also reflect passages "
    "absent from this version. No unlock condition is inferred.*"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fold(value):
    result, words = [], []
    for line in value.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        if line.strip():
            words.append(line.strip())
        elif words:
            result.append(" ".join(words))
            words = []
    if words:
        result.append(" ".join(words))
    return tuple(result)


def encode(value):
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    value = "".join("\\" + c if c in "\\`*_[]#" else c for c in value)
    if value.startswith(("- ", "+ ")):
        value = "\\" + value
    match = re.match(r"(\d+)([.)]) ", value)
    if match:
        at = len(match[1])
        value = value[:at] + "\\" + value[at:]
    return value


def decode(value):
    decoded = html.unescape(re.sub(r"\\([\\`*_\[\]#.+)\-])", r"\1", value))
    require(encode(decoded) == value, "Noncanonical/unsafe Markdown escapes")
    return decoded


def prefix(value):
    first = value.splitlines()[0] if value else ""
    if first[:1] in ("＃", "#"):
        require(first in ("＃？？？", "＃???"), f"Unreviewed speaker prefix: {first}")
        return "???"
    return None


def verify(package: Path, plan_path: Path, markdown_path: Path, audit_path: Path) -> dict:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    manifest_path = plan_path.parent / plan["source_manifest"]
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    audit = json.loads(audit_path.read_bytes())
    md_bytes = markdown_path.read_bytes()
    document = md_bytes.decode("utf-8")
    require(plan.get("schema_version") == 1 and plan.get("reviewed") is True, "Unreviewed plan")
    require(audit.get("schema_version") == 1 and audit.get("offset_unit") == "unicode_codepoints",
            "Unsupported audit format")
    require(audit.get("plan_sha256") == digest(plan_bytes), "Plan hash mismatch")
    require(audit.get("source_manifest_sha256") == digest(manifest_bytes), "Manifest hash mismatch")
    require(audit.get("output_sha256") == digest(md_bytes) and audit.get("output_bytes") == len(md_bytes),
            "Output hash/size mismatch")
    datasets, hashes = {}, {}
    for filename in FILES:
        data = (package / filename).read_bytes()
        hashes[filename] = digest(data)
        datasets[filename] = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    require(hashes == manifest["source_sha256"] == audit["source_sha256"], "Source hashes changed")
    scenes = [s for s in datasets["06_scenes.jsonl"]
              if s.get("series") == "story" and s.get("episode") == plan["episode"]]
    require([(s["seq"], s["id"]) for s in scenes] == [(s["seq"], s["id"]) for s in plan["scenes"]],
            "Missing/reordered scene")
    require(len({s["id"] for s in scenes}) == len(scenes), "Duplicate scene")
    require([s["seq"] for s in scenes] == sorted({s["seq"] for s in scenes}), "Source scene order")
    require(audit.get("episode") == plan["episode"], "Episode mismatch")
    scenes_by_id = {s["id"]: s for s in scenes}
    raw = [r for r in datasets["00_dialogue.jsonl"] if r.get("scene") in scenes_by_id]
    raw_by_id = {r["id"]: r for r in raw}
    require(len(raw_by_id) == len(raw), "Duplicate source entry")
    name_sets = defaultdict(lambda: defaultdict(set))
    for r in datasets["07_names_characters.jsonl"]:
        if r.get("key") is not None and r.get("en"):
            name_sets[r["key"]][r.get("part")].add(r["en"].strip())

    def short_name(key):
        for part in ("nickname", "name_short", "name", "name_full"):
            values = name_sets[key][part]
            require(len(values) < 2, "Ambiguous English short name")
            if values:
                name = next(iter(values))
                require(name != "NoData", "Placeholder speaker")
                return name
        raise ValueError(f"Missing speaker {key}")

    by_short = defaultdict(set)
    for row in raw:
        if row["kind"] == "dialogue":
            key = row["speaker"]["id"]
            by_short[short_name(key)].add(key)
    display = {}
    for short, keys in by_short.items():
        full = {}
        for key in keys:
            names = name_sets[key]["name_full"] or name_sets[key]["name"] or {short}
            require(len(names) == 1, "Ambiguous full name")
            full[key] = next(iter(names))
        if len(set(full.values())) > 1:
            display.update(full)

    entries, groups, all_rows = {}, {s["id"]: [] for s in scenes}, {s["id"]: [] for s in scenes}
    for row in raw:
        kind, rid, sid = row["kind"], row["id"], row["scene"]
        require(kind in PROSE | META | UI, f"Unreviewed kind: {rid}")
        require(isinstance(row.get("en"), str) and row["en"].strip(), f"Empty English: {rid}")
        all_rows[sid].append(row)
        if kind in UI:
            continue
        en, label, override = row["en"], None, None
        speaker = row.get("speaker") or {}
        if kind == "dialogue":
            a, b = prefix(row.get("jp", "")), prefix(en)
            require(not (a and b and a != b), "Contradictory speaker overrides")
            override = b or a
            label = override or display.get(speaker.get("id")) or short_name(speaker.get("id"))
            if b:
                en = en.partition("\n")[2]
        elif en.startswith("＃"):
            en = en[1:]
        if "＜主人公名＞" in en:
            en = en.replace("＜主人公名＞", short_name(4501))
        require(not re.search(r"[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f＜＞＃\x00-\x08\x0b\x0c\x0e-\x1f]", en),
                f"Unreviewed source token: {rid}")
        text = fold(en)
        require(bool(text), "Empty readable entry")
        identity = (kind, speaker.get("id"), speaker.get("jp"), override, label, fold(row["en"]))
        entries[rid] = {"id": rid, "kind": kind, "speaker": label, "text": text,
                        "identity": identity, "order": row["order"], "scene": sid}
        groups[sid].append(entries[rid])
    for scene in scenes:
        rs = all_rows[scene["id"]]
        require(len(rs) == scene["rows"], "Source/index row count mismatch")
        require([r["order"] for r in rs] == sorted({r["order"] for r in rs}), "Unordered source rows")
    mission_rows = datasets["05_mission_text.jsonl"]
    missions = {r["id"]: r for r in mission_rows}
    require(len(missions) == len(mission_rows), "Duplicate mission title ID")

    def title(sid):
        visited = set()
        while sid not in visited:
            visited.add(sid)
            scene = scenes_by_id[sid]
            if scene.get("mission_row"):
                rid = scene["mission_row"]
                lines = missions[rid]["en"].strip().splitlines()
                if len(lines) > 1 and re.fullmatch(r"(?:Episode\s+)?\d+(?:話)?", lines[0].strip()):
                    lines.pop(0)
                return " ".join(line.strip() for line in lines), rid
            sid = scene.get("variant_of")
            require(sid in scenes_by_id, "Unresolved mission title")
        raise ValueError("Cyclic mission title")

    require(manifest["prose"] == sum(r["kind"] in PROSE for r in raw), "Inventory prose count")
    require([s["id"] for s in manifest["scenes"]] == [s["id"] for s in scenes], "Inventory scenes")
    for given, scene in zip(manifest["scenes"], scenes):
        sid = scene["id"]
        require(given["seq"] == scene["seq"] and given["title"] == title(sid)[0], "Inventory scene title")
        require(given["rows"] == len(all_rows[sid]) and
                given["prose"] == sum(e["kind"] in PROSE for e in groups[sid]) and
                given["metadata"] == sum(e["kind"] in META for e in groups[sid]) and
                given["kinds"] == dict(Counter(r["kind"] for r in all_rows[sid])), "Inventory counts")
        if scene.get("variant_of"):
            base_id = scene["variant_of"]
            require(given.get("variant_of") == base_id, "Inventory variant base")
            ops = SequenceMatcher(None, [r["identity"] for r in groups[base_id]],
                                  [r["identity"] for r in groups[sid]], autojunk=False).get_opcodes()
            changed = [r for tag, _, _, left, right in ops if tag != "equal" for r in groups[sid][left:right]]
            require(given.get("changed_prose") == sum(r["kind"] in PROSE for r in changed) and
                    given.get("changed_metadata") == sum(r["kind"] in META for r in changed),
                    "Inventory variant difference counts")
        exact = next((s["id"] for s in scenes if s["seq"] < scene["seq"] and
                      [r["identity"] for r in groups[s["id"]]] == [r["identity"] for r in groups[sid]]), None)
        require(given.get("exact_reading_alias_of") == exact, "Inventory exact-alias proof")

    expected, coverage, alignments = [], {}, {}

    def literal(value):
        expected.append({"kind": "literal", "text": value})

    def show(entry, mode, level):
        require(coverage.get(entry["id"], {}).get("status") != "shown", "Duplicate displayed row")
        coverage[entry["id"]] = {"status": "shown", "block": len(expected)}
        expected.append({"kind": "entry", "row": entry["id"], "mode": mode, "heading_level": level})

    def section_for(scene, order):
        return next(s for s in reversed(scene["sections"]) if s["at"] <= order)

    literal(f"# Super Robot Wars OE — Episode {plan['episode']:02d}")
    literal("*English reading script*")
    literal(NOTE)
    previous, chapters = {}, []
    n = plan["context_entries"]
    require(type(n) is int and 1 <= n <= 20, "Invalid excerpt context")
    for scene in plan["scenes"]:
        sid, mode = scene["id"], scene["mode"]
        rows = groups[sid]
        require(scene.get("reviewed") is True and mode in ("full", "variant", "alias"), "Unreviewed scene")
        if mode in ("alias", "variant"):
            require(scene.get("of") in previous, "Forward/unknown variant reference")
            base_scene = previous[scene["of"]]
            require(title(base_scene["id"])[1] == title(sid)[1], "Unrelated source versions")
            base = groups[base_scene["id"]]
        if mode != "alias":
            sections = scene["sections"]
            ats = [s["at"] for s in sections]
            require(ats and ats[0] == 1 and ats == sorted(set(ats)) and
                    set(ats) <= {r["order"] for r in rows}, "Invalid section boundaries")
            for section in sections:
                require(section["mode"] in ("story", "conditional", "failure"), "Invalid quotation mode")
                heading = section.get("heading")
                require(heading is None or isinstance(heading, str) and heading.strip() and "\n" not in heading,
                        "Invalid editorial heading")
                require(section["mode"] == "story" or bool(heading), "Unlabelled alternative exchange")
        for row in all_rows[sid]:
            if row["kind"] in UI:
                coverage[row["id"]] = {"status": "technical", "kind": row["kind"]}
        heading = encode(title(sid)[0])
        if mode == "alias":
            require([r["identity"] for r in rows] == [r["identity"] for r in base], "Unsafe alias")
            for row, target in zip(rows, base):
                coverage[row["id"]] = {"status": "alias", "target": target["id"]}
            label = scenes_by_id[sid].get("variant", "parallel")
            target_label = scenes_by_id[base_scene["id"]].get("variant")
            target = f"version {target_label}" if target_label else "the main version"
            literal(f"*Source-variant note: version {label} of {heading} has the same reading text, "
                    f"speaker identities and headings as {target}; it is not repeated.*")
        else:
            literal("---")
            if mode == "full":
                chapters.append(scene["chapter"])
                literal(f"## Episode {plan['episode']:02d}-{scene['chapter']}: {heading}")
                for row in rows:
                    section = section_for(scene, row["order"])
                    if section["at"] == row["order"] and section.get("heading"):
                        level = 3 if section["mode"] == "story" else 4
                        literal("#" * level + " " + encode(section["heading"]))
                    show(row, section["mode"], 3)
            else:
                require(scene["label"] == scenes_by_id[sid].get("variant"), "Incorrect variant label")
                ops = SequenceMatcher(None, [r["identity"] for r in base],
                                      [r["identity"] for r in rows], autojunk=False).get_opcodes()
                require(any(op[0] != "equal" for op in ops), "Unnecessary variant")
                alignments[sid] = [list(op) for op in ops]
                # Independent context-window union; deliberately NOT get_grouped_opcodes.
                windows = []
                for tag, a, b, c, d in ops:
                    if tag == "equal":
                        for row, target in zip(rows[c:d], base[a:b]):
                            coverage[row["id"]] = {"status": "alias", "target": target["id"]}
                    else:
                        left, right = max(0, c - n), min(len(rows), d + n)
                        if windows and left <= windows[-1][1]:
                            windows[-1][1] = max(windows[-1][1], right)
                        else:
                            windows.append([left, right])
                literal(f"## Alternative text — {heading}, version {scene['label']}")
                literal(ALTERNATIVE)
                for number, (start, end) in enumerate(windows, 1):
                    require(start < end, "Empty variant excerpt")
                    context = title(sid)[0]
                    for row in rows[:start + 1]:
                        if row["kind"] in META:
                            context = row["text"][0]
                    literal(f"### {encode(context)} — variant passage {number}")
                    last_section = None
                    for row in rows[start:end]:
                        section = section_for(scene, row["order"])
                        if (last_section != section["at"] and section.get("heading") and
                                (section["mode"] != "story" or row["order"] == section["at"])):
                            literal("#### " + encode(section["heading"]))
                        last_section = section["at"]
                        show(row, section["mode"], 4)
        previous[scene["seq"]] = scene
    require(chapters == list(range(1, len(chapters) + 1)), "Chapter order")
    require(set(coverage) == set(raw_by_id), "Incomplete independently derived coverage")
    require(audit["coverage"] == coverage, "Coverage/alias/source-order mismatch")
    require(audit["alignments"] == alignments, "Variant alignment mismatch")
    require(len(audit["blocks"]) == len(expected), "Missing/extra output block")
    position = 0
    for block, event in zip(audit["blocks"], expected):
        meta = {k: v for k, v in block.items() if k not in ("start", "end")}
        require(meta == event, "Output block order/role mismatch")
        require(type(block["start"]) is int and type(block["end"]) is int and
                block["start"] == position < block["end"] <= len(document), "Invalid/uncovered output span")
        body = document[position:block["end"]]
        position = block["end"]
        require(body.endswith("\n\n"), "Missing block separator")
        body = body[:-2]
        if event["kind"] == "literal":
            require(body == event["text"], "Editorial heading/note mismatch")
            continue
        row = entries[event["row"]]
        if row["kind"] in META:
            marker = "#" * event["heading_level"] + " "
            require(body.startswith(marker) and "\n" not in body and len(row["text"]) == 1,
                    "Source heading missing/changed")
            require(decode(body[len(marker):]) == row["text"][0], "Source heading text mismatch")
            continue
        if event["mode"] != "story":
            lines = body.split("\n")
            require(all(line == ">" or line.startswith("> ") for line in lines), "Conditional quote missing")
            body = "\n".join("" if line == ">" else line[2:] for line in lines)
        else:
            require(not any(line.startswith(">") for line in body.split("\n")), "Unexpected quotation")
        parts = body.split("\n\n")
        require(all("\n" not in p for p in parts), "Unexpected soft wrap in rendered prose")
        if row["speaker"] is not None:
            match = re.fullmatch(r"\*\*(.+):\*\* (.*)", parts[0])
            require(match is not None, "Missing speaker label")
            require(decode(match[1]) == row["speaker"], "Speaker identity mismatch")
            parts[0] = match[2]
        require(tuple(decode(p) for p in parts) == row["text"],
                f"Full prose/paragraph mismatch: {row['id']}")
    require(position == len(document), "Extra text outside audited blocks")
    metrics = Counter()
    for rid, state in coverage.items():
        kind = raw_by_id[rid]["kind"]
        family = "prose" if kind in PROSE else "metadata" if kind in META else "technical"
        metrics[family + "_source"] += 1
        metrics[family + "_" + state["status"]] += 1
        if family == "prose" and state["status"] == "shown":
            metrics["prose_" + expected[state["block"]]["mode"]] += 1
        if state["status"] == "alias":
            target, seen = state["target"], {rid}
            require(entries[rid]["identity"] == entries[target]["identity"], "Nonidentical alias")
            while coverage[target]["status"] == "alias":
                require(target not in seen, "Alias cycle")
                seen.add(target)
                target = coverage[target]["target"]
            require(coverage[target]["status"] == "shown", "Alias has no displayed endpoint")
    require(audit["metrics"] == dict(metrics), "Coverage metrics mismatch")
    return {"status": "PASS", "episode": plan["episode"], "output_bytes": len(md_bytes),
            "output_sha256": digest(md_bytes), "source_sha256": hashes,
            "plan_sha256": digest(plan_bytes), "source_rows_checked": len(raw),
            "source_scenes_checked": len(scenes), "output_blocks_checked": len(expected),
            "metrics": dict(sorted(metrics.items()))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    if args.report:
        require(not args.report.resolve().is_relative_to(args.package.resolve()) and
                args.report.resolve() not in {args.plan.resolve(), args.markdown.resolve(), args.audit.resolve(),
                                             (args.plan.parent / json.loads(args.plan.read_bytes())["source_manifest"]).resolve()},
                "Refusing to overwrite inputs")
    report = verify(args.package, args.plan, args.markdown, args.audit)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_bytes(rendered.encode("utf-8"))
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
