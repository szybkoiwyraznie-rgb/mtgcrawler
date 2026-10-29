"""Source-bound synthetic checks for the owner's OE-style reading format."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

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

    def test_cross_preset_registration_resolves_without_cross_mission_guess(self):
        results, participants = E.deployments_for_mission(self.reader, self.mission)
        self.assertTrue(any(row[0] == '[Jednostka nieustalona]' for row in results['Jednostki gracza']))
        p = copy.deepcopy(self.graph['presets']['cab:7'])
        p['playerPlacementData'] = []
        p['enemyPlacementData'] = []
        p['rpObjectRegisterDatas'] = [{'rpRegister': [{'robotReferenceId': 'DYNAMIC_REF', 'robotBasisID': 'R1'}]}]
        self.graph['presets']['cab:8'] = p
        # A separate mission must not influence this mission.
        other = copy.deepcopy(self.mission)
        other['composition'] = [{'preset': 'cab:8'}]
        results, _ = E.deployments_for_mission(self.reader, self.mission)
        self.assertTrue(any(row[0] == '[Jednostka nieustalona]' for row in results['Jednostki gracza']))
        # Explicit registration in another preset of the same mission is evidence.
        self.mission['composition'].append({'preset': 'cab:8'})
        results, participants = E.deployments_for_mission(self.reader, self.mission)
        self.assertTrue(any(row[0] == 'R1' for row in results['Jednostki gracza']))
        self.assertIn('R1', participants['robot'])

    def test_ambiguous_cross_preset_reference_does_not_invent_unit(self):
        p = copy.deepcopy(self.graph['presets']['cab:7'])
        p['playerPlacementData'] = []
        p['enemyPlacementData'] = []
        p['rpObjectRegisterDatas'] = [{'rpRegister': [
            {'robotReferenceId': 'DYNAMIC_REF', 'robotBasisID': 'R1'},
            {'robotReferenceId': 'DYNAMIC_REF', 'robotBasisID': 'R2'},
        ]}]
        self.graph['presets']['cab:8'] = p
        self.mission['composition'].append({'preset': 'cab:8'})
        with patch.object(E, 'name_for', side_effect=lambda reader, kind, identity, scope: identity):
            results, _ = E.deployments_for_mission(self.reader, self.mission)
        self.assertTrue(any(row[0] == '[Jednostka nieustalona]' for row in results['Jednostki gracza']))

    def test_actual_source_row_distinguishes_reserved_key_from_missing_translation(self):
        self.tables.extend([
            {'table': 'dic_text_robot', 'key': 'present', 'jp': 'JP', 'en': 'EN'},
            {'table': 'dic_text_robot', 'key': 'blank', 'jp': '', 'en': ''},
        ])
        links = {'schema': 1, 'robots': {'R1': {'text_id': 'TEXT', 'source': 'fixture'}},
                 'groups': {'robot': {'TEXT': [
                     {'table': 'dic_text_robot', 'address': 'reserved'},
                     {'table': 'dic_text_robot', 'address': 'blank'},
                     {'table': 'dic_text_robot', 'address': 'present'},
                 ]}}}
        reader = Reader(self.graph, self.scenes, self.tables, [self.plan], links=links)
        result = '\n'.join(E.first_dictionary(reader, 'robot', ('R1',), set()))
        self.assertNotIn('reserved', result)
        self.assertNotIn('blank', result)
        self.assertIn('[Brak polskiego opisu]', result)
        self.assertEqual(reader.missing, {('table', 'dic_text_robot', 'present')})

    def test_missing_source_table_is_not_silently_treated_as_absent_row(self):
        links = {'schema': 1, 'robots': {'R1': {'text_id': 'TEXT', 'source': 'fixture'}},
                 'groups': {'robot': {'TEXT': [{'table': 'not_loaded', 'address': 'key'}]}}}
        reader = Reader(self.graph, self.scenes, self.tables, [self.plan], links=links)
        result = '\n'.join(E.first_dictionary(reader, 'robot', ('R1',), set()))
        self.assertIn('[Nie odczytano tabeli encyklopedii]', result)
        self.assertNotIn('nie ma tekstu', result)

    def test_default_reference_is_base_profile_only_with_consistent_names(self):
        base = self.graph['records']['RobotBasicDatas']['listRobotBaseData'][0]
        base['defaultReferenceId'] = 'R1'
        self.graph['presets']['cab:7']['playerPlacementData'][0]['playerPlacement'][0]['robotReferenceId'] = 'R1'
        reader = Reader(self.graph, self.scenes, self.tables, [self.plan])
        results, _ = E.deployments_for_mission(reader, self.mission)
        self.assertTrue(any(row[0] == 'R1' for row in results['Jednostki gracza']))
        # A second record declaring the same reference but a different name
        # makes it ambiguous, even though the base ID happens to match.
        alt = copy.deepcopy(base)
        alt['id'], alt['displayNameKey'] = 'R2', 'RN2'
        self.graph['records']['RobotBasicDatas']['listRobotBaseData'].append(alt)
        reader = Reader(self.graph, self.scenes, self.tables, [self.plan])
        with patch.object(E, 'name_for', side_effect=lambda reader, kind, identity, scope: identity):
            results, _ = E.deployments_for_mission(reader, self.mission)
        self.assertTrue(any(row[0] == '[Jednostka nieustalona]' for row in results['Jednostki gracza']))

    def test_facial_default_alias_requires_both_matching_name_keys(self):
        faces = self.graph['records']['PilotBasicDatas']['listFacialSettingData']
        faces[:] = [{'id': 'F1', 'defaultReferenceId': 'F0', 'nameKey': 'PN', 'fullNameKey': 'PF'},
                    {'id': 'F0', 'defaultReferenceId': 'F0', 'nameKey': 'PN', 'fullNameKey': 'PF'}]
        reader = Reader(self.graph, self.scenes, self.tables, [self.plan])
        self.assertEqual(E.facial_dictionary_ids(reader, 'F1', 'MissionData'), ('F1', 'F0'))
        faces[1]['fullNameKey'] = 'OTHER'
        self.assertEqual(E.facial_dictionary_ids(reader, 'F1', 'MissionData'), ('F1', None))

    def test_aligned_tables_without_escapes(self):
        table = E.rows_table(['Slot', 'Nazwa', 'Opis'], [(1, 'Żółw', 'Opis'), (20, 'Rakieta', 'Długi opis')])
        lines = table[:-1]
        self.assertEqual(len({len(line) for line in lines}), 1)
        self.assertEqual(len({tuple(i for i, c in enumerate(line) if c == '|') for line in lines}), 1)
        self.assertNotIn('\\', '\n'.join(lines))

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
