#!/usr/bin/env python3
"""Domyka brakujące linie scenariusza: pamięć tłumaczeń + kolejka do uzupełnienia.

Zwrotka PL3 objęła 26 plików szablonu v8 — cały scenariusz podstawowy i widoki.
Nie objęła jednak **scen DLC i części odcinków**, których w zwrotce nie było:
w korpusie gry to 75 372 linie z japońskim tekstem (54 475 unikalnych).

To narzędzie nie udaje, że ich nie ma. Robi trzy rzeczy:

1. liczy dokładnie, czego brakuje (per plik i per unikalny tekst japoński),
2. nakłada **pamięć tłumaczeń** z `translations/pl-dlc/MEMORY.json`
   (`japoński -> polski`, jedna linia = jedno wejście; to samo zdanie w grze
   powtarza się setki razy, więc pamięć domyka więcej linii niż ma wpisów),
3. wypisuje kolejkę **nieprzetłumaczonych** unikalnych tekstów, w kolejności
   częstości, żeby praca szła od najbardziej widocznych miejsc.

Wynik jest wejściem dla `pl_import.import_batch` przez manifest, więc każda
linia przechodzi tę samą bramkę co zwrotka tłumacza (tokeny, limity, układ).
Nic nie jest wstawiane „na oko”: brak wpisu w pamięci = linia w kolejce.

    python3 tools/translate_missing.py --report /tmp/braki.json \\
        --queue /tmp/kolejka.json --plan translations/pl3/PLAN_PL3.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(HERE / 'tools'))

import s6_extra  # noqa: E402

LETTER = re.compile(r'[ぁ-んァ-ヶ一-龥A-Za-z0-9]')


def corpus(source_dir: Path) -> list[dict]:
    rows = s6_extra.load(source_dir / 'scenario.jsonl')
    return [row for row in rows if (row.get('jp') or '').strip()]


def missing(plan: dict, rows: list[dict]) -> list[dict]:
    return [row for row in rows
            if row['id'].rsplit(':', 1)[1] not in plan['scenes'].get(row['file'], {})]


def load_memory(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema') != 1 or not isinstance(data.get('entries'), dict):
        raise ValueError(f'{path}: oczekiwano {{"schema": 1, "entries": {{...}}}}')
    return {source: target for source, target in data['entries'].items()
            if isinstance(target, str) and target.strip()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--source-dir', type=Path, default=HERE / 'data' / 's6-full')
    parser.add_argument('--memory', type=Path, default=HERE / 'translations' / 'pl-dlc' / 'MEMORY.json')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--queue', type=Path)
    args = parser.parse_args(argv)
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    rows = corpus(args.source_dir)
    gaps = missing(plan, rows)
    memory = load_memory(args.memory)
    counts = Counter(row['jp'] for row in gaps)
    translated = [text for text in counts if text in memory]
    covered_lines = sum(counts[text] for text in translated)
    queue = [{'jp': text, 'count': counts[text], 'en': next(
        (row.get('en') for row in gaps if row['jp'] == text and (row.get('en') or '').strip()), None)}
        for text in sorted(counts, key=lambda t: (-counts[t], t)) if text not in memory]
    report = {
        'missing_lines': len(gaps),
        'missing_unique': len(counts),
        'missing_files': len({row['file'] for row in gaps}),
        'memory_entries': len(memory),
        'covered_by_memory_lines': covered_lines,
        'covered_by_memory_percent': round(covered_lines / len(gaps) * 100, 2) if gaps else 100.0,
        'untranslated_unique': len(queue),
        'untranslated_lines': len(gaps) - covered_lines,
        'without_english': sum(1 for row in gaps if not (row.get('en') or '').strip()),
        'punctuation_only_unique': sum(1 for text in counts if not LETTER.search(text)),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n',
                               encoding='utf-8')
    if args.queue:
        args.queue.parent.mkdir(parents=True, exist_ok=True)
        args.queue.write_text(json.dumps({'schema': 1, 'queue': queue}, ensure_ascii=False,
                                         indent=1) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
