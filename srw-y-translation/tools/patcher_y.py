#!/usr/bin/env python3
"""Install or restore a source-bound SRW Y translation, using local game files.

Stage and verify every rebuilt bundle before touching the game; preserve verified
backups beside originals. A state file records exact patched hashes for safe undo.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from apply_y_plan import build_bundle, jobs_for, name_jobs, safe_relative, sha

GAME_DATA = 'SUPER ROBOT WARS Y_Data/StreamingAssets'
BACKUP = '.srwy-original.bak'
# Katalog diagnostyczny: patcher zapisuje tu **kopię** bundla, którego nie dało
# się zapisać (same pliki gry zostają nietknięte). Bez tego każdy rozjazd
# wymagał nowej rundy zbierania danych od właściciela.
SAMPLES = Path('przyklady')
NARZEDZIA = Path('narzedzia')
TEMP = '.srwy-new.tmp'
REMEMBERED_PATH_FILE = 'sciezka_gry.txt'
GAME_CANDIDATE_SUFFIXES = (
    'SUPER ROBOT WARS Y',
    'SRWY',
    'Games/SUPER ROBOT WARS Y',
    'Games/SRWY',
    'Gry/SUPER ROBOT WARS Y',
    'Gry/SRWY',
    'SteamLibrary/steamapps/common/SUPER ROBOT WARS Y',
    'SteamLibrary/steamapps/common/SRWY',
    'Steam/steamapps/common/SUPER ROBOT WARS Y',
    'Steam/steamapps/common/SRWY',
    'Program Files (x86)/Steam/steamapps/common/SUPER ROBOT WARS Y',
    'Program Files (x86)/Steam/steamapps/common/SRWY',
    'Program Files/Steam/steamapps/common/SUPER ROBOT WARS Y',
    'Program Files/Steam/steamapps/common/SRWY',
)


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


def _keep_sample(target: Path, rel: str) -> None:
    """Kopia bundla, którego nie udało się zbudować — do diagnozy, bez zmian w grze."""
    samples = Path.cwd() / SAMPLES
    samples.mkdir(parents=True, exist_ok=True)
    copy = samples / (('oa_' if rel.startswith('aa/') else '') + target.name)
    if not copy.exists():
        shutil.copy2(target, copy)
        print(f'Kopia pliku do diagnostyki (gra nietknięta): {copy}')


def plan_rows_with_text(plan: dict) -> dict:
    """Wiersze planu, które mają polski tekst — po pliku/tabeli."""
    wanted = {}
    for name, rows in plan.get('scenes', {}).items():
        keys = {key for key, row in rows.items() if row.get('pl')}
        if keys:
            wanted[name] = keys
    for name, rows in plan.get('tables', {}).items():
        keys = {key for key, row in rows.items() if row.get('pl')}
        if keys:
            wanted[name] = keys
    return wanted


def summarise(report: dict, plan: dict) -> dict:
    """Co z planu trafiło do gry, a co nie — liczby i pełne listy do raportu.

    Wiersz, którego **żadna** kopia pliku w grze nie zawiera w tym brzmieniu,
    zostaje po japońsku. To nie jest błąd instalacji i nie ma powodu, żeby przez
    jedną taką linię gra została bez pozostałych osiemdziesięciu tysięcy — ale
    musi być policzony i wypisany co do sztuki, bo to wsad do następnej paczki
    dla tłumacza.
    """
    applied = report.get('trafione_wiersze', {})
    nieuzyte = {}
    for name, keys in plan_rows_with_text(plan).items():
        left = sorted(keys - applied.get(name, set()))
        if left:
            nieuzyte[name] = left
    return {
        'schema': 1,
        'zapisane_linie': report.get('zapisane', 0),
        'dopasowane_numerem': report.get('po_numerze', 0),
        'dopasowane_zdaniem': report.get('po_zdaniu', 0),
        'linie_planu_bez_miejsca_w_grze': sum(len(v) for v in nieuzyte.values()),
        'pliki_z_innym_tekstem': len({x['plik'] for x in report.get('inny_tekst', ())}),
        'inny_tekst': report.get('inny_tekst', []),
        'niejednoznaczne': report.get('niejednoznaczne', []),
        'kopie_bez_dopasowania': report.get('kopie_bez_dopasowania', []),
        'nieuzyte_wiersze_planu': nieuzyte,
    }


def write_report(summary: dict, folder: Path | None = None) -> Path:
    path = (folder or Path.cwd()) / 'RAPORT_ROZJAZDOW.json'
    write_atomic(path, (json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode())
    return path


def print_summary(summary: dict, failures: list) -> None:
    print('')
    print('--- PODSUMOWANIE ---')
    print(f"Zapisanych linii: {summary['zapisane_linie']} "
          f"(po numerze {summary['dopasowane_numerem']}, "
          f"po samym zdaniu {summary['dopasowane_zdaniem']})")
    print(f"Linie planu, dla których gra nie ma tego zdania: "
          f"{summary['linie_planu_bez_miejsca_w_grze']} — zostają oryginalne")
    print(f"Linie gry o innym brzmieniu niż zwrotka: {len(summary['inny_tekst'])} "
          f"w {summary['pliki_z_innym_tekstem']} plikach")
    if summary['niejednoznaczne']:
        print(f"Linie niejednoznaczne (kilka różnych tłumaczeń tego samego zdania): "
              f"{len(summary['niejednoznaczne'])} — nie zapisano żadnego")
    if failures:
        print(f'Bundle, których nie dało się zbudować: {len(failures)}')
        for item in failures[:10]:
            print(f"  {item['bundle']}: {item['blad']}")
        if len(failures) > 10:
            print(f'  …i {len(failures) - 10} więcej (pełna lista w raporcie)')
    print('Pełna lista: narzedzia\\RAPORT_ROZJAZDOW.json')


def build_all(root: Path, jobs: dict, named: dict, plan: dict, builder,
              stage: Path | None, report: dict, samples: bool = True):
    """Buduje **wszystkie** bundle i zbiera wszystkie problemy, nie pierwszy.

    Do 2026-11-11 pierwszy niezbudowany plik przerywał cały przebieg, więc jedno
    uruchomienie u właściciela pokazywało dokładnie jeden problem: 106/488, potem
    139/488, potem znowu 139/488. Przy 488 bundlach to droga donikąd. Teraz
    przebieg idzie do końca, a gra i tak zostaje nietknięta, dopóki lista
    problemów nie jest pusta.
    """
    entries, failures = [], []
    for number, (rel, job) in enumerate(sorted(jobs.items()), 1):
        target = target_for(root, rel)
        print(f'Budowanie {number}/{len(jobs)}: {rel}', flush=True)
        named_items = named.get(rel) if named else None
        try:
            extra = {'named': named_items, 'written': report.setdefault('zapisane_pliki', set())
                     } if named_items else {}
            patched, counts = builder(rel, target.read_bytes(), job, plan,
                                      report=report, **extra)
        except (ValueError, KeyError) as error:
            # Plik zostaje w grze nietknięty; jego **kopia** ląduje w `przyklady/`,
            # żeby dało się zbadać rozjazd bez kolejnej rundy zbierania danych.
            if samples:
                _keep_sample(target, rel)
            failures.append({'bundle': rel, 'blad': str(error)})
            print(f'  PROBLEM: {error}', flush=True)
            continue
        if stage is None:
            continue
        path = stage / f'{number}.bundle'
        path.write_bytes(patched)
        entries.append({'path': rel, 'original': job['source']['sha256'],
                        'patched': sha(patched), 'counts': counts, 'stage': str(path)})
    return entries, failures


def check(streaming: Path, plan: dict, index: dict, builder=build_bundle) -> dict:
    """Sprawdza całą grę i nie zmienia w niej ani bajtu (`SPRAWDZ.bat`)."""
    root = streaming.resolve()
    jobs = jobs_for(plan, index)
    named = collections.defaultdict(list)
    for item in name_jobs(plan, jobs):
        named[item['path']].append(item)
    for rel, job in jobs.items():
        target = target_for(root, rel)
        if not target.is_file() or file_hash(target) != job['source']['sha256']:
            raise ValueError(f'{rel}: brak lub inna wersja pliku; gra nie została zmieniona')
    report: dict = {}
    _, failures = build_all(root, jobs, named, plan, builder, None, report)
    summary = summarise(report, plan)
    summary['niezbudowane_bundle'] = failures
    write_report(summary, NARZEDZIA if NARZEDZIA.is_dir() else None)
    print_summary(summary, failures)
    return summary


def install(streaming: Path, plan: dict, index: dict, state: Path, builder=build_bundle) -> dict:
    root = streaming.resolve()
    if state.exists():
        raise ValueError('Istnieje stan poprzedniej instalacji; najpierw uruchom COFNIJ.bat')
    jobs = jobs_for(plan, index)
    named = collections.defaultdict(list)
    for item in name_jobs(plan, jobs):
        named[item['path']].append(item)
    wanted_by_name = {item['name'] for items in named.values() for item in items}
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
        report: dict = {}
        entries, failures = build_all(root, jobs, named, plan, builder, stage, report)
        written = report.get('zapisane_pliki', set())
        summary = summarise(report, plan)
        summary['niezbudowane_bundle'] = failures
        write_report(summary, NARZEDZIA if NARZEDZIA.is_dir() else None)
        if failures:
            # Gra zostaje nietknięta, ale raport mówi o **wszystkich** plikach,
            # a nie tylko o pierwszym — jedno uruchomienie, pełna diagnoza.
            print_summary(summary, failures)
            raise ValueError(
                f'{len(failures)} bundli nie dało się zbudować (pierwszy: '
                f"{failures[0]['bundle']}: {failures[0]['blad']}). "
                'Nic nie zostało zapisane w grze; pełna lista w '
                'narzedzia\\RAPORT_ROZJAZDOW.json')
        # Plik znaleziony w grze, ale bez ani jednej pasującej linii, to rozjazd
        # tekstu (jest w raporcie), a nie brak pliku. Mylenie tych dwóch rzeczy
        # dawałoby komunikat „nie znaleziono”, który wysyła szukającego w las.
        unwritten = sorted(wanted_by_name - written - report.get('znalezione_pliki', set()))
        if unwritten:
            # Cichy brak byłby gorszy niż błąd: plan tłumaczy te pliki, a żaden
            # bundle gry ich nie zawierał.
            raise ValueError('nie znaleziono plików scen w bundlach: ' + ', '.join(unwritten))
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
    print_summary(summary, [])
    return saved


def _verify_restore_entry(root: Path, item: dict) -> str:
    target = target_for(root, item['path'])
    backup = Path(str(target) + BACKUP)
    if not backup.is_file() or backup.is_symlink() or file_hash(backup) != item['original']:
        raise ValueError('brak lub niezgodna kopia oryginału')
    if not target.is_file():
        raise ValueError('brak pliku gry')
    current = file_hash(target)
    if current != item['original'] and current != item['patched']:
        raise ValueError('inny plik gry; nie nadpisano')
    return current


def restore_one(root: Path, item: dict) -> None:
    target = target_for(root, item['path'])
    backup = Path(str(target) + BACKUP)
    current = _verify_restore_entry(root, item)
    if current == item['original']:
        return
    tmp = Path(str(target) + TEMP)
    stage_copy(backup, tmp, item['original'])
    try:
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)
    if file_hash(target) != item['original']:
        raise ValueError('przywrócony plik nie przeszedł weryfikacji')


def _same_dir(a: Path, b: Path) -> bool:
    try:
        if os.path.normcase(str(a.resolve())) == os.path.normcase(str(b.resolve())):
            return True
        if a.exists() and b.exists():
            return os.path.samefile(a, b)
    except OSError:
        return False
    return False


def restore(streaming: Path, state: Path, index: dict) -> int:
    if not state.is_file():
        raise ValueError(
            f'Brak pliku stanu {state}; uruchom COFNIJ.bat z folderu, z którego zainstalowano patch.')
    root = streaming.resolve()
    saved = json.loads(state.read_text(encoding='utf-8'))
    if saved.get('schema') != 1 or not isinstance(saved.get('streaming'), str):
        raise ValueError('nieprawidłowy plik stanu patcha')
    entries = saved.get('files')
    if not entries or len({x['path'] for x in entries}) != len(entries):
        raise ValueError('nieprawidłowa lista plików w stanie')
    for item in entries:
        rel = safe_relative(item['path'])
        if rel not in index['bundles'] or item['original'] != index['bundles'][rel]['sha256']:
            raise ValueError(f'{rel}: stan nie odpowiada indeksowi')
    saved_streaming = Path(saved['streaming'])
    if not _same_dir(saved_streaming, root):
        problems = []
        for item in entries:
            try:
                _verify_restore_entry(root, item)
            except Exception as exc:
                problems.append(f"{item['path']}: {exc}")
        if problems:
            raise ValueError(
                f"stan dotyczy innego folderu gry ({saved['streaming']}); "
                f"w wybranym folderze ({root}) nie zgadzają się kopie lub pliki: "
                + '; '.join(problems[:5]))
        print(
            f"Uwaga: folder gry zmienił ścieżkę z {saved['streaming']} na {root}; "
            f"wszystkie kopie ({len(entries)}) i sumy zgodne ze stanem — przywracam.",
            flush=True,
        )
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


def streaming_from_path(path: Path) -> Path | None:
    """Normalizuje wskazany folder (gry, `_Data` albo `StreamingAssets`) do `StreamingAssets`."""
    if not path.is_dir():
        return None
    direct = path / GAME_DATA
    if direct.is_dir():
        return direct
    if path.name == 'SUPER ROBOT WARS Y_Data' and (path / 'StreamingAssets').is_dir():
        return path / 'StreamingAssets'
    if path.name == 'StreamingAssets' and (path / 'aa').is_dir():
        return path
    return None


def game_dir_from_streaming(streaming: Path) -> Path:
    if streaming.name == 'StreamingAssets' and streaming.parent.name == 'SUPER ROBOT WARS Y_Data':
        return streaming.parent.parent
    if streaming.name == 'StreamingAssets':
        return streaming.parent
    return streaming


def candidate_game_dirs(drives: str = 'CDEFGHIJKLMNOPQRSTUVWXYZ') -> list[Path]:
    candidates = []
    for letter in drives:
        if os.name == 'nt' and not os.path.isdir(f'{letter}:\\'):
            continue
        for suffix in GAME_CANDIDATE_SUFFIXES:
            candidates.append(Path(f'{letter}:/{suffix}'))
    return candidates


def discover_games(candidates: list[Path] | None = None) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for p in (candidates if candidates is not None else candidate_game_dirs()):
        streaming = streaming_from_path(p)
        if streaming is None:
            continue
        key = os.path.normcase(str(streaming.resolve()))
        if key not in seen:
            seen.add(key)
            found.append(streaming)
    return found


def _pick_directory_tk(title: str, initial: Path | None = None) -> str | None:
    try:
        import tkinter
        from tkinter import filedialog
    except Exception:
        return None
    try:
        root = tkinter.Tk()
    except Exception:
        return None
    root.withdraw()
    try:
        root.attributes('-topmost', True)
    except Exception:
        pass
    for step in ('update', 'lift', 'focus_force'):
        try:
            getattr(root, step)()
        except Exception:
            pass
    initialdir = str(initial) if initial is not None and initial.is_dir() else None
    try:
        chosen = filedialog.askdirectory(
            parent=root, title=title, initialdir=initialdir, mustexist=True)
    except Exception:
        return None
    finally:
        try:
            root.destroy()
        except Exception:
            pass
    return chosen or ''


def _pick_directory_winforms(title: str, initial: Path | None = None) -> str | None:
    if os.name != 'nt':
        return None
    env = os.environ.copy()
    env['SRWY_PICK_TITLE'] = title
    env['SRWY_PICK_INITIAL'] = str(initial) if initial is not None and initial.is_dir() else ''
    script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$form = New-Object System.Windows.Forms.Form -Property @{ TopMost = $true }; "
        "$dlg = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$dlg.Description = $env:SRWY_PICK_TITLE; "
        "$dlg.ShowNewFolderButton = $false; "
        "if ($env:SRWY_PICK_INITIAL -and (Test-Path -LiteralPath $env:SRWY_PICK_INITIAL)) { "
        "  $dlg.SelectedPath = $env:SRWY_PICK_INITIAL "
        "}; "
        "if ($dlg.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { "
        "  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
        "  Write-Output $dlg.SelectedPath "
        "} else { exit 2 }"
    )
    try:
        result = subprocess.run(
            ['powershell', '-NoProfile', '-STA', '-Command', script],
            capture_output=True, text=True, encoding='utf-8', env=env,
        )
    except OSError:
        return None
    if result.returncode == 2:
        return ''
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def pick_directory(title: str, initial: Path | None = None) -> str | None:
    """Otwiera okno wyboru folderu (Tk albo WinForms); `''` = anulowano, `None` = brak GUI."""
    chosen = _pick_directory_tk(title, initial)
    if chosen is not None:
        return chosen
    return _pick_directory_winforms(title, initial)


def _show_gui_warning(title: str, message: str) -> None:
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
    except Exception:
        return
    root.withdraw()
    try:
        root.attributes('-topmost', True)
    except Exception:
        pass
    try:
        messagebox.showwarning(title, message, parent=root)
    except Exception:
        pass
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def prompt_game_streaming(title: str, initial: Path | None = None) -> Path:
    cur_initial = initial
    while True:
        chosen = pick_directory(title, cur_initial)
        if chosen is None:
            break
        if not chosen:
            raise ValueError('Anulowano wybór folderu gry.')
        path = Path(chosen)
        streaming = streaming_from_path(path)
        if streaming is not None:
            return streaming
        print(
            f'W folderze "{path}" nie znaleziono {GAME_DATA}. '
            'Wybierz folder zawierający plik SUPER ROBOT WARS Y.exe.',
            flush=True,
        )
        _show_gui_warning(
            'Nieprawidłowy folder gry',
            f'W folderze:\n{path}\nnie znaleziono podfolderu {GAME_DATA}.\n\n'
            'Wybierz główny folder gry SUPER ROBOT WARS Y (z plikiem SUPER ROBOT WARS Y.exe).',
        )
        if path.is_dir():
            cur_initial = path

    print('Nie można otworzyć okna wyboru folderu — podaj ścieżkę ręcznie albo uruchom z --game.')
    while True:
        try:
            raw = input('Podaj folder gry SUPER ROBOT WARS Y (Enter = anuluj): ').strip().strip('"')
        except EOFError as exc:
            raise ValueError(
                'Nie można otworzyć okna wyboru folderu ani odczytać ścieżki; '
                'użyj parametru --game <folder_gry>') from exc
        if not raw:
            raise ValueError('Anulowano wybór folderu gry.')
        streaming = streaming_from_path(Path(raw))
        if streaming is not None:
            return streaming
        print(f'W folderze "{raw}" nie znaleziono {GAME_DATA}. Spróbuj ponownie.')


def _looks_like_patched_copy(streaming: Path, saved: dict) -> bool:
    files = saved.get('files') or []
    if not files:
        return False
    for item in files[:3]:
        rel = item.get('path')
        if not rel:
            return False
        try:
            target = target_for(streaming, rel)
        except ValueError:
            return False
        if not Path(str(target) + BACKUP).is_file():
            return False
    return True


def _remembered_streaming(remember_path: Path | None) -> Path | None:
    if remember_path is None or not remember_path.is_file():
        return None
    try:
        raw = remember_path.read_text(encoding='utf-8').strip().strip('"')
    except OSError:
        return None
    if not raw:
        return None
    return streaming_from_path(Path(raw))


def _save_remembered_streaming(remember_path: Path | None, streaming: Path) -> None:
    if remember_path is None:
        return
    try:
        remember_path.parent.mkdir(parents=True, exist_ok=True)
        remember_path.write_text(str(game_dir_from_streaming(streaming)) + '\n', encoding='utf-8')
    except OSError:
        pass


def find_streaming(action: str = 'install', state_path: Path | None = None,
                   remember_path: Path | None = None) -> Path:
    saved = None
    if action == 'restore' and state_path is not None and state_path.is_file():
        try:
            saved = json.loads(state_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            saved = None
    if saved and isinstance(saved.get('streaming'), str):
        saved_streaming = streaming_from_path(Path(saved['streaming']))
        if saved_streaming is not None:
            if _looks_like_patched_copy(saved_streaming, saved):
                print(f'Znaleziono grę ze stanu instalacji: {game_dir_from_streaming(saved_streaming)}')
                return saved_streaming
            other_patched = [s for s in discover_games()
                             if not _same_dir(s, saved_streaming) and _looks_like_patched_copy(s, saved)]
            if not other_patched:
                return saved_streaming
        else:
            print(
                f"Poprzedni folder gry ze stanu instalacji nie istnieje ({saved['streaming']}) "
                '— szukam przeniesionej gry...',
                flush=True,
            )

    found = discover_games()
    if action == 'restore' and saved is not None:
        matched = [s for s in found if _looks_like_patched_copy(s, saved)]
        if len(matched) == 1:
            print(f'Znaleziono przeniesioną grę: {game_dir_from_streaming(matched[0])}')
            return matched[0]
        if len(matched) > 1:
            print('Znaleziono kilka kopii gry z kopiami zapasowymi:')
            for s in matched:
                print(f'  {game_dir_from_streaming(s)}')
        else:
            remembered = _remembered_streaming(remember_path)
            if remembered is not None and _looks_like_patched_copy(remembered, saved):
                print(f'Znaleziono grę z zapamiętanej ścieżki: {game_dir_from_streaming(remembered)}')
                return remembered
            print('Nie znaleziono automatycznie przeniesionej gry — otwieram okno wyboru folderu.',
                  flush=True)
        chosen = prompt_game_streaming(
            'Wybierz folder gry SUPER ROBOT WARS Y do cofnięcia patcha')
        _save_remembered_streaming(remember_path, chosen)
        return chosen

    remembered = _remembered_streaming(remember_path)
    if len(found) == 1 and (remembered is None or _same_dir(found[0], remembered)):
        print(f'Znaleziono grę: {game_dir_from_streaming(found[0])}')
        return found[0]
    if not found and remembered is not None:
        print(f'Znaleziono zapamiętany folder gry: {game_dir_from_streaming(remembered)}')
        return remembered
    if found:
        print('Znaleziono kilka możliwych folderów gry — wybierz właściwy w oknie:')
        for s in found:
            print(f'  {game_dir_from_streaming(s)}')
        if remembered is not None and all(not _same_dir(s, remembered) for s in found):
            print(f'  {game_dir_from_streaming(remembered)}')
    else:
        print('Nie znaleziono gry automatycznie — otwieram okno wyboru folderu.', flush=True)
    initial = game_dir_from_streaming(remembered) if remembered is not None else None
    chosen = prompt_game_streaming(
        'Wybierz folder gry SUPER ROBOT WARS Y (ten z plikiem SUPER ROBOT WARS Y.exe)',
        initial=initial,
    )
    _save_remembered_streaming(remember_path, chosen)
    return chosen


def find_game(action: str = 'install', state_path: Path | None = None,
              remember_path: Path | None = None) -> Path:
    return game_dir_from_streaming(
        find_streaming(action=action, state_path=state_path, remember_path=remember_path))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'restore', 'check'))
    parser.add_argument('--game', type=Path)
    parser.add_argument('--plan', type=Path, default=Path('plan.json'))
    parser.add_argument('--index', type=Path, default=Path('game_text_bundle_index.json'))
    parser.add_argument('--state', type=Path, default=Path('STAN_PATCHA.json'))
    args = parser.parse_args(argv)
    try:
        check_game_stopped()
        if args.game is not None:
            streaming = streaming_from_path(args.game)
            if streaming is None:
                raise ValueError(
                    f'Nie znaleziono folderu StreamingAssets w: {args.game / GAME_DATA}')
        else:
            streaming = find_streaming(
                action=args.action,
                state_path=args.state,
                remember_path=args.state.parent / REMEMBERED_PATH_FILE,
            )
        index = json.loads(args.index.read_text(encoding='utf-8'))
        if args.action == 'check':
            plan = json.loads(args.plan.read_text(encoding='utf-8'))
            summary = check(streaming, plan, index)
            print('GOTOWE — sprawdzenie bez zmian w grze. '
                  f"Zapisalnych linii: {summary['zapisane_linie']}.")
        elif args.action == 'install':
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
