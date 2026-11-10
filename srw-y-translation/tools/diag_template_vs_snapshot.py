#!/usr/bin/env python3
"""Diagnose where the committed translator template and the S6-full snapshot disagree.

Why this tool exists: `bind_v8_return.py` refuses a whole batch when *any*
displayed Japanese line differs from the numbered S6-full record. That refusal
is correct — it is our only proof that a returned line lands on the right
record — but it says nothing about *who* is wrong. This tool answers that
question separately: it renders the committed template (`translations/template-v8/`
plus the v8.1 appendix) against the snapshot and lists every element whose
displayed JP or EN differs, with the corpus row, the string id and the kind of
difference.

It is a diagnostic only. It never writes to the template, the snapshot or a
return, and a clean result here is *not* permission to skip `bind_v8_return.py`.

Usage (in `srw-y-translation/`):

    python3 tools/diag_template_vs_snapshot.py --out data/template_snapshot_diff_y.json
    python3 tools/diag_template_vs_snapshot.py            # same, JSON on stdout
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import bind_v8_return as binder
import build_translator_package as renderer
from check_pl_template import load_template
from pl_import import SLOT, canonical

HERE = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = HERE / 'data' / 's6-full'
DEFAULT_TEMPLATE = HERE / 'translations' / 'template-v8'
DEFAULT_APPENDIX = HERE / 'translations' / 'patch-v8-1' / 'odcinek-99-dodatek.md'

# The binder's heading only accepts `## Scena 12/611 — …`. The v8.1 appendix numbers its
# scenes per file (`## Scena D1/6 — …`), so a scan that used the binder's pattern alone
# would skip all 299 appendix elements without saying a word.
APPENDIX_HEADING = re.compile(r'^## Scena \S+ — (cse\S+)$', re.M)


def _displayed(block: str) -> tuple[str, str]:
    """Return the displayed JP and EN of one rendered element, as the template prints them."""
    limit = re.search(r'^   limit: .+$', block, re.M)
    slots = list(SLOT.finditer(block))
    jp = block[:limit.start()].rstrip('\n') if limit else block
    head, _, rest = jp.partition('\n')
    jp = head.split('] ', 1)[1] + ('\n' + rest if rest else '') if '] ' in head else jp
    en = ''
    if slots:
        start = re.search(r'^   EN:(?: .*)?$', block, re.M)
        if start:
            en = block[start.start():slots[0].start()].rstrip('\n')[len('   EN: '):]
    return jp, en


def _expected(row: dict) -> tuple[str, str]:
    jp = '\n'.join(renderer.render_text('', row['jp'])) if row.get('jp') else ''
    en = ('\n'.join(renderer.render_text('', row['en'])) if row.get('en')
          else '(brak wersji angielskiej w grze)')
    return jp, en


def _classify(a: str, b: str) -> str:
    """Triage label so a human can sort the list without reading both strings."""
    strip = lambda s: s.replace('\u3000', '').replace(' ', '').replace('\n', '')
    return 'tylko biale znaki' if strip(a) == strip(b) else 'inna tresc'


def _check(block: str, row: dict, name: str, number: int) -> tuple[str, str] | None:
    """Ask the real gate. Returns None when it would accept, else (field, reason)."""
    try:
        binder.validate_rendered(block, row, name, number)
        return None
    except Exception as error:  # the gate raises ImportFailure; keep the reason verbatim
        message = str(error)
        field = 'en' if 'EN nie odpowiada' in message or 'brak EN' in message else 'jp'
        reason = message.split(': ', 1)[-1].strip() if ': ' in message else message
        return field, reason


def _record(findings: list, counts: dict, block: str, row: dict, name: str,
            scene: str | None, number: int, row_id: str) -> bool:
    """Record one element; returns True when the gate accepts it unchanged."""
    verdict = _check(block, row, name, number)
    if verdict is None:
        return True
    field, reason = verdict
    counts[field] += 1
    jp, en = _displayed(block)
    exp_jp, exp_en = _expected(row)
    shown, expected = (jp, exp_jp) if field == 'jp' else (en, exp_en)
    findings.append({'plik': name, 'scena': scene, 'element': number, 'wiersz': row_id,
                     'pole': field, 'klasa': _classify(shown, expected),
                     'powod': reason, 'szablon': shown, 'snapshot': expected})
    return False


def scan(template: dict[str, str], source_dir: Path, appendix: Path | None) -> dict:
    old = renderer.SCENARIO
    try:
        renderer.SCENARIO = source_dir / 'scenario.jsonl'
        scenes = {scene['key']: scene for scene in renderer.load_scenes()}
    finally:
        renderer.SCENARIO = old
    tables = renderer.read_jsonl(source_dir / 'tables.jsonl')
    views: dict[str, list] = {}
    renderer.build_view_files(tables, {}, records=views)

    texts = dict(template)

    findings: list[dict] = []
    counts = {'pliki': 0, 'elementy': 0, 'jp': 0, 'en': 0, 'wiersz': 0, 'zgodne': 0}
    per_file: dict[str, int] = {}
    for name in sorted(texts):
        text = texts[name]
        counts['pliki'] += 1
        per_file[name] = 0
        scenes_in_file = list(binder.HEADING.finditer(text))
        if scenes_in_file:
            for index, heading in enumerate(scenes_in_file):
                stop = (scenes_in_file[index + 1].start()
                        if index + 1 < len(scenes_in_file) else len(text))
                section = text[heading.end():stop]
                scene = scenes.get(heading[1])
                starts = [m.start() for m in binder.ELEMENT.finditer(section)] + [len(section)]
                for start, end in zip(starts, starts[1:]):
                    counts['elementy'] += 1
                    per_file[name] += 1
                    block = section[start:end]
                    number = int(re.match(r'\d+', block)[0])
                    if not scene or number > len(scene['rows']):
                        findings.append({'plik': name, 'scena': heading[1], 'element': number,
                                         'wiersz': None, 'pole': 'wiersz',
                                         'klasa': 'brak wiersza w snapshocie'})
                        counts['wiersz'] += 1
                        continue
                    row = scene['rows'][number - 1]
                    counts['zgodne'] += _record(findings, counts, block, row, name,
                                                heading[1], number, row['id'])
        elif name in views:
            rows = views[name]
            starts = [m.start() for m in binder.ELEMENT.finditer(text)] + [len(text)]
            for index, (start, end) in enumerate(zip(starts, starts[1:])):
                counts['elementy'] += 1
                per_file[name] = per_file.get(name, 0) + 1
                block = text[start:end]
                number = int(re.match(r'\d+', block)[0])
                if number > len(rows):
                    findings.append({'plik': name, 'scena': None, 'element': number,
                                     'wiersz': None, 'pole': 'wiersz',
                                     'klasa': 'brak wiersza w snapshocie'})
                    counts['wiersz'] += 1
                    continue
                row = rows[number - 1]
                counts['zgodne'] += _record(findings, counts, block, row, name, None,
                                            number, f"{row.get('table')}:{row.get('key')}")

    if appendix and appendix.is_file():
        counts['pliki'] += 1
        name = appendix.name
        per_file[name] = 0
        rows = [row for scene in renderer.APPENDIX_SCENES for row in scene['rows']]
        if not rows:
            raise SystemExit('doklejka v8.1 istnieje, ale APPENDIX_SCENES jest puste — '
                             'load_scenes() nie rozpoznał pliku dodatku')
        text = canonical(appendix.read_text(encoding='utf-8-sig'))
        starts = [m.start() for m in binder.ELEMENT.finditer(text)] + [len(text)]
        for number, (start, end) in enumerate(zip(starts, starts[1:]), 1):
            counts['elementy'] += 1
            per_file[name] += 1
            if number > len(rows):
                findings.append({'plik': name, 'scena': None, 'element': number,
                                 'wiersz': None, 'pole': 'wiersz',
                                 'klasa': 'brak wiersza w snapshocie'})
                counts['wiersz'] += 1
                continue
            row = rows[number - 1]
            counts['zgodne'] += _record(findings, counts, text[start:end], row, name, None,
                                        number, row['id'])

    by_file: dict[str, int] = {}
    for finding in findings:
        by_file[finding['plik']] = by_file.get(finding['plik'], 0) + 1
    skipped = sorted(name for name, seen in per_file.items() if not seen)
    return {
        'schema': 1,
        'kind': 'diagnostic_template_vs_s6full',
        'pliki_bez_elementow': skipped,
        'note': ('Diagnostyka, nie zgoda na pominięcie bind_v8_return. Kazda roznica '
                 'oznacza, ze wyslany tlumaczowi wzorzec i nasz snapshot S6-full '
                 'pokazuja inny tekst na tym samym numerze elementu.'),
        'counts': counts,
        'findings_by_file': dict(sorted(by_file.items())),
        'findings': findings,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--template', type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument('--appendix', type=Path, default=DEFAULT_APPENDIX)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(argv)

    report = scan(load_template(args.template), args.source_dir, args.appendix)
    text = json.dumps(report, ensure_ascii=False, indent=1) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding='utf-8')
        print(json.dumps(report['counts'], ensure_ascii=False))
        print(json.dumps(report['findings_by_file'], ensure_ascii=False))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
