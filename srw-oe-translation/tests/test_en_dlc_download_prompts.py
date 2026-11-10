"""EN: japońskie zapowiedzi pobierania w `config_dlc_id` (etap 17, 2026-11-10).

19 z 103 pustych wierszy `config_dlc_id` to nie nazwy własne, a japońskie
komunikaty pobierania (rozdziały 2–8, misje dodatkowe, jednostka, symulatory).
Ten sam typ komunikatu po angielsku był już wypełniony w `config00` (rozdz. 1)
i `config04` (misje dodatkowe), więc był to brak, nie decyzja.

Moduł pilnuje trzech rzeczy: plan jest zapisem dokładnie tych 19 adresów,
pakiet ma w nich tekst (a nie pustkę), a pozostałe puste `config_dlc_id`
to rzeczywiście identyfikatory bez japońskiego tekstu.
"""
import json
import re
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import translation_check as C  # noqa: E402

PLAN = ROOT / "config/en/dlc-download-prompts-2026-11-10.json"
CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


def load_rows(name):
    path = ROOT / "pakiet_EN" / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class DlcDownloadPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN.read_text(encoding="utf-8"))
        cls.changes = cls.plan["changes"]
        cls.rows = {row["id"]: row for row in load_rows("04_config_text.jsonl")}

    def test_plan_is_source_bound_to_nineteen_dlc_rows(self):
        self.assertEqual(self.plan["schema"], 1)
        self.assertEqual(len(self.changes), 19)
        self.assertEqual(len({c["id"] for c in self.changes}), 19)
        for change in self.changes:
            self.assertEqual(change["file"], "04_config_text.jsonl")
            self.assertEqual(change["operation"], "add")
            self.assertEqual(change["before"], "")
            row = self.rows[change["id"]]
            self.assertTrue(change["id"].startswith("dlc_id:"), change["id"])
            self.assertEqual(change["jp"], row["jp"], "plan musi trzymać japoński źródłowy tekst")
            self.assertTrue(CJK.search(change["jp"]), change["id"])

    def test_every_reviewed_row_now_carries_english(self):
        for change in self.changes:
            row = self.rows[change["id"]]
            self.assertEqual(row["en"], change["after"], change["id"])
            self.assertTrue(row["en"].strip())

    def test_backfill_keeps_japanese_layout_and_never_invents_tokens(self):
        for change in self.changes:
            after, jp = change["after"], change["jp"]
            self.assertEqual(after.count("\n"), jp.count("\n"), change["id"])
            self.assertLessEqual(set(C.tokens(after)), set(C.tokens(jp)), change["id"])
            after.encode("cp932")  # CP932-encodable, no exotic characters
            self.assertNotIn("\x00", after)

    def test_no_japanese_text_left_in_config_dlc_id(self):
        """Żaden wiersz `config_dlc_id` z japońskim tekstem nie może zostać pusty."""
        rows = [r for r in load_rows("04_config_text.jsonl") if r.get("category") == "config_dlc_id"]
        self.assertTrue(rows)
        left = [r["id"] for r in rows if CJK.search(r.get("jp") or "") and not (r.get("en") or "").strip()]
        self.assertEqual(left, [], "japoński komunikat bez przekładu: " + ", ".join(left))

    def test_remaining_empty_dlc_rows_are_identifiers_only(self):
        """Puste wiersze, które zostają, to identyfikatory paczek/nazwy własne."""
        rows = [r for r in load_rows("04_config_text.jsonl") if r.get("category") == "config_dlc_id"]
        empty = [r for r in rows if not (r.get("en") or "").strip()]
        self.assertTrue(empty, "oczekujemy identyfikatorów bez tekstu (np. JP0700-…, config0N.pac)")
        for row in empty:
            self.assertFalse(CJK.search(row.get("jp") or ""), row["id"])


if __name__ == "__main__":
    unittest.main()
