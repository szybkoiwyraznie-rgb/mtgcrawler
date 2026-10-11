"""Inventory every CP932-bearing container in a directory (read-only).

For each *.cpk / *.EDAT under the given folder, reports how much translatable text it
holds and in what shape, so per-category extractors (menus, names, items, help, ...) can
be designed. Two shapes are distinguished:

* ``events``   -- EDAT/EVNT narration records (handled by export_strings.py);
* ``strings``  -- plain NUL-separated CP932 string tables (menus/names/items/help/...);
* ``binary``   -- no readable text.

Members that the CPK writer cannot open (constant-storage / ITOC-only containers such as
u16tbl/system/font) are scanned as raw bytes instead. Output is a compact per-file summary
suitable for pasting back.

Usage:
    python tools/scan_translatable.py <dir> [--min-wide N]
"""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_write
import crilayla


def _wide_count(s: str) -> int:
    return sum(1 for ch in s if unicodedata.east_asian_width(ch) in ("W", "F"))


def text_runs(blob: bytes, min_wide: int = 2):
    """Yield decoded CP932 strings from NUL-separated chunks that look like text."""
    for chunk in blob.split(b"\x00"):
        if len(chunk) < 4:
            continue
        try:
            s = chunk.decode("cp932")
        except Exception:
            continue
        if _wide_count(s) >= min_wide and not s.isspace():
            yield s


def scan_blob(blob: bytes, min_wide: int):
    runs = list(text_runs(blob, min_wide))
    return len(runs), runs[:3]


def scan_file(path: Path, min_wide: int) -> dict:
    data = path.read_bytes()
    out = {"file": path.name, "size": len(data), "members": 0,
           "events": 0, "text_members": 0, "total_runs": 0, "samples": []}
    members = []
    try:
        cpk = cpk_write.load(path)
        for m in cpk.members:
            blob = m.blob
            if crilayla.is_crilayla(blob):
                try:
                    blob = crilayla.decompress(blob).data
                except Exception:
                    continue
            members.append((m.name, blob))
        out["members"] = len(members)
    except Exception:
        members = [(path.name, data)]  # constant-storage / non-cpk: scan raw

    for name, blob in members:
        if blob[:4] == b"EDAT":
            # count narration records
            try:
                import grow_event_text as g
                _d, sections = g.parse_edat(blob)
                recs = 0
                pos = 0
                while True:
                    i = blob.find(g.RECORD_TYPE, pos)
                    if i < 0:
                        break
                    try:
                        length = struct.unpack_from("<I", blob, i + 4)[0]
                    except Exception:
                        break
                    if length < g.RECORD_OVERHEAD or i + length > len(blob):
                        pos = i + 1
                        continue
                    recs += 1
                    pos = i + length
                out["events"] += recs
            except Exception:
                pass
        n, samples = scan_blob(blob, min_wide)
        if n:
            out["text_members"] += 1
            out["total_runs"] += n
            for s in samples:
                if len(out["samples"]) < 3:
                    out["samples"].append(f"{name}: {s[:40]}")
    return out


import struct  # noqa: E402  (used in scan_file)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    min_wide = 2
    if "--min-wide" in argv:
        i = argv.index("--min-wide")
        min_wide = int(argv[i + 1])
        del argv[i:i + 2]
    if len(argv) != 1:
        raise SystemExit("usage: scan_translatable.py <dir> [--min-wide N]")
    root = Path(argv[0])
    files = sorted(list(root.glob("*.cpk")) + list(root.glob("*.EDAT")))
    if not files:
        raise SystemExit(f"no .cpk/.EDAT under {root}")
    for f in files:
        r = scan_file(f, min_wide)
        kind = "events" if r["events"] else ("strings" if r["total_runs"] else "binary")
        print(f"{r['file']:18} {kind:7} members={r['members']:3} events={r['events']:4} "
              f"runs={r['total_runs']:5}")
        for s in r["samples"]:
            print(f"      | {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
