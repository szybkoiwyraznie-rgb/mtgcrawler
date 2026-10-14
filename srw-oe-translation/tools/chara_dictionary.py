#!/usr/bin/env python3
"""Character encyclopedia records from the SRW OE ``CharaDictionary`` pools (read-only).

MEASURED 2026-10-12 on all 25 local ``imenu`` containers plus the ``config*`` copies
(582 records, 289 distinct keys) [ZWERYFIKOWANE] - the same pool layout as
:mod:`dict_pool_shift` (``u32 count``, ``u32 offsets[]``, records of 12 string pointers).

The 12 strings of a record are, by content (not by index - index 1 is the only one that ever
moves, and only between a name and the ``－－－`` placeholder)::

    [0]   character name            霧隠虎太郎
    [1]   voice actor               折笠愛  (or －－－ when the game has none)
    [2]   encyclopedia entry text   the display template ＠０\\r plus, after it, the entry itself.
                                    The NoData record (key 65535) proves the role: its text is
                                    図鑑用のデータが存在していません。 ("there is no encyclopedia
                                    data") - the game's own placeholder for an empty entry.  Only
                                    3 of 582 records carry any entry text (図鑑用…, デスザウラーの
                                    ゾイドコアと融合した姿。, （ルルーシュ・ランペルージ）); the other
                                    579 hold the bare template, so the encyclopedia's descriptions
                                    are NOT part of the shipped data for those characters.
    [3]   series / work title       元気爆発ガンバルガー
    [4]   nickname with its label   愛称：虎太郎
    [5]   voice actor with label    声優：折笠愛
    [8]   ＠６\\r                     display template (＠N = placeholder for field N)
    [9]   ＠０\\r\\n＠６\\r             display template
    [10]  alternate name            1 record: 勇者ラムネス（馬場ラムネ）
    [11]  short display name        マリア  (217 distinct values)

The speaker key is the u16 at record offset +0x40 (``dict_pool_shift.SPEAKER_KEY_OFFSET``), the same
key the dialogue and battle-quote records carry.  Characters the game does not voice keep the
``－－－`` placeholder in [1]/[5] and count as "no voice actor", never as a name.

Priority when a key appears in several pools (the user rule from session 2): first record in pool
order - containers sorted by file name, records by index.  Duplicates are reported, not merged.

Game text - the output belongs under ``local/`` (gitignored).

Usage:
    python tools/chara_dictionary.py --dir google_drive --out local/chara_dictionary.json \\
        [--keys local/dialogue_key_counts.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import dict_pool_shift as dps  # noqa: E402
import inline_names as IN  # noqa: E402
import speaker_map as SM  # noqa: E402

POOL_MARK = "CharaDictionary"
PLACEHOLDER = "－－－"
ENTRY_TEMPLATE = "＠０\r"
NICK_LABEL = "愛称："
VOICE_LABEL = "声優："
# A name is "clean" when it has no private-use/control characters and is short.  Measured
# exceptions (which a stricter regex flagged as junk) are real names: 勇者ラムネス（馬場ラムネ）,
# タマＱ, Ｃ．Ｃ., コーウェン＆スティンガー, ルドルフ・ゲアハルト・ツェッペリンⅢ世.
_NAME_MAX = 32


def clean_name(text: str) -> bool:
    """True when a name field holds no control/private-use characters and fits the name slot."""
    return bool(text) and len(text) <= _NAME_MAX and all(
        unicodedata.category(c) != "Co" and ord(c) >= 0x20 for c in text)


def decode(raw: bytes) -> str:
    """CP932 string without its NUL; private-use bytes make the whole field unusable."""
    try:
        text = raw.decode("cp932")
    except UnicodeDecodeError:
        return ""
    return "" if any(unicodedata.category(c) == "Co" for c in text) else text


def parse_record(record: dps.Record) -> dict:
    """One record -> {key, name, voice_actor, nickname, series, entry, templates, ...}."""
    strings = [decode(s) for s in record.strings]
    while len(strings) < 12:
        strings.append("")
    voice = strings[5][len(VOICE_LABEL):] if strings[5].startswith(VOICE_LABEL) else strings[1]
    nickname = strings[4][len(NICK_LABEL):] if strings[4].startswith(NICK_LABEL) else ""
    entry = strings[2]
    if entry.startswith(ENTRY_TEMPLATE):
        entry = entry[len(ENTRY_TEMPLATE):]
    return {
        "key": struct.unpack_from("<H", record.prefix, dps.SPEAKER_KEY_OFFSET)[0],
        "name": strings[0],
        "name_clean": clean_name(strings[0]),
        "voice_actor": "" if voice in ("", PLACEHOLDER) else voice,
        "voice_actor_raw": voice,
        "nickname": nickname,
        "series": strings[3],
        "entry": entry,
        "alt_name": strings[10],
        "short_name": strings[11],
        "templates": {"2": strings[2], "8": strings[8], "9": strings[9]},
        "strings": strings,
    }


def collect(directory: Path, read_members=None) -> Tuple[List[dict], List[str]]:
    """Every CharaDictionary record in every container of ``directory``. Returns (rows, errors)."""
    read_members = read_members or SM.read_members
    rows: List[dict] = []
    errors: List[str] = []
    for path in sorted(directory.iterdir()):
        name = path.name.lower()
        if not name.endswith((".cpk", ".edat")):
            continue
        if not (name.startswith("imenu") or name.startswith("config")):
            continue
        try:
            members = read_members(path)
        except Exception as exc:
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        for member_name, blob in members:
            subfiles = IN.pac_subfiles(blob) if member_name.lower().endswith(".pac") \
                else [(member_name, blob)]
            for sub, data in subfiles:
                if POOL_MARK not in sub:
                    continue
                try:
                    pool = dps.parse_pool(data)
                except Exception as exc:
                    errors.append(f"{path.name}/{sub}: {type(exc).__name__}: {exc}")
                    continue
                for index, record in enumerate(pool.records):
                    rows.append({"container": path.name, "member": sub, "record": index,
                                 **parse_record(record)})
    return rows, errors


def by_key(rows: List[dict]) -> Tuple[Dict[int, dict], List[int]]:
    """key -> first record in container/record order; also the list of duplicated keys."""
    index: Dict[int, dict] = {}
    duplicates: List[int] = []
    for row in rows:
        if row["key"] in index:
            duplicates.append(row["key"])
            continue
        index[row["key"]] = row
    return index, duplicates


def coverage(rows: List[dict], keys: Dict[int, int]) -> dict:
    index, _ = by_key(rows)
    missing = sorted(k for k in keys if k not in index)
    return {"records": len(rows), "keys": len(index), "asked": len(keys),
            "covered": len(keys) - len(missing), "missing": missing,
            "missing_lines": sum(keys[k] for k in missing),
            "with_entry_text": sum(1 for k, r in index.items() if r["entry"]),
            "with_voice_actor": sum(1 for k, r in index.items() if r["voice_actor"])}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", type=Path, required=True, help="directory with imenu*/config* files")
    ap.add_argument("--out", type=Path, required=True, help="JSON output (keep under local/)")
    ap.add_argument("--keys", type=Path, default=None,
                    help="optional JSON {key: count} to report coverage against")
    args = ap.parse_args(argv)

    rows, errors = collect(args.dir)
    index, duplicates = by_key(rows)
    summary = {"records": len(rows), "keys": len(index), "duplicate_keys": len(set(duplicates)),
               "with_entry_text": sum(1 for r in index.values() if r["entry"]),
               "with_voice_actor": sum(1 for r in index.values() if r["voice_actor"]),
               "with_nickname": sum(1 for r in index.values() if r["nickname"]),
               "name_pattern_mismatch": [k for k, r in index.items() if not r["name_clean"]][:20],
               "errors": errors[:20], "error_count": len(errors)}
    if args.keys:
        keys = {int(k): int(v) for k, v in json.loads(args.keys.read_text(encoding="utf-8")).items()}
        summary["coverage"] = coverage(rows, keys)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary, "records": rows}, ensure_ascii=False,
                                   indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
