"""Strażnik: wydanie PL3 odtwarza się z samego repozytorium, bez warstwy korekt.

Pytanie, na które odpowiada ten plik, brzmi: czy da się zbudować plan wydania
mając **tylko** to, co jest w gicie? Sprawdzamy cały łańcuch, nie jego koniec:
surowa zwrotka tłumacza (`translations/pl3/surowe/PL.zip`) jest wyrównywana do
wzorca v8, poprawki są na nią nakładane **raz** (`tools/normalize_return.py`),
a wynik musi być **bajt w bajt** równy zwrotce, z której buduje się paczkę
(`translations/pl3/PL`), i dawać plan identyczny z `translations/pl3/PLAN_PL3.json`.

Gdyby ktoś kiedyś „poprawił” zwrotkę wydania i zapomniał dopisać poprawki do
`CORRECTIONS.json`, ten test padnie — i to jest cała jego rola.

Manifest wiążący zwrotkę ze wzorcem nie jest wersjonowany (93 MB wierszy gry),
więc test odtwarza go tak, jak robi to `tools/bind_v8_return.py`: ze wzorca v8,
który w repo jest, i ze źródeł `data/s6-full`.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import bind_v8_return  # noqa: E402
import check_pl_template  # noqa: E402
import normalize_return  # noqa: E402
import pl_import  # noqa: E402
import realign_return  # noqa: E402

RETURN = ROOT / 'translations' / 'pl3'
RAW_ZIP = RETURN / 'surowe' / 'PL.zip'
CORRECTIONS = RETURN / 'surowe' / 'CORRECTIONS.json'
TEMPLATE = ROOT / 'translations' / 'template-v8'
SOURCE = ROOT / 'data' / 's6-full'


@pytest.fixture(scope='module')
def shipped() -> dict[str, str]:
    return pl_import.read_returns(RETURN / 'PL')


@pytest.fixture(scope='module')
def corrections() -> dict:
    return json.loads(CORRECTIONS.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def manifest() -> dict:
    template = check_pl_template.load_template(TEMPLATE)
    return bind_v8_return.bind(template, pl_import.read_returns(RETURN / 'PL'), SOURCE)


def test_raw_return_is_flat_zip_of_27_files():
    with zipfile.ZipFile(RAW_ZIP) as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
    assert len(names) == len(set(names)) == 27
    assert all(name.endswith('.md') and '/' not in name for name in names)


def test_corrections_are_pinned_to_the_realigned_return(tmp_path, corrections):
    raw = tmp_path / 'raw'
    raw.mkdir()
    with zipfile.ZipFile(RAW_ZIP) as archive:
        for item in archive.infolist():
            if not item.is_dir():
                (raw / item.filename).write_bytes(archive.read(item))
    aligned = tmp_path / 'aligned'
    realign_return.main(['--input', str(raw), '--output', str(aligned)])
    returned = pl_import.read_returns(aligned)
    assert len(returned) == 27
    hashes = {name: pl_import.digest(pl_import.canonical(text))
              for name, text in returned.items()}
    # dodatek nie należy do partii v8 (ma własny manifest), więc nie ma go w sumach
    assert set(corrections['input_sha256']) == set(hashes) - {'odcinek-99-dodatek.md'}
    assert hashes == {name: corrections['input_sha256'].get(name, hashes[name])
                      for name in hashes}
    assert len(corrections['entries']) == 24


def test_shipped_return_is_raw_return_plus_corrections(tmp_path, shipped, corrections,
                                                       manifest):
    raw = tmp_path / 'raw'
    raw.mkdir()
    with zipfile.ZipFile(RAW_ZIP) as archive:
        for item in archive.infolist():
            if not item.is_dir():
                (raw / item.filename).write_bytes(archive.read(item))
    aligned = tmp_path / 'aligned'
    realign_return.main(['--input', str(raw), '--output', str(aligned)])
    returned = pl_import.read_returns(aligned)
    result, changed = normalize_return.normalise(manifest, returned, corrections)
    touched = {entry['file'] for entry in corrections['entries']}
    assert changed == len(touched) == 4
    # plik dodatku jest przepisywany bez zmian — nie ma go we wzorcu v8
    assert set(result) - set(shipped) == {'odcinek-99-dodatek.md'}
    assert {name: result[name] for name in shipped} == shipped


def test_plan_from_repository_return_matches_the_shipped_plan(shipped, manifest):
    plan = pl_import.import_batch(manifest, shipped, source_dir=SOURCE)
    expected = json.loads((RETURN / 'PLAN_PL3.json').read_text(encoding='utf-8'))
    assert plan['tables'] == expected['tables']
    assert plan['scenes'] == expected['scenes']
    assert plan['accepted'] == expected['accepted'] == 85_311
    # cała warstwa korekt jest już w tekście: nic nie jest „stosowane” przy budowie
    assert plan['overrides_applied'] == 0
