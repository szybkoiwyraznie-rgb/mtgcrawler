"""Unscoped dictionary rows must go only to the chapters that hold their key."""
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tests')]
import build_translation_patch as B
import test_table_write as F


def robo_pool(keys):
    records = []
    for key in keys:
        extra = bytearray(8)
        struct.pack_into('<H', extra, 0, key)  # 7 pointers = 28-byte prefix
        records.append(F.make_record([b'x'], extra=bytes(extra), nptr=7))
    return F.make_pool(records)


def keyed(key):
    return {'id': f'robonote:{key}:series', 'part': 'series', 'key': key,
            'source': {'container': None, 'member': 'srw_DL_RoboDictionary'}}


class KeyRoutingTests(unittest.TestCase):
    def test_routes_to_matching_chapters_including_repeated_keys(self):
        data = {b'one': {'srw_DL_RoboDictionary01.bin': robo_pool([1, 5, 5])},
                b'two': {'srw_DL_RoboDictionary02.bin': robo_pool([2, 5])}}
        stores = {'config01': b'one', 'config02': b'two'}
        with patch.object(B, 'container_members', side_effect=lambda blob: list(data[blob])), \
             patch.object(B, '_members_of_blob', side_effect=lambda blob: data[blob]):
            one, both, absent = keyed('1'), keyed(5), keyed(99)
            out = B.attach_containerless([one, both, absent], stores)
        self.assertEqual(out['config01'], [one, both])
        self.assertEqual(out['config02'], [both])

    def test_broken_member_remains_routed_for_writer_diagnostics(self):
        member = 'srw_DL_RoboDictionary01.bin'
        with patch.object(B, 'container_members', return_value=[member]), \
             patch.object(B, '_members_of_blob', return_value={member: b'bad'}):
            out = B.attach_containerless([keyed(99)], {'config01': b'original'})
        self.assertEqual(out['config01'], [keyed(99)])

    def test_invalid_pointer_cannot_be_silently_filtered(self):
        member = 'srw_DL_RoboDictionary01.bin'
        bad = bytearray(robo_pool([1]))
        struct.pack_into('<I', bad, 8, 0xffffffff)  # first pointer, key table still legible
        with patch.object(B, 'container_members', return_value=[member]), \
             patch.object(B, '_members_of_blob', return_value={member: bytes(bad)}):
            out = B.attach_containerless([keyed(99)], {'config01': b'original'})
        self.assertEqual(out['config01'], [keyed(99)])

    def test_empty_dictionary_does_not_receive_label_but_malformed_does(self):
        member = 'srwDL_CharaDictionary08.bin'
        label = {'id': 'label:4', 'part': 'label', 'source': {'container': None, 'member': 'srwDL_CharaDictionary'}}
        data = {b'empty': {member: b'\0\0\0\0'}, b'bad': {member: b'bad'}}
        with patch.object(B, 'container_members', return_value=[member]), \
             patch.object(B, '_members_of_blob', side_effect=lambda blob: data[blob]):
            out = B.attach_containerless([label], {'empty': b'empty', 'bad': b'bad'})
        self.assertEqual(out['empty'], [])
        self.assertEqual(out['bad'], [label])

    def test_redirect_ignores_unit_with_no_local_robot_record(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            builder = B.ContainerBuild('config00.cpk', b'container', [], Path(tmp))
            reference = keyed(1)
            unit = {'id': 'unit:3990:series', 'category': 'unit_series', 'part': 'series',
                    'key': '3990', 'jp': 'series', 'en': 'series',
                    'source': {'container': 'config00.cpk', 'member': 'unit_list'}}
            with patch.object(B, '_members_of_blob', return_value={'srw_DL_RoboDictionary00.bin': robo_pool([1])}):
                out = builder._redirect_unit_series([reference, unit])
            self.assertEqual(out, [reference])
            self.assertEqual(builder.report['problems'], [])
            self.assertIn('no local target', builder.report['info'][0])

    def test_redirect_retains_row_when_pool_is_malformed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            builder = B.ContainerBuild('config00.cpk', b'container', [], Path(tmp))
            reference = keyed(1)
            unit = {'id': 'unit:3990:series', 'category': 'unit_series', 'part': 'series',
                    'key': '3990', 'jp': 'series', 'en': 'series',
                    'source': {'container': 'config00.cpk', 'member': 'unit_list'}}
            bad = bytearray(robo_pool([1]))
            struct.pack_into('<I', bad, 8, 0xffffffff)
            with patch.object(B, '_members_of_blob', return_value={'srw_DL_RoboDictionary00.bin': bytes(bad)}):
                out = builder._redirect_unit_series([reference, unit])
            self.assertEqual([r['id'] for r in out], ['robonote:1:series', 'unit:3990:series'])
            self.assertTrue(out[1]['__redirected'])

    def test_redirect_recognizes_numeric_string_key(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            builder = B.ContainerBuild('config01.EDAT', b'container', [], Path(tmp))
            reference = keyed(5)
            unit = {'id': 'unit:5:series', 'category': 'unit_series', 'part': 'series',
                    'key': '5', 'jp': 'series', 'en': 'series',
                    'source': {'container': 'config01.EDAT', 'member': 'unit_list'}}
            with patch.object(B, '_members_of_blob', return_value={'srw_DL_RoboDictionary01.bin': robo_pool([5])}):
                out = builder._redirect_unit_series([reference, unit])
            self.assertEqual(out, [reference])

    def test_explicit_container_and_non_dictionary_are_unchanged(self):
        scoped = {'id': 'explicit', 'key': 5, 'source': {'container': 'config01', 'member': 'anything'}}
        other = {'id': 'other', 'key': 5, 'source': {'container': None, 'member': 'plain'}}
        with patch.object(B, 'container_members', return_value=['plain']), \
             patch.object(B, '_members_of_blob', return_value={'plain': b'blob'}):
            out = B.attach_containerless([scoped, other], {'config01': b'original'})
        self.assertEqual(out['config01'], [scoped, other])


if __name__ == '__main__':
    unittest.main()
