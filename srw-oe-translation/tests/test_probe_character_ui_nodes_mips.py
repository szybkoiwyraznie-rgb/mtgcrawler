"""Synthetic validation of the research UI-node probe; no game files."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import probe_character_ui_nodes_mips as P


def sample(fallback=True):
    head = bytearray(12)
    struct.pack_into('<II', head, 4, P.NODES + 0x20, P.NODES + 0x40)
    nodes = bytearray(3 * 0x20)
    data = [
        (P.NODES + 0x20, P.NODES + 0x40, 0x548, P.ANCHOR, 0x12345678),
        (0, P.NODES, 0x549, P.RECORD + 0x100, 0),
        (P.NODES, 0, 0x54a, P.FALLBACK if fallback else P.RECORD + 0x200, 0),
    ]
    for i, entry in enumerate(data):
        struct.pack_into('<5I', nodes, i * 0x20, *entry)
    strings = [b''] * 12
    strings[3] = b'series'
    strings[10] = b'' if fallback else b'character'
    return nodes, head, strings


class UINodeProbeTests(unittest.TestCase):
    def test_valid_fallback_and_nonempty_direct_slot(self):
        for fallback in (True, False):
            nodes, head, strings = sample(fallback)
            self.assertEqual(P.validate_nodes(nodes, head, strings, b'fallback'), fallback)

    def test_rejects_changed_links_tags_options_and_fallback(self):
        for offset in (0, 8, 16, 0x20 + 16, 0x40 + 8):
            nodes, head, strings = sample()
            nodes[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                P.validate_nodes(nodes, head, strings, b'fallback')
        nodes, head, strings = sample()
        strings[10] = b'nonempty'
        with self.assertRaisesRegex(ValueError, 'fallback'):
            P.validate_nodes(nodes, head, strings, b'fallback')
        nodes, head, strings = sample()
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            P.validate_nodes(nodes, head, strings, b'')

    def test_wrong_elf_refused_before_reading_files(self):
        with self.assertRaisesRegex(ValueError, 'executable'):
            P.verify(b'not a game executable', Path('missing'), Path('missing'))


if __name__ == '__main__':
    unittest.main()
