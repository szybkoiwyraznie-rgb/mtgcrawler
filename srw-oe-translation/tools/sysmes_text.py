#!/usr/bin/env python3
"""Every text of configst's ``sysmes.bin`` (read-only; text goes only to the ``--out`` JSONL).

Why this exists
---------------
The translator package held no row at all from ``sysmes.bin`` -- the member that carries the
menu, help and warning texts of ``configst.cpk`` (``第１章 本編``, ``精神コマンドを使用した際の
エフェクトを表示するかを指定します。``, the DLC download notices).  The package coverage audit
(``tools/coverage_audit.py``) found it: 824 scanned runs of ``configst.cpk`` had no row anywhere.
Build the rows here, merge them into ``04_config_text.jsonl`` with ``--merge-into``.

Layout (measured, see :mod:`sysmes_pack`)
----------------------------------------
    'SMES' | u32 file_size | u32 count | record/pointer table (to 0x2500) | text pool

The pool holds CP932 strings, NUL-terminated and padded to a 4-byte boundary; the pointer
table stores ``u32 pool_offset`` words, so every row's ``offset`` is the **pool offset** the
writer needs to rewrite the pointer when the text grows.

Usage::

    python tools/sysmes_text.py --configst google_drive/configst.cpk --out local/sysmes_text.jsonl
    python tools/sysmes_text.py --configst ... --merge-into local/translation/04_config_text.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import configst_pack as CSP  # noqa: E402
import speaker_map as SM  # noqa: E402
import sysmes_pack as SP  # noqa: E402
import extract_structured as ES  # noqa: E402

CONTAINER = "configst.cpk"
MEMBER = "sysmes.bin"


def sysmes_blob(path: Path) -> bytes:
    """The decompressed ``sysmes.bin`` of a ``configst.cpk`` (cpk -> pac -> member)."""
    pac = dict(SM.read_members(path))["configst.pac"]
    for sub in CSP.parse_pac(pac)["subs"]:
        if sub["name"] == MEMBER:
            return sub["data"]
    raise ValueError(f"{path} has no member {MEMBER}")


def pool_strings(sm: bytes) -> List[dict]:
    """One row per pool string: the scan says where each string starts, the NUL where it ends."""
    starts = SP.string_starts(sm)
    out: List[dict] = []
    for offset in starts:
        end = sm.find(b"\x00", offset)
        if end < 0:
            continue
        raw = sm[offset:end]
        try:
            text = raw.decode("cp932")
        except UnicodeDecodeError:
            continue
        if not text or not ES.has_cjk(text) if hasattr(ES, "has_cjk") else False:
            pass
        if not text:
            continue
        if not any("\u3040" <= ch <= "\u9fff" or ch in "、。「」！？…ー『』（）／" for ch in text):
            continue
        out.append({"id": f"sysmes:{CONTAINER}/{MEMBER}:{offset}", "category": "config_sysmes",
                    "part": "text", "jp": text, "en": "", "bytes": len(raw), "mode": "grow",
                    "max_bytes": None,
                    "source": {"container": CONTAINER, "member": MEMBER, "offset": offset}})
    return out


def merge_into(rows: List[dict], target: Path) -> dict:
    """Add rows the target does not have yet (by id); the file is rewritten in place."""
    existing = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    known = {row["id"] for row in existing}
    added = [row for row in rows if row["id"] not in known]
    if added:
        merged = existing + added
        merged.sort(key=lambda row: (row["source"]["container"], row["source"]["member"],
                                     row["source"]["offset"]))
        with target.open("w", encoding="utf-8") as handle:
            for row in merged:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"existing": len(existing), "added": len(added), "total": len(existing) + len(added)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract configst sysmes.bin texts (read-only)")
    parser.add_argument("--configst", type=Path, required=True, help="configst.cpk of the game")
    parser.add_argument("--out", type=Path, help="where to write the JSONL")
    parser.add_argument("--merge-into", type=Path, help="package JSONL to add the rows to")
    args = parser.parse_args(argv)

    sm = sysmes_blob(args.configst)
    rows = pool_strings(sm)
    chars = sum(len(row["jp"]) for row in rows)
    print(f"{MEMBER}: {len(sm)} B, tekstów w puli: {len(rows)} ({chars} znaków)")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"zapisane: {args.out}")
    if args.merge_into:
        report = merge_into(rows, args.merge_into)
        print(f"w {args.merge_into}: było {report['existing']}, dodane {report['added']}, "
              f"razem {report['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
