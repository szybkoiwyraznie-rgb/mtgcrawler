#!/usr/bin/env python3
"""Fill a translation package with synthetic English for the full-chain rehearsal.

No translation is involved.  The tool takes the base package (``00``-``08`` JSONL, as it went
to the translator) and writes a copy in which the ``en`` of every selected row holds a
**synthetic** English text, so that :mod:`build_translation_patch` can be exercised end to end
on the real containers *before* a single translated line exists - and again before the final
patch, with whatever rules changed in between.  It replaces the ad-hoc ``scale_fill``/``mkpkg``
helpers that lived only in a sandbox and were lost with it; this one is tested and committed.

The synthetic text is built to be accepted wherever a real translation would be, and refused
only where a real translation would be refused too:

* every text is CP932 ASCII that **starts with a unique marker** (``t0a1z`` in the full
  rehearsal, ``TESTDIALO1`` in smoke mode), so :mod:`patch_spot_check` can find each row in
  the rebuilt bytes;
* the **same Japanese text gets the same English everywhere** - that is what a consistent
  glossary does, and it is what the pool writers require (two rows fighting over one pool
  string with different English are refused by design);
* every control token of the jp is kept in order (``＠0``…``＠9``, ``%%``, ``＃``, ``\\r``), the
  number of line breaks is kept, and the kana tokens are dropped **with the glyph character
  after them** - the ``<0x0F>`` of the raw form and, through ``tokeny.tsv``, the ``%s`` of the
  display form that stand for one (``T`` kinds); literal ``%s`` (``L``) and functional
  controls (``C``) stay.  This is the 2026-10-14 rule of ``translation_check``/``table_write``;
* the length follows the original: each text segment gets about ``ratio`` x its Japanese
  width (default 1.2, a measured English/Japanese width ratio), capped by the in-game box
  (46 half-width units per dialogue/quote line, 50 for narration) and by ``max_bytes`` of the
  fixed slots (``len(bytes) + 1 <= max_bytes``, the slot writer's rule) - so the growth paths
  are exercised everywhere growth is allowed and nothing is refused for a self-inflicted
  budget;
* every filled row is passed through :func:`translation_check.check_row` with the sidecar
  entry of the row; a row the checker would flag is left **empty** and counted (fail closed) -
  the rehearsal never feeds the writers something the real process would stop at the gate.

Selection: ``--containers`` and/or ``--dlc`` restrict the rows to the containers you actually
have (a sandbox holds six of them; the user's PC holds all), ``--skip-files`` drops whole
package files (``03`` to repeat the 2026-10-13 baseline), ``--smoke`` keeps one row per
(file, category, member family) plus one row with a kana token and one with ``\\r`` where the
group has them - a package of a few dozen rows that still touches every writer.

Rows with an empty jp, rows whose jp carries no text at all (only tokens) and rows whose
marker cannot fit the budget are not filled; the report says how many and why.  Nothing the
user owns is read or written: the input is the package, the output is a new folder.

Usage::

    python3 tools/scale_fill.py --package local/pkg --out local/scale_pkg --dlc ../google_drive
    python3 tools/scale_fill.py --package local/pkg --out local/smoke_pkg --dlc ../google_drive --smoke
    python3 tools/scale_fill.py --package local/pkg --out local/scale_pkg --dlc ../google_drive \\
        --skip-files 03            # the 2026-10-13 baseline selection (7 files)
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import export_strings                 # noqa: E402
import item_skill_write as ISW        # noqa: E402
import token_map as TMAP              # noqa: E402
import translation_check as TC        # noqa: E402

PACKAGE_FILES = (
    "00_dialogue.jsonl",
    "01_battle_quotes.jsonl",
    "02_items.jsonl",
    "03_skills.jsonl",
    "04_config_text.jsonl",
    "05_mission_text.jsonl",
    "07_names_characters.jsonl",
    "08_names_units_weapons.jsonl",
)

#: in-game widths the writers enforce (event_text_apply.BOX_WIDTH / NARRATION_WIDTH)
BOX_WIDTH = 46
NARRATION_TARGET = 50       # the manual's limit for narration (the game draws up to 52)
DEFAULT_RATIO = 1.2         # English width / Japanese width, per text segment

#: deterministic filler vocabulary (plain ASCII, no token characters)
WORDS = ("the quick brown fox jumps over a lazy dog and runs far away from old grey hills "
         "while small birds sing above calm rivers under bright skies near quiet towns").split()

#: bytes a token costs in the file - the display-form ``%s`` is counted as the literal (2),
#: the worst case; ``＠0`` is 3 bytes in CP932, ``＃`` and ``%%`` are 2
_TOKEN_RE = TC.TOKEN_RE


class FillError(RuntimeError):
    pass


# --------------------------------------------------------------------------- segments

def kinds_for(jp: str, pct: Optional[Tuple[str, List[str]]]) -> List[str]:
    """One kind letter per ``%s`` of ``jp``: the sidecar entry when it is fresh, else ``L``.

    Mirrors :func:`translation_check.expected_tokens`: a stale entry (another jp, another
    count) falls back to the strict rule, where every ``%s`` is kept.
    """
    count = TC.tokens(jp).count("%s")
    if pct is not None:
        map_jp, kinds = pct
        if map_jp == jp and len(kinds) == count:
            return list(kinds)
    return ["L"] * count


def segments(jp: str, kinds: Sequence[str]) -> List[Tuple[str, str]]:
    """Cut a jp into ``(type, value)`` pieces: ``txt``, ``tok``, ``nl``, ``ctl``.

    Kana tokens disappear here together with the character after them: the raw ``\\x0f`` of
    the raw form and the ``%s`` of the display form whose kind is ``T``.  Everything else the
    English must carry (tokens, ``\\r``, line breaks) is kept as its own piece, in order.
    """
    out: List[Tuple[str, str]] = []
    i = 0
    pct_index = 0
    swallow = False
    while i < len(jp):
        match = _TOKEN_RE.match(jp, i)
        if match:
            token = match.group(0)
            i = match.end()
            if token == "%s":
                kind = kinds[pct_index] if pct_index < len(kinds) else "L"
                pct_index += 1
                if kind == "T":
                    swallow = True            # the glyph's second byte follows the %s
                    continue
            swallow = False
            out.append(("tok", token))
            continue
        ch = jp[i]
        i += 1
        if swallow:
            swallow = False
            if ch not in "\n\r":              # measured: always 0x20-0x39, never a break
                continue
        if ch == "\n":
            out.append(("nl", ch))
        elif ch == "\x0f":
            if i < len(jp) and jp[i] not in "\n\r":
                i += 1                        # raw-form kana token: drop the glyph byte too
        elif ord(ch) < 0x20:
            out.append(("ctl", ch))
        elif out and out[-1][0] == "txt":
            out[-1] = ("txt", out[-1][1] + ch)
        else:
            out.append(("txt", ch))
    return out


def _token_bytes(token: str) -> int:
    if token == "%s":
        return 2
    return len(token.encode("cp932", "replace"))


# --------------------------------------------------------------------------- markers

def marker_for(index: int, smoke_code: Optional[str] = None, ordinal: int = 0) -> str:
    """``t`` + 4 base-36 digits in the full rehearsal, ``TEST<CODE><n>`` in smoke mode."""
    if smoke_code is not None:
        return f"TEST{smoke_code}{ordinal}"
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    value = index
    for _ in range(4):
        out = digits[value % 36] + out
        value //= 36
    return "t" + out


def short_marker(index: int) -> str:
    """The marker for a budget too small for the full one: base-36 digits only."""
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    value = index
    while True:
        out = digits[value % 36] + out
        value //= 36
        if not value:
            return out


def smoke_code(row: dict) -> str:
    """Up to six capital letters naming the category (or the scene kind) of a row."""
    name = row.get("kind") if (row.get("category") == "dialogue" and row.get("kind")) \
        else (row.get("category") or "row")
    for prefix in ("config_", "character_", "robo_", "unit_", "weapon_", "battle_"):
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    letters = re.sub(r"[^A-Za-z]", "", name).upper()
    return (letters or "ROW")[:6]


def member_family(member: Optional[str]) -> str:
    """A member name without its numbers: ``srwDL_Item00.bin`` -> ``srwDL_Item.bin``."""
    return re.sub(r"[0-9]+", "", member or "")


# --------------------------------------------------------------------------- the text

def _fill_words(target: int, prefix: str, cursor: List[int]) -> str:
    """``prefix`` plus filler words, never longer than ``target`` characters.

    When the next word of the cycle does not fit, the following few are tried, so a short
    piece (``1話`` before a line break) still gets a word instead of nothing.
    """
    if len(prefix) > target:
        return ""
    text = prefix
    guard = 0
    while guard < 64:
        guard += 1
        placed = False
        for ahead in range(8):
            word = WORDS[(cursor[0] + ahead) % len(WORDS)]
            candidate = (text + " " + word) if text else word
            if len(candidate) <= target:
                text = candidate
                cursor[0] += ahead + 1
                placed = True
                break
        if not placed:
            break
    return text


def synthesize(jp: str, kinds: Sequence[str], marker: str, *, ratio: float = DEFAULT_RATIO,
               line_cap: Optional[int] = None, byte_budget: Optional[int] = None,
               short: Optional[str] = None, cursor: Optional[List[int]] = None) -> Optional[str]:
    """The synthetic English for one jp, or ``None`` when no marker fits the budget.

    ``line_cap`` is the in-game width of one ``\\n``-line (half-width units), ``byte_budget``
    the largest CP932 length allowed for the whole text.  The marker lands in the longest
    text piece; when it does not fit, ``short`` (a shorter marker) is tried, then ``None``.
    """
    pieces = segments(jp, kinds)
    if not any(kind == "txt" for kind, _ in pieces):
        return None
    cursor = cursor if cursor is not None else [0]

    # per-line fixed width (tokens, controls) and the text pieces of the line
    lines: List[List[int]] = [[]]
    for index, (kind, value) in enumerate(pieces):
        if kind == "nl":
            lines.append([])
        else:
            lines[-1].append(index)
    targets: Dict[int, int] = {}
    fixed_by_line: List[int] = []
    for line in lines:
        fixed = sum(export_strings.display_width(pieces[i][1]) for i in line
                    if pieces[i][0] != "txt")
        fixed_by_line.append(fixed)
        texts = [i for i in line if pieces[i][0] == "txt"]
        if not texts:
            continue
        units = {i: export_strings.display_width(pieces[i][1]) for i in texts}
        wanted = {i: max(1, math.ceil(units[i] * ratio)) for i in texts}
        room = None if line_cap is None else max(0, line_cap - fixed)
        if room is not None and sum(wanted.values()) > room:
            total = sum(units.values()) or 1
            wanted = {i: (units[i] * room) // total for i in texts}
        targets.update(wanted)

    if byte_budget is not None:
        fixed_bytes = sum(_token_bytes(v) if k == "tok" else 1
                          for k, v in pieces if k != "txt")
        room = max(0, byte_budget - fixed_bytes)
        if sum(targets.values()) > room:
            total = sum(targets.values()) or 1
            scaled = {i: (t * room) // total for i, t in targets.items()}
            # integer division may leave a few bytes unused; they go to the longest piece
            if scaled:
                longest = max(scaled, key=lambda i: (scaled[i], -i))
                scaled[longest] += room - sum(scaled.values())
            targets = scaled

    longest = max(targets, key=lambda i: (targets[i], -i))
    # a short jp split by tokens leaves every piece tiny: the marker piece borrows from
    # the other pieces of its line (any line when no line cap applies) - the per-line
    # width and the byte total do not change, so both budgets still hold
    line_of = {i: n for n, line in enumerate(lines) for i in line}
    deficit = len(marker) - targets[longest]
    donors = [i for i in targets
              if i != longest and (line_cap is None or line_of[i] == line_of[longest])]
    for donor in sorted(donors, key=lambda i: -targets[i]):
        if deficit <= 0:
            break
        take = min(targets[donor], deficit)
        targets[donor] -= take
        targets[longest] += take
        deficit -= take
    if targets[longest] < len(marker) and byte_budget is None:
        # no hard byte budget: the ratio is realism, not a limit - the marker piece gets at
        # least the marker (within the line's width; a 2-character jp name is a 5-letter
        # English word more often than not anyway)
        if line_cap is None:
            targets[longest] = len(marker)
        else:
            line = lines[line_of[longest]]
            used = fixed_by_line[line_of[longest]] + sum(
                targets[i] for i in line if i in targets and i != longest)
            targets[longest] = max(targets[longest], min(len(marker), line_cap - used))
    chosen = marker
    if targets[longest] < len(marker):
        if short is None or targets[longest] < len(short):
            return None
        chosen = short

    out: List[str] = []
    for index, (kind, value) in enumerate(pieces):
        if kind == "txt":
            out.append(_fill_words(targets[index], chosen if index == longest else "", cursor))
        else:
            out.append(value)
    return "".join(out)


# --------------------------------------------------------------------------- per row

def boxed(row: dict) -> bool:
    """Rows the writers measure against the 46-unit dialogue box."""
    if row.get("category") == "battle_quote":
        return True
    return row.get("category") == "dialogue" and row.get("kind") != "narration"


def narration(row: dict) -> bool:
    return row.get("category") == "dialogue" and row.get("kind") == "narration"


def constraints(rows: Sequence[dict]) -> Tuple[Optional[int], Optional[int]]:
    """The strictest ``(line_cap, byte_budget)`` over rows sharing one jp."""
    line_cap: Optional[int] = None
    budget: Optional[int] = None
    for row in rows:
        if boxed(row):
            line_cap = BOX_WIDTH if line_cap is None else min(line_cap, BOX_WIDTH)
        elif narration(row):
            line_cap = NARRATION_TARGET if line_cap is None else min(line_cap, NARRATION_TARGET)
        max_bytes = row.get("max_bytes")
        fixed = TC.fixed_slot_limit(row)             # the measured fixed-stride slot, if any
        if fixed is not None and (not isinstance(max_bytes, int) or fixed < max_bytes):
            max_bytes = fixed
        if isinstance(max_bytes, int) and max_bytes > 0:
            room = max_bytes - 1                     # one byte under the limit, on purpose:
            budget = room if budget is None else min(budget, room)   # a rehearsal, not a race
    return line_cap, budget


def problems_of(row: dict, en: str, pct) -> List[str]:
    """What the gate would say about this English: checker errors plus the box warnings."""
    probe = dict(row)
    probe["en"] = en
    errors, _warnings = TC.check_row(probe, pct=pct)
    if boxed(row) or narration(row):
        # the writers' rule: dialogue/quote lines are refused over 46, narration is noted
        # over 52 (event_text_apply) - the checker only warns, so it is enforced here
        cap = BOX_WIDTH if boxed(row) else 52
        for line in en.split("\n"):
            if export_strings.display_width(line) > cap:
                errors.append(f"a line is {export_strings.display_width(line)} wide, "
                              f"the box fits {cap}")
                break
    return errors


# --------------------------------------------------------------------------- selection

def selected(row: dict, containers: Optional[set], containerless: bool) -> bool:
    container = (row.get("source") or {}).get("container")
    if container is None:
        return containerless
    return containers is None or container in containers


def with_twins(candidates: List[dict], files: Dict[str, List[dict]]) -> List[dict]:
    """``candidates`` plus the rows the package check binds to them.

    The name files carry one row per container copy under the *same id* (``char:600:series``
    in ``config01.EDAT`` and in ``imenu01.EDAT``) and ``copy_of`` links between duplicates.
    ``translation_check`` demands that a copy and its source read the same, so when one of them
    is picked the whole id/copy_of group is filled - with the same English, since they share jp.
    Rows of skipped files are never added (they are not in ``files``' candidate pool).
    """
    by_id: Dict[str, List[dict]] = {}
    by_source: Dict[str, List[dict]] = {}
    for rows in files.values():
        for row in rows:
            by_id.setdefault(row.get("id"), []).append(row)
            if row.get("copy_of"):
                by_source.setdefault(row["copy_of"], []).append(row)
    chosen = {id(row) for row in candidates}
    out = list(candidates)
    queue = list(candidates)
    while queue:
        row = queue.pop()
        linked = list(by_id.get(row.get("id"), []))
        if row.get("copy_of"):
            linked += by_id.get(row["copy_of"], [])
        linked += by_source.get(row.get("id"), [])
        for twin in linked:
            if id(twin) not in chosen and twin.get("__file") == row.get("__file"):
                chosen.add(id(twin))
                out.append(twin)
                queue.append(twin)
    return out


def smoke_pick(rows: List[dict], token_map: Dict[str, Tuple[str, List[str]]]) -> List[dict]:
    """One row per (file, category/kind, member family, container), plus the group's first
    row with a dropped kana token and its first row with a carriage return."""
    groups: "OrderedDict[tuple, List[dict]]" = OrderedDict()
    for row in rows:
        source = row.get("source") or {}
        key = (row.get("__file"), row.get("category"), row.get("kind"),
               member_family(source.get("member")), source.get("container"))
        groups.setdefault(key, []).append(row)
    picked: List[dict] = []
    for members in groups.values():
        picked.append(members[0])
        kana = next((r for r in members[1:]
                     if "\x0f" in (r.get("jp") or "")
                     or "T" in kinds_for(r.get("jp") or "", token_map.get(r.get("id")))), None)
        if kana is not None:
            picked.append(kana)
        cr = next((r for r in members[1:] if "\r" in (r.get("jp") or "") and r is not kana), None)
        if cr is not None:
            picked.append(cr)
    return picked


# --------------------------------------------------------------------------- the run

def fill(package: Path, out: Path, *, containers: Optional[Iterable[str]] = None,
         containerless: bool = True, skip_files: Iterable[str] = (), smoke: bool = False,
         ratio: float = DEFAULT_RATIO) -> dict:
    """Write the filled package to ``out`` and return the report (also written there)."""
    package = Path(package)
    out = Path(out)
    if out.resolve() == package.resolve():
        raise FillError("--out must be a different folder than --package")
    container_set = set(containers) if containers is not None else None
    skip = {str(s)[:2] for s in skip_files}

    sidecar = TMAP.find_sidecar([package])
    token_map = TMAP.load_map(sidecar) if sidecar else {}

    files: Dict[str, List[dict]] = OrderedDict()
    for name in PACKAGE_FILES:
        path = package / name
        if path.exists():
            rows = ISW.read_package(path)
            for row in rows:
                row["__file"] = name
            files[name] = rows

    report: dict = {"package": str(package), "out": str(out), "smoke": smoke, "ratio": ratio,
                    "containers": sorted(container_set) if container_set is not None else None,
                    "containerless": containerless, "skip_files": sorted(skip),
                    "sidecar": str(sidecar) if sidecar else None,
                    "rows": 0, "selected": 0, "filled": 0, "distinct_jp": 0,
                    "unfilled": {}, "per_file": {}, "markers": {}}

    candidates: List[dict] = []
    for name, rows in files.items():
        report["rows"] += len(rows)
        if name[:2] in skip:
            continue
        for row in rows:
            if selected(row, container_set, containerless):
                candidates.append(row)
    if smoke:
        candidates = smoke_pick(candidates, token_map)
    candidates = with_twins(candidates, files)
    report["selected"] = len(candidates)

    # one English per distinct jp, under the strictest constraints of the rows sharing it
    groups: "OrderedDict[str, List[dict]]" = OrderedDict()
    for row in candidates:
        jp = row.get("jp") or ""
        groups.setdefault(jp, []).append(row)
    report["distinct_jp"] = len(groups)

    def note(reason: str, row: dict) -> None:
        bucket = report["unfilled"].setdefault(reason, {"rows": 0, "first": []})
        bucket["rows"] += 1
        if len(bucket["first"]) < 20:
            bucket["first"].append(row.get("id"))

    cursor = [0]
    ordinals: Dict[str, int] = {}
    index = 0
    for jp, members in groups.items():
        if not jp.strip():
            for row in members:
                note("empty jp", row)
            continue
        index += 1
        first = members[0]
        pct = next((token_map.get(r.get("id")) for r in members if r.get("id") in token_map), None)
        kinds = kinds_for(jp, pct)
        if smoke:
            code = smoke_code(first)
            ordinals[code] = ordinals.get(code, 0) + 1
            marker = marker_for(index, code, ordinals[code])
        else:
            marker = marker_for(index)
        line_cap, budget = constraints(members)
        en = synthesize(jp, kinds, marker, ratio=ratio, line_cap=line_cap, byte_budget=budget,
                        short=short_marker(index), cursor=cursor)
        if en is None:
            reason = "no text in jp (only tokens)" if not any(
                k == "txt" for k, _ in segments(jp, kinds)) else "marker does not fit the budget"
            for row in members:
                note(reason, row)
            continue
        landed = 0
        for row in members:
            problems = problems_of(row, en, token_map.get(row.get("id")))
            if problems:
                note("gate: " + problems[0].split(":")[0][:60], row)
                continue
            row["en"] = en
            landed += 1
            report["filled"] += 1
            per = report["per_file"].setdefault(row["__file"], {"selected": 0, "filled": 0})
            per["filled"] += 1
        if landed:
            # smoke: marker -> the row id it stands for (never the Japanese text itself)
            report["markers"][marker] = first.get("id") if smoke else landed
    for row in candidates:
        per = report["per_file"].setdefault(row["__file"], {"selected": 0, "filled": 0})
        per["selected"] += 1

    out.mkdir(parents=True, exist_ok=True)
    for name, rows in files.items():
        with (out / name).open("w", encoding="utf-8") as handle:
            for row in rows:
                clean = {k: v for k, v in row.items() if not k.startswith("__")}
                handle.write(json.dumps(clean, ensure_ascii=False) + "\n")
    for extra in ("06_scenes.jsonl", "index.json", "name_map.tsv"):
        if (package / extra).exists():
            shutil.copy2(package / extra, out / extra)
    if sidecar:
        shutil.copy2(sidecar, out / TMAP.SIDECAR_NAME)
    if not smoke:
        report["markers"] = {"count": len(report["markers"])}
    (out / "fill_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, required=True, help="the base package folder")
    parser.add_argument("--out", type=Path, required=True, help="where the filled copy goes")
    parser.add_argument("--containers", nargs="*", default=None,
                        help="only rows of these containers (names, e.g. config00.cpk)")
    parser.add_argument("--dlc", type=Path, nargs="*", default=[],
                        help="folders whose file names are the containers you have")
    parser.add_argument("--no-containerless", action="store_true",
                        help="drop the rows without a container (08 dictionary names)")
    parser.add_argument("--skip-files", nargs="*", default=[],
                        help="package files to leave empty, by prefix (e.g. 03)")
    parser.add_argument("--smoke", action="store_true",
                        help="one row per category/member family: a small smoke package")
    parser.add_argument("--ratio", type=float, default=DEFAULT_RATIO,
                        help=f"English width per Japanese width (default {DEFAULT_RATIO})")
    args = parser.parse_args(argv)

    containers = None
    if args.containers is not None or args.dlc:
        containers = set(args.containers or [])
        for folder in args.dlc:
            containers.update(p.name for p in Path(folder).rglob("*") if p.is_file())
    report = fill(args.package, args.out, containers=containers,
                  containerless=not args.no_containerless, skip_files=args.skip_files,
                  smoke=args.smoke, ratio=args.ratio)
    print(f"wiersze w pakiecie: {report['rows']}; wybrane: {report['selected']}; "
          f"wypełnione: {report['filled']} ({report['distinct_jp']} różnych jp)")
    for reason, bucket in report["unfilled"].items():
        print(f"  niewypełnione - {reason}: {bucket['rows']}")
    for name, per in report["per_file"].items():
        print(f"  {name}: {per['filled']}/{per['selected']}")
    print(f"zapisano: {args.out} (fill_report.json obok)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
