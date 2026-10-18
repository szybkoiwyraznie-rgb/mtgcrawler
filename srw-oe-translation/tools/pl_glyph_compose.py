#!/usr/bin/env python3
"""Compose Polish glyphs at build time from the user's own ASCII font cells.

No game bitmap is stored here or shipped. Only small diacritic recipes are code.
The base letter is copied pixel-for-pixel: no resampling, dilation, centering,
vertical shift or external typeface. The marks use the source letter's coverage
scale (the measured native font peaks at 9/15, not Roboto's 15/15).
"""
from __future__ import annotations

BASE_LETTERS = dict(zip("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ"))
STYLE = "native-ascii-plus-marks-v1"
COLS, ROWS, CELL = 8, 14, 56


def ascii_rows(ank: bytes, base: str) -> list[list[int]]:
    if len(base) != 1 or not 0x20 <= ord(base) < 0x80:
        raise ValueError("expected an ASCII base character")
    start = (ord(base) - 0x20) * CELL
    data = ank[start:start + CELL]
    if len(data) != CELL:
        raise ValueError("ASCII cell is outside ank.fta")
    return [[n for b in data[y * 4:(y + 1) * 4] for n in (b & 15, b >> 4)]
            for y in range(ROWS)]


def accent_mask(letter: str, base: list[list[int]]) -> dict[tuple[int, int], int]:
    """(x,y)->coverage for a sparse accent only, never an entire base bitmap."""
    if letter not in BASE_LETTERS:
        raise ValueError(f"unsupported Polish letter {letter!r}")
    if len(base) != ROWS or any(len(row) != COLS for row in base):
        raise ValueError("expected a 14x8 source letter")
    if any(not isinstance(v, int) or not 0 <= v <= 15 for row in base for v in row):
        raise ValueError("source coverage must be 4-bit integers")
    peak = max(map(max, base))
    if peak < 4:
        raise ValueError("empty or too faint ASCII source letter")
    edge = max(1, round(peak / 3))
    lower = letter.lower()
    if lower in "ąę":
        # The native baseline ends at row 11. Never move the body to fit a tail.
        if any(v for row in base[12:] for v in row):
            raise ValueError("source has no free rows below baseline for ogonek")
        right = [x for x, value in enumerate(base[11]) if value >= max(1, peak // 2)]
        if not right:
            raise ValueError("source does not reach the expected baseline")
        anchor = max(right)
        if anchor < 1:
            raise ValueError("no horizontal room for ogonek")
        return {(anchor - 1, 12): peak, (anchor, 12): edge,
                (anchor - 1, 13): edge, (anchor, 13): peak}
    if lower == "ł":
        # Find the native stem, so lowercase l and uppercase L need no shift.
        stem = max(range(COLS), key=lambda x: sum(base[y][x] for y in range(4, 9)))
        points = {(stem + 1, 6): peak, (stem + 2, 6): edge,
                  (stem, 7): peak, (stem + 1, 7): edge,
                  (stem - 1, 8): peak, (stem, 8): edge}
        if any(not 0 <= x < COLS for x, y in points):
            raise ValueError("no horizontal room for stroke")
        return points
    if lower == "ż":
        y = 0 if letter.isupper() else 2
        points = {(3, y): peak, (4, y): edge}
    else:  # ć ń ó ś ź and uppercase: a small rising acute
        y = 0 if letter.isupper() else 1
        points = {(4, y): peak, (5, y): edge,
                  (3, y + 1): peak, (4, y + 1): edge}
    # Faint native antialiasing may share row 1, but never clip a strong body pixel.
    if any(base[y][x] >= max(4, peak // 2) for x, y in points):
        raise ValueError("source letter leaves no room above body for accent")
    return points


def compose(ank: bytes) -> dict[str, list[list[int]]]:
    glyphs = {}
    for letter, source in BASE_LETTERS.items():
        base = ascii_rows(ank, source)
        result = [row[:] for row in base]
        for (x, y), coverage in accent_mask(letter, base).items():
            result[y][x] = max(result[y][x], coverage)
        glyphs[letter] = result
    return glyphs


def verify_native(ank_before: bytes, ank_after: bytes,
                  byte_map: dict[str, int]) -> dict:
    """Independent raw-cell audit: keep native bodies/alpha and untouched ASCII.

    Decode physical katakana cells with explicit byte-0x40 arithmetic. Assert the
    output equals the original ASCII outside the small permitted mark mask; this
    catches shrinking/boldening/offsetting even if a writer's own round-trip agrees.
    """
    failures, letters = [], {}
    for letter, source in BASE_LETTERS.items():
        base = ascii_rows(ank_before, source)
        start = (byte_map[letter] - 0x40) * CELL
        raw = ank_after[start:start + CELL]
        if len(raw) != CELL:
            failures.append(f"{letter}: missing physical cell")
            continue
        actual = [[n for b in raw[y * 4:(y + 1) * 4] for n in (b & 15, b >> 4)]
                  for y in range(ROWS)]
        mask = accent_mask(letter, base)
        changed = 0
        for y in range(ROWS):
            for x in range(COLS):
                expected = max(base[y][x], mask.get((x, y), 0))
                if actual[y][x] != expected:
                    failures.append(f"{letter}: wrong source-body/mark pixel {x},{y}")
                if (x, y) not in mask and actual[y][x] != base[y][x]:
                    failures.append(f"{letter}: body changed outside accent")
                changed += actual[y][x] != base[y][x]
        if not changed:
            failures.append(f"{letter}: accent is missing")
        letters[letter] = {"base": source, "accent_pixels_changed": changed,
                           "native_peak": max(map(max, base)),
                           "output_peak": max(map(max, actual))}
    if ank_before[:96 * CELL] != ank_after[:96 * CELL]:
        failures.append("ASCII source cells changed")
    return {"ok": not failures, "failures": failures, "style": STYLE, "letters": letters}
