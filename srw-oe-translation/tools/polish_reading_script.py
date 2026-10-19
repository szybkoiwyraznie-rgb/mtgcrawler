#!/usr/bin/env python3
"""Build Polish counterparts of the delivered early reading editions (including the prologue episode).

The delivered EN Markdown is an editorial reference, never a translation source.
Every prose block is rebound to an ordered physical source row before reading PL.
Re-evaluate variants in Polish: an EN alias alone is not evidence of a PL alias.
"""
import argparse
from difflib import SequenceMatcher
import hashlib
import html
import json
from pathlib import Path
import re

from build_reading_script import render_entry
from reading_script_source import HEADINGS, PROSE, SOURCE_FILES, paragraphs
from polish_reading_source import EarlyReadingSource
from mech_catalog_sources import need


def sha(data): return hashlib.sha256(data).hexdigest()


def normalize_reference(value):
    value = html.unescape(re.sub(r'\\([\\`*_\[\]#])', r'\1', value))
    # Legacy editions italicize parenthesized thoughts; the current renderer
    # leaves their text unchanged. Do NOT strip emphasis inside spoken text.
    return re.sub(r'(?<=\*\* )\*\((.*?)\)\*$', r'(\1)', value)


def recover_blocks(source, reference):
    keys = {}
    for sid, entries in source.entries.items():
        for entry in entries:
            for mode in ('story', 'conditional'):
                for level in ((3, 4) if entry.kind in HEADINGS else (3,)):
                    value = render_entry(entry, mode, level)
                    variants = [value]
                    if entry.speaker:
                        key = (entry.row.get('speaker') or {}).get('id')
                        names = set().union(*source.names[key].values())
                        if entry.speaker == 'Comms / Speaker':
                            names.add('Radio')  # Legacy channel label, not a person.
                        variants += [value.replace('**' + entry.speaker + ':**', '**' + n + ':**', 1) for n in names]
                    for variant in variants:
                        keys.setdefault(normalize_reference(variant), set()).add((sid, entry.order, entry.id, mode, level))
    current, variant, last = None, False, 0
    episode_zero = {s.get('episode') for s in source.scenes} == {0}
    used, out = set(), []
    base_scenes = iter(s for s in source.scenes if not s.get('variant_of'))
    reference_blocks = reference.decode('utf-8').strip().split('\n\n')
    max_parts = max(len(k.split('\n\n')) for k in keys)
    skip_until = 0
    for index, block in enumerate(reference_blocks):
        if index < skip_until:
            continue
        if block.startswith('## Editorial notes'): break
        if block.startswith('## DLC text variant'):
            variant = True
            continue
        if block.startswith('## ') and episode_zero and block not in ('## Prologue', '## Interlude'):
            need(current is not None, 'Episode 0 section before source scene')
            out.append({'heading': block, 'block': index})
            continue
        if block.startswith('## '):
            scene = next(base_scenes)
            current, last, variant = scene['id'], 0, False
            out.append({'mission': current, 'block': index})
            continue
        if not current or variant: continue
        options = []
        for parts in range(1, max_parts + 1):
            combined = '\n\n'.join(reference_blocks[index:index + parts])
            options.extend((*x, parts) for x in keys.get(normalize_reference(combined), set())
                           if x[0] == current and x[1] > last)
        if options:
            _, last, rid, mode, level, parts = min(options, key=lambda x: (x[1], x[3] != 'story', x[2], x[4]))
            skip_until = index + parts
            used.add(rid)
            out.append({'row': rid, 'mode': mode, 'level': level, 'block': index})
        elif block.startswith('#'):
            out.append({'heading': block, 'block': index})
        else:
            need(block == '---', f'Unmapped literary block {index}')
    need(next(base_scenes, None) is None, 'Unmapped base scene')
    expected = {e.id for sid, entries in source.entries.items() if not source.scene_by_id[sid].get('variant_of')
                for e in entries if e.kind in PROSE}
    need(expected <= used, f'Unmapped base prose: {sorted(expected - used)}')
    return out


def validate_plan(plan, source, reference):
    need({s.get('episode') for s in source.scenes} == {plan['episode']}, 'Episode/source selection differs')
    need(plan.get('schema') == 1 and plan.get('reviewed') is True, 'Unreviewed Polish editorial plan')
    need(plan['reference_sha256'] == sha(reference), 'Delivered English reference changed')
    need(plan['english_source_sha256'] == source.hashes, 'English source changed; review the bindings again')
    blocks = [{k: v for k, v in b.items() if k not in ('pl', 'mission_row')} for b in plan['blocks']]
    need(blocks == recover_blocks(source, reference), 'Editorial plan/source mapping differs')
    reference_blocks = reference.decode().strip().split('\n\n')
    for b in plan['blocks']:
        if 'mission_row' in b:
            title = ' '.join(paragraphs(source.missions[b['mission_row']]['en']))
            need(title == reference_blocks[b['block']][3:], 'Mission-title identity differs')
        elif 'mission' in b:
            need(plan['episode'] == 0 and b.get('pl', '').strip(), 'Missing source mission title')
        if 'heading' in b and 'mission_row' not in b:
            need(b.get('pl', '').startswith(b['heading'].split(' ', 1)[0] + ' '), 'Missing Polish editorial heading')


def reading_entry(entry, mode='story', level=3):
    value = render_entry(entry, mode, level)
    if entry.kind in PROSE:
        # Italicize only complete parenthesized thought paragraphs. Preserve all
        # words/punctuation, including the Polish translator's existing choices.
        def thought(match): return match[1] + '*' + match[2] + '*'
        value = re.sub(r'(^|\n\n|\*\* )(\([^\n]*\))(?=$|\n\n)', thought, value)
    return value


def windows(opcodes, length, context=1):
    """One labelled excerpt per edit, retaining whole-entry immediate context."""
    return [(tag, i1, i2, j1, j2, max(0, j1 - context), min(length, j2 + context))
            for tag, i1, i2, j1, j2 in opcodes if tag != 'equal']


def build(plan, english, polish, reference):
    validate_plan(plan, english, reference)
    # Physical row/JP metadata must agree before any text can be localized.
    for rid, row in english.by_id.items():
        other = polish.by_id.get(rid)
        need(other is not None and {k: v for k, v in row.items() if k not in ('en', 'pl')} ==
             {k: v for k, v in other.items() if k not in ('en', 'pl')}, f'Polish source binding differs: {rid}')
    en_entries = {e.id: e for es in english.entries.values() for e in es}
    pl_entries = {e.id: e for es in polish.entries.values() for e in es}
    pieces, audit, coverage = [], [], {}
    position = 0
    def put(value, rid=None, role=None):
        nonlocal position
        value += '\n\n'
        if rid:
            audit.append({'row': rid, 'start': position, 'end': position + len(value), 'role': role})
        pieces.append(value)
        position += len(value)
    episode = plan['episode']
    put(f'# Super Robot Wars OE — Epizod {episode}')
    put('*Polski scenariusz do czytania · Tekst PL3*')
    put('> **Uwaga dla czytelnika:** Dialogi w cytatach są warunkowe lub sytuacyjne. Pogrupowano je dla wygody '
        'lektury, nie jako gwarantowaną kolejność wydarzeń podczas rozgrywki. Nie dopisujemy dokładnych progów HP, '
        'tur ani innych wyzwalaczy, których nie potwierdza eksport tekstu. Alternatywne rozstrzygnięcia i wersje '
        'źródłowe nie są kolejnymi wydarzeniami fabuły.')
    put('---')
    blocks_by_scene = {}
    current = None
    for block in plan['blocks']:
        if 'mission' in block:
            current = block['mission']
            blocks_by_scene[current] = [block]
        else:
            blocks_by_scene[current].append(block)
    title_maps = {}
    for sid, blocks in blocks_by_scene.items():
        first = blocks[0]
        if 'mission_row' in first:
            mission = polish.missions[first['mission_row']]
            need(bool(mission.get('pl', '').strip()), f'Missing Polish mission {mission["id"]}')
            title_maps[sid] = ' '.join(paragraphs(mission['pl']))
        else:
            title_maps[sid] = first['pl']
    def show(entry, mode, role='shown', level=3):
        put(reading_entry(entry, mode, level), entry.id, role)
        coverage[entry.id] = {'status': role}
    seen = []
    variant_audit = []
    for scene in polish.scenes:
        sid, base = scene['id'], scene.get('variant_of')
        if not base:
            put('## ' + title_maps[sid])
            for b in blocks_by_scene[sid][1:]:
                if 'row' in b:
                    need(en_entries[b['row']].kind == pl_entries[b['row']].kind, 'Entry kind changed')
                    show(pl_entries[b['row']], b['mode'], level=b['level'])
                elif 'mission_row' in b:
                    mission = polish.missions[b['mission_row']]
                    need(bool(mission.get('pl', '').strip()), f'Missing Polish mission {mission["id"]}')
                    put(b['heading'].split(' ', 1)[0] + ' ' + ' '.join(paragraphs(mission['pl'])))
                else:
                    put(b['pl'])
            seen.append(sid)
            continue
        target = polish.entries[sid]
        # Prefer an exact earlier PL alias, including non-base variants.
        target_identity = [e.identity for e in target]
        alias = next((old for old in seen if [e.identity for e in polish.entries[old]] == target_identity), None)
        if alias:
            for a, b in zip(polish.entries[alias], target):
                coverage[b.id] = {'status': 'alias', 'of': a.id}
            variant_audit.append({'scene': sid, 'alias_of': alias})
            seen.append(sid)
            continue
        original = polish.entries[base]
        ops = SequenceMatcher(None, [e.identity for e in original], target_identity, autojunk=False).get_opcodes()
        for tag, i1, i2, j1, j2 in ops:
            if tag == 'equal':
                for a, b in zip(original[i1:i2], target[j1:j2]):
                    coverage[b.id] = {'status': 'alias', 'of': a.id}
        put('## Wariant tekstu DLC — ' + title_maps[base])
        label = scene.get('variant') or 'odmienna wersja źródłowa'
        put(f'*Wersja: {label}. To alternatywny tekst tej samej misji, nie dalszy ciąg wydarzeń. '
            'Pokazano zmienione fragmenty wraz z bezpośrednim kontekstem; wspólnych ustępów nie powtarzamy.*')
        excerpt_audit = []
        for n, (tag, i1, i2, j1, j2, lo, hi) in enumerate(windows(ops, len(target)), 1):
            if tag == 'delete':
                put('#### Uwaga o wersji — tutaj pominięto poniższy fragment')
                for entry in original[i1:i2]:
                    put(reading_entry(entry, 'conditional'), entry.id, 'omission-note')
            put(f'### Fragment alternatywny {n}')
            for index in range(lo, hi):
                entry = target[index]
                kind = 'variant' if j1 <= index < j2 else 'context'
                show(entry, 'conditional', role=kind)
            excerpt_audit.append({'tag': tag, 'base': [i1, i2], 'target': [j1, j2], 'window': [lo, hi]})
        variant_audit.append({'scene': sid, 'base': base, 'excerpts': excerpt_audit})
        seen.append(sid)
    expected = {e.id for es in polish.entries.values() for e in es if e.kind in PROSE}
    need(expected <= coverage.keys(), f'Uncovered Polish prose: {sorted(expected - coverage.keys())}')
    # Check all aliases in Polish, not merely against the EN edition.
    for rid, item in coverage.items():
        if item['status'] == 'alias':
            need(pl_entries[rid].identity == pl_entries[item['of']].identity, f'Unsafe Polish alias: {rid}')
    shown = {a['row'] for a in audit if a['role'] != 'omission-note' and pl_entries[a['row']].kind in PROSE}
    aliases = expected - shown
    dialogue = sum(e.kind == 'dialogue' for es in polish.entries.values() for e in es)
    narration = len(expected) - dialogue
    put('---'); put('## Uwagi redakcyjne')
    put('- **Tekst:** Dialogi i narracja pochodzą bezpośrednio z zaakceptowanego pakietu PL3, z pól `pl` '
        'w `00_dialogue.jsonl`. Nie tłumaczono ponownie angielskiego scenariusza i nie dopisywano brakującej prozy. '
        'Techniczne zawijanie wierszy połączono w akapity; zachowano granice akapitów i treść myśli w nawiasach.')
    put('- **Imiona:** Znaczniki własnego imienia i nazwiska bohatera wyświetlono jako domyślne **Seishiro Kusanagi**. '
        'Nazwy rozmówców pochodzą z polskich pól tabel postaci. Osoby o wspólnych krótkich imionach rozróżniono '
        'pełnymi nazwami. Jawna anonimowość i kanał łączności mają pierwszeństwo przed portretem rozmówcy; '
        'technicznego prefiksu nie powtarzamy w wypowiedzi.')
    put('- **Układ:** Zachowano układ scen i redakcyjne drogowskazy angielskiego wydania. Tytuły misji i '
        'wyświetlane wpisy miejsca/czasu pochodzą z PL3. Pozostałe polskie nagłówki są wyłącznie drogowskazami '
        'redakcyjnymi, nie dodatkową narracją gry. Nie dodano początkowej listy odnośników.')
    put('- **Dialogi warunkowe:** Cytaty wyróżniają wymiany warunkowe, sytuacyjne i alternatywne rozstrzygnięcia. '
        'Nie każda taka wymiana jest opcjonalna. Kolejność źródłowa nie stanowi gwarantowanej kolejności rozgrywki; '
        'dokładnych wyzwalaczy nie dopowiadamy.')
    put('- **Wersje DLC:** Identyczne polskie ustępy pokazano raz. Zmienione fragmenty i jawne pominięcia są '
        'oznaczone osobno, z kontekstem. To wersje alternatywne, nie późniejsze wydarzenia. Zgodność kopii '
        'sprawdzono ponownie w języku polskim, zamiast zakładać ją na podstawie angielskiego tekstu.')
    put(f'- **Pokrycie:** Uwzględniono wszystkie **{dialogue} wypowiedzi** i **{narration} wpisów narracji** tego '
        f'epizodu: **{len(shown)} różnych wpisów** pokazano bezpośrednio, a **{len(aliases)} identycznych wpisów '
        'wersji alternatywnych** reprezentują odpowiadające im ustępy. Kontekst fragmentów może być powtórzony. '
        'Pominięto osobne cele misji, panele pomocy, techniczne etykiety silnika/kamery i puste wypełniacze.')
    put('- **Wydanie źródłowe:** Japońskie **1.08**, **NPJH50521**. Grupowanie scen: `06_scenes.jsonl`; '
        'tytuły misji i nazwy postaci: `05_mission_text.jsonl` i `07_names_characters.jsonl`. '
        'To wydanie do czytania, bez zmian w pakiecie gry i bez deklaracji pełnego testu rozgrywki.')
    result = ''.join(pieces)
    return result, {'episode': episode, 'source_sha256': polish.hashes, 'blocks': audit, 'coverage': coverage,
                    'variants': variant_audit, 'prose_total': len(expected), 'prose_shown_unique': len(shown),
                    'prose_aliased': len(aliases), 'output_sha256': sha(result.encode())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--english', type=Path, required=True)
    parser.add_argument('--polish', type=Path, required=True)
    parser.add_argument('--references', type=Path, required=True)
    parser.add_argument('--plans', type=Path, default=Path('docs/reading-script/polish'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--episodes', type=int, nargs='+', choices=range(4), default=(0, 1, 2, 3),
                        help='Select only requested episodes; 0 includes the prologue/training')
    args = parser.parse_args(argv)
    need(all(not args.out.resolve().is_relative_to(p.resolve()) for p in
             (args.english, args.polish, args.references, args.plans)), 'Refusing output among inputs')
    args.out.mkdir(parents=True, exist_ok=True)
    for episode in args.episodes:
        plan = json.loads((args.plans / f'episode_{episode:02}.json').read_bytes())
        reference = (args.references / f'srwoe_episode_{episode:02}.md').read_bytes()
        en = EarlyReadingSource(args.english, episode)
        pl = EarlyReadingSource(args.polish, episode, 'pl')
        text, audit = build(plan, en, pl, reference)
        (args.out / f'srwoe_episode_{episode:02}_PL.md').write_text(text, encoding='utf-8')
        (args.out / f'episode_{episode:02}_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
        print(episode, audit['prose_total'], audit['prose_shown_unique'], audit['prose_aliased'], audit['output_sha256'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
