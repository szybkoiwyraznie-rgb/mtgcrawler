#!/usr/bin/env python3
"""Find game text that the translation package has no row for, and export it as rows.

Why this exists
---------------
Every reader covers the structure it was written for; whatever sits outside those structures is
invisible to the package without anyone noticing.  ``tools/coverage_audit.py`` reports the gap;
this tool turns the gap into rows, so "no text left behind" is a number instead of a promise.

What counts as text
-------------------
The check is a byte scan for CP932 double-byte runs (the same scan the audit uses), then three
filters -- each one printed in the report so nothing is dropped silently:

* already covered: the run, or a suffix of it, is contained in some package row (a run can start
  on a stray lead byte, so up to ``--trim`` characters are dropped from the front), or the whole
  NUL-delimited span around the run is covered (a big string split by control bytes into several
  runs);
* decoding artifact: the run is a fragment of a binary field, not text -- the members listed in
  ``SKIP_MEMBERS`` hold numbers (IEEE floats), file bookkeeping or nothing translatable, and their
  runs decode into stray kanji pairs;
* control placeholder: the run is nothing but a text-engine control (``＠０``, ``＠６``), the
  template the game fills in at run time.

``max_bytes`` is the length limit in English bytes (the terminator not counted - the same reading
as ``translation_check`` and the translator manual): the string's own span, or for an unusable
span the space from the run to the next string start in the same member, capped at
``--max-slot``.  These members keep their strings in a pool with a pointer table, so a longer
translation needs the pointer rewrite (``tools/sysmes_pack.py`` does that for ``sysmes.bin``);
until then the limit is what fits in place.

Usage::

    python tools/text_runs_export.py --container google_drive/configst.cpk \\
        --package local/translation --out local/leftovers.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import configst_pack as CSP  # noqa: E402
import dict_pool_shift as DPS  # noqa: E402
import extract_structured as ES  # noqa: E402
import speaker_map as SM  # noqa: E402

CATEGORY = "config_leftover"
EVENT_CATEGORY = "event_leftover"

#: Members whose CP932 runs are binary values, file bookkeeping or audio/SFX ids, not text.
#: ``srwDL_Dmg.bin`` is a table of damage values -- its runs are IEEE-754 floats read as kanji
#: (``9a 99 89 41`` = 17.2); ``Makefile`` is the CRI build recipe shipped inside the archive.
SKIP_MEMBERS = {
    "srwDL_Dmg.bin": "tabela wartości liczbowych (floaty czytane jako kanji)",
    "Makefile": "przepis budowania archiwum CRI, nie tekst gry",
}

#: A run that is only a text-engine control (full-width ``＠`` + digit/letter) is a template,
#: not translatable text: the game substitutes the value at run time.
CONTROL_ONLY = re.compile(r"^[＠＄％][0-9０-９A-Za-zＡ-Ｚａ-ｚ]{0,2}$")

#: Short runs without any kana are more often halves of binary fields than words.
def plausible(text: str) -> bool:
    if CONTROL_ONLY.match(text):
        return False
    if not any("\u3040" <= ch <= "\u30ff" for ch in text) and len(text) < 3:
        return False
    return True


def member_blobs(path: Path) -> Dict[str, bytes]:
    """``{member name: bytes}`` for a container; a ``.pac`` member is split into its sub-members."""
    blobs: Dict[str, bytes] = {}
    for name, data in SM.read_members(path):
        if name.endswith(".pac"):
            try:
                for sub in CSP.parse_pac(data)["subs"]:
                    blobs[sub["name"]] = sub["data"]
            except Exception:
                blobs[name] = data
        else:
            blobs[name] = data
    return blobs


#: Rows already produced by this tool must not count as coverage, or a rerun would report
#: "nothing missing" because the previous run's own output now sits in the package.
OWN_CATEGORIES = {"config_leftover", "event_leftover"}


def package_texts(package: Path) -> str:
    """Every ``jp`` of every JSONL under the package directory, as one searchable blob."""
    texts: List[str] = []
    for path in sorted(package.glob("*.jsonl")) + sorted(package.glob("**/*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    jp = row.get("jp")
                    if jp and row.get("category") not in OWN_CATEGORIES:
                        texts.append(jp)
    return "\n".join(texts)


def covered(text: str, blob: str, trim: int = 3) -> bool:
    if not text:
        return False          # nothing is never "already in the package"
    if text in blob:
        return True
    for drop in range(1, min(trim, len(text) - 3) + 1):
        if text[drop:] in blob:
            return True
    return False


def span_around(data: bytes, offset: int) -> bytes:
    """The NUL-delimited bytes around ``offset`` (the record the string sits in)."""
    start = data.rfind(b"\x00", 0, offset) + 1
    end = data.find(b"\x00", offset)
    return data[start:end if end >= 0 else len(data)]


def text_of(span: bytes) -> str:
    """The span decoded as text, with the game's control bytes shown as the package shows them.

    The engine writes ``%s`` where a value is substituted (the same form the extracted skill rows
    use) and ``0x0F`` as the pool's token byte; both become ``%s`` so the translator keeps the
    placeholder instead of losing it.  A line break (``0x0A``) stays a line break.
    """
    out: List[str] = []
    i = 0
    while i < len(span):
        byte = span[i]
        if byte == 0x0A:
            out.append("\n")
            i += 1
            continue
        if byte < 0x20 or byte == 0x7F:
            out.append("%s")
            i += 1
            continue
        if (0x81 <= byte <= 0x9F or 0xE0 <= byte <= 0xFC) and i + 1 < len(span):
            try:
                out.append(span[i:i + 2].decode("cp932"))
                i += 2
                continue
            except UnicodeDecodeError:
                return ""
        try:
            out.append(span[i:i + 1].decode("cp932"))
        except UnicodeDecodeError:
            return ""
        i += 1
    return "".join(out)


def next_start(data: bytes, offset: int) -> int:
    """Offset of the next CP932 run in the member, or the member end."""
    for other, _ in ES.scan_runs(data):
        if other > offset:
            return other
    return len(data)


def growable(data: bytes) -> bool:
    """True when the project already has a writer that rebuilds this member byte-identically.

    ``dict_pool_shift`` rebuilds the character-dictionary pools (pointer words recomputed), so a
    longer translation fits there and no length limit has to be put on the translator.  The test is
    the rebuild itself: a no-edit rebuild that reproduces the input proves the layout is understood
    for *this* member, instead of trusting a list of names.
    """
    try:
        return DPS.rebuild_pool(data) == data
    except Exception:
        return False


def row_text(data: bytes, offset: int, text: str, max_span: int = 128) -> tuple:
    """``(text for the translator, limit in English bytes)`` for the string ``offset`` sits in.

    The unit the game stores is the NUL-delimited record, so that is the unit the translator gets:
    a template such as ``…の「＠３」コマンドで出現`` is one string, not three fragments, and the
    full line keeps the runtime placeholders visible.  A run whose record is unusable (no NUL
    nearby, mojibake, longer than ``max_span``) falls back to the run itself with the space up to
    the next string start -- both cases keep the in-place limit honest.
    """
    span = span_around(data, offset)
    run_bytes = len(text.encode("cp932"))
    if len(span) <= max_span:
        decoded = text_of(span)
        if decoded and "�" not in decoded:
            try:
                decoded.encode("cp932")
            except UnicodeEncodeError:
                pass
            else:
                return decoded, len(span)
    slot = min(next_start(data, offset) - offset, max_span)
    return text, max(slot - 1, run_bytes)


def find_rows(path: Path, blob: str, trim: int = 3, max_slot: int = 256,
             category: str = CATEGORY) -> List[dict]:
    """Rows for every plausible text run of the container that the package does not cover."""
    rows: List[dict] = []
    for member, data in member_blobs(path).items():
        if member in SKIP_MEMBERS:
            continue
        seen = set()
        for offset, text in ES.scan_runs(data):
            if len(text) < 2 or not plausible(text):
                continue
            if covered(text, blob, trim):
                continue
            if covered(text_of(span_around(data, offset)), blob, trim):
                continue
            line, limit = row_text(data, offset, text, max_slot)
            if line in seen:
                continue
            seen.add(line)
            grow = growable(data)
            rows.append({"id": f"leftover:{path.name}/{member}:{offset}",
                         "category": category, "part": "text", "jp": line, "en": "",
                         "bytes": len(line.encode("cp932")),
                         "mode": "grow" if grow else "slot",
                         "max_bytes": None if grow else limit,
                         "source": {"container": path.name, "member": member, "offset": offset}})
    return rows


def merge_into(rows: Iterable[dict], target: Path) -> dict:
    """Add rows the target file does not have yet (by id); rewrite it sorted by source."""
    existing = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    known = {row["id"] for row in existing}
    added = [row for row in rows if row["id"] not in known]
    if added:
        merged = existing + added
        merged.sort(key=lambda row: (row["source"]["container"], row["source"]["member"],
                                     row["source"]["offset"]))
        with target.open("w", encoding="utf-8") as handle:
            for row in merged:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"existing": len(existing), "added": len(added), "total": len(existing) + len(added)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export game text the package has no row for")
    parser.add_argument("--container", type=Path, action="append", required=True)
    parser.add_argument("--package", type=Path, required=True, help="katalog z *.jsonl pakietu")
    parser.add_argument("--out", type=Path, help="gdzie zapisać wiersze")
    parser.add_argument("--merge-into", type=Path, help="plik pakietu, do którego dopisać wiersze")
    parser.add_argument("--trim", type=int, default=3, help="ile znaków wolno obciąć z przodu")
    parser.add_argument("--max-slot", type=int, default=256, help="górny limit długości (bajty)")
    parser.add_argument("--category", default=CATEGORY, help="kategoria wierszy w pakiecie")
    args = parser.parse_args(argv)

    blob = package_texts(args.package)
    rows: List[dict] = []
    for container in args.container:
        found = find_rows(container, blob, args.trim, args.max_slot, args.category)
        chars = sum(len(row["jp"]) for row in found)
        print(f"{container.name}: {len(found)} tekstów bez wiersza ({chars} znaków)")
        if args.category == CATEGORY:
            for member in SKIP_MEMBERS:
                if member in member_blobs(container):
                    print(f"    pominięty {member}: {SKIP_MEMBERS[member]}")
        rows.extend(found)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"zapisane: {args.out}")
    if args.merge_into and rows:
        report = merge_into(rows, args.merge_into)
        print(f"w {args.merge_into}: było {report['existing']}, dodane {report['added']}, "
              f"razem {report['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
