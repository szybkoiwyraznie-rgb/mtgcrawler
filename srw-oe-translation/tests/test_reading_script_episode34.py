"""Finale regression/mutations against existing pakiet_EN; no prose copied into Git.

All corruptions happen in temporary generated copies. The four package files and
the delivered Markdown are never changed. Hashes, sizes and offsets are repaired
before rejection, so these tests exercise semantics, not just checksum failures.
"""
import copy
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))
from reading_script_source import ReadingSource, SOURCE_FILES  # noqa: E402
from build_reading_script import build  # noqa: E402
from verify_reading_script import verify  # noqa: E402


class Episode34Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = PROJECT / "pakiet_EN"
        cls.plan_path = PROJECT / "docs/reading-script/episode_34.json"
        if not (cls.package / "00_dialogue.jsonl").exists():
            raise unittest.SkipTest("English package not present")
        cls.plan = json.loads(cls.plan_path.read_bytes())
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        # Preserve the delivered finale's exact frozen source, not a rewritten
        # historical manifest. Only the22 UI notes and ten subsequently audited PL-only title rows
        # may be removed; the resulting whole-file hash must equal the old hash.
        manifest_path = cls.plan_path.parent / cls.plan["source_manifest"]
        frozen_hashes = json.loads(manifest_path.read_bytes())["source_sha256"]
        overrides = {}
        note_file = cls.package / "05_mission_text.jsonl"
        if hashlib.sha256(note_file.read_bytes()).hexdigest() != frozen_hashes[note_file.name]:
            review = json.loads((PROJECT / "config/pl/ui-qa-mission-notes-2026-10-19.json").read_bytes())
            title_review = json.loads((PROJECT / 'config/pl/ui-mission-titles-2026-10-20.json').read_bytes())
            added = {entry['id'] for entry in review['entries'] + title_review['entries']}
            lines = note_file.read_bytes().splitlines(keepends=True)
            old = b"".join(line for line in lines if json.loads(line)['id'] not in added)
            if hashlib.sha256(old).hexdigest() != frozen_hashes[note_file.name]:
                raise ValueError("Unreviewed source change to frozen finale baseline")
            overrides[note_file.name] = old
        names_file = cls.package / "07_names_characters.jsonl"
        if hashlib.sha256(names_file.read_bytes()).hexdigest() != frozen_hashes[names_file.name]:
            kallen_review = json.loads((PROJECT / 'config/pl/char-2320-kallen-2026-10-23.json').read_bytes())
            lines = names_file.read_bytes().splitlines(keepends=True)
            for entry in kallen_review['entries']:
                idx = entry['line_index']
                if not (0 <= idx < len(lines)) or lines[idx] != entry['after_line'].encode('utf-8'):
                    raise ValueError("Unreviewed source change to frozen finale baseline")
                lines[idx] = entry['before_line'].encode('utf-8')
            old_names = b"".join(lines)
            if hashlib.sha256(old_names).hexdigest() != frozen_hashes[names_file.name]:
                raise ValueError("Unreviewed source change to frozen finale baseline")
            overrides[names_file.name] = old_names
        if overrides:
            frozen = Path(cls.temp.name) / 'frozen-package'
            frozen.mkdir()
            for name in SOURCE_FILES:
                if name in overrides:
                    (frozen / name).write_bytes(overrides[name])
                else:
                    shutil.copyfile(cls.package / name, frozen / name)
            cls.package = frozen
        cls.source = ReadingSource(cls.package, 34)
        cls.sids = {s["seq"]: s["id"] for s in cls.source.scenes}
        cls.entry_by_id = {e.id: e for es in cls.source.entries.values() for e in es}
        cls.text, cls.original_audit = build(cls.source, cls.plan)
        cls.original_audit["plan_sha256"] = hashlib.sha256(cls.plan_path.read_bytes()).hexdigest()
        manifest = cls.plan_path.parent / cls.plan["source_manifest"]
        cls.original_audit["source_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        cls.original_payloads = [cls.text[b["start"]:b["end"]] for b in cls.original_audit["blocks"]]
        cls.md = Path(cls.temp.name) / "episode.md"
        cls.audit_path = Path(cls.temp.name) / "audit.json"
        cls.md.write_bytes(cls.text.encode("utf-8"))
        cls.audit_path.write_text(json.dumps(cls.original_audit, ensure_ascii=False), encoding="utf-8")
        # Negative tests must not pass because of an unrelated baseline failure.
        cls.baseline = verify(cls.package, cls.plan_path, cls.md, cls.audit_path)
        assert cls.baseline["status"] == "PASS"

    def setUp(self):
        self.audit = copy.deepcopy(self.original_audit)
        self.payloads = list(self.original_payloads)

    def index(self, seq, order):
        entry = next(e for e in self.source.entries[self.sids[seq]] if e.order == order)
        return self.audit["coverage"][entry.id]["block"]

    def reject(self):
        position = 0
        for block, payload in zip(self.audit["blocks"], self.payloads):
            block["start"], block["end"] = position, position + len(payload)
            position += len(payload)
        data = "".join(self.payloads).encode("utf-8")
        self.audit["output_bytes"] = len(data)
        self.audit["output_sha256"] = hashlib.sha256(data).hexdigest()
        self.md.write_bytes(data)
        self.audit_path.write_text(json.dumps(self.audit, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            verify(self.package, self.plan_path, self.md, self.audit_path)
        self.assertNotIn("hash", str(caught.exception).lower())
        self.assertNotIn("span", str(caught.exception).lower())

    def test_baseline_full_coverage_and_reproducibility(self):
        report = self.baseline
        self.assertEqual(report["source_rows_checked"], 7723)
        self.assertEqual(report["source_scenes_checked"], 7)
        self.assertEqual(report["metrics"]["prose_source"], 7471)
        self.assertEqual(report["metrics"]["prose_shown"], 3338)
        self.assertEqual(report["metrics"]["prose_alias"], 4133)
        self.assertEqual(report["metrics"]["metadata_source"], 210)
        self.assertEqual(report["metrics"]["technical_source"], 42)
        # Regenerated in the repository on 2026-10-24 (the previously delivered copy was
        # lost); it differs from the lost original only in the English name wording
        # (Karen -> Kallen), 212,920 B / 4f1c6c3e... -> 212,780 B / 75f0cb5f...
        self.assertEqual(report["output_bytes"], 212780)
        self.assertEqual(report["output_sha256"],
                         "75f0cb5fd04beb2b1a6611a8529143caf13d1a724e215c1abcc8cd085e4bbe93")
        self.assertEqual(build(self.source, self.plan)[0], self.text)

    def test_changed_opening_narration(self):
        i = self.index(251, 1)
        self.payloads[i] = self.payloads[i][:-2] + " CORRUPTED\n\n"
        self.reject()

    def test_wrong_speaker(self):
        i = self.index(251, 5)
        self.payloads[i] = re.sub(r"\*\*.+?:\*\*", "**Wrong speaker:**", self.payloads[i], count=1)
        self.reject()

    def test_anonymous_voice_is_not_revealed(self):
        i = self.index(254, 597)
        self.payloads[i] = self.payloads[i].replace("**???:**", "**Revealed identity:**")
        self.reject()

    def test_conditional_dialogue_cannot_become_main_story(self):
        i = self.index(251, 44)
        self.payloads[i] = self.payloads[i].removeprefix("> ")
        self.reject()

    def test_failure_cannot_become_a_guaranteed_event(self):
        i = self.index(251, 132)
        self.payloads[i] = self.payloads[i].removeprefix("> ")
        self.reject()

    def test_failure_heading_is_required(self):
        i = next(i for i, b in enumerate(self.audit["blocks"])
                 if "Alternative failure outcome" in b.get("text", ""))
        self.payloads[i] = "#### The next event\n\n"
        self.reject()

    def test_adeus_card_is_meaningful_metadata(self):
        self.payloads[self.index(255, 763)] = "#### Missing heading\n\n"
        self.reject()

    def test_time_heading_is_required(self):
        self.payloads[self.index(254, 894)] = "### Wrong time\n\n"
        self.reject()

    def test_main_ending_last_reply_is_required(self):
        self.payloads[self.index(254, 1759)] = "\n\n"
        self.reject()

    def test_variant_e_last_reply_is_required(self):
        self.payloads[self.index(255, 1802)] = "\n\n"
        self.reject()

    def test_variant_f_additional_battle_dialogue_is_required(self):
        self.payloads[self.index(256, 105)] = "> \n\n"
        self.reject()

    def test_variant_f_additional_pentagona_farewell_is_required(self):
        self.payloads[self.index(256, 1305)] = "\n\n"
        self.reject()

    def test_variant_f_final_thought_is_preserved(self):
        entry = next(e for e in self.source.entries[self.sids[256]]
                     if e.order > 1700 and e.text[0].startswith("("))
        i = self.audit["coverage"][entry.id]["block"]
        self.payloads[i] = self.payloads[i].replace("(", "").replace(")", "")
        self.reject()

    def test_repetition_inside_a_scene_is_not_deduplicated(self):
        entries = self.source.entries[self.sids[254]]
        counts = Counter(e.identity for e in entries)
        repeated = next(e for e in entries if e.kind == "dialogue" and counts[e.identity] > 1)
        self.payloads[self.audit["coverage"][repeated.id]["block"]] = "\n\n"
        self.reject()

    def test_unsafe_alias_to_base_instead_of_f(self):
        source = next(e for e in self.source.entries[self.sids[257]] if e.order == 105)
        wrong_target = self.source.entries[self.sids[254]][0].id
        self.audit["coverage"][source.id]["target"] = wrong_target
        self.reject()

    def test_prose_order_is_preserved(self):
        a, b = self.index(251, 1), self.index(251, 2)
        self.payloads[a], self.payloads[b] = self.payloads[b], self.payloads[a]
        self.reject()

    def test_no_initial_navigation(self):
        self.payloads[0] += "- [Jump ahead](#mission)\n\n"
        self.reject()

    def test_no_unreviewed_extra_ending(self):
        self.payloads[-1] += "An invented extra ending.\n\n"
        self.reject()

    def test_package_remains_unchanged(self):
        self.assertEqual(self.source.hashes, ReadingSource(self.package, 34).hashes)


if __name__ == "__main__":
    unittest.main()
