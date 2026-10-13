#!/usr/bin/env python3
"""Write translated battle quotes from the package into a ``mesbtl`` container.

The battle-quote containers (``mesbtl00.cpk`` from the disc, ``mesbtl01-31.EDAT`` from the DLC,
all of them CPK tables once decrypted) hold one ``p<speaker key>.pac`` member per speaker.  Each
pac is CRILAYLA-compressed at rest; decompressed it is a pac header followed by one ``EDAT``
header whose ``EVNT`` sections hold the quote records -- the same record family the story
dialogue uses (type ``0xC9``, text at record + 20), measured on mesbtl00.cpk/p0050.pac:

* every package row of ``01_battle_quotes.jsonl`` lands exactly on a ``0xC9`` record of the
  decompressed member (8660/8660 rows of mesbtl00 verified, text byte-identical),
* the EDAT size field of a pac sits at ``edat + 4`` (not at 4 -- a pac header sits in front) and
  holds the sum of the EVNT section sizes, growing by the same delta as the record,
* the pac header in front of the EDAT holds no offsets into the sections (scanned: no u32 of the
  header equals any section offset), so growth inside the EDAT never invalidates it.

The changed member is written back *stored* (``FileSize == ExtractSize``), which ``cpk_write``
documents as legal and which is what the working Korean patch did; untouched members keep their
original bytes and compression.  The empty-record pacs (``p0995``/``p0996``) and the placeholder
containers (``mesbtl09``, ``mesbtl16-18``, ``mesbtl20-31``) carry no rows and are never rebuilt.

Rows with an empty ``en`` are skipped, so a partially translated package leaves every
untranslated quote byte-identical.

Usage::

    python3 tools/quotes_apply.py --container ../google_drive/mesbtl00.cpk \
        --package local/translation --out local/patched/mesbtl00.cpk
    python3 tools/quotes_apply.py --container ../google_drive/mesbtl00.cpk --identity
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_write                    # noqa: E402
import crilayla                     # noqa: E402
import event_text_apply as ETA      # noqa: E402

PACKAGE_FILE = "01_battle_quotes.jsonl"


def decompressed(raw: bytes) -> bytes:
    """The member body the writer works on: CRILAYLA decoded when compressed, else the raw bytes."""
    if crilayla.is_crilayla(raw):
        return crilayla.decompress(raw).data
    return raw


def rows_for_container(package: Path, container: str) -> Dict[str, List[dict]]:
    """``{member: [rows]}`` of every package row of this container that carries English."""
    path = Path(package) / PACKAGE_FILE
    by_member: Dict[str, List[dict]] = {}
    if not path.exists():
        return by_member
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        source = row.get("source") or {}
        if source.get("container") != container:
            continue
        if not (row.get("en") or "").strip():
            continue          # partial mode: an untranslated quote stays byte-identical
        by_member.setdefault(source.get("member") or "", []).append(row)
    return by_member


def apply_member(raw: bytes, rows: List[dict]) -> tuple:
    """Apply rows to one pac.  Returns ``(new body, was compressed, report)``."""
    blob = decompressed(raw)
    modified, report = ETA.apply_member(blob, rows)
    report["bytes"] = len(modified) - len(blob)
    return modified, crilayla.is_crilayla(raw), report


def apply_container(src: Path, dst: Path, rows_by_member: Dict[str, List[dict]],
                    dry_run: bool = False) -> dict:
    """Rebuild the container with every translated pac, member by member.

    Each rebuild writes one changed member stored and carries the others along untouched; the
    result of one step is the input of the next, so a container with many translated speakers is
    rebuilt exactly once per changed member, each step verified by the writer itself.
    """
    summary = {"container": src.name, "members": 0, "applied": 0, "skipped": 0, "refused": 0,
               "problems": [], "per_member": {}, "written": None, "dry_run": dry_run}
    cpk = cpk_write.load(src)
    have = {m.name for m in cpk.members}
    current = src
    produced = False
    for member in sorted(rows_by_member):
        rows = rows_by_member[member]
        if member not in have:
            summary["problems"].append(f"{member}: not a member of {src.name}")
            continue
        raw = next(m.blob for m in cpk_write.load(current).members if m.name == member)
        body, was_compressed, report = apply_member(raw, rows)
        entry = {"rows": len(rows), "applied": report["applied"],
                 "skipped": len(report["skipped"]), "refused": len(report["refused"]),
                 "was_compressed": was_compressed, "bytes": report["bytes"]}
        summary["members"] += 1
        summary["applied"] += report["applied"]
        summary["skipped"] += len(report["skipped"])
        summary["refused"] += len(report["refused"])
        for message in report["skipped"][:5]:
            summary["problems"].append(f"{member}: skipped: {message}")
        for message in report["refused"][:5]:
            summary["problems"].append(f"{member}: refused: {message}")
        for message in report["problems"]:
            summary["problems"].append(f"{member}: {message}")
        summary["per_member"][member] = entry
        if report["problems"] or dry_run or not report["changed"]:
            continue
        cpk_now = cpk_write.load(current)
        out = cpk_write.rebuild(cpk_now, (member, body))
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(out)
        produced = True
        current = dst
        entry["written_stored"] = True
    if produced and not dry_run:
        summary["written"] = str(dst)
        summary["container_bytes"] = dst.stat().st_size - src.stat().st_size
    return summary


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--package", type=Path, default=Path("local/translation"))
    parser.add_argument("--out", type=Path, help="where to write the rebuilt container")
    parser.add_argument("--identity", action="store_true",
                        help="rebuild the container unchanged and compare with the original")
    parser.add_argument("--dry-run", action="store_true",
                        help="run every writer check but write nothing")
    args = parser.parse_args(argv)

    if args.identity:
        ok, message = cpk_write.verify_identity(args.container)
        print(("IDENTITY OK: " if ok else "IDENTITY FAILED: ") + message)
        return 0 if ok else 1

    rows_by_member = rows_for_container(args.package, args.container.name)
    if not rows_by_member:
        print(json.dumps({"container": args.container.name, "members": 0, "applied": 0,
                          "note": "no translated rows for this container"}, ensure_ascii=False))
        return 0
    if not args.out and not args.dry_run:
        parser.error("--out is needed unless --identity or --dry-run is given")
    summary = apply_container(args.container, args.out or args.container, rows_by_member,
                              dry_run=args.dry_run)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 1 if summary["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
