#!/usr/bin/env python3
"""Try to identify the cipher protecting SRW Y's asset bundles.

Why this exists: the `.bundle` files under `StreamingAssets/aa/StandaloneWindows64`
carry **no `UnityFS` header at all** — every byte is high entropy and no 16-byte
block repeats, so the whole file is encrypted with a per-file keystream (see
`docs/S2_FINDINGS.md`). The catalogue is useless until that is undone, because
nothing else describes what is inside those files.

What it does: takes a blob of *candidate key material* (for SRW Y that is
`global-metadata.dat`, which holds the managed **string literals**), pulls out
every printable string of an AES key size and every hex run that decodes to one,
then tries a small set of stock constructions against the first block of a real
bundle, looking for the `UnityFS` signature. A hit is proof, not a guess.

Nothing is brute-forced beyond literal extraction: if this finds nothing, the key
is a byte array compiled into `GameAssembly.dll` or derived at runtime, and the
answer is a runtime dump instead (see `docs/FEASIBILITY.md`).

The AES here is a plain implementation with no dependencies, so the tool runs in
the same place the tests run. It is checked against the FIPS-197 vectors in
`tests/test_keyhunt.py`; it is not constant-time and must never be used for
anything but this analysis.

Usage:
    python3 tools/keyhunt.py --bundle local/bundles/x.bundle --candidates global-metadata.dat
    python3 tools/keyhunt.py --bundle a.bundle b.bundle --candidates meta.dat \
        --list-words wordlist.txt --limit 200000

Exit codes: 0 always (a hunt that finds nothing is a result, not an error), 2 on
bad input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = 1
SIGNATURE = b"UnityFS"
KEY_SIZES = (16, 24, 32)
HEX_RUN = re.compile(rb"\b[0-9a-fA-F]{32,64}\b")
PRINTABLE = re.compile(rb"[\x20-\x7e]{16,64}")
STRING_RUN = re.compile(rb"[\x20-\x7e]{4,}")
SCAN_WINDOW = 512

# ---------------------------------------------------------------- AES (FIPS-197)


def _build_sbox() -> tuple[list[int], list[int]]:
    sbox = [0] * 256
    inv = [0] * 256
    p = q = 1
    while True:
        # multiply p by 3, divide q by 3 in GF(2^8)
        p = p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)
        q ^= q << 1
        q ^= q << 2
        q ^= q << 4
        q &= 0xFF
        if q & 0x80:
            q ^= 0x09
        x = q ^ ((q << 1) | (q >> 7)) ^ ((q << 2) | (q >> 6)) ^ ((q << 3) | (q >> 5)) ^ ((q << 4) | (q >> 4))
        sbox[p] = (x ^ 0x63) & 0xFF
        inv[sbox[p]] = p
        if p == 1:
            break
    sbox[0] = 0x63
    inv[0x63] = 0
    return sbox, inv


SBOX, INV_SBOX = _build_sbox()
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D]


def _xtime(a: int) -> int:
    a <<= 1
    return (a ^ 0x1B) & 0xFF if a & 0x100 else a


def _mul(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        b >>= 1
        a = _xtime(a)
    return result


def expand_key(key: bytes) -> list[list[int]]:
    nk = len(key) // 4
    if len(key) not in KEY_SIZES:
        raise ValueError("key must be 16, 24 or 32 bytes")
    words = [list(key[i * 4:i * 4 + 4]) for i in range(nk)]
    total = 4 * (nk + 7)
    for i in range(nk, total):
        temp = list(words[i - 1])
        if i % nk == 0:
            temp = temp[1:] + temp[:1]
            temp = [SBOX[b] for b in temp]
            temp[0] ^= RCON[i // nk - 1]
        elif nk > 6 and i % nk == 4:
            temp = [SBOX[b] for b in temp]
        words.append([a ^ b for a, b in zip(words[i - nk], temp)])
    return words


def _add_round_key(state: list[int], words: list[list[int]], round_index: int) -> None:
    for col in range(4):
        word = words[round_index * 4 + col]
        for row in range(4):
            state[col * 4 + row] ^= word[row]


def encrypt_block(key: bytes, block: bytes) -> bytes:
    words = expand_key(key)
    rounds = len(words) // 4 - 1
    state = list(block)
    _add_round_key(state, words, 0)
    for rnd in range(1, rounds + 1):
        state = [SBOX[b] for b in state]
        # ShiftRows (state is column-major: index = col*4 + row)
        state = [state[(col + row) % 4 * 4 + row] for col in range(4) for row in range(4)]
        if rnd != rounds:
            mixed = []
            for col in range(4):
                a = state[col * 4:col * 4 + 4]
                mixed += [
                    _mul(a[0], 2) ^ _mul(a[1], 3) ^ a[2] ^ a[3],
                    a[0] ^ _mul(a[1], 2) ^ _mul(a[2], 3) ^ a[3],
                    a[0] ^ a[1] ^ _mul(a[2], 2) ^ _mul(a[3], 3),
                    _mul(a[0], 3) ^ a[1] ^ a[2] ^ _mul(a[3], 2),
                ]
            state = mixed
        _add_round_key(state, words, rnd)
    return bytes(state)


def decrypt_block(key: bytes, block: bytes) -> bytes:
    words = expand_key(key)
    rounds = len(words) // 4 - 1
    state = list(block)
    _add_round_key(state, words, rounds)
    for rnd in range(rounds - 1, -1, -1):
        # InvShiftRows
        state = [state[(col - row) % 4 * 4 + row] for col in range(4) for row in range(4)]
        state = [INV_SBOX[b] for b in state]
        _add_round_key(state, words, rnd)
        if rnd != 0:
            unmixed = []
            for col in range(4):
                a = state[col * 4:col * 4 + 4]
                unmixed += [
                    _mul(a[0], 14) ^ _mul(a[1], 11) ^ _mul(a[2], 13) ^ _mul(a[3], 9),
                    _mul(a[0], 9) ^ _mul(a[1], 14) ^ _mul(a[2], 11) ^ _mul(a[3], 13),
                    _mul(a[0], 13) ^ _mul(a[1], 9) ^ _mul(a[2], 14) ^ _mul(a[3], 11),
                    _mul(a[0], 11) ^ _mul(a[1], 13) ^ _mul(a[2], 9) ^ _mul(a[3], 14),
                ]
            state = unmixed
    return bytes(state)


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _counter_block(value: int, little_endian: bool = False) -> bytes:
    return value.to_bytes(16, "little" if little_endian else "big")


# ------------------------------------------------------------------- candidates


def candidates_from_blob(blob: bytes, limit: int = 0) -> list[bytes]:
    """Every printable AES-size string and every hex run that decodes to one."""
    seen: set[bytes] = set()
    out: list[bytes] = []

    def add(value: bytes) -> None:
        if len(value) in KEY_SIZES and value not in seen:
            seen.add(value)
            out.append(value)

    for match in PRINTABLE.finditer(blob):
        run = match.group()
        for size in KEY_SIZES:
            for start in range(0, len(run) - size + 1):
                add(run[start:start + size])
        if limit and len(out) >= limit:
            return out
    for match in HEX_RUN.finditer(blob):
        run = match.group()
        if len(run) % 2 == 0:
            try:
                add(bytes.fromhex(run.decode("ascii")))
            except ValueError:
                pass
    return out


def candidates_from_words(text: str) -> list[bytes]:
    out = []
    for line in text.splitlines():
        word = line.strip()
        if not word:
            continue
        raw = word.encode("utf-8", "ignore")
        if len(raw) in KEY_SIZES:
            out.append(raw)
    return out


# ---------------------------------------------------------------------- schemes


def _decrypt_variants(key: bytes, data: bytes) -> dict[str, bytes]:
    """Stock constructions, each returning the bytes expected at offset 0."""
    block = data[:16]
    if len(block) < 16:
        return {}
    variants = {
        "aes-ecb": decrypt_block(key, block),
        "aes-cbc-iv0": _xor(decrypt_block(key, block), bytes(16)),
        "aes-ctr-0": _xor(encrypt_block(key, _counter_block(0)), block),
        "aes-ctr-1": _xor(encrypt_block(key, _counter_block(1)), block),
        "aes-ctr-0-le": _xor(encrypt_block(key, _counter_block(0, True)), block),
        "xor-repeat": _xor(block, (key * 2)[:16]),
    }
    if len(data) >= 32:
        iv = data[:16]
        variants["aes-cbc-iv-prefix"] = _xor(decrypt_block(key, data[16:32]), iv)
        variants["aes-ctr-iv-prefix"] = _xor(encrypt_block(key, iv), data[16:32])
        variants["aes-ctr-iv-prefix-1"] = _xor(
            encrypt_block(key, _xor(iv, _counter_block(1))), data[16:32])
    return variants


def matches(key: bytes, data: bytes) -> list[str]:
    """Scheme names whose output starts with the UnityFS signature."""
    hits = []
    for name, plain in _decrypt_variants(key, data).items():
        if plain.startswith(SIGNATURE):
            hits.append(name)
            continue
        # a 16-byte encrypted header would push the signature right
        if SIGNATURE in plain[:SCAN_WINDOW]:
            hits.append(name + "+offset")
    return hits


def hunt(bundles: list[Path], keys: list[bytes], verbose: bool = False) -> dict:
    samples = []
    for bundle in bundles:
        if not bundle.is_file():
            raise ValueError(f"not a file: {bundle}")
        samples.append((bundle.name, bundle.read_bytes()[:SCAN_WINDOW]))
    found = []
    keys = [key for key in keys if len(key) in KEY_SIZES]
    for index, key in enumerate(keys):
        if verbose and index % 5000 == 0:
            print(f"  tried {index}/{len(keys)} keys", file=sys.stderr)
        for name, data in samples:
            schemes = matches(key, data)
            if schemes:
                found.append({"key_hex": key.hex(), "key_repr": _readable(key),
                              "bundle": name, "schemes": schemes})
    return {
        "schema": SCHEMA,
        "bundles": [path.name for path in bundles],
        "candidates_tried": len(keys),
        "found": found,
    }


def _readable(key: bytes) -> str:
    try:
        text = key.decode("ascii")
    except UnicodeDecodeError:
        return key.hex()
    return text if text.isprintable() else key.hex()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bundle", required=True, nargs="+", type=Path)
    parser.add_argument("--candidates", type=Path, nargs="*", default=[],
                        help="blobs to mine for key material (e.g. global-metadata.dat)")
    parser.add_argument("--list-words", type=Path, action="append", default=[],
                        help="word list, one candidate key per line")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    keys: list[bytes] = []
    for source in args.candidates:
        if not source.is_file():
            print(f"error: not a file: {source}", file=sys.stderr)
            return 2
        keys += candidates_from_blob(source.read_bytes(), args.limit)
    for wordlist in args.list_words:
        keys += candidates_from_words(wordlist.read_text(encoding="utf-8", errors="replace"))
    keys = list(dict.fromkeys(keys))
    if args.limit:
        keys = keys[:args.limit]
    if not keys:
        print("error: no candidate keys — pass --candidates or --list-words", file=sys.stderr)
        return 2

    try:
        result = hunt(args.bundle, keys, args.verbose)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"candidates tried : {result['candidates_tried']:,}")
    print(f"bundles          : {', '.join(result['bundles'])}")
    if result["found"]:
        for hit in result["found"]:
            print(f"MATCH  {hit['key_repr']}  ({hit['schemes']}) on {hit['bundle']}")
    else:
        print("no match — the key is not a literal string of an AES key size")
    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(f"report written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
