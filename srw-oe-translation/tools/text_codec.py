#!/usr/bin/env python3
"""The single point where the patch build picks its text codec.

``en`` (default) is the shipped behaviour: CP932 bytes, ``export_strings.display_width``.
``pl`` is the Polish patch: the 18 letters become the private two-byte codes of
``tools/pl_text.py`` (drawn by the extended font), width counts them 2.

The language is set once per build (:func:`set_lang`) instead of being threaded through
every writer signature - the writers already funnel their encoding through a handful of
helpers, and a build is one language start to finish.  Tests that switch the language
reset it in ``tearDown`` (:func:`set_lang("en")``).

The row *field* follows the language too (:func:`field`): ``build_translation_patch`` maps
``pl`` onto ``en`` while loading, so every writer keeps reading one field.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import export_strings  # noqa: E402
import pl_text  # noqa: E402

_LANG = "en"


def set_lang(lang: str) -> None:
    """Select the codec for the rest of the build (``en`` or ``pl``)."""
    global _LANG
    if lang not in ("en", "pl"):
        raise ValueError(f"unknown lang {lang!r} (expected 'en' or 'pl')")
    _LANG = lang


def lang() -> str:
    return _LANG


def field() -> str:
    """The package field the translation lives in for the current language."""
    return _LANG


def encode(text: str) -> bytes:
    """Game bytes for ``text`` under the current language (UnicodeEncodeError propagates)."""
    if _LANG == "pl":
        return pl_text.encode(text)
    return text.encode("cp932")


def display_width(text: str) -> int:
    """On-screen width in half-width units under the current language."""
    if _LANG == "pl":
        return pl_text.display_width(text)
    return export_strings.display_width(text)


def cstring(data: bytes, start: int = 0, end: int = None) -> bytes:
    """The NUL-terminated text at ``data[start:end]``, Shift-JIS-aware.

    A NUL that is the trail byte of a double-byte character does not terminate anything: the
    Polish letters sit at 0x82FA..0x830B, and ś (0x8300) carries a literal 0x00 trail.  For
    plain ASCII and for real Shift-JIS (whose trails never reach the control range) the result
    is exactly the old ``split(b"\\x00")[0]``.
    """
    end = len(data) if end is None else end
    position = start
    while position < end:
        byte = data[position]
        if byte == 0:
            return data[start:position]
        if 0x81 <= byte <= 0x9F or 0xE0 <= byte <= 0xFC:
            position += 2              # a double-byte character: the trail may be any byte
        else:
            position += 1
    return data[start:end]


def decode(data: bytes) -> str:
    """Text for game bytes under the current language (strict; errors propagate)."""
    if _LANG == "pl":
        return pl_text.decode(data)
    return data.decode("cp932")
