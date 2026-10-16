#!/usr/bin/env python3
"""Write translated text into a fixed-width slot (mission titles, and later the other slot kinds).

Several text kinds are not records with a length field but cells of a fixed stride: a mission title
is 128 bytes with the title at +10, so a translation has to fit the room it was given and is padded
with NULs (measured, see ``mission_text`` and ``docs/EXPERIMENT_LOG.md``).  Growing those cells would
move every following record, which is why the rule here is: fit the slot or refuse the row.

The container path mirrors ``item_skill_write``: CPK -> ``*.pac`` subfile -> slot bytes, rebuilding
the PAC and then the container, and the result is verified by re-reading it and by checking that
nothing outside the written slots changed.

Usage:
    python3 tools/slot_text_apply.py --container X.cpk --kind mission_title --member milstP00.bin \
        --package local/translation --out local/patched/X.cpk [--identity]
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import configst_pack  # noqa: E402
import cpk_write  # noqa: E402
import mission_text  # noqa: E402
import speaker_map as SM  # noqa: E402


class SlotError(ValueError):
    """The row cannot be written as asked (nothing is written when this is raised)."""


def spec_for(kind: str, role: str = "title") -> dict:
    """The measured layout of one slot kind, with the slot offset we write."""
    spec = mission_text.SPECS.get(kind)
    if spec is None:
        raise SlotError(f"no measured layout for kind {kind!r}")
    for position, (offset, name, _size) in enumerate(spec["slots"]):
        if name == role:
            return {"kind": kind, "header": spec["header"], "stride": spec["stride"],
                    "slot": offset, "role": role, "position": position}
    raise SlotError(f"kind {kind!r} has no slot {role!r}")


def records(blob: bytes, spec: dict) -> int:
    stride = spec["stride"] or len(blob)
    return (len(blob) - spec["header"]) // stride


def slot_span(blob: bytes, spec: dict, index: int) -> Tuple[int, int]:
    """(start, end) of the room a slot has: its measured size (``mission_text.SPECS``)."""
    stride = spec["stride"] or len(blob)
    base = spec["header"] + index * stride
    start = base + spec["slot"]
    size = mission_text.slot_span(mission_text.SPECS[spec["kind"]], spec["position"], stride)
    return start, min(start + size, base + stride)


def read_slot(blob: bytes, spec: dict, index: int) -> str:
    stride = spec["stride"] or len(blob)
    base = spec["header"] + index * stride + spec["slot"]
    raw = blob[base:base + stride - spec["slot"]].split(b"\x00", 1)[0]
    try:
        return raw.decode("cp932")
    except UnicodeDecodeError:
        return ""


def write_slots(blob: bytes, spec: dict, edits: Dict[int, str]) -> Tuple[bytes, List[str]]:
    """Put each ``{record index: text}`` into its slot; returns the new blob and the report.

    Raises :class:`SlotError` when a text does not fit or cannot be encoded -- the caller writes
    nothing in that case.  Bytes outside the edited slots are copied verbatim.
    """
    out = bytearray(blob)
    report: List[str] = []
    for index in sorted(edits, reverse=True):
        if index < 0 or index >= records(blob, spec):
            raise SlotError(f"record {index} is outside the file ({records(blob, spec)} records)")
        start, end = slot_span(blob, spec, index)
        try:
            text = edits[index].encode("cp932")
        except UnicodeEncodeError as error:
            raise SlotError(f"record {index}: {error}") from error
        room = end - start
        if len(text) >= room:
            raise SlotError(f"record {index}: the text is {len(text)} bytes, the slot has {room - 1} "
                            f"(one byte stays NUL)")
        out[start:end] = text + b"\x00" * (room - len(text))
        report.append(f"record {index}: {len(text)} bytes into {room - 1}")
    return bytes(out), report


def verify(original: bytes, modified: bytes, spec: dict, edits: Dict[int, str]) -> List[str]:
    """Everything outside the edited slots must be untouched, and the slots must read back."""
    problems: List[str] = []
    if len(original) != len(modified):
        problems.append(f"length changed: {len(original)} -> {len(modified)}")
        return problems
    allowed = bytearray(len(original))
    for index in edits:
        start, end = slot_span(original, spec, index)
        allowed[start:end] = b"\x01" * (end - start)
    for position, (before, after) in enumerate(zip(original, modified)):
        if before != after and not allowed[position]:
            problems.append(f"byte {position} changed outside the slots")
            break
    for index, text in edits.items():
        if read_slot(modified, spec, index) != text:
            problems.append(f"record {index} does not read back as written")
    return problems


def rows_of_package(package: Path, container: str, kind: str) -> List[dict]:
    """Package rows of this kind and container that carry English."""
    rows: List[dict] = []
    for path in sorted(Path(package).glob("05_*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            source = row.get("source") or {}
            if row.get("category") != kind or source.get("container") != container:
                continue
            if (row.get("en") or "").strip():
                rows.append(row)
    return rows


def edits_for_member(blob: bytes, spec: dict, rows: List[dict], member: str) -> Dict[int, str]:
    """``{record index: English}`` for the rows that name this member, by their measured offset."""
    edits: Dict[int, str] = {}
    stride = spec["stride"] or len(blob)
    for row in rows:
        source = row["source"]
        if source.get("member") != member:
            continue
        offset = int(source["offset"])
        # a slot offset is header + i*stride + slot, and nothing else
        if offset < spec["header"] + spec["slot"] \
                or (offset - spec["header"] - spec["slot"]) % stride != 0:
            raise SlotError(f"{row['id']}: offset {offset} is not a {spec['role']} slot of {member}")
        index = (offset - spec["header"] - spec["slot"]) // stride
        if read_slot(blob, spec, index) != (row["jp"] or ""):
            raise SlotError(f"{row['id']}: the slot holds something else than the package says")
        edits[index] = row["en"]
    return edits


def apply_container(src: Path, dst: Path, kind: str, member: str, edits: Dict[int, str],
                    dry_run: bool = False) -> dict:
    """Write the slots of one PAC subfile of one container, then verify by re-reading."""
    spec = spec_for(kind)
    cpk = cpk_write.load(src)
    report: dict = {"container": src.name, "member": member, "kind": kind, "applied": 0,
                    "slots": [], "problems": []}
    replacement = None
    for entry in cpk.members:
        if not entry.name.lower().endswith(".pac"):
            continue
        pac = configst_pack.parse_pac(entry.blob)
        for sub in pac["subs"]:
            if sub["name"] != member:
                continue
            modified, slot_report = write_slots(sub["data"], spec, edits)
            report["problems"] = verify(sub["data"], modified, spec, edits)
            if report["problems"]:
                raise SlotError("; ".join(report["problems"]))
            report["slots"] = slot_report
            report["applied"] = len(edits)
            report["member_bytes"] = len(sub["data"])
            report["member_delta"] = len(modified) - len(sub["data"])
            sub["data"] = modified
            replacement = (entry.name, configst_pack.rebuild_pac(pac))
        if replacement is not None:
            break
    if replacement is None:
        raise SlotError(f"{src.name} holds no PAC subfile named {member!r}")
    if dry_run:
        return report
    out = cpk_write.rebuild(cpk, replacement=replacement)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(out)
    report["written"] = str(dst)
    report["container_delta"] = dst.stat().st_size - src.stat().st_size
    # re-read the container we just wrote: the slots must say what we put there
    again = cpk_write.load(dst)
    for entry in again.members:
        if not entry.name.lower().endswith(".pac"):
            continue
        pac = configst_pack.parse_pac(entry.blob)
        for sub in pac["subs"]:
            if sub["name"] != member:
                continue
            for index, text in edits.items():
                if read_slot(sub["data"], spec_for(kind), index) != text:
                    raise SlotError(f"re-read after writing: record {index} does not match")
            report["verified"] = True
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--kind", default="mission_title")
    parser.add_argument("--member", help="PAC subfile name, e.g. milstP00.bin "
                                         "(only needed together with --package)")
    parser.add_argument("--package", type=Path, help="package folder to take the English from")
    parser.add_argument("--out", type=Path, help="write the patched container here")
    parser.add_argument("--identity", action="store_true",
                        help="rebuild without changes and require the file back byte for byte")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass

    if args.identity:
        cpk = cpk_write.load(args.container)
        original = args.container.read_bytes()
        rebuilt = cpk_write.rebuild(cpk, None)
        if rebuilt != original:
            print(f"IDENTITY FAILED: {len(rebuilt)} bytes rebuilt, {len(original)} original")
            return 1
        print(f"IDENTITY OK: {len(original)} bytes identical")
        return 0

    if args.package is None or args.out is None:
        print("--package and --out are required unless --identity is used")
        return 2
    rows = rows_of_package(args.package, args.container.name, args.kind)
    if not rows:
        print(f"no filled {args.kind} rows for {args.container.name} in {args.package}")
        return 2
    try:
        # the edits are planned against the file itself, so the package only says what to write
        cpk = cpk_write.load(args.container)
        blob = None
        for entry in cpk.members:
            if entry.name.lower().endswith(".pac"):
                for sub in configst_pack.parse_pac(entry.blob)["subs"]:
                    if sub["name"] == args.member:
                        blob = sub["data"]
        if blob is None:
            raise SlotError(f"{args.container.name} holds no PAC subfile named {args.member!r}")
        spec = spec_for(args.kind)
        edits = edits_for_member(blob, spec, rows, args.member)
        report = apply_container(args.container, args.out, args.kind, args.member, edits,
                                 args.dry_run)
    except SlotError as error:
        print(f"PRZERWANE: {error}")
        return 1
    print(json.dumps({key: report[key] for key in
                      ("container", "member", "kind", "applied", "member_delta", "container_delta")
                      if key in report}, ensure_ascii=False))
    for line in report["slots"]:
        print("  " + line)
    if report.get("written"):
        print(f"zapisane: {report['written']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
