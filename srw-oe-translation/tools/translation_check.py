#!/usr/bin/env python3
"""Check a filled-in translation package before it goes back into the game files.

The checher is deliberately strict about everything the game cares about and forgiving about style:

* every ``en`` must be CP932-encodable (the font's charset is CP932),
* the control characters the game draws with (``\r`` clears the box, ``0x0F`` switches to half
  width) must stay exactly as they are,
* the ordered list of control tokens must match ``jp`` (``＠0``…``＠9``, ``%s``, ``%%``, ``％s``,
  ``＄n``, ``＃``, ``{XX}`` — the game substitutes them), with one measured exception: the ``%s``
  of the display form that stand for a kana token ``0x0F xx`` (one voiced-kana glyph) must be
  DROPPED from the English together with the character after them, exactly like the ``<0x0F>``
  marker of the raw form.  Which ``%s`` is which only the raw bytes know, so the checker reads
  the sidecar ``tokeny.tsv`` (``tools/token_map.py``) next to the package; without it the old
  strict rule applies (every ``%s`` of jp must appear in the English),
* the number of ``\\n`` line breaks must match ``jp`` (the dialogue boxes and list rows are drawn
  around them),
* ``max_bytes`` (a fixed slot) is a hard error, ``suggested_max`` (item/skill UI width) is a warning;
  for the fixed-stride tables ``mission_text`` measured (mission titles, BGM, map/background/group
  names) the measured slot size is the limit even when an older package row claims more,
* a dialogue or battle-quote line wider than the in-game box (``export_strings.box_limit`` - the
  widest line the game itself draws for that kind - half-width units) is
  a warning: the game draws the box around ``jp`` and clips anything wider.

Rows with an empty ``en`` are reported as untranslated, not as errors, so the check can be run while
translating.  ``--require-complete`` turns them into errors for a release check.

The text is compared **as it is written**, not stripped: a third of the Japanese dialogue lines end
with a real line break, and stripping the translation would report a break mismatch on correct work.
Only a whitespace-only ``en`` counts as untranslated.

Usage::

    python tools/translation_check.py --package local/translation
    python tools/translation_check.py --package local/translation --require-complete --strict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import export_strings  # noqa: E402
import item_skill_write as ISW  # noqa: E402
import mission_text as MT  # noqa: E402
import token_map as TMAP  # noqa: E402

EXT_DAT_RECORD = 388   # the measured one-record ``*_ext.dat`` file (mission_text)
TOKEN_RE = re.compile(r"＠[0-9]|%%|%s|％[A-Za-z0-9]+|＄[0-9]*|＃|\{[0-9A-Fa-f]{2}\}")
BOX_WIDTH = export_strings.TYPICAL_LINE   # the typical dialogue line (46); the hard limit per
BOXED = ("dialogue", "battle_quote")      # kind is export_strings.box_limit, as in the writers
CATEGORIES = ("dialogue", "quote", "item", "skill", "config", "mission", "name")

# List columns measured on the user's in-game screenshot of the unit list (2026-10-15, PPSSPP at
# 1967 px wide = 4.1x; half-width glyph pitch ~7 PSP px, full-width ~13 px): the unit-name column
# is ~105 px = 14.6 half-width cells and the pilot column starts at cell 15, so an ASCII name of
# 15 cells already touches the pilot name (the game squeezes full-width Japanese to fit, never
# ASCII).  ``unit_name`` (unit_list ``name``) is the list column -> hard limit; the pilot column
# (``name_short``/``name_narrow``, which of the two the list draws is not measured) -> warning.
LIST_CELLS = {"unit_name": 14}
LIST_CELLS_SOFT = {"character_name_short": 14, "character_name_narrow": 14}

# ``%s`` whose JP completion byte is the second half of a kana glyph.  The engine fills ``%s`` with
# a pool fragment; 88 Skill00 fragments end in a dangling lead byte (0x0F kana lead, ``＠`` colour
# lead, ``%``) that the byte right after ``%s`` in the record completes.  The only 0x0F case is
# fragment 150 ``ｸﾞﾙｰ<0F>`` + ``4`` = ｸﾞﾙｰﾌﾟ (group); its English fragment ``Group`` has no dangling
# byte, so an English record that keeps ``%s4`` shows ``Group4`` in the game (seen in build #17,
# battle weapon panel of Coord. Atk).  Measured list: 9 occurrences in 8 records (r236 twice).
# The value is (byte, occurrences); the other ``%s4`` of the record (r240: the level of
# ``連携攻撃%s4``) are numbers and stay, so the rule is a count: the English may keep at most
# ``jp.count("%s4") - occurrences`` of them.
COMPLETION_BYTE = {
    f"skill:config00.cpk/srwDL_Skill00.bin:r{n}:effect": ("4", 2 if n == 236 else 1)
    for n in (236, 237, 238, 239, 240, 241, 651, 652)
}


def tokens(text: str) -> List[str]:
    """Control tokens of one string, in order."""
    return TOKEN_RE.findall(text)


def expected_tokens(jp: str, pct: Optional[Tuple[str, List[str]]] = None) -> List[str]:
    """The ordered control tokens the English line must carry.

    ``pct`` is the sidecar entry of the row (``tokeny.tsv``: the row's jp and one kind letter
    per ``%s`` of that jp - ``L`` literal placeholder, ``T`` kana token ``0x0F xx``, ``C`` other
    control).  With a matching entry the kana tokens drop out of the expected list: they draw
    one voiced kana glyph, which has no place in an English line (the raw-form rows follow the
    same rule - the validator below refuses any 0x0F in ``en``).  Every other token stays
    mandatory, count and order.  Without the sidecar - or with a stale entry (jp differs or the
    kinds count differs) - the strict list applies: every token of jp, every ``%s`` included.
    """
    found = tokens(jp)
    if pct is None:
        return found
    map_jp, kinds = pct
    if map_jp != jp or len(kinds) != found.count("%s"):
        return found                        # stale sidecar entry: fail closed, strict rule
    expected: List[str] = []
    index = 0
    for token in found:
        if token == "%s":
            if kinds[index] != "T":
                expected.append(token)
            index += 1
        else:
            expected.append(token)
    return expected


def kana_signatures(jp: str, pct: Optional[Tuple[str, List[str]]]) -> List[str]:
    """How each kana token of a display-form jp looks on the page: ``%s`` plus the character
    after it (the glyph's second byte, ``%s*`` ``%s&`` in ``%s*ﾒｰ%s&`` = ﾀﾞﾒｰｼﾞ), in order.

    Empty without a sidecar entry, with a stale one (jp or ``%s`` count differs) and for jp
    without kana tokens - the same fail-closed rule as ``expected_tokens``.
    """
    if pct is None:
        return []
    map_jp, kinds = pct
    hits = [match for match in re.finditer(r"%s", jp)]
    if map_jp != jp or len(kinds) != len(hits):
        return []
    return [jp[match.start():match.end() + 1]
            for kind, match in zip(kinds, hits) if kind == "T"]


def strip_kana_tokens(en: str, jp: str, pct: Optional[Tuple[str, List[str]]]) -> str:
    """Drop from the English the kana tokens a translator copied over from the jp.

    The views render a kana token ``0x0F xx`` as ``%s`` followed by the glyph's second byte,
    so a translator who keeps every placeholder writes ``%s*%s&Damage`` for ``%s*ﾒｰ%s&``.  The
    token draws one voiced kana glyph and has no place in an English line (``expected_tokens``
    drops it, the writers never emit it), so each ``%s`` the sidecar marks as ``T`` is removed
    from the English together with the character after it - but only as the exact pair the jp
    shows (``%s*``), never a bare ``%s`` that could be a literal placeholder the English must
    keep.  Each pair is removed once, in the order of the jp; anything else stays as written,
    and without a matching sidecar entry the text comes back untouched.  An English that
    already carries only the mandatory tokens is returned as is.
    """
    signatures = kana_signatures(jp, pct)
    keep = jp.count("%s") - len(signatures)          # the literal/control %s the EN must carry
    if not signatures or en.count("%s") <= keep:
        return en
    out = en
    for signature in signatures:
        position = out.find(signature)
        if position < 0:
            continue
        out = out[:position] + out[position + len(signature):]
    return out


def same_tokens(found: List[str], expected: List[str]) -> bool:
    """``True`` when the English carries the expected tokens: same count of each, and the same
    order of every token that does something - ``%%`` is the escaped literal percent sign, it
    consumes no argument and colours nothing, so the English may move it with the number it
    belongs to (``%sの14%%にする`` -> ``14%% of %s``)."""
    return found.count("%%") == expected.count("%%") and \
        [token for token in found if token != "%%"] == \
        [token for token in expected if token != "%%"]


def controls(text: str) -> List[int]:
    """Every control character except the plain line break, as code points (CR, 0x0F, ...).

    ``\\r`` (0x0D) clears the dialogue box - dropping it silently breaks the display, so the
    check treats it as structural. ``0x0F`` is different: it is the lead byte of a two-byte
    token ``0x0F xx`` (xx always 0x20-0x39 in this game, verified across the whole package)
    that draws one voiced half-width kana glyph; the byte after it is part of the glyph, not
    text. English has no voiced kana, so the EN text must carry NO 0x0F at all - keeping it
    before a Latin letter would make the game swallow that letter as the token's second byte.
    """
    return sorted(ord(ch) for ch in text if ord(ch) < 32 and ch != "\n")


def list_cells(text: str) -> int:
    """Width of a list cell in half-width cells: one per CP932 byte of the drawn characters.

    The game's font has one full-width glyph for every two-byte CP932 code (``∞``, ``α``, ``※``
    included - ``export_strings.display_width`` counts those East-Asian-ambiguous characters as
    one) and one half-width glyph per single byte (ASCII, half-width kana).
    """
    drawn = "".join(ch for ch in text if unicodedata.category(ch) != "Cc")
    try:
        return len(drawn.encode("cp932"))
    except UnicodeEncodeError:
        return export_strings.display_width(drawn)


def encode(text: str) -> Optional[str]:
    """None when the text encodes to CP932, otherwise the failure message."""
    try:
        text.encode("cp932")
    except UnicodeEncodeError as exc:
        return f"not CP932-encodable ({exc.reason} at {exc.start})"
    return None


def fixed_slot_limit(row: dict) -> Optional[int]:
    """``max_bytes`` the measured fixed-stride slot allows (size - NUL), or None for other rows.

    The ``05`` rows (and the leftover rows pointing at the same tables) carry the member and
    the slot's offset; ``mission_text.slot_size_at`` knows the field sizes.  The one-record
    ``*_ext.dat`` kinds take the file as the record: a row does not carry the file size, so the
    measured 388-byte record is assumed (every slot of the two 348-byte files lies below it).
    """
    source = row.get("source") or {}
    member = source.get("member")
    offset = source.get("offset")
    if not member or not isinstance(offset, int):
        return None
    size = MT.slot_size_at(member, offset, EXT_DAT_RECORD if member.lower().endswith("_ext.dat")
                           else None)
    return None if size is None else size - 1


def check_row(row: dict, require_complete: bool = False,
              pct: Optional[Tuple[str, List[str]]] = None) -> Tuple[List[str], List[str]]:
    """(errors, warnings) for one package row; ``pct`` is its ``tokeny.tsv`` entry."""
    errors: List[str] = []
    warnings: List[str] = []
    text = row.get("en") or ""
    jp = row.get("jp") or ""
    if not text.strip():
        message = "untranslated (empty en)"
        (errors if require_complete else warnings).append(message)
        return errors, warnings
    problem = encode(text)
    if problem:
        errors.append(problem)
    expected = expected_tokens(jp, pct)
    if not same_tokens(tokens(text), expected):
        if expected != tokens(jp):
            errors.append(f"control tokens changed: the English must carry {expected} (the kana "
                          f"tokens 0x0F of the jp are dropped with their glyph, tokeny.tsv), "
                          f"got {tokens(text)}")
        else:
            errors.append(f"control tokens changed: {tokens(jp)} -> {tokens(text)}")
    if text.count("\n") != jp.count("\n"):
        errors.append(f"line breaks changed: {jp.count(chr(10))} -> {text.count(chr(10))}")
    jp_controls = [code for code in controls(jp) if code != 0x0F]
    en_controls = controls(text)
    if 0x0F in en_controls:
        errors.append("the <0x0F> token must not stay in the English text - in Japanese it and "
                      "the character after it are one voiced kana glyph; write the English plain")
    if [code for code in en_controls if code != 0x0F] != jp_controls:
        errors.append("control characters changed: "
                      f"{[hex(code) for code in controls(jp)]} -> "
                      f"{[hex(code) for code in en_controls]}")
    size = len(text.encode("cp932")) if not problem else 0
    fixed = fixed_slot_limit(row)
    if fixed is not None and (row.get("max_bytes") is None or fixed < row["max_bytes"]):
        if size > fixed:
            errors.append(f"over budget: {size} > the measured {fixed + 1}-byte slot "
                          f"(max_bytes {fixed}; the package row says {row.get('max_bytes')})")
    elif row.get("max_bytes") is not None and size > row["max_bytes"]:
        errors.append(f"over budget: {size} > max_bytes {row['max_bytes']}")
    elif row.get("suggested_max") and size > row["suggested_max"]:
        warnings.append(f"wider than the game's field: {size} > suggested_max {row['suggested_max']}")
    for side, jp_edge, en_edge in (("leading", jp[:1], text[:1]), ("trailing", jp[-1:], text[-1:])):
        if en_edge.isspace() and en_edge != "\n" and not jp_edge.isspace():
            warnings.append(f"{side} whitespace {en_edge!r} that the jp does not have - the "
                            "writers keep it exactly as written")
    limit_cells = LIST_CELLS.get(row.get("category") or "")
    soft_cells = LIST_CELLS_SOFT.get(row.get("category") or "")
    if limit_cells is not None or soft_cells is not None:
        width = list_cells(text)
        if limit_cells is not None and width > limit_cells:
            errors.append(f"too wide for the unit list column: {width} half-width cells, the "
                          f"column fits {limit_cells} (ASCII is never squeezed by the game)")
        elif soft_cells is not None and width > soft_cells:
            warnings.append(f"wider than the pilot column of the unit list: {width} half-width "
                            f"cells, measured {soft_cells} (fine for enemies that never sit in "
                            "the list)")
    completion = COMPLETION_BYTE.get(row.get("id") or "")
    if completion:
        byte, occurrences = completion
        allowed = max(jp.count("%s" + byte) - occurrences, 0)
        if text.count("%s" + byte) > allowed:
            errors.append(f"the byte '{byte}' right after %s is the second half of a kana glyph "
                          f"(pool fragment ｸﾞﾙｰ<0F> + '{byte}' = ｸﾞﾙｰﾌﾟ) in {occurrences} place(s); "
                          "the English fragment is 'Group', so write '%s' alone there or the game "
                          f"shows 'Group{byte}' (at most {allowed} '%s{byte}' may stay)")
    if row.get("category") in BOXED:
        # the same rule the writers refuse by: wider than the game's own widest line of the kind
        kind = row.get("kind") or row.get("category")
        limit = export_strings.box_limit(kind)
        widths = [export_strings.display_width(line) for line in text.split("\n")]
        over = [width for width in widths if width > limit]
        if over and kind != "narration":   # narration is a note in the writer, not a refusal
            which = widths.index(max(widths)) + 1
            warnings.append(f"line {which} is {max(widths)} wide, the in-game box fits {limit} "
                            f"({kind})")
    return errors, warnings


def check_rows(rows: Iterable[dict], require_complete: bool = False,
               token_map: Optional[Dict[str, Tuple[str, List[str]]]] = None) -> dict:
    """Per-file counters plus the first problems of every kind.

    Rows that a DLC re-release repeats carry ``copy_of``: the translation is not written twice, so
    an empty copy is not a problem as long as its source is empty too, and a filled copy must equal
    its source (``tools/translation_copy.py`` fills them).
    """
    rows = list(rows)
    by_id = {row["id"]: row for row in rows if row.get("id")}
    report = {"files": {}, "errors": [], "warnings": [], "structural_rows": 0}
    for row in rows:
        name = row.get("_file") or row.get("category") or "?"
        if "jp" not in row and "en" not in row:
            report["structural_rows"] += 1          # 06_scenes: an index, nothing to translate
            continue
        bucket = report["files"].setdefault(name, {"rows": 0, "filled": 0, "empty": 0,
                                                   "errors": 0, "warnings": 0})
        bucket["rows"] += 1
        pct = token_map.get(row.get("id")) if token_map else None
        errors, warnings = check_row(row, require_complete, pct=pct)
        source = by_id.get(row.get("copy_of")) if row.get("copy_of") else None
        if source is not None:
            if (row.get("en") or "").strip() and (row["en"] or "") != (source.get("en") or ""):
                errors.append("copy differs from its source row "
                              f"({row['copy_of']})")
            elif not (row.get("en") or "").strip() and (source.get("en") or "").strip() \
                    and not require_complete:
                warnings.append(f"copy of {row['copy_of']} can be filled by "
                                "tools/translation_copy.py")
        if (row.get("en") or "").strip():
            bucket["filled"] += 1
        else:
            bucket["empty"] += 1
        bucket["errors"] += len(errors)
        bucket["warnings"] += len(warnings)
        row_id = row.get("id", "?")
        report["errors"].extend(f"{row_id}: {message}" for message in errors[:3])
        report["warnings"].extend(f"{row_id}: {message}" for message in warnings[:3])
        if len(report["errors"]) > 400 and len(report["warnings"]) > 400:
            break
    for message, ids in conflicting_duplicates(rows):
        for row_id in ids:
            report["errors"].append(f"{row_id}: {message}")
            name = by_id[row_id].get("_file") or by_id[row_id].get("category") or "?"
            if name in report["files"]:
                report["files"][name]["errors"] += 1
    report["totals"] = {
        "rows": sum(b["rows"] for b in report["files"].values()),
        "filled": sum(b["filled"] for b in report["files"].values()),
        "empty": sum(b["empty"] for b in report["files"].values()),
        "errors": sum(b["errors"] for b in report["files"].values()),
        "warnings": sum(b["warnings"] for b in report["files"].values()),
    }
    return report


RECORD_MEMBERS = ("srwDL_Skill00.bin", "srwDL_Item00.bin")   # conv-B record members scanned twice


def conflicting_duplicates(rows: Iterable[dict]) -> List[Tuple[str, List[str]]]:
    """Rows of one record member that carry the same Japanese with different English.

    ``03_skills.jsonl``/``02_items.jsonl`` hold the record roles and ``04_config_text.jsonl``
    scans the same members again under offset ids (``config_skill``/``config_item``).  The
    writer (``item_skill_write``) merges the rows per record role and, when two rows disagree,
    SKIPS THE WHOLE RECORD and only notes it in ``build_report.json`` (``skipped``: "two rows,
    two translations") - build #18, first run: record 236 (Coord. Atk) stayed Japanese in all
    four roles.  Caught here as an error on every row of the conflict.
    """
    groups: Dict[Tuple[str, str, str], Dict[str, List[str]]] = {}
    for row in rows:
        source = row.get("source") or {}
        if source.get("member") not in RECORD_MEMBERS or not (row.get("en") or "").strip():
            continue
        key = (source.get("container") or "", source["member"], row.get("jp") or "")
        groups.setdefault(key, {}).setdefault(row["en"], []).append(row.get("id", "?"))
    problems = []
    for (container, member, _jp), by_en in groups.items():
        if len(by_en) < 2:
            continue
        ids = [row_id for id_list in by_en.values() for row_id in id_list]
        problems.append((f"{len(by_en)} different translations of the same {member} string in "
                         f"{container} ({', '.join(ids)}) - the writer skips the whole record; "
                         "give every row the same English", ids))
    return problems


def format_report(report: dict) -> str:
    lines = ["# Raport kontroli pakietu", ""]
    lines.append(f"{'plik':<28}{'wiersze':>8}{'wypełnione':>12}{'puste':>8}{'błędy':>7}{'uwagi':>7}")
    for name in sorted(report["files"]):
        bucket = report["files"][name]
        lines.append(f"{name:<28}{bucket['rows']:>8}{bucket['filled']:>12}{bucket['empty']:>8}"
                     f"{bucket['errors']:>7}{bucket['warnings']:>7}")
    totals = report["totals"]
    lines.append("")
    lines.append(f"RAZEM: {totals['rows']} wierszy, {totals['filled']} wypełnionych, "
                 f"{totals['empty']} pustych, {totals['errors']} błędów, {totals['warnings']} uwag")
    if report.get("structural_rows"):
        lines.append(f"(pominięto {report['structural_rows']} wierszy strukturalnych: 06_scenes)")
    for label, key in (("BŁĘDY", "errors"), ("UWAGI", "warnings")):
        if report[key]:
            lines.append("")
            lines.append(f"## {label} (pierwsze {min(len(report[key]), 200)})")
            lines.extend("  " + line for line in report[key][:200])
    return "\n".join(lines) + "\n"


def collect(paths: Iterable[Path]) -> List[dict]:
    """Package rows of every ``*.jsonl`` given; each row remembers its file name."""
    rows, files = ISW.collect_rows(paths)
    by_name = {}
    for path in files:
        for row in ISW.read_package(path):
            row["_file"] = path.name
            by_name.setdefault(path.name, []).append(row)
    # the scene index is read first so the copy check can see every package row
    return [row for name in sorted(by_name) for row in by_name[name]]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, nargs="+", required=True,
                        help="package JSONL files, or a directory holding them")
    parser.add_argument("--out", type=Path, default=None, help="where to write the text report")
    parser.add_argument("--require-complete", action="store_true",
                        help="treat an empty en as an error (release check)")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any error")
    parser.add_argument("--token-map", type=Path, default=None,
                        help="tokeny.tsv with the %%s kinds (default: next to the package)")
    args = parser.parse_args(argv)

    rows = collect(args.package)
    sidecar = args.token_map or TMAP.find_sidecar(list(args.package))
    token_map = TMAP.load_map(sidecar) if sidecar else {}
    if sidecar:
        print(f"mapa tokenów: {sidecar} ({len(token_map)} wierszy)")
    else:
        print("mapa tokenów: brak (tokeny.tsv obok pakietu) - każde %s z jp musi zostać w EN")
    report = check_rows(rows, require_complete=args.require_complete, token_map=token_map)
    text = format_report(report)
    print(text)
    out = args.out or (args.package[0] / "check_report.txt" if args.package[0].is_dir()
                       else Path("local/translation/check_report.txt"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("wrote", out)
    if args.strict and report["totals"]["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
