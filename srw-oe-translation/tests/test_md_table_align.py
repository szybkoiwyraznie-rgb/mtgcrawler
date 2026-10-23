"""Tests for monospace Notepad++ Markdown table alignment (`tools/md_table_align.py`)."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import md_table_align as TA  # noqa: E402


class MarkdownTableAlignTests(unittest.TestCase):
    def test_pipe_columns_align_and_strip_html_br_tags(self) -> None:
        raw = "\n".join([
            "| Miejsce | Nazwa | Moc bazowa | Zasięg | Trafienie | EN | Morale | Warunek | Zdolności — opisy bazowe |",
            "|---:|---|---:|:---:|---:|---:|---:|---|---|",
            '| 0 | Wiązkowy karabin masz. GN | 2300 | 1–3 | +30 | 5 | — | Brak w tym polu | **Na powietrze (poziom bazowy 1):** Teren "Pow": Cel+50% Atk x1.4<br><br>**Broń wiązkowa (poziom bazowy 1):** Kryt+4% Unik-4% |',
            "| 4 | GN Sword III | 4200 | 1–1 | +40 | 30 | — | Brak w tym polu | **Pchnięcie (poziom bazowy 1):** Odpycha wroga o 1 pole<br>Zderzenie Obraż.500 Obraż. od upadku 1000<br>Ignoruje Osłonę; bez wsparcia |",
        ]) + "\n"

        aligned = TA.align_markdown_tables(raw, max_line_width=216)
        self.assertNotIn("<br>", aligned)
        lines = aligned.strip().splitlines()
        self.assertGreaterEqual(len(lines), 7)

        # Every line has identical length <= 216 and identical pipe offsets!
        pipe_positions = [[idx for idx, ch in enumerate(ln) if ch == "|"] for ln in lines]
        for pos in pipe_positions[1:]:
            self.assertEqual(pos, pipe_positions[0])
        for ln in lines:
            self.assertLessEqual(len(ln), 216)

    def test_spirit_table_wraps_before_viewport_edge(self) -> None:
        raw = "\n".join([
            "| Slot | Duch | Typ | Lv1 (poz. / koszt) | Lv2 (poz. / koszt) | Lv3 (poz. / koszt) | Efekty poziomów (`Lv1`–`Lv3`) |",
            "|---:|---|---|---|---|---|---|",
            "| 2 | **Zapał** | Typ do wyboru | **Poz. 8** (20 SP) | **Poz. 30** (30 SP) | **Poz. 52** (40 SP) | Cel: ty Efekt: 1 razy / Lv1 SP-20 Zadawane obrażenia x1,5 / Lv2 SP-30 Zadawane obrażenia x2,0 / Lv3 SP-40 Zadawane obrażenia x2,5 |",
        ]) + "\n"

        aligned = TA.align_markdown_tables(raw, max_line_width=216)
        lines = aligned.strip().splitlines()
        pipe_positions = [[idx for idx, ch in enumerate(ln) if ch == "|"] for ln in lines]
        for pos in pipe_positions[1:]:
            self.assertEqual(pos, pipe_positions[0])
        for ln in lines:
            self.assertLessEqual(len(ln), 216)

    def test_fenced_code_blocks_untouched(self) -> None:
        raw = "```markdown\n| a | b |\n|---|---|\n| 1 | 2222 |\n```\n"
        self.assertEqual(TA.align_markdown_tables(raw), raw)


if __name__ == "__main__":
    unittest.main()
