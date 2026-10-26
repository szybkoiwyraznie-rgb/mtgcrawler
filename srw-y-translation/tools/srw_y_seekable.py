#!/usr/bin/env python3
"""The game's exact stream construction, and the key hunt for it.

The published Unity `SeekableAesStream` (the class the Unity Addressables variant
ships, and the snippet the Japanese and Chinese Unity communities repost under that
name) does this:

    key  = new PasswordDeriveBytes(password, salt).GetBytes(16)   // AES-128
    aes  = AesManaged { Mode = ECB, Padding = None, IV = zeros }
    for block n = 1, 2, 3, ...:
        nonce = BitConverter.GetBytes(n) padded with zeros to 16 bytes
        keystream_block_n = aes.Encrypt(nonce)

so the keystream is `AES-ECB(key, LE32(n) || 0^12)` with the counter in the **first**
four bytes, starting at 1 - not the "state + i" form that every earlier attempt
assumed, and with no IV at all. The salt is normally the bundle's own name
(`Encoding.UTF8.GetBytes(name)`), which is why every file has a different keystream
while the password stays the same.

`PasswordDeriveBytes` is the old .NET class, not Rfc2898: it is PBKDF1 with SHA-1 -
`h = SHA1(password || salt)`, then `h = SHA1(h)` for the remaining iterations, default
100.

This module implements both, and a sweep that tests candidate passwords against a
known pair: for a candidate password and the bundle's name, the keystream follows, so
two AES calls decide it. Nothing about the candidate can be right by accident.

    python srw_y_seekable.py selftest
    python srw_y_seekable.py sweep --pairs local/pairs --plain local/owner_carve4 \
        --literals literals.txt --out seekable_hit.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import time
from pathlib import Path

SCRIPT_VERSION = "2026-10-26.13"
BLOCK = 16
SWEEP_ITERATIONS = (100, 1, 1000)


# ------------------------------------------------------------------- key derivation
def password_derive_bytes(password: bytes, salt: bytes, count: int = 16,
                          iterations: int = 100) -> bytes:
    """.NET `PasswordDeriveBytes`: PBKDF1 over SHA-1 (first hash block).

    For the 16 bytes this game needs, the derivation is the classic PBKDF1:
    `h = SHA1(password || salt)`, then `iterations - 1` further SHA-1 rounds.
    """
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    digest = hashlib.sha1(password + salt).digest()
    for _ in range(iterations - 1):
        digest = hashlib.sha1(digest).digest()
    return digest[:count]


def rfc2898_bytes(password: bytes, salt: bytes, count: int = 16,
                  iterations: int = 1000) -> bytes:
    """`Rfc2898DeriveBytes` (PBKDF2-SHA1), in case the game used the newer class."""
    return hashlib.pbkdf2_hmac("sha1", password, salt, iterations, count)


# ----------------------------------------------------------------------- keystream
def counter_nonce(index: int) -> bytes:
    """`BitConverter.GetBytes(blockNumber)` in a zeroed 16-byte buffer."""
    return struct.pack("<i", index) + b"\x00" * (BLOCK - 4)


def keystream(key: bytes, length: int, start: int = 1) -> bytes:
    """The bytes the stream XORs into the file, from `start` blocks in."""
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    out = bytearray()
    index = start
    while len(out) < length:
        out += ecb.encrypt(counter_nonce(index))
        index += 1
    return bytes(out[:length])


def decrypt(key: bytes, data: bytes) -> bytes:
    stream = keystream(key, len(data))
    return bytes(a ^ b for a, b in zip(data, stream))


def encrypt(key: bytes, data: bytes) -> bytes:
    return decrypt(key, data)           # XOR with the same stream


# --------------------------------------------------------------------------- checks
def name_salts(name: str, size: int = 0) -> list[tuple[str, bytes]]:
    """Every per-file value the reader could use as the salt.

    The salt has to differ per file (the 276 keystreams are all different), and these
    are the only per-file things a reader has before it reads a byte.
    """
    stem = name[:-7] if name.endswith(".bundle") else name
    out = [("name", name.encode()), ("stem", stem.encode()),
           ("name-lower", name.lower().encode()),
           ("stem-lower", stem.lower().encode())]
    try:
        raw = bytes.fromhex(stem)
        out.append(("stem-hex", raw))
    except ValueError:
        pass
    if size:
        out.append(("size-ascii", str(size).encode()))
        out.append(("size-hex", f"{size:x}".encode()))
    out += [("md5(name)", hashlib.md5(name.encode()).digest()),
            ("sha1(name)", hashlib.sha1(name.encode()).digest()),
            ("sha256(name)", hashlib.sha256(name.encode()).digest())]
    return out


def matches(key: bytes, keystream_known: bytes) -> bool:
    """Two blocks of AES: a wrong key cannot pass 32 bytes."""
    if len(keystream_known) < 32:
        return False
    return keystream(key, 32) == keystream_known[:32]


def verify(key: bytes, pairs) -> list[dict]:
    opened = []
    for row in pairs:
        if matches(key, row["keystream"]):
            opened.append({"bundle": row["name"], "mode": "seekable-aes-ecb-ctr"})
    return opened


# ---------------------------------------------------------------------------- sweep
def sweep(passwords, pairs, iterations_list=SWEEP_ITERATIONS,
          derive="password", progress=None) -> list[dict]:
    """Test each password against the first pair, with every name-based salt."""
    first = pairs[0]
    salts = name_salts(first["name"], first.get("size", 0))
    started = time.time()
    for index, password in enumerate(passwords):
        if progress and index and index % 5000 == 0:
            progress(index, time.time() - started)
        for salt_label, salt in salts:
            for iterations in iterations_list:
                if derive == "password":
                    key = password_derive_bytes(password, salt, 16, iterations)
                else:
                    key = rfc2898_bytes(password, salt, 16, iterations)
                if matches(key, first["keystream"]):
                    return [{"password": password.decode("latin-1"),
                             "salt": salt_label, "iterations": iterations,
                             "derive": derive, "key_hex": key.hex(),
                             "verified": verify(key, pairs)}]
    return []


# ------------------------------------------------------------------------- selftest
def selftest() -> int:
    ok = True

    def check(label: str, good: bool) -> None:
        nonlocal ok
        ok &= bool(good)
        print(f"  {label:<26}{'ok' if good else 'FAILED'}")

    # PBKDF1 reference: SHA1("password" + "salt") for one iteration
    digest = hashlib.sha1(b"password" + b"salt").digest()
    check("pdb one iteration", password_derive_bytes(b"password", b"salt", 16, 1)
          == digest[:16])
    check("pdb 100 iterations",
          password_derive_bytes(b"password", b"salt", 16, 100)
          == _pbkdf1(b"password", b"salt", 100)[:16])

    nonce = counter_nonce(1)
    check("counter is LE32 at offset 0",
          nonce == b"\x01\x00\x00\x00" + b"\x00" * 12)

    key = bytes(range(16))
    stream = keystream(key, 48)
    check("keystream length", len(stream) == 48)
    check("first block is E(LE32(1))", stream[:16]
          == _aes_block(key, counter_nonce(1)))
    check("second block is E(LE32(2))", stream[16:32]
          == _aes_block(key, counter_nonce(2)))

    payload = b"UnityFS\x00" + bytes(range(64))
    check("round trip", decrypt(key, encrypt(key, payload)) == payload)
    check("detects its own key", matches(key, stream))
    check("rejects a wrong key", not matches(bytes(16), stream))

    salts = name_salts("1cc7e02ee5711c6ba87a0e364f62198c.bundle")
    labels = [label for label, _ in salts]
    check("name salts", "name" in labels and "stem-hex" in labels)
    check("stem-hex is 16 bytes",
          dict(salts)["stem-hex"] == bytes.fromhex("1cc7e02ee5711c6ba87a0e364f62198c"))

    print(f"selftest: {'PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


def _pbkdf1(password: bytes, salt: bytes, iterations: int) -> bytes:
    """Straight PBKDF1 reference, written separately on purpose."""
    value = hashlib.sha1(password + salt).digest()
    for _ in range(iterations - 1):
        value = hashlib.sha1(value).digest()
    return value


def _aes_block(key: bytes, block: bytes) -> bytes:
    from Crypto.Cipher import AES

    return AES.new(key, AES.MODE_ECB).encrypt(block)


# ------------------------------------------------------------------------------ cli
def load_pairs(pairs_dir: Path, plain_dir: Path) -> list[dict]:
    plain_by_size: dict[int, dict[str, bytes]] = {}
    for path in Path(plain_dir).rglob("*.bundle"):
        data = path.read_bytes()
        if data[:7] == b"UnityFS":
            plain_by_size.setdefault(len(data), {})[
                hashlib.sha256(data).hexdigest()] = data
    out = []
    for path in sorted(Path(pairs_dir).glob("*.bundle")):
        cipher = path.read_bytes()
        plains = plain_by_size.get(len(cipher)) or {}
        if len(plains) != 1:
            continue
        plain = next(iter(plains.values()))[:48]
        cipher_head = cipher[:48]
        out.append({"name": path.name, "size": len(cipher),
                    "keystream": bytes(a ^ b for a, b in zip(plain, cipher_head))})
    return out


def cmd_sweep(args) -> int:
    print(f"srw_y_seekable {SCRIPT_VERSION}")
    pairs = load_pairs(Path(args.pairs), Path(args.plain))
    print(f"pairs: {len(pairs)}")
    if not pairs:
        return 2
    passwords = [line.encode("utf-8", "ignore") for line in
                 Path(args.literals).read_text(encoding="utf-8",
                                               errors="ignore").splitlines() if line]
    if args.max_literals:
        passwords = passwords[:args.max_literals]
    passwords = [p for p in passwords if len(p) >= 1]
    print(f"passwords: {len(passwords):,}")

    started = time.time()
    for derive in args.derive:
        hits = sweep(passwords, pairs, args.iterations, derive,
                     progress=lambda i, dt: print(f"  {i:,} passwords, {dt:.0f}s",
                                                  flush=True))
        print(f"{derive}: {'HIT' if hits else 'no hit'} "
              f"({time.time() - started:.0f}s)")
        if hits:
            for hit in hits:
                print(json.dumps(hit, indent=1))
            Path(args.out).write_text(json.dumps(hits, indent=1) + "\n",
                                      encoding="utf-8")
            return 0
    Path(args.out).write_text("[]\n", encoding="utf-8")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=SCRIPT_VERSION)
    parser.add_argument("command", nargs="?", default="selftest",
                        choices=["selftest", "sweep", "stream"])
    parser.add_argument("--pairs", default="local/pairs")
    parser.add_argument("--plain", default="local/owner_carve4")
    parser.add_argument("--literals", default="literals.txt")
    parser.add_argument("--max-literals", type=int, default=0)
    parser.add_argument("--iterations", type=int, nargs="+",
                        default=list(SWEEP_ITERATIONS))
    parser.add_argument("--derive", nargs="+", default=["password", "rfc2898"])
    parser.add_argument("--out", default="seekable_hit.json")
    parser.add_argument("--key", help="with `stream`: hex key")
    parser.add_argument("--salt", help="with `stream`: bundle name, as the salt")
    parser.add_argument("--password", help="with `stream`: password")
    args = parser.parse_args(argv)

    if args.command == "selftest":
        return selftest()
    if args.command == "stream":
        key = bytes.fromhex(args.key) if args.key else password_derive_bytes(
            args.password.encode(), args.salt.encode(), 16, 100)
        print(f"srw_y_seekable {SCRIPT_VERSION}")
        print(f"key {key.hex()}  keystream {keystream(key, 32)[:16].hex()} ...")
        return 0
    return cmd_sweep(args)


if __name__ == "__main__":
    sys.exit(main())
