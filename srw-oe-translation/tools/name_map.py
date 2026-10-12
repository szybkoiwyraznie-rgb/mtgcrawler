#!/usr/bin/env python3
"""Speaker key -> name table for the whole key universe (dialogue + battle quotes).

Why this exists
---------------
The goal requires that *every* dialogue line and every battle quote carries the name of the
speaker.  Three game structures can supply a name for a key; predecessors wrote three separate
tools for them (``speaker_names.py``, ``name_union.py`` and probes that no longer exist), and the
precedence between them was never proven.  This tool is the single, measured answer:

=========  ==================================================================  =====================
source     what it is                                                        measured agreement
=========  ==================================================================  =====================
charalist  ``charalist<NN>.bin``, 172-byte records (see charalist_table.py)   404 keys - the superset
dict       ``srwDL_CharaDictionary<NN>.bin`` pools (see chara_dictionary.py)  289 keys, ⊂ charalist+NoData
config     config ``.pac`` name slot at key-0x14 (speaker_names.py)          marker rule 89/91 = charalist
=========  ==================================================================  =====================

Measured relations (2026-10-12) [ZWERYFIKOWANE]
------------------------------------------------
* ``charalist.name_full == CharaDictionary.name`` for **285/288** common keys (NFKC-normalised;
  283/288 without normalisation) and
  ``charalist.name_short == CharaDictionary.nickname`` for **288/288** - the two independent
  structures describe the same character table.  The 5 exceptions are width variants
  (``ｱﾘｬﾘｬ･ｺﾘｬﾘｬ･ﾖｯｺｰﾗ三世`` vs ``アリリャ・…``), an empty full name (4135) and a
  parenthesised alias in the dictionary (400).
* The charalist is therefore the name source; the dictionary adds the voice actor, the series
  title and the nickname (goal subpoint c).
* The config name slots are **redundant**: of the 201 quote keys they hit, 190 are already in the
  charalist and the other 11 are single-character byte-coincidence junk (keys 3, 6, 7, 8, 50, 55,
  60, 101, 151, 733, 991 - small integers matching random data).  Only slots with the u16
  ``0x6401`` marker agree with the charalist (89/91; the two exceptions are abbreviations such as
  連邦士官/連邦軍士官 and RS隊員/レッドショルダー隊員);
  unmarked slots are wrong in 91/214 cases.  Hence: never take a name from an unmarked slot, and
  treat marked ones as verification, not as a source.
* Key universe: 313 dialogue keys (26,468 lines) ∪ 319 quote keys (29,577 records) = 321 keys;
  19 quote keys are not in the charalist and only 13 of those carry real text.

Output (game text -> keep under ignored ``local/``)::

    {"summary": {...}, "rows": [{"key": 4501, "short": "セイシロウ", "full": "セイシロウ・クサナギ",
                                 "name_narrow": "ｾｲｼﾛｳ", "series": ..., "voice_actor": ...,
                                 "dialogue_lines": 12, "quote_records": 0,
                                 "source": "charalist", "conflicts": [...]}]}

Usage::

    python tools/name_map.py --dir google_drive \\
        --jsonl local/dialogue/dialogue.jsonl local/battle_quotes/battle_quotes.jsonl \\
        --out local/name_map.json [--tsv local/name_map.tsv] [--verify-config]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import chara_dictionary as CD  # noqa: E402
import charalist_table as CT  # noqa: E402

KINDS = {"dialogue": "dialogue_lines", "quote": "quote_records", "other": "other_texts"}


def _kind_of(path: Path) -> str:
    """Which counter a JSONL file feeds.  Decided by the type of the text, not by the file name."""
    stem = path.stem.lower()
    if "quote" in stem:
        return "quote"
    if "dialogue" in stem:
        return "dialogue"
    return "other"


def load_universe(paths: Sequence[Path]) -> Dict[int, dict]:
    """Read JSONL rows ({key, text, ...}) and count them per key and per kind."""
    universe: Dict[int, dict] = {}
    for path in paths:
        kind = _kind_of(path)
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if "key" not in row:
                    continue
                entry = universe.setdefault(int(row["key"]),
                                            {"dialogue_lines": 0, "quote_records": 0, "other_texts": 0})
                entry[KINDS[kind]] += 1
    return universe


def _nfkc(text: Optional[str]) -> str:
    return unicodedata.normalize("NFKC", text or "").replace(" ", "")


def resolve(universe: Dict[int, dict], charalist: Dict[int, dict],
            dictionary: Dict[int, dict]) -> List[dict]:
    """One row per key of the universe; charalist wins, the dictionary fills in what it lacks."""
    rows: List[dict] = []
    for key in sorted(universe):
        ch = charalist.get(key)
        di = dictionary.get(key)
        conflicts: List[dict] = []
        if ch and di:
            if di["name"] and _nfkc(di["name"]) != _nfkc(ch["name_full"]):
                conflicts.append({"field": "full", "charalist": ch["name_full"],
                                  "dictionary": di["name"]})
            if di["nickname"] and _nfkc(di["nickname"]) != _nfkc(ch["name_short"]):
                conflicts.append({"field": "short", "charalist": ch["name_short"],
                                  "dictionary": di["nickname"]})
        row = {
            "key": key,
            **universe[key],
            "short": (ch or {}).get("name_short") or (di or {}).get("nickname") or None,
            "full": (ch or {}).get("name_full") or (di or {}).get("name") or None,
            "name_narrow": (ch or {}).get("name_narrow") or None,
            "nickname": (di or {}).get("nickname") or None,
            "series": (di or {}).get("series") or None,
            "voice_actor": (di or {}).get("voice_actor") or None,
            "source": "charalist" if ch else ("dictionary" if di else None),
            "conflicts": conflicts,
        }
        if row["full"] in (None, "") and not row["short"]:
            row["source"] = None
        rows.append(row)
    return rows


def verify_config_markers(rows: List[dict], pacs: Dict[str, bytes]) -> dict:
    """Cross-check the config name slots against the charalist (marker slots only)."""
    import speaker_names as SN

    by_key = {r["key"]: r for r in rows}
    agree = disagree = unmarked = 0
    examples: List[dict] = []
    for name, blob in sorted(pacs.items()):
        for key, recs in SN.scan(blob).items():
            row = by_key.get(key)
            if row is None:
                continue
            for rec in recs:
                if rec["confidence"] != "marker":
                    unmarked += 1
                    continue
                got, want = _nfkc(rec["name"]), _nfkc(row["short"])
                if got == want:
                    agree += 1
                else:
                    disagree += 1
                    if len(examples) < 10:
                        examples.append({"file": name, "key": key, "slot": rec["name"],
                                         "charalist": row["short"]})
    return {"agree": agree, "disagree": disagree, "unmarked_slots_ignored": unmarked,
            "examples": examples,
            "rule": "a config name slot is trusted only when the u16 0x6401 marker follows the key"}


def coverage(rows: List[dict]) -> dict:
    counts = collections.Counter(r["source"] or "none" for r in rows)
    unresolved = [r["key"] for r in rows if r["source"] is None]
    return {
        "keys": len(rows),
        "dialogue_keys": sum(1 for r in rows if r["dialogue_lines"]),
        "quote_keys": sum(1 for r in rows if r["quote_records"]),
        "with_short_name": sum(1 for r in rows if r["short"]),
        "with_voice_actor": sum(1 for r in rows if r["voice_actor"]),
        "with_series": sum(1 for r in rows if r["series"]),
        "by_source": dict(counts),
        "conflicts": sum(1 for r in rows if r["conflicts"]),
        "unresolved": unresolved,
        "unresolved_records": {
            "dialogue_lines": sum(r["dialogue_lines"] for r in rows if r["source"] is None),
            "quote_records": sum(r["quote_records"] for r in rows if r["source"] is None),
        },
        "totals": {name: sum(r[field] for r in rows) for name, field in KINDS.items()},
    }


def write_tsv(path: Path, rows: Iterable[dict]) -> None:
    header = ["key", "short", "full", "voice_actor", "series", "dialogue_lines", "quote_records",
              "source", "conflicts"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write("\t".join(header) + "\n")
        for row in rows:
            handle.write("\t".join([
                str(row["key"]), row["short"] or "", row["full"] or "", row["voice_actor"] or "",
                row["series"] or "", str(row["dialogue_lines"]), str(row["quote_records"]),
                row["source"] or "", ";".join(c["field"] for c in row["conflicts"]),
            ]) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", type=Path, required=True,
                    help="directory with config*/imenu* containers (charalist + dictionary)")
    ap.add_argument("--jsonl", type=Path, nargs="+", required=True,
                    help="extraction JSONL files that define the key universe")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tsv", type=Path, default=None)
    ap.add_argument("--verify-config", action="store_true",
                    help="also cross-check the config name slots (slower)")
    args = ap.parse_args(argv)

    containers = sorted(p for p in args.dir.iterdir()
                        if p.name.lower().startswith(("config", "imenu")))
    charalist, cl_errors, cl_members = CT.collect(args.dir)
    dictionary, di_errors = CD.collect(args.dir)
    summary = {
        "charalist_members": cl_members, "charalist_records": len(charalist),
        "dictionary_records": len(dictionary),
        "charalist_errors": cl_errors, "dictionary_errors": di_errors,
        "containers": len(containers),
    }
    cl_index = CT.by_key(charalist)
    di_index, _ = CD.by_key(dictionary)
    universe = load_universe(args.jsonl)
    rows = resolve(universe, cl_index, di_index)
    summary.update(coverage(rows))
    extra = {"rows": rows}
    if args.verify_config:
        import speaker_map as SM
        pacs = {}
        for path in containers:
            if not path.name.lower().startswith("config"):
                continue            # name slots live in the config containers only
            for member, blob in SM.read_members(path):
                if member.lower().endswith(".pac"):
                    pacs[member] = blob
        extra["config_check"] = verify_config_markers(rows, pacs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary, **extra}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    if args.tsv:
        write_tsv(args.tsv, rows)
    print(json.dumps({k: v for k, v in summary.items() if k != "unresolved"},
                     ensure_ascii=False, indent=1))
    print("unresolved keys:", summary["unresolved"])
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
