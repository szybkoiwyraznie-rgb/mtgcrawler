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


def audit_container(path: Path, blob: str, trim: int = 3) -> Dict[str, object]:
    report: Dict[str, object] = {"container": path.name, "members": 0, "runs": 0,
                                 "missing": [], "missing_chars": 0, "ok": True}
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
    return report


def collect(paths: Iterable[Path]) -> List[Path]:
    out: List[Path] = []
    for path in paths:
        if path.is_dir():
            out.extend(sorted(p for p in path.iterdir()
                              if p.suffix.lower() in (".cpk", ".edat")))
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
    containers = collect(args.dir)
    reports = []
    for path in containers:
        report = audit_container(path, blob, args.trim)
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
