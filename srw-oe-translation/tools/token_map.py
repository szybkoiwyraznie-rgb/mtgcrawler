#!/usr/bin/env python3
"""Build the %s token map for a translation package (``tokeny.tsv``).

The package shows item/skill/config text in two forms and one of them is ambiguous:

* the **raw form** keeps the real bytes - a ``0x0F`` control is visible in the jp and the
  view renders it as ``<0x0F>``; the English must drop it together with the character after
  it (one voiced-kana glyph) and keep every literal ``%s`` - unambiguous, no map needed;
* the **display form** renders every control byte as ``%s`` - and a literal ``%s`` of the
  game's own formatter looks exactly the same.  Measured on the real files: the second byte
  of a kana token is a digit, a space or punctuation as often as a symbol (``.`` 46x, ``&``
  38x, ``*`` 42x, ``4`` 52x, ``1`` 49x...), and a literal ``%s`` is most often followed by a
  digit too - by eye, and by any text-side rule, ``%s4`` cannot be told apart.  Only the raw
  bytes in the game file know which is which.

This tool resolves the raw string of every display-form package row whose jp contains
``%s`` and writes one TSV line per row::

    id <TAB> kinds <TAB> jp(json)

``kinds`` is a comma-separated list, one entry per ``%s`` of the jp, in order:

* ``L`` - a literal ``%s`` placeholder of the game's formatter: the English MUST keep it
  (count and order),
* ``T`` - a kana token ``0x0F xx``: one voiced-kana glyph; the English MUST drop it together
  with the character after the ``%s`` (the glyph's second byte),
* ``C`` - another control token (e.g. ``\\r`` clearing the dialogue box): the English MUST
  keep it as ``%s``.

``tools/translation_check.py`` and ``tools/translation_import.py`` load ``tokeny.tsv``
automatically when it lies next to the package JSONL; without it the old strict rule applies
(every ``%s`` of the jp must appear in the English, which is wrong for the kana tokens).

Resolution per row (guard: ``TW.display(raw)`` must equal the jp, nothing is written blind):

1. item/skill record field rows (``part`` in ``ISR.FIELDS``): the field bytes of the parsed
   record at ``source.record_offset``;
2. every other row: the NUL-delimited run containing ``source.offset`` in the member
   (leftover, tail-pool, sysmes and mission rows).

Rows whose jp contains a real ``0x0F`` (raw form) and rows without ``%s`` are skipped -
they need no map.  Any row that cannot be resolved is reported and fails the run.

Usage::

    python tools/token_map.py --package local/translation --dlc ../google_drive
    python tools/token_map.py --package local/translation --dlc ../google_drive --out tokeny.tsv
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP          # noqa: E402
import cpk_write                     # noqa: E402
import item_skill_records as ISR     # noqa: E402
import item_skill_write as ISW       # noqa: E402
import table_write as TW             # noqa: E402

SIDECAR_NAME = "tokeny.tsv"
HEADER = ("# tokeny.tsv - rodzaje każdego %s w jp (kolejność jak w tekście):\n"
          "#   L = literalny placeholder gry (zostaje w EN, co do sztuki i kolejności)\n"
          "#   T = token kany 0x0F (znika z EN razem ze znakiem stojącym po %s)\n"
          "#   C = inna kontrolka, np. \\r czyszczące okno dialogowe (zostaje w EN jako %s)\n"
          "# kolumny: id <TAB> kinds <TAB> jp (JSON)\n")


class MapError(RuntimeError):
    pass


# ---------------------------------------------------------------- containers

class Containers:
    """Member bytes of every container the package points at, found under --dlc dirs."""

    def __init__(self, dlc_dirs: List[Path]):
        self.dlc_dirs = dlc_dirs
        self._members: Dict[Tuple[str, str], bytes] = {}
        self._loaded: Dict[str, Dict[str, bytes]] = {}

    def _find(self, container: str) -> Path:
        for dlc in self.dlc_dirs:
            candidate = dlc / container
            if candidate.is_file():
                return candidate
            hits = sorted(dlc.rglob(container))
            if hits:
                return hits[0]
        raise MapError(f"container not found under --dlc: {container}")

    def _load(self, container: str) -> Dict[str, bytes]:
        if container in self._loaded:
            return self._loaded[container]
        path = self._find(container)
        members: Dict[str, bytes] = {}
        if path.suffix.lower() == ".pac":
            subs = CSP.parse_pac(path.read_bytes())["subs"]
            members.update((sub["name"], sub["data"]) for sub in subs)
        else:
            cpk = cpk_write.load(path)
            for member in cpk.members:
                body = cpk_write.decompressed(member.blob)
                if member.name.lower().endswith(".pac"):
                    try:
                        subs = CSP.parse_pac(body)["subs"]
                    except Exception:
                        subs = []
                    if subs:
                        members.update((sub["name"], sub["data"]) for sub in subs)
                        continue
                members[member.name] = body
        self._loaded[container] = members
        return members

    def member(self, container: str, member: str) -> bytes:
        key = (container, member)
        if key not in self._members:
            members = self._load(container)
            if member not in members:
                raise MapError(f"member not found: {container}/{member}")
            self._members[key] = members[member]
        return self._members[key]


# ---------------------------------------------------------------- resolution

def containing_run(blob: bytes, offset: int) -> Optional[bytes]:
    """The NUL-delimited run containing ``offset`` (the writer's fallback for leftovers)."""
    if offset is None or offset < 0 or offset >= len(blob):
        return None
    start = blob.rfind(b"\x00", 0, offset) + 1
    end = blob.find(b"\x00", offset)
    return blob[start:] if end < 0 else blob[start:end]


def field_candidates(row: dict, blob: bytes) -> List[bytes]:
    """Raw-bytes candidates of an item/skill record field row (empty when not one).

    The package rows of 02/03 carry no record offset - their ``source.offset`` is the RECORD
    start (the run there is the binary record header) and the record number lives in the row
    id (``item:config00.cpk/srwDL_Item00.bin:r33:effect``).  The field bytes come from the
    parsed record: ``record_offset``/``record`` when present, otherwise the number from the id.
    """
    part = row.get("part")
    source = row.get("source") or {}
    if part not in ISR.FIELDS:
        return []
    kind = "item" if (row.get("category") == "item" or "Item" in str(source.get("member", ""))) \
        else "skill"
    try:
        parsed = ISR.parse_member(blob, kind, str(source.get("member", "")),
                                  str(source.get("container", "")))
    except Exception:
        return []
    records = parsed.get("records", [])
    candidates: List[dict] = []
    record_offset = source.get("record_offset")
    record_index = source.get("record")
    if record_index is None:
        match = re.search(r":r(\d+):", str(row.get("id", "")))
        record_index = int(match.group(1)) if match else None
    if record_offset is not None:
        candidates = [rec for rec in records if rec.get("offset") == record_offset]
    elif isinstance(record_index, int) and 0 <= record_index < len(records):
        candidates = [records[record_index]]
    out: List[bytes] = []
    for record in candidates:
        offset = record.get(f"{part}_offset")
        if offset is None or offset >= parsed["tail_offset"]:
            continue
        start = record.get("offset", 0) + offset
        end = blob.find(b"\x00", start)
        out.append(blob[start:] if end < 0 else blob[start:end])
    return out


def raw_for_row(row: dict, containers: Containers) -> Optional[bytes]:
    """The raw string behind the row's jp, or None when it cannot be resolved safely."""
    source = row.get("source") or {}
    container, member = source.get("container"), source.get("member")
    if not container or not member:
        return None
    try:
        blob = containers.member(container, member)
    except MapError:
        return None
    jp = row.get("jp") or ""
    for raw in field_candidates(row, blob):
        if TW.display(raw) == jp:
            return raw
    offset = source.get("offset")
    if isinstance(offset, int) and 0 <= offset < len(blob):
        # sysmes-style rows: the offset is the start of a LOGICAL string inside a longer
        # NUL run (one run holds several of them) - the writer slices it the same way
        end = blob.find(b"\x00", offset)
        suffix = blob[offset:] if end < 0 else blob[offset:end]
        if TW.display(suffix) == jp:
            return suffix
    raw = containing_run(blob, offset)
    if raw is not None and TW.display(raw) == jp:
        return raw
    return None


def kinds_of(raw: bytes) -> List[str]:
    """One letter per ``%s`` of the display form, in order (see the module docstring)."""
    letters = []
    for kind in TW.token_kinds(raw):
        if kind == b"%s":
            letters.append("L")
        elif kind == TW.KANA_TOKEN:
            letters.append("T")
        else:
            letters.append("C")
    return letters


# ---------------------------------------------------------------- build/write

def needs_map(row: dict) -> bool:
    """True for display-form rows whose jp carries at least one ambiguous ``%s``."""
    jp = row.get("jp") or ""
    return "%s" in jp and "\x0f" not in jp


def build_map(rows: List[dict], containers: Containers) -> Tuple[List[Tuple[str, str, str]],
                                                                  List[str]]:
    """(tsv entries, unresolved row reports) for the given package rows."""
    entries: List[Tuple[str, str, str]] = []
    unresolved: List[str] = []
    for row in rows:
        if not needs_map(row):
            continue
        raw = raw_for_row(row, containers)
        if raw is None:
            unresolved.append(f"{row.get('id', '?')}: cannot resolve the raw string")
            continue
        entries.append((row["id"], ",".join(kinds_of(raw)), json.dumps(row["jp"],
                                                                      ensure_ascii=False)))
    return entries, unresolved


def write_map(path: Path, entries: List[Tuple[str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [HEADER]
    lines.extend(f"{ident}\t{kinds}\t{jp}\n" for ident, kinds, jp in entries)
    path.write_text("".join(lines), encoding="utf-8")


def load_map(path: Path) -> Dict[str, Tuple[str, List[str]]]:
    """id -> (jp, kinds) from a ``tokeny.tsv``; shared by the checker and the importer."""
    table: Dict[str, Tuple[str, List[str]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        ident, kinds, jp = parts
        table[ident] = (json.loads(jp), kinds.split(",") if kinds else [])
    return table


def find_sidecar(package_paths: List[Path]) -> Optional[Path]:
    """``tokeny.tsv`` next to the package (or next to one of its JSONL files)."""
    for path in package_paths:
        directory = path if path.is_dir() else path.parent
        candidate = directory / SIDECAR_NAME
        if candidate.is_file():
            return candidate
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, nargs="+", required=True,
                        help="package JSONL files, or a directory holding them")
    parser.add_argument("--dlc", type=Path, nargs="+", required=True,
                        help="directories with the game containers (searched recursively)")
    parser.add_argument("--out", type=Path, default=None,
                        help=f"where to write the map (default: next to the package, "
                             f"{SIDECAR_NAME})")
    args = parser.parse_args(argv)

    rows, _files = ISW.collect_rows(args.package)

    containers = Containers(list(args.dlc))
    entries, unresolved = build_map(rows, containers)
    out = args.out or (args.package[0] if args.package[0].is_dir()
                       else args.package[0].parent) / SIDECAR_NAME
    write_map(out, entries)

    total = sum(1 for row in rows if needs_map(row))
    print(f"wierszy w pakiecie: {len(rows)}; z %s w jp (forma display): {total}; "
          f"rozwiazanych: {len(entries)}; nierozwiazanych: {len(unresolved)}")
    for line in unresolved[:40]:
        print("  " + line)
    print("zapisano", out)
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
