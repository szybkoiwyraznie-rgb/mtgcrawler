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
        'scenario_texts': {'x_sdemo.lua': {'0.1#1': ['仮'], '0.1#2': ['仮']}},
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

    def test_source_mission_mode_and_null_pointer_are_preserved(self):
        obj = object_('a', 1, {'m_Name': 'MissionData', 'missionRomList': [
            {'id': 'm0001_0000001', 'serifuOnly': 1,
             'composition': [{'preset_file': {'m_FileID': 0, 'm_PathID': 0}}]}]})
        mission = IX.compile_index([obj])['missions'][0]
        self.assertEqual(mission['serifuOnly'], 1)
        self.assertEqual(mission['source_index'], 0)
        self.assertEqual(mission['composition'][0]['preset_pointer'], {'m_FileID': 0, 'm_PathID': 0})

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

    def test_lua_order_carries_source_text_identity_and_locale_alternatives(self):
        a = object_('a', 1, {'m_Name': 'x.lua', 'reading_units': [{'key': '0.1#1', 'text': '仮'}]})
        b = object_('b', 2, {'m_Name': 'x.lua', 'reading_units': [{'key': '0.1#1', 'text': 'Synthetic'}]})
        graph = IX.compile_index([a, b])
        self.assertEqual(graph['scenario_order']['x.lua'], ['0.1#1'])
        self.assertEqual(set(graph['scenario_texts']['x.lua']['0.1#1']), {'仮', 'Synthetic'})

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
        del self.plan['tables']['ace_bonus']['k7']
        files = self.reader().render()
        text = '\n'.join(files.values())
        self.assertIn('Pierwsza kwestia.', text)
        self.assertIn('BRAK PL', text)
        self.assertNotIn('NO_EN_FALLBACK', text)
        self.assertNotIn('NO_SCENE_EN', text)
        self.assertNotIn('架空', text)

    def test_male_default_excludes_female_variant(self):
        text = self.reader().scenes()['rozdzial-01.md']
        self.assertNotIn('0.1\\#2', text)
        self.assertNotIn('wariant: bohaterka', text)
        self.assertIn('wariant: bohater', text)

    def test_female_only_mission_uses_female_and_shared_lines(self):
        self.scenes[0]['branch'] = None
        text = self.reader().scenes()['rozdzial-01.md']
        self.assertIn('Wariant misji: bohaterka', text)
        self.assertIn('Pierwsza kwestia.', text)
        self.assertLess(text.index('0.1\\#2'), text.index('0.1\\#1'))

    def test_missing_japanese_row_cannot_turn_mixed_mission_into_female_only(self):
        self.scenes[0]['jp'] = None
        reader = self.reader(plans=[])
        text = reader.scenes()['rozdzial-01.md']
        self.assertIn('Wariant misji: bohater.', text)
        self.assertNotIn('wariant: bohaterka', text)

    def test_gender_is_selected_over_whole_mission_not_each_file(self):
        row = copy.deepcopy(self.scenes[1])
        row['file'] = 'female.lua'
        row['id'] = 'scenario:female.lua:0.1#2'
        self.scenes.append(row)
        self.g['scenario_order']['female.lua'] = ['0.1#2']
        self.g['scenario_texts']['female.lua'] = {'0.1#2': ['仮']}
        self.g['missions'][0]['composition'][0]['dlgev_file'] = 'female.lua'
        text = self.reader().scenes()['rozdzial-01.md']
        self.assertNotIn('wariant: bohaterka', text)
        self.assertNotIn('0.1\\#2', text)

    def test_locale_orders_are_selected_by_exact_source_identity(self):
        self.g['scenario_variants'] = {'x_sdemo.lua': [
            {'units': [{'key': '0.1#1', 'text': 'NO_SCENE_EN'},
                       {'key': '0.1#2', 'text': 'NO_SCENE_EN'}], 'origin': {'file': 'en'}},
            {'units': [{'key': '0.1#2', 'text': '仮'},
                       {'key': '0.1#1', 'text': '仮'}], 'origin': {'file': 'jp'}}]}
        self.scenes[0]['branch'] = None
        reader = self.reader()
        text = reader.scenes()['rozdzial-01.md']
        self.assertLess(text.index('0.1\\#2'), text.index('0.1\\#1'))
        self.assertEqual(reader.verified_order['x_sdemo.lua']['matched_language'], 'jp')
        self.g['scenario_variants']['x_sdemo.lua'].append(
            {'units': list(reversed(self.g['scenario_variants']['x_sdemo.lua'][1]['units'])), 'origin': {}})
        with self.assertRaisesRegex(ValueError, 'ambiguous matched Lua order'):
            self.reader().render()

    def event_variant(self):
        self.scenes[0]['table'] = 1
        self.scenes[1]['table'] = 2
        variant = {'units': [{'key': '0.1#2', 'text': '仮', 'table': 2},
                             {'key': '0.1#1', 'text': '仮', 'table': 1}],
                   'origin': {'file': 'jp'},
                   'event_registry': {'status': 'verified-static-registry',
                       'entries': [{'table': 1, 'event_id': 100}, {'table': 2, 'event_id': 200}],
                       'chronology_verified': False}}
        self.g['scenario_variants'] = {'x_sdemo.lua': [variant]}
        return variant

    def test_event_table_identity_is_bound_before_gender_filtering(self):
        self.event_variant()
        self.scenes[1]['table'] = 999  # excluded female line still must validate
        with self.assertRaisesRegex(ValueError, 'Lua event table does not match S6'):
            self.reader().render()

    def test_distinct_registries_cannot_be_merged_even_with_matching_text(self):
        variant = self.event_variant()
        other = copy.deepcopy(variant)
        other['event_registry']['entries'][0]['event_id'] = 777
        self.g['scenario_variants']['x_sdemo.lua'].append(other)
        with self.assertRaisesRegex(ValueError, 'ambiguous matched event registry'):
            self.reader().render()

    def test_event_block_heading_never_claims_trigger_chronology(self):
        self.event_variant()
        text = self.reader().scenes()['rozdzial-01.md']
        self.assertIn('ID rejestru: 100', text)
        self.assertIn('nie chronologię wywołań', text)
        self.assertNotIn('ID rejestru: 200', text)

    def test_unassigned_scene_never_disappears(self):
        self.g['missions'] = []
        files = self.reader().scenes()
        self.assertIn('sceny-bez-misji.md', files)
        self.assertIn('Pierwsza kwestia.', files['sceny-bez-misji.md'])

    def test_default_mode_refuses_unverified_order(self):
        self.g['scenario_order'] = {}
        with self.assertRaisesRegex(ValueError, 'missing verified Lua order'):
            self.reader().scenes()

    def test_release_mode_refuses_unverified_order(self):
        self.g['scenario_order'] = {}
        reader = R.Reader(self.g, self.scenes, self.tables, [self.plan], require_order=True)
        with self.assertRaisesRegex(ValueError, 'missing verified Lua order'):
            reader.render()

    def test_speaker_is_localized_only_by_exact_pid_not_japanese_name(self):
        row = dict(self.scenes[0], pid='P1', speaker_jp='fake name')
        self.assertEqual(self.reader().speaker(row), 'Łucja')
        row['pid'] = 'UNKNOWN'
        self.assertIn('BRAK POWIĄZANIA', self.reader().speaker(row))

    def test_incomplete_original_order_refused(self):
        self.g['scenario_order']['x_sdemo.lua'] = ['0.1#1']
        with self.assertRaisesRegex(ValueError, 'incomplete Lua order'):
            self.reader().scenes()

    def test_lua_order_from_another_text_revision_is_refused(self):
        self.g['scenario_texts']['x_sdemo.lua']['0.1#1'] = ['別']
        with self.assertRaisesRegex(ValueError, 'Lua source text does not match S6'):
            self.reader().render()

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
        self.assertNotIn('execNo', text)
        self.assertIn('SUB', text)
        self.assertIn('nie symulacja', text)
        self.assertIn('warunkowe warianty', text)
        self.assertIn('Łucja', text)  # resolved only through explicit pilotBasisID

    def test_participants_resolve_only_explicit_mission_assignments_and_deduplicate(self):
        preset = self.g['presets']['cab:7']
        preset['rpObjectRegisterDatas'][0]['rpRegister'] += [
            {'robotReferenceId': 'DYNAMIC_REF', 'robotBasisID': 'R1',
             'pilotReferenceId': 'UNRELATED', 'pilotBasisID': 'P1'},
            {'pilotReferenceId': 'UNRELATED'}, {'pilotReferenceId': 'P1'},
            {'subpilotList': [{'pilotBasisID': 'P1'}]}]
        participants, unresolved = self.reader().mission_participants(self.g['missions'][0])
        self.assertEqual(participants, {'pilot': {'P1'}, 'robot': {'R1'}})
        self.assertNotIn(('robot_runtime', 'DYNAMIC_REF'), unresolved)
        self.assertIn(('pilot_runtime', 'P1'), unresolved)  # reference != basis
        self.assertIn(('pilot_runtime', 'SUB_REF'), unresolved)

    def test_first_appearance_is_per_character_not_translated_name_or_technical_variant(self):
        self.g['records']['PilotBasicDatas']['listPilotBaseData'].append(
            {'id': 'P2', 'facialId': 'F1'})
        later = copy.deepcopy(self.g['missions'][0])
        later['id'] = 'm0002_0000002'
        self.g['missions'].append(later)
        self.g['presets']['cab:7']['enemyPlacementData'][0]['enemyPlacement'].append({'pilotBasisID': 'P2'})
        text = self.reader().deployments()
        self.assertEqual(text.count('BIOGRAFII: F1'), 1)
        self.assertEqual(text.count('OPISU: R1'), 1)
        self.assertIn('BRAK POTWIERDZONEGO', text)

    def test_dialogue_only_npc_is_a_first_appearance_without_a_battle_preset(self):
        self.g['missions'][0]['composition'][0]['preset'] = None
        self.g['records']['PilotBasicDatas']['listFacialSettingData'].append({'id': 'NPC1', 'nameKey': 'PN'})
        self.scenes[0].update(pid='NPC1', speaker_jp='仮')
        text = self.reader().deployments()
        self.assertIn('Pozostałe postacie dialogów', text)
        self.assertIn('ID postaci: NPC1', text)
        self.assertEqual(text.count('BIOGRAFII: NPC1'), 1)

    def test_repeated_npc_and_technical_pilot_share_exact_character_identity(self):
        self.scenes[0].update(pid='P1', speaker_jp='仮')
        later = copy.deepcopy(self.g['missions'][0])
        later['id'] = 'm0002_0000002'
        self.g['missions'].append(later)
        text = self.reader().deployments()
        self.assertEqual(text.count('BIOGRAFII: F1'), 1)
        self.assertNotIn('ID postaci: F1', text)  # already listed with pilots

    def test_same_localized_name_is_not_a_character_identity(self):
        self.g['records']['PilotBasicDatas']['listFacialSettingData'].append({'id': 'NPC1', 'nameKey': 'PN'})
        self.scenes[0].update(pid='NPC1', speaker_jp='仮')
        text = self.reader().deployments()
        self.assertEqual(text.count('BIOGRAFII: F1'), 1)
        self.assertEqual(text.count('BIOGRAFII: NPC1'), 1)

    def test_dialogue_characters_use_the_same_mission_protagonist_filter(self):
        self.g['records']['PilotBasicDatas']['listFacialSettingData'].append({'id': 'NPC_F', 'nameKey': 'PN'})
        self.scenes[0].update(pid='P1', speaker_jp='仮')
        self.scenes[1].update(pid='NPC_F', speaker_jp='仮')
        text = self.reader().deployments()
        self.assertNotIn('NPC\\_F', text)
        self.assertNotIn('BIOGRAFII: NPC', text)

    def test_unknown_dialogue_pid_is_never_guessed_by_nearby_name(self):
        self.scenes[0].update(pid='P1x', speaker_jp='仮')
        text = self.reader().deployments()
        self.assertIn('P1x — [BRAK POWIĄZANIA POSTACI]', text)
        self.assertNotIn('BIOGRAFII: P1x', text)

    def test_variant_selection_uses_context_as_well_as_identical_text(self):
        good = self.event_variant()
        wrong = copy.deepcopy(good)
        wrong['origin'] = {'file': 'old-revision'}
        wrong['units'][0]['table'] = 7
        self.g['scenario_variants']['x_sdemo.lua'].insert(0, wrong)
        reader = self.reader()
        reader.scenes()
        self.assertEqual(reader.verified_order['x_sdemo.lua']['origins'], [{'file': 'jp'}])

    def test_source_pid_and_branch_are_validated_before_gender_selection(self):
        variant = self.event_variant()
        variant['units'][0]['pid'] = 'SOURCE_PID'
        with self.assertRaisesRegex(ValueError, 'context pid does not match S6'):
            self.reader().render()
        variant['units'][0].pop('pid')
        variant['units'][0]['branch'] = 'M'
        with self.assertRaisesRegex(ValueError, 'context branch does not match S6'):
            self.reader().render()

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
        self.assertEqual(first['unverified_script_order'], [])
        self.assertEqual(first['mission_protagonists']['MissionData/m0001_0000001'], 'M')

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
