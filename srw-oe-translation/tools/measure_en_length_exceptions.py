#!/usr/bin/env python3
"""Zestaw wyjątków długościowych EN względem PL-final i pojemności JP.

Reguła 1 z `docs/EN_PL_PARITY_LEDGER.md`: poprawka EN ma się mieścić w
szerokości, jaką finalnie osiągnęła PL w tym samym slocie; jeśli sensownego
angielskiego nie da się zmieścić, wolno użyć najkrótszej wersji **nie dłuższej
niż pojemność JP** — a każde odstępstwo musi być jawnie wypisane.

To narzędzie liczy te odstępstwa z danych, żeby nie były deklaracją:
bierze każdy wiersz dotknięty planem z `config/en/*.json` i porównuje
szerokość EN z szerokością PL w tym samym slocie (`pakiet_PL/polish.jsonl`)
oraz z szerokością pola japońskiego (`jp`, tokeny sterujące pominięte).

Dwie klasy:

* `over_jp` — EN szersze niż japońskie pole. To realne ryzyko techniczne
  (najdłuższy tekst, jaki gra pokazała w polu); musi mieć uzasadnienie.
* `over_pl_within_jp` — EN szersze niż PL-final, ale w pojemności JP.
  Bez ryzyka: PL była po prostu krótsza (polski bywa zwięźlejszy).

Wyjście jest deterministyczne: JSON z hashami źródeł + Markdown z tabelą.

    python3 tools/measure_en_length_exceptions.py            # zapisz dokument
    python3 tools/measure_en_length_exceptions.py --check     # tylko porównaj
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))
import translation_check as C  # noqa: E402

TOK = C.TOKEN_RE
OUT_JSON = HERE / 'config' / 'en_length_exceptions.json'
OUT_MD = HERE / 'docs' / 'pl' / 'EN_LENGTH_EXCEPTIONS.md'

# Granice pól ZMIERZONE W GRZE (nie „szerokość japońskiego napisu”): jeśli
# klasa ma zmierzony limit, to on rozstrzyga; szerokość `jp` jest wtedy tylko
# dolną granicą i nie wolno na jej podstawie ogłaszać przepełnienia.
MEASURED_FIELD_LIMITS = {
    # PL v4.5: slot paska wyboru misji zmierzony na zrzucie (32 komórki/linia).
    'mission_title': 32,
    'mission_note': 32,
    # PL v4.8/2026-11-06: pełna nazwa Ducha mieści się w 10 komórkach
    # (najdłuższy japoński napis w tym polu: 威圧 / „Intimidate”).
    'spirit': 10,
}

# Nazwa Ducha ma zmierzony slot 10 komórek; opis efektu to inny widget i inna
# reguła (szerokość japońskiego opisu), więc nie wolno przykładać do niego
# limitu nazwy — to była pułapka pierwszego pomiaru.
SPIRIT_NAME_MAX_CELLS = 10

# Kolejność i uzasadnienie klas: starsze wpisy zostają, nowe dopisujemy.
EXCEPTION_CLASSES = {
    'mission_title': (
        'Tytuły misji w pasku wyboru misji. Decyzja właściciela (2026-11-10, '
        'opcja (a)): 32 komórki na linię — slot zmierzony na zrzucie z gry '
        '(PL v4.5), szerszy niż najkrótszy japoński tytuł. JP jest tu krótsze, '
        'bo japońskie tytuły są zwięzłe; limit wyznacza slot, nie JP.'),
    'mission_note': (
        'Kopie tytułu misji w `*_ext.dat` (karta misji) — ten sam slot i ta sama '
        'decyzja co `mission_title`.'),
    'skill_effect': (
        'Efekt umiejętności/cechy broni w wierszu tabeli (`rNNN:effect` i jego '
        'lustra w puli). Tabele są zawijane wg liczby linii EN od 2026-11-09 '
        '(docs/LAMANIE_LINII_TABEL.md); nadwyżka 1-3 komórek wobec napisu jp '
        'siedzi w tokenach %sNN%% i tagu <Nazwa> i nie przekracza żadnego '
        'zmierzonego progu wiersza. Bez zmierzonego limitu widgetu - '
        'runtime_tested: false.'),
    'sysmes': (
        'Krótkie etykiety paska/statusu (sysmes.bin). Część z nich ma własne, '
        'węższe powtórzone pole - te pilnuje label_fit i plan portu; nadwyżka '
        'wobec napisu jp wynosi tu 1-3 komórki i dotyczy wierszy, których slot '
        'nie został zmierzony na zrzucie. Do potwierdzenia w grze, nie do '
        'skracania w ciemno.'),
    'dialogue': (
        'Dialog. Limit linii dialogu pilnuje builder (`export_strings.box_limit`); '
        'EN mieści się w pojemności JP, a jest szersze od PL-final tylko dlatego, '
        'że polski przekład tej linii jest krótszy. To nie odstępstwo od reguły.'),
    'config_dlc_id': (
        'Zapowiedź pobierania (pula stringów, tryb `grow`). 1 komórka ponad JP '
        'przy nazwie „Tactical Simulator”; JP ma 26 komórek, EN 27. Zostawione: '
        'pole jest pulą (realokacja przy zapisie), a pełna nazwa trybu jest '
        'nazwą własną z tabeli (alpha/beta). Odnotowane jawnie, nie ukryte.'),
}


def cells(text: str) -> int:
    """Najszersza linia w komórkach gry; tokeny sterujące nie liczą się."""
    widths = []
    for line in (text or '').split('\n'):
        bare = TOK.sub('', line)
        try:
            widths.append(len(bare.encode('cp932')))
        except UnicodeEncodeError:  # PL diakrytyki: jeden bajt na literę
            widths.append(len(unicodedata.normalize('NFD', bare).encode('ascii', 'ignore')))
    return max(widths, default=0)


def load_packages() -> tuple[dict, dict]:
    en: dict[str, list[dict]] = {}
    for path in sorted(glob.glob(str(HERE / 'pakiet_EN' / '*.jsonl'))):
        for line in Path(path).read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get('id'):
                    en.setdefault(row['id'], []).append(row)
    pl: dict[str, str] = {}
    for line in (HERE / 'pakiet_PL' / 'polish.jsonl').read_text(encoding='utf-8').splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get('pl'):
                pl.setdefault(row['id'], row['pl'])
    return en, pl


def classify(row_id: str) -> str:
    if row_id.startswith('spirit:'):
        return 'spirit'  # rozdzielane dalej przez `refine`: nazwa Ducha vs efekt

    if row_id.startswith('skill:') or ':effect' in row_id:
        return 'skill_effect'
    if row_id.startswith('sysmes:'):
        return 'sysmes'
    if row_id.startswith('exe:'):
        return 'exe'
    if row_id.startswith('item:'):
        return 'item'
    if row_id.startswith('terrain:') or row_id.startswith('map:'):
        return 'terrain'
    return classify_rest(row_id)


def classify_rest(row_id: str) -> str:
    if row_id.startswith('mission_note:'):
        return 'mission_note'
    if row_id.startswith('mission_title:'):
        return 'mission_title'
    if row_id.startswith('dlc_id:'):
        return 'config_dlc_id'
    if row_id.startswith('dlg:'):
        return 'dialogue'
    if row_id.startswith('exe:'):
        return 'exe'
    return 'other'


def measure() -> dict:
    en, pl = load_packages()
    over_limit, over_jp, over_pl = [], [], []
    touched = 0
    for plan in sorted(glob.glob(str(HERE / 'config' / 'en' / '*.json'))):
        data = json.loads(Path(plan).read_text(encoding='utf-8'))
        for change in data.get('changes') or []:
            if change.get('operation') == 'add':
                candidates = [r for r in en.get(change['id'], []) if r.get('en') == change['after']]
            else:
                candidates = [r for r in en.get(change['id'], []) if r.get('en') == change['after']]
            for row in candidates:
                touched += 1
                kind = classify(row['id'])
                if kind == 'spirit' and cells(row['en']) > SPIRIT_NAME_MAX_CELLS:
                    kind = 'spirit_effect'
                width_en, width_jp = cells(row['en']), cells(row['jp'])
                width_pl = cells(pl.get(row['id'])) if row['id'] in pl else None
                record = {
                    'plan': Path(plan).name,
                    'id': row['id'],
                    'kind': kind,
                    'en': row['en'],
                    'cells_en': width_en,
                    'cells_jp': width_jp,
                    'cells_pl': width_pl,
                }
                limit = MEASURED_FIELD_LIMITS.get(kind)
                basis = 'zmierzone pole gry' if limit is not None else 'szerokość napisu jp (dolna granica)'
                applicable = limit if limit is not None else width_jp
                record['limit'] = applicable
                record['limit_basis'] = basis
                if width_en > applicable:
                    (over_limit if limit is not None else over_jp).append(record)
                elif width_pl is not None and width_en > width_pl:
                    over_pl.append(record)
    return {
        'schema': 1,
        'method': ('Szerokość = najszersza linia po usunięciu tokenów sterujących '
                   '(TOKEN_RE z translation_check), japoński w CP932, polski po '
                   'złożeniu diakrytyków do jednego bajtu. Liczone dla wierszy, '
                   'które faktycznie noszą tekst z planu (en == after).'),
        'plans_glob': 'config/en/*.json',
        'touched_rows': touched,
        'over_measured_limit': over_limit,
        'over_jp_string_only': over_jp,
        'over_pl_within_jp': over_pl,
        'counts': {
            'touched_rows': touched,
            'over_measured_limit': len(over_limit),
            'over_jp_string_only': len(over_jp),
            'over_pl_within_jp': len(over_pl),
            'by_kind_over_limit': _count_by_kind(over_limit),
            'by_kind_over_jp': _count_by_kind(over_jp),
            'by_kind_over_pl': _count_by_kind(over_pl),
        },
    }


def _count_by_kind(rows: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row['kind']] = counts.get(row['kind'], 0) + 1
    return dict(sorted(counts.items()))


def render_markdown(data: dict) -> str:
    counts = data['counts']
    lines = [
        '# Wyjątki długościowe EN — zmierzone, nie deklarowane',
        '',
        'Plik generowany przez `tools/measure_en_length_exceptions.py`. Nie edytuj',
        'ręcznie: po zmianie planów w `config/en/` uruchom narzędzie i dołóż',
        'uzasadnienie nowej klasy w `EXCEPTION_CLASSES`.',
        '',
        'Reguła z [`EN_PL_PARITY_LEDGER.md`](../EN_PL_PARITY_LEDGER.md): EN ma się',
        'mieścić w szerokości PL-final; jeśli się nie da — w pojemności JP; każde',
        'odstępstwo musi być wypisane. Ten dokument jest tym wypisem.',
        '',
        '## Podsumowanie',
        '',
        f"- wierszy dotkniętych planami portu: **{counts['touched_rows']}**",
        f"- EN szersze niż **zmierzony limit pola**: **{counts['over_measured_limit']}**"
        f" ({_describe(counts['by_kind_over_limit'])})",''
        '  → twardy błąd, gdy niepuste; pilnuje tego test',
        f"- EN szersze niż **napis japoński**, ale bez zmierzonego limitu pola:"
        f" **{counts['over_jp_string_only']}** ({_describe(counts['by_kind_over_jp'])})",
        f"- EN szersze niż PL-final, ale **w limicie pola**: **{counts['over_pl_within_jp']}**"
        f" ({_describe(counts['by_kind_over_pl'])})",
        '',
        '## EN szersze niż zmierzony limit pola (wymaga decyzji)',
        '',
        'Puste = żaden wiersz portu nie przekracza limitu zmierzonego w grze.',
        '',
    ]
    if data['over_measured_limit']:
        lines += ['| klasa | plan | slot | EN | kom. EN | kom. JP |', '|---|---|---|---|---|---|']
        for row in data['over_measured_limit']:
            note = EXCEPTION_CLASSES.get(row['kind'], '_brak uzasadnienia w narzędziu_')
            lines.append(
                f"| `{row['kind']}` | `{row['plan']}` | `{row['id']}` | "
                f"{_md(row['en'])} | {row['cells_en']} | {row['limit']} |")
            lines.append(f"| | | ↳ {note} | | | |")
    else:
        lines.append('_Brak._')
    lines += ['', '## EN szersze niż napis japoński, bez zmierzonego limitu pola', '',
              'Dla tych klas nie znamy zmierzonej pojemności widgetu — szerokość napisu',
              'japońskiego jest tylko **dolną granicą** (gra mogła pokazywać w polu',
              'tekst dłuższy niż to, co ma japoński odpowiednik). Ryzyko niepotwierdzone:',
              '`runtime_tested` jest `false`. Lista jest kompletna i generowana z danych.',
              '']
    if data['over_jp_string_only']:
        lines += ['| klasa | plan | slot | EN | kom. EN | kom. JP | nadwyżka |',
                  '|---|---|---|---|---|---|---|']
        for row in data['over_jp_string_only']:
            lines.append(
                f"| `{row['kind']}` | `{row['plan']}` | `{row['id']}` | "
                f"{_md(row['en'])} | {row['cells_en']} | {row['cells_jp']} | "
                f"{row['cells_en'] - row['cells_jp']} |")
    else:
        lines.append('_Brak._')
    lines += ['', '## EN szersze niż PL-final, ale w limicie pola (bez ryzyka)', '',
              'Tu limitem jest zmierzony slot, jeśli klasa go ma, a w przeciwnym razie',
              'szerokość napisu japońskiego.', '']
    if data['over_pl_within_jp']:
        lines += ['| klasa | plan | slot | EN | kom. EN | kom. PL | limit |',
                  '|---|---|---|---|---|---|---|']
        for row in data['over_pl_within_jp']:
            lines.append(
                f"| `{row['kind']}` | `{row['plan']}` | `{row['id']}` | "
                f"{_md(row['en'])} | {row['cells_en']} | {row['cells_pl']} | {row['limit']} |")
    else:
        lines.append('_Brak._')
    lines += ['', '## Klasy i uzasadnienia', '']
    for kind, note in sorted(EXCEPTION_CLASSES.items()):
        lines.append(f'- **`{kind}`** — {note}')
    lines.append('')
    return '\n'.join(lines)


def _describe(counts: dict) -> str:
    return ', '.join(f'`{k}` {v}' for k, v in counts.items()) or 'brak'


def _md(text: str) -> str:
    return '`' + text.replace('|', '\\|').replace('\n', '\\n') + '`'


def write(data: dict, check: bool = False) -> int:
    payload = dict(data)
    payload['counts_sha256'] = hashlib.sha256(
        json.dumps(data['counts'], sort_keys=True).encode()).hexdigest()
    json_text = json.dumps(payload, ensure_ascii=False, indent=1) + '\n'
    md_text = render_markdown(data)
    if check:
        same = (OUT_JSON.exists() and OUT_JSON.read_text(encoding='utf-8') == json_text
                and OUT_MD.exists() and OUT_MD.read_text(encoding='utf-8') == md_text)
        print(json.dumps({'check': 'ok' if same else 'stale', 'counts': data['counts']},
                         ensure_ascii=False))
        return 0 if same else 1
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json_text, encoding='utf-8')
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md_text, encoding='utf-8')
    print(json.dumps({'written': [str(OUT_JSON.relative_to(HERE)), str(OUT_MD.relative_to(HERE))],
                      'counts': data['counts']}, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    return write(measure(), check=args.check)


if __name__ == '__main__':
    raise SystemExit(main())
