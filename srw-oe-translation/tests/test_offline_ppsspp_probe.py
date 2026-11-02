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


if __name__ == '__main__':
    unittest.main()
