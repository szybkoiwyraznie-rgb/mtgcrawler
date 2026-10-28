"""Source-bound synthetic checks for the owner's OE-style reading format."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_reading_y import fixture
from build_reading_y import Reader
import build_reading_oe_style as E


class ReadingOEStyleTests(unittest.TestCase):
    def setUp(self):
        self.graph, self.scenes, self.tables, self.plan = fixture()
        self.reader = Reader(self.graph, self.scenes, self.tables, [self.plan])
        self.mission = self.graph['missions'][0]

    def test_female_only_mission_flag_precedes_incidental_male_line(self):
        self.mission['missionOpenCond'] = [{'condType': 'Flag', 'paramString': 'M000B_FHERO'}]
        self.assertEqual(self.reader.protagonist_for_assets(self.reader.mission_assets(self.mission)), 'M')
        self.assertEqual(E.choice(self.reader, self.mission), 'F')

    def test_dialogue_and_game_tags_are_readable_without_changing_words(self):
        self.assertEqual(E.dialogue('「Witaj, $n!\nTu $kwbgrupa$kwe.」', 'Forte', 'Forte Tsukinowa'),
                         'Witaj, Forte! Tu grupa.')
        self.assertEqual(E.dialogue('（Myśl…）'), '*(Myśl…)*')

    def test_unmatched_player_reference_not_guessed_or_joined_across_presets(self):
        results, participants = E.deployments_for_mission(self.reader, self.mission)
        row = next(iter(results['Jednostki gracza']))
        self.assertIn('NIEROZPOZNANA REFERENCJA', row[0])
        self.assertIn('R1', participants['robot'])  # an explicit enemy record, not a guess
        # A register in a different preset must not be used for the first one.
        p = copy.deepcopy(self.graph['presets']['cab:7'])
        p['playerPlacementData'] = []
        p['enemyPlacementData'] = []
        p['rpObjectRegisterDatas'] = [{'rpRegister': [{'robotReferenceId': 'DYNAMIC_REF', 'robotBasisID': 'R1'}]}]
        self.graph['presets']['cab:8'] = p
        self.mission['composition'].append({'preset': 'cab:8'})
        results, _ = E.deployments_for_mission(self.reader, self.mission)
        self.assertTrue(any('NIEROZPOZNANA REFERENCJA' in row[0] for row in results['Jednostki gracza']))

    def test_source_bound_episode_has_readable_lines_no_per_line_ids(self):
        body, count = E.episode(self.reader, self.mission, 1)
        self.assertEqual(count, 1)
        self.assertIn('Pierwsza kwestia.', body)
        self.assertNotIn('### 0.1', body)
        self.assertIn('misje 1 i 2', body.lower())

    def test_pilot_and_mech_cards_contain_descriptions(self):
        robot = self.reader.definition('listRobotBaseData', 'R1', 'MissionData')
        pilot = self.reader.definition('listPilotBaseData', 'P1', 'MissionData')
        body = '\n'.join(E.robot_card(self.reader, robot, 'MissionData', set()) +
                         E.pilot_card(self.reader, pilot, 'MissionData', set()))
        for value in ('2000', '42', 'Opis zdolności', 'Opis rozkazu', 'Opis umiejętności', 'Broń próbna'):
            self.assertIn(value, body)
