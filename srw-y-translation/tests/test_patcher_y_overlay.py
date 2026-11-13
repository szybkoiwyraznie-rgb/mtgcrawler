"""Nakładka na pliki z moda 4K: instalacja, cofanie i los etykiet rozdzielczości.

Decyzja właściciela (2026-11-13): patch ma działać także wtedy, gdy gra ma już
mod 4K. Mod dostarcza pliki jako **gotowe kopie** (`2d69c099…bundle` różni się od
oryginału 1.4.0 o trzy wiersze), więc suma z indeksu nigdy się nie zgodzi i
stara weryfikacja odmawiała instalacji.

Ten plik pilnuje trzech rzeczy, z których każda była realnym błędem:

* `install(overlay=True)` przyjmuje plik z moda, a kopia zapasowa i stan
  instalacji opisują **ten** plik — `COFNIJ.bat` ma przywrócić moda, nie
  oryginał 1.4.0, którego w grze nigdy nie było (objaw: „plik zmieniony
  w trakcie budowy”, bo wpis dostawał sumę z indeksu),
* bez `--bez-nakladki` plik, który nie jest bundlem gry, jest odrzucany, a gra
  zostaje nietknięta — nakładka nie może zamienić w polski tekst czegokolwiek,
  co leży pod nazwą pliku,
* etykieta rozdzielczości podmieniona przez mod **zostaje** nietknięta; plan
  PL9 ma w tych wierszach tekst z 1.4.0, więc zapisanie go cofało podmianę
  moda (3840x2160 wracało jako 1920×1200).

Nic tu nie sięga po `local/`, Drive ani `/tmp`: „plik z moda” powstaje w teście
z kryptografii, która jest w repozytorium (ten sam szyfr, ta sama nazwa pliku).
"""

import hashlib
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import patcher_y as patcher
from apply_y_plan import table_edit
from s6_tables import table_header, walk_records
from srw_y_bundle_crypt import decrypt, encrypt

REL = 'aa/StandaloneWindows64/2d69c099bfdf0e252dabe84dbbba11df.bundle'
NAME = 'system_text_en-US'


def mod_file_bytes(name: str, tail: bytes = b'fake bundle body') -> bytes:
    """Plik „z moda”: szyfrogram, którego początek odszyfrowuje się do `UnityFS`.

    Dokładnie tego sprawdza patcher (`bundle_is_ours`), więc test przechodzi tę
    samą drogę co plik właściciela, bez 950 KB danych w repozytorium.
    """
    return encrypt(name, b'UnityFS\x00' + bytes(8) + tail)


def setup(tmp_path, file_bytes=None):
    root = tmp_path / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets'
    folder = root / 'aa' / 'StandaloneWindows64'
    folder.mkdir(parents=True)
    name = Path(REL).name
    data = mod_file_bytes(name) if file_bytes is None else file_bytes
    (folder / name).write_bytes(data)
    plan = {'schema': 1, 'tables': {}, 'scenes': {'a.lua': {'1#1': {'en': 'en', 'pl': 'pol'}}}}
    index = {'schema': 1, 'bundles': {REL: {
        'sha256': hashlib.sha256(b'original-1.4.0').hexdigest(),
        'tables': [],
        'scenes': [{'name': 'a.lua', 'lang': 'en', 'path_id': 1}]}}}
    return root, plan, index, data


def fake_builder(path, source, job, plan, **kwargs):
    return source + b'-patched', {'test': 1}


def test_overlay_install_accepts_mod_file_and_restores_it_exactly(tmp_path, monkeypatch):
    """Kopia i stan opisują plik z moda, a `restore` oddaje go co do bajtu."""
    monkeypatch.chdir(tmp_path)
    root, plan, index, mod_data = setup(tmp_path)
    state = tmp_path / 'state.json'
    result = patcher.install(root, plan, index, state, builder=fake_builder, overlay=True)
    target = patcher.target_for(root, REL)
    assert result['files'][0]['original'] == hashlib.sha256(mod_data).hexdigest()
    assert target.read_bytes() == mod_data + b'-patched'
    backup = Path(str(target) + patcher.BACKUP)
    assert backup.read_bytes() == mod_data
    assert '"overlay": true' in state.read_text(encoding='utf-8')
    assert patcher.restore(root, state, index) == 1
    assert target.read_bytes() == mod_data and not state.exists()


def test_strict_mode_still_refuses_the_mod_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root, plan, index, mod_data = setup(tmp_path)
    with pytest.raises(ValueError, match='inna wersja pliku'):
        patcher.install(root, plan, index, tmp_path / 'state.json',
                        builder=fake_builder, overlay=False)
    assert patcher.target_for(root, REL).read_bytes() == mod_data


def test_overlay_refuses_a_file_that_is_not_a_bundle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root, plan, index, _ = setup(tmp_path, file_bytes=b'not a bundle at all')
    target = patcher.target_for(root, REL)
    with pytest.raises(ValueError, match='nie pochodzi z gry ani z moda'):
        patcher.install(root, plan, index, tmp_path / 'state.json',
                        builder=fake_builder, overlay=True)
    assert target.read_bytes() == b'not a bundle at all'
    assert not (tmp_path / 'state.json').exists()


def test_bundle_is_ours_reads_the_decrypted_signature_only(tmp_path):
    name = Path(REL).name
    ours = tmp_path / name
    ours.write_bytes(mod_file_bytes(name))
    assert patcher.bundle_is_ours(ours, REL)
    assert decrypt(name, ours.read_bytes())[:7] == b'UnityFS'
    # Ten sam szyfrogram pod inną nazwą to inny klucz — i już nie „nasz” plik.
    other = tmp_path / 'inny.bundle'
    other.write_bytes(ours.read_bytes())
    assert not patcher.bundle_is_ours(other, 'aa/StandaloneWindows64/inny.bundle')


def test_check_is_read_only_in_overlay_mode(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root, plan, index, mod_data = setup(tmp_path)
    patcher.check(root, plan, index, builder=fake_builder, overlay=True)
    assert patcher.target_for(root, REL).read_bytes() == mod_data


# ------------------------------------------------------- etykiety rozdzielczości
LABEL_KEYS = ['009a8dad:1d60b014', '009a8dad:1d60b015', '009a8dad:1d60b016']
MOD_LABELS = ['3840x2160', '2560x1440', '1920x1080']
PLAN_LABELS = ['1920×1200', '1920×1080', '1280×800']


def labels_table(keys: list[str], texts: list[str], name: str = NAME) -> bytes:
    """Tabela w układzie gry, z **podanymi** kluczami (layout jak `s6_tables`)."""
    out = bytearray(b'\x00' * 28 + struct.pack('<I', len(name)) + name.encode())
    out += bytes(-len(out) % 4)
    out += struct.pack('<I', 5) + b'en-US'
    out += bytes(-len(out) % 4)
    out += struct.pack('<I', 2) + bytes(8) + struct.pack('<I', 0)
    out += struct.pack('<I', len(texts))
    for key, text in zip(keys, texts):
        high, low = (int(part, 16) for part in key.split(':'))
        encoded = text.encode('utf-8')
        out += struct.pack('<III', low, high, len(encoded)) + encoded
        out += bytes(-len(out) % 4) + bytes(4)
    return bytes(out) + struct.pack('<II', 2, 0)


def plan_rows(pairs) -> dict:
    return {key: {'jp': '', 'en': en, 'pl': pl} for key, en, pl in pairs}


def texts_of(raw: bytes, name: str = NAME) -> list[str]:
    start, count = table_header(raw, name)
    return [row['text'] for row in walk_records(raw, start, count)[0]]


def test_overlay_keeps_resolution_labels_the_mod_already_changed():
    """Wiersz z etykietą 4K w grze nie dostaje polskiego tekstu z planu.

    Plan PL9 trzyma tam tekst 1.4.0 (`1920×1200`), a mod ma `3840x2160`.
    Zapisanie planu cofało podmianę moda — sprawdzone 2026-11-13 na prawdziwym
    pliku `2d69c099…bundle` z moda.
    """
    rows = plan_rows(zip(LABEL_KEYS, PLAN_LABELS, PLAN_LABELS))
    raw = labels_table(LABEL_KEYS, MOD_LABELS)
    report = {}
    new, count = table_edit(NAME, raw, rows, 'en', report=report, overlay=True)
    assert texts_of(new) == MOD_LABELS, 'etykiety z moda zostały nadpisane tekstem z planu'
    assert count == 0
    assert report['etykieta_moda'][0]['wiersze'][0]['gra'] == MOD_LABELS[0]


def test_without_overlay_the_label_rows_still_wait_for_a_matching_source():
    """Poza nakładką etykieta 4K to zwykły rozjazd — nic nie jest zapisywane."""
    rows = plan_rows(zip(LABEL_KEYS, PLAN_LABELS, PLAN_LABELS))
    report = {}
    new, count = table_edit(NAME, labels_table(LABEL_KEYS, MOD_LABELS), rows, 'en',
                            report=report, overlay=False)
    assert texts_of(new) == MOD_LABELS and count == 0
    assert len(report['inny_tekst']) == 3 and 'etykieta_moda' not in report


def test_overlay_still_reports_a_real_divergence_as_divergence():
    """Tekst inny niż plan i niebędący etykietą 4K to rozjazd, nie zapis."""
    rows = plan_rows([(LABEL_KEYS[0], 'Hello', 'Cześć')])
    report = {}
    new, count = table_edit(NAME, labels_table(LABEL_KEYS[:1], ['Something else']),
                            rows, 'en', report=report, overlay=True)
    assert texts_of(new) == ['Something else'] and count == 0
    assert report['inny_tekst'][0]['gra'] == 'Something else'
    assert 'etykieta_moda' not in report


def test_overlay_writes_rows_the_mod_did_not_touch():
    rows = plan_rows([(LABEL_KEYS[0], 'Hello', 'Cześć')])
    new, count = table_edit(NAME, labels_table(LABEL_KEYS[:1], ['Hello']),
                            rows, 'en', overlay=True)
    assert count == 1 and texts_of(new) == ['Cześć']
