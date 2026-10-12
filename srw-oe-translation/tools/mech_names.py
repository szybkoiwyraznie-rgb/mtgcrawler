#!/usr/bin/env python3
"""Collect mecha (robot) name candidates from SRW OE config containers.

Read-only. Sources, per config container (config*.cpk / config*.EDAT):

  * srw_DL_RoboDictionary*.bin  record slot 3 (u32 offset table at record start;
    slot 3 holds a mecha display name or a placeholder).
  * unit_list*.bin  384-byte records: CP932 name at +0 and display name at +140.
  * robolist.bin    (structure not yet decoded; reported as a count only).

Each name is recorded with its source and container so the translator can see
where it came from. Output contains game text, so it goes under local/ only.

Usage:
    python tools/mech_names.py --dir google_drive --out local/mech/mech_names.json
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_write  # noqa: E402
import crilayla  # noqa: E402

UNIT_STRIDE = 384


def _cp932(raw: bytes) -> str | None:
    seg = raw.split(b"\x00", 1)[0]
    if not seg:
        return None
    try:
        return seg.decode("cp932")
    except UnicodeDecodeError:
        return None


def pac_entries(blob: bytes) -> dict[str, bytes]:
    """Index of a config .pac: entries at base 0x10 stride 0x28 (u32 offset, u32 size, name at +8)."""
    out: dict[str, bytes] = {}
    base = 0x10
    while base + 0x28 <= 0x800:
        off, size = struct.unpack_from("<II", blob, base)
        name = blob[base + 8:base + 0x28].split(b"\x00", 1)[0].decode("ascii", "replace")
        if not name:
            break
        out[name] = blob[off:off + size]
        base += 0x28
    return out


def robo_dictionary_slot3(data: bytes) -> list[str | None]:
    count = struct.unpack_from("<I", data, 0)[0]
    offs = [struct.unpack_from("<I", data, 4 + 4 * i)[0] for i in range(count)]
    ends = offs[1:] + [len(data)]
    names: list[str | None] = []
    for o, e in zip(offs, ends):
        rec = data[o:e]
        if len(rec) < 4 * 4:
            names.append(None)
            continue
        slot3 = struct.unpack_from("<I", rec, 4 * 3)[0]
        names.append(_cp932(rec[slot3:]) if 0 < slot3 < len(rec) else None)
    return names


def unit_list_names(data: bytes) -> list[tuple[str | None, str | None]]:
    rows = []
    for i in range(len(data) // UNIT_STRIDE):
        r = data[i * UNIT_STRIDE:(i + 1) * UNIT_STRIDE]
        rows.append((_cp932(r[0:140]), _cp932(r[140:280])))
    return rows


def collect(path: Path) -> list[dict]:
    cpk = cpk_write.load(path)
    found: list[dict] = []
    for m in cpk.members:
        blob = m.blob
        if blob[:4] != b"CRIL" and blob[:4] != b"EVNT" and crilayla.is_crilayla(blob):
            blob = crilayla.decompress(blob).data
        if not m.name.endswith(".pac"):
            continue
        try:
            entries = pac_entries(blob)
        except struct.error:
            continue
        for name, data in entries.items():
            if name.startswith("srw_DL_RoboDictionary") and name.endswith(".bin"):
                for n in robo_dictionary_slot3(data):
                    if n:
                        found.append({"name": n, "source": "robo_dict_slot3", "container": path.stem})
            elif name.startswith("unit_list") and name.endswith(".bin"):
                for base_n, disp_n in unit_list_names(data):
                    if base_n:
                        found.append({"name": base_n, "source": "unit_list_base", "container": path.stem})
                    if disp_n:
                        found.append({"name": disp_n, "source": "unit_list_display", "container": path.stem})
            elif name == "robolist.bin":
                found.append({"name": None, "source": "robolist_records", "container": path.stem,
                              "count": struct.unpack_from("<I", data, 0)[0]})
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", type=Path, default=Path("google_drive"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    files = sorted(p for p in args.dir.iterdir()
                   if p.name.startswith("config") and p.suffix in (".cpk", ".EDAT"))
    rows: list[dict] = []
    errors: list[str] = []
    for f in files:
        try:
            rows.extend(collect(f))
        except Exception as e:  # keep going; report at the end
            errors.append(f"{f.name}: {type(e).__name__}: {e}")

    names = collections.Counter(r["name"] for r in rows if r.get("name"))
    by_source = collections.Counter(r["source"] for r in rows)
    summary = {
        "containers": len(files),
        "errors": errors,
        "rows": len(rows),
        "unique_names": len(names),
        "by_source": dict(by_source),
        "robolist_counts": {r["container"]: r["count"] for r in rows if r["source"] == "robolist_records"},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary,
                                    "names": sorted(names, key=lambda n: (-names[n], n)),
                                    "occurrences": {n: names[n] for n in names},
                                    "rows": rows}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
