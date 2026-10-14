#!/usr/bin/env python3
"""Sub-file bisection: recombine an ORIGINAL container with a BUILT one, member by member.

``BISEKCJA.bat`` narrows a crash to one container (2026-10-14: ``config00.cpk``).  The next step
is *inside* the container: which of its changed sub-files (``.pac`` entries or CPK members) the
game objects to.  This tool takes the original container and the built container and writes a
hybrid in which only the named sub-files come from the build; everything else stays original.
No text is written here - the sub-files are copied as the builder produced them - so a variant
is exactly "the build, minus the members you leave original".

Variants of the same container differ only in which members are taken, so a crash table over a
handful of variants pins the member without any new writer code.  ``--pad-only`` is the control
experiment: nothing taken, the ``.pac`` is padded with zero bytes to the built one's size (does
the game mind the *size* alone?).

Usage::

    python tools/container_mix.py --original local/usrdir/config00.cpk \
        --built local/build9/DLC/config00.cpk --list
    python tools/container_mix.py --original ... --built ... --take "srwDL_DLC_ID00.bin" \
        --out local/bisect/V1/config00.cpk
    python tools/container_mix.py --original ... --built ... --take "*" --keep "srwDL_DLC_ID00.bin" \
        --out local/bisect/V5/config00.cpk
    python tools/container_mix.py --original ... --built ... --pad-only --out local/bisect/V6/config00.cpk

``--take`` / ``--keep`` are globs over sub-file names; ``--keep`` wins.  The report (JSON next to
the output, ``<name>.mix.json``) lists every member, where it came from, its size and MD5, so a
tested variant is reproducible from the two inputs.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP  # noqa: E402
import cpk_write  # noqa: E402


class MixError(Exception):
    pass


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def members_of(path: Path) -> Tuple[object, Dict[str, bytes], Optional[str]]:
    """(cpk, {sub name: data}, pac member name or None) of a container.

    A container whose single member is a ``.pac`` is opened one level deeper (``config00.cpk``,
    ``configst.cpk``, the DLC ``configNN.EDAT``); any other container is mixed at CPK-member level.
    """
    cpk = cpk_write.load(path)
    if len(cpk.members) == 1 and cpk.members[0].name.lower().endswith(".pac"):
        member = cpk.members[0]
        pac = CSP.parse_pac(cpk_write.decompressed(member.blob))
        return cpk, {s["name"]: s["data"] for s in pac["subs"]}, member.name
    return cpk, {m.name: cpk_write.decompressed(m.blob) for m in cpk.members}, None


def selected(name: str, take: Sequence[str], keep: Sequence[str]) -> bool:
    if any(fnmatch.fnmatch(name, pattern) for pattern in keep):
        return False
    return any(fnmatch.fnmatch(name, pattern) for pattern in take)


def plan(original: Dict[str, bytes], built: Dict[str, bytes], take: Sequence[str],
         keep: Sequence[str]) -> List[dict]:
    """One entry per member: source ('original' | 'built'), sizes, whether the build changed it."""
    if list(original) != list(built):
        raise MixError("the two containers do not hold the same members in the same order")
    rows = []
    for name in original:
        changed = original[name] != built[name]
        use_built = changed and selected(name, take, keep)
        rows.append({"member": name, "changed_by_build": changed,
                     "source": "built" if use_built else "original",
                     "size_original": len(original[name]), "size_built": len(built[name]),
                     "md5_original": _md5(original[name]), "md5_built": _md5(built[name])})
    return rows


def mix(original_path: Path, built_path: Path, take: Sequence[str], keep: Sequence[str],
        pad_only: bool = False) -> Tuple[bytes, dict]:
    cpk, orig_members, pac_name = members_of(original_path)
    _cpk_b, built_members, pac_name_b = members_of(built_path)
    if pac_name != pac_name_b:
        raise MixError("original and built containers have different shapes")
    rows = plan(orig_members, built_members, () if pad_only else take, keep)
    chosen = {r["member"]: built_members[r["member"]] for r in rows if r["source"] == "built"}
    report = {"original": str(original_path), "built": str(built_path), "pad_only": pad_only,
              "take": list(take), "keep": list(keep), "members": rows,
              "taken": sorted(chosen), "changed_by_build": [r["member"] for r in rows
                                                            if r["changed_by_build"]]}
    if pac_name is not None:
        member = cpk.members[0]
        pac = CSP.parse_pac(cpk_write.decompressed(member.blob))
        for sub in pac["subs"]:
            if sub["name"] in chosen:
                sub["data"] = chosen[sub["name"]]
        new_pac = CSP.rebuild_pac(pac)
        if pad_only:
            built_len = len(cpk_write.decompressed(_cpk_b.members[0].blob))
            if built_len < len(new_pac):
                raise MixError("--pad-only: the built pac is smaller than the original")
            new_pac = new_pac + b"\x00" * (built_len - len(new_pac))
        if not chosen and not pad_only:
            out = cpk.data                                 # nothing taken: the original, verbatim
        else:
            out = cpk_write.rebuild(cpk, replacement=(pac_name, new_pac))
        report["pac_size"] = len(new_pac)
    else:
        if pad_only:
            raise MixError("--pad-only needs a single-.pac container")
        if len(chosen) > 1:
            raise MixError("CPK-level mixing supports one member per run (rebuild swaps one)")
        out = cpk.data
        for name, data in chosen.items():
            out = cpk_write.rebuild(cpk, replacement=(name, data))
    report["size"] = len(out)
    report["md5"] = _md5(out)
    return out, report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--built", required=True, type=Path)
    parser.add_argument("--take", nargs="*", default=[], metavar="GLOB",
                        help="members to take from the built container (globs)")
    parser.add_argument("--keep", nargs="*", default=[], metavar="GLOB",
                        help="members to keep original even when --take matches (globs)")
    parser.add_argument("--pad-only", action="store_true",
                        help="take nothing; pad the original .pac to the built size")
    parser.add_argument("--list", action="store_true", help="show the members the build changed")
    parser.add_argument("--out", type=Path, help="output container (report written next to it)")
    args = parser.parse_args(argv)

    if args.list:
        _cpk, orig_members, _pac = members_of(args.original)
        _cpk_b, built_members, _pac_b = members_of(args.built)
        for row in plan(orig_members, built_members, args.take, args.keep):
            flag = "CHANGED" if row["changed_by_build"] else "same   "
            print(f"{flag} {row['member']:30s} {row['size_original']:8d} -> {row['size_built']:8d}")
        return 0
    if args.out is None:
        parser.error("--out is required unless --list")
    try:
        data, report = mix(args.original, args.built, args.take, args.keep, args.pad_only)
    except (MixError, cpk_write.CpkError if hasattr(cpk_write, "CpkError") else MixError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    report_path = args.out.with_name(args.out.name + ".mix.json")
    report_path.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{args.out}: {len(data)} B md5 {report['md5']}; taken from the build: "
          f"{', '.join(report['taken']) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
