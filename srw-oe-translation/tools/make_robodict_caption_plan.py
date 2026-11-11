#!/usr/bin/env python3
"""Zbuduj plan PL dla podpisów encyklopedii robotów, których gra pokazuje po japońsku.

Powód powstania (2026-11-11): właściciel po raz trzeci przysłał zrzut ekranu
z japońskim podpisem w „Przeglądzie robotów”. Za każdym razem naprawiano dokładnie
to, co było na zrzucie, bo `pl_ui_corrections` wpuszczało tylko rodziny „typ”
i „pilot”. Tu idziemy odwrotnie: narzędzie **samo wylicza** wszystkie wiersze
`config_leftover` z plików `srw_DL_RoboDictionary*.bin`, które mają tekst japoński
i nie mają polskiego, i wymaga tłumaczenia dla każdego z nich. Jeśli choć jeden
zostanie bez wpisu w `CAPTIONS`, narzędzie odmawia zbudowania planu — więc nie da
się już zrobić „połowy roboty”.

Polskie brzmienia są zbudowane z terminów, które w `pakiet_PL/polish.jsonl` już są
(`Podłożenie`, `Kosmos`, `Organoid`, `Zaku II Kai`, `D-Sserd`, `King Squasher`,
`(okręt)`, `(okręt-matka)`), a nie wymyślone od nowa. Każdy wiersz przechodzi
`translation_check.check_row`, czyli m.in. twardy budżet bajtów pola.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pl_release_package as R
import pl_text
import translation_check as C
from pl_ui_corrections import caption_family

JP_CHARS = re.compile(r'[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]')
MEMBER = re.compile(r'srw_DL_RoboDictionary\d{2}\.bin')

#: Rozmiar: pole ma tylko 13 bajtów, więc skrót „Rozm.” jak w panelu danych
#: jednostki, gdzie przyjęto już `Masa 54,0 t` / `Dł. 25,0 m`.
SIZE = {'小型': 'mały', '中型': 'średni', '大型': 'duży'}
#: Nazwy zrostów w brzmieniu, które jest już w tłumaczeniu; `Imp.` jak w EN `Mech Emp.`
FUSION = {
    'ＤＧ細胞': 'komórki DG',
    'インベーダー': 'Invader',
    '邪神ドラゴ': 'Evil God Drago',
    '機械化帝国': 'Imp. Mechanizacji',
}

CAPTIONS: dict[str, str] = {
    '（母艦ユニット）': '(okręt-matka)',
    '（艦船ユニット）': '(okręt)',
    '「ハイパーモード」形態': 'forma Hyper Mode',
    '「ハイパー化」形態': 'forma Hyper',
    '「オーガノイド」形態': 'forma Organoid',
    '「ワイルドウィーゼルユニット」装備': 'z zestawem Wild Weasel',
    '「スーパーパック」装備': 'z zestawem Super Pack',
    '「アーマードパック」装備': 'z zestawem Armored Pack',
    '（「宇」属性の地形があるＭＡＰのみ出撃可能）': '(tylko mapy z terenem Kosmos)',
    '（ザクⅡ改（バーニィ）の「設置」コマンドで出現）': '(pojawia się po Podłożeniu: Zaku II Kai)',
    'ザクⅡ改（バーニィ）の「＠6設置＠0」コマンドで出現': 'Pojawia się po ＠6Podłożeniu＠0: Zaku II Kai',
    '（ディザード（アム）の「設置」コマンドで出現）': '(pojawia się po Podłożeniu: D-Sserd)',
    'ディザード（アム）の「＠6設置＠0」コマンドで出現': 'Pojawia się po ＠6Podłożeniu＠0: D-Sserd',
    'キングスカッシャー（ラムネス）の「召喚」武器で登場': 'Przywołanie bronią King Squashera',
}
for _jp, _pl in SIZE.items():
    CAPTIONS[f'サイズ：{_jp}'] = f'Rozm.: {_pl}'
    for _fjp, _fpl in FUSION.items():
        CAPTIONS[f'サイズ：{_jp}\u3000「{_fjp}」と融合'] = f'Rozm.: {_pl} + {_fpl}'


def missing_rows(base: Path, stored: Path) -> list[dict]:
    """Wiersze encyklopedii z japońskim tekstem, które nie mają polskiego."""
    rows, _ = R.I.load_rows(base)
    done = set()
    for line in (stored / R.DATA).read_text(encoding='utf-8').splitlines():
        if not line:
            continue
        entry = json.loads(line)
        if entry.get('pl'):
            done.add((entry['file'], entry['source_sha256']))
    out = []
    for row in rows:
        source = row.get('source') or {}
        if not MEMBER.fullmatch(str(source.get('member', ''))):
            continue
        if row.get('category') != 'config_leftover':
            continue
        if not JP_CHARS.search(row.get('jp') or ''):
            continue
        if (row.get('_file'), R.binding(row)) in done:
            continue
        out.append(row)
    return out


def build(base: Path, stored: Path) -> dict:
    rows = missing_rows(base, stored)
    unknown = sorted({r['jp'] for r in rows if r['jp'] not in CAPTIONS})
    if unknown:
        raise SystemExit('brak polskiego brzmienia dla podpisów:\n  ' + '\n  '.join(unknown))
    changes, problems = [], []
    for row in sorted(rows, key=lambda r: (r['_file'], r['id'])):
        text = CAPTIONS[row['jp']]
        family = caption_family(row['jp'], row.get('en') or '')
        if family is None:
            problems.append(f"{row['id']}: podpis poza przejrzanymi rodzinami")
            continue
        errors, _ = C.check_row({**row, 'pl': text}, field='pl')
        if errors:
            problems.append(f"{row['id']} ({len(pl_text.encode(text))} B, "
                            f"budżet {row.get('max_bytes')}): " + '; '.join(errors))
            continue
        source = row['source']
        changes.append({
            'operation': 'add',
            'file': row['_file'],
            'id': row['id'],
            'source_sha256': R.binding(row),
            'source_jp': row['jp'],
            'source_en': row.get('en'),
            'container': source.get('container'),
            'member': source.get('member'),
            'offset': source.get('offset'),
            'max_bytes': row.get('max_bytes'),
            'family': family,
            'after': text,
        })
    if problems:
        raise SystemExit('wiersze odrzucone:\n  ' + '\n  '.join(problems))
    return {'schema': 1, 'changes': changes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=HERE.parent / 'pakiet_EN')
    parser.add_argument('--stored', type=Path, default=HERE.parent / 'pakiet_PL')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    plan = build(args.base, args.stored)
    args.out.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f"{len(plan['changes'])} podpisów -> {args.out}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
