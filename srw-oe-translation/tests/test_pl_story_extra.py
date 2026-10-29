"""PL extra/simulator scenario review (2026-10-24): grammar repairs.

The story-language pass released as v4.3 covered the 35 reading episodes
(``docs/reading-script/polish/episode_00.json``..``episode_34.json``,
32,156 of the 48,879 dialogue rows).  The remaining 16,725 rows live in the
``evept101``-``evept108`` extra/simulator containers and in ``eventP*`` rows
outside the episode blocks.  They were reviewed against JP/EN and against
the already-accepted Polish rendering of identical Japanese lines:

* ``No... przeszkadza.`` (Yoko answering Kamina) was not a sentence - the
  whole predicate was missing.
* ``Nie przegramy, prawda?`` turned Araara's confident 負けませんことよ into a
  question tag.
* ``GoShogun nie wyrzuciło ...`` used an active verb without an agent for the
  passive 飛ばされなかった (three DLC copies).
* ``To ja Gurren Lagann wydobędę ...`` missed the instrumental case.
* ``Okręt przyspiesza wiązka naprowadzająca ...`` reversed subject and object.
* ``materia pokonuje nietknięta przekrój czasoprzestrzeni`` was the calque the
  episode review had already replaced everywhere else.
* ``Brak wam czujności, wszystkim.``, ``siedziba na cały Układ Słoneczny``,
  ``Ten alarm chyba nie to oznacza, co?`` and ``Nie, to nie jest aż tak
  wygodne.`` duplicated the same scene in the DLC containers with the wording
  the episode review had superseded.

This module pins the plan, the snapshot ledger chain and the resulting text;
it needs no game files.
"""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pl_release_package as R  # noqa: E402
import translation_check as C  # noqa: E402

PLAN_NAME = "story-language-extra-2026-10-24.json"
V43_DATA_SHA = "e54562d803f8e011987b801c5439c2ee02dbe21d77775b9fe93c82386bc69262"
EXTRA_PREFIXES = (
    "dlg:evept101.EDAT/", "dlg:evept102.EDAT/", "dlg:evept103.EDAT/",
    "dlg:evept104.EDAT/", "dlg:evept105.EDAT/", "dlg:evept106.EDAT/",
    "dlg:evept107.EDAT/", "dlg:evept108.EDAT/",
)
RETIRED = (
    "No... przeszkadza",
    "Nie przegramy, prawda",
    "GoShogun nie wyrzuciło",
    "Okręt przyspiesza wiązka",
    "pokonuje nietknięta przekrój",
    "Brak wam czujności, wszystkim",
    "siedzibę na cały Układ",
    "siedziby na Układ Słoneczny",
    "Ten alarm chyba nie to oznacza",
    "Gurren Lagann wydobędę",
    "aż tak wygodne",
)


class ExtraScenePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "config/pl" / PLAN_NAME).read_text(encoding="utf-8"))
        cls.snapshot = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))
        cls.source = {row["id"]: row for row in R.I.load_rows(ROOT / "pakiet_EN")[0]}
        cls.entries = {
            entry["source_sha256"]: entry
            for entry in map(json.loads, (ROOT / "pakiet_PL/polish.jsonl").read_text(encoding="utf-8").splitlines())
        }

    def test_snapshot_ledger_chain(self):
        raw = (ROOT / "pakiet_PL/polish.jsonl").read_bytes()
        self.assertEqual(self.snapshot["data_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertGreaterEqual(self.snapshot["entries"], 108794)
        # This plan's edition is pinned by its own ledger entry (previous
        # snapshot hash + plan hash); later batches legitimately move the
        # snapshot on, so the newest entry is not assumed to be this plan.
        entry = next(
            h for h in self.snapshot["owner_story_language_corrections"] if h["plan"] == PLAN_NAME
        )
        self.assertEqual(entry["plan"], PLAN_NAME)
        self.assertEqual(entry["entries"], 22)
        self.assertEqual(entry["episode"], "extra")
        self.assertEqual(entry["previous_data_sha256"], V43_DATA_SHA)
        self.assertEqual(
            entry["sha256"],
            hashlib.sha256((ROOT / "config/pl" / PLAN_NAME).read_bytes()).hexdigest(),
        )
        self.assertFalse(entry["runtime_tested"])

    def test_every_edit_is_bound_and_landed(self):
        self.assertEqual(len(self.plan["changes"]), 22)
        for edit in self.plan["changes"]:
            with self.subTest(id=edit["id"]):
                row = self.source[edit["id"]]
                self.assertEqual(R.binding(row), edit["source_sha256"])
                self.assertEqual(self.entries[edit["source_sha256"]]["id"], edit["id"])
                self.assertEqual(self.entries[edit["source_sha256"]]["pl"], edit["after"])
                self.assertNotEqual(edit["before"], edit["after"])
                # Prose shape preserved: line breaks and control characters
                # must match the Japanese source exactly.
                jp = row.get("jp") or ""
                self.assertEqual(edit["after"].count("\n"), jp.count("\n"))
                self.assertEqual(
                    [ord(ch) for ch in edit["after"] if ord(ch) < 32 and ch != "\n"],
                    [ord(ch) for ch in edit["before"] if ord(ch) < 32 and ch != "\n"],
                )
                errors, _warnings = C.check_row({**row, "pl": edit["after"]}, field="pl")
                self.assertEqual(errors, [])

    def test_retired_wordings_are_gone_everywhere(self):
        values = [(entry["id"], entry["pl"]) for entry in self.entries.values()]
        for phrase in RETIRED:
            with self.subTest(phrase=phrase):
                hits = [row_id for row_id, text in values if phrase in (text or "")]
                self.assertEqual(hits, [], phrase)

    def test_extra_containers_are_covered_by_the_plan(self):
        touched = {edit["id"] for edit in self.plan["changes"]}
        self.assertTrue(touched)
        for row_id in touched:
            self.assertTrue(
                row_id.startswith(EXTRA_PREFIXES) or row_id.startswith(
                    ("dlg:eventP01.EDAT/", "dlg:eventP05.EDAT/", "dlg:eventP22.EDAT/")
                ),
                row_id,
            )
        # All eight extra containers exist in the package; the review scope
        # claim in NEXT_STEP refers to them by name.
        containers = {
            row_id.split(":", 1)[1].split("/", 1)[0]
            for _sha, entry in self.entries.items()
            for row_id in (entry["id"],)
            if row_id.startswith(EXTRA_PREFIXES)
        }
        self.assertEqual(
            containers,
            {f"evept{n}.EDAT" for n in range(101, 109)},
        )

    def test_semantics_of_the_corrected_lines(self):
        by_id = {
            row["id"]: self.entries.get(R.binding(row), {}).get("pl")
            for row in self.source.values()
        }
        self.assertEqual(by_id["dlg:evept108.EDAT/DL102_90J.bin:5828"], "No... nie jest dobrze.")
        self.assertEqual(by_id["dlg:eventP01.EDAT/DL102_90.bin:5828"], "No... nie jest dobrze.")
        self.assertEqual(by_id["dlg:evept106.EDAT/DL521_12G.bin:3104"], "Nie przegramy, zapewniam!")
        self.assertIn(
            "GoShogun nie trafił do innej czasoprzestrzeni",
            by_id["dlg:evept104.EDAT/DL834_13E.bin:95252"],
        )
        self.assertTrue(
            by_id["dlg:evept105.EDAT/DL834_13F.bin:99364"].startswith("GoShogun nie trafił")
        )
        self.assertTrue(
            by_id["dlg:evept108.EDAT/DL834_13J.bin:99384"].startswith("GoShogun nie trafił")
        )
        self.assertEqual(
            by_id["dlg:evept101.EDAT/DL103_40B.bin:3320"],
            "Wiązka naprowadzająca ze stacji\nprzyspiesza okręt.",
        )
        self.assertEqual(
            by_id["dlg:evept103.EDAT/DL103_40D.bin:19004"],
            "Wam wszystkim brak czujności.\nEskadra Skull i Connect Force,\n"
            "wszystkie jednostki lądować na okręcie!",
        )
        self.assertEqual(
            by_id["dlg:eventP22.EDAT/DL208_30.bin:6664"],
            "To ja wydobędę Gurren Lagannem\nto, co jest zakopane w ziemi.",
        )


if __name__ == "__main__":
    unittest.main()
