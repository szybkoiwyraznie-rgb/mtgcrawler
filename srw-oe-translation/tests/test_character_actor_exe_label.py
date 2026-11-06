"""Source-bound Polish label for the character actor override in 1.08 EXE."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import exe_strings as X
import pl_release_package as R
import pl_text
import text_codec

ROW = 'exe:PBOOT.PBP/DATA.PSP:0x08bf43a0'
PLAN = ROOT / 'config/pl/character-actor-exe-label-2026-11-02.json'


class ActorOverrideTests(unittest.TestCase):
    def test_source_plan_binding_and_budget(self):
        source = next(json.loads(line) for line in (ROOT / 'pakiet_EN/09_executable.jsonl').read_text(encoding='utf-8').splitlines() if ROW in line)
        entry = next(json.loads(line) for line in (ROOT / 'pakiet_PL/polish.jsonl').read_text(encoding='utf-8').splitlines() if ROW in line)
        plan = json.loads(PLAN.read_text(encoding='utf-8'))['changes'][0]
        self.assertEqual(source['jp'], '声優：戸谷公次')
        self.assertEqual(entry['source_sha256'], R.binding(source))
        self.assertEqual(entry['source_sha256'], plan['source_sha256'])
        self.assertEqual(entry['pl'], plan['after'])
        self.assertEqual(entry['pl'], 'Głos: K.Totani')
        self.assertEqual(len(pl_text.encode(entry['pl'])), source['max_bytes'])
        manifest = json.loads((ROOT / 'pakiet_PL/snapshot.json').read_text(encoding='utf-8'))
        history = next(h for h in manifest['owner_ui_corrections'] if h['plan'] == PLAN.name)
        self.assertEqual(history['sha256'], hashlib.sha256(PLAN.read_bytes()).hexdigest())

    def test_writer_preserves_every_neighbor_byte(self):
        row = next(json.loads(line) for line in (ROOT / 'pakiet_EN/09_executable.jsonl').read_text(encoding='utf-8').splitlines() if ROW in line)
        row['source']['offset'] = 128
        row['en'] = 'Głos: K.Totani'
        original = bytearray(b'X' * 256)
        original[128:143] = row['jp'].encode('cp932') + b'\0'
        previous = text_codec.lang()
        text_codec.set_lang('pl')
        try:
            result, report = X.apply_rows(bytes(original), [row])
            self.assertEqual(report['applied'], 1)
            self.assertEqual(result[128:142], pl_text.encode('Głos: K.Totani'))
            self.assertEqual(result[142:], original[142:])
            self.assertEqual(result[:128], original[:128])
        finally:
            text_codec.set_lang(previous)


if __name__ == '__main__':
    unittest.main()
