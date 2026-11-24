"""Series of the scene-only speakers in `docs/srwoe_mission_deployments.md`.

Owner request (2026-11-23): in the section `Postacie wypowiadające się w
skrypcie sceny (bez obecności w deployment — bez statystyk)` every character
must show the series they come from. These tests keep the delivered document,
the generator rule and the surgical tool on the same line format, and check the
series is the character-dictionary value — not a guess.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import add_scene_speaker_series as SERIES  # noqa: E402
import mission_deployments as MD  # noqa: E402
import pl_release_package as R  # noqa: E402

DOC = ROOT / 'docs' / 'srwoe_mission_deployments.md'
UNRECORDED = MD.SCENE_SPEAKER_SERIES_UNRECORDED
BLOCKS = re.compile(
    r'^\*(?:Postacie wypowiadające się|Postać wypowiadająca się) w skrypcie sceny'
    r'[^\n]*\*\n((?:- [^\n]*\n)+)',
    re.M,
)


def bullets(doc: str) -> list[str]:
    return [line for block in BLOCKS.findall(doc) for line in block.splitlines()]


MISSION_RE = re.compile(r'^### (?:Odcinek \d+|Symulator) — .*?\(`([A-Z0-9_]+)`\)$', re.M)


def mission_sections(doc: str) -> dict[str, str]:
    """Mission body per code, split on the mission headings only (not on card h3s)."""
    marks = [(m.start(), m.group(1)) for m in MISSION_RE.finditer(doc)]
    return {code: doc[start:(marks[i + 1][0] if i + 1 < len(marks) else len(doc))]
            for i, (start, code) in enumerate(marks)}


class DocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = DOC.read_text(encoding='utf-8')

    def test_every_scene_speaker_shows_a_series(self) -> None:
        blocks = BLOCKS.findall(self.doc)
        self.assertEqual(len(blocks), 221)
        lines = bullets(self.doc)
        self.assertEqual(len(lines), 4363)
        for line in lines:
            self.assertRegex(line, r'^- .+ — seria: .+$', line)
            # one series per bullet: the dictionary may give several titles,
            # they are joined with '; ', never with a second ' — seria: '
            self.assertEqual(line.count(' — seria: '), 1, line)
        self.assertEqual(sum(1 for line in lines if line.endswith(' — seria: ' + UNRECORDED)), 74)

    def test_series_come_from_the_character_dictionary(self) -> None:
        lines = set(bullets(self.doc))
        for expected in (
            '- Fraw Bow — seria: Mobile Suit Gundam',
            '- Sayla Mass — seria: Mobile Suit Gundam',
            '- Himari Yaegaki — seria: Super Robot Wars Original',
            '- Masaki Andoh — seria: Super Robot Wars Original',
            '- Fiona Elisi Linette — seria: Zoids: Chaotic Century',
            '- Christina Mackenzie — seria: Mobile Suit Gundam 0080: War in the Pocket',
            '- Maria Shiratori — seria: Matchless Raijin-Oh',
            '- Shiro — seria: Super Robot Wars Original',
            'Oficer Federacji — seria: ' + UNRECORDED,
            '??? — seria: ' + UNRECORDED,
        ):
            self.assertIn(expected if expected.startswith('- ') else '- ' + expected, lines)

    def test_two_characters_sharing_a_nickname_keep_their_own_series(self) -> None:
        # `Shiro Amada` (nickname `Shiro`) and the OG `Shiro` both speak in
        # DL209_13 and neither is deployed there, so both appear in the name
        # list — each with its own series. The nickname must never decide.
        section = mission_sections(self.doc)['DL209_13']
        self.assertIn('\n- Shiro — seria: Super Robot Wars Original\n', section)
        self.assertIn('\n- Shiro Amada — seria: Mobile Suit Gundam: The 08th MS Team\n', section)
        # Deployed characters keep a full card whose `**Seria:**` line comes
        # from the pilot catalogue and never carries the list annotation.
        self.assertIn('\n#### Shiro Amada\n', self.doc)
        self.assertIn('\n**Seria:** Mobile Suit Gundam: The 08th MS Team\n', self.doc)

    def test_generator_line_format(self) -> None:
        self.assertEqual(MD.scene_speaker_line('Fraw Bow', 'Mobile Suit Gundam'),
                         '- Fraw Bow — seria: Mobile Suit Gundam')
        self.assertEqual(MD.scene_speaker_line('Bandit', None), f'- Bandit — seria: {UNRECORDED}')
        self.assertEqual(MD.scene_speaker_line('Bandit', ''), f'- Bandit — seria: {UNRECORDED}')
        self.assertIn('scene_speaker_line(char_names_pl[cid]', (ROOT / 'tools' / 'mission_deployments.py').read_text(encoding='utf-8'))


class DictionaryTests(unittest.TestCase):
    """The series map is read from the repo-only materialized package."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.polish = Path(cls.tmp.name) / 'pakiet_PL'
        R.materialize(ROOT / 'pakiet_EN', ROOT / 'pakiet_PL', cls.polish)
        cls.series = MD.load_character_series(cls.polish)
        cls.index = SERIES.SpeakerIndex(ROOT / 'pakiet_EN', cls.polish)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_series_map_skips_the_nodata_row(self) -> None:
        self.assertNotIn(65535, self.series)
        self.assertEqual(self.series[500], 'Matchless Raijin-Oh')
        self.assertEqual(self.series[4424], 'Super Robot Wars Original')  # scene-only `Shiro`
        self.assertEqual(self.series[1401], 'Mobile Suit Gundam: The 08th MS Team')

    def test_resolution_is_mission_scoped(self) -> None:
        self.assertEqual(self.index.series_for('DL100_02', 'eventP00.cpk', 'Fraw Bow'),
                         'Mobile Suit Gundam')
        self.assertEqual(self.index.series_for('DL100_01', 'eventP00.cpk', 'Himari Yaegaki'),
                         'Super Robot Wars Original')
        # Both the OG `Shiro` and `Shiro Amada` (whose nickname is `Shiro`)
        # speak in DL209_13; the primary name decides, never the nickname.
        self.assertEqual(self.index.series_for('DL209_13', 'eventP02.EDAT', 'Shiro'),
                         'Super Robot Wars Original')
        self.assertEqual(self.index.series_for('DL209_13', 'eventP02.EDAT', 'Shiro Amada'),
                         'Mobile Suit Gundam: The 08th MS Team')
        # A character the dictionary has no series for keeps the documented label.
        code, name = next((code, line[2:-len(' — seria: ' + UNRECORDED)])
                          for code, section in mission_sections(DOC.read_text(encoding='utf-8')).items()
                          for line in section.splitlines()
                          if line.endswith(' — seria: ' + UNRECORDED))
        self.assertEqual(self.index.series_for(code, None, name), UNRECORDED)
        with self.assertRaises(SystemExit):
            self.index.series_for('DL100_01', 'eventP00.cpk', 'Nie ma takiej postaci')

    def test_rewrite_is_idempotent_on_the_delivered_document(self) -> None:
        text = DOC.read_text(encoding='utf-8')
        rewritten, report = SERIES.rewrite(text, self.index, notes=False)
        self.assertEqual(report['blocks'], 221)
        self.assertEqual(report['already'], 4363)
        self.assertEqual(report['names'], 0)
        self.assertEqual(rewritten, text)

    def test_rewrite_annotates_both_heading_forms(self) -> None:
        text = (
            '# T\n\n'
            '### Odcinek 0 — Na ratunek White Base (`DL100_02`)\n\n'
            '**Źródło:** `eventP00.cpk/DL100_02_Entry.dat`\n\n'
            '*Postać wypowiadająca się w skrypcie sceny (bez obecności w deployment — bez statystyk):*\n'
            '- Fraw Bow\n\n'
            '### Odcinek 1 — X (`DL101_11`)\n\n'
            '**Źródło:** `eventP00.cpk/DL101_11_Entry.dat`\n\n'
            '*Postacie wypowiadające się w skrypcie sceny (bez obecności w deployment — bez statystyk):*\n'
            '- Asuma Shinohara\n- Suol Douglas\n\n'
        )
        rewritten, report = SERIES.rewrite(text, self.index, notes=False)
        self.assertEqual(report['blocks'], 2)
        self.assertEqual(report['names'], 3)
        self.assertIn('- Fraw Bow — seria: Mobile Suit Gundam\n', rewritten)
        self.assertIn('- Asuma Shinohara — seria: Mobile Police Patlabor\n', rewritten)
        self.assertIn('- Suol Douglas — seria: Super Robot Wars Original\n', rewritten)
        # The prose notes are only rewritten when the pinned document carries them.
        with self.assertRaises(SystemExit):
            SERIES.rewrite(text, self.index)
        # Unknown names stop the run instead of getting an invented series.
        broken = text + ('*Postacie wypowiadające się w skrypcie sceny'
                         ' (bez obecności w deployment — bez statystyk):*\n- Nobody Here\n')
        with self.assertRaises(SystemExit):
            SERIES.rewrite(broken, self.index, notes=False)

    def test_tool_report_matches_the_document(self) -> None:
        report_path = ROOT / 'docs' / 'mission-deployments-scene-series-2026-11-23.json'
        self.assertTrue(report_path.is_file(), 'brak raportu narzędzia dla dostarczonego dokumentu')
        report = json.loads(report_path.read_text(encoding='utf-8'))
        self.assertEqual(report['sections'], 224)
        self.assertEqual(report['blocks'], 221)
        self.assertEqual(report['names'], 4363)
        self.assertEqual(report['unrecorded'], 74)
        self.assertEqual(report['output_sha256'], SERIES.sha(DOC.read_bytes()))


if __name__ == '__main__':
    unittest.main()
