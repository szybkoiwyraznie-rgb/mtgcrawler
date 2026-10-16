#!/usr/bin/env python3
"""Build UI containers (``system.cpk``, ``IM1000.cpk`` …) with English captions painted into
their GIM textures.

Pipeline (all offline, originals only read):

1. every spec in ``ui_labels/*.json`` names one texture (``mensys_03`` …);
2. each original container is opened (``speaker_map.read_members`` → CRILAYLA-decompressed
   member), its PAC index is walked — nested ``*.pac`` included — and every ``<texture>.gim``
   that has a spec is rendered with :mod:`gim_label` and spliced back **at the same offset
   with the same length** (the encoder keeps the palette and all headers);
3. the member is written back either STORED (``--compress stored``) or re-compressed with
   our CRILAYLA encoder (``--compress crilayla``), through ``cpk_itoc_write`` (ITOC-only
   containers such as ``system.cpk``) or ``cpk_write`` (TOC containers such as ``IM1000.cpk``);
4. the new container is read back: every patched GIM must decode to the rendered pixels and
   every other byte of the member must be unchanged, or the run fails.

Only containers that actually hold a spec'd texture are written.  A JSON report (names,
sizes, md5, per-label fit) is written next to them; no game bytes are printed or logged.

Usage::

    python tools/ui_texture_patch.py --originals local/usrdir_ui --out local/ui_build \\
        [--specs ui_labels] [--compress stored|crilayla] [--preview-dir DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cpk_itoc_write  # noqa: E402
import cpk_write  # noqa: E402
import crilayla  # noqa: E402
import gim_image  # noqa: E402
import gim_label  # noqa: E402
import speaker_map  # noqa: E402

ROOT = HERE.parent
DEFAULT_SPECS = ROOT / "ui_labels"


class UiPatchError(Exception):
    """Refused: the message says what is wrong; nothing half-written."""


@dataclass
class Occurrence:
    container: str
    member: str
    path: str            # e.g. "srwDL_Inter_Tex.pac/intsys_01.gim"
    offset: int          # absolute offset inside the decompressed member
    size: int


@dataclass
class ContainerResult:
    name: str
    kind: str
    original_size: int
    original_md5: str
    new_size: int = 0
    new_md5: str = ""
    member_size: int = 0          # unpacked bytes of the rewritten member(s), summed
    member_stored_as: int = 0     # packed bytes of the rewritten member(s), summed
    members: List[dict] = field(default_factory=list)   # [{name, index, size, stored_as}]
    textures: List[str] = field(default_factory=list)
    labels: Dict[str, List[dict]] = field(default_factory=dict)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def load_specs(spec_dir: Path) -> Dict[str, dict]:
    specs: Dict[str, dict] = {}
    for p in sorted(Path(spec_dir).glob("*.json")):
        spec = gim_label.load_spec(p)
        name = spec["texture"]
        if name in specs:
            raise UiPatchError(f"two specs for texture {name!r}")
        spec["_file"] = str(p)
        specs[name] = spec
    if not specs:
        raise UiPatchError(f"no label specs in {spec_dir}")
    return specs


def walk_gims(blob: bytes, prefix: str = "", member_name: str = "") -> List[Tuple[str, int, int]]:
    """(path, absolute offset, size) of every ``*.gim`` in a PAC, nested PACs included.

    A member that *is* a GIM (``navisys.cpk`` holds ``navisys_01.gim`` / ``navisys_02.gim``
    directly, no PAC around them) counts as one hit covering the whole blob.
    """
    if member_name.lower().endswith(".gim") and blob[:4] == gim_image.MAGIC[:4]:
        return [(prefix + member_name, 0, len(blob))]
    try:
        entries = gim_image.pac_entries(blob)
    except gim_image.GimError:
        return []
    out: List[Tuple[str, int, int]] = []
    for name, off, size in entries:
        if name.lower().endswith(".gim"):
            out.append((prefix + name, off, size))
        elif name.lower().endswith(".pac"):
            for sub, soff, ssize in walk_gims(blob[off:off + size], prefix + name + "/"):
                out.append((sub, off + soff, ssize))
    return out


def container_kind(path: Path) -> str:
    """'itoc' for ITOC-only containers, 'toc' for containers with a TOC."""
    try:
        cpk_itoc_write.load(path)
        return "itoc"
    except cpk_itoc_write.ItocWriteError as exc:
        if "has a TOC" in str(exc):
            return "toc"
        raise UiPatchError(f"{path.name}: {exc}") from exc


def patch_member(blob: bytes, hits: List[Tuple[str, int, int]], specs: Dict[str, dict],
                 report: ContainerResult, preview_dir: Optional[Path]) -> Tuple[bytes, Dict[int, bytes]]:
    """Render every spec'd GIM found in ``blob``; returns (new blob, {offset: new gim raw})."""
    out = bytearray(blob)
    expected: Dict[int, bytes] = {}
    for path, off, size in hits:
        texture = Path(path).stem
        spec = specs.get(texture)
        if spec is None:
            continue
        raw = blob[off:off + size]
        try:
            new_raw, rep, _ = gim_label.render_labels(raw, spec)
        except gim_label.LabelError as exc:
            raise UiPatchError(f"{report.name}/{path}: {exc}") from exc
        if len(new_raw) != size:
            raise UiPatchError(f"{report.name}/{path}: encoder changed the size")
        out[off:off + size] = new_raw
        expected[off] = new_raw
        report.textures.append(path)
        report.labels[path] = [
            {"id": r.id, "en": r.en, "box": list(r.box), "size": r.size, "text_width": r.text_width,
             "x_scale": r.x_scale, "kept": r.skipped, "erased": r.erased} for r in rep.labels]
        if preview_dir:
            gim_label.preview(raw, preview_dir / f"{texture}_before.png", 4,
                              [lab["box"] for lab in spec["labels"]])
            gim_label.preview(new_raw, preview_dir / f"{texture}_after.png", 4)
    return bytes(out), expected


def store(blob: bytes, mode: str) -> bytes:
    if mode == "stored":
        return blob
    if mode == "crilayla":
        packed = crilayla.compress(blob)
        if crilayla.decompress(packed).data != blob:
            raise UiPatchError("CRILAYLA round trip failed")
        return packed
    raise UiPatchError(f"unknown --compress mode {mode!r}")


def verify_container(path: Path, member_index: int, member_name: str, new_blob: bytes) -> None:
    members = speaker_map.read_members(path)
    if member_index >= len(members):
        raise UiPatchError(f"{path.name}: member {member_index} missing after rebuild")
    name, got = members[member_index]
    if got != new_blob:
        raise UiPatchError(f"{path.name}: member {member_name!r} does not read back identical")


def build(originals: Path, out_dir: Path, specs: Dict[str, dict], compress: str,
          preview_dir: Optional[Path] = None) -> List[ContainerResult]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: List[ContainerResult] = []
    for cpk_path in sorted(Path(originals).glob("*.cpk")):
        try:
            members = speaker_map.read_members(cpk_path)
        except Exception:  # not a container we can read (fail per file, report)
            continue
        # which members hold a spec'd texture (PAC members are walked, GIM members count whole)
        targets: List[Tuple[int, str, bytes, List[Tuple[str, int, int]]]] = []
        for index, (member_name, blob) in enumerate(members):
            hits = walk_gims(blob, member_name=member_name)
            if any(Path(p).stem in specs for p, _, _ in hits):
                targets.append((index, member_name, blob, hits))
        if not targets:
            continue
        data = cpk_path.read_bytes()
        kind = container_kind(cpk_path)
        res = ContainerResult(cpk_path.name, kind, len(data), md5(data))
        if kind == "itoc" and len(members) != 1:
            raise UiPatchError(f"{cpk_path.name}: {len(members)} members in an ITOC-only container — "
                               f"cpk_itoc_write handles single-member containers only")
        out_path = out_dir / cpk_path.name
        current = cpk_path            # the container the next rewrite starts from
        rewritten: List[Tuple[int, str, bytes, Dict[int, bytes]]] = []
        for index, member_name, blob, hits in targets:
            new_blob, expected = patch_member(blob, hits, specs, res, preview_dir)
            # everything outside the GIM spans must be byte-identical
            check = bytearray(new_blob)
            for off, raw in expected.items():
                check[off:off + len(raw)] = blob[off:off + len(raw)]
            if bytes(check) != blob:
                raise UiPatchError(f"{cpk_path.name}/{member_name}: bytes outside the textures changed")
            packed = store(new_blob, compress)
            if kind == "itoc":
                cpk = cpk_itoc_write.load(current)
                new_data = cpk_itoc_write.rebuild(cpk, {0: (packed, len(new_blob))})
            else:
                cpk = cpk_write.load(current)
                new_data = cpk_write.rebuild(cpk, (member_name, packed, len(new_blob)))
            out_path.write_bytes(new_data)
            current = out_path        # a second member is rewritten on top of the first
            rewritten.append((index, member_name, new_blob, expected))
            res.member_size += len(new_blob)
            res.member_stored_as += len(packed)
            res.members.append({"name": member_name, "index": index, "size": len(new_blob),
                                "stored_as": len(packed)})
        new_data = out_path.read_bytes()
        back_members = speaker_map.read_members(out_path)
        if len(back_members) != len(members):
            raise UiPatchError(f"{cpk_path.name}: {len(back_members)} members after the rebuild, "
                               f"expected {len(members)}")
        for index, member_name, new_blob, expected in rewritten:
            verify_container(out_path, index, member_name, new_blob)
            # and the textures decode to what we rendered
            back = back_members[index][1]
            for off, raw in expected.items():
                if back[off:off + len(raw)] != raw:
                    raise UiPatchError(f"{cpk_path.name}/{member_name}: texture at {off} did not "
                                       f"survive the rebuild")
        # untouched members must read back byte-identical too
        touched = {index for index, _, _, _ in rewritten}
        for index, (member_name, blob) in enumerate(members):
            if index not in touched and back_members[index][1] != blob:
                raise UiPatchError(f"{cpk_path.name}/{member_name}: an untouched member changed")
        res.new_size, res.new_md5 = len(new_data), md5(new_data)
        results.append(res)
    if not results:
        raise UiPatchError(f"no container in {originals} holds a spec'd texture")
    return results


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--originals", type=Path, required=True, help="folder with the ORIGINAL *.cpk")
    ap.add_argument("--out", type=Path, required=True, help="output folder for the patched *.cpk")
    ap.add_argument("--specs", type=Path, default=DEFAULT_SPECS)
    ap.add_argument("--compress", choices=("stored", "crilayla"), default="stored")
    ap.add_argument("--preview-dir", type=Path)
    args = ap.parse_args(argv)
    try:
        specs = load_specs(args.specs)
        results = build(args.originals, args.out, specs, args.compress, args.preview_dir)
    except (UiPatchError, gim_label.LabelError, gim_image.GimError, cpk_itoc_write.ItocWriteError,
            ValueError, OSError) as exc:
        print(f"REFUSED — {exc}")
        return 1
    report = {"compress": args.compress, "specs": sorted(Path(s["_file"]).name for s in specs.values()),
              "containers": [vars(r) for r in results]}
    (args.out / "ui_texture_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                     encoding="utf-8")
    for r in results:
        print(f"{r.name}: {r.kind}, {r.original_size} -> {r.new_size} bytes (member {r.member_size} "
              f"stored as {r.member_stored_as}), textures: {', '.join(r.textures)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
