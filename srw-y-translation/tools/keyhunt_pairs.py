#!/usr/bin/env python3
"""Hunt the bundle key with the 276 plaintext/ciphertext pairs as an oracle.

Why this exists: a keystream is only useful for patching one file at a time, and the
text of the game sits in files nobody has carved. What is actually needed is the key,
so that any bundle can be decrypted and re-encrypted statically - no game running, no
memory carving.

The pairs make that hunt cheap and honest. For a paired file

    keystream = ciphertext XOR plaintext

and for a counter-like cipher `keystream[i] = E(key, state + i)`. So a candidate key
can be judged with two AES calls: decrypt `keystream[0]` to get `state`, then check
that encrypting the next counter value gives `keystream[16:32]`. No IV from memory is
needed, and a wrong candidate cannot pass (32 bytes of coincidence).

Candidates come from where a password or salt would hide: the string literals of the
IL2CPP metadata and of the binary. Each string is tried as

* a key directly (16/24/32 bytes), and hex-decoded, and hashed (MD5/SHA-1/SHA-256),
* and as a `Rfc2898DeriveBytes` password with a salt from a small candidate list
  (the string itself, the bundle hash from the catalogue, the bundle name, constants).

Three ciphers are tested: AES in counter/OFB/CFB/CBC/ECB forms, RC4 and ChaCha20 - the
metadata names `Rijndael`, `AesManaged`, `CryptoStream` and `Rfc2898`, so AES is likely,
but a wrong guess about the cipher must not produce a false "no".

    python keyhunt_pairs.py strings --from global-metadata.dat --out literals.txt
    python keyhunt_pairs.py hunt --pairs pairs/ --plain local/owner_carve4 \\
        --literals literals.txt --files 3
    python keyhunt_pairs.py hunt --pairs pairs/ --plain local/owner_carve4 \\
        --literals literals.txt --pbkdf2 --salt-from-catalog catalog.json
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
import time
from pathlib import Path

SCRIPT_VERSION = "2026-10-26.13"
PROBE = 48


# ------------------------------------------------------------------------ candidates
def strings_from(blob: bytes, minimum: int = 4, maximum: int = 96) -> list[str]:
    """Printable ASCII runs, plus UTF-16LE runs (the metadata mixes both)."""
    out = set()
    for match in re.finditer(rb"[\x20-\x7e]{%d,%d}" % (minimum, maximum), blob):
        out.add(match.group().decode("ascii"))
    wide = rb"(?:[\x20-\x7e]\x00){%d,%d}" % (minimum, maximum)
    for match in re.finditer(wide, blob):
        out.add(match.group().decode("utf-16-le"))
    return sorted(out)


def key_forms(text: str) -> list[tuple[str, bytes]]:
    """Ways a literal becomes an AES key."""
    forms: list[tuple[str, bytes]] = []
    raw = text.encode("utf-8", "ignore")
    if len(raw) in (16, 24, 32):
        forms.append(("raw", raw))
    if len(raw) > 32:
        forms.append(("raw-trunc", raw[:32]))
    if re.fullmatch(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{48}|[0-9a-fA-F]{64}", text):
        try:
            forms.append(("hex", bytes.fromhex(text)))
        except ValueError:
            pass
    forms.append(("md5", hashlib.md5(raw).digest()))
    forms.append(("sha1-16", hashlib.sha1(raw).digest()[:16]))
    forms.append(("sha256", hashlib.sha256(raw).digest()))
    try:
        decoded = base64.b64decode(text, validate=True)
        if len(decoded) in (16, 24, 32):
            forms.append(("base64", decoded))
    except Exception:
        pass
    seen, out = set(), []
    for label, key in forms:
        if len(key) in (16, 24, 32) and key not in seen:
            seen.add(key)
            out.append((label, key))
    return out


# ---------------------------------------------------------------------------- pairs
def load_pairs(pairs_dir: Path, plain_dir: Path) -> list[dict]:
    """Every bundle with a carved plaintext and one file of the same size on disk."""
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
        plain = next(iter(plains.values()))
        out.append({"name": path.name, "size": len(cipher),
                    "plain": plain[:PROBE], "cipher": cipher[:PROBE],
                    "keystream": bytes(a ^ b for a, b in
                                       zip(plain[:PROBE], cipher[:PROBE]))})
    return out


# --------------------------------------------------------------------------- oracle
def aes_hit(key: bytes, keystream: bytes) -> str | None:
    """Which AES construction turns this keystream? Two calls for the common case."""
    from Crypto.Cipher import AES

    if len(key) not in (16, 24, 32) or len(keystream) < 32:
        return None
    ecb = AES.new(key, AES.MODE_ECB)
    state = ecb.decrypt(keystream[0:16])
    want1 = keystream[16:32]
    for label, offset in (("ctr-le", 1), ("ctr-be", 1)):
        counter = (int.from_bytes(state, "little" if label.endswith("le") else "big")
                   + offset)
        block = counter.to_bytes(16, "little" if label.endswith("le") else "big")
        if ecb.encrypt(block) == want1:
            return label
    # 32-bit counter in the last four bytes
    for order in ("little", "big"):
        tail = (int.from_bytes(state[12:16], order) + 1) % (1 << 32)
        if ecb.encrypt(state[:12] + tail.to_bytes(4, order)) == want1:
            return "ctr32-" + ("le" if order == "little" else "be")
    # OFB: the next keystream block is E(previous keystream block)
    if ecb.encrypt(keystream[0:16]) == want1:
        return "ofb"
    # ECB on the plaintext blocks: keystream is not needed, check the file instead
    if ecb.decrypt(keystream[16:32]) == b"\x00" * 16:
        return "ecb-zero"
    # CFB/CBC style: keystream[16:32] = E(ciphertext block 0) XOR plaintext block 1
    if ecb.encrypt(keystream[0:16]) == want1:
        return "cfb-like"
    return None


def rc4_hit(key: bytes, keystream: bytes) -> str | None:
    try:
        from Crypto.Cipher import ARC4
    except ImportError:
        return None
    stream = ARC4.new(key).encrypt(b"\x00" * len(keystream))
    return "rc4" if stream[:len(keystream)] == keystream[:len(keystream)] else None


def chacha_hit(key: bytes, keystream: bytes) -> str | None:
    if len(key) != 32:
        return None
    try:
        from Crypto.Cipher import ChaCha20
    except ImportError:
        return None
    for nonce in (b"\x00" * 8, b"\x00" * 12):
        try:
            stream = ChaCha20.new(key=key, nonce=nonce).encrypt(b"\x00" * 32)
        except Exception:
            continue
        if stream == keystream[:32]:
            return "chacha20-" + str(len(nonce))
    return None


def test_key(key: bytes, keystream: bytes, ciphers=("aes", "rc4", "chacha")) -> str | None:
    """Fast filter: is this key right for this file, and under which cipher?"""
    if len(key) < 5:
        return None
    if "aes" in ciphers:
        hit = aes_hit(key, keystream)
        if hit:
            return hit
    if "rc4" in ciphers:
        hit = rc4_hit(key, keystream)
        if hit:
            return hit
    if "chacha" in ciphers:
        hit = chacha_hit(key, keystream)
        if hit:
            return hit
    return None


def verify(key: bytes, pairs) -> dict:
    """Re-check a key against every pair with the full construction list."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import srw_y_key as S

    opened = []
    for row in pairs:
        hits = S.check_key(key, row["cipher"], row["size"])
        if hits:
            opened.append({"bundle": row["name"], "mode": hits[0]["mode"]})
    return {"pairs": len(pairs), "opened": len(opened), "detail": opened[:5]}


# --------------------------------------------------------------------------- hunt
def hunt_keys(candidates, pairs, ciphers, limit_files=1, progress=None) -> list[dict]:
    hits = []
    files = pairs[:max(1, limit_files)]
    for index, (label, key) in enumerate(candidates):
        if progress and index and index % 20000 == 0:
            progress(index, len(hits))
        for row in files:
            hit = test_key(key, row["keystream"], ciphers)
            if hit:
                hits.append({"mode": hit, "key_hex": key.hex(), "origin": label,
                             "bundle": row["name"]})
                break
    return hits


def hunt_pbkdf2(candidates, pairs, salts, iterations, limit_files=2,
                progress=None) -> list[dict]:
    """key = Rfc2898DeriveBytes(password, salt, iterations).digest(32) (+16)."""
    hits = []
    files = pairs[:max(1, limit_files)]
    for index, (label, password) in enumerate(candidates):
        if progress and index and index % 200 == 0:
            progress(index, len(hits))
        for salt_label, salt in salts:
            if len(salt) < 8:
                continue
            for count in iterations:
                derived = hashlib.pbkdf2_hmac("sha1", password, salt, count, 32)
                for key in (derived, derived[:16]):
                    for row in files:
                        hit = test_key(key, row["keystream"], ("aes",))
                        if hit:
                            hits.append({"mode": hit + f"/pbkdf2-{count}",
                                         "key_hex": key.hex(), "origin": label,
                                         "salt": salt_label.decode("latin-1")[:60],
                                         "bundle": row["name"]})
                            return hits
    return hits


# ------------------------------------------------------------------- catalog salts
def catalog_salts(catalog_path: Path, names: set[str]) -> dict[str, list[bytes]]:
    """Per-bundle salt guesses from the Addressables catalogue entries."""
    try:
        data = json.loads(Path(catalog_path).read_bytes())
        extra = base64.b64decode(data["m_ExtraDataString"])
        internal_ids = data["m_InternalIds"]
    except Exception as error:
        print(f"catalogue unreadable: {error}")
        return {}
    text = extra.decode("utf-16-le", "ignore")
    entries = re.findall(r'\{"m_Hash":"([0-9a-f]{32})".*?"m_BundleName":"([^"]*)"', text)
    out: dict[str, list[bytes]] = {}
    for index, (hash_hex, bundle_name) in enumerate(entries):
        internal = internal_ids[index] if index < len(internal_ids) else ""
        stem = Path(internal.replace("\\", "/")).name
        if stem in names:
            out.setdefault(stem, []).extend([
                hash_hex.encode(), bytes.fromhex(hash_hex),
                bundle_name.encode(), stem.encode(),
                stem.replace(".bundle", "").encode(),
            ])
    return out


# ------------------------------------------------------------------------------ cli
def cmd_strings(args) -> int:
    seen: set[str] = set()
    for path in args.sources:
        blob = Path(path).read_bytes()
        found = strings_from(blob, args.minimum, args.maximum)
        print(f"{path}: {len(found):,} strings")
        seen.update(found)
    ordered = sorted(seen, key=lambda s: (len(s), s))
    Path(args.out).write_text("\n".join(ordered) + "\n", encoding="utf-8")
    print(f"{len(ordered):,} unique strings -> {args.out}")
    return 0


def cmd_hunt(args) -> int:
    print(f"keyhunt_pairs {SCRIPT_VERSION}")
    pairs = load_pairs(Path(args.pairs), Path(args.plain))
    by_name = {row["name"]: row for row in pairs}
    print(f"pairs: {len(pairs)}")
    if not pairs:
        print("no pairs; check --pairs and --plain")
        return 2

    literals = []
    if args.literals:
        literals = [line for line in Path(args.literals).read_text(
            encoding="utf-8", errors="ignore").splitlines() if line]
        if args.max_literals:
            literals = literals[:args.max_literals]
        print(f"literals: {len(literals):,}")

    if args.pbkdf2:
        salts: list[tuple[bytes, bytes]] = [
            (b"self", None),  # placeholder, replaced per literal
            (b"SRWY", b"SRWY"),
            (b"salt", b"salt"),
            (b"SUPER ROBOT WARS Y", b"SUPER ROBOT WARS Y"),
            (b"Bundle", b"Bundle"),
            (b"SeekableAesStream", b"SeekableAesStream"),
        ]
        salt_rows: list[tuple[bytes, bytes]] = []
        for label, value in salts:
            if value is not None:
                salt_rows.append((label, value))

        per_bundle: dict[str, list[bytes]] = {}
        if args.salt_from_catalog:
            per_bundle = catalog_salts(Path(args.salt_from_catalog),
                                       set(by_name))
            print(f"catalogue salts for {len(per_bundle)} of our bundles")

        # passwords: every literal; salts: the literal itself, a few constants, and
        # (for the first bundle) any per-bundle value the catalogue knows
        candidates = [(text, text.encode("utf-8", "ignore")) for text in literals]
        hits = []
        started = time.time()
        first = pairs[0]
        for index, (label, password) in enumerate(candidates):
            local = list(salt_rows) + [(f"self:{label}", password)]
            for salt in per_bundle.get(first["name"], []):
                local.append((f"catalog:{salt[:24].hex()}", salt))
            for salt_label, salt in local:
                if len(salt) < 8:
                    continue
                for count in args.pbkdf2_iterations:
                    derived = hashlib.pbkdf2_hmac("sha1", password, salt, count, 32)
                    for key in (derived, derived[:16]):
                        hit = test_key(key, first["keystream"], ("aes",))
                        if hit:
                            hits.append({"mode": hit + f"/pbkdf2-{count}",
                                         "key_hex": key.hex(), "origin": label,
                                         "salt": salt_label.decode("latin-1")[:60],
                                         "bundle": first["name"]})
                            print(json.dumps(hits[-1]))
                            return 0
            if index and index % 500 == 0:
                print(f"  {index:,} passwords, {time.time() - started:.0f}s, "
                      f"{len(hits)} hits", flush=True)
        print(f"pbkdf2: no hit in {time.time() - started:.0f}s")

    if args.skip_keys:
        return 1

    candidates = []
    for text in literals:
        for label, key in key_forms(text):
            candidates.append((f"{label}:{text}", key))
    print(f"key candidates: {len(candidates):,}")
    started = time.time()
    hits = hunt_keys(candidates, pairs, tuple(args.ciphers), args.files,
                     progress=lambda done, found: print(
                         f"  {done:,} candidates, {time.time() - started:.0f}s, "
                         f"{found} hits", flush=True))
    print(f"searched {len(candidates):,} candidates in {time.time() - started:.0f}s")
    for hit in hits:
        print(json.dumps(hit))
        report = verify(bytes.fromhex(hit["key_hex"]), pairs)
        print(f"  verified on {report['opened']}/{report['pairs']} pairs: "
              f"{report['detail']}")
    Path(args.out).write_text(json.dumps(
        {"script_version": SCRIPT_VERSION, "pairs": len(pairs),
         "candidates": len(candidates), "hits": hits}, indent=1) + "\n",
        encoding="utf-8")
    print(f"report: {args.out}")
    return 0 if hits else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=SCRIPT_VERSION)
    sub = parser.add_subparsers(dest="cmd", required=True)

    strs = sub.add_parser("strings", help="dump literal candidates from a binary")
    strs.add_argument("--from", dest="sources", nargs="+", required=True)
    strs.add_argument("--out", required=True)
    strs.add_argument("--minimum", type=int, default=4)
    strs.add_argument("--maximum", type=int, default=96)

    hunt = sub.add_parser("hunt", help="test candidates against the pairs")
    hunt.add_argument("--pairs", default="local/pairs")
    hunt.add_argument("--plain", default="local/owner_carve4")
    hunt.add_argument("--literals")
    hunt.add_argument("--max-literals", type=int, default=0)
    hunt.add_argument("--files", type=int, default=2,
                      help="how many pairs a candidate must open")
    hunt.add_argument("--ciphers", nargs="+", default=["aes", "rc4", "chacha"])
    hunt.add_argument("--pbkdf2", action="store_true")
    hunt.add_argument("--pbkdf2-iterations", nargs="+", type=int,
                      default=[1000, 10000])
    hunt.add_argument("--salt-from-catalog")
    hunt.add_argument("--skip-keys", action="store_true")
    hunt.add_argument("--out", default="keyhunt_report.json")

    args = parser.parse_args(argv)
    return cmd_strings(args) if args.cmd == "strings" else cmd_hunt(args)


if __name__ == "__main__":
    sys.exit(main())
