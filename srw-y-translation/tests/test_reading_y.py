"""Synthetic Y reading graph / editions, no assets or text from OE or Y."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import reading_index as IX
import build_reading_y as R
from pl_import import source_fingerprints


def object_(file, identity, tree, externals=()):
    return {'file': file, 'path_id': identity, 'tree': tree,
            'externals': list(externals), 'bundle_sha256': 'fixture-sha'}


def fixture():
    records = {
        'PilotBasicDatas': {'listPilotBaseData': [{'id': 'P1', 'facialId': 'F1',
            'parameters': {'sp': 42}, 'aceBonusId': 'AB1',
            'growSpirits': [{'id': 'SP1', 'mastaryLevel': 8, 'cost': 12}],
            'growSkills': [{'skillId': 'SK1', 'mastaryLevels': [1, 10]}]}],
            'listFacialSettingData': [{'id': 'F1', 'nameKey': 'PN'}],
            'listSpiritCommandData': [{'id': 'SP1', 'nameKey': 'SN', 'descriptionKey': 'SD'}],
            'listPilotSkillData': [{'id': 'SK1', 'nameKey': 'KN', 'descriptionKey': 'KD'}]},
        'RobotBasicDatas': {'listRobotBaseData': [{'id': 'R1', 'displayNameKey': 'RN',
            'parameters': {'hp': 2000}, 'customBonusId': 'CB1',
            'skills': [{'id': 'RS1', 'nameKey': 'AN', 'descriptionKey': 'AD'}],
            'weapons': [{'id': 'W1', 'displayNameKey': 'WN', 'power': 3000, 'rangeMin': 1,
                         'rangeMax': 4, 'costEn': 10, 'bullet': 3}]}]}}
    shared = {'pilot_name': {'PN': 'k1'}, 'robot_name': {'RN': 'k2'},
        'spirit_command': {'SN': 'k3', 'SD': 'k4'}, 'skill_active': {'KN': 'k5', 'KD': 'k6'},
        'ace_bonus': {'AB1': 'k7'}, 'custom_bonus': {'CB1': 'k8'},
        'weapon_name': {'WN': 'k9'}, 'active_ability': {'AN': 'k10', 'AD': 'k11'},
        'mission_title': {'MT': 'k12'}}
    tables = []
    pl = ['Łucja', 'Mech próbny', 'Rozkaz', 'Opis rozkazu', 'Umiejętność', 'Opis umiejętności',
          'Bonus asa', 'Bonus modyfikacji', 'Broń próbna', 'Zdolność', 'Opis zdolności', 'Misja próbna']
    translations = {}
    for owner, entries in shared.items():
        for key in entries.values():
            i = int(key[1:])
            row = {'table': owner, 'key': key, 'index': i, 'jp': '架空', 'en': 'NO_EN_FALLBACK'}
            tables.append(row)
            translations.setdefault(owner, {})[key] = {'jp': row['jp'], 'en': row['en'], 'pl': pl[i-1]}
    scenarios = [{'id': f'scenario:x_sdemo.lua:0.1#{i}', 'file': 'x_sdemo.lua',
                  'scene': 'x', 'kind': 'sdemo', 'pack': 'base', 'string_id': '0.1',
                  'jp': '仮', 'en': 'NO_SCENE_EN', 'speaker_jp': '', 'branch': 'F' if i == 2 else 'M'}
                 for i in (1, 2)]
    graph = {'schema': 1, 'records': records, 'shared': shared, 'issues': [],
        'scenario_order': {'x_sdemo.lua': ['0.1#2', '0.1#1']},
        'missions': [{'id': 'm0001_0000001', 'title': 'MT', 'chapterNo': 1,
            'collection': 'MissionData', 'composition': [{'sdemo_file': 'x_sdemo',
            'dlgev_file': '', 'script_file': 's1', 'preset': 'cab:7'}]}],
        'presets': {'cab:7': {'name': 'preset', 'enemyPlacementData': [{'execNo': 100,
            'enemyPlacement': [{'robotBasisID': 'R1', 'pilotBasisID': 'P1', 'flagCondition': [{'flag': 'F1'}]}]}],
            'playerPlacementData': [{'execNo': 0, 'playerPlacement': [{'robotReferenceId': 'DYNAMIC_REF'}]}],
            'rpObjectRegisterDatas': [{'execNo': 7, 'rpRegister': [{'control': 'RideOn',
                'subpilotList': [{'pilotReferenceId': 'SUB_REF'}]}]}]}}}
    plan = {'schema': 1, 'tables': translations, 'scenes': {'x_sdemo.lua': {
        '0.1#1': {'jp': '仮', 'en': 'NO_SCENE_EN', 'pl': 'Pierwsza kwestia.'}}}}
    return graph, scenarios, tables, plan


class IndexTests(unittest.TestCase):
    def test_external_unity_pointer_is_not_just_a_path_id(self):
        owner = object_('a', 1, {}, ['b'])
        right, wrong = object_('b', 7, {'m_Name': 'right'}), object_('c', 7, {'m_Name': 'wrong'})
        mapping = {('b', 7): right, ('c', 7): wrong}
        self.assertIs(IX.pointer(owner, {'m_FileID': 1, 'm_PathID': 7}, mapping), right)
        self.assertIsNone(IX.pointer(owner, {'m_FileID': 2, 'm_PathID': 7}, mapping))
        self.assertIsNone(IX.pointer(owner, {'m_FileID': 1, 'm_PathID': 0}, mapping))

    def test_shared_keys_use_table_and_full_64bit_id(self):
        obj = object_('a', 1, {'m_Name': 'pilot_name Shared Data',
                              'm_Entries': [{'m_Id': 0x12345678ABCDEF01, 'm_Key': 'PN'}]})
        graph = IX.compile_index([obj])
        self.assertEqual(graph['shared']['pilot_name']['PN'], '12345678:abcdef01')

    def test_mission_preset_link_is_exact_pointer_not_similar_name(self):
        mission = object_('a', 1, {'m_Name': 'MissionData', 'missionRomList': [
            {'id': 'm0001_0000001', 'composition': [{'preset_file': {'m_FileID': 1, 'm_PathID': 7}}]}]}, ['b'])
        preset = object_('b', 7, {'m_Name': 'unrelated_name_preset'})
        graph = IX.compile_index([mission, preset])
        self.assertEqual(graph['missions'][0]['composition'][0]['preset'], 'b:7')
        self.assertEqual(graph['stats']['preset_links'], 1)

    def test_missing_preset_is_counted_not_guessed_from_mission_id(self):
        obj = object_('a', 1, {'m_Name': 'MissionData', 'missionRomList': [
            {'id': 'm0001_0000001', 'composition': [{'preset_file': {'m_FileID': 1, 'm_PathID': 9}}]}]}, ['missing'])
        graph = IX.compile_index([obj])
        self.assertIsNone(graph['missions'][0]['composition'][0]['preset'])
        self.assertEqual(graph['stats']['unresolved_preset_links'], 1)

    def test_global_preset_is_not_a_story_mission(self):
        obj = object_('a', 1, {'m_Name': 'MissionData', 'missionRomList': [{'id': 'mission_global_preset'}]})
        graph = IX.compile_index([obj])
        self.assertEqual(graph['missions'], [])
        self.assertEqual(graph['stats']['system_entries'], 1)

    def test_conflicting_pointer_and_master_data_are_refused(self):
        a = object_('a', 1, {'m_Name': 'PilotBasicDatas', 'listPilotBaseData': [{'id': 'P1'}]})
        b = object_('a', 1, {'m_Name': 'different'})
        with self.assertRaises(ValueError):
            IX.compile_index([a, b])
        c = object_('b', 2, {'m_Name': 'PilotBasicDatas', 'listPilotBaseData': [{'id': 'P2'}]})
        with self.assertRaises(ValueError):
            IX.compile_index([a, c])

    def test_dlc_redefinitions_stay_separate(self):
        a = object_('a', 1, {'m_Name': 'PilotBasicDatas', 'listPilotBaseData': [{'id': 'P1'}]})
        b = object_('b', 2, {'m_Name': 'PilotBasicDatas_DlcOf1', 'listPilotBaseData': [{'id': 'P1', 'value': 2}]})
        self.assertEqual(IX.compile_index([a, b])['stats']['pilots'], 2)


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.g, self.scenes, self.tables, self.plan = fixture()

    def reader(self, plans=None):
        return R.Reader(self.g, self.scenes, self.tables, [self.plan] if plans is None else plans)

    def test_partial_translation_does_not_fall_back_to_english_or_japanese_prose(self):
        files = self.reader().render()
        text = '\n'.join(files.values())
        self.assertIn('Pierwsza kwestia.', text)
        self.assertIn('BRAK PL', text)
        self.assertNotIn('NO_EN_FALLBACK', text)
        self.assertNotIn('NO_SCENE_EN', text)
        self.assertNotIn('架空', text)

    def test_exact_occurrence_order_and_both_protagonist_variants(self):
        text = self.reader().scenes()['rozdzial-01.md']
        self.assertLess(text.index('0.1\\#2'), text.index('0.1\\#1'))
        self.assertIn('wariant: bohaterka', text)
        self.assertIn('wariant: bohater', text)

    def test_unassigned_scene_never_disappears(self):
        self.g['missions'] = []
        files = self.reader().scenes()
        self.assertIn('sceny-bez-misji.md', files)
        self.assertIn('Pierwsza kwestia.', files['sceny-bez-misji.md'])

    def test_no_original_script_order_is_explicitly_unverified(self):
        self.g['scenario_order'] = {}
        self.assertIn('brak weryfikacji', self.reader().scenes()['rozdzial-01.md'])

    def test_incomplete_original_order_refused(self):
        self.g['scenario_order']['x_sdemo.lua'] = ['0.1#1']
        with self.assertRaisesRegex(ValueError, 'incomplete Lua order'):
            self.reader().scenes()

    def test_pilot_skills_spirit_levels_and_costs_are_joined_by_id(self):
        text = self.reader().pilots()
        for expected in ['Łucja', 'Opis rozkazu', 'Opis umiejętności', 'Poziom nauki: 8', 'koszt: 12', 'Bonus asa']:
            self.assertIn(expected, text)

    def test_mech_weapons_and_abilities(self):
        text = self.reader().robots()
        for expected in ['Mech próbny', 'Broń próbna', '3000', 'Opis zdolności', 'Bonus modyfikacji']:
            self.assertIn(expected, text)

    def test_runtime_reference_is_not_silently_used_as_basis(self):
        text = self.reader().deployments()
        self.assertIn('DYNAMIC', text)
        self.assertIn('execNo 100', text)
        self.assertIn('SUB', text)
        self.assertIn('nie symulacja', text)
        self.assertIn('flagCondition', text)
        self.assertIn('Łucja', text)  # resolved only through explicit pilotBasisID

    def test_conflicting_plans_or_stale_sources_are_refused(self):
        other = copy.deepcopy(self.plan)
        other['scenes']['x_sdemo.lua']['0.1#1']['pl'] = 'Inna kwestia'
        with self.assertRaisesRegex(ValueError, 'conflicting translation'):
            self.reader([self.plan, other])
        other['scenes']['x_sdemo.lua']['0.1#1']['jp'] = '別'
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.reader([other])

    def test_empty_translation_plan_entry_is_not_a_fallback(self):
        self.plan['scenes']['x_sdemo.lua']['0.1#1']['pl'] = ''
        with self.assertRaisesRegex(ValueError, 'empty'):
            self.reader()

    def test_dlc_scope_first_then_base_never_arbitrary_other_dlc(self):
        self.g['shared']['pilot_name-DLC1'] = {'PN': 'd1'}
        reader = self.reader()
        value = reader.localized('pilot_name', 'PN', 'PilotBasicDatas_DlcOf1')
        self.assertIn('pilot_name-DLC1/d1', value)
        self.assertEqual(reader.localized('pilot_name', 'PN', 'PilotBasicDatas_DlcOf2'), 'Łucja')
        self.assertIsNone(reader.definition('unknown', 'P1', 'PilotBasicDatas'))

    def test_ambiguous_definitions_are_refused(self):
        self.g['records']['PilotBasicDatas']['listPilotSkillData'].append(
            {'id': 'SK1', 'nameKey': 'different'})
        with self.assertRaisesRegex(ValueError, 'ambiguous definition'):
            self.reader().pilots()

    def test_markdown_and_html_in_translation_cannot_inject_structure(self):
        self.plan['scenes']['x_sdemo.lua']['0.1#1']['pl'] = '<script>bad</script>\n# heading\n[text](url)'
        text = self.reader().scenes()['rozdzial-01.md']
        self.assertNotIn('<script>', text)
        self.assertIn('&lt;script&gt;', text)
        self.assertIn('> \\# heading', text)

    def test_archive_timestamps_and_order_are_fixed(self):
        one = R.archive_bytes({'b.md': 'B', 'a.md': 'Ł'})
        self.assertEqual(one, R.archive_bytes({'a.md': 'Ł', 'b.md': 'B'}))


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = self.root / 's6'
        self.sources.mkdir()
        graph, scenes, tables, plan = fixture()
        for name, rows in [('scenario.jsonl', scenes), ('tables.jsonl', tables)]:
            (self.sources / name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
        self.graph = self.root / 'index.json'
        self.graph.write_text(json.dumps(graph), encoding='utf-8')
        plan['source_sha256'] = source_fingerprints(self.sources)
        self.plan = self.root / 'accepted.json'
        self.plan.write_text(json.dumps(plan), encoding='utf-8')

    def build(self, target):
        return R.build(self.sources, self.graph, [self.plan], target)

    def test_full_synthetic_build_is_byte_reproducible_and_zip_matches_md(self):
        a, b = self.root / 'first', self.root / 'second'
        first, second = self.build(a), self.build(b)
        self.assertEqual(first, second)
        self.assertEqual((a / 'srwy_reading_PL.zip').read_bytes(), (b / 'srwy_reading_PL.zip').read_bytes())
        with zipfile.ZipFile(a / 'srwy_reading_PL.zip') as z:
            for name in z.namelist():
                self.assertEqual(z.read(name), (a / name).read_bytes())
        self.assertFalse(first['runtime_tested'])
        self.assertTrue(first['untranslated_or_unlinked'])

    def test_stale_snapshot_refused_before_creating_output(self):
        (self.sources / 'tables.jsonl').write_text('\n', encoding='utf-8')
        target = self.root / 'out'
        with self.assertRaises(ValueError):
            self.build(target)
        self.assertFalse(target.exists())

    def test_refuses_overwrite_and_source_overlap(self):
        target = self.root / 'out'
        self.build(target)
        before = (target / 'srwy_reading_PL.zip').read_bytes()
        with self.assertRaises(ValueError):
            self.build(target)
        self.assertEqual((target / 'srwy_reading_PL.zip').read_bytes(), before)
        with self.assertRaises(ValueError):
            self.build(self.sources / 'out')

    def test_publish_failure_leaves_no_partial_output(self):
        target = self.root / 'out'
        with patch.object(R.os, 'rename', side_effect=OSError('injected failure')):
            with self.assertRaises(OSError):
                self.build(target)
        self.assertFalse(target.exists())
        self.assertFalse(list(self.root.glob('.reading-*')))


if __name__ == '__main__':
    unittest.main()
