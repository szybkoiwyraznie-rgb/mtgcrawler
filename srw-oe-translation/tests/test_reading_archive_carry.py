"""Reading-archive carry support and the deployment-title refresh helper."""
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


class CarriedEpisodeGuardTests(unittest.TestCase):
    """A carried episode is only acceptable when a rebuild provably cannot change it."""

    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((ROOT / 'docs/reading-script/polish/PL5_v4.5_reading.delivery.json')
                                 .read_text(encoding='utf-8'))

    def test_carried_episode_references_none_of_the_changed_rows(self):
        self.assertEqual(len(self.receipt['carried_members']), 1)
        carried = self.receipt['carried_members'][0]
        guard = carried['guard']
        plan = json.loads((ROOT / guard['episode_plan']).read_text(encoding='utf-8'))
        rows = {b['row'] for b in plan['blocks'] if 'row' in b}
        mission_rows = {b['mission_row'] for b in plan['blocks'] if 'mission_row' in b}
        self.assertEqual((len(rows), len(mission_rows)),
                         (guard['episode_plan_rows'], guard['episode_plan_mission_rows']))
        total = 0
        for name in guard['checked_change_plans']:
            changes = json.loads((ROOT / name).read_text(encoding='utf-8'))['changes']
            total += len(changes)
            inside = [c['id'] for c in changes if c['id'] in rows or c['id'] in mission_rows]
            self.assertEqual(inside, [], f'{name} touches the carried episode')
        self.assertEqual(total, guard['changed_rows_total'])
        self.assertEqual(guard['changed_rows_inside_episode'], 0)

    def test_carried_member_is_the_previously_delivered_bytes(self):
        carried = self.receipt['carried_members'][0]
        self.assertEqual(carried['sha256'], carried['guard']['previous_delivery_sha256'])
        self.assertEqual(carried['name'], 'srwoe_episode_34_PL.md')


if __name__ == '__main__':
    unittest.main()
