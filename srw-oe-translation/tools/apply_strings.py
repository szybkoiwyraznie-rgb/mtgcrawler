"""Apply translated strings (from export_strings output) back into event packages.

Closes the read -> translate -> write loop. Reads a ``*.strings.json`` produced by
``export_strings.py`` in which the ``target`` fields have been filled by a translator, and
rewrites each record with its translation via ``grow_event_text.grow_record`` (which handles
in-place growth and the inner EVNT size fields). The result is rebuilt into a new CPK image.

Safety, fail closed:
* a row whose ``target`` is empty is left untouched;
* a row is applied only if the record at its ``record_offset`` still decodes to its recorded
  ``source`` (so a stale/mismatched table never clobbers the wrong bytes);
* every target line's display width must fit the in-game dialogue box (default 46 half-width
  units, see docs/HANDOFF.md §2); over-wide targets are refused, not clipped;
* the target must encode in CP932.

Records within one member are applied in descending ``record_offset`` order so an edit never
shifts a record that is still to be processed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_write
import crilayla
import export_strings
import grow_event_text

BOX_WIDTH = 46  # in-game dialogue box, half-width units (docs/HANDOFF.md §2)


def check_target(target: str, budget: int = BOX_WIDTH) -> List[str]:
    problems = []
    for line in target.split("\n"):
        w = export_strings.display_width(line)
        if w > budget:
            problems.append(f"a target line is {w} wide, budget is {budget}: {line!r}")
    return problems


def apply_to_member(data: bytes, rows: List[dict], budget: int = BOX_WIDTH) -> bytes:
    """Return the member with every applicable row's record rewritten to its target."""
    out = data
    for row in sorted(rows, key=lambda r: r["record_offset"], reverse=True):
        target = row.get("target", "")
        if not target:
            continue
        problems = check_target(target, budget)
        if problems:
            raise ValueError("; ".join(problems))
        off = row["record_offset"]
        current = grow_event_text.record_text(out, off)
        if current.decode("cp932", errors="replace") != row["source"]:
            raise ValueError(
                f"record at {off} no longer matches its recorded source; refusing to apply"
            )
        try:
            encoded = target.encode("cp932")
        except UnicodeEncodeError as e:
            raise ValueError(f"target at {off} does not encode in cp932: {e}")
        out = grow_event_text.grow_record(out, off, encoded)
    return out


def apply_package(cpk_path: Path, strings_path: Path, out_path: Path, budget: int = BOX_WIDTH) -> dict:
    import shutil

    rows = json.loads(Path(strings_path).read_text(encoding="utf-8"))
    by_member: dict[str, list] = {}
    for row in rows:
        if row.get("target"):
            by_member.setdefault(row["member"], []).append(row)

    if not by_member:
        shutil.copyfile(cpk_path, out_path)
        return {"applied": 0, "members": 0}

    current = Path(cpk_path)
    applied = 0
    for member_name, member_rows in by_member.items():
        cpk = cpk_write.load(current)
        member = next(m for m in cpk.members if m.name == member_name)
        body = (
            crilayla.decompress(member.blob).data
            if crilayla.is_crilayla(member.blob)
            else member.blob
        )
        new_body = apply_to_member(body, member_rows, budget)
        image = cpk_write.rebuild(cpk, (member_name, new_body))
        out_path.write_bytes(image)
        current = out_path  # next member rebuilds on top of the previous result
        applied += len(member_rows)
    return {"applied": applied, "members": len(by_member)}


def main(argv: Optional[list[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    budget = BOX_WIDTH
    if "--budget" in args:
        i = args.index("--budget")
        budget = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 3:
        print("usage: apply_strings.py <package.EDAT|cpk> <strings.json> <out> [--budget N]")
        return 2
    summary = apply_package(Path(args[0]), Path(args[1]), Path(args[2]), budget)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
