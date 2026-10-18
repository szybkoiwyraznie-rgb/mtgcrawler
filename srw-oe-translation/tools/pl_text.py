#!/usr/bin/env python3
"""Polish text codec for the PL patch: 18 letters as private two-byte codes.

The game font (``tools/font_pl.py``) learns the letters ą ć ę ł ń ó ś ź ż and their
uppercase forms as ``kanji.fta`` slots 3540-3557, reachable through ``kanjiL.tbl`` cells
for the two-byte codes 0x82FA-0x830B.  Both properties are measurable on the shipped
codec stack:

* none of the 18 letters encodes in CP932, so plain ``str.encode("cp932")`` fails on every
  Polish target - this module substitutes the letters with their codes *first* and only
  then CP932-encodes the rest (fail closed: anything else unencodable still raises);
* none of the 18 codes decodes in CP932 (``illegal multibyte sequence``), so a stray code
  can never masquerade as a different character - :func:`decode` recognizes the codes
  explicitly and CP932-decodes everything between them.

Width
-----
A letter drawn from the 14 px ``kanji.fta`` cell advances like any other two-byte glyph
(hypothesis pending the in-game test, conservative by design): :func:`display_width`
counts it 2, the same as CJK.  If the game advances less, lines only wrap earlier; the
46-unit dialogue budget from ``docs/HANDOFF.md`` §2 stays honoured.
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

# letter -> two-byte code (font_pl is the single source of truth; import its map)
PL_TO_CODE: Dict[str, int] = font_pl.pl_code_map()
CODE_TO_PL: Dict[bytes, str] = {
    code.to_bytes(2, "big"): letter for letter, code in PL_TO_CODE.items()
}
PL_LETTERS = frozenset(PL_TO_CODE)


def encode(text: str, errors: str = "strict") -> bytes:
    """``text`` as game bytes: Polish letters as their private codes, rest as CP932."""
    out = bytearray()
    for ch in text:
        code = PL_TO_CODE.get(ch)
        if code is not None:
            out += code.to_bytes(2, "big")
        else:
            try:
                out += ch.encode("cp932")
            except UnicodeEncodeError:
                if errors != "strict":
                    continue
                raise
    return bytes(out)


def decode(data: bytes) -> str:
    """Game bytes back to text; the 18 private codes become Polish letters again."""
    out = []
    plain = bytearray()  # run of ordinary CP932 bytes between private codes
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        if 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xEF:  # CP932 lead byte
            pair = data[i:i + 2]
            letter = CODE_TO_PL.get(pair)
            if letter is not None:
                out.append(plain.decode("cp932"))
                plain = bytearray()
                out.append(letter)
                i += 2
                continue
            plain += data[i:i + 2]
            i += 2
        else:
            plain += data[i:i + 1]
            i += 1
    out.append(plain.decode("cp932"))
    return "".join(out)


def is_pl(text: str) -> bool:
    """True when ``text`` needs this codec (contains at least one Polish letter)."""
    return any(ch in PL_LETTERS for ch in text)


def display_width(s: str) -> int:
    """``export_strings.display_width`` with the Polish letters counted as full-width."""
    total = 0
    for ch in s:
        if unicodedata.category(ch) == "Cc":
            continue
        if ch in PL_LETTERS or unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 2
        else:
            total += 1
    return total
