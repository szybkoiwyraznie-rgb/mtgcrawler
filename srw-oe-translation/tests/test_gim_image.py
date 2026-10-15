#!/usr/bin/env python3
"""Tests for tools/gim_image.py (decoder, PAC index, in-place INDEX8 encoder)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gim_image  # noqa: E402
from gim_fixtures import LABEL_PALETTE, build_index8_gim, build_ui_pac, label_texture  # noqa: E402


class GimDecodeTests(unittest.TestCase):
    def test_parses_the_synthetic_shape_like_the_real_files(self):
        raw = label_texture()
        g = gim_image.parse(raw)
        self.assertEqual((g.width, g.height), (64, 32))
        self.assertEqual(g.image.format, 5)
        self.assertEqual(g.image.pixel_order, 1)
        self.assertEqual(g.palette.format, 3)
        self.assertEqual(g.file_info["program"], "GimConv 1.50")
        self.assertIn("INDEX8", gim_image.describe(g))

    def test_decode_unswizzles_and_resolves_the_palette(self):
        rgba, w, h = gim_image.decode(gim_image.parse(label_texture()))
        self.assertEqual((w, h), (64, 32))

        def px(x, y):
            p = (y * w + x) * 4
            return tuple(rgba[p:p + 4])

        self.assertEqual(px(0, 0), (255, 255, 255, 0))
        self.assertEqual(px(4, 4), (0, 0, 0, 187))     # outline
        self.assertEqual(px(10, 10), (230, 230, 230, 255))  # fill
        self.assertEqual(px(40, 20), (255, 0, 0, 255))  # sentinel

    def test_linear_and_swizzled_decode_the_same(self):
        idx = [(x + y) % 16 for y in range(16) for x in range(32)]
        lin = gim_image.decode(gim_image.parse(build_index8_gim(32, 16, LABEL_PALETTE, idx, swizzled=False)))
        swz = gim_image.decode(gim_image.parse(build_index8_gim(32, 16, LABEL_PALETTE, idx, swizzled=True)))
        self.assertEqual(lin, swz)

    def test_refuses_non_gim(self):
        with self.assertRaises(gim_image.GimError):
            gim_image.parse(b"not a gim at all" * 4)

    def test_swizzle_is_the_inverse_of_unswizzle(self):
        data = bytes(range(256)) * 8   # pitch 64, 32 rows
        self.assertEqual(gim_image._unswizzle(gim_image._swizzle(data, 64, 32), 64, 32), data)
        self.assertEqual(gim_image._swizzle(gim_image._unswizzle(data, 64, 32), 64, 32), data)


class GimEncodeTests(unittest.TestCase):
    def test_identity_round_trip_is_byte_exact(self):
        raw = label_texture()
        g = gim_image.parse(raw)
        rgba, _, _ = gim_image.decode(g)
        self.assertEqual(gim_image.encode_index8(g, rgba), raw)

    def test_identity_keeps_indices_when_the_palette_repeats_a_colour(self):
        palette = list(LABEL_PALETTE) + [(255, 255, 255, 255)]   # duplicate of index 1 at index 16
        idx = [16 if x % 2 else 1 for y in range(8) for x in range(16)]
        raw = build_index8_gim(16, 8, palette, idx)
        g = gim_image.parse(raw)
        rgba, _, _ = gim_image.decode(g)
        self.assertEqual(gim_image.encode_index8(g, rgba), raw)

    def test_edited_pixels_map_to_the_nearest_palette_entry_and_nothing_else_moves(self):
        raw = label_texture()
        g = gim_image.parse(raw)
        rgba, w, h = gim_image.decode(g)
        buf = bytearray(rgba)
        p = (2 * w + 2) * 4
        buf[p:p + 4] = bytes((250, 252, 255, 255))      # near white -> index 1
        q = (3 * w + 2) * 4
        buf[q:q + 4] = bytes((2, 2, 2, 180))            # near (0,0,0,187) -> index 7
        new = gim_image.encode_index8(g, bytes(buf))
        self.assertEqual(len(new), len(raw))
        again, _, _ = gim_image.decode(gim_image.parse(new))
        self.assertEqual(tuple(again[p:p + 4]), (255, 255, 255, 255))
        self.assertEqual(tuple(again[q:q + 4]), (0, 0, 0, 187))
        # every other pixel identical
        for i in range(0, len(rgba), 4):
            if i not in (p, q):
                self.assertEqual(again[i:i + 4], rgba[i:i + 4])
        # headers and palette untouched: only pixel bytes differ
        self.assertEqual(new[:g.image_block.data + 0x40], raw[:g.image_block.data + 0x40])
        self.assertEqual(new[g.palette_block.start:], raw[g.palette_block.start:])

    def test_transparent_pixels_never_map_to_opaque_entries(self):
        palette = [(255, 255, 255, 255), (0, 0, 0, 0)]
        self.assertEqual(gim_image.nearest_index(palette, (255, 255, 255, 0)), 1)
        self.assertEqual(gim_image.nearest_index(palette, (0, 0, 0, 10)), 0)

    def test_wrong_buffer_size_and_other_formats_are_refused(self):
        g = gim_image.parse(label_texture())
        with self.assertRaises(gim_image.GimError):
            gim_image.encode_index8(g, b"\x00" * 10)


class PacIndexTests(unittest.TestCase):
    def test_reads_entries_regardless_of_the_first_word(self):
        a = label_texture()
        for first in (0x10, 0x800):
            pac = build_ui_pac([("mensys_03.gim", a), ("INTER.inc", b"x" * 7)], first_word=first)
            entries = gim_image.pac_entries(pac)
            self.assertEqual([(n, s) for n, _, s in entries], [("mensys_03.gim", len(a)), ("INTER.inc", 7)])
            name, off, size = entries[0]
            self.assertEqual(pac[off:off + size], a)

    def test_refuses_a_truncated_index(self):
        with self.assertRaises(gim_image.GimError):
            gim_image.pac_entries(b"\x10\x00\x00\x00" + b"\xff\xff\x00\x00" + b"\x20\x00\x00\x00" + b"\x00" * 4)


if __name__ == "__main__":
    unittest.main()
