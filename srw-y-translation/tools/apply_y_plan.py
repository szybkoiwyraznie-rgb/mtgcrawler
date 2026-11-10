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
    # Co indeks ma po japońsku — liczone **przed** pętlą, bo w trakcie rośnie
    # `seen_scenes` i kolejne bundle gubiłyby swoje luki.
    indexed_ja = {item['name'] for entry in index['bundles'].values()
                  for item in entry['scenes'] if item['lang'] == 'ja'}
    # Scena z udowodnionym bliźniakiem jest już pokryta — jej własne bundle bywają
    # chińskie/koreańskie, więc szukanie jej „po nazwie” tylko by je wciągnęło.
    indexed_ja |= {name for name, rows in wanted_scenes.items() if sibling_exception(rows)}
    jobs = {}
    for path, entry in index['bundles'].items():
        safe_relative(path)
        if not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']):
            raise ValueError(f'{path}: nieprawidłowy hash')
        tables = [t for t in entry['tables'] if t['table'] in wanted_tables]
        scenes = [s for s in entry['scenes'] if s['name'] in wanted_scenes]
        prefixes = tuple((entry.get('by_name') or {}).get('scenes') or ())
        # `by_name` uzupełnia **tylko** luki: scena, której indeks nie ma po japońsku,
        # dostaje kandydatów z bundli właściciela. Scen już pokrytych nie ruszamy,
        # żeby rozszerzenie indeksu nie zmieniło wydanego patcha.
        by_name = sorted(name for name in wanted_scenes
                         if name.startswith(prefixes) and name not in indexed_ja)
        if not tables and not scenes and not by_name:
            continue
        for item in tables:
            if item['lang'] not in ('ja', 'en'):
                raise ValueError(f'{path}: nieznany język')
            seen_tables.add((item['table'], item['lang']))
        for item in scenes:
            if item['lang'] not in ('ja', 'en'):
                raise ValueError(f'{path}: nieznany język')
            seen_scenes.add((item['name'], item['lang']))
        # Bundle, w którym obiekt rozpoznajemy po nazwie: oba języki są możliwe,
        # a o tym, który jest w środku, decyduje tekst porównany przy zapisie.
        seen_scenes.update((name, lang) for name in by_name for lang in ('ja', 'en'))
        ids = [x['path_id'] for x in tables + scenes]
        if len(set(ids)) != len(ids):
            raise ValueError(f'{path}: powtórzony identyfikator obiektu')
        jobs[path] = {'source': entry, 'tables': tables, 'scenes': scenes,
                      'by_name': by_name}
    for kind, wanted, seen in (('tabela', wanted_tables, seen_tables),
                                ('scena', wanted_scenes, seen_scenes)):
        for name, rows in wanted.items():
            for lang in ('ja', 'en'):
                if any(row.get('jp' if lang == 'ja' else 'en') is not None for row in rows.values()):
                    if (name, lang) not in seen:
                        # The EN-only variant has no JA asset; its JP text is
                        # an explicitly source-bound reference to a sibling.
                        # Never grant the exception to tables or genuine JA rows.
                        inferred = (kind == 'scena' and lang == 'ja' and (name, 'en') in seen
                                    and sibling_exception(rows))
                        if not inferred:
                            raise ValueError(f'{kind} {name}: brak obiektu {lang} w indeksie')
    if not jobs:
        raise ValueError('plan nie zawiera żadnych celów')
    return jobs


SIBLING_METHODS = {'variant line matched to the JP sibling',
                  'variant line matched to an exact JP sibling line'}


def sibling_exception(rows: dict) -> bool:
    """Czy scena ma udowodniony japoński bliźniak zamiast własnego obiektu `ja`?

    Wariant, który w grze istnieje tylko po angielsku, ma japoński tekst wiersza
    w bliźniaczej scenie; plan trzyma wtedy ślad (`jp_sibling_reference`). Tylko
    taki wiersz może nie mieć obiektu `ja` w indeksie.
    """
    return all(not row.get('jp') or (
        isinstance(row.get('jp_sibling_reference'), dict)
        and row['jp_sibling_reference'].get('method') in SIBLING_METHODS
        and isinstance(row['jp_sibling_reference'].get('file'), str)
        and row['jp_sibling_reference']['file'].endswith('.lua')
        and row.get('en') is not None) for row in rows.values())


def still_missing(plan: dict, index: dict, jobs: dict) -> list[str]:
    """Sceny, które plan tłumaczy, a których nie ma ani w indeksie, ani w `by_name`."""
    seen = {(s['name'], s['lang']) for job in jobs.values() for s in job['scenes']}
    seen |= {(name, lang) for job in jobs.values() for name in job.get('by_name', ())
             for lang in ('ja', 'en')}
    missing = []
    for name, rows in plan.get('scenes', {}).items():
        filled = [row for row in rows.values() if row.get('pl')]
        if not filled or sibling_exception(rows):
            continue
        if (name, 'ja') not in seen:
            missing.append(name)
    return sorted(missing)


def name_jobs(plan: dict, jobs: dict) -> list[dict]:
    """Obiekty, których indeks nie zna `path_id` — rozwiązywane w pliku gracza.

    `path_id` jest liczbą z konkretnej kompilacji assetów. Dla bundli, które
    dostaliśmy później, indeks zna tylko nazwę obiektu (`by_name`), więc patcher
    szuka obiektu po nazwie w bundlu gracza, sprawdza, czy *każde* jego wystąpienie
    zgadza się z planem, i dopiero wtedy go zapisuje. Numer nigdy nie pochodzi
    z cudzej kompilacji.
    """
    wanted = plan.get('scenes', {})
    return [{'path': path, 'name': name}
            for path, job in sorted(jobs.items())
            for name in wanted
            if name in job.get('by_name', ())]


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


def scene_edits(script: str, rows: dict) -> dict:
    """Wiersze planu, które wolno zapisać: każde wystąpienie musi się zgadzać.

    Język bierzemy z tekstu w grze, nie z nazwy pliku: nowsze bundle trzymają
    japoński pod sufiksem `_sdemo`, a angielski pod tym samym `_sdemo` w innym
    bundlu. Dla wiersza, w którym plan nie ma tekstu w danym języku (`None`),
    wystąpienie może po prostu nie istnieć.
    """
    old = units(script)
    edits = {}
    for key, row in rows.items():
        if key not in old:
            if row.get('jp') is None or row.get('en') is None:
                continue
            raise ValueError(f'brak wystąpienia {key}')
        # jp i en bywają identyczne (nazwy, liczby) — wtedy nie ma czego rozstrzygać
        if not any(old[key] == row.get(lang) for lang in ('jp', 'en')):
            raise ValueError(f'inny tekst wystąpienia {key}')
        edits[key] = row['pl']
    return edits


def scene_match_count(script: str, rows: dict) -> int:
    """Ile wierszy planu w tym pliku ma tekst równy japońskiemu albo angielskiemu."""
    old = units(script)
    return sum(1 for key, row in rows.items()
               if key in old and any(old[key] == row.get(lang) for lang in ('jp', 'en')))


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


def build_bundle(path: str, cipher: bytes, job: dict, plan: dict,
                 named: list[dict] | None = None, written: set | None = None):
    """Przebudowuje bundle. `named` to obiekty scen znalezione po nazwie.

    Każdy taki obiekt jest zapisywany tylko wtedy, gdy wszystkie jego wystąpienia
    zgadzają się z planem; liczba zapisanych wystąpień musi się zgadzać co do
    sztuki, inaczej bundle nie powstaje.
    """
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
    for item in named or []:
        if item['path'] != path:
            continue
        found = [obj for obj in objects.values()
                 if obj.type.name == 'TextAsset' and str(obj.read().m_Name) == item['name']]
        if not found:
            # `by_name` mówi, w których bundlach *może* leżeć plik o tym prefiksie,
            # a nie w którym leży: tej informacji nie ma w repozytorium. Brak pliku
            # w tym bundlu jest więc normalny — jest w sąsiednim.
            continue
        if len(found) != 1:
            raise ValueError(f"{path}: obiektów o nazwie {item['name']}: {len(found)}")
        data = found[0].read()
        try:
            chosen = scene_edits(data.m_Script, plan['scenes'][item['name']])
        except ValueError:
            # Ten sam plik sceny leży w grze w kilku językach. Jeśli w tym obiekcie
            # ani jedna linia nie zgadza się z japońskim/angielskim z planu, to jest
            # chińska albo koreańska kopia — nie ruszamy jej. Częściowe dopasowanie
            # (np. zmieniony plik gry) nadal przerywa pracę.
            if scene_match_count(data.m_Script, plan['scenes'][item['name']]) == 0:
                counts['pominiete_kopie_w_innym_jezyku'] += 1
                continue
            raise
        new, used = apply_pl(data.m_Script, chosen)
        if used != set(chosen):
            raise ValueError(f"{item['name']}: nie wszystkie wystąpienia zostały zapisane")
        before = units(data.m_Script)
        if units(new) != {key: chosen.get(key, text) for key, text in before.items()}:
            raise ValueError(f"{item['name']}: kontrola zapisanych wystąpień nie przeszła")
        edits[found[0].path_id] = textasset_raw(found[0].get_raw_data(), new.encode('utf-8'))
        counts['scene_by_name'] += len(chosen)
        if written is not None:
            written.add(item['name'])
    rebuilt, _ = rebuild_plain(name, plain, edits)
    cipher_out = encrypt(name, rebuilt)
    if decrypt(name, cipher_out) != rebuilt:
        raise ValueError(f'{path}: niezgodność szyfrowania')
    final = {o.path_id: o.get_raw_data() for o in UnityPy.load(rebuilt).objects if o.path_id in edits}
    if final != edits:
        raise ValueError(f'{path}: odczyt edytowanych obiektów niezgodny z zapisem')
    return cipher_out, dict(counts)
