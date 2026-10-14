#!/usr/bin/env python3
"""Text tables inside the config containers: items, skills, reference/help, DLC ids (read-only).

Why this exists
---------------
The project goal requires item names **with their effect descriptions**, skill descriptions and
the help/reference texts (all "grow" candidates).  They live in three members of the config
containers (``srwDL_ItemNN.bin``, ``srwDL_SkillNN.bin``, ``srwDL_ReferenceNN.bin``) plus the
chapter-title table ``srwDL_DLC_IDNN.bin``.  Until now only a handful of names were known from
ad-hoc probes; nothing extracted all of them, and the table conventions were not written down.

Measured table conventions (config00, 2026-10-12) [ZWERYFIKOWANE]
-----------------------------------------------------------------
Convention A - ``u32 count`` at +0, then ``count`` u32 record offsets from +4:
    ``srwDL_ReferenceNN.bin`` (28 records in config00), ``srwDL_DLC_IDNN.bin`` (41),
    ``srwDL_ShopNN.bin`` (182), ``wp_listNN.bin``, and in configst:
    ``srwDL_Skill_Tag.bin`` (151), ``srwDL_Achievement.bin`` (75), ``srwDL_ItemDrop.bin`` (1092).
    The first offset equals ``4 + 4*count`` (end of the offset table = start of record 0).
Convention B - ``u32 tail_offset`` at +0, ``u32 count`` at +4, ``count`` u32 record offsets from
    +8: ``srwDL_Item00.bin`` (300 records in config00), ``srwDL_Skill00.bin`` (1469), and in
    configst: ``srwDL_Spirit.bin`` (60 records - the spirit-command names and descriptions),
    ``srwDL_StatusChange.bin`` (101).  The first
    offset equals ``8 + 4*count``; the records end at ``tail_offset`` and the remaining bytes
    (``tail_offset``..EOF) are a tail pool of description fragments; that pool is extracted too.
Convention C - pool with its own offset table: ``u32 table_start`` at +0 (8 in every measured
    file), ``u32 0`` at +4, then the offset table from +8 up to ``u32[table_start]`` (whose value is
    the start of the first string, i.e. the table is self-delimiting).  Measured on the DLC members
    ``srwDL_Item01-08.bin`` / ``srwDL_Skill01-08.bin``.  Measured relation to the disc tables:
    - the pool of ``srwDL_Item01-08`` is a subset of the ``srwDL_Item00`` tail pool (75/75 strings,
      0 new), so the item text is fully covered by config00;
    - ``srwDL_Skill01-08`` pool contains all 583 ``srwDL_Skill00`` tail strings plus ~239 one- to
      three-character fragments (format noise such as ``\n(``, ``%``); nothing that looks like a
      new skill description.  Both DLC files are special-cased in the summary, not treated as new.

Record contents
---------------
* ``srwDL_ReferenceNN`` record: 8 u32 pointers at +0 pointing at the record's own strings
  (labels, short description, title, long body text with $/＠ button markup, template labels).
  Verified: every pointer lands exactly on a text run.
* ``srwDL_ItemNN`` / ``srwDL_SkillNN`` record: a u16 table starting at +40 holding text spans
  (start,end pairs / starts), then the strings.  Item ids are the u16 at +0 (e.g. 10000, 10019).
  The field roles are NOT finalised (name at +54 in most records, description right after,
  short form later) - therefore this tool extracts *every* text run with its exact offset and
  leaves the role labels to the caller.

Extraction rule (deliberately conservative)
-------------------------------------------
A run is kept when it decodes as CP932, is at least ``MIN_RUN`` bytes, contains no control
character other than newline, and contains no private-use character.  Runs with and without CJK
are both kept (an item description can be pure ``%s`` format text); each row records ``has_cjk``.

Where a member's own layout is measured (the pointer families of ``table_write`` - reference,
DLC id, shop, skill tag, achievement, dictionaries - and the field boundaries of
``item_skill_records`` - item/skill records with their tail pool), the runs are checked against
the offsets those tables actually point at [ZWERYFIKOWANE 2026-10-14, config00/configst/config01]:

* a run no pointer names is a binary field that happens to decode (``' N'`` = u16 20000, ``'0u'``
  = 30000 - prices and ids in the shop, item and achievement records); it is kept in the raw
  output with ``orphan: true`` and the translator export drops it (97 of 6,602 judged strings);
* a run that *contains* a pointer target starts with bytes that belong to the previous field
  (``!チョバムアーマーSR`` - the ``!`` is a count byte; ``\x02\x05解説書：戦術`` - formatting
  bytes before a reference heading, which the control filter used to reject whole); it is
  snapped to the pointer target (``snapped: true``), so the row carries the string the game reads.

Members without a measured layout (spirit, status change, item drop, sysmes) keep every run.

Output contains game text, so it goes under ignored ``local/`` only.

Usage:
    python tools/config_text_tables.py --configs google_drive --out local/text_tables
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inline_names as IN  # noqa: E402
import item_skill_records as ISR  # noqa: E402
import speaker_map as SM  # noqa: E402
import table_write as TW  # noqa: E402

TABLES = (
    ("srwDL_Item", "item"),
    ("srwDL_Skill", "skill"),
    ("srwDL_Reference", "reference"),
    ("srwDL_DLC_ID", "dlc_id"),
    # tables that live in configst (help/UI side)
    ("srwDL_Spirit", "spirit"),
    ("srwDL_Achievement", "achievement"),
    ("srwDL_Skill_Tag", "skill_tag"),
    ("srwDL_StatusChange", "status_change"),
    ("srwDL_ItemDrop", "item_drop"),
    # shop catalogue: convention A; its records hold item ids and only ~5 label strings
    ("srwDL_Shop", "shop"),
)
CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]")
MIN_RUN = 2
REFERENCE_POINTERS = 8


def parse_table(blob: bytes) -> Optional[dict]:
    """Detect convention A, B or C.  Returns dict(count, offsets, data_start, data_end, convention).

    C is the pool form (see the module docstring): the offset table runs from +8 up to the value
    stored at +0, and every entry addresses one string of the pool.  In C the "records" are the
    individual pool strings, so ``data_end`` is EOF and ``pool`` is True.
    """
    if len(blob) < 8:
        return None
    for conv in ("A", "B", "C"):
        if conv == "C":
            table_start = struct.unpack_from("<I", blob, 0)[0]
            if table_start < 8 or table_start % 4 or table_start + 4 > len(blob):
                continue
            if struct.unpack_from("<I", blob, 4)[0] != 0:
                continue
            table_end = struct.unpack_from("<I", blob, table_start)[0]
            if table_end <= table_start or (table_end - table_start) % 4 or table_end >= len(blob):
                continue
            count = (table_end - table_start) // 4
            offs = list(struct.unpack_from("<%dI" % count, blob, table_start))
            if offs[0] != table_end or any(offs[i] > offs[i + 1] for i in range(count - 1)):
                continue
            return {"convention": "C", "count": count, "offsets": offs,
                    "data_start": offs[0], "data_end": len(blob), "pool": True}
        head = 4 if conv == "A" else 8
        try:
            count = struct.unpack_from("<I", blob, 0 if conv == "A" else 4)[0]
        except struct.error:
            continue
        if not (0 < count <= 20000) or head + 4 * count > len(blob):
            continue
        offs = list(struct.unpack_from("<%dI" % count, blob, head))
        if offs[0] != head + 4 * count:
            continue
        if any(offs[i] > offs[i + 1] for i in range(count - 1)):
            continue
        if conv == "B":
            # the word at +0 is the start of the tail pool; records end there
            data_end = struct.unpack_from("<I", blob, 0)[0]
            if not (offs[-1] <= data_end <= len(blob)):
                continue
        else:
            data_end = len(blob)
        return {"convention": conv, "count": count, "offsets": offs,
                "data_start": offs[0], "data_end": data_end, "pool": False}
    return None


def clean_run(raw: bytes) -> Tuple[Optional[str], bool]:
    """Decode one NUL-terminated run; reject control/PUA junk.  Returns (text, has_cjk)."""
    if len(raw) < MIN_RUN:
        return None, False
    try:
        text = raw.decode("cp932")
    except UnicodeDecodeError:
        return None, False
    for ch in text:
        if unicodedata.category(ch) == "Co":      # private use
            return None, False
        if ord(ch) < 0x20 and ch != "\n":         # keep newline, drop other controls
            return None, False
    return text, bool(CJK.search(text))


def string_starts(blob: bytes, member: str, kind: str) -> Optional[set]:
    """Absolute offsets of the strings the member's own record tables point at.

    ``None`` when no measured layout covers the member - then every clean run is kept, as before.
    Convention-A records come from the pointer families of :mod:`table_write`; item/skill records
    (convention B) from the field boundaries of :mod:`item_skill_records`.  The convention-B tail
    pool has no table of its own (records reach it through u16 words), so it is never judged.
    """
    family = TW.family_of(member)
    if family is not None:
        try:
            starts = set()
            for start, end in TW.record_spans(blob):
                record = TW.parse_record(blob[start:end], family)
                starts.update(start + p for p, text in zip(record.pointers, record.strings) if text)
            return starts
        except TW.TableError:
            return None
    if kind in ISR.KIND_PREFIX and member not in ISR.EXCLUDED:
        parsed = ISR.parse_member(blob, kind, member)
        if parsed["errors"] or not parsed["records"]:
            return None
        starts = set()
        for record in parsed["records"]:
            for role in ISR.FIELDS:
                if record[role]:
                    starts.add(record["offset"] + record[f"{role}_offset"])
        return starts
    return None


def record_strings(rec: bytes, base: int = 0, starts: Optional[set] = None) -> List[dict]:
    """Every clean NUL-terminated run in a record, with its in-record offset.

    With ``starts`` (absolute offsets, see :func:`string_starts`) a run is judged against the
    member's own tables: kept when it begins at a target, snapped to a target that lies inside it
    (``snapped``), otherwise flagged ``orphan`` (a binary field that happens to decode).
    """
    out = []
    i = 0
    n = len(rec)
    while i < n:
        if rec[i]:
            j = i
            while j < n and rec[j]:
                j += 1
            raw = rec[i:j]
            entry = None
            if starts is not None and base + i not in starts:
                inside = sorted(t - base - i for t in starts if base + i < t < base + j)
                if inside:
                    cut = inside[0]
                    text, has_cjk = clean_run(raw[cut:])
                    if text is not None:
                        entry = {"rel": i + cut, "bytes": j - i - cut, "text": text,
                                 "has_cjk": has_cjk, "snapped": True}
                if entry is None:
                    text, has_cjk = clean_run(raw)
                    if text is not None:
                        entry = {"rel": i, "bytes": j - i, "text": text, "has_cjk": has_cjk,
                                 "orphan": True}
            else:
                text, has_cjk = clean_run(raw)
                if text is not None:
                    entry = {"rel": i, "bytes": j - i, "text": text, "has_cjk": has_cjk}
            if entry is not None:
                out.append(entry)
            i = j
        i += 1
    return out


def reference_pointers(rec: bytes) -> Optional[dict]:
    """Read the 8 u32 pointers of a reference record and check where they land.

    Measured: a pointer aims at the *printable* start of a text run - either the run start itself
    (byte before is NUL) or a position 1-2 bytes into it (the run begins with 1-2 control bytes
    such as 0x01 0x01 or 0x02 0x0F that mark formatting).  A target is counted as a hit when its
    byte is non-NUL and the preceding byte is NUL or a control byte.
    """
    if len(rec) < 4 * REFERENCE_POINTERS:
        return None
    ptrs = list(struct.unpack_from("<%dI" % REFERENCE_POINTERS, rec, 0))
    hits = 0
    total = 0
    for p in ptrs:
        if not (0 < p < len(rec)):
            continue
        total += 1
        if rec[p] != 0 and (rec[p - 1] == 0 or rec[p - 1] < 0x20):
            hits += 1
    return {"pointers": ptrs, "pointer_hits": hits, "pointer_total": total,
            "all_hit": total > 0 and hits == total}


def extract_member(container: str, member: str, blob: bytes, kind: str) -> dict:
    """Parse one member and return {rows, stats}.

    Convention A/B: one row per record plus, for B, one extra row for the tail pool.
    Convention C: one row per pool string.
    """
    if len(blob) < 16:
        return {"rows": [], "stats": {"container": container, "member": member, "kind": kind,
                                      "convention": None, "records": 0, "records_with_text": 0,
                                      "strings": 0, "text_bytes": 0, "empty": True,
                                      "error": None}}
    table = parse_table(blob)
    if table is None:
        return {"rows": [], "stats": {"container": container, "member": member, "kind": kind,
                                      "convention": None, "records": 0, "records_with_text": 0,
                                      "strings": 0, "text_bytes": 0, "empty": False,
                                      "error": "table not recognised"}}
    recs: List[dict] = []
    ptr_ok = ptr_total = runs_total = bytes_total = with_text = 0
    starts = None if table.get("pool") else string_starts(blob, member, kind)
    orphans = snapped = 0

    if table.get("pool"):
        for i, start in enumerate(table["offsets"]):
            end = table["offsets"][i + 1] if i + 1 < table["count"] else len(blob)
            text, has_cjk = clean_run(blob[start:end].split(b"\x00")[0])
            if text is None:
                continue
            recs.append({"container": container, "member": member, "kind": kind, "record": i,
                         "record_offset": start, "record_len": end - start, "id": None,
                         "pool": True,
                         "strings": [{"rel": 0, "bytes": len(blob[start:end].split(b"\x00")[0]),
                                      "text": text, "has_cjk": has_cjk}]})
            with_text += 1
            runs_total += 1
            bytes_total += len(blob[start:end].split(b"\x00")[0])
    else:
        for i in range(table["count"]):
            start = table["offsets"][i]
            end = table["offsets"][i + 1] if i + 1 < table["count"] else table["data_end"]
            rec = blob[start:end]
            strings = record_strings(rec, start, starts)
            orphans += sum(1 for s in strings if s.get("orphan"))
            snapped += sum(1 for s in strings if s.get("snapped"))
            row = {"container": container, "member": member, "kind": kind, "record": i,
                   "record_offset": start, "record_len": len(rec),
                   "id": struct.unpack_from("<H", rec, 0)[0] if len(rec) >= 2 else None,
                   "strings": strings}
            if kind == "reference":
                info = reference_pointers(rec)
                if info:
                    row["pointers"] = info["pointers"]
                    ptr_ok += info["all_hit"]
                    ptr_total += 1
            if strings:
                with_text += 1
                runs_total += len(strings)
                bytes_total += sum(s["bytes"] for s in strings)
            recs.append(row)
        if table["convention"] == "B" and table["data_end"] < len(blob):
            tail = blob[table["data_end"]:]
            strings = record_strings(tail)        # the pool has no table to judge runs against
            if strings:
                recs.append({"container": container, "member": member, "kind": kind,
                             "record": None, "record_offset": table["data_end"],
                             "record_len": len(tail), "id": None, "pool": True,
                             "strings": strings})
                runs_total += len(strings)
                bytes_total += sum(s["bytes"] for s in strings)

    return {"rows": recs,
            "stats": {"container": container, "member": member, "kind": kind,
                      "convention": table["convention"], "records": table["count"],
                      "records_with_text": with_text, "strings": runs_total,
                      "text_bytes": bytes_total, "empty": False,
                      "layout_checked": starts is not None, "orphans": orphans,
                      "snapped": snapped,
                      "reference_pointer_records_ok": ptr_ok if kind == "reference" else None,
                      "reference_records": ptr_total if kind == "reference" else None,
                      "error": None}}


def scan(configs_dir: Path) -> Tuple[List[dict], List[dict], List[str]]:
    rows: List[dict] = []
    stats: List[dict] = []
    errors: List[str] = []
    for path in sorted(configs_dir.iterdir()):
        if not (path.name.lower().startswith("config")
                and path.suffix.lower() in (".cpk", ".edat")):
            continue
        try:
            members = SM.read_members(path)
        except Exception as exc:
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        for member_name, blob in members:
            if not member_name.lower().endswith(".pac"):
                continue
            try:
                subfiles = dict(IN.pac_subfiles(blob))
            except Exception as exc:
                errors.append(f"{path.name}/{member_name}: {type(exc).__name__}: {exc}")
                continue
            for sub, data in subfiles.items():
                for prefix, kind in TABLES:
                    if sub.startswith(prefix):
                        result = extract_member(path.name, sub, data, kind)
                        rows.extend(result["rows"])
                        stats.append(result["stats"])
    return rows, stats, errors


def unique_strings(rows: List[dict]) -> List[dict]:
    """Group every extracted run by text; keep each location (absolute file offset included)."""
    groups: Dict[str, dict] = {}
    for row in rows:
        for s in row["strings"]:
            entry = groups.setdefault(s["text"], {"text": s["text"], "has_cjk": s["has_cjk"],
                                                  "bytes": s["bytes"], "kinds": set(),
                                                  "locations": []})
            entry["kinds"].add(row["kind"])
            entry["locations"].append({
                "container": row["container"], "member": row["member"],
                "record": row["record"], "offset": row["record_offset"] + s["rel"],
                "pool": bool(row.get("pool")),
            })
    out = []
    for text, entry in groups.items():
        entry["kinds"] = sorted(entry["kinds"])
        entry["occurrences"] = len(entry["locations"])
        out.append(entry)
    out.sort(key=lambda e: (-e["occurrences"], e["text"]))
    return out


def summarise(stats: List[dict]) -> dict:
    by_kind: Dict[str, dict] = {}
    for st in stats:
        if st.get("error") or st.get("empty"):
            continue
        k = st["kind"]
        agg = by_kind.setdefault(k, {"members": 0, "records": 0, "records_with_text": 0,
                                     "strings": 0, "text_bytes": 0})
        agg["members"] += 1
        agg["records"] += st["records"]
        agg["records_with_text"] += st["records_with_text"]
        agg["strings"] += st["strings"]
        agg["text_bytes"] += st["text_bytes"]
    return by_kind


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--configs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True,
                    help="output directory (JSONL per table kind + summary.json)")
    args = ap.parse_args(argv)

    rows, stats, errors = scan(args.configs)
    args.out.mkdir(parents=True, exist_ok=True)
    by_kind: Dict[str, list] = collections.defaultdict(list)
    for row in rows:
        by_kind[row["kind"]].append(row)
    for kind, kind_rows in sorted(by_kind.items()):
        (args.out / f"{kind}.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in kind_rows) + "\n",
            encoding="utf-8")
    unique = unique_strings(rows)
    (args.out / "unique_strings.jsonl").write_text(
        "\n".join(json.dumps(u, ensure_ascii=False) for u in unique) + "\n", encoding="utf-8")
    unique_stats = {
        "unique_strings": len(unique),
        "unique_with_cjk": sum(1 for u in unique if u["has_cjk"]),
        "unique_ascii_only": sum(1 for u in unique if not u["has_cjk"]),
        "unique_bytes": sum(u["bytes"] for u in unique),
        "multi_location": sum(1 for u in unique if u["occurrences"] > 1),
    }
    summary = {"by_kind": summarise(stats), "unique": unique_stats, "errors": errors,
               "members": {st["member"]: st for st in stats
                           if not st.get("error") and not st.get("empty")}}
    (args.out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"by_kind": summary["by_kind"], "unique": unique_stats, "errors": errors},
                     ensure_ascii=False, indent=1))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
