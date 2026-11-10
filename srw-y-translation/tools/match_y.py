#!/usr/bin/env python3
"""Która linia pliku gry dostaje które polskie zdanie — dowodem jest zdanie.

Dlaczego to powstało (2026-11-10/11, po czterech nieudanych instalacjach PL7).
Plan adresuje linie **numerem** jednostki (`49.0#1` = identyfikator łańcucha plus
numer wystąpienia w pliku). Numer pochodzi z jednej, wybranej kopii pliku sceny.
Część scen leży w grze w **dwóch fizycznych kopiach o różnej treści**
(`Dlc1/31aad14a…` i `aa/StandaloneWindows64/986728319f…` dla
`cse20_2010_0201710a_sdemo.lua`): jedna ma 158 jednostek, druga 160. W takiej
kopii ten sam numer wskazuje **inne zdanie** albo nie istnieje wcale, a że numer
wystąpienia liczy się od początku pliku, jedna brakująca linia przesuwa numerację
wszystkim następnym.

Stara brama porównywała `numer → tekst` i przy pierwszej różnicy przerywała całą
instalację. Dawało to jeden komunikat na jedno uruchomienie u właściciela:
`216.0#1` (106/488), potem `103.1#1` (139/488), potem `49.0#1` (139/488)…
i tak bez końca, bo tekstu każdej kopii nie ma w repozytorium — jest tylko
na dysku właściciela.

Reguła, którą wprowadza ten moduł, jest **ostrzejsza**, nie luźniejsza:

    polskie zdanie trafia wyłącznie tam, gdzie tekst w pliku gry jest
    **co do znaku** tym, co tłumacz miał przed sobą.

Numer przestaje być dowodem i staje się tylko podpowiedzią (szybka ścieżka).
Dowodem jest równość zdania — a to gwarancja mocniejsza niż zgodność numeru,
bo zgodny numer nigdy nie dowodził, że pod spodem jest to samo zdanie.

Co z linii, których nie da się dopasować:

* linia pliku gry, której zdania **nie ma** w zwrotce tłumacza, zostaje
  oryginalna i trafia do raportu razem ze swoim tekstem z gry — to jest wsad do
  korpusu i do następnej paczki dla tłumacza, a nie „pominięcie po cichu”,
* linia, dla której pasuje **kilka** wierszy planu o **różnym** polskim tekście,
  nie dostaje nic i jest zgłoszona jako niejednoznaczna — zgadywanie tutaj
  byłoby wstawieniem polskiego zdania w cudze miejsce,
* wiersz planu, który nie trafił do **żadnej** kopii w grze, jest policzony
  i wypisany na końcu instalacji.
"""
from __future__ import annotations

import collections
from typing import NamedTuple

# Teksty wiersza planu, które wolno porównywać z plikiem gry. `pl` nigdy tu nie
# wchodzi: polski jest treścią patcha, nie dowodem tożsamości linii.
SOURCE_FIELDS = ('jp', 'en')


class SceneMatch(NamedTuple):
    """Wynik dopasowania jednej kopii pliku sceny do wierszy planu."""

    edits: dict          # klucz jednostki **w tym pliku** -> polski tekst
    applied: list        # klucze wierszy planu, które tu trafiły
    by_key: int          # dopasowane numerem i zdaniem (szybka ścieżka)
    by_text: int         # dopasowane samym zdaniem (inna numeracja kopii)
    divergent: list      # {'key', 'gra', 'plan'} — numer planu, inne zdanie w grze
    ambiguous: list      # {'key', 'gra', 'warianty'} — kilka różnych tłumaczeń
    unapplied: list      # klucze planu z polskim tekstem, których ta kopia nie ma


def units_in_order(script: str) -> list[tuple[str, str]]:
    """Jednostki pliku w kolejności z pliku: `(klucz, tekst)`."""
    from s6_scenario import parse_units, unit_key

    seen: collections.Counter = collections.Counter()
    return [(unit_key(unit, seen), unit['text']) for unit in parse_units(script)]


def source_texts(row: dict) -> tuple[str, ...]:
    """Teksty źródłowe wiersza (japoński, angielski) — bez pustych."""
    return tuple(row[field] for field in SOURCE_FIELDS if row.get(field) is not None)


def match_scene(units: list[tuple[str, str]], rows: dict) -> SceneMatch:
    """Dopasowuje wiersze planu do jednostek **tej** kopii pliku.

    `units` to lista `(klucz, tekst)` z pliku gry, `rows` to wiersze planu dla tej
    sceny (`klucz planu -> {'jp', 'en', 'pl'}`). Kolejność wyników jest
    deterministyczna: dwa przebiegi na tych samych danych dają to samo.
    """
    translated = {key: row for key, row in rows.items() if row.get('pl')}
    # Wiersze planu po zdaniu źródłowym — w kolejności planu, żeby powtórzenia
    # tego samego zdania szły po kolei (n-te wystąpienie w pliku bierze n-ty wiersz).
    by_text: dict[str, list[str]] = collections.defaultdict(list)
    for key, row in translated.items():
        for text in source_texts(row):
            by_text[text].append(key)

    edits: dict[str, str] = {}
    applied: list[str] = []
    used: set[str] = set()
    counts = {'key': 0, 'text': 0}

    # 1. Szybka ścieżka: numer się zgadza **i** zdanie się zgadza.
    for file_key, text in units:
        row = translated.get(file_key)
        if row is not None and text in source_texts(row) and file_key not in used:
            edits[file_key] = row['pl']
            applied.append(file_key)
            used.add(file_key)
            counts['key'] += 1

    # 2. Dowód ze zdania: kopia ma inną numerację, ale to samo zdanie.
    divergent: list[dict] = []
    ambiguous: list[dict] = []
    for file_key, text in units:
        if file_key in edits:
            continue
        candidates = [key for key in by_text.get(text, ()) if key not in used]
        if not candidates:
            if file_key in translated:
                # numer planu istnieje w tej kopii, ale mówi innym zdaniem:
                # to jest dokładnie ten przypadek, który wywracał instalację
                divergent.append({'key': file_key, 'gra': text,
                                  'plan': (source_texts(translated[file_key]) or ('',))[0]})
            continue
        variants = sorted({translated[key]['pl'] for key in candidates})
        if len(variants) > 1:
            ambiguous.append({'key': file_key, 'gra': text, 'warianty': variants})
            continue
        chosen = candidates[0]
        edits[file_key] = translated[chosen]['pl']
        applied.append(chosen)
        used.add(chosen)
        counts['text'] += 1

    unapplied = [key for key in translated if key not in used]
    return SceneMatch(edits=edits, applied=applied, by_key=counts['key'],
                      by_text=counts['text'], divergent=divergent,
                      ambiguous=ambiguous, unapplied=unapplied)


def match_table(existing: dict, rows: dict, lang: str) -> SceneMatch:
    """To samo dla tabeli: klucz jest nazwany, więc liczy się zgodność tekstu.

    Klucz tabeli (`00000019:079`) nie jest numerem pozycji, tylko nazwą pola, więc
    nie przesuwa się między kopiami. Zostaje jedno pytanie: czy gra trzyma pod tym
    kluczem ten sam tekst źródłowy, który widział tłumacz. Jeśli nie — nie piszemy
    tam nic i mówimy o tym w raporcie.
    """
    edits: dict[str, str] = {}
    applied: list[str] = []
    divergent: list[dict] = []
    unapplied: list[str] = []
    field = 'jp' if lang == 'ja' else 'en'
    for key, row in rows.items():
        expected = row.get(field)
        if key not in existing:
            # tej tabeli w tym języku po prostu nie ma takiego wiersza
            unapplied.append(key)
            continue
        if expected is None:
            if lang == 'en':
                # wiersz bez angielskiego źródła: nie ma czego porównać
                unapplied.append(key)
                continue
            divergent.append({'key': key, 'gra': existing[key], 'plan': ''})
            continue
        if existing[key] != expected:
            divergent.append({'key': key, 'gra': existing[key], 'plan': expected})
            continue
        if not row.get('pl'):
            unapplied.append(key)
            continue
        edits[key] = row['pl']
        applied.append(key)
    return SceneMatch(edits=edits, applied=applied, by_key=len(edits), by_text=0,
                      divergent=divergent, ambiguous=[], unapplied=unapplied)


def add_to_report(report: dict | None, kind: str, name: str, bundle: str,
                  match: SceneMatch) -> None:
    """Dokłada wynik jednej kopii do wspólnego raportu instalacji."""
    if report is None:
        return
    report.setdefault('zapisane', 0)
    report['zapisane'] += len(match.edits)
    report.setdefault('po_numerze', 0)
    report['po_numerze'] += match.by_key
    report.setdefault('po_zdaniu', 0)
    report['po_zdaniu'] += match.by_text
    applied = report.setdefault('trafione_wiersze', {}).setdefault(name, set())
    applied.update(match.applied)
    for item in match.divergent:
        report.setdefault('inny_tekst', []).append(
            {'plik': name, 'bundle': bundle, 'rodzaj': kind, **item})
    for item in match.ambiguous:
        report.setdefault('niejednoznaczne', []).append(
            {'plik': name, 'bundle': bundle, 'rodzaj': kind, **item})
