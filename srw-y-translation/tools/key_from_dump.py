#!/usr/bin/env python3
"""Offline analysis of a candidate dump - no game, no owner needed.

`key --dump candidates.bin` writes every 16/24/32-byte heap array the scanner saw.
This script takes that snapshot plus one encrypted bundle and grinds through the
hypotheses that would otherwise each cost the owner another run:

1. every construction in `srw_y_key.check_key` (ten counter rules, OFB, CFB-128,
   CFB-8, CBC, ECB), for each candidate and for its 16-byte halves;
2. the recovered state `AES-decrypt(key, ciphertext0 xor plaintext0)` against
   values it could plausibly equal: the file name turned into 16 bytes, its hashes,
   all zeros, or any 16-byte window inside `GameAssembly.dll` and
   `global-metadata.dat` - a hit there says the key is right even if the advance
   rule is one nobody guessed, because the IV turned out to be a constant;
3. simple structure in the state (a 12-byte nonce with a 32-bit counter, an
   all-zero tail).

    python key_from_dump.py candidates.bin 1cc7e02e....bundle \
        --dll GameAssembly.dll --metadata global-metadata.dat --out dump_report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import srw_y_key as S  # noqa: E402

SCRIPT_VERSION = "2026-10-26.8"


def states_from_name(stem: str) -> dict:
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
    out[b"\x00" * S.BLOCK] = "zeros"
    out[b"\xff" * S.BLOCK] = "ones"
    return out


def state_shape(state: bytes) -> str | None:
    if state[:12] == b"\x00" * 12:
        return "nonce12-zero"
    if state[12:] == b"\x00" * 4:
        return "counter32-zero"
    if state[:7] == b"\x00" * 7:
        return "counter32-be-zero"
    return None


def scan_constants(paths, targets: set) -> list[dict]:
    """Find 16-byte windows in these files that equal one of `targets`."""
    hits = []
    for path in paths:
        if not path or not Path(path).exists():
            continue
        data = Path(path).read_bytes()
        window = None
        for offset in range(0, len(data) - S.BLOCK):
            window = data[offset:offset + S.BLOCK]
            if window in targets:
                hits.append({"file": str(path), "offset": offset,
                             "state_hex": window.hex()})
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dump", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--dll", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path, default=Path("dump_report.json"))
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args(argv)

    print(f"key_from_dump {SCRIPT_VERSION}")
    data = args.bundle.read_bytes()
    size = len(data)
    cipher = data[:48]
    known = S.known_plain(size)
    states = states_from_name(args.bundle.stem)
    keys = S.read_dump(args.dump)
    if args.limit:
        keys = keys[:args.limit]
    print(f"{len(keys):,} candidates, bundle {size:,} B")

    from Crypto.Cipher import AES

    hits, shapes, state_to_key = [], {}, {}
    for index, key in enumerate(keys):
        forms = [key]
        if len(key) == 32:
            forms += [key[:16], key[16:], hashlib.sha256(key).digest(),
                      hashlib.md5(key).digest()]
        for form in forms:
            for hit in S.check_key(form, cipher, size, states, known):
                hits.append({"mode": hit["mode"], "key_hex": form.hex(),
                             "state_hex": hit["state"].hex(),
                             "origin": key.hex()})
            same = (int.from_bytes(cipher[0:S.BLOCK], "big")
                    ^ int.from_bytes(known[0:S.BLOCK], "big")).to_bytes(
                S.BLOCK, "big")
            state = AES.new(form, AES.MODE_ECB).decrypt(same)
            label = state_shape(state)
            if label:
                shapes[label] = shapes.get(label, 0) + 1
            state_to_key.setdefault(state, (form, key))
        if index and index % 50000 == 0:
            print(f"  {index:,} candidates, {len(hits)} hits", flush=True)

    print(f"hits from known constructions: {len(hits)}")
    for hit in hits[:10]:
        print(f"  {hit['mode']}: key {hit['key_hex']} state {hit['state_hex']}")

    constant_hits = scan_constants([args.dll, args.metadata], set(state_to_key))
    print(f"states found as 16-byte constants in DLL/metadata: {len(constant_hits)}")
    for hit in constant_hits[:10]:
        form, origin = state_to_key[bytes.fromhex(hit["state_hex"])]
        print(f"  {hit['file']} +{hit['offset']:#x}: state {hit['state_hex']} "
              f"key {form.hex()}")

    report = {"script_version": SCRIPT_VERSION, "bundle": str(args.bundle),
              "candidates": len(keys), "hits": hits,
              "state_shapes": shapes, "constant_hits": constant_hits}
    args.out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"report: {args.out}")
    return 0 if (hits or constant_hits) else 1


if __name__ == "__main__":
    sys.exit(main())
