#!/usr/bin/env python3
"""Rebuild source-hash-bound SRW Y bundles from a validated Polish import plan.

Does not install into the game: caller supplies original bytes and gets rebuilt
bytes. Every target is checked against JP/EN, all edits are read back, and the
existing rebuild code verifies every untouched Unity object and side stream.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
from pathlib import PurePosixPath
import re

import UnityPy
from build_pl_scene_patch import apply_pl, textasset_raw
from s6_scenario import parse_units, unit_key
from s6_tables import table_header, walk_records
from s6_write import encode_table
from srw_y_bundle_crypt import decrypt, encrypt
from srw_y_rebuild import rebuild_plain


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: str) -> str:
    p = PurePosixPath(value)
    if (not value or '\\' in value or p.is_absolute() or any(x in ('.', '..') for x in p.parts)
            or any(':' in x for x in p.parts) or not value.endswith('.bundle')):
        raise ValueError(f'niebezpieczna ścieżka: {value}')
    if not (value.startswith('aa/StandaloneWindows64/') or len(p.parts) == 2):
        raise ValueError(f'nieoczekiwana ścieżka: {value}')
    return value


def jobs_for(plan: dict, index: dict) -> dict:
    if plan.get('schema') != 1 or index.get('schema') != 1:
        raise ValueError('nieobsługiwana wersja planu lub indeksu')
    wanted_tables = plan['tables']
    wanted_scenes = plan['scenes']
    seen_tables, seen_scenes = set(), set()
    jobs = {}
    for path, entry in index['bundles'].items():
        safe_relative(path)
        if not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']):
            raise ValueError(f'{path}: nieprawidłowy hash')
        tables = [t for t in entry['tables'] if t['table'] in wanted_tables]
        scenes = [s for s in entry['scenes'] if s['name'] in wanted_scenes]
        if not tables and not scenes:
            continue
        for item in tables:
            if item['lang'] not in ('ja', 'en'):
                raise ValueError(f'{path}: nieznany język')
            seen_tables.add((item['table'], item['lang']))
        for item in scenes:
            if item['lang'] not in ('ja', 'en'):
                raise ValueError(f'{path}: nieznany język')
            seen_scenes.add((item['name'], item['lang']))
        ids = [x['path_id'] for x in tables + scenes]
        if len(set(ids)) != len(ids):
            raise ValueError(f'{path}: powtórzony identyfikator obiektu')
        jobs[path] = {'source': entry, 'tables': tables, 'scenes': scenes}
    for kind, wanted, seen in (('tabela', wanted_tables, seen_tables),
                                ('scena', wanted_scenes, seen_scenes)):
        for name, rows in wanted.items():
            for lang in ('ja', 'en'):
                if any(row.get('jp' if lang == 'ja' else 'en') is not None for row in rows.values()):
                    if (name, lang) not in seen:
                        raise ValueError(f'{kind} {name}: brak obiektu {lang} w indeksie')
    if not jobs:
        raise ValueError('plan nie zawiera żadnych celów')
    return jobs


def units(script: str) -> dict:
    seen = Counter()
    return {unit_key(u, seen): u['text'] for u in parse_units(script)}


def table_edit(name: str, raw: bytes, rows: dict, lang: str):
    start, count = table_header(raw, name)
    before, _ = walk_records(raw, start, count)
    existing = {r['key']: r['text'] for r in before}
    if len(existing) != len(before):
        raise ValueError(f'{name}: powtórzone klucze tabeli')
    edits = {}
    for key, row in rows.items():
        expected = row['jp' if lang == 'ja' else 'en']
        if expected is None and lang == 'en' and key not in existing:
            continue
        if key not in existing or existing[key] != expected:
            raise ValueError(f'{name}: brak lub inny tekst klucza {key}')
        edits[key] = row['pl']
    new_raw = encode_table(raw, edits)
    start, new_count = table_header(new_raw, name)
    after = walk_records(new_raw, start, new_count)[0]
    if new_count != count or any(r['text'] != edits.get(r['key'], existing[r['key']]) for r in after):
        raise ValueError(f'{name}: zapis tabeli nie przeszedł kontroli')
    return new_raw, len(edits)


def scene_edit(name: str, raw: bytes, script: str, rows: dict, lang: str):
    old = units(script)
    edits = {}
    for key, row in rows.items():
        expected = row['jp' if lang == 'ja' else 'en']
        if expected is None and lang == 'en' and key not in old:
            continue
        if key not in old or old[key] != expected:
            raise ValueError(f'{name}: brak lub inny tekst wystąpienia {key}')
        edits[key] = row['pl']
    new, used = apply_pl(script, edits)
    if used != set(edits):
        raise ValueError(f'{name}: nie wszystkie wystąpienia zostały zapisane')
    now = units(new)
    if now != {key: edits.get(key, text) for key, text in old.items()}:
        raise ValueError(f'{name}: kontrola zapisanych wystąpień nie przeszła')
    return textasset_raw(raw, new.encode('utf-8')), len(edits)


def build_bundle(path: str, cipher: bytes, job: dict, plan: dict):
    if sha(cipher) != job['source']['sha256']:
        raise ValueError(f'{path}: niezgodna wersja oryginału')
    name = PurePosixPath(path).name
    plain = decrypt(name, cipher)
    env = UnityPy.load(plain)
    objects = {o.path_id: o for o in env.objects}
    edits, counts = {}, Counter()
    for item in job['tables']:
        obj = objects.get(item['path_id'])
        if obj is None or obj.type.name != 'MonoBehaviour' or str(obj.read().m_Name) != item['name']:
            raise ValueError(f"{path}: niezgodny obiekt tabeli {item['name']}")
        new, count = table_edit(item['name'], obj.get_raw_data(), plan['tables'][item['table']], item['lang'])
        edits[item['path_id']] = new
        counts['table_' + item['lang']] += count
    for item in job['scenes']:
        obj = objects.get(item['path_id'])
        if obj is None or obj.type.name != 'TextAsset':
            raise ValueError(f"{path}: brak obiektu sceny {item['name']}")
        data = obj.read()
        if str(data.m_Name) != item['name']:
            raise ValueError(f"{path}: niezgodna nazwa sceny {item['name']}")
        new, count = scene_edit(item['name'], obj.get_raw_data(), data.m_Script,
                                plan['scenes'][item['name']], item['lang'])
        edits[item['path_id']] = new
        counts['scene_' + item['lang']] += count
    rebuilt, _ = rebuild_plain(name, plain, edits)
    cipher_out = encrypt(name, rebuilt)
    if decrypt(name, cipher_out) != rebuilt:
        raise ValueError(f'{path}: niezgodność szyfrowania')
    final = {o.path_id: o.get_raw_data() for o in UnityPy.load(rebuilt).objects if o.path_id in edits}
    if final != edits:
        raise ValueError(f'{path}: odczyt edytowanych obiektów niezgodny z zapisem')
    return cipher_out, dict(counts)
