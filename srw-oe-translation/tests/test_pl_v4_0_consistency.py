from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pl_release_package as R  # noqa: E402
import translation_import as TI  # noqa: E402


class TestPlV40Consistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.en_dir = ROOT / "pakiet_EN"
        cls.pl_dir = ROOT / "pakiet_PL"
        cls.snapshot = json.loads((cls.pl_dir / "snapshot.json").read_text("utf-8"))
        cls._tmp = tempfile.TemporaryDirectory()
        cls.mat = Path(cls._tmp.name) / "mat"
        R.materialize(cls.en_dir, cls.pl_dir, cls.mat)
        _, cls.by_file = TI.load_rows(cls.mat)
        cls.by_id = {
            row["id"]: row
            for rows in cls.by_file.values()
            for row in rows
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_snapshot_manifest_and_full_validation(self) -> None:
        self.assertEqual(self.snapshot["entries"], 108794)
        self.assertIn("owner_ui_corrections", self.snapshot)
        self.assertIn("merge_provenance", self.snapshot)
        actual_sha = hashlib.sha256((self.pl_dir / "polish.jsonl").read_bytes()).hexdigest()
        self.assertEqual(self.snapshot["data_sha256"], actual_sha)

        _, materialized = TI.load_rows(self.mat)
        checked = R.validate(materialized, self.en_dir)
        self.assertEqual(len(checked["errors"]), 0)
        totals = checked["totals"]
        self.assertEqual(totals["rows"], 109176)
        self.assertEqual(totals["filled"], 108805)
        self.assertEqual(totals["empty"], 371)
        self.assertEqual(totals["errors"], 0)

    def test_kallen_vs_karen_and_editorial_preservations(self) -> None:
        for part in ("name_short", "name_narrow", "nickname", "short_name"):
            self.assertEqual(self.by_id[f"char:2320:{part}"]["pl"], "Kallen", part)
        self.assertEqual(self.by_id["char:2320:name_full"]["pl"], "Kallen Kozuki")

        for part in ("name_short", "name_narrow", "nickname", "short_name"):
            self.assertEqual(self.by_id[f"char:1409:{part}"]["pl"], "Karen", part)
        self.assertEqual(self.by_id["char:1409:name_full"]["pl"], "Karen Joshua")

        matchless_rows = [
            row
            for row in self.by_file["00_dialogue.jsonl"] + self.by_file["01_battle_quotes.jsonl"]
            if "Matchless" in (row.get("pl") or "")
        ]
        self.assertGreaterEqual(len(matchless_rows), 15)

        ally_rows = [
            row
            for row in self.by_file["07_names_characters.jsonl"]
            if "Ally" in (row.get("en") or "")
        ]
        self.assertTrue(ally_rows)
        for row in ally_rows:
            marker = "(Ally)" if "(Ally)" in row["en"] else "/Ally"
            self.assertIn(marker, row["pl"], row["id"])

        for row in self.by_file["00_dialogue.jsonl"]:
            pl = row.get("pl") or ""
            if "＜主人公名＞" in (row.get("jp") or "") and pl:
                self.assertIn("＜主人公名＞", pl, row["id"])
                self.assertNotIn("Seishiro", pl, row["id"])

    def test_global_terminology_and_gender_invariants(self) -> None:
        forbidden = (
            "Przeklęte Connect Force",
            "panowie z Connect Force",
            "Zaurersi",
            "Zaurerów",
            "Saurerów",
            "Mucus Gate'ów",
            "Mucus Gate'y",
            "Brama Mucus",
            "Bramy Mucus",
            "Bramę Mucus",
            "Bramą Mucus",
        )
        for name in ("00_dialogue.jsonl", "01_battle_quotes.jsonl", "05_mission_text.jsonl"):
            for row in self.by_file[name]:
                pl = row.get("pl") or ""
                for bad in forbidden:
                    self.assertNotIn(bad, pl, f"{row['id']} contains {bad!r}: {pl!r}")

    def test_story_dlc_and_mission_text_fixes(self) -> None:
        self.assertEqual(
            self.by_id["dlg:eventP02.EDAT/DL105_70.bin:4788"]["pl"],
            "Dragon Escort zostaje zniszczony",
        )
        self.assertEqual(
            self.by_id["dlg:eventP03.EDAT/DL311_13.bin:1860"]["pl"],
            "Moduł kontroli zostaje zniszczony",
        )
        self.assertEqual(
            self.by_id["dlg:eventP05.EDAT/DL518_11.bin:6844"]["pl"],
            "Ray zostaje zniszczony",
        )
        self.assertEqual(
            self.by_id["dlg:eventP06.EDAT/DL625_13.bin:7356"]["pl"],
            "Evil God Drago zostaje zestrzelony",
        )
        self.assertEqual(
            self.by_id["dlg:eventP07.EDAT/DL728_13.bin:5232"]["pl"],
            "True Posaydal zostaje zestrzelony",
        )
        self.assertEqual(
            self.by_id["dlg:eventP08.EDAT/DL831_12.bin:1212"]["pl"],
            "Cowen & Stinger zostają zestrzeleni",
        )
        self.assertEqual(self.by_id["dlg:eventP07.EDAT/DL726_11.bin:7460"]["pl"], "Mówisz o sobie?")
        self.assertEqual(self.by_id["dlg:eventP08.EDAT/DL830_13.bin:61756"]["pl"], "Tak... Van wygrał!")
        self.assertIn("jedną z naaas", self.by_id["dlg:eventP08.EDAT/DL831_12.bin:9360"]["pl"])
        self.assertIn("profesjonalistką", self.by_id["dlg:eventP08.EDAT/DL834_13.bin:98776"]["pl"])
        self.assertIn("Saurersów", self.by_id["dlg:eventP08.EDAT/DL832_40.bin:6260"]["pl"])
        self.assertIn("Saurersi", self.by_id["dlg:eventP08.EDAT/DL834_11.bin:6432"]["pl"])

        for dlc_id in (
            "dlg:eventP08.EDAT/DL834_13.bin:51632",
            "dlg:evept104.EDAT/DL834_13E.bin:51640",
            "dlg:evept105.EDAT/DL834_13F.bin:55228",
            "dlg:evept108.EDAT/DL834_13J.bin:55244",
        ):
            self.assertEqual(self.by_id[dlc_id]["pl"], "Dobrze, przetnę go Shiden Swordem!")

        self.assertEqual(
            self.by_id["mission_note:eventP05.EDAT/DL521_12_ext.dat:r0:note_a"]["pl"],
            '"＠6Demon Goburiki＠0" porusza się w specjalny sposób.',
        )
        self.assertEqual(
            self.by_id["map_name:config00.cpk/srwDL_Map_S.bin:r7:name"]["pl"],
            "64_Mapa ataku 10 (mrok pustki)",
        )
        self.assertEqual(
            self.by_id["mission_title:config08.EDAT/milstP08.bin:r20:title"]["pl"],
            "Transport Ark Ship",
        )
        self.assertEqual(
            self.by_id["mission_note:eventP08.EDAT/DL832_40_ext.dat:r0:title"]["pl"],
            "Transport Ark Ship",
        )

    def test_mission_deployments_doc_synced(self) -> None:
        doc = (ROOT / "docs" / "srwoe_mission_deployments.md").read_text("utf-8")
        self.assertNotIn(
            "#### Kallen Kozuki\n\n- **Seria:** Code Geass\n- **Nazwa skrócona:** Karen",
            doc,
        )
        self.assertIn(
            "#### Kallen Kozuki\n\n- **Seria:** Code Geass\n- **Nazwa skrócona:** Kallen",
            doc,
        )
        self.assertNotIn("Posaydal Regular", doc)
        self.assertNotIn("Control AI", doc)
        self.assertIn('> "Demon Goburiki" porusza się w specjalny sposób.', doc)
        self.assertIn("### Odcinek 32 — Transport Ark Ship (`DL832_40`)", doc)
        for idx, line in enumerate(doc.splitlines(), 1):
            if line.startswith("|"):
                self.assertLessEqual(len(line), 216, f"Pipe line > 216 at L{idx}")
            self.assertNotIn("[ID ", line, f"Forbidden [ID ...] at L{idx}")


if __name__ == "__main__":
    unittest.main()
