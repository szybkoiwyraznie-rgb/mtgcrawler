#!/usr/bin/env python3
"""Add the fragment-pool strings an older package never saw to ``04_config_text.jsonl``.

The pools behind the item/skill/spirit/status records (convention B, ``srwDL_Skill00`` and
friends) and the DLC copies (convention C, ``srwDL_Skill01-08`` / ``srwDL_Item01-08``) carry
their own u32 pointer tables.  Until 2026-10-14 the extractor split the convention-B pool into
NUL runs and dropped every run holding a control byte, so the 137 Skill00 fragments written with
the game's ``0x0F xx`` kana tokens (``ﾀﾞﾒｰｼﾞ-``, ``防御時､ﾀﾞﾒｰｼﾞ軽減``, ``(ﾗｲｼﾞﾝｵｰと合体)`` ...)
and their DLC copies never reached the translator - and ``coverage_audit`` could not see it,
because its byte scan breaks runs at the same control bytes.

This tool reads the pools the way ``config_text_tables.extract_member`` now does (one row per
pointer, control tokens shown as ``%s``) and appends to the package every pool string the
package does not hold for that member yet, as a normal ``grow`` row with the string's exact
offset.  Rows already present (by member and jp) are left untouched - their shared pool-start id
still works, the writer matches them by content.  Nothing is removed, no English is changed.

The DLC pools repeat the disc pool string for string (``srwDL_Skill01-08`` = the 720 strings of
``srwDL_Skill00``, ``srwDL_Item01-08`` and configst's ``srwDL_Item`` = the 76 of ``srwDL_Item00``),
so a new row of a copy member gets ``copy_of`` = the id of the new config00 row with the same
text: the translator writes each fragment once, ``tools/translation_copy.py`` fills the rest.

The old split also turned the pointer table itself into "strings" (``痺``, ``ｸ8``, ``+&`` - 85 rows
over the four disc pools, measured 2026-10-14); such rows read back from no pool string, the
writer refuses them, and ``--prune-stale`` removes them (they are listed in the report first).

Usage:
    python tools/pool_rows_refresh.py --package local/translation --dlc google_drive [--check]
    python tools/pool_rows_refresh.py --package local/translation --dlc google_drive --prune-stale
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import config_text_tables as CTT  # noqa: E402
import token_map as TM            # noqa: E402

CONFIG_FILE = "04_config_text.jsonl"

#: the disc members whose pools the DLC members repeat (new rows elsewhere copy these)
BASE_MEMBERS = ("srwDL_Skill00.bin", "srwDL_Item00.bin", "srwDL_Spirit.bin", "srwDL_StatusChange.bin")

#: the pool members, by kind, with the containers measured to hold them
POOL_MEMBERS: Dict[str, Tuple[str, ...]] = {
    "skill": ("srwDL_Skill00.bin",) + tuple(f"srwDL_Skill{i:02d}.bin" for i in range(1, 9)),
    "item": ("srwDL_Item00.bin", "srwDL_Item.bin") + tuple(f"srwDL_Item{i:02d}.bin" for i in range(1, 9)),
    "spirit": ("srwDL_Spirit.bin",),
    "status_change": ("srwDL_StatusChange.bin",),
}


def load_rows(path: Path) -> List[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def pool_rows(container: str, member: str, blob: bytes, kind: str) -> List[dict]:
    """The package rows of one member's pool strings, in ``translator_export.config_rows`` shape."""
    out: List[dict] = []
    for item in CTT.extract_member(container, member, blob, kind)["rows"]:
        if not item.get("pool"):
            continue
        for string in item.get("strings", []):
            text = string.get("text") or ""
            if not text or string.get("orphan"):
                continue
            offset = item.get("record_offset", 0) + string.get("rel", 0)
            out.append({
                "id": f"{kind}:{container}/{member}:{offset}",
                "category": f"config_{kind}",
                "part": "text",
                "jp": text,
                "en": "",
                "bytes": string.get("bytes") or len(text.encode("cp932", "replace")),
                "mode": "grow",
                "max_bytes": None,
                "source": {"container": container, "member": member, "offset": offset},
            })
    return out


def containers_of(rows: Sequence[dict]) -> Dict[str, set]:
    """``{container: {member, ...}}`` of every pool member the package already points at."""
    found: Dict[str, set] = {}
    members = {m for names in POOL_MEMBERS.values() for m in names}
    for row in rows:
        source = row.get("source") or {}
        if source.get("member") in members and source.get("container"):
            found.setdefault(source["container"], set()).add(source["member"])
    return found


def refresh(package: Path, dlc_dirs: List[Path], apply: bool, prune_stale: bool = False) -> dict:
    path = package / CONFIG_FILE
    rows = load_rows(path)
    have = {((r.get("source") or {}).get("member"), r.get("jp")) for r in rows}
    containers = TM.Containers(dlc_dirs)
    report: dict = {"package": str(package), "apply": apply, "members": {}, "added": 0,
                    "unreadable": [], "pruned": 0}
    added: List[dict] = []
    stale_rows: List[dict] = []
    base_ids: Dict[Tuple[str, str], str] = {}        # (kind, jp) -> id of the new config00 row
    copies = 0
    for container, members in sorted(containers_of(rows).items()):   # config00 sorts first
        for member in sorted(members):
            kind = next(k for k, names in POOL_MEMBERS.items() if member in names)
            try:
                blob = containers.member(container, member)
            except TM.MapError as error:
                report["unreadable"].append(f"{container}/{member}: {error}")
                continue
            fresh = pool_rows(container, member, blob, kind)
            new = [r for r in fresh if (member, r["jp"]) not in have]
            # rows of the old naive split that no pool string reads back as (the pointer table
            # decoded as text gave single kanji such as 痺 / 蘒): reported, never deleted here
            texts = {r["jp"] for r in fresh}
            pool_start = min([r["source"]["offset"] for r in fresh] or [0]) - 4 * len(fresh)
            stale = [r for r in rows if (r.get("source") or {}).get("member") == member
                     and (r.get("source") or {}).get("container") == container
                     and isinstance((r.get("source") or {}).get("offset"), int)
                     and r["source"]["offset"] >= pool_start
                     and r.get("jp") not in texts and r.get("category") == f"config_{kind}"]
            if stale:
                report.setdefault("stale", {})[f"{container}/{member}"] = [r["jp"] for r in stale]
                stale_rows.extend(stale)
            for row in new:
                key = (kind, row["jp"])
                if member in BASE_MEMBERS:
                    base_ids.setdefault(key, row["id"])
                elif key in base_ids:
                    row["copy_of"] = base_ids[key]
                    copies += 1
            report["members"][f"{container}/{member}"] = {"pool": len(fresh), "new": len(new)}
            added.extend(new)
    report["added"] = len(added)
    report["copies"] = copies
    report["distinct_new_texts"] = len({r["jp"] for r in added})
    if apply and prune_stale and stale_rows:
        drop = {id(r) for r in stale_rows}
        rows = [r for r in rows if id(r) not in drop]
        report["pruned"] = len(stale_rows)
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                        encoding="utf-8")
    if apply and added:
        with path.open("a", encoding="utf-8") as handle:
            for row in added:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--dlc", type=Path, action="append", required=True,
                        help="directory holding the containers (repeatable)")
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    parser.add_argument("--prune-stale", action="store_true",
                        help="also remove the rows no pool string reads back as (listed as 'stale')")
    args = parser.parse_args(argv)
    report = refresh(args.package, args.dlc, apply=not args.check, prune_stale=args.prune_stale)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if report["unreadable"] else 0


if __name__ == "__main__":
    sys.exit(main())
