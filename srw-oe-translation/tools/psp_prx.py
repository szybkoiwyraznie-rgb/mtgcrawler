#!/usr/bin/env python3
"""Decrypt a PSP ``~PSP`` executable (``PBOOT.PBP`` → ``DATA.PSP``, or a disc ``EBOOT.BIN``) to
its plain ELF - pure Python, no third-party module.

Why this exists: the last Japanese strings of SRW OE that no data file holds (battle-panel
``移動後``/``敵``/``味方``, ``メインパイロット``, ``SELECT パイロット表示変更``, the 1.08
ability lines ``<貫通 Lv2> 敵の防御-35%`` …) live in the executable itself.  The 1.08 update
executable is ``PBOOT.PBP`` → ``DATA.PSP`` (tag ``0x2E5E10F0``, decrypt mode 25), which the
user's DLC folder already contains - but it is KIRK-encrypted, so :mod:`exe_strings` needs this
module first.

What is ported (and only this - measured on the user's ``PBOOT.PBP``, 2026-10-15):

* AES-128 decryption (FIPS-197, table driven), CBC with a zero IV the way libkirk's
  ``AES_cbc_decrypt`` does it;
* KIRK command 7 (AES-CBC with one of the key-vault keys, ``kirk7``) and command 1 (the
  ``KIRK_CMD1_HEADER`` whose AES key is itself wrapped with the KIRK-1 key);
* the "type 5" PRX scheme PPSSPP uses for the ``0x2E5Exxxx`` game-update tags (tag key +
  a fixed 16-byte XOR seed, ``PRXType5::decrypt`` + ``pspFinishType5``) and the plainer "type 2"
  scheme of the retail ``0xD916xxF0`` EBOOT tags (same steps, no XOR);
* the SHA-1 check PPSSPP performs is kept - a wrong key fails closed instead of producing noise;
* gzip-compressed payloads (``comp_attribute & 1``) are inflated.

Keys and the algorithm are the public ones from PPSSPP (``Core/ELF/PrxDecrypter.cpp``, GPL-2.0,
itself after PSARDUMPER/JPCSP) and libkirk (``kirk_engine.c``); nothing here was derived from
the game.  Only the tags listed in :data:`TAG_KEYS` are supported - anything else raises
:class:`PrxError` naming the tag, so a different print of the game is reported, not mangled.

Usage::

    python3 tools/psp_prx.py PBOOT.PBP -o DATA.elf          # PBP: takes its DATA.PSP
    python3 tools/psp_prx.py EBOOT.BIN -o EBOOT.elf         # bare ~PSP file
    python3 tools/psp_prx.py PBOOT.PBP --info               # header fields only

Pure Python decrypts the 5.5 MB executable in roughly 15-30 s - acceptable for a one-shot build
step; the result is cached by the callers (md5 of the input) where it matters.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PSP_MAGIC = 0x5053507E  # "~PSP"
PBP_MAGIC = b"\x00PBP"
ELF_MAGIC = b"\x7fELF"

PBP_NAMES = ("PARAM.SFO", "ICON0.PNG", "ICON1.PMF", "PIC0.PNG", "PIC1.PNG", "SND0.AT3",
             "DATA.PSP", "DATA.PSAR")


class PrxError(Exception):
    """Decryption refused or failed - the message says why (tag, SHA-1, size)."""


# --------------------------------------------------------------------------------------------
# AES-128 decryption (FIPS-197), table driven.  Decrypt only - nothing here ever encrypts.
# --------------------------------------------------------------------------------------------

def _build_tables() -> Tuple[List[int], List[int], List[int], List[int], List[int], List[int]]:
    sbox = [0] * 256
    inv = [0] * 256
    p = q = 1
    while True:  # generate the S-box from the multiplicative inverse in GF(2^8)
        p = p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)
        q ^= q << 1
        q ^= q << 2
        q ^= q << 4
        q &= 0xFF
        if q & 0x80:
            q ^= 0x09
        x = q ^ (q << 1) ^ (q << 2) ^ (q << 3) ^ (q << 4)
        x = (x ^ (x >> 8) ^ 0x63) & 0xFF
        sbox[p] = x
        inv[x] = p
        if p == 1:
            break
    sbox[0] = 0x63
    inv[0x63] = 0

    def xt(a: int) -> int:
        a <<= 1
        return (a ^ 0x1B) & 0xFF if a & 0x100 else a

    def mul(a: int, b: int) -> int:
        r = 0
        while b:
            if b & 1:
                r ^= a
            a = xt(a)
            b >>= 1
        return r

    td0, td1, td2, td3 = [], [], [], []
    for i in range(256):
        s = inv[i]
        e, b, d, n = mul(s, 0x0E), mul(s, 0x0B), mul(s, 0x0D), mul(s, 0x09)
        w = (e << 24) | (n << 16) | (d << 8) | b
        td0.append(w)
        td1.append(((w >> 8) | (w << 24)) & 0xFFFFFFFF)
        td2.append(((w >> 16) | (w << 16)) & 0xFFFFFFFF)
        td3.append(((w >> 24) | (w << 8)) & 0xFFFFFFFF)
    return sbox, inv, td0, td1, td2, td3


_SBOX, _INV_SBOX, _TD0, _TD1, _TD2, _TD3 = _build_tables()
_RCON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def _expand_key(key: bytes) -> List[int]:
    if len(key) != 16:
        raise ValueError("AES-128 key must be 16 bytes")
    w = list(struct.unpack(">4I", key))
    for i in range(4, 44):
        t = w[i - 1]
        if i % 4 == 0:
            t = ((t << 8) | (t >> 24)) & 0xFFFFFFFF
            t = ((_SBOX[t >> 24] << 24) | (_SBOX[(t >> 16) & 0xFF] << 16)
                 | (_SBOX[(t >> 8) & 0xFF] << 8) | _SBOX[t & 0xFF])
            t ^= _RCON[i // 4 - 1] << 24
        w.append(w[i - 4] ^ t)
    return w


def _inv_mix_word(x: int) -> int:
    # InvMixColumns of one already-substituted column, via the T tables on the S-box values.
    return (_TD0[_SBOX[x >> 24]] ^ _TD1[_SBOX[(x >> 16) & 0xFF]]
            ^ _TD2[_SBOX[(x >> 8) & 0xFF]] ^ _TD3[_SBOX[x & 0xFF]])


class AES128:
    """Decrypt-only AES-128 (equivalent inverse cipher, round keys pre-mixed)."""

    __slots__ = ("_rk",)

    def __init__(self, key: bytes):
        w = _expand_key(key)
        # decryption round keys in reverse order; InvMixColumns applied to rounds 1..9
        rk = []
        for r in range(10, -1, -1):
            col = w[4 * r:4 * r + 4]
            if 0 < r < 10:
                col = [_inv_mix_word(c) for c in col]
            rk.extend(col)
        self._rk = rk

    def decrypt_block(self, block: bytes) -> bytes:
        rk = self._rk
        td0, td1, td2, td3, inv = _TD0, _TD1, _TD2, _TD3, _INV_SBOX
        s0, s1, s2, s3 = struct.unpack(">4I", block)
        s0 ^= rk[0]
        s1 ^= rk[1]
        s2 ^= rk[2]
        s3 ^= rk[3]
        k = 4
        for _ in range(9):
            t0 = td0[s0 >> 24] ^ td1[(s3 >> 16) & 0xFF] ^ td2[(s2 >> 8) & 0xFF] ^ td3[s1 & 0xFF] ^ rk[k]
            t1 = td0[s1 >> 24] ^ td1[(s0 >> 16) & 0xFF] ^ td2[(s3 >> 8) & 0xFF] ^ td3[s2 & 0xFF] ^ rk[k + 1]
            t2 = td0[s2 >> 24] ^ td1[(s1 >> 16) & 0xFF] ^ td2[(s0 >> 8) & 0xFF] ^ td3[s3 & 0xFF] ^ rk[k + 2]
            t3 = td0[s3 >> 24] ^ td1[(s2 >> 16) & 0xFF] ^ td2[(s1 >> 8) & 0xFF] ^ td3[s0 & 0xFF] ^ rk[k + 3]
            s0, s1, s2, s3 = t0, t1, t2, t3
            k += 4
        o0 = ((inv[s0 >> 24] << 24) | (inv[(s3 >> 16) & 0xFF] << 16) | (inv[(s2 >> 8) & 0xFF] << 8) | inv[s1 & 0xFF]) ^ rk[k]
        o1 = ((inv[s1 >> 24] << 24) | (inv[(s0 >> 16) & 0xFF] << 16) | (inv[(s3 >> 8) & 0xFF] << 8) | inv[s2 & 0xFF]) ^ rk[k + 1]
        o2 = ((inv[s2 >> 24] << 24) | (inv[(s1 >> 16) & 0xFF] << 16) | (inv[(s0 >> 8) & 0xFF] << 8) | inv[s3 & 0xFF]) ^ rk[k + 2]
        o3 = ((inv[s3 >> 24] << 24) | (inv[(s2 >> 16) & 0xFF] << 16) | (inv[(s1 >> 8) & 0xFF] << 8) | inv[s0 & 0xFF]) ^ rk[k + 3]
        return struct.pack(">4I", o0, o1, o2, o3)

    def cbc_decrypt_zero_iv(self, data: bytes) -> bytes:
        """libkirk ``AES_cbc_decrypt``: CBC with an all-zero IV, whole 16-byte blocks only."""
        if len(data) % 16:
            raise ValueError("AES-CBC input is not a multiple of 16 bytes")
        out = bytearray(len(data))
        prev = bytes(16)
        dec = self.decrypt_block
        for i in range(0, len(data), 16):
            blk = data[i:i + 16]
            plain = dec(blk)
            out[i:i + 16] = bytes(a ^ b for a, b in zip(plain, prev))
            prev = blk
        return bytes(out)


# --------------------------------------------------------------------------------------------
# KIRK (libkirk port - the two commands PRX decryption needs)
# --------------------------------------------------------------------------------------------

KIRK1_KEY = bytes.fromhex("98C940975C1D10E87FE60EA3FD03A8BA")

# key vault entries used by the tags below (libkirk ``keyvault[code]``)
KEYVAULT: Dict[int, bytes] = {
    0x43: bytes.fromhex("F88174B1BDE9BFDD45E2F55589CF46AB"),
    0x48: bytes.fromhex("09B1C705C35F536677C0EB3677DF8307"),
    0x5A: bytes.fromhex("EEAF49E009879BEFAAD6326A3213C429"),
    0x5B: bytes.fromhex("8D26B90F431DBB08DB1DDAC5B52C92ED"),
    0x5D: bytes.fromhex("115A5D20D53A8DD39CC5AF410F0F186F"),
    0x62: bytes.fromhex("02326AE7D396CE7F1C419DD65207ED09"),
}


def kirk7(data: bytes, code: int) -> bytes:
    """KIRK command 7: AES-128-CBC (zero IV) decryption with key-vault key ``code``."""
    key = KEYVAULT.get(code)
    if key is None:
        raise PrxError("kirk7: no key-vault entry for code 0x%02X" % code)
    return AES128(key).cbc_decrypt_zero_iv(data)


def kirk1_decrypt(header: bytes, payload: bytes, data_size: int, data_offset: int) -> bytes:
    """KIRK command 1 without the CMAC/ECDSA checks: unwrap the AES key with the KIRK-1 key,
    then decrypt ``data_size`` bytes of ``payload`` starting at ``data_offset``."""
    keys = AES128(KIRK1_KEY).cbc_decrypt_zero_iv(header[:0x20])
    aes_key = keys[:16]
    body = payload[data_offset:data_offset + data_size]
    if len(body) != data_size:
        raise PrxError("kirk1: payload shorter than data_size (%d < %d)" % (len(body), data_size))
    return AES128(aes_key).cbc_decrypt_zero_iv(body)


# --------------------------------------------------------------------------------------------
# PRX tags (subset of PPSSPP's g_tagInfo2)
# --------------------------------------------------------------------------------------------

_XOR_2E5E = bytes.fromhex("69BA5534F0C0D671E31FDB97E07CD22A")

#: tag -> (16-byte tag key, kirk7 code, scheme type, xor seed or None)
TAG_KEYS: Dict[int, Tuple[bytes, int, int, Optional[bytes]]] = {
    # game updates / PSN (PBOOT.PBP) - type 5 with the fixed XOR seed
    0x2E5E0AF0: (bytes.fromhex("ACD76D90333738923141D636AF9F1715"), 0x48, 5, _XOR_2E5E),
    0x2E5E10F0: (bytes.fromhex("9D5C5BAF8CD8697E519F7096E6D5C4E8"), 0x48, 5, _XOR_2E5E),
    0x2E5E11F0: (bytes.fromhex("75EBE843F4878FD0147F7E39ADAF049D"), 0x48, 5, _XOR_2E5E),
    0x2E5E12F0: (bytes.fromhex("8A7BC9D6525888EA518360CA1679E207"), 0x48, 5, _XOR_2E5E),
    0x2E5E13F0: (bytes.fromhex("FFA468C331CAB74CF123FF01653D2636"), 0x48, 5, _XOR_2E5E),
    # retail disc executables - type 2 (no XOR)
    0xD91605F0: (bytes.fromhex("B88C458BB6E76EB85159A6537C5E8631"), 0x5D, 2, None),
    0xD91606F0: (bytes.fromhex("ED10E036C4FE83F375705EF6A44005F7"), 0x5D, 2, None),
    0xD91608F0: (bytes.fromhex("5C770CBBB4C24FA27E3B4EB4B4C870AF"), 0x5D, 2, None),
    0xD91609F0: (bytes.fromhex("D036127580562043C430943E1C75D1BF"), 0x5D, 2, None),
    0xD9160AF0: (bytes.fromhex("10A9AC16AE19C07E3B607786016FF263"), 0x5D, 2, None),
    0xD9160BF0: (bytes.fromhex("8383F13753D0BEFC8DA73252460AC2C2"), 0x5D, 2, None),
    0xD91611F0: (bytes.fromhex("61B0C0587157D9FA74670E5C7E6E95B9"), 0x5D, 2, None),
    0xD91612F0: (bytes.fromhex("9E20E1CDD788DEC0319B10AFC5B87323"), 0x5D, 2, None),
    0xD91613F0: (bytes.fromhex("EBFF40D8B41AE166913B8F64B6FCB712"), 0x5D, 2, None),
    0xD91614F0: (bytes.fromhex("FDF7B73C9FD1339511B8B5BB54237385"), 0x5D, 2, None),
    0xD91615F0: (bytes.fromhex("C803E34450F1E72A6A0DC361B68E5F51"), 0x5D, 2, None),
    0xD91616F0: (bytes.fromhex("5303B86A101998491CAF30E4251B6B28"), 0x5D, 2, None),
    0xD91617F0: (bytes.fromhex("02FA487375AFAE0A67892B954B0987A3"), 0x5D, 2, None),
    0xD91618F0: (bytes.fromhex("96967CC3F712DA621BF69A9A4444BC48"), 0x5D, 2, None),
    0xD91619F0: (bytes.fromhex("E032A7086B2B292CD14D5BEEA8C8B4E9"), 0x5D, 2, None),
    0xD9161AF0: (bytes.fromhex("27E5A74952E194673566910CE89A2524"), 0x5D, 2, None),
    0xD91620F0: (bytes.fromhex("521CB45F403B9ADDACFCEA92FDDDF590"), 0x5D, 2, None),
    0xD91621F0: (bytes.fromhex("D1912EA621142962F6EDAECBDDA3BAFE"), 0x5D, 2, None),
    0xD91622F0: (bytes.fromhex("595D784D21B201176C9AB51BDAB7F9E6"), 0x5D, 2, None),
    0xD91623F0: (bytes.fromhex("AA45EB4F62FBD10D71D562D2F5BFA52F"), 0x5D, 2, None),
    0xD91624F0: (bytes.fromhex("61B726AF8BF14158836AC49212CBB1E9"), 0x5D, 2, None),
    0xD91628F0: (bytes.fromhex("49A4FC66DCE76221DB18A750D6A8C1B6"), 0x5D, 2, None),
}


# --------------------------------------------------------------------------------------------
# ~PSP header
# --------------------------------------------------------------------------------------------

def psp_header(blob: bytes) -> dict:
    """The fields of the 0x150-byte ``~PSP`` header this module needs (little endian)."""
    if len(blob) < 0x150 or struct.unpack_from("<I", blob, 0)[0] != PSP_MAGIC:
        raise PrxError("not a ~PSP executable (magic mismatch or shorter than 0x150 bytes)")
    (sig, attribute, comp_attribute, ver_lo, ver_hi) = struct.unpack_from("<IHHBB", blob, 0)
    modname = blob[0x0A:0x26].split(b"\0", 1)[0].decode("ascii", "replace")
    elf_size, psp_size, entry, modinfo_offset, bss_size = struct.unpack_from("<IIIIi", blob, 0x28)
    devkit, decrypt_mode = struct.unpack_from("<II", blob, 0x78)
    comp_size, data_offset = struct.unpack_from("<ii", blob, 0xB0)
    tag = struct.unpack_from("<I", blob, 0xD0)[0]
    return {
        "attribute": attribute, "comp_attribute": comp_attribute,
        "module_version": "%d.%d" % (ver_hi, ver_lo), "modname": modname,
        "elf_size": elf_size, "psp_size": psp_size, "entry": entry,
        "modinfo_offset": modinfo_offset, "bss_size": bss_size,
        "devkit_version": devkit, "decrypt_mode": decrypt_mode,
        "comp_size": comp_size, "data_offset": data_offset, "tag": tag,
        "compressed": bool(comp_attribute & 1),
    }


def expand_seed(key: bytes, code: int, bonus: Optional[bytes] = None) -> bytes:
    """PPSSPP ``expandSeed``: 9 counter-prefixed copies of the tag key through kirk7."""
    buf = bytearray()
    for i in range(0x90 // 0x10):
        blk = bytearray(key)
        blk[0] = i
        buf += blk
    out = bytearray(kirk7(bytes(buf), code))
    if bonus:
        for i in range(len(out)):
            out[i] ^= bonus[i % 0x10]
    return bytes(out)


def _sha1(*parts: bytes) -> bytes:
    h = hashlib.sha1()
    for p in parts:
        h.update(p)
    return h.digest()


def decrypt_prx(blob: bytes, verify_sha1: bool = True) -> bytes:
    """``~PSP`` bytes → plain ELF bytes (inflated when the header says gzip).

    Raises :class:`PrxError` for unknown tags, a failed SHA-1 or a result that is not an ELF.
    """
    hdr = psp_header(blob)
    tag = hdr["tag"]
    if tag not in TAG_KEYS:
        raise PrxError("unsupported ~PSP tag 0x%08X (decrypt mode %d)" % (tag, hdr["decrypt_mode"]))
    key, code, scheme, xor1 = TAG_KEYS[tag]
    size = hdr["psp_size"]
    if size > len(blob):
        raise PrxError("~PSP truncated: psp_size %d > %d bytes available" % (size, len(blob)))
    prx = blob[:size]

    xorbuf = expand_seed(key, code)
    # PRXType2/5 view of the header
    tag_bytes = prx[0xD0:0xD4]
    empty = bytes(0x58)
    ident = bytearray(prx[0x140:0x150])
    sha1 = bytearray(prx[0x12C:0x140])
    kirk_header = bytearray(prx[0x80:0xB0] + prx[0xC0:0xD0])
    kirk_meta = prx[0xB0:0xC0]
    prx_header = prx[0x00:0x80]

    if scheme == 5:
        data = bytearray(bytes(kirk_header) + bytes(sha1[:0x10]))
        if xor1:
            for i in range(0x50):
                data[i] ^= xor1[i % 0x10]
        data = bytearray(kirk7(bytes(data), code))
        kirk_header[:] = data[:0x40]
        sha1[:0x10] = data[0x40:0x50]
        # second step: XOR then kirk7 over id (0x10) + sha1 (0x14) + first 0x3C of kirk header
        region = bytearray(bytes(ident) + bytes(sha1) + bytes(kirk_header[:0x3C]))
        if xor1:
            for i in range(0x60):
                region[i] ^= xor1[i % 0x10]
        region = bytearray(kirk7(bytes(region), code))
        ident[:] = region[:0x10]
        sha1[:] = region[0x10:0x24]
        kirk_header[:0x3C] = region[0x24:0x60]
    elif scheme == 2:
        region = bytearray(bytes(ident) + bytes(sha1) + bytes(kirk_header[:0x3C]))
        region = bytearray(kirk7(bytes(region), code))
        ident[:] = region[:0x10]
        sha1[:] = region[0x10:0x24]
        kirk_header[:0x3C] = region[0x24:0x60]
    else:  # pragma: no cover - table only holds 2 and 5
        raise PrxError("scheme %d not implemented" % scheme)

    if verify_sha1:
        digest = _sha1(tag_bytes, xorbuf[:0x10], empty, bytes(ident), bytes(kirk_header),
                       kirk_meta, prx_header)
        if digest != bytes(sha1):
            raise PrxError("SHA-1 mismatch for tag 0x%08X - wrong key or damaged file" % tag)

    # decryptKirkHeader: XOR with xorbuf[0x10:0x50], kirk7, XOR with xorbuf[0x50:0x90]
    kh = bytearray(kirk_header)
    for i in range(0x40):
        kh[i] ^= xorbuf[0x10 + i]
    kh = bytearray(kirk7(bytes(kh), code))
    for i in range(0x40):
        kh[i] ^= xorbuf[0x50 + i]
    # KIRK_CMD1_HEADER: keys (0x40) + unused (0x20) + mode/ecdsa (0x10) + metadata (0x10) = 0x90
    data_size, data_offset = struct.unpack_from("<ii", kirk_meta, 0)
    if data_size <= 0 or data_offset < 0:
        raise PrxError("bad kirk metadata (data_size %d, data_offset %d)" % (data_size, data_offset))
    # the CMD1 header lives at out+0x40 and its payload at out+0x40+0x90+data_offset
    payload_start = 0x40 + 0x90 + data_offset
    payload = prx[payload_start:]
    aligned = (data_size + 15) & ~15
    plain = kirk1_decrypt(bytes(kh), payload, min(aligned, len(payload)) & ~15, 0)
    out = plain[:data_size]
    if hdr["compressed"]:
        if out[:2] == b"\x1f\x8b":
            out = zlib.decompress(out, 16 + zlib.MAX_WBITS)
        else:
            raise PrxError("compressed payload is not gzip (KL4E/KL3E not supported)")
    if out[:4] != ELF_MAGIC:
        raise PrxError("decrypted payload is not an ELF (tag 0x%08X)" % tag)
    return out


# --------------------------------------------------------------------------------------------
# PBP container helpers
# --------------------------------------------------------------------------------------------

def pbp_entries(blob: bytes) -> List[Tuple[str, int, int]]:
    """``[(name, offset, size)]`` of the eight PBP sub-files (size 0 when absent)."""
    if blob[:4] != PBP_MAGIC:
        raise PrxError("not a PBP file")
    offs = list(struct.unpack_from("<8I", blob, 8))
    ends = offs[1:] + [len(blob)]
    return [(name, off, max(0, end - off)) for name, off, end in zip(PBP_NAMES, offs, ends)]


def pbp_get(blob: bytes, name: str) -> bytes:
    for n, off, size in pbp_entries(blob):
        if n == name:
            return blob[off:off + size]
    raise KeyError(name)


def pbp_replace(blob: bytes, name: str, data: bytes) -> bytes:
    """Rebuild the PBP with one sub-file replaced (offsets recomputed, order kept)."""
    entries = pbp_entries(blob)
    parts = []
    for n, off, size in entries:
        parts.append(data if n == name else blob[off:off + size])
    header = bytearray(blob[:0x28])
    pos = 0x28
    for i, part in enumerate(parts):
        struct.pack_into("<I", header, 8 + 4 * i, pos)
        pos += len(part)
    return bytes(header) + b"".join(parts)


def load_executable(path: Path) -> Tuple[bytes, str]:
    """Return ``(~PSP or ELF bytes, kind)`` for a PBP, a bare ``~PSP`` file or a plain ELF."""
    blob = path.read_bytes()
    if blob[:4] == PBP_MAGIC:
        return pbp_get(blob, "DATA.PSP"), "pbp"
    if blob[:4] == ELF_MAGIC:
        return blob, "elf"
    if struct.unpack_from("<I", blob, 0)[0] == PSP_MAGIC:
        return blob, "psp"
    raise PrxError("%s: neither PBP, ~PSP nor ELF" % path.name)


def elf_from(path: Path) -> bytes:
    """Decrypt whatever ``path`` is into plain ELF bytes (passes a plain ELF through)."""
    blob, kind = load_executable(path)
    if kind == "elf":
        return blob
    return decrypt_prx(blob)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", type=Path, help="PBOOT.PBP / EBOOT.PBP / EBOOT.BIN / DATA.PSP")
    parser.add_argument("-o", "--out", type=Path, help="where to write the plain ELF")
    parser.add_argument("--info", action="store_true", help="print the ~PSP header and exit")
    args = parser.parse_args(argv)

    blob, kind = load_executable(args.input)
    if kind == "elf":
        print("%s: already a plain ELF (%d bytes, md5 %s)" % (args.input.name, len(blob),
                                                              hashlib.md5(blob).hexdigest()))
        if args.out:
            args.out.write_bytes(blob)
        return 0
    hdr = psp_header(blob)
    print("%s: ~PSP module %r v%s tag 0x%08X mode %d elf_size %d psp_size %d%s" % (
        args.input.name, hdr["modname"], hdr["module_version"], hdr["tag"], hdr["decrypt_mode"],
        hdr["elf_size"], hdr["psp_size"], " gzip" if hdr["compressed"] else ""))
    if args.info:
        return 0
    try:
        elf = decrypt_prx(blob)
    except PrxError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2
    print("decrypted: %d bytes, md5 %s" % (len(elf), hashlib.md5(elf).hexdigest()))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(elf)
        print("written: %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
