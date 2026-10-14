#!/usr/bin/env python3
"""token_map: sidecar `tokeny.tsv` - which %s of a display-form jp is a literal and which a kana
token; only the raw bytes of the game file can tell (the display of both is identical)."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
for path in (HERE.parent / "tools", HERE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import item_skill_records as ISR   # noqa: E402
import table_write as TW           # noqa: E402
import token_map as TM             # noqa: E402
from test_item_skill_write import build_member, build_record   # noqa: E402


class FakeContainers:
    def __init__(self, blobs):
        self.blobs = blobs

    def member(self, container, member):
        try:
            return self.blobs[(container, member)]
        except KeyError:
            raise TM.MapError(f"member not found: {container}/{member}")


class KindsTests(unittest.TestCase):
    def test_letters_follow_the_display_order(self):
        raw = b"lit %s" + b"\x0f*" + b"\x0d" + b"%s end"
        self.assertEqual(TW.display(raw), "lit %s%s*%s%s end")
        self.assertEqual(TM.kinds_of(raw), ["L", "T", "C", "L"])

    def test_kana_only_string(self):
        raw = "追加".encode("cp932") + b"\x0f*" + "ﾒｰｼﾞ".encode("cp932")
        self.assertEqual(TM.kinds_of(raw), ["T"])


class BuildMapTests(unittest.TestCase):
    def setUp(self):
        self.blob = build_member(
            "skill",
            [build_record("skill", 1000, "対地", "lit %s ctrl \x0f end")],
            pool_runs=("pool%s\x0f&run",))
        self.parsed = ISR.parse_member(self.blob, "skill", "m.bin", "c.cpk")
        self.rec = self.parsed["records"][0]
        self.containers = FakeContainers({("c.cpk", "m.bin"): self.blob})

    def field_bytes(self):
        start = self.rec["offset"] + self.rec["effect_offset"]
        end = self.blob.find(b"\x00", start)
        return self.blob[start:end]

    def test_record_field_row_resolves_through_the_record(self):
        # the package offset of a field row is the RECORD start - the run there is binary;
        # the map must go through the record's field offset instead
        jp = TW.display(self.field_bytes())
        rows = [{"id": "f1", "category": "skill", "part": "effect", "jp": jp,
                 "source": {"container": "c.cpk", "member": "m.bin",
                            "offset": self.rec["offset"],
                            "record_offset": self.rec["offset"]}}]
        entries, unresolved = TM.build_map(rows, self.containers)
        self.assertEqual(unresolved, [])
        self.assertEqual(entries, [("f1", "L,T", f'"{jp}"')])

    def test_pool_row_resolves_through_the_containing_run(self):
        jp = TW.display(b"pool%s\x0f&run")
        rows = [{"id": "p1", "category": "config_leftover", "jp": jp,
                 "source": {"container": "c.cpk", "member": "m.bin",
                            "offset": self.parsed["tail_offset"] + 4}}]
        entries, unresolved = TM.build_map(rows, self.containers)
        self.assertEqual(unresolved, [])
        self.assertEqual(entries[0][0:2], ("p1", "L,T"))

    def test_record_number_from_the_row_id_when_the_source_has_no_record(self):
        # the real 02/03 rows carry only container/member/offset (the RECORD start); the
        # record number lives in the id: item:config00.cpk/srwDL_Item00.bin:r0:effect
        jp = TW.display(self.field_bytes())
        rows = [{"id": "skill:c.cpk/m.bin:r0:effect", "category": "skill", "part": "effect",
                 "jp": jp,
                 "source": {"container": "c.cpk", "member": "m.bin",
                            "offset": self.rec["offset"]}}]
        entries, unresolved = TM.build_map(rows, self.containers)
        self.assertEqual(unresolved, [])
        self.assertEqual(entries[0][1], "L,T")

    def test_sysmes_style_logical_string_starts_at_the_offset(self):
        # one NUL run holding several logical strings: the row's jp is the slice FROM the
        # offset (the writer slices it the same way), not the whole run
        blob = b"ABC%sDEF%sGHI\x00"
        containers = FakeContainers({("c.cpk", "m.bin"): blob})
        rows = [{"id": "sysmes:c.cpk/m.bin:5", "jp": "DEF%sGHI",
                 "source": {"container": "c.cpk", "member": "m.bin", "offset": 5}}]
        entries, unresolved = TM.build_map(rows, containers)
        self.assertEqual(unresolved, [])
        self.assertEqual(entries, [("sysmes:c.cpk/m.bin:5", "L", '"DEF%sGHI"')])

    def test_raw_form_and_plain_rows_need_no_map(self):
        rows = [{"id": "r1", "jp": "AB\x0f&CD", "source": {}},          # raw form
                {"id": "r2", "jp": "zwykły tekst", "source": {}}]       # no %s at all
        self.assertFalse(TM.needs_map(rows[0]))
        self.assertFalse(TM.needs_map(rows[1]))
        entries, unresolved = TM.build_map(rows, self.containers)
        self.assertEqual(entries, [])
        self.assertEqual(unresolved, [])

    def test_unresolvable_row_is_reported_not_guessed(self):
        rows = [{"id": "x1", "category": "skill", "part": "effect", "jp": "coś%sinnego",
                 "source": {"container": "c.cpk", "member": "m.bin", "offset": 0}}]
        entries, unresolved = TM.build_map(rows, self.containers)
        self.assertEqual(entries, [])
        self.assertEqual(len(unresolved), 1)
        self.assertIn("x1", unresolved[0])

    def test_missing_container_is_reported(self):
        rows = [{"id": "x2", "jp": "a%sb", "source": {"container": "brak.cpk",
                                                      "member": "m.bin", "offset": 0}}]
        entries, unresolved = TM.build_map(rows, FakeContainers({}))
        self.assertEqual(entries, [])
        self.assertEqual(len(unresolved), 1)


class WriteLoadTests(unittest.TestCase):
    def test_roundtrip_and_sidecar_discovery(self):
        entries = [("id:1", "L,T", '"jp1"'), ("id:2", "T", '"jp2%s"')]
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            out = package / TM.SIDECAR_NAME
            TM.write_map(out, entries)
            table = TM.load_map(out)
            self.assertEqual(table["id:1"], ("jp1", ["L", "T"]))
            self.assertEqual(table["id:2"], ("jp2%s", ["T"]))
            self.assertEqual(TM.find_sidecar([package]), out)
            self.assertEqual(TM.find_sidecar([package / "02_items.jsonl"]), out)
            self.assertIsNone(TM.find_sidecar([package / "brak" / "cos.jsonl"]))

    def test_header_comments_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / TM.SIDECAR_NAME
            TM.write_map(out, [])
            self.assertEqual(TM.load_map(out), {})
            self.assertTrue(out.read_text(encoding="utf-8").startswith("# tokeny.tsv"))


if __name__ == "__main__":
    unittest.main()
