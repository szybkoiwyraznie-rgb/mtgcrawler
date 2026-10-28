"""Polish written into UI prefabs — the text that is not in any table.

Only repo-owned data is checked here: the committed translation manifest must
say exactly what each patch replaces. Tests that needed the owner's private
title-screen bundle were removed (their inputs live only on Drive).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))


def test_translation_file_covers_every_wanted_string():
    """Each entry must say what it replaces — a patch matched by position is a bug."""
    import json
    data = json.loads((HERE / 'translations' / 'ui_test_pl.json').read_text(encoding='utf-8'))
    for stem, spec in data['bundles'].items():
        assert len(stem) == 32 and all(c in '0123456789abcdef' for c in stem)
        for row in spec['strings']:
            assert row['old'] and row['pl']
            assert row['old'] != row['pl']
            # the replacement is a UI label; a line break belongs to the original only
            assert row['pl'].endswith('\n') == row['old'].endswith('\n')
