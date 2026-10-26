"""Battle-voice speaker tools: the parts that must be right before game data arrives.

The join itself needs files from the owner, so what is tested here is everything that
can be checked without them: phrase search picks the right group, anchors refuse to
contradict themselves, the id decoding is exact, and the Unity data scanners only
accept a pair when the neighbour really is a known group id.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import voice_bank_content as content  # noqa: E402
import voice_bank_ip as bankip  # noqa: E402
import voice_bank_map as bankmap  # noqa: E402
import voice_identify_speaker as identify  # noqa: E402
import voice_speaker_map as speakermap  # noqa: E402
import build_bvc_rest_request as bvc3  # noqa: E402
import voice_phrase_anchor as anchor  # noqa: E402


def row(table, key, jp, en=""):
    return {"id": f"table:{table}:{key}", "table": table, "key": key,
            "jp": jp, "en": en, "jp_bytes": len(jp), "en_bytes": len(en)}


BANKS = {
    "00000411": [row("battle_voice", "00000411:00000b000", "ブライ・ソード！"),
                 row("battle_voice", "00000411:00000b001", "ブライガー、行くぞ！")],
    "01999dc9": [row("battle_voice", "01999dc9:115e0b000", "俺の名はアムロだ"),
                 row("battle_voice", "01999dc9:118a0b000", "当たれっ！")],
    "0000157d": [row("battle_voice", "0000157d:00020b000", "イデオンソード！")],
}


class SearchTests(unittest.TestCase):
    def test_phrase_lands_in_one_group(self):
        hits = identify.search("ブライ・ソード", BANKS)
        self.assertEqual([hit["bank"] for hit in hits], ["00000411"])
        self.assertEqual(hits[0]["hits"], 1)
        self.assertEqual(hits[0]["quotes"], 2)

    def test_phrase_absent_returns_nothing(self):
        self.assertEqual(identify.search("存在しない台詞", BANKS), [])

    def test_identical_counts_are_flagged_as_ambiguous(self):
        same = "ブライ・ソード！"
        shared = {bank: [row("battle_voice", f"{bank}:00000b000", same)]
                  for bank in BANKS}
        anchors = [{"phrase": same, "speaker": "テスト"}]
        check = identify.check_anchors(anchors, shared)
        self.assertTrue(any("niejednoznaczne" in problem for problem in check["problems"]))

    def test_two_speakers_cannot_share_a_group(self):
        anchors = [{"phrase": "ブライ・ソード", "speaker": "A"},
                   {"phrase": "ブライガー", "speaker": "B"}]
        check = identify.check_anchors(anchors, BANKS)
        self.assertEqual(len(check["problems"]), 1)
        self.assertIn("kilku mówców", check["problems"][0])

    def test_two_speakers_in_different_groups_are_accepted(self):
        anchors = [{"phrase": "ブライ・ソード", "speaker": "A"},
                   {"phrase": "イデオンソード", "speaker": "B"}]
        check = identify.check_anchors(anchors, BANKS)
        self.assertEqual(check["problems"], [])
        self.assertEqual(check["resolved"]["B"][0]["bank"], "0000157d")

    def test_order_key_decodes_generator_fields(self):
        # low = (machine << 12) | sequence, high = the group id
        decoded = identify.order_key("01999dc9", 0x15E0B000)
        self.assertEqual(decoded["id"], 0x01999DC9)
        self.assertEqual(decoded["machine"], 0x20B)
        self.assertEqual(decoded["sequence"], 0)
        self.assertGreater(decoded["timestamp_like"], 0)


class TypetreeScanTests(unittest.TestCase):
    def test_self_check_passes(self):
        self.assertEqual(bankmap.self_check(), 0)

    def test_shared_data_needs_the_id_next_to_the_key(self):
        import struct
        ids = {0x01999DC9}
        good = struct.pack("<II", 0xB000, 0x01999DC9) + b"AMRO_012"
        self.assertEqual(len(bankmap.scan_shared_data(good, ids)), 1)
        far = struct.pack("<II", 0xB000, 0x01999DC9) + b"\x00" * 200 + b"AMRO_012"
        self.assertEqual(bankmap.scan_shared_data(far, ids), [])

    def test_pilot_scan_requires_a_word_boundary(self):
        import struct
        ids = {0x01999DC9}
        blob = struct.pack("<II", 0xB000, 0x01999DC9) + b"AMRO\x00"
        self.assertEqual([item["code"] for item in
                          bankmap.scan_pilot_data(blob, ids, ["AMRO", "AMR"])], ["AMRO"])


class EvidenceTests(unittest.TestCase):
    def test_pronouns_and_names_are_counted_per_group(self):
        rows = [row("battle_voice", "01999dc9:115e0b000", "俺の名はアムロだ"),
                row("battle_voice", "01999dc9:118a0b000", "当たれっ！"),
                row("pilot_name", "000010a1:13c3dc000", "アムロ"),
                row("battle_voice-DLC1", "00000411:00000b000", "私が行く")]
        result = content.analyse(rows)
        by_bank = {group["bank"]: group for group in result["groups"]}
        self.assertEqual(by_bank["01999dc9"]["quotes"], 2)
        self.assertEqual(by_bank["01999dc9"]["pronouns"], {"ore": 1})
        self.assertEqual(by_bank["00000411"]["table"], "battle_voice-DLC1")
        self.assertEqual(dict(by_bank["01999dc9"]["names"]["pilot_name"])["アムロ"], 1)

    def test_markdown_keeps_the_sample_quotes(self):
        text = content.render_md({"groups": [{
            "group": 1, "bank": "01999dc9", "table": "battle_voice", "quotes": 2,
            "pronouns": {"ore": 1}, "names": {"pilot_name": [["アムロ", 1]]},
            "samples": ["俺の名はアムロだ", "当たれっ！"]}]})
        self.assertIn("Grupa 1", text)
        self.assertIn("アムロ × 1", text)
        self.assertIn("当たれっ！", text)


class RequestPlanTests(unittest.TestCase):
    def test_listing_paths_are_relative_to_streaming_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            listing = Path(tmp) / "listing.txt"
            listing.write_text(
                "279321\tD:\\Games\\SRWY\\SUPER ROBOT WARS Y_Data\\StreamingAssets\\aa\\StandaloneWindows64\\abc.bundle\n",
                encoding="utf-8")
            paths = bankmap_paths(listing)
        self.assertEqual(paths["abc.bundle"],
                         "aa/StandaloneWindows64/abc.bundle")


class SeriesEvidenceTests(unittest.TestCase):
    """A bank earns a series only when the quotes name enough units of one series."""

    @staticmethod
    def bank(name, quotes):
        return {'bank': name, 'table': 'battle_voice',
                'quotes': [{'jp': text} for text in quotes]}

    def test_units_are_mapped_by_distinctive_names_only(self):
        robots = [{'display': 'ライディーン', 'formal': 'ライディーン', 'ip': 'BRVRDN'},
                  {'display': 'Ｚ', 'formal': 'Ｚ', 'ip': 'GNWOM'}]  # too short to trust
        mapping = bankip.name_to_series(robots)
        self.assertEqual(mapping, {'ライディーン': 'BRVRDN'})

    def test_longer_name_does_not_credit_the_shorter_one(self):
        names = [('ゴッドライディーン', 'BRVRDN'), ('ライディーン', 'GODGN')]
        self.assertEqual(bankip.series_in('ゴッドライディーン！', names), {'BRVRDN'})
        self.assertEqual(bankip.series_in('ライディーン！', names), {'GODGN'})

    def test_bank_with_one_dominant_series_is_assigned(self):
        mapping = {'ライディーン': 'BRVRDN', 'ゴッドライディーン': 'BRVRDN'}
        quotes = ['ライディーン、いけ！'] * 25 + ['ゴッドライディーン！'] * 5
        result = bankip.score([self.bank('00000411', quotes)], mapping)
        bank = result['banks'][0]
        self.assertTrue(bank['assigned'])
        self.assertEqual(bank['top_series'], 'BRVRDN')
        self.assertEqual(result['assigned'], 1)

    def test_thin_evidence_leaves_the_bank_unassigned(self):
        mapping = {'ライディーン': 'BRVRDN', 'ゴッドライディーン': 'BRVRDN'}
        quotes = ['ライディーン、いけ！'] * 3 + ['当たれっ！'] * 40
        bank = bankip.score([self.bank('0000157d', quotes)], mapping)['banks'][0]
        self.assertFalse(bank['assigned'])
        self.assertEqual(bank['top_series'], '')
        self.assertEqual(bank['share'], 1.0)  # pure, but far too few quotes

    def test_mixed_banks_are_left_numeric(self):
        mapping = {'ライディーン': 'BRVRDN', 'ゴッドライディーン': 'GODGN'}
        quotes = ['ライディーン！'] * 20 + ['ゴッドライディーン！'] * 20
        bank = bankip.score([self.bank('01999dc9', quotes)], mapping)['banks'][0]
        self.assertFalse(bank['assigned'])
        self.assertAlmostEqual(bank['share'], 0.5)


class SpeakerMapTests(unittest.TestCase):
    """The join that names a battle quote: table row -> shared key -> container nameText."""

    tables = [
        {'table': 'battle_voice', 'key': '01999dc9:15e0b000', 'jp': '当たれっ！'},
        {'table': 'battle_voice', 'key': '01999dc9:15e0b001', 'jp': 'いくぞ'},
        {'table': 'battle_voice', 'key': '01999dc9:15e0b002', 'jp': '無い'},
        {'table': 'pilot_name', 'key': '000010a1:3c3dc000', 'jp': 'アムロ'},
    ]
    shared = {'01999dc9:15e0b000': 'F069_002', '01999dc9:15e0b001': 'F069_003'}
    waves = {
        'F069_002': {'speaker': 'ルルーシュ', 'name_key': 'CGRRR_001', 'face_key': 'LLSH',
                     'dialogue': '当たれっ！', 'container': 'GEARE_LL1_00', 'file': 'a.bundle'},
        'F069_003': {'speaker': 'ルルーシュ', 'name_key': 'CGRRR_001', 'face_key': 'LLSH',
                     'dialogue': 'いくぞ', 'container': 'GEARE_LL1_00', 'file': 'a.bundle'},
    }
    pilots = [{'id': 'LLSH_D', 'name': 'ルルーシュ', 'gender': 'm', 'bvc': 'GEARE_LL1_00'}]

    def test_only_quotes_with_a_named_wave_are_attributed(self):
        result = speakermap.build(self.tables, self.shared, self.waves, self.pilots)
        self.assertEqual(result['rows'], 3)          # pilot_name is not a battle quote
        self.assertEqual(result['mapped'], 2)        # the third row has no WaveId
        self.assertEqual(result['speakers'], 1)
        self.assertEqual(result['top_speakers'][0], ('ルルーシュ', 2))

    def test_gender_comes_from_the_pilot_table_and_may_be_missing(self):
        result = speakermap.build(self.tables, self.shared, self.waves, self.pilots)
        self.assertEqual(result['with_gender'], 2)
        nobody = speakermap.build(self.tables, self.shared, self.waves, [])
        self.assertEqual(nobody['with_gender'], 0)
        self.assertEqual(nobody['mapped'], 2)        # attribution does not depend on it

    def test_a_quote_without_a_container_is_left_unattributed(self):
        result = speakermap.build(self.tables, self.shared, {}, self.pilots)
        self.assertEqual(result['mapped'], 0)
        self.assertEqual(result['speakers'], 0)

    def test_report_states_the_denominator(self):
        text = speakermap.render_md(speakermap.build(self.tables, self.shared,
                                                     self.waves, self.pilots))
        self.assertIn('3', text)
        self.assertIn('66.7%', text)
        self.assertIn('ルルーシュ', text)


class ContainerRequestTests(unittest.TestCase):
    """The third kit asks for exactly the container bundles we do not have yet."""

    def test_pattern_matches_every_naming_shape_seen(self):
        for name in ('GEARE_LL1_00', '1SPBO_BK0_00', '2BVDG_RG0_00', 'OSROG_AI0_01'):
            self.assertTrue(bvc3.CONTAINER.match(name), name)

    def test_pattern_rejects_audio_and_other_assets(self):
        for name in ('BvcCommon', 'F321_026', 'battle_voice Shared Data', 'GEARE_LL1'):
            self.assertFalse(bvc3.CONTAINER.match(name), name)

    def test_script_block_has_one_entry_per_bundle(self):
        plan = {'wanted': [{'folder': 'aa/StandaloneWindows64', 'file': 'x.bundle'}],
                'bytes': 2048}
        text = bvc3.ps_block(plan)
        self.assertEqual(text.count("@{"), 1)
        self.assertIn('SRW_Y_BVC3.zip', text)


class PhraseAnchorTests(unittest.TestCase):
    """A catchphrase must come back as the pilot who shouts it, not as the robot named."""

    rows = [
        {'jp': 'イデオンソード！', 'speaker': 'コスモ', 'key': '0000157d:5320b006',
         'wave': 'B09_289', 'container': '3EXID_YK0_00', 'name_key': 'LGNGIDEON_001',
         'face': 'IDEON'},
        {'jp': 'イデオンソード！', 'speaker': 'デク', 'key': '0000157d:5320b007',
         'wave': 'B09_290', 'container': '3EXID_YK0_00', 'name_key': 'LGNGIDEON_002',
         'face': 'IDEON'},
        {'jp': '当たれっ！', 'speaker': 'デク', 'key': '0000157d:5320b008', 'wave': 'B09_291',
         'container': '3EXID_YK0_00', 'name_key': '', 'face': ''},
    ]

    def test_expected_speaker_is_found_among_several(self):
        result = anchor.check(self.rows, 'イデオンソード', 'コスモ')
        self.assertEqual(result['verdict'], 'ZGODNY')
        self.assertEqual(result['hits'], 2)
        self.assertEqual(result['agree'], 1)
        self.assertEqual(result['speakers'], ['コスモ', 'デク'])

    def test_unrelated_phrase_cannot_vouch_for_a_speaker(self):
        result = anchor.check(self.rows, '当たれっ', 'コスモ')
        self.assertEqual(result['verdict'], 'BRAK')
        self.assertEqual(result['agree'], 0)

    def test_sample_carries_the_whole_encoding_path(self):
        sample = anchor.check(self.rows, 'イデオンソード', 'コスモ')['sample']
        self.assertEqual(sample['wave'], 'B09_289')
        self.assertEqual(sample['container'], '3EXID_YK0_00')
        self.assertEqual(sample['key'].split(':')[0], '0000157d')  # the bank


def bankmap_paths(listing):
    import build_voice_speaker_request as request
    return request.listing_paths(listing)


if __name__ == "__main__":
    unittest.main()
