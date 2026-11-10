#!/usr/bin/env python3
"""Jedno polecenie: zwrotka tłumacza (`Y_PLn.zip`) → gotowy patch do gry.

Po co to istnieje. Wracająca rozmowa „czy to już pełne?” brała się z tego, że patch
był składany z kilku ręcznych kroków, a każdy krok mógł coś po cichu pominąć
(albo agent mógł o nim zapomnieć). Tutaj cała droga jest jednym poleceniem,
a wszystko, czego potrzebuje, leży w repozytorium:

* **wzorzec v8** — `translations/template-v8/` (numeracja i limity pól),
* **źródła gry** — `data/s6-full/` + `data/s6-extra/` (japoński i angielski tekst),
* **dodatek v8.1** — `translations/patch-v8-1/import_manifest.json`,
* **indeks bundli** — `data/game_text_bundle_index.json` (gdzie leży każda scena),
* **narzędzia** — `tools/` (importer, wiązanie, audyt, builder paczki).

Co robi z każdym plikiem zwrotki:

1. wyrównanie do wzorca po **japońskim zdaniu** (`realign_return`), gdy plik
   powstał przed poprawką numeracji — nigdy po numerze wiersza,
2. wiązanie ze wzorcem (`bind_v8_return.bind`) — plik, którego nie ma we wzorcu,
   idzie do dodatku przez własny manifest; jeśli nie pasuje i tam, praca staje,
3. import przez tę samą bramkę co zawsze (`pl_import.import_batch`): tokeny,
   limity, układ — pusty slot zostaje pusty, nic nie jest zgadywane,
4. złożenie **jednego** planu (baza + dodatek) z kontrolą kolizji wierszy,
5. audyt pokrycia wobec korpusu gry: ile linii scenariusza i wierszy tabel
   wychodzi po polsku, a ile zostaje oryginalnych,
6. paczka (`build_y_release`) + opcjonalnie publikacja na Dysk.

Czego to narzędzie **nie** robi: nie tłumaczy. Tekst pochodzi wyłącznie od
tłumacza; agent może poprawić linię tylko wtedy, gdy wymusza to limit pola i
taka poprawka jest zapisana jako korekta z uzasadnieniem.

    python3 tools/one_click_patch.py --return Y_PL4.zip --label PL8
    python3 tools/one_click_patch.py --return Y_PL4.zip --label PL8 --out build/PL8
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import bind_v8_return  # noqa: E402
import build_y_release  # noqa: E402
import check_pl_template  # noqa: E402
import pl_import  # noqa: E402
import normalize_return  # noqa: E402
import realign_return  # noqa: E402
import s6_extra  # noqa: E402
from apply_y_plan import jobs_for, name_jobs, still_missing  # noqa: E402

TEMPLATE = HERE / 'translations' / 'template-v8'
APPENDIX_MANIFEST = HERE / 'translations' / 'patch-v8-1' / 'import_manifest.json'
APPENDIX_FILE = 'odcinek-99-dodatek.md'
SOURCES = HERE / 'data' / 's6-full'
INDEX = HERE / 'data' / 'game_text_bundle_index.json'


def log(message: str) -> None:
    print(message, flush=True)


def align(returned: dict, template: dict, workdir: Path) -> tuple[dict, set]:
    """Pliki powstałe przed poprawką numeracji wyrównuje po japońskim zdaniu."""
    raw, changed = {}, []
    for name, text in returned.items():
        body = pl_import.canonical(text)
        base = template.get(name)
        if base is not None and pl_import.SLOT.sub('   PL:', body) != base:
            raw[name] = body
            changed.append(name)
        else:
            raw[name] = body
    if not changed:
        return returned, set()
    source, target = workdir / 'raw', workdir / 'aligned'
    source.mkdir(parents=True, exist_ok=True)
    for name in changed:
        (source / name).write_text(raw[name], encoding='utf-8')
    realign_return.main(['--input', str(source), '--output', str(target)])
    aligned = pl_import.read_returns(target)
    log(f'wyrównane do wzorca: {len(changed)} plików ({", ".join(sorted(changed))})')
    # zwrotka w repo ma być po wyrównaniu — inaczej „surowa” i „wydana” znów się rozjadą
    result = dict(returned)
    result.update(aligned)
    return result, set(changed)


def bind_all(returned: dict, template: dict) -> tuple[dict, dict]:
    """Zwraca `(manifest bazowy, manifesty dodatków)`; nic nie ginie po cichu."""
    base = {name: text for name, text in returned.items() if name in template}
    extras = {name: text for name, text in returned.items() if name not in template}
    manifest = bind_v8_return.bind(template, base, SOURCES) if base else None
    appendix = {}
    if extras:
        known = json.loads(APPENDIX_MANIFEST.read_text(encoding='utf-8'))['files']
        for name in sorted(extras):
            if name not in known:
                raise ImportFailure(f'{name}: nie ma go ani we wzorcu v8, ani w dodatku')
            appendix[name] = extras[name]
        if set(appendix) != set(known):
            missing = sorted(set(known) - set(appendix))
            raise ImportFailure('dodatek niepełny, brakuje: ' + ', '.join(missing))
    return manifest, appendix


class ImportFailure(RuntimeError):
    pass


def plan_of(manifest: dict | None, returned: dict) -> dict:
    if manifest is None:
        return {'tables': {}, 'scenes': {}}
    return pl_import.import_batch(manifest, returned, source_dir=SOURCES)


def merge(base: dict, extra: dict) -> dict:
    merged = {'schema': 1, 'tables': {name: dict(rows) for name, rows in base['tables'].items()},
              'scenes': {name: dict(rows) for name, rows in base['scenes'].items()}}
    for name, rows in extra['tables'].items():
        for key, row in rows.items():
            if key in merged['tables'].get(name, {}) and merged['tables'][name][key] != row:
                raise ImportFailure(f'kolizja tabeli {name} {key}')
            merged['tables'].setdefault(name, {})[key] = row
    for name, rows in extra['scenes'].items():
        for key, row in rows.items():
            if key in merged['scenes'].get(name, {}) and merged['scenes'][name][key] != row:
                raise ImportFailure(f'kolizja sceny {name} {key}')
            merged['scenes'].setdefault(name, {})[key] = row
    merged['accepted'] = (sum(len(rows) for rows in merged['tables'].values())
                          + sum(len(rows) for rows in merged['scenes'].values()))
    return merged


def coverage(plan: dict) -> dict:
    """Ile linii gry wychodzi po polsku — liczone wobec korpusu, nie z planu."""
    rows = [row for row in s6_extra.load(SOURCES / 'scenario.jsonl')
            if (row.get('jp') or '').strip()]
    translated = sum(1 for row in rows
                     if (plan['scenes'].get(row['file'], {}).get(row['id'].rsplit(':', 1)[1], {})
                         .get('pl') or '').strip())
    tables = [json.loads(line) for line in
              (SOURCES / 'tables.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    table_rows = [row for row in tables if (row.get('jp') or '').strip()]
    table_done = sum(1 for row in table_rows if (plan['tables'].get(row['table'], {})
                                                 .get(row['key'], {}).get('pl')))
    return {'scene_lines': len(rows), 'scene_lines_translated': translated,
            'scene_percent': round(translated / len(rows) * 100, 2) if rows else 100.0,
            'table_rows': len(table_rows), 'table_rows_translated': table_done,
            'table_percent': round(table_done / len(table_rows) * 100, 2) if table_rows else 100.0}


def find_corrections(returned: dict, given: Path | None) -> dict | None:
    """Korekty pasujące do **tej** zwrotki, po sumach; inaczej brak korekt.

    Korekty to zapis decyzji tłumacza/agenta o skrótach wymuszonych limitem pola —
    bez nich importer słusznie odrzuca zwrotkę. Szukamy ich w repo po
    `input_sha256`, więc nowa zwrotka od tłumacza nie odziedziczy cudzych.
    """
    hashes = {name: pl_import.digest(pl_import.canonical(text)) for name, text in returned.items()}
    candidates = [given] if given else sorted(HERE.glob('translations/*/*/CORRECTIONS.json')) + sorted(
        HERE.glob('translations/*/CORRECTIONS.json'))
    for path in candidates:
        data = json.loads(path.read_text(encoding='utf-8'))
        stored = data.get('input_sha256') or {}
        if stored and all(hashes.get(name) == value for name, value in stored.items()):
            data['source'] = str(path.relative_to(HERE))
            return data
    return None


def template_manifest(template: dict, returned: dict) -> dict:
    """Manifest tylko do nałożenia korekt (indeksy elementów), nie do importu."""
    return bind_v8_return.bind(template, {name: text for name, text in returned.items()
                                          if name in template}, SOURCES)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--return', dest='returns', type=Path, nargs='+', required=True,
                        help='zwrotka: ZIP, katalog albo pliki .md')
    parser.add_argument('--label', required=True, help='etykieta wydania, np. PL8')
    parser.add_argument('--out', type=Path, default=HERE / 'build' / 'one_click')
    parser.add_argument('--corrections', type=Path,
                        help='plik korekt; bez podania: szukany automatycznie po sumach zwrotki')
    parser.add_argument('--keep-return', action='store_true',
                        help='skopiuj zwrotkę do translations/<etykieta>/PL (domyślnie: tak)')
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    returned = {}
    for path in args.returns:
        returned.update(pl_import.read_returns(path))
    log(f'zwrotka: {len(returned)} plików')

    template = check_pl_template.load_template(TEMPLATE)
    with tempfile.TemporaryDirectory() as temporary:
        returned, realigned = align(returned, template, Path(temporary))
    corrections = find_corrections(returned, args.corrections)
    if corrections is not None:
        returned, changed = normalize_return.normalise(
            template_manifest(template, returned), returned, corrections)
        log(f'korekty: {len(corrections["entries"])} w {changed} plikach '
            f'({corrections.get("source", "podane")})')
    manifest, appendix = bind_all(returned, template)
    log(f'związane z wzorcem v8: {len(manifest["files"]) if manifest else 0} plików; '
        f'plików dodatku: {len(appendix)}')

    base = plan_of(manifest, {name: returned[name] for name in (manifest or {}).get('files', {})})
    extra = {'tables': {}, 'scenes': {}}
    if appendix:
        appendix_manifest = json.loads(APPENDIX_MANIFEST.read_text(encoding='utf-8'))
        extra = pl_import.import_batch(appendix_manifest, appendix, source_dir=SOURCES)
    plan = merge(base, extra)

    report = {
        'schema': 1, 'kind': 'full_return_verified', 'runtime_tested': False,
        'return_label': args.label,
        'input_sha256': {name: pl_import.digest(pl_import.canonical(text))
                         for name, text in returned.items()},
        'manifest_sha256': (pl_import.digest(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
                            if manifest else None),
        'accepted_records_including_repeats': plan['accepted'],
        'nonempty_slots': sum(1 for manifest_part in (base, extra)
                              for rows in list(manifest_part['scenes'].values())
                              + list(manifest_part['tables'].values())
                              for row in rows.values() if row.get('pl')),
        'empty_slots': (base.get('empty_slots', 0) + extra.get('empty_slots', 0)),
        'quarantined_slots': 0, 'historical_quarantined_groups': 0,
        'historical_diagnostics': 0, 'overrides_applied': 0, 'entries': [],
        'coverage': coverage(plan),
        'realigned_files': sorted(realigned),
        'bundle_by_name': [],
    }
    plan['input_sha256'] = report['input_sha256']
    plan['manifest_sha256'] = report['manifest_sha256']
    plan['overrides_applied'] = 0
    plan['empty_slots'] = report['empty_slots']
    plan['runtime_tested'] = False
    plan_bytes = (json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    report['plan_sha256'] = hashlib.sha256(plan_bytes).hexdigest()
    plan_path = out / f'PLAN_{args.label}.json'
    report_path = out / f'AUDIT_{args.label}.json'
    plan_path.write_bytes(plan_bytes)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    index = json.loads(INDEX.read_text(encoding='utf-8'))
    jobs = jobs_for(plan, index)
    missing = still_missing(plan, index, jobs)
    if missing:
        raise ImportFailure('plan tłumaczy sceny bez adresu w grze: ' + ', '.join(missing))
    by_name = sorted({item['name'] for item in name_jobs(plan, jobs)})
    report['bundle_by_name'] = by_name
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    log(f'bundli do załatania: {len(jobs)} (w tym {len(by_name)} obiektów po nazwie)')

    archive = out / f'SRW_Y_PATCH_{args.label}.zip'
    built = build_y_release.build(plan_path, report_path, INDEX, archive)
    log(json.dumps(built, ensure_ascii=False, indent=1))
    log('pokrycie: ' + json.dumps(report['coverage'], ensure_ascii=False))
    if args.keep_return:
        target = HERE / 'translations' / args.label.lower() / 'PL'
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        for name, text in sorted(returned.items()):
            (target / name).write_text(text, encoding='utf-8')
        log(f'zwrotka zapisana w repo: {target.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ImportFailure, pl_import.ImportFailure) as exc:
        print(f'PRZERWANO: {exc}', file=sys.stderr)
        raise SystemExit(2)
