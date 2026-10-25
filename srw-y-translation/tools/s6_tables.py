#!/usr/bin/env python3
"""S6 step 2: read every localization table, in both languages, and pair the rows.

Object layout (measured; the typetree in this build does not describe these objects):

    +0    12 x 0x00
    +12   u32 1, u32 1, 8 B hash
    +28   u32 name length, name (UTF-8), pad to 4
          u32 locale length, locale ("ja-JP" / "en-US"), pad to 4
          u32 2, 8 B hash, u32 0, u32 record count
          records ...
          u32 2, u32 0                     <- 8-byte terminator, always present

One record:

    u32   key low            \  the same (low, high) pair appears in the JP and
    u32   key high           /  the EN file for the same string, so this is the row id
    u32   length of the text in bytes
    ...   the UTF-8 text
          pad to 4
    u32   always 0 in all 72,436 records of the 288 objects read here

so `next = align4(record + 12 + length) + 4`. This walks every table exactly, ends on
the terminator, and reproduces the record count stored in the object header (a mismatch
is a hard error, never a silent skip).

Rows are paired **by key, not by position**: the two files list the same strings in a
different order (e.g. `robot_name` starts with Raideen in Japanese and with Combattler V
in English), so position pairing would silently mismatch almost everything.

Output: `local/s6/tables.jsonl`, one row per string, Japanese original + English
reference + the Japanese byte length (the length the game's own field holds).
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

ROOTS = (HERE / 'local' / 's4_plain', HERE / 'local' / 's6' / 'plain' / 'tekst')
OUT = HERE / 'local' / 's6' / 'tables.jsonl'
REPORT = HERE / 'local' / 's6' / 'tables_report.json'
LOCALES = {'_ja-JP': 'ja', '_en-US': 'en'}
TERMINATOR = struct.pack('<II', 2, 0)


class TableError(ValueError):
    """Raised when a table does not follow the layout above."""


def align4(value: int) -> int:
    return (value + 3) // 4 * 4


def split_locale(name: str) -> tuple[str | None, str | None]:
    for suffix, language in LOCALES.items():
        if name.endswith(suffix):
            return name[: -len(suffix)], language
    return None, None


def table_header(raw: bytes, name: str) -> tuple[int, int]:
    """Return (offset of the first record, record count) for one table object."""
    marker = name.encode('utf-8')
    at = raw.find(marker)
    if at < 0:
        raise TableError(f'{name}: name not found in the object')
    p = align4(at + len(marker))
    locale_length = struct.unpack_from('<I', raw, p)[0]
    if not 1 <= locale_length <= 16:
        raise TableError(f'{name}: implausible locale length {locale_length}')
    p = align4(p + 4 + locale_length)
    if struct.unpack_from('<I', raw, p)[0] != 2:
        raise TableError(f'{name}: expected u32 2 after the locale')
    if struct.unpack_from('<I', raw, p + 12)[0] != 0:
        raise TableError(f'{name}: expected u32 0 before the record count')
    count = struct.unpack_from('<I', raw, p + 16)[0]
    return p + 20, count


def walk_records(raw: bytes, start: int, count: int) -> tuple[list[dict], int]:
    """Walk `count` records; return them plus the offset just past the last one."""
    rows = []
    p = start
    for index in range(count):
        if p + 12 > len(raw):
            raise TableError(f'ran out of data at record {index}')
        length = struct.unpack_from('<I', raw, p + 8)[0]
        end = p + 12 + length
        if end > len(raw):
            raise TableError(f'record {index} overruns the object ({length} B)')
        try:
            text = raw[p + 12:end].decode('utf-8')
        except UnicodeDecodeError as error:
            raise TableError(f'record {index} is not UTF-8: {error}') from None
        low, high = struct.unpack_from('<II', raw, p)
        rows.append({'offset': p + 12, 'bytes': length, 'text': text,
                     'key': f'{high:08x}:{low:08x}'})
        p = align4(end) + 4
    return rows, p


def read_tables() -> tuple[dict[tuple[str, str], list[dict]], list[dict]]:
    tables: dict[tuple[str, str], list[dict]] = {}
    problems: list[dict] = []
    for root in ROOTS:
        for path in sorted(root.rglob('*.bundle')):
            env = UnityPy.load(str(path))
            for obj in env.objects:
                if obj.type.name != 'MonoBehaviour':
                    continue
                data = obj.read()
                name = data.m_Name
                table, language = split_locale(name)
                if table is None:
                    problems.append({'object': name, 'bundle': path.name,
                                     'problem': 'no locale suffix'})
                    continue
                try:
                    raw = obj.get_raw_data()
                    start, count = table_header(raw, name)
                    rows, end = walk_records(raw, start, count)
                    if raw[end:] != TERMINATOR:
                        raise TableError(
                            f'expected the 8-byte terminator at {end}, got '
                            f'{raw[end:end + 8].hex()}')
                except TableError as error:
                    problems.append({'object': name, 'bundle': path.name,
                                     'problem': str(error)})
                    continue
                if (table, language) in tables:
                    problems.append({'object': name, 'bundle': path.name,
                                     'problem': 'duplicate table'})
                    continue
                tables[(table, language)] = rows
    return tables, problems


def pair_rows(tables: dict[tuple[str, str], list[dict]]) -> tuple[list[dict], list[dict]]:
    """Join the two languages on the record key; keep Japanese order."""
    names = sorted({table for table, _ in tables})
    rows, unpaired = [], []
    for table in names:
        ja = tables.get((table, 'ja'))
        en = tables.get((table, 'en'))
        if ja is None or en is None:
            unpaired.append({'table': table, 'ja': bool(ja), 'en': bool(en)})
        by_key = {row['key']: row for row in en or ()}
        for index, ja_row in enumerate(ja or ()):
            en_row = by_key.pop(ja_row['key'], None)
            rows.append({
                'id': f'table:{table}:{ja_row["key"]}',
                'table': table,
                'key': ja_row['key'],
                'index': index,
                'jp': ja_row['text'],
                'en': en_row['text'] if en_row else None,
                'jp_bytes': ja_row['bytes'],
                'en_bytes': en_row['bytes'] if en_row else None,
            })
        for leftover in by_key.values():
            rows.append({
                'id': f'table:{table}:{leftover["key"]}',
                'table': table,
                'key': leftover['key'],
                'index': None,
                'jp': None,
                'en': leftover['text'],
                'jp_bytes': None,
                'en_bytes': leftover['bytes'],
            })
    return rows, unpaired


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--report', type=Path, default=REPORT)
    args = parser.parse_args(argv)

    tables, problems = read_tables()
    rows, unpaired = pair_rows(tables)

    with args.out.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')

    per_table = Counter(row['table'] for row in rows)
    report = {
        'tables': len(per_table),
        'tables_per_language': {
            'ja': sum(1 for _, language in tables if language == 'ja'),
            'en': sum(1 for _, language in tables if language == 'en'),
        },
        'rows': len(rows),
        'unpaired_tables': unpaired,
        'problems': problems,
        'identical_jp_en': sum(1 for row in rows if row['jp'] == row['en']),
        'missing_side': sum(1 for row in rows if row['jp'] is None or row['en'] is None),
        'jp_characters': sum(len(row['jp'] or '') for row in rows),
        'en_characters': sum(len(row['en'] or '') for row in rows),
        'per_table': dict(sorted(per_table.items())),
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n',
                           encoding='utf-8')

    print(f'tables: {report["tables_per_language"]["ja"]} ja / '
          f'{report["tables_per_language"]["en"]} en')
    print(f'rows: {len(rows):,}   missing one side: {report["missing_side"]}')
    print(f'jp characters: {report["jp_characters"]:,}   '
          f'en characters: {report["en_characters"]:,}')
    print(f'rows where jp == en: {report["identical_jp_en"]:,}')
    for table in ('prologue', 'system_text', 'battle_voice'):
        if table in per_table:
            print(f'  {table}: {per_table[table]:,} rows')
    if unpaired:
        print(f'UNPAIRED: {unpaired}')
    if problems:
        print(f'PROBLEMS: {len(problems)}')
        for problem in problems:
            print('  ', problem)
    print(f'written {args.out.relative_to(HERE)} and {args.report.relative_to(HERE)}')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
