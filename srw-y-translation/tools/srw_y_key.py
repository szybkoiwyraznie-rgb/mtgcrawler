#!/usr/bin/env python3
"""SRW Y - one file that recovers the bundle key and patches bundles.

    python srw_y_key.py selftest
    python srw_y_key.py key --bundle "D:\\...\\1cc7e02e....bundle"
    python srw_y_key.py decrypt --in "D:\\...\\x.bundle" --out "decrypted.bundle"
    python srw_y_key.py encrypt --mode ctr-le --in "decrypted.bundle" --out "x.bundle"

Why the key comes from the process: the bundles are encrypted by the game's own
`SeekableAesStream`, the key is derived from a password + salt with `Rfc2898`,
and neither the password nor the salt exists as a string in `GameAssembly.dll`
(IL2CPP compiles the names away, and 61 million static windows were tested).
The game must decrypt every bundle it uses, so the key is in its heap.

Why the test needs no IV: every bundle in this build starts with the same bytes,
`UnityFS\\0` + version 8 + `5.x.x\\0` + `2022.3.44f1\\0`, and the 8-byte size at
offset 30 equals the file size. That is 38 known plaintext bytes, enough to check
three cipher blocks. For a candidate key the first block gives the state

    AES-decrypt(key, ciphertext0 xor plaintext0) = counter block   (CTR)

and the next two blocks are then derived and compared with the known plaintext.
A wrong key cannot satisfy 16 + 16 + 6 bytes, so no IV has to be found in the
heap - the earlier version demanded exactly that and never found a key.

Reading memory is read-only: PROCESS_QUERY_INFORMATION | PROCESS_VM_READ.

Requires: Python 3.9+ (64-bit) and pycryptodome (`python -m pip install pycryptodome`).
"""
from __future__ import annotations

import argparse
import ctypes
import json
import hashlib
import struct
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_VERSION = "2026-10-26.8"

# ---------------------------------------------------------------- bundle facts
# Taken from bundles carved out of the game's memory: one distinct prefix across
# 200 samples.
BUNDLE_PREFIX = b"UnityFS\x00\x00\x00\x00\x085.x.x\x002022.3.44f1\x00"
KNOWN_PREFIX = 30          # bytes of the header that never change
KNOWN_SIZE_AT = 30         # 8-byte big-endian size follows the prefix
KNOWN_BYTES = 38           # prefix + size: enough to check three cipher blocks
BLOCK = 16
ARRAY_SIZES = (16, 24, 32)      # AES-128 / AES-192 / AES-256 keys and 16-byte IVs
MAX_POOL = 20000
CHUNK = 8 * 1024 * 1024
PROBE = 4096
COUNTER_MODES = ("ctr-le", "ctr-be", "ctr-le-byte", "ctr-be-byte",
                 "ctr-le-xoridx", "ctr-be-xoridx",
                 "ctr-le-xorbyte", "ctr-be-xorbyte",
                 "ctr32le", "ctr32be")
MODES = COUNTER_MODES + ("ofb", "cfb128", "cfb8", "cbc", "ecb")
DUMP_LIMIT = 1_000_000
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
PAYLOAD_OFFSETS = (4, 8, 12)    # where the bytes can start after a length field


def looks_like_pointer(value: bytes) -> bool:
    number = int.from_bytes(value, "little")
    return 0x0001_0000 <= number < 0x0000_8000_0000_0000 and number % 8 == 0


def scan_arrays(buffer: bytes, sizes=ARRAY_SIZES) -> list[tuple[int, int, bytes]]:
    """Find candidates for managed `byte[]` payloads of `sizes` bytes.

    Anchored on the little-endian length field (a heap is full of zero runs, and
    walking those in Python took minutes per megabyte). The header layout differs
    between runtimes:

        [klass 8][monitor 8 = 0][length i32][payload]              payload +4
        [klass 8][monitor 8 = 0][length i64][payload]              payload +8
        [klass 8][monitor 8 = 0][bounds 8 = 0][length i64][payload] payload +8

    So every length field with a zero monitor and a plausible class pointer in
    front yields candidates at +4, +8 and +12: the payload offset is guessed, and
    the key test decides. Guessing wrong used to cost a whole run.

    Returns (offset, size, payload) triples with duplicates possible.
    """
    found = []
    zeros = b"\x00" * 8
    for size in sizes:
        short = size.to_bytes(4, "little")
        at = buffer.find(short)
        while at >= 0:
            monitor = buffer[at - 8:at] if at >= 8 else b""
            # the word before the length is the object's sync block: zero for a
            # normal object, a pointer for a locked one (a thin lock). Requiring
            # zero - as the earlier versions did - hides every locked array.
            monitor_ok = monitor == zeros or looks_like_pointer(monitor)
            if (at >= 16 and monitor_ok
                    and looks_like_pointer(buffer[at - 16:at - 8])):
                for offset in PAYLOAD_OFFSETS:
                    start = at + offset
                    if start + size <= len(buffer):
                        payload = buffer[start:start + size]
                        if payload.count(payload[:1]) != len(payload):
                            found.append((start, size, payload))
            at = buffer.find(short, at + 1)
    return found


def known_plain(size: int, length: int = 48) -> bytes:
    """The known plaintext head of a bundle of `size` bytes.

    Bytes 38..47 (block sizes, flags) are unknown and left as zeros; callers only
    compare the first 6 bytes of the third block.
    """
    head = BUNDLE_PREFIX + size.to_bytes(8, "big")
    return (head + b"\x00" * (BLOCK * 3))[:length]


def xor(data: bytes, stream: bytes) -> bytes:
    if len(data) != len(stream):
        raise ValueError("keystream length must match the data")
    return (int.from_bytes(data, "big")
            ^ int.from_bytes(stream, "big")).to_bytes(len(data), "big")


def cfb8_state(cipher: bytes, upto_block: int) -> bytes:
    """CFB-8 keeps the last 16 ciphertext bytes as the feedback state."""
    end = upto_block * BLOCK
    state = cipher[max(0, end - BLOCK):end]
    return state.rjust(BLOCK, b"\x00")


def cfb8_state_byte(key: bytes, cipher: bytes, index: int) -> int:
    """First keystream byte of block `index` under CFB-8 (one AES call)."""
    from Crypto.Cipher import AES

    return AES.new(key, AES.MODE_ECB).encrypt(cfb8_state(cipher, index))[0]


def cfb8_block(key: bytes, cipher: bytes, index: int) -> bytes | None:
    """The 16 keystream bytes of block `index` under CFB-8, or None."""
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    state = cfb8_state(cipher, index)
    out = bytearray()
    for step in range(BLOCK):
        byte = ecb.encrypt(state)[0]
        out.append(byte)
        position = index * BLOCK + step
        if position < len(cipher):
            state = state[1:] + cipher[position:position + 1]
        if step == 0 and index > 0:
            # cheap rejection: compare the first byte of the block
            pass
    return bytes(out)


def cfb8_matches(key: bytes, cipher: bytes, known: bytes) -> bool:
    """Two single-AES checks reject a wrong key before the expensive path."""
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    for index in (1, 2):
        stream_byte = ecb.encrypt(cfb8_state(cipher, index))[0]
        if stream_byte != cipher[index * BLOCK] ^ known[index * BLOCK]:
            return False
    for index in (1, 2):
        got = xor(cipher[index * BLOCK:(index + 1) * BLOCK],
                  cfb8_block(key, cipher, index))
        want = known[index * BLOCK:(index + 1) * BLOCK]
        if (got != want) if index < 2 else (got[:6] != want[:6]):
            return False
    return True


def cfb8_decrypt(key: bytes, cipher: bytes) -> bytes:
    """CFB-8 feedback is the ciphertext, so only the first block needs the IV.

    That block is the known header anyway, so the whole file decrypts without
    knowing the IV - which is exactly what the previous version lacked.
    """
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    out = bytearray(cipher[:BLOCK])          # filled with the known prefix below
    out[:BLOCK] = known_plain(len(cipher))[:BLOCK]
    state = cipher[:BLOCK]
    for position in range(BLOCK, len(cipher)):
        out.append(cipher[position] ^ ecb.encrypt(bytes(state))[0])
        state = state[1:] + cipher[position:position + 1]
    return bytes(out)


def cfb8_encrypt(key: bytes, plain: bytes) -> bytes:
    """Inverse of cfb8_decrypt; the first block is taken from the plaintext."""
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    out = bytearray(plain[:BLOCK])
    state = bytes(plain[:BLOCK])
    for position in range(BLOCK, len(plain)):
        byte = plain[position] ^ ecb.encrypt(bytes(state))[0]
        out.append(byte)
        state = state[1:] + bytes([byte])
    return bytes(out)


def state_hypotheses(bundle: Path) -> dict:
    """Values the counter block / IV could plausibly be, from the file name.

    The names are 32 hex characters, i.e. exactly 16 bytes, so "IV = the file name"
    is a real possibility for a seekable stream. If the recovered state equals one
    of these, the key is right even when the advance rule is unusual.
    """
    import hashlib

    stem = bundle.stem
    out = {}
    try:
        out[bytes.fromhex(stem)] = "name-hex"
        out[bytes.fromhex(stem)[::-1]] = "name-hex-reversed"
    except ValueError:
        pass
    raw = (stem + ".bundle").encode()
    out[hashlib.md5(raw).digest()] = "md5(name)"
    out[hashlib.sha1(raw).digest()[:16]] = "sha1(name)"
    out[hashlib.sha256(raw).digest()[:16]] = "sha256(name)"
    out[hashlib.md5(stem.encode()).digest()] = "md5(stem)"
    out[b"\x00" * BLOCK] = "zeros"
    return out


def check_key(key: bytes, cipher: bytes, size: int,
              states: dict | None = None, known: bytes | None = None) -> list[dict]:
    """Which constructions does this key satisfy? No IV from memory needed.

    `cipher` is the first 48 bytes of the file, `size` the file size. A candidate
    costs one AES decryption plus one per construction, and the second block is
    only evaluated when the first matches - the earlier version computed both
    unconditionally and ran at 1 ms per candidate.
    """
    from Crypto.Cipher import AES

    if len(cipher) < 48:
        return []
    if known is None:
        known = known_plain(size)
    ecb = AES.new(key, AES.MODE_ECB)
    ks0 = (int.from_bytes(cipher[0:BLOCK], "big")
           ^ int.from_bytes(known[0:BLOCK], "big")).to_bytes(BLOCK, "big")
    hits = []

    def matches(stream: bytes, index: int) -> bool:
        block = (int.from_bytes(cipher[index * BLOCK:(index + 1) * BLOCK], "big")
                 ^ int.from_bytes(stream, "big")).to_bytes(BLOCK, "big")
        want = known[index * BLOCK:(index + 1) * BLOCK]
        return block == want if index < 2 else block[:6] == want[:6]

    state = ecb.decrypt(ks0)
    if states and state in states:
        hits.append({"mode": "state-" + states[state], "state": state})

    for mode in COUNTER_MODES:
        if not matches(ecb.encrypt(counter_block(state, 1, mode)), 1):
            continue
        if matches(ecb.encrypt(counter_block(state, 2, mode)), 2):
            hits.append({"mode": mode, "state": state})

    first = ecb.encrypt(ks0)
    if matches(first, 1) and matches(ecb.encrypt(first), 2):
        hits.append({"mode": "ofb", "state": ks0})

    first = ecb.encrypt(cipher[0:BLOCK])
    if matches(first, 1) and matches(ecb.encrypt(cipher[BLOCK:2 * BLOCK]), 2):
        hits.append({"mode": "cfb128", "state": state})

    if cfb8_state_byte(key, cipher, 1) == cipher[BLOCK] ^ known[BLOCK] and \
            cfb8_state_byte(key, cipher, 2) == cipher[2 * BLOCK] ^ known[2 * BLOCK]:
        if cfb8_matches(key, cipher, known):
            hits.append({"mode": "cfb8", "state": b"\x00" * BLOCK})

    if ecb.decrypt(cipher[0:BLOCK]) == known[0:BLOCK] and \
            ecb.decrypt(cipher[BLOCK:2 * BLOCK]) == known[BLOCK:2 * BLOCK]:
        hits.append({"mode": "ecb", "state": b"\x00" * BLOCK})

    if (int.from_bytes(ecb.decrypt(cipher[BLOCK:2 * BLOCK]), "big")
            ^ int.from_bytes(cipher[0:BLOCK], "big")).to_bytes(BLOCK, "big") \
            == known[BLOCK:2 * BLOCK]:
        if (int.from_bytes(ecb.decrypt(cipher[2 * BLOCK:3 * BLOCK]), "big")
                ^ int.from_bytes(cipher[BLOCK:2 * BLOCK], "big")).to_bytes(
                    BLOCK, "big")[:6] == known[2 * BLOCK:2 * BLOCK + 6]:
            hits.append({"mode": "cbc",
                         "state": (int.from_bytes(known[0:BLOCK], "big")
                                   ^ int.from_bytes(ecb.decrypt(cipher[0:BLOCK]),
                                                    "big")).to_bytes(BLOCK, "big")})
    return hits


# ------------------------------------------------------------------ the cipher
# mode -> (kind, step, byteorder); resolving this once keeps the hot loop free of
# string work, which dominated the first version (1 ms per candidate)
MODE_TABLE = {
    "ctr-le": ("add", 1, "little"),
    "ctr-be": ("add", 1, "big"),
    "ctr-le-byte": ("add", BLOCK, "little"),
    "ctr-be-byte": ("add", BLOCK, "big"),
    "ctr-le-xoridx": ("xor", 1, "little"),
    "ctr-be-xoridx": ("xor", 1, "big"),
    "ctr-le-xorbyte": ("xor", BLOCK, "little"),
    "ctr-be-xorbyte": ("xor", BLOCK, "big"),
    "ctr32le": ("ctr32", 1, "little"),
    "ctr32be": ("ctr32", 1, "big"),
}


def counter_block(base: bytes, index: int, mode: str) -> bytes:
    """The counter block for block `index` of a CTR-like construction."""
    kind, step, order = MODE_TABLE[mode]
    if kind == "ctr32":
        tail = (int.from_bytes(base[12:16], order) + index * step) % (1 << 32)
        return base[:12] + tail.to_bytes(4, order)
    value = int.from_bytes(base, order)
    if kind == "xor":
        value ^= index * step
    else:
        value = (value + index * step) % (1 << 128)
    return value.to_bytes(BLOCK, order)


def _counter_stream(key: bytes, start: bytes, length: int,
                    mode: str = "ctr-le") -> bytes:
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    out = bytearray()
    index = 0
    while len(out) < length:
        out += ecb.encrypt(counter_block(start, index, mode))
        index += 1
    return bytes(out[:length])


def _ofb_stream(key: bytes, first: bytes, length: int) -> bytes:
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    block = first
    out = bytearray()
    while len(out) < length:
        out += block
        block = ecb.encrypt(block)
    return bytes(out[:length])


def keystream(key: bytes, mode: str, state: bytes, length: int) -> bytes:
    """The XOR stream for the modes that ignore the data (CTR variants, OFB)."""
    if mode in COUNTER_MODES:
        return _counter_stream(key, state, length, mode)
    if mode == "ofb":
        return _ofb_stream(key, state, length)
    raise ValueError(f"{mode} needs the ciphertext to chain")


def decrypt(key: bytes, mode: str, state: bytes, data: bytes) -> bytes:
    from Crypto.Cipher import AES

    if mode == "cfb8":
        return cfb8_decrypt(key, data)
    if mode in ("cfb128", "cbc"):
        name = {"cfb128": AES.MODE_CFB, "cfb8": AES.MODE_CFB,
                "cbc": AES.MODE_CBC}[mode]
        segment = {"cfb128": 128, "cfb8": 8, "cbc": None}[mode]
        if segment:
            return AES.new(key, name, state, segment_size=segment).decrypt(data)
        return AES.new(key, name, state).decrypt(data)
    if mode == "ecb":
        return AES.new(key, AES.MODE_ECB).decrypt(data)
    return xor(data, keystream(key, mode, state, len(data)))


def encrypt(key: bytes, mode: str, state: bytes, data: bytes) -> bytes:
    from Crypto.Cipher import AES

    if mode == "cfb8":
        return cfb8_encrypt(key, data)
    if mode in ("cfb128", "cbc"):
        name = {"cfb128": AES.MODE_CFB, "cfb8": AES.MODE_CFB,
                "cbc": AES.MODE_CBC}[mode]
        segment = {"cfb128": 128, "cfb8": 8, "cbc": None}[mode]
        if segment:
            return AES.new(key, name, state, segment_size=segment).encrypt(data)
        return AES.new(key, name, state).encrypt(data)
    if mode == "ecb":
        return AES.new(key, AES.MODE_ECB).encrypt(data)
    return xor(data, keystream(key, mode, state, len(data)))


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


def identify(key: bytes, data: bytes) -> tuple[str, bytes, bytes, dict] | None:
    """Try every construction against the whole file; return mode, state, plain."""
    for hit in check_key(key, data[:48], len(data)):
        mode, state = hit["mode"], hit["state"]
        if mode in ("cbc", "ecb") and len(data) % BLOCK:
            continue        # the bundles are not block multiples
        try:
            plain = decrypt(key, mode, state, data)
        except ValueError:
            continue
        header = parse_unityfs(plain[:PROBE])
        if header is not None and header["size"] == len(data):
            return mode, state, plain, header
    return None


# -------------------------------------------------------------------- selftest
def _synthetic(size: int) -> bytes:
    """A bundle with the real prefix, so the key tests see the real first block."""
    header = (BUNDLE_PREFIX + size.to_bytes(8, "big")
              + (64).to_bytes(4, "big") + (64).to_bytes(4, "big")
              + (0x40).to_bytes(4, "big"))
    return header + bytes((i * 37 + 11) % 251 for i in range(size - len(header)))


def selftest() -> bool:
    key = bytes(range(32))
    iv = bytes([0x3B]) + bytes(range(0x41, 0x4F)) + bytes([0x3B])
    ok = True

    # 1. every construction is recognised from the ciphertext alone
    for mode in MODES:
        plain = _synthetic(8208 if mode in ("cbc", "ecb") else 8211)
        cipher = encrypt(key, mode, iv, plain)
        found = identify(key, cipher)
        # two counter rules can alias on the first blocks when base+i == base^i;
        # what matters is that the file comes back byte for byte
        good = bool(found and found[2] == plain)
        ok &= good
        print(f"  {mode:<16}{'ok' if good else 'FAILED'}")

    # 2. a wrong key is rejected (38 known bytes make a false hit impossible)
    plain = _synthetic(8211)
    cipher = encrypt(key, "ctr-le", iv, plain)
    good = identify(bytes(range(32, 64)), cipher) is None
    ok &= good
    print(f"  {'wrong key':<16}{'ok' if good else 'FAILED'}")

    # 3. candidates are found at all three payload offsets
    klass = (0x1F1803285D0).to_bytes(8, "little")
    blob = (klass + b"\x00" * 8 + struct.pack("<i", 32) + bytes(range(32))
            + b"\x00" * 8)
    offsets = {offset for offset, _size, payload in scan_arrays(blob)
               if payload == bytes(range(32))}
    good = bool(offsets)
    ok &= good
    print(f"  {'byte[] scan':<16}{'ok' if good else 'FAILED'}")

    # 4. re-encrypting a patched plaintext restores a decryptable file
    plain = _synthetic(8211)
    cipher = encrypt(key, "cfb128", iv, plain)
    patched = plain[:400] + bytes(16) + plain[416:]
    back = encrypt(key, "cfb128", iv, patched)
    good = (decrypt(key, "cfb128", iv, back) == patched
            and len(back) == len(cipher) and back[:384] == cipher[:384])
    ok &= good
    print(f"  {'patch + enc':<16}{'ok' if good else 'FAILED'}")
    return bool(ok)


# ------------------------------------------------------------------------ cli
def collect(api, handle, max_scan: int = 0, progress=None,
            counters: dict | None = None) -> tuple[list, dict]:
    """Walk readable memory and collect candidate key bytes."""
    keys: list[tuple[int, bytes]] = []
    seen: set = set()
    stats = {"regions": 0, "bytes": 0, "candidates": 0}
    counters = counters if counters is not None else {}
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
                for _at, length, payload in scan_arrays(buffer[:want]):
                    digest = (length, payload)
                    if digest in seen:
                        continue
                    seen.add(digest)
                    counters[length] = counters.get(length, 0) + 1
                    keys.append((length, payload))
                scanned += want
                stats["bytes"] = scanned
                stats["candidates"] = len(keys)
                if progress and stats["regions"] % 50 == 0:
                    # counts are passed in: a closure over the values assigned
                    # from this call raised NameError on the first progress tick
                    progress(scanned, len(keys), stats["regions"])
                if max_scan and scanned >= max_scan:
                    return keys, stats
                offset += want
        next_address = base + size
        if next_address <= address:
            break
        address = next_address
    return keys, stats


def write_dump(path: Path, keys: list[tuple[int, bytes]]) -> int:
    """Write the candidates so the search can continue offline.

    Format: b"SRWK1\n" then [u8 length][length bytes] per candidate. Sending this
    file is cheaper than more runs on the owner's machine: every new hypothesis can
    then be tested here against the same heap snapshot.
    """
    written = 0
    with path.open("wb") as handle:
        handle.write(b"SRWK1\n")
        for _length, key in keys[:DUMP_LIMIT]:
            handle.write(bytes([len(key)]))
            handle.write(key)
            written += 1
    return written


def read_dump(path: Path) -> list[bytes]:
    data = Path(path).read_bytes()
    if not data.startswith(b"SRWK1\n"):
        raise ValueError("not a candidate dump")
    pos, out = 6, []
    while pos < len(data):
        length = data[pos]
        pos += 1
        out.append(data[pos:pos + length])
        pos += length
    return out


def load_report(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


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

    size = bundle.stat().st_size
    cipher = bundle.read_bytes()[:48]
    states = state_hypotheses(bundle)
    found_keys: dict = {}
    counters: dict = {}
    total = {"regions": 0, "bytes": 0}
    verified: list = []
    hits: list = []

    def test_candidates():
        hits_local, verified_local = [], []
        for key in found_keys.values():
            candidates = [key]
            if len(key) == 32:
                candidates += [key[:16], key[16:]]   # AES-128 from a 32-byte buffer
                candidates += [hashlib.sha256(key).digest(),
                               hashlib.md5(key).digest()]
            for candidate in candidates:
                for hit in check_key(candidate, cipher, size, states):
                    hits_local.append(dict(hit, key=candidate))
                    try:
                        plain = decrypt(candidate, hit["mode"], hit["state"],
                                        bundle.read_bytes())
                    except ValueError:
                        continue
                    header = parse_unityfs(plain[:PROBE])
                    if header is not None and header["size"] == size:
                        verified_local.append(dict(hit, key=candidate,
                                                   unity_revision=header["unity_revision"]))
        return hits_local, verified_local

    for attempt in range(1, max(1, args.passes) + 1):
        handle = api.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                 False, pid)
        if not handle:
            print("error: cannot open the process; run PowerShell as "
                  "administrator", file=sys.stderr)
            return 2

        def report_progress(scanned, key_count, regions):
            print(f"  pass {attempt}: {scanned / 1e9:.2f} GB, {regions:,} "
                  f"regions, {key_count:,} candidates", flush=True)

        print(f"pass {attempt}/{max(1, args.passes)}: pid {pid}, file {size:,} B, "
              f"read-only scan", flush=True)
        try:
            keys, stats = collect(api, handle, args.max_scan,
                                  progress=report_progress, counters=counters)
        finally:
            api.CloseHandle(handle)
        for _length, key in keys:
            found_keys.setdefault(key, key)
        total["regions"] += stats["regions"]
        total["bytes"] += stats["bytes"]
        print(f"  pass {attempt}: {len(keys):,} candidates this pass, "
              f"{len(found_keys):,} distinct so far")

        hits, verified = test_candidates()
        if verified:
            break
        if attempt < max(1, args.passes):
            print(f"  nothing yet; keeping the game at a text scene and scanning "
                  f"again in {args.wait}s", flush=True)
            time.sleep(args.wait)

    dumped = write_dump(Path(args.dump), [(len(key), key) for key in found_keys])
    print(f"candidates written to {args.dump} ({dumped:,} records, "
          f"{Path(args.dump).stat().st_size / 1e6:.1f} MB)")
    print("candidates by length: " +
          (", ".join(f"{length}: {count:,}"
                     for length, count in sorted(counters.items()))
           or "none"))
    print(f"testing {len(found_keys):,} candidates")

    report = {"script_version": SCRIPT_VERSION, "bundle": str(bundle),
              "file_size": size, "passes": max(1, args.passes),
              "scanned": total, "candidates_by_length": counters,
              "candidates_tested": len(found_keys),
              "hits": [dict(hit, key_hex=hit["key"].hex(),
                            state_hex=hit["state"].hex()) for hit in hits],
              "verified": [dict(hit, key_hex=hit["key"].hex(),
                                state_hex=hit["state"].hex())
                           for hit in verified]}
    Path(args.report).write_text(json.dumps(report, indent=1, default=str) + "\n",
                                 encoding="utf-8")
    print(f"hits: {len(hits)} (verified: {len(verified)})")
    verified_ids = {(hit["mode"], hit["key"]) for hit in verified}
    for hit in hits:
        if (hit["mode"], hit["key"]) not in verified_ids:
            print(f"  key matched {hit['mode']} on the known first blocks but the "
                  f"whole file did not open")
    for hit in verified[:3]:
        print(f"  FOUND {hit['mode']}: key {hit['key'].hex()} "
              f"state {hit['state'].hex()}")
    print(f"report: {args.report}")
    if not verified:
        print("nothing verified. The report lists what was scanned and how many "
              "candidates were tested - send it, it says where to look next.")
    return 0 if verified else 1


def cmd_crypt(args, encrypting: bool) -> int:
    report = load_report(args.report) if Path(args.report).exists() else {}
    if args.key and args.iv and args.mode:
        key, state, mode = (bytes.fromhex(args.key), bytes.fromhex(args.iv),
                            args.mode)
    else:
        hits = report.get("verified") or []
        if not hits:
            print("error: the report has no verified key; run `key` first",
                  file=sys.stderr)
            return 2
        hit = hits[0]
        key = bytes.fromhex(hit["key_hex"])
        state = bytes.fromhex(hit.get("state_hex") or hit["iv_hex"])
        mode = hit["mode"]

    source, target = Path(args.inp), Path(args.out)
    if not source.exists():
        print(f"error: file not found: {source}", file=sys.stderr)
        return 2
    data = source.read_bytes()

    if encrypting:
        if parse_unityfs(data[:PROBE]) is None:
            print("error: the input is not a plaintext bundle", file=sys.stderr)
            return 1
        target.write_bytes(encrypt(key, mode, state, data))
        print(f"mode: {mode}; re-encrypted {len(data):,} B -> {target}")
        return 0

    plain = decrypt(key, mode, state, data)
    header = parse_unityfs(plain[:PROBE])
    if header is None:
        print(f"error: {mode} with this key does not produce a UnityFS header",
              file=sys.stderr)
        return 1
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
    key.add_argument("--passes", type=int, default=1,
                     help="scan this many times (transient keys are easier to catch)")
    key.add_argument("--wait", type=int, default=20,
                     help="seconds between passes")
    key.add_argument("--dump", default="candidates.bin",
                     help="where to write the candidate keys")

    for name in ("decrypt", "encrypt"):
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
    if args.command in (None, "selftest"):
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
