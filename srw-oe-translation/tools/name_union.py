#!/usr/bin/env python3
"""Union of every speaker key seen in EVNT dialogue and in battle-quote members -> display name.

RULES (user decisions, 2026-10-11):
* Name priority: (1) first dictionary record in imenu pool order (file, then record index),
  (2) first config name-slot record (scan order), (3) raw name-slot decode that KEEPS 0x0F tokens
  as ``{0F xx}`` placeholders, (4) ``UNNAMED``.
* A key that has two dictionary records takes the first one. Duplicate records with identical
  names are reported, not merged (the alias hypothesis was not supported; see EXPERIMENT_LOG).
* Generic characters (officer, soldier, pilot) count as names: they are in the game.
* Battle-quote members are linked by key (member ``p<key>.pac``), so each quote record gets the
  name of its key.

INPUTS (all under local/, gitignored, they contain game text):
  --dialogue local/whole_game_map.json      (built by local/whole_game_map.py from event probes)
  --speakers  local/whole_game_speakers.json
  --battle    local/battle_members.json     (tools/battle_members.py output)
  --configs   config*.cpk / config*.EDAT    (read-only, for the raw token fallback)

OUTPUT: --out JSON (one row per key) and --md Markdown table. Both hold game text: keep in local/.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
import re
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import speaker_names as SN  # noqa: E402
import token_solve as TS  # noqa: E402

_TOKEN_PH = re.compile(r"\{0F ([0-9A-F]{2})\}")


def apply_known_tokens(name: str) -> tuple:
    """Replace {0F xx} placeholders by the verified voiced-kana map. Returns (name, fully_mapped)."""
    toks = [int(m.group(1), 16) for m in _TOKEN_PH.finditer(name)]
    if not toks:
        return name, True
    ok = True
    out = name
    for t in toks:
        ch = TS.TOKEN_MAP.get(t)
        if ch is None:
            ok = False
            break
        out = _TOKEN_PH.sub(ch, out, count=1)
    return out, ok

KEY_OFF = SN.KEY_OFF
SLOT = SN.SLOT
TOKEN = 0x0F


def raw_decode_slot(blob: bytes, start: int) -> Optional[str]:
    """Decode a 16-byte name slot keeping 0x0F xx tokens as ``{0F xx}``. None if not a name."""
    if start < 0 or start + SLOT > len(blob):
        return None
    raw = blob[start:start + SLOT]
    end = raw.find(b"\x00")
    if end <= 0:
        return None
    body = raw[:end]
    out = []
    i = 0
    while i < len(body):
        if body[i] == TOKEN and i + 1 < len(body):
            out.append("{0F %02X}" % body[i + 1])
            i += 2
            continue
        # Two-byte CP932 only for lead bytes 0x81-0x9F / 0xE0-0xFC. Bytes 0xA1-0xDF are single-byte
        # half-width katakana and must never swallow a following 0x0F token byte.
        lead_ok = 0x81 <= body[i] <= 0x9F or 0xE0 <= body[i] <= 0xFC
        if lead_ok and i + 1 < len(body) and body[i + 1] != TOKEN:
            try:
                out.append(body[i:i + 2].decode("cp932"))
                i += 2
                continue
            except UnicodeDecodeError:
                pass
        try:
            out.append(body[i:i + 1].decode("cp932"))
        except UnicodeDecodeError:
            return None
        i += 1
    # NFKC folds half-width katakana (ｵﾝ -> オン); tokens are placeholders and are kept as-is.
    s = unicodedata.normalize("NFKC", "".join(out)).strip()
    return s or None


FULLWIDTH_RE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\uff10-\uff19\uff21-\uff3a\uff41-\uff5a]")
CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")


def is_name(name: str, marker: bool) -> bool:
    """Strict acceptance. Marker-verified slots pass; others need >=2 full-width chars, no controls."""
    if not name or CTRL_RE.search(name.replace("{0F ", "").replace("}", "")):
        return False
    if marker:
        return True
    # Unmarked slots: reject game labels (digits, symbols, BGM/scene wording seen in probes).
    if re.search(r"[0-9%.!?/:+*\-－ー]|BGM|ｂｇｍ", name, re.IGNORECASE):
        return False
    if name[:1] in ("ー", "ｰ", "-", "・"):  # fragments that start mid-word
        return False
    return len(FULLWIDTH_RE.findall(name)) >= 2


def raw_scan(blob: bytes, key: int) -> List[dict]:
    """Raw name-slot candidates for one key (marker-verified first), strict filter applied."""
    needle = struct.pack("<I", key)
    res = []
    i = blob.find(needle)
    while i >= 0:
        q = i
        if q - KEY_OFF >= 0:
            name = raw_decode_slot(blob, q - KEY_OFF)
            if name:
                marker = struct.unpack_from("<H", blob, q + SN.MARK_OFF)[0] == SN.MARK \
                    if q + SN.MARK_OFF + 2 <= len(blob) else False
                if is_name(name, marker):
                    res.append({"offset": q - KEY_OFF, "name": name, "marker": marker})
        i = blob.find(needle, i + 1)
    res.sort(key=lambda r: (not r["marker"], r["offset"]))
    return res


def load_config_blobs(paths: List[Path]) -> Dict[str, bytes]:
    return SN.load_pacs(paths)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dialogue", required=True, type=Path)
    ap.add_argument("--speakers", required=True, type=Path)
    ap.add_argument("--battle", required=True, type=Path)
    ap.add_argument("--configs", nargs="+", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--md", type=Path)
    args = ap.parse_args(argv)

    dialogue = json.loads(args.dialogue.read_text(encoding="utf-8"))
    speakers = json.loads(args.speakers.read_text(encoding="utf-8"))
    battle = json.loads(args.battle.read_text(encoding="utf-8"))
    pacs = load_config_blobs(args.configs)

    keys = {}
    for k in dialogue:
        keys[int(k, 16) if isinstance(k, str) and k.startswith("0x") else int(k)] = True
    for k in battle:
        keys[int(k)] = True

    rows = []
    unresolved_raw = 0
    for key in sorted(keys):
        hk = hex(key)
        row = {"key": key, "hex": hk, "dialogue": key in {int(x, 16) if str(x).startswith("0x") else int(x) for x in dialogue},
               "battle_records": battle.get(str(key), {}).get("records", 0),
               "battle_member": (battle.get(str(key), {}).get("members") or [None])[0],
               "name": None, "source": None, "dict_first": None, "dict_count": 0, "events": []}
        sp = speakers.get(hk)
        if sp:
            row["events"] = sp.get("events", [])
            dicts = sp.get("dict_files") or []
            row["dict_count"] = len(sp.get("dict", []) or [])
            if sp.get("src") == "dict" and sp.get("name"):
                row["name"] = sp["name"]
                row["source"] = "dict"
                row["dict_first"] = (sp.get("dict") or [{}])[0] if sp.get("dict") else None
            elif sp.get("src") == "config" and sp.get("name"):
                row["name"] = sp["name"]
                row["source"] = "config"
        if row["name"] is None:
            cands = []
            for fname, blob in pacs.items():
                for r in raw_scan(blob, key):
                    cands.append({"file": fname, **r})
            cands.sort(key=lambda c: (not c["marker"], c["file"], c["offset"]))
            if cands:
                row["name"] = cands[0]["name"]
                mapped, all_ok = apply_known_tokens(cands[0]["name"])
                if all_ok and mapped != cands[0]["name"]:
                    row["name_raw"] = cands[0]["name"]
                    row["name"] = mapped
                    row["token_mapped"] = True
                row["source"] = "config_raw" if "{0F" in cands[0]["name"] else "config_raw_clean"
                row["confidence"] = "marker" if cands[0]["marker"] else "unmarked-review"
                row["raw_candidates"] = len(cands)
                if "{0F" in cands[0]["name"]:
                    unresolved_raw += 1
            else:
                row["name"] = "UNNAMED"
                row["source"] = "none"
        rows.append(row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

    counts = {}
    for r in rows:
        counts[r["source"]] = counts.get(r["source"], 0) + 1
    print("keys:", len(rows), "by source:", counts)
    print("dialogue keys:", sum(1 for r in rows if r["dialogue"]),
          " battle-only keys:", sum(1 for r in rows if not r["dialogue"]))
    print("raw names with 0F tokens:", unresolved_raw)

    if args.md:
        lines = ["| key | hex | name | source | battle records | events |", "|---:|---|---|---|---:|---|"]
        for r in rows:
            ev = ", ".join(r["events"][:4]) if r["events"] else ""
            lines.append(f'| {r["key"]} | {r["hex"]} | {r["name"]} | {r["source"]} | {r["battle_records"]} | {ev} |')
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("wrote", args.md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
