#!/usr/bin/env python3
"""Owner-side tool: re-break the Polish skill and spirit descriptions in place.

Round 6 (2026-11-09). The Data Help screen does not wrap text: the `\\n` bytes in
the string *are* the lines the player sees. The shipped patch wrote those strings as
one long line, so they run out of the frame. `tools/wrap_like_en.py` already
re-broke **804** entries of `03_umiejetnosci.md` to match the English line count;
this script puts exactly those strings into the game's own tables.

What it does, per bundle named in `lamanie_rows.json` (five files, pinned — nothing
on the disk is searched):

1. read the file, decrypt it, open the table objects it is supposed to contain;
2. for every listed row check the **current** text and accept only two states:
   the Japanese original (the fix runs before the main patch) or the one-line
   Polish the patch wrote (the normal case) — anything else is reported, never
   overwritten;
3. re-emit each table (`s6_write.encode_table`), rebuild the bundle
   (`srw_y_rebuild.rebuild_plain`, which proves every other object came back byte
   for byte), encrypt, keep a `.srwy-lamanie-original.bak` beside it, then read the
   result back and confirm the new texts are there.

`restore` puts the backup back only if the file still matches what this script
wrote — so a half-finished install can always be undone, and a file the owner
already restored (or that another kit changed afterwards) is never clobbered.

    python lamanie_opisow.py install
    python lamanie_opisow.py restore

Both actions write `RAPORT_LAMANIE_LINII.txt` and remember what they changed in
`STAN_LAMANIE.json`, both next to this file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import UnityPy  # noqa: E402

from cipher_fast import plain_of  # noqa: E402
from s6_tables import split_locale, table_header, walk_records  # noqa: E402
from s6_write import encode_table  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402
from srw_y_rebuild import rebuild_plain  # noqa: E402

#: In the kit the row list sits next to this script; in the workshop it is the
#: committed `data/lamanie_linii_rows.json`.
ROWS = HERE / 'lamanie_rows.json'
if not ROWS.is_file():
    ROWS = HERE.parent / 'data' / 'lamanie_linii_rows.json'
STATE = HERE / 'STAN_LAMANIE.json'
REPORT = HERE / 'RAPORT_LAMANIE_LINII.txt'
BACKUP = '.srwy-lamanie-original.bak'
GAME_DATA = 'SUPER ROBOT WARS Y_Data'
AA = 'StreamingAssets/aa/StandaloneWindows64'
STAMP = 'lamanie-linii-1'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def log(lines: list[str], text: str) -> None:
    print(text, flush=True)
    lines.append(text)


def check_game_stopped() -> None:
    if os.name != 'nt':
        return
    result = subprocess.run(['tasklist', '/fo', 'csv', '/nh'], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('nie można sprawdzić procesów; zamknij grę i spróbuj ponownie')
    for row in result.stdout.splitlines():
        if 'super robot wars y' in row.lower():
            raise ValueError('gra jest uruchomiona — zamknij ją przed poprawką lub cofnięciem')


def find_game() -> Path:
    here = Path.cwd()
    if (here / GAME_DATA / AA).is_dir():
        return here
    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
        for suffix in ('Games/SUPER ROBOT WARS Y', 'Gry/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SRWY',
                       'Program Files/Steam/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SUPER ROBOT WARS Y',
                       'Program Files/Steam/steamapps/common/SUPER ROBOT WARS Y'):
            candidate = Path(f'{letter}:/{suffix}')
            if (candidate / GAME_DATA).is_dir():
                print(f'Znaleziono grę: {candidate}')
                return candidate
    return Path(input('Podaj folder gry SUPER ROBOT WARS Y: ').strip().strip('"'))


def load_rows() -> dict:
    return json.loads(ROWS.read_text(encoding='utf8'))


def accepted(row: dict) -> set[str]:
    """The only texts a row may hold before we write: JP original or the flat Polish."""
    return {text for text in (row['jp'], row['flat'], row['pl']) if text}


def table_edits(name: str, raw: bytes, rows: list[dict]) -> tuple[bytes, Counter, list[dict]]:
    """Rebuild one table object; return the new bytes, counters and any conflicts."""
    start, count = table_header(raw, name)
    before, _ = walk_records(raw, start, count)
    existing = {record['key']: record['text'] for record in before}
    replacements, counts, conflicts = {}, Counter(), []
    for row in rows:
        text = existing.get(row['key'])
        if text is None:
            conflicts.append({'table': name, 'key': row['key'], 'problem': 'brak wiersza'})
            continue
        if text == row['pl']:
            counts['juz_poprawne'] += 1
            continue
        if text not in accepted(row):
            conflicts.append({'table': name, 'key': row['key'],
                              'problem': 'inny tekst w grze', 'found': text[:60]})
            continue
        replacements[row['key']] = row['pl']
        counts['poprawione'] += 1
    if not replacements:
        return raw, counts, conflicts
    new_raw = encode_table(raw, replacements)
    start_after, count_after = table_header(new_raw, name)
    after, _ = walk_records(new_raw, start_after, count_after)
    if count_after != count or any(
            record['text'] != replacements.get(record['key'], existing[record['key']])
            for record in after):
        raise ValueError(f'{name}: kontrola zapisu tabeli nie przeszła')
    return new_raw, counts, conflicts


def patch_bundle(path: Path, rows: list[dict], lines: list[str]) -> dict:
    """Apply one bundle; returns a state entry for `STAN_LAMANIE.json`."""
    original = path.read_bytes()
    stems = Counter()
    plain = plain_of(path)
    env = UnityPy.load(plain)
    objects = {obj.path_id: obj for obj in env.objects}
    wanted: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        wanted[row['table']].append(row)
    edits, counts, conflicts = {}, Counter(), []
    for table, table_items in sorted(wanted.items()):
        matches = []
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            if (obj.read().m_Name or '') == table:
                matches.append(obj)
        if len(matches) != 1:
            raise ValueError(f'{path.name}: tabela {table} występuje {len(matches)} raz(y)')
        obj = matches[0]
        raw = obj.get_raw_data()
        new_raw, table_counts, table_conflicts = table_edits(table, raw, table_items)
        counts.update(table_counts)
        conflicts += table_conflicts
        if new_raw is not raw:
            edits[obj.path_id] = new_raw
        stems[table] += table_counts['poprawione']
    if not edits:
        log(lines, f'   {path.name}: nic do poprawienia ({counts["juz_poprawne"]} już poprawne)')
        return {'changed': False, 'sha256_backup': sha256(original),
                'sha256_after': sha256(original), 'rows': dict(stems)}

    # A second pass must not overwrite the record of the pristine file: the .bak beside
    # a bundle always holds the game's own original, so its hash is what "backup" means
    # (the same trap `tlo_bazy2.py` hit — `sha256_before` there was the previous pass).
    backup = path.with_name(path.name + BACKUP)
    if not backup.is_file():
        backup.write_bytes(original)
        created_backup = True
        backup_hash = sha256(original)
    else:
        created_backup = False
        backup_hash = sha256(backup.read_bytes())
    rebuilt, _ = rebuild_plain(path.name, plain, edits)
    out = encrypt(path.name, rebuilt)
    if decrypt(path.name, out) != rebuilt:
        raise ValueError(f'{path.name}: szyfrowanie nie odtwarza zbudowanego pliku')
    back = {obj.path_id: obj.get_raw_data() for obj in UnityPy.load(rebuilt).objects
            if obj.path_id in edits}
    if back != edits:
        raise ValueError(f'{path.name}: odczyt poprawionych tabel niezgodny z zapisem')
    path.write_bytes(out)
    log(lines, f'   {path.name}: poprawione wiersze {sum(stems.values())}, '
               f'{len(stems)} tabel, rozmiar {len(original)} -> {len(out)} B'
               + ('' if created_backup else ' (kopia .bak już była — trzymam oryginał)'))
    for conflict in conflicts:
        log(lines, f'      POMINIĘTY {conflict["table"]} {conflict["key"]}: {conflict["problem"]}'
                   + (f' — „{conflict["found"]}”' if conflict.get('found') else ''))
    return {'changed': True, 'sha256_backup': backup_hash, 'sha256_after': sha256(out),
            'rows': dict(stems), 'conflicts': conflicts,
            'size_before': len(original), 'size_after': len(out)}


def install(game: Path, lines: list[str]) -> int:
    payload = load_rows()
    streaming = game / GAME_DATA / AA
    if not streaming.is_dir():
        raise ValueError(f'nie ma folderu {streaming}')
    per_bundle: dict[str, list[dict]] = defaultdict(list)
    for row in payload['rows']:
        per_bundle[row['bundle']].append(row)
    state = {'schema': 1, 'stamp': STAMP,
             'when': time.strftime('%Y-%m-%d %H:%M:%S'), 'bundles': {}}
    missing = [name for name in per_bundle if not (streaming / name).is_file()]
    if missing:
        raise ValueError('brak w grze plików: ' + ', '.join(missing))
    log(lines, f'Poprawiam {len(payload["rows"])} wierszy w {len(per_bundle)} plikach.')
    for name in sorted(per_bundle):
        log(lines, f' {name}')
        entry = patch_bundle(streaming / name, per_bundle[name], lines)
        state['bundles'][name] = entry
        if entry['changed']:
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf8')
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf8')
    changed = sum(1 for entry in state['bundles'].values() if entry['changed'])
    fixed = sum(sum(entry['rows'].values()) for entry in state['bundles'].values())
    log(lines, f'GOTOWE. Plików zmienionych: {changed}; wierszy poprawionych: {fixed}.')
    if changed:
        log(lines, 'Wejdź w ekran Database i sprawdź opisy umiejętności. '
                   'Cofnięcie: COFNIJ.bat z tego folderu.')
    else:
        log(lines, 'Nic nie było do poprawienia — opisy są już połamane.')
    return 0


def restore(lines: list[str]) -> int:
    if not STATE.is_file():
        raise ValueError(f'nie ma {STATE.name} — nie wiem, co przywrócić; '
                         'uruchom POPRAW.bat i dopiero potem cofaj')
    state = json.loads(STATE.read_text(encoding='utf8'))
    restored = skipped = 0
    for name, entry in sorted(state['bundles'].items()):
        path = Path(entry.get('path') or '')
        if not path.is_file():
            candidates = list(Path.cwd().rglob(name))
            if not candidates:
                raise ValueError(f'nie znajduję {name}; uruchom COFNIJ.bat z folderu gry')
            path = candidates[0]
        backup = path.with_name(path.name + BACKUP)
        if not entry.get('changed'):
            log(lines, f'   {name}: nie było zmieniane — pomijam')
            continue
        if not backup.is_file():
            raise ValueError(f'{name}: brak kopii {BACKUP} — nie ruszam pliku')
        current = sha256(path.read_bytes())
        if current != entry['sha256_after']:
            log(lines, f'   {name}: plik zmienił się po poprawce (inna łatka?) — NIE cofam')
            skipped += 1
            continue
        pristine = backup.read_bytes()
        path.write_bytes(pristine)
        if sha256(path.read_bytes()) != sha256(pristine):
            raise ValueError(f'{name}: przywrócony plik nie zgadza się z kopią')
        backup.unlink()
        restored += 1
        log(lines, f'   {name}: przywrócony oryginał')
    log(lines, f'GOTOWE. Przywrócone pliki: {restored}; pominięte: {skipped}.')
    if restored:
        STATE.unlink(missing_ok=True)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Poprawka łamania linii w opisach.')
    parser.add_argument('action', choices=('install', 'restore'))
    parser.add_argument('--game', type=Path)
    args = parser.parse_args(argv)
    lines = [f'RAPORT LAMANIE LINII — {time.strftime("%Y-%m-%d %H:%M:%S")}',
             f'Działanie: {"poprawka" if args.action == "install" else "cofnięcie"}']
    try:
        check_game_stopped()
        if args.action == 'install':
            game = args.game or find_game()
            lines.append(f'Folder gry: {game}')
            code = install(Path(game), lines)
            AA_PATH = Path(game) / GAME_DATA / AA
            if STATE.is_file():
                state = json.loads(STATE.read_text(encoding='utf8'))
                for name, entry in state['bundles'].items():
                    entry['path'] = str(AA_PATH / name)
                STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1),
                                 encoding='utf8')
        else:
            code = restore(lines)
    except Exception as error:                     # noqa: BLE001 - the BAT prints it
        lines.append(f'BŁĄD: {error}')
        REPORT.write_text('\n'.join(lines) + '\n', encoding='utf8')
        print(f'\nBŁĄD: {error}', flush=True)
        return 1
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf8')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
