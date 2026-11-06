#!/usr/bin/env python3
"""Install or restore a source-bound SRW Y translation, using local game files.

Stage and verify every rebuilt bundle before touching the game; preserve verified
backups beside originals. A state file records exact patched hashes for safe undo.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from apply_y_plan import build_bundle, jobs_for, safe_relative, sha

GAME_DATA = 'SUPER ROBOT WARS Y_Data/StreamingAssets'
BACKUP = '.srwy-original.bak'
TEMP = '.srwy-new.tmp'


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def target_for(root: Path, rel: str) -> Path:
    safe_relative(rel)
    root = root.resolve()
    target = root.joinpath(*rel.split('/'))
    if not target.resolve().is_relative_to(root) or target.is_symlink():
        raise ValueError(f'{rel}: ścieżka wychodzi poza folder gry lub jest dowiązaniem')
    return target


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.srwy-state-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def stage_copy(src: Path, dest: Path, expected: str) -> None:
    """Exclusive file creation: never overwrite an existing backup or temp file."""
    created = False
    try:
        with src.open('rb') as source, dest.open('xb') as out:
            created = True
            shutil.copyfileobj(source, out, 1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        if file_hash(dest) != expected:
            raise ValueError(f'{dest}: błędna suma kopii')
    except Exception:
        if created:
            dest.unlink(missing_ok=True)
        raise


def install(streaming: Path, plan: dict, index: dict, state: Path, builder=build_bundle) -> dict:
    root = streaming.resolve()
    if state.exists():
        raise ValueError('Istnieje stan poprzedniej instalacji; najpierw uruchom COFNIJ.bat')
    jobs = jobs_for(plan, index)
    for rel, job in jobs.items():
        target = target_for(root, rel)
        if not target.is_file() or file_hash(target) != job['source']['sha256']:
            raise ValueError(f'{rel}: brak lub inna wersja pliku; gra nie została zmieniona')
        backup = Path(str(target) + BACKUP)
        if backup.exists() and (backup.is_symlink() or file_hash(backup) != job['source']['sha256']):
            raise ValueError(f'{rel}: istniejąca kopia nie pasuje do oryginału')
        if Path(str(target) + TEMP).exists():
            raise ValueError(f'{rel}: istnieje plik tymczasowy; niczego nie nadpisano')
    with tempfile.TemporaryDirectory(prefix='srwy-build-') as folder:
        stage = Path(folder)
        entries = []
        for number, (rel, job) in enumerate(sorted(jobs.items()), 1):
            target = target_for(root, rel)
            print(f'Budowanie {number}/{len(jobs)}: {rel}', flush=True)
            patched, counts = builder(rel, target.read_bytes(), job, plan)
            path = stage / f'{number}.bundle'
            path.write_bytes(patched)
            entries.append({'path': rel, 'original': job['source']['sha256'],
                            'patched': sha(patched), 'counts': counts, 'stage': str(path)})
        # Backups are never overwritten, and every one is verified before game files change.
        for item in entries:
            target = target_for(root, item['path'])
            if file_hash(target) != item['original']:
                raise ValueError(f"{item['path']}: plik zmieniony w trakcie budowy")
            backup = Path(str(target) + BACKUP)
            if not backup.exists():
                stage_copy(target, backup, item['original'])
            if backup.is_symlink() or file_hash(backup) != item['original']:
                raise ValueError(f"{item['path']}: kopia nie przeszła weryfikacji")
        saved = {'schema': 1, 'streaming': str(root), 'files': [
            {k: v for k, v in item.items() if k != 'stage'} for item in entries]}
        write_atomic(state, (json.dumps(saved, ensure_ascii=False, indent=2) + '\n').encode())
        changed = []
        try:
            for item in entries:
                target = target_for(root, item['path'])
                if file_hash(target) != item['original']:
                    raise ValueError(f"{item['path']}: plik zmienił się przed instalacją")
                tmp = Path(str(target) + TEMP)
                stage_copy(Path(item['stage']), tmp, item['patched'])
                try:
                    os.replace(tmp, target)
                finally:
                    tmp.unlink(missing_ok=True)
                changed.append(item)
                if file_hash(target) != item['patched']:
                    raise ValueError(f"{item['path']}: zapis nie przeszedł weryfikacji")
        except Exception as exc:
            errors = []
            for item in reversed(changed):
                try:
                    restore_one(root, item)
                except Exception as error:
                    errors.append(f"{item['path']}: {error}")
            if errors:
                raise ValueError(f'Błąd instalacji: {exc}; nie przywrócono: {errors}. Zachowaj stan i kopie.') from exc
            state.unlink(missing_ok=True)
            raise ValueError(f'Błąd instalacji, zmiany cofnięte: {exc}') from exc
    return saved


def restore_one(root: Path, item: dict) -> None:
    target = target_for(root, item['path'])
    backup = Path(str(target) + BACKUP)
    if not backup.is_file() or backup.is_symlink() or file_hash(backup) != item['original']:
        raise ValueError('brak lub niezgodna kopia oryginału')
    if not target.is_file():
        raise ValueError('brak pliku gry')
    current = file_hash(target)
    if current == item['original']:
        return
    if current != item['patched']:
        raise ValueError('inny plik gry; nie nadpisano')
    tmp = Path(str(target) + TEMP)
    stage_copy(backup, tmp, item['original'])
    try:
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)
    if file_hash(target) != item['original']:
        raise ValueError('przywrócony plik nie przeszedł weryfikacji')


def restore(streaming: Path, state: Path, index: dict) -> int:
    root = streaming.resolve()
    saved = json.loads(state.read_text(encoding='utf-8'))
    if saved.get('schema') != 1 or Path(saved['streaming']).resolve() != root:
        raise ValueError('stan dotyczy innego folderu gry')
    entries = saved['files']
    if not entries or len({x['path'] for x in entries}) != len(entries):
        raise ValueError('nieprawidłowa lista plików w stanie')
    for item in entries:
        rel = safe_relative(item['path'])
        if rel not in index['bundles'] or item['original'] != index['bundles'][rel]['sha256']:
            raise ValueError(f'{rel}: stan nie odpowiada indeksowi')
    errors = []
    for item in entries:
        try:
            restore_one(root, item)
            print(f"Przywrócono: {item['path']}", flush=True)
        except Exception as exc:
            errors.append(f"{item['path']}: {exc}")
    if errors:
        raise ValueError('Nie wszystkie pliki przywrócono; zachowaj stan i kopie: ' + '; '.join(errors))
    state.unlink()
    return len(entries)


def check_game_stopped():
    if os.name != 'nt':
        return
    result = subprocess.run(['tasklist', '/fo', 'csv', '/nh'], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Nie można sprawdzić uruchomionych procesów; zamknij grę i spróbuj ponownie')
    for row in csv.reader(result.stdout.splitlines()):
        if row and 'super robot wars y' in row[0].lower():
            raise ValueError('Gra jest uruchomiona — zamknij ją przed instalacją lub cofnięciem')


def find_game() -> Path:
    candidates = []
    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
        for suffix in ('Games/SUPER ROBOT WARS Y', 'Gry/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SRWY',
                       'Program Files/Steam/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SUPER ROBOT WARS Y',
                       'Program Files/Steam/steamapps/common/SUPER ROBOT WARS Y'):
            candidates.append(Path(f'{letter}:/{suffix}'))
    for p in candidates:
        if (p / GAME_DATA).is_dir():
            print(f'Znaleziono grę: {p}')
            return p
    return Path(input('Podaj folder gry SUPER ROBOT WARS Y: ').strip().strip('"'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'restore'))
    parser.add_argument('--game', type=Path)
    parser.add_argument('--plan', type=Path, default=Path('plan.json'))
    parser.add_argument('--index', type=Path, default=Path('game_text_bundle_index.json'))
    parser.add_argument('--state', type=Path, default=Path('STAN_PATCHA.json'))
    args = parser.parse_args(argv)
    try:
        check_game_stopped()
        game = args.game or find_game()
        streaming = game / GAME_DATA
        if not streaming.is_dir():
            raise ValueError(f'Nie znaleziono folderu StreamingAssets: {streaming}')
        index = json.loads(args.index.read_text(encoding='utf-8'))
        if args.action == 'install':
            plan = json.loads(args.plan.read_text(encoding='utf-8'))
            result = install(streaming, plan, index, args.state)
            print(f"GOTOWE. Zmieniono {len(result['files'])} plików; kopie są obok oryginałów.")
        else:
            print(f'GOTOWE. Przywrócono {restore(streaming, args.state, index)} plików.')
    except (OSError, ValueError, KeyError) as exc:
        print(f'BŁĄD: {exc}', file=sys.stderr)
        return 1
    return 0


class Tee:
    def __init__(self, stream, log):
        self.stream, self.log = stream, log

    def write(self, text):
        self.stream.write(text)
        self.log.write(text)
        self.log.flush()

    def flush(self):
        self.stream.flush()
        self.log.flush()

    def isatty(self):
        return self.stream.isatty()


if __name__ == '__main__':
    with open('RAPORT_PATCHA.txt', 'w', encoding='utf-8') as log:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = Tee(stdout, log), Tee(stderr, log)
        try:
            code = main()
        finally:
            sys.stdout, sys.stderr = stdout, stderr
    raise SystemExit(code)
