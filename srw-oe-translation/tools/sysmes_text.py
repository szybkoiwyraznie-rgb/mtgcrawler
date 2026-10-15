#!/usr/bin/env python3
"""Every text of configst's ``sysmes.bin`` (read-only; text goes only to the ``--out`` JSONL).

Why this exists
---------------
The translator package held no row at all from ``sysmes.bin`` -- the member that carries the
menu, help and warning texts of ``configst.cpk`` (``第１章 本編``, ``精神コマンドを使用した際の
エフェクトを表示するかを指定します。``, the DLC download notices).  The package coverage audit
(``tools/coverage_audit.py``) found it: 824 scanned runs of ``configst.cpk`` had no row anywhere.
Build the rows here, merge them into ``04_config_text.jsonl`` with ``--merge-into``.

Layout (measured 2026-10-14, see :mod:`sysmes_pack`)
---------------------------------------------------
    'SMES' | u32 file_size | u32 count | u32 1 | count x {u32 off, u32 id} | pool

The pool holds exactly ``count`` CP932 strings in sequence (NUL-terminated, padded to 4 B)
and entry k points at string k with an offset relative to the pool start.  One row per
WHOLE string: a row's ``offset`` is the absolute offset of that string in ``sysmes.bin``.
(The first version of this exporter walked the run scanner instead and emitted 1,141 extra
rows for the tails of strings that contain ASCII / half-width / control bytes; those rows are
not pool entries, the builder ignores them and ``--prune-fragments`` removes them.)

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


def has_japanese(text: str) -> bool:
    """Kana / kanji / full-width punctuation -- and HALF-WIDTH katakana (U+FF61..U+FF9F).

    The half-width range was missing until 2026-10-15: the pool strings written with the
    ``0x0F xx`` voiced-kana tokens (``ﾒｲﾝ<0F>0ｲﾛｯﾄ`` = メインパイロット, ``ｻ<0F>3<0F>0ｲﾛｯﾄ`` = サブ
    パイロット, ``ｿｰﾄ``, ``<0F>6ｰ<0F>&`` = ページ, ``＠1[GRﾐｯｼｮﾝ]``, ``ｼﾐｭﾚｰﾀｰﾐｯｼｮﾝ``, the ``＠4<0F>#ｰﾏｰ:``
    status line) were dropped here, so they never reached the package and stayed Japanese in
    the game (build #19 screenshots).  The builder's sysmes writer needs the WHOLE string.
    """
    return any("\u3040" <= ch <= "\u9fff" or "\uff61" <= ch <= "\uff9f"
               or ch in "、。「」！？…ー『』（）／" for ch in text)


def pool_strings(sm: bytes) -> List[dict]:
    """One row per pool string (the table entry's whole text), Japanese ones only."""
    parsed = SP.parse(sm)
    out: List[dict] = []
    for offset, raw in zip(parsed.starts, parsed.strings):
        try:
            text = raw.decode("cp932")
        except UnicodeDecodeError:
            continue
        if not text:
            continue
        if not has_japanese(text):
            continue
        out.append({"id": f"sysmes:{CONTAINER}/{MEMBER}:{offset}", "category": "config_sysmes",
                    "part": "text", "jp": text, "en": "", "bytes": len(raw), "mode": "grow",
                    "max_bytes": None,
                    "source": {"container": CONTAINER, "member": MEMBER, "offset": offset}})
    return out


def fragment_ids(sm: bytes, rows: List[dict]) -> List[str]:
    """Ids of ``config_sysmes`` rows whose offset is not a whole-string start."""
    starts = set(SP.parse(sm).starts)
    return [row["id"] for row in rows
            if row.get("category") == "config_sysmes"
            and (row.get("source") or {}).get("member") == MEMBER
            and (row.get("source") or {}).get("offset") not in starts]


def merge_into(rows: List[dict], target: Path, prune: Sequence[str] = ()) -> dict:
    """Add rows the target does not have yet (by id), drop ``prune`` ids; rewritten in place."""
    existing = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    drop = set(prune)
    kept = [row for row in existing if row["id"] not in drop]
    known = {row["id"] for row in kept}
    added = [row for row in rows if row["id"] not in known]
    if added or len(kept) != len(existing):
        merged = kept + added
        merged.sort(key=lambda row: (row["source"]["container"], row["source"]["member"],
                                     row["source"]["offset"]))
        with target.open("w", encoding="utf-8") as handle:
            for row in merged:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"existing": len(existing), "added": len(added), "pruned": len(existing) - len(kept),
            "total": len(kept) + len(added)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract configst sysmes.bin texts (read-only)")
    parser.add_argument("--configst", type=Path, required=True, help="configst.cpk of the game")
    parser.add_argument("--out", type=Path, help="where to write the JSONL")
    parser.add_argument("--merge-into", type=Path, help="package JSONL to add the rows to")
    parser.add_argument("--prune-fragments", action="store_true",
                        help="with --merge-into: drop sysmes rows that are not whole strings")
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
        prune: List[str] = []
        if args.prune_fragments:
            present = [json.loads(line) for line in
                       args.merge_into.read_text(encoding="utf-8").splitlines() if line.strip()]
            prune = fragment_ids(sm, present)
        report = merge_into(rows, args.merge_into, prune)
        print(f"w {args.merge_into}: było {report['existing']}, dodane {report['added']}, "
              f"usunięte fragmenty {report['pruned']}, razem {report['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
