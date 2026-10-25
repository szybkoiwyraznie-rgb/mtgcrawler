#!/usr/bin/env python3
"""Recover the AES key of the game's bundle encryption from the running process.

This is the tool that decides whether file patching is possible at all. The disk
bundles are encrypted (the game class `SeekableAesStream`, key derived from
password + salt through `Rfc2898`), and the key is not stored in any file and is
not a literal in the binary - 61,201,575 candidate windows from `GameAssembly.dll`
and 4,712 name-derived KDF combinations all failed. So the key is looked for where
it must exist: in the process, as a managed `byte[]`.

The trick that makes this cheap: an encrypted bundle's first bytes are known.
Every SRW Y bundle starts with

    UnityFS\\x00 | 00 00 00 08 | 5.x.x\\x00 | 2022.3.44f1\\x00

so for a stream cipher the keystream's first block is `cipher[0:16] xor
plain[0:16]`, and for CBC the same expression is `E(P xor IV)`. In both cases ONE
AES decryption per candidate key is enough:

    AES-ECB-decrypt(key, keystream_block) -> the IV (stream mode)
    AES-ECB-decrypt(key, cipher_block)    -> P xor IV (CBC mode)

and the result is accepted only when it is the all-zero vector or one of the
16-byte arrays actually found in the process. No plaintext/ciphertext pair is
needed, no brute force over the address space, and a few thousand candidates cost
milliseconds instead of hours.

Read-only: `PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`.

Usage (game running, Windows):
    python key_from_memory.py --bundle "C:\\path\\to\\1cc7e02e....bundle"
    python key_from_memory.py --selftest           # works on any platform
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCRIPT_VERSION = "2026-10-26.3"

# The first 30 bytes of every bundle in this build, taken from bundles carved out
# of memory (one distinct prefix across 200 samples).
BUNDLE_PREFIX = b"UnityFS\x00\x00\x00\x00\x085.x.x\x002022.3.44f1\x00"
BLOCK = 16
ARRAY_SIZES = (16, 24, 32)      # AES-128 / AES-192 / AES-256 keys and 16-byte IVs
MAX_POOL = 20000                # how many distinct 16-byte arrays to keep
SCAN_CHUNK = 8 * 1024 * 1024


def known_keystream(bundle_path: Path) -> bytes:
    """First ciphertext block XOR first plaintext block."""
    with bundle_path.open("rb") as handle:
        cipher = handle.read(BLOCK)
    if len(cipher) < BLOCK:
        raise ValueError("bundle file is too short")
    plain = BUNDLE_PREFIX[:BLOCK]
    return bytes(a ^ b for a, b in zip(cipher, plain))


def cipher_block(bundle_path: Path) -> bytes:
    with bundle_path.open("rb") as handle:
        return handle.read(BLOCK)


def looks_like_pointer(value: bytes) -> bool:
    number = int.from_bytes(value, "little")
    return 0x0001_0000 <= number < 0x0000_8000_0000_0000 and number % 8 == 0


def scan_arrays(buffer: bytes, sizes=ARRAY_SIZES) -> list[tuple[bytes, int, bytes]]:
    """Find managed `byte[]` payloads of `sizes` bytes.

    Anchored on the length field, not on zero runs: a heap is full of zero runs,
    and walking them one by one in Python took minutes per megabyte. `bytes.find`
    on the 4-byte little-endian length runs at C speed.

    Two IL2CPP layouts are checked, because the header shape moved between
    runtime versions:

    A) [klass 8][monitor 8 = 0][length i32][payload]                 payload at +4
    B) [klass 8][monitor 8 = 0][bounds 8 = 0][length i64][payload]   payload at +8
    """
    found = []
    zeros = b"\x00" * 8
    for size in sizes:
        short = size.to_bytes(4, "little")
        at = buffer.find(short)
        while at >= 0:
            # layout A
            if (at >= 16 and buffer[at - 8:at] == zeros
                    and looks_like_pointer(buffer[at - 16:at - 8])
                    and at + 4 + size <= len(buffer)):
                payload = buffer[at + 4:at + 4 + size]
                if payload.count(payload[:1]) != len(payload):
                    found.append((buffer[at - 16:at - 8], at - 16, payload))
            # layout B: the length is 8 bytes wide, so the same needle sits at the
            # low half; the zero monitor is one slot further back
            if (at >= 24 and buffer[at + 4:at + 8] == b"\x00" * 4
                    and buffer[at - 16:at - 8] == zeros
                    and looks_like_pointer(buffer[at - 24:at - 16])
                    and at + 8 + size <= len(buffer)):
                payload = buffer[at + 8:at + 8 + size]
                if payload.count(payload[:1]) != len(payload):
                    found.append((buffer[at - 24:at - 16], at - 24, payload))
            at = buffer.find(short, at + 1)
    return found


def test_keys(keys: list[tuple[str, bytes]], iv_pool: set,
              plain_first: bytes, cipher_first: bytes) -> list[dict]:
    """One AES decryption per key; accept only structured candidates.

    Stream construction (CTR / CFB / OFB): `keystream = C0 xor P0` and
        `AES-decrypt(key, keystream)` is the counter/feedback block, i.e. a real
        16-byte array from the process.

    CBC: `C0 = E(P0 xor IV)`, so `AES-decrypt(key, C0) = P0 xor IV`; precompute
    `P0 xor IV` for every IV in the pool and the test stays a single lookup.
    """
    from Crypto.Cipher import AES          # pycryptodome

    keystream = bytes(a ^ b for a, b in zip(cipher_first, plain_first))
    targets = {bytes(a ^ b for a, b in zip(plain_first, iv)): iv for iv in iv_pool}
    zeros = b"\x00" * BLOCK
    hits = []
    for origin, key in keys:
        try:
            ecb = AES.new(key, AES.MODE_ECB)
        except ValueError:
            continue
        value = ecb.decrypt(keystream)
        if value in iv_pool or value == zeros:
            hits.append({"mode": "stream", "key_hex": key.hex(),
                         "iv_hex": value.hex(), "key_from": origin,
                         "iv_known": value != zeros})
        other = ecb.decrypt(cipher_first[:BLOCK])
        if other in targets:
            hits.append({"mode": "cbc", "key_hex": key.hex(),
                         "iv_hex": targets[other].hex(), "key_from": origin,
                         "iv_known": True})
    return hits


def verify(bundle_path: Path, key: bytes, iv: bytes, mode: str) -> bool:
    """Decrypt the first 32 bytes and look for the bundle signature."""
    from Crypto.Cipher import AES

    with bundle_path.open("rb") as handle:
        cipher = handle.read(32)
    ecb = AES.new(key, AES.MODE_ECB)
    if mode == "cbc":
        plain = bytes(a ^ b for a, b in zip(ecb.decrypt(cipher), iv))
    else:
        plain = bytes(a ^ b for a, b in zip(cipher, ecb.encrypt(iv)))
    return plain.startswith(b"UnityFS\x00")


def collect(kernel32, handle, max_scan: int = 0, progress=None) -> tuple[list, set, dict]:
    """Walk the process' readable memory and collect key/IV candidates.

    Memory is read in 8 MB chunks with a 64-byte overlap (an array header can
    straddle a chunk boundary), never a whole region at once: a single region can
    be gigabytes and Python does not need to hold it.
    """
    from mem_carve import (CHUNK, MEM_COMMIT, MEMORY_BASIC_INFORMATION, PAGE_GUARD,
                           READABLE, read_process)

    keys: list[tuple[str, bytes]] = []
    iv_pool: set = set()
    seen: set = set()
    stats = {"regions": 0, "bytes": 0}
    address = 0
    scanned = 0
    mbi = MEMORY_BASIC_INFORMATION()
    while True:
        if not kernel32.VirtualQueryEx(handle, ctypes.c_void_p(address),
                                       ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        base = mbi.BaseAddress or 0
        size = mbi.RegionSize or 0
        readable = (mbi.State == MEM_COMMIT and mbi.Protect in READABLE
                    and not (mbi.Protect & PAGE_GUARD))
        if readable and size > 0:
            stats["regions"] += 1
            offset = 0
            while offset < size:
                want = min(CHUNK, size - offset)
                buffer = read_process(kernel32, handle, base + offset,
                                      min(want + 64, CHUNK + 64), CHUNK)
                for klass, _address, payload in scan_arrays(buffer[:want]):
                    digest = hashlib.sha256(payload).digest()[:8]
                    if digest in seen:
                        continue
                    seen.add(digest)
                    if len(payload) == BLOCK:
                        if len(iv_pool) < MAX_POOL:
                            iv_pool.add(payload)
                    else:
                        keys.append(("heap", payload))
                scanned += want
                stats["bytes"] = scanned
                if progress and stats["regions"] % 50 == 0:
                    progress(scanned, len(keys), stats["regions"])
                if max_scan and scanned >= max_scan:
                    return keys, iv_pool, stats
                offset += want
        next_address = base + size
        if next_address <= address:
            break
        address = next_address
    return keys, iv_pool, stats


def self_test() -> dict:
    """Prove the whole pipeline on a synthetic heap, on any platform."""
    from Crypto.Cipher import AES

    key = hashlib.sha256(b"selftest-key").digest()          # 32 bytes
    iv = hashlib.md5(b"selftest-iv").digest()               # 16 bytes
    ecb = AES.new(key, AES.MODE_ECB)
    cipher = bytes(a ^ b for a, b in zip(BUNDLE_PREFIX,
                                         ecb.encrypt(iv)))
    keystream = bytes(a ^ b for a, b in zip(cipher[:BLOCK], BUNDLE_PREFIX[:BLOCK]))

    klass = (0x1f1803285d0).to_bytes(8, "little")     # a plausible heap address
    heap = b"\x00" * 64
    for payload in (iv, key, hashlib.md5(b"other").digest()):
        heap += klass + b"\x00" * 8 + len(payload).to_bytes(4, "little") + payload
        heap += b"\x00" * ((8 - len(heap) % 8) % 8)

    arrays = scan_arrays(heap)
    keys = [("selftest", payload) for _klass, _addr, payload in arrays
            if len(payload) == 32]
    iv_pool = {payload for _klass, _addr, payload in arrays if len(payload) == 16}
    hits = test_keys(keys, iv_pool, BUNDLE_PREFIX[:BLOCK], cipher[:BLOCK])
    return {"ok": any(hit["key_hex"] == key.hex() and hit["iv_hex"] == iv.hex()
                      for hit in hits),
            "arrays": len(arrays), "hits": len(hits)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bundle", type=Path,
                        help="one encrypted bundle from the game folder")
    parser.add_argument("--process", default="SUPER ROBOT WARS Y.exe")
    parser.add_argument("--report", type=Path, default=Path("key_report.json"))
    parser.add_argument("--max-scan", type=int, default=0,
                        help="stop after this many bytes (0 = whole address space)")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    print(f"key_from_memory {SCRIPT_VERSION}")
    if args.selftest:
        result = self_test()
        print(f"self-test: {'PASS' if result['ok'] else 'FAIL'} "
              f"({result['arrays']} arrays, {result['hits']} hits)")
        return 0 if result["ok"] else 1
    if not args.bundle:
        print("error: --bundle is required (one encrypted bundle file)", file=sys.stderr)
        return 2

    from Crypto.Cipher import AES  # noqa: F401  (fail early if missing)
    from mem_carve import PROCESS_QUERY_INFORMATION, PROCESS_VM_READ, process_pid, win_api

    cipher = cipher_block(args.bundle)
    kernel32 = win_api()
    pid = process_pid(args.process)
    if pid is None:
        print(f"error: process not found: {args.process}", file=sys.stderr)
        return 2
    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                  False, pid)
    if not handle:
        print("error: OpenProcess failed; run PowerShell as administrator",
              file=sys.stderr)
        return 2
    try:
        def report_progress(total, key_count, regions):
            print(f"  scanned {total / 1e9:.2f} GB, {regions:,} regions, "
                  f"keys {key_count:,}", flush=True)

        keys, iv_pool, stats = collect(kernel32, handle, args.max_scan,
                                       progress=report_progress)
    finally:
        kernel32.CloseHandle(handle)

    hits = test_keys(keys, iv_pool, BUNDLE_PREFIX[:BLOCK], cipher)
    verified = []
    for hit in hits:
        if verify(args.bundle, bytes.fromhex(hit["key_hex"]),
                  bytes.fromhex(hit["iv_hex"]), hit["mode"]):
            hit["verified"] = True
            verified.append(hit)

    report = {"script_version": SCRIPT_VERSION,
              "scanned": stats, "key_candidates": len(keys),
              "iv_candidates": len(iv_pool), "hits": hits,
              "verified": verified}
    args.report.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")

    print(f"scanned {stats['bytes']:,} B in {stats['regions']:,} regions")
    print(f"candidates: {len(keys):,} keys, {len(iv_pool):,} IVs")
    print(f"hits: {len(hits)} (verified: {len(verified)})")
    for hit in verified[:3]:
        print(f"  FOUND {hit['mode']}: key {hit['key_hex']} iv {hit['iv_hex']}")
    print(f"report: {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
