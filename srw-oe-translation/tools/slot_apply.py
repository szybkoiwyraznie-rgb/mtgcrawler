#!/usr/bin/env python3
"""Write translated text into fixed slots in place - the writer for everything that cannot grow.

The package marks such rows ``mode: slot`` and gives each one its budget: ``max_bytes`` is the
room the game measured for the string (the slot span for the mission/BGM/map tables, the
distance to the next string for the leftover scan).  This writer takes rows at their word:

* the row's offset lands inside one NUL-delimited span of the member, and the row's ``jp`` must
  read back from that span (in the file's own form or in the ``%s`` display form -
  :func:`table_write.match_form` decides, so control tokens are put back byte for byte);
* the translation must fit: ``len(bytes) + 1 <= max_bytes`` (a row without ``max_bytes`` gets
  the span itself as the budget, which is the strictest honest reading);
* the budget area behind the span must be clean zero padding - a slot whose declared room is
  taken by other bytes is refused, not overwritten;
* the write is in place: the span becomes ``translation + NUL padding``, the member never
  changes size, and the verification re-reads the result and diffs everything outside the
  written spans against the original.

Rows this writer owns in the full build: the ``05`` slot tables of the config and event
containers (mission notes and titles, BGM titles, map/background/group names), the leftover
slot rows of ``04`` (``srwDL_CalcType``, ``srwDL_Map_S``, the charalist cell), and the
tail-pool rows of the convention-B members that :mod:`item_skill_write` refuses to resize
(the mixed binary/text tails of ``srwDL_Skill00`` and friends).

Fail-closed like every writer here: a refused row is reported with its reason and the member is
left byte-identical when anything about the result does not verify.

Usage::

    python3 tools/slot_apply.py --container ../google_drive/config00.cpk \
        --package local/translation --out local/patched/config00.cpk
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP   # noqa: E402
import cpk_write              # noqa: E402
import inline_names as IN     # noqa: E402
import table_write as TW      # noqa: E402

#: package files whose slot-mode rows this writer applies
PACKAGE_FILES = ("04_config_text.jsonl", "05_mission_text.jsonl")


def span_around(data: bytes, offset: int) -> Tuple[int, bytes]:
    """(start, bytes) of the NUL-delimited span the offset sits in."""
    start = data.rfind(b"\x00", 0, offset) + 1
    end = data.find(b"\x00", offset)
    return start, data[start:end if end >= 0 else len(data)]


def pool_spans(data: bytes, start: int) -> List[Tuple[int, bytes]]:
    """(start, bytes) of every NUL-delimited run at or after ``start``."""
    out: List[Tuple[int, bytes]] = []
    i = max(0, start)
    n = len(data)
    while i < n:
        j = i
        while j < n and data[j]:
            j += 1
        if j > i:
            out.append((i, data[i:j]))
        i = j + 1
    return out


def apply_member(blob: bytes, rows: Iterable[dict], member: str = "",
                 pool: bool = False) -> Tuple[bytes, dict]:
    """Write every fitting row in place.  Returns (bytes, report).

    ``pool=True`` is the tail-pool pass of the orchestrator: the package marks every string of
    a convention-B tail pool with the pool's *start* offset (one id for the whole pool), so a
    pool row is looked up by content among the NUL-delimited runs at or after that offset and
    every occurrence is written in place (the pool holds duplicate runs and any of them can be
    the one the game reads).  In-place means same size or shorter: the pool is copied verbatim
    by the record rebuild and its strings sit back to back, so a longer translation is refused
    and the string stays Japanese.
    """
    report = {"member": member, "applied": 0, "refused": [], "problems": [], "bytes": 0,
              "regions": []}
    out = bytearray(blob)
    planned: Dict[int, Tuple[bytes, str]] = {}      # span start -> (value, row id)
    spans_cache: Dict[int, List[Tuple[int, bytes]]] = {}
    for row in rows:
        row_id = row.get("id")
        source = row.get("source") or {}
        offset = source.get("offset")
        en = (row.get("en") or "").strip()
        if not en:
            continue
        if not isinstance(offset, int):
            report["refused"].append(f"{row_id}: no byte offset")
            continue
        start, span = span_around(blob, offset)
        targets: List[Tuple[int, bytes, Optional[str]]] = []
        if pool:
            # every occurrence of the row's string in the pool gets the same English: the
            # pool holds duplicate runs and any of them can be the one the game reads
            runs = spans_cache.get(offset)
            if runs is None:
                runs = spans_cache[offset] = pool_spans(blob, offset)
            for run_start, run in runs:
                run_form = TW.match_form(row.get("jp"), run)
                if run_form is not None:
                    targets.append((run_start, run, run_form))
            if not targets:
                report["refused"].append(f"{row_id}: jp not found in the pool at {offset}")
                continue
        else:
            form = TW.match_form(row.get("jp"), span) if span else None
            if form is None:
                if not span:
                    report["refused"].append(
                        f"{row_id}: the offset {offset} sits on an empty span")
                else:
                    report["refused"].append(
                        f"{row_id}: jp does not match the span at {start}")
                continue
            targets.append((start, span, form))
        for start, span, form in targets:
            try:
                value = TW.encode_en(en, span, form)
            except TW.TableError as exc:
                report["refused"].append(f"{row_id}: {exc}")
                continue
            budget = int(row.get("max_bytes") or 0) or (len(span) + 1)
            if len(value) + 1 > budget:
                report["refused"].append(
                    f"{row_id}: {len(value)} bytes + NUL do not fit the {budget}-byte budget")
                continue
            # only the bytes the write newly occupies behind the original span must be clean
            # padding; the rest of the budget area is never touched
            if any(blob[start + len(span):start + len(value)]):
                report["refused"].append(
                    f"{row_id}: the growth area behind the span is not clean padding")
                continue
            previous = planned.get(start)
            if previous is not None:
                if previous[0] != value:
                    report["refused"].append(
                        f"{row_id}: conflicts with {previous[1]} on the span at {start}")
                    planned[start] = (b"", "__conflict__")
                continue
            planned[start] = (value, row_id)
    written: List[Tuple[int, int]] = []
    for start, (value, row_id) in sorted(planned.items()):
        if row_id == "__conflict__":
            continue
        _span_start, span = span_around(blob, start)
        budget_end = start + len(value)
        # pad to the end of the original span, so a shorter translation leaves zeros, not
        # leftovers of the Japanese text
        end = max(budget_end, start + len(span))
        out[start:end] = value + b"\x00" * (end - start - len(value))
        written.append((start, end))
        report["applied"] += 1
    if not written:
        return blob, report
    modified = bytes(out)
    report["regions"] = written
    report["problems"] = verify(blob, modified, written)
    report["bytes"] = len(modified) - len(blob)
    if report["problems"]:
        return blob, report
    return modified, report


def verify(original: bytes, modified: bytes, written: List[Tuple[int, int]]) -> List[str]:
    """Same size, changes only inside the written spans, and no text lost outside them."""
    problems: List[str] = []
    if len(original) != len(modified):
        return ["the member changed size"]
    mask = bytearray(len(original))
    for start, end in written:
        mask[start:end] = b"\x01" * (end - start)
    for i, (a, b) in enumerate(zip(original, modified)):
        if a != b and not mask[i]:
            problems.append(f"byte {i} changed outside a written span")
            break
    return problems


def rows_for_container(package: Path, container: str, members: Optional[Iterable[str]] = None,
                       slot_only: bool = True) -> List[dict]:
    """Slot rows of one container that carry English.

    ``slot_only`` keeps the rows the package measured a budget for; the orchestrator passes
    ``slot_only=False`` for the tail-pool rows of the convention-B members, which are grow-mode
    rows the record writer refused to resize.
    """
    wanted = set(members) if members is not None else None
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
            if source.get("container") != container:
                continue
            if wanted is not None and source.get("member") not in wanted:
                continue
            if not (row.get("en") or "").strip():
                continue
            if slot_only and row.get("mode") != "slot":
                continue
            rows.append(row)
    return rows


def apply_container(src: Path, dst: Path, rows: List[dict], dry_run: bool = False,
                    pool: bool = False) -> dict:
    """Rebuild the container with every translated slot member, chained through ``dst``.

    ``pool=True`` switches every member to the tail-pool content lookup of
    :func:`apply_member` (the orchestrator's ``tail-slots`` pass).
    """
    summary = {"container": src.name, "members": 0, "applied": 0, "refused": 0,
               "problems": [], "per_member": {}, "written": None, "dry_run": dry_run}
    by_member: Dict[str, List[dict]] = {}
    for row in rows:
        by_member.setdefault((row.get("source") or {}).get("member") or "", []).append(row)
    current = src
    produced = False
    cpk = cpk_write.load(src)
    have = {m.name for m in cpk.members}
    for member in cpk.members:
        targets: List[Tuple[str, bytes]] = []
        if member.name.lower().endswith(".pac"):
            pac = CSP.parse_pac(cpk_write.decompressed(member.blob))
            changed = False
            for sub in pac["subs"]:
                mine = by_member.get(sub["name"])
                if not mine:
                    continue
                blob, report = _apply(sub["name"], sub["data"], mine, summary, pool)
                if report and report["applied"] and not report["problems"]:
                    sub["data"] = blob
                    changed = True
            if changed:
                targets.append((member.name, CSP.rebuild_pac(pac)))
        else:
            mine = by_member.get(member.name)
            if mine:
                blob, report = _apply(member.name, cpk_write.decompressed(member.blob),
                                      mine, summary, pool)
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
    for name in by_member:
        if name not in have and not any(name == m for m in have):
            # a pac subfile name is fine; anything else the container does not hold at all
            found = False
            for member in cpk.members:
                if member.name.lower().endswith(".pac"):
                    if any(s["name"] == name for s in
                           CSP.parse_pac(cpk_write.decompressed(member.blob))["subs"]):
                        found = True
                        break
            if not found:
                summary["problems"].append(f"{name}: not a member of {src.name}")
    if produced and not dry_run:
        summary["written"] = str(dst)
        summary["container_bytes"] = dst.stat().st_size - src.stat().st_size
    return summary


def _apply(sub_name: str, data: bytes, rows: List[dict], summary: dict,
           pool: bool = False):
    blob, report = apply_member(data, rows, sub_name, pool=pool)
    summary["members"] += 1
    summary["applied"] += report["applied"]
    summary["refused"] += len(report["refused"])
    summary["problems"].extend(f"{sub_name}: {m}" for m in report["problems"])
    for line in report["refused"][:8]:
        summary["problems"].append(f"{sub_name}: refused: {line}")
    summary["per_member"][sub_name] = {"applied": report["applied"],
                                       "refused": len(report["refused"])}
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
