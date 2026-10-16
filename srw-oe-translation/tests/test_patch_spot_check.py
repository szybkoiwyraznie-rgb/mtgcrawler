"""Synthetic tests for tools/patch_spot_check.py (no game data)."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
sys.path.insert(0, str(HERE))

import patch_spot_check as PSC  # noqa: E402
from test_configst_pack import make_pac  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402


def cp932(text: str) -> bytes:
    return text.encode("cp932")


def row(row_id, container, member, en, jp="日本語", **extra):
    base = {"id": row_id, "category": "dialogue", "part": "dialogue", "jp": jp, "en": en,
            "mode": "grow", "source": {"container": container, "member": member, "offset": 0}}
    base.update(extra)
    return base


class SequenceTests(unittest.TestCase):
    def test_pieces_drop_the_placeholders_and_empty_parts(self):
        self.assertEqual(PSC.pieces_of("%sA%sB%s"), [b"A", b"B"])
        self.assertEqual(PSC.pieces_of("plain"), [b"plain"])
        self.assertEqual(PSC.pieces_of("%s%s"), [])

    def test_pieces_must_follow_in_order_within_the_gap(self):
        body = b"xx" + b"ALPHA" + b"%s" + b"BETA" + b"\x00" * 20 + b"ALPHA" + b"\x00" * 20 + b"BETA"
        self.assertEqual(PSC.count_sequence(body, [b"ALPHA", b"BETA"]), 1)
        self.assertEqual(PSC.count_sequence(body, [b"ALPHA"]), 2)
        self.assertEqual(PSC.count_sequence(body, [b"ALPHA", b"BETA"], max_gap=40), 2)
        self.assertEqual(PSC.count_sequence(body, [b"GAMMA"]), 0)

    def test_matches_do_not_overlap(self):
        self.assertEqual(PSC.count_sequence(b"aaaa", [b"aa"]), 2)


class RequiredHitsTests(unittest.TestCase):
    def test_record_and_offset_rows_of_one_field_need_one_hit(self):
        record = {"id": "item:c/srwDL_Item00.bin:r0:name", "part": "name", "record": 0,
                  "source": {"offset": 1208}}
        offset = {"id": "item:c/srwDL_Item00.bin:1262", "part": "text",
                  "source": {"offset": 1262}}
        self.assertEqual(PSC.required_hits([record, offset], "srwDL_Item00.bin"), 1)
        self.assertEqual(PSC.required_hits([record, record, offset], "srwDL_Item00.bin"), 2)
        self.assertEqual(PSC.required_hits([offset, offset], "srwDL_Item00.bin"), 2)

    def test_pool_members_need_one_hit(self):
        rows = [{"id": "a", "part": "name", "source": {}}, {"id": "b", "part": "name", "source": {}}]
        self.assertEqual(PSC.required_hits(rows, "srwDL_CharaDictionary00.bin"), 1)
        self.assertEqual(PSC.required_hits(rows, "DL100_01.bin"), 2)


class ContainerTests(unittest.TestCase):
    def build(self, tmp: Path):
        event = build_synthetic_cpk([
            {"name": "DL100_01.bin", "data": b"\x00" * 8 + cp932("HELLO there\r\n") + b"\x00" * 8
                                         + cp932("HELLO there\r\n") + b"\x00" * 8, "id": 0},
            {"name": "DL100_02.bin", "data": b"\x00" * 16, "id": 1},
        ])
        pac = make_pac([("srwDL_Item00.bin", b"\x00" * 4 + cp932("Repair Kit") + b"\x00" * 4),
                        ("srwDL_CharaDictionary00.bin", b"\x00" * 4 + cp932("Amuro") + b"\x00" * 4)])
        config = build_synthetic_cpk([{"name": "config00.pac", "data": pac, "id": 0}])
        quotes = build_synthetic_cpk([{"name": "p0050.pac",
                                       "data": b"\x00" * 16 + b"EDAT" + cp932("Fire!") + b"\x00" * 8,
                                       "id": 0}])
        built = tmp / "patch" / "DLC"
        built.mkdir(parents=True)
        (built / "eventP00.cpk").write_bytes(event)
        (built / "config00.cpk").write_bytes(config)
        (built / "mesbtl00.cpk").write_bytes(quotes)
        return tmp / "patch"

    def test_member_bodies_split_pacs_and_keep_quote_packs_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            built = self.build(Path(tmp))
            names = [n for n, _ in PSC.member_bodies(built / "DLC" / "config00.cpk")]
            self.assertEqual(names, ["srwDL_Item00.bin", "srwDL_CharaDictionary00.bin"])
            names = [n for n, _ in PSC.member_bodies(built / "DLC" / "mesbtl00.cpk")]
            self.assertEqual(names, ["p0050.pac"])
            found = PSC.find_containers(built)
            self.assertEqual(list(found), ["config00.cpk", "eventP00.cpk", "mesbtl00.cpk"])
            self.assertEqual(list(PSC.find_containers(built, ["eventP00.cpk"])), ["eventP00.cpk"])

    def test_check_counts_landed_missing_short_and_containerless(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            built = self.build(tmp)
            package = tmp / "pkg"
            package.mkdir()
            rows00 = [
                row("dlg:eventP00.cpk/DL100_01.bin:8", "eventP00.cpk", "DL100_01.bin", "HELLO there\r\n"),
                row("dlg:eventP00.cpk/DL100_01.bin:40", "eventP00.cpk", "DL100_01.bin", "HELLO there\r\n",
                    copy_of="dlg:eventP00.cpk/DL100_01.bin:8"),
                row("dlg:eventP00.cpk/DL100_02.bin:0", "eventP00.cpk", "DL100_02.bin", "MISSING text"),
                row("dlg:eventP00.cpk/DL100_02.bin:4", "eventP00.cpk", "DL100_02.bin", ""),
                row("dlg:eventP00.cpk/DL100_02.bin:6", "eventP00.cpk", "DL100_02.bin", "ok"),
                row("dlg:eventP01.cpk/DL200_01.bin:0", "eventP01.cpk", "DL200_01.bin", "elsewhere"),
            ]
            rows01 = [row("quo:mesbtl00.cpk/p0050.pac:20", "mesbtl00.cpk", "p0050.pac", "Fire!",
                          category="battle_quote", part="quote")]
            rows02 = [{"id": "item:config00.cpk/srwDL_Item00.bin:r0:name", "category": "config_item",
                       "part": "name", "record": 0, "jp": "修理キット", "en": "Repair Kit",
                       "source": {"container": "config00.cpk", "member": "srwDL_Item00.bin",
                                  "offset": 0}}]
            rows04 = [{"id": "item:config00.cpk/srwDL_Item00.bin:4", "category": "config_item",
                       "part": "text", "jp": "修理キット", "en": "Repair Kit",
                       "source": {"container": "config00.cpk", "member": "srwDL_Item00.bin",
                                  "offset": 4}}]
            rows07 = [{"id": "char:1:name", "category": "character_name", "part": "name",
                       "jp": "アムロ", "en": "Amuro", "key": 1,
                       "source": {"container": None, "member": "srwDL_CharaDictionary", "offset": None}},
                      {"id": "char:2:name", "category": "character_name", "part": "name",
                       "jp": "シャア", "en": "Char Aznable", "key": 2,
                       "source": {"container": None, "member": "srwDL_CharaDictionary", "offset": None}}]
            for name, rows in (("00_dialogue.jsonl", rows00), ("01_battle_quotes.jsonl", rows01),
                               ("02_items.jsonl", rows02), ("04_config_text.jsonl", rows04),
                               ("07_names_characters.jsonl", rows07)):
                with (package / name).open("w", encoding="utf-8") as handle:
                    for r in rows:
                        handle.write(json.dumps(r, ensure_ascii=False) + "\n")

            report = PSC.check(package, built)
            self.assertEqual(report["rows_filled"], 10)
            self.assertEqual(report["not_built"], 1)                 # eventP01 is not in the build
            self.assertEqual(report["rows_checked"], 9)
            self.assertEqual(report["landed"], 6)
            self.assertEqual(report["missing"], 2)
            self.assertEqual(report["short"], 1)
            self.assertEqual(report["missing_ids"], ["dlg:eventP00.cpk/DL100_02.bin:0", "char:2:name"])
            self.assertEqual(report["short_ids"], ["dlg:eventP00.cpk/DL100_02.bin:6"])
            ev = report["containers"]["eventP00.cpk"]
            self.assertEqual((ev["rows"], ev["landed"], ev["missing"], ev["short"]), (4, 2, 1, 1))
            cf = report["containers"]["config00.cpk"]
            self.assertEqual((cf["rows"], cf["landed"], cf["missing"]), (2, 2, 0))
            self.assertEqual(report["containers"]["mesbtl00.cpk"]["landed"], 1)
            # the container-less names may land in any container: Amuro is in the dictionary,
            # Char is nowhere
            cl = report["containerless"]
            self.assertEqual((cl["rows"], cl["landed"], cl["missing"]), (2, 1, 1))
            self.assertEqual(report["per_file"]["00_dialogue.jsonl"]["landed"], 2)

    def test_group_shortfall_is_reported_with_its_hits(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            built = self.build(tmp)
            package = tmp / "pkg"
            package.mkdir()
            rows = [row(f"dlg:eventP00.cpk/DL100_01.bin:{i}", "eventP00.cpk", "DL100_01.bin",
                        "HELLO there\r\n") for i in range(3)]      # the member holds it twice
            with (package / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
                for r in rows:
                    handle.write(json.dumps(r, ensure_ascii=False) + "\n")
            report = PSC.check(package, built)
            self.assertEqual((report["landed"], report["missing"]), (2, 1))
            self.assertEqual(report["missing_ids"],
                             ["dlg:eventP00.cpk/DL100_01.bin:2  [group of 3: 2/3 hits]"])

    def test_cli_writes_report_and_missing_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            built = self.build(tmp)
            package = tmp / "pkg"
            package.mkdir()
            rows = [row("dlg:eventP00.cpk/DL100_01.bin:8", "eventP00.cpk", "DL100_01.bin", "HELLO there\r\n"),
                    row("dlg:eventP00.cpk/DL100_02.bin:0", "eventP00.cpk", "DL100_02.bin", "MISSING text")]
            with (package / "00_dialogue.jsonl").open("w", encoding="utf-8") as handle:
                for r in rows:
                    handle.write(json.dumps(r, ensure_ascii=False) + "\n")
            missing = tmp / "missing.txt"
            with contextlib.redirect_stdout(io.StringIO()) as console:
                code = PSC.main(["--package", str(package), "--built", str(built),
                                 "--out", str(missing)])
            self.assertEqual(code, 1)                                # something is missing
            self.assertIn("trafione: 1; brak: 1", console.getvalue())
            report = json.loads((built / "spot_check.json").read_text(encoding="utf-8"))
            self.assertEqual(report["missing"], 1)
            self.assertEqual(missing.read_text(encoding="utf-8").splitlines()[1],
                             "dlg:eventP00.cpk/DL100_02.bin:0")

    def test_missing_folders_are_an_error_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                code = PSC.main(["--package", tmp, "--built", str(Path(tmp) / "nope")])
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
