#!/usr/bin/env python3
"""Tests for tools/gim_label.py (caption rendering into INDEX8 textures) and the end-to-end
container build in tools/ui_texture_patch.py, all on synthetic fixtures."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gim_image  # noqa: E402
import gim_label  # noqa: E402
import speaker_map  # noqa: E402
import text_codec  # noqa: E402
import ui_texture_patch  # noqa: E402
from gim_fixtures import build_ui_pac, label_texture, label_texture_rgba  # noqa: E402
from test_cpk_itoc_write import build_itoc_only_cpk  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402

try:
    import PIL  # noqa: F401
    HAVE_PIL = True
except ImportError:  # pragma: no cover
    HAVE_PIL = False

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / gim_label.DEFAULT_FONT


def spec(**overrides):
    base = {"texture": "mensys_03", "size": 10, "min_size": 7,
            "labels": [{"id": "atk", "jp": "攻撃", "en": "ATK", "box": [2, 3, 22, 17]}]}
    base.update(overrides)
    return base


def pixel(rgba, w, x, y):
    p = (y * w + x) * 4
    return tuple(rgba[p:p + 4])


@unittest.skipUnless(HAVE_PIL, "Pillow not installed")
class RenderLabelsTests(unittest.TestCase):
    def test_font_is_shipped_with_the_repo(self):
        self.assertTrue(FONT.is_file(), FONT)
        self.assertTrue((FONT.parent / "LICENSE-Roboto.txt").is_file())

    def test_caption_replaces_the_glyph_box_and_leaves_the_rest_alone(self):
        raw = label_texture()
        new, report, rgba = gim_label.render_labels(raw, spec())
        self.assertEqual(len(new), len(raw))
        self.assertFalse(report.errors)
        res = report.labels[0]
        self.assertIsNotNone(res.size)
        self.assertLessEqual(res.text_width, 20)
        decoded, w, h = gim_image.decode(gim_image.parse(new))
        self.assertEqual(len(rgba), len(decoded))   # rgba = canvas before palette quantisation
        # something opaque was drawn inside the box …
        inside = [pixel(decoded, w, x, y) for y in range(3, 17) for x in range(2, 22)]
        self.assertTrue(any(c[3] > 0 for c in inside))
        # … the original outline corner is gone (cleared to the transparent colour) …
        self.assertEqual(pixel(decoded, w, 4, 4)[3], 0)
        # … and the sentinel outside the box survived.
        self.assertEqual(pixel(decoded, w, 40, 20), (255, 0, 0, 255))
        original, _, _ = gim_image.decode(gim_image.parse(raw))
        for y in range(h):
            for x in range(w):
                if not (2 <= x < 22 and 3 <= y < 17):
                    self.assertEqual(pixel(decoded, w, x, y), pixel(original, w, x, y), (x, y))

    def test_colours_default_to_the_original_glyph_colours(self):
        fill, outline, transparent = gim_label.glyph_colours(
            gim_image.decode(gim_image.parse(label_texture()))[0], 64, (2, 3, 22, 17))
        self.assertEqual(fill, (230, 230, 230, 255))
        self.assertEqual(outline, (0, 0, 0, 187))
        self.assertEqual(transparent, (255, 255, 255, 0))

    def test_null_en_keeps_the_japanese_pixels(self):
        raw = label_texture()
        s = spec()
        s["labels"][0]["en"] = None
        new, report, _ = gim_label.render_labels(raw, s)
        self.assertEqual(new, raw)
        self.assertTrue(report.labels[0].skipped)

    def test_polish_caption_override_does_not_change_english(self):
        raw = label_texture()
        s = spec()
        s["labels"][0]["pl"] = "SK"
        previous = text_codec.lang()
        try:
            text_codec.set_lang("en")
            _, english, _ = gim_label.render_labels(raw, s)
            text_codec.set_lang("pl")
            _, polish, _ = gim_label.render_labels(raw, s)
        finally:
            text_codec.set_lang(previous)
        self.assertEqual(english.labels[0].en, "ATK")
        self.assertEqual(polish.labels[0].en, "SK")
        self.assertFalse(english.errors)
        self.assertFalse(polish.errors)

    def test_polish_active_spirit_orb_labels_are_localized_and_fit(self):
        localized = {
            "valor": "ZA", "bullseye": "CE", "accel": "PE", "flash": "PR",
            "focus": "SK", "persist": "NI", "wall": "MU", "gain": "WY",
            "fortune": "FT", "disrupt": "ZM",
        }
        spec_path = ROOT / "ui_labels/mensys_15.json"
        orb_spec = gim_label.load_spec(spec_path)
        orbs = {lab["id"]: lab for lab in orb_spec["labels"] if lab["id"] in localized}
        self.assertEqual(set(orbs), set(localized))
        for label_id, expected in localized.items():
            with self.subTest(orb=label_id):
                lab = orbs[label_id]
                self.assertEqual(lab.get("pl"), expected)
                self.assertEqual(len(expected), 2)
                x0, y0, x1, y1 = lab["box"]
                size, _, _ = gim_label.fit_size(
                    ROOT / orb_spec.get("font", gim_label.DEFAULT_FONT), expected,
                    x1 - x0, y1 - y0, lab.get("size", orb_spec.get("size", 9)),
                    lab.get("min_size", orb_spec.get("min_size", 6)),
                    lab.get("squeeze", orb_spec.get("squeeze", 1.0)))
                self.assertIsNotNone(size)
        self.assertEqual(orbs["focus"]["en"], "FO")

    def test_empty_en_erases_the_box_without_drawing(self):
        raw = label_texture()
        s = spec()
        s["labels"][0]["en"] = ""
        new, report, canvas = gim_label.render_labels(raw, s)
        self.assertTrue(report.labels[0].erased)
        self.assertNotEqual(new, raw)
        gim = gim_image.parse(new)
        rgba, w, h = gim_image.decode(gim)
        orig, _, _ = gim_image.decode(gim_image.parse(raw))
        x0, y0, x1, y1 = s["labels"][0]["box"]
        # every pixel inside the box is now the texture's transparent colour …
        box_pixels = {pixel(rgba, w, x, y) for y in range(y0, y1) for x in range(x0, x1)}
        self.assertEqual(len(box_pixels), 1)
        self.assertEqual(next(iter(box_pixels))[3], 0)
        # … and nothing outside the box changed
        for y in range(h):
            for x in range(w):
                if not (x0 <= x < x1 and y0 <= y < y1):
                    self.assertEqual(pixel(rgba, w, x, y), pixel(orig, w, x, y), (x, y))
        # whitespace-only is still a spec error (neither erase nor caption)
        s["labels"][0]["en"] = "   "
        with self.assertRaises(gim_label.LabelError):
            gim_label.render_labels(raw, s)

    def test_caption_that_does_not_fit_is_refused_not_clipped(self):
        s = spec()
        s["labels"][0]["en"] = "A caption far too long for twenty pixels"
        with self.assertRaises(gim_label.LabelError) as ctx:
            gim_label.render_labels(label_texture(), s)
        self.assertIn("does not fit", str(ctx.exception))

    def test_squeeze_condenses_before_shrinking(self):
        s = spec(size=12, min_size=12, squeeze=0.6)
        s["labels"][0]["en"] = "SIZE"
        _, report, _ = gim_label.render_labels(label_texture(), s)
        r = report.labels[0]
        self.assertEqual(r.size, 12)
        self.assertLess(r.x_scale, 1.0)
        self.assertLessEqual(r.text_width, 20)

    def test_bad_boxes_and_duplicate_ids_are_refused(self):
        s = spec()
        s["labels"][0]["box"] = [60, 4, 70, 16]
        with self.assertRaises(gim_label.LabelError):
            gim_label.render_labels(label_texture(), s)
        s = spec()
        s["labels"].append(dict(s["labels"][0]))
        with self.assertRaises(gim_label.LabelError):
            gim_label.render_labels(label_texture(), s)

    def test_bg_from_column_copies_the_row_colour_into_the_cleared_box(self):
        raw = label_texture()
        s = spec()
        # column 40 holds the red sentinel at row 20: clearing rows 14..26 from that column
        # must paint row 20 red and the other rows transparent (right of the short caption).
        s["labels"][0].update({"box": [44, 14, 60, 26], "clear": [44, 14, 60, 26], "bg_from_column": 40,
                               "en": "A"})
        new, _, _ = gim_label.render_labels(raw, s)
        decoded, w, _ = gim_image.decode(gim_image.parse(new))
        self.assertEqual(pixel(decoded, w, 59, 20), (255, 0, 0, 255))
        self.assertEqual(pixel(decoded, w, 59, 14)[3], 0)
        self.assertEqual(pixel(decoded, w, 59, 25)[3], 0)

    def test_fit_size_reports_none_below_the_minimum(self):
        size, scale, width = gim_label.fit_size(FONT, "WWWWWWWW", 10, 12, 10, 8)
        self.assertIsNone(size)
        self.assertGreater(width, 10)

    def test_repo_specs_are_valid_and_their_fonts_exist(self):
        specs = ui_texture_patch.load_specs(ROOT / "ui_labels")
        self.assertIn("mensys_03", specs)
        for name, s in specs.items():
            self.assertTrue((ROOT / s.get("font", gim_label.DEFAULT_FONT)).is_file(), name)
            ids = [lab["id"] for lab in s["labels"]]
            self.assertEqual(len(ids), len(set(ids)), name)
            for lab in s["labels"]:
                self.assertIn("jp", lab, f"{name}/{lab['id']}")
                self.assertEqual(len(lab["box"]), 4)


@unittest.skipUnless(HAVE_PIL, "Pillow not installed")
class UiTexturePatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.originals = self.root / "orig"
        self.originals.mkdir()
        self.texture = label_texture()
        inner = build_ui_pac([("mensys_03.gim", self.texture), ("INTER.inc", b"x" * 9)], first_word=0x800)
        pac = build_ui_pac([("layout.bin", b"L" * 100), ("tex.pac", inner)])
        self.pac = pac
        import crilayla
        (self.originals / "system.cpk").write_bytes(build_itoc_only_cpk([(0, crilayla.compress(pac), len(pac))]))
        (self.originals / "other.cpk").write_bytes(build_itoc_only_cpk([(0, b"no textures here" * 10, 160)]))
        self.specs = self.root / "specs"
        self.specs.mkdir()
        (self.specs / "mensys_03.json").write_text(json.dumps(spec()), encoding="utf-8")

    def test_walk_finds_nested_gims(self):
        hits = ui_texture_patch.walk_gims(self.pac)
        self.assertEqual([h[0] for h in hits], ["tex.pac/mensys_03.gim"])
        _, off, size = hits[0]
        self.assertEqual(self.pac[off:off + size], self.texture)

    def _build(self, compress):
        out = self.root / f"out_{compress}"
        results = ui_texture_patch.build(self.originals, out, ui_texture_patch.load_specs(self.specs), compress)
        return out, results

    def test_builds_only_the_container_with_a_spec_d_texture(self):
        for compress in ("stored", "crilayla"):
            out, results = self._build(compress)
            self.assertEqual([r.name for r in results], ["system.cpk"])
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["system.cpk"])
            res = results[0]
            self.assertEqual(res.kind, "itoc")
            self.assertEqual(res.textures, ["tex.pac/mensys_03.gim"])
            self.assertEqual(res.labels["tex.pac/mensys_03.gim"][0]["en"], "ATK")
            if compress == "stored":
                self.assertEqual(res.member_stored_as, res.member_size)
            else:
                self.assertLess(res.member_stored_as, res.member_size)
            # read back through the trusted reader: member differs from the original only inside the GIM
            member = dict(speaker_map.read_members(out / "system.cpk"))["ID00000"]
            self.assertEqual(len(member), len(self.pac))
            hits = ui_texture_patch.walk_gims(member)
            _, off, size = hits[0]
            self.assertNotEqual(member[off:off + size], self.texture)
            self.assertEqual(member[:off], self.pac[:off])
            self.assertEqual(member[off + size:], self.pac[off + size:])
            expected, _, _ = gim_label.render_labels(self.texture, spec())
            self.assertEqual(member[off:off + size], expected)

    def test_unfit_caption_refuses_the_whole_build(self):
        bad = spec()
        bad["labels"][0]["en"] = "This will never fit in twenty pixels"
        (self.specs / "mensys_03.json").write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(ui_texture_patch.UiPatchError):
            self._build("stored")
        self.assertFalse((self.root / "out_stored" / "system.cpk").exists())

    def test_cli_writes_a_report(self):
        out = self.root / "cli"
        rc = ui_texture_patch.main(["--originals", str(self.originals), "--out", str(out),
                                    "--specs", str(self.specs), "--compress", "stored"])
        self.assertEqual(rc, 0)
        report = json.loads((out / "ui_texture_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["containers"][0]["name"], "system.cpk")
        self.assertNotIn("blob", json.dumps(report))


@unittest.skipUnless(HAVE_PIL, "Pillow not installed")
class BareGimTocContainerTests(unittest.TestCase):
    """navisys.cpk shape: a TOC container whose members ARE textures (no PAC), true colour,
    with ExtractSize stored once as a schema constant."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.originals = self.root / "orig"
        self.originals.mkdir()
        self.tex1 = label_texture_rgba()
        self.tex2 = label_texture_rgba()
        cpk = build_synthetic_cpk([{"name": "navisys_01.gim", "data": self.tex1, "id": 0},
                                   {"name": "navisys_02.gim", "data": self.tex2, "id": 1}],
                                  enabled_sizes=True, constant_extract=True)
        (self.originals / "navisys.cpk").write_bytes(cpk)
        self.specs = self.root / "specs"
        self.specs.mkdir()
        self.spec2 = spec(texture="navisys_02")
        (self.specs / "navisys_02.json").write_text(json.dumps(self.spec2), encoding="utf-8")

    def _build(self):
        out = self.root / "out"
        results = ui_texture_patch.build(self.originals, out, ui_texture_patch.load_specs(self.specs), "stored")
        return out, results

    def test_walk_treats_a_gim_member_as_one_whole_texture(self):
        self.assertEqual(ui_texture_patch.walk_gims(self.tex2, member_name="navisys_02.gim"),
                         [("navisys_02.gim", 0, len(self.tex2))])
        self.assertEqual(ui_texture_patch.walk_gims(self.tex2), [])          # no name, no PAC index: nothing
        self.assertEqual(ui_texture_patch.walk_gims(b"x" * 64, member_name="a.gim"), [])

    def test_only_the_spec_d_member_is_rewritten(self):
        out, results = self._build()
        self.assertEqual([r.name for r in results], ["navisys.cpk"])
        res = results[0]
        self.assertEqual(res.kind, "toc")
        self.assertEqual(res.textures, ["navisys_02.gim"])
        self.assertEqual([m["name"] for m in res.members], ["navisys_02.gim"])
        self.assertEqual(res.labels["navisys_02.gim"][0]["en"], "ATK")
        back = dict(speaker_map.read_members(out / "navisys.cpk"))
        self.assertEqual(back["navisys_01.gim"], self.tex1)
        expected, _, _ = gim_label.render_labels(self.tex2, self.spec2)
        self.assertEqual(back["navisys_02.gim"], expected)
        self.assertNotEqual(expected, self.tex2)
        self.assertEqual(len(expected), len(self.tex2))      # constant ExtractSize must still hold

    def test_two_spec_d_members_are_rewritten_on_top_of_each_other(self):
        spec1 = spec(texture="navisys_01")
        spec1["labels"][0]["en"] = "DEF"
        (self.specs / "navisys_01.json").write_text(json.dumps(spec1), encoding="utf-8")
        out, results = self._build()
        res = results[0]
        self.assertEqual(res.textures, ["navisys_01.gim", "navisys_02.gim"])
        self.assertEqual([m["index"] for m in res.members], [0, 1])
        back = dict(speaker_map.read_members(out / "navisys.cpk"))
        self.assertEqual(back["navisys_01.gim"], gim_label.render_labels(self.tex1, spec1)[0])
        self.assertEqual(back["navisys_02.gim"], gim_label.render_labels(self.tex2, self.spec2)[0])
        self.assertNotEqual(back["navisys_01.gim"], back["navisys_02.gim"])


if __name__ == "__main__":
    unittest.main()
