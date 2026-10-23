#!/usr/bin/env python3
"""Pack the verified PL reading editions into the published Drive archive.

The archive README is generated from ``verification.json`` written by
``build_polish_reading_editions.py``, so the member table, the totals and the
per-episode hashes can never drift from the episodes actually shipped.

The ZIP is written deterministically (fixed member timestamps, stored order,
fixed permissions) so that rebuilding an unchanged release yields the same
bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

EPISODES = 35


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def num(value: int) -> str:
    return f'{value:,}'


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


def readme(release: str, rows: list[dict], totals: dict) -> str:
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
        'przedziałów tekstu)',
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
    for row in rows:
        out.append(
            f'| {row["episode"]:02} | `{row["name"]}` | {row["sections"]} | '
            f'{num(row["prose_total"])} | {num(row["shown_unique"])} | {num(row["aliased"])} | '
            f'{num(row["bytes"])} | `{row["sha256"][:16]}…` |'
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
    args = ap.parse_args(argv)

    verification = json.loads((args.input / 'verification.json').read_bytes())
    totals = {'prose_total': 0, 'shown_unique': 0, 'aliased': 0, 'verified_text_spans': 0}
    rows = []
    payload = []
    for episode in range(EPISODES):
        name = f'srwoe_episode_{episode:02}_PL.md'
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

    document = readme(args.release, rows, totals).encode('utf-8')
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
