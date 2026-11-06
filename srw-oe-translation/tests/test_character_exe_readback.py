"""Release readback verification is fail-closed without proprietary data."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import verify_character_exe_readback as V
import pl_text


class ExeReadbackTests(unittest.TestCase):
    def setUp(self):
        self.addresses = list(V.EXPECTED)
        self.offsets = {int(a, 16) - V.EX.LOAD_BASE: 100 + i * 512 for i, a in enumerate(self.addresses)}
        self.rows = []
        self.data = bytearray(3000)
        self.data[:4] = V.psp_prx.ELF_MAGIC
        for address in self.addresses:
            text = V.EXPECTED[address]
            offset = self.offsets[int(address, 16) - V.EX.LOAD_BASE]
            encoded = pl_text.encode(text)
            self.data[offset:offset + len(encoded) + 1] = encoded + b'\0'
            self.rows.append({'source': {'vaddr': address, 'offset': offset}, 'pl': text, 'max_bytes': len(encoded)})

    def check(self):
        with patch.object(V.EX, 'Elf') as elf:
            elf.return_value.file_offset.side_effect = self.offsets.get
            return V.verify_image(bytes(self.data), self.rows)

    def test_actual_slot_bytes(self):
        result = self.check()
        self.assertEqual(result['protected_psp_executable_dialogs_verified'], 3)
        self.assertTrue(result['actor_and_gai_verified'])

    def test_changed_or_truncated_value_refused(self):
        self.data[self.rows[0]['source']['offset']] = 0
        with self.assertRaisesRegex(ValueError, 'physical executable readback mismatch'):
            self.check()

    def test_missing_duplicate_and_unreviewed_rows_refused(self):
        row = self.rows.pop()
        with self.assertRaisesRegex(ValueError, 'missing required'):
            self.check()
        self.rows.extend([row, row])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.check()
        self.rows.pop()
        self.rows[0]['pl'] = 'unreviewed'
        with self.assertRaisesRegex(ValueError, 'package differs'):
            self.check()

    def test_wrong_offset_and_budget_refused(self):
        self.rows[0]['source']['offset'] += 1
        with self.assertRaisesRegex(ValueError, 'source offset'):
            self.check()
        self.rows[0]['source']['offset'] -= 1
        self.rows[0]['max_bytes'] -= 1
        with self.assertRaisesRegex(ValueError, 'slot budget'):
            self.check()


if __name__ == '__main__':
    unittest.main()
