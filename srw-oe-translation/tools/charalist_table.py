#!/usr/bin/env python3
"""Character table ``charalist<NN>.bin`` from the SRW OE config containers (read-only).

MEASURED 2026-10-12 on every local ``config00..19`` container [ZWERYFIKOWANE]:

* ``charalist<NN>.bin`` is a header-less array of **172-byte records**: member size = 172 x records.
  16 members hold 404 records in total (charalist00 = 134, charalist01 = 102, charalist02 = 55,
  charalist03 = 31, ...); the member numbers with no file (09, 16, 17, 18) carry no records.
* record layout::

      +0    短縮名      short display name, CP932, NUL-terminated (e.g. ブライト)
      +32   フルネーム  full name (e.g. ブライト・ノア)
      +76   半角名      narrow/half-width form, may hold 0x0F token bytes (e.g. {0F}3ﾗｲﾄ)
      +96   u16 key     **the speaker key used by dialogue and battle-quote records**
      +98   u16         0 in every record measured
      +100  u16         alias key - present in 12 records, always the key of another record
                        (e.g. the ダ・サイダー record carries 406 next to its own 405)
      +102  u16         0 / 10 / 20 / 30 (group or rank field, not decoded)
      +104  u16         non-zero in 140 records (12815, 2563, 15378, 20504 - not decoded)
      rest              zero in every record measured

  Every key is unique across all members and the keys inside one member ascend monotonically, which
  is what makes +96 safe to read without a header.

Coverage of the speaker keys found in the game (measured, see docs/COVERAGE.md):
300 of the 319 battle-quote keys and all 283 story-dialogue keys of the local extraction are in
this table; the 19 leftovers are listed by ``--missing`` with their quote counts.

This tool reads CP932 game text, so its output belongs under ``local/`` (gitignored).

Usage:
    python tools/charalist_table.py --configs DIR --out local/charalist.json [--missing KEYS.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inline_names as IN  # noqa: E402
import speaker_map as SM  # noqa: E402

RECORD = 172
NAME_OFFSETS = (0, 32, 76)
KEY_OFFSET = 96
ALIAS_OFFSET = 100
GROUP_OFFSET = 102
EXTRA_OFFSET = 104


def cstring(record: bytes, offset: int) -> str:
    """CP932 NUL-terminated string at ``offset`` ('' when the record holds none)."""
    end = record.find(b"\x00", offset)
    end = len(record) if end < 0 else end
    field = record[offset:end]
    if not field or len(field) > 32:
        return ""
    try:
        text = field.decode("cp932")
    except UnicodeDecodeError:
        return ""
    return text if all(unicodedata.category(c) != "Co" for c in text) else ""


def parse_member(member: str, blob: bytes, container: str = "") -> Tuple[List[dict], List[str]]:
    """Records of one charalist member; a size that is not a whole number of records is an error."""
    errors: List[str] = []
    if len(blob) % RECORD:
        errors.append(f"{container}:{member}: size {len(blob)} is not a multiple of {RECORD}")
    rows: List[dict] = []
    for index in range(len(blob) // RECORD):
        record = blob[index * RECORD:(index + 1) * RECORD]
        short, full, narrow = (cstring(record, off) for off in NAME_OFFSETS)
        rows.append({
            "container": container, "member": member, "record": index,
            "key": struct.unpack_from("<H", record, KEY_OFFSET)[0],
            "alias": struct.unpack_from("<H", record, ALIAS_OFFSET)[0],
            "group": struct.unpack_from("<H", record, GROUP_OFFSET)[0],
            "extra": struct.unpack_from("<H", record, EXTRA_OFFSET)[0],
            "name_short": short, "name_full": full, "name_narrow": narrow,
        })
    return rows, errors


def collect(config_dir: Path, read_members=None) -> Tuple[List[dict], List[str], int]:
    """Every charalist record in ``config*.cpk`` / ``config*.EDAT``. Returns (rows, errors, members).

    ``read_members`` defaults to :func:`speaker_map.read_members` (CPK table + CRILAYLA); tests
    inject their own reader so the container layer stays out of the unit tests.
    """
    read_members = read_members or SM.read_members
    rows: List[dict] = []
    errors: List[str] = []
    members = 0
    for path in sorted(config_dir.iterdir()):
        if not (path.name.lower().startswith("config") and path.suffix.lower() in (".cpk", ".edat")):
            continue
        for member_name, blob in read_members(path):
            subfiles = IN.pac_subfiles(blob) if member_name.lower().endswith(".pac") \
                else [(member_name, blob)]
            for sub, data in subfiles:
                if not sub.startswith("charalist"):
                    continue
                members += 1
                parsed, member_errors = parse_member(sub, data, path.name)
                rows.extend(parsed)
                errors.extend(member_errors)
    return rows, errors, members


def by_key(rows: List[dict]) -> Dict[int, dict]:
    """key -> record. Keys are unique across the game (measured 404/404), a clash is reported."""
    index: Dict[int, dict] = {}
    for row in rows:
        index.setdefault(row["key"], row)
    return index


def coverage(rows: List[dict], keys: Dict[int, int]) -> dict:
    """How many of ``keys`` (key -> count) the table covers, plus the missing ones."""
    index = by_key(rows)
    missing = sorted(k for k in keys if k not in index)
    return {
        "records": len(rows),
        "keys": len(index),
        "asked": len(keys),
        "covered": len(keys) - len(missing),
        "missing": missing,
        "missing_quotes": sum(keys[k] for k in missing),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--configs", type=Path, required=True, help="directory with config*.cpk/.EDAT")
    ap.add_argument("--out", type=Path, required=True, help="JSON output (keep under local/)")
    ap.add_argument("--keys", type=Path, default=None,
                    help="optional JSON {key: count} to report coverage against")
    ap.add_argument("--missing", type=Path, default=None, help="write the missing keys as JSON there")
    args = ap.parse_args(argv)

    rows, errors, members = collect(args.configs)
    index = by_key(rows)
    summary = {"members": members, "records": len(rows), "keys": len(index),
               "duplicates": len(rows) - len(index),
               "with_alias": sum(1 for r in rows if r["alias"]),
               "errors": errors[:20], "error_count": len(errors)}
    if args.keys:
        keys = {int(k): int(v) for k, v in json.loads(args.keys.read_text(encoding="utf-8")).items()}
        summary["coverage"] = coverage(rows, keys)
        if args.missing:
            args.missing.parent.mkdir(parents=True, exist_ok=True)
            args.missing.write_text(json.dumps(summary["coverage"]["missing"]), encoding="utf-8")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary, "records": rows}, ensure_ascii=False,
                                   indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
