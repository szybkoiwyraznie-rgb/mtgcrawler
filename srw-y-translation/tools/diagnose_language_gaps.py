#!/usr/bin/env python3
"""Diagnoza rozjazdu korpus <-> gra: czyja to wina i co dokładnie poprawić.

Gdy patcher trafi na linię, w której tekst w pliku gry różni się od korpusu,
pytanie brzmi zawsze tak samo: **kto się myli — korpus czy plik gry?** Ten
narzędzie odpowiada na to danymi, bez zgadywania, i wypisuje gotową poprawkę.

Dane wejściowe (wszystko z repo, nic od właściciela):

* `przyklady/` w folderze patchera — patcher kopiuje tam oryginał bundla, w którym
  wykrył różnicę (bez zmiany w grze),
* `data/game_text_bundle_index.json` — który bundle i obiekt,
* `data/s6-full/` + `data/s6-extra/jp_overrides_y.json` — korpus.

Dla każdej różnicy narzędzie czyta tekst z pliku gry (`UnityPy`) i porównuje:

| korpus | gra | wniosek |
| --- | --- | --- |
| `A` | `A` | fałszywy alarm — sprawdź indeks obiektu |
| inny | inny | **korpus się myli** → wpis do `jp_overrides_y.json` |
| brak | jest | korpus niepełny → wpis do `jp_overrides_y.json` |

Wynik to plik `overrides.json` gotowy do dołączenia do
`data/s6-extra/jp_overrides_y.json` (albo `--write`, żeby dopisać od razu).
Dopiero po tym korpus i gra się zgadzają, więc patch wchodzi w tę linię.

    python3 tools/diagnose_language_gaps.py --samples /sciezka/narzedzia/../przyklady
    python3 tools/diagnose_language_gaps.py --samples … --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

import pl_import  # noqa: E402
from srw_y_bundle_crypt import decrypt  # noqa: E402


def units_of(script: str) -> dict:
    from collections import Counter

    from s6_scenario import parse_units, unit_key
    seen = Counter()
    return {unit_key(unit, seen): unit['text'] for unit in parse_units(script)}


def rows_of_corpus() -> dict:
    import s6_extra
    return {row['id']: row for row in s6_extra.load(HERE / 'data' / 's6-full' / 'scenario.jsonl')}


def scripts_in(bundle: Path) -> dict:
    """Teksty wszystkich obiektów TextAsset w bundlu gry, po nazwie obiektu.

    Patcher kopiuje bundel pod nazwą z prefiksem `oa_` (gdy leżał w `aa/`), bo
    `decrypt` rozpoznaje format po nazwie pliku — prefiks trzeba zdjąć.
    """
    name = bundle.name[3:] if bundle.name.startswith('oa_') else bundle.name
    env = UnityPy.load(decrypt(name, bundle.read_bytes()))
    found = {}
    for obj in env.objects:
        if obj.type.name != 'TextAsset':
            continue
        data = obj.read()
        found[str(data.m_Name)] = data.m_Script
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--samples', type=Path, required=True,
                        help='katalog z oryginałami bundli (patcher zapisuje go jako przyklady/)')
    parser.add_argument('--index', type=Path, default=HERE / 'data' / 'game_text_bundle_index.json')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write', action='store_true',
                        help='dopisz poprawki do data/s6-extra/jp_overrides_y.json')
    args = parser.parse_args(argv)
    corpus = rows_of_corpus()
    index = json.loads(args.index.read_text(encoding='utf-8'))
    # Bez `--gaps` sprawdzamy **wszystkie** jednostki w podanych bundlach — tak
    # działa diagnoza po awarii instalacji: patcher zostawił kopię w `przyklady/`,
    # a my chcemy zobaczyć każdą linię, nie tylko tę, na której stanął.
    wanted = set()
    overrides, checked, matches = {}, 0, 0
    for bundle in sorted(args.samples.glob('*.bundle')):
        for name, script in scripts_in(bundle).items():
            for key, text in units_of(script).items():
                if wanted and (name, key) not in wanted:
                    continue
                row_id = f'scenario:{name}:{key}'
                row = corpus.get(row_id)
                if row is None:
                    overrides[row_id] = {'jp': text}
                    checked += 1
                    continue
                checked += 1
                if (row.get('jp') or '') == text:
                    matches += 1
                    continue
                overrides[row_id] = {'jp': text, 'speaker_jp': row.get('speaker_jp'),
                                     'jp_bytes': len(text.encode('utf-8'))}
    report = {'schema': 1, 'checked': checked, 'already_agree': matches,
              'corrections': len(overrides)}
    print(json.dumps(report, ensure_ascii=False, indent=1))
    for row_id, value in list(overrides.items())[:20]:
        print(f"  {row_id}\n    korpus: {corpus.get(row_id, {}).get('jp')!r}\n    gra:    {value['jp']!r}")
    if args.output:
        args.output.write_text(json.dumps({'schema': 1, 'rows': overrides}, ensure_ascii=False,
                                          indent=1) + '\n', encoding='utf-8')
    if args.write and overrides:
        path = HERE / 'data' / 's6-extra' / 'jp_overrides_y.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        data['rows'].update(overrides)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f'dopisano {len(overrides)} poprawek do {path.relative_to(HERE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
