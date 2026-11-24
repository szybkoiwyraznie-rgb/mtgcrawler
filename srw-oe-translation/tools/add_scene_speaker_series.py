#!/usr/bin/env python3
"""Add the character-dictionary series to the scene-speaker name lists.

Why this exists: ``tools/mission_deployments.py`` regenerates
``docs/srwoe_mission_deployments.md`` from the private ``eventP*``/``config*``
containers and the decrypted 1.08 ELF. Those are not available in every
workspace, so the checked-in document cannot be regenerated whenever only the
*reading* form of one section changes. The owner asked (2026-11-23) that the
list of characters who only speak in a scene script — the section headed
``Postacie wypowiadające się w skrypcie sceny (bez obecności w deployment —
bez statystyk)`` — show, next to every name, the series the character comes
from.

This tool applies exactly that to a *pinned* delivered copy: it refuses any
other bytes, rewrites only the ``- Name`` bullets inside those lists, and
reproduces the rest of the file byte-for-byte. It is intentionally not a
generator: a canonical ``mission_deployments.py`` run (which now emits the same
lines) supersedes it as soon as the private inputs are available again.

Series source: the ``series`` part of the character dictionary
(``07_names_characters.jsonl`` in the materialized ``pakiet_PL``), keyed by the
character key that ``00_dialogue.jsonl``/``06_scenes.jsonl`` record as the
speaker. A speaker whose dictionary row has no series (generic soldiers,
officers, ``???``) is labelled ``brak wpisu w słowniku postaci`` — the same
wording ``pilot_catalog`` uses, never an invented title.

Resolution is per mission: the speaker ids of that mission's scene scripts are
read from the English package, so a duplicated Polish name resolves to the
character who actually speaks there. A name that is still ambiguous *with
different series* stops the run instead of guessing.

The bullet rewrite and the prose/section-note strings (`NOTE_EDITS`) that
mention the series are both applied here, so one pinned run reproduces the
delivered document; a diff of its output contains nothing but the annotated
names, the five note lines and the two section-heading forms.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mission_deployments as MD  # noqa: E402
import pl_release_package as R  # noqa: E402

#: Character-dictionary parts that can carry the name a scene list prints.
NAME_PARTS = ('name_full', 'name_short', 'name', 'nickname', 'short_name', 'name_narrow')

SECTION_RE = re.compile(r'^### (?:Odcinek \d+|Symulator) — .*?\(`([A-Z0-9_]+)`\)$', re.M)
SOURCE_RE = re.compile(r'\*\*Źródło:\*\* `([^`/]+)/')
BLOCK_RE = re.compile(
    r'(\*(?:Postacie wypowiadające się|Postać wypowiadająca się) w skrypcie sceny[^\n]*\*\n)'
    r'((?:- [^\n]*\n)+)'
)

#: Prose in the document header/section note that must follow the bullets, byte
#: for byte the strings `mission_deployments.py` now emits. Kept here so one
#: pinned run of this tool reproduces the delivered document; the counts pin
#: how many times each string must appear (194 plural + 27 singular lists).
NOTE_EDITS = (
    ('*Postacie wypowiadające się w skrypcie sceny (bez obecności w deployment — bez statystyk):*',
     '*Postacie wypowiadające się w skrypcie sceny (bez obecności w deployment — bez statystyk; '
     'przy nazwie podano serię pochodzenia):*', 194),
    ('*Postać wypowiadająca się w skrypcie sceny (bez obecności w deployment — bez statystyk):*',
     '*Postać wypowiadająca się w skrypcie sceny (bez obecności w deployment — bez statystyk; '
     'przy nazwie podano serię pochodzenia):*', 27),
    ('scenach scenariuszowych są wymienione wyłącznie jako nazwy na końcu sekcji postaci. ',
     'scenach scenariuszowych są wymienione na końcu sekcji postaci wyłącznie jako nazwy wraz '
     'z serią pochodzenia (ze słownika postaci gry). ', 1),
    ('**wyłącznie jako nazwa** na końcu sekcji postaci — bez karty statystyk '
     '(`00_dialogue.jsonl` + `06_scenes.jsonl`).',
     '**wyłącznie jako nazwa z serią pochodzenia** na końcu sekcji postaci — bez karty statystyk '
     '(`00_dialogue.jsonl` + `06_scenes.jsonl`; seria z `07_names_characters.jsonl`, część `series`).', 1),
    ('ustalenia wyłącznie **listy nazw** postaci, które nie występują w rozstawieniu — bez kart statystyk.',
     'ustalenia wyłącznie **listy nazw** postaci, które nie występują w rozstawieniu — bez kart '
     'statystyk; przy każdej nazwie podano serię pochodzenia z części `series` słownika postaci '
     '(`07_names_characters.jsonl`), a `brak wpisu w słowniku postaci` oznacza, że słownik nie ma '
     'dla tej postaci wiersza serii (postacie zbiorowe, oficerowie, `???`).', 1),
)
ALREADY_RE = re.compile(r' — seria: ')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_dictionary(polish_dir: Path) -> tuple[dict[int, dict[str, str]], dict[int, str]]:
    """Polish name parts and series per character key from the materialized package."""
    names: dict[int, dict[str, str]] = defaultdict(dict)
    series: dict[int, set[str]] = defaultdict(set)
    for r in MD.M.rows(polish_dir, '07_names_characters.jsonl'):
        if r.get('key') is None:
            continue
        key = int(r['key'])
        if r.get('part') == 'series':
            if r.get('jp') not in ('', None, 'NoData'):
                title = (r.get('pl') or '').strip()
                if title:
                    series[key].add(title)
            continue
        if r.get('part') in NAME_PARTS:
            value = (r.get('pl') or '').strip()
            if value:
                names[key].setdefault(r['part'], value)
    return names, {k: '; '.join(sorted(v)) for k, v in series.items()}


def primary_name(parts: dict[str, str]) -> str:
    """The name the deployment document prints for a speaker."""
    return parts.get('name_full') or parts.get('name_short') or ''


class SpeakerIndex:
    """Speaker character ids per mission code plus the Polish name/series data."""

    def __init__(self, english_dir: Path, polish_dir: Path) -> None:
        self.by_pkg_code, self.by_code = MD.load_scene_speakers(english_dir)
        self.names, self.series = load_dictionary(polish_dir)
        self.by_mission_names: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
        for code, cids in self._all_by_code().items():
            for cid in cids:
                parts = self.names.get(cid)
                if parts:
                    name = primary_name(parts)
                    if name:
                        self.by_mission_names[code][name].append(cid)

    def _all_by_code(self) -> dict[str, list[int]]:
        merged: dict[str, list[int]] = defaultdict(list)
        for (_pkg, code), cids in self.by_pkg_code.items():
            for cid in cids:
                if cid not in merged[code]:
                    merged[code].append(cid)
        for code, cids in self.by_code.items():
            for cid in cids:
                if cid not in merged[code]:
                    merged[code].append(cid)
        return merged

    def candidates(self, code: str, package: str | None, name: str) -> list[int]:
        """Every speaker id of this mission that prints `name` (package-scoped when known).

        The name the document prints is the character's primary name. Only when
        no speaker of the mission has it as the primary name do the other
        dictionary forms (nickname, short/narrow name) count — otherwise a
        deployed `Shiro Amada` (nickname `Shiro`) would shadow the scene-only
        `Shiro` from a different series.
        """
        def scoped(match) -> list[int]:
            found: list[int] = []
            if package:
                found += [cid for cid in self.by_pkg_code.get((package, code), []) if match(cid)]
            found += [cid for cid in self.by_code.get(code, []) if match(cid) and cid not in found]
            if not found:
                found = [cid for cid in self.by_mission_names.get(code, {}).get(name, [])
                         if match(cid)]
            return found

        primary = scoped(lambda cid: primary_name(self.names.get(cid) or {}) == name)
        if primary:
            return primary
        return scoped(lambda cid: name in self._printed_names(cid))

    def _printed_names(self, cid: int) -> set[str]:
        parts = self.names.get(cid) or {}
        return {primary_name(parts), *parts.values()} - {''}

    def series_for(self, code: str, package: str | None, name: str) -> str:
        cids = self.candidates(code, package, name)
        if not cids:
            raise SystemExit(f'nieznana postać mówiąca: {name!r} w misji {code}')
        titles = {self.series.get(cid, '') for cid in cids}
        titles.discard('')
        if len(titles) > 1:
            raise SystemExit(
                f'nazwa {name!r} w misji {code} wskazuje kilka serii: {sorted(titles)}')
        return titles.pop() if titles else MD.SCENE_SPEAKER_SERIES_UNRECORDED


def rewrite(text: str, index: SpeakerIndex, notes: bool = True) -> tuple[str, dict]:
    """Annotate every scene-speaker bullet; return the text and a report.

    `notes=False` skips the `NOTE_EDITS` prose pass, which lets tests annotate a
    synthetic document that carries no header prose.
    """
    headings = [(m.start(), m.group(1)) for m in SECTION_RE.finditer(text)]
    if not headings:
        raise SystemExit('brak nagłówków misji — to nie jest dokument rozstawień')
    out: list[str] = []
    cursor = 0
    report = {'sections': len(headings), 'blocks': 0, 'names': 0,
              'unrecorded': 0, 'already': 0, 'by_code': {}}
    for pos_index, (start, code) in enumerate(headings):
        end = headings[pos_index + 1][0] if pos_index + 1 < len(headings) else len(text)
        chunk = text[start:end]
        out.append(text[cursor:start])
        cursor = start
        package_match = SOURCE_RE.search(chunk)
        package = package_match.group(1) if package_match else None

        def annotate(match: re.Match) -> str:
            header, bullets = match.group(1), match.group(2)
            lines = []
            counted = 0
            for line in bullets.splitlines():
                name = line[2:]
                if ALREADY_RE.search(name):
                    report['already'] += 1
                    lines.append(line)
                    continue
                series = index.series_for(code, package, name)
                if series == MD.SCENE_SPEAKER_SERIES_UNRECORDED:
                    report['unrecorded'] += 1
                lines.append(MD.scene_speaker_line(name, series))
                counted += 1
            report['blocks'] += 1
            report['names'] += counted
            report['by_code'][code] = report['by_code'].get(code, 0) + counted
            return header + '\n'.join(lines) + '\n'

        chunk = BLOCK_RE.sub(annotate, chunk)
        out.append(chunk)
        cursor = end
    out.append(text[cursor:])
    document = ''.join(out)

    if notes:
        for before, after, expected in NOTE_EDITS:
            found = document.count(before)
            if found != expected:
                raise SystemExit(f'notatka występuje {found} razy, oczekiwano {expected}: {before[:60]!r}')
            document = document.replace(before, after)
            report['note_edits'] = report.get('note_edits', 0) + found
    return document, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--source', required=True, type=Path, help='Pinned delivered deployments .md')
    ap.add_argument('--pin-sha256', required=True, help='Expected SHA-256 of --source')
    ap.add_argument('--english', type=Path, default=HERE.parent / 'pakiet_EN',
                    help='English package with 00_dialogue.jsonl/06_scenes.jsonl')
    ap.add_argument('--stored-pl', type=Path, default=HERE.parent / 'pakiet_PL',
                    help='Stored pakiet_PL snapshot directory')
    ap.add_argument('--polish', type=Path, default=None,
                    help='Already materialized pakiet_PL directory (skips materialization)')
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--report', type=Path, help='Optional JSON report path')
    args = ap.parse_args(argv)

    raw = args.source.read_bytes()
    if sha(raw) != args.pin_sha256:
        raise SystemExit(f'unexpected source bytes: {sha(raw)} != {args.pin_sha256}')

    with tempfile.TemporaryDirectory() as td:
        polish = args.polish or Path(td) / 'pakiet_PL'
        if args.polish is None:
            R.materialize(args.english, args.stored_pl, polish)
        index = SpeakerIndex(args.english, polish)
        text, report = rewrite(raw.decode('utf-8'), index)

    if report['blocks'] == 0:
        raise SystemExit('nie znaleziono żadnej listy postaci mówiących — przerwano')
    data = text.encode('utf-8')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    if args.out.read_bytes() != data:
        raise SystemExit('output readback differs')

    record = {
        'tool': 'add_scene_speaker_series.py',
        'source_sha256': sha(raw),
        'output_sha256': sha(data),
        'output_bytes': len(data),
        'series_source': '07_names_characters.jsonl:series',
        'unrecorded_label': MD.SCENE_SPEAKER_SERIES_UNRECORDED,
        **report,
    }
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n',
                               encoding='utf-8')
    print(json.dumps({k: v for k, v in record.items() if k != 'by_code'},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
