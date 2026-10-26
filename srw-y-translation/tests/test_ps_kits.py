"""Lint the PowerShell kits handed to the owner, without running PowerShell.

The owner has no repository checkout and only PowerShell 5.1, so a syntax error in a
generated script costs a whole round trip (it happened on 2026-10-25: a trailing comma
in an array literal made PS 5.1 stop with "Missing expression after ','").  These
tests check the generated files the way 5.1 reads them: BOM + CRLF, ASCII only, no
trailing comma before a closing paren, balanced braces and parentheses, and the
expected number of entries.

    python3 -m unittest discover -s tests
"""
import re
import sys
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import build_dlc_bundle_request as dlc  # noqa: E402
import build_free_patch_request as free_kit  # noqa: E402
import build_text_upload_request as text_kit  # noqa: E402
import build_voice_speaker_request as voice_kit  # noqa: E402

KITS = [
    ('dlc', dlc, 'collect_dlc_bundles.ps1', 'SRW_Y_ZBIERZ_DLC.zip', 'ZBIERZ_DLC_BUNDLE.ps1'),
    ('text', text_kit, 'collect_text_bundles.ps1', 'SRW_Y_ZBIERZ_TEKST.zip', 'ZBIERZ_TEKST.ps1'),
    ('free', free_kit, 'collect_free_patch.ps1', 'SRW_Y_ZBIERZ_S6E.zip', 'ZBIERZ_S6E.ps1'),
    ('voice', voice_kit, 'collect_voice_speaker_data.ps1', 'SRW_Y_GLOSY_PROSBA.zip',
     'ZBIERZ_GLOSY.ps1'),
]


def strip_strings(source: str) -> str:
    """Remove '...' and "..." contents so bracket counting looks at code only."""
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


class KitTests(unittest.TestCase):
    @staticmethod
    def plan_for(module):
        if module is dlc:
            return module.survey(dlc.read_listing(dlc.LISTING))
        if module is free_kit:
            return module.survey(module.read_listing(module.LISTING))
        if module is voice_kit:
            return module.resolve()
        import json
        if not text_kit.MAPPING.is_file():
            raise unittest.SkipTest('brak local/mapping.json — plik roboczy poza '
                                    'repozytorium, zestaw juz odebrany')
        mapping = json.loads(text_kit.MAPPING.read_text(encoding='utf-8'))
        sizes = text_kit.read_listing(text_kit.LISTING)
        have = {path.name for path in text_kit.HAVE.glob('*.bundle')}
        return text_kit.collect(mapping, sizes, have)

    def kit_paths(self, module, ps_name, zip_name):
        plan = self.plan_for(module)
        wanted = plan.get('wanted') or plan.get('need') or []
        if not wanted:
            raise unittest.SkipTest('nic do zebrania — paczki z tymi plikami juz odebrane')
        return plan, module.ps_block(plan)

    def test_no_trailing_comma_before_closing_paren(self):
        for name, module, ps_name, _zip, _member in KITS:
            with self.subTest(kit=name):
                _plan, ps_text = self.kit_paths(module, ps_name, None)
                bad = re.findall(r',\s*\n\s*\)', ps_text)
                self.assertEqual(bad, [], 'PS 5.1 rejects a trailing comma in @( ... )')

    def test_brackets_balance_without_strings(self):
        for name, module, ps_name, _zip, _member in KITS:
            with self.subTest(kit=name):
                _plan, ps_text = self.kit_paths(module, ps_name, None)
                code = strip_strings(ps_text)
                self.assertEqual(code.count('{'), code.count('}'))
                self.assertEqual(code.count('('), code.count(')'))

    def test_array_entries_are_well_formed(self):
        for name, module, ps_name, _zip, _member in KITS:
            with self.subTest(kit=name):
                plan, ps_text = self.kit_paths(module, ps_name, None)
                start = ps_text.index('$pliki = @(')
                block = ps_text[start:ps_text.index('\n    )', start)]
                lines = [line.strip() for line in block.splitlines()[1:] if line.strip()]
                expected = len(plan['wanted']) if 'wanted' in plan else len(plan['need'])
                self.assertEqual(len(lines), expected)
                for line in lines[:-1]:
                    self.assertTrue(line.endswith(','), line)
                self.assertFalse(lines[-1].endswith(','), lines[-1])

    def test_written_files_are_ps51_friendly(self):
        for name, module, ps_name, _zip, _member in KITS:
            with self.subTest(kit=name):
                path = HERE / 'tools' / ps_name
                raw = path.read_bytes()
                self.assertTrue(raw.startswith(b'\xef\xbb\xbf'), 'missing UTF-8 BOM')
                self.assertEqual(raw.count(b'\n'), raw.count(b'\r\n'), 'LF-only line found')
                raw[3:].decode('ascii')  # PS 5.1 reads a BOM-less file as ANSI

    def test_zip_members_are_loadable(self):
        for name, _module, _ps, zip_name, member in KITS:
            with self.subTest(kit=name):
                path = HERE / 'build' / zip_name
                if not path.is_file():
                    # built kits are generated, never committed: build one to check it
                    self.skipTest(f'{zip_name} nie jest zbudowany')
                with zipfile.ZipFile(path) as archive:
                    names = set(archive.namelist())
                    self.assertEqual(names, {member, 'URUCHOM_TO.bat', 'CZYTAJ_TO.txt'})
                    data = archive.read(member)
                    self.assertTrue(data.startswith(b'\xef\xbb\xbf'))
                    batch = archive.read('URUCHOM_TO.bat')
                    batch.decode('ascii')
                    self.assertIn(b'pause', batch)
                    self.assertIn(b'Unblock-File', batch)


class RegressionTests(unittest.TestCase):
    """The exact text that failed in the owner's PowerShell on 2026-10-25."""

    def test_former_failure_line_is_gone(self):
        path = HERE / 'tools' / 'collect_dlc_bundles.ps1'
        content = path.read_text(encoding='utf-8-sig')
        self.assertNotIn("f='0dc28ec7b48c3414801a3167ba57f929.bundle' },", content,
                         'the last entry must not end with a comma')


if __name__ == '__main__':
    unittest.main()
