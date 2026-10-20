#!/usr/bin/env python3
"""Polish text codec for the PL patch: 18 letters as one-byte half-width katakana codes.

The game font (``tools/font_pl.py``) draws the letters ą ć ę ł ń ó ś ź ż and their uppercase
forms in the 8x14 ``ank.fta`` cells of 18 half-width katakana bytes (0xA1-0xDF).  A letter
therefore advances one cell, like any ASCII letter (owner's requirement, 2026-10-18).

Rules
-----
* a Polish letter encodes as its single byte (:data:`font_pl.PL_BYTES`);
* a half-width katakana character (U+FF61-U+FF9F) in Polish text is an **error**: its CP932
  byte is one of the 63 katakana bytes, and the 18 of them are taken by Polish letters
  (fail closed; the Polish text has no katakana);
* everything else encodes as CP932;
* :func:`decode` maps the 18 bytes back to letters (analysis only; katakana is not decoded).
"""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path
from typing import Dict

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import font_pl  # noqa: E402

#: letter -> single game byte (font_pl is the single source of truth)
PL_TO_BYTE: Dict[str, int] = font_pl.pl_byte_map()
BYTE_TO_PL: Dict[int, str] = {b: ch for ch, b in PL_TO_BYTE.items()}
PL_LETTERS = frozenset(PL_TO_BYTE)


def _is_halfwidth_katakana(ch: str) -> bool:
    return 0xFF61 <= ord(ch) <= 0xFF9F


def encode(text: str, errors: str = "strict") -> bytes:
    """``text`` as game bytes: Polish letters as their single bytes, the rest as CP932."""
    out = bytearray()
    for ch in text:
        byte = PL_TO_BYTE.get(ch)
        if byte is not None:
            out.append(byte)
            continue
        if _is_halfwidth_katakana(ch):
            # its CP932 byte is one of the bytes taken by Polish letters
            if errors != "strict":
                continue
            raise UnicodeEncodeError("cp932", text, 0, 1,
                                     "half-width katakana is reserved for Polish letters")
        try:
            out += ch.encode("cp932")
        except UnicodeEncodeError:
            if errors != "strict":
                continue
            raise
    return bytes(out)


def decode(data: bytes) -> str:
    """Game bytes back to text; the 18 katakana bytes become Polish letters again."""
    out = []
    plain = bytearray()
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        if b in BYTE_TO_PL:
            if plain:
                out.append(plain.decode("cp932"))
                plain = bytearray()
            out.append(BYTE_TO_PL[b])
            i += 1
            continue
        if 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC:  # CP932 lead byte
            plain += data[i:i + 2]
            i += 2
        else:
            plain += data[i:i + 1]
            i += 1
    if plain:
        out.append(plain.decode("cp932"))
    return "".join(out)


def is_pl(text: str) -> bool:
    """True when ``text`` needs this codec (contains at least one Polish letter)."""
    return any(ch in PL_LETTERS for ch in text)


def display_width(s: str) -> int:
    """Drawn half-width cells: PL/ASCII = 1, two-byte CP932 glyphs = 2.

    In particular CP932 ellipses, curly quotes and ambiguous symbols are NOT ASCII-width.
    Invalid characters use a diagnostic fallback; encode() remains the strict gate.
    """
    total = 0
    for ch in s:
        if unicodedata.category(ch) == "Cc":
            continue
        try:
            total += len(encode(ch))
        except UnicodeEncodeError:
            total += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return total
