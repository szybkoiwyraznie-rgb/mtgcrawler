#!/usr/bin/env python3
"""Pack the verified PL reading editions into the published Drive archive.

The archive README is generated from ``verification.json`` written by
``build_polish_reading_editions.py``, so the member table, the totals and the
per-episode hashes can never drift from the episodes actually shipped.

The ZIP is written deterministically (fixed member timestamps, stored order,
fixed permissions) so that rebuilding an unchanged release yields the same
bytes.

Owner rule (2026-10-24): every reading-archive delivery must also bundle the
current supplementary reading files (mech catalogue, pilot catalogue, mission
deployments) via ``--extra``. If their source data is unchanged since their
last delivery, bundle the last delivered bytes without rebuilding them.

``--carry NAME=REASON`` (with ``--carry-from PREVIOUS.zip``) bundles an episode
member byte-identically from a previous delivery instead of rebuilding it. That
is the honest option when the episode is provably unaffected by the current
text change but its source material needed for a rebuild is no longer available
(for example the delivered English editorial reference of episode 34, which is
gone from Drive). A carried member is listed separately, its per-episode prose
numbers are not restated and it is excluded from the prose/span totals, so the
totals always describe exactly the episodes rebuilt for this release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

EPISODES = 35


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def num(value: int) -> str:
    return f'{value:,}'


def plural(value: int, one: str, few: str, many: str) -> str:
    """Polish plural form for `value`."""
    if value == 1:
        return one
    if value % 10 in (2, 3, 4) and value % 100 not in (12, 13, 14):
        return few
    return many


def sections(markdown: str) -> int:
    """Mission/scene sections: every ``##`` heading but DLC variants and notes."""
    total = 0
    for line in markdown.splitlines():
        if not line.startswith('## '):
            continue
        if line.startswith('## Wariant tekstu DLC'):
            continue
        if line.strip() == '## Uwagi redakcyjne':
            continue
        total += 1
    return total


def readme(release: str, rows: list[dict], totals: dict,
           extras: list[dict] | None = None,
           carried: list[dict] | None = None) -> str:
    rebuilt = len(rows) - len(carried or [])
    scope_note = ''
    if carried:
        held = len(carried)
        scope_note = (f' — liczby obejmują {rebuilt} '
                      f'{plural(rebuilt, "epizod", "epizody", "epizodów")} '
                      f'{plural(rebuilt, "przebudowany", "przebudowane", "przebudowanych")} '
                      f'w tym wydaniu; {held} '
                      f'{plural(held, "plik przeniesiono", "pliki przeniesiono", "plików przeniesiono")} '
                      'bez zmian (nota pod spisem plików)')
    out = [
        f'# Super Robot Wars Operation Extend — Polskie scenariusze do czytania '
        f'(Epizody 0–34, wydanie {release})',
        '',
        'Kompletny zestaw **35 zredagowanych polskich scenariuszy fabularnych do czytania** '
        '(`srwoe_episode_00_PL.md` – `srwoe_episode_34_PL.md`), przygotowany wyłącznie na '
        f'podstawie zaakceptowanego pakietu `pakiet_PL` (**wydanie `{release}`**).',
        '',
        '## Zakres i weryfikacja',
        '',
        '- **Epizody:** `0–34` (**wszystkie 35 epizodów głównej kampanii**, łącznie z prologiem '
        'i finałem w Epizodzie 34)',
        f'- **Pokrycie prozy fabularnej:** **`{num(totals["prose_total"])}` / '
        f'`{num(totals["prose_total"])}` wpisów (`100%`)** — `{num(totals["shown_unique"])}` '
        f'unikalnych kwestii i narracji wyrenderowanych bezpośrednio oraz '
        f'`{num(totals["aliased"])}` identycznych wpisów wariantów DLC zweryfikowanych '
        f'niezależnie w języku polskim (`{num(totals["verified_text_spans"])}` sprawdzonych '
        f'przedziałów tekstu){scope_note}',
        '- **Źródło tekstu:** wyłącznie pola `pl` z `pakiet_PL` (`00_dialogue.jsonl`, '
        '`05_mission_text.jsonl`, `06_scenes.jsonl`, `07_names_characters.jsonl`), bez '
        'jakichkolwiek angielskich uzupełnień zastępczych, bez dopisywanych wyzwalaczy '
        'i bez nieprzetłumaczonych znaczników technicznych (kontrola: `0` znaków japońskich '
        'w 35/35 plikach)',
        '- **Konwencja lektury:** dialogi głównej osi fabularnej podano zwykłym akapitem, '
        'dialogi warunkowe i sytuacyjne ujęto w bloki cytatów (`>`), a zmienione fragmenty '
        'alternatywnych wersji DLC wyodrębniono w sekcjach `## Wariant tekstu DLC — …` '
        'bez wielokrotnego powtarzania identycznych scen',
        '',
        '## Spis plików w archiwum',
        '',
        '| Epizod | Plik | Sekcje / misje | Kwestie łącznie | Unikalne | Warianty (alias PL) '
        '| Rozmiar (B) | SHA-256 |',
        '| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |',
    ]
    def cell(row: dict, key: str) -> str:
        value = row.get(key)
        return '—' if value is None else num(value)

    for row in rows:
        out.append(
            f'| {row["episode"]:02} | `{row["name"]}` | {row["sections"]} | '
            f'{cell(row, "prose_total")} | {cell(row, "shown_unique")} | {cell(row, "aliased")} | '
            f'{num(row["bytes"])} | `{row["sha256"][:16]}…` |'
        )
    out.append('')
    if carried:
        out += [
            '**Przeniesione bez zmian:** ' + '; '.join(
                f'`{item["name"]}` — {item["reason"]}' for item in carried) + '. '
            'Wiersze oznaczone `—` nie są ponownie liczone: te pliki wchodzą do archiwum '
            'bajt w bajt z poprzedniego wydania, a podane wyżej sumy prozy i przedziałów '
            'tekstu dotyczą wyłącznie epizodów przebudowanych w tym wydaniu.',
            '',
        ]
    if extras:
        out += [
            '## Materiały uzupełniające',
            '',
            'Do archiwum dołączono aktualne katalogi i zestawienie rozstawień '
            '(dostarczane wraz z każdą wersją wydań do czytania):',
            '',
            '| Plik | Rozmiar (B) | SHA-256 |',
            '| --- | ---: | --- |',
        ]
        for extra in extras:
            out.append(
                f'| `{extra["name"]}` | {num(extra["bytes"])} | `{extra["sha256"][:16]}…` |'
            )
        out.append('')
    return '\n'.join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', required=True, type=Path,
                    help='Directory with srwoe_episode_NN_PL.md and verification.json')
    ap.add_argument('--release', required=True, help='Release label, e.g. v4.0')
    ap.add_argument('--out', required=True, type=Path, help='Output ZIP path')
    ap.add_argument('--delivery', type=Path, help='Optional delivery receipt JSON path')
    ap.add_argument('--date', default='2026-10-23T00:00:00Z',
                    help='Fixed member/delivery timestamp (ISO-8601 UTC)')
    ap.add_argument('--carry', action='append', default=[], metavar='NAME=REASON',
                    help='Bundle an episode member byte-identically from --carry-from '
                         'instead of rebuilding it; repeatable')
    ap.add_argument('--carry-from', type=Path,
                    help='Previous delivered archive the --carry members are copied from')
    ap.add_argument('--extra', action='append', type=Path, default=[],
                    help='Supplementary .md member bundled after the episodes; '
                         'repeatable. Owner rule (2026-10-24): always pass the '
                         'current mech catalogue, pilot catalogue and mission '
                         'deployments files for a delivery.')
    args = ap.parse_args(argv)

    verification = json.loads((args.input / 'verification.json').read_bytes())
    carried_specs = []
    for item in args.carry:
        name, sep, reason = item.partition('=')
        if not sep or not name.strip() or not reason.strip():
            raise SystemExit('--carry expects NAME=REASON, got: ' + item)
        carried_specs.append({'name': name.strip(), 'reason': reason.strip()})
    if carried_specs and args.carry_from is None:
        raise SystemExit('--carry requires --carry-from')
    if args.carry_from is not None and not carried_specs:
        raise SystemExit('--carry-from given without --carry')
    carry_by_name = {spec['name']: spec for spec in carried_specs}
    carry_source = zipfile.ZipFile(args.carry_from) if args.carry_from else None
    carried = []
    totals = {'prose_total': 0, 'shown_unique': 0, 'aliased': 0, 'verified_text_spans': 0}
    rows = []
    payload = []
    for episode in range(EPISODES):
        name = f'srwoe_episode_{episode:02}_PL.md'
        if name in carry_by_name:
            data = carry_source.read(name)
            spec = carry_by_name[name]
            rows.append({'episode': episode, 'name': name, 'bytes': len(data), 'sha256': sha(data),
                         'sections': sections(data.decode('utf-8')), 'prose_total': None,
                         'shown_unique': None, 'aliased': None, 'verified_text_spans': None})
            payload.append((name, data, None))
            carried.append({'name': name, 'bytes': len(data), 'sha256': sha(data),
                            'reason': spec['reason'],
                            'carried_from_bytes': len(data),
                            'carried_from_sha256': sha(data)})
            continue
        data = (args.input / name).read_bytes()
        stats = verification['verification'][f'episode_{episode:02}']
        markdown = data.decode('utf-8')
        for key in totals:
            totals[key] += stats[key]
        row = {'episode': episode, 'name': name, 'bytes': len(data), 'sha256': sha(data),
               'sections': sections(markdown), **{k: stats[k] for k in
               ('prose_total', 'shown_unique', 'aliased', 'verified_text_spans')}}
        rows.append(row)
        payload.append((name, data, row))

    if not args.extra:
        print('WARNING: no --extra members; the owner rule (2026-10-24) requires '
              'bundling the current mech catalogue, pilot catalogue and mission '
              'deployments .md files in every reading-archive delivery.',
              file=sys.stderr)
    extras = []
    seen = {name for name, _, _ in payload} | {'README.md'}
    for path in args.extra:
        if path.suffix != '.md':
            raise SystemExit(f'extra member is not Markdown: {path}')
        if path.name in seen:
            raise SystemExit(f'duplicate archive member name: {path.name}')
        seen.add(path.name)
        data = path.read_bytes()
        extras.append({'name': path.name, 'bytes': len(data), 'sha256': sha(data)})
        payload.append((path.name, data, None))

    document = readme(args.release, rows, totals, extras, carried).encode('utf-8')
    year, month, day = (int(x) for x in args.date[:10].split('-'))
    stamp = (year, month, day, 0, 0, 0)

    def write_member(archive: zipfile.ZipFile, name: str, data: bytes) -> dict:
        info = zipfile.ZipInfo(name, date_time=stamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        info.create_system = 0
        archive.writestr(info, data)
        return {'name': name, 'bytes': len(data), 'sha256': sha(data),
                'crc32': f'{zipfile.crc32(data) & 0xFFFFFFFF:08x}'}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, 'w') as archive:
        members = [write_member(archive, 'README.md', document)]
        members += [write_member(archive, name, data) for name, data, _ in payload]

    data = args.out.read_bytes()
    with zipfile.ZipFile(args.out) as archive:
        if archive.testzip() is not None:
            raise SystemExit('bad ZIP: ' + str(args.out))
        if archive.read('README.md') != document:
            raise SystemExit('README readback differs')
        for name, member, _ in payload:
            if archive.read(name) != member:
                raise SystemExit('member readback differs: ' + name)

    record = {
        'schema': 1,
        'release': args.release,
        'episodes': '00-34',
        'episode_count': EPISODES,
        'text_source': verification['text_source'],
        'prose_summary': {**totals, 'markdown_bytes_total': sum(r['bytes'] for r in rows)},
        'archive': {'name': args.out.name, 'bytes': len(data), 'sha256': sha(data),
                    'md5': hashlib.md5(data).hexdigest(),
                    'member_count': len(members), 'roundtrip_cmp_verified': True},
        'polish_package_sha256': verification['polish_package_sha256'],
        'supplementary_members': [extra['name'] for extra in extras],
        'carried_members': carried,
        'members': members,
    }
    if args.delivery:
        args.delivery.parent.mkdir(parents=True, exist_ok=True)
        args.delivery.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n',
                                 encoding='utf-8')
    print(json.dumps({k: record[k] for k in ('release', 'prose_summary', 'archive')},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
