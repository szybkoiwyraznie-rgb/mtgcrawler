#!/usr/bin/env python3
"""Work with a (plaintext, ciphertext) pair of the same bundle - no key needed.

The memory carve holds decrypted bundles (`UnityFS` at offset 0); the same
bundle on disk is the encrypted file with the **same length**, and for 276 sizes
exactly one file on disk has that length. For such a pair

    keystream = ciphertext XOR plaintext

and, because every construction tested so far (CTR/OFB/CFB/CBC/ECB) is a stream
over the file, that keystream depends only on the key and the per-file state -
not on the bytes of the bundle. So:

    patched = (new bundle, zero-padded to the original size) XOR keystream

is a drop-in replacement the game decrypts correctly, without recovering the key.
The only rule is that the rebuilt bundle must not grow past the original file
size (Japanese is 3 bytes per character in UTF-8, Polish about 1.1, so a
translation normally shrinks).

    python pair_keystream.py info    plain.bundle cipher.bundle
    python pair_keystream.py save    plain.bundle cipher.bundle --out pair.ks
    python pair_keystream.py check   plain.bundle cipher.bundle --ks pair.ks
    python pair_keystream.py encrypt new.bundle --ks pair.ks --out patched.bundle
    python pair_keystream.py survey  pairs/ --out survey.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_VERSION = "2026-10-26.8"
MAGIC = b"SRWKS1\n"


def xor(data: bytes, stream: bytes) -> bytes:
    if len(data) > len(stream):
        raise ValueError(
            f"data is {len(data)} B but the keystream is only {len(stream)} B; "
            f"a patched bundle must not grow past the original file")
    return bytes(a ^ b for a, b in zip(data, stream))


def keystream(plain: bytes, cipher: bytes) -> bytes:
    if len(plain) != len(cipher):
        raise ValueError(f"lengths differ: plaintext {len(plain)} B, "
                         f"ciphertext {len(cipher)} B")
    return xor(plain, cipher)


def plain_header_ok(plain: bytes) -> bool:
    """A carved bundle must start with UnityFS and declare its own size."""
    if plain[:7] != b"UnityFS":
        return False
    if len(plain) < 38:
        return False
    # size is a big-endian u64 right after "UnityFS\0", version, "5.x.x", "2022.3.44f1"
    return int.from_bytes(plain[30:38], "big") == len(plain)


def load_pair(plain_path: Path, cipher_path: Path) -> tuple[bytes, bytes]:
    plain = Path(plain_path).read_bytes()
    cipher = Path(cipher_path).read_bytes()
    if len(plain) != len(cipher):
        raise ValueError(f"not a pair: {plain_path} is {len(plain)} B, "
                         f"{cipher_path} is {len(cipher)} B")
    return plain, cipher


def save_stream(path: Path, stream: bytes) -> None:
    Path(path).write_bytes(MAGIC + stream)


def load_stream(path: Path) -> bytes:
    data = Path(path).read_bytes()
    if not data.startswith(MAGIC):
        raise ValueError("not a saved keystream")
    return data[len(MAGIC):]


def survey(folder: Path) -> dict:
    """Do different bundles share a keystream? That would mean a shared state."""
    pairs = sorted(folder.glob("*.ks"))
    seen: dict[str, list[str]] = {}
    rows = []
    for path in pairs:
        stream = load_stream(path)
        head = stream[:32].hex()
        rows.append({"keystream": str(path), "bytes": len(stream),
                     "head": head})
        seen.setdefault(head, []).append(path.stem)
    shared = {head: names for head, names in seen.items() if len(names) > 1}
    return {"script_version": SCRIPT_VERSION, "pairs": rows,
            "distinct_keystream_heads": len(seen), "shared_heads": shared}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    info = sub.add_parser("info", help="describe a pair and its keystream")
    info.add_argument("plain", type=Path)
    info.add_argument("cipher", type=Path)

    save = sub.add_parser("save", help="write the keystream to a .ks file")
    save.add_argument("plain", type=Path)
    save.add_argument("cipher", type=Path)
    save.add_argument("--out", type=Path, required=True)

    check = sub.add_parser("check", help="re-encrypt the plaintext and compare")
    check.add_argument("plain", type=Path)
    check.add_argument("cipher", type=Path)
    check.add_argument("--ks", type=Path, required=True)

    enc = sub.add_parser("encrypt", help="encrypt a rebuilt bundle with a keystream")
    enc.add_argument("bundle", type=Path)
    enc.add_argument("--ks", type=Path, required=True)
    enc.add_argument("--out", type=Path, required=True)
    enc.add_argument("--pad", type=lambda v: int(v, 0), default=0,
                     help="pad the bundle to this size before encrypting")

    srv = sub.add_parser("survey", help="compare saved keystreams")
    srv.add_argument("folder", type=Path)
    srv.add_argument("--out", type=Path, default=Path("survey.json"))

    args = parser.parse_args(argv)
    print(f"pair_keystream {SCRIPT_VERSION}")

    if args.cmd == "info":
        plain, cipher = load_pair(args.plain, args.cipher)
        stream = keystream(plain, cipher)
        zeros = sum(1 for byte in stream if byte == 0)
        print(f"size          {len(plain):,} B (both files agree)")
        print(f"plain header  {'ok, UnityFS' if plain_header_ok(plain) else 'NOT a bundle'}")
        print(f"cipher header {cipher[:8].hex()}")
        print(f"keystream     {stream[:32].hex()} ...")
        print(f"zero bytes    {zeros} ({100 * zeros / len(stream):.1f}%)")
        return 0 if plain_header_ok(plain) else 1

    if args.cmd == "save":
        plain, cipher = load_pair(args.plain, args.cipher)
        stream = keystream(plain, cipher)
        save_stream(args.out, stream)
        print(f"saved {len(stream):,} B keystream to {args.out}")
        return 0

    if args.cmd == "check":
        plain, cipher = load_pair(args.plain, args.cipher)
        stream = load_stream(args.ks)
        if len(stream) != len(plain):
            print(f"length mismatch: keystream {len(stream)} B, files {len(plain)} B")
            return 1
        again = xor(plain, stream)
        ok = again == cipher
        print("round trip    " + ("ok, byte-exact" if ok else "MISMATCH"))
        return 0 if ok else 1

    if args.cmd == "encrypt":
        stream = load_stream(args.ks)
        bundle = args.bundle.read_bytes()
        if args.pad:
            if args.pad < len(bundle):
                print(f"bundle is {len(bundle)} B, pad target {args.pad} B is smaller")
                return 1
            bundle = bundle + b"\x00" * (args.pad - len(bundle))
        elif len(bundle) < len(stream):
            bundle = bundle + b"\x00" * (len(stream) - len(bundle))
        try:
            patched = xor(bundle, stream)
        except ValueError as error:
            print(error)
            return 1
        args.out.write_bytes(patched)
        print(f"wrote {len(patched):,} B to {args.out}")
        return 0

    report = survey(args.folder)
    args.out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"{len(report['pairs'])} keystreams, "
          f"{report['distinct_keystream_heads']} distinct heads, "
          f"{len(report['shared_heads'])} shared")
    print(f"report: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
