"""Reading-archive README/plural helpers, the deployment-title refresh and the
repository-only build guarantee."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import build_reading_archive as A  # noqa: E402


class ArchiveReadmeTests(unittest.TestCase):
    def rows(self, stats):
        return [{'episode': 0, 'name': 'srwoe_episode_00_PL.md', 'sections': 4,
                 'prose_total': stats, 'shown_unique': stats, 'aliased': 0,
                 'verified_text_spans': stats, 'bytes': 100, 'sha256': '0' * 64}]

    def test_carried_member_is_listed_separately_and_keeps_totals_honest(self):
        carried = [{'name': 'srwoe_episode_34_PL.md', 'reason': 'powód testowy'}]
        text = A.readme('v9.9', self.rows(10) + self.rows(None), {'prose_total': 10,
                       'shown_unique': 10, 'aliased': 0, 'verified_text_spans': 10},
                       None, carried)
        self.assertIn('Przeniesione bez zmian', text)
        self.assertIn('powód testowy', text)
        # the carried row has no restated prose numbers
        self.assertIn('| 00 | `srwoe_episode_00_PL.md` | 4 | 10 | 10 | 0 |', text)
        self.assertIn('| 00 | `srwoe_episode_00_PL.md` | 4 | — | — | 0 |', text)
        self.assertIn('1 plik przeniesiono bez zmian', text)
        self.assertNotIn('20 / 20', text)

    def test_polish_plural_forms(self):
        self.assertEqual(A.plural(1, 'epizod', 'epizody', 'epizodów'), 'epizod')
        self.assertEqual(A.plural(3, 'epizod', 'epizody', 'epizodów'), 'epizody')
        self.assertEqual(A.plural(12, 'epizod', 'epizody', 'epizodów'), 'epizodów')
        self.assertEqual(A.plural(34, 'epizod', 'epizody', 'epizodów'), 'epizody')


class DeploymentTitleRefreshTests(unittest.TestCase):
    SOURCE = (
        '# Rozstawienia\n\n'
        '### Odcinek 2 — Długi tytuł misji (`DL102_11`)\n\ntreść\n\n'
        '### Odcinek 9 — Krótki tytuł (`DL209_12`)\n\ntreść\n'
    )

    def plan(self, tmp: Path) -> Path:
        plan = {'changes': [
            {'id': 'mission_title:config00.cpk/milstP00.bin:r14:title',
             'before': 'Ep. 2: Długi tytuł misji', 'after': 'Ep. 2: Krótki'},
            {'id': 'mission_note:eventP00.cpk/DL102_11_ext.dat:r0:title',
             'before': 'Ep. 2\nDługi tytuł misji', 'after': 'Ep. 2\nKrótki'},
        ]}
        path = tmp / 'plan.json'
        path.write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
        return path

    def run_tool(self, source: Path, pin: str, plan: Path, out: Path):
        return subprocess.run(
            [sys.executable, str(ROOT / 'tools/refresh_mission_deployments_titles.py'),
             '--source', str(source), '--pin-sha256', pin, '--plan', str(plan),
             '--out', str(out)], capture_output=True, text=True)

    def test_only_heading_lines_change_and_pin_is_enforced(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            source = tmp / 'deployments.md'
            source.write_text(self.SOURCE, encoding='utf-8')
            pin = hashlib.sha256(self.SOURCE.encode()).hexdigest()
            out = tmp / 'out.md'
            result = self.run_tool(source, pin, self.plan(tmp), out)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                out.read_text(encoding='utf-8'),
                self.SOURCE.replace('Długi tytuł misji (`DL102_11`)', 'Krótki (`DL102_11`)'))
            bad = self.run_tool(source, '0' * 64, self.plan(tmp), tmp / 'bad.md')
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('unexpected source bytes', bad.stderr + bad.stdout)
            self.assertFalse((tmp / 'bad.md').exists())


class RepositoryOnlyBuildTests(unittest.TestCase):
    """The v4.5 delivery must rebuild every episode from repository inputs alone.

    The owner rejected a build that depends on Drive: the 35 English reader
    editions are committed, and episode 34 is regenerated like all the others.
    These tests fail if a future delivery reintroduces an out-of-repo input or a
    carried-over member.
    """

    RECEIPT = ROOT / 'docs/reading-script/polish/PL5_v4.5_reading.delivery.json'
    REFS = ROOT / 'docs/reading-script/english-reference'

    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(cls.RECEIPT.read_text(encoding='utf-8'))

    def test_no_carried_member_is_delivered(self):
        self.assertFalse(self.receipt.get('carried_members'))
        self.assertEqual(self.receipt['english_reference']['files'], '35/35 '
                         'srwoe_episode_00.md .. srwoe_episode_34.md')
        self.assertEqual(self.receipt['english_reference']['verified_against_plan_reference_sha256'],
                         '35/35')
        episodes = self.receipt['changes_vs_v4_3']['changed_episodes'] + \
            self.receipt['changes_vs_v4_3']['unchanged_episodes']
        self.assertEqual(sorted(set(episodes)), [f'{n:02d}' for n in range(35)],
                         'all 35 episodes must be rebuilt from the package')
        self.assertIn('34', self.receipt['changes_vs_v4_3']['changed_episodes'])

    def test_english_references_live_in_the_repository(self):
        manifest = json.loads((self.REFS / 'references.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['files']), 35)
        for name, meta in manifest['files'].items():
            data = (self.REFS / name).read_bytes()
            self.assertEqual(len(data), meta['bytes'], name)
            self.assertEqual(hashlib.sha256(data).hexdigest(), meta['sha256'], name)
        self.assertFalse(self.receipt['english_reference']['external_input_required'])
        self.assertTrue(self.receipt['english_reference']['directory']
                        .startswith('docs/reading-script/english-reference'))

    def test_plans_are_pinned_to_the_committed_references(self):
        manifest = json.loads((self.REFS / 'references.json').read_text(encoding='utf-8'))
        plans = ROOT / 'docs/reading-script/polish'
        for number in range(35):
            plan = json.loads((plans / f'episode_{number:02d}.json').read_text(encoding='utf-8'))
            name = f'srwoe_episode_{number:02d}.md'
            self.assertEqual(plan['reference_sha256'], manifest['files'][name]['sha256'],
                             f'{name} pin drifted from the committed reference')

    def test_builder_verifies_the_repository_reference_set(self):
        source = (ROOT / 'tools/build_polish_reading_editions.py').read_text(encoding='utf-8')
        self.assertIn("project / 'docs/reading-script/english-reference'", source)
        self.assertIn("manifest_path = args.references / 'references.json'", source)
        self.assertIn('--skip-reference-manifest-check', source)

    def test_receipt_archive_matches_the_local_zip_when_present(self):
        archive = ROOT / 'local/dist_reading_v4_5/srwoe_reading_PL_00-34.zip'
        if not archive.exists():
            self.skipTest('local archive not kept in the checkout')
        data = archive.read_bytes()
        self.assertEqual(len(data), self.receipt['archive']['bytes'])
        self.assertEqual(hashlib.sha256(data).hexdigest(), self.receipt['archive']['sha256'])
        self.assertTrue(self.receipt['archive']['download_back_byte_identical'])
        self.assertEqual(self.receipt['archive']['drive_file_id'],
                         '1zEOrnN0mwgRQv4Y1T-hBlXMxTmt_yKjv')


if __name__ == '__main__':
    unittest.main()
