"""Owner story-language edits are exact, source-bound and prose-only."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pl_release_package as R
import pl_story_corrections as S


class StoryCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base = self.root / "base"
        self.stored = self.root / "snapshot"
        self.base.mkdir()
        self.stored.mkdir()
        self.source = dict(
            id="dlg:test.bin:10",
            category="dialogue",
            kind="dialogue",
            part="dialogue",
            jp="一行目。\n試してみたら？",
            en="First line.\nWhy not try it?",
            speaker={"id": 1, "jp": "テスト", "source": "charalist"},
            scene="test.bin",
            order=1,
            bytes=20,
            mode="event",
            max_bytes=None,
            source={"container": "test.cpk", "member": "test.bin", "offset": 10},
        )
        (self.base / "00_dialogue.jsonl").write_text(
            json.dumps(self.source, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self.binding = R.binding(self.source)
        self.entry = dict(
            file="00_dialogue.jsonl",
            id=self.source["id"],
            source_sha256=self.binding,
            pl="Pierwsza linia.\nMoże się przekonasz?",
        )
        data = (R.canonical(self.entry) + "\n").encode()
        (self.stored / R.DATA).write_bytes(data)
        self.manifest = dict(
            schema=1,
            entries=1,
            data_sha256=hashlib.sha256(data).hexdigest(),
            source_return=dict(name="unchanged.zip", sha256="b" * 64),
        )
        (self.stored / R.MANIFEST).write_text(json.dumps(self.manifest), encoding="utf-8")
        self.edit = dict(
            file=self.entry["file"],
            id=self.entry["id"],
            source_sha256=self.binding,
            before=self.entry["pl"],
            after="Pierwsza linia.\nMoże spróbuj?",
            reason="test invitation",
        )
        self.plan = self.root / "story-ep01.json"

    def run_plan(self, edits=None, out_name="out"):
        self.plan.write_text(
            json.dumps(dict(schema=1, episode=1, changes=edits or [self.edit]), ensure_ascii=False),
            encoding="utf-8",
        )
        return S.apply(self.base, self.stored, self.plan, self.root / out_name)

    def test_changes_only_pl_and_records_story_provenance(self):
        result = self.run_plan()
        self.assertEqual(result["source_return"], self.manifest["source_return"])
        self.assertEqual(result["entries"], 1)
        self.assertEqual(
            json.loads((self.root / "out" / R.DATA).read_text(encoding="utf-8"))["pl"],
            self.edit["after"],
        )
        self.assertEqual(
            json.loads((self.stored / R.DATA).read_text(encoding="utf-8"))["pl"],
            self.entry["pl"],
        )
        ledger = result[S.LEDGER]
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["plan"], self.plan.name)
        self.assertEqual(ledger[0]["episode"], 1)
        self.assertEqual(ledger[0]["previous_data_sha256"], self.manifest["data_sha256"])
        self.assertFalse(ledger[0]["runtime_tested"])

    def test_explicit_copy_alias_must_be_included_with_same_text(self):
        copy_source = dict(
            self.source,
            id="dlg:test-copy.bin:10",
            copy_of=self.source["id"],
            scene="test-copy.bin",
            order=2,
            source={"container": "test-copy.cpk", "member": "test-copy.bin", "offset": 10},
        )
        (self.base / "00_dialogue.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in (self.source, copy_source)),
            encoding="utf-8",
        )
        copy_binding = R.binding(copy_source)
        copy_entry = dict(self.entry, id=copy_source["id"], source_sha256=copy_binding)
        entries = sorted(
            (self.entry, copy_entry), key=lambda entry: (entry["file"], entry["source_sha256"])
        )
        data = "".join(R.canonical(entry) + "\n" for entry in entries).encode()
        (self.stored / R.DATA).write_bytes(data)
        manifest = dict(self.manifest, entries=2, data_sha256=hashlib.sha256(data).hexdigest())
        (self.stored / R.MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "omits explicit copy alias"):
            self.run_plan(out_name="copy-missing")

        copy_edit = dict(
            self.edit,
            id=copy_source["id"],
            source_sha256=copy_binding,
            reason="explicit DLC copy of the same line",
        )
        result = self.run_plan([self.edit, copy_edit], out_name="copy-complete")
        self.assertEqual(result["entries"], 2)
        written = {
            entry["id"]: entry["pl"]
            for entry in map(
                json.loads, (self.root / "copy-complete" / R.DATA).read_text(encoding="utf-8").splitlines()
            )
        }
        self.assertEqual(set(written.values()), {self.edit["after"]})

    def test_stale_binding_id_or_previous_text_is_refused(self):
        for field in ("source_sha256", "id", "before"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "stale"):
                    self.run_plan([{**self.edit, field: "wrong"}], out_name=f"out-{field}")
                self.assertFalse((self.root / f"out-{field}").exists())

    def test_line_break_control_duplicate_and_wrong_file_are_refused(self):
        bad_edits = (
            {**self.edit, "after": "Pierwsza linia. Może spróbuj?"},
            {**self.edit, "after": "Pierwsza linia.\nMoże spróbuj?\x0f"},
            {**self.edit, "after": self.edit["before"]},
            {**self.edit, "file": "04_config_text.jsonl"},
        )
        for index, edit in enumerate(bad_edits):
            with self.subTest(index=index), self.assertRaises(ValueError):
                self.run_plan([edit], out_name=f"bad-{index}")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.run_plan([self.edit, self.edit], out_name="bad-duplicate")


if __name__ == "__main__":
    unittest.main()
