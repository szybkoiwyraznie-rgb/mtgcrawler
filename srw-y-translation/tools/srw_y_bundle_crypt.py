#!/usr/bin/env python3
"""The SRW Y bundle cipher, recovered: password, salt, keystream, round trip.

This closes S3. The `.bundle` files in `StreamingAssets/aa/StandaloneWindows64` are
encrypted with the `SeekableAesStream` class the Unity community publishes, and the
game's own copy of it is `SeekableAesStream` in `Assembly-CSharp` (14 methods,
`.ctor` at RVA `0x429cf0`, `Cipher` at `0x429840`) - the class the metadata has been
showing since S2.

How the password was found (see `docs/S3_KEY_FOUND.md`): the pair data proved the
construction and the salt but refused every printable string, and the remaining
doubt was whether the password was a *string literal* at all. Reading
`CustomAssetBundleResource::LoadLocalBundle` (RVA `0xbce440`) in `GameAssembly.dll`
showed the call

    SeekableAesStream..ctor(fileStream, password, Encoding.UTF8.GetBytes(filePath))

with the password taken from one fixed slot, and a sweep of the 13,428 exact
`Il2CppStringLiteral` records - not the printable runs between them - produced

    password = "ComBBStudioSRTeam"
    salt     = the bundle's file name without ".bundle"
    key      = new PasswordDeriveBytes(password, salt).GetBytes(16)   # PBKDF1-SHA1, 100
    aes      = AES-128, ECB, no padding
    keystream[16n .. 16n+16) = AES_ECB(key, LE32(n) || 0^12), n from 1
    plain = cipher XOR keystream        (same length, no padding, no header skip)

All 276 known pairs agree on their first 32 KiB - which is all the memory carve ever
held, see `verify`.

    python srw_y_bundle_crypt.py selftest
    python srw_y_bundle_crypt.py verify --pairs local/pairs --plain local/owner_carve4
    python srw_y_bundle_crypt.py decrypt NAME.bundle out.bundle --pairs local/pairs
    python srw_y_bundle_crypt.py encrypt NAME.bundle out.bundle
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

SCRIPT_VERSION = "2026-10-27.1"
PASSWORD = b"ComBBStudioSRTeam"
SALT_SUFFIX = ".bundle"
ITERATIONS = 100
KEY_BYTES = 16
BLOCK = 16
# The memory carver kept 32 KiB per bundle and zero-filled the rest, so that is the
# only part of a carved bundle that can be compared against anything.
CARVE_LIMIT = 32768


# ------------------------------------------------------------------------ derivation
def salt_for(name: str) -> bytes:
    """`Path.GetFileName(path)` as UTF-8: the file name without the `.bundle` tail.

    The executable concatenates the bundle directory with the location's internal id
    and hands the result to `Path.GetFileName`, then `Encoding.UTF8.GetBytes`, so the
    salt is exactly the name on disk minus the extension. A name without `.bundle` is
    used unchanged.
    """
    stem = name[:-len(SALT_SUFFIX)] if name.endswith(SALT_SUFFIX) else name
    return stem.encode("utf-8")


def key_for(name: str, password: bytes = PASSWORD, iterations: int = ITERATIONS) -> bytes:
    """`PasswordDeriveBytes(password, salt).GetBytes(16)`: PBKDF1 over SHA-1."""
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    digest = hashlib.sha1(password + salt_for(name)).digest()
    for _ in range(iterations - 1):
        digest = hashlib.sha1(digest).digest()
    return digest[:KEY_BYTES]


# ------------------------------------------------------------------------- keystream
def nonce(index: int) -> bytes:
    """`BitConverter.GetBytes(blockNumber)` in a zeroed block, so LE32 first."""
    return struct.pack("<i", index) + b"\x00" * (BLOCK - 4)


def keystream(key: bytes, length: int) -> bytes:
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    out = bytearray()
    index = 1
    while len(out) < length:
        out += ecb.encrypt(nonce(index))
        index += 1
    return bytes(out[:length])


def xor_stream(data: bytes, key: bytes) -> bytes:
    stream = keystream(key, len(data))
    return bytes(a ^ b for a, b in zip(data, stream))


def decrypt(name: str, data: bytes) -> bytes:
    return xor_stream(data, key_for(name))


def encrypt(name: str, data: bytes) -> bytes:
    return xor_stream(data, key_for(name))


# ---------------------------------------------------------------------------- verify
def verify(pairs_dir: Path, plain_dir: Path, limit: int = 0) -> dict:
    """Every pair must come back: the ciphertext decrypts to the carved plaintext.

    The carve holds only the first 32 KiB of each bundle (the carver stopped there),
    so "matches" means the decrypted head equals the carved head byte for byte; the
    rest of the file cannot be checked against anything we have, which is why the
    key was accepted only after all 276 heads agreed.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import srw_y_seekable as seekable

    rows = seekable.load_pairs(pairs_dir, plain_dir)
    # Unique bundle size -> its single distinct plaintext, the same rule load_pairs
    # uses; a size shared by two different carves cannot be paired at all.
    by_size: dict[int, dict[str, Path]] = {}
    for path in Path(plain_dir).rglob("*.bundle"):
        data = path.read_bytes()
        if data[:7] != b"UnityFS":        # a carve that is not a bundle is noise
            continue
        by_size.setdefault(len(data), {})[hashlib.sha256(data).hexdigest()] = path

    checked, head_ok, oracle_ok, failures = 0, 0, 0, []
    for row in (rows[:limit] if limit else rows):
        name = row["name"]
        data = (pairs_dir / name).read_bytes()
        plain = decrypt(name, data)
        checked += 1
        oracle_ok += bytes(a ^ b for a, b in zip(data[:32], plain[:32])) == row["keystream"][:32]
        carved = by_size.get(len(data)) or {}
        if len(carved) == 1:
            head = next(iter(carved.values())).read_bytes()[:CARVE_LIMIT]
            if plain[:len(head)] == head:
                head_ok += 1
            else:
                failures.append(name)
    return {"pairs": checked, "oracle_matches": oracle_ok,
            "carve_head_matches": head_ok, "failures": failures[:10]}


# ------------------------------------------------------------------------- selftest
def selftest() -> int:
    ok = True

    def check(label: str, good: bool) -> None:
        nonlocal ok
        ok &= bool(good)
        print(f"  {label:<40}{'ok' if good else 'FAILED'}")

    check("salt drops the extension", salt_for("aa/bb.bundle") == b"aa/bb")
    check("salt of a bare name", salt_for("abcd") == b"abcd")
    key = key_for("1cc7e02ee5711c6ba87a0e364f62198c.bundle")
    check("key is 16 bytes", len(key) == 16)
    check("key is PBKDF1-SHA1 x100",
          key == _pbkdf1(b"ComBBStudioSRTeam",
                         b"1cc7e02ee5711c6ba87a0e364f62198c", 100)[:16])
    check("two files get different keys",
          key_for("a.bundle") != key_for("b.bundle"))
    check("iteration count matters", key_for("a.bundle", iterations=1) != key_for("a.bundle"))

    payload = b"UnityFS\x00" + bytes(range(256)) * 3
    name = "e7be81fb466fc8979ee233d1c1a2558c.bundle"
    blob = encrypt(name, payload)
    check("ciphertext differs from plain", blob != payload)
    check("round trip", decrypt(name, blob) == payload)
    check("round trip is length preserving", len(blob) == len(payload))
    check("same input encrypts to the same bytes", encrypt(name, payload) == blob)
    # the ciphertext starts with the bundle header, so compare the stream itself
    check("first stream block is E(LE32(1))",
          keystream(key_for(name), 16) == _aes(key_for(name), nonce(1)))
    check("second stream block is E(LE32(2))",
          keystream(key_for(name), 32)[16:] == _aes(key_for(name), nonce(2)))
    check("wrong file name does not decrypt",
          decrypt("00000000000000000000000000000000.bundle", blob) != payload)

    print("selftest: " + ("PASS" if ok else "FAILED"))
    return 0 if ok else 1


def _pbkdf1(password: bytes, salt: bytes, iterations: int) -> bytes:
    digest = hashlib.sha1(password + salt).digest()
    for _ in range(iterations - 1):
        digest = hashlib.sha1(digest).digest()
    return digest


def _aes(key: bytes, block: bytes) -> bytes:
    from Crypto.Cipher import AES

    return AES.new(key, AES.MODE_ECB).encrypt(block)


def _first_block(key: bytes) -> bytes:
    return _aes(key, nonce(1))


# ------------------------------------------------------------------------------ cli
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest")

    v = sub.add_parser("verify", help="check the recovered key against every pair")
    v.add_argument("--pairs", type=Path, required=True)
    v.add_argument("--plain", type=Path, required=True)
    v.add_argument("--limit", type=int, default=0)
    v.add_argument("--out", type=Path)

    for command in ("decrypt", "encrypt"):
        d = sub.add_parser(command, help=f"{command} one bundle")
        d.add_argument("name", help="the bundle's file name (it is the salt)")
        d.add_argument("output", type=Path)
        d.add_argument("--input", type=Path, help="default: the bundle in the pairs store")
        d.add_argument("--pairs", type=Path, default=Path("local/pairs"))

    args = parser.parse_args(argv)
    if args.command == "selftest":
        return selftest()

    if args.command == "verify":
        report = verify(args.pairs, args.plain, args.limit)
        print(f"key: {PASSWORD.decode()}  iterations {ITERATIONS}  salt: file name")
        print(f"pairs checked        : {report['pairs']}")
        print(f"32-byte oracle       : {report['oracle_matches']}/{report['pairs']}")
        print(f"carved head matches  : {report['carve_head_matches']}/{report['pairs']}")
        if report["failures"]:
            print("failures             : " + ", ".join(report["failures"]))
        if args.out:
            args.out.write_text(json.dumps(report, indent=1))
        ok = (report["oracle_matches"] == report["pairs"]
              and report["carve_head_matches"] == report["pairs"])
        return 0 if ok else 1

    name = Path(args.name).name
    source = args.input or (args.pairs / name)
    if not source.exists():
        print(f"missing input: {source}")
        return 2
    data = source.read_bytes()
    result = decrypt(name, data) if args.command == "decrypt" else encrypt(name, data)
    args.output.write_bytes(result)
    print(f"{args.command}: {source} -> {args.output}  {len(result):,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
