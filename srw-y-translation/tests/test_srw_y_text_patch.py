"""Tests for the localization table walker and for the opening translation file.

Nothing here touches game data: the table is synthesized and the translation is
the JSON that lives in the repository.
"""
import json
import struct
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import srw_y_text_patch as patch  # noqa: E402

TRANSLATION = HERE / 'translations' / 'opening_pl.json'


def make_table(strings, gap=b'\x00\x00\x00\x00\x00\xb0\x60\x07\x72\x04\x00\x00'):
    """Build a table the way the game stores it: header, then prefix+text+gap."""
    out = bytearray(b'\x00' * 88)
    for text in strings:
        data = text.encode('utf-8')
        out += struct.pack('<i', len(data)) + data + gap
    return bytes(out)


class IsTextTests(unittest.TestCase):
    def test_accepts_prose(self):
        self.assertTrue(patch.is_text(b'The Earth.\nThis planet in a remote corner.'))
        self.assertTrue(patch.is_text('地球……\n天の川銀河の辺境'.encode()))

    def test_rejects_binary(self):
        self.assertFalse(patch.is_text(b'\x00\x01\x02\x03\xff\xfe'))
        self.assertFalse(patch.is_text(b'ab'))


class FindBlocksTests(unittest.TestCase):
    def test_finds_every_string_in_order(self):
        texts = ['The Earth.\nThis planet in a remote corner of the galaxy.',
                 'Sixty years ago, interstellar war ravaged our planet...',
                 'Ziemia……\nTa planeta na skraju Drogi Mlecznej']
        raw = make_table(texts)
        blocks = patch.find_blocks(raw)
        self.assertEqual([b[2].decode() for b in blocks], texts)
        for offset, size, data in blocks:
            self.assertEqual(struct.unpack('<i', raw[offset:offset + 4])[0], size)
            self.assertEqual(raw[offset + 4:offset + 4 + size], data)

    def test_rejects_a_length_that_runs_past_the_end(self):
        raw = struct.pack('<i', 9999) + b'short'
        self.assertEqual(patch.find_blocks(raw), [])


class ReplaceBlocksTests(unittest.TestCase):
    def test_longer_and_shorter_text_keep_the_gaps(self):
        texts = ['The Earth.\nThis planet in a remote corner of the galaxy.',
                 'Sixty years ago, interstellar war ravaged our planet...']
        raw = make_table(texts)
        blocks = patch.find_blocks(raw)
        new = ['Ziemia.\nTa planeta na skraju Drogi Mlecznej, bardzo daleko.',
               'Sześćdziesiąt lat temu.']
        out = patch.replace_blocks(raw, blocks, new)
        self.assertNotEqual(len(out), len(raw))
        got = [b[2].decode() for b in patch.find_blocks(out)]
        self.assertEqual(got, new)
        # the header and every inter-field gap stay byte for byte
        self.assertEqual(out[:88], raw[:88])
        gap = raw[blocks[0][0] + 4 + blocks[0][1]:blocks[1][0]]
        self.assertIn(gap, out)

    def test_same_length_edit_keeps_the_size(self):
        texts = ['The Earth.\nThis planet in a remote corner of the galaxy.']
        raw = make_table(texts)
        blocks = patch.find_blocks(raw)
        size = len(texts[0].encode())
        same = 'Ziemia.\nTa planeta w dalekim zakątku.'
        same = same + ' ' * (size - len(same.encode()))
        self.assertEqual(len(same.encode()), size)
        out = patch.replace_blocks(raw, blocks, [same])
        self.assertEqual(len(out), len(raw))
        self.assertEqual(patch.find_blocks(out)[0][2].decode(), same)


class TranslationFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trans = json.loads(TRANSLATION.read_text(encoding='utf-8'))

    def test_twenty_four_blocks(self):
        self.assertEqual(len(self.trans['blocks']), 24)
        self.assertEqual([b['n'] for b in self.trans['blocks']], list(range(1, 25)))

    def test_every_block_has_all_three_languages(self):
        for block in self.trans['blocks']:
            for key in ('ja', 'en', 'pl'):
                self.assertTrue(block.get(key), f'block {block["n"]} has no {key}')
            self.assertEqual(block['pl'], block['pl'].strip() or block['pl'])

    def test_polish_uses_real_diacritics(self):
        joined = ''.join(b['pl'] for b in self.trans['blocks'])
        for char in 'ąćęłńóśźż':
            self.assertIn(char, joined, f'missing {char}')

    def test_polish_is_not_longer_than_the_english_text_box(self):
        """The box was laid out for the English string; keep the Polish inside it."""
        for block in self.trans['blocks']:
            pl = len(block['pl'].encode())
            en = len(block['en'].encode())
            self.assertLessEqual(pl, en + 12,
                                 f'block {block["n"]}: {pl} B Polish vs {en} B English')


if __name__ == '__main__':
    unittest.main()
