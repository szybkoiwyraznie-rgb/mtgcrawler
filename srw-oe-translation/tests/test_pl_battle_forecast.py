"""Synthetic instruction & UI tests for Polish Battle Forecast fixes."""

from __future__ import annotations

import math
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import battle_forecast_pl as B
import exe_strings as E
import spirit_name_cache as S

RELOC_CALL_SITES = {
    0x1CB1C8,  # jal measure_width
    0x1CB1E8,  # jal set_position
    0x1CB228,  # original mode 2 jal
    0x1CB23C,  # original mode 2 jal
    0x1CB26C,  # original mode 1 jal
    0x1CB280,  # original mode 1 jal
}


def f2u(v: float) -> int:
    return struct.unpack("<I", struct.pack("<f", v))[0]


def u2f(u: int) -> float:
    return struct.unpack("<f", struct.pack("<I", u & 0xFFFFFFFF))[0]


class BattleForecastPlTests(unittest.TestCase):
    def fixture(self) -> tuple[bytes, int, int, int]:
        text_off = 0xA0
        rodata_addr = 0x3EEC70
        rodata_off = 0x3EED10
        size = rodata_off + (0x3F4524 - rodata_addr) + 16
        buf = bytearray(size)
        for address, old, _ in B.TEXT_PATCHES:
            struct.pack_into("<I", buf, text_off + address, old)
        for address, old, _ in B.RODATA_PATCHES:
            struct.pack_into("<I", buf, rodata_off + (address - rodata_addr), old)
        return bytes(buf), text_off, rodata_off, rodata_addr

    def test_disjoint_from_spirit_cache_and_relocs(self) -> None:
        bf_addrs = {a for a, _, _ in B.TEXT_PATCHES}
        sp_addrs = {a for a, _, _ in S.PATCHES}
        self.assertFalse(bf_addrs & sp_addrs)
        self.assertFalse(bf_addrs & RELOC_CALL_SITES)
        self.assertEqual(len(bf_addrs), len(B.TEXT_PATCHES))

    def test_synthetic_patch_sections_and_guardrails(self) -> None:
        raw, text_off, rodata_off, rodata_addr = self.fixture()
        patched = B.patch_sections(raw, text_off, rodata_off, rodata_addr)
        changed = sum(1 for a, b in zip(raw, patched) if a != b)
        self.assertLessEqual(changed, 4 * (len(B.TEXT_PATCHES) + len(B.RODATA_PATCHES)))

        lv_pos = rodata_off + (0x3F451C - rodata_addr)
        self.assertEqual(patched[lv_pos : lv_pos + 8], b" Lv%d\x00\x00\x00")

        # 512.0f texture width and 28.0f ' Lv%d' advance
        self.assertEqual(
            struct.unpack_from("<I", patched, text_off + 0x1CAF90)[0], 0x3C054400
        )
        self.assertEqual(
            struct.unpack_from("<I", patched, text_off + 0x1CAFE8)[0], 0x3C0441E0
        )

        # Corrupting any expected word must fail closed
        corrupt = bytearray(raw)
        corrupt[text_off + B.TEXT_PATCHES[0][0]] ^= 0xFF
        with self.assertRaises(ValueError):
            B.patch_sections(bytes(corrupt), text_off, rodata_off, rodata_addr)

    def test_cwcheat_addresses_and_values(self) -> None:
        lines = B.cheat_lines()
        self.assertEqual(len(lines), len(B.TEXT_PATCHES) + len(B.RODATA_PATCHES))
        self.assertIn("_L 0x201CEF90 0x3C054400", lines)
        self.assertIn("_L 0x201CEFE8 0x3C0441E0", lines)
        self.assertIn("_L 0x203F851C 0x25764C20", lines)
        self.assertIn("_L 0x203F8520 0x00000064", lines)

    def test_mips_cop1_auto_fit_screen_bounds(self) -> None:
        """Execute patched 0x089cf1a0..0x089cf2a0 words and check screen spans."""
        base = E.LOAD_BASE
        RELOC_CALL_SITES_LOCAL = {
            0x1CB1BC,  # jal build_left_labels
            0x1CB1D0,  # jal sub_089cef34 (measure + create CFontString)
            0x1CB1E8,  # jal CFontString::set_position
            0x1CB214,  # jal build_unit_labels
            0x1CB228,  # original mode 2 jal
            0x1CB23C,  # original mode 2 jal
            0x1CB258,  # jal build_right_labels
            0x1CB26C,  # original mode 1 jal
            0x1CB280,  # original mode 1 jal
        }
        self.assertFalse({a for a, _, _ in B.TEXT_PATCHES} & RELOC_CALL_SITES_LOCAL)

        code = {
            0x089CF1A0: 0x1E400015,  # bgtz $s2, 0x089cf1f8
            0x089CF1A4: 0x2A440002,  # slti $a0, $s2, 2
            0x089CF1A8: 0x0640003D,  # bltz $s2, 0x089cf2a0
            0x089CF1AC: 0x00000000,
            0x089CF1B4: 0x00000000,
            0x089CF1B8: 0x00000000,
            0x089CF1BC: 0x00000000,
            0x089CF1C0: 0x00000000,
            0x089CF1C4: 0x00000000,
            0x089CF1C8: 0x00000000,
            0x089CF1CC: 0x00000000,
            0x089CF1D0: 0x0C000001,  # stub: sub_089cef34 -> $f0 = total_w
            0x089CF1D4: 0x00000000,
            0x089CF1E8: 0x0C000002,  # stub: set_position($a0, $f12, $f13)
            0x089CF1F0: 0x1000002B,  # b 0x089cf2a0 (exit)
            0x089CF1F4: 0x00000000,
            0x089CF1F8: 0x14800014,  # bne  $a0, $zero, 0x089cf24c
            0x089CF1FC: 0x2A440003,  # slti $a0, $s2, 3
            0x089CF200: 0x10800027,  # beq  $a0, $zero, 0x089cf2a0
            0x089CF204: 0x00000000,
            0x089CF208: 0x00000000,
            0x089CF20C: 0x00000000,
            0x089CF210: 0x00000000,
            0x089CF214: 0x00000000,
            0x089CF218: 0x00000000,
            0x089CF228: 0xDEAD0001,
            0x089CF23C: 0xDEAD0002,
            0x089CF24C: 0x00000000,
            0x089CF250: 0x00000000,
            0x089CF254: 0x00000000,
            0x089CF258: 0x00000000,
            0x089CF25C: 0x00000000,
            0x089CF26C: 0xDEAD0003,
            0x089CF280: 0xDEAD0004,
            0x089CF290: 0x10000003,
            0x089CF294: 0x00000000,
        }
        for rel, _, new_w in B.TEXT_PATCHES:
            va = base + rel
            if 0x089CF1A0 <= va <= 0x089CF294:
                code[va] = new_w

        def run_case(mode: int, total_w: float, parent_x: float):
            gpr = [0] * 32
            fpr = [0] * 32
            cc = [False]
            mem = {0x1014: 0x2000, 0x201C: f2u(1.0)}
            gpr[16] = 0x1000  # $s0
            gpr[18] = mode    # $s2
            fpr[20] = f2u(5.0)
            pos_out = []

            def exec_insn(ins: int):
                op = (ins >> 26) & 0x3F
                rs = (ins >> 21) & 0x1F
                rt = (ins >> 16) & 0x1F
                rd = (ins >> 11) & 0x1F
                imm = ins & 0xFFFF
                simm = imm - 0x10000 if (imm & 0x8000) else imm
                if ins == 0:
                    return
                if op == 0x0F:
                    gpr[rt] = (imm << 16) & 0xFFFFFFFF
                elif op == 0x09:
                    gpr[rt] = (gpr[rs] + simm) & 0xFFFFFFFF
                elif op == 0x0A:
                    sval = gpr[rs] - 0x100000000 if (gpr[rs] & 0x80000000) else gpr[rs]
                    gpr[rt] = 1 if sval < simm else 0
                elif op == 0x23:
                    gpr[rt] = mem[(gpr[rs] + simm) & 0xFFFFFFFF]
                elif op == 0x39:
                    mem[(gpr[rs] + simm) & 0xFFFFFFFF] = fpr[rt]
                elif op == 0x03:
                    target = ins & 0x03FFFFFF
                    if target == 1:
                        fpr[0] = f2u(total_w)
                    elif target == 2:
                        pos_out.append((u2f(fpr[12]), u2f(fpr[13])))
                    else:
                        raise AssertionError(f"unexpected call target {target:#x}")
                elif op == 0x11:
                    fmt = rs
                    ft, fs, fd, fn = rt, rd, (ins >> 6) & 0x1F, ins & 0x3F
                    if fmt == 0x04:
                        fpr[fs] = gpr[rt]
                    elif fmt == 0x10:
                        a, b = u2f(fpr[fs]), u2f(fpr[ft])
                        if fn == 0x06:
                            fpr[fd] = fpr[fs]
                        elif fn == 0x01:
                            fpr[fd] = f2u(a - b)
                        elif fn == 0x03:
                            fpr[fd] = f2u(a / b)
                        elif fn == 0x3C:
                            cc[0] = a < b
                        else:
                            raise AssertionError(f"unexpected cop1 fn {fn:#x}")
                else:
                    raise AssertionError(f"unexpected opcode {ins:#010x}")

            pc = 0x089CF1A0
            steps = 0
            while pc != 0x089CF2A0:
                steps += 1
                self.assertLess(steps, 100)
                ins = code[pc]
                op = (ins >> 26) & 0x3F
                rs = (ins >> 21) & 0x1F
                rt = (ins >> 16) & 0x1F
                imm = ins & 0xFFFF
                simm = imm - 0x10000 if (imm & 0x8000) else imm
                sval = gpr[rs] - 0x100000000 if (gpr[rs] & 0x80000000) else gpr[rs]
                if op == 0x04:
                    taken = gpr[rs] == gpr[rt]
                    exec_insn(code[pc + 4])
                    pc = (pc + 4 + (simm << 2)) if taken else (pc + 8)
                elif op == 0x05:
                    taken = gpr[rs] != gpr[rt]
                    exec_insn(code[pc + 4])
                    pc = (pc + 4 + (simm << 2)) if taken else (pc + 8)
                elif op == 0x07:
                    taken = sval > 0
                    exec_insn(code[pc + 4])
                    pc = (pc + 4 + (simm << 2)) if taken else (pc + 8)
                elif op == 0x01 and rt == 0:
                    taken = sval < 0
                    exec_insn(code[pc + 4])
                    pc = (pc + 4 + (simm << 2)) if taken else (pc + 8)
                elif op == 0x14:
                    taken = gpr[rs] == gpr[rt]
                    if taken:
                        exec_insn(code[pc + 4])
                        pc = pc + 4 + (simm << 2)
                    else:
                        pc = pc + 8
                elif op == 0x11 and rs == 0x08:
                    cond = bool(rt & 1)
                    taken = cc[0] == cond
                    exec_insn(code[pc + 4])
                    pc = (pc + 4 + (simm << 2)) if taken else (pc + 8)
                elif op == 0x03:
                    exec_insn(code[pc + 4])
                    exec_insn(ins)
                    pc += 8
                else:
                    exec_insn(ins)
                    pc += 4

            self.assertEqual(len(pos_out), 1)
            rel_x, rel_y = pos_out[0]
            self.assertTrue(math.isclose(rel_y, 5.0))
            sx = u2f(mem[0x201C])
            x0 = parent_x + rel_x + 5.0 * sx
            x1 = parent_x + rel_x + total_w * sx
            return sx, x0, x1

        # Screen 2: 'Na powietrze Lv1 Na okręty Lv1' (217 px) on left bar -> fits >= 0!
        sx, x0, x1 = run_case(0, 217.0, 0.0)
        self.assertGreaterEqual(x0, 0.0)
        self.assertAlmostEqual(x1, 190.0, places=2)
        self.assertLess(sx, 1.0)

        # Worst-case 259 px left weapon bar -> fits [3.19 .. 190.0]!
        sx, x0, x1 = run_case(0, 259.0, 0.0)
        self.assertGreater(x0, 3.0)
        self.assertAlmostEqual(x1, 190.0, places=2)

        # Screen 3 support bar: 'Na okręty Lv1 Broń wiązkowa Lv1' (224 px) -> [285.375 .. 477]!
        sx, x0, x1 = run_case(1, 224.0, 275.0)
        self.assertAlmostEqual(x0, 285.375, places=3)
        self.assertAlmostEqual(x1, 477.0, places=2)

        # Worst-case 350 px unit skill bar (mode 2) -> fits inside 416 px!
        sx, x0, x1 = run_case(2, 350.0, 214.0)
        self.assertGreater(x0, 226.0)
        self.assertAlmostEqual(x1, 416.0, places=2)

    def test_terrain_restriction_panel_alignment_and_full_polish_strings(self) -> None:
        """Map terrain panel (0x089b7c88..0x089b7d34) left-aligns at X=14 and unclips 'postoju'."""
        import pl_text

        raw, text_off, rodata_off, rodata_addr = self.fixture()
        patched = B.patch_sections(raw, text_off, rodata_off, rodata_addr)

        for x_rel in (0x1B3C90, 0x1B3CC4, 0x1B3CEC):
            self.assertEqual(
                struct.unpack_from("<I", patched, text_off + x_rel)[0], 0x3406000E
            )
        self.assertEqual(
            struct.unpack_from("<I", patched, text_off + 0x1B3CD0)[0], 0x24A5422A
        )

        terr_pos = rodata_off + (0x3F4218 - rodata_addr)
        terr_raw = patched[terr_pos : terr_pos + 28]
        cstr_stop, rest = terr_raw.split(b"\x00", 1)
        self.assertEqual(pl_text.decode(cstr_stop), "Ląd: bez postoju")
        # Starts at 0x08bf822a == 0x08bf8218 + 18 (16 bytes + 2 nulls)
        cstr_ban = terr_raw[18:].split(b"\x00", 1)[0]
        self.assertEqual(pl_text.decode(cstr_ban), "Ląd: zakaz")

        # Post-EXE terrain words may hold EXE.apply_rows output before overwrite
        exe_buf = bytearray(raw)
        exe_buf[terr_pos : terr_pos + 16] = pl_text.encode("Ląd: bez post.") + b"\x00\x00"
        post = B.patch_sections(
            bytes(exe_buf), text_off, rodata_off, rodata_addr, allow_translated_terrain=True
        )
        self.assertEqual(post, patched)

    def test_surround_ok_badge_specs_and_crisp_rendering(self) -> None:
        """Both 'Okrążenie' ('OK') badges in tacsys_15 and mensys_15 use crisp layout."""
        import json
        import gim_label

        root = Path(__file__).resolve().parents[1]
        tac = json.loads((root / "ui_labels" / "tacsys_15.json").read_text(encoding="utf-8"))
        men = json.loads((root / "ui_labels" / "mensys_15.json").read_text(encoding="utf-8"))

        tac_ok = next(x for x in tac["labels"] if x["id"] == "surround_badge")
        men_ok = next(x for x in men["labels"] if x["id"] == "surround")
        self.assertEqual(tac_ok["pl"], "OK")
        self.assertEqual(men_ok["pl"], "OK")
        self.assertTrue(tac_ok["pl_layout"]["crisp"])
        self.assertTrue(men_ok["pl_layout"]["crisp"])
        self.assertEqual(tac_ok["pl_layout"]["box"], [5, 18, 20, 30])
        self.assertEqual(men_ok["pl_layout"]["box"], [107, 3, 118, 12])

        try:
            import PIL  # noqa: F401
        except ImportError:
            return
        font_path = root / tac["font"]
        s1, cap1 = gim_label.fit_crisp_size(
            font_path, "OK", 15, 12, 8, 7, (255, 255, 255, 255), (47, 28, 12, 255)
        )
        self.assertIsNotNone(s1)
        self.assertLessEqual(cap1.width, 15)
        self.assertLessEqual(cap1.height, 12)
        raw_rgba = cap1.tobytes()
        white_px = sum(
            1
            for i in range(0, len(raw_rgba), 4)
            if raw_rgba[i : i + 4] == b"\xff\xff\xff\xff"
        )
        self.assertGreaterEqual(white_px, 20)

        s2, cap2 = gim_label.fit_crisp_size(
            font_path, "OK", 11, 9, 7, 6, (255, 255, 255, 255), (54, 23, 0, 255)
        )
        self.assertIsNotNone(s2)
        self.assertLessEqual(cap2.width, 11)
        self.assertLessEqual(cap2.height, 9)


if __name__ == "__main__":
    unittest.main()
