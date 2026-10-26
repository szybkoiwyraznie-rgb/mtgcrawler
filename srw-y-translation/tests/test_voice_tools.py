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


def bankmap_paths(listing):
    import build_voice_speaker_request as request
    return request.listing_paths(listing)


if __name__ == "__main__":
    unittest.main()
