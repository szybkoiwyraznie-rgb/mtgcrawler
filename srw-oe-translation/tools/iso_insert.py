#!/usr/bin/env python3
"""Put ready container files into a COPY of the user's ISO (what ``WGRAJ_DO_ISO.bat`` runs).

The user receives builds and bisection variants as loose files (``config00.cpk``,
``configst.cpk`` ...) and cannot put a file "into an ISO" by hand.  This tool takes the original
ISO and a folder with such files, maps every top-level file of the folder to
``PSP_GAME/USRDIR/<name>``, and writes ``<out>/patched.iso`` with :func:`iso_pack.patch_iso`
(the original is only read).  Fail-closed:

* a file whose name the ISO does not have under ``USRDIR`` stops the run (wrong folder);
* only top-level files are taken - sub-folders (e.g. ``PLAN_B_sub_pliki/V1``) are separate
  variants and are listed as a hint, never merged;
* the source ISO must still carry the ORIGINAL member for every file being replaced (known
  md5 of the user's 1.08 disc) - a previously patched ISO is refused, so variants never stack;
* every inserted member is read back from the new ISO and its md5 compared.

Prints names, sizes and md5 only - never game bytes.  Output goes under ``srw-oe-wgrane/``
(gitignored, next to the .bat) in a folder named after the chosen folder.

Usage::

    python tools/iso_insert.py --iso GAME.iso --files USRDIR_EN_build10 [--out-root srw-oe-wgrane]
    python tools/iso_insert.py --iso GAME.iso --files PLAN_B_sub_pliki/V1 --out local/x/patched.iso
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import iso_pack  # noqa: E402

# md5 of the USRDIR containers of the user's original disc (SRW OE 1.08, measured 2026-10-14 on
# the files the user uploaded as "USRDIR originals"); a source ISO whose member differs is not
# the original (or not this edition) and is refused unless --force is given.
KNOWN_ORIGINALS: Dict[str, str] = {
    "config00.cpk": "266366c3bee66130d4b7cb57a1b1e3d4",
    "configst.cpk": "c87e404032fc5cadc7aae22f15f6833b",
    "eventP00.cpk": "5fd6eea0e3732b17c48aa44859d86b02",
    "imenu00.cpk": "bec96255271d89bcb07cfe41be15bb1f",
    "mesbtl00.cpk": "f614ab6297136b38fb39ab96e41863d7",
    # UI texture containers (2026-10-15, measured on the user's USRDIR copies of the same disc):
    # the texture builds (tools/ui_texture_patch.py) replace these, so a stacked insert is refused too.
    "system.cpk": "75b0d0d44f1afb3af027b93e38e223c6",
    "IM1000.cpk": "54077cbbf76c06251a220f9085bb2fc3",
    "IM3000.cpk": "5447d366aa01f8060138ecf4ae2ed80f",
    "tacsys.cpk": "0e29a50724e7eec384a6ab2555539e32",
    "IM9000.cpk": "2a490e70670c2ff374764635225fbaff",
    "navisys.cpk": "08d5b99a29c779968b78259a2fc16b40",   # 2 bare RGBA8888 GIMs (navigation buttons)
}
SKIPPED_SUFFIXES = {".txt", ".json", ".md", ".zip", ".log", ".csv", ".html", ".bat", ".py", ".exe"}


class InsertError(Exception):
    """The run cannot proceed safely; the message says why (Polish, for the .bat window)."""


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def candidates(folder: Path) -> List[Path]:
    """Top-level files of ``folder`` that look like game containers (notes/reports skipped)."""
    return sorted(p for p in folder.iterdir()
                  if p.is_file() and p.suffix.lower() not in SKIPPED_SUFFIXES
                  and not p.name.lower().endswith(".mix.json"))


def variant_folders(folder: Path) -> List[Path]:
    """Sub-folders that hold their own container files (shown as a hint, never merged)."""
    found = []
    for sub in sorted(folder.rglob("*")):
        if sub.is_dir() and sub != folder and candidates(sub):
            found.append(sub)
    return found


def plan(iso: Path, folder: Path, force: bool = False) -> List[dict]:
    """What would be inserted: one entry per file with the ISO key and both md5s; fail-closed."""
    if not iso.is_file():
        raise InsertError(f"Nie ma takiego pliku ISO: {iso}")
    if not folder.is_dir():
        raise InsertError(f"Nie ma takiego folderu: {folder}")
    files = candidates(folder)
    if not files:
        hint = variant_folders(folder)
        text = (f"W folderze {folder} nie ma plikow do wgrania (np. config00.cpk)."
                " Pliki .txt/.json sa pomijane.")
        if hint:
            text += " Pliki sa w podfolderach - wskaz JEDEN z nich: " + ", ".join(
                str(h.relative_to(folder)) for h in hint[:8])
        raise InsertError(text)
    with iso.open("rb") as fh:
        records = iso_pack._walk_record_offsets(fh)
    by_path = {}
    for key, (offset, lba, size, is_dir) in records.items():
        if not is_dir:
            by_path[key.split(";")[0].strip("/")] = (key, lba, size)
    entries = []
    for path in files:
        wanted = f"psp_game/usrdir/{path.name.lower()}"
        if wanted not in by_path:
            raise InsertError(f"W ISO nie ma pliku PSP_GAME/USRDIR/{path.name} - to nie jest plik"
                              f" z tej gry albo wskazano zly folder. Nic nie zapisano.")
        key, lba, size = by_path[wanted]
        with iso.open("rb") as fh:
            fh.seek(lba * iso_pack.BLOCK_SIZE)
            current = fh.read(size)
        new = path.read_bytes()
        entry = {"file": path.name, "iso_key": key, "size_in_iso": size, "md5_in_iso": md5(current),
                 "size_new": len(new), "md5_new": md5(new),
                 "original_known": KNOWN_ORIGINALS.get(path.name)}
        if entry["md5_new"] == entry["md5_in_iso"]:
            raise InsertError(f"{path.name}: plik z folderu jest IDENTYCZNY z tym w ISO"
                              f" (md5 {entry['md5_new']}) - to ISO ma go juz wgranego albo to"
                              f" oryginalny plik. Wskaz oryginalne ISO i folder z buildem.")
        known = entry["original_known"]
        if known and entry["md5_in_iso"] != known and not force:
            raise InsertError(f"{path.name} w tym ISO nie jest oryginalny (md5 {entry['md5_in_iso']},"
                              f" oryginal 1.08: {known}). To ISO bylo juz zmieniane - wskaz"
                              f" ORYGINALNE ISO, zeby warianty sie nie nakladaly. Nic nie zapisano.")
        entries.append(entry)
    return entries


def insert(iso: Path, folder: Path, out_iso: Path, force: bool = False) -> dict:
    """Write ``out_iso`` = ``iso`` with the folder's files inserted; read every member back."""
    entries = plan(iso, folder, force=force)
    if out_iso.resolve() == iso.resolve():
        raise InsertError("Wynik nie moze nadpisac zrodlowego ISO.")
    out_iso.parent.mkdir(parents=True, exist_ok=True)
    patch = {e["iso_key"]: (folder / e["file"]).read_bytes() for e in entries}
    result = iso_pack.patch_iso(iso, out_iso, patch)
    failures = []
    for e in entries:
        back = iso_pack.read_member(out_iso, e["iso_key"])
        e["md5_read_back"] = md5(back)
        if e["md5_read_back"] != e["md5_new"] or len(back) != e["size_new"]:
            failures.append(e["file"])
    report = {"iso": str(iso), "files": str(folder), "out": str(out_iso),
              "iso_size_in": iso.stat().st_size, "iso_size_out": out_iso.stat().st_size,
              "applied": result["applied"], "members": entries, "read_back_failures": failures}
    if failures:
        out_iso.unlink(missing_ok=True)
        raise InsertError("Odczyt kontrolny z nowego ISO nie zgadza sie dla: "
                          + ", ".join(failures) + " - plik wynikowy usuniety.")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--iso", type=Path, required=True, help="the ORIGINAL game ISO (read only)")
    parser.add_argument("--files", type=Path, required=True,
                        help="folder with the files to insert (top level only)")
    parser.add_argument("--out", type=Path, default=None, help="output ISO path")
    parser.add_argument("--out-root", type=Path, default=Path("srw-oe-wgrane"),
                        help="when --out is not given: <out-root>/<folder name>/patched.iso")
    parser.add_argument("--force", action="store_true",
                        help="insert even when the ISO member is not the known original")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    folder = args.files
    out_iso = args.out or (args.out_root / (folder.resolve().name or "wynik") / "patched.iso")
    try:
        if args.dry_run:
            entries = plan(args.iso, folder, force=args.force)
            report = {"dry_run": True, "members": entries, "out": str(out_iso)}
        else:
            report = insert(args.iso, folder, out_iso, force=args.force)
            (out_iso.parent / "wgrane_report.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    except InsertError as exc:
        print(f"BLAD: {exc}")
        return 1
    except ValueError as exc:
        print(f"BLAD: {exc}")
        return 1
    print(f"ISO zrodlowe: {args.iso}")
    print(f"Folder z plikami: {folder}")
    for e in report["members"]:
        tag = "" if e.get("original_known") in (None, e["md5_in_iso"]) else "  (UWAGA: w ISO nie byl oryginalny)"
        print(f"  {e['file']}: w ISO {e['size_in_iso']} B md5 {e['md5_in_iso']}  ->  wgrany"
              f" {e['size_new']} B md5 {e['md5_new']}{tag}")
    if args.dry_run:
        print("(proba - nic nie zapisano)")
    else:
        print(f"Zapisano: {out_iso}  ({report['iso_size_out']} B; zrodlo {report['iso_size_in']} B)")
        print("Odczyt kontrolny z nowego ISO: zgodny dla wszystkich wgranych plikow.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
