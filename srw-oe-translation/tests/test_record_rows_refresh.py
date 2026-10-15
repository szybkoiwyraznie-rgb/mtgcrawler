"""tools/record_rows_refresh.py: record fields without a package row get one (synthetic data)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import item_skill_records as ISR  # noqa: E402
import record_rows_refresh as RRR  # noqa: E402
from test_item_skill_write import build_member, build_record  # noqa: E402

MEMBER = "srwDL_Spirit.bin"


class RefreshTest(unittest.TestCase):
    def setUp(self):
        self.blob = build_member("skill", [
            build_record("skill", 19, "集中", "＠6%s1", name_level="集中", effect_brief="集中",
                         label="1ターン､回避補正上昇"),
            build_record("skill", 20, "幸運", "資金2倍 \x0f.ﾛｯ\x0f4率+5％", name_level="幸運"),
        ], pool_runs=["対象:自機"])
        self.parsed = ISR.parse_member(self.blob, "skill", MEMBER)
        recs = self.parsed["records"]
        src = {"container": "configst.cpk", "member": MEMBER}

        def row(record, role, jp, en):
            offset = recs[record]["offset"] + recs[record][f"{role}_offset"]
            return {"id": f"spirit:configst.cpk/{MEMBER}:{offset}", "category": "config_spirit",
                    "part": "text", "jp": jp, "en": en, "source": dict(src, offset=offset)}
        # the scan reached everything of record 0 except its name; record 1 has its name only
        self.rows = [row(0, "name_level", "集中", "Focus"), row(0, "effect", "＠6%s1", "＠6%s1"),
                     row(0, "effect_brief", "集中", "Focus"), row(0, "label", "1ターン､回避補正上昇", ""),
                     row(1, "name", "幸運", "Luck")]

    def package(self, folder):
        path = Path(folder) / RRR.CONFIG_FILE
        with path.open("w", encoding="utf-8") as handle:
            for r in self.rows:
                handle.write(json.dumps(r, ensure_ascii=False) + "\n")
        return Path(folder)

    def test_missing_fields_and_sibling_english(self):
        offsets, fields = RRR.covered_targets(self.rows)
        missing, skipped = RRR.missing_fields(self.blob, MEMBER, "configst.cpk", "skill", offsets, fields)
        self.assertEqual([(m["record"]["record"], m["role"], m["text"]) for m in missing],
                         [(0, "name", "集中"), (1, "name_level", "幸運")])
        self.assertEqual(len(skipped), 1)                       # the kana-token effect of record 1
        self.assertIn("kana tokens", skipped[0])
        recs = self.parsed["records"]
        self.assertEqual(RRR.sibling_english(self.rows, MEMBER, recs[0], "集中"), "Focus")
        self.assertEqual(RRR.sibling_english(self.rows, MEMBER, recs[1], "幸運"), "Luck")
        self.assertIsNone(RRR.sibling_english(self.rows, MEMBER, recs[1], "集中"))   # other record

    def test_refresh_appends_rows_once_and_check_mode_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(tmp)
            real = RRR.CM.members_of
            RRR.CM.members_of = lambda path: (None, {MEMBER: self.blob, "sysmes.bin": b"x"}, None)
            try:
                dry = RRR.refresh(package, {"configst.cpk": Path("configst.cpk")}, check=True)
                self.assertEqual((dry["added"], dry["prefilled"], dry["written"]), (2, 2, False))
                self.assertEqual(len(package.joinpath(RRR.CONFIG_FILE).read_text(
                    encoding="utf-8").splitlines()), 5)
                report = RRR.refresh(package, {"configst.cpk": Path("configst.cpk")})
                self.assertTrue(report["written"])
                lines = package.joinpath(RRR.CONFIG_FILE).read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(lines), 7)
                added = [json.loads(l) for l in lines[5:]]
                recs = self.parsed["records"]
                self.assertEqual(added[0]["source"]["offset"], recs[0]["offset"] + recs[0]["name_offset"])
                self.assertEqual((added[0]["jp"], added[0]["en"], added[0]["mode"]), ("集中", "Focus", "grow"))
                self.assertEqual((added[1]["jp"], added[1]["en"]), ("幸運", "Luck"))
                self.assertEqual(added[0]["category"], "config_spirit")
                # a second run finds nothing left
                again = RRR.refresh(package, {"configst.cpk": Path("configst.cpk")})
                self.assertEqual((again["added"], again["written"]), (0, False))
                self.assertEqual(len(again["skipped"]), 1)
            finally:
                RRR.CM.members_of = real


if __name__ == "__main__":
    unittest.main()
