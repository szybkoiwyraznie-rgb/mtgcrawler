"""Strażnik kompletności: wszystko, czego patch potrzebuje, leży w repozytorium.

Ten test istnieje, bo przez trzy sesje wracał ten sam problem: agent twierdził,
że „brakuje plików gry / indeksu / zwrotki”, i przez to patch wychodził niepełny
albo trzeba było pytać właściciela o rzeczy, które już dawno były w repo.

Sprawdza, że w gicie są:

* źródła gry (`data/s6-full/`: `scenario.jsonl`, `tables.jsonl` + limity/grupy),
* indeks bundli (`data/game_text_bundle_index.json`),
* wzorzec v8 (`translations/template-v8/`),
* zwrotka PL3 w wersji **wydanej** (`translations/pl3/PL/`) i surowej
  (`translations/pl3/surowe/PL.zip` + `CORRECTIONS.json`),
* dodatek v8.1 z własnym manifestem (`translations/pl3/appendix/`),
* plan wydania PL7 = cała zwrotka (`translations/pl7/PLAN_PL7.json`),
* narzędzia wydania: `one_click_patch.py`, `build_y_release.py`,
  `pl_import.py`, `bind_v8_return.py`, `apply_y_plan.py`, `patcher_y.py`.

Jeśli czegoś brakuje, test mówi **co** i **czym** to odtworzyć — zamiast zostawiać
to do zgadywania następnej sesji.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
TRANSLATIONS = ROOT / 'translations'
TOOLS = ROOT / 'tools'


def tracked(path: Path) -> bool:
    """Czy plik jest w gicie (a nie tylko na dysku)."""
    result = subprocess.run(['git', 'ls-files', '--error-unmatch', str(path)],
                            cwd=ROOT, capture_output=True, text=True)
    return result.returncode == 0


def test_game_sources_are_committed():
    for name in ('scenario.jsonl', 'tables.jsonl'):
        path = DATA / 's6-full' / name
        assert path.is_file(), f'brak źródła gry: {path.relative_to(ROOT)}'
        assert tracked(path), f'{path.relative_to(ROOT)} jest poza gitem'
    # limity pól i grupy powtórzeń są w `data/`, nie w `s6-full` — importer czyta je stąd
    for name in ('limits_y.json', 'package_appendix_y.json'):
        path = DATA / name
        assert tracked(path), f'{path.relative_to(ROOT)} musi być w gicie'
    assert (DATA / 's6-extra').is_dir(), 'brak data/s6-extra (wiersze dodane później)'


def test_bundle_index_is_committed():
    path = DATA / 'game_text_bundle_index.json'
    assert tracked(path), 'indeks bundli musi być w gicie — bez niego patch nie wie, gdzie pisać'
    index = json.loads(path.read_text(encoding='utf-8'))
    assert index['schema'] == 1 and index['bundles'], 'pusty indeks bundli'


def test_template_v8_is_committed():
    sceny = sorted((TRANSLATIONS / 'template-v8' / 'sceny').glob('*.md'))
    widoki = sorted((TRANSLATIONS / 'template-v8' / 'widoki').glob('*.md'))
    assert len(sceny) == 39 and len(widoki) == 10, 'niepełny wzorzec v8'
    assert all(tracked(path) for path in sceny + widoki), 'wzorzec v8 poza gitem'


def test_pl3_return_is_committed_in_both_forms():
    shipped = sorted((TRANSLATIONS / 'pl3' / 'PL').glob('*.md'))
    assert len(shipped) == 26, 'zwrotka wydania PL3 powinna mieć 26 plików v8'
    assert all(tracked(path) for path in shipped)
    assert tracked(TRANSLATIONS / 'pl3' / 'surowe' / 'PL.zip'), 'brak surowej zwrotki tłumacza'
    assert tracked(TRANSLATIONS / 'pl3' / 'surowe' / 'CORRECTIONS.json')


def test_appendix_is_committed_with_its_manifest():
    folder = TRANSLATIONS / 'pl3' / 'appendix'
    assert tracked(folder / 'odcinek-99-dodatek.md')
    manifest = json.loads((folder / 'import_manifest.json').read_text(encoding='utf-8'))
    assert manifest['schema'] == 2 and 'odcinek-99-dodatek.md' in manifest['files']


def test_pl7_plan_covers_the_whole_return():
    plan = json.loads((TRANSLATIONS / 'pl7' / 'PLAN_PL7.json').read_text(encoding='utf-8'))
    assert tracked(TRANSLATIONS / 'pl7' / 'PLAN_PL7.json')
    assert plan['accepted'] == 85_610
    # dodatek (299 rekordów, 7 scen) musi być w planie, a nie tylko w plikach
    assert 'cse20_3738_0999900a_sdemo.lua' in plan['scenes']
    assert plan['scenes']['cse20_3738_0999900a_sdemo.lua'], 'scena dodatku bez rekordów'


def test_release_tools_are_committed():
    for name in ('one_click_patch.py', 'build_y_release.py', 'pl_import.py',
                 'bind_v8_return.py', 'apply_y_plan.py', 'patcher_y.py',
                 'realign_return.py', 'normalize_return.py', 'check_pl_template.py'):
        path = TOOLS / name
        assert path.is_file(), f'brak narzędzia: {name}'
        assert tracked(path), f'tools/{name} poza gitem'
