#!/usr/bin/env python3
"""Test a matrix of key-derivation hypotheses against a known pair.

`SeekableAesStream` takes a `password` and a `salt`, and the class must be seekable,
which means the position-dependent state cannot come from earlier bytes - it has to
come from something the reader knows before reading: the bundle's own name, its hash,
or a constant. That narrows the search to a matrix:

    key = derivation(password, salt, iterations)   x   key length 16 / 32
    password in {literals, file name, catalogue fields, constants}
    salt     in {file name, file hash, catalogue fields, constants}

Each row is judged with two AES calls (see `keyhunt_pairs.aes_hit`): a wrong key
cannot pass, so there is no false-positive bookkeeping. One file is enough to reject a
row; a row that opens one file is retested on ten more before anything is claimed.

    python kdf_matrix.py --pairs local/pairs --plain local/owner_carve4 \\
        --literals literals.txt --catalog catalog.json --out matrix.json
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import keyhunt_pairs as K  # noqa: E402

SCRIPT_VERSION = "2026-10-26.13"

CONSTANTS = [
    b"", b"SUPER ROBOT WARS Y", b"SRWY", b"SRW", b"BBStudio", b"SRTeam",
    b"SeekableAesStream", b"AddressablesMainContentCatalog", b"salt", b"password",
    b"Bundle", b"AssetBundle", b"UnityFS", b"2022.3.44f1", b"StandaloneWindows64",
]
ITERATIONS = [1, 100, 1000, 10000]


def name_forms(stem: str, bundle_name: str | None) -> list[tuple[str, bytes]]:
    """Everything the reader already knows about a file, as bytes."""
    out: list[tuple[str, bytes]] = [("stem-ascii", stem.encode())]
    try:
        raw = bytes.fromhex(stem)
        out += [("stem-hex", raw), ("stem-hex-reversed", raw[::-1])]
    except ValueError:
        pass
    out += [
        ("md5(stem)", hashlib.md5(stem.encode()).digest()),
        ("sha1(stem)", hashlib.sha1(stem.encode()).digest()),
        ("sha256(stem)", hashlib.sha256(stem.encode()).digest()),
        ("md5(stem.bundle)", hashlib.md5((stem + ".bundle").encode()).digest()),
        ("sha256(stem.bundle)", hashlib.sha256((stem + ".bundle").encode()).digest()),
    ]
    if bundle_name:
        out += [("bundleName", bundle_name.encode()),
                ("md5(bundleName)", hashlib.md5(bundle_name.encode()).digest())]
    return out


def derivations(password: bytes, salt: bytes, iterations: int) -> list[tuple[str, bytes]]:
    rows = []
    for digest in ("sha1", "sha256"):
        try:
            raw = hashlib.pbkdf2_hmac(digest, password, salt or b"\x00", iterations, 32)
        except Exception:
            continue
        rows.append((f"pbkdf2-{digest}-{iterations}-32", raw))
        rows.append((f"pbkdf2-{digest}-{iterations}-16", raw[:16]))
    if iterations == 1:
        joined = password + salt
        rows += [("md5(pw+salt)", hashlib.md5(joined).digest()),
                 ("sha256(pw+salt)", hashlib.sha256(joined).digest()),
                 ("sha256(salt+pw)", hashlib.sha256(salt + password).digest()),
                 ("md5(salt+pw)", hashlib.md5(salt + password).digest())]
    return rows


def catalogue_fields(path: Path | None) -> dict[str, bytes]:
    if not path or not path.exists():
        return {}
    data = json.loads(Path(path).read_bytes())
    fields = {"locator_id": str(data.get("m_LocatorId", "")).encode(),
              "build_hash": str(data.get("m_BuildResultHash", "")).encode()}
    return {key: value for key, value in fields.items() if value}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pairs", default="local/pairs")
    parser.add_argument("--plain", default="local/owner_carve4")
    parser.add_argument("--literals")
    parser.add_argument("--max-literals", type=int, default=0)
    parser.add_argument("--catalog")
    parser.add_argument("--out", default="kdf_matrix.json")
    parser.add_argument("--password-source", choices=["literals", "names", "both"],
                        default="names",
                        help="which passwords to sweep (names = the cheap matrix)")
    args = parser.parse_args(argv)

    print(f"kdf_matrix {SCRIPT_VERSION}")
    pairs = K.load_pairs(Path(args.pairs), Path(args.plain))
    print(f"pairs: {len(pairs)}")
    if not pairs:
        return 2
    first = pairs[0]
    stem = first["name"].replace(".bundle", "")
    fields = catalogue_fields(Path(args.catalog) if args.catalog else None)

    names = name_forms(stem, None)
    password_sets: list[tuple[str, bytes]] = [(f"const:{c.decode('latin-1')}", c)
                                              for c in CONSTANTS]
    password_sets += [(f"field:{k}", v) for k, v in fields.items()]
    if args.password_source in ("names", "both"):
        password_sets += [(f"name:{label}", value) for label, value in names]
    if args.literals:
        literals = Path(args.literals).read_text(encoding="utf-8",
                                                 errors="ignore").splitlines()
        literals = [line for line in literals if 6 <= len(line) <= 64]
        if args.max_literals:
            literals = literals[:args.max_literals]
        print(f"literals as passwords: {len(literals):,}")
        password_sets += [(f"lit:{text}", text.encode("utf-8", "ignore"))
                          for text in literals]

    salt_sets: list[tuple[str, bytes]] = [(f"const:{c.decode('latin-1')}", c)
                                          for c in CONSTANTS]
    salt_sets += [(f"field:{k}", v) for k, v in fields.items()]
    salt_sets += [(f"name:{label}", value) for label, value in names]

    started = time.time()
    tried = 0
    for (pw_label, password), (salt_label, salt) in itertools.product(password_sets,
                                                                      salt_sets):
        if password == salt and pw_label == salt_label:
            pass
        for iterations in ITERATIONS:
            for label, key in derivations(password, salt, iterations):
                tried += 1
                hit = K.test_key(key, first["keystream"], ("aes", "rc4"))
                if not hit:
                    continue
                print(f"HIT {label} {hit}: {pw_label} / {salt_label}")
                opened = []
                for row in pairs[:12]:
                    found = K.test_key(key, row["keystream"], ("aes", "rc4"))
                    if found:
                        opened.append((row["name"], found))
                print(f"  opens {len(opened)}/12: {opened[:4]}")
                Path(args.out).write_text(json.dumps(
                    {"script_version": SCRIPT_VERSION, "derivation": label,
                     "cipher": hit, "password": pw_label, "salt": salt_label,
                     "key_hex": key.hex(), "opens": opened}, indent=1) + "\n",
                    encoding="utf-8")
                return 0
            if tried % 2000 == 0:
                print(f"  {tried:,} derivations, {time.time() - started:.0f}s",
                      flush=True)

    print(f"no hit after {tried:,} derivations in {time.time() - started:.0f}s")
    Path(args.out).write_text(json.dumps(
        {"script_version": SCRIPT_VERSION, "tried": tried, "hits": []},
        indent=1) + "\n", encoding="utf-8")
    return 1


if __name__ == "__main__":
    sys.exit(main())
