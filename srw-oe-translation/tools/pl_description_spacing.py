"""Offline PL description-join audit; proposes SPACE INSERTIONS in templates only.

Never called by the runtime builder. Reviewed proposals become source-bound snapshot
edits. Pool fragments stay byte-identical (including DLC). Real four argument indices
must be supplied by the caller; never replace %s with guessed words or insert spaces
at every placeholder (some placeholders intentionally split a word).
"""
import re
import translation_check as C

LETTERS = 'A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż'
PATTERNS = (
    re.compile(r'(?<=>)(?=\S)'),
    re.compile(r'(?<![0-9]):(?=[' + LETTERS + r'0-9])'),
    re.compile(r'[0-9%％](?=[' + LETTERS + r'])'),
    re.compile(r'(?:PD|Zasięg|Morale|sojusznicy|wrogowie)(?=[0-9])'),
)


def expand(template, arguments):
    """Visible text + (template start,end) origin for each glyph; colour tags hidden.

    The source range of an argument is its %s token, not the fragment's storage.
    This lets a separator be added next to that token WITHOUT changing shared pools.
    """
    visible, origins = [], []
    i = arg = 0
    while i < len(template):
        if template[i:i+2] == '%s':
            if arg >= len(arguments):
                raise ValueError('missing physical format argument')
            value = arguments[arg]; arg += 1
            # Fragment colour tags are non-rendered too.
            visible.extend(value); origins.extend([(i,i+2)]*len(value)); i += 2
        elif template[i:i+2] == '%%':
            visible.append('%'); origins.append((i,i+2)); i += 2
        else:
            visible.append(template[i]); origins.append((i,i+1)); i += 1
    # A fragment may end in ＠ and the template supply its colour digit.
    # The renderer sees controls AFTER substitution, not independently per chunk.
    raw=''.join(visible); hidden=set()
    for match in re.finditer(r'＠[0-9０-９]',raw):hidden.update(range(match.start(),match.end()))
    return ''.join(ch for i,ch in enumerate(raw)if i not in hidden), [o for i,o in enumerate(origins)if i not in hidden]


def propose(template, arguments=()):
    """Return whitespace-only revised template and unresolved fragment-internal gaps.

    No alpha-alpha word splitting, comma rewriting, grammar or numeric changes.
    printf conversions/newlines/colour controls must remain exactly unchanged.
    """
    visible, origins = expand(template, arguments)
    boundaries = set()
    for pattern in PATTERNS:
        for match in pattern.finditer(visible):
            at = match.end()
            # A greater-than comparison isn't a coloured skill heading.
            if pattern is PATTERNS[0] and '<' not in visible[:at].rsplit('\n',1)[-1]:
                continue
            boundaries.add(at)
    points, unresolved = set(), []
    for at in sorted(boundaries):
        if not 0 < at < len(visible):
            continue
        left,right=origins[at-1],origins[at]
        if left == right:
            unresolved.append(dict(position=at, reason='inside shared fragment; not changed'))
        else:
            points.add(right[0])
    revised = template
    for at in sorted(points, reverse=True):
        revised = revised[:at] + ' ' + revised[at:]
    if C.tokens(revised) != C.tokens(template):
        raise ValueError('proposal would alter formatter tokens')
    if revised.replace(' ','') != template.replace(' ','') or revised.count('\n') != template.count('\n'):
        raise ValueError('proposal is not space-only')
    if expand(revised, arguments)[0].replace(' ', '') != visible.replace(' ', ''):
        raise ValueError('proposal changes visible text or splits a colour control')
    return revised, unresolved
