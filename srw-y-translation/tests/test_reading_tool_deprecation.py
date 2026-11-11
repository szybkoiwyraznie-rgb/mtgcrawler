"""Nieaktualne generatory czytanek muszą być oznaczone — inaczej wracają do użycia.

Realna wpadka z 2026-11-10: agent zbudował wydanie `tools/build_reading_y.py`,
pierwszym generatorem z początku projektu, i oddał właścicielowi skrypt pocięty na
rozdziały z zagnieżdżonym ZIP-em. Plik niczym się nie różnił od aktualnych, więc nic
nie zasygnalizowało pomyłki. Ten test pilnuje trzech rzeczy: że przestarzałe narzędzia
mówią o tym w pierwszej linii docstringa, że krzyczą na stderr przy uruchomieniu, i że
tabela w `AGENTS.md` wymienia jedne i drugie.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
AGENTS = ROOT / 'AGENTS.md'
MARKER = 'NIEAKTUALNE'

#: Narzędzia pierwszego wydania czytanek. `build_reading_y.py` zostaje mimo to w repo:
#: `Reader`, `jsonl`, `md` i `archive_bytes` są wspólną podstawą aktualnego potoku.
OBSOLETE = ('build_reading_y.py', 'build_reading_package.py', 'summarize_receipt.py')

#: Potok, z którego faktycznie powstają wydania.
CURRENT = ('rebuild_reading_pl8.py', 'rebuild_reading_pl2.py',
           'build_reading_pl2.py', 'build_reading_oe_style.py')


def docstring(name: str) -> str:
    text = ast.get_docstring(ast.parse((TOOLS / name).read_text(encoding='utf-8')))
    assert text, f'{name}: brak docstringa'
    return text


class DeprecationMarkerTests(unittest.TestCase):
    def test_nieaktualne_narzedzia_mowia_o_tym_w_pierwszej_linii(self):
        for name in OBSOLETE:
            with self.subTest(name):
                first = docstring(name).splitlines()[0]
                self.assertIn(MARKER, first,
                              f'{name}: pierwsza linia docstringa musi ostrzegać')

    def test_nieaktualne_narzedzia_wskazuja_aktualne_wejscie(self):
        """Samo „nieaktualne” nie wystarczy — agent musi wiedzieć, czego użyć."""
        for name in OBSOLETE:
            with self.subTest(name):
                self.assertIn('rebuild_reading_pl8.py', docstring(name))

    def test_aktualne_narzedzia_nie_sa_oznaczone(self):
        for name in CURRENT:
            with self.subTest(name):
                self.assertNotIn(MARKER, docstring(name).splitlines()[0],
                                 f'{name}: aktualne narzędzie oznaczone jako nieaktualne')

    def test_uruchomienie_nieaktualnego_narzedzia_ostrzega_na_stderr(self):
        """Ostrzeżenie ma lecieć przy wywołaniu CLI, nie przy imporcie modułu."""
        for name in OBSOLETE:
            with self.subTest(name):
                done = subprocess.run([sys.executable, str(TOOLS / name), '--help'],
                                      capture_output=True, text=True)
                self.assertIn(MARKER, done.stderr, f'{name}: brak ostrzeżenia na stderr')

    def test_import_modulu_nie_hałasuje(self):
        """`build_reading_y` jest importowany przez aktualny potok — cicho."""
        done = subprocess.run(
            [sys.executable, '-c', 'import sys; sys.path.insert(0, %r); import build_reading_y'
             % str(TOOLS)], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn(MARKER, done.stderr)

    def test_agents_md_wymienia_kazde_narzedzie_z_obu_list(self):
        text = AGENTS.read_text(encoding='utf-8')
        self.assertIn('Czytanki — które narzędzie jest aktualne', text)
        for name in OBSOLETE + CURRENT:
            with self.subTest(name):
                self.assertIn(name, text, f'{name}: brak w tabeli w AGENTS.md')

    def test_kazdy_builder_wydan_jest_sklasyfikowany(self):
        """Nowy generator musi trafić na jedną z list, zamiast zostać bez etykiety."""
        known = set(OBSOLETE) | set(CURRENT)
        builders = {p.name for p in TOOLS.glob('*reading*.py')
                    if re.match(r'(build|rebuild)_reading', p.name)}
        self.assertEqual(builders - known, set(),
                         'nieskalsyfikowany builder czytanek — dopisz go do OBSOLETE '
                         'albo CURRENT i do tabeli w AGENTS.md')


if __name__ == '__main__':
    unittest.main()
