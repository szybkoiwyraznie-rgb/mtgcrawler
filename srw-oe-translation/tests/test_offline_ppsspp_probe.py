"""Synthetic tests for the offline research helper; no game assets or emulator."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research' / 'ppsspp-headless'))
import probe_offline as P


class OfflineProbeTests(unittest.TestCase):
    def test_rejects_incomplete_vram(self):
        with self.assertRaisesRegex(ValueError, 'byte count'):
            P.convert(b'')

    def test_rejects_bad_parameters_and_filenames(self):
        for stride, fmt in ((479, 1), (4097, 1), (512, -1), (512, 4)):
            with self.subTest(stride=stride, fmt=fmt), self.assertRaises(ValueError):
                P.convert(b'', stride, fmt)
        self.assertEqual(P.frame_parameters('vram-001-active-04044000-512-3.raw'), (512, 3))
        self.assertEqual(P.frame_parameters('vram-001-04000000.raw'), (512, 1))
        with self.assertRaises(ValueError):
            P.frame_parameters('other.raw')

    def test_decodes_5551_and_stride(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest('Pillow is not installed')
        raw = bytearray(P.FRAME_BYTES)
        raw[0:2] = (0x001f).to_bytes(2, 'little')
        raw[512 * 2:512 * 2 + 2] = (0x03e0).to_bytes(2, 'little')
        image = P.convert(bytes(raw))
        self.assertEqual(image.size, (480, 272))
        self.assertEqual(image.getpixel((0, 0)), (255, 0, 0))
        self.assertEqual(image.getpixel((0, 1)), (0, 255, 0))
        self.assertEqual(image.getpixel((0, 2)), (0, 0, 0))

    def test_other_hardware_pixel_formats(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest('Pillow is not installed')
        for fmt, packed, expected in ((0, bytes.fromhex('e007'), (0, 255, 0)),
                                      (2, bytes.fromhex('0f0f'), (255, 0, 255)),
                                      (3, bytes([12, 34, 56, 255]), (12, 34, 56))):
            bpp = len(packed)
            raw = bytearray(480 * 272 * bpp)
            raw[:bpp] = packed
            with self.subTest(fmt=fmt):
                self.assertEqual(P.convert(bytes(raw), 480, fmt).getpixel((0, 0)), expected)


if __name__ == '__main__':
    unittest.main()
