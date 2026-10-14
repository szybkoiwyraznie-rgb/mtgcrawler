#!/usr/bin/env python3
"""Native "pick one option" window for the .bat scripts (radio list, OK / Anuluj).

Same contract as :mod:`pick_path`: the user never types, the chosen VALUE is written to
``--out`` (UTF-8, no BOM, no newline) and the exit code says what happened:

* ``0`` - an option was chosen and written,
* ``2`` - the window was closed / cancelled,
* ``3`` - no dialog is possible here (no Tk / no desktop) - the .bat may fall back to a
  typed letter, the only situation where typing is acceptable.

Usage::

    pick_choice.py bisect --out chosen.txt
    pick_choice.py custom --out chosen.txt --title "..." --option "A|opis A" --option "B|opis B"

The ``bisect`` preset is the crash-hunt list of ``BISEKCJA.bat``: every value is the
``--only`` / ``--skip`` glob set the builder receives (see build_translation_patch.py).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

CHOSEN, CANCELLED, NO_DIALOG = 0, 2, 3

#: value written to --out  |  label shown to the user.  Value = ``<letter>:<filter spec>``;
#: the spec is what ``build_translation_patch.py --filter`` takes (``only=`` / ``skip=`` +
#: comma-separated file-name globs) and the letter names the output folder.
BISECT_OPTIONS: List[Tuple[str, str]] = [
    ("A:only=configst.cpk",
     "A  ISO: tylko configst.cpk (menu / teksty systemowe / sysmes) - reszta oryginalna"),
    ("B:only=config00.cpk",
     "B  ISO: tylko config00.cpk (nazwy, umiejetnosci, przedmioty, lista DLC)"),
    ("C:only=eventP00.cpk",
     "C  ISO: tylko eventP00.cpk (dialogi rozdzialu 1)"),
    ("D:only=mesbtl00.cpk",
     "D  ISO: tylko mesbtl00.cpk (kwestie bitewne)"),
    ("E:only=imenu00.cpk",
     "E  ISO: tylko imenu00.cpk (menu intermisji)"),
    ("F:skip=*.EDAT",
     "F  ISO: wszystkie 5 plikow z ISO przetlumaczone, DLC zostaje ORYGINALNE"),
    ("G:only=*.EDAT",
     "G  tylko DLC (wszystkie EDAT) przetlumaczone, ISO zostaje ORYGINALNE"),
    ("H:only=eventP*.EDAT,evept*.EDAT",
     "H  tylko DLC z dialogami (eventP*/evept* EDAT), ISO oryginalne"),
    ("I:only=config*.EDAT,mesbtl*.EDAT,imenu*.EDAT",
     "I  tylko DLC bez dialogow (config*/mesbtl*/imenu* EDAT), ISO oryginalne"),
]

PRESETS = {
    "bisect": {
        "title": "BISEKCJA - ktory kawalek ma byc przetlumaczony w tym buildzie?",
        "options": BISECT_OPTIONS,
    },
}


def _tk_root():
    try:
        import tkinter as tk  # noqa: WPS433
    except Exception:  # pragma: no cover - depends on the local Python build
        return None, None
    try:
        root = tk.Tk()
    except Exception:  # pragma: no cover - no desktop / no display
        return None, None
    root.withdraw()
    return tk, root


def choose(title: str, options: Sequence[Tuple[str, str]]) -> Tuple[int, Optional[str]]:
    """(exit code, chosen value) - a modal window with one radio button per option."""
    tk, root = _tk_root()
    if tk is None:
        return NO_DIALOG, None
    root.deiconify()
    root.title(title)
    root.attributes("-topmost", True)
    var = tk.StringVar(value=options[0][0])
    result = {"code": CANCELLED, "value": None}
    tk.Label(root, text=title, padx=12, pady=8, anchor="w", justify="left").pack(fill="x")
    for value, label in options:
        tk.Radiobutton(root, text=label, variable=var, value=value, anchor="w",
                       justify="left", padx=18).pack(fill="x")

    def ok():
        result["code"], result["value"] = CHOSEN, var.get()
        root.destroy()

    def cancel():
        root.destroy()

    bar = tk.Frame(root, pady=10)
    bar.pack()
    tk.Button(bar, text="OK - buduj", width=14, command=ok).pack(side="left", padx=8)
    tk.Button(bar, text="Anuluj", width=14, command=cancel).pack(side="left", padx=8)
    root.protocol("WM_DELETE_WINDOW", cancel)
    root.bind("<Return>", lambda _e: ok())
    root.bind("<Escape>", lambda _e: cancel())
    root.update_idletasks()
    root.geometry("+%d+%d" % ((root.winfo_screenwidth() - root.winfo_reqwidth()) // 2,
                              (root.winfo_screenheight() - root.winfo_reqheight()) // 3))
    for step in ("deiconify", "lift", "focus_force"):  # in front of the console window
        try:
            getattr(root, step)()
        except Exception:
            pass
    root.mainloop()
    return result["code"], result["value"]


def parse_option(text: str) -> Tuple[str, str]:
    value, sep, label = text.partition("|")
    if not sep or not value or not label:
        raise argparse.ArgumentTypeError(f"--option needs VALUE|LABEL, got {text!r}")
    return value, label


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("what", choices=sorted(PRESETS) + ["custom"])
    parser.add_argument("--out", required=True, type=Path,
                        help="file that receives the chosen value (no newline)")
    parser.add_argument("--title", default=None)
    parser.add_argument("--option", action="append", type=parse_option, default=[],
                        metavar="VALUE|LABEL", help="an option for 'custom' (repeatable)")
    args = parser.parse_args(argv)

    if args.what == "custom":
        options = list(args.option)
        title = args.title or "Wybierz"
    else:
        preset = PRESETS[args.what]
        options = list(preset["options"])
        title = args.title or preset["title"]
    if not options:
        parser.error("no options to choose from")
    code, value = choose(title, options)
    if code == CHOSEN and value is not None:
        args.out.write_text(value, encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
