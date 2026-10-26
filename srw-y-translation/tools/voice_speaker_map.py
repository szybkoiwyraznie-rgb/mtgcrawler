#!/usr/bin/env python3
"""Join every `battle_voice` quote to its speaker, from the game's own data.

The chain, all of it read from files the owner sent back:

    battle_voice table row      key = <bank>:<entry id>          local/s6/tables.jsonl
      -> entry key (the WaveId) id -> "F321_026"                 *battle_voice Shared Data*
      -> speaker                WaveId -> PlayDetails            the BVC containers
                                 {nameText, NameKey, FaceKey, dialogueText}

`nameText` is the speaker exactly as the game prints it above the line, `NameKey` is the
`pilot_name`/`dic_text_name` key behind that name, and `FaceKey` is the portrait the game
shows. Nothing here is inferred from quote content — a quote is attributed only when the
game's own container names the speaker for that WaveId.

Outputs (game text, so `local/`, never committed):

    local/s6/voice_speakers.json   per WaveId: speaker, name key, face, container
    local/s6/voice_map.json        per table row: speaker + gender, coverage numbers
    docs/VOICE_MAP_Y.md            readable coverage report

    python3 tools/voice_speaker_map.py
    python3 tools/voice_speaker_map.py --quiet          # only the summary
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from pilot_master import VOICE_ROOT, decrypt  # noqa: E402

TABLES = HERE / 'local' / 's6' / 'tables.jsonl'
PILOTS = HERE / 'local' / 's6' / 'pilots.json'
SHARED_DIR = VOICE_ROOT / 'aa' / 'StandaloneWindows64'   # battle_voice Shared Data
BVC_DIR = VOICE_ROOT / 'bvc' / 'aa' / 'StandaloneWindows64'   # voice containers, kit 2
#: every further container kit the owner returns lands in local/voice/bvc<N>/ — all are read
BVC_DIRS = sorted(VOICE_ROOT.glob('bvc*/aa/StandaloneWindows64'))
OUT_SPEAKERS = HERE / 'local' / 's6' / 'voice_speakers.json'
OUT_MAP = HERE / 'local' / 's6' / 'voice_map.json'
OUT_MD = HERE / 'docs' / 'VOICE_MAP_Y.md'


def unity_load(path: Path):
    import UnityPy
    return UnityPy.load(decrypt(path))


def shared_keys(directory: Path = SHARED_DIR) -> dict[str, str]:
    """entry id (`high:low`) -> key name (the WaveId), from every Shared Data object."""
    mapping: dict[str, str] = {}
    for path in sorted(directory.glob('*.bundle')):
        env = unity_load(path)
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            if 'm_Entries' not in tree or 'Shared Data' not in str(tree.get('m_Name', '')):
                continue
            for entry in tree['m_Entries']:
                entry_id = entry['m_Id']
                mapping[f'{entry_id >> 32:08x}:{entry_id & 0xffffffff:08x}'] = entry['m_Key']
    return mapping


def container_speakers(*directories: Path) -> tuple[dict[str, dict], dict[str, int]]:
    """WaveId -> speaker record, plus a per-container count of WaveIds it names."""
    waves: dict[str, dict] = {}
    per_file: dict[str, int] = {}
    files = [path for directory in (directories or tuple(BVC_DIRS))
             if directory.is_dir() for path in directory.glob('*.bundle')]
    for path in sorted(files):
        env = unity_load(path)
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            if 'PlayCategories' not in tree:
                continue  # a pure audio container (CriWare AWB) — no speaker data
            name = str(tree.get('m_Name', ''))
            found = 0
            for category in tree['PlayCategories']:
                for judge in category.get('judgements', []):
                    for order in judge.get('PlayOrders', []):
                        for detail in order.get('PlayDetails', []):
                            wave = detail.get('WaveId')
                            if not wave:
                                continue
                            found += 1
                            waves.setdefault(wave, {
                                'speaker': (detail.get('nameText') or '').strip(),
                                'name_key': detail.get('NameKey', ''),
                                'face_key': detail.get('FaceKey', ''),
                                'dialogue': (detail.get('dialogueText') or '').strip(),
                                'container': name,
                                'file': path.name,
                            })
            per_file[name] = found
    return waves, per_file


def pilot_genders(pilots: list[dict]) -> dict[str, str]:
    """Speaker name -> 'm'/'f', from the pilot master data (name match only)."""
    genders: dict[str, str] = {}
    for pilot in pilots:
        name = (pilot.get('name') or '').strip()
        if name and pilot.get('gender') in ('m', 'f'):
            genders.setdefault(name, pilot['gender'])
    return genders


def build(tables: list[dict], shared: dict[str, str], waves: dict[str, dict],
          pilots: list[dict]) -> dict:
    genders = pilot_genders(pilots)
    rows = [row for row in tables if row['table'].startswith('battle_voice')]
    mapped = []
    by_table = collections.Counter()
    total_by_table = collections.Counter()
    for row in rows:
        total_by_table[row['table']] += 1
        wave = shared.get(row['key'])
        detail = waves.get(wave or '')
        if not detail or not detail['speaker']:
            continue
        mapped.append({**row, 'wave': wave, 'speaker': detail['speaker'],
                       'name_key': detail['name_key'], 'face': detail['face_key'],
                       'container': detail['container'],
                       'gender': genders.get(detail['speaker'], '')})
        by_table[row['table']] += 1
    speakers = collections.Counter(item['speaker'] for item in mapped)
    banks = collections.defaultdict(set)
    for item in mapped:
        banks[item['speaker']].add(item['key'].split(':')[0])
    return {
        'rows': len(rows),
        'mapped': len(mapped),
        'unattributed': len(rows) - len(mapped),
        'waves_known': len(shared),
        'waves_with_speaker': len(waves),
        'by_table': {table: {'mapped': by_table[table], 'rows': total_by_table[table],
                             'unattributed': total_by_table[table] - by_table[table]}
                     for table in sorted(total_by_table)},
        'speakers': len(speakers),
        'with_gender': sum(1 for item in mapped if item['gender']),
        'top_speakers': speakers.most_common(15),
        'many_banks': sorted(((name, sorted(bank_list)) for name, bank_list in banks.items()),
                             key=lambda pair: -len(pair[1]))[:10],
        'rows_mapped': mapped,
    }


def render_md(result: dict) -> str:
    lines = ['# Cytaty bitewne — mówcy z danych gry (`tools/voice_speaker_map.py`)', '',
             'Każda kwestia jest przypisana **tylko** wtedy, gdy kontener głosu gry podaje',
             'dla jej `WaveId` pole `nameText` — imię mówcy, które gra sama wyświetla nad',
             'kwestią. Żadnego zgadywania z treści.', '',
             f"- kwestii w tabeli `battle_voice`: **{result['rows']:,}**",
             f"- z odczytanym mówcą: **{result['mapped']:,}** "
             f"({result['mapped'] / max(result['rows'], 1):.1%})",
             f"- różnych mówców: **{result['speakers']}**",
             f"- z płcią z `PilotBasicDatas`: {result['with_gender']:,} kwestii",
             f"- bez kontenera w wydanym buildzie: **{result.get('unattributed', 0):,}** "
             f"({result.get('unattributed', 0) / max(result['rows'], 1):.1%}) — te kwestie nie "
             "mają swojego zestawu głosu w danych; nie są zgadywane", '',
             '| tabela | z mówcą | bez kontenera | wszystkich |', '|---|---|---|---|']
    for table, counts in result['by_table'].items():
        lines.append(f"| `{table}` | {counts['mapped']:,} | "
                     f"{counts.get('unattributed', 0):,} | {counts['rows']:,} |")
    lines += ['', '## Najczęstsi mówcy', '', '| mówca | kwestii |', '|---|---|']
    for name, count in result['top_speakers']:
        lines.append(f'| {name} | {count:,} |')
    lines += ['', '## Mówcy w więcej niż jednym banku', '',
              'Bank głosów to jedna seria, więc ten sam mówca może mówić w kilku bankach',
              '(np. postać gościnna w cudzej serii). To nie błąd — to własność danych.', '']
    for name, bank_list in result['many_banks']:
        lines.append(f"- {name}: `{'`, `'.join(bank_list)}`")
    lines.append('')
    return '\n'.join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    if not BVC_DIRS:
        raise SystemExit(f'brak {BVC_DIR} — rozpakuj SRW_Y_BVC.zip do {VOICE_ROOT}')
    tables = [json.loads(line) for line in TABLES.open(encoding='utf-8') if line.strip()]
    pilots = json.loads(PILOTS.read_text(encoding='utf-8')) if PILOTS.is_file() else []
    shared = shared_keys()
    waves, per_file = container_speakers()
    result = build(tables, shared, waves, pilots)

    OUT_SPEAKERS.write_text(json.dumps(waves, ensure_ascii=False, indent=1) + '\n',
                            encoding='utf-8')
    OUT_MAP.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(result), encoding='utf-8')

    print(f"kwestii: {result['rows']:,}, z mówcą: {result['mapped']:,} "
          f"({result['mapped'] / max(result['rows'], 1):.1%}), "
          f"mówców: {result['speakers']}, kontenerów z treścią: {len(per_file)}")
    if not args.quiet:
        for name, count in result['top_speakers'][:10]:
            print(f'  {name:24s} {count:5d}')
    print(f'zapisano {OUT_SPEAKERS.relative_to(HERE)}, {OUT_MAP.relative_to(HERE)}, '
          f'{OUT_MD.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
