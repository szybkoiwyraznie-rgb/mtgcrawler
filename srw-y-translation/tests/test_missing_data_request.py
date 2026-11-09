"""Kit 6 (`SRW_Y_BRAKUJACE_DANE_PROSBA.zip`) — collector behaviour on a synthetic game.

The collector runs on the owner's machine, so the only thing we can test here is its
logic: catalogue parsing, address selection, skipping bundles we already have, the
listing, and the safety caps. A synthetic `StreamingAssets` tree is built from the same
catalogue encoder the parser tests use.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'tools'))

import test_map_catalog as fixture  # noqa: E402

KIT = ROOT / 'tools' / 'kit_zbierz_brakujace.py'


def game_tree(base: Path, *, addresses: dict[str, str], known: set[str]) -> Path:
    """`StreamingAssets` with one catalogue and one file per address -> bundle name."""
    streaming = base / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets'
    bundle_dir = streaming / 'aa' / 'StandaloneWindows64'
    bundle_dir.mkdir(parents=True)
    keys, entries, buckets, internal = [], [], [], []
    bundle_key: dict[str, int] = {}
    for name in sorted(set(addresses.values())):
        bundle_key[name] = len(keys)
        keys.append(name)
        internal.append('{' + 'UnityEngine.AddressableAssets.Addressables.RuntimePath'
                        '}\\StandaloneWindows64\\' + name + '.bundle')
        entries.append((len(internal) - 1, 1, -1, 0, 0, 0, 0))
        buckets.append((len(keys) - 1, [len(entries) - 1]))
        (bundle_dir / f'{name}.bundle').write_bytes(b'x' * 64 + name.encode())
    for address, name in sorted(addresses.items()):
        keys.append(address)
        entries.append((0, 2, bundle_key[name], 0, 0, 0, 0))
        buckets.append((len(keys) - 1, [len(entries) - 1]))
    catalog = fixture.build_catalog(keys, entries, buckets)
    catalog['m_InternalIds'] = internal
    (streaming / 'aa' / 'catalog.json').write_text(json.dumps(catalog), encoding='utf-8')
    (streaming / 'aa' / 'catalog.hash').write_text('hash\n', encoding='utf-8')
    (streaming / 'aa' / 'settings.json').write_text('{}\n', encoding='utf-8')
    return streaming


class KitShapeTests(unittest.TestCase):
    """The kit must look like the ones that already ran on the owner's machine."""

    def setUp(self):
        import build_missing_data_request as builder
        self.builder = builder

    def test_bat_checks_python_and_says_so(self):
        text = self.builder.BATCH
        self.assertIn('py -3 -c "import sys; assert sys.version_info >= (3,9)"', text)
        self.assertIn('python -c "import sys; assert sys.version_info >= (3,9)"', text)
        self.assertIn(':nopython', text)
        self.assertIn('https://www.python.org/downloads/', text)
        self.assertIn('pause', text)

    def test_bat_is_ascii_and_crlf_when_written(self):
        raw = self.builder.BATCH.replace('\n', '\r\n').encode('ascii')  # raises if not ASCII
        self.assertGreater(raw.count(b'\r\n'), 10)
        self.assertEqual(raw.count(b'\n'), raw.count(b'\r\n'))

    def test_collector_is_stdlib_only(self):
        source = KIT.read_text(encoding='utf-8')
        for module in ('UnityPy', 'Crypto', 'lz4'):
            self.assertNotIn(f'import {module}', source)

    def test_collector_writes_a_log_next_to_the_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            streaming = game_tree(base, addresses={'Assets/Datas/MissionData': 'aaaa'},
                                  known=set())
            desktop = base / 'Desktop'
            desktop.mkdir()
            result = subprocess.run(
                [sys.executable, str(KIT), '--streamingassets', str(streaming),
                 '--desktop', str(desktop)],
                capture_output=True, text=True, stdin=subprocess.DEVNULL)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            log = desktop / 'SRW_Y_BRAKUJACE_log.txt'
            self.assertTrue(log.is_file())
            self.assertIn('SRW Y', log.read_text(encoding='utf-8'))


class CollectorTests(unittest.TestCase):
    def run_collector(self, streaming: Path, desktop: Path,
                      known: set[str] | None = None) -> dict:
        args = [sys.executable, str(KIT), '--streamingassets', str(streaming),
                '--desktop', str(desktop)]
        if known is not None:
            known_file = desktop / 'znane.json'
            known_file.parent.mkdir(parents=True, exist_ok=True)
            known_file.write_text(json.dumps({'schema': 1, 'bundles': {
                name: 'x' for name in known}}), encoding='utf-8')
            args += ['--known', str(known_file)]
        result = subprocess.run(
            args,
            capture_output=True, text=True, stdin=subprocess.DEVNULL, env={'PYTHONPATH': str(ROOT / 'tools'),
                                                 'PATH': '/usr/bin:/bin'})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = desktop / 'SRW_Y_BRAKUJACE_DANE' / 'manifest.json'
        self.assertTrue(manifest.is_file())
        return json.loads(manifest.read_text(encoding='utf-8'))

    def test_selects_by_address_and_skips_what_we_have(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            streaming = game_tree(base, addresses={
                'Assets/Datas/MissionData': 'aaaa',
                'Assets/Datas/MissionD4Data': 'bbbb',
                'MissionLayerList_main': 'cccc',
                'Assets/Localization/localization-LOCALE_ja-JP': 'cccc',
                'Assets/Datas/Scenario/jp/cse20_2000_0106300a_dlgev.lua.txt_ja-JP': 'dddd',
                'Assets/Datas/Scenario/en/cse20_2000_0106300a_dlgev.lua.txt_en-US': 'dddd',
                'AnniversaryStoryPreset': 'eeee',
                'Assets/Datas/Scenario/jp/cse20_0001_0000310a_dlgev.lua.txt_ja-JP': 'ffff',
            }, known={'aaaa'})
            scenes = base / 'sceny.json'
            scenes.write_text(json.dumps({'schema': 1,
                                          'scenes': ['cse20_2000_0106300a']}), encoding='utf-8')
            known = base / 'znane.json'
            known.write_text(json.dumps({'schema': 1, 'bundles': {'aaaa': 'x'}}),
                             encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(KIT), '--streamingassets', str(streaming),
                 '--desktop', str(base / 'Desktop'), '--sceny', str(scenes),
                 '--known', str(known)],
                capture_output=True, text=True, stdin=subprocess.DEVNULL)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((base / 'Desktop' / 'SRW_Y_BRAKUJACE_DANE' / 'manifest.json')
                                  .read_text(encoding='utf-8'))
            got = {item['path'].rsplit('/', 1)[-1] for item in manifest['bundles']}
            self.assertEqual(got, {'bbbb.bundle', 'cccc.bundle', 'dddd.bundle'})
            reasons = {item['path'].rsplit('/', 1)[-1]: item['reasons']
                       for item in manifest['bundles']}
            self.assertEqual(reasons['dddd.bundle'], ['scena bez JP: cse20_2000_0106300a'])
            self.assertIn('mission', reasons['bbbb.bundle'])
            self.assertEqual(manifest['problems'], [])

    def test_listing_and_catalogs_are_shipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            streaming = game_tree(base, addresses={'Assets/Datas/MissionData': 'aaaa'},
                                  known=set())
            manifest = self.run_collector(streaming, base / 'Desktop')
            target = base / 'Desktop' / 'SRW_Y_BRAKUJACE_DANE'
            self.assertTrue((target / 'lista.txt').is_file())
            self.assertIn('aaaa.bundle', (target / 'lista.txt').read_text(encoding='utf-8'))
            self.assertEqual(sorted(manifest['catalogs']),
                             ['aa__catalog.hash', 'aa__catalog.json', 'aa__settings.json'])
            self.assertTrue((base / 'Desktop' / 'SRW_Y_BRAKUJACE_DANE.zip').is_file())

    def test_scene_without_japanese_is_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            streaming = game_tree(base, addresses={
                'Assets/Datas/Scenario/en/cse20_0047_0202820a_sdemo.lua.txt_en-US': 'aaaa',
                'Assets/Datas/Scenario/jp/cse20_0047_0202820a_sdemo.lua.txt_ja-JP': 'bbbb',
                'Assets/Datas/Scenario/jp/cse20_0001_0000310a_sdemo.lua.txt_ja-JP': 'cccc',
            }, known=set())
            scenes = base / 'sceny.json'
            scenes.write_text(json.dumps({'schema': 1, 'scenes': ['cse20_0047_0202820a']}),
                              encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(KIT), '--streamingassets', str(streaming),
                 '--desktop', str(base / 'Desktop'), '--sceny', str(scenes)],
                capture_output=True, text=True, stdin=subprocess.DEVNULL)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((base / 'Desktop' / 'SRW_Y_BRAKUJACE_DANE' / 'manifest.json')
                                  .read_text(encoding='utf-8'))
            names = {item['path'].rsplit('/', 1)[-1]: item['reasons']
                     for item in manifest['bundles']}
            self.assertEqual(set(names), {'aaaa.bundle', 'bbbb.bundle'})
            self.assertEqual(names['bbbb.bundle'], ['scena bez JP: cse20_0047_0202820a'])

    def test_pack_catalog_is_read_too(self):
        """`catalog_<pack>.json` counts as a catalogue — missing it cost twenty missions."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            streaming = game_tree(base, addresses={'Assets/Datas/MissionData': 'aaaa'},
                                  known=set())
            keys = ['bbbb', 'Assets/Datas/MissionD4Data']
            entries = [(0, 1, -1, 0, 0, 0, 0), (0, 2, 0, 0, 0, 0, 0)]
            internal = ['{RP}\\StandaloneWindows64\\bbbb.bundle']
            catalog = fixture.build_catalog(keys, entries, [(0, [0]), (1, [1])])
            catalog['m_InternalIds'] = internal
            pack = streaming / 'BonusMission'
            pack.mkdir()
            (pack / 'bbbb.bundle').write_bytes(b'x' * 32)
            (pack / 'catalog_bonusmission.json').write_text(json.dumps(catalog),
                                                            encoding='utf-8')
            manifest = self.run_collector(streaming, base / 'Desktop')
            names = {item['path'] for item in manifest['bundles']}
            self.assertIn('BonusMission/bbbb.bundle', names)
            self.assertIn('BonusMission__catalog_bonusmission.json', manifest['catalogs'])

    def test_unknown_pack_is_included_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            streaming = game_tree(base, addresses={'Assets/Datas/MissionData': 'aaaa'},
                                  known=set())
            new_pack = streaming / 'Dlc9'
            new_pack.mkdir()
            (new_pack / 'abcd.bundle').write_bytes(b'x' * 16)
            manifest = self.run_collector(streaming, base / 'Desktop')
            names = {item['path'] for item in manifest['bundles']}
            self.assertIn('Dlc9/abcd.bundle', names)


if __name__ == '__main__':
    unittest.main()
