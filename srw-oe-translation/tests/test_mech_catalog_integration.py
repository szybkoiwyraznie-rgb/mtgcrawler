"""Optional real-input catalogue regression and semantic mutations.

Requires the user's original private containers; no game bytes are test fixtures.
Every mutation is confined to temporary output. The document, its audit, hashes,
byte count, and span map are rebuilt together, so checksum rejection is not enough.
"""
from pathlib import Path
import copy
import hashlib
import json
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from mech_catalog_sources import collect, CONFIG_FILES
from mech_catalog import build_model, render
from verify_mech_catalog import verify


class MechCatalogueIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs = PROJECT.parent / "google_drive"
        cls.package = PROJECT / "pakiet_EN"
        cls.elf = cls.configs / "EBOOT.BIN"
        if not all((cls.configs / n).is_file() for n in CONFIG_FILES) or not cls.elf.is_file():
            raise unittest.SkipTest("Private original game inputs are not present (not stored in Git)")
        cls.manifest = PROJECT / "docs/mech-catalog/source-inventory.json"
        cls.engine = PROJECT / "docs/mech-catalog/engine-map.json"
        cls.errata = PROJECT / "docs/mech-catalog/description-errata.json"
        cls.source = collect(cls.configs, cls.package)
        cls.model = build_model(cls.source, cls.package, cls.elf.read_bytes(),
                               json.loads(cls.engine.read_bytes()), json.loads(cls.errata.read_bytes()))
        cls.initial_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [cls.elf] + [cls.configs / n for n in CONFIG_FILES]}
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.md = Path(cls.temp.name) / "catalog.md"
        cls.audit_path = Path(cls.temp.name) / "audit.json"
        cls.baseline_text, positions = render(cls.model)
        cls.base_audit = {"schema_version": 1, "model": cls.model, "positions": positions,
                          "output_bytes": len(cls.baseline_text.encode()),
                          "output_sha256": hashlib.sha256(cls.baseline_text.encode()).hexdigest(),
                          "source_manifest_sha256": hashlib.sha256(cls.manifest.read_bytes()).hexdigest(),
                          "engine_map_sha256": hashlib.sha256(cls.engine.read_bytes()).hexdigest(),
                          "description_errata_sha256": hashlib.sha256(cls.errata.read_bytes()).hexdigest()}
        cls.md.write_text(cls.baseline_text, encoding="utf-8")
        cls.audit_path.write_text(json.dumps(cls.base_audit, ensure_ascii=False), encoding="utf-8")
        # Establish a positive baseline before running any negative test.
        cls.baseline = verify(cls.configs, cls.package, cls.elf, cls.manifest, cls.engine, cls.errata, cls.md, cls.audit_path)
        assert cls.baseline["status"] == "PASS"

    def setUp(self):
        self.audit = copy.deepcopy(self.base_audit)
        self.current = self.audit["model"]

    def unit(self, uid):
        return next(u for u in self.current["units"] if u["unit_id"] == uid)

    def reject(self, mutate_text=None):
        text, positions = render(self.current)
        if mutate_text:
            changed = mutate_text(text)
            self.assertNotEqual(text, changed, "Mutation must actually change the output")
            text = changed
        data = text.encode()
        self.audit.update(output_bytes=len(data), output_sha256=hashlib.sha256(data).hexdigest(), positions=positions)
        self.md.write_bytes(data)
        self.audit_path.write_text(json.dumps(self.audit, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            verify(self.configs, self.package, self.elf, self.manifest, self.engine, self.errata, self.md, self.audit_path)
        self.assertNotIn("hash", str(caught.exception).lower())
        self.assertNotIn("span", str(caught.exception).lower())

    def test_complete_baseline_and_determinism(self):
        self.assertEqual(self.baseline["counts_checked"]["units"], 393)
        self.assertEqual(self.baseline["counts_checked"]["weapons_and_actions"], 1485)
        self.assertEqual(self.baseline["counts_checked"]["base_descriptions"], 249)
        self.assertEqual(self.baseline_text, render(self.current)[0])

    def test_dropped_internal_unit_is_detected(self):
        self.current["units"] = [u for u in self.current["units"] if u["unit_id"] != 3999]
        self.current["summary"]["units"] -= 1
        self.reject()

    def test_dropped_weapon_is_detected(self):
        self.unit(1000)["weapons"].pop()
        self.current["summary"]["weapons_and_actions"] -= 1
        self.reject()

    def test_dropped_animation_is_detected(self):
        u = self.unit(3900)
        at = next(i for i, w in enumerate(u["weapons"]) if not w["selector"])
        u["weapons"].pop(at)
        self.reject()

    def test_wrong_weapon_name(self):
        self.unit(1000)["weapons"][0]["name"] = "Wrong weapon"
        self.reject()

    def test_maximum_power_cannot_replace_base_power(self):
        self.unit(1000)["weapons"][1]["power"] = 5100
        self.reject()

    def test_wrong_range(self):
        self.unit(1000)["weapons"][1]["range_max"] += 1
        self.reject()

    def test_wrong_en_cost(self):
        self.unit(3900)["weapons"][0]["en"] += 1
        self.reject()

    def test_wrong_will_requirement(self):
        self.unit(3900)["weapons"][5]["will"] -= 10
        self.reject()

    def test_lost_conditional_gate(self):
        self.unit(1000)["weapons"][4]["gate"] = 0
        self.reject()

    def test_skill_translation_key_is_not_an_assignment_alias(self):
        self.unit(1000)["weapons"][1]["skills"][0]["alias_id"] = 2171
        self.reject()

    def test_dropped_support_pilot(self):
        self.unit(3900)["pilots"].pop(1)
        self.reject()

    def test_wrong_pilot_name(self):
        self.unit(3900)["pilots"][0]["name"] = "Wrong pilot"
        self.reject()

    def test_enemy_and_ally_profiles_cannot_be_merged(self):
        profiles = self.unit(1112)["pilots"][0]["profiles"]
        self.assertGreater(len(profiles), 1)
        profiles[0]["skills"] += profiles[1]["skills"]
        self.reject()

    def test_wrong_pilot_skill_namespace(self):
        self.unit(3900)["pilots"][0]["profiles"][0]["skills"][0]["alias_id"] = 2
        self.reject()

    def test_wrong_pilot_learn_level(self):
        self.unit(3900)["pilots"][0]["profiles"][0]["skills"][0]["learn_level"] = 99
        self.reject()

    def test_no_invented_native_ability_for_empty_record(self):
        self.assertEqual(self.unit(1005)["native_skills"], [])
        self.unit(1005)["native_skills"].append({"slot": 0, "alias_id": 160})
        self.reject()

    def test_unknown_native_reference_cannot_disappear(self):
        u = self.unit(491)
        u["native_skills"] = [s for s in u["native_skills"] if s["alias_id"] != 230]
        self.reject()

    def test_missing_group_membership(self):
        self.unit(1005)["group_ids"] = []
        self.reject()

    def test_inferred_series_cannot_be_called_dictionary_fact(self):
        self.assertEqual(self.unit(491)["series"]["method"], "pilot_association")
        self.unit(491)["series"]["method"] = "unit_dictionary"
        self.reject()

    def test_base_skill_cannot_be_a_template_or_higher_level(self):
        self.current["skills"]["592"]["base_level"] = 65535
        self.reject()

    def test_executable_description_cannot_be_silently_replaced(self):
        self.current["skills"]["983"]["description"] = "Acc,Eva+999"
        self.reject()

    def test_markdown_description_corruption(self):
        self.reject(lambda text: text.replace("Acc,Eva+8", "Acc,Eva+9", 1))

    def test_false_starting_availability_claim(self):
        self.reject(lambda text: text.replace("No gate does **not** mean available at the start of a new game.",
                                              "No gate means available at the start of a new game.", 1))

    def test_summary_cannot_hide_unknown_references(self):
        self.current["summary"]["unresolved_native_references"] = []
        self.reject()

    def test_inputs_remain_byte_identical(self):
        current = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [self.elf] + [self.configs / n for n in CONFIG_FILES]}
        self.assertEqual(current, self.initial_hashes)
        self.assertEqual(collect(self.configs, self.package)["summary"]["package_sha256"],
                         self.source["summary"]["package_sha256"])


if __name__ == "__main__":
    unittest.main()
