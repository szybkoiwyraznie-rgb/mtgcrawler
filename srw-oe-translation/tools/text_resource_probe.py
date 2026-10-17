#!/usr/bin/env python3
"""Read-only, bounded-memory exact-text probe for CPK/PAC resources or stored files.

One CPK member is decompressed at a time. Reports offsets/identities only, never
exports complete game text or assets. A match is a lead, not approval to edit an
unknown structure. Inputs must be the user's own decrypted files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import configst_pack
import cpk_table
import crilayla
import speaker_map


def encodings(text):
    forms = {}
    for encoding in ("cp932", "utf-8", "utf-16le", "utf-16be"):
        try:
            forms[encoding] = text.encode(encoding)
        except UnicodeEncodeError:
            pass
    # Some PSP tables use little-endian u16 Shift-JIS character values.
    try:
        parts = [c.encode("cp932") for c in text]
        forms["cp932-u16le"] = b"".join(p[::-1] if len(p) == 2 else p + b"\0" for p in parts)
    except UnicodeEncodeError:
        pass
    return forms


def find_all(blob, needle):
    if not needle:
        raise ValueError("Empty search string")
    start, positions = 0, []
    while True:
        at = blob.find(needle, start)
        if at < 0:
            return positions
        positions.append(at)
        start = at + 1


def leaves(name, blob, depth=0):
    if crilayla.is_crilayla(blob):
        blob = crilayla.decompress(blob).data
    if name.lower().endswith(".pac"):
        if depth >= 8:
            raise ValueError("PAC nesting limit")
        parsed = configst_pack.parse_pac(blob)
        for sub in parsed["subs"]:
            yield from leaves(name + "/" + sub["name"], sub["data"], depth + 1)
    else:
        yield name, blob


def source_members(path):
    with path.open("rb") as handle:
        magic = handle.read(4)
    if magic != b"CPK ":
        yield path.name, path.read_bytes()
        return
    table = cpk_table.read_cpk_table(path)
    offsets = speaker_map.member_offsets(path, table)
    with path.open("rb") as handle:
        for entry, offset in zip(table["entries"], offsets):
            handle.seek(offset)
            raw = handle.read(entry["file_size"])
            if len(raw) != entry["file_size"]:
                raise ValueError("Truncated CPK member")
            yield from leaves(entry["name"], raw)


def probe(path, texts):
    forms = [(text, encoding, raw) for text in texts for encoding, raw in encodings(text).items()]
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    result = {"file": path.name, "bytes": path.stat().st_size, "sha256": digest.hexdigest(),
              "leaves_scanned": 0, "matches": []}
    for member, blob in source_members(path):
        result["leaves_scanned"] += 1
        for text, encoding, needle in forms:
            positions = find_all(blob, needle)
            if positions:
                result["matches"].append({"member": member, "member_bytes": len(blob),
                    "member_sha256": hashlib.sha256(blob).hexdigest(), "text": text,
                    "encoding": encoding, "offsets": positions})
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", type=Path, nargs="+", required=True)
    ap.add_argument("--text", action="append", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.resolve() in {p.resolve() for p in args.inputs}:
        raise ValueError("Refusing to overwrite input")
    records = []
    for path in args.inputs:
        record = probe(path, args.text)
        records.append(record)
        print(f"{path.name}: {record['leaves_scanned']} leaves, {len(record['matches'])} matching spans", flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"status": "probe-only", "files": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
