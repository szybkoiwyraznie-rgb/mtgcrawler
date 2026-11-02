"""Synthetic validation of the research UI-node probe; no game files."""
import struct
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import probe_character_ui_nodes_mips as P


def sample(fallback=True):
    head = bytearray(12)
    struct.pack_into('<II', head, 4, P.NODES + 0x14, P.NODES + 0x28)
    nodes = bytearray(3 * 0x14)
    data = [
        (P.NODES + 0x14, P.NODES + 0x28, 0x548, P.ANCHOR, 0x12345678),
        (0, P.NODES, 0x549, P.RECORD + 0x100, 0),
        (P.NODES, 0, 0x54a, P.FALLBACK if fallback else P.RECORD + 0x200, 0),
    ]
    for i, entry in enumerate(data):
        struct.pack_into('<5I', nodes, i * 0x14, *entry)
    strings = [b''] * 12
    strings[3] = b'series'
    strings[10] = b'' if fallback else b'character'
    return nodes, head, strings


class UINodeProbeTests(unittest.TestCase):
    def test_valid_fallback_and_nonempty_direct_slot(self):
        for fallback in (True, False):
            nodes, head, strings = sample(fallback)
            self.assertEqual(P.validate_nodes(nodes, head, strings, P.FALLBACK), fallback)

    def test_rejects_changed_links_tags_options_and_fallback(self):
        for offset in (0, 8, 16, 0x14 + 16, 0x28 + 8):
            nodes, head, strings = sample()
            nodes[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                P.validate_nodes(nodes, head, strings, P.FALLBACK)
        nodes, head, strings = sample()
        strings[10] = b'nonempty'
        with self.assertRaisesRegex(ValueError, 'fallback'):
            P.validate_nodes(nodes, head, strings, P.FALLBACK)

    def test_full_function_first_node_pointers_are_checked(self):
        nodes, head, strings = sample()
        struct.pack_into('<II', nodes, 12, P.RECORD + 0x310, 0x3f03a0)
        self.assertTrue(P.validate_nodes(nodes, head, strings, P.FALLBACK,
                                         P.RECORD + 0x310, 0x3f03a0))
        with self.assertRaisesRegex(ValueError, 'first UI field'):
            P.validate_nodes(nodes, head, strings, P.FALLBACK, P.RECORD + 0x311, 0x3f03a0)
        with self.assertRaisesRegex(ValueError, 'first UI field'):
            P.validate_nodes(nodes, head, strings, P.FALLBACK, P.RECORD + 0x310, 0x3f03a1)

    def test_null_character_nodes(self):
        nodes, head, _ = sample()
        struct.pack_into('<II', nodes, 12, 0, 0)
        struct.pack_into('<I', nodes, 0x14 + 12, 0)
        struct.pack_into('<I', nodes, 0x28 + 12, 0)
        P.validate_null_nodes(nodes, head)
        for offset in (0, 8, 12, 16, 0x14 + 12, 0x28 + 12):
            broken = bytearray(nodes)
            broken[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                P.validate_null_nodes(broken, head)

    def test_collects_real_table_and_rejects_bad_data(self):
        row = bytearray(172)
        row[32:37] = b'name\0'
        struct.pack_into('<H', row, 96, 3315)
        with patch.object(P.CM, 'members_of', return_value=(None, {'charalist01.bin': bytes(row)}, None)):
            blob, indices = P.collect_charalist([Path('config')])
            self.assertEqual(blob, bytes(row))
            self.assertEqual(indices, {3315: 0})
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                P.collect_charalist([Path('config'), Path('config')])
        with patch.object(P.CM, 'members_of', return_value=(None, {'charalist01.bin': b'x'}, None)):
            with self.assertRaisesRegex(ValueError, 'malformed'):
                P.collect_charalist([Path('config')])
        row[32:76] = b'x' * 44
        with patch.object(P.CM, 'members_of', return_value=(None, {'charalist01.bin': bytes(row)}, None)):
            with self.assertRaisesRegex(ValueError, 'unterminated'):
                P.collect_charalist([Path('config')])

    def test_wrong_elf_refused_before_reading_files(self):
        with self.assertRaisesRegex(ValueError, 'executable'):
            P.verify(b'not a game executable', Path('missing'), Path('missing'))


if __name__ == '__main__':
    unittest.main()
