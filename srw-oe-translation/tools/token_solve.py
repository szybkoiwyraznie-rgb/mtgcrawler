#!/usr/bin/env python3
"""Solve the 0x0F xx glyph tokens by aligning token strings against plain strings (read-only).

IDEA (2026-10-11): a string that contains a token, e.g. ``ﾗｲ<0F 26>ﾝ``, is the same text as a plain
string elsewhere in the game with one character in place of the token (``ライジン``). Each token
occurrence therefore gives a candidate set: the characters that fit the token's place in every
plain string matching the pattern. Intersecting candidate sets over all occurrences of the same
token value narrows it to a single kana when the corpus is large enough.

Corpus:
* plain strings: NUL-terminated CP932 runs of length >= 2 from config*.pac members and imenu
  dictionary members (NFKC-normalised), with NO 0x0F and no control bytes;
* token strings: the same runs that contain at least one ``0x0F xx`` pair.

Output: a JSON with, for each token value, the number of occurrences and the ranked candidate
characters. Candidate evidence is an [HIPOTEZA] until checked by hand; the JSON is game text
and must stay under ``local/``.

Usage:
    python tools/token_solve.py --configs DIR --out local/token_solve.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import speaker_map as SM  # noqa: E402

TOKEN = 0x0F
RUN_MIN = 2

# Verified statistically on 2026-10-11 (control test in docs/NAME_SOURCES.md section 5):
# token byte 0x20 + i -> the i-th voiced/half-voiced katakana in this order. The correct order
# maps 1218 of 4059 fully mapped token strings onto plain corpus strings; shifted, reversed
# or reflected orders map 0. Token values outside 0x20-0x39 are NOT mapped (not covered here).
VOICED_SEQ = "ガギグゲゴザジズゼゾダヂヅデドバパビピブプベペボポヴ"
TOKEN_MAP = {0x20 + i: c for i, c in enumerate(VOICED_SEQ)}


def apply_token_map(text: str, toks: List[int]) -> Tuple[str, bool]:
    """Replace each placeholder (U+E000) with its mapped kana. Returns (text, fully_mapped)."""
    out = text
    for t in toks:
        ch = TOKEN_MAP.get(t)
        if ch is None:
            return out, False
        out = out.replace("\ue000", ch, 1)
    return out, True


def cp932_runs(blob: bytes):
    """Yield (offset, raw bytes) for NUL-terminated runs made of printable CP932 bytes."""
    i = 0
    n = len(blob)
    while i < n:
        j = i
        while j < n and blob[j] != 0:
            j += 1
        if j - i >= RUN_MIN:
            yield i, blob[i:j]
        i = j + 1


def decode_with_tokens(raw: bytes):
    """Return (text with '\\uE000' per token, list of token values) or None if not CP932."""
    out: List[str] = []
    toks: List[int] = []
    i = 0
    while i < len(raw):
        b = raw[i]
        if b == TOKEN:
            if i + 1 >= len(raw):
                return None
            toks.append(raw[i + 1])
            out.append("\ue000")
            i += 2
            continue
        if (0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC) and i + 1 < len(raw) and raw[i + 1] != TOKEN:
            try:
                out.append(raw[i:i + 2].decode("cp932"))
                i += 2
                continue
            except UnicodeDecodeError:
                return None
        try:
            out.append(raw[i:i + 1].decode("cp932"))
        except UnicodeDecodeError:
            return None
        i += 1
    text = unicodedata.normalize("NFKC", "".join(out))
    return text, toks


def is_plain(text: str) -> bool:
    return "\ue000" not in text and not re.search(r"[\x00-\x1f\x7f]", text) and len(text) >= RUN_MIN


def collect(configs_dir: Path):
    plain: collections.Counter = collections.Counter()
    tokstrs: List[Tuple[str, List[int]]] = []
    for p in sorted(configs_dir.iterdir()):
        if not (p.name.lower().startswith(("config", "imenu")) and p.suffix.lower() in (".cpk", ".edat")):
            continue
        for name, blob in SM.read_members(p):
            for _, raw in cp932_runs(blob):
                if TOKEN in raw:
                    d = decode_with_tokens(raw)
                    if d and d[1]:
                        tokstrs.append(d)
                else:
                    d = decode_with_tokens(raw)
                    if d and is_plain(d[0]):
                        plain[d[0]] += 1
    return plain, tokstrs


def solve(plain: collections.Counter, tokstrs):
    plain_list = list(plain)
    # Index plain strings by length so each token string only scans same-length candidates.
    by_len: Dict[int, List[str]] = collections.defaultdict(list)
    for s in plain_list:
        by_len[len(s)].append(s)
    evidence: Dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    occ: collections.Counter = collections.Counter()
    matches_total = 0
    for text, toks in tokstrs:
        for t in toks:
            occ[t] += 1
        pat = re.escape(text).replace(re.escape("\ue000"), "(.)")
        rx = re.compile("^" + pat + "$")
        # Each capture group corresponds to one token in order.
        for s in by_len.get(len(text), []):
            m = rx.match(s)
            if m:
                matches_total += 1
                for gi, t in enumerate(toks):
                    evidence[t][m.group(gi + 1)] += 1
    result = {}
    for t in sorted(occ):
        cands = evidence[t].most_common(12)
        result[f"{t:02X}"] = {"occurrences": occ[t], "candidates": cands}
    return result, matches_total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--configs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    plain, tokstrs = collect(args.configs)
    print(f"plain strings: {len(plain)}  token strings: {len(tokstrs)}")
    result, matches = solve(plain, tokstrs)
    print(f"regex matches: {matches}; token values: {len(result)}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
