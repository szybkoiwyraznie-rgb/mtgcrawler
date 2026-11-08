#!/usr/bin/env python3
"""The bundle cipher with the XOR done in C, for whole-game scans.

`srw_y_bundle_crypt.decrypt` XORs the keystream byte by byte, which is perfectly
fine for the handful of bundles a patch touches and far too slow for thousands of
files (about 1 MB/s). The keystream and the AES calls are the same here; only the
XOR moves into `Crypto.Util.strxor`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import srw_y_bundle_crypt as cipher  # noqa: E402


def decrypt_bundle(name: str, data: bytes) -> bytes:
    """Decrypt one bundle; falls back to the reference cipher without pycryptodome."""
    try:
        from Crypto.Cipher import AES
        from Crypto.Util import strxor
    except ImportError:  # pragma: no cover - the kit installs pycryptodome
        return cipher.decrypt(name, data)
    key = cipher.key_for(name)
    blocks = (len(data) + 15) // 16
    ecb = AES.new(key, AES.MODE_ECB)
    chunks = []
    for start in range(1, blocks + 1, 4096):
        stop = min(start + 4096, blocks + 1)
        chunks.append(ecb.encrypt(b''.join(cipher.nonce(i) for i in range(start, stop))))
    stream = b''.join(chunks)
    padded = data + b'\x00' * (len(stream) - len(data))
    return strxor.strxor(padded, stream)[:len(data)]


def plain_of(path: Path) -> bytes:
    """The plaintext of a bundle file on disk, whether it is still encrypted or not."""
    data = Path(path).read_bytes()
    return data if data[:7] == b'UnityFS' else decrypt_bundle(Path(path).name, data)
