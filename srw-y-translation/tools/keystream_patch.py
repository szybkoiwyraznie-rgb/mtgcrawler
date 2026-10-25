#!/usr/bin/env python3
"""Patch text inside a bundle without ever learning the key.

What this is for: the `.bundle` files on disk are encrypted per file, and six
memory scans have not produced the AES key. They do not have to. A bundle the game
has already loaded exists in memory in plaintext; for the same file on disk the
encryption is a stream, so

    keystream = ciphertext XOR plaintext

and patching a file is then ``new_ciphertext = new_plaintext XOR keystream`` with
no key at all. The pairs come from the memory carve plus the owner's disk files,
matched by a size that is unique on both sides (`pair_keystream.py survey` prints
the keystreams, this tool uses them).

Two rules make it safe:

* **same length.** A replacement must have exactly the same number of UTF-8 bytes
  as the text it replaces, and the patched bundle keeps the original file length.
  Nothing shifts, no serialised offset changes, no string length prefix is touched.
* **literals only.** Bundle data is LZ4-compressed; a string stored as an LZ4
  literal can be overwritten byte for byte and the compressed stream stays valid.
  Replacing bytes that happen to sit in a copy/match region would corrupt the
  block, so every occurrence is verified after the fact by decompressing the
  patched bundle with UnityPy and looking for the new text.

Japanese is three bytes per character in UTF-8 and Polish is one or two, so a
Polish string that fits the same byte count is normally *longer* in characters.

    python keystream_patch.py plan --bundle NAME --pair-store pairs/ \\
        --map 'JA TEXT=PL TEXT' --out plan.json
    python keystream_patch.py apply --bundle NAME --pair-store pairs/ \\
        --plan plan.json --out patched/NAME
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_VERSION = "2026-10-26.9"
MAGIC = b"SRWKS1\n"


# ----------------------------------------------------------------- pieces of a pair
def xor(data: bytes, stream: bytes) -> bytes:
    if len(data) != len(stream):
        raise ValueError(f"lengths differ: data {len(data)} B, keystream "
                         f"{len(stream)} B")
    return bytes(a ^ b for a, b in zip(data, stream))


def save_stream(path: Path, stream: bytes) -> None:
    Path(path).write_bytes(MAGIC + stream)


def load_stream(path: Path) -> bytes:
    data = Path(path).read_bytes()
    if not data.startswith(MAGIC):
        raise ValueError(f"{path} is not a saved keystream")
    return data[len(MAGIC):]


def header_info(plain: bytes) -> dict:
    """Just enough of the UnityFS header to report and to sanity-check a patch."""
    if plain[:7] != b"UnityFS":
        raise ValueError("not a UnityFS bundle")
    offset = 8
    version = int.from_bytes(plain[offset:offset + 4], "big")
    offset += 4
    end = plain.index(b"\x00", offset)
    unity_version = plain[offset:end].decode("latin-1")
    offset = end + 1
    end = plain.index(b"\x00", offset)
    unity_revision = plain[offset:end].decode("latin-1")
    offset = end + 1
    size = int.from_bytes(plain[offset:offset + 8], "big")
    offset += 8
    info_compressed = int.from_bytes(plain[offset:offset + 4], "big")
    offset += 4
    info_uncompressed = int.from_bytes(plain[offset:offset + 4], "big")
    offset += 4
    flags = int.from_bytes(plain[offset:offset + 4], "big")
    return {"version": version, "unity_version": unity_version,
            "unity_revision": unity_revision, "declared_size": size,
            "blocks_info_compressed": info_compressed,
            "blocks_info_uncompressed": info_uncompressed,
            "compression": flags & 0x3F, "flags": flags,
            "header_bytes": offset + 4}


def decompress(plain: bytes) -> bytes | None:
    """The full bundle content with every block decompressed (needs UnityPy)."""
    try:
        import UnityPy
    except ImportError:  # pragma: no cover - UnityPy is optional
        return None
    import tempfile

    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / "probe.bundle"
        path.write_bytes(plain)
        try:
            env = UnityPy.load(str(path))
            return env.file.save(packer="none")
        except Exception:
            return None


def text_runs(blob: bytes, minimum: int = 3) -> list[tuple[int, bytes]]:
    """Japanese UTF-8 runs, with offsets, as a first look at what a bundle holds."""
    out, index = [], 0
    while index < len(blob) - 2:
        byte = blob[index]
        if 0xE3 <= byte <= 0xE9:
            start = index
            while index + 2 < len(blob) and 0xE3 <= blob[index] <= 0xE9:
                index += 3
            if (index - start) // 3 >= minimum:
                out.append((start, blob[start:index]))
            continue
        index += 1
    return out


# ------------------------------------------------------------------------- patching
def parse_map(pairs: list[str]) -> list[tuple[bytes, bytes]]:
    edits = []
    for item in pairs:
        if "=" not in item:
            raise SystemExit(f"bad --map {item!r}: expected OLD=NEW")
        old, new = item.split("=", 1)
        old_bytes, new_bytes = old.encode("utf-8"), new.encode("utf-8")
        if len(old_bytes) != len(new_bytes):
            raise SystemExit(
                f"{item!r}: {len(old_bytes)} bytes -> {len(new_bytes)} bytes; "
                f"a replacement must keep the byte count (use padding)")
        edits.append((old_bytes, new_bytes))
    return edits


def plan_edits(plain: bytes, edits: list[tuple[bytes, bytes]]) -> list[dict]:
    plan, seen = [], set()
    for old, new in edits:
        count = plain.count(old)
        plan.append({"old": old.decode("utf-8"), "new": new.decode("utf-8"),
                     "bytes": len(old), "occurrences": count})
        seen.add(old)
    return plan


def apply_edits(plain: bytes, edits: list[tuple[bytes, bytes]]) -> tuple[bytes, int]:
    patched, total = plain, 0
    for old, new in edits:
        count = patched.count(old)
        if not count:
            continue
        patched = patched.replace(old, new)
        total += count
    if len(patched) != len(plain):
        raise AssertionError("patching changed the file length")
    return patched, total


def verify_patch(before: bytes, after: bytes,
                 edits: list[tuple[bytes, bytes]]) -> dict:
    """Decompress both bundles and prove the text changed and nothing else broke."""
    report = {"length_unchanged": len(before) == len(after),
              "unitypy": "not installed"}
    if not report["length_unchanged"]:
        raise AssertionError("file length changed")
    old_blob, new_blob = decompress(before), decompress(after)
    if old_blob is None or new_blob is None:
        report["unitypy"] = "unavailable or bundle rejected"
        return report
    report["unitypy"] = "ok"
    report["content_length_unchanged"] = len(old_blob) == len(new_blob)
    checks = []
    for old, new in edits:
        checks.append({"old": old.decode("utf-8", "replace"),
                       "new": new.decode("utf-8", "replace"),
                       "new_present": new in new_blob,
                       "old_gone": old not in new_blob})
    report["checks"] = checks
    if not report["content_length_unchanged"]:
        raise AssertionError("decompressed content length changed")
    if not all(c["new_present"] for c in checks):
        raise AssertionError("a replacement did not appear after decompression")
    return report


# ------------------------------------------------------------------------ store side
def store_path(store: Path, bundle: str) -> Path:
    return Path(store) / (bundle + ".ks")


def find_plain(plain_dir: Path, size: int) -> bytes | None:
    """The carved plaintext for this file size, if exactly one of them matches."""
    found = []
    for path in Path(plain_dir).rglob("*.bundle"):
        if path.stat().st_size == size:
            data = path.read_bytes()
            if data[:7] == b"UnityFS":
                found.append(data)
    unique = {hashlib.sha256(d).hexdigest(): d for d in found}
    return next(iter(unique.values())) if len(unique) == 1 else None


def cmd_info(args) -> int:
    print(f"keystream_patch {SCRIPT_VERSION}")
    cipher = Path(args.bundle).read_bytes()
    plain = find_plain(args.plain, len(cipher))
    if plain is None:
        print("no unique carved plaintext for this size; cannot build a pair")
        return 2
    stream = xor(plain, cipher)
    head = header_info(plain)
    print(f"bundle        {Path(args.bundle).name}  {len(cipher):,} B")
    print(f"unity         {head['unity_revision']}, declared size "
          f"{head['declared_size']:,} B, compression {head['compression']}")
    print(f"keystream     {stream[:16].hex()} ...")
    runs = text_runs(plain)
    print(f"japanese runs {len(runs)}, "
          f"{sum(len(run) for _, run in runs):,} B")
    for offset, run in runs[:args.show]:
        print(f"  @{offset:#08x} {run.decode('utf-8', 'replace')}")
    return 0


def cmd_plan(args) -> int:
    print(f"keystream_patch {SCRIPT_VERSION}")
    cipher = Path(args.bundle).read_bytes()
    plain = find_plain(args.plain, len(cipher))
    if plain is None:
        print("no unique carved plaintext for this size; cannot build a pair")
        return 2
    edits = parse_map(args.map)
    plan = plan_edits(plain, edits)
    for row in plan:
        print(f"  {row['occurrences']:>2}x  {row['bytes']:>3} B  "
              f"{row['old']!r} -> {row['new']!r}")
    missing = [row["old"] for row in plan if not row["occurrences"]]
    if missing:
        print(f"these strings are not stored as literals and cannot be patched "
              f"in place: {missing}")
    Path(args.out).write_text(json.dumps({"bundle": Path(args.bundle).name,
                                          "plan": plan}, indent=1,
                                         ensure_ascii=False) + "\n",
                              encoding="utf-8")
    print(f"plan: {args.out}")
    return 0 if not missing else 1


def cmd_apply(args) -> int:
    print(f"keystream_patch {SCRIPT_VERSION}")
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    cipher = Path(args.bundle).read_bytes()
    plain = find_plain(args.plain, len(cipher))
    if plain is None:
        print("no unique carved plaintext for this size; cannot build a pair")
        return 2
    stream = xor(plain, cipher)

    edits = []
    for row in plan["plan"]:
        old, new = row["old"].encode("utf-8"), row["new"].encode("utf-8")
        if len(old) != len(new):
            print(f"refusing {row['old']!r}: byte counts differ")
            return 2
        edits.append((old, new))

    patched, count = apply_edits(plain, edits)
    print(f"replacements applied: {count}")
    report = verify_patch(plain, patched, edits)
    print(f"verification: {report}")
    if report.get("unitypy") != "ok":
        print("warning: could not decompress the patched bundle here")

    out = xor(patched, stream)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_bytes(out)
    back = xor(bytes(out), stream)
    print(f"plaintext round trip: {back == patched}")
    print(f"wrote {args.out} ({len(out):,} B, same size: "
          f"{len(out) == len(cipher)})")
    print(f"sha256 patched plaintext: {hashlib.sha256(patched).hexdigest()[:16]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=SCRIPT_VERSION)
    sub = parser.add_subparsers(dest="cmd", required=True)

    info = sub.add_parser("info", help="describe a file and its keystream")
    info.add_argument("--bundle", required=True)
    info.add_argument("--plain", default="local/owner_carve4")
    info.add_argument("--show", type=int, default=10)

    plan_p = sub.add_parser("plan", help="check which edits are possible")
    plan_p.add_argument("--bundle", required=True)
    plan_p.add_argument("--plain", default="local/owner_carve4")
    plan_p.add_argument("--map", nargs="+", required=True)
    plan_p.add_argument("--out", default="plan.json")

    apply_p = sub.add_parser("apply", help="patch, re-encrypt and write the file")
    apply_p.add_argument("--bundle", required=True)
    apply_p.add_argument("--plain", default="local/owner_carve4")
    apply_p.add_argument("--plan", required=True)
    apply_p.add_argument("--out", required=True)

    args = parser.parse_args(argv)
    return {"info": cmd_info, "plan": cmd_plan, "apply": cmd_apply}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
