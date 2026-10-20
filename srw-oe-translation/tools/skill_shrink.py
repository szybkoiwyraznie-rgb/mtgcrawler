#!/usr/bin/env python3
"""Shrink the English of ``srwDL_Skill00.bin`` to its in-game size budget (package -> package).

Why
---
The skill table of ``config00.cpk`` has a conservative runtime-safety budget based on
2026-10-14/15 PPSSPP tests: Japanese text padded with spaces loaded at 217 090 B
but failed at Loading at 218 110 B; a smaller enclosing archive did not rescue a
228 202 B member. These tests do not identify an exact fixed buffer or rule out a
shared allocation arena. The builder guard is 216 768 B, with a safety margin.
The full English of the 2026-10-14 package needs 228 202 B (+19 244 B over Japanese).
Shortening text is the existing supported way to fit the guard; structural storage
optimisations or an engine allocation patch are not established as impossible,
but require separate research and validation. This tool makes shortening reproducible
and reviewable instead of hand-editing 4 900 rows.

What
----
Reads a translation package (the JSONL files the builder consumes), rewrites the English of
every ``srwDL_Skill00.bin`` row - the record fields in ``03_skills.jsonl`` and the fragment-pool
and offset rows in ``04_config_text.jsonl`` - with one rule table, measures the member the
builder would produce (pool first, then the records, exactly like ``build_translation_patch``),
and writes a package copy plus a review TSV of every changed row.  Rows of other members are
copied untouched.

Rules (``config/skill_shrink_rules.tsv``; UTF-8, ``kind<TAB>from<TAB>to``, ``#`` comments):

``name``
    exact base name of a skill -> shorter name.  Applies to ``name``, to ``name_level``
    (``X LvN`` -> ``Y LN``), to a pool fragment equal to the name and to the coloured
    ``<X>`` / ``<X%sN>`` header a long effect text starts with.
``phrase``
    literal substring replacement, applied in file order to every English that is not a name.
``exact``
    whole-string replacement for one English text (tried before and after the phrases, so the
    key may be the package's text or the text the phrases produce).

Built in: the level suffix ``' LvN'`` becomes ``' LN'`` (the English SRW convention), unless
``--keep-lv``.

Guards: the tokens of a row (``%s``, ``%%``, ``＠n``, ``％x``, ``＄``, ``＃``, line breaks) must
survive in the same order and the result must be CP932-encodable - a rule that breaks either
leaves the row's English alone and the row is reported.  The same function rewrites the ``03``
and ``04`` rows of one field, so the two sources never disagree (``merge_edits`` would refuse the
record).  Exit status 1 when the measured member is still over the budget.

The DLC fragment pools (2026-10-15, test Y)
-------------------------------------------
``config01-08.EDAT`` each carry ``srwDL_Skill0N.bin``: a convention-C pool of the same 720
fragments that sit in the tail pool of ``Skill00`` (every chapter has its own copy).  In the
game, ORIGINAL ISO + the eight rebuilt EDATs crashed at "Loading" with the stack of the Skill00
size crash, while the rebuilt ISO with ORIGINAL EDATs booted - the only growth in those EDATs
that matters by size is the pools (+1 758 B each).  Whether the budget is one arena for
Skill00 + the eight pools or a 16 KiB slot per pool is open; both readings are satisfied by
"no pool larger than its original" (``POOL_LIMIT``) plus "Skill00 + 8 pools no larger than the
largest total that ever booted" (``SKILL_TOTAL_LIMIT``), so those are the gates here.

Hence ``--dlc-original DIR`` (folder with the original ``config01..08.EDAT``): the pool rows of
``04`` get the English of the Skill00 row with the same Japanese (one pool text per fragment,
shortened by the same rules; the pools were at the pre-shrink English before) and ``copy_of``
pointing at that row, every pool is measured with the real pool writer, and the exit status
is 1 when a pool or the total is over its budget.

Usage::

    python tools/skill_shrink.py --package local/pakiet --original local/usrdir/config00.cpk \\
        --dlc-original local/inputs --rules config/skill_shrink_rules.tsv \\
        --out local/pakiet_ciasny --report local/shrink.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import container_mix as CM  # noqa: E402
import item_skill_records as ISR  # noqa: E402
import item_skill_write as ISW  # noqa: E402
import table_write as TW  # noqa: E402

MEMBER = "srwDL_Skill00.bin"
POOL_RE = re.compile(r"^srwDL_Skill0([1-8])\.bin$")
# Every original DLC pool is 15 638 B (8 header + 720 x 4 offsets + 12 750 B of text).  The
# in-game result "original ISO + rebuilt EDATs (pools 17 396 B) crashes at Loading, rebuilt ISO
# (Skill00 216 518 B) + original EDATs boots" is read conservatively: a pool may not outgrow its
# original, and Skill00 + the eight pools may not exceed the largest total that booted
# (variant W1: 217 090 + 8 x 15 638).  Relax only after a measured in-game ladder.
POOL_LIMIT = 15_638
SKILL_TOTAL_LIMIT = 342_194
SKILLS_FILE = "03_skills.jsonl"
CONFIG_FILE = "04_config_text.jsonl"
RULE_KINDS = ("name", "phrase", "exact")
LEVEL_RE = re.compile(r"^(.*\S) Lv(\d{1,2})$")
HEADER_RE = re.compile(r"<([^<>%\n]+?)(%s\d*)?>")
GUARD_RE = re.compile(r"＠[0-9]|%%|%s|％[A-Za-z0-9]+|＄[0-9]*|＃|\n")


class ShrinkError(Exception):
    """A rule file or package the tool refuses to work on."""


class Rules:
    def __init__(self) -> None:
        self.names: Dict[str, str] = {}
        self.phrases: List[Tuple[str, str]] = []
        self.exacts: Dict[str, str] = {}

    def __len__(self) -> int:
        return len(self.names) + len(self.phrases) + len(self.exacts)


def load_rules(path: Path) -> Rules:
    """The rule table; a malformed line refuses the whole file (fail closed)."""
    rules = Rules()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.rstrip("\r").split("\t")
        if len(parts) != 3 or parts[0] not in RULE_KINDS or not parts[1]:
            raise ShrinkError(f"{path.name}:{number}: expected kind<TAB>from<TAB>to with kind in "
                              f"{RULE_KINDS}, got {line!r}")
        kind, src, dst = parts
        src = src.replace("\\n", "\n")
        dst = dst.replace("\\n", "\n")
        if kind == "name":
            if src in rules.names and rules.names[src] != dst:
                raise ShrinkError(f"{path.name}:{number}: name {src!r} mapped twice")
            rules.names[src] = dst
        elif kind == "phrase":
            rules.phrases.append((src, dst))
        else:
            if src in rules.exacts and rules.exacts[src] != dst:
                raise ShrinkError(f"{path.name}:{number}: exact {src!r} mapped twice")
            rules.exacts[src] = dst
    return rules


def split_level(en: str) -> Tuple[str, Optional[str]]:
    match = LEVEL_RE.match(en)
    if match:
        return match.group(1), match.group(2)
    return en, None


def shorten(en: str, rules: Rules, known_names: Iterable[str], level_suffix: str = " L") -> str:
    """The shorter English of one row (names, level suffix, exact texts, phrases, headers)."""
    base, level = split_level(en)
    if base in rules.names or base in known_names:
        short = rules.names.get(base, base)
        return short + (f"{level_suffix}{level}" if level is not None else "")
    if en in rules.exacts:
        return rules.exacts[en]
    out = en
    if rules.names:
        out = HEADER_RE.sub(
            lambda m: "<" + rules.names.get(m.group(1), m.group(1)) + (m.group(2) or "") + ">",
            out)
    for src, dst in rules.phrases:
        out = out.replace(src, dst)
    return rules.exacts.get(out, out)


def guard_problem(before: str, after: str) -> Optional[str]:
    """Why ``after`` may not replace ``before`` (tokens changed, not CP932), or None."""
    if GUARD_RE.findall(before) != GUARD_RE.findall(after):
        return "the rewrite changes the tokens (%s / ＠n / line breaks)"
    try:
        after.encode("cp932")
    except UnicodeEncodeError as exc:
        return f"not CP932-encodable: {exc}"
    if not after.strip():
        return "the rewrite leaves the text empty"
    return None


# ----------------------------------------------------------------------------- the package

def read_jsonl(path: Path) -> List[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def is_skill00(row: dict) -> bool:
    return (row.get("source") or {}).get("member") == MEMBER


def identity(row: dict) -> bool:
    """English == Japanese up to surrounding whitespace: the builder leaves such bytes alone
    (``build_translation_patch.identity``; `` Lv`` copied back as ``Lv`` must not lose its space),
    so the measurement and the rewrite skip these rows too."""
    en, jp = row.get("en"), row.get("jp")
    return isinstance(en, str) and isinstance(jp, str) and bool(en.strip()) \
        and en.strip() == jp.strip()


def translated(row: dict) -> bool:
    """A Skill00 row the builder would write: filled English that is not the Japanese."""
    return is_skill00(row) and filled(row)


def filled(row: dict) -> bool:
    """Any row the builder would write: filled English that is not the Japanese."""
    return bool(TW.english(row)) and not identity(row)


def known_skill_names(rows3: Iterable[dict]) -> set:
    return {row["en"] for row in rows3
            if is_skill00(row) and row.get("part") == "name" and TW.english(row)}


def rewrite_rows(rows: List[dict], rules: Rules, names: set, level_suffix: str
                 ) -> Tuple[List[dict], List[dict], List[str]]:
    """(rows with the Skill00 English rewritten, change records, guard refusals)."""
    out, changes, refused = [], [], []
    for row in rows:
        if not translated(row):
            out.append(row)
            continue
        en = TW.english(row)
        new = shorten(en, rules, names, level_suffix)
        if new == en:
            out.append(row)
            continue
        problem = guard_problem(en, new)
        if problem:
            refused.append(f"{row.get('id')}: {problem}: {en!r} -> {new!r}")
            out.append(row)
            continue
        copy = dict(row)
        copy["en"] = new
        out.append(copy)
        changes.append({"id": row.get("id"), "part": row.get("part"), "jp": row.get("jp"),
                        "before": en, "after": new,
                        "saved": len(en.encode("cp932")) - len(new.encode("cp932"))})
    return out, changes, refused


# ----------------------------------------------------------------------------- the measurement

def skill00_blob(original: Path) -> bytes:
    _, subs, _ = CM.members_of(original)
    if MEMBER not in subs:
        raise ShrinkError(f"{original}: no {MEMBER} inside")
    return subs[MEMBER]


def measure(blob: bytes, rows3: List[dict], rows4: List[dict]) -> dict:
    """The member the builder would produce from these rows: pool first, then the records."""
    parsed = ISR.parse_member(blob, "skill", MEMBER)
    if parsed["errors"]:
        raise ShrinkError(f"{MEMBER} does not parse: {parsed['errors'][:2]}")
    tail = parsed["tail_offset"]
    rows3 = [r for r in rows3 if translated(r)]
    rows4 = [r for r in rows4 if translated(r)
             and isinstance((r.get("source") or {}).get("offset"), int)]
    pool_rows = [r for r in rows4 if r["source"]["offset"] >= tail]
    offset_rows = [r for r in rows4 if r["source"]["offset"] < tail]
    pool_edits, pool_skipped, pool_stats = ISW.plan_pool_edits(pool_rows, MEMBER, parsed, blob)
    pooled = ISW.rebuild_pool(blob, parsed, pool_edits)
    parsed2 = ISR.parse_member(pooled, "skill", MEMBER)
    edits, skipped, stats = ISW.plan_edits(rows3, MEMBER, parsed2)
    offset_edits, offset_skipped, _ = ISW.plan_offset_edits(offset_rows, MEMBER, parsed2, pooled)
    edits, conflicts = ISW.merge_edits(edits, offset_edits)
    limits = ISW.MEMBER_SIZE_LIMITS.copy()
    try:
        ISW.MEMBER_SIZE_LIMITS.clear()            # measure, do not refuse
        out, _ = ISW.rebuild_member(pooled, "skill", edits, MEMBER)
    finally:
        ISW.MEMBER_SIZE_LIMITS.update(limits)
    by_record = {r["record"]: r for r in parsed["records"]}
    growth: Dict[str, int] = collections.Counter()
    for row in rows3:
        role, record = row.get("part"), row.get("record")
        if role in ISR.FIELDS and record in by_record and by_record[record].get(role) == row["jp"]:
            growth[role] += len(row["en"].encode("cp932")) - len(row["jp"].encode("cp932"))
    growth["pool"] = len(pooled) - len(blob)
    return {"original": len(blob), "size": len(out), "growth": len(out) - len(blob),
            "growth_by_field": dict(growth), "pool_rows_applied": pool_stats["applied"],
            "rows_applied": stats["applied"],
            "refusals": pool_skipped + skipped + offset_skipped + conflicts}


def remaining(rows3: List[dict], rows4: List[dict], tail_offset: int, top: int = 40
              ) -> List[dict]:
    """The distinct English texts that still add the most bytes (for the next manual pass).

    The ``04`` offset rows below the tail offset address the same record fields as the ``03``
    rows (the builder merges them), so only the pool rows of ``04`` count here."""
    weight: Dict[Tuple[str, str, str], int] = collections.Counter()
    count: Dict[Tuple[str, str, str], int] = collections.Counter()
    seen_offsets = set()
    for row in rows3 + rows4:
        if not translated(row):
            continue
        en = TW.english(row)
        offset = (row.get("source") or {}).get("offset")
        part = row.get("part") or "text"
        if part == "text":
            if not isinstance(offset, int) or offset < tail_offset or offset in seen_offsets:
                continue
            seen_offsets.add(offset)
        key = (part if part != "text" else "pool", row.get("jp") or "", en)
        growth = len(en.encode("cp932")) - len((row.get("jp") or "").encode("cp932"))
        weight[key] += growth
        count[key] += 1
    rows = [{"part": k[0], "jp": k[1], "en": k[2], "growth": v, "rows": count[k]}
            for k, v in weight.items() if v > 0]
    rows.sort(key=lambda r: (-r["growth"], r["part"], r["en"]))
    return rows[:top]


# ----------------------------------------------------------------------------- the DLC pools

def pool_member(row: dict) -> Optional[str]:
    member = (row.get("source") or {}).get("member") or ""
    return member if POOL_RE.match(member) else None


def sync_pools(rows4: List[dict]) -> Tuple[List[dict], List[dict], List[str]]:
    """Give every grow row of ``srwDL_Skill01..08.bin`` the English of the Skill00 row with the
    same Japanese and ``copy_of`` = that row's id.

    Skill00 lists one Japanese several times (the inline record texts repeat); all of them
    carry one English.  ``copy_of`` needs an id that is unique in the file (583 tail-pool rows
    of Skill00 share the id of the pool start, so ``translation_copy`` could not tell them
    apart): the copy source is the highest-offset twin with a unique id, and a fragment whose
    twins all share an id gets the English only.  Slot rows (fixed-width leftovers) and
    fragments without a Skill00 twin are left alone and reported."""
    by_jp: Dict[str, List[dict]] = collections.defaultdict(list)
    id_count: Dict[str, int] = collections.Counter(row.get("id") for row in rows4)
    for row in rows4:
        if (row.get("source") or {}).get("member") == MEMBER and translated(row):
            by_jp[row["jp"]].append(row)
    out, changes, problems = [], [], []
    for row in rows4:
        member = pool_member(row)
        if member is None or row.get("mode") == "slot" or not filled(row):
            out.append(row)
            continue
        twins = by_jp.get(row["jp"])
        if not twins:
            problems.append(f"{row.get('id')}: no Skill00 row with this Japanese")
            out.append(row)
            continue
        englishes = {TW.english(t) for t in twins}
        if len(englishes) > 1:
            problems.append(f"{row.get('id')}: Skill00 rows disagree on the English {sorted(englishes)!r}")
            out.append(row)
            continue
        unique = [t for t in twins if id_count[t.get("id")] == 1]
        source = max(unique, key=lambda t: (t.get("source") or {}).get("offset") or 0) \
            if unique else None
        en = TW.english(twins[0])
        copy_of = source.get("id") if source is not None else row.get("copy_of")
        if en == TW.english(row) and row.get("copy_of") == copy_of:
            out.append(row)
            continue
        copy = dict(row)
        changes.append({"id": row.get("id"), "part": "pool", "jp": row.get("jp"),
                        "before": TW.english(row), "after": en,
                        "saved": len(TW.english(row).encode("cp932")) - len(en.encode("cp932"))})
        copy["en"] = en
        if copy_of:
            copy["copy_of"] = copy_of
        out.append(copy)
    return out, changes, problems


def pool_blob(edat: Path, member: str) -> bytes:
    _, subs, _ = CM.members_of(edat)
    if member not in subs:
        raise ShrinkError(f"{edat}: no {member} inside")
    return subs[member]


def measure_pools(dlc_original: Path, rows4: List[dict]) -> Dict[str, dict]:
    """``{member: {original, size, fits, refused}}`` for every pool whose original EDAT is in
    the folder, rebuilt with the real pool writer from the rows of that member."""
    result: Dict[str, dict] = {}
    by_member: Dict[str, List[dict]] = collections.defaultdict(list)
    for row in rows4:
        member = pool_member(row)
        if member is not None and filled(row):      # the builder skips identity rows too
            by_member[member].append(row)
    for member, rows in sorted(by_member.items()):
        n = POOL_RE.match(member).group(1)
        edat = dlc_original / f"config0{n}.EDAT"
        if not edat.is_file():
            result[member] = {"original": None, "size": None, "fits": None,
                              "problem": f"{edat.name} not in {dlc_original}"}
            continue
        blob = pool_blob(edat, member)
        try:
            modified, report = TW.apply_member(blob, member, rows)
        except TW.TableError as exc:
            result[member] = {"original": len(blob), "size": None, "fits": False, "problem": str(exc)}
            continue
        result[member] = {"original": len(blob), "size": len(modified),
                          "fits": len(modified) <= POOL_LIMIT,
                          "refused": len(report.get("refused", [])) + len(report.get("problems", []))}
    return result


# ----------------------------------------------------------------------------- the run

def run(package: Path, original: Path, rules_path: Path, out: Optional[Path],
        report_path: Optional[Path], limit: int, level_suffix: str, top: int,
        dlc_original: Optional[Path] = None, pool_limit: int = POOL_LIMIT,
        total_limit: int = SKILL_TOTAL_LIMIT) -> dict:
    rules = load_rules(rules_path)
    rows3 = read_jsonl(package / SKILLS_FILE)
    rows4 = read_jsonl(package / CONFIG_FILE)
    names = known_skill_names(rows3)
    blob = skill00_blob(original)
    before = measure(blob, rows3, rows4)
    new3, changes3, refused3 = rewrite_rows(rows3, rules, names, level_suffix)
    new4, changes4, refused4 = rewrite_rows(rows4, rules, names, level_suffix)
    after = measure(blob, new3, new4)
    report = {"package": str(package), "original": str(original), "rules": str(rules_path),
              "rule_count": len(rules), "limit": limit,
              "before": before, "after": after,
              "changed_rows": {SKILLS_FILE: len(changes3), CONFIG_FILE: len(changes4)},
              "guard_refusals": refused3 + refused4,
              "fits": after["size"] <= limit, "over_by": max(0, after["size"] - limit),
              "remaining": remaining(new3, new4, ISR.parse_member(blob, "skill", MEMBER)["tail_offset"],
                                     top)}
    pool_changes: List[dict] = []
    if dlc_original is not None:
        pools_before = measure_pools(dlc_original, rows4)
        new4, pool_changes, pool_problems = sync_pools(new4)
        pools_after = measure_pools(dlc_original, new4)
        sizes = [v["size"] for v in pools_after.values() if v.get("size") is not None]
        total = after["size"] + sum(sizes)
        report["pools"] = {"limit": pool_limit, "before": pools_before, "after": pools_after,
                           "synced_rows": len(pool_changes), "problems": pool_problems,
                           "all_fit": bool(sizes) and all(v["fits"] for v in pools_after.values()),
                           "total": total, "total_limit": total_limit,
                           "total_fits": total <= total_limit and len(sizes) == 8}
        report["changed_rows"][CONFIG_FILE] += len(pool_changes)
        report["fits"] = report["fits"] and report["pools"]["all_fit"] and report["pools"]["total_fits"]
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        for path in sorted(package.iterdir()):
            if path.is_file() and path.name not in (SKILLS_FILE, CONFIG_FILE):
                shutil.copyfile(path, out / path.name)
        write_jsonl(out / SKILLS_FILE, new3)
        write_jsonl(out / CONFIG_FILE, new4)
        with (out / "SKROCENIA_Skill00.tsv").open("w", encoding="utf-8", newline="\n") as handle:
            handle.write("id\tpart\tjp\ten_before\ten_after\tsaved_bytes\n")
            for change in changes3 + changes4 + pool_changes:
                handle.write("\t".join(str(change[k]).replace("\n", "\\n").replace("\t", " ")
                                       for k in ("id", "part", "jp", "before", "after", "saved"))
                             + "\n")
        report["out"] = str(out)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--package", type=Path, required=True, help="package folder (JSONL)")
    parser.add_argument("--original", type=Path, required=True, help="the original config00.cpk")
    parser.add_argument("--rules", type=Path, default=HERE.parent / "config" / "skill_shrink_rules.tsv")
    parser.add_argument("--out", type=Path, help="write the shortened package copy here")
    parser.add_argument("--report", type=Path, help="write the JSON report here")
    parser.add_argument("--limit", type=int, default=ISW.SKILL00_LIMIT,
                        help="member budget in bytes (default: the measured in-game limit)")
    parser.add_argument("--keep-lv", action="store_true", help="keep ' LvN' instead of ' LN'")
    parser.add_argument("--top", type=int, default=40, help="remaining texts to list")
    parser.add_argument("--dlc-original", type=Path,
                        help="folder with the original config01..08.EDAT: sync + measure the DLC pools")
    parser.add_argument("--pool-limit", type=int, default=POOL_LIMIT,
                        help="budget of one DLC pool (default: its original size)")
    parser.add_argument("--total-limit", type=int, default=SKILL_TOTAL_LIMIT,
                        help="budget of Skill00 + the eight pools (default: the largest total that booted)")
    args = parser.parse_args(argv)
    try:
        report = run(args.package, args.original, args.rules, args.out, args.report, args.limit,
                     " Lv" if args.keep_lv else " L", args.top, args.dlc_original,
                     args.pool_limit, args.total_limit)
    except (ShrinkError, ISW.WriteError, OSError) as exc:
        print(f"skill_shrink: {exc}", file=sys.stderr)
        return 2
    before, after = report["before"], report["after"]
    print(f"{MEMBER}: original {before['original']} B; package English {before['size']} B "
          f"(+{before['growth']}); after {report['rule_count']} rules {after['size']} B "
          f"(+{after['growth']}); budget {report['limit']} B -> "
          f"{'FITS' if report['fits'] else 'OVER by %d B' % report['over_by']}")
    print("growth by field:", json.dumps(after["growth_by_field"], sort_keys=True))
    print(f"rows changed: {report['changed_rows']}; guard refusals: {len(report['guard_refusals'])}; "
          f"writer refusals: {len(after['refusals'])}")
    for line in report["guard_refusals"][:10]:
        print("  refused:", line)
    for row in report["remaining"][:args.top]:
        print(f"  +{row['growth']:>4} x{row['rows']:<3} [{row['part']}] {row['en']!r}")
    pools = report.get("pools")
    if pools:
        for member, info in pools["after"].items():
            was = pools["before"].get(member, {}).get("size")
            state = "?" if info.get("fits") is None else ("FITS" if info["fits"] else "OVER")
            print(f"  {member}: original {info.get('original')} B; before {was} B; after "
                  f"{info.get('size')} B; budget {pools['limit']} B -> {state}"
                  + (f"; {info['problem']}" if info.get("problem") else ""))
        print(f"  pools synced rows: {pools['synced_rows']}; problems: {len(pools['problems'])}; "
              f"Skill00 + 8 pools = {pools['total']} B / {pools['total_limit']} B -> "
              f"{'FITS' if pools['total_fits'] else 'OVER'}")
        for line in pools["problems"][:10]:
            print("  pool:", line)
    return 0 if report["fits"] else 1


if __name__ == "__main__":
    sys.exit(main())
