#!/usr/bin/env python3
"""Bisection INSIDE one convention-B member (e.g. ``srwDL_Skill00.bin``): what part of a rebuilt
member makes the game crash - its size, its record texts, or its fragment pool?

Round 1 of the sub-file bisection (``container_mix``) showed that ``config00.cpk`` with ONLY the
rebuilt ``srwDL_Skill00.bin`` crashes at "Loading" (variant V2, build #10, pool pointers right),
while the rebuilt dictionaries/DLC list do not.  This tool takes the ORIGINAL container and the
BUILT one, and writes one container per variant in which only that member differs:

``pad``          original member + zero padding to the built member's size (size only);
``rec_en_pool_jp`` the built records (English texts, pool pointers right) + the ORIGINAL pool strings;
``rec_jp_pool_en`` the original records + the built (English) pool strings, table recomputed;
``names_only``   original member with only ``name``/``name_level`` taken from the build (effects,
                 brief, label and the pool stay Japanese) - rebuilt with ``item_skill_write``;
``effects_only`` the complement: ``effect``/``effect_brief``/``label`` from the build, names Japanese;
``half_a`` / ``half_b``  all five fields from the build for the first / second half of the records.

Round 2 answered with ``pad`` alone: the ORIGINAL member + zeros to the built size crashes too
(S1, 2026-10-15), so the texts are not what the loader trips over - the size is (or the zeros).
The **size ladder** (``--ladder``) settles that with structurally valid growth: the original
Japanese texts, with spaces appended to ``effect`` fields (4 at a time, round robin, no field and
no line longer than the member's own Japanese maximum), until the member has exactly the requested
size - records grow, the pool moves, pointers are recomputed, i.e. the same kind of growth a
translation causes.  One container per size; the game then tells which rung still loads.

Every variant is re-parsed (record count, pool pointers, pool strings) before it is written, and the
report next to it carries sizes and md5s only.  Game text never leaves ``local/``.

Usage::

    python tools/member_variants.py --original local/usrdir/config00.cpk \\
        --built local/build10/DLC/config00.cpk --member srwDL_Skill00.bin --out-dir local/round2
    python tools/member_variants.py --original local/usrdir/config00.cpk --member srwDL_Skill00.bin \\
        --ladder 210942 212990 217086 221182 225278 228202 --out-dir local/round3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP  # noqa: E402
import container_mix as CM  # noqa: E402
import cpk_write  # noqa: E402
import item_skill_records as ISR  # noqa: E402
import item_skill_write as ISW  # noqa: E402

VARIANTS = ("pad", "rec_en_pool_jp", "rec_jp_pool_en", "names_only", "effects_only", "half_a", "half_b")
NAME_ROLES = ("name", "name_level")
EFFECT_ROLES = ("effect", "effect_brief", "label")


class VariantError(Exception):
    """The member cannot be varied safely (layout not understood)."""


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def field_bytes(blob: bytes, row: dict) -> Dict[str, bytes]:
    """The five text fields of one record as raw bytes (NUL and slack stripped)."""
    offset, length = row["offset"], row["length"]
    bounds = struct.unpack_from("<6H", blob, offset + ISR.BOUNDARY_TABLE)
    rec = blob[offset:offset + length]
    return {role: rec[bounds[k]:bounds[k + 1]].rstrip(b"\x00") for k, role in enumerate(ISR.FIELDS)}


def parsed(blob: bytes, kind: str, member: str) -> dict:
    out = ISR.parse_member(blob, kind, member)
    if out["errors"]:
        raise VariantError(f"{member}: does not parse: {out['errors'][:2]}")
    return out


def edits_between(original: bytes, built: bytes, kind: str, member: str,
                  roles: Sequence[str], records: Optional[range] = None) -> Dict[int, Dict[str, bytes]]:
    """Per-record edits that carry the built member's bytes for ``roles`` (where they differ)."""
    po, pb = parsed(original, kind, member), parsed(built, kind, member)
    if len(po["records"]) != len(pb["records"]):
        raise VariantError(f"{member}: record counts differ ({len(po['records'])} vs {len(pb['records'])})")
    edits: Dict[int, Dict[str, bytes]] = {}
    for ro, rb in zip(po["records"], pb["records"]):
        if records is not None and ro["record"] not in records:
            continue
        fo, fb = field_bytes(original, ro), field_bytes(built, rb)
        changed = {role: fb[role] for role in roles if fo[role] != fb[role]}
        if changed:
            edits[ro["record"]] = changed
    return edits


def pool_strings(blob: bytes, kind: str, member: str) -> Tuple[int, List[bytes]]:
    p = parsed(blob, kind, member)
    _, strings = ISR.parse_tail_pool(blob, p["tail_offset"])
    return p["tail_offset"], strings


def make_variant(name: str, original: bytes, built: bytes, kind: str, member: str) -> bytes:
    if name == "pad":
        if len(built) < len(original):
            raise VariantError("pad: the built member is smaller than the original")
        return original + b"\x00" * (len(built) - len(original))
    if name == "rec_en_pool_jp":
        tail_b, _ = pool_strings(built, kind, member)
        _, strings_o = pool_strings(original, kind, member)
        return built[:tail_b] + ISR.build_tail_pool(tail_b, strings_o)
    if name == "rec_jp_pool_en":
        tail_o, _ = pool_strings(original, kind, member)
        _, strings_b = pool_strings(built, kind, member)
        return original[:tail_o] + ISR.build_tail_pool(tail_o, strings_b)
    if name == "names_only":
        out, _ = ISW.rebuild_member(original, kind, edits_between(original, built, kind, member, NAME_ROLES), member)
        return out
    if name == "effects_only":
        out, _ = ISW.rebuild_member(original, kind, edits_between(original, built, kind, member, EFFECT_ROLES), member)
        return out
    if name in ("half_a", "half_b"):
        count = len(parsed(original, kind, member)["records"])
        half = count // 2
        rng = range(0, half) if name == "half_a" else range(half, count)
        out, _ = ISW.rebuild_member(original, kind, edits_between(original, built, kind, member, ISR.FIELDS, rng), member)
        return out
    raise VariantError(f"unknown variant {name!r}")


def check(blob: bytes, kind: str, member: str, reference: bytes) -> dict:
    """Re-parse a variant: same record count as the reference, pool pointers right, pool parses."""
    p = parsed(blob, kind, member)
    ref = parsed(reference, kind, member)
    faults = ISW.pool_pointer_faults(blob, p) + ISW.base_pointer_faults(blob, p)
    _, strings = ISR.parse_tail_pool(blob, p["tail_offset"])
    if len(p["records"]) != len(ref["records"]) or faults:
        raise VariantError(f"{member}: variant does not hold (records {len(p['records'])}, "
                           f"pointer faults {len(faults)})")
    return {"records": len(p["records"]), "tail_offset": p["tail_offset"], "pool_strings": len(strings),
            "size": len(blob), "md5": _md5(blob)}


def with_member(original_path: Path, member: str, data: bytes,
                align: Optional[int] = None) -> Tuple[bytes, int]:
    """The original container with ONE sub-file replaced; returns (bytes, pac size).

    ``align`` re-packs the ``.pac`` with that placement unit for ALL sub-files (default: the
    original 0x800); the member itself may be the original bytes - then only the packing changes.
    """
    cpk, _members, pac_name = CM.members_of(original_path)
    if pac_name is None:
        raise VariantError("only single-.pac containers are supported")
    pac = CSP.parse_pac(cpk_write.decompressed(cpk.members[0].blob))
    hit = False
    for sub in pac["subs"]:
        if sub["name"] == member:
            sub["data"] = data
            hit = True
    if not hit:
        raise VariantError(f"{member} is not in {original_path.name}")
    new_pac = CSP.rebuild_pac(pac) if align is None else CSP.rebuild_pac(pac, align)
    return cpk_write.rebuild(cpk, replacement=(pac_name, new_pac)), len(new_pac)


def space_room(effect: bytes, max_field: int, max_line: int) -> int:
    """How many bytes of spaces ``effect`` can take at its end without exceeding ``max_field``
    bytes in total or ``max_line`` bytes on its last line."""
    last = effect.rsplit(b"\n", 1)[-1]
    return max(0, min(max_field - len(effect), max_line - len(last)))


def grow_with_spaces(original: bytes, kind: str, member: str, target_size: int,
                     max_field: Optional[int] = None, max_line: Optional[int] = None) -> bytes:
    """The original member grown to exactly ``target_size`` bytes by appending spaces to ``effect``
    texts (4 bytes per record per round, round robin over the records that still have room).

    ``max_field`` / ``max_line`` default to the member's own maxima, so no field and no line gets
    longer than the longest Japanese one.  Records are 4-byte aligned, so ``target_size`` must be
    the original size plus a multiple of 4; the pool keeps its strings and moves behind the records.
    """
    p = parsed(original, kind, member)
    effects = {row["record"]: field_bytes(original, row)["effect"] for row in p["records"]}
    if max_field is None:
        max_field = max(len(e) for e in effects.values())
    if max_line is None:
        max_line = max(len(line) for e in effects.values() for line in e.split(b"\n"))
    need = target_size - len(original)
    if need < 0 or need % 4:
        raise VariantError(f"target {target_size} must be the original size {len(original)} plus a "
                           f"multiple of 4")
    if need == 0:
        return original      # the rung at the original size is the original member, byte for byte
    added = {key: 0 for key in effects}
    while need > 0:
        progressed = False
        for key, effect in effects.items():
            if need <= 0:
                break
            if space_room(effect + b" " * added[key], max_field, max_line) >= 4:
                added[key] += 4
                need -= 4
                progressed = True
        if not progressed:
            raise VariantError(f"{member}: not enough room for {target_size - len(original)} bytes of "
                               f"spaces with fields <= {max_field} B and lines <= {max_line} B")
    edits = {key: {"effect": effects[key] + b" " * count} for key, count in added.items() if count}
    out, _ = ISW.rebuild_member(original, kind, edits, member)
    if len(out) != target_size:
        raise VariantError(f"{member}: grew to {len(out)} B, wanted {target_size}")
    return out


def build_ladder(original_path: Path, member: str, sizes: Sequence[int], out_dir: Path,
                 labels: Optional[Dict[int, str]] = None, max_field: Optional[int] = None,
                 max_line: Optional[int] = None, align: Optional[int] = None) -> List[dict]:
    """One container per requested member size (original texts + spaces); see grow_with_spaces.

    ``align`` re-packs the ``.pac`` with a smaller placement unit (sub-files packed closer, same
    bytes) - a size rung can then be combined with a SMALLER container than the original.
    """
    kind = ISW._kind_of(member)
    if kind is None:
        raise VariantError(f"{member} is not a convention-B member this tool knows")
    _c, orig_members, _p = CM.members_of(original_path)
    original = orig_members[member]
    reports = []
    for index, size in enumerate(sizes, 1):
        label = (labels or {}).get(size, f"T{index}")
        data = grow_with_spaces(original, kind, member, size, max_field, max_line)
        info = check(data, kind, member, original)
        container, pac_size = with_member(original_path, member, data, align)
        folder = out_dir / label
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / original_path.name
        target.write_bytes(container)
        variant = f"spaces_{size}" if size != len(original) else "original_member"
        if align is not None:
            variant += f"_pac_align_{align}"
        report = {"label": label, "variant": variant, "member": member, "pac_align": align or CSP.ALIGN,
                  "member_original_size": len(original), "member_built_size": size,
                  "member_variant": info, "pac_size": pac_size,
                  "container_size": len(container), "container_md5": _md5(container)}
        target.with_name(target.name + ".variant.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        reports.append(report)
    return reports


def build_all(original_path: Path, built_path: Path, member: str, out_dir: Path,
              variants: Sequence[str] = VARIANTS, labels: Optional[Dict[str, str]] = None) -> List[dict]:
    kind = ISW._kind_of(member)
    if kind is None:
        raise VariantError(f"{member} is not a convention-B member this tool knows")
    _c, orig_members, _p = CM.members_of(original_path)
    _c2, built_members, _p2 = CM.members_of(built_path)
    original, built = orig_members[member], built_members[member]
    if original == built:
        raise VariantError(f"{member} is identical in both containers - nothing to vary")
    reports = []
    for index, name in enumerate(variants, 1):
        label = (labels or {}).get(name, f"S{index}")
        data = make_variant(name, original, built, kind, member)
        # the padded member is checked on its structured part - the zeros behind the pool are
        # exactly what the variant is about (the loader copies them, the parser never reads them)
        info = check(data[:len(original)] if name == "pad" else data, kind, member, original)
        info["size"], info["md5"] = len(data), _md5(data)
        container, pac_size = with_member(original_path, member, data)
        folder = out_dir / label
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / original_path.name
        target.write_bytes(container)
        report = {"label": label, "variant": name, "member": member, "member_original_size": len(original),
                  "member_built_size": len(built), "member_variant": info, "pac_size": pac_size,
                  "container_size": len(container), "container_md5": _md5(container)}
        target.with_name(target.name + ".variant.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        reports.append(report)
    return reports


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--built", type=Path, help="the rebuilt container (variants S1..)")
    parser.add_argument("--member", required=True, help="e.g. srwDL_Skill00.bin")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--variants", nargs="*", default=list(VARIANTS), choices=VARIANTS)
    parser.add_argument("--ladder", nargs="+", type=int, metavar="SIZE",
                        help="size ladder instead: member sizes to grow the ORIGINAL to with spaces")
    parser.add_argument("--max-field", type=int, help="ladder: effect field cap in bytes "
                        "(default: the member's own Japanese maximum)")
    parser.add_argument("--max-line", type=int, help="ladder: effect line cap in bytes (default: own maximum)")
    parser.add_argument("--align", type=int, help="ladder: re-pack the .pac with this placement unit "
                        "for all sub-files (default: the original 2048)")
    parser.add_argument("--labels", nargs="+", help="ladder: folder names, one per SIZE (default T1..)")
    args = parser.parse_args(argv)
    if args.ladder is None and args.built is None:
        parser.error("either --built (variants) or --ladder SIZE ... (size ladder) is required")
    try:
        if args.ladder is not None:
            if args.labels and len(args.labels) != len(args.ladder):
                parser.error("--labels needs one name per --ladder SIZE")
            labels = dict(zip(args.ladder, args.labels)) if args.labels else None
            reports = build_ladder(args.original, args.member, args.ladder, args.out_dir, labels,
                                   max_field=args.max_field, max_line=args.max_line, align=args.align)
        else:
            reports = build_all(args.original, args.built, args.member, args.out_dir, args.variants)
    except (VariantError, ISW.WriteError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    for r in reports:
        v = r["member_variant"]
        print(f"{r['label']:4} {r['variant']:15} member {v['size']:>7} B (orig {r['member_original_size']}, "
              f"built {r['member_built_size']})  pac {r['pac_size']}  container {r['container_size']} "
              f"md5 {r['container_md5']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
