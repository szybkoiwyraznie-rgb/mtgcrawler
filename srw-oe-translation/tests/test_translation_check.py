"""Synthetic tests for tools/translation_check.py (no game data)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import export_strings  # noqa: E402
import translation_check as TC  # noqa: E402


def row(jp, en, **extra):
    base = {"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "category": "dialogue", "part": "dialogue",
            "jp": jp, "en": en}
    base.update(extra)
    return base


class TokensTest(unittest.TestCase):
    def test_tokens_are_collected_in_order(self):
        self.assertEqual(TC.tokens("＠4<対地%s1>＠0 %s40%%"), ["＠4", "%s", "＠0", "%s", "%%"])

    def test_full_width_percent_and_hash_are_tokens(self):
        self.assertEqual(TC.tokens("＃？？？　％s％d ＄1"), ["＃", "％s", "％d", "＄1"])

    def test_plain_text_has_no_tokens(self):
        self.assertEqual(TC.tokens("それは、パイロットの腕次第ってところかな。"), [])

    def test_the_literal_percent_may_move_with_its_number(self):
        # ``%%`` consumes no argument: ``与える最低%sを%sの14%%にする`` -> ``Minimum %s dealt: 14%% of %s``
        # keeps both %s in order and the one literal percent (9 skill rows of the real views)
        errors, _ = TC.check_row(row("与える最低%sを%sの14%%にする", "Minimum %s dealt: 14%% of %s"))
        self.assertEqual(errors, [])

    def test_a_dropped_or_reordered_argument_is_still_an_error(self):
        errors, _ = TC.check_row(row("%sの14%%", "14 of %s"))
        self.assertTrue(any("control tokens changed" in message for message in errors))
        errors, _ = TC.check_row(row("＠4<%s>＠0 %s", "＠0<%s>＠4 %s"))
        self.assertTrue(any("control tokens changed" in message for message in errors))


class KanaSidecarTests(unittest.TestCase):
    """tokeny.tsv (tools/token_map.py): which %s of a display-form jp is a kana token 0x0F."""

    def test_a_dropped_kana_token_is_correct_with_the_map(self):
        errors, _ = TC.check_row(row("AB%s&CD", "WXYZ"), pct=("AB%s&CD", ["T"]))
        self.assertEqual(errors, [])

    def test_a_kept_kana_token_is_an_error_even_with_the_map(self):
        errors, _ = TC.check_row(row("AB%s&CD", "XY%s&ZW"), pct=("AB%s&CD", ["T"]))
        self.assertTrue(any("kana" in message for message in errors))

    def test_without_the_map_the_strict_rule_still_applies(self):
        errors, _ = TC.check_row(row("AB%s&CD", "WXYZ"))
        self.assertTrue(any("control tokens changed" in message for message in errors))

    def test_literal_placeholders_stay_mandatory_with_the_map(self):
        kinds = ("%s20%s\n%s", ["L", "L", "L"])
        errors, _ = TC.check_row(row("%s20%s\n%s", "x20y\nz"), pct=kinds)
        self.assertTrue(any("control tokens changed" in message for message in errors))
        errors, _ = TC.check_row(row("%s20%s\n%s", "A%sB%s\nC%s"), pct=kinds)
        self.assertEqual(errors, [])

    def test_other_tokens_keep_their_order_around_the_dropped_kana(self):
        self.assertEqual(TC.expected_tokens("＠0%s%s&", ("＠0%s%s&", ["L", "T"])),
                         ["＠0", "%s"])
        errors, _ = TC.check_row(row("＠0%s%s&", "＠0%s"), pct=("＠0%s%s&", ["L", "T"]))
        self.assertEqual(errors, [])
        errors, _ = TC.check_row(row("＠0%s%s&", "%s＠0"), pct=("＠0%s%s&", ["L", "T"]))
        self.assertTrue(errors)

    def test_strip_kana_tokens_removes_the_copied_pairs_only(self):
        jp = "防御時､%s*ﾒｰ%s&-"
        pct = (jp, ["T", "T"])
        self.assertEqual(TC.kana_signatures(jp, pct), ["%s*", "%s&"])
        self.assertEqual(TC.strip_kana_tokens("On defense, %s*%s&damage-", jp, pct),
                         "On defense, damage-")
        # already clean: untouched
        self.assertEqual(TC.strip_kana_tokens("On defense, damage-", jp, pct),
                         "On defense, damage-")
        # a bare %s is never removed - it could be a literal the English must keep
        self.assertEqual(TC.strip_kana_tokens("On defense, %s damage-", jp, pct),
                         "On defense, %s damage-")
        # literal placeholders stay, the kana pair around them goes
        mixed = "%s4ﾀﾞ%s*"
        self.assertEqual(TC.strip_kana_tokens("%s4 Da%s*", mixed, (mixed, ["L", "T"])), "%s4 Da")
        # each pair is removed once, in the order of the jp
        self.assertEqual(TC.strip_kana_tokens("%s*%s*x", "%s*ﾀ%s*", ("%s*ﾀ%s*", ["T", "T"])), "x")
        # no sidecar entry or a stale one: nothing happens (the checker then refuses)
        self.assertEqual(TC.strip_kana_tokens("a%s*b", jp, None), "a%s*b")
        self.assertEqual(TC.strip_kana_tokens("a%s*b", jp, ("inne", ["T", "T"])), "a%s*b")
        self.assertEqual(TC.strip_kana_tokens("a%s*b", jp, (jp, ["T"])), "a%s*b")
        # the stripped text passes the checker, the copied one does not
        errors, _ = TC.check_row(row(jp, TC.strip_kana_tokens("On defense, %s*%s&damage-", jp, pct)),
                                 pct=pct)
        self.assertEqual(errors, [])
        errors, _ = TC.check_row(row(jp, "On defense, %s*%s&damage-"), pct=pct)
        self.assertTrue(errors)

    def test_a_stale_map_entry_falls_back_to_the_strict_rule(self):
        errors, _ = TC.check_row(row("AB%s&CD", "WXYZ"), pct=("inne jp", ["T"]))
        self.assertTrue(any("control tokens changed" in message for message in errors))
        errors, _ = TC.check_row(row("AB%s&CD", "WXYZ"), pct=("AB%s&CD", []))
        self.assertTrue(any("control tokens changed" in message for message in errors))

    def test_check_rows_consults_the_map_by_row_id(self):
        rows = [row("AB%s&CD", "WXYZ", id="kana:1"), row("CD%sEF", "WXYZ", id="kana:2")]
        report = TC.check_rows(rows, token_map={"kana:1": ("AB%s&CD", ["T"])})
        self.assertEqual(report["totals"]["errors"], 1)     # only the unmapped row fails
        self.assertIn("kana:2", report["errors"][0])


class RowTest(unittest.TestCase):
    def test_clean_row_has_no_problems(self):
        errors, warnings = TC.check_row(row("おはよう\nございます", "Good morning\nsir"))
        self.assertEqual((errors, warnings), ([], []))

    def test_empty_translation_is_a_warning_by_default(self):
        errors, warnings = TC.check_row(row("おはよう", ""))
        self.assertEqual(errors, [])
        self.assertIn("untranslated", warnings[0])

    def test_empty_translation_is_an_error_in_release_mode(self):
        errors, _ = TC.check_row(row("おはよう", "  "), require_complete=True)
        self.assertIn("untranslated", errors[0])

    def test_missing_token_is_an_error(self):
        errors, _ = TC.check_row(row("＠4<対地%s1>＠0", "Anti-ground %s1"))
        self.assertEqual(len(errors), 1)
        self.assertIn("control tokens changed", errors[0])

    def test_reordered_token_is_an_error(self):
        errors, _ = TC.check_row(row("＠4a＠0b", "＠0a＠4b"))
        self.assertIn("control tokens changed", errors[0])

    def test_line_break_count_must_match(self):
        errors, _ = TC.check_row(row("あ\nい", "one line"))
        self.assertIn("line breaks changed", errors[0])

    def test_trailing_break_of_the_japanese_is_kept(self):
        # a third of the dialogue lines end with a real break; stripping the translation would
        # report a mismatch on correct work
        errors, warnings = TC.check_row(row("ＥＮ補充、完了！\r\n", "EN supply, complete!\r\n"))
        self.assertEqual((errors, warnings), ([], []))

    def test_a_translation_without_the_trailing_break_is_an_error(self):
        errors, _ = TC.check_row(row("ＥＮ補充、完了！\n", "EN supply, complete!"))
        self.assertIn("line breaks changed", errors[0])

    def test_dropped_carriage_return_is_an_error(self):
        errors, _ = TC.check_row(row("あ\r\nい", "a\nb"))
        self.assertIn("control characters changed", errors[0])

    def test_dropping_the_voiced_kana_token_in_english_is_correct(self):
        # JP `0x0F xx` (xx in 0x20-0x39) is ONE voiced half-width kana glyph; English writes
        # the name plain, so the token (and the byte it consumed) disappears from the EN text
        errors, warnings = TC.check_row(row("\x0f3ﾗ", "Ra"))
        self.assertEqual(errors, [])

    def test_keeping_the_voiced_kana_token_in_english_is_an_error(self):
        errors, _ = TC.check_row(row("\x0f3ﾗ", "\x0f3Ra"))
        self.assertIn("<0x0F>", errors[0])

    def test_english_keeps_the_carriage_return_but_drops_the_token(self):
        errors, warnings = TC.check_row(row("あ\x0f3ﾗ\r\n", "aRa\r\n"))
        self.assertEqual((errors, warnings), ([], []))

    def test_plain_line_breaks_are_not_reported_as_control_characters(self):
        errors, _ = TC.check_row(row("あ\nい", "a\nb"))
        self.assertEqual(errors, [])

    def test_non_cp932_is_an_error(self):
        errors, _ = TC.check_row(row("あ", "Zażółć"))
        self.assertIn("not CP932-encodable", errors[0])

    def test_fixed_slot_budget_is_a_hard_error(self):
        errors, _ = TC.check_row(row("あ", "12", max_bytes=1))
        self.assertIn("over budget", errors[0])

    def test_ui_hint_is_only_a_warning(self):
        errors, warnings = TC.check_row(row("あ", "12", suggested_max=1))
        self.assertEqual(errors, [])
        self.assertIn("suggested_max", warnings[0])


class FixedSlotLimitTest(unittest.TestCase):
    def slot_row(self, en, max_bytes, member="srwDL_Map_S.bin", offset=16):
        return {"id": "map_name:config00.cpk/srwDL_Map_S.bin:r0:name", "category": "map_name",
                "part": "name", "jp": "宇宙マップ", "en": en, "mode": "slot", "max_bytes": max_bytes,
                "source": {"container": "config00.cpk", "member": member, "offset": offset}}

    def test_the_measured_field_beats_a_stale_record_wide_max_bytes(self):
        errors, _ = TC.check_row(self.slot_row("x" * 40, 159))
        self.assertTrue(any("measured 32-byte slot" in e for e in errors), errors)
        errors, _ = TC.check_row(self.slot_row("x" * 31, 159))
        self.assertEqual(errors, [])

    def test_a_tighter_package_budget_still_applies(self):
        errors, _ = TC.check_row(self.slot_row("x" * 20, 10))
        self.assertTrue(any("max_bytes 10" in e for e in errors), errors)

    def test_an_ext_dat_title_row_is_capped_at_the_measured_40_byte_slot(self):
        # the one-record file is not in the row; the measured 388-byte record is assumed
        ext = self.slot_row("x" * 42, 43, member="DL311_12_ext.dat", offset=344)
        self.assertEqual(TC.fixed_slot_limit(ext), 39)
        errors, _ = TC.check_row(ext)
        self.assertTrue(any("measured 40-byte slot" in e for e in errors), errors)
        self.assertEqual(TC.fixed_slot_limit(self.slot_row("x", 159, member="DL311_12_ext.dat",
                                                           offset=24)), 159)
        errors, _ = TC.check_row(self.slot_row("x" * 39, 43, member="DL311_12_ext.dat", offset=344))
        self.assertEqual(errors, [])

    def test_other_members_are_untouched(self):
        self.assertIsNone(TC.fixed_slot_limit(self.slot_row("x", 159, member="srwDL_Item00.bin")))
        self.assertIsNone(TC.fixed_slot_limit(self.slot_row("x", 159, offset=20)))
        self.assertEqual(TC.fixed_slot_limit(self.slot_row("x", 159)), 31)


class WhitespaceTest(unittest.TestCase):
    def test_edge_whitespace_absent_from_the_jp_is_a_warning_not_an_error(self):
        errors, warnings = TC.check_row(row("加速", " Accel "))
        self.assertEqual(errors, [])
        self.assertEqual(len([w for w in warnings if "whitespace" in w]), 2)

    def test_edge_whitespace_the_jp_also_has_is_silent(self):
        errors, warnings = TC.check_row(row("　　 サブミッション　　", "　　 Sub mission　　"))
        self.assertEqual(errors, [])
        self.assertFalse([w for w in warnings if "whitespace" in w])
        errors, warnings = TC.check_row(row("説明。\n", "Text.\n"))
        self.assertEqual(errors, [])
        self.assertFalse([w for w in warnings if "whitespace" in w])


class BoxWidthTest(unittest.TestCase):
    LIMIT = export_strings.box_limit("dialogue")   # 52: the widest line the game itself draws

    def test_a_long_dialogue_line_is_a_warning(self):
        _, warnings = TC.check_row(row("あ", "x" * (self.LIMIT + 1)))
        self.assertIn("the in-game box fits 52 (dialogue)", warnings[0])

    def test_a_line_that_fits_is_clean(self):
        errors, warnings = TC.check_row(row("あ", "x" * self.LIMIT))
        self.assertEqual((errors, warnings), ([], []))

    def test_a_battle_quote_has_the_quote_limit(self):
        quote = row("あ", "x" * 51)
        quote["category"] = "battle_quote"
        _, warnings = TC.check_row(quote)
        self.assertIn("the in-game box fits 50 (battle_quote)", warnings[0])

    def test_a_box_clear_does_not_count(self):
        errors, warnings = TC.check_row(row("あ\r", "x" * self.LIMIT + "\r"))
        self.assertEqual((errors, warnings), ([], []))

    def test_full_width_characters_count_double(self):
        _, warnings = TC.check_row(row("あ", "あ" * (self.LIMIT // 2 + 1)))
        self.assertTrue(any("the in-game box fits" in message for message in warnings))

    def test_non_boxed_categories_are_not_measured(self):
        wide = row("あ", "x" * (TC.BOX_WIDTH + 5))
        wide["category"] = "config_help"
        _, warnings = TC.check_row(wide)
        self.assertEqual(warnings, [])

    def test_box_width_matches_the_writer(self):
        import event_text_apply
        self.assertEqual(TC.BOX_WIDTH, event_text_apply.BOX_WIDTH)
        self.assertEqual(TC.BOX_WIDTH, export_strings.TYPICAL_LINE)


class CopyTest(unittest.TestCase):
    def test_filled_copy_must_equal_its_source(self):
        rows = [row("あ", "one"), row("い", "one", copy_of="dlg:eventP00.cpk/DL100_01.bin:1844")]
        rows[1]["id"] = "dlg:eventP00.cpk/DL100_01.bin:2000"
        report = TC.check_rows(rows)
        self.assertEqual(report["totals"]["errors"], 0)

    def test_copy_that_differs_from_its_source_is_an_error(self):
        rows = [row("あ", "one"), row("い", "uno", copy_of="dlg:eventP00.cpk/DL100_01.bin:1844")]
        rows[1]["id"] = "dlg:eventP00.cpk/DL100_01.bin:2000"
        report = TC.check_rows(rows)
        self.assertIn("copy differs from its source row", report["errors"][0])

    def test_empty_copy_with_a_translated_source_is_a_pointer_to_copy_the_row(self):
        rows = [row("あ", "one"), row("い", "", copy_of="dlg:eventP00.cpk/DL100_01.bin:1844")]
        rows[1]["id"] = "dlg:eventP00.cpk/DL100_01.bin:2000"
        report = TC.check_rows(rows)
        self.assertEqual(report["totals"]["errors"], 0)
        self.assertTrue(any("translation_copy.py" in warning for warning in report["warnings"]))

    def test_structural_rows_are_counted_apart(self):
        report = TC.check_rows([{"id": "a/b.bin", "seq": 1, "rows": 3},
                                dict(row("あ", "a"), _file="00_dialogue.jsonl")])
        self.assertEqual(report["structural_rows"], 1)
        self.assertEqual(report["totals"]["rows"], 1)


class ReportTest(unittest.TestCase):
    def test_totals_and_first_problems(self):
        rows = [row("あ", "a"), row("い", ""), row("う", "１２３", max_bytes=1)]
        report = TC.check_rows(rows)
        self.assertEqual(report["totals"], {"rows": 3, "filled": 2, "empty": 1,
                                            "errors": 1, "warnings": 1})
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(len(report["warnings"]), 1)

    def test_text_report_mentions_every_file(self):
        report = TC.check_rows([dict(row("あ", "a"), _file="00_dialogue.jsonl"),
                                dict(row("い", "b"), _file="03_skills.jsonl")])
        text = TC.format_report(report)
        self.assertIn("00_dialogue.jsonl", text)
        self.assertIn("03_skills.jsonl", text)
        self.assertIn("RAZEM: 2 wierszy", text)


if __name__ == "__main__":
    unittest.main()


class ListColumnTest(unittest.TestCase):
    """The unit-list columns measured on the 2026-10-15 screenshot (14 half-width cells)."""

    def test_a_unit_name_wider_than_the_column_is_an_error(self):
        errors, _ = TC.check_row(row("ストライクフリーダムガンダム", "Strike Freedom Gundam",
                                     id="unit:3010:name", category="unit_name"))
        self.assertEqual(len(errors), 1)
        self.assertIn("21 half-width cells, the column fits 14", errors[0])

    def test_fourteen_cells_fit_and_full_width_counts_double(self):
        errors, warnings = TC.check_row(row("ストライクフリーダムガンダム", "Strike Freedom",
                                            id="unit:3010:name", category="unit_name"))
        self.assertEqual((errors, warnings), ([], []))
        errors, _ = TC.check_row(row("∞ジャスティスガンダム", "∞ Justice",      # 2 + 8 = 10
                                     id="unit:3011:name", category="unit_name"))
        self.assertEqual(errors, [])
        errors, _ = TC.check_row(row("∞ジャスティスガンダム", "∞ Justice Gnd",   # 2 + 12 = 14
                                     id="unit:3011:name", category="unit_name"))
        self.assertEqual(errors, [])
        errors, _ = TC.check_row(row("∞ジャスティスガンダム", "∞ Justice Gnda",  # 15
                                     id="unit:3011:name", category="unit_name"))
        self.assertEqual(len(errors), 1)

    def test_the_long_display_name_is_not_a_list_column(self):
        errors, warnings = TC.check_row(row("ストライクフリーダムガンダム", "Strike Freedom Gundam",
                                            id="unit:3010:name_display", category="unit_name_display"))
        self.assertEqual((errors, warnings), ([], []))

    def test_a_wide_pilot_short_name_is_only_a_warning(self):
        errors, warnings = TC.check_row(row("ミスター・ブシドー／味方", "Mr. Bushido (Ally)",
                                            id="char:2401:name_short", category="character_name_short"))
        self.assertEqual(errors, [])
        self.assertIn("wider than the pilot column", warnings[0])
        errors, warnings = TC.check_row(row("ミスター・ブシドー／味方", "Bushido/Ally",
                                            id="char:2401:name_short", category="character_name_short"))
        self.assertEqual((errors, warnings), ([], []))


class CompletionByteTest(unittest.TestCase):
    """``%s4`` of the Coord. Atk / group-sortie records: the ``4`` completes the kana fragment."""

    R239 = "skill:config00.cpk/srwDL_Skill00.bin:r239:effect"
    R240 = "skill:config00.cpk/srwDL_Skill00.bin:r240:effect"
    R236 = "skill:config00.cpk/srwDL_Skill00.bin:r236:effect"
    JP239 = "＠4<連携攻撃%s3>＠0%s15%% %s4全機が攻撃\n攻撃力表示は\x0f\"ﾙｰ\x0f4全機の合計値\n%s"
    JP240 = "＠4<連携攻撃%s4>＠0%s20%% %s4全機が攻撃\n攻撃力表示は\x0f\"ﾙｰ\x0f4全機の合計値\n%s"
    JP236 = "包囲率が上昇し攻撃回数が%s4全機分になる\n%s4全機の合計値\n%s"

    def test_the_build_17_text_is_refused(self):
        errors, _ = TC.check_row(row(self.JP239, "＠4<Coord. Atk%s3>＠0%s15%% %s4All units attack\n"
                                     "Shown Atk = group total\n%s", id=self.R239, category="skill"))
        self.assertTrue([e for e in errors if "Group4" in e], errors)

    def test_the_corrected_text_passes(self):
        errors, _ = TC.check_row(row(self.JP239, "＠4<Coord. Atk%s3>＠0%s15%% all %s units attack\n"
                                     "Shown Atk = group total\n%s", id=self.R239, category="skill"))
        self.assertEqual(errors, [])

    def test_the_level_number_of_r240_is_not_the_completion_byte(self):
        errors, _ = TC.check_row(row(self.JP240, "＠4<Coord. Atk%s4>＠0%s20%% all %s units attack\n"
                                     "Shown Atk = group total\n%s", id=self.R240, category="skill"))
        self.assertEqual(errors, [])
        errors, _ = TC.check_row(row(self.JP240, "＠4<Coord. Atk%s4>＠0%s20%% %s4All units attack\n"
                                     "Shown Atk = group total\n%s", id=self.R240, category="skill"))
        self.assertTrue([e for e in errors if "Group4" in e], errors)

    def test_r236_drops_both(self):
        errors, _ = TC.check_row(row(self.JP236, "Surround Up; attacks = all %s units\n"
                                     "Shown Atk = %s4 total\n%s", id=self.R236, category="skill"))
        self.assertTrue([e for e in errors if "Group4" in e], errors)
        errors, _ = TC.check_row(row(self.JP236, "Surround Up; attacks = all %s units\n"
                                     "Shown Atk = %s total\n%s", id=self.R236, category="skill"))
        self.assertEqual(errors, [])

    def test_other_records_keep_their_numbers(self):
        errors, _ = TC.check_row(row("%s4ﾀｰﾝ継続", "%s4 turns", id="skill:config00.cpk/srwDL_Skill00.bin:r9:effect",
                                     category="skill"))
        self.assertEqual(errors, [])


class ConflictingDuplicateTest(unittest.TestCase):
    """The 04 scan of Skill00 repeats the 03 record rows: both must say the same English."""

    def rows(self, en04):
        src = {"container": "config00.cpk", "member": "srwDL_Skill00.bin", "offset": 38868}
        return [row("包囲率が上昇し%s4全機分になる", "Surround Up; all %s units", id="skill:config00.cpk/srwDL_Skill00.bin:r236:effect",
                    category="skill", source=src),
                row("包囲率が上昇し%s4全機分になる", en04, id="skill:config00.cpk/srwDL_Skill00.bin:38940",
                    category="config_skill", source=dict(src, offset=38940))]

    def test_two_translations_of_one_record_string_are_errors_on_both_rows(self):
        report = TC.check_rows(self.rows("Surround Up; all %s4 units"))
        conflicts = [e for e in report["errors"] if "different translations of the same" in e]
        self.assertEqual(len(conflicts), 2)
        self.assertEqual(report["totals"]["errors"], 2)

    def test_identical_translations_are_fine(self):
        report = TC.check_rows(self.rows("Surround Up; all %s units"))
        self.assertFalse([e for e in report["errors"] if "different translations" in e])

    def test_an_empty_duplicate_is_not_a_conflict(self):
        report = TC.check_rows(self.rows(""))
        self.assertFalse([e for e in report["errors"] if "different translations" in e])

    def test_dialogue_may_translate_one_japanese_line_two_ways(self):
        src = {"container": "eventP00.cpk", "member": "DL100_01.bin", "offset": 1}
        rows = [row("はい", "Yes", id="a", source=src), row("はい", "Right", id="b", source=dict(src, offset=2))]
        self.assertFalse([e for e in TC.check_rows(rows)["errors"] if "different translations" in e])
