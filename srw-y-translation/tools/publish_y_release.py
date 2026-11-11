#!/usr/bin/env python3
"""Publikacja wydania SRW Y bez duplikatów — ta sama paczka = jedno wydanie.

Problem, który to narzędzie zamyka (zmierzone 2026-11-11): workflow tworzył
**nowe wydanie po każdym scaleniu do `main`**, a `main` dostaje commit także
wtedy, gdy plan PL się nie zmienił. Efekt: `patch-y-pl9-2026-11-11` i
`patch-y-57-d8ec8812` wiozą **bajtowo identyczny** instalator
(SHA-256 `5c1e36ed…940f`, 6 107 179 B), a `patch-y-57-d8ec8812` jest w opisie
nazwane „niepełne tłumaczenie”, choć pokrycie tabel to 100%. Dla pobierającego
wygląda to jak dwa różne wydania, choć to jedno.

Zasada publikacji jest teraz **liczona z sumy instalatora**, nie z numeru
przebiegu CI:

* **nowa suma** → nowe wydanie, tag `patch-y-<etykieta>-<data>`
  (np. `patch-y-pl9-2026-11-11`), oznaczone jako `Latest`, tytuł z etykietą;
* **suma już opublikowana** → **nic nowego nie powstaje**; do istniejącego
  wydania dopisywane są tylko brakujące załączniki (ten sam plik → nadpisanie
  jest błędem, więc `--clobber` nie jest używany dla ZIP-a o innej treści),
  a numer przebiegu jest dopisany do opisu. To jedno miejsce, w którym wolno
  powiedzieć „to samo wydanie” — bo potwierdza to SHA-256, nie nazwa pliku.

Publikacja korzysta z `gh` (interfejs GitHub API). Wydanie, którego instalator
ma **inną** sumę niż budowany teraz, nigdy nie jest nadpisywane: dostaje
wzmiankę o nowszym wydaniu, ale zostaje jako archiwum.

    python3 tools/publish_y_release.py --tag patch-y-<etykieta>-<data> \\
        --title "SRW Y — <etykieta+pokrycie z planu>" \\
        --notes build/release_y/OPIS_WYDANIA.md \\
        --zip build/patcher/SRW_Y_PATCH_PL.zip \\
        --extra build/release_y/SHA256SUMS.txt build/release_y/PL_COVERAGE.json \\
              build/release_y/RELEASE_INFO.json

    python3 tools/publish_y_release.py --plan-only      # co by zrobił, bez gh

Wyjście (stdout) to JSON z decyzją: `new_release`, `reuse_release` albo
`nothing_to_do`, plus tag i suma — workflow publikuje tylko wtedy, gdy jest co
publikować.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import release_y  # noqa: E402

# Tytuł wydania musi mówić, co to jest i jak szeroki jest przekład. Stary
# szablon z workflow („PL (niepełne tłumaczenie)”) trafiał też do wydania
# z 100% tabel, więc tytuł bierzemy z etykiety planu i pokrycia, nie z literału.
TITLE = 'SRW Y — {label} (tabele {table_pct}%, scenariusz {scene_pct}%)'
ARCHIVE_NOTE = ('Starsze wydanie tego samego projektu — instalator ma inną sumę niż '
                'bieżące wydanie. Zostaje jako archiwum; do instalacji użyj wydania '
                'oznaczonego jako Latest.')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gh_json(args: list[str]) -> object:
    out = subprocess.run(['gh', *args], capture_output=True, text=True, check=True)
    return json.loads(out.stdout) if out.stdout.strip() else None


def releases(repo: str) -> list[dict]:
    """Wszystkie wydania repo, bez stron pominiętych (per_page=100, do 5 stron)."""
    result: list[dict] = []
    for page in range(1, 6):
        batch = gh_json(['api', f'repos/{repo}/releases?per_page=100&page={page}'])
        if not batch:
            break
        result.extend(batch)
        if len(batch) < 100:
            break
    return result


def installer_digest(release: dict) -> str | None:
    """SHA-256 instalatora wydania: z GitHub `digest`, a gdy go nie ma — z `SHA256SUMS.txt`."""
    for asset in release.get('assets') or []:
        name = asset.get('name', '')
        if not name.endswith('.zip'):
            continue
        digest = asset.get('digest') or ''
        if digest.startswith('sha256:'):
            return digest.split(':', 1)[1]
    return None


def find_by_digest(all_releases: list[dict], digest: str) -> dict | None:
    for release in all_releases:
        if installer_digest(release) == digest:
            return release
    return None


def plan_prefix(release: dict) -> str | None:
    """Etykieta (`PL…`) z tagu `patch-y-<etykieta>-<data>`."""
    match = re.fullmatch(r'patch-y-(pl\d+)-.*', release.get('tag_name', ''), re.IGNORECASE)
    return match.group(1).upper() if match else None


def coverages() -> tuple[str, dict]:
    current = release_y.load_release()
    plan = json.loads(current['plan'].read_text(encoding='utf-8'))
    report = json.loads(current['report'].read_text(encoding='utf-8'))
    import build_y_release_meta
    return current['label'], build_y_release_meta.coverage(plan, report)


def release_title(label: str, coverage: dict) -> str:
    return TITLE.format(label=label,
                        table_pct=f'{coverage["tables"]["percent_rows"]:g}',
                        scene_pct=f'{coverage["scenes"]["percent_lines"]:g}'.replace('.', ','))


def decide(all_releases: list[dict], digest: str, label: str) -> dict:
    """Decyzja bez dotykania GitHuba — czysta funkcja na liście wydań."""
    same = find_by_digest(all_releases, digest)
    if same is not None:
        return {'action': 'reuse_release', 'tag': same['tag_name'],
                'release_id': same['id'], 'sha256': digest, 'label': label}
    return {'action': 'new_release', 'tag': None, 'release_id': None,
            'sha256': digest, 'label': label}


def publish(repo: str, tag: str, title: str, notes: Path, zip_path: Path,
            extra: list[Path], summary: dict, run: str = '') -> dict:
    """Utwórz nowe wydanie albo uzupełnij istniejące o brakujące załączniki."""
    attaches = [zip_path, *extra]
    existing = None
    for release in releases(repo):
        if release['tag_name'] == tag:
            existing = release
            break
    if existing is None:
        subprocess.run(['gh', 'release', 'create', tag,
                        '--title', title,
                        '--notes-file', str(notes),
                        '--latest',
                        *[str(p) for p in attaches]],
                       check=True, capture_output=True, text=True)
        summary['action'] = 'created'
        summary['tag'] = tag
    else:
        names = {asset['name'] for asset in existing.get('assets') or []}
        missing_file = [p for p in attaches if p.name not in names]
        if missing_file:
            subprocess.run(['gh', 'release', 'upload', tag,
                            *[str(p) for p in missing_file]], check=True,
                           capture_output=True, text=True)
        if run:
            body = existing.get('body') or ''
            marker = f'<!-- run {run} -->'
            if marker not in body:
                body = (body.rstrip() + '\n\n' + marker + '\n'
                        + f'Ten sam instalator (SHA-256 `{summary["sha256"]}`) zbudowany '
                          f'ponownie w przebiegu CI `{run}`; bez zmian w treści.\n')
                subprocess.run(['gh', 'api', '-X', 'PATCH',
                                f'repos/{repo}/releases/{existing["id"]}',
                                '-f', f'body={body}'], check=True,
                               capture_output=True, text=True)
        summary['action'] = 'reused'
        summary['tag'] = tag
    # `Latest` ustawiamy także po ponownym użyciu: wydanie z tą samą sumą jest
    # bieżące, a GitHub potrafi trzymać jako Latest starsze oznaczenie.
    subprocess.run(['gh', 'api', '-X', 'PATCH', f'repos/{repo}/releases/tags/{tag}',
                    '-F', 'make_latest=true'], check=True, capture_output=True, text=True)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--repo', default='')
    parser.add_argument('--tag', default='')
    parser.add_argument('--title', default='')
    parser.add_argument('--notes', type=Path)
    parser.add_argument('--zip', type=Path)
    parser.add_argument('--extra', type=Path, nargs='*', default=[])
    parser.add_argument('--run', default='')
    parser.add_argument('--plan-only', action='store_true',
                        help='pokaż decyzję z listy wydań, nic nie publikuj')
    parser.add_argument('--json', action='store_true', help='wynik jako JSON (dla CI)')
    args = parser.parse_args(argv)

    label, coverage = coverages()
    if not args.zip and not args.plan_only:
        parser.error('podaj --zip (albo --plan-only)')
    digest = sha256(args.zip) if args.zip else '0' * 64
    if not args.repo:
        parser.error('podaj --repo właściciel/nazwa')

    all_releases = releases(args.repo)
    decision = decide(all_releases, digest, label)
    same_plan = [r['tag_name'] for r in all_releases
                 if plan_prefix(r) == label and installer_digest(r) == digest]
    result = {**decision,
              'title': args.title or release_title(label, coverage),
              'releases_with_this_digest': same_plan,
              'table_percent': coverage['tables']['percent_rows'],
              'scene_percent': coverage['scenes']['percent_lines']}

    if args.plan_only:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0

    if decision['action'] == 'reuse_release':
        existing = next(r for r in all_releases if r['id'] == decision['release_id'])
        publish(args.repo, existing['tag_name'], result['title'], args.notes,
                args.zip, args.extra, result, run=args.run)
    else:
        if not args.tag:
            parser.error('nowe wydanie wymaga --tag')
        if not args.notes:
            parser.error('nowe wydanie wymaga --notes')
        publish(args.repo, args.tag, result['title'], args.notes, args.zip,
                args.extra, result, run=args.run)

    print(json.dumps(result, ensure_ascii=False, indent=1) if args.json
          else f'{result["action"]}: {result["tag"]} sha256={digest}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
