#!/usr/bin/env python3
"""Zbierz z gry to, czego brakuje w repo: katalogi Addressables, listę plików i bundli.

Uruchamiane NA KOMPUTERZE WŁAŚCICIELA (przez `URUCHOM_TO.bat` w zestawie), nie tutaj.
Skrypt **niczego nie zmienia**: czyta folder gry, kopiuje wybrane pliki i pakuje je do
`SRW_Y_BRAKUJACE_DANE.zip` na pulpicie.

Co zbiera:

* wszystkie katalogi Addressables (`catalog.json`, `catalog.hash`, `settings.json`,
  `catalog.bin`) — one mówią, co jest w grze i w którym bundlu;
* pełną listę plików pod `StreamingAssets/aa` z rozmiarami (`lista.txt`) — dowód, czego
  jeszcze nie mamy;
* bundle wybrane po adresach z katalogu: misje (`mission`), presety (`preset`) oraz scena
  otwarcia DLC-RD-01 (`2000_0106300`, obie wersje językowe);
* bundle spoza paczek, które już mamy (gdyby gra miała dodatki, o których nie wiemy).

Bundli, które już są w repozytorium (`znane_bundles.json`), nie wysyła ponownie.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from map_catalog import Catalog, CatalogError, load_catalog  # noqa: E402

HERE = Path(__file__).resolve().parent
LOG_NAME = 'SRW_Y_BRAKUJACE_log.txt'
_LOG: list[str] = []


def log(text: str = '') -> None:
    """Every step goes to the window *and* to the log on the Desktop.

    The first version of this kit printed nothing before the first slow step, so on the
    owner's machine the window stayed black and there was nothing to go on. Now the first
    line appears before anything else happens, and the whole run is written to a file.
    """
    _LOG.append(text)
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'), flush=True)


def desktop_dir(explicit: str | None = None) -> Path:
    """The real Desktop: OneDrive redirects it, and `%USERPROFILE%\\Desktop` may not exist."""
    if explicit:
        return Path(explicit)
    home = Path.home()
    for candidate in (home / 'Desktop', home / 'OneDrive' / 'Desktop',
                      home / 'OneDrive' / 'Pulpit', home / 'Pulpit'):
        if candidate.is_dir():
            return candidate
    return home
KNOWN = HERE / 'znane_bundles.json'
CATALOG_NAMES = ('catalog.json', 'catalog.hash', 'settings.json', 'catalog.bin')
#: adresy assetów, które nas interesują (małe litery, dopasowanie po fragmencie)
SELECTORS = {
    'mission': 'dane misji (tytuł, rozdział, mapa misji)',
}
#: sceny, dla których w korpusie nie ma japońskiego — lista z repozytorium
SCENES_FILE = HERE / 'sceny_bez_ja.json'
KNOWN_PACKS = {'aa', 'AnniversaryExpansionPack', 'BonusMission', 'DeluxeEdition', 'Dlc1',
               'Dlc2', 'EarlyPurchase', 'ExpansionPack', 'PremiumSound',
               'SeasonPassBonus', 'UltimateEdition'}
MAX_SINGLE = 40 * 1024 * 1024
MAX_TOTAL = 400 * 1024 * 1024


def stem(name: str) -> str:
    """Bundle file name without the `.bundle` suffix — that is how we key the known set."""
    return name[:-7] if name.endswith('.bundle') else name


def known_bundles(path: Path | None = None) -> dict[str, str]:
    path = path or KNOWN
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    bundles = data.get('bundles', data)
    return {stem(name): digest for name, digest in bundles.items()}


def find_streamingassets(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    candidates = [
        r'D:\Games\SUPER ROBOT WARS Y',
        r'C:\Games\SUPER ROBOT WARS Y',
        r'E:\Games\SUPER ROBOT WARS Y',
        r'C:\Program Files (x86)\Steam\steamapps\common\SUPER ROBOT WARS Y',
        r'D:\SteamLibrary\steamapps\common\SUPER ROBOT WARS Y',
        r'E:\SteamLibrary\steamapps\common\SUPER ROBOT WARS Y',
    ]
    for root in candidates:
        path = Path(root) / 'SUPER ROBOT WARS Y_Data' / 'StreamingAssets'
        if path.is_dir():
            return path
    answer = input('Nie znalazłem gry. Wklej folder StreamingAssets: ').strip().strip('"')
    return Path(answer)


def scan(streaming: Path) -> dict[str, int]:
    """Relative path -> size, everything under StreamingAssets (the listing is small)."""
    found = {}
    for path in sorted(streaming.rglob('*')):
        if path.is_file():
            found[path.relative_to(streaming).as_posix()] = path.stat().st_size
    return found


def catalogs(streaming: Path) -> list[Path]:
    return sorted(path for path in streaming.rglob('catalog.json') if path.is_file())


def missing_scenes(path: Path | None = None) -> list[str]:
    """Scene ids the corpus has only in English (written by the kit builder)."""
    path = path or SCENES_FILE
    if not path.is_file():
        return []
    return list(json.loads(path.read_text(encoding='utf-8')).get('scenes', []))


def selector_for(address: str, scenes: list[str]) -> list[str]:
    name = address.lower()
    reasons = [key for key in SELECTORS if key in name]
    reasons += [f'scena bez JP: {scene}' for scene in scenes if scene in address]
    return reasons


def select(streaming: Path, listing: dict[str, int], known: dict[str, str],
           scenes: list[str] | None = None) -> tuple[dict, list]:
    """Which bundles to copy, and why. Resolution comes from the game's own catalogues."""
    scenes = scenes if scenes is not None else missing_scenes()
    by_name = {path.rsplit('/', 1)[-1]: path for path in listing}
    chosen: dict[str, dict] = {}
    problems = []
    for catalog_path in catalogs(streaming):
        try:
            catalog = Catalog(load_catalog(catalog_path))
        except CatalogError as error:
            problems.append(f'{catalog_path.relative_to(streaming).as_posix()}: {error}')
            log(f'  nie czytam {catalog_path.name}: {error}')
            continue
        log(f'  {catalog_path.relative_to(streaming).as_posix()}: '
            f'{len(catalog.addresses):,} adresow')
        for index, address in enumerate(catalog.addresses):
            reasons = selector_for(address, scenes)
            if not reasons:
                continue
            bundle = catalog.bundle_for(index)
            if not bundle:
                continue
            if stem(bundle) in known:
                continue
            relative = by_name.get(bundle)
            if relative is None:
                problems.append(f'brak pliku bundla w grze: {bundle} (asset {address})')
                continue
            entry = chosen.setdefault(relative, {
                'path': relative, 'bytes': listing[relative], 'reasons': set(), 'addresses': []})
            entry['reasons'].update(reasons)
            if len(entry['addresses']) < 20:
                entry['addresses'].append(address)
    # paczki, których w ogóle nie znamy (nowy dodatek?) — po jednym bundlu na paczkę
    for relative, size in listing.items():
        if not relative.endswith('.bundle') or size > MAX_SINGLE:
            continue
        pack = relative.split('/')[0] if '/' in relative else 'aa'
        if pack in KNOWN_PACKS:
            continue
        if stem(relative.rsplit('/', 1)[-1]) in known:
            continue
        entry = chosen.setdefault(relative, {
            'path': relative, 'bytes': size, 'reasons': set(), 'addresses': []})
        entry['reasons'].add(f'nieznana paczka: {pack}')
    rows = []
    total = 0
    for entry in sorted(chosen.values(), key=lambda item: (sorted(item['reasons'])[0], item['path'])):
        if entry['bytes'] > MAX_SINGLE or total + entry['bytes'] > MAX_TOTAL:
            problems.append(f'pominięty (za duży): {entry["path"]} — {entry["bytes"]:,} B')
            continue
        total += entry['bytes']
        entry['reasons'] = sorted(entry['reasons'])
        rows.append(entry)
    return {'rows': rows, 'bytes': total}, problems


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            sha.update(chunk)
    return sha.hexdigest()


def collect(streaming: Path, target: Path, known: dict[str, str],
            scenes: list[str] | None = None) -> dict:
    listing = scan(streaming)
    log(f'  plikow w grze: {len(listing):,}')
    log(f'  katalogow Addressables: {len(catalogs(streaming))}')
    plan, problems = select(streaming, listing, known, scenes)
    if target.exists():
        shutil.rmtree(target)
    (target / 'bundles').mkdir(parents=True)
    (target / 'katalogi').mkdir()
    (target / 'lista.txt').write_text(
        '\n'.join(f'{size}\t{path}' for path, size in listing.items()) + '\n', encoding='utf-8')
    catalogs_copied = []
    for catalog_path in catalogs(streaming):
        folder = catalog_path.parent.relative_to(streaming).as_posix().replace('/', '_') or 'aa'
        for name in CATALOG_NAMES:
            source = catalog_path.parent / name
            if not source.is_file():
                continue
            destination = target / 'katalogi' / f'{folder}__{name}'
            shutil.copy2(source, destination)
            catalogs_copied.append(destination.name)
    log(f'  wybranych bundli: {len(plan["rows"])} ({plan["bytes"]:,} B)')
    copied = []
    for entry in plan['rows']:
        source = streaming / entry['path']
        if not source.is_file():
            problems.append(f'zniknął w trakcie: {entry["path"]}')
            continue
        destination = target / 'bundles' / entry['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append({'path': entry['path'], 'bytes': entry['bytes'],
                       'sha256': digest(destination), 'reasons': entry['reasons'],
                       'addresses': entry['addresses']})
    manifest = {'schema': 1, 'created': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'game': str(streaming), 'catalogs': catalogs_copied, 'bundles': copied,
                'bytes': sum(item['bytes'] for item in copied), 'problems': problems}
    (target / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return manifest


def report(manifest: dict) -> str:
    lines = ['SRW Y — zbieranie brakujących danych', '=' * 40, '']
    lines.append(f'bundle do wysłania: {len(manifest["bundles"])} '
                 f'({manifest["bytes"] / (1024 * 1024):.1f} MB)')
    lines.append(f'katalogi Addressables: {len(manifest["catalogs"])}')
    for item in manifest['bundles']:
        lines.append(f'  {item["path"]}  {item["bytes"]:,} B  [{", ".join(item["reasons"])}]')
    if manifest['problems']:
        lines += ['', 'UWAGI:'] + [f'  {problem}' for problem in manifest['problems']]
    return '\n'.join(lines) + '\n'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--streamingassets', help='folder StreamingAssets (zwykle wykrywany)')
    parser.add_argument('--desktop', help='gdzie zapisać wynik (domyślnie pulpit)')
    parser.add_argument('--known', type=Path, help='lista bundli, których nie wysyłać')
    parser.add_argument('--sceny', type=Path, help='lista scen bez japońskiego')
    args = parser.parse_args(argv)

    log('=================================================')
    log('SRW Y - zbieranie brakujacych danych (wersja 3)')
    log('Skrypt niczego nie zmienia w grze: czyta i kopiuje.')
    log('=================================================')
    dest = desktop_dir(args.desktop)
    log_path = dest / LOG_NAME
    try:
        return run(args, dest)
    except Exception:                                  # noqa: BLE001 - the owner runs this
        log('')
        log('PRZERWANE - zrzut ponizej. Niczego nie zmieniono w grze.')
        log(traceback.format_exc())
        return 1
    finally:
        try:
            log_path.write_text('\n'.join(_LOG) + '\n', encoding='utf-8')
            print(f'\nLog: {log_path}', flush=True)
        except OSError:
            pass
        try:
            input('\nNacisnij Enter, zeby zamknac okno...')
        except (EOFError, KeyboardInterrupt):
            pass


def run(args, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    known = known_bundles(args.known)
    scenes = missing_scenes(args.sceny)
    log(f'bundli, ktorych nie wysylam ponownie: {len(known)}')
    log(f'scen bez japonskiego do sprawdzenia: {len(scenes)}')
    log('')
    log('Szukam gry...')
    streaming = find_streamingassets(args.streamingassets)
    if not (streaming / 'aa').is_dir():
        log(f'To nie wyglada na StreamingAssets: {streaming}')
        return 2
    log(f'folder gry: {streaming}')
    target = dest / 'SRW_Y_BRAKUJACE_DANE'
    log('')
    log('Czytam liste plikow w grze (moze potrwac chwile)...')
    manifest = collect(streaming, target, known, scenes)
    (target / 'RAPORT_BRAKUJACE.txt').write_text(report(manifest), encoding='utf-8')
    log('')
    log('Pakuje...')
    archive = dest / 'SRW_Y_BRAKUJACE_DANE'
    shutil.make_archive(str(archive), 'zip', target)
    log(report(manifest))
    log(f'Gotowe: {archive.with_suffix(".zip")}')
    log('Wgraj ten ZIP na Drive i napisz, ze jest.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
