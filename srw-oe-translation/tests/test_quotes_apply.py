#!/usr/bin/env python3
"""Synthetic tests for tools/quotes_apply.py (no game data).

The fixture reproduces the battle-quote pac as measured on mesbtl00.cpk/p0050.pac:

    pac header  u32 (edat offset - 16), u16 message ids, zero padding, 16 zero bytes
    "EDAT"      u32 size (= sum of the EVNT section sizes)  u32 section_count
    section x   "EVNT" u32 size (= 4 + payload)  payload
    payload     u32 0 (the zero word that marks the mesbtl variant)  C8 wrapper
    wrapper     C8 u32 size  C9 records
    C9 record   u32 0xC9  u32 size (4-aligned)  six u16 words  text  NUL padding

The pac-level rules under test: find_edat locates the header behind the pac prefix, the EDAT
size field at edat+4 grows by the record delta, CRILAYLA-compressed members are decoded for the
writer and written back stored, rows with an empty ``en`` change nothing, and a container whose
members do not change is reproduced byte for byte.
"""
from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import cpk_write  # noqa: E402
import crilayla  # noqa: E402
import event_text_apply as ETA  # noqa: E402
import quotes_apply as QA  # noqa: E402
from test_cpk_table import build_synthetic_cpk  # noqa: E402


def dialogue_record(speaker: int, text: bytes) -> bytes:
    size = ETA.padded_size(len(text))
    header = struct.pack("<6H", 1, speaker, 0, 0, 0, 0xFFFF)
    return (struct.pack("<II", 0xC9, size) + header + text
            + b"\x00" * (size - ETA.TEXT_OFFSET_IN_RECORD - len(text)))


def mesbtl_section(speaker: int, text: bytes) -> bytes:
    """One EVNT section holding one C8 wrapper with one C9 quote (the measured shape)."""
    inner = dialogue_record(speaker, text)
    wrapper = struct.pack("<II", 0xC8, 8 + len(inner)) + inner
    payload = struct.pack("<I", 0) + wrapper          # the zero word of the mesbtl variant
    return b"EVNT" + struct.pack("<I", 4 + len(payload)) + payload


def quote_pac(quotes, pac_header_pad: int = 48) -> bytes:
    """A pac: header (no EVNT/EDAT magic in it), 16 zero bytes, then the EDAT with its sections."""
    sections = b"".join(mesbtl_section(speaker, text) for speaker, text in quotes)
    edat = b"EDAT" + struct.pack("<II", sum(
        4 + len(mesbtl_section(s, t)) - 8 for s, t in quotes), len(quotes)) + sections
    header_len = pac_header_pad
    header = struct.pack("<I", header_len - 16) + struct.pack("<H", len(quotes))
    header += b"\x00" * (header_len - len(header))     # the last 16 zeros belong to the pad
    return header + edat


def quote_offsets(pac: bytes):
    records, errors = ETA.parse_block_records(pac)
    assert not errors, errors
    return [r["offset"] + ETA.TEXT_START[r["type"]] for r in records if r["type"] == 0xC9]


def row(offset: int, jp: str, en: str, member: str = "p0050.pac",
        container: str = "mesbtl00.cpk") -> dict:
    return {"id": f"quote:{member}:{offset}", "category": "battle_quote", "part": "quote",
            "jp": jp, "en": en, "kind": "dialogue",
            "source": {"container": container, "member": member, "offset": offset}}


class PacFormatTests(unittest.TestCase):
    QUOTES = [(50, "みせつけてやる！".encode("cp932")),
              (50, "いくぜ！".encode("cp932")),
              (50, "おわりだ！".encode("cp932"))]

    def setUp(self):
        self.pac = quote_pac(self.QUOTES)
        self.offsets = quote_offsets(self.pac)

    def test_find_edat_looks_past_the_pac_header(self):
        self.assertEqual(ETA.find_edat(self.pac), 48)
        self.assertEqual(ETA.find_edat(b"EDAT" + struct.pack("<II", 0, 0) + b"EVNT..."), 0)
        self.assertEqual(ETA.find_edat(b"no header here"), -1)

    def test_the_fixture_walks_without_errors(self):
        _blocks, errors = ETA.EW.blocks(self.pac)
        self.assertEqual(errors, [])
        self.assertEqual(len(self.offsets), 3)

    def test_the_edat_size_field_is_the_sum_of_the_section_sizes(self):
        edat = ETA.find_edat(self.pac)
        declared = struct.unpack_from("<I", self.pac, edat + 4)[0]
        blocks, _ = ETA.EW.blocks(self.pac)
        self.assertEqual(declared, sum(b["size"] for b in blocks))

    def test_growing_a_quote_updates_every_size_around_it(self):
        jp = self.QUOTES[1][1]
        en = "Here we go, and then some more!".encode("cp932")
        modified, report = ETA.apply_member(
            self.pac, [row(self.offsets[1], jp.decode("cp932"), en.decode("cp932"))])
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["applied"], 1)
        delta = len(modified) - len(self.pac)
        self.assertEqual(delta, ETA.padded_size(len(en)) - ETA.padded_size(len(jp)))
        edat_old = ETA.find_edat(self.pac)
        edat_new = ETA.find_edat(modified)
        self.assertEqual(edat_new, edat_old)             # the pac header never moves
        size_old = struct.unpack_from("<I", self.pac, edat_old + 4)[0]
        size_new = struct.unpack_from("<I", modified, edat_new + 4)[0]
        self.assertEqual(size_new - size_old, delta)     # the EDAT size grows by the delta
        self.assertEqual(modified[:edat_old], self.pac[:edat_old])   # header untouched
        texts = [t for _k, _r, t in ETA.texts_of_member(modified)]
        self.assertIn(en.decode("cp932"), texts)
        self.assertIn(self.QUOTES[0][1].decode("cp932"), texts)

    def test_a_row_with_empty_english_is_skipped_by_the_row_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            (package / QA.PACKAGE_FILE).write_text(
                '{"source": {"container": "mesbtl00.cpk", "member": "p0050.pac", "offset": 1},'
                ' "jp": "x", "en": ""}\n'
                '{"source": {"container": "mesbtl00.cpk", "member": "p0050.pac", "offset": 2},'
                ' "jp": "x", "en": "y"}\n'
                '{"source": {"container": "other.cpk", "member": "p0050.pac", "offset": 3},'
                ' "jp": "x", "en": "z"}\n', encoding="utf-8")
            by_member = QA.rows_for_container(package, "mesbtl00.cpk")
        self.assertEqual([r["source"]["offset"] for r in by_member["p0050.pac"]], [2])

    def test_crilayla_round_trip_feeds_the_writer(self):
        pac = quote_pac(self.QUOTES, pac_header_pad=208)   # a CRILAYLA entry needs 0x100 bytes
        compressed = crilayla.compress_literal(pac)
        self.assertTrue(crilayla.is_crilayla(compressed))
        self.assertEqual(QA.decompressed(compressed), pac)
        self.assertEqual(QA.decompressed(pac), pac)


class ContainerTests(unittest.TestCase):
    QUOTES = [(50, "みせつけてやる！".encode("cp932")), (50, "いくぜ！".encode("cp932"))]

    def build_container(self, compress: bool) -> tuple:
        # a CRILAYLA entry needs at least its 0x100-byte trailer, so the pac header is padded
        pad = 208
        pac = quote_pac(self.QUOTES, pac_header_pad=pad)
        if compress:
            # real containers align every member; the synthetic builder packs tight, so pad the
            # stored stream to the declared alignment (a CRILAYLA reader ignores trailing zeros)
            stored = crilayla.compress_literal(pac)
            stored += b"\x00" * ((-len(stored)) % 16)
        else:
            # an uncompressed member must BE aligned: grow the pac header instead of appending
            pad += (-len(pac)) % 16
            pac = quote_pac(self.QUOTES, pac_header_pad=pad)
            stored = pac
        entries = [{"dir": "", "name": "p0050.pac", "data": stored, "id": 0},
                   {"dir": "", "name": "p9999.pac", "data": b"\x00" * 64, "id": 1}]
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "mesbtl00.cpk"
        # align 16: the synthetic content is packed tight, and a rebuilt member that shrinks
        # moves its neighbour back by one alignment unit (a real container aligns to 0x800 and
        # its first pac is stored compressed, so a stored replacement always grows)
        path.write_bytes(build_synthetic_cpk(entries, align=16))
        return path, pac

    def test_a_translated_member_is_written_stored_and_reads_back(self):
        src, pac = self.build_container(compress=True)
        offsets = quote_offsets(pac)
        en = "Watch me show you what I can do!"
        rows = {"p0050.pac": [row(offsets[0], self.QUOTES[0][1].decode("cp932"), en)]}
        dst = src.parent / "out" / "mesbtl00.cpk"
        summary = QA.apply_container(src, dst, rows)
        self.assertEqual(summary["problems"], [])
        self.assertEqual(summary["applied"], 1)
        self.assertTrue(dst.exists())
        rebuilt = cpk_write.load(dst)
        touched = next(m for m in rebuilt.members if m.name == "p0050.pac")
        other = next(m for m in rebuilt.members if m.name == "p9999.pac")
        self.assertEqual(touched.file_size, touched.extract_size)     # written stored
        self.assertFalse(crilayla.is_crilayla(touched.blob))
        self.assertEqual(other.blob, b"\x00" * 64)                    # untouched, byte-identical
        texts = [t for _k, _r, t in ETA.texts_of_member(touched.blob)]
        self.assertIn(en, texts)
        self.assertIn(self.QUOTES[1][1].decode("cp932"), texts)

    def test_several_members_chain_through_the_destination(self):
        src, pac = self.build_container(compress=False)
        offsets = quote_offsets(pac)
        rows = {"p0050.pac": [row(offsets[0], self.QUOTES[0][1].decode("cp932"), "One!"),
                              row(offsets[1], self.QUOTES[1][1].decode("cp932"), "Two!")]}
        dst = src.parent / "mesbtl00.cpk.new"
        summary = QA.apply_container(src, dst, rows)
        self.assertEqual(summary["problems"], [])
        self.assertEqual(summary["applied"], 2)
        rebuilt = cpk_write.load(dst)
        touched = next(m for m in rebuilt.members if m.name == "p0050.pac")
        texts = [t for _k, _r, t in ETA.texts_of_member(touched.blob)]
        self.assertEqual(sorted(texts), sorted(["One!", "Two!"]))

    def test_a_container_without_changes_is_not_written(self):
        src, pac = self.build_container(compress=True)
        offsets = quote_offsets(pac)
        # the row's text does not sit at the claimed offset -> skipped, nothing written
        rows = {"p0050.pac": [row(offsets[0] + 2, self.QUOTES[0][1].decode("cp932"), "Nope!")]}
        dst = src.parent / "mesbtl00.cpk.new"
        summary = QA.apply_container(src, dst, rows)
        self.assertIsNone(summary["written"])
        self.assertFalse(dst.exists())
        self.assertEqual(summary["applied"], 0)
        self.assertTrue(any("skipped" in p for p in summary["problems"]))

    def test_a_member_that_is_not_in_the_container_is_reported(self):
        src, _pac = self.build_container(compress=False)
        rows = {"p1234.pac": [row(10, "x", "y", member="p1234.pac")]}
        summary = QA.apply_container(src, src.parent / "out.cpk", rows)
        self.assertIsNone(summary["written"])
        self.assertTrue(any("not a member" in p for p in summary["problems"]))

    def test_dry_run_checks_without_writing(self):
        src, pac = self.build_container(compress=False)
        offsets = quote_offsets(pac)
        rows = {"p0050.pac": [row(offsets[0], self.QUOTES[0][1].decode("cp932"), "Yes!")]}
        dst = src.parent / "dry.cpk"
        summary = QA.apply_container(src, dst, rows, dry_run=True)
        self.assertEqual(summary["applied"], 1)
        self.assertFalse(dst.exists())


if __name__ == "__main__":
    unittest.main()
