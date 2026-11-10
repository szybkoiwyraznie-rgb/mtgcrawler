"""The v8.1 appendix: new elements outside v8, without touching v8's numbering.

The appendix exists because the shipped v8 package was rendered before some corpus rows
had a Japanese source line (and before three scenes were in the corpus at all).  Putting
those elements into the existing scene files would shift the number of every later
element and invalidate the translator's filled `PL:` lines, so they live in one extra
file whose numbering is local to itself.

These tests are the guard rails: the appendix must contain exactly the rows listed in
`data/package_appendix_y.json`, every element must either have a `PL:` slot or be an
explicit repeat, the import manifest must agree element for element, and no listed line
may also be rendered in a v8 scene file.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / 'translations' / 'patch-v8-1'
SCENY = ROOT / 'translations' / 'template-v8' / 'sceny'
APPENDIX = PATCH / 'odcinek-99-dodatek.md'
MANIFEST = PATCH / 'import_manifest.json'
DATA = ROOT / 'data' / 'package_appendix_y.json'
SCENARIO = ROOT / 'data' / 's6-full' / 'scenario.jsonl'

ELEMENT = re.compile(r'^(\d+)\. ', re.M)
SCENE = re.compile(r'^## Scena (D\d+/\d+) — (cse\S+)$', re.M)


def normalise(text: str) -> str:
    return re.sub(r'\s+', '', text or '')


class AppendixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = APPENDIX.read_text(encoding='utf-8')
        cls.data = json.loads(DATA.read_text(encoding='utf-8'))
        cls.manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        cls.entry = cls.manifest['files']['odcinek-99-dodatek.md']

    def test_elements_match_the_committed_row_list(self):
        self.assertEqual(len(ELEMENT.findall(self.text)), len(self.data['rows']))
        self.assertEqual(len(self.data['rows']), 299)

    def test_numbering_restarts_in_every_scene(self):
        """v8 numbers elements per scene (`index` in the scene's rows), so the appendix does too."""
        text = self.text
        starts = [match.start() for match in SCENE.finditer(text)] + [len(text)]
        for begin, end in zip(starts, starts[1:]):
            numbers = [int(match.group(1)) for match in ELEMENT.finditer(text[begin:end])]
            self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_every_element_has_a_slot_or_an_explicit_repeat(self):
        repeats = self.text.count('(powtórzenie elementu')
        slots = self.text.count('\n   PL:')
        self.assertEqual(slots, len(self.data['rows']) - repeats)
        self.assertEqual(slots, sum(1 for element in self.entry['elements'] if element['slot']))
        self.assertEqual(len(self.entry['elements']), len(self.data['rows']))

    def test_manifest_matches_the_rendered_file(self):
        self.assertEqual(self.manifest['schema'], 2)
        self.assertEqual(self.entry['sha256'],
                         __import__('hashlib').sha256(
                             self.entry['text'].encode('utf-8')).hexdigest())
        self.assertEqual(len(self.entry['elements']), len(ELEMENT.findall(self.text)))

    def test_v8_has_no_text_for_these_scenes(self):
        """Five of the six scenes had zero elements in v8; the sixth (`2010`) misses two lines.

        `2010` carried **275** elements until 2026-11-10. One of them was a stale block for
        `sdemo:49.0` in the older wording (`ワルキュー…`), printed although the appendix
        already carried that row correctly: the scene had 275 elements for 274 rows, so
        everything from #104 on sat one row off. `tools/reconcile_template_v8.py` removed
        that block, leaving 274 — still exactly two fewer than the 276 rows in the file.
        """
        counts: dict[str, int] = {}
        current = None
        for path in sorted(SCENY.glob('*.md')):
            if path.name == APPENDIX.name:
                continue
            for line in path.read_text(encoding='utf-8').splitlines():
                match = re.match(r'^## Scena \d+/\d+ — (cse\S+)$', line)
                if match:
                    current = match.group(1)
                    counts.setdefault(current, 0)
                elif current and ELEMENT.match(line):
                    counts[current] += 1
        empty = {'cse20_2000_0106300a', 'cse20_3000_0100000a', 'cse20_3499_0107410a',
                 'cse20_3738_0999900a', 'cse20_8000_0000300a'}
        for scene in empty:
            self.assertEqual(counts.get(scene, 0), 0, scene)
        self.assertEqual(counts['cse20_2010_0201710a'], 274)
        per_scene = {}
        for row in self.data['rows']:
            per_scene[row['scene']] = per_scene.get(row['scene'], 0) + 1
        self.assertEqual(per_scene['cse20_2010_0201710a'], 2)
        self.assertEqual(sum(per_scene.values()) - per_scene['cse20_2010_0201710a'],
                         len(self.data['rows']) - 2)

    def test_scene_headers_count_six(self):
        headers = SCENE.findall(self.text)
        self.assertEqual([number for number, _ in headers],
                         [f'D{i}/6' for i in range(1, 7)])


if __name__ == '__main__':
    unittest.main()
