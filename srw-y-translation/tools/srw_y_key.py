#!/usr/bin/env python3
"""SRW Y - one file that recovers the bundle key and patches bundles.

Two jobs, one script, so the game folder never needs a toolkit:

    python srw_y_key.py selftest
    python srw_y_key.py key --bundle "D:\\...\\1cc7e02e....bundle"
    python srw_y_key.py decrypt --in "D:\\...\\x.bundle" --out "decrypted.bundle"
    python srw_y_key.py encrypt --mode ctr-le --in "decrypted.bundle" --out "x.bundle"

Why the key comes from the process: the bundles are encrypted by the game's own
`SeekableAesStream`, the key is derived from a password + salt with `Rfc2898`,
and neither the password nor the salt exists as a string in `GameAssembly.dll`
(IL2CPP compiles the names away, and 61 million static windows were tested).
The game must decrypt every bundle it uses, so the key is in its heap.

How one AES operation tests a key: every bundle in this build starts with the
same 30 bytes, so for a stream construction

    keystream0 = ciphertext0 xor plaintext0        and   AES-decrypt(key, keystream0) = IV

and for CBC

    AES-decrypt(key, ciphertext0) = plaintext0 xor IV

so a candidate key is accepted only when that value is a real 16-byte array from
the same heap (or all zeros). No plaintext file needed, no brute force.

Reading memory is read-only: PROCESS_QUERY_INFORMATION | PROCESS_VM_READ.

Requires: Python 3.9+ (64-bit) and pycryptodome (`python -m pip install pycryptodome`).
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

SCRIPT_VERSION = "2026-10-26.2"

# ---------------------------------------------------------------- bundle facts
# Taken from bundles carved out of the game's memory: one distinct prefix across
# 200 samples.
BUNDLE_PREFIX = b"UnityFS\x00\x00\x00\x00\x085.x.x\x002022.3.44f1\x00"
BLOCK = 16
ARRAY_SIZES = (16, 24, 32)      # AES-128 / AES-192 / AES-256 keys and 16-byte IVs
MAX_POOL = 20000                # how many distinct 16-byte arrays to keep
CHUNK = 8 * 1024 * 1024
PROBE = 4096
MODES = ("ctr-le", "ctr-be", "cfb128", "ofb", "cbc")
DEFAULT_PROCESS = "SUPER ROBOT WARS Y.exe"

# --------------------------------------------------------------- windows api
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
READABLE = (0x02, 0x04, 0x08, 0x20, 0x40, 0x80)   # READONLY..WRITECOMBINE


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.c_uint32),
                ("PartitionId", ctypes.c_uint16),
                ("__alignment1", ctypes.c_uint16),
                ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.c_uint32),
                ("Protect", ctypes.c_uint32),
                ("Type", ctypes.c_uint32),
                ("__alignment2", ctypes.c_uint32)]


def win_api():
    """Load kernel32 with explicit prototypes (ctypes defaults to `int`)."""
    if sys.platform != "win32":
        raise RuntimeError("reading the game's memory needs Windows")
    if ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("a 64-bit Python is required for a 64-bit game")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel32.CloseHandle.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.VirtualQueryEx.restype = ctypes.c_size_t
    kernel32.VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                        ctypes.POINTER(MEMORY_BASIC_INFORMATION),
                                        ctypes.c_size_t]
    kernel32.ReadProcessMemory.restype = ctypes.c_int
    kernel32.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                           ctypes.c_void_p, ctypes.c_size_t,
                                           ctypes.POINTER(ctypes.c_size_t)]
    return kernel32


def process_pid(image_name: str) -> int | None:
    """Find a PID by image name, without third-party modules."""
    result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {image_name}",
                             "/FO", "CSV", "/NH"],
                            capture_output=True, text=True, check=False)
    for line in result.stdout.splitlines():
        parts = [item.strip('"') for item in line.split('","')]
        if len(parts) >= 2 and parts[0].lower() == image_name.lower():
            try:
                return int(parts[1])
            except ValueError:
                continue
    return None


def read_process(api, handle, address: int, size: int, piece: int = CHUNK) -> bytes:
    """Read `size` bytes at `address`; a short read ends the buffer."""
    view = (ctypes.c_char * piece)()
    out = bytearray()
    while len(out) < size:
        want = min(piece, size - len(out))
        read = ctypes.c_size_t(0)
        ok = api.ReadProcessMemory(ctypes.c_void_p(handle),
                                   ctypes.c_void_p(address + len(out)),
                                   ctypes.cast(view, ctypes.c_void_p),
                                   want, ctypes.byref(read))
        if not ok or read.value == 0:
            break
        out += view.raw[:read.value]
    return bytes(out)


# -------------------------------------------------------------- key recovery
def looks_like_pointer(value: bytes) -> bool:
    number = int.from_bytes(value, "little")
    return 0x0001_0000 <= number < 0x0000_8000_0000_0000 and number % 8 == 0


def scan_arrays(buffer: bytes, sizes=ARRAY_SIZES) -> list[tuple[bytes, int, bytes]]:
    """Find managed `byte[]` payloads of `sizes` bytes.

    Anchored on the little-endian length field: a heap is full of zero runs, and
    walking them in Python took minutes per megabyte. Two IL2CPP layouts:

    A) [klass 8][monitor 8 = 0][length i32][payload]                 payload at +4
    B) [klass 8][monitor 8 = 0][bounds 8 = 0][length i64][payload]   payload at +8
    """
    found = []
    zeros = b"\x00" * 8
    for size in sizes:
        short = size.to_bytes(4, "little")
        at = buffer.find(short)
        while at >= 0:
            if (at >= 16 and buffer[at - 8:at] == zeros
                    and looks_like_pointer(buffer[at - 16:at - 8])
                    and at + 4 + size <= len(buffer)):
                payload = buffer[at + 4:at + 4 + size]
                if payload.count(payload[:1]) != len(payload):
                    found.append((buffer[at - 16:at - 8], at - 16, payload))
            if (at >= 24 and buffer[at + 4:at + 8] == b"\x00" * 4
                    and buffer[at - 16:at - 8] == zeros
                    and looks_like_pointer(buffer[at - 24:at - 16])
                    and at + 8 + size <= len(buffer)):
                payload = buffer[at + 8:at + 8 + size]
                if payload.count(payload[:1]) != len(payload):
                    found.append((buffer[at - 24:at - 16], at - 24, payload))
            at = buffer.find(short, at + 1)
    return found


def cipher_block(bundle: Path) -> bytes:
    with bundle.open("rb") as handle:
        data = handle.read(BLOCK)
    if len(data) < BLOCK:
        raise ValueError("bundle file is too short")
    return data


def test_keys(keys: list[tuple[str, bytes]], iv_pool: set,
              plain_first: bytes, cipher_first: bytes) -> list[dict]:
    """One AES decryption per key; accept only structured candidates."""
    from Crypto.Cipher import AES

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
        other = ecb.decrypt(cipher_first)
        if other in targets:
            hits.append({"mode": "cbc", "key_hex": key.hex(),
                         "iv_hex": targets[other].hex(), "key_from": origin,
                         "iv_known": True})
    return hits


def collect(api, handle, max_scan: int = 0, progress=None) -> tuple[list, set, dict]:
    """Walk readable memory and collect key/IV candidates.

    Chunks of 8 MB with 64 bytes of overlap, so an array header that straddles a
    chunk boundary is still seen.
    """
    keys: list[tuple[str, bytes]] = []
    iv_pool: set = set()
    seen: set = set()
    stats = {"regions": 0, "bytes": 0}
    address = 0
    scanned = 0
    mbi = MEMORY_BASIC_INFORMATION()
    while True:
        if not api.VirtualQueryEx(handle, ctypes.c_void_p(address),
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
                buffer = read_process(api, handle, base + offset,
                                      min(want + 64, CHUNK + 64), CHUNK)
                for _klass, _addr, payload in scan_arrays(buffer[:want]):
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
                    progress(scanned)
                if max_scan and scanned >= max_scan:
                    return keys, iv_pool, stats
                offset += want
        next_address = base + size
        if next_address <= address:
            break
        address = next_address
    return keys, iv_pool, stats


def verify(bundle: Path, key: bytes, iv: bytes, mode: str) -> bool:
    """Decrypt the first 32 bytes and look for the bundle signature."""
    from Crypto.Cipher import AES

    with bundle.open("rb") as handle:
        data = handle.read(32)
    ecb = AES.new(key, AES.MODE_ECB)
    if mode == "cbc":
        plain = bytes(a ^ b for a, b in zip(ecb.decrypt(data), iv))
    else:
        plain = bytes(a ^ b for a, b in zip(data, ecb.encrypt(iv)))
    return plain.startswith(b"UnityFS\x00")


# ------------------------------------------------------------------ the cipher
def _counter_stream(key: bytes, start: bytes, length: int, little: bool) -> bytes:
    """AES-CTR with the whole 16-byte block as the counter."""
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    value = int.from_bytes(start, "little" if little else "big")
    out = bytearray()
    while len(out) < length:
        out += ecb.encrypt(value.to_bytes(BLOCK, "little" if little else "big"))
        value = (value + 1) % (1 << 128)
    return bytes(out[:length])


def xor(data: bytes, stream: bytes) -> bytes:
    if len(data) != len(stream):
        raise ValueError("keystream length must match the data")
    return (int.from_bytes(data, "big")
            ^ int.from_bytes(stream, "big")).to_bytes(len(data), "big")


def _cipher(key: bytes, iv: bytes, mode: str):
    from Crypto.Cipher import AES

    if mode == "cfb128":
        return AES.new(key, AES.MODE_CFB, iv, segment_size=128)
    if mode == "ofb":
        return AES.new(key, AES.MODE_OFB, iv)
    if mode == "cbc":
        return AES.new(key, AES.MODE_CBC, iv)
    raise ValueError(f"unknown mode: {mode}")


def decrypt(key: bytes, iv: bytes, data: bytes, mode: str) -> bytes:
    if mode == "ctr-le":
        return xor(data, _counter_stream(key, iv, len(data), True))
    if mode == "ctr-be":
        return xor(data, _counter_stream(key, iv, len(data), False))
    return _cipher(key, iv, mode).decrypt(data)


def encrypt(key: bytes, iv: bytes, data: bytes, mode: str) -> bytes:
    if mode == "ctr-le":
        return xor(data, _counter_stream(key, iv, len(data), True))
    if mode == "ctr-be":
        return xor(data, _counter_stream(key, iv, len(data), False))
    return _cipher(key, iv, mode).encrypt(data)


def parse_unityfs(data: bytes) -> dict | None:
    """Parse a UnityFS header (big-endian, Unity 5+ layout)."""
    if not data.startswith(b"UnityFS\x00") or len(data) < 48:
        return None
    pos = 8
    try:
        pos += 4                                   # version
        values = []
        for _ in range(2):                         # player version, revision
            end = data.find(b"\x00", pos, pos + 256)
            if end < 0:
                return None
            values.append(data[pos:end].decode("latin-1", "replace"))
            pos = end + 1
        size = struct.unpack_from(">q", data, pos)[0]
        pos += 8
        blocks = struct.unpack_from(">I", data, pos)[0]
        unblocks = struct.unpack_from(">I", data, pos + 4)[0]
        flags = struct.unpack_from(">I", data, pos + 8)[0]
    except struct.error:
        return None
    if size <= 0 or size > (1 << 40):
        return None
    if not values[1].startswith(("20", "5.")):
        return None
    return {"unity_revision": values[1], "size": size,
            "compressed_blocks_info_size": blocks,
            "uncompressed_blocks_info_size": unblocks, "flags": flags}


def identify(key: bytes, iv: bytes, data: bytes):
    """Return (mode, plaintext, header) for the first construction that fits."""
    for mode in MODES:
        if mode == "cbc" and len(data) % BLOCK:
            continue                # the bundles are not block multiples
        try:
            probe = decrypt(key, iv, data[:PROBE], mode)
        except ValueError:
            continue
        header = parse_unityfs(probe)
        if header is None or header["size"] != len(data):
            continue
        try:
            return mode, decrypt(key, iv, data, mode), header
        except ValueError:
            continue
    return None


# -------------------------------------------------------------------- selftest
def _synthetic(size: int) -> bytes:
    """A bundle with the real prefix, so the key tests see the real first block."""
    header = (BUNDLE_PREFIX + size.to_bytes(8, "big")
              + (64).to_bytes(4, "big") + (64).to_bytes(4, "big")
              + (0x40).to_bytes(4, "big"))
    return header + bytes((i * 37 + 11) % 251 for i in range(size - len(header)))


def selftest() -> bool:
    from Crypto.Cipher import AES

    ok = True

    # 1. the prefix is the real one and the keystream identity holds
    key = hashlib.sha256(b"selftest").digest()
    iv = hashlib.md5(b"selftest-iv").digest()
    ecb = AES.new(key, AES.MODE_ECB)
    cipher = bytes(a ^ b for a, b in zip(BUNDLE_PREFIX, ecb.encrypt(iv)))
    keystream = bytes(a ^ b for a, b in zip(cipher[:BLOCK], BUNDLE_PREFIX[:BLOCK]))
    hits = test_keys([("selftest", key)], {iv}, BUNDLE_PREFIX[:BLOCK],
                     cipher[:BLOCK])
    ok &= ecb.decrypt(keystream) == iv[:BLOCK]
    ok &= any(hit["key_hex"] == key.hex() and hit["iv_hex"] == iv.hex()
              for hit in hits)
    print(f"  key test        {'ok' if ok else 'FAILED'}")

    # 2. arrays in both layouts are found, constant payloads are not
    klass = (0x1F1803285D0).to_bytes(8, "little")
    blob = b"\x00" * 32
    for payload in (bytes(range(16)), bytes(range(32)), bytes(range(24))):
        blob += klass + b"\x00" * 8 + struct.pack("<i", len(payload)) + payload
        blob += b"\x00" * ((8 - len(blob) % 8) % 8)
    found = [len(payload) for _k, _a, payload in scan_arrays(blob)]
    arrays_ok = sorted(found) == [16, 24, 32] and scan_arrays(
        klass + b"\x00" * 8 + struct.pack("<i", 32) + b"\x00" * 32) == []
    ok &= arrays_ok
    print(f"  byte[] scan     {'ok' if arrays_ok else 'FAILED'}")

    # 3. every construction round-trips and is identified as itself
    for mode in MODES:
        plain = _synthetic(8192 if mode == "cbc" else 8203)
        round_trip = identify(key, iv, encrypt(key, iv, plain, mode))
        good = bool(round_trip and round_trip[0] == mode and round_trip[1] == plain)
        ok &= good
        print(f"  {mode:14}{'ok' if good else 'FAILED'}")
    return bool(ok)


# ------------------------------------------------------------------------ cli
def load_key(args) -> tuple[bytes, bytes, str | None]:
    if args.key and args.iv:
        return bytes.fromhex(args.key), bytes.fromhex(args.iv), None
    if args.report:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
        hits = report.get("verified") or report.get("hits") or []
        if not hits:
            raise SystemExit("the report has no key hits; run `key` again")
        hit = hits[0]
        return (bytes.fromhex(hit["key_hex"]), bytes.fromhex(hit["iv_hex"]),
                hit.get("mode"))
    if args.key and args.iv:
        return bytes.fromhex(args.key), bytes.fromhex(args.iv), None
    raise SystemExit("give --report, or both --key and --iv")


def cmd_key(args) -> int:
    bundle = Path(args.bundle)
    if not bundle.exists():
        print(f"error: bundle not found: {bundle}", file=sys.stderr)
        return 2
    pid = process_pid(args.process)
    if pid is None:
        print(f"error: the game is not running ({args.process})", file=sys.stderr)
        return 2
    try:
        api = win_api()
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    handle = api.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                             False, pid)
    if not handle:
        print("error: cannot open the process; run PowerShell as administrator",
              file=sys.stderr)
        return 2
    print(f"attached to pid {pid}; scanning read-only", flush=True)
    try:
        keys, iv_pool, stats = collect(
            api, handle, args.max_scan,
            progress=lambda total: print(f"  scanned {total / 1e9:.2f} GB, "
                                         f"keys {len(keys):,}", flush=True))
    finally:
        api.CloseHandle(handle)

    first = cipher_block(bundle)
    hits = test_keys(keys, iv_pool, BUNDLE_PREFIX[:BLOCK], first)
    verified = []
    for hit in hits:
        if verify(bundle, bytes.fromhex(hit["key_hex"]),
                  bytes.fromhex(hit["iv_hex"]), hit["mode"]):
            hit["verified"] = True
            verified.append(hit)

    report = {"script_version": SCRIPT_VERSION, "scanned": stats,
              "key_candidates": len(keys), "iv_candidates": len(iv_pool),
              "hits": hits, "verified": verified, "bundle": str(bundle)}
    Path(args.report).write_text(json.dumps(report, indent=1) + "\n",
                                 encoding="utf-8")
    print(f"scanned {stats['bytes']:,} B in {stats['regions']:,} regions")
    print(f"candidates: {len(keys):,} keys, {len(iv_pool):,} IVs")
    print(f"hits: {len(hits)} (verified: {len(verified)})")
    for hit in verified[:3]:
        print(f"  FOUND {hit['mode']}: key {hit['key_hex']} iv {hit['iv_hex']}")
    print(f"report: {args.report}")
    if not verified:
        print("nothing verified - keep the game running with a scene loaded and "
              "run again")
    return 0 if verified else 1


def cmd_crypt(args, encrypting: bool) -> int:
    key, iv, reported = load_key(args)
    source = Path(args.inp)
    target = Path(args.out)
    if not source.exists():
        print(f"error: file not found: {source}", file=sys.stderr)
        return 2
    data = source.read_bytes()
    if encrypting:
        header = parse_unityfs(data[:PROBE])
        if header is None:
            print("error: the input is not a plaintext bundle", file=sys.stderr)
            return 1
        mode = args.mode or reported
        if mode is None:
            print("error: pass --mode (it is printed by the decrypt run)",
                  file=sys.stderr)
            return 2
        target.write_bytes(encrypt(key, iv, data, mode))
        print(f"mode: {mode}; re-encrypted {len(data):,} B -> {target}")
        return 0

    if args.mode:
        plain = decrypt(key, iv, data, args.mode)
        header = parse_unityfs(plain[:PROBE])
        if header is None:
            print(f"error: {args.mode} does not produce a UnityFS header",
                  file=sys.stderr)
            return 1
        mode = args.mode
    else:
        found = identify(key, iv, data)
        if found is None:
            print("error: no construction fits; the key or the IV is wrong",
                  file=sys.stderr)
            return 1
        mode, plain, header = found
    target.write_bytes(plain)
    print(f"mode: {mode}")
    print(f"unity: {header['unity_revision']}, size {header['size']:,} B")
    print(f"wrote {target} ({len(plain):,} B)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SRW Y key recovery and bundle "
                                                 "patching")
    parser.add_argument("--version", action="version", version=SCRIPT_VERSION)
    sub = parser.add_subparsers(dest="command")

    key = sub.add_parser("key", help="find the key in the running game")
    key.add_argument("--bundle", required=True, help="one encrypted bundle")
    key.add_argument("--process", default=DEFAULT_PROCESS)
    key.add_argument("--report", default="key_report.json")
    key.add_argument("--max-scan", type=int, default=0,
                     help="stop after this many bytes (0 = everything)")

    for name, encrypting in (("decrypt", False), ("encrypt", True)):
        part = sub.add_parser(name, help=f"{name} a bundle")
        part.add_argument("--in", dest="inp", required=True)
        part.add_argument("--out", required=True)
        part.add_argument("--report", default="key_report.json")
        part.add_argument("--key")
        part.add_argument("--iv")
        part.add_argument("--mode", choices=MODES)

    sub.add_parser("selftest", help="prove the script works, no game needed")

    args = parser.parse_args(argv)
    print(f"srw_y_key {SCRIPT_VERSION}")
    if args.command == "selftest" or args.command is None:
        ok = selftest()
        print(f"selftest: {'PASS' if ok else 'FAILED'}")
        return 0 if ok else 1
    if args.command == "key":
        return cmd_key(args)
    if args.command == "decrypt":
        return cmd_crypt(args, False)
    if args.command == "encrypt":
        return cmd_crypt(args, True)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
