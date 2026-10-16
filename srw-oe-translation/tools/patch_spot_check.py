#!/usr/bin/env python3
"""Spot-check a built patch against the package it was built from: did every filled row land?

The builder's ``build_report.json`` keeps only the first problems of every writer, so after a
rehearsal (or a real build) nobody can list *which* rows did not make it.  This tool reads the
filled package again, opens every built container (CPK, or a decrypted ``.EDAT`` that parses as
one), splits PAC members into their ``srwDL_*.bin`` sub-members and looks for the English of
every filled row in the member the row points at.

What "landed" means here: the English is cut at every ``%s`` (a literal placeholder or a control
byte the writers keep in place), each piece is encoded in CP932 and the pieces must appear in
order with at most ``MAX_GAP`` bytes between them.  Rows without a container (the ``08``
dictionary names) may land in any container; rows whose English is too short to be looked
for (the shortest rehearsal markers) are counted apart, not as missing.

Rows that share a member and an English are looked for together, and the number of hits they
need is the number of *physical* strings behind them, as far as the package shows it:

* the ``04`` offset rows of the item/skill tables describe the same fields as the ``02``/``03``
  record rows (the record writer merges them into one edit), so a group needs
  ``max(record rows, offset rows)`` hits, not their sum;
* in the pointer-pool members of :mod:`table_write` one string may serve several records and
  the writer rewrites every matching run at once - one hit there means the group landed.

Everything else (event records, battle quotes, name cells, slots) needs one hit per row.

Usage::

    python3 tools/patch_spot_check.py --package local/scale_pkg --built local/scale_patch
        [--containers config00.cpk ...] [--report local/scale_patch/spot_check.json]
        [--out local/scale_patch/missing.txt]

Read-only: nothing under ``--built`` or ``--package`` is modified.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import configst_pack as CSP   # noqa: E402
import cpk_write              # noqa: E402
import item_skill_write as ISW  # noqa: E402
import table_write as TW      # noqa: E402

PACKAGE_FILES = ("00_dialogue.jsonl", "01_battle_quotes.jsonl", "02_items.jsonl", "03_skills.jsonl",
                 "04_config_text.jsonl", "05_mission_text.jsonl", "07_names_characters.jsonl",
                 "08_names_units_weapons.jsonl")
MAX_GAP = 8          # bytes allowed between two consecutive pieces (a %s literal is 2, a control 1)
MIN_CHARS = 3        # shorter English is not looked for - too many accidental hits


class SpotError(Exception):
    pass


# --------------------------------------------------------------------------- containers

def member_bodies(path: Path) -> List[Tuple[str, bytes]]:
    """``[(member name, body bytes)]`` of one built container, PAC members split into subs.

    A ``.pac`` that does not parse (the mesbtl quote packs: 16 zero bytes, then ``EDAT``) or
    parses to zero subs is kept whole under its own name - the body is still searchable.
    """
    cpk = cpk_write.load(path)
    out: List[Tuple[str, bytes]] = []
    for member in cpk.members:
        body = cpk_write.decompressed(member.blob)
        if member.name.lower().endswith(".pac"):
            subs: List[dict] = []
            try:
                subs = CSP.parse_pac(body)["subs"]
            except Exception:
                subs = []
            if subs:
                out.extend((sub["name"], sub["data"]) for sub in subs)
                continue
        out.append((member.name, body))
    return out


def find_containers(built: Path, names: Optional[Iterable[str]] = None) -> Dict[str, Path]:
    """Container files under ``built`` (any depth) by name; optionally only the given names."""
    wanted = set(names) if names is not None else None
    found: Dict[str, Path] = OrderedDict()
    for path in sorted(built.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in (".cpk", ".edat"):
            continue
        if wanted is not None and path.name not in wanted:
            continue
        found.setdefault(path.name, path)
    return found


# --------------------------------------------------------------------------- the search

def pieces_of(en: str) -> List[bytes]:
    """The CP932 pieces of an English text, cut at every ``%s``; empty pieces are dropped."""
    out: List[bytes] = []
    for piece in en.split("%s"):
        if piece:
            out.append(piece.encode("cp932", "replace"))
    return out


def count_sequence(body: bytes, pieces: Sequence[bytes], max_gap: int = MAX_GAP) -> int:
    """How many times the pieces appear in order (gaps <= max_gap), without overlapping."""
    if not pieces:
        return 0
    count = 0
    pos = 0
    first = pieces[0]
    while True:
        start = body.find(first, pos)
        if start < 0:
            return count
        cursor = start + len(first)
        ok = True
        for piece in pieces[1:]:
            nxt = body.find(piece, cursor, cursor + max_gap + len(piece))
            if nxt < 0:
                ok = False
                break
            cursor = nxt + len(piece)
        if ok:
            count += 1
            pos = cursor
        else:
            pos = start + 1


def read_rows(package: Path) -> List[dict]:
    rows: List[dict] = []
    for name in PACKAGE_FILES:
        path = package / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            row["__file"] = name
            rows.append(row)
    return rows


def filled(row: dict) -> bool:
    return bool((row.get("en") or "").strip())


def is_offset_row(row: dict) -> bool:
    """A ``04`` string-offset row (``part='text'``, no record index) - see item_skill_write."""
    source = row.get("source") or {}
    return (row.get("part") == "text" and row.get("record") is None
            and ISW._record_from_id(row.get("id")) is None
            and isinstance(source.get("offset"), int))


def required_hits(rows: Sequence[dict], member: str) -> int:
    """How many occurrences of one English a group of rows needs (see the module docstring)."""
    if member and TW.family_of(member) is not None:
        return 1
    offsets = sum(1 for r in rows if is_offset_row(r))
    structured = len(rows) - offsets
    if offsets and structured:
        return max(offsets, structured)
    return len(rows)


def check(package: Path, built: Path, containers: Optional[Iterable[str]] = None,
          max_gap: int = MAX_GAP) -> dict:
    """The spot-check report for a filled package against a built tree."""
    package = Path(package)
    built = Path(built)
    if not package.is_dir():
        raise SpotError(f"package folder not found: {package}")
    if not built.is_dir():
        raise SpotError(f"built folder not found: {built}")
    rows = [r for r in read_rows(package) if filled(r)]
    paths = find_containers(built, containers)
    if not paths:
        raise SpotError(f"no containers under {built}")
    bodies: Dict[str, List[Tuple[str, bytes]]] = OrderedDict()
    for name, path in paths.items():
        bodies[name] = member_bodies(path)

    report: dict = {"package": str(package), "built": str(built), "max_gap": max_gap,
                    "containers": {name: {"rows": 0, "landed": 0, "missing": 0, "short": 0,
                                          "members": len(members)}
                                   for name, members in bodies.items()},
                    "containerless": {"rows": 0, "landed": 0, "missing": 0, "short": 0},
                    "rows_filled": len(rows), "rows_checked": 0, "landed": 0, "missing": 0,
                    "short": 0, "not_built": 0, "missing_ids": [], "short_ids": [],
                    "per_file": {}}

    # rows sharing a member and an English are looked for together: n rows need n hits
    groups: "OrderedDict[tuple, List[dict]]" = OrderedDict()
    for row in rows:
        source = row.get("source") or {}
        container = source.get("container")
        if container is not None and container not in bodies:
            report["not_built"] += 1          # a container that was not part of this build
            continue
        key = (container, source.get("member") or "", row["en"])
        groups.setdefault(key, []).append(row)

    def account(bucket: dict, which: str, n: int = 1) -> None:
        bucket[which] += n
        if which in ("landed", "missing", "short"):
            report[which] += n

    for (container, member, en), members in groups.items():
        bucket = report["containers"][container] if container is not None else report["containerless"]
        per = [report["per_file"].setdefault(r["__file"], {"rows": 0, "landed": 0, "missing": 0,
                                                             "short": 0}) for r in members]
        account(bucket, "rows", len(members))
        report["rows_checked"] += len(members)
        for p in per:
            p["rows"] += 1
        pieces = pieces_of(en)
        if sum(len(p) for p in pieces) < MIN_CHARS:
            account(bucket, "short", len(members))
            for p in per:
                p["short"] += 1
            report["short_ids"].extend(r["id"] for r in members)
            continue
        if container is not None:
            scopes = [(container, name, body) for name, body in bodies[container]]
        else:
            scopes = [(c, name, body) for c, mem in bodies.items() for name, body in mem]
        matching = [s for s in scopes if TW.member_matches(member, s[1])] if member else []
        if not matching:
            matching = scopes             # no member named (or none such): any member counts
        hits = sum(count_sequence(body, pieces, max_gap) for _c, _n, body in matching)
        needed = required_hits(members, member)
        if hits >= needed:
            landed = len(members)
        else:
            # not enough occurrences: the shortfall is reported row by row, from the end of
            # the group (which of the rows is the one missing cannot be told from bytes)
            landed = max(0, len(members) - (needed - hits))
        account(bucket, "landed", landed)
        account(bucket, "missing", len(members) - landed)
        for i, p in enumerate(per):
            p["landed" if i < landed else "missing"] += 1
        for r in members[landed:]:
            note = "" if len(members) == 1 else f"  [group of {len(members)}: {hits}/{needed} hits]"
            report["missing_ids"].append(r["id"] + note)
    return report


def write_missing(report: dict, path: Path) -> None:
    lines = [f"# missing rows of {report['package']} in {report['built']}: {report['missing']}"]
    lines.extend(report["missing_ids"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, required=True, help="the filled package folder")
    parser.add_argument("--built", type=Path, required=True,
                        help="the build output (containers at any depth, e.g. DLC/)")
    parser.add_argument("--containers", nargs="*", default=None,
                        help="only these container names")
    parser.add_argument("--report", type=Path, default=None,
                        help="where the JSON report goes (default: <built>/spot_check.json)")
    parser.add_argument("--out", type=Path, default=None,
                        help="text file with every missing row id")
    parser.add_argument("--max-gap", type=int, default=MAX_GAP)
    args = parser.parse_args(argv)
    try:
        report = check(args.package, args.built, args.containers, args.max_gap)
    except SpotError as error:
        print(f"błąd: {error}")
        return 2
    target = args.report or (args.built / "spot_check.json")
    target.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.out:
        write_missing(report, args.out)
    print(f"wiersze z EN: {report['rows_filled']}; sprawdzone: {report['rows_checked']}; "
          f"trafione: {report['landed']}; brak: {report['missing']}; za krótkie: {report['short']}"
          + (f"; poza buildem: {report['not_built']}" if report["not_built"] else ""))
    for name, bucket in report["containers"].items():
        print(f"  {name}: {bucket['landed']}/{bucket['rows']} trafionych, brak {bucket['missing']}"
              + (f", za krótkie {bucket['short']}" if bucket["short"] else ""))
    cl = report["containerless"]
    if cl["rows"]:
        print(f"  (bez kontenera): {cl['landed']}/{cl['rows']} trafionych, brak {cl['missing']}")
    print(f"raport: {target}" + (f"; lista braków: {args.out}" if args.out else ""))
    return 1 if report["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
