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
        # the kana-token effect of record 1 is a row too since 2026-10-16: display form (%s per
        # control byte), flagged tokens=True - no longer a skip
        self.assertEqual([(m["record"]["record"], m["role"], m["text"], m["tokens"]) for m in missing],
                         [(0, "name", "集中", False), (1, "name_level", "幸運", False),
                          (1, "effect", "資金2倍 %s.ﾛｯ%s4率+5％", True)])
        self.assertEqual(skipped, [])
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
                self.assertEqual((dry["added"], dry["prefilled"], dry["token_rows"], dry["written"]),
                                 (3, 2, 1, False))
                self.assertEqual(len(package.joinpath(RRR.CONFIG_FILE).read_text(
                    encoding="utf-8").splitlines()), 5)
                self.assertFalse(package.joinpath("tokeny.tsv").exists())
                report = RRR.refresh(package, {"configst.cpk": Path("configst.cpk")})
                self.assertTrue(report["written"])
                lines = package.joinpath(RRR.CONFIG_FILE).read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(lines), 8)
                added = [json.loads(l) for l in lines[5:]]
                recs = self.parsed["records"]
                self.assertEqual(added[0]["source"]["offset"], recs[0]["offset"] + recs[0]["name_offset"])
                self.assertEqual((added[0]["jp"], added[0]["en"], added[0]["mode"]), ("集中", "Focus", "grow"))
                self.assertEqual((added[1]["jp"], added[1]["en"]), ("幸運", "Luck"))
                self.assertEqual(added[0]["category"], "config_spirit")
                # the token field: display-form jp, the field's real byte length, a note, and
                # its tokeny.tsv entry (T = kana token the English drops)
                self.assertEqual((added[2]["jp"], added[2]["en"]), ("資金2倍 %s.ﾛｯ%s4率+5％", ""))
                self.assertEqual(added[2]["bytes"], len("資金2倍 \x0f.ﾛｯ\x0f4率+5％".encode("cp932")))
                self.assertIn("tokeny.tsv", added[2]["note"])
                self.assertEqual(report["sidecar_entries"], 1)
                self.assertEqual(report["sidecar"], [{"id": added[2]["id"], "kinds": "T,T"}])
                sidecar = package.joinpath("tokeny.tsv").read_text(encoding="utf-8")
                self.assertIn(added[2]["id"] + "\tT,T\t", sidecar)
                # a second run finds nothing left
                again = RRR.refresh(package, {"configst.cpk": Path("configst.cpk")})
                self.assertEqual((again["added"], again["written"]), (0, False))
                self.assertEqual(again["skipped"], [])
            finally:
                RRR.CM.members_of = real

    def test_repeated_token_texts_point_at_the_first_row(self):
        blob = build_member("skill", [
            build_record("skill", 30, "幸運", "x", label="資金2倍 \x0f.ﾛｯ\x0f4率上昇"),
            build_record("skill", 31, "幸運", "x", label="資金2倍 \x0f.ﾛｯ\x0f4率上昇"),
        ], pool_runs=["対象:自機"])
        parsed = ISR.parse_member(blob, "skill", MEMBER)
        recs = parsed["records"]
        rows = []
        for i in (0, 1):
            for role in ("name", "effect"):
                offset = recs[i]["offset"] + recs[i][f"{role}_offset"]
                rows.append({"id": f"spirit:configst.cpk/{MEMBER}:{offset}", "category": "config_spirit",
                             "part": "text", "jp": recs[i][role], "en": "Fortune",
                             "source": {"container": "configst.cpk", "member": MEMBER, "offset": offset}})
        self.rows = rows
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(tmp)
            real = RRR.CM.members_of
            RRR.CM.members_of = lambda path: (None, {MEMBER: blob}, None)
            try:
                report = RRR.refresh(package, {"configst.cpk": Path("configst.cpk")}, check=True)
            finally:
                RRR.CM.members_of = real
        self.assertEqual((report["added"], report["token_rows"], report["copies"]), (2, 2, 1))
        first, second = report["rows"]
        self.assertEqual(first["jp"], "資金2倍 %s.ﾛｯ%s4率上昇")
        lines = report["rows"]
        self.assertEqual(lines[0]["id"], f"spirit:configst.cpk/{MEMBER}:"
                                         f"{recs[0]['offset'] + recs[0]['label_offset']}")


if __name__ == "__main__":
    unittest.main()
