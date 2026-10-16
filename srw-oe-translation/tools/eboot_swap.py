#!/usr/bin/env python3
"""Put the ORIGINAL disc program (``PSP_GAME/SYSDIR/EBOOT.BIN``) back into a copy of a built ISO.

``EBOOT_TEST.bat`` runs this.  Why it exists (2026-10-16, v9 build crashes at ``Loading...``):
that build was the FIRST ever to boot with a replaced ``EBOOT.BIN`` (the ``exe_step`` plain ELF),
and at the same time the first in-game test of the v7/v8/v9 package data - the crash therefore has
two independent candidate causes.  This tool builds the data-only variant: the current
``patched.iso`` (v9 containers, our EBOOT) with the ORIGINAL program from the user's 1.08 ISO.

* new ISO boots and plays  ->  the EBOOT replacement is the culprit; the program strings go back
  to the confirmed CWCheat route until the ELF route is fixed;
* it still crashes at Loading  ->  the crash lives in the data (v7/v8/v9); bisect the containers
  (``BISEKCJA.bat``) - the EBOOT route may still be innocent.

Fail-closed, like :mod:`iso_insert`:

* the two ISO paths must be different files, and the output never overwrites an input;
* the source (original) member must exist and must be the signed ``~PSP`` program - a plain ELF
  there means the ISOs were probably given in the wrong order (the build always carries a plain
  ELF), and a program this project built is refused outright (no stacking);
* the target (build) member must be a plain ELF - when ``exe_step`` did not run, the build keeps
  the original ``~PSP`` and there is nothing to revert;
* identical programs in both ISOs stop the run (nothing would change);
* every patched member is read back from the new ISO and its md5 compared.

Prints names, sizes, md5 and the ``~PSP``/ELF classification only - never game bytes.

Usage::

    python tools/eboot_swap.py --target-iso srw-oe-patch/patched.iso --source-iso GAME.iso
                               [--out PATH] [--out-root srw-oe-eboot-test] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import iso_pack  # noqa: E402
from iso_insert import KNOWN_BUILT_ELF  # noqa: E402  (one table of our built programs)

EBOOT_KEY = "psp_game/sysdir/eboot.bin"
#: the only legal direction: the original ISO carries the signed program, the build carries
#: a plain ELF (exe_step wrote it, or its PBOOT fallback).  Everything else is ambiguous and
#: refused, so the two ISOs can never be silently given in the wrong order.
LEGAL_SOURCE_KIND, LEGAL_TARGET_KIND = "~PSP", "ELF"


class SwapError(Exception):
    """The run cannot proceed safely; the message says why (Polish, for the .bat window)."""


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def kind(blob: bytes) -> str:
    if blob[:4] == b"\x7fELF":
        return "ELF"
    return "~PSP" if blob[:4] == b"~PSP" else "?"


def plan(source_iso: Path, target_iso: Path, out_iso: Path, force: bool = False) -> dict:
    """What would be swapped: both programs classified, all guards applied; fail-closed."""
    source_iso, target_iso, out_iso = Path(source_iso), Path(target_iso), Path(out_iso)
    if not source_iso.is_file():
        raise SwapError(f"Nie ma takiego pliku ISO (oryginal): {source_iso}")
    if not target_iso.is_file():
        raise SwapError(f"Nie ma takiego pliku ISO (build): {target_iso}")
    if source_iso.resolve() == target_iso.resolve():
        raise SwapError("Oba wskazane ISO to ten sam plik - potrzeba DWOCH: build oraz oryginal 1.08.")
    for name, path in (("docelowe", target_iso), ("zrodlowe", source_iso)):
        if out_iso.resolve() == path.resolve():
            raise SwapError(f"Wynik nadpisalby ISO {name} ({path}) - podaj inna sciezke wyjsciowa.")
    try:
        src = iso_pack.read_member(source_iso, EBOOT_KEY)
    except ValueError as exc:
        raise SwapError(f"W ORYGINALNYM ISO ({source_iso.name}) nie ma EBOOT.BIN ({exc}) - "
                        f"wskazano zle ISO?") from exc
    try:
        tgt = iso_pack.read_member(target_iso, EBOOT_KEY)
    except ValueError as exc:
        raise SwapError(f"W ISO BUILDU ({target_iso.name}) nie ma EBOOT.BIN ({exc}) - "
                        f"wskazano zle ISO?") from exc
    k_src, k_tgt = kind(src), kind(tgt)
    entry = {
        "source_iso": str(source_iso), "target_iso": str(target_iso), "out_iso": str(out_iso),
        "source": {"size": len(src), "md5": md5(src), "kind": k_src},
        "target": {"size": len(tgt), "md5": md5(tgt), "kind": k_tgt},
    }
    if k_src == "?":
        raise SwapError(f"EBOOT.BIN w ORYGINALNYM ISO nie jest ani szyfrowanym programem (~PSP), "
                        f"ani ELF-em (naglowek {src[:4]!r}) - to nie jest ISO tej gry.")
    built = KNOWN_BUILT_ELF.get(entry["source"]["md5"])
    if built:
        raise SwapError(f"EBOOT.BIN w ORYGINALNYM ISO to {built} - wskazano NASZ program jako "
                        f"oryginal. Zamiana odmowiona, zeby warianty sie nie nakladaly.")
    if entry["source"]["md5"] == entry["target"]["md5"]:
        raise SwapError(f"EBOOT.BIN jest IDENTYCZNY w obu ISO (md5 {entry['source']['md5']}) - "
                        f"nie ma czego zamieniac. Czy na pewno wskazano build z podmienionym "
                        f"programem?")
    if (k_src, k_tgt) != (LEGAL_SOURCE_KIND, LEGAL_TARGET_KIND) and not force:
        if k_tgt != LEGAL_TARGET_KIND:
            raise SwapError(f"EBOOT.BIN w ISO BUILDU nie jest jawnym ELF-em ({k_tgt}) - to build "
                            f"bez podmienionego programu, nie ma czego przywracac.")
        if k_src != LEGAL_SOURCE_KIND:
            raise SwapError(f"EBOOT.BIN w ORYGINALNYM ISO jest jawnym ELF-em, a w BUILDU {k_tgt} - "
                            f"oba ISO maja programy nieszyfrowane albo kolejnosc jest odwrocona. "
                            f"Build (ten co pada) wskazuj jako PIERWSZE okno, oryginal 1.08 jako "
                            f"DRUGIE. Jesli to naprawde twoj oryginal - uruchom z --force.")
    return entry


def swap(source_iso: Path, target_iso: Path, out_iso: Path, force: bool = False,
         dry_run: bool = False) -> dict:
    """Write ``out_iso`` = ``target_iso`` with the source ISO's original EBOOT.BIN; read back."""
    source_iso, target_iso, out_iso = Path(source_iso), Path(target_iso), Path(out_iso)
    entry = plan(source_iso, target_iso, out_iso, force=force)
    if dry_run:
        entry["dry_run"] = True
        return entry
    out_iso.parent.mkdir(parents=True, exist_ok=True)
    src = iso_pack.read_member(source_iso, EBOOT_KEY)
    result = iso_pack.patch_iso(target_iso, out_iso, {EBOOT_KEY: src})
    back = iso_pack.read_member(out_iso, EBOOT_KEY)
    entry.update({"applied": result["applied"], "iso_size_in": target_iso.stat().st_size,
                  "iso_size_out": out_iso.stat().st_size,
                  "md5_read_back": md5(back), "read_back_ok": back == src})
    if not entry["read_back_ok"]:
        out_iso.unlink(missing_ok=True)
        raise SwapError("Odczyt kontrolny z nowego ISO nie zgadza sie - plik wynikowy usuniety.")
    return entry


def _thousands(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def _print_report(entry: dict) -> None:
    print(f"ISO buildu (ten co pada): {entry['target_iso']}")
    print(f"ISO oryginalne 1.08:      {entry['source_iso']}")
    t, s = entry["target"], entry["source"]
    print(f"  EBOOT.BIN w buildzie:   {_thousands(t['size']):>13} B  {t['kind']:<5} md5 {t['md5']}")
    print(f"  EBOOT.BIN z oryginalu:  {_thousands(s['size']):>13} B  {s['kind']:<5} md5 {s['md5']}")
    if entry.get("dry_run"):
        print("(proba - nic nie zapisano)")
        return
    print(f"Zapisano: {entry['out_iso']}  ({_thousands(entry['iso_size_out'])} B;"
          f" zrodlo {_thousands(entry['iso_size_in'])} B)")
    print("Odczyt kontrolny z nowego ISO: zgodny.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target-iso", type=Path, required=True,
                        help="the BUILT ISO (HOKUS_POKUS patched.iso) - the one that crashes")
    parser.add_argument("--source-iso", type=Path, required=True,
                        help="the ORIGINAL 1.08 game ISO - only read")
    parser.add_argument("--out", type=Path, default=None,
                        help="output ISO path (default: <out-root>/patched_EBOOT_oryginalny.iso)")
    parser.add_argument("--out-root", type=Path, default=Path("srw-oe-eboot-test"),
                        help="when --out is not given: <out-root>/patched_EBOOT_oryginalny.iso")
    parser.add_argument("--force", action="store_true",
                        help="swap even when the original ISO's EBOOT.BIN is a plain ELF "
                             "(some dump tools leave it decrypted)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    out_iso = args.out or (args.out_root / "patched_EBOOT_oryginalny.iso")
    if not args.dry_run:
        out_iso.parent.mkdir(parents=True, exist_ok=True)
    try:
        entry = swap(args.source_iso, args.target_iso, out_iso, force=args.force,
                     dry_run=args.dry_run)
        if not args.dry_run:
            (out_iso.parent / "eboot_swap_report.json").write_text(
                json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
    except (SwapError, ValueError) as exc:
        print(f"BLAD: {exc}")
        return 1
    _print_report(entry)
    if not args.dry_run:
        print()
        print("TEST A/B: uruchom ten plik w PPSSPP z WYLACZONYM plikiem cheatow")
        print("(ustawienia PPSSPP -> Cheaty off, albo zmien nazwe cheats\\NPJH50521.ini).")
        print("Napisy programu wroca po japonsku - to OCZEKIWANE; chodzi o to, czy gra")
        print("przejdzie Loading i czy dziala dalej (menu, intermisja, misja, sejw).")
        print("  dziala       -> winna jest podmiana EBOOT.BIN; napisy programu wracaja")
        print("                  na plik CWCheat do czasu naprawy drogi ELF.")
        print("  pada na Loading -> winne sa DANE (pakiet v7/v8/v9) - wtedy BISEKCJA.bat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
