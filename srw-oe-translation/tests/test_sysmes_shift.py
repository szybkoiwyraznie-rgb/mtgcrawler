"""sysmes_shift is a shim over sysmes_pack.translate (the old shift model was wrong)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import sysmes_pack as sp  # noqa: E402
import sysmes_shift as ss  # noqa: E402


class SysmesShiftShimTests(unittest.TestCase):
    def test_shift_translate_delegates_and_verifies(self):
        sm = sp.make_sysmes(["Ａ", "ライブラリー", "リファレンス", "クレジット"])
        new, lines = ss.shift_translate(sm, {"ライブラリー": "LIBRARY", "クレジット": "CREDITS"})
        self.assertTrue(ss.verify(sm, new, {"ライブラリー": "LIBRARY", "クレジット": "CREDITS"}))
        parsed = sp.parse(new)
        self.assertEqual(parsed.strings[1:], [b"LIBRARY", "リファレンス".encode("cp932"), b"CREDITS"])
        self.assertEqual({k for k, _ in lines}, {"ライブラリー", "クレジット"})

    def test_verify_rejects_a_foreign_change(self):
        sm = sp.make_sysmes(["Ａ", "ライブラリー", "リファレンス"])
        new = sp.apply_edits(sm, {"リファレンス": "REFERENCE"})
        self.assertFalse(ss.verify(sm, new, {"ライブラリー": "LIBRARY"}))


if __name__ == "__main__":
    unittest.main()
