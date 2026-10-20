#!/usr/bin/env python3
"""Read-only check of the two reported DLC activation records in installed files.

This verifies bytes in config04/imenu04, NOT the state currently loaded in an
emulator. Recursively lists every matching copy; never silently picks a backup.
Reports relative paths only. No save, ISO or DLC file is modified.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Optional

import configst_pack as CSP
import speaker_map
import table_write
import pl_text

MEMBER = "srwDL_DLC_ID04.bin"
FILES = ("config04.EDAT", "imenu04.EDAT")
TARGETS = {
    "config26.pac": {"jp": "「復活のゴブーリキ軍団」", "en": "Return of the Goburiki Army", "description_offset": 120,
                     "product": "JP0700-NPJH50521_00-ADDPACKAGE000041"},
    "config27.pac": {"jp": "「盗賊団の悲劇」", "en": "The Bandits' Tragedy", "description_offset": 484,
                     "product": "JP0700-NPJH50521_00-ADDPACKAGE000042"},
}


class DlcTitleError(ValueError):
    pass


def expectations(rows: Iterable[dict], field: str = "en") -> dict:
    relevant = [r for r in rows if (r.get("source") or {}).get("member") == MEMBER]
    result = {}
    for payload, target in TARGETS.items():
        titles = {r[field] for r in relevant if r.get("jp") == target["jp"] and (r.get(field) or "").strip()}
        if not titles:
            continue
        if len(titles) != 1:
            raise DlcTitleError("Conflicting package names for a reported DLC record")
        descriptions = {r[field] for r in relevant if r["source"].get("offset") == target["description_offset"]
                        and (r.get(field) or "").strip()}
        if len(descriptions) > 1:
            raise DlcTitleError("Conflicting DLC descriptions")
        result[payload] = {"title": next(iter(titles)), "description": next(iter(descriptions), None)}
    return result


def inspect_table(blob: bytes, expected: Optional[dict] = None, lang: str = "en") -> dict:
    if lang not in ("en", "pl"):
        raise DlcTitleError("Expected en or pl codec")
    if lang == "pl" and expected is None:
        raise DlcTitleError("PL readback requires explicit package expectations; no EN fallback")
    encode = pl_text.encode if lang == "pl" else lambda text: text.encode("cp932")
    decode = pl_text.decode if lang == "pl" else lambda raw: raw.decode("cp932", "strict")
    expected = expected if expected is not None else {k: {"title": v["en"], "description": None} for k,v in TARGETS.items()}
    records = table_write.parse_pool(blob, table_write.family_of(MEMBER))
    found = {}
    for record in records:
        payload = record.strings[3].decode("ascii", "strict")
        if payload not in expected:
            continue
        if payload in found:
            raise DlcTitleError(f"Duplicate DLC payload {payload}")
        if record.strings[5] != TARGETS[payload]["product"].encode("ascii"):
            raise DlcTitleError(f"Unexpected PSN identity for {payload}")
        title0, title1, description = [decode(value) for value in record.strings[:3]]
        want = expected[payload]
        title_ok = record.strings[0] == record.strings[1] == encode(want["title"])
        desc_ok = record.strings[2] == encode(want["description"]) if want["description"] is not None else None
        found[payload] = {"expected_title": want["title"], "title_slots": [title0,title1],
                          "titles_match_package": title_ok, "titles_english": title_ok if lang == "en" else None, "description_matches_package": desc_ok,
                          "reported_jp_occurrences": sum(s.count(TARGETS[payload]["jp"].encode("cp932"))
                                                         for s in record.strings[:3])}
    missing = sorted(set(expected) - set(found))
    return {"passed": not missing and all(r["titles_match_package"] and r["description_matches_package"] is not False
                                         for r in found.values()),
            "missing_payloads": missing, "records": found, "lang": lang,
            "member_bytes": len(blob), "member_sha256": hashlib.sha256(blob).hexdigest()}


def inspect_container(path: Path, expected: Optional[dict] = None, lang: str = "en") -> dict:
    raw = path.read_bytes()
    if raw[:4] != b"CPK ":
        raise DlcTitleError("Not a decrypted CPK; the title table cannot be inspected")
    tables = []
    for member, blob in speaker_map.read_members(path):
        if member == MEMBER:
            tables.append(blob)
        elif member.lower().endswith(".pac"):
            tables += [s["data"] for s in CSP.parse_pac(blob)["subs"] if s["name"] == MEMBER]
    if len(tables) != 1:
        raise DlcTitleError(f"Expected one {MEMBER}, found {len(tables)}")
    return {"file": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "md5": hashlib.md5(raw).hexdigest(), **inspect_table(tables[0], expected, lang)}


def inspect_folder(folder: Path, expected: Optional[dict] = None, lang: str = "en") -> dict:
    results, missing, ambiguous = [], [], []
    files = [p for p in folder.rglob("*") if p.is_file()]
    for logical in FILES:
        matches = sorted(p for p in files if p.name.casefold() == logical.casefold())
        if not matches:
            missing.append(logical)
        if len(matches) > 1:
            ambiguous.append(logical)
        for path in matches:
            try:
                result = inspect_container(path, expected, lang)
            except Exception as exc:
                result = {"file": path.name, "passed": False, "error": str(exc)}
            result["relative_path"] = path.relative_to(folder).as_posix()
            results.append(result)
    return {"schema_version": 1, "read_only": True,
            "scope": "Selected installed-folder file bytes, not the emulator's loaded RAM or save state",
            "passed": not missing and not ambiguous and all(r["passed"] for r in results),
            "missing_files": missing, "multiple_copies": ambiguous, "files": results}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dlc", type=Path, required=True, help="The installed folder actually used by PPSSPP")
    ap.add_argument("--package", type=Path, help="Optional kit package, to check filled descriptions too")
    ap.add_argument("--lang", choices=("en", "pl"), default="en")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if not a.dlc.is_dir():
        raise DlcTitleError("Installed DLC folder does not exist")
    if a.out.suffix.lower() != ".json":
        raise DlcTitleError("The report must be a .json file")
    if a.package and (a.out.resolve() == a.package.resolve() or a.package.resolve() in a.out.resolve().parents):
        raise DlcTitleError("Write the report outside the translation package")
    # Reports must not overwrite any source, including a misleading .EDAT --out.
    if a.out.resolve() == a.dlc.resolve() or a.dlc.resolve() in a.out.resolve().parents:
        raise DlcTitleError("Write the report outside the installed DLC folder")
    if a.lang == "pl" and not a.package:
        raise DlcTitleError("--lang pl requires --package; no English fallback")
    expected = None
    if a.package:
        rows = [json.loads(l) for l in (a.package/"04_config_text.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        expected = expectations(rows, field=a.lang)
        if set(expected) != set(TARGETS):
            raise DlcTitleError("The kit does not define both DLC titles")
    result = inspect_folder(a.dlc, expected, lang=a.lang)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS — files match the kit" if result["passed"] else "ATTENTION — missing, unreadable, duplicate or mismatched DLC files")
    for entry in result["files"]:
        print(entry["relative_path"] + ": " + ("PASS" if entry["passed"] else "CHECK"))
        for payload, record in entry.get("records", {}).items():
            print("  " + payload + ": " + " / ".join(record["title_slots"]))
    print("Report: " + a.out.name)
    print("No game/save files were modified. File PASS does not prove what an old emulator save state contains.")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
