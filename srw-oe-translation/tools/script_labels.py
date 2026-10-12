#!/usr/bin/env python3
"""Link speaker keys to the labels in the user's labelled script copies (read-only).

Generalises local/align_script.py from eventP00 to every event container. For each EVNT dialogue
record (key, Japanese text) the normalised text is matched against the normalised Japanese part of
every ``Label: text`` line in the script copies. A key gets a label tally; the label is the
user's own calibration label (English). Per the user's rule, a config name is authoritative and
these labels are used only for keys with no config/dictionary name (see name_union.py).

Output contains game text and the user's labels: write it under local/ only.

Usage:
    python tools/script_labels.py --dir google_drive --scripts "google_drive/SRW OE Chapter 1 v.3.0.txt" \
        "google_drive/SRW OE Chapter 2 fix.txt" --out local/script_labels.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import speaker_map as SM  # noqa: E402
import crilayla  # noqa: E402
import speaker_probe as sp  # noqa: E402

LABEL = re.compile(r"^([^:：]{1,40})[:：]\s?(.*)$")
STRIP = re.compile(r"[\s\u3000「」『』（）()\[\]【】〈〉《》…・.,、。!！?？~〜ー―\-\"'“”]")


def norm(s: str) -> str:
    return STRIP.sub("", unicodedata.normalize("NFKC", s))


def game_records(path: Path):
    """Yield (member, key, text) for every dialogue record of an event container."""
    try:
        members = SM.read_members(path)  # CPK and EDAT, read-only, CRILAYLA-aware
    except Exception:
        return
    for name, blob in members:
        if name.endswith(sp.SKIP_SUFFIXES):
            continue
        b = blob
        if b[:4] != b"EVNT" and crilayla.is_crilayla(b):
            b = crilayla.decompress(b).data
        start = sp.find_stream_start(b)
        if start is None:
            continue
        recs, _ = sp.walk_records(b, start)
        for off, t, n in recs:
            if t != sp.DIALOGUE:
                continue
            d = sp.dialogue_key(b, off, n)
            if d is None:
                continue
            raw = b[off + 20:off + n].split(b"\x00\x00")[0]
            try:
                txt = raw.decode("cp932")
            except UnicodeDecodeError:
                continue
            yield name, d[1], txt


def script_pairs(path: Path):
    """Yield (label, normalised Japanese text) for every labelled script line."""
    for raw in path.read_bytes().decode("utf-8", "replace").splitlines():
        s = raw.strip()
        m = LABEL.match(s)
        if not m:
            continue
        label = m.group(1).strip()
        text = norm(m.group(2))
        if label and text:
            yield label, text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--scripts", nargs="+", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)

    by_text = collections.defaultdict(collections.Counter)
    for sc in args.scripts:
        for label, text in script_pairs(sc):
            by_text[text][label] += 1

    tally = collections.defaultdict(collections.Counter)
    files = sorted(p for p in args.dir.iterdir()
                   if p.name.lower().startswith(("eventp", "evept")) and p.suffix.lower() in (".cpk", ".edat"))
    total = matched = 0
    for p in files:
        for member, key, txt in game_records(p):
            total += 1
            labels = by_text.get(norm(txt))
            if not labels:
                continue
            matched += 1
            tally[key][labels.most_common(1)[0][0]] += 1

    out = {f"0x{k:x}": {"labels": dict(v.most_common()), "lines": sum(v.values())}
           for k, v in sorted(tally.items())}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"game dialogue records: {total}; matched to a script line: {matched}; keys labelled: {len(out)}")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
