#!/usr/bin/env python3
"""Add the convention-A table strings an older package never addressed; prune the stale rows.

The record-table families of :mod:`table_write` (CharaDictionary, RoboDictionary, Reference,
Shop, DLC_ID, ...) reached the translator through three exporters that each saw a part of the
records: ``translator_export.character_rows`` wrote slots 0-4 of a CharaDictionary record,
``unit_rows`` slots 0/1/3 of a RoboDictionary record, ``config_rows`` the runs the NUL-run scan
judged clean.  What fell through [measured 2026-10-16 on config00-19/imenu00-19]:

* CharaDictionary slot 11 (the short name the Character Viewer grid draws - 291 records), the
  ``愛称：`` / ``声優：`` labels of slots 4/5 (the keyed rows carry only the text behind them);
* RoboDictionary slot 4 (variant type), 5 (display-name override), 6 (narrow name) and the
  ``全長 －－－`` / ``重量 －－－`` placeholder lines the exporter skipped as "no text";
* Reference slot 0 (section titles, glued to two control bytes in front of them) and any slot
  whose body carries ``0x0F xx`` kana tokens (the level-gap page: ``clean_run`` rejected it and
  the leftover scan exported nine fragments of it instead);
* the ``ﾌｧﾐ通ｺﾗ%s7`` DLC_ID titles (kana token).

This tool walks every family member of the given containers the way the writer does
(``table_write.parse_pool``), and for every record slot with translatable text that no row
addresses - neither a keyed row (``key`` + ``part`` of ``PART_SLOT``, a label row for a
labelled slot) nor an offset row at the string's start - appends the row the writer reads:

* ``char:K:short_name`` (file 07, ``copy_of`` the nickname row when the text is the same),
  the two label rows ``label:srwDL_CharaDictionary:4/5`` (``part: label``, ``source.slot``);
* ``robonote:K:type|name|name_narrow|length|weight`` (file 08, container-less like the other
  robonote rows; ``name`` / ``name_narrow`` take ``copy_of`` the ``unit:K:name`` row when the
  Japanese is identical);
* ``reference|dlc_id|shop:<container>/<member>:<offset>`` (file 04) for the key-less families.

A new row takes the English of a row that already translates the identical Japanese in the same
family (``sibling``), otherwise ``en`` stays empty for the translator.  A member byte-identical
to one already walked (imenuNN = configNN) is skipped: the build mirrors the rows
(``build_translation_patch.mirror_identical_members``).

``--prune`` removes, in the walked containers only, the offset rows the writer can never apply:
``unreachable`` (the offset lies in no string the member's tables point at - a binary field that
decodes, or a run glued to the byte in front of the real string; its English is carried over to
the new row of the real string, ``salvaged``), ``stale`` (the ``jp`` is not the string at that
offset: fragments of a tokenised body) and ``superseded`` (a leftover row repeating a labelled
slot whole, ``愛称：仁`` - the keyed row and the label row own that slot now; the whole-string
row only conflicts with them).  Without ``--prune`` they are only listed.  Nothing else is
removed and no existing English is changed.

Usage:
    python tools/table_rows_refresh.py --package local/pakiet --containers local/dlc/*.EDAT \\
        local/inputs/config00.cpk [--prune] [--check] [--report out.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP     # noqa: E402
import speaker_map as SM        # noqa: E402
import table_write as TW        # noqa: E402
import token_map as TM          # noqa: E402

FILE_CHAR = "07_names_characters.jsonl"
FILE_UNIT = "08_names_units_weapons.jsonl"
FILE_CONFIG = "04_config_text.jsonl"
PACKAGE_FILES = (FILE_CONFIG, FILE_CHAR, FILE_UNIT)

#: family prefix -> (row id prefix, category prefix, package file, container-less?)
KEYED = {
    "srwDL_CharaDictionary": ("char", "character", FILE_CHAR, False),
    "srw_DL_RoboDictionary": ("robonote", "robo", FILE_UNIT, True),
}
#: key-less families -> row kind (id / category suffix)
OFFSET_KIND = {"srwDL_Reference": "reference", "srwDL_DLC_ID": "dlc_id", "srwDL_Shop": "shop",
               "srwDL_Skill_Tag": "skill_tag", "srwDL_Achievement": "achievement"}
#: keyed parts whose English follows another row of the same key when the Japanese is identical
COPY_FROM = {("srw_DL_RoboDictionary", "name"): "unit:{key}:name",
             ("srw_DL_RoboDictionary", "name_narrow"): "unit:{key}:name",
             ("srwDL_CharaDictionary", "short_name"): "char:{key}:nickname"}


def read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def family_members(path: Path) -> Dict[str, bytes]:
    """``{sub-member name: bytes}`` of every :mod:`table_write` family member in a container."""
    out: Dict[str, bytes] = {}
    members = SM.read_members(path)
    items = members.items() if isinstance(members, dict) else [(m[0], m[1]) for m in members]
    for name, data in items:
        if name.lower().endswith(".pac"):
            for sub in CSP.parse_pac(data)["subs"]:
                if TW.family_of(sub["name"]) is not None:
                    out[sub["name"]] = sub["data"]
        elif TW.family_of(name) is not None:
            out[name] = data
    return out


def slot_part(prefix: str, slot: int) -> Optional[str]:
    """The ``part`` whose slots include ``slot`` (first match), or None for an unmapped slot."""
    for part, slots in TW.PART_SLOT.get(prefix, {}).items():
        if slot in (slots if isinstance(slots, tuple) else (slots,)):
            return part
    return None


def translatable(raw: bytes) -> Optional[str]:
    """Display form of a string that carries text to translate, else None.

    Pure templates (``＠６%s``), empty strings and token-only runs are not rows; a string counts
    when, with the kana tokens and control bytes gone, a letter or a CJK character is left.
    """
    if not raw:
        return None
    bare = bytearray()
    i = 0
    while i < len(raw):
        if raw[i] == TW.KANA_TOKEN:
            i += 2
            continue
        if raw[i] < 0x20 or raw[i] == 0x7F:
            i += 1
            continue
        bare.append(raw[i])
        i += 1
    try:
        text = bytes(bare).decode("cp932")
    except UnicodeDecodeError:
        return None
    text = text.replace("＠", "")
    if not any(ch.isalpha() for ch in text):
        return None
    return TW.display(raw)


def row_bytes(text: str) -> int:
    try:
        return len(text.encode("cp932"))
    except UnicodeEncodeError:
        return len(text.encode("utf-8"))


class Index:
    """What the package already addresses, plus the siblings' English by (family, jp)."""

    def __init__(self, rows: List[dict]):
        self.offsets: Dict[Tuple[str, str], Dict[int, List[str]]] = {}  # (container, member) -> offset -> [jp]
        self.keyed: set = set()                       # (container | None, prefix, key, part)
        self.labels: set = set()                      # (prefix, slot)
        self.english: Dict[Tuple[str, str], str] = {}  # (prefix, jp) -> en
        self.first_id: Dict[Tuple[str, str], str] = {}  # (prefix, jp) -> id of the first row
        self.by_id: Dict[str, dict] = {}
        for row in rows:
            self.add(row)

    def add(self, row: dict) -> None:
        source = row.get("source") or {}
        member = source.get("member") or ""
        prefix = TW.sub_name_prefix(member)
        if row.get("id"):
            self.by_id.setdefault(row["id"], row)
        if row.get("part") == TW.LABEL_PART:
            if isinstance(source.get("slot"), int):
                self.labels.add((prefix, source["slot"]))
            return
        if row.get("key") is not None and prefix in TW.PART_SLOT \
                and row.get("part") in TW.PART_SLOT[prefix]:
            self.keyed.add((source.get("container"), prefix, int(row["key"]), row["part"]))
        elif isinstance(source.get("offset"), int) and source.get("container"):
            self.offsets.setdefault((source["container"], member), {}) \
                .setdefault(source["offset"], []).append(row.get("jp") or "")
        jp = row.get("jp")
        if jp and row.get("id"):
            self.first_id.setdefault((prefix, jp), row["id"])
        en = (row.get("en") or "").strip()
        if en and jp and (prefix, jp) not in self.english:
            self.english[(prefix, jp)] = row["en"]

    def has_keyed(self, container: Optional[str], prefix: str, key: int, part: str) -> bool:
        return (container, prefix, key, part) in self.keyed or (None, prefix, key, part) in self.keyed

    def has_offset(self, container: str, member: str, start: int, raw: bytes) -> bool:
        """A writable offset row for this string: at its start or inside it (the leftover scan
        recorded hits mid-string; the writer resolves those to the string, see
        table_write.resolve_one) AND carrying the whole string as its jp - a fragment row
        inside a longer body does not cover the body."""
        for offset, jps in self.offsets.get((container, member), {}).items():
            if start <= offset <= start + len(raw) \
                    and any(TW.match_form(jp, raw) is not None for jp in jps):
                return True
        return False


def member_strings(blob: bytes, member: str) -> Dict[Tuple[int, int], Tuple[int, bytes]]:
    """``{(record, slot): (absolute offset, raw bytes)}`` of every string a member holds."""
    family = TW.family_of(member)
    out: Dict[Tuple[int, int], Tuple[int, bytes]] = {}
    for i, (rec, (start, _end)) in enumerate(zip(TW.parse_pool(blob, family),
                                                 TW.record_spans(blob))):
        for slot, raw in enumerate(rec.strings):
            out[(i, slot)] = (start + rec.pointers[slot], raw)
    return out


def walk_member(container: str, member: str, blob: bytes, index: Index, report: dict
                ) -> Tuple[List[dict], Dict[Tuple[int, int], Tuple[int, bytes]]]:
    """New rows for one member + ``{(record, slot): (offset, raw)}`` of every string it holds."""
    family = TW.family_of(member)
    prefix = TW.sub_name_prefix(member)
    spans = TW.record_spans(blob)
    records = TW.parse_pool(blob, family)
    strings = member_strings(blob, member)
    new: List[dict] = []
    for i, (rec, (start, _end)) in enumerate(zip(records, spans)):
        key = TW.record_key(blob, (start, _end), family) if family.key else None
        for slot, raw in enumerate(rec.strings):
            offset = start + rec.pointers[slot]
            if raw and index.has_offset(container, member, offset, raw):
                continue
            label = TW.SLOT_LABELS.get((prefix, slot))
            text_raw = raw
            if label and raw.startswith(label):
                text_raw = raw[len(label):]
                if (prefix, slot) not in index.labels:
                    row = {"id": f"label:{prefix}:{slot}", "category": "config_label",
                           "part": TW.LABEL_PART, "jp": label.decode("cp932"), "en": "",
                           "bytes": len(label), "mode": "grow", "max_bytes": None,
                           "source": {"container": None, "member": prefix, "slot": slot}}
                    row["en"] = index.english.get((prefix, row["jp"]), "")
                    new.append(row)
                    index.labels.add((prefix, slot))
                    report["labels"] += 1
            text = translatable(text_raw)
            if text is None:
                continue
            raw_text = text_raw
            part = slot_part(prefix, slot) if key is not None else None
            if part is not None:
                id_prefix, cat_prefix, _file, containerless = KEYED[prefix]
                row_container = None if containerless else container
                if index.has_keyed(row_container, prefix, key, part):
                    continue
                row = {"id": f"{id_prefix}:{key}:{part}", "category": f"{cat_prefix}_{part}",
                       "part": part, "jp": text, "en": "", "bytes": row_bytes(text),
                       "mode": "grow", "max_bytes": None, "key": key,
                       "source": {"container": row_container,
                                  "member": prefix if containerless else member,
                                  "offset": i if containerless else 0}}
                template = COPY_FROM.get((prefix, part))
                source_row = index.by_id.get(template.format(key=key)) if template else None
                if source_row is not None and source_row.get("jp") == text:
                    row["copy_of"] = source_row["id"]        # one translation per key
                    row["en"] = source_row.get("en") or ""
                    report["copies"] += 1
                elif (prefix, text) in index.first_id and index.first_id[(prefix, text)] != row["id"]:
                    row["copy_of"] = index.first_id[(prefix, text)]   # one translation per text
                    row["en"] = index.english.get((prefix, text), "")
                    report["copies"] += 1
                else:
                    row["en"] = index.english.get((prefix, text), "")
                new.append(row)
                report["keyed"] += 1
            else:
                kind = OFFSET_KIND.get(prefix)
                if kind is None:
                    report["unmapped"].append(f"{container}/{member} record {i} slot {slot}: "
                                              f"{text[:30]!r}")
                    continue
                row = {"id": f"{kind}:{container}/{member}:{offset}", "category": f"config_{kind}",
                       "part": "text", "jp": text, "en": index.english.get((prefix, text), ""),
                       "bytes": row_bytes(text), "mode": "grow", "max_bytes": None,
                       "source": {"container": container, "member": member, "offset": offset}}
                first = index.first_id.get((prefix, text))
                if first and first != row["id"]:
                    row["copy_of"] = first
                    report["copies"] += 1
                new.append(row)
                report["offset_rows"] += 1
            index.add(row)
            if "%s" in text:
                row["_kinds"] = ",".join(TM.kinds_of(raw_text))   # sidecar entry, popped on write
            if row["en"]:
                report["filled_from_sibling"] += 1
            else:
                report["empty"] += 1
    return new, strings


def update_sidecar(package: Path, added: List[dict], removed_ids: Iterable[str]) -> int:
    """``tokeny.tsv`` next to the package: one entry per added row whose jp shows a ``%s``
    (kinds measured on the raw bytes while walking), minus the pruned rows."""
    sidecar = package / TM.SIDECAR_NAME
    existing = TM.load_map(sidecar) if sidecar.is_file() else {}
    drop = set(removed_ids)
    merged: Dict[str, Tuple[str, str]] = {
        ident: (",".join(kinds), json.dumps(jp, ensure_ascii=False))
        for ident, (jp, kinds) in existing.items() if ident not in drop}
    entries = 0
    for row in added:
        kinds = row.pop("_kinds", None)
        if kinds is None:
            continue
        merged[row["id"]] = (kinds, json.dumps(row["jp"], ensure_ascii=False))
        entries += 1
    if entries or (drop & set(existing)):
        TM.write_map(sidecar, [(ident, kinds, jp) for ident, (kinds, jp) in merged.items()])
    return entries


def stale_rows(rows: List[dict], walked: Dict[Tuple[str, str], Dict[Tuple[int, int],
               Tuple[int, bytes]]]) -> List[Tuple[dict, str, str]]:
    """Offset rows of the walked members the writer can never apply: (row, kind, reason).

    ``unreachable``: the offset lies in no string the member's tables point at (a binary field
    that decodes, or a run glued to the byte in front of the real string); ``stale``: the jp is
    not the string at that offset (fragments of a tokenised body, glued runs); ``superseded``: a
    leftover row repeating a labelled slot whole, now owned by the keyed row + the label row.
    """
    out: List[Tuple[dict, str, str]] = []
    for row in rows:
        source = row.get("source") or {}
        container, member, offset = source.get("container"), source.get("member"), source.get("offset")
        if row.get("part") == TW.LABEL_PART or row.get("key") is not None \
                or not isinstance(offset, int) or (container, member) not in walked:
            continue
        prefix = TW.sub_name_prefix(member)
        hit = None
        for (rec, slot), (start, raw) in walked[(container, member)].items():
            if raw and start <= offset <= start + len(raw):
                hit = (rec, slot, start, raw)
                break
        if hit is None:
            out.append((row, "unreachable", "offset lies in no string of the member"))
            continue
        rec, slot, start, raw = hit
        label = TW.SLOT_LABELS.get((prefix, slot))
        if TW.match_form(row.get("jp"), raw) is None:
            out.append((row, "stale", f"jp is not the string at record {rec} slot {slot}"))
        elif label and raw.startswith(label) and row.get("category") == "config_leftover":
            out.append((row, "superseded",
                        f"labelled slot {slot} is owned by the keyed row and the label row"))
    return out


def salvage(unreachable: List[dict], new_rows: List[dict]) -> int:
    """Carry the English of a glued row (``!チョバムアーマーSR`` at 5913) over to the new row of
    the real string (``チョバムアーマーSR`` at 5914) when that one is still empty; the glued
    characters are dropped from the English too when it starts with them.  Returns the count."""
    by_target: Dict[Tuple[str, str], List[dict]] = {}
    for row in new_rows:
        source = row.get("source") or {}
        if isinstance(source.get("offset"), int) and source.get("container"):
            by_target.setdefault((source["container"], source["member"]), []).append(row)
    moved = 0
    for old in unreachable:
        source = old.get("source") or {}
        old_jp, old_en = old.get("jp") or "", (old.get("en") or "").strip()
        if not old_en or old_en == old_jp:
            continue
        for row in by_target.get((source.get("container"), source.get("member")), []):
            gap = row["source"]["offset"] - source["offset"]
            if not 0 < gap <= 3 or (row.get("en") or "").strip() or not old_jp.endswith(row["jp"]):
                continue
            glue = old_jp[: len(old_jp) - len(row["jp"])]
            en = old_en[len(glue):].lstrip() if old_en.startswith(glue) else old_en
            row["en"] = en
            row["salvaged_from"] = old.get("id")
            moved += 1
            break
    return moved


def refresh(package: Path, containers: List[Path], prune: bool = False, check: bool = False
            ) -> dict:
    files = {name: package / name for name in PACKAGE_FILES}
    rows_by_file = {name: read_jsonl(path) for name, path in files.items()}
    all_rows = [row for name in PACKAGE_FILES for row in rows_by_file[name]]
    index = Index(all_rows)
    report = {"containers": [], "labels": 0, "keyed": 0, "offset_rows": 0, "copies": 0,
              "filled_from_sibling": 0, "empty": 0, "mirrored_skipped": [], "unmapped": [],
              "pruned": [], "added": {name: 0 for name in PACKAGE_FILES}, "errors": []}
    seen_digest: Dict[Tuple[str, str], str] = {}
    walked: Dict[Tuple[str, str], Dict[Tuple[int, int], Tuple[int, bytes]]] = {}
    new_by_file: Dict[str, List[dict]] = {name: [] for name in PACKAGE_FILES}
    for path in sorted(containers, key=lambda p: (not p.name.lower().startswith("config"), p.name)):
        try:
            members = family_members(path)
        except Exception as exc:          # a container that is not a CPK/PAC: say so, go on
            report["errors"].append(f"{path.name}: {exc}")
            continue
        report["containers"].append(path.name)
        for member, blob in sorted(members.items()):
            digest = hashlib.md5(blob).hexdigest()
            if (member, digest) in seen_digest:
                report["mirrored_skipped"].append(f"{path.name}/{member} = "
                                                  f"{seen_digest[(member, digest)]}")
                try:
                    walked[(path.name, member)] = member_strings(blob, member)
                except TW.TableError:
                    pass
                continue
            seen_digest[(member, digest)] = path.name
            try:
                new, strings = walk_member(path.name, member, blob, index, report)
            except TW.TableError as exc:
                report["errors"].append(f"{path.name}/{member}: {exc}")
                continue
            walked[(path.name, member)] = strings
            for row in new:
                prefix = TW.sub_name_prefix((row.get("source") or {}).get("member") or "")
                target = KEYED[prefix][2] if prefix in KEYED and row.get("part") != "text" \
                    else FILE_CONFIG
                new_by_file[target].append(row)
    pruned_ids = set()
    judged = stale_rows(all_rows, walked)
    report["salvaged"] = salvage([row for row, kind, _why in judged if kind == "unreachable"],
                                 [row for rows in new_by_file.values() for row in rows])
    for row, kind, why in judged:
        report.setdefault(kind, []).append(
            f"{row.get('id')} [{(row.get('source') or {}).get('container')}]: {why}")
        if prune:
            report["pruned"].append(f"{kind}: {row.get('id')}")
            pruned_ids.add(id(row))
    added_rows = [row for rows in new_by_file.values() for row in rows]
    removed_ids = [r.get("id") for r in all_rows if id(r) in pruned_ids]
    report["sidecar_entries"] = sum(1 for row in added_rows if "_kinds" in row)
    if not check:
        update_sidecar(package, added_rows, removed_ids)
    else:
        for row in added_rows:
            row.pop("_kinds", None)
    for name in PACKAGE_FILES:
        rows = [r for r in rows_by_file[name] if id(r) not in pruned_ids]
        removed = len(rows_by_file[name]) - len(rows)
        rows.extend(new_by_file[name])
        report["added"][name] = len(new_by_file[name])
        if not check and (new_by_file[name] or removed):
            write_jsonl(files[name], rows)
    report["pruned_count"] = len(report["pruned"])
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--containers", type=Path, nargs="+", required=True,
                        help="config*.cpk/.EDAT and imenu*.cpk/.EDAT files (decrypted)")
    parser.add_argument("--prune", action="store_true",
                        help="also remove the offset rows the writer can never apply")
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = refresh(args.package, args.containers, prune=args.prune, check=args.check)
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"containers {len(report['containers'])}  label rows {report['labels']}  keyed rows "
          f"{report['keyed']}  offset rows {report['offset_rows']}  (copies {report['copies']}, "
          f"filled from siblings {report['filled_from_sibling']}, salvaged {report['salvaged']}, "
          f"left empty {report['empty'] - report['salvaged']})  stale {len(report.get('stale', []))}"
          f"  superseded {len(report.get('superseded', []))}  unreachable "
          f"{len(report.get('unreachable', []))}  pruned {report['pruned_count']}  mirrored skipped "
          f"{len(report['mirrored_skipped'])}" + ("  [check only]" if args.check else ""))
    for line in report["unmapped"][:20]:
        print("  unmapped:", line)
    for line in report["errors"]:
        print("  error:", line)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
