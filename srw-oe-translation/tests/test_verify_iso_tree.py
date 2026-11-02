from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import iso_pack
import verify_iso_tree as V


class CompareTreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.tree = root / 'tree'
        (self.tree / 'DIR').mkdir(parents=True)
        (self.tree / 'DIR' / 'abc.dat').write_bytes(b'abc')
        (self.tree / 'empty').write_bytes(b'')
        self.iso = root / 'image.iso'
        self.iso.write_bytes(iso_pack.build_iso({'DIR': {'abc.dat': b'abc'}, 'empty': b''}))

    def test_identical_and_same_size_content_change(self):
        result = V.verify(self.iso, self.tree)
        self.assertTrue(result['matches'])
        self.assertEqual(result['hashes_compared'], 2)
        (self.tree / 'DIR' / 'abc.dat').write_bytes(b'xyz')
        self.assertEqual(V.verify(self.iso, self.tree)['mismatched'], ['DIR/abc.dat'])

    def test_missing_extra_and_case_sensitive(self):
        (self.tree / 'DIR' / 'abc.dat').unlink()
        (self.tree / 'DIR' / 'ABC.dat').write_bytes(b'abc')
        result = V.verify(self.iso, self.tree)
        self.assertFalse(result['matches'])
        self.assertEqual(result['only_in_tree'], ['DIR/ABC.dat'])
        self.assertEqual(result['only_in_iso'], ['DIR/abc.dat'])

    def test_size_difference_and_symlink(self):
        (self.tree / 'empty').write_bytes(b'x')
        self.assertEqual(V.verify(self.iso, self.tree)['mismatched'], ['empty'])
        (self.tree / 'link').symlink_to(self.tree / 'empty')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            V.verify(self.iso, self.tree)


if __name__ == '__main__':
    unittest.main()
