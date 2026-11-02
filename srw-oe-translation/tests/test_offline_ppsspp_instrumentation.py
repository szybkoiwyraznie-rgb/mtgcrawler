"""Compile the offline instrumentation against synthetic controller/memory stubs."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HEADER = Path(__file__).resolve().parents[1] / 'research/ppsspp-headless/OfflineResearch.h'


@unittest.skipUnless(shutil.which('c++'), 'C++ compiler is unavailable')
class InstrumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        d = Path(cls.temp.name)
        (d / 'Core/HLE').mkdir(parents=True)
        (d / 'Core/HLE/sceCtrl.h').write_text('''
#pragma once
#define CTRL_CIRCLE 0x2000
#define CTRL_CROSS 0x4000
#define CTRL_TRIANGLE 0x1000
#define CTRL_SQUARE 0x8000
#define CTRL_UP 0x0010
#define CTRL_DOWN 0x0040
#define CTRL_LEFT 0x0080
#define CTRL_RIGHT 0x0020
#define CTRL_START 0x0008
#define CTRL_SELECT 0x0001
#define CTRL_LTRIGGER 0x0100
#define CTRL_RTRIGGER 0x0200
void __CtrlUpdateButtons(unsigned int a, unsigned int b);
''')
        (d / 'Core/MemMap.h').write_text('''
#pragma once
namespace Memory {
inline bool IsValidRange(unsigned int, unsigned int) { return true; }
inline const unsigned char *GetPointerUnchecked(unsigned int) {
    static unsigned char bytes[512*272*2]{}; return bytes;
}
}
''')
        (d / 'test.cpp').write_text('''
#include <cstdio>
static double now = 0;
double time_now_d() { return now; }
void __CtrlUpdateButtons(unsigned int a, unsigned int b) { std::printf("%x %x\\n",a,b); }
#include "OfflineResearch.h"
int main() {
    OfflineResearch r; r.Start();
    for (double t : {0.0, 0.3, 0.7, 2.0}) { now = t; r.Step(); }
    r.Stop();
}
''')
        shutil.copyfile(HEADER, d / 'OfflineResearch.h')
        cls.binary = d / 'test'
        subprocess.run(['c++', '-std=c++17', '-I', str(d), str(d / 'test.cpp'), '-o', str(cls.binary)], check=True)
        cls.root = d

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def environment(self):
        env = dict(os.environ)
        env.pop('PPSSPP_RESEARCH_SCHEDULE', None)
        env.pop('PPSSPP_RESEARCH_VRAM_PREFIX', None)
        return env

    def test_disabled_is_inert(self):
        out = subprocess.run([self.binary], env=self.environment(), capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout, '')
        self.assertEqual(out.stderr, '')

    def test_schedule_capture_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(dir=self.root) as temp:
            d = Path(temp)
            plan = d / 'plan.txt'
            plan.write_text('0.2 2000 0.4\n')
            env = self.environment()
            env['PPSSPP_RESEARCH_SCHEDULE'] = str(plan)
            env['PPSSPP_RESEARCH_VRAM_PREFIX'] = str(d / 'vram')
            out = subprocess.run([self.binary], env=env, capture_output=True, text=True, check=True)
            self.assertEqual(out.stdout.splitlines(), ['2000 0', '0 2000'])
            files = list(d.glob('*.raw'))
            self.assertEqual(len(files), 4)
            self.assertTrue(all(f.stat().st_size == 512 * 272 * 2 for f in files))
            again = subprocess.run([self.binary], env=env, capture_output=True, text=True)
            self.assertEqual(again.returncode, 2)
            self.assertIn('cannot create new VRAM output', again.stderr)
            self.assertEqual(len(list(d.glob('*.raw'))), 4)

    def test_rejects_bad_or_overlapping_schedule(self):
        with tempfile.TemporaryDirectory(dir=self.root) as temp:
            plan = Path(temp) / 'plan.txt'
            env = self.environment()
            env['PPSSPP_RESEARCH_SCHEDULE'] = str(plan)
            for contents in ('0.2 100000 0.4\n', '0.2 2000 1\n0.3 4000 1\n', 'nan 2000 1\n', '0.2 2000 1 bad\n'):
                with self.subTest(contents=contents):
                    plan.write_text(contents)
                    out = subprocess.run([self.binary], env=env, capture_output=True, text=True)
                    self.assertEqual(out.returncode, 2)
                    self.assertIn('invalid or overlapping', out.stderr)


if __name__ == '__main__':
    unittest.main()
