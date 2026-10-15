#!/usr/bin/env python3
"""Audit: does the translation package hold EVERY text that the game files hold?

The package is built by extractors that walk known structures (EVNT chains, table
records). This tool is the independent check: it byte-scans the raw containers for
CP932 runs -- exactly the way ``extract_structured`` does -- and asks of every run
"is this text somewhere in the package?". Runs that no package row contains are
reported per container, so a gap in an extractor shows up as a number instead of
as a surprise during translation.

False positives are handled by trimming: a scan run can start on a stray lead byte
(the byte before the real text), so a run counts as covered when any of its
suffixes (up to `--trim` characters dropped) is contained in some package row.

Two checks are stricter than "contained in some row", because for them a fragment row
is worthless to the writers:

* the ``sysmes.bin`` pool of ``configst.cpk`` is written whole string by whole string
  (``build_translation_patch._sysmes_edits`` ignores a row that is only the tail of a
  pool string), so every pool string with Japanese must be some row's ``jp`` EXACTLY -
  in raw form (with its ``0x0F`` kana tokens) or in display form (``%s`` per token).
  The byte scan alone missed 31 such strings in package v5 (``ﾒｲﾝ<0F>0ｲﾛｯﾄ``,
  `` 達成！…`` with a leading space, ``%sが使用可能になりました！``): their tails were
  rows, the wholes were not, and the game kept showing Japanese;
* the executable (``PBOOT.PBP`` in a ``--dir``, decrypted by :mod:`psp_prx`) is written
  in place by :mod:`exe_strings`; every string it extracts must be a row's ``jp`` exactly.

Read-only: nothing is written except the report (``--out``).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_structured as ES  # noqa: E402
import speaker_map as SM  # noqa: E402

_JP = None   # compiled lazily (re is cheap, but keep the import list honest)


def _has_japanese(text: str) -> bool:
    global _JP
    if _JP is None:
        import re
        _JP = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\uff61-\uff9f]")
    return bool(_JP.search(text))


def sysmes_missing_whole(pool: bytes, texts: set) -> List[Dict[str, object]]:
    """Pool strings of a ``sysmes.bin`` with Japanese that no row holds WHOLE.

    The byte scan below is satisfied by a row that covers only the tail of a string (the
    first exporter emitted such tails), but the builder's sysmes writer replaces whole pool
    entries only, so a tail row never reaches the game.  A string counts as covered when the
    package has its raw text (``0x0F xx`` kana tokens included) or its display form
    (:func:`table_write.display`, tokens resolved to the voiced kana).
    """
    import sysmes_pack as SMSP
    import table_write as TW
    parsed = SMSP.parse(pool)
    starts = SMSP.string_starts(pool)
    missing: List[Dict[str, object]] = []
    for raw, offset in zip(parsed.strings, starts):
        if not raw:
            continue
        display = TW.display(raw)
        if not _has_japanese(display):
            continue
        if raw.decode("cp932", "replace") in texts or display in texts:
            continue
        missing.append({"member": "sysmes.bin", "offset": offset, "text": display,
                        "whole_string": True})
    return missing


def audit_sysmes_whole(path: Path, texts: set) -> List[Dict[str, object]]:
    """:func:`sysmes_missing_whole` over the ``configst.pac/sysmes.bin`` of a ``configst.cpk``."""
    import configst_pack as CSP
    members = dict(SM.read_members(path))
    pac = members.get("configst.pac")
    if pac is None:
        return []
    subs = {sub["name"]: sub["data"] for sub in CSP.parse_pac(pac)["subs"]}
    pool = subs.get("sysmes.bin")
    if pool is None:
        return []
    return sysmes_missing_whole(pool, texts)


def audit_executable(path: Path, texts: set) -> Dict[str, object]:
    """Every string :mod:`exe_strings` extracts from the executable must be a row's jp."""
    import exe_strings as EXE
    import psp_prx
    report: Dict[str, object] = {"container": path.name, "members": 1, "runs": 0,
                                 "missing": [], "missing_chars": 0, "ok": True}
    try:
        elf = psp_prx.elf_from(path)
        rows, _rejects = EXE.extract_rows(EXE.Elf(elf))
    except Exception as error:  # noqa: BLE001 - reported like an unreadable container
        report["ok"] = False
        report["error"] = f"{type(error).__name__}: {error}"
        return report
    report["runs"] = len(rows)
    for row in rows:
        if row["jp"] in texts:
            continue
        report["missing"].append({"member": EXE.MEMBER, "offset": row["source"]["offset"],
                                  "vaddr": row["source"]["vaddr"], "text": row["jp"]})
        report["missing_chars"] += len(row["jp"])
    return report


def load_package_texts(package: Path) -> List[str]:
    texts: List[str] = []
    for path in sorted(package.glob("*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                jp = row.get("jp")
                if jp:
                    texts.append(jp)
    return texts


def covered(run: str, blob: str, trim: int = 3) -> bool:
    """True when the run (or a suffix of it) sits inside some package text."""
    if run in blob:
        return True
    for drop in range(1, min(trim, len(run) - 3) + 1):
        if run[drop:] in blob:
            return True
    return False


def audit_container(path: Path, blob: str, trim: int = 3,
                    texts: set | None = None) -> Dict[str, object]:
    report: Dict[str, object] = {"container": path.name, "members": 0, "runs": 0,
                                 "missing": [], "missing_chars": 0, "ok": True}
    if path.name.upper() == "PBOOT.PBP":
        return audit_executable(path, texts or set())
    try:
        members = list(SM.read_members(path))
    except Exception as error:  # a container we cannot even read is worth reporting
        report["ok"] = False
        report["error"] = f"{type(error).__name__}: {error}"
        return report
    report["members"] = len(members)
    seen = set()
    for member, data in members:
        for offset, text in ES.scan_runs(data):
            if len(text) < 4:
                continue
            report["runs"] += 1
            if text in seen:
                continue
            seen.add(text)
            if not covered(text, blob, trim):
                report["missing"].append({"member": member, "offset": offset, "text": text})
                report["missing_chars"] += len(text)
    if texts is not None and path.name.lower() == "configst.cpk":
        try:
            whole = audit_sysmes_whole(path, texts)
        except Exception as error:  # noqa: BLE001
            report["ok"] = False
            report["error"] = f"sysmes whole-string check: {type(error).__name__}: {error}"
            return report
        report["sysmes_whole_missing"] = len(whole)
        for item in whole:
            report["missing"].append(item)
            report["missing_chars"] += len(str(item["text"]))
    return report


def collect(paths: Iterable[Path]) -> List[Path]:
    out: List[Path] = []
    for path in paths:
        if path.is_dir():
            out.extend(sorted(p for p in path.iterdir()
                              if p.suffix.lower() in (".cpk", ".edat")
                              or p.name.upper() == "PBOOT.PBP"))
        else:
            out.append(path)
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package coverage audit (read-only)")
    parser.add_argument("--package", type=Path, required=True, help="katalog z *.jsonl")
    parser.add_argument("--dir", type=Path, action="append", required=True,
                        help="katalog z kontenerami gry (można podać kilka)")
    parser.add_argument("--trim", type=int, default=3, help="ile znaków wolno obciąć z przodu")
    parser.add_argument("--out", type=Path, help="gdzie zapisać raport JSON")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    texts = load_package_texts(args.package)
    blob = "\n".join(texts)
    exact = set(texts)
    containers = collect(args.dir)
    reports = []
    for path in containers:
        report = audit_container(path, blob, args.trim, exact)
        reports.append(report)
        if not args.quiet:
            if not report["ok"]:
                print(f"{report['container']:24} NIE CZYTA SIE: {report['error']}")
                continue
            miss = len(report["missing"])  # type: ignore[arg-type]
            flag = "OK" if miss == 0 else "!!"
            print(f"{report['container']:24} członki {report['members']:3} "
                  f"przebiegi {report['runs']:6} brak-w-pakiecie {miss:5} "
                  f"znaków {report['missing_chars']:6} {flag}")
    summary = {"package_texts": len(texts), "containers": len(reports),
               "missing": sum(len(r["missing"]) for r in reports),  # type: ignore[arg-type]
               "missing_chars": sum(r["missing_chars"] for r in reports)}
    if args.out:
        args.out.write_text(json.dumps({"summary": summary, "reports": reports},
                                       ensure_ascii=False, indent=1), encoding="utf-8")
        if not args.quiet:
            print(f"raport: {args.out}")
    if not args.quiet:
        print(f"RAZEM: brakuje {summary['missing']} tekstów / {summary['missing_chars']} znaków")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
