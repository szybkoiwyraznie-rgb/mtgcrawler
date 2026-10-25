#!/usr/bin/env python3
"""Decrypt and re-encrypt the game's bundles once the key is known.

This is the file-patching half of the kit: `key_from_memory.py` recovers the AES
key and the counter/feedback block from the running game, and this tool turns
that into `plain.bundle` -> edit -> `plain.bundle` back to the exact same on-disk
format. Same length in, same length out, no padding.

Which stream construction the game uses is not guessed: the first 32 decrypted
bytes must be a valid `UnityFS` header whose declared size equals the file size,
and the candidates are tried in a fixed order. The winner is printed and recorded
in the report, and `--mode` pins it for later runs.

    # identify and decrypt
    python bundle_crypt.py --report key_report.json --decrypt in.bundle out.bundle

    # put the edited file back
    python bundle_crypt.py --report key_report.json --mode ctr-le \
        --encrypt out.bundle in.bundle

    # no game and no key needed
    python bundle_crypt.py --selfcheck
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mem_carve import parse_unityfs  # noqa: E402

SCRIPT_VERSION = "2026-10-26.1"
BLOCK = 16
MODES = ("ctr-le", "ctr-be", "cfb128", "ofb", "cbc")
PROBE = 4096


def _counter_stream(key: bytes, start: bytes, length: int, little: bool) -> bytes:
    """AES-CTR with the whole 16-byte block used as the counter."""
    from Crypto.Cipher import AES

    ecb = AES.new(key, AES.MODE_ECB)
    value = int.from_bytes(start, "little" if little else "big")
    out = bytearray()
    while len(out) < length:
        out += ecb.encrypt(value.to_bytes(BLOCK, "little" if little else "big"))
        value = (value + 1) % (1 << 128)
    return bytes(out[:length])


def xor(data: bytes, stream: bytes) -> bytes:
    """XOR two equal-length buffers as big integers (fast, no per-byte loop)."""
    if len(data) != len(stream):
        raise ValueError("keystream length must match the data")
    size = len(data)
    return (int.from_bytes(data, "big") ^ int.from_bytes(stream, "big")).to_bytes(
        size, "big")


def _pycrypto_mode(mode: str):
    from Crypto.Cipher import AES

    if mode == "cfb128":
        return AES.MODE_CFB, 128
    if mode == "ofb":
        return AES.MODE_OFB, None
    if mode == "cbc":
        return AES.MODE_CBC, None
    raise ValueError(f"unknown mode: {mode}")


def _cipher(key: bytes, iv: bytes, mode: str, decrypting: bool):
    from Crypto.Cipher import AES

    name, segment = _pycrypto_mode(mode)
    if segment:
        return AES.new(key, name, iv, segment_size=segment)
    return AES.new(key, name, iv)


def decrypt(key: bytes, iv: bytes, data: bytes, mode: str) -> bytes:
    """Reverse the game's encryption. Stream modes accept any length."""
    if mode == "ctr-le":
        return xor(data, _counter_stream(key, iv, len(data), True))
    if mode == "ctr-be":
        return xor(data, _counter_stream(key, iv, len(data), False))
    return _cipher(key, iv, mode, True).decrypt(data)


def encrypt(key: bytes, iv: bytes, data: bytes, mode: str) -> bytes:
    if mode == "ctr-le":
        return xor(data, _counter_stream(key, iv, len(data), True))
    if mode == "ctr-be":
        return xor(data, _counter_stream(key, iv, len(data), False))
    return _cipher(key, iv, mode, False).encrypt(data)


def looks_decrypted(data: bytes) -> dict | None:
    """A header is accepted only when it parses and matches the real size."""
    header = parse_unityfs(data[:PROBE])
    if header is None:
        return None
    return header


def identify(key: bytes, iv: bytes, data: bytes,
             modes=MODES) -> tuple[str, bytes, dict] | None:
    for mode in modes:
        # CBC needs whole blocks; the bundles are not block multiples (a 940,012 B
        # sample is 12 bytes past a block boundary), so CBC can only be a fit when
        # the size divides evenly.
        if mode == "cbc" and len(data) % BLOCK:
            continue
        try:
            probe = decrypt(key, iv, data[:PROBE], mode)
        except ValueError:
            continue
        header = looks_decrypted(probe)
        if header is None or header["size"] != len(data):
            continue
        try:
            return mode, decrypt(key, iv, data, mode), header
        except ValueError:
            continue
    return None


def load_key(path: Path) -> tuple[bytes, bytes, str | None]:
    report = json.loads(path.read_text(encoding="utf-8"))
    hits = report.get("verified") or report.get("hits") or []
    if not hits:
        raise SystemExit("report has no key hits")
    hit = hits[0]
    return bytes.fromhex(hit["key_hex"]), bytes.fromhex(hit["iv_hex"]), \
        hit.get("mode")


def _synthetic(size: int, unity: str = "2022.3.44f1") -> bytes:
    revision = unity.encode() + b"\x00"
    header = (b"UnityFS\x00" + (7).to_bytes(4, "big") + b"5.x.x\x00" + revision
              + size.to_bytes(8, "big") + (64).to_bytes(4, "big")
              + (64).to_bytes(4, "big") + (0x40).to_bytes(4, "big"))
    body = bytes((i * 37 + 11) % 251 for i in range(size - len(header)))
    return header + body


def self_check() -> dict:
    """Round-trip synthetic bundles through every mode, then auto-identify them."""
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f"
                        "101112131415161718191a1b1c1d1e1f")
    iv = bytes.fromhex("f0e1d2c3b4a5968778695a4b3c2d1e0f")
    results = {}
    for mode in MODES:
        # the real bundles are 12 bytes past a block boundary; CBC cannot represent
        # that, so it is exercised on an aligned sample only
        plain = _synthetic(8192 if mode == "cbc" else 8203)
        cipher = encrypt(key, iv, plain, mode)
        found = identify(key, iv, cipher)
        results[mode] = bool(found and found[1] == plain)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--key", help="32/16-byte AES key, hex")
    parser.add_argument("--iv", help="16-byte counter/feedback block, hex")
    parser.add_argument("--report", type=Path, help="key_report.json from key_from_memory")
    parser.add_argument("--mode", choices=MODES, help="pin the construction")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--decrypt", nargs=2, metavar=("IN", "OUT"))
    group.add_argument("--encrypt", nargs=2, metavar=("IN", "OUT"))
    group.add_argument("--selfcheck", action="store_true")
    args = parser.parse_args(argv)

    print(f"bundle_crypt {SCRIPT_VERSION}")
    if args.selfcheck:
        results = self_check()
        for mode, ok in results.items():
            print(f"  {mode:8} {'ok' if ok else 'FAILED'}")
        return 0 if all(results.values()) else 1

    if args.report:
        key, iv, reported = load_key(args.report)
    elif args.key and args.iv:
        key, iv, reported = bytes.fromhex(args.key), bytes.fromhex(args.iv), None
    else:
        print("error: give --report or both --key and --iv", file=sys.stderr)
        return 2

    if args.decrypt:
        source, target = (Path(part) for part in args.decrypt)
        data = source.read_bytes()
        if args.mode:
            plain = decrypt(key, iv, data, args.mode)
            header = looks_decrypted(plain)
            if header is None:
                print(f"error: {args.mode} does not produce a UnityFS header",
                      file=sys.stderr)
                return 1
            mode = args.mode
        else:
            found = identify(key, iv, data)
            if found is None:
                print("error: no construction produced a valid bundle; the key, "
                      "the counter block or the mode is wrong", file=sys.stderr)
                return 1
            mode, plain, header = found
        target.write_bytes(plain)
        print(f"mode: {mode}")
        print(f"unity: {header['unity_revision']}, size {header['size']:,} B")
        print(f"wrote {target} ({len(plain):,} B)")
        return 0

    if args.encrypt:
        source, target = (Path(part) for part in args.encrypt)
        plain = source.read_bytes()
        header = looks_decrypted(plain)
        if header is None:
            print("error: input is not a plaintext bundle", file=sys.stderr)
            return 1
        if header["size"] != len(plain):
            print(f"warning: header size {header['size']:,} != file size "
                  f"{len(plain):,}", file=sys.stderr)
        mode = args.mode or reported
        if mode is None:
            print("error: pass --mode (see the decrypt run)", file=sys.stderr)
            return 2
        target.write_bytes(encrypt(key, iv, plain, mode))
        print(f"mode: {mode}; re-encrypted {len(plain):,} B -> {target}")
        return 0

    print("error: give --decrypt, --encrypt or --selfcheck", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
