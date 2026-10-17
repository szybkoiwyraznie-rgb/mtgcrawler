#!/usr/bin/env python3
"""Bisect the translated DLC by plain FILE COPIES (what ``DLC_TEST.bat`` runs).

2026-10-16, after the v9 crash hunt: TEST T1 proved the v9 ISO side good - the game runs with
the v9 ``patched.iso`` and the ORIGINAL DLC folder, and the patched ``EBOOT.BIN`` shows its
English (the 1.08 weapon-ability lines) in-game.  The crash therefore lives in the v9 DLC
EDATs, and bisecting them needs no rebuild at all: the emulator reads
``...\\PSP\\GAME\\NPJH50521`` as loose files, so a round is copying one GROUP of v9 EDATs over
the working folder, booting once, and reading the result.

Groups (file-name globs, case-insensitive, on the folder's top level):

=================  =====================================================
``konfig_imenu``   ``config*.EDAT`` + ``imenu*.EDAT`` (dictionaries)
``eventy``         ``eventP*.EDAT`` + ``evept*.EDAT`` (dialogue)
``mesbtl``         ``mesbtl*.EDAT`` (battle quotes)
``wszystko``       every ``.EDAT``
``oryginaly``      restore EVERY differing file from the ORIGINALS folder
=================  =====================================================

plus half-variants (``konfig_imenu_a/b``, ``eventy_a/b``, ``mesbtl_a/b``) for the second
bisection level, and per-group restores (``r_<group>``).

Fail-closed:

* the working folder, the v9 folder and the originals folder must exist and be pairwise
  different paths; nothing is ever deleted; sources are only read;
* only files that exist on BOTH sides and differ by md5 are copied; each copy is verified by
  md5 read-back from the working folder;
* an empty plan stops the run with a hint (wrong folders, or the group is already applied);
* ``PBOOT.PBP`` is treated like any other file (the v9 build patched it; restoring brings the
  original back - PPSSPP releases never read it, but keep the folder true to the originals).
* names, sizes and md5 only - never game bytes.  A JSON report lands under ``--out-root``.

Usage::

    python tools/dlc_test.py --working "...\\GAME\\NPJH50521" --v9 "...\\NPJH50521_v9"
                             --originals "D:\\SRWOE\\NPJH50521" --variant eventy_a
    python tools/dlc_test.py ... --variant oryginaly        # restore everything
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


class TestError(Exception):
    """The round cannot proceed safely; the message says why (Polish, for the .bat window)."""


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


#: name group -> file-name globs (matched case-insensitively against the folder's top level).
#: Halves split by chapter number: a = chapters 1-8 / the first half of the set, b = the rest.
GROUPS: Dict[str, List[str]] = {
    "konfig_imenu": ["config*.EDAT", "imenu*.EDAT"],
    "konfig_imenu_a": ["config0[1-8].EDAT", "imenu0[1-8].EDAT"],
    "konfig_imenu_b": ["config0[9].EDAT", "config[1-4][0-9].EDAT",
                       "imenu0[9].EDAT", "imenu[1-3][0-9].EDAT"],
    "eventy": ["eventP*.EDAT", "evept*.EDAT"],
    "eventy_a": ["eventP0[1-9].EDAT", "evept10[1-4].EDAT"],
    "eventy_b": ["eventP1[0-9].EDAT", "eventP[23][0-9].EDAT", "evept10[5-8].EDAT"],
    "mesbtl": ["mesbtl*.EDAT"],
    "mesbtl_a": ["mesbtl0[1-9].EDAT", "mesbtl1[0-5].EDAT"],
    "mesbtl_b": ["mesbtl1[6-9].EDAT", "mesbtl[23][0-9].EDAT"],
    "wszystko": ["*.EDAT"],
}
RESTORE_ALL = "oryginaly"


def _match(name: str, patterns: List[str]) -> bool:
    low = name.lower()
    return any(fnmatch.fnmatchcase(low, p.lower()) for p in patterns)


def plan(working: Path, source: Path, patterns: List[str]) -> List[dict]:
    """Entries to copy: files present on both sides whose md5 differs (sources are read-only)."""
    if not working.is_dir():
        raise TestError(f"Nie ma takiego folderu (DZIALAJACY): {working}")
    if not source.is_dir():
        raise TestError(f"Nie ma takiego folderu (ZRODLO): {source}")
    try:
        if working.resolve() == source.resolve():
            raise TestError("Folder dzialajacy i zrodlo to TEN SAM folder - potrzeba dwoch "
                            "(dzialajacy w emulatorze, drugi z plikami do wgrania).")
    except OSError as exc:
        raise TestError(f"Nie da sie porownac sciezek folderow: {exc}") from exc
    entries: List[dict] = []
    missing = same = 0
    for path in sorted(working.iterdir()):
        if not path.is_file() or not _match(path.name, patterns):
            continue
        src = source / path.name
        if not src.is_file():
            missing += 1
            continue
        current = path.read_bytes()
        new = src.read_bytes()
        if md5(current) == md5(new):
            same += 1
            continue
        entries.append({"file": path.name, "size": len(new), "md5_from": md5(current),
                        "md5_to": md5(new)})
    if not entries:
        text = (f"Zadna grupa plikow sie nie roznia (identycznych: {same}, brak u zrodla: "
                f"{missing}) - nic do zrobienia.")
        if missing:
            text += f" Uwaga: {missing} pasujacych plikow nie ma w folderze zrodla."
        raise TestError(text)
    return entries


def apply(working: Path, source: Path, patterns: List[str], out_root: Path, variant: str,
          dry_run: bool = False) -> dict:
    """Copy the planned v9/originals files over the working folder; verify every read-back."""
    working, source, out_root = Path(working), Path(source), Path(out_root)
    entries = plan(working, source, patterns)
    if dry_run:
        return {"variant": variant, "dry_run": True, "entries": entries}
    report: dict = {"variant": variant, "working": str(working), "source": str(source),
                    "entries": [], "failures": []}
    for e in entries:
        src = source / e["file"]
        dst = working / e["file"]
        dst.write_bytes(src.read_bytes())
        back = dst.read_bytes()
        e["read_back_ok"] = md5(back) == e["md5_to"]
        if not e["read_back_ok"]:
            report["failures"].append(e["file"])
        report["entries"].append(e)
    if report["failures"]:
        raise TestError("Odczyt kontrolny nie zgadza sie dla: "
                        + ", ".join(report["failures"]) + " - sprawdz dysk i uruchom ponownie.")
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / f"raport_{variant}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def _thousands(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def _print_report(report: dict) -> None:
    entries = report["entries"]
    total = sum(e["size"] for e in entries)
    if report.get("dry_run"):
        print(f"(proba - nic nie zapisano) {len(entries)} plikow do zmiany, "
              f"{_thousands(total)} B:")
    else:
        print(f"Zmieniono {len(entries)} plikow ({_thousands(total)} B):")
    for e in entries:
        print(f"  {e['file']:<18} {_thousands(e['size']):>10} B  md5 {e['md5_from'][:8]}"
              f" -> {e['md5_to'][:8]}")
    if not report.get("dry_run"):
        print("Odczyt kontrolny: zgodny dla wszystkich plikow.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--working", type=Path, required=True,
                        help="the emulator DLC folder the game actually reads (modified!)")
    parser.add_argument("--v9", type=Path, required=True,
                        help="folder with the translated (v9) EDAT files")
    parser.add_argument("--originals", type=Path, default=None,
                        help="folder with the ORIGINAL files (needed to restore)")
    parser.add_argument("--variant", required=True,
                        help="group name: " + ", ".join(sorted(GROUPS)) + ", " + RESTORE_ALL)
    parser.add_argument("--out-root", type=Path, default=Path("srw-oe-dlc-test"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.variant == RESTORE_ALL:
            if not args.originals:
                raise TestError("Przywracanie potrzebuje folderu ORYGINALOW (--originals).")
            if args.working.resolve() == args.originals.resolve():
                raise TestError("Folder dzialajacy i folder oryginolow to TEN SAM folder - "
                                "przywracanie mialoby skutki tylko wtedy, gdy dzialajacy jest "
                                "juz zmieniony; wskaz emulatorowy folder NPJH50521.")
            report = apply(args.working, args.originals, ["*"], args.out_root, args.variant,
                           args.dry_run)
        elif args.variant.startswith("r_"):
            group = args.variant[2:]
            if group not in GROUPS:
                raise TestError(f"Nie ma takiej grupy: {group}")
            if not args.originals:
                raise TestError("Przywracanie potrzebuje folderu ORYGINALOW (--originals).")
            report = apply(args.working, args.originals, GROUPS[group], args.out_root,
                           args.variant, args.dry_run)
        elif args.variant in GROUPS:
            report = apply(args.working, args.v9, GROUPS[args.variant], args.out_root,
                           args.variant, args.dry_run)
        else:
            raise TestError("Nie ma takiego wariantu: " + args.variant
                            + ". Dostepne: " + ", ".join(sorted(GROUPS) + [RESTORE_ALL]))
    except TestError as exc:
        print(f"BLAD: {exc}")
        return 1
    except OSError as exc:
        print(f"BLAD: {exc}")
        return 1
    _print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
