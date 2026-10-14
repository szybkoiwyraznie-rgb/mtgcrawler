"""sysmes_text exports one row per whole pool string and can prune the old tail rows."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import sysmes_pack as sp  # noqa: E402
import sysmes_text as st  # noqa: E402


class SysmesTextTests(unittest.TestCase):
    def setUp(self):
        self.sm = sp.make_sysmes(["Ａ", "ＨＰ", "表示切換", "%sが使用可能になりました！",
                                  "ｼｽﾃﾑ設定１"])
        self.starts = sp.parse(self.sm).starts

    def test_one_row_per_japanese_whole_string(self):
        rows = st.pool_strings(self.sm)
        self.assertEqual([r["jp"] for r in rows],
                         ["表示切換", "%sが使用可能になりました！", "ｼｽﾃﾑ設定１"])
        self.assertEqual([r["source"]["offset"] for r in rows], self.starts[2:])
        self.assertEqual(rows[0]["id"], f"sysmes:configst.cpk/sysmes.bin:{self.starts[2]}")
        self.assertTrue(all(r["mode"] == "grow" for r in rows))

    def test_fragment_rows_are_detected_and_pruned_on_merge(self):
        rows = st.pool_strings(self.sm)
        tail = dict(rows[1])
        tail["id"] = f"sysmes:configst.cpk/sysmes.bin:{self.starts[3] + 2}"
        tail["jp"] = "が使用可能になりました！"
        tail["source"] = dict(tail["source"], offset=self.starts[3] + 2)
        package = [rows[0], tail]
        self.assertEqual(st.fragment_ids(self.sm, package), [tail["id"]])
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "04_config_text.jsonl"
            target.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in package),
                              encoding="utf-8")
            report = st.merge_into(rows, target, prune=[tail["id"]])
            merged = [json.loads(l) for l in target.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(report, {"existing": 2, "added": 2, "pruned": 1, "total": 3})
        self.assertEqual([r["jp"] for r in merged],
                         ["表示切換", "%sが使用可能になりました！", "ｼｽﾃﾑ設定１"])


if __name__ == "__main__":
    unittest.main()
