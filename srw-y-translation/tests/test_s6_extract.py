"""Synthetic tests for the S6 extractors (no game data needed)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import s6_scenario as SC  # noqa: E402
import s6_tables as TB  # noqa: E402


def table_object(name: str, locale: str, texts: list[str]) -> bytes:
    """One MonoBehaviour table object, built the way the game stores it."""
    head = bytes(12) + struct.pack('<II', 1, 1) + bytes(8)
    name_bytes = name.encode()
    head += struct.pack('<I', len(name_bytes)) + name_bytes
    head += bytes(-len(head) % 4)
    locale_bytes = locale.encode()
    head += struct.pack('<I', len(locale_bytes)) + locale_bytes
    head += bytes(-len(head) % 4)
    head += struct.pack('<I', 2) + bytes(8) + struct.pack('<I', 0)
    head += struct.pack('<I', len(texts))
    body = b''
    for index, text in enumerate(texts):
        encoded = text.encode()
        body += struct.pack('<II', 0x1000 + index, 0)
        body += struct.pack('<I', len(encoded)) + encoded
        body += bytes(-(len(body) + 4) % 4)     # pad, then the always-zero u32
        body += bytes(4)
    return head + body + struct.pack('<II', 2, 0)


class TableTest(unittest.TestCase):
    def test_walk_returns_every_text_and_lands_on_the_terminator(self):
        texts = ['The Earth.\nThis planet', '「ん…？」', 'Methuss']
        raw = table_object('prologue_en-US', 'en-US', texts)
        start, count = TB.table_header(raw, 'prologue_en-US')
        self.assertEqual(count, len(texts))
        rows, end = TB.walk_records(raw, start, count)
        self.assertEqual([row['text'] for row in rows], texts)
        self.assertEqual(raw[end:], TB.TERMINATOR)

    def test_keys_survive_and_identify_a_row(self):
        raw = table_object('pilot_name_ja-JP', 'ja-JP', ['洸', 'マリ'])
        start, count = TB.table_header(raw, 'pilot_name_ja-JP')
        rows, _ = TB.walk_records(raw, start, count)
        self.assertEqual([row['key'] for row in rows], ['00000000:00001000',
                                                       '00000000:00001001'])

    def test_byte_length_is_the_encoded_length_not_the_character_count(self):
        raw = table_object('robot_name_ja-JP', 'ja-JP', ['ライディーン'])
        start, count = TB.table_header(raw, 'robot_name_ja-JP')
        rows, _ = TB.walk_records(raw, start, count)
        self.assertEqual(rows[0]['bytes'], 18)

    def test_a_truncated_object_is_an_error_not_a_short_read(self):
        raw = table_object('prologue_en-US', 'en-US', ['one', 'two'])[:-20]
        start, count = TB.table_header(raw, 'prologue_en-US')
        with self.assertRaises(TB.TableError):
            TB.walk_records(raw, start, count)


class ScenarioTest(unittest.TestCase):
    SCRIPT = (
        '  {Cmd_BGM_Play, Y_DEM_2, [[Y_DEM_2]]},  -- BGM\r\n'
        '  {Inst_BG_Draw, 221, 0, BgSizeNormal, [[221\\t通常サイズ<tag>左下]], LeftBottom},\r\n'
        '  {WPos_c, 2, FDMode_Normal, pid_CHISE, \r\n'
        '  [[ちせ\r\n「ん…？」]],\r\n'
        '   0, NULL, NULL},  -- <srw-tag=speakEE>(x)<srw-tag=string-id>(87.0)\r\n'
        '  {WPos_a, 2, FDMode_Normal, pid_GAUMA, \r\n'
        '  [[ガウマ\r\n「そうか」]],\r\n'
        '   0, NULL, NULL},  -- <srw-tag=speakEE>(x)<srw-tag=string-id>(88.0)\r\n'
    )

    def test_only_literals_with_a_string_id_are_lines(self):
        units = SC.parse_units(self.SCRIPT)
        self.assertEqual([unit['string_id'] for unit in units], ['87.0', '88.0'])

    def test_speaker_is_the_first_line_and_the_rest_is_the_line(self):
        first = SC.parse_units(self.SCRIPT)[0]
        self.assertEqual(first['speaker'], 'ちせ')
        self.assertEqual(first['text'], '「ん…？」')

    def test_carriage_returns_never_reach_the_translator(self):
        first = SC.parse_units(self.SCRIPT)[0]
        self.assertNotIn('\r', first['speaker'] + first['text'])

    def test_repeated_string_ids_get_distinct_keys(self):
        seen = {}
        import collections
        counter = collections.Counter()
        units = [{'string_id': '1.0'}, {'string_id': '1.0'}]
        keys = [SC.unit_key(unit, counter) for unit in units]
        self.assertEqual(keys, ['1.0#1', '1.0#2'])


if __name__ == '__main__':
    unittest.main()
