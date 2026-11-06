#!/usr/bin/env python3
"""Experimental pilot-label repair using ONLY existing bytes in installed DLC.

Works on a COPY of installed PL v4.10-compatible configNN/imenuNN pairs. No
pointers, record sizes, archive directory entries, or other bytes move. Input
files are never modified. Short labels/names are unavoidable where the original
field is smaller than the Polish translation. Not a production release or a
proof that gameplay and saves are safe. Never include game output in Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

import configst_pack as PAC
import container_mix as CM
import cpk_table
import pl_text
import table_write as TW

MEMBER = re.compile(r'^srwDL_CharaDictionary(\d\d)\.bin$')
JAPANESE = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')
NICK = pl_text.encode('Pseudonim: ')
VOICE = pl_text.encode('Głos: ')
SHORT_NICK = pl_text.encode('Ps.: ')
# Full target text -> shorter text only where the original byte slot is too
# small. These alternatives concern text already in the Polish package.
SHORT = {
    'Hero Lamuness (Lamune Baba)': 'Hero Lamuness(Lamune Baba)',
    'Hebi Metako': 'HebiMetako',
    'Chirico': 'Chiri.',
    'Hagu Hagu': 'HaguHagu',
    'Król Pafuricii': 'Król Pafur.',
    'Królowa Pafuricii': 'Król. Pafur.',
    'Shinn': 'Shi.',
    'Vanilla': 'Vanil.',
    'Coconna': 'Cocon.',
    'Evil God Drago': 'Bóg Drago',
    '＠０\rHiltz zespolony z rdzeniem Death Saurera.': '＠０\rHiltz i rdzeń Death Saurera w jednym.',
}


def _clip(text: str, limit: int) -> str:
    result = ''
    for char in text:
        if len(pl_text.encode(result + char)) > limit:
            break
        result += char
    return result


def _actor(text: str, limit: int) -> str:
    if len(pl_text.encode(text)) <= limit:
        return text
    words = text.split()
    if not words or limit < 4:
        raise ValueError('voice actor cannot be abbreviated safely')
    prefix = words[0][0] + '.' if len(words) > 1 else ''
    surname = words[-1]
    if len(pl_text.encode(prefix + surname)) <= limit:
        return prefix + surname
    room = limit - len(pl_text.encode(prefix)) - 1
    if room < 1:
        raise ValueError('voice actor slot too small')
    return prefix + _clip(surname, room) + '.'


def _fitted(target: bytes, limit: int) -> bytes:
    if len(target) <= limit:
        return target
    text = pl_text.decode(target)
    if text not in SHORT:
        raise ValueError(f'translation does not fit: {text!r} ({len(target)} > {limit})')
    result = pl_text.encode(SHORT[text])
    if len(result) > limit:
        raise ValueError('short translation does not fit')
    return result


def repair_pool(before: bytes, target: bytes, name: str) -> tuple[bytes, list[dict]]:
    if not MEMBER.fullmatch(name):
        raise ValueError('unexpected dictionary name')
    fam = TW.family_of(name)
    spans_a, spans_b = TW.record_spans(before), TW.record_spans(target)
    a, b = TW.parse_pool(before, fam), TW.parse_pool(target, fam)
    keys_a = [TW.record_key(before, span, fam) for span in spans_a]
    keys_b = [TW.record_key(target, span, fam) for span in spans_b]
    if keys_a != keys_b:
        raise ValueError(f'{name}: record keys/order mismatch')
    output = bytearray(before)
    edits: list[dict] = []
    for i, (left, right) in enumerate(zip(a, b)):
        if left.unexplained_refs:
            raise ValueError(f'{name}: unexplained reference in record {i}')
        for slot in (1, 2, 4, 5, 10, 11):
            if JAPANESE.search(pl_text.decode(right.strings[slot])):
                raise ValueError(f'{name} record {i} slot {slot}: imenu has untranslated Japanese')
        proposed: dict[int, bytes] = {}
        for slot in (2, 10, 11):
            if left.strings[slot].rstrip(b' ') != right.strings[slot]:
                proposed[slot] = _fitted(right.strings[slot], len(left.strings[slot]))
        if left.strings[4].rstrip(b' ') != right.strings[4]:
            if not right.strings[4].startswith(NICK):
                raise ValueError(f'{name}: target nickname label is not Polish')
            nickname = right.strings[4][len(NICK):]
            full = NICK + nickname
            proposed[4] = full if len(full) <= len(left.strings[4]) else SHORT_NICK + nickname
        actor_different = left.strings[1].rstrip(b' ') != right.strings[1]
        voice_different = left.strings[5].rstrip(b' ') != right.strings[5]
        if actor_different or voice_different:
            if not right.strings[5].startswith(VOICE) or right.strings[5][len(VOICE):] != right.strings[1]:
                raise ValueError(f'{name}: actor fields do not match')
            actor_text = pl_text.decode(right.strings[1])
            limits = []
            if actor_different:
                limits.append(len(left.strings[1]))
            if voice_different:
                limits.append(len(left.strings[5]) - len(VOICE))
            actor = pl_text.encode(_actor(actor_text, min(limits)))
            if actor_different:
                proposed[1] = actor
            if voice_different:
                proposed[5] = VOICE + actor
        start, end = spans_a[i]
        for slot, value in proposed.items():
            old = left.strings[slot]
            if not value or b'\0' in value or len(value) > len(old):
                raise ValueError(f'{name} record {i} slot {slot}: invalid or oversized value')
            if JAPANESE.search(pl_text.decode(value)):
                raise ValueError(f'{name} record {i} slot {slot}: target still Japanese')
            pos = start + left.pointers[slot]
            if pos + len(old) >= end or before[pos:pos + len(old)] != old or before[pos + len(old)] != 0:
                raise ValueError('slot bounds mismatch')
            padded = value.ljust(len(old), b' ')
            if padded == old:
                continue
            output[pos:pos + len(old)] = padded
            edits.append({'index': i, 'key': keys_a[i], 'slot': slot,
                          'offset': pos, 'bytes': len(old),
                          'result': pl_text.decode(value), 'target': pl_text.decode(right.strings[slot])})
    result = bytes(output)
    if len(result) != len(before) or TW.record_spans(result) != spans_a:
        raise ValueError('dictionary layout changed')
    reread = TW.parse_pool(result, fam)
    touched = {(e['index'], e['slot']): e for e in edits}
    for i, (prior, now) in enumerate(zip(a, reread)):
        if prior.prefix != now.prefix or prior.tail != now.tail or prior.pointers != now.pointers:
            raise ValueError('record metadata, padding or pointers changed')
        for slot in range(12):
            edit = touched.get((i, slot))
            expected = pl_text.encode(edit['result']).ljust(edit['bytes'], b' ') if edit else prior.strings[slot]
            if now.strings[slot] != expected:
                raise ValueError('slot readback mismatch')
    return result, edits


def load_hash_pins() -> dict:
    hash_file = Path(__file__).with_name('fixed-pilot-test-v410-hashes.json')
    if not hash_file.exists():
        hash_file = Path(__file__).resolve().parent.parent / 'config/pl/fixed-pilot-test-v410-hashes.json'
    return json.loads(hash_file.read_text(encoding='utf-8'))


def patch_config(config: Path, imenu: Path) -> tuple[bytes, dict]:
    original = config.read_bytes()
    index = cpk_table.read_cpk_table(config)
    entries = index['entries']
    if len(entries) != 1 or not entries[0]['name'].lower().endswith('.pac'):
        raise ValueError(f'{config.name}: expected one PAC member')
    entry = entries[0]
    if entry['compressed']:
        raise ValueError(f'{config.name}: compressed PAC cannot be patched in place')
    pac_start, pac_size = entry['absolute_offset'], entry['file_size']
    pac = original[pac_start:pac_start + pac_size]
    info = PAC.parse_pac(pac)
    subs = info['subs']
    if any(s['offset'] < info['data_base'] or s['offset'] + s['size'] > len(pac) for s in subs):
        raise ValueError('invalid PAC subfile range')
    ranges = sorted((s['offset'], s['offset'] + s['size']) for s in subs)
    if any(ranges[i][1] > ranges[i + 1][0] for i in range(len(ranges) - 1)):
        raise ValueError('overlapping PAC members')
    matches = [s for s in subs if MEMBER.fullmatch(s['name'])]
    if len(matches) != 1:
        raise ValueError(f'{config.name}: expected one character dictionary')
    sub = matches[0]
    _, translations, _ = CM.members_of(imenu)
    if sub['name'] not in translations:
        raise ValueError(f'{imenu.name}: missing matching dictionary')
    pins = load_hash_pins().get(sub['name'])
    digest = lambda data: hashlib.sha256(data).hexdigest()
    if (not pins or digest(sub['data']) not in pins['source_sha256']
            or digest(translations[sub['name']]) != pins['imenu_sha256']):
        raise ValueError(f'{config.name}/{imenu.name}: incompatible dictionary version')
    changed, edits = repair_pool(sub['data'], translations[sub['name']], sub['name'])
    pos = pac_start + sub['offset']
    result = original[:pos] + changed + original[pos + sub['size']:]
    if len(result) != len(original) or result[:pos] != original[:pos] or result[pos + sub['size']:] != original[pos + sub['size']:]:
        raise ValueError('container bytes outside dictionary changed')
    for i, (a, b) in enumerate(zip(original, result)):
        if a != b and not any(pos + e['offset'] <= i < pos + e['offset'] + e['bytes'] for e in edits):
            raise ValueError('byte outside an edited string changed')
    return result, {'container': config.name, 'dictionary': sub['name'], 'edits': edits,
                    'sha256_before': hashlib.sha256(original).hexdigest(),
                    'sha256_after': hashlib.sha256(result).hexdigest(),
                    'bytes': len(result)}


def build(source: Path, out: Path) -> dict:
    source = source.resolve(strict=True)
    out = out.resolve()
    if not source.is_dir() or out.exists() or source == out or source in out.parents or out in source.parents:
        raise ValueError('select input folder and a NEW separate output folder')
    candidates = sorted(p for p in source.iterdir() if re.fullmatch(r'config\d\d\.EDAT', p.name, re.I) and p.is_file())
    if not candidates:
        raise ValueError('no configNN.EDAT files found in selected folder')
    by_name = {p.name.casefold(): p for p in source.iterdir() if p.is_file()}
    if len(by_name) != sum(p.is_file() for p in source.iterdir()):
        raise ValueError('duplicate names ignoring case')
    out.parent.mkdir(parents=True, exist_ok=True)
    reports = []
    with tempfile.TemporaryDirectory(prefix='.pilot-test-', dir=out.parent) as tmp:
        stage = Path(tmp) / 'wynik-test'
        (stage / 'NOWE').mkdir(parents=True)
        (stage / 'KOPIE').mkdir()
        expected_dictionaries = load_hash_pins()
        for config in candidates:
            _, members, _ = CM.members_of(config)
            dicts = [n for n in members if MEMBER.fullmatch(n)]
            expected = f'srwDL_CharaDictionary{config.name[6:8]}.bin'
            if not dicts:
                if expected in expected_dictionaries:
                    raise ValueError(f'{config.name}: missing expected character dictionary')
                continue
            if len(dicts) != 1:
                raise ValueError(f'{config.name}: multiple character dictionaries')
            if MEMBER.fullmatch(dicts[0]).group(1) != config.name[6:8]:
                raise ValueError(f'{config.name}: dictionary number mismatch')
            if not TW.record_spans(members[dicts[0]]):
                if expected in expected_dictionaries:
                    raise ValueError(f'{config.name}: expected dictionary is empty')
                continue
            suffix = config.name[6:8]
            imenu = by_name.get(f'imenu{suffix}.edat'.casefold())
            if imenu is None:
                raise ValueError(f'{config.name}: missing imenu{suffix}.EDAT')
            result, report = patch_config(config, imenu)
            if not report['edits']:
                continue
            if hashlib.sha256(config.read_bytes()).hexdigest() != report['sha256_before']:
                raise ValueError('input changed during build')
            (stage / 'NOWE' / config.name).write_bytes(result)
            (stage / 'KOPIE' / config.name).write_bytes(config.read_bytes())
            if hashlib.sha256((stage / 'NOWE' / config.name).read_bytes()).hexdigest() != report['sha256_after']:
                raise ValueError('output readback failed')
            if hashlib.sha256((stage / 'KOPIE' / config.name).read_bytes()).hexdigest() != report['sha256_before']:
                raise ValueError('backup readback failed')
            reports.append(report)
        if not reports:
            raise ValueError('no matching untranslated fields found; nothing written')
        summary = {'experimental': True, 'runtime_verified': False, 'input_folder': str(source),
                   'containers_changed': len(reports), 'cells_changed': sum(len(r['edits']) for r in reports),
                   'containers': reports}
        (stage / 'RAPORT.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if out.exists():
            raise ValueError('output appeared during build')
        stage.rename(out)
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    report = build(args.source, args.out)
    print(f"Zmienione pliki: {report['containers_changed']}, pola: {report['cells_changed']}")
    print('Test eksperymentalny: wejście i zapisy gry nie zostały zmienione.')


if __name__ == '__main__':
    main()
