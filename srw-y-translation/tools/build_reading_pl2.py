#!/usr/bin/env python3
"""PL2 reading edition in the accepted OE-style format, from source-bound data."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

from build_reading_y import Reader, archive_bytes, jsonl
from build_reading_oe_style import scene_rows, episode, deployment_document, choice, mission_title
from build_translator_package import row_gender
from pl_import import source_fingerprints, verify_sources


def number(mission):
    match = re.fullmatch(r'm(\d{4})_\d{7}', mission['id'])
    if not match:
        raise ValueError('nieznany format identyfikatora misji')
    return int(match[1])


def assess(reader, mission):
    groups = scene_rows(reader, mission)
    rows = [row for _, _, group in groups for row in group]
    chosen = choice(reader, mission)
    assets = reader.mission_assets(mission)
    unknown_jp = sum(1 for asset in assets for row in reader._scenes_by_file.get(asset, [])
                     if not row.get('jp') and row_gender(row, reader._gender_tables) in (None, chosen))
    present = sum(('scene', row['file'], row['id'].rsplit(':', 1)[1]) in reader.pl for row in rows)
    # The protagonist selector can touch a missing key in this defaultdict;
    # test for actual rows rather than key membership.
    unavailable = [a for a in assets if not reader._scenes_by_file.get(a)]
    return {'number': number(mission), 'id': mission['id'], 'selected': len(rows),
            'translated': present, 'unknown_jp': unknown_jp, 'missing_assets': unavailable,
            'protagonist': chosen, 'eligible': bool(rows) and present == len(rows) and not unknown_jp}


def build(source_dir, index, plan, links, out, audit):
    if out.exists():
        raise ValueError('katalog wyjściowy już istnieje')
    graph = json.loads(index.read_text(encoding='utf8'))
    if graph.get('compaction', {}).get('source_sha256') != source_fingerprints(source_dir):
        raise ValueError('indeks nie odpowiada źródłu')
    raw_plan = plan.read_bytes()
    data = json.loads(raw_plan)
    report = json.loads(audit.read_text(encoding='utf8'))
    if (report.get('kind') != 'full_return_verified' or report.get('return_label') != 'PL2'
            or report.get('plan_sha256') != hashlib.sha256(raw_plan).hexdigest()
            or report.get('input_sha256') != data.get('input_sha256')
            or report.get('manifest_sha256') != data.get('manifest_sha256')
            or report.get('accepted_records_including_repeats') != data.get('accepted')
            or report.get('quarantined_slots') != 0
            or report.get('overrides_applied') != data.get('overrides_applied')):
        raise ValueError('audyt nie odpowiada zweryfikowanemu planowi PL2')
    verify_sources(data, source_dir)
    reader = Reader(graph, jsonl(source_dir / 'scenario.jsonl'), jsonl(source_dir / 'tables.jsonl'),
                    [data], links=json.loads(links.read_text(encoding='utf8')))
    candidates = sorted((m for m in graph['missions'] if m['collection'] == 'MissionData'),
                        key=lambda m: m['source_index'])
    if not candidates or number(candidates[0]) != 0:
        raise ValueError('brak prologu')
    assessed, selected, seen = [], [], set()
    # A contiguous prefix of source-order main missions, stopping before the
    # first incomplete translated mission; not an invented chronology.
    for mission in candidates:
        result = assess(reader, mission)
        assessed.append(result)
        if not result['eligible']:
            break
        if result['number'] in seen:
            raise ValueError('powtórzony numer misji')
        seen.add(result['number'])
        selected.append(mission)
    if not selected or len(selected) < 2:
        raise ValueError('brak pełnych misji w planie')
    files, counts = {}, {}
    for mission in selected:
        n = number(mission)
        text, count = episode(reader, mission, n, edition='PL2')
        if count != assessed[len(counts)]['translated']:
            raise ValueError(f'{mission["id"]}: niepełny scenariusz')
        files[f'srwy_episode_{n:02d}_PL.md'] = text
        counts[mission['id']] = count
    files['srwy_mission_deployments.md'] = deployment_document(
        reader, selected[1:], edition='PL2', numbers=[number(m) for m in selected[1:]])
    numbers = [number(m) for m in selected]
    gaps = sorted(set(range(numbers[0], numbers[-1] + 1)) - set(numbers))
    unavailable = sum(len(item['missing_assets']) for item in assessed if item['eligible'])
    files['README.md'] = ('# Czytanki SRW Y — druga zwrotka PL2\n\n'
        f'Prolog i {len(selected)-1} misji, w tym alternatywne początki bohatera i bohaterki. '
        'Wybrano kolejne misje z głównej listy, w których wszystkie rozpoznane wiersze '
        'wybranego wariantu mają przekład PL2. Sceny sytuacyjne nie mają potwierdzonej chronologii.\n\n'
        + (f'Brak numerów {", ".join(map(str, gaps))}: nie są w tej głównej liście w tym zakresie; '
           'nie dopisano nieprzetłumaczonych misji z innych list.\n\n' if gaps else '')
        + (f'Liczba odwołań do scen bez odpowiadającego pliku w dostępnym korpusie: {unavailable}; '
           'nie można potwierdzić, czy zawierałyby dialogi.\n\n' if unavailable else '')
        + 'Zestawienie jednostek i profili: [srwy_mission_deployments.md](srwy_mission_deployments.md). '
          'Braki w danych i niepotwierdzone powiązania są oznaczone.\n\n'
        + '\n'.join(f'- [{"Prolog" if number(m) == 0 else "Misja " + str(number(m))}]'
                    f'(srwy_episode_{number(m):02d}_PL.md)' for m in selected) + '\n')
    out.mkdir(parents=True)
    for name, body in files.items():
        (out / name).write_text(body, encoding='utf8', newline='\n')
    archive = archive_bytes(files)
    (out / 'SRW_Y_CZYTANKI_PL2_POPRAWIONE.zip').write_bytes(archive)
    receipt = {'edition': 'PL2', 'missions': [m['id'] for m in selected], 'numbers': numbers,
               'gaps': gaps, 'scene_rows': counts, 'coverage': assessed,
               'translated_used': len(reader.used), 'missing': len(reader.missing),
               'missing_detail': [list(k) for k in sorted(reader.missing)],
               'chronology_verified': False}
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--translations', type=Path, required=True)
    p.add_argument('--links', type=Path, required=True)
    p.add_argument('--audit', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    r = build(a.source_dir, a.index, a.translations, a.links, a.out, a.audit)
    print(json.dumps({'missions': len(r['missions']) - 1, 'scene_rows': sum(r['scene_rows'].values()),
                      'missing': r['missing'], 'first_incomplete': r['coverage'][-1]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
