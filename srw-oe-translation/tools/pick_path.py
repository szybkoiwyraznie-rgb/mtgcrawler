#!/usr/bin/env python3
"""Native "choose a file / choose a folder" window for the .bat scripts.

The user's standing rule (said twice, 2026-10-12 and 2026-10-14): a .bat for the user
NEVER asks to type a path - it opens a selector, like ``PATCH_ISO_TEST.bat`` /
``run_pipeline.py`` do.  This helper is that selector for every script, so a new .bat
only needs one ``call :pick`` line instead of re-inventing (or forgetting) the dialog.

Usage::

    pick_path.py iso          --out chosen.txt [--initial DIR]
    pick_path.py dlc          --out chosen.txt [--initial DIR]
    pick_path.py package      --out chosen.txt [--initial DIR]
    pick_path.py translation  --out chosen.txt [--initial DIR]
    pick_path.py file|dir     --out chosen.txt [--title T] [--initial DIR] [--ext iso]

The chosen path is written to ``--out`` as UTF-8 without BOM and without a newline, so a
.bat can read it back with ``set /p "VAR=" < chosen.txt`` (no ``for /f`` quoting games).
Nothing else is printed on stdout.

Exit codes (the .bat branches on them):

* ``0`` - a path was chosen and written,
* ``2`` - the user closed the window without choosing (the .bat should stop politely),
* ``3`` - no dialog is possible here (Python without Tk, or no desktop) - the .bat may
  fall back to a typed path; this is the only situation in which typing is acceptable.

The presets (``iso``, ``dlc``, ``package``, ``translation``) carry the Polish titles and
file filters, so the .bat stays pure ASCII.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

PRESETS = {
    "iso": {
        "kind": "file",
        "title": "Wybierz swoje ISO SRW OE (wersja 1.08) - plik jest tylko czytany",
        "filetypes": [("Obraz ISO", "*.iso"), ("Wszystkie pliki", "*.*")],
    },
    "dlc": {
        "kind": "dir",
        "title": "Wybierz folder z ODSZYFROWANYMI plikami DLC (np. FULL_DLC)",
    },
    "package": {
        "kind": "dir",
        "title": "Wybierz folder pakietu tlumaczenia (ten z plikiem 00_dialogue.jsonl)",
    },
    "translation": {
        "kind": "dir",
        "title": "Wybierz folder zwroconego tlumaczenia (sceny\\ i widoki\\) albo ten sam co pakiet",
    },
}

CHOSEN, CANCELLED, NO_DIALOG = 0, 2, 3


def _tk_root():
    """A hidden Tk root on top of other windows, or None when no dialog is possible."""
    try:
        import tkinter
    except ImportError:
        return None
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        return None
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except tkinter.TclError:
        pass
    # Bring the (hidden) owner to the front so the dialog it owns opens in front of the
    # console instead of behind it (reported as "the window flashes and nothing happens").
    for step in ("update", "lift", "focus_force"):
        try:
            getattr(root, step)()
        except Exception:
            pass
    return root


def choose(kind: str, title: str, initial: Optional[Path] = None,
           filetypes=None) -> Optional[str]:
    """Open the dialog; '' when the user cancels, None when no dialog is possible."""
    root = _tk_root()
    if root is None:
        return None
    from tkinter import filedialog
    initialdir = str(initial) if initial is not None and Path(initial).is_dir() else None
    try:
        if kind == "dir":
            chosen = filedialog.askdirectory(parent=root, title=title, initialdir=initialdir,
                                             mustexist=True)
        else:
            chosen = filedialog.askopenfilename(
                parent=root, title=title, initialdir=initialdir,
                filetypes=filetypes or [("Wszystkie pliki", "*.*")])
    except Exception:  # Tk raised while opening - treat as "no dialog here"
        return None
    finally:
        try:
            root.destroy()
        except Exception:
            pass
    return chosen or ""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("what", choices=sorted(PRESETS) + ["file", "dir"])
    parser.add_argument("--out", required=True, type=Path,
                        help="file that receives the chosen path (UTF-8, no newline)")
    parser.add_argument("--title", default=None)
    parser.add_argument("--initial", default=None, help="folder the window opens in")
    parser.add_argument("--ext", default=None, help="file extension filter for 'file', e.g. iso")
    args = parser.parse_args(argv)

    preset = PRESETS.get(args.what, {"kind": args.what, "title": args.title or "Wybierz"})
    kind = preset["kind"]
    title = args.title or preset["title"]
    filetypes = preset.get("filetypes")
    if args.ext and kind == "file":
        ext = args.ext.lstrip(".")
        filetypes = [(f"Pliki *.{ext}", f"*.{ext}"), ("Wszystkie pliki", "*.*")]
    initial = Path(args.initial) if args.initial else None

    chosen = choose(kind, title, initial, filetypes)
    if chosen is None:
        return NO_DIALOG
    if chosen == "":
        return CANCELLED
    # Windows dialogs return forward slashes; the .bat side is happier with backslashes.
    text = str(Path(chosen))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(text.encode("utf-8"))
    return CHOSEN


if __name__ == "__main__":
    sys.exit(main())
