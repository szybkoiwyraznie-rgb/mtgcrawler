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

    def test_removed_anchors_leave_no_broken_unit_links(self):
        text, _ = render(sample_model())
        self.assertNotIn("#unit-", text)
        self.assertIn("Series source: Example &amp; Robot.", text)
        self.assertIn("Example &amp; Robot (ID 1), Example &amp; Robot (ID 2)", text)


if __name__ == "__main__":
    unittest.main()
