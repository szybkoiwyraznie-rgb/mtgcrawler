"""PL non-dialogue prose audit (2026-10-26): unit-data panel + system messages.

No language review had ever covered the ``02_items``/``03_skills``/
``04_config_text``/``05_mission_text`` polish rows (28,431 PL rows).  The
controlled-class scans found the prose itself clean, but two systemic defects
stood out:

* ``08_names_units_weapons`` ``weight``/``length`` (348 rows, 25 distinct
  strings) still carried the ENGLISH column - ``Weight ...``/``Len. ...``,
  ``Empty Wt.``, ``Dry Weight`` - even though the translated rows of the very
  same field already use ``Masa 54,0 t`` / ``Dł. 25,0 m``.  The unit-data
  panel of the mech dictionary was therefore half translated, half English.
* ``04_config_text`` ``sysmes`` (9 rows): the save-failure prompts were still
  ``Save failed. ...`` in English, and the overlapping full-version string
  ``製品版をダウンロードします。`` carried the game title instead of its meaning
  (the English column has the same defect - out of scope here).

This module pins the source-bound plan, the snapshot ledger chain, the
resulting text, the width rule and the copy-group consistency.  It needs no
game files.
"""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pl_release_package as R  # noqa: E402
import pl_text  # noqa: E402
import translation_check as C  # noqa: E402

PLAN_NAME = "nondialogue-unit-data-sysmes-2026-10-26.json"
PLAN_SHA = "e2f1e0604c192a450c7da5b7ef050a4abbfced9980a1d383155c210eb339934d"
PREVIOUS_DATA_SHA = "788ab91c72822b149e6d893b4c3b404d1dbebc50743dae0cc8380b46202fcf62"
DATA_SHA = "321d22bd9297569ed9e5caca1dcd64319c12f863b3a8c1b488d5147559711fd8"
ENTRIES = 357
UNIT_FILE = "08_names_units_weapons.jsonl"
CONFIG_FILE = "04_config_text.jsonl"


def line_width(text):
    return max(pl_text.display_width(line) for line in text.split("\n"))


class NonDialogueAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan_path = ROOT / "config/pl" / PLAN_NAME
        cls.plan = json.loads(cls.plan_path.read_text(encoding="utf-8"))
        cls.snapshot = json.loads((ROOT / "pakiet_PL/snapshot.json").read_text(encoding="utf-8"))
        cls.entries = {
            (e["file"], e["source_sha256"]): e
            for e in map(json.loads, (ROOT / "pakiet_PL/polish.jsonl").read_text(encoding="utf-8").splitlines())
        }
        cls.rows, _ = R.I.load_rows(ROOT / "pakiet_EN")
        cls.by_key = {(r["_file"], R.binding(r)): r for r in cls.rows}

    def pl(self, file_name, row):
        return self.entries[(file_name, R.binding(row))]["pl"]

    def test_plan_is_pinned_and_complete(self):
        self.assertEqual(hashlib.sha256(self.plan_path.read_bytes()).hexdigest(), PLAN_SHA)
        self.assertEqual(self.plan["schema"], 1)
        self.assertEqual(len(self.plan["changes"]), ENTRIES)
        files = {edit["file"] for edit in self.plan["changes"]}
        self.assertEqual(files, {UNIT_FILE, CONFIG_FILE})

    def test_snapshot_ledger_chain(self):
        raw = (ROOT / "pakiet_PL/polish.jsonl").read_bytes()
        self.assertEqual(self.snapshot["data_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.snapshot["data_sha256"], DATA_SHA)
        # Ledger-relative: later plan batches append to the same chain.
        entry = next(e for e in reversed(self.snapshot["owner_ui_corrections"]) if e["plan"] == PLAN_NAME)
        self.assertEqual(entry["entries"], ENTRIES)
        self.assertEqual(entry["previous_data_sha256"], PREVIOUS_DATA_SHA)
        self.assertEqual(entry["sha256"], PLAN_SHA)
        self.assertFalse(entry["runtime_tested"])

    def test_every_edit_is_source_bound_and_token_safe(self):
        for edit in self.plan["changes"]:
            key = (edit["file"], edit["source_sha256"])
            source = self.by_key[key]
            self.assertEqual(source["id"], edit["id"])
            self.assertEqual(self.entries[key]["id"], edit["id"])
            self.assertEqual(self.entries[key]["pl"], edit["after"])
            self.assertNotEqual(edit["before"], edit["after"])
            self.assertEqual(C.tokens(edit["before"]), C.tokens(edit["after"]))
            self.assertEqual(edit["before"].count("\n"), edit["after"].count("\n"))
            self.assertNotIn("\x0f", edit["after"])
            pl_text.encode(edit["after"])
            errors, _ = C.check_row({**source, "pl": edit["after"]}, field="pl")
            self.assertFalse(errors, edit["id"])

    def test_width_rule(self):
        """No row grows beyond what already shipped, and small fields keep JP+4."""
        for edit in self.plan["changes"]:
            source = self.by_key[(edit["file"], edit["source_sha256"])]
            limit = max(line_width(edit["before"]), line_width(source["jp"]) + 4)
            self.assertLessEqual(line_width(edit["after"]), edit["max_cells"])
            self.assertEqual(edit["max_cells"], limit)

    def test_unit_data_panel_is_fully_polish(self):
        weight = [r for r in self.rows if r["_file"] == UNIT_FILE and r.get("part") == "weight"]
        length = [r for r in self.rows if r["_file"] == UNIT_FILE and r.get("part") == "length"]
        self.assertEqual(len(weight), 303)
        self.assertEqual(len(length), 304)
        for row in weight + length:
            text = self.pl(UNIT_FILE, row)
            self.assertTrue(text, row["id"])
            self.assertFalse(
                text.startswith(("Weight", "Len.", "Empty Wt.", "Dry Weight")), row["id"]
            )
            prefix = "Masa" if row["part"] == "weight" else "Dł."
            self.assertTrue(text.startswith(prefix), f"{row['id']}: {text!r}")
            self.assertNotIn("  ", text)
        # Spot checks of the conventions: Polish decimal comma, unit after a
        # space, English leftovers inside the value gone.
        self.assertEqual(
            self.pl(UNIT_FILE, next(r for r in self.rows if r["id"] == "robonote:1:weight")),
            "Masa 54,0 t",
        )
        self.assertEqual(
            self.pl(UNIT_FILE, next(r for r in self.rows if r["id"] == "robonote:65535:weight")),
            "Masa －－－",
        )
        self.assertEqual(
            self.pl(UNIT_FILE, next(r for r in self.rows if r["id"] == "robonote:401:length")),
            "Dł. 485 shin",
        )
        self.assertEqual(
            self.pl(UNIT_FILE, next(r for r in self.rows if r["id"] == "robonote:2500:length")),
            "Dł. 6,9 mett",
        )

    def test_unit_data_copies_stay_identical(self):
        """A rewritten robonote row keeps its copy group byte-identical."""
        base = {}
        for row in self.rows:
            if row["_file"] == UNIT_FILE and row.get("part") in ("weight", "length", "type", "note"):
                base[row["id"]] = self.pl(UNIT_FILE, row)
        checked = 0
        for row in self.rows:
            if row["_file"] != UNIT_FILE:
                continue
            copied_from = row.get("copy_of")
            if not copied_from or copied_from not in base:
                continue
            checked += 1
            self.assertEqual(self.pl(UNIT_FILE, row), base[copied_from], row["id"])
        self.assertGreater(checked, 400)

    def test_system_messages_are_polish(self):
        def text(offset):
            row = next(r for r in self.rows if r["id"] == f"sysmes:configst.cpk/sysmes.bin:{offset}")
            return row, self.pl(CONFIG_FILE, row)

        row, pl = text(39944)
        self.assertNotIn("Save failed", pl)
        self.assertEqual(
            pl,
            'Zapis nie powiódł się.\nPo "Starcie gry" z ekranu tytułowego\n'
            "gra ruszy od poprzedniego zapisu.\nCzy na pewno?",
        )
        self.assertEqual(pl.count("\n"), row["jp"].count("\n"))
        # The overlapping fragments carry the same wording as the full row.
        for offset, expected_lines in ((39967, 3), (40006, 2)):
            frag_row, frag = text(offset)
            self.assertEqual(frag.count("\n"), expected_lines - 1)
            self.assertIn(frag.split("\n")[-1], {"Czy na pewno?", "Kontynuować bez zapisu?"})
            self.assertTrue(frag.startswith(("Po ", "Gra ")), frag)
        for offset in (40068, 44704):
            frag_row, frag = text(offset)
            self.assertEqual(frag, "Zapis nie powiódł się.\nKontynuować bez zapisu?")
            self.assertEqual(frag.count("\n"), frag_row["jp"].count("\n"))
        # 製品版をダウンロードします。 no longer shows the game title.
        for offset in (43897, 44013):
            _, frag = text(offset)
            self.assertEqual(frag, "Pobierz pełną wersję gry.")
        for offset in (43894, 44010):
            _, frag = text(offset)
            self.assertEqual(frag, "-\nPobierz pełną wersję gry.")

    def test_no_english_label_survives_in_the_audited_scope(self):
        """Every audited row is Polish; the English column is not copied verbatim."""
        for edit in self.plan["changes"]:
            source = self.by_key[(edit["file"], edit["source_sha256"])]
            if source.get("category") == "config_sysmes":
                continue  # covered by the explicit assertions above
            self.assertNotEqual(edit["after"].strip(), (source.get("en") or "").strip(), edit["id"])


class ExecutablePolicyTests(unittest.TestCase):
    """Part 2 of the audit: the executable strings are fully governed.

    The five candidates found in ``09_executable`` (the English autosave
    warning, the English connection-error and age-restriction dialogs, and the
    diacritic-less ``Ukonczone do Ep. %d`` / ``Lacznie tur %d``) are not
    defects: ``tools/exe_strings.py`` keeps the three ``sceUtilityMsgDialog``
    rows in ASCII because the PSP system font has no patched Polish glyphs, and
    the UTF-8 save-metadata strings must stay ASCII because there is no
    verified Polish codec path for them.  These tests pin that boundary so a
    later pass does not "fix" the ASCII on purpose-built slots.
    """

    EXE_FILE = "09_executable.jsonl"

    @classmethod
    def setUpClass(cls):
        cls.rows, _ = R.I.load_rows(ROOT / "pakiet_EN")
        cls.entries = {
            (e["file"], e["source_sha256"]): e
            for e in map(json.loads, (ROOT / "pakiet_PL/polish.jsonl").read_text(encoding="utf-8").splitlines())
        }

    def exe_rows(self):
        for row in self.rows:
            if row["_file"] != self.EXE_FILE:
                continue
            entry = self.entries.get((self.EXE_FILE, R.binding(row)))
            yield row, entry["pl"] if entry else None

    def test_every_polish_executable_row_passes_its_own_writer_rules(self):
        import exe_strings as E

        checked = 0
        for row, text in self.exe_rows():
            if not text:
                continue
            checked += 1
            patch, why = E.check_en({**row, "en": text}, target_lang="pl")
            self.assertIsNotNone(patch, f"{row['id']}: {why}")
            self.assertGreaterEqual(len(patch), 1, row["id"])
        self.assertEqual(checked, 399)

    def test_system_dialog_and_utf8_save_rows_stay_ascii(self):
        import exe_strings as E

        ascii_rows = {}
        for row, text in self.exe_rows():
            if not text:
                continue
            source = row.get("source") or {}
            vaddr = str(source.get("vaddr", "")).lower()
            utf8 = (source.get("encoding") or "").lower() == "utf-8"
            if vaddr in E.SYSTEM_FONT_VADDRS or utf8:
                ascii_rows[vaddr or row["id"]] = text
                self.assertFalse(pl_text.is_pl(text), row["id"])
        self.assertEqual(len(ascii_rows), 6)
        self.assertEqual(ascii_rows["0x08bf3988"], "Ukonczone do Ep. %d")
        self.assertIn("Lacznie tur %d", ascii_rows["0x08bf39a4"])
        self.assertTrue(ascii_rows["0x08bf3678"].startswith("This game supports autosave."))

    def test_the_only_english_sentences_left_are_the_system_dialogs(self):
        import exe_strings as E

        english = {}
        for row, text in self.exe_rows():
            if not text:
                continue
            source = row.get("source") or {}
            if text != (row.get("en") or ""):
                continue
            # A sentence, not a title/proper noun: several words and a full stop.
            if " " in text.strip() and text.rstrip().endswith((".", "!", "?")) and not pl_text.is_pl(text):
                english[str(source.get("vaddr", "")).lower()] = text
        self.assertEqual(sorted(english), sorted(E.SYSTEM_FONT_VADDRS))
        self.assertTrue(any(t.startswith("This content is age-restricted") for t in english.values()))
        self.assertTrue(any(t.startswith("Connection error occurred.") for t in english.values()))


if __name__ == "__main__":
    unittest.main()
