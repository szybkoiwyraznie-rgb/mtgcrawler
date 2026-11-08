#!/usr/bin/env python3
"""Break Polish UI/table text the way the English original is broken.

Why this exists
---------------
The game does **not** wrap text in these boxes. Whatever line breaks the string
carries are the breaks the player sees: the English tables carry explicit `\\n`
and the Polish translation, following the translator package rule ("write the
whole line after `PL:`, the tools take care of breaking"), arrived as one long
line. In the Data Help panel that produced a single line running out of the
frame (owner's screenshot, 2026-11-09: „Im wyższe Morale, tym wyższe parametry
i obrażenia. …” in one piece).

What it does
------------
For every element of a catalogue whose `EN:` block has more than one line while
`PL:` has exactly one, it splits the Polish text into **the same number of
lines** as the English, choosing the split points with a small dynamic program:

* lines may only break at spaces (so no word is cut, and the character count of
  the record does not change — a space becomes a newline, which is what the
  field budget counts anyway);
* the cost is the squared deviation from the *proportional* length of the
  matching English line, so a short English line gets a short Polish line;
* a line may not start with a punctuation mark or end with a hyphen.

Omitting `--write` is a dry run (it only reports); `--out` stores the report.

    python tools/wrap_like_en.py --out /tmp/wrap_dry.json
    python tools/wrap_like_en.py --write --out translations/pl2/WRAP_REVIEW.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GLOB = 'translations/pl2/PL/widoki/*.md'

ELEMENT = re.compile(r'^\d+\. \[')
KEY = re.compile(r'^   (?:EN|PL|limit|tokeny):')
EN_LINE = re.compile(r'^   EN:(?: (.*))?$')
PL_LINE = re.compile(r'^   PL:(?: (.*))?$')
#: A Polish line must not begin with these; they would look like a typo.
BAD_START = set(',.;:!?)]}»”’%')
#: A line must not end with a hyphen or an opening bracket.
BAD_END = set('-–—([{«„‘')
#: How much longer than the matching English line a Polish line may get before
#: the tool reports it for review instead of silently shipping it.
TOLERANCE = 12
#: Breaking a line is cheap after a punctuation mark, and expensive in the middle
#: of a clause or right before a short function word ("i", "w", "gdy", "się"…).
#: The weights are in "characters of length error", so 30 means "accept up to 30
#: characters of unevenness to avoid a mid-clause break".
PUNCT_END = set('.,:;!?…')
NO_PUNCT_COST = 30
STOPWORDS = set('a i o u w z że by gdy się nie na do od po za pod nad dla lub oraz '
                'że go mu ją je ich ale czy jak też także tylko już jeszcze'.split())
STOPWORD_COST = 40


#: Spans that must not be split, even though they contain spaces: quoted game
#: terms ("'Penetr. barier'"), rich-text links ("<link=0>Smash</link>") and
#: brace placeholders ("{{0}}"). Splitting inside one of those produced lines
#: like "… efekt 'Penetr." / "barier'." in the first pass.
SPAN = re.compile(r"<link=\d+>.*?</link>|'[^']*'|„[^”]*”|\{[^}]*\}")


def tokenize(text: str) -> list[str]:
    """Split on the spaces that are *outside* the spans above.

    Splitting at every space and then re-joining put a space inside
    `('Baza danych')`, which changed the record. Scanning character by character
    keeps the text byte-identical: `' '.join(tokenize(text)) == text`.
    """
    spans = [(match.start(), match.end()) for match in SPAN.finditer(text)]

    def inside(index: int) -> bool:
        return any(begin <= index < finish for begin, finish in spans)

    tokens: list[str] = []
    current: list[str] = []
    for index, character in enumerate(text):
        if character == ' ' and not inside(index):
            if current:
                tokens.append(''.join(current))
                current = []
        else:
            current.append(character)
    if current:
        tokens.append(''.join(current))
    return tokens


def block(lines: list[str], start: int, stop: int) -> list[str]:
    """Text of a `key:` line and the indented continuation lines after it."""
    first = lines[start]
    body = [re.sub(r'^   [A-Za-z]+:(?: |$)', '', first)]
    for line in lines[start + 1:stop]:
        if not line.startswith('   ') or ELEMENT.match(line.lstrip()):
            break
        if KEY.match(line):        # only the catalogue's own keys end a block
            break
        body.append(line[3:])
    return [part.rstrip() for part in body]


def segment(words: list[str], targets: list[int]) -> list[str] | None:
    """Split `words` into `len(targets)` lines closest to the target lengths."""
    count = len(words)
    lines_wanted = len(targets)
    if count < lines_wanted:
        return None
    infinity = float('inf')
    # cost[i][k]: best cost for the first i words split into k lines.
    cost = [[infinity] * (lines_wanted + 1) for _ in range(count + 1)]
    back = [[0] * (lines_wanted + 1) for _ in range(count + 1)]
    cost[0][0] = 0.0
    for k in range(1, lines_wanted + 1):
        target = targets[k - 1]
        for end in range(1, count + 1):
            for start in range(end - 1, -1, -1):
                if cost[start][k - 1] == infinity:
                    continue
                piece = words[start:end]
                text = ' '.join(piece)
                if piece[0][0] in BAD_START or text[-1] in BAD_END:
                    continue
                if start and piece[0].strip('„”"''’').lower() in STOPWORDS:
                    continue
                delta = len(text) - target
                penalty = delta * delta
                if k > 1 and start and words[start - 1][-1] not in PUNCT_END:
                    penalty += NO_PUNCT_COST
                candidate = cost[start][k - 1] + penalty
                if candidate < cost[end][k]:
                    cost[end][k] = candidate
                    back[end][k] = start
    if cost[count][lines_wanted] == infinity:
        return None
    out: list[str] = []
    end, k = count, lines_wanted
    while k:
        start = back[end][k]
        out.append(' '.join(words[start:end]))
        end, k = start, k - 1
    return list(reversed(out))


def proportional(en_lines: list[str], total: int) -> list[int]:
    """English line lengths scaled to the Polish length."""
    if not sum(len(line) for line in en_lines):
        return [total // len(en_lines)] * len(en_lines)
    scale = total / sum(len(line) for line in en_lines)
    return [max(4, round(len(line) * scale)) for line in en_lines]


def wrap_file(path: Path, write: bool) -> dict:
    lines = path.read_text(encoding='utf8').splitlines()
    report = {'file': str(path.relative_to(ROOT)), 'elements': 0, 'wrapped': 0,
              'already_multi': 0, 'single_language': 0, 'skipped': [], 'warnings': [],
              'changes': []}
    out_lines = list(lines)
    starts = [index for index, line in enumerate(lines) if ELEMENT.match(line)]
    bounds = starts + [len(lines)]
    # Rewriting changes the number of lines, so edit from the bottom up.
    for start, stop in reversed(list(zip(bounds, bounds[1:]))):
        element_lines = lines[start:stop]
        en_at = pl_at = None
        for offset, line in enumerate(element_lines):
            if en_at is None and EN_LINE.match(line):
                en_at = offset
            elif pl_at is None and PL_LINE.match(line):
                pl_at = offset
        if en_at is None or pl_at is None:
            report['single_language'] += 1
            continue
        report['elements'] += 1
        en = block(element_lines, en_at, pl_at)
        pl = block(element_lines, pl_at, len(element_lines))
        # PL block may swallow trailing blank lines — drop them.
        while pl and not pl[-1]:
            pl.pop()
        if not any(part.strip() for part in pl):
            continue
        if len(pl) > 1:
            report['already_multi'] += 1
            continue
        if len(en) < 2:
            continue
        text = pl[0]
        words = tokenize(text)
        targets = proportional(en, len(text))
        wrapped = segment(words, targets)
        if wrapped is None:
            report['skipped'].append({'header': element_lines[0][:60],
                                      'reason': 'nie da się podzielić na tyle samo linii'})
            continue
        if any(len(line) > len(en[min(index, len(en) - 1)]) + TOLERANCE
               for index, line in enumerate(wrapped)):
            report['warnings'].append({'header': element_lines[0][:60],
                                       'pl': wrapped, 'en': en})
        new_block = ['   PL: ' + wrapped[0]] + ['   ' + line for line in wrapped[1:]]
        absolute = start + pl_at
        out_lines[absolute:absolute + 1] = new_block
        report['wrapped'] += 1
        report['changes'].append({'header': element_lines[0][:60],
                                  'lines': len(wrapped),
                                  'pl': wrapped,
                                  'en': en})
    if write and out_lines != lines:
        path.write_text('\n'.join(out_lines) + '\n', encoding='utf8')
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--glob', default=DEFAULT_GLOB)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    reports = [wrap_file(path, args.write) for path in sorted(ROOT.glob(args.glob))]
    totals = {'files': len(reports),
              'wrapped': sum(item['wrapped'] for item in reports),
              'already_multi': sum(item['already_multi'] for item in reports),
              'skipped': sum(len(item['skipped']) for item in reports),
              'warnings': sum(len(item['warnings']) for item in reports)}
    payload = {'schema': 1, 'mode': 'write' if args.write else 'check',
               'rule': 'tyle samo linii co EN, podzial tylko na spacjach, '
                       'koszt = odchylenie od proporcjonalnej dlugosci linii EN',
               'totals': totals, 'files': reports}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n',
                            encoding='utf8')
    print(json.dumps(totals, ensure_ascii=False))
    for item in reports:
        if item['wrapped'] or item['warnings']:
            print(f"  {item['file']}: zawinieto {item['wrapped']}, "
                  f"ostrzezen {len(item['warnings'])}, pominietych {len(item['skipped'])}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
