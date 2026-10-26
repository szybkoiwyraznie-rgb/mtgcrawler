"""Tests for the mission-data kit (request 5) — the scene -> chapter route.

The kit exists because the scenario scripts carry no mission titles (measured: 15 of 378,
all incidental words in dialogue), so the link must live in the game's own mission data.
These tests pin down what the plan contains, so the owner is never sent a kit that asks
for audio, for scenes, or for the same bundle twice.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_mission_request as kit  # noqa: E402


class MissionPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not kit.LISTING.is_file():
            raise unittest.SkipTest('brak local/intake/listing_sizes.txt — dane właściciela')
        cls.plan = kit.survey()

    def test_found_the_whole_class(self):
        # every asset named after a mission in the catalogue is either planned or held
        expected = set(kit.NAMES)
        got = {address for item in self.plan['wanted'] for address in item['addresses']}
        self.assertEqual(expected - got - set(self.plan['already_have']), set())

    def test_no_duplicate_bundle(self):
        bundles = [item['bundle'] for item in self.plan['wanted']]
        self.assertEqual(len(bundles), len(set(bundles)))

    def test_only_small_data_files(self):
        # mission data, not audio: nothing over 1 MB, and the whole kit under 1 MB
        self.assertLess(self.plan['bytes'], 1024 * 1024)
        for item in self.plan['wanted']:
            self.assertLess(item['bytes'], 1024 * 1024, item['label'])

    def test_every_entry_has_a_folder_and_a_size(self):
        for item in self.plan['wanted']:
            self.assertTrue(item['folder'], item['label'])
            self.assertGreater(item['bytes'], 0, item['label'])
            self.assertTrue(item['file'].endswith('.bundle'), item['label'])

    def test_plan_is_deterministic(self):
        again = kit.survey()
        self.assertEqual([item['bundle'] for item in self.plan['wanted']],
                         [item['bundle'] for item in again['wanted']])


class MissionCollectorTests(unittest.TestCase):
    def test_ps1_is_ascii_with_crlf(self):
        if not kit.PS1.is_file():
            raise unittest.SkipTest('brak wygenerowanego zbieraka')
        raw = kit.PS1.read_bytes()
        self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
        self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))
        raw[3:].decode('ascii')  # BOM + ASCII body, the way PS 5.1 wants it

    def test_every_planned_file_is_in_the_script(self):
        if not kit.PS1.is_file():
            raise unittest.SkipTest('brak wygenerowanego zbieraka')
        text = kit.PS1.read_text(encoding='utf-8-sig')
        plan = kit.survey()
        for item in plan['wanted']:
            self.assertIn(item['file'], text)


if __name__ == '__main__':
    unittest.main()
