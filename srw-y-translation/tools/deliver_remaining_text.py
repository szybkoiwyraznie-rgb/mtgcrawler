#!/usr/bin/env python3
"""Brakujący tekst: paczka dla tłumacza + przeniesienie tego, co już przetłumaczone.

Do 2026-11-11 brakowało narzędzia, które odpowiada na pytanie „co mam wysłać
tłumaczowi i co da się domknąć bez niego”. To narzędzie robi **dwie** rzeczy,
rozłączne i sprawdzalne:

1. **Paczka dla tłumacza** (`sceny/`) — tylko elementy **bez** polskiego tekstu
   w aktualnym planie, z tymi samymi numerami, limitami i kluczami co wzorzec
   v8. Tłumacz wraca plikami `.md` i wchodzą one tą samą drogą co zwrotka PL3
   (`one_click_patch.py` → `pl_import`: tokeny, limity, układ, dozwolone znaki).
   Paczka domyka **wyłącznie** brakujące linie; nic przetłumaczonego nie wraca
   do tłumacza.

2. **Przeniesienie bez nowego tekstu** (`transfer.json` + `CORRECTIONS.json`) —
   brakująca linia, której japoński tekst ma w planie **dokładnie jedno**
   polskie brzmienie, dostaje to brzmienie. Zasady, których nie wolno złamać:

   * tekst japoński musi się zgadzać **co do znaku**,
   * polskie brzmienie musi być **jedno** — teksty z kilkoma brzmieniami
     (「うん…」 → 「Ano…」/「Dobrze…」/「Mhm…」) zostają dla tłumacza i są
     policzone osobno, bo wybór zależy od mówcy i sceny,
   * kandydat nie może być identyczny z japońskim źródłem (to nie jest przekład),
   * kandydat musi przejść **tę samą bramkę** co zwrotka (`validate_text`),
   * każdy przeniesiony wiersz trafia do `CORRECTIONS.json` z japońskim
     oryginałem, sumą i powodem, więc widać dokładnie, czym różni się zwrotka
     od planu; narzędzie **nigdy** nie podmienia brzmienia, które tłumacz już
     napisał.

   To **nie jest tłumaczenie**: to użycie tego samego zdania tam, gdzie gra ma
   to samo zdanie i tłumacz dał mu jedno brzmienie. Wiersze, których nie da się
   przenieść bezpiecznie, **zostają w paczce dla tłumacza** — jeden niepokryty
   wiersz nie może zniknąć.

    python3 tools/deliver_remaining_text.py --write      # do repo
    python3 tools/deliver_remaining_text.py --check      # porównanie z repo
    python3 tools/deliver_remaining_text.py              # tylko liczby
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import pl_import  # noqa: E402
import release_y  # noqa: E402
import s6_extra  # noqa: E402

TEMPLATE = HERE / 'translations' / 'template-v8'
SCENARIO = HERE / 'data' / 's6-full' / 'scenario.jsonl'
TABLES = HERE / 'data' / 's6-full' / 'tables.jsonl'
OUT_DIR = HERE / 'translations' / 'pl-remaining'
TRANSFER = OUT_DIR / 'transfer.json'
CORRECTIONS = OUT_DIR / 'CORRECTIONS.json'
PACKAGE_DIR = OUT_DIR / 'sceny'
SUMMARY = HERE / 'data' / 'remaining_text_y.json'

ELEMENT = pl_import.ELEMENT
SLOT = pl_import.SLOT
LIMIT = pl_import.LIMIT
EN_LINE = re.compile(r'(?m)^   EN:(?: (.*))?$')
HEADER_PREFIX = re.compile(r'\d+\. \[[^\]\n]*\](?: )?')


def element_japanese(block: str) -> tuple[str, str]:
    """(how the text was found, the game text of this element).

    The Japanese sits between the `N. [label] ` header prefix and the `limit:`
    line — **including** the part on the header line itself. Elements whose
    Japanese the package never carried show `EN:` only and are matched by it.
    """
    limit = LIMIT.search(block)
    prefix = HEADER_PREFIX.match(block)
    if limit and prefix and not prefix.group().startswith('\n'):
        body = block[prefix.end():limit.start()].rstrip('\n')
        if body.strip():
            return 'body', body
    en = EN_LINE.search(block)
    if en and (en.group(1) or '').strip():
        return 'en', en.group(1)
    return 'none', ''


class DeliveryError(RuntimeError):
    """Niespójność danych — kończymy pracę, zamiast po cichu coś pominąć."""


def memory_index(plan: dict) -> dict[str, set]:
    """Rendered Japanese text → every Polish wording the released plan gives it.

    The plan carries the source and the wording side by side, so the index is
    built from it alone — no corpus lookup can silently drop a table row, where
    the plan keys rows by their bundle key rather than by scene file.
    """
    import build_translator_package as renderer
    pairs: dict[str, set] = collections.defaultdict(set)
    for section in ('scenes', 'tables'):
        for entries in plan[section].values():
            for rec in entries.values():
                jp = (rec.get('jp') or '')
                pl = (rec.get('pl') or '').strip()
                if jp and pl:
                    pairs['jp:' + '\n'.join(renderer.render_text('', jp))].add(pl)
    return pairs


def transcript() -> None:
    """Register every rendered game text, so a block can be matched to its row.

    Both languages: an element whose Japanese the package never carried shows
    `EN:` only and is matched by that English line. Rows are streamed and only
    the rendered strings are kept — the source rows themselves are 180 000 dicts
    and would cost far more memory than the lookup is worth.
    """
    import build_translator_package as renderer
    for field in _RENDERED:
        _RENDERED[field].clear()
    # Table strings live beside the script, not inside it: a view element is
    # matched against `tables.jsonl`, a scene element against `scenario.jsonl`.
    for path in (SCENARIO, TABLES):
        for row in s6_extra.load(path):
            for field in ('jp', 'en'):
                value = row.get(field)
                if not value:
                    continue
                # The `.md` shows the text after `N. [speaker] ` with continuation
                # lines indented by three spaces; that rendering is what a block
                # is compared against.
                # 16-byte digests instead of the strings: the whole corpus is
                # ~200 000 rendered texts and the strings alone cost hundreds of
                # megabytes, which is enough to get the test process killed.
                _RENDERED[field].add(_fingerprint('\n'.join(
                    renderer.render_text('', value))))


def template_blocks() -> dict:
    """Per template file: ordered element blocks with their slot, limit and source text."""
    result = {}
    for sub in ('sceny', 'widoki'):
        for path in sorted((TEMPLATE / sub).glob('*.md')):
            text = pl_import.canonical(path.read_text(encoding='utf-8'))
            starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
            blocks = []
            for i in range(len(starts) - 1):
                block = text[starts[i]:starts[i + 1]]
                limit = LIMIT.search(block)
                slot = SLOT.search(block)
                kind_of_source, source = element_japanese(block)
                en = EN_LINE.search(block)
                blocks.append({
                    'block': block,
                    'slot': bool(slot),
                    'slot_value': (slot.group(1) or '') if slot else '',
                    'limit': int(limit[1]) if limit else None,
                    'source_kind': kind_of_source,
                    'source': source,
                    'en': (en.group(1) or '') if en else '',
                })
            result[f'{sub}/{path.name}'] = {'text': text, 'blocks': blocks,
                                            'kind': sub, 'name': path.name}
    return result


# Rendered source text → the corpus rows that show exactly it. Only **whole**
# strings are matched: an element block can be half of a two-language line
# (``「主人公は男性」/「主人公は女性」`` is one row with both halves), and borrowing
# the whole wording for one half would put the other half on a line that does not
# show it. A fragment simply stays for the translator.
_RENDERED = {'jp': set(), 'en': set()}


def _fingerprint(text: str) -> bytes:
    """16 bytes per rendered string: the corpus index holds ~200 000 of them."""
    return hashlib.blake2b(text.encode('utf-8'), digest_size=16).digest()


def shows_source(text: str, field: str = 'jp') -> bool:
    """Is `text` exactly what some corpus row shows in that language?"""
    return _fingerprint(text) in _RENDERED[field]


def decide(jp: str, limit: int | None, wordings: dict[str, set],
           field: str = 'jp') -> dict:
    """Can this missing line be filled with a wording the translator already wrote?"""
    if not jp.strip():
        return {'action': 'leave', 'reason': 'element bez tekstu źródłowego'}
    if not shows_source(jp, field):
        return {'action': 'leave', 'reason': 'brak tekstu w korpusie gry'}
    seen = set(wordings.get(f'{field}:{jp}', set()))
    if not seen:
        return {'action': 'leave', 'reason': 'brak polskiego odpowiednika w planie'}
    if len(seen) > 1:
        return {'action': 'leave',
                'reason': 'kilka polskich brzmień — wybór zależy od mówcy i sceny'}
    value = next(iter(seen))
    if value == jp:
        return {'action': 'leave', 'reason': 'polskie brzmienie identyczne z japońskim'}
    try:
        pl_import.validate_text(value, jp, limit)
    except pl_import.ImportFailure as exc:
        return {'action': 'leave', 'reason': f'bramka importu: {exc}'}
    return {'action': 'transfer', 'pl': value}


def fill_slot(block: str, value: str) -> str:
    """Put the wording into the element's own `PL:` line, leaving the rest untouched."""
    marker = SLOT.search(block)
    if not marker:
        raise DeliveryError('element bez slotu PL nie może dostać tekstu')
    return block[:marker.start()] + f'   PL: {value}' + block[marker.end():]


def template_manifest(templates: dict) -> dict:
    """The v8 manifest for the template itself — the address the importer resolves.

    It is built by the same `bind_v8_return` the one-click pipeline uses, so an
    element number here is the same element number the importer will see. That
    matters for repeat elements: the template's own content decides which of
    them carry a `PL:` slot, and the numbering must not drift from it.
    """
    import check_pl_template
    import one_click_patch as oc
    # `bind_all` names files without the `sceny/`/`widoki/` prefix the template
    # directory uses, so the flat name is what has to go in.
    files = {template['name']: template['text'] for template in templates.values()}
    template = check_pl_template.load_template(oc.TEMPLATE)
    manifest, appendix = oc.bind_all(files, template)
    if appendix:
        raise DeliveryError('wzorzec v8 nie może zawierać plików dodatku')
    return manifest


def plan_state(plan: dict) -> tuple[dict, dict]:
    """`(rows already translated, rows the plan leaves blank)` keyed by game row."""
    filled, blank = {}, {}
    for section, kind in (('tables', 'table'), ('scenes', 'scene')):
        for name, entries in plan[section].items():
            for key, rec in entries.items():
                address = (kind, name, key)
                if (rec.get('pl') or '').strip():
                    filled[address] = rec['pl']
                else:
                    blank[address] = rec
    return filled, blank


def row_address(element: dict) -> tuple[str, str, str]:
    """The `(kind, file-or-table, key)` the plan stores this element under."""
    row = element['row']
    if row['import_kind'] == 'table':
        return 'table', row['table'], row['key']
    return 'scene', row['file'], row['id'].rsplit(':', 1)[1]


def build() -> dict:
    """Render the package and the transfer from the released plan."""
    current = release_y.load_release()
    plan = json.loads(current['plan'].read_text(encoding='utf-8'))
    report = json.loads(current['report'].read_text(encoding='utf-8'))
    transcript()  # fills `_RENDERED`, used by `window()` below
    wordings = memory_index(plan)
    templates = template_blocks()
    manifest = template_manifest(templates)
    translated, _blank_rows = plan_state(plan)
    # Not every template file was ever sent back: PL9's plan records the digests
    # of 27 files, so an element outside them has no returned text at all. That is
    # a different job from a file the translator has and left blank, and the two
    # have to be counted apart.
    returned_files = set((plan.get('input_sha256') or {}))

    transfers, packages = [], {}
    counters = collections.Counter()
    reasons = collections.Counter()
    for key, template in templates.items():
        kind, name = template['kind'], template['name']
        spec = manifest['files'][name]
        remaining = []
        for position, (info, element) in enumerate(
                zip(template['blocks'], spec['elements'])):
            index = position + 1
            if not element['slot']:
                continue  # repeats inherit the wording of their root element
            address = row_address(element)
            if address in translated:
                counters['already_translated'] += 1
                continue
            # A row the release leaves blank but whose element number has no
            # `PL:` line cannot be addressed from a return at all; it is a source
            # mismatch, not something the translator can fill, so it is counted
            # instead of being put in the package.
            if not info['slot']:
                counters['unaddressable'] += 1
                reasons['wiersz planu bez linii PL w tym miejscu wzorca'] += 1
                continue
            decision = decide(info['source'].strip(), info['limit'], wordings,
                              'en' if info['source_kind'] == 'en' else 'jp')
            if decision['action'] == 'transfer':
                transfers.append({'file': name, 'kind': kind, 'element': index,
                                  'source_kind': info['source_kind'],
                                  'jp': info['source'], 'pl': decision['pl'],
                                  'limit': info['limit'],
                                  'row': list(address)})
                counters['transferred'] += 1
                info['filled'] = decision['pl']
            else:
                reasons[decision['reason']] += 1
                counters['left_for_translator'] += 1
                counters['left_in_returned_file' if name in returned_files
                         else 'left_in_file_never_returned'] += 1
                remaining.append(info['block'])
        if remaining:
            packages[name] = render_package(name, kind, remaining)

    return {
        'schema': 1,
        'label': current['label'],
        'plan_sha256': report.get('plan_sha256'),
        'summary': {
            'transferred': counters['transferred'],
            'left_for_translator': counters['left_for_translator'],
            'left_in_returned_file': counters['left_in_returned_file'],
            'left_in_file_never_returned': counters['left_in_file_never_returned'],
            'already_translated': counters['already_translated'],
            'unaddressable': counters['unaddressable'],
            'package_files': len(packages),
            'leave_reasons': dict(sorted(reasons.items())),
        },
        'transfer': transfers,
        'packages': {name: hashlib.sha256(text.encode('utf-8')).hexdigest()
                     for name, text in sorted(packages.items())},
        '_package_texts': packages,
        '_returned_files': returned_files,
    }


def render_package(name: str, kind: str, blocks: list[str]) -> str:
    title = ('Brakujące linie scenariusza' if kind == 'sceny'
             else 'Brakujące teksty widoków (tabel)')
    lines = [
        f'# {name} — {title} — SRW Y',
        '',
        'Ten plik zawiera **tylko elementy bez polskiego tekstu**. Klucze i limity są',
        'te same co we wzorcu v8. Polski wpisujesz w jednej linii po `PL:`.',
        '',
        'Numeracja zaczyna się od nowa w każdej scenie (`## Scena …`), więc numer',
        'elementu służy do odnalezienia się w pliku, a nie do adresowania wiersza.',
        'Plik wchodzi do wydania przez `tools/merge_remaining_return.py`, który',
        'dopasowuje elementy po nagłówku i scenie, a nie po numerze.',
        '',
        'Elementów bez slotu `PL:` (powtórzenia) tu nie ma — dostają tekst z elementu,',
        'od którego dziedziczą.',
        '',
    ]
    for block in blocks:
        lines.append(block.rstrip('\n'))
        lines.append('')
    return '\n'.join(lines).rstrip('\n') + '\n'


def render_corrections(data: dict) -> dict:
    entries = [{
        'file': row['file'],
        'element_ordinal': row['element'],
        'original': row['jp'],  # the source text as the element shows it
        'expected_value_sha256': pl_import.digest(row['jp']),
        'replacement': row['pl'],
        'root_ordinal': row['element'],
        'reason': 'przeniesienie: to samo zdanie japońskie ma w wydanym planie jedno '
                  'polskie brzmienie (bez nowego tekstu)',
    } for row in data['transfer']]
    return {'schema': 1, 'kind': 'carried_over_wording',
            'plan_sha256': data['plan_sha256'],
            'count': len(entries), 'entries': entries}


def render_zip(data: dict) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, text in sorted(data['_package_texts'].items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 11, 0, 0, 0))
            info.external_attr = 0o644 << 16
            archive.writestr(info, text.encode('utf-8'))
    return buffer.getvalue()


def render_readme(data: dict) -> str:
    summary = data['summary']
    lines = [
        '# SRW Y — tekst, którego jeszcze nie ma',
        '',
        f'Wydanie **{data["label"]}**, plan SHA-256 `{data["plan_sha256"]}`. '
        'Wszystko poniżej jest policzone z repozytorium: '
        '`tools/deliver_remaining_text.py --check` odtwarza ten katalog.',
        '',
        '## Co jest w katalogu',
        '',
        f'- `sceny/` i `sceny.zip` — **{summary["left_for_translator"]} elementów** bez '
        f'polskiego tekstu w {summary["package_files"]} plikach `.md`. To praca dla '
        'tłumacza.',
        f'- `transfer.json` — **{summary["transferred"]} brakujących linii**, które mają '
        'już polskie brzmienie w planie (identyczne zdanie japońskie, jedno brzmienie). '
        'Nie wymagają tłumaczenia.',
        '- `CORRECTIONS.json` — ten sam transfer w formie, którą czyta '
        '`tools/one_click_patch.py`; każdy wpis ma japoński oryginał, jego sumę i powód.',
        '',
        '## Czego to narzędzie nie robi',
        '',
        '- Nie tłumaczy i nie dopisuje własnego tekstu. Przenosi wyłącznie brzmienie, '
        'które tłumacz już napisał dla **identycznego** zdania japońskiego.',
        '- Nie przenosi tekstów, które mają w planie kilka brzmień (np. 「うん…」 → '
        '「Ano…」/「Dobrze…」/「Mhm…」) — wybór zależy od mówcy i sceny, więc zostają '
        'w paczce dla tłumacza.',
        '- Nie rusza niczego, co jest już w planie, i nie zmienia żadnego wiersza '
        'tłumacza.',
        '',
        '## Powody, dla których element został dla tłumacza',
        '',
        '| powód | elementów |',
        '| --- | ---: |',
    ]
    for reason, count in sorted(summary['leave_reasons'].items(),
                                key=lambda kv: (-kv[1], kv[0])):
        lines.append(f'| {reason} | {count} |')
    lines.append('')
    return '\n'.join(lines)


def write(data: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if PACKAGE_DIR.exists():
        for path in PACKAGE_DIR.glob('*.md'):
            path.unlink()
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in sorted(data['_package_texts'].items()):
        (PACKAGE_DIR / name).write_text(text, encoding='utf-8')
    (OUT_DIR / 'README.md').write_text(render_readme(data), encoding='utf-8')
    TRANSFER.write_text(json.dumps({'schema': 1, 'label': data['label'],
                                    'plan_sha256': data['plan_sha256'],
                                    'transfer': data['transfer']},
                                   ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    CORRECTIONS.write_text(json.dumps(render_corrections(data), ensure_ascii=False,
                                      indent=1) + '\n', encoding='utf-8')
    SUMMARY.write_text(json.dumps({k: v for k, v in data.items() if not k.startswith('_')},
                                  ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (OUT_DIR / 'sceny.zip').write_bytes(render_zip(data))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        data = build()
    except DeliveryError as exc:
        print(f'PRZERWANO: {exc}', file=sys.stderr)
        return 2
    if args.write:
        write(data)
        print(f'zapisane: {OUT_DIR.relative_to(HERE)}')
    if args.check:
        stored = json.loads(SUMMARY.read_text(encoding='utf-8'))
        expected = {k: v for k, v in data.items() if not k.startswith('_')}
        problems = []
        if stored != expected:
            problems.append('data/remaining_text_y.json')
        if render_readme(data) != (OUT_DIR / 'README.md').read_text(encoding='utf-8'):
            problems.append('translations/pl-remaining/README.md')
        if (OUT_DIR / 'sceny.zip').read_bytes() != render_zip(data):
            problems.append('translations/pl-remaining/sceny.zip')
        if render_corrections(data) != json.loads(
                CORRECTIONS.read_text(encoding='utf-8')):
            problems.append('translations/pl-remaining/CORRECTIONS.json')
        for name, text in data['_package_texts'].items():
            if (PACKAGE_DIR / name).read_text(encoding='utf-8') != text:
                problems.append(f'translations/pl-remaining/sceny/{name}')
        if problems:
            print('ROZJAZD: ' + ', '.join(problems))
            return 1
        print('OK: paczka i transfer zgodne z repozytorium')
    if not (args.write or args.check):
        print(json.dumps(data['summary'], ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
