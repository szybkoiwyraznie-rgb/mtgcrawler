"""A tools-only update must be complete, inert with respect to user data, and importable."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build_builder_update as U
import build_distribution as D


class BuilderUpdateTests(unittest.TestCase):
    def test_complete_tools_only_archive(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp);out=root/'update.zip';receipt=U.build(out)
            with zipfile.ZipFile(out)as z:
                self.assertIsNone(z.testzip())
                manifest=json.loads(z.read('BUILDER_TOOLS.json'))
                tools={f'tools/{s}.py'for s in D._resolve(U.HERE,('build_translation_patch',))}
                self.assertEqual(set(z.namelist()),tools|{'BUILDER_TOOLS.json','README_BUILDER_UPDATE.md'})
                self.assertEqual(set(manifest['sha256_by_file']),tools)
                self.assertEqual(manifest['languages'],['en','pl'])
                self.assertFalse(manifest['translation_files_included'])
                self.assertFalse(manifest['launchers_replaced'])
                self.assertFalse(manifest['game_binaries_included'])
                for name in tools:
                    self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),manifest['sha256_by_file'][name])
                # Overlay exactly as a user would. Translation and launcher survive.
                kit=root/'kit';(kit/'translation').mkdir(parents=True)
                sentinel=kit/'translation/07_names_characters.jsonl'
                sentinel.write_bytes(b'private PL translation sentinel')
                launcher=kit/'PATCH.bat';launcher.write_bytes(b'original EN or PL launcher')
                z.extractall(kit)
            self.assertEqual(sentinel.read_bytes(),b'private PL translation sentinel')
            self.assertEqual(launcher.read_bytes(),b'original EN or PL launcher')
            # No repository modules on this subprocess path: exercise extracted deps.
            for lang in ['en','pl']:
                run=subprocess.run([sys.executable,'tools/build_translation_patch.py','--help'],cwd=kit,
                                   capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stderr)
                self.assertIn('--lang',run.stdout)
            self.assertEqual(receipt['sha256'],hashlib.sha256(out.read_bytes()).hexdigest())

    def test_refuses_to_overwrite_existing_archive(self):
        with tempfile.TemporaryDirectory()as temp:
            out=Path(temp)/'update.zip';out.write_bytes(b'do not overwrite')
            with self.assertRaises(FileExistsError):U.build(out)
            self.assertEqual(out.read_bytes(),b'do not overwrite')
