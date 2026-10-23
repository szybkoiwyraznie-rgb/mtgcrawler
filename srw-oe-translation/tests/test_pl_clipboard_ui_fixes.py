"""Tests for the 2026-10-21 Polish UI & terrain fixes (Clipboard-1..4.jpg)."""
import hashlib
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pl_release_package as R
import pl_text
import terrain_names as T
import translation_check as C


def _synthetic_attr_from_en_package() -> bytes:
    """Construct the exact 145-record Japanese attr.par name layout from 10_map_terrain.jsonl
    and verify validate_row/patch_attr mechanics on synthetic + real record layouts."""
    rows = [
        json.loads(line)
        for line in (ROOT / "pakiet_EN" / "10_map_terrain.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    buf = bytearray(4 + T.RECORDS * T.RECORD_SIZE)
    struct.pack_into("<I", buf, 0, T.RECORDS)
    for idx in range(T.RECORDS):
        # Opaque non-name attribute bytes (32..64) filled deterministically to prove mask safety.
        for b in range(T.NAME_SIZE, T.RECORD_SIZE):
            buf[4 + idx * T.RECORD_SIZE + b] = (idx * 7 + b) & 0xFF
    for row in rows:
        idx = row["record"]
        jp = row["jp"].encode("cp932")
        buf[4 + idx * T.RECORD_SIZE : 4 + idx * T.RECORD_SIZE + len(jp)] = jp
    return bytes(buf)


class ClipboardUIFixesTests(unittest.TestCase):
    def test_terrain_validate_row_keeps_english_ascii_and_supports_polish_diacritics(self):
        row = {
            "id": "terrain:lmap.cpk/attr.par:r7:name",
            "category": "terrain_name",
            "part": "name",
            "record": 7,
            "jp": "森／高台",
            "en": "Las/Wzgórze",
            "bytes": 8,
            "mode": "slot",
            "max_bytes": 31,
            "source": {"container": "lmap.cpk", "member": "attr.par", "offset": 4 + 7 * 64},
        }
        with self.assertRaisesRegex(T.TerrainError, "printable ASCII"):
            T.validate_row(row, target_lang="en")

        encoded = T.validate_row(row, target_lang="pl")
        self.assertEqual(encoded, pl_text.encode("Las/Wzgórze"))
        self.assertEqual(pl_text.display_width("Las/Wzgórze"), 11)
        self.assertEqual(C.check_row({**row, "pl": "Las/Wzgórze"}, field="pl"), ([], []))
        self.assertTrue(C.check_row(row, field="en")[0])

        too_wide = {**row, "en": "Śnieżne wzgórze"}
        with self.assertRaisesRegex(T.TerrainError, "screen budget"):
            T.validate_row(too_wide, target_lang="pl")

    def test_patch_attr_preserves_all_non_name_bytes_for_polish_diacritics(self):
        blob = _synthetic_attr_from_en_package()
        fake_sha = hashlib.sha256(blob).hexdigest()
        en_rows = {
            r["id"]: r
            for r in (
                json.loads(line)
                for line in (ROOT / "pakiet_EN" / "10_map_terrain.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        pl_map = {
            e["id"]: e["pl"]
            for e in (
                json.loads(line)
                for line in (ROOT / "pakiet_PL" / R.DATA).read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
            if e["file"] == "10_map_terrain.jsonl"
        }
        merged = [{**r, "en": pl_map[rid]} for rid, r in en_rows.items()]
        orig_sha = T.ORIGINAL_SHA256
        try:
            T.ORIGINAL_SHA256 = fake_sha
            patched, detail = T.patch_attr(blob, merged, target_lang="pl")
            # Second pass is idempotent on already-patched Polish cells.
            patched_again, detail_again = T.patch_attr(patched, merged, target_lang="pl")
        finally:
            T.ORIGINAL_SHA256 = orig_sha

        self.assertEqual(patched, patched_again)
        self.assertEqual(detail["changed"], len(en_rows))
        self.assertEqual(detail_again["changed"], 0)
        self.assertTrue(detail["outside_name_cells_unchanged"])
        # Verify record 3 ('Wzgórze') and record 7 ('Las/Wzgórze') in exact 32-byte cells.
        self.assertEqual(patched[4 + 3 * 64 : 4 + 3 * 64 + 32], pl_text.encode("Wzgórze").ljust(32, b"\0"))
        self.assertEqual(patched[4 + 7 * 64 : 4 + 7 * 64 + 32], pl_text.encode("Las/Wzgórze").ljust(32, b"\0"))

    def test_stored_snapshot_has_all_four_clipboard_fixes(self):
        plan = json.loads((ROOT / "config" / "pl" / "ui-clipboard-2026-10-21.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["schema"], 1)
        self.assertEqual(len(plan["changes"]), 51)

        base_jp = {
            ("04_config_text.jsonl", R.binding(r)): r["jp"]
            for r in (
                json.loads(line)
                for line in (ROOT / "pakiet_EN" / "04_config_text.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        entries_by_binding = {
            (e["file"], e["source_sha256"]): e["pl"]
            for e in (
                json.loads(line)
                for line in (ROOT / "pakiet_PL" / R.DATA).read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        entries = {
            (e["file"], e["id"]): e["pl"]
            for e in (
                json.loads(line)
                for line in (ROOT / "pakiet_PL" / R.DATA).read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        spirit_pool_by_jp = {
            jp: entries_by_binding[("04_config_text.jsonl", bsha)]
            for (_, bsha), jp in base_jp.items()
            if jp in (" HP", "機 <移動力上昇>＠")
        }
        # Clipboard-1.jpg: tail-pool fragment #35 (jp=' HP') -> ' Odnawia ', while pool #23 (Wiatr) stays intact
        self.assertEqual(spirit_pool_by_jp[" HP"], " Odnawia ")
        self.assertEqual(spirit_pool_by_jp["機 <移動力上昇>＠"], "jedn. <Ruch w górę>＠")
        # Clipboard-2.jpg & Clipboard-3.jpg: Defend/Evade bar space before green 30%
        self.assertEqual(entries[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:11644")], "＠0Obrażenia ＠230％＠0 mniej")
        self.assertEqual(entries[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:11647")], "Obrażenia ＠230％＠0 mniej")
        self.assertEqual(entries[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:11672")], "＠0Premia do uniku ＠230％＠0 więcej")
        self.assertEqual(entries[("04_config_text.jsonl", "sysmes:configst.cpk/sysmes.bin:11675")], "Premia do uniku ＠230％＠0 więcej")
        # Clipboard-4.jpg + full map terrain diacritics
        self.assertEqual(entries[("10_map_terrain.jsonl", "terrain:lmap.cpk/attr.par:r3:name")], "Wzgórze")
        self.assertEqual(entries[("10_map_terrain.jsonl", "terrain:lmap.cpk/attr.par:r7:name")], "Las/Wzgórze")


if __name__ == "__main__":
    unittest.main()
