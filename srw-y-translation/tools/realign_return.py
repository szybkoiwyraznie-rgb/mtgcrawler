#!/usr/bin/env python3
"""Move finished `PL:` entries onto the reconciled template by Japanese text, never by number.

After `tools/reconcile_template_v8.py` closes the stale block in `odcinek-20.md`, the
numbering of that one scene shifts by one, so a return made against the old numbering no
longer matches the template. Renumbering a translator's file by position would silently
reattach every Polish line to its neighbour — the single worst thing this project could
do. So each filled block is carried over by the identity of its Japanese text:

* blocks are grouped by (speaker, full Japanese text). The template does repeat a line
  word for word, so a duplicate is accepted only when the Polish is identical; if the two
  copies were translated differently the run stops instead of guessing,
* the new template supplies the structure (numbers, limits, EN, tokens),
* only the Polish value travels.

Element numbers are sequential in the source files, so the ordinal — not the printed
label — identifies a block; the printed label is rewritten to whatever the template says.

Usage (in `srw-y-translation/`):

    python3 tools/realign_return.py --input local/pl3-work/v8in \
        --output local/pl3-work/v8in-aligned --check
    python3 tools/realign_return.py --input local/pl3-work/v8in \
        --output local/pl3-work/v8in-aligned
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
from pathlib import Path

from bind_v8_return import HEADING
from check_pl_template import load_template
from pl_import import ImportFailure, SLOT, canonical
from reconcile_template_v8 import JP_FIXES, JP_REVERTS


def corrected_japanese() -> dict[str, str]:
    """Brzmienie w zwrotce -> brzmienie we wzorcu, gdy wzorzec był „poprawiany”.

    Historia w jednym akapicie: 2026-11-10 wzorzec v8 dostał dwie „poprawki” JP,
    bo korpus (zbudowany z kopii bundla `_Patch`) mówił inaczej. Zwrotka PL3
    wróciła od tłumacza z brzmieniem **z gry** (`友情…`, `返`), czyli tym, które
    wzorzec miał pierwotnie. Poprawki okazały się błędne i zostały cofnięte
    (`JP_REVERTS`), więc teraz to zwrotka ma brzmienie, którego wzorzec nie ma —
    i wyrównanie musi je rozpoznać, inaczej polski tekst tej linii zostałby
    uznany za osierocony.

    Mapowanie bierzemy z tego samego miejsca, w którym stoi cofnięcie, żeby nie
    dało się ich rozjechać. `JP_FIXES` zostaje na przyszłość: gdyby kiedyś
    zaistniała **prawdziwa** poprawka, ta funkcja obsłuży ją bez zmian.
    """
    mapping = {}
    # Kierunek jest ten sam w obu tabelach: `anchor` to brzmienie, które stoi
    # w pliku zwrotki, `replacement` — to, które ma wzorzec. `JP_REVERTS` czyta
    # się więc „wzorzec miał X, wrócił do Y”, a zwrotka ma X (bo tłumacz dostał
    # wzorzec już po błędnej poprawce), więc mapowanie X -> Y jest poprawne.
    pairs = JP_FIXES + JP_REVERTS
    for _name, anchor, replacement, _why in pairs:
        if '] ' not in anchor or '] ' not in replacement:
            continue
        old, new = anchor.split('] ', 1)[1], replacement.split('] ', 1)[1]
        if old != new:
            mapping[old] = new
    return mapping

HERE = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = HERE / 'translations' / 'template-v8'
ELEMENT = re.compile(r'^(\d+)\. ', re.M)


def split_blocks(text: str) -> tuple[str, list[str], list[str]]:
    """Return (text before the first block, blocks with `PL:` blanked, Polish values).

    The Polish value is read from the *original* block: reading it from the blanked copy
    would silently report zero translations carried over.
    """
    spans = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
    head = text[:spans[0]] if len(spans) > 1 else text
    blocks, values = [], []
    for start, stop in zip(spans, spans[1:]):
        block = text[start:stop]
        blocks.append(SLOT.sub('   PL:', block))
        values.append(polish(block))
    return head, blocks, values


def identity(block: str) -> tuple[str, str]:
    """(speaker, japanese) — what a translation is attached to.

    The speaker is part of the identity because the same courtesy line can appear twice
    in one scene from two people, and those are two different rows.
    """
    limit = block.find('\n   limit:')
    body = block if limit < 0 else block[:limit]
    lines = body.splitlines()
    head = lines[0]
    match = re.match(r'\d+\. (\[[^\]]*\]) (.*)$', head)
    if not match:
        raise ImportFailure(f'nierozpoznany element: {head[:60]}')
    speaker, first = match[1], match[2]
    rest = [line.strip() for line in lines[1:]]
    return speaker, '\n'.join([first] + rest)


def polish(block: str) -> str:
    found = [m[1] or '' for m in SLOT.finditer(block)]
    if len(found) > 1:
        raise ImportFailure('element z więcej niż jednym PL')
    return found[0] if found else ''


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a scene file into (preamble, [(heading line, section body)]).

    Numbering restarts at 1 in every scene, so alignment and renumbering must be done per
    section — a file-wide counter would produce labels the template never had.
    """
    headings = list(HEADING.finditer(text))
    if not headings:
        return text, []
    preamble = text[:headings[0].start()]
    sections = []
    for index, heading in enumerate(headings):
        stop = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        # heading.end() sits before the newline that the pattern does not consume
        sections.append((heading[0], text[heading.end() + 1:stop]))
    return preamble, sections


def realign_section(new_section: str, old_section: str, name: str,
                    scene: str) -> tuple[str, int]:
    new_head, new_blocks, _ = split_blocks(new_section)
    _old_head, old_blocks, old_values = split_blocks(old_section)

    rename = corrected_japanese()
    old_keys = []
    for block in old_blocks:
        speaker, jp = identity(block)
        old_keys.append((speaker, rename.get(jp, jp)))
    new_keys = [identity(block) for block in new_blocks]

    # Align by content, never by position: only identical Japanese may be paired, and for
    # identical Japanese a swap is harmless because the game shows the same line twice.
    matcher = difflib.SequenceMatcher(None, old_keys, new_keys, autojunk=False)
    mapping: dict[int, int] = {}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for offset in range(i2 - i1):
                mapping[i1 + offset] = j1 + offset
        elif tag in ('replace', 'delete'):
            orphaned = [(i, old_keys[i]) for i in range(i1, i2) if old_values[i].strip()]
            if orphaned:
                raise ImportFailure(
                    f'{name} / {scene}: {len(orphaned)} wypełnionych kwestii nie ma '
                    f'odpowiednika w nowym wzorcu, np. {orphaned[0][1][1][:48]}')

    carried = {new_index: old_values[old_index] for old_index, new_index in mapping.items()
               if old_values[old_index].strip()}
    out = []
    for position, block in enumerate(new_blocks, 1):
        value = carried.get(position - 1, '')
        block = SLOT.sub(lambda _m: f'   PL: {value}' if value else '   PL:', block)
        out.append(re.sub(r'^\d+\.', f'{position}.', block, count=1))
    return new_head + ''.join(out), len(carried)


def realign(template_text: str, returned_text: str, name: str) -> tuple[str, dict]:
    new_preamble, new_sections = split_sections(template_text)
    old_preamble, old_sections = split_sections(returned_text)
    if len(new_sections) != len(old_sections):
        raise ImportFailure(f'{name}: zwrotka ma {len(old_sections)} scen, wzorzec '
                            f'{len(new_sections)}')
    out, carried = [new_preamble], 0
    for (new_heading, new_body), (old_heading, old_body) in zip(new_sections, old_sections):
        if new_heading != old_heading:
            raise ImportFailure(f'{name}: inna kolejność scen: {new_heading!r} vs {old_heading!r}')
        body, count = realign_section(new_body, old_body, name, new_heading)
        carried += count
        out.append(new_heading + '\n' + body)
    return ''.join(out), {'carried': carried, 'template': len(new_sections)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--template', type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument('--check', action='store_true', help='nic nie zapisuj')
    args = parser.parse_args(argv)
    if args.output.resolve() == args.input.resolve():
        raise ImportFailure('wynik nie może nadpisać zwrotki')
    if args.input.is_dir() and args.output.resolve().is_relative_to(args.input.resolve()):
        raise ImportFailure('wynik musi być poza katalogiem zwrotki')

    template = load_template(args.template)
    changed, total = [], 0
    for path in sorted(args.input.rglob('*.md')):
        name = path.name
        text = canonical(path.read_text(encoding='utf-8-sig'))
        base = template.get(name)
        if base is None:
            print(f'{name}: poza wzorcem v8 — przepisuję bez zmian')
            if not args.check:
                args.output.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, args.output / name)
            continue
        if SLOT.sub('   PL:', text) == base:
            print(f'{name}: już zgodny ze wzorcem')
            new_text, stats = text, {'carried': 0, 'template': 0}
        else:
            new_text, stats = realign(base, text, name)
            changed.append(name)
            print(f'{name}: przeniesiono {stats["carried"]} tłumaczeń na '
                  f'{stats["template"]} elementów wzorca')
        total += stats['carried']
        if not args.check:
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / name).write_text(new_text, encoding='utf-8')
    print(f'plików zmienionych: {len(changed)}, przeniesionych tłumaczeń: {total}')
    if changed:
        print('  ' + ', '.join(changed))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ImportFailure as exc:
        print(f'ODRZUCONO — nic nie zapisano:\n{exc}')
        raise SystemExit(1)
