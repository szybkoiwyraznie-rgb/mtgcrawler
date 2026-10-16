"""coverage_audit: whole sysmes strings and executable strings must be package rows.

Synthetic data only (sysmes_pack.make_sysmes, tests/exe_fixtures.Builder) - no game bytes.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import coverage_audit as CA  # noqa: E402
import sysmes_pack as SP  # noqa: E402
import sysmes_text as ST  # noqa: E402
import table_write as TW  # noqa: E402
from exe_fixtures import Builder, cp932  # noqa: E402

# ﾒｲﾝ<0F>0ｲﾛｯﾄ = メインパイロット: the pool string carries a voiced-kana token
MAIN_PILOT_RAW = b"\xd2\xb2\xdd\x0f0\xb2\xdb\xaf\xc4"


class LabelledRunTests(unittest.TestCase):
    """A dictionary slot ``愛称：仁`` is two rows in the package (the label row and the keyed
    nickname): the run is covered when both halves are, whatever its length (the plain trim
    rule needs 3 characters left after the label, so ``愛称：仁`` and ``愛称：ゆう`` used to be
    reported missing once the whole-string leftover rows were pruned, package v7)."""

    def test_label_plus_text_covers_the_short_runs(self):
        blob = "\n".join(["愛称：", "仁", "ゆう", "声優：", "田中真弓", "クッキー"])
        for run in ("愛称：仁", "愛称：ゆう", "声優：田中真弓", "愛称：クッキー"):
            self.assertTrue(CA.covered(run, blob), run)

    def test_a_missing_half_still_counts_as_missing(self):
        self.assertFalse(CA.covered("愛称：仁", "\n".join(["愛称：", "飛鳥"])))      # text missing
        self.assertFalse(CA.covered("愛称：仁", "\n".join(["仁", "声優："])))        # label missing
        self.assertFalse(CA.covered("愛称：", "\n".join(["愛称：仁"])) is None)

    def test_the_label_must_be_a_whole_row(self):
        # the label inside some longer row (an old whole-string leftover) is not a label row
        self.assertFalse(CA.covered("愛称：仁", "\n".join(["愛称：飛鳥", "仁"])))


class SysmesWholeStringTests(unittest.TestCase):
    def setUp(self):
        self.pool = SP.make_sysmes([b"Now Loading", "表示切換".encode("cp932"), MAIN_PILOT_RAW,
                                    "%sが使用可能になりました！".encode("cp932")])
        self.starts = SP.string_starts(self.pool)

    def test_tail_rows_do_not_cover_a_pool_string(self):
        texts = {"が使用可能になりました！", "表示切換", "ｲﾛｯﾄ"}       # tails only
        missing = CA.sysmes_missing_whole(self.pool, texts)
        self.assertEqual([m["offset"] for m in missing], [self.starts[2], self.starts[3]])
        self.assertTrue(all(m["whole_string"] for m in missing))
        self.assertEqual(missing[0]["text"], TW.display(MAIN_PILOT_RAW))

    def test_raw_or_display_form_counts_as_covered(self):
        texts = {"表示切換", "%sが使用可能になりました！", MAIN_PILOT_RAW.decode("cp932")}
        self.assertEqual(CA.sysmes_missing_whole(self.pool, texts), [])
        texts = {"表示切換", "%sが使用可能になりました！", TW.display(MAIN_PILOT_RAW)}
        self.assertEqual(CA.sysmes_missing_whole(self.pool, texts), [])

    def test_exporter_emits_the_half_width_kana_strings(self):
        # the exporter's old Japanese test skipped half-width katakana: these rows were the
        # "Main Pilot / Sub Pilot / Sort / Page" leftovers of build #19
        self.assertTrue(ST.has_japanese(MAIN_PILOT_RAW.decode("cp932")))
        self.assertTrue(ST.has_japanese("ｿｰﾄ"))
        self.assertFalse(ST.has_japanese("Now Loading"))
        rows = ST.pool_strings(self.pool)
        self.assertEqual([r["source"]["offset"] for r in rows], self.starts[1:])
        texts = {r["jp"] for r in rows}
        self.assertEqual(CA.sysmes_missing_whole(self.pool, texts), [])


class ExecutableAuditTests(unittest.TestCase):
    def setUp(self):
        b = Builder()
        s_after = b.string("after", cp932("移動後"))
        s_enemy = b.string("enemy", cp932("敵"))
        b.ref_pair(s_after, reg=4)
        b.ref_pair(s_enemy, reg=5)
        self.blob = b.build()

    def test_plain_elf_strings_are_audited(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "PBOOT.PBP"
            exe.write_bytes(self.blob)
            report = CA.audit_executable(exe, {"移動後"})
            self.assertTrue(report["ok"])
            self.assertEqual(report["runs"], 2)
            self.assertEqual([m["text"] for m in report["missing"]], ["敵"])
            self.assertTrue(report["missing"][0]["vaddr"].startswith("0x"))
            self.assertEqual(CA.audit_executable(exe, {"移動後", "敵"})["missing"], [])

    def test_collect_picks_pboot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PBOOT.PBP").write_bytes(self.blob)
            (root / "config00.cpk").write_bytes(b"x")
            (root / "ICON0.PNG").write_bytes(b"x")
            names = sorted(p.name for p in CA.collect([root]))
            self.assertIn("PBOOT.PBP", names)
            self.assertNotIn("ICON0.PNG", names)

    def test_rows_written_by_the_package_cover_the_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "PBOOT.PBP"
            exe.write_bytes(self.blob)
            import exe_strings as EXE
            rows, _ = EXE.extract_rows(EXE.Elf(self.blob))
            package = Path(tmp) / "pkg"
            package.mkdir()
            (package / "09_executable.jsonl").write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
            texts = set(CA.load_package_texts(package))
            self.assertEqual(CA.audit_executable(exe, texts)["missing"], [])


if __name__ == "__main__":
    unittest.main()
