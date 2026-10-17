"""Reader-facing machine headers hide technical IDs; the audit still keeps them."""
from pathlib import Path
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mech_catalog import render


def sample_model():
    def unit(key):
        return {"unit_id": key, "name": "Example & Robot", "base_id": key,
                "list_name": "Short label", "source": {"container": "fixture.cpk", "member": "unit_list.bin", "unit_index": key},
                "series": {"titles": ["Example Work"], "method": "unit_dictionary", "source_ids": [key]},
                "pilots": [], "native_skills": [], "group_ids": [], "weapons": []}
    a, b = unit(1), unit(2)
    b["series"].update(method="labelled_form", source_ids=[1])
    return {"summary": {"units": 2, "weapons_and_actions": 0, "unresolved_native_references": [],
                        "units_with_no_native_skill_assignment": 2},
            "units": [a, b], "skills": {},
            "groups": [{"id": 1, "name": "Example group", "unit_ids": [1, 2]}]}


class CataloguePresentationTests(unittest.TestCase):
    def test_machine_headings_have_only_names_including_duplicates(self):
        text, _ = render(sample_model())
        self.assertEqual(text.count("## Example &amp; Robot\n"), 2)
        self.assertNotRegex(text, r'<a\b|^\*Data: | — Unit \d+')
        self.assertNotIn("*Data: ", text)
        self.assertNotIn("base-ID field", text)
        self.assertNotIn("List label:", text)

    def test_removing_visible_ids_does_not_remove_internal_provenance(self):
        model = sample_model()
        before = copy.deepcopy(model)
        _, audit = render(model)
        self.assertEqual(model, before)
        self.assertEqual([u["unit_id"] for u in audit["units"]], [1, 2])
        self.assertEqual(model["units"][0]["source"]["container"], "fixture.cpk")

    def test_confirmed_series_tag_is_hidden_but_inference_stays_visible(self):
        text, _ = render(sample_model())
        self.assertIn("**Series:** Example Work\n\n", text)
        self.assertNotIn(" — *unit dictionary*.", text)
        self.assertIn(" — *form-derived; see provenance*.", text)

    def test_all_pilot_profiles_keep_names_without_numeric_suffixes(self):
        model = sample_model()
        model["units"][0]["pilots"] = [
            {"slot": i, "character_id": 100+i, "name": name,
             "profiles": [{"name": name, "character_id": key, "skills": [], "ace_alias": 0}
                          for key in (100+i, 200+i)]}
            for i, name in enumerate(("Pilot A", "Pilot B"))]
        before = copy.deepcopy(model)
        text, _ = render(model)
        for name in ("Pilot A", "Pilot B"):
            self.assertIn(f"**Assigned profile: {name}**", text)
            self.assertIn(f"**Linked alternate profile: {name}**", text)
        self.assertNotIn(" — Character ", text)
        self.assertNotIn(" (ID 100)", text)
        self.assertNotIn(" (ID 200)", text)
        self.assertNotIn("Spirit Commands are intentionally excluded.", text)
        self.assertIn("No native special-skill assignment in this character record.", text)
        self.assertEqual(model, before)

    def test_special_entries_and_stats_remain_without_repeated_notice(self):
        model = sample_model()
        model["units"][0]["weapons"] = [{"slot": 0, "name": "Example action", "selector": 0,
            "power": 100, "range_min": 1, "range_max": 2, "hit": 3, "en": 4, "will": 0,
            "gate": 0, "skills": []}]
        model["summary"]["weapons_and_actions"] = 1
        text, _ = render(model)
        self.assertIn("#### Additional entries — zero selector (animations / special records)", text)
        self.assertIn("| 0 | Example action | 100 | 1–2 | +3 | 4 |", text)
        self.assertNotIn("These are retained for completeness.", text)

    def test_removed_anchors_leave_no_broken_unit_links(self):
        text, _ = render(sample_model())
        self.assertNotIn("#unit-", text)
        self.assertIn("Series source: Example &amp; Robot.", text)
        self.assertIn("Example &amp; Robot (ID 1), Example &amp; Robot (ID 2)", text)


if __name__ == "__main__":
    unittest.main()
