#!/usr/bin/env python3
"""Build a test ISO: the user's own disc plus the translated dialogue lines.

The repository carries no game data, so this tool does not ship a patched container.  It reads
``PSP_GAME/USRDIR/eventP00.cpk`` out of the ISO in front of it, checks it against the hashes
recorded in the patch spec (a different edition therefore stops the run instead of being
silently corrupted), applies the English lines with the measured dialogue writer
(``event_text_apply``) and writes a new ISO in which only that one file is repointed.  The spec
holds offsets, hashes and our English lines only -- never Japanese game text.

Usage:
    python3 tools/iso_test_patch.py [in.iso] [out.iso] [--spec FILE] [--work DIR] [--dry-run]

Without an ``in.iso`` a file dialog opens (the same way ``run_pipeline`` asks for its folders), and
the test ISO is written next to the disc the user picked, as ``<name>-test.iso``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import event_text_apply as ETA  # noqa: E402
import iso_pack  # noqa: E402
import speaker_map as SM  # noqa: E402

DEFAULT_SPEC = Path(__file__).resolve().parent.parent / "test-patches" / "eventP00-scena1.json"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def load_spec(path: Path) -> dict:
    """Read a patch spec and check the fields the run depends on."""
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    for field in ("container", "member", "lines"):
        if not spec.get(field):
            raise ValueError(f"{Path(path).name}: the spec has no {field!r}")
    for number, line in enumerate(spec["lines"], 1):
        if "offset" not in line or not line.get("text"):
            raise ValueError(f"{Path(path).name}: line {number} needs an offset and a text")
    return spec


def rows_from_spec(blob: bytes, member: str, spec: dict) -> Tuple[List[dict], List[str]]:
    """Writer rows for the spec lines, with the Japanese text read from the member itself.

    The spec deliberately carries no Japanese, so each target is located by the offset measured on
    the hashed file and the text that stands there is read back for the writer's own check.
    """
    records, _ = ETA.parse_block_records(blob)
    by_offset: Dict[int, dict] = {}
    for record in records:
        if record["type"] != ETA.RECORD_TEXT:
            continue
        at = record["offset"] + ETA.TEXT_OFFSET_IN_RECORD
        if at not in by_offset or record["size"] < by_offset[at]["size"]:
            by_offset[at] = record
    rows: List[dict] = []
    problems: List[str] = []
    for number, line in enumerate(spec["lines"], 1):
        offset = int(line["offset"])
        record = by_offset.get(offset)
        if record is None:
            problems.append(f"line {number}: no dialogue record starts at {offset} in this file "
                            "(a different game edition?)")
            continue
        rows.append({
            "id": f"test:{member}:{offset}",
            "category": "dialogue",
            "kind": "dialogue",
            "jp": ETA.text_of(blob, record).decode("cp932", "replace"),
            "en": line["text"],
            "source": {"container": spec["container"], "member": member, "offset": offset},
        })
    return rows, problems


def default_out_path(iso: Path) -> Path:
    """Where the test ISO goes when nobody says otherwise: next to the disc you picked."""
    iso = Path(iso)
    return iso.with_name(f"{iso.stem}-test.iso")


def choose_iso(initial: Optional[Path] = None) -> Optional[Path]:
    """Ask for the disc in a file dialog; None when Tk is missing, there is no desktop, or the
    user cancels (the caller then falls back to a typed path)."""
    try:
        import tkinter
        from tkinter import filedialog
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
    try:
        chosen = filedialog.askopenfilename(
            title="Wybierz swoja kopie ISO SRW OE (wersja 1.08)",
            initialdir=str(initial) if initial and Path(initial).is_dir() else None,
            filetypes=[("Obraz ISO", "*.iso"), ("Wszystkie pliki", "*.*")],
        )
    except tkinter.TclError:
        return None
    finally:
        root.destroy()
    return Path(chosen) if chosen else None


def prompt_iso() -> Optional[Path]:
    """Console fallback for machines without a dialog: one typed path, quotes allowed."""
    try:
        typed = input("Nie wybrano pliku ISO. Podaj sciezke do swojej kopii ISO: ").strip().strip('"')
    except EOFError:
        return None
    return Path(typed) if typed else None


def apply_test_patch(iso_in: Path, iso_out: Path, spec: dict, work: Optional[Path] = None,
                     dry_run: bool = False) -> dict:
    """Read the container from ``iso_in``, apply the spec and write ``iso_out``.

    Every step that could quietly corrupt something is a gate: the container and the member must
    hash to the values the offsets were measured on, every line must land in its own dialogue
    record, the writer's own verification must come out empty, and no member other than the one in
    the spec may change.  Only then is the ISO written.
    """
    iso_in, iso_out = Path(iso_in), Path(iso_out)
    container_name, member = spec["container"], spec["member"]
    report: dict = {"iso": str(iso_in), "container": container_name, "member": member,
                    "lines": len(spec["lines"]), "problems": [], "written": None}

    try:
        container = iso_pack.read_member(iso_in, container_name)
    except ValueError as error:
        raise ValueError(
            f"w tym pliku nie ma {container_name} ({error}) - podaj sciezke do pliku ISO gry, "
            "nie do innego pliku.") from error
    report["container_bytes"] = len(container)
    if spec.get("md5_container") and md5(container) != spec["md5_container"]:
        raise ValueError(
            f"kontener {container_name} w tym ISO ma inny skrot niz ten, na ktorym mierzylem "
            f"offsety (jest {md5(container)}, oczekiwany {spec['md5_container']}). "
            "To inna wersja gry - przerwij i zglos to, offsety trzeba zmierzyc od nowa.")

    with tempfile.TemporaryDirectory() as temporary:
        area = Path(work) if work else Path(temporary)
        area.mkdir(parents=True, exist_ok=True)
        original_path = area / "original.cpk"
        patched_path = area / "patched.cpk"
        original_path.write_bytes(container)

        members = dict(SM.read_members(original_path))
        if member not in members:
            raise ValueError(f"{container_name} has no member {member!r}")
        report["member_bytes"] = len(members[member])
        report["member_md5"] = md5(members[member])
        if spec.get("md5_member") and report["member_md5"] != spec["md5_member"]:
            raise ValueError(
                f"czlon {member} ma inny skrot niz zmierzony ({report['member_md5']} zamiast "
                f"{spec['md5_member']}) - to inna wersja gry, przerwij i zglos to.")

        rows, problems = rows_from_spec(members[member], member, spec)
        if problems:
            raise ValueError("; ".join(problems))

        result = ETA.apply_container(original_path, member, rows, patched_path)
        report["apply"] = {key: result[key] for key in
                           ("rows", "applied", "skipped", "refused", "problems", "bytes")}
        if (result["applied"] != len(rows) or result["problems"] or result["skipped"]
                or result["refused"]):
            raise ValueError(f"wtrysk nie wyszedl czysto: {json.dumps(report['apply'], ensure_ascii=False)}")
        # the writer walks the rows from the end of the file, the report reads better in file order
        report["replaced"] = [(offset, jp.decode("cp932", "replace"), en.decode("cp932", "replace"))
                              for offset, jp, en in sorted(result["changed"])]

        patched_members = dict(SM.read_members(patched_path))
        if sorted(patched_members) != sorted(members):
            raise ValueError("zbior czlonkow zmienil sie przy przebudowie")
        changed = [name for name in members if members[name] != patched_members[name]]
        report["changed_members"] = changed
        if changed != [member]:
            raise ValueError(f"poza {member!r} zmienily sie jeszcze: {changed}")
        report["container_delta"] = patched_path.stat().st_size - len(container)

        if dry_run:
            return report
        patched = patched_path.read_bytes()
        key, _, _ = iso_pack.find_member(iso_in, container_name)
        report["patch"] = iso_pack.patch_iso(iso_in, iso_out, {key: patched})
        report["written"] = str(iso_out)
        report["out_bytes"] = iso_out.stat().st_size
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("iso", type=Path, nargs="?", help="your own copy of the game ISO "
                                                          "(a file dialog opens when omitted)")
    parser.add_argument("out", type=Path, nargs="?", help="the test ISO to write "
                                                          "(default: next to the input)")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC, help="patch spec (default: %(default)s)")
    parser.add_argument("--work", type=Path, help="keep the intermediate containers in this directory")
    parser.add_argument("--dry-run", action="store_true", help="check everything, write nothing")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(errors="replace")  # konsola Windows nie ma japonskich znakow
    except Exception:
        pass

    iso = args.iso
    if iso is None:
        print("Wybierz swoje ISO w oknie, ktore sie zaraz otworzy...")
        iso = choose_iso() or prompt_iso()
    if iso is None:
        print("PRZERWANE: nie wybrano pliku ISO.")
        return 2
    iso = Path(iso)
    if not iso.is_file():
        print(f"PRZERWANE: nie ma pliku {iso}")
        return 2
    out = Path(args.out) if args.out else default_out_path(iso)
    args.iso, args.out = iso, out

    spec = load_spec(args.spec)
    print(f"ISO wejsciowe: {args.iso}")
    print(f"ISO wyjsciowe: {args.out}")
    print(f"kontener: {spec['container']} | czlon: {spec['member']} | linii w przepisie: {len(spec['lines'])}")
    try:
        report = apply_test_patch(args.iso, args.out, spec, args.work, args.dry_run)
    except (ValueError, OSError) as error:
        print(f"PRZERWANE: {error}")
        return 1

    print(f"kontener {report['container_bytes']} B (md5 {spec.get('md5_container', '?')})")
    print(f"czlon {report['member']}: {report['member_bytes']} B, po zmianie {report['apply']['bytes']:+d} B")
    print(f"linie: {report['apply']['applied']}/{report['lines']} wpisane, "
          f"pominiete {len(report['apply']['skipped'])}, odrzucone {len(report['apply']['refused'])}, "
          f"problemy {len(report['apply']['problems'])}")
    print("wymienione linie:")
    for number, (offset, jp, en) in enumerate(report["replaced"], 1):
        print(f"  [{number}] {offset}: {jp!r}")
        print(f"       -> {en!r}")
    print(f"zmienione czlonki: {', '.join(report['changed_members'])} (tylko ten)")
    print(f"kontener po zmianie: {report['container_delta']:+d} B")
    if report.get("written"):
        print(f"ISO wyjsciowe: {report['written']} ({report['out_bytes']} B)")
        print("Gotowe: uruchom to ISO w PPSSPP.")
    else:
        print("--dry-run: nic nie zapisalem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
