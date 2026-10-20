"""Build BOTH real text-only kits offline, checking workflow's release contract."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build_release_pair as R
import build_distribution as D


class PairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup)
        cls.root=Path(cls.tmp.name);cls.out=cls.root/'pair';cls.version='test-pair'
        cls.records=R.build(cls.out,cls.version)

    def test_both_languages_same_version_and_current_tools(self):
        self.assertEqual(set(self.records),{'en','pl'})
        for lang,record in self.records.items():
            with zipfile.ZipFile(self.out/record['name'])as z:
                m=json.loads(z.read('RELEASE_MANIFEST.json'))
                self.assertEqual(m['language'],lang);self.assertEqual(m['version'],self.version)
                self.assertFalse(m['validation']['errors'])
                self.assertFalse(m['game_data_included'])
                self.assertEqual(z.read('tools/build_translation_patch.py'),(R.ROOT/'tools/build_translation_patch.py').read_bytes())
                for stem in D._resolve(R.ROOT/'tools'):
                    compile(z.read(f'tools/{stem}.py'),stem,'exec')
                self.assertFalse(any(Path(n).suffix.lower()in{'.iso','.edat','.cpk','.bin','.dat','.fta','.pbp','.sav'}for n in z.namelist()))
            self.assertEqual(hashlib.sha256((self.out/record['name']).read_bytes()).hexdigest(),record['sha256'])

    def test_pl_has_coverage_correct_launchers_and_no_missing_metadata(self):
        with zipfile.ZipFile(self.out/self.records['pl']['name'])as z:
            self.assertIn(b'--lang pl',z.read('PATCH.bat'))
            self.assertNotIn(b'the font step takes a moment',z.read('PATCH.bat'))
            self.assertNotIn(b'recompresses font.cpk',z.read('PATCH.bat'))
            self.assertIn(b'--lang pl',z.read('CHECK_DLC.bat'))
            self.assertIn('translation/tokeny.tsv',z.namelist())
            c=json.loads(z.read('translation/PL_COVERAGE.json'))
            self.assertTrue(c['partial']);self.assertEqual(c['source_return'],json.loads((R.ROOT/'pakiet_PL/snapshot.json').read_text())['source_return'])
            self.assertGreater(c['totals']['filled'],0)
        self.assertTrue((self.out/'SHA256SUMS.txt').exists())
        self.assertTrue((self.out/'RELEASE_PAIR.json').exists())

    def test_missing_pl_does_not_validate_as_english_only_release(self):
        empty=self.root/'missing';empty.mkdir()
        with self.assertRaises(FileNotFoundError):R.verify_pair(empty,self.version)

    def test_refuses_stale_output(self):
        with self.assertRaisesRegex(ValueError,'stale'):R.build(self.out,self.version)

    def test_version_cannot_escape_output_or_inject_shell(self):
        for version in ['../outside','a/b','bad\nversion','$(echo nope)']:
            with self.assertRaisesRegex(ValueError,'unsafe'):R.build(self.root/'unsafe',version)


class WorkflowTests(unittest.TestCase):
    def test_push_main_builds_two_then_publishes_only_main(self):
        text=(R.ROOT.parent/'.github/workflows/release.yml').read_text()
        self.assertIn('branches: [main]',text)
        self.assertIn('pull_request:',text)
        self.assertIn('tools/build_release_pair.py',text)
        self.assertIn("github.ref == 'refs/heads/main'",text)
        self.assertIn('needs: build',text)
        self.assertIn('uses: actions/download-artifact@v4',text)
        self.assertIn('sha256sum --check SHA256SUMS.txt',text)
        self.assertIn('"$EN" "$PL"',text)
        self.assertNotIn('list_connector',text)
        self.assertNotIn('local/pakiet_v',text)
