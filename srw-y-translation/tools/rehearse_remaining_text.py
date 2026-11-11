#!/usr/bin/env python3
"""Próba generalna: czy przeniesiony tekst przechodzi prawdziwą bramkę importu.

`deliver_remaining_text.py` mówi, ile linii da się domknąć bez tłumacza. To
narzędzie sprawdza to **na prawdziwej bramce**, a nie „na oko”: bierze wzorzec
v8, wpisuje przeniesione brzmienia w ich własne linie `PL:`, usuwa elementy,
które zostają dla tłumacza, i przepuszcza tak powstałą „zwrotkę” przez
`one_click_patch` (`bind_all` → `plan_of` → `pl_import.import_batch`).
Jeśli bramka cokolwiek odrzuci, próba się nie liczy.

Zgodność, której pilnujemy:

* każdy przeniesiony element trafia do planu **z dokładnie tym brzmieniem**,
* żaden wiersz, który plan już ma, nie zmienia brzmienia ani nie znika,
* elementy zostawione tłumaczowi nie trafiają do planu po cichu.

    python3 tools/rehearse_remaining_text.py            # próba + podsumowanie
    python3 tools/rehearse_remaining_text.py --write    # zapis wyniku do data/
    python3 tools/rehearse_remaining_text.py --check    # porównanie z zapisem
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import check_pl_template  # noqa: E402
import deliver_remaining_text as deliver  # noqa: E402
import one_click_patch as oc  # noqa: E402
import pl_import  # noqa: E402
import release_y  # noqa: E402

RESULT = HERE / 'data' / 'remaining_text_rehearsal.json'


def released_return() -> dict:
    """The return the released plan was built from, found by the plan's own digests.

    No path and no label is hardcoded: the plan stores the SHA-256 of every file
    it was built from, so the files that reproduce those sums *are* the return —
    wherever they sit under `translations/` today. Several copies of a name may
    exist (a raw return next to an aligned one); only the matching sum counts, and
    two different files with the same name are refused rather than guessed.
    """
    plan = json.loads(release_y.load_release()['plan'].read_text(encoding='utf-8'))
    expected = plan.get('input_sha256') or {}
    if not expected:
        raise SystemExit('PRZERWANO: plan nie ma sum plików wejściowych')
    found: dict[str, str] = {}
    for path in sorted(HERE.glob('translations/**/*.md')):
        name = path.name
        if name not in expected:
            continue
        text = path.read_text(encoding='utf-8')
        if pl_import.digest(pl_import.canonical(text)) != expected[name]:
            continue
        if name in found and found[name] != pl_import.canonical(text):
            raise SystemExit(f'PRZERWANO: dwie różne zwrotki o nazwie {name}')
        found[name] = pl_import.canonical(text)
    missing = sorted(set(expected) - set(found))
    if missing:
        raise SystemExit('PRZERWANO: brak zwrotki dla ' + ', '.join(missing))
    return found


def return_texts(data: dict) -> tuple[dict, dict]:
    """The return these lines would arrive in: the released one, plus the transfers.

    `bind_v8_return` refuses anything whose structure differs from the template,
    so a return always carries **every** element — an untranslated one simply keeps
    its empty `PL:`. What this function adds is the transferred wording on its own
    element and nothing else, and counts what stays blank in each file.
    """
    filled = {(row['file'], row['element']): row['pl'] for row in data['transfer']}
    released = released_return()
    texts, blank = {}, {}
    for name, text in released.items():
        starts = [m.start() for m in deliver.ELEMENT.finditer(text)] + [len(text)]
        pieces, blanks = [text[:starts[0]]], 0
        for position in range(len(starts) - 1):
            block = text[starts[position]:starts[position + 1]]
            element = position + 1
            slot = deliver.SLOT.search(block)
            value = filled.get((name, element))
            if slot and value is not None:
                pieces.append(deliver.fill_slot(block, value))
                continue
            pieces.append(block)
            if slot and not (slot.group(1) or '').strip():
                blanks += 1
        texts[name] = ''.join(pieces)
        blank[name] = blanks
    return texts, blank


def run() -> dict:
    data = deliver.build()
    texts, blank = return_texts(data)
    template = check_pl_template.load_template(oc.TEMPLATE)
    failures = []
    manifest, appendix = oc.bind_all(texts, template)
    base = oc.plan_of(manifest, {name: texts[name] for name in manifest['files']})
    extra = {'tables': {}, 'scenes': {}}
    if appendix:
        # The appendix (`odcinek-99-dodatek.md`) has its own manifest; the release
        # merged it into the plan, so the rehearsal has to do the same.
        appendix_manifest = json.loads(oc.APPENDIX_MANIFEST.read_text(encoding='utf-8'))
        extra = pl_import.import_batch(appendix_manifest, appendix, source_dir=oc.SOURCES)
    plan = oc.merge(base, extra)

    target = {(row['file'], row['element']) for row in data['transfer']}
    released = json.loads(release_y.load_release()['plan'].read_text(encoding='utf-8'))
    rows = {}
    for section, kind in (('tables', 'table'), ('scenes', 'scene')):
        for name, entries in plan[section].items():
            for key, rec in entries.items():
                rows[(kind, name, key)] = rec

    released_rows = {}
    for section, kind in (('tables', 'table'), ('scenes', 'scene')):
        for name, entries in released[section].items():
            for key, rec in entries.items():
                released_rows[(kind, name, key)] = rec

    changed = [key for key, rec in released_rows.items()
               if key in rows and rows[key]['pl'] != rec['pl']]
    lost = [key for key in released_rows if key not in rows]
    # The transfers are *meant* to add rows; anything else that changed would be
    # a rewrite of the translator's work and is the actual failure.
    transferred_rows = set()
    for name in sorted(manifest['files']):
        spec = manifest['files'][name]
        values = [m[1] or '' for m in deliver.SLOT.finditer(texts[name])]
        for element, value in zip([e for e in spec['elements'] if e['slot']], values):
            if value:
                transferred_rows.add(deliver.row_address(element))
    unexpected = [key for key in changed if key not in transferred_rows]

    # Every transfer must be in the plan with its own wording, at the row the
    # importer resolved for that element.
    missing = []
    for name in sorted(manifest['files']):
        spec = manifest['files'][name]
        slots = [e for e in spec['elements'] if e['slot']]
        values = [m[1] or '' for m in deliver.SLOT.finditer(texts[name])]
        for element, value in zip(slots, values):
            row = element['row']
            key = ((('table', row['table'], row['key'])) if row['import_kind'] == 'table'
                   else ('scene', row['file'], row['id'].rsplit(':', 1)[1]))
            if not value:
                continue
            got = rows.get(key, {}).get('pl')
            if got != pl_import.layout(value, row):
                missing.append({'file': name, 'row': key[2], 'expected': value,
                                'got': '' if got is None else got})

    return {
        'schema': 1,
        'label': data['label'],
        'plan_sha256': data['plan_sha256'],
        'gate': 'one_click_patch.bind_all + pl_import.import_batch',
        'summary': {
            'transferred': data['summary']['transferred'],
            'left_for_translator': data['summary']['left_for_translator'],
            'return_files': len(texts),
            'elements_left_blank_in_return': sum(blank.values()),
            'plan_rows_after_rehearsal': len(rows),
            'released_rows': len(released_rows),
            'rows_added_by_transfer': len(transferred_rows - set(released_rows)),
            'rows_wording_changed': len(changed),
            'rows_changed_outside_transfer': len(unexpected),
            'rows_lost': len(lost),
            'transfers_not_landed': len(missing),
        },
        'changed_outside_transfer': unexpected[:20],
        'lost_rows': lost[:20],
        'transfers_not_landed': missing[:20],
        'blank_per_file': dict(sorted(blank.items())),
        'passed': not (unexpected or lost or missing),
        'failures': failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = run()
    except pl_import.ImportFailure as exc:
        print('BRAMKA ODRZUCIŁA PRÓBĘ:\n' + str(exc), file=sys.stderr)
        return 2
    text = json.dumps(result, ensure_ascii=False, indent=1) + '\n'
    if args.write:
        RESULT.write_text(text, encoding='utf-8')
        print(f'zapisane: {RESULT.relative_to(HERE)}')
    if args.check:
        if RESULT.read_text(encoding='utf-8') != text:
            print('ROZJAZD: data/remaining_text_rehearsal.json nie odpowiada próbie')
            return 1
        print('OK: próba generalna zgodna z zapisem')
    print(json.dumps(result['summary'], ensure_ascii=False, indent=1))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
