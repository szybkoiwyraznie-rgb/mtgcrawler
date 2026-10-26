#!/usr/bin/env python3
"""Test every cheap way a bundle key could be built from a string.

The published `SeekableAesStream` (see `srw_y_seekable.py`) derives its AES key with
`PasswordDeriveBytes(password, salt)`. That is one hypothesis among several, and the
older hunts in this project never separated them: they fixed the counter rule and the
derivation while varying the password. When nothing matches, that experiment cannot
say *which* of the three unknowns was wrong.

This tool runs the other half of the matrix. For every candidate string it builds the
key every plausible way and, for each key, the keystream every plausible counter rule
produces, then compares all of it against a real pair:

    keys      md5(s), sha1(s)[:16], sha256(s)[:16], sha256(s), raw[:16], raw[-16:],
              raw padded with zeros to 16 / 32
    layout    AES-128/192/256-ECB over the counter block, the counter written as
              LE32/LE64/BE32 in the first bytes or as a full 128-bit value, counting
              from 0 or 1

A hit is not a guess: 32 bytes of keystream either appear or they do not.

    python key_matrix.py sweep --pairs local/pairs --plain local/owner_carve4 \\
        --literals local/literals.txt
    python key_matrix.py selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import time
from pathlib import Path

SCRIPT_VERSION = "2026-10-26.14"
ORACLE_BYTES = 32


# ------------------------------------------------------------------------ keystream
def layouts(key: bytes, length: int = ORACLE_BYTES) -> dict[str, bytes]:
    """Every counter layout this project has reason to consider."""
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)

    def build(pack, pad: int) -> bytes:
        out, index = b"", 0
        while len(out) < length:
            out += ecb.encrypt(pack(index) + b"\x00" * pad)
            index += 1
        return out[:length]

    return {
        "le32@1": build(lambda n: struct.pack("<I", n + 1), 12),
        "le32@0": build(lambda n: struct.pack("<I", n), 12),
        "le64@1": build(lambda n: struct.pack("<Q", n + 1), 8),
        "be32@1": build(lambda n: struct.pack(">I", n + 1), 12),
        "be128@1": build(lambda n: struct.pack(">QQ", 0, n + 1), 0),
        "le128@1": build(lambda n: struct.pack("<QQ", n + 1, 0), 0),
    }


def keys_from(text: bytes) -> dict[str, bytes]:
    """Every key a build script plausibly makes out of one string."""
    if not text:
        return {}
    out = {
        "md5": hashlib.md5(text).digest(),
        "sha1-16": hashlib.sha1(text).digest()[:16],
        "sha256-16": hashlib.sha256(text).digest()[:16],
        "sha256-32": hashlib.sha256(text).digest(),
    }
    if len(text) >= 16:
        out["raw16"] = text[:16]
        out["raw-last16"] = text[-16:]
    else:
        out["pad16"] = text + b"\x00" * (16 - len(text))
    if len(text) <= 32:
        out["pad32"] = text + b"\x00" * (32 - len(text))
    else:
        out["raw32"] = text[:32]
        out["raw-last32"] = text[-32:]
    return {name: key for name, key in out.items() if len(key) in (16, 24, 32)}


# ---------------------------------------------------------------------------- sweep
def sweep(needles, oracles, limit: int = 0, progress=None) -> list[dict]:
    """Compare every derived key/layout against every oracle's first 32 bytes."""
    started = time.time()
    checked = 0
    for index, text in enumerate(needles):
        if progress and index and index % 50000 == 0:
            progress(index, time.time() - started)
        for key_name, key in keys_from(text).items():
            for layout_name, stream in layouts(key).items():
                checked += 1
                for bundle, oracle in oracles:
                    if stream == oracle[:ORACLE_BYTES]:
                        return [{"needle": text.decode("latin-1"), "key": key_name,
                                 "layout": layout_name, "bundle": bundle,
                                 "key_hex": key.hex(), "checked": checked}]
        if limit and index + 1 >= limit:
            break
    if progress:
        progress(index + 1, time.time() - started)
    return []


def oracles_from_pairs(pairs, count: int) -> list[tuple[str, bytes]]:
    return [(row["name"], row["keystream"][:ORACLE_BYTES]) for row in pairs[:count]]


# ------------------------------------------------------------------------- selftest
def selftest() -> int:
    ok = True

    def check(label: str, good: bool) -> None:
        nonlocal ok
        ok &= bool(good)
        print(f"  {label:<32}{'ok' if good else 'FAILED'}")

    from Crypto.Cipher import AES

    key = hashlib.sha256(b"Com.BBStudio.SRTeam").digest()[:16]
    stream = layouts(key)["le32@1"]
    ecb = AES.new(key, AES.MODE_ECB)
    check("le32@1 is E(LE32(1)||0^12)", stream[:16] == ecb.encrypt(struct.pack("<I", 1) + b"\x00" * 12))
    check("le32@0 differs from le32@1", layouts(key)["le32@0"] != stream)
    check("be32@1 differs from le32@1", layouts(key)["be32@1"] != stream)

    keys = keys_from(b"0123456789abcdef")
    check("raw16 for a 16-char string", keys["raw16"] == b"0123456789abcdef")
    check("pad16 for a short string", keys_from(b"abc")["pad16"] == b"abc" + b"\x00" * 13)
    check("32-byte keys are kept", len(keys_from(b"a" * 30)["pad32"]) == 32)
    check("empty text makes no key", keys_from(b"") == {})

    oracle = [("fake", layouts(key)["le32@1"])]
    hit = sweep([b"nope", b"Com.BBStudio.SRTeam"], oracle)
    check("sweep finds the string", bool(hit) and hit[0]["key"] == "sha256-16"
          and hit[0]["layout"] == "le32@1")
    check("sweep rejects a wrong string", not sweep([b"nope"], oracle))
    check("a hit reports how much was checked", hit[0]["checked"] > 0)

    print("selftest: " + ("PASS" if ok else "FAILED"))
    return 0 if ok else 1


# ------------------------------------------------------------------------------- cli
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest")

    p = sub.add_parser("sweep", help="test a candidate list against real pairs")
    p.add_argument("--pairs", type=Path, required=True)
    p.add_argument("--plain", type=Path, required=True)
    p.add_argument("--literals", type=Path, required=True)
    p.add_argument("--oracles", type=int, default=2)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--out", type=Path)

    args = parser.parse_args(argv)
    if args.command == "selftest":
        return selftest()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import srw_y_seekable as seekable

    print(f"key_matrix {SCRIPT_VERSION}")
    pairs = seekable.load_pairs(args.pairs, args.plain)
    if not pairs:
        print("no pairs: nothing to test against")
        return 2
    oracles = oracles_from_pairs(pairs, args.oracles)
    print(f"pairs {len(pairs)}, oracles {len(oracles)}: "
          + ", ".join(name for name, _ in oracles))

    needles = [line.encode("utf-8", "ignore")
               for line in args.literals.read_text(errors="ignore").splitlines()]
    print(f"needles: {len(needles):,}")

    def progress(done, seconds):
        print(f"  {done:,} in {seconds:.0f}s", flush=True)

    hits = sweep(needles, oracles, limit=args.limit, progress=progress)
    if args.out:
        args.out.write_text(json.dumps(hits, indent=1))
    if hits:
        print("HIT " + json.dumps(hits[0]))
        return 0
    print("no hit")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
