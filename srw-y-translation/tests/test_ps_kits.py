"""Lint the owner's PowerShell collectors using only files committed in this repo.

PowerShell 5.1 is unforgiving: a trailing comma in an array literal or a missing
UTF-8 BOM cost a whole round trip with the owner (2026-10-25). Every check here
reads a committed `tools/collect_*.ps1` or regenerates a collector from committed
metadata — no `local/`, no Drive, no built zips, and no skips.

    python3 -m pytest tests/test_ps_kits.py -q
"""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_dictionary_request as dictionary_kit  # noqa: E402
import build_graph_request as graph_kit  # noqa: E402
import build_preset_request as preset_kit  # noqa: E402
import build_final_preset_request as final_kit  # noqa: E402

TOOLS = HERE / 'tools'
COMMITTED = sorted(TOOLS.glob('collect_*.ps1'))


def strip_strings(source: str) -> str:
    """Remove '...' and \"...\" contents so bracket counting looks at code only."""
    out = []
    index = 0
    while index < len(source):
        char = source[index]
        if char == "'":
            end = source.find("'", index + 1)
            if end < 0:
                break
            index = end + 1
            continue
        if char == '"':
            index += 1
            while index < len(source) and source[index] != '"':
                index += 2 if source[index] == '`' else 1
            index += 1
            continue
        out.append(char)
        index += 1
    return ''.join(out)


def generated():
    """(name, PS text, expected number of @-array entries)."""
    return [
        ('dictionary', dictionary_kit.ps_block(dictionary_kit.survey()), 11),
        ('graph', graph_kit.ps_block(graph_kit.survey()), 366),
        ('preset', preset_kit.ps_block(preset_kit.survey()), 109),
        ('final', final_kit.ps_block(final_kit.survey()), None),
    ]


class CommittedScriptTests(unittest.TestCase):
    def test_there_are_owner_collectors_to_lint(self):
        self.assertGreaterEqual(len(COMMITTED), 10)

    def test_every_collector_is_bom_crlf_ascii(self):
        for path in COMMITTED:
            with self.subTest(script=path.name):
                raw = path.read_bytes()
                self.assertTrue(raw.startswith(b'\xef\xbb\xbf'), 'missing UTF-8 BOM')
                self.assertGreater(raw.count(b'\n'), 0)
                self.assertEqual(raw.count(b'\n'), raw.count(b'\r\n'),
                                 'LF-only line found; PS 5.1 needs CRLF')
                raw[3:].decode('ascii')

    def test_every_collector_has_balanced_brackets_and_no_trailing_comma(self):
        for path in COMMITTED:
            with self.subTest(script=path.name):
                text = path.read_text(encoding='utf-8-sig')
                self.assertEqual(re.findall(r',\s*\n\s*\)', text), [],
                                 'PS 5.1 rejects a trailing comma in @( ... )')
                code = strip_strings(text)
                self.assertEqual(code.count('{'), code.count('}'))
                self.assertEqual(code.count('('), code.count(')'))

    def test_every_collector_parses_with_a_real_powershell_grammar(self):
        # tree-sitter-powershell is a declared CI dependency (abi3 wheel).
        import tree_sitter
        import tree_sitter_powershell
        parser = tree_sitter.Parser(
            tree_sitter.Language(tree_sitter_powershell.language()))
        for path in COMMITTED:
            with self.subTest(script=path.name):
                raw = path.read_bytes()
                if raw.startswith(b'\xef\xbb\xbf'):
                    raw = raw[3:]
                tree = parser.parse(raw)
                self.assertFalse(tree.root_node.has_error,
                                 'gramatyka PowerShell widzi blad skladni')

    def test_generated_collector_matches_the_committed_file(self):
        for ps_name, text in [
                ('collect_dictionary_tables.ps1',
                 dictionary_kit.ps_block(dictionary_kit.survey())),
                ('collect_script_graphs.ps1',
                 graph_kit.ps_block(graph_kit.survey())),
                ('collect_missing_presets.ps1',
                 preset_kit.ps_block(preset_kit.survey())),
                ('collect_final_presets.ps1',
                 final_kit.ps_block(final_kit.survey()))]:
            with self.subTest(script=ps_name):
                expected = b'\xef\xbb\xbf' + text.replace('\n', '\r\n').encode('ascii')
                self.assertEqual((TOOLS / ps_name).read_bytes(), expected)


class GeneratedScriptTests(unittest.TestCase):
    def test_no_trailing_comma_and_balanced_brackets(self):
        for name, text, _expected in generated():
            with self.subTest(kit=name):
                self.assertEqual(re.findall(r',\s*\n\s*\)', text), [])
                code = strip_strings(text)
                self.assertEqual(code.count('{'), code.count('}'))
                self.assertEqual(code.count('('), code.count(')'))
                text.encode('ascii')

    def test_array_entries_are_well_formed(self):
        for name, text, expected in generated():
            if expected is None:
                continue
            with self.subTest(kit=name):
                self.assertIn('$pliki = @(', text)
                start = text.index('$pliki = @(')
                block = text[start:text.index('\n    )', start)]
                lines = [line.strip() for line in block.splitlines()[1:] if line.strip()]
                self.assertEqual(len(lines), expected)
                self.assertTrue(all(line.endswith(',') for line in lines[:-1]))
                self.assertFalse(lines[-1].endswith(','))


class RegressionTests(unittest.TestCase):
    """The exact text that failed in the owner's PowerShell on 2026-10-25."""

    def test_former_failure_line_is_gone(self):
        content = (TOOLS / 'collect_dlc_bundles.ps1').read_text(encoding='utf-8-sig')
        self.assertNotIn("f='0dc28ec7b48c3414801a3167ba57f929.bundle' },", content,
                         'the last entry must not end with a comma')


if __name__ == '__main__':
    unittest.main()
