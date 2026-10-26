#!/usr/bin/env python3
"""Try password+salt derivations for the `SeekableAesStream` protection.

The metadata of SRW Y names the mechanism precisely:

* `Assets/Scripts/Addressable/SeekableAesStreamcs.cs` — a custom seekable AES
  stream with fields ``password``, ``salt``, ``buffer``, ``streamPos``, ``aes``,
  ``encryptor`` and a ``Cipher`` property;
* `Com.BBStudio.SRTeam.Encryption|EnctyptionInfo` with ``KeySize``, ``BlockSize``,
  ``Mode``, ``IV`` and ``Padding``.

So the key is not a plain constant: it is derived from a password and a salt.
The obvious derivation in .NET is `Rfc2898DeriveBytes` (PBKDF2-HMAC-SHA1) — the
class name is present in the metadata too. This tool therefore does what
`keyhunt.py` does not: it takes **password × salt × iteration × digest × counter
layout** and looks for `UnityFS`.

Search space is deliberately small and explicit: the caller supplies the
passwords and salts (from a word list or from the game's own strings). This is a
guessing tool, not a cracker — it cannot invent the password.

Usage:
    python3 tools/kdf_hunt.py --bundle x.bundle \
        --passwords words.txt --salts words.txt --iterations 1 1000 10000
    python3 tools/kdf_hunt.py --bundle x.bundle --strings global-metadata.dat \
        --max-strings 5000

Exit codes: 0 always, 2 on bad input.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keyhunt as K  # noqa: E402

SCHEMA = 1
DIGESTS = ("sha1", "sha256", "md5")
PRINTABLE_RUN = re.compile(rb"[\x20-\x7e]{4,64}")


def derive(password: bytes, salt: bytes, iterations: int, digest: str, size: int) -> bytes:
    """PBKDF2 with the given digest; `hashlib.pbkdf2_hmac` handles all of them."""
    return hashlib.pbkdf2_hmac(digest, password, salt, iterations, dklen=size)


def variants_for(key: bytes, data: bytes) -> list[str]:
    """Scheme names under which `key` turns `data` into a UnityFS header."""
    found = list(K.matches(key, data))
    # seekable AES often starts the counter at the block index of the file offset
    # and little-endian; K.matches already covers the common layouts, this adds
    # the "IV = first key bytes" and "counter as two 64-bit halves" cases.
    for name, plain in {
        "aes-ctr-le64": K._xor(K.encrypt(key, keyhash_counter(0, "little")), data[:16]),
        "aes-ctr-be64": K._xor(K.encrypt(key, keyhash_counter(0, "big")), data[:16]),
    }.items():
        if plain.startswith(b"UnityFS"):
            found.append(name)
    return found


def keyhash_counter(value: int, endian: str) -> bytes:
    return value.to_bytes(8, endian) * 2


def hunt(passwords: list[bytes], salts: list[bytes], iterations: list[int],
         digests: list[str], sizes: list[int], samples: list[tuple[str, bytes]],
         verbose: bool = False) -> dict:
    tried = 0
    found = []
    for password, salt, iteration, digest, size in itertools.product(
            passwords, salts, iterations, digests, sizes):
        key = derive(password, salt, iteration, digest, size)
        tried += 1
        if verbose and tried % 200 == 0:
            print(f"  {tried:,} derivations", file=sys.stderr)
        for name, data in samples:
            schemes = variants_for(key, data)
            if schemes:
                found.append({
                    "password": password.decode("utf-8", "replace"),
                    "salt": salt.decode("utf-8", "replace"),
                    "iterations": iteration,
                    "digest": digest,
                    "key_size": size,
                    "key_hex": key.hex(),
                    "bundle": name,
                    "schemes": schemes,
                })
                return {"schema": SCHEMA, "tried": tried, "found": found}
    return {"schema": SCHEMA, "tried": tried, "found": found}


def words_from_file(path: Path) -> list[bytes]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        word = line.strip()
        if word:
            out.append(word.encode("utf-8", "ignore"))
    return out


def words_from_blob(path: Path, limit: int) -> list[bytes]:
    """Unique printable runs — a game's own vocabulary is the best word list."""
    blob = path.read_bytes()
    seen: dict[bytes, None] = {}
    for match in PRINTABLE_RUN.finditer(blob):
        run = match.group()
        if run not in seen:
            seen[run] = None
            if len(seen) >= limit:
                break
    return list(seen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bundle", required=True, nargs="+", type=Path)
    parser.add_argument("--passwords", type=Path)
    parser.add_argument("--salts", type=Path)
    parser.add_argument("--strings", type=Path,
                        help="blob to mine for both passwords and salts")
    parser.add_argument("--max-strings", type=int, default=2000)
    parser.add_argument("--iterations", type=int, nargs="+", default=[1, 1000])
    parser.add_argument("--digests", nargs="+", default=list(DIGESTS))
    parser.add_argument("--sizes", type=int, nargs="+", default=[16, 32])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    passwords: list[bytes] = []
    salts: list[bytes] = []
    if args.passwords:
        passwords += words_from_file(args.passwords)
    if args.salts:
        salts += words_from_file(args.salts)
    if args.strings:
        if not args.strings.is_file():
            print(f"error: not a file: {args.strings}", file=sys.stderr)
            return 2
        mined = words_from_blob(args.strings, args.max_strings)
        if not passwords:
            passwords = list(mined)
        if not salts:
            salts = list(mined)
    if not passwords or not salts:
        print("error: give --passwords/--salts or --strings", file=sys.stderr)
        return 2

    samples = []
    for bundle in args.bundle:
        if not bundle.is_file():
            print(f"error: not a file: {bundle}", file=sys.stderr)
            return 2
        samples.append((bundle.name, bundle.read_bytes()[:512]))

    total = (len(passwords) * len(salts) * len(args.iterations)
             * len(args.digests) * len(args.sizes))
    print(f"passwords {len(passwords):,} x salts {len(salts):,} x iterations "
          f"{args.iterations} x digests {args.digests} x sizes {args.sizes} "
          f"= {total:,} derivations")
    result = hunt(passwords, salts, args.iterations, args.digests, args.sizes,
                  samples, args.verbose)
    print(f"tried {result['tried']:,}")
    if result["found"]:
        for hit in result["found"]:
            print(f"MATCH password={hit['password']!r} salt={hit['salt']!r} "
                  f"iter={hit['iterations']} digest={hit['digest']} "
                  f"size={hit['key_size']} schemes={hit['schemes']}")
    else:
        print("no match")
    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(f"report written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
