#!/usr/bin/env python3
"""Assemble every extracted category into translator-facing JSONL files (plus an index).

The extraction tools each write their own artifact under ``local/``; a translator needs one
place with one row per translatable string, a stable id, the source location, the byte budget
and the speaker of dialogue/quote rows.  This tool joins those artifacts and writes
``local/translation/`` - never the repository, because the files hold game text.

Row shape (one JSON object per line)::

    {"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "category": "dialogue", "part": "dialogue",
     "jp": "...", "en": "", "bytes": 65, "mode": "grow", "max_bytes": null,
     "speaker": {"id": 4501, "jp": "アムロ・レイ", "source": "charalist"},
     "source": {"container": "eventP00.cpk", "member": "DL100_01.bin", "offset": 1844}}

``mode``/``max_bytes`` say how the string may grow: ``grow`` = the container rebuild handles any
length (dialogue, quotes, config pools), ``slot`` = the string sits in a fixed span whose size is
``max_bytes`` (item/skill slots, fixed-stride mission/menu records).

Speaker coverage is reported in ``index.json``; the acceptance criterion recorded with the user is
100% of dialogue *text* translated and speaker names for at least 99% of dialogue lines.

A flat ``strings.csv`` (same rows, one CSV line each) is written next to the JSONL files for
translators who prefer a spreadsheet; ``tools/translation_tools.py`` remains the older CSV
template/checker for the per-run ``text/<package>/units.jsonl`` exports.

Usage:
    python tools/translator_export.py --local local --out local/translation [--no-csv]
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def load_jsonl(path: Path) -> List[dict]:
    """Every JSON object of a JSONL file; a missing file is an empty list."""
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_speakers(path: Path) -> Dict[int, dict]:
    """{key: {short, full, voice_actor, series, source}} from name_map.tsv."""
    speakers: Dict[int, dict] = {}
    if not path.exists():
        return speakers
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            try:
                key = int(row["key"])
            except (KeyError, ValueError):
                continue
            speakers[key] = {
                "short": row.get("short", ""),
                "full": row.get("full", ""),
                "voice_actor": row.get("voice_actor", ""),
                "series": row.get("series", ""),
                "source": row.get("source", ""),
            }
    return speakers


def speaker_of(speakers: Dict[int, dict], key: Optional[int], key_name: str = "id") -> dict:
    """The speaker block of a row: the name when the project has one, the bare key otherwise."""
    entry = speakers.get(key) if key is not None else None
    name = ""
    source = None
    if entry:
        name = entry["full"] or entry["short"]
        source = entry["source"]
    return {key_name: key, "jp": name or None, "source": source}


def row_bytes(text: str) -> int:
    """CP932 bytes of the string (what the game file stores)."""
    try:
        return len(text.encode("cp932"))
    except UnicodeEncodeError:
        return len(text.encode("utf-8"))


def dialogue_rows(local: Path, speakers: Dict[int, dict]) -> List[dict]:
    """Scene dialogue plus narration/conditions/help/labels and the embedded block texts."""
    rows: List[dict] = []
    for part, name in (
        ("dialogue", "dialogue/dialogue.jsonl"),
        ("other", "dialogue/other_text.jsonl"),
        ("embedded", "dialogue/embedded_text.jsonl"),
    ):
        for item in load_jsonl(local / name):
            text = item.get("text", "")
            if not text:
                continue
            key = item.get("key")
            rows.append(
                {
                    "id": f"dlg:{item['container']}/{item['member']}:{item['text_offset']}",
                    "category": "dialogue",
                    "part": part,
                    "jp": text,
                    "en": "",
                    "bytes": item.get("bytes") or row_bytes(text),
                    "mode": "grow",
                    "max_bytes": None,
                    "speaker": speaker_of(speakers, key),
                    "kind": item.get("kind"),
                    "source": {
                        "container": item["container"],
                        "member": item["member"],
                        "offset": item["text_offset"],
                    },
                }
            )
    return rows


def quote_rows(local: Path, speakers: Dict[int, dict]) -> List[dict]:
    """Battle quotes of every ``mesbtl`` container."""
    rows: List[dict] = []
    for item in load_jsonl(local / "battle_quotes/battle_quotes.jsonl"):
        text = item.get("text", "")
        if not text:
            continue
        rows.append(
            {
                "id": f"quo:{item['container']}/{item['member']}:{item['text_offset']}",
                "category": "battle_quote",
                "part": "quote",
                "jp": text,
                "en": "",
                "bytes": item.get("bytes") or row_bytes(text),
                "mode": "grow",
                "max_bytes": None,
                "speaker": speaker_of(speakers, item.get("key")),
                "source": {
                    "container": item["container"],
                    "member": item["member"],
                    "offset": item["text_offset"],
                },
            }
        )
    return rows


def item_skill_rows(local: Path, kind: str) -> List[dict]:
    """Item or skill records: one row per filled slot (name, effect, extra)."""
    rows: List[dict] = []
    for item in load_jsonl(local / "item_skill.jsonl"):
        if item.get("kind") != kind:
            continue
        for slot in ("name", "effect", "extra"):
            text = item.get(slot) or ""
            if not text:
                continue
            span = item.get(f"{slot}_slot")
            rows.append(
                {
                    "id": f"{kind}:{item['container']}/{item['member']}:r{item['record']}:{slot}",
                    "category": kind,
                    "part": slot,
                    "jp": text,
                    "en": "",
                    "bytes": row_bytes(text),
                    "mode": "slot",
                    "max_bytes": span - 1 if isinstance(span, int) and span else None,
                    "key": item.get("key"),
                    "level": item.get("level"),
                    "source": {
                        "container": item["container"],
                        "member": item["member"],
                        "offset": item["offset"],
                    },
                }
            )
    return rows


def config_rows(local: Path) -> List[dict]:
    """Every ``config_text_tables`` kind (reference, spirit, achievements, shop, ...)."""
    rows: List[dict] = []
    for path in sorted((local / "text_tables").glob("*.jsonl")):
        kind = path.stem
        for item in load_jsonl(path):
            for string in item.get("strings", []):
                text = string.get("text") or ""
                if not text:
                    continue
                offset = item.get("record_offset", 0) + string.get("rel", 0) if not item.get("pool") \
                    else item.get("record_offset", 0)
                rows.append(
                    {
                        "id": f"{kind}:{item['container']}/{item['member']}:{offset}",
                        "category": f"config_{kind}",
                        "part": "text",
                        "jp": text,
                        "en": "",
                        "bytes": string.get("bytes") or row_bytes(text),
                        "mode": "grow",
                        "max_bytes": None,
                        "source": {
                            "container": item["container"],
                            "member": item["member"],
                            "offset": offset,
                        },
                    }
                )
    return rows


def mission_rows(local: Path) -> List[dict]:
    """Mission titles/notes, BGM titles, map/background/squad names (fixed-stride records)."""
    rows: List[dict] = []
    for item in load_jsonl(local / "mission_text.jsonl"):
        for slot in item.get("slots", []):
            text = slot.get("text") or ""
            if not text:
                continue
            rows.append(
                {
                    "id": f"{item['kind']}:{item['container']}/{item['member']}:"
                          f"r{item['record']}:{slot['role']}",
                    "category": item["kind"],
                    "part": slot["role"],
                    "jp": text,
                    "en": "",
                    "bytes": slot.get("bytes") or row_bytes(text),
                    "mode": "slot",
                    "max_bytes": (slot.get("span") or 0) - 1 or None,
                    "source": {
                        "container": item["container"],
                        "member": item["member"],
                        "offset": item["offset"] + slot["offset"],
                    },
                }
            )
    return rows


def character_rows(local: Path) -> List[dict]:
    """Character names, nicknames, series and voice actors (one row per field and key)."""
    rows: List[dict] = []
    seen = set()

    def add(key: Optional[int], field: str, text: str, container: str, member: str, offset: int) -> None:
        if not text or not text.strip():
            return
        ident = (field, text)
        rows.append(
            {
                "id": f"char:{key}:{field}",
                "category": f"character_{field}",
                "part": field,
                "jp": text,
                "en": "",
                "bytes": row_bytes(text),
                "mode": "grow",
                "max_bytes": None,
                "key": key,
                "duplicate": ident in seen,
                "source": {"container": container, "member": member, "offset": offset},
            }
        )
        seen.add(ident)

    for record in (json.loads((local / "chara_dictionary.json").read_text(encoding="utf-8"))["records"]
                   if (local / "chara_dictionary.json").exists() else []):
        container, member = record["container"], record["member"]
        add(record.get("key"), "name", record.get("name", ""), container, member, 0)
        add(record.get("key"), "nickname", record.get("nickname", ""), container, member, 0)
        add(record.get("key"), "series", record.get("series", ""), container, member, 0)
        add(record.get("key"), "voice_actor", record.get("voice_actor", ""), container, member, 0)
        add(record.get("key"), "entry", record.get("entry", ""), container, member, 0)
    for record in (json.loads((local / "charalist.json").read_text(encoding="utf-8"))["records"]
                   if (local / "charalist.json").exists() else []):
        container, member, key = record["container"], record["member"], record.get("key")
        add(key, "name_short", record.get("name_short", ""), container, member, 0)
        add(key, "name_full", record.get("name_full", ""), container, member, 0)
        add(key, "name_narrow", record.get("name_narrow", ""), container, member, 0)
    return rows


def unit_rows(local: Path) -> List[dict]:
    """Unit names, series, weapon names and the robot-dictionary notes (short fields)."""
    rows: List[dict] = []
    units_csv = local / "units/units.csv"
    if units_csv.exists():
        with units_csv.open(encoding="utf-8", newline="") as handle:
            for record in csv.DictReader(handle):
                unit = record.get("unit_id")
                for field, column in (("name", "name"), ("name_display", "name_display"), ("series", "series")):
                    text = record.get(column, "")
                    if not text:
                        continue
                    rows.append(
                        {
                            "id": f"unit:{unit}:{field}",
                            "category": f"unit_{field}",
                            "part": field,
                            "jp": text,
                            "en": "",
                            "bytes": row_bytes(text),
                            "mode": "grow",
                            "max_bytes": None,
                            "key": unit,
                            "source": {"container": record.get("container"), "member": "unit_list",
                                       "offset": record.get("unit_index")},
                        }
                    )
    weapons = json.loads((local / "units/unit_weapons.json").read_text(encoding="utf-8")) \
        if (local / "units/unit_weapons.json").exists() else {}
    for unit_record in weapons.get("units", []):
        unit = unit_record.get("unit_id")
        container = unit_record.get("container")
        for weapon in unit_record.get("weapons", []):
            for field in ("name", "name_short"):
                text = weapon.get(field) or ""
                if not text:
                    continue
                rows.append(
                    {
                        "id": f"weapon:{unit}:{weapon.get('index')}:{field}",
                        "category": f"weapon_{field}",
                        "part": field,
                        "jp": text,
                        "en": "",
                        "bytes": row_bytes(text),
                        "mode": "grow",
                        "max_bytes": None,
                        "key": unit,
                        "source": {"container": container, "member": "wp_list",
                                   "offset": weapon.get("index")},
                    }
                )
    for record in weapons.get("robo_dictionary", []):
        unit = record.get("unit_id")
        for field in ("series", "length", "weight"):
            text = (record.get(field) or "").strip()
            if not text or "－－－" in text:
                continue
            rows.append(
                {
                    "id": f"robonote:{unit}:{field}",
                    "category": f"robo_{field}",
                    "part": field,
                    "jp": text,
                    "en": "",
                    "bytes": row_bytes(text),
                    "mode": "grow",
                    "max_bytes": None,
                    "key": unit,
                    "source": {"container": None, "member": "srw_DL_RoboDictionary",
                               "offset": record.get("record")},
                }
            )
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


CSV_COLUMNS = ("id", "category", "part", "jp", "en", "bytes", "max_bytes", "mode",
               "speaker_key", "speaker_jp", "container", "member", "offset")


def write_csv(path: Path, rows: Iterable[dict]) -> int:
    """Flat CSV view of the same rows (spreadsheet-friendly for translators)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_COLUMNS)
        for row in rows:
            speaker = row.get("speaker") or {}
            source = row.get("source") or {}
            writer.writerow([
                row["id"], row["category"], row["part"], row["jp"], row.get("en", ""),
                row["bytes"], row.get("max_bytes") or "", row["mode"],
                speaker.get("id") if speaker.get("id") is not None else "",
                speaker.get("jp") or "",
                source.get("container") or "", source.get("member") or "", source.get("offset") or "",
            ])
            count += 1
    return count


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--local", default="local", help="folder with the extraction artifacts")
    parser.add_argument("--out", default="local/translation", help="output folder (keep it ignored)")
    parser.add_argument("--no-csv", action="store_true", help="skip the flat strings.csv")
    args = parser.parse_args(argv)

    local = Path(args.local)
    out = Path(args.out)
    speakers = load_speakers(local / "name_map.tsv")

    parts = {
        "00_dialogue.jsonl": dialogue_rows(local, speakers),
        "01_battle_quotes.jsonl": quote_rows(local, speakers),
        "02_items.jsonl": item_skill_rows(local, "item"),
        "03_skills.jsonl": item_skill_rows(local, "skill"),
        "04_config_text.jsonl": config_rows(local),
        "05_mission_text.jsonl": mission_rows(local),
        "10_names_characters.jsonl": character_rows(local),
        "11_names_units_weapons.jsonl": unit_rows(local),
    }

    index: dict = {"parts": {}, "categories": {}, "speaker": {}}
    for name, rows in parts.items():
        write_jsonl(out / name, rows)
        index["parts"][name] = {
            "rows": len(rows),
            "jp_bytes": sum(row["bytes"] for row in rows),
            "unique_jp": len({row["jp"] for row in rows}),
        }
        for row in rows:
            entry = index["categories"].setdefault(row["category"], {"rows": 0, "jp_bytes": 0})
            entry["rows"] += 1
            entry["jp_bytes"] += row["bytes"]

    # Only these two groups carry a speaker key: the scene lines and the battle quotes.
    # Narration/conditions/help/labels and the embedded block texts have no speaker by design.
    for label, part, kinds in (("dialogue", "00_dialogue.jsonl", ("dialogue",)),
                               ("battle_quote", "01_battle_quotes.jsonl", ("quote",))):
        rows = [row for row in parts[part] if row.get("part") in kinds]
        named = sum(1 for row in rows if (row.get("speaker") or {}).get("jp"))
        index["speaker"][label] = {
            "rows": len(rows),
            "named": named,
            "unnamed": len(rows) - named,
            "unnamed_percent": round(100.0 * (len(rows) - named) / len(rows), 2) if rows else 0.0,
        }

    index["totals"] = {
        "rows": sum(part["rows"] for part in index["parts"].values()),
        "jp_bytes": sum(part["jp_bytes"] for part in index["parts"].values()),
        "files": sorted(index["parts"]),
    }
    index["notes"] = [
        "mode=grow: the container rebuild accepts any string length (dialogue, quotes, config pools).",
        "mode=slot: the string sits in a fixed span; max_bytes is that span minus its NUL.",
        "speaker.jp = null means the project has no name for that key yet (see index.speaker).",
        "Only the dialogue and quote rows carry a speaker; narration/help/label rows do not.",
        "Keep strings CP932-encodable; keep the in-game placeholders (＠0-＠9, ％s, ＄) intact.",
    ]
    if not args.no_csv:
        flat = [row for rows in parts.values() for row in rows]
        index["totals"]["csv_rows"] = write_csv(out / "strings.csv", flat)
    (out / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"totals": index["totals"], "speaker": index["speaker"],
                      "categories": sorted(index["categories"])}, ensure_ascii=False, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
