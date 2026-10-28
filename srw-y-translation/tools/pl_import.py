#!/usr/bin/env python3
"""Strict, atomic Markdown return intake. No game/Unity dependencies.

python tools/pl_import.py --manifest build/plik_dla_tlumacza/import_manifest.json \
    --input local/zwrotka --output local/import_pl.json
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata
import zipfile

SLOT = re.compile(r'^   PL:(?: (.*))?$', re.M)
ELEMENT = re.compile(r'^\d+\. \[', re.M)
LIMIT = re.compile(r'^   limit: do (\d+) znaków$', re.M)
MAX_BYTES = 64 * 1024 * 1024
# OE regression: '% obrażeń' is prose, but %02d, %s and %% are engine tokens.
# Deliberately do not accept a SPACE printf flag (see OE ReturnedTranslationPercentTests).
PRINTF = r'%%|%[-+#0]*(?:[0-9]+|\*)?(?:\.[0-9*]+)?[diuoxXfFeEgGcsp]'
# Explicit keyword delimiters can be immediately followed by Latin prose. Matching
# the generic dollar identifier first would turn '$kwbVAL' into one fake token.
# Bracketed prose such as [Elita] is not an engine placeholder; named placeholders
# carry a colon, except for the game's explicit [protagonist]. Fullwidth percent
# is ordinary punctuation, not an argument-bearing printf token.
IMPORT_TOKEN_RE = re.compile(
    PRINTF + r'|＠\d|＃|\{[^}]*\}|＜[^＞]+＞|\$(?:kwb|kwe|[A-Za-z][A-Za-z0-9]*)'
    r'|\[(?:[A-Za-z]+\d*:|protagonist)\]')
SOURCE_NAMES = ('scenario.jsonl', 'tables.jsonl', 'limits.json', 'groups.json',
                'voice_map.json', 'voice_groups.json', 'mission_map.json')
DEFAULT_SOURCE_DIR = Path(__file__).resolve().parents[1] / 'local' / 's6'


def source_fingerprints(directory: Path) -> dict:
    """Full private input snapshot, not just the rows present in this return batch."""
    result = {}
    for name in SOURCE_NAMES:
        path = directory / name
        if not path.is_file():
            if name in ('scenario.jsonl', 'tables.jsonl'):
                raise ImportFailure(f'{name}: brak aktualnego źródła S6')
            result[name] = None
        else:
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify_sources(manifest: dict, directory: Path) -> None:
    expected = manifest.get('source_sha256')
    if not isinstance(expected, dict) or set(expected) != set(SOURCE_NAMES):
        raise ImportFailure('manifest bez pełnej pieczęci źródeł — odtwórz i porównaj pakiet')
    current = source_fingerprints(directory)
    stale = [name for name in SOURCE_NAMES if current[name] != expected[name]]
    if stale:
        raise ImportFailure('nieaktualny manifest — zmienione źródła: ' + ', '.join(stale))


class ImportFailure(ValueError):
    pass


def verify_bindings(manifest: dict, directory: Path) -> None:
    """Like OE's live row resolution: a private manifest is not a replacement for S6.

    Check identity AND source text against live rows, never find a target by JP alone.
    In-memory unbound manifests exist only for synthetic renderer/unit tests.
    """
    indexes = {'scene': {}, 'table': {}}
    for kind, filename in (('scene', 'scenario.jsonl'), ('table', 'tables.jsonl')):
        for line in (directory / filename).read_text(encoding='utf-8-sig').splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ImportFailure(f'{filename}: oczekiwano rekordu JSONL')
            key = row.get('id') if kind == 'scene' else (row.get('table'), row.get('key'))
            indexes[kind].setdefault(key, []).append(row)
    for name, spec in manifest['files'].items():
        for element in spec['elements']:
            row = element['row']
            kind = row['import_kind']
            fields = ('id', 'file', 'string_id', 'jp', 'en') if kind == 'scene' else (
                'table', 'key', 'index', 'jp', 'en')
            key = row.get('id') if kind == 'scene' else (row.get('table'), row.get('key'))
            candidates = indexes.get(kind, {}).get(key, [])
            if not candidates or any(any(r.get(k) != row.get(k) for k in fields) for r in candidates):
                raise ImportFailure(f'{name}: brak/niezgodny rekord źródłowy {key}')


def canonical(text: str) -> str:
    return text.removeprefix('\ufeff').replace('\r\n', '\n')


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def make_manifest(files: dict, records: dict, source_sha256: dict | None = None) -> dict:
    """Bind renderer order to exact private source rows; not a translator input."""
    result = {'schema': 2, 'source_sha256': source_sha256, 'files': {}}
    for name, rows in records.items():
        text = canonical(files[name])
        starts = [m.start() for m in ELEMENT.finditer(text)] + [len(text)]
        if len(starts) - 1 != len(rows):
            raise ImportFailure(f'{name}: renderer/record count mismatch')
        elements, seen = [], {}
        for i, row in enumerate(rows):
            block = text[starts[i]:starts[i + 1]]
            slots = list(SLOT.finditer(block))
            key = (row.get('jp'), row.get('en'))
            parent = seen.get(key)
            if len(slots) > 1 or (not slots and parent is None):
                raise ImportFailure(f'{name}: invalid repeat/slot at element {i + 1}')
            if slots:
                seen[key] = i
            limit = LIMIT.search(block)
            elements.append({'row': row, 'slot': bool(slots),
                             'repeat': None if slots else parent,
                             'limit': int(limit[1]) if limit else None})
        result['files'][name] = {'text': text, 'sha256': digest(text), 'elements': elements}
    for name, text in files.items():
        if name not in result['files']:
            text = canonical(text)
            result['files'][name] = {'text': text, 'sha256': digest(text), 'elements': []}
    return result


def read_returns(path: Path) -> dict[str, str]:
    """Read a directory, single MD or flat ZIP without extracting untrusted paths."""
    found, total = {}, 0

    def add(name, data):
        nonlocal total
        total += len(data)
        if total > MAX_BYTES:
            raise ImportFailure('partia przekracza 64 MiB')
        if Path(name).name != name or name in found:
            raise ImportFailure(f'{name}: zduplikowana lub nieprawidłowa nazwa')
        found[name] = canonical(data.decode('utf-8-sig'))

    if path.is_dir():
        for p in sorted(path.rglob('*')):
            if p.is_symlink():
                raise ImportFailure(f'{p.name}: dowiązania są niedozwolone')
            if p.is_file():
                if p.suffix.lower() != '.md':
                    raise ImportFailure(f'{p.name}: oczekiwano pliku .md')
                if p.stat().st_size > MAX_BYTES:
                    raise ImportFailure('plik przekracza 64 MiB')
                add(p.name, p.read_bytes())
    elif path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path) as z:
            if sum(i.file_size for i in z.infolist()) > MAX_BYTES:
                raise ImportFailure('ZIP przekracza 64 MiB po rozpakowaniu')
            for item in z.infolist():
                if item.is_dir():
                    continue
                if not item.filename.endswith('.md'):
                    raise ImportFailure(f'{item.filename}: oczekiwano płaskiego ZIP z .md')
                add(item.filename, z.read(item))
    else:
        if path.suffix.lower() != '.md' or path.stat().st_size > MAX_BYTES:
            raise ImportFailure('oczekiwano .md, katalogu lub płaskiego ZIP')
        add(path.name, path.read_bytes())
    if not found:
        raise ImportFailure('brak plików Markdown')
    return found


def token_counts(text: str) -> Counter:
    return Counter(IMPORT_TOKEN_RE.findall(text))


def validate_text(text: str, source: str, limit: int | None) -> None:
    if limit is None:
        raise ImportFailure('pole nie ma zmierzonego limitu — wymaga weryfikacji')
    if len(text) > limit:
        raise ImportFailure(f'limit {limit}, wpisano {len(text)} znaków')
    if '  ' in text:
        raise ImportFailure('wielokrotne spacje w PL — układ odtwarzają narzędzia')
    if text != text.strip():
        raise ImportFailure('spacje na początku lub końcu PL')
    # The Godzilla title contains a Japanese pronunciation annotation, not an
    # engine placeholder. Its official EN is "Godzilla Singular Point"; this
    # exact exception does not relax checks for other fullwidth angle content.
    token_source = source
    if source == 'ゴジラ S.P＜シンギュラポイント＞':
        token_source = source.replace('＜シンギュラポイント＞', '')
    if token_counts(text) != token_counts(token_source):
        raise ImportFailure('niezgodna liczba lub treść tokenów')
    # Named bracket placeholders are independently resolved by name; their prose
    # order may differ across languages. Positional printf and control tags keep order.
    ordered = lambda value: [t for t in IMPORT_TOKEN_RE.findall(value)
                             if t != '%%' and not t.startswith('[')]
    if ordered(text) != ordered(token_source):
        raise ImportFailure('niezgodna kolejność tokenów sterujących/argumentów')
    # Known game syntax is exempt, but cannot be added: Counter above binds it to JP.
    prose = IMPORT_TOKEN_RE.sub('', text)
    # These additional symbols are present in the shipped JP/EN text corpus;
    # that is evidence of use, not a claim of per-screen font coverage.
    allowed = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ„“”’‘–—…«»「」『』（）～％×・↑←↓→★')
    for c in prose:
        if not (' ' <= c <= '~' or c in allowed):
            raise ImportFailure(f'znak poza zatwierdzonym zestawem: U+{ord(c):04X}')
    if unicodedata.normalize('NFC', text) != text:
        raise ImportFailure('tekst nie jest w normalizacji NFC')
    if '\\n' in text or '\\r' in text or ']]' in text:
        raise ImportFailure('niedozwolony escape lub zamknięcie literału Lua')


def layout(text: str, row: dict) -> str:
    """Keep bounded scene layout; let table widgets wrap Polish text themselves.

    The PL1 game screenshots show that copying JP table line counts and blank
    lines splits Polish mid-sentence, then the UI wraps it again. Table edge
    separators remain as before; internal JP formatting is not mapped by position.
    Scene wrapping is unchanged pending separate in-game evidence.
    """
    words = re.findall(r'(?:' + IMPORT_TOKEN_RE.pattern + r'|\S)+', text)
    if row['import_kind'] == 'scene':
        lines = ['']
        for word in words:
            if len(word) > 90:
                raise ImportFailure('wyraz/token dłuższy niż 90 znaków')
            if len(lines[-1]) + bool(lines[-1]) + len(word) > 90:
                lines.append(word)
            else:
                lines[-1] += (' ' if lines[-1] else '') + word
        if len(lines) > 3:
            raise ImportFailure('tekst wymaga ponad 3 linii po 90 znaków')
        original = row.get('jp') or ''
        leading = re.match(r'^(?:\r\n|\r|\n)+', original)
        trailing = re.search(r'(?:\r\n|\r|\n)+$', original)
        result = (leading[0] if leading else '') + '\n'.join(lines) + (trailing[0] if trailing else '')
        if len(re.split(r'\r\n|\r|\n', result)) > 3:
            raise ImportFailure('strukturalne puste linie źródła przekraczają limit 3 linii')
        return result
    template_source = row.get('jp') or row.get('en') or ''
    template = re.split(r'(\r\n|\r|\n)', template_source)
    content_positions = [i for i in range(0, len(template), 2) if template[i].strip()]
    if not content_positions:
        raise ImportFailure('pole chronione: źródło zawiera tylko białe znaki')
    first, last = content_positions[0], content_positions[-1]
    # Unlike internal line breaks, boundary separators might be structural.
    # Preserve the existing edge policy until there is specific evidence otherwise.
    prefix = ''.join(template[i] for i in range(1, first, 2))
    suffix = ''.join(template[i] for i in range(last + 1, len(template), 2))
    return prefix + text + suffix


def import_batch(manifest: dict, returned: dict, require_complete=False,
                 *, source_dir: Path | None = None, overrides: dict | None = None) -> dict:
    if manifest.get('schema') != 2:
        raise ImportFailure('nieobsługiwana wersja manifestu')
    if manifest.get('source_sha256') is not None or source_dir is not None:
        if source_dir is None:
            raise ImportFailure('manifest produkcyjny wymaga aktualnego source_dir')
        verify_sources(manifest, source_dir)
        verify_bindings(manifest, source_dir)
    known = manifest['files']
    errors, accepted, blanks, hashes = [], [], 0, {}
    if not returned:
        raise ImportFailure('pusta partia')
    substitutions = {}
    if overrides is not None:
        if overrides.get('schema') != 1 or not isinstance(overrides.get('entries'), list):
            raise ImportFailure('nieprawidłowa wersja korekt')
        expected = overrides.get('input_sha256')
        actual = {name: digest(canonical(text)) for name, text in returned.items()}
        if expected != actual:
            raise ImportFailure('korekty nie odpowiadają dokładnej zwrotce')
        for entry in overrides['entries']:
            name, ordinal = entry.get('file'), entry.get('element_ordinal')
            if (name not in returned or type(ordinal) is not int or ordinal < 1
                    or not isinstance(entry.get('replacement'), str) or not entry['replacement']
                    or not isinstance(entry.get('expected_id'), str)
                    or not isinstance(entry.get('expected_value_sha256'), str)
                    or not isinstance(entry.get('original'), str)
                    or digest(entry['original']) != entry['expected_value_sha256']
                    or type(entry.get('root_ordinal')) is not int or entry['root_ordinal'] < 1
                    or not isinstance(entry.get('reason'), str) or not entry['reason']):
                raise ImportFailure('nieprawidłowa korekta')
            key = (name, ordinal)
            if key in substitutions:
                raise ImportFailure(f'{name}, element #{ordinal}: powtórzona korekta')
            substitutions[key] = entry
    applied_overrides = set()
    for name, raw in sorted(returned.items()):
        if name not in known:
            errors.append(f'{name}: plik nie występuje w manifeście')
            continue
        spec = known[name]
        baseline, text = canonical(spec['text']), canonical(raw)
        if digest(baseline) != spec['sha256']:
            errors.append(f'{name}: uszkodzony manifest')
            continue
        if SLOT.sub('   PL:', text) != baseline:
            errors.append(f'{name}: zmieniona struktura/JP/EN/numeracja lub wieloliniowe PL')
            continue
        values = [m[1] or '' for m in SLOT.finditer(text)]
        elements = spec['elements']
        bad_repeat = False
        if len(values) != sum(bool(e['slot']) for e in elements):
            errors.append(f'{name}: uszkodzony manifest — liczba slotów')
            continue
        for i, e in enumerate(elements):
            if e['slot']:
                continue
            parent = e['repeat']
            if (type(parent) is not int or not 0 <= parent < i
                    or any(e['row'].get(k) != elements[parent]['row'].get(k) for k in ('jp', 'en'))):
                errors.append(f'{name}: uszkodzone powtórzenie #{i + 1}')
                bad_repeat = True
        if bad_repeat:
            continue
        slots = iter(values)
        inherited = {}
        for i, element in enumerate(spec['elements']):
            value = next(slots) if element['slot'] else inherited[element['repeat']]
            override = substitutions.get((name, i + 1))
            if override:
                root = i + 1 if element['slot'] else element['repeat'] + 1
                if (not value or root != override['root_ordinal']
                        or element['row'].get('id') != override['expected_id']
                        or digest(value) != override['expected_value_sha256']):
                    raise ImportFailure(f'{name}, element #{i + 1}: korekta nie odpowiada źródłu')
                value = override['replacement']
                applied_overrides.add((name, i + 1))
            inherited[i] = value
            if not value:
                if element['slot']:
                    blanks += 1
                    if require_complete:
                        errors.append(f'{name}, element #{i + 1}: puste PL')
                continue
            row = element['row']
            try:
                source = row.get('jp') or ''
                # A real table key can contain empty JP and nonempty EN. This uses
                # the supplied translation and EN for token/layout validation; it
                # does not invent a translation or create a missing game key.
                if not source.strip() and row['import_kind'] == 'table':
                    source = row.get('en') or ''
                if not source.strip():
                    raise ImportFailure('pole chronione: puste źródło')
                if row['import_kind'] == 'table' and re.sub(r'-DLC\d+$', '', row['table']) in ('font', 'fonts'):
                    raise ImportFailure('pole chronione: klucz zasobu czcionki')
                validate_text(value, source, element['limit'])
                pl = layout(value, row)
                accepted.append({'source_file': name, 'ordinal': i + 1,
                                 'row': row, 'pl': pl})
            except ImportFailure as exc:
                errors.append(f'{name}, element #{i + 1}: {exc}')
        hashes[name] = digest(text)
    if errors:
        raise ImportFailure('\n'.join(errors))
    if applied_overrides != set(substitutions):
        raise ImportFailure('korekta nie została zastosowana do elementu zwrotki')
    tables, scenes = {}, {}
    for item in accepted:
        row, pl = item['row'], item['pl']
        if row['import_kind'] == 'table':
            dest, key = tables.setdefault(row['table'], {}), row['key']
        else:
            dest = scenes.setdefault(row['file'], {})
            key = row['id'].rsplit(':', 1)[1]  # string_id#occurrence, never a bare ID
        if key in dest and (dest[key]['pl'] != pl or dest[key]['jp'] != row['jp']
                            or dest[key]['en'] != row.get('en')):
            raise ImportFailure(f'{key}: sprzeczne źródła/tłumaczenia tego samego rekordu')
        dest[key] = {'jp': row['jp'], 'en': row.get('en'), 'pl': pl}
    if source_dir is not None:
        verify_sources(manifest, source_dir)
    return {'schema': 1, 'source_sha256': manifest.get('source_sha256'), 'runtime_tested': False, 'input_sha256': hashes,
            'manifest_sha256': digest(json.dumps(manifest, ensure_ascii=False, sort_keys=True)),
            'accepted': len(accepted), 'empty_slots': blanks,
            'overrides_applied': len(applied_overrides),
            'tables': tables, 'scenes': scenes}


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as f:
            temp = Path(f.name)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--source-dir', type=Path, default=DEFAULT_SOURCE_DIR,
                        help='Aktualne lokalne dane S6, nie katalog zwrotki')
    parser.add_argument('--overrides', type=Path, help='Jawne korekty związane z dokładną zwrotką')
    parser.add_argument('--check', action='store_true', help='Pełna walidacja bez zapisu')
    parser.add_argument('--require-complete', action='store_true',
                        help='Wymagaj wszystkich PL w przesłanych plikach (nie całego pakietu)')
    args = parser.parse_args(argv)
    if not args.check and args.output is None:
        parser.error('--output jest wymagane bez --check')
    try:
        # Do not allow a successful import to overwrite its own inputs.
        if args.output and args.output.resolve() in (args.manifest.resolve(), args.input.resolve()):
            raise ImportFailure('wynik nie może nadpisać wejścia')
        if args.output and args.input.is_dir() and args.output.resolve().is_relative_to(args.input.resolve()):
            raise ImportFailure('wynik musi być poza katalogiem zwrotki')
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        if not manifest.get('source_sha256'):
            raise ImportFailure('manifest bez pieczęci źródeł — odtwórz i porównaj pakiet')
        if args.output and args.output.resolve() in {(args.source_dir / n).resolve() for n in SOURCE_NAMES}:
            raise ImportFailure('wynik nie może nadpisać danych S6')
        corrections = (json.loads(args.overrides.read_text(encoding='utf-8'))
                       if args.overrides else None)
        if args.output and args.overrides and args.output.resolve() == args.overrides.resolve():
            raise ImportFailure('wynik nie może nadpisać korekt')
        result = import_batch(manifest, read_returns(args.input), args.require_complete,
                              source_dir=args.source_dir, overrides=corrections)
        verify_sources(manifest, args.source_dir)
        if not args.check:
            atomic_write(args.output, result)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f'ODRZUCONO — nic nie zapisano:\n{exc}')
        return 1
    print(f'OK: {result["accepted"]} rekordów, {result["empty_slots"]} pustych PL. '
          + ('Kontrola bez zapisu.' if args.check else f'Zapisano {args.output}'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
