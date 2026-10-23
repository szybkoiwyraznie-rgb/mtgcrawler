"""Regression tests for PL v3.5 Episode 0-1 + game-wide gender & short-reply QA."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pl_release_package as R
import translation_import as I


EXPECTED_DIALOGUE_FIXES = {
    "dlg:eventP00.cpk/DL101_40.bin:896": "Tak!",
    "dlg:eventP00.cpk/DL101_40.bin:2368": "Że co?!",
    "dlg:eventP00.cpk/DL100_01.bin:9332": "To ty jesteś...?\nNowa w Connect Force?",
    "dlg:eventP00.cpk/DL101_60.bin:2172": "Ugh!",
    "dlg:eventP00.cpk/DL101_70.bin:5324": "Pa, pa, dziewczyny!",
    "dlg:eventP00.cpk/DL101_80.bin:1872": "Dwa miesiące temu prawie nic się nie działo,\na w tym miesiącu były już 22 zgłoszenia!",
    "dlg:evept106.EDAT/DL101_80G.bin:1872": "Dwa miesiące temu prawie nic się nie działo,\na w tym miesiącu były już 22 zgłoszenia!",
    "dlg:eventP00.cpk/DL101_80.bin:10864": "Tak jest!",
    "dlg:evept106.EDAT/DL101_80G.bin:10864": "Tak jest!",
    "dlg:eventP00.cpk/DL101_80.bin:17864": "Nie do wiary...\r\n",
    "dlg:evept106.EDAT/DL101_80G.bin:17836": "Nie do wiary...\r\n",
    "dlg:eventP02.EDAT/DL207_13.bin:21308": "Tak!",
    "dlg:evept101.EDAT/DL207_13B.bin:21376": "Tak!",
    "dlg:eventP02.EDAT/DL207_20.bin:22772": "Tak...\n",
    "dlg:eventP03.EDAT/DL310_20.bin:10660": "Tak!",
    "dlg:eventP08.EDAT/DL831_20.bin:2928": "Tak!",
    "dlg:eventP05.EDAT/DL520_60.bin:4336": "Pojawiliście się, Connect Force!\nI ty, Lamuness!",
    "dlg:eventP07.EDAT/DL728_12.bin:3924": "A więc przybyliście, Connect Force!",
    "dlg:evept104.EDAT/DL728_12E.bin:3924": "A więc przybyliście, Connect Force!",
}

EXPECTED_QUOTE_FIXES = {
    "quo:mesbtl00.cpk/p0500.pac:33740": "「Z tym 'czasem' to mogłeś sobie darować!」",
    "quo:mesbtl00.cpk/p0500.pac:36632": "「Przyjęłam!」",
    "quo:mesbtl00.cpk/p0525.pac:5136": "「Przyjęłam!」",
    "quo:mesbtl00.cpk/p0525.pac:5320": "「Przyjęłam!」",
    "quo:mesbtl00.cpk/p0526.pac:5136": "「Przyjęłam!」",
    "quo:mesbtl00.cpk/p0526.pac:5320": "「Przyjęłam!」",
    "quo:mesbtl00.cpk/p4501.pac:29364": "「Hwaaa! S-są za silni!」",
    "quo:mesbtl00.cpk/p0700.pac:23864": "「Przyjęłam!」",
    "quo:mesbtl00.cpk/p0710.pac:11864": "「Co? Dostałem?」",
    "quo:mesbtl00.cpk/p0733.pac:4456": "「W takim stanie\n trudno to nazwać zwycięstwem.」",
    "quo:mesbtl00.cpk/p1301.pac:5036": "「Och... Chybił?!」",
    "quo:mesbtl00.cpk/p2505.pac:12772": "「Chyba po prostu tamten spudłował...」",
    "quo:mesbtl00.cpk/p3711.pac:27284": "「Drugiego razu nie będzie! Unikaj porządnie!」",
    "quo:mesbtl01.EDAT/p2642.pac:8712": "「Przyjęłam!」",
    "quo:mesbtl01.EDAT/p2642.pac:11236": "「Przyjęłam!」",
    "quo:mesbtl01.EDAT/p4101.pac:12820": "「Przyjęłam!」",
    "quo:mesbtl02.EDAT/p4122.pac:10300": "「Przyjęłam!」",
    "quo:mesbtl02.EDAT/p4122.pac:10388": "「Przyjęłam!」",
    "quo:mesbtl19.EDAT/p4420.pac:9744": "「Przyjęłam!」",
    "quo:mesbtl19.EDAT/p4420.pac:9992": "「Przyjęłam!」",
}

FEMALE_SPEAKERS = {
    "白鳥マリア",
    "朝岡しのぶ",
    "キャサリン・グラス",
    "モニカ・ラング",
    "フィーネ・エレシーヌ・リネ",
    "ムンベイ",
    "クロ",
    "ヒマリ・ヤエガキ",
    "クリスチーナ・マッケンジー",
    "カレン・ジョシュワ",
    "泉野明",
    "香貫花・クランシー",
}


class PLv35GenderAndContextQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.out = Path(cls.tmp.name) / "materialized-pl"
        cls.coverage = R.materialize(ROOT / "pakiet_EN", ROOT / "pakiet_PL", cls.out)
        cls.rows, cls.by_file = I.load_rows(cls.out)

    def test_all_v35_dialogue_fixes_active(self):
        dlg = {r["id"]: r["pl"] for r in self.by_file["00_dialogue.jsonl"]}
        for row_id, expected in EXPECTED_DIALOGUE_FIXES.items():
            self.assertEqual(dlg[row_id], expected, row_id)
        # Owner decision: keep 'Matchless' catchphrase lines intact.
        self.assertIn("Matchless", dlg["dlg:eventP00.cpk/DL101_70.bin:3476"])

    def test_all_v35_battle_quote_fixes_active(self):
        bq = {r["id"]: r["pl"] for r in self.by_file["01_battle_quotes.jsonl"]}
        for row_id, expected in EXPECTED_QUOTE_FIXES.items():
            self.assertEqual(bq[row_id], expected, row_id)

    def test_no_female_speaker_uses_masculine_przyjalem(self):
        offenders = [
            r["id"]
            for r in self.by_file["01_battle_quotes.jsonl"]
            if (r.get("speaker") or {}).get("jp") in FEMALE_SPEAKERS
            and "Przyjąłem" in (r.get("pl") or "")
        ]
        self.assertEqual(offenders, [])

    def test_no_dobrze_short_reply_after_question_across_dialogue(self):
        # Every single 'Dobrze!'/'Dobrze...' reply after '?' in the 47,056-row corpus
        # has been manually audited: only 'Zostańmy przyjaciółkami, dobrze?' -> 'Dobrze!'
        # and 'Jak się miewasz?' -> 'Dobrze!' (plus its 3 epilogue variants) are valid Polish.
        idiomatic_allowed = {
            "dlg:eventP04.EDAT/DL414_11.bin:3844",
            "dlg:eventP08.EDAT/DL834_13.bin:65264",
            "dlg:evept104.EDAT/DL834_13E.bin:65248",
            "dlg:evept105.EDAT/DL834_13F.bin:68852",
            "dlg:evept108.EDAT/DL834_13J.bin:68876",
        }
        dlg = self.by_file["00_dialogue.jsonl"]
        offenders = []
        for i in range(1, len(dlg)):
            prev, cur = dlg[i - 1], dlg[i]
            if cur["id"].rsplit(":", 1)[0] != prev["id"].rsplit(":", 1)[0]:
                continue
            if prev.get("pl", "").rstrip().endswith("?") or prev.get("pl", "").rstrip().endswith("?!"):
                if (
                    cur.get("jp", "").strip() in ("はい！", "うん！", "うん…。")
                    and cur.get("pl", "").strip() in ("Dobrze!", "Dobrze...")
                    and cur["id"] not in idiomatic_allowed
                ):
                    offenders.append(cur["id"])
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
