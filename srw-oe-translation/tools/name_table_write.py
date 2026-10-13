#!/usr/bin/env python3
"""Write translated names into the fixed-stride name tables (charalist, unit_list, wp_list).

These three members are arrays of fixed-size records with the names in fixed cells, measured on
config00.cpk and config01.EDAT (the longest strings found anywhere in the game fit the cells):

    charalist<NN>.bin   172-byte records, key u16 @ +96
                        name_short  @ +0   cell 32 (text <= 31, longest in game: 20)
                        name_full   @ +32  cell 44 (text <= 43, longest in game: 32)
                        name_narrow @ +76  cell 20 (text <= 19, longest in game: 14)
    unit_list<NN>.bin   384-byte records, key u16 @ +84
                        name        @ +0   cell 64 (text <= 63, longest in game: 46)
                        name_display@ +140 cell 64 (text <= 63, longest in game: 42)
    wp_list<NN>.bin     offset table (u32 first_offset @ +4), one variable record per unit:
                        unit_id u32 @ +0, weapon count u32 @ +4, then count x 256-byte weapon
                        entries from +12; in each entry:
                        name        @ +32  cell 64 (text <= 63, longest in game: 48)
                        name_short  @ +96  cell 32 (text <= 31, longest in game: 25)

Growing a cell would move every following record and nothing points at these tables by offset
from the outside, but the cells are the layout the game's UI measures against - so the rule here
is the slot rule: a translation that fits the cell is written in place (NUL + zero padding, the
member never changes size), a translation that does not fit is refused and reported, never
truncated.  The ``mode: grow`` label these rows carry in the package describes the wish, not the
bytes; this writer applies what the bytes allow (see docs/COVERAGE.md).

Row addressing is the ``07``/``08`` one: ``key`` + ``part``.  Weapon rows also carry the weapon
index in ``source.offset`` (a string).  The ``jp`` of a row is checked before anything is
written, in the three forms the exporters used: the file's own bytes, the voiced-kana mapped
form of the weapon short names (``0x0F xx`` tokens rendered as their kana), and the ``%s``
display form.  A mapped-form English loses the kana tokens - the cell keeps what fits, and the
loss is reported per row so it is a number, not a surprise.

Usage::

    python3 tools/name_table_write.py --container ../google_drive/config00.cpk \
        --package local/translation --out local/patched/config00.cpk
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP   # noqa: E402
import cpk_write              # noqa: E402
import inline_names as IN     # noqa: E402
import speaker_map as SM      # noqa: E402
import table_write as TW      # noqa: E402
import unit_weapons as UW     # noqa: E402

PACKAGE_FILES = ("07_names_characters.jsonl", "08_names_units_weapons.jsonl")


class NameTableError(ValueError):
    pass


#: family -> how the member is cut into records and where the cells live
SPECS: Dict[str, dict] = {
    "charalist": {"cells": {"name_short": (0, 32), "name_full": (32, 44),
                            "name_narrow": (76, 20)},
                  "key": ("u16", 96)},
    "unit_list": {"cells": {"name": (0, 64), "name_display": (140, 64)},
                  "key": ("u16", 84)},
    "wp_list": {"cells": {"name": (32, 64), "name_short": (96, 32)},
                "key": ("u32", 0), "header": 12, "entry": 256},
}


def family_of(member: str) -> Optional[str]:
    for family in SPECS:
        if member.startswith(family):
            return family
    return None


def cstring(blob: bytes, start: int, width: int) -> bytes:
    return blob[start:start + width].split(b"\x00", 1)[0]


def record_starts(blob: bytes, family: str) -> List[Tuple[int, int]]:
    """(start, end) of every record of the member."""
    spec = SPECS[family]
    if family == "wp_list":
        offs = IN.record_offsets(blob)
        if not offs:
            raise NameTableError("wp_list without a readable offset table")
        return list(zip(offs, offs[1:] + [len(blob)]))
    stride = {"charalist": 172, "unit_list": 384}[family]
    if len(blob) % stride:
        raise NameTableError(f"{family}: member size {len(blob)} is not a multiple of {stride}")
    n = len(blob) // stride
    return [(i * stride, (i + 1) * stride) for i in range(n)]


def record_key(blob: bytes, start: int, family: str) -> Optional[int]:
    kind, off = SPECS[family]["key"]
    size = 2 if kind == "u16" else 4
    return int.from_bytes(blob[start + off:start + off + size], "little")


def cell_targets(blob: bytes, family: str, start: int, end: int, part: str,
                 index: Optional[int]) -> List[Tuple[int, int]]:
    """(absolute cell start, cell width) of the cell a row part names."""
    off, width = SPECS[family]["cells"][part]
    if family != "wp_list":
        return [(start + off, width)]
    header, entry = SPECS[family]["header"], SPECS[family]["entry"]
    count = struct.unpack_from("<I", blob, start + 4)[0]
    if index is None or not (0 <= index < count):
        raise NameTableError(f"weapon index {index} outside the {count} entries of the unit")
    base = start + header + entry * index
    if base + entry > end:
        raise NameTableError("weapon entry runs past the record")
    return [(base + off, width)]


def match_cell(jp: Optional[str], raw: bytes, mapped_form: bool) -> Optional[str]:
    """Which form the row's jp is in, or None when the cell does not hold this text."""
    if mapped_form:
        text, mapped, _toks, _fully = UW.short_name_forms(raw)
        if jp in (mapped, text):
            return "raw"          # tokens cannot survive an English line; the cell is written
    return TW.match_form(jp, raw)


def apply_member(blob: bytes, member: str, rows: Iterable[dict]) -> Tuple[bytes, dict]:
    """Write every fitting row into its cell.  Returns (bytes, report); nothing moves."""
    family = family_of(member)
    report = {"member": member, "family": family, "applied": 0, "refused": [], "problems": [],
              "token_loss": 0, "bytes": 0}
    if family is None:
        report["problems"].append(f"{member}: not a name table")
        return blob, report
    spans = record_starts(blob, family)
    keys: Dict[int, List[int]] = {}
    for i, (start, _end) in enumerate(spans):
        keys.setdefault(record_key(blob, start, family), []).append(i)
    out = bytearray(blob)
    written: List[Tuple[int, int]] = []
    for row in rows:
        row_id = row.get("id")
        part = row.get("part")
        en = (row.get("en") or "").strip()
        if not en or part not in SPECS[family]["cells"]:
            continue
        try:
            key = int(row.get("key"))
        except (TypeError, ValueError):
            report["refused"].append(f"{row_id}: no numeric key")
            continue
        matches = keys.get(key, [])
        if family == "wp_list":
            matches = [i for i in matches]        # unit ids are unique per member in practice
        if not matches:
            report["refused"].append(f"{row_id}: no record with key {key}")
            continue
        index = None
        source = row.get("source") or {}
        if family == "wp_list":
            try:
                index = int(source.get("offset"))
            except (TypeError, ValueError):
                report["refused"].append(f"{row_id}: weapon rows need their index")
                continue
        for i in matches:
            start, end = spans[i]
            try:
                targets = cell_targets(blob, family, start, end, part, index)
            except NameTableError as exc:
                report["refused"].append(f"{row_id}: {exc}")
                continue
            for cell_start, width in targets:
                raw = cstring(blob, cell_start, width)
                form = match_cell(row.get("jp"), raw, family == "wp_list"
                                  and part == "name_short")
                if form is None:
                    report["refused"].append(
                        f"{row_id}: jp does not match the cell at {cell_start} ({raw[:16]!r})")
                    continue
                try:
                    value = TW.encode_en(en, raw, form)
                except TW.TableError as exc:
                    report["refused"].append(f"{row_id}: {exc}")
                    continue
                if len(value) > width - 1:
                    report["refused"].append(
                        f"{row_id}: {len(value)} bytes do not fit the {width - 1}-byte cell")
                    continue
                if family == "wp_list" and part == "name_short" and b"\x0f" in raw \
                        and b"\x0f" not in value:
                    report["token_loss"] += 1
                out[cell_start:cell_start + width] = value + b"\x00" * (width - len(value))
                written.append((cell_start, width))
                report["applied"] += 1
    if not written:
        return blob, report
    modified = bytes(out)
    report["problems"] = verify(blob, modified, written)
    report["bytes"] = len(modified) - len(blob)
    if report["problems"]:
        return blob, report
    return modified, report


def verify(original: bytes, modified: bytes, written: List[Tuple[int, int]]) -> List[str]:
    """The member keeps its size and only the written cells differ."""
    problems = []
    if len(original) != len(modified):
        problems.append("the member changed size")
        return problems
    mask = bytearray(len(original))
    for start, width in written:
        mask[start:start + width] = b"\x01" * width
    for i, (a, b) in enumerate(zip(original, modified)):
        if a != b and not mask[i]:
            problems.append(f"byte {i} changed outside a written cell")
            break
    return problems


def rows_for_container(package: Path, container: str) -> List[dict]:
    rows: List[dict] = []
    for name in PACKAGE_FILES:
        path = Path(package) / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            source = row.get("source") or {}
            if source.get("container") not in (container, None):
                continue
            if not (row.get("en") or "").strip():
                continue
            if family_of(source.get("member") or "") is None:
                continue
            rows.append(row)
    return rows


def rows_for_member(rows: Iterable[dict], sub_name: str) -> List[dict]:
    """Rows of this member: full name match, or the bare family name of the 07/08 exports."""
    family = family_of(sub_name)
    out = []
    for row in rows:
        member = (row.get("source") or {}).get("member") or ""
        if member == sub_name or member == family:
            out.append(row)
    return out


def apply_container(src: Path, dst: Path, rows: List[dict], dry_run: bool = False) -> dict:
    """Rebuild the container with every translated name table, chained through ``dst``."""
    summary = {"container": src.name, "members": 0, "applied": 0, "refused": 0, "token_loss": 0,
               "problems": [], "per_member": {}, "written": None, "dry_run": dry_run}
    current = src
    produced = False
    for member in cpk_write.load(src).members:
        targets: List[Tuple[str, bytes]] = []
        if member.name.lower().endswith(".pac"):
            pac = CSP.parse_pac(cpk_write.decompressed(member.blob))
            changed = False
            for sub in pac["subs"]:
                mine = rows_for_member(rows, sub["name"])
                if not mine or family_of(sub["name"]) is None:
                    continue
                blob, report = _apply(sub["name"], sub["data"], mine, summary)
                if report and report["applied"] and not report["problems"]:
                    sub["data"] = blob
                    changed = True
            if changed:
                targets.append((member.name, CSP.rebuild_pac(pac)))
        else:
            mine = rows_for_member(rows, member.name)
            if mine and family_of(member.name) is not None:
                blob, report = _apply(member.name, cpk_write.decompressed(member.blob),
                                      mine, summary)
                if report and report["applied"] and not report["problems"]:
                    targets.append((member.name, blob))
        for name, blob in targets:
            if dry_run:
                continue
            out = cpk_write.rebuild(cpk_write.load(current), (name, blob))
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(out)
            produced = True
            current = dst
    if produced and not dry_run:
        summary["written"] = str(dst)
        summary["container_bytes"] = dst.stat().st_size - src.stat().st_size
    return summary


def _apply(sub_name: str, data: bytes, rows: List[dict], summary: dict):
    try:
        blob, report = apply_member(data, sub_name, rows)
    except NameTableError as exc:
        summary["problems"].append(f"{sub_name}: {exc}")
        return None, None
    summary["members"] += 1
    summary["applied"] += report["applied"]
    summary["refused"] += len(report["refused"])
    summary["token_loss"] += report["token_loss"]
    summary["problems"].extend(f"{sub_name}: {m}" for m in report["problems"])
    for line in report["refused"][:8]:
        summary["problems"].append(f"{sub_name}: refused: {line}")
    summary["per_member"][sub_name] = {k: report[k] for k in
                                       ("applied", "token_loss") if k in report}
    summary["per_member"][sub_name]["refused"] = len(report["refused"])
    return blob, report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    rows = rows_for_container(args.package, args.container.name)
    if not args.out and not args.dry_run:
        parser.error("--out is needed unless --dry-run is given")
    summary = apply_container(args.container, args.out or args.container, rows,
                              dry_run=args.dry_run)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 1 if summary["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
