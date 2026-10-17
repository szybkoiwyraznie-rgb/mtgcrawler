"""End-to-end synthetic rendering and independent-verifier mutation tests."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from reading_script_source import ReadingSource  # noqa: E402
from build_reading_script import build, escape  # noqa: E402
from verify_reading_script import verify, decode  # noqa: E402


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fixture(root):
    package = root / "package"
    package.mkdir()
    base = [
        ("narration", "A synthetic\nopening.\n\nAnother paragraph.", None, "fixture"),
        ("location", "＃Test room", None, "fixture"),
        ("dialogue", "A repeated line.", 1, "fixture"),
        ("dialogue", "Hello, ＜主人公名＞!", 4501, "fixture"),
        ("dialogue", "A repeated line.", 1, "fixture"),
        ("dialogue", "＃???\nAn anonymous voice.", 1, "＃？？？\nfixture"),
        ("dialogue", r"Literal *stars*, _underscores_, [brackets], <tags>, &amp; and \\.", 2, "fixture"),
        ("label", "A synthetic card", None, "fixture"),
        ("dialogue", "First paragraph.\n\nSecond paragraph.", 1, "fixture"),
        ("dialogue", "An alternative outcome.", 1, "fixture"),
        ("dialogue", "The synthetic ending.", 4501, "fixture"),
        ("help", "UI instruction, not story prose.", None, "fixture"),
    ]
    variant = list(base)
    variant[2] = ("dialogue", "A repeated line!", 1, "fixture")
    variant[4] = ("dialogue", "A repeated line.", 2, "fixture")  # speaker-only change
    variant.insert(4, ("dialogue", "A variant-only line.", 2, "fixture"))
    alias = [(kind, en.replace("\n", "\r\n") + "\n", key, jp) for kind, en, key, jp in variant]
    rows, scenes, planned = [], [], []
    for seq, contents, label in ((1, base, None), (2, variant, "E"), (3, alias, "J")):
        sid = f"fixture/{seq}"
        local = []
        for order, (kind, en, key, jp) in enumerate(contents, 1):
            r = {"id": f"dlg:{sid}:{order}", "scene": sid, "order": order,
                 "kind": kind, "en": en, "jp": jp}
            if key is not None:
                r["speaker"] = {"id": key, "jp": f"fixture speaker {key}", "source": "fixture"}
            local.append(r)
        rows.extend(local)
        s = {"id": sid, "seq": seq, "series": "story", "episode": 34, "rows": len(local)}
        if seq == 1:
            s["mission_row"] = "mission:fixture"
        else:
            s.update(variant_of="fixture/1", variant=label)
        scenes.append(s)
        p = {"id": sid, "seq": seq, "reviewed": True, "mode": {1: "full", 2: "variant", 3: "alias"}[seq]}
        if seq == 3:
            p["of"] = 2
        else:
            failure = next(r["order"] for r in local if r["en"] == "An alternative outcome.")
            p["sections"] = [
                {"at": 1, "mode": "story", "heading": None},
                {"at": 3, "mode": "conditional", "heading": "Conditional dialogue — synthetic encounter"},
                {"at": failure, "mode": "failure", "heading": "Alternative failure outcome — synthetic"},
                {"at": failure + 1, "mode": "story", "heading": "Synthetic ending"},
            ]
            if seq == 1:
                p["chapter"] = 1
            else:
                p.update(of=1, label="E")
        planned.append(p)
    names = [{"key": key, "part": "nickname", "en": name} for key, name in
             ((1, "Alice"), (2, "Bob"), (4501, "Seishiro"))]
    datasets = {"00_dialogue.jsonl": rows, "05_mission_text.jsonl": [
        {"id": "mission:fixture", "en": "Episode 34\nSynthetic mission"}],
        "06_scenes.jsonl": scenes, "07_names_characters.jsonl": names}
    for filename, data in datasets.items():
        (package / filename).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in data), encoding="utf-8")
    source = ReadingSource(package, 34)
    write_json(root / "inventory.json", source.inventory())
    plan = {"schema_version": 1, "episode": 34, "reviewed": True,
            "source_manifest": "inventory.json", "context_entries": 2, "scenes": planned}
    write_json(root / "plan.json", plan)
    text, audit = build(source, plan)
    audit["plan_sha256"] = hashlib.sha256((root / "plan.json").read_bytes()).hexdigest()
    audit["source_manifest_sha256"] = hashlib.sha256((root / "inventory.json").read_bytes()).hexdigest()
    return package, source, plan, text, audit


class ReadingPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package, self.source, self.plan, self.text, self.audit = fixture(self.root)
        self.payloads = [self.text[b["start"]:b["end"]] for b in self.audit["blocks"]]

    def persist(self):
        # Deliberately repair hashes AND every character offset after mutations.
        position = 0
        for block, payload in zip(self.audit["blocks"], self.payloads):
            block.update(start=position, end=position + len(payload))
            position += len(payload)
        data = "".join(self.payloads).encode("utf-8")
        self.audit["output_sha256"] = hashlib.sha256(data).hexdigest()
        self.audit["output_bytes"] = len(data)
        (self.root / "edition.md").write_bytes(data)
        write_json(self.root / "audit.json", self.audit)

    def check(self):
        self.persist()
        return verify(self.package, self.root / "plan.json", self.root / "edition.md", self.root / "audit.json")

    def index(self, rid):
        return self.audit["coverage"][rid]["block"]

    def rejects_semantically(self):
        with self.assertRaises(ValueError) as caught:
            self.check()
        self.assertNotIn("hash", str(caught.exception).lower())
        self.assertNotIn("span", str(caught.exception).lower())

    def test_full_roundtrip_and_determinism(self):
        self.assertEqual(self.check()["status"], "PASS")
        text2, audit2 = build(self.source, self.plan)
        self.assertEqual(self.text, text2)
        self.assertEqual(audit2["coverage"], self.audit["coverage"])
        self.assertEqual(self.audit["metrics"]["prose_shown"] + self.audit["metrics"]["prose_alias"],
                         self.audit["metrics"]["prose_source"])

    def test_same_scene_repeated_lines_are_both_shown(self):
        self.assertNotEqual(self.index("dlg:fixture/1:3"), self.index("dlg:fixture/1:5"))
        self.assertEqual(self.check()["status"], "PASS")

    def test_speaker_only_variant_is_not_an_alias(self):
        self.assertEqual(self.audit["coverage"]["dlg:fixture/2:6"]["status"], "shown")
        self.assertIn("**Bob:** A repeated line.", self.text)

    def test_markup_roundtrip(self):
        for value in (r"*a* _b_ [c] <d> &amp; \\.", "- bullet", "+ plus", "1. item", "2) item", "# title", "`code`"):
            self.assertEqual(decode(escape(value)), value)
        self.assertEqual(self.check()["status"], "PASS")

    def test_changed_narration_rejected_with_repaired_hashes(self):
        i = self.index("dlg:fixture/1:1")
        self.payloads[i] = self.payloads[i].replace("synthetic", "invented")
        self.rejects_semantically()

    def test_missing_final_line_rejected(self):
        self.payloads[self.index("dlg:fixture/1:11")] = "\n\n"
        self.rejects_semantically()

    def test_flattened_paragraphs_rejected(self):
        i = self.index("dlg:fixture/1:9")
        self.payloads[i] = self.payloads[i].replace("\n>\n> ", " ")
        self.rejects_semantically()

    def test_wrong_speaker_rejected(self):
        i = self.index("dlg:fixture/1:3")
        self.payloads[i] = self.payloads[i].replace("Alice", "Bob")
        self.rejects_semantically()

    def test_anonymity_loss_rejected(self):
        i = self.index("dlg:fixture/1:6")
        self.payloads[i] = self.payloads[i].replace("???", "Alice")
        self.rejects_semantically()

    def test_dynamic_token_leak_rejected(self):
        i = self.index("dlg:fixture/1:4")
        self.payloads[i] = self.payloads[i].replace("Hello, Seishiro!", "Hello, ＜主人公名＞!")
        self.rejects_semantically()

    def test_conditional_presented_as_main_story_rejected(self):
        i = self.index("dlg:fixture/1:3")
        self.payloads[i] = self.payloads[i].removeprefix("> ")
        self.rejects_semantically()

    def test_failure_label_loss_rejected(self):
        i = next(i for i, b in enumerate(self.audit["blocks"]) if "Alternative failure outcome" in b.get("text", ""))
        self.payloads[i] = "#### Successful continuation\n\n"
        self.rejects_semantically()

    def test_meaningful_label_loss_rejected(self):
        i = self.index("dlg:fixture/1:8")
        self.payloads[i] = "### Wrong card\n\n"
        self.rejects_semantically()

    def test_reordered_prose_rejected(self):
        a, b = self.index("dlg:fixture/1:3"), self.index("dlg:fixture/1:4")
        self.payloads[a], self.payloads[b] = self.payloads[b], self.payloads[a]
        self.rejects_semantically()

    def test_variant_unique_line_loss_rejected(self):
        self.payloads[self.index("dlg:fixture/2:5")] = "\n\n"
        self.rejects_semantically()

    def test_false_alias_rejected(self):
        self.audit["coverage"]["dlg:fixture/3:5"]["target"] = "dlg:fixture/1:3"
        self.rejects_semantically()

    def test_initial_navigation_rejected(self):
        self.payloads[0] = "- [Jump to mission](#mission)\n\n" + self.payloads[0]
        self.rejects_semantically()

    def test_alias_must_match_english_not_just_metadata(self):
        bad = copy.deepcopy(self.plan)
        bad["scenes"][1] = {"id": "fixture/2", "seq": 2, "reviewed": True, "mode": "alias", "of": 1}
        with self.assertRaisesRegex(ValueError, "Unsafe whole-scene alias"):
            build(self.source, bad)

    def test_unreviewed_plan_rejected(self):
        self.plan["reviewed"] = False
        with self.assertRaisesRegex(ValueError, "reviewed"):
            build(self.source, self.plan)

    def test_incorrect_inventory_counts_rejected_even_with_repaired_hash(self):
        path = self.root / "inventory.json"
        manifest = json.loads(path.read_text())
        manifest["scenes"][1]["changed_prose"] += 1
        write_json(path, manifest)
        self.audit["source_manifest_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.rejects_semantically()

    def test_input_package_unchanged(self):
        self.check()
        self.assertEqual(self.source.hashes, ReadingSource(self.package, 34).hashes)


if __name__ == "__main__":
    unittest.main()
