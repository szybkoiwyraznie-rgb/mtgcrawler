#!/usr/bin/env python3
"""Inventory of every member (and every PAC subfile) of every local container, with its reader.

Purpose (audit, COVERAGE): prove which pieces of the game data the project already reads and
which ones no reader touches yet.  Findings so far [ZWERYFIKOWANE 2026-10-12]:

* the disc-side packages (``system``, ``tacsys``, ``tactics``, ``taclevup``, ``mesbmp00``) use the
  "ITOC blob" CPK layout (entries carry no offsets), so they are read through
  ``speaker_map.member_offsets`` (sequential, 2048-aligned) - the only rule that closes the byte
  budget;
* the text readers match **PAC subfile names**, not container member names: ``config00.pac``
  alone holds 34 subfiles (``bg2dlist.bin`` ... ``unit_index_list.bin``), and only some of them
  have a reader.  Measuring at member level alone therefore hides both coverage and gaps, so the
  inventory walks both levels.

Game data stays out of the repository: the JSON/TSV output belongs under the ignored ``local/``
folder.

Usage:
    python tools/member_inventory.py --dir ../google_drive --out local/member_inventory.json \
        [--tsv local/member_inventory.tsv]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_table  # noqa: E402
import crilayla  # noqa: E402
import inline_names as IN  # noqa: E402
import speaker_map as SM  # noqa: E402

CONTAINER_SUFFIXES = (".cpk", ".edat")

# Reader -> the JSON files that carry its ``member -> container`` map.  The names in those maps
# are container members for the loose-text containers and PAC subfiles for the ``config*.pac``
# ones, so one flat name set covers both levels.
# Reader outputs that name the files they consumed.  Every JSON under the output folder is
# walked (keys and string values alike) and any game file name it mentions claims that file for
# the output's own name - so a new reader is covered as soon as it writes its summary.
READER_OUTPUTS = (
    "local/text_tables/summary.json",
    "local/item_skill_summary.json",
    "local/charalist.json",
    "local/units",
    "local/name_map.json",
)
OUTPUT_STEMS = {
    "text_tables/summary": "text_tables",
    "text_tables": "text_tables",
    "item_skill_summary": "item_skill",
    "charalist": "charalist_table",
    "units": "unit_records",
    "name_map": "name_map",
}

MARKER_READERS = (
    ("chara_dictionary", "CharaDictionary"),
    ("robo_dictionary", "RoboDictionary"),
    ("mission_notes", "_ext.dat"),
)


def containers(directory: Path) -> List[Path]:
    """Every container file of the directory, sorted by name."""
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in CONTAINER_SUFFIXES)


def member_rows(path: Path) -> Tuple[List[dict], Optional[str]]:
    """[(name, stored, extracted, offset, compressed), ...] plus an error string when unreadable."""
    try:
        data = path.read_bytes()
        table = cpk_table.read_cpk_table(path)
        offsets = SM.member_offsets(path, table)
    except Exception as exc:  # noqa: BLE001 - report, never hide a file
        return [], f"{type(exc).__name__}: {exc}"
    rows = []
    for entry, offset in zip(table["entries"], offsets):
        raw = data[offset:offset + entry["file_size"]]
        if entry.get("compressed") or crilayla.is_crilayla(raw):
            try:
                extracted = len(crilayla.decompress(raw).data)
            except Exception:  # noqa: BLE001 - the size is informative, the failure is not fatal
                extracted = entry.get("extract_size")
        else:
            extracted = len(raw)
        rows.append(
            {
                "member": entry["name"],
                "stored": entry["file_size"],
                "extracted": extracted,
                "offset": offset,
                "compressed": bool(entry.get("compressed")),
            }
        )
    return rows, None


def subfile_rows(blob: bytes) -> List[dict]:
    """PAC subfiles of one member; empty when the member is not a PAC index.

    MEASURED 2026-10-12 [ZWERYFIKOWANE]: every ``.pac`` of this game is a PAC *index* (0x28-byte
    entries from 0x10: u32 data offset, u32 size, 0x20-byte ASCII name) - including the ones whose
    name looks like a texture (``r0001/0000_000.pac``, ``IM1000.pac``, ``svicon.pac``). Two index
    shapes exist: the table starts at 0x10 and runs to the offset named in the blob's first word
    (``config00.pac``: 0x800, ``IM1000.pac``: 0x1f0), or that word is a short header size (32) and
    the table keeps going past it (``r0001/0000_000.pac``). Both are read with bounds checks, so a
    truncated member yields nothing instead of invented subfiles.
    """
    entries = _pac_index(blob)
    if entries is None:  # the index does not end where the header says; scan it permissively
        entries = _pac_index_permissive(blob)
    if not entries:
        return []
    names = [name for name, _, _ in entries]
    if len(set(names)) != len(names):
        return []
    return [{"subfile": name, "size": size} for name, _, size in entries]


def _pac_entry(blob: bytes, base: int):
    """One index entry as (name, offset, size), or None when the slot holds no name."""
    raw = blob[base + 8:base + 0x28].split(b"\x00")[0]
    if not re.fullmatch(rb"[\x21-\x7e]{1,31}", raw or b"\x00"):
        return None
    offset, size = struct.unpack_from("<2I", blob, base)
    return raw.decode("ascii"), offset, size


def _pac_entries_ok(entries, blob_len: int) -> bool:
    """Bounds and overlap checks shared by both index readers."""
    for name, offset, size in entries:
        if size == 0 or offset < 0x10 or offset + size > blob_len:
            return False
    for (_, offset, size), (_, next_offset, _) in zip(entries, entries[1:]):
        if next_offset < offset + size:
            return False
    return bool(entries)


def _pac_index(blob: bytes) -> Optional[List[Tuple[str, int, int]]]:
    """[(name, offset, size), ...] for a table bounded by the header's first word.

    Returns None when that word is too small to hold even one entry (the other index shape),
    and an empty list when the table is malformed.
    """
    if len(blob) < 0x30:
        return []
    index_end = struct.unpack_from("<I", blob, 0)[0]
    if not (0x18 <= index_end <= min(len(blob), 0x800)):
        return None
    if index_end < 0x10 + 0x28:
        return None
    out: List[Tuple[str, int, int]] = []
    base = 0x10
    while base + 0x28 <= index_end:
        entry = _pac_entry(blob, base)
        if entry is None:
            break
        out.append(entry)
        base += 0x28
    if not _pac_entries_ok(out, len(blob)):
        return []
    return out


def _pac_index_permissive(blob: bytes) -> List[Tuple[str, int, int]]:
    """Same table read past a short header, stepping 0x28 or 8 bytes like ``pac_subfiles``."""
    out: List[Tuple[str, int, int]] = []
    base = 0x10
    limit = min(len(blob), 0x800)
    while base + 0x28 <= limit:
        entry = _pac_entry(blob, base)
        if entry is None:
            base += 0x08
            continue
        out.append(entry)
        base += 0x28
    if not _pac_entries_ok(out, len(blob)):
        return []
    return out


FILE_NAME = re.compile(r"^[A-Za-z0-9_./-]+\.(?:bin|dat|txt|pac|gim|cpk|ssa|sss|bsb|dff|anm|brtex)$|^ID\d{5}$")


def _harvest(value, out: Set[str]) -> None:
    """Collect every game-file-name-looking string (or dict key) of a JSON tree."""
    if isinstance(value, str):
        if FILE_NAME.match(value):
            out.add(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and FILE_NAME.match(key):
                out.add(key)
            _harvest(item, out)
    elif isinstance(value, list):
        for item in value:
            _harvest(item, out)


def reader_names(paths: Iterable[Path]) -> Dict[str, str]:
    """{file name: the output that read it} harvested from every reader output on disk."""
    claimed: Dict[str, str] = {}
    for path in paths:
        files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for json_path in files:
            if "member_inventory" in json_path.name:
                continue  # the audit's own output must not claim anything
            try:
                blob = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            found: Set[str] = set()
            _harvest(blob, found)
            label = OUTPUT_STEMS.get(json_path.stem) or OUTPUT_STEMS.get(
                json_path.parent.name + "/" + json_path.stem
            ) or json_path.stem
            for name in found:
                claimed.setdefault(name, label)
    return claimed


def classify(name: str, container: str, claimed: Dict[str, str]) -> str:
    """Which reader owns this file (or 'unread')."""
    if name in claimed:
        return claimed[name]
    for reader, marker in MARKER_READERS:
        if marker in name:
            return reader
    if container.lower().startswith("mesbtl"):
        return "battle_quotes"
    if name.lower().endswith(".bin") and container.lower().startswith(("eventp", "evept")):
        return "event_dialogue"
    return "unread"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default="../google_drive", help="folder with .cpk/.EDAT containers")
    parser.add_argument("--out", default="local/member_inventory.json")
    parser.add_argument("--tsv", default="local/member_inventory.tsv")
    args = parser.parse_args(argv)

    claimed = reader_names([Path(c) for c in READER_OUTPUTS])
    print(f"names claimed by the reader outputs: {len(claimed)}"
          f" ({len(set(claimed.values()))} readers: {sorted(set(claimed.values()))})")

    directory = Path(args.dir)
    rows: List[dict] = []
    errors: List[str] = []
    for path in containers(directory):
        members, error = member_rows(path)
        if error:
            errors.append(f"{path.name}: {error}")
            continue
        container_rows = []
        for row in members:
            row["container"] = path.name
            row["reader"] = classify(row["member"], path.name, claimed)
            container_rows.append(row)
        rows.extend(container_rows)
        # second level: PAC subfiles need the decompressed bytes, so the member list is re-read
        try:
            blobs = SM.read_members(path)
        except Exception:  # noqa: BLE001 - already reported above through member_rows
            continue
        by_name = {name: blob for name, blob in blobs}
        for row in container_rows:
            blob = by_name.get(row["member"])
            if blob is None:
                continue
            subs = subfile_rows(blob)
            if not subs:
                continue
            row["subfiles"] = len(subs)
            for sub in subs:
                rows.append(
                    {
                        "container": path.name,
                        "member": row["member"],
                        "subfile": sub["subfile"],
                        "stored": sub["size"],
                        "extracted": sub["size"],
                        "reader": classify(sub["subfile"], path.name, claimed),
                        "level": "subfile",
                    }
                )

    by_reader = collections.Counter(r["reader"] for r in rows)
    unread = [r for r in rows if r["reader"] == "unread"]
    unread_names = sorted({r.get("subfile") or r["member"] for r in unread})
    print(f"containers {len({r['container'] for r in rows})} / files {len(rows)}")
    for reader, count in by_reader.most_common():
        print(f"   {reader:24s} {count}")
    exts = collections.Counter(
        Path(r.get("subfile") or r["member"]).suffix.lower().lstrip(".") or "(none)"
        for r in unread
    )
    print(f"unread extensions: {dict(exts)}")
    unique_unread = collections.Counter(
        re.sub(r"\d+", "#", r.get("subfile") or r["member"]) for r in unread
    )
    print(f"unread distinct names: {len(unique_unread)}")
    for name, count in unique_unread.most_common(45):
        sizes = sorted({r["extracted"] for r in unread if re.sub(r"\d+", "#", r.get("subfile") or r["member"]) == name})
        print(f"   {name:44s} x{count:4d}  sizes {sizes[:3]}..{sizes[-1]}")
    if errors:
        print(f"containers with errors: {len(errors)}")
        for error in errors[:10]:
            print("   ", error)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "files": rows,
                "by_reader": dict(by_reader),
                "unread_distinct": unread_names,
                "errors": errors,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    tsv = Path(args.tsv)
    tsv.parent.mkdir(parents=True, exist_ok=True)
    with tsv.open("w", encoding="utf-8") as handle:
        handle.write("container\tmember\tsubfile\tstored\textracted\treader\tlevel\n")
        for row in rows:
            handle.write(
                f"{row['container']}\t{row['member']}\t{row.get('subfile', '')}\t{row['stored']}\t"
                f"{row['extracted']}\t{row['reader']}\t{row.get('level', 'member')}\n"
            )
    print(f"wrote {out} and {tsv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
