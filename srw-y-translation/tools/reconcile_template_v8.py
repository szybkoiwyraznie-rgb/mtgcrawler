#!/usr/bin/env python3
"""Reconcile the delivered v8 template with the S6-full snapshot (owner decision 2026-11-10).

Two independent defects, both measured by `tools/diag_template_vs_snapshot.py`:

1. `sceny/odcinek-20.md` still shows a stale block for `cse20_2010_0201710a`. When
   `data/package_appendix_y.json` took `sdemo:49.0` and `sdemo:103.1` into the v8.1
   appendix, the main file was never re-rendered: it kept one block for `sdemo:49.0`
   in an older wording (`ワルキュー…`, no `レ`) *and* the appendix printed the same row
   correctly. The scene therefore had 275 elements for 274 rows, so every element from
   #104 on sat one row off and #275 had no row at all. The rows stay in the appendix —
   nothing the translator filled moves — and the stale block is dropped from the main
   file.

2. Three Japanese lines in `dlc-BonusMission.md` disagree with the game text. The owner
   settled them against the game's own English text, an independent translation of the
   same script:
     * #279 `友情` → `友達` — the surrounding lines call it "moc przyjaźni", so 友達 fits.
     * #284 needs no fix: the template already prints `『Ａアデン』`, matching the game's
       English ("at the A. Ardent"); it is the *snapshot* that still has `別の場所`
       (`Ａアデン` 61 hits, `別の場所でやるから` 1). Left as a documented snapshot lag.
     * #277 `返ってくる` → `帰ってくる` — EN "come back alive"; 4 corpus hits against 0.

`translations/template-v8/` is frozen and signed because PL1 returns are checked against
its `SHA256SUMS`, so this script rewrites the file *and* the sum in the same run, and
refuses to start unless the live file matches the recorded sum.

Usage (in `srw-y-translation/`, dry run first):

    python3 tools/reconcile_template_v8.py --check
    python3 tools/reconcile_template_v8.py --write
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import bind_v8_return as binder
import build_translator_package as renderer
from pl_import import ImportFailure, canonical

HERE = Path(__file__).resolve().parents[1]
TEMPLATE = HERE / 'translations' / 'template-v8'
SOURCE = HERE / 'data' / 's6-full'

STALE_SCENE = 'cse20_2010_0201710a'
STALE_FILE = 'sceny/odcinek-20.md'

# (file, anchor, replacement) — every anchor must occur exactly once
JP_FIXES = [
    ('sceny/dlc-BonusMission.md',
     '279. [Dialog - ノーヴィー (wariant: bohaterka)] 「友情…」',
     '279. [Dialog - ノーヴィー (wariant: bohaterka)] 「友達…」',
     'gra: EN "Friendship..." przy kwestii o "mocy przyjaźni"; 友達 = 94 wystąpienia'),
    ('sceny/dlc-BonusMission.md',
     '277. [Dialog - レンレン] 「その代わり、絶対に生きて返ってくるのよ！」',
     '277. [Dialog - レンレン] 「その代わり、絶対に生きて帰ってくるのよ！」',
     'gra: EN "come back alive"; 帰 = 4 wystąpienia, 返 = 0'),
]


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_sums(root: Path) -> dict[str, str]:
    sums = {}
    for line in (root / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
        sha, name = line.split('  ', 1)
        sums[name] = sha
    return sums


def write_sums(root: Path, sums: dict[str, str]) -> None:
    body = '\n'.join(f'{sha}  {name}' for name, sha in sorted(sums.items()))
    (root / 'SHA256SUMS').write_text(body + '\n', encoding='utf-8')


def section_of(text: str, scene_key: str) -> tuple[int, int]:
    """Character span of one scene section, from the end of its heading to the next one."""
    headings = list(binder.HEADING.finditer(text))
    for index, heading in enumerate(headings):
        if heading[1] == scene_key:
            stop = (headings[index + 1].start() if index + 1 < len(headings) else len(text))
            return heading.end(), stop
    raise ImportFailure(f'{scene_key}: brak sceny w pliku')


def renumber(section: str) -> str:
    """Close the gap after a removed block: element numbers are positions, not ids."""
    spans = [m.start() for m in binder.ELEMENT.finditer(section)]
    out, cursor, index = [], 0, 0
    for start in spans:
        out.append(section[cursor:start])
        out.append(f'{index + 1}.')
        dot = section.index('.', start)
        cursor = dot + 1
        index += 1
    out.append(section[cursor:])
    return ''.join(out)


def blocks_of(section: str) -> list[str]:
    spans = [m.start() for m in binder.ELEMENT.finditer(section)] + [len(section)]
    return [section[a:b] for a, b in zip(spans, spans[1:])]


def scene_verdict(rows: list[dict], blocks: list[str]) -> list[tuple[int, str]]:
    failures = []
    for number, block in enumerate(blocks, 1):
        if number > len(rows):
            failures.append((number, 'brak wiersza'))
            continue
        try:
            binder.validate_rendered(block, rows[number - 1], 'template', number)
        except Exception as error:  # ImportFailure raised by the gate
            failures.append((number, str(error).split(': ', 1)[-1]))
    return failures


def drop_one_block(rows: list[dict], blocks: list[str]) -> tuple[int, list[str]]:
    """Find the single block whose removal makes the scene line up with its rows.

    Exactly one candidate must work: with none, another defect is in play; with more
    than one, the choice would be arbitrary. Either way we stop instead of guessing.
    """
    working = []
    for index in range(len(blocks)):
        candidate = blocks[:index] + blocks[index + 1:]
        if len(candidate) != len(rows):
            continue
        if not scene_verdict(rows, candidate):
            working.append(index)
    if len(working) != 1:
        raise ImportFailure(f'oczekiwano dokładnie jednego bloku do usunięcia, '
                            f'zadziałało {len(working)}: {[i + 1 for i in working]}')
    index = working[0]
    return index, blocks[:index] + blocks[index + 1:]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='policz, nic nie zapisuj')
    parser.add_argument('--write', action='store_true', help='zapisz pliki i sumy')
    args = parser.parse_args(argv)
    if not (args.check or args.write):
        parser.error('podaj --check albo --write')

    sums = read_sums(TEMPLATE)
    changes: dict[Path, bytes] = {}

    # --- 1. the stale block in odcinek-20 --------------------------------------------
    path = TEMPLATE / STALE_FILE
    data = path.read_bytes()
    if _digest(data) != sums[STALE_FILE]:
        raise ImportFailure(f'{STALE_FILE}: plik nie odpowiada sumie z SHA256SUMS')
    text = canonical(data.decode('utf-8'))

    old_scenario = renderer.SCENARIO
    try:
        renderer.SCENARIO = SOURCE / 'scenario.jsonl'
        scenes = {scene['key']: scene for scene in renderer.load_scenes()}
    finally:
        renderer.SCENARIO = old_scenario
    rows = scenes[STALE_SCENE]['rows']

    start, stop = section_of(text, STALE_SCENE)
    section = text[start:stop]
    blocks = blocks_of(section)
    numbers = [int(block.split('.', 1)[0]) for block in blocks]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ImportFailure('numeracja sceny nie jest ciągła — nie ruszam')
    before = scene_verdict(rows, blocks)
    print(f'{STALE_FILE} / {STALE_SCENE}: elementów {len(blocks)}, wierszy {len(rows)}, '
          f'niezgodnych {len(before)}')
    if len(blocks) != len(rows) + 1:
        raise ImportFailure(f'oczekiwano jednego bloku nadmiaru, jest '
                            f'{len(blocks) - len(rows)}')

    index, kept = drop_one_block(rows, blocks)
    assert not scene_verdict(rows, kept)
    print(f'  usuwam element #{index + 1}: {blocks[index].splitlines()[0][:64]}')
    spans = [m.start() for m in binder.ELEMENT.finditer(section)] + [len(section)]
    new_section = renumber(section[:spans[index]] + section[spans[index + 1]:])
    new_text = text[:start] + new_section + text[stop:]

    # verify on the rebuilt file, not on the in-memory list
    check_start, check_stop = section_of(new_text, STALE_SCENE)
    final_blocks = blocks_of(new_text[check_start:check_stop])
    final_numbers = [int(block.split('.', 1)[0]) for block in final_blocks]
    if final_numbers != list(range(1, len(final_numbers) + 1)):
        raise ImportFailure(f'po usunięciu bloku numeracja nie jest ciągła: {final_numbers[:5]}…')
    final = scene_verdict(rows, final_blocks)
    if final or len(final_blocks) != len(rows):
        raise ImportFailure(f'po usunięciu bloku scena nadal się nie zgadza: {final[:3]}')
    print(f'  po naprawie: elementów {len(final_blocks)}, niezgodnych {len(final)}')
    changes[path] = new_text.encode('utf-8')

    # --- 2. the three Japanese lines ---------------------------------------------------
    bonus_path = TEMPLATE / 'sceny' / 'dlc-BonusMission.md'
    bonus_data = bonus_path.read_bytes()
    if _digest(bonus_data) != sums['sceny/dlc-BonusMission.md']:
        raise ImportFailure('sceny/dlc-BonusMission.md: plik nie odpowiada sumie')
    bonus = canonical(bonus_data.decode('utf-8'))
    for name, anchor, replacement, why in JP_FIXES:
        count = bonus.count(anchor)
        if count != 1:
            raise ImportFailure(f'{name}: kotwica występuje {count} razy, oczekiwano 1: '
                                f'{anchor[:48]}')
        bonus = bonus.replace(anchor, replacement)
        print(f'dlc-BonusMission.md: {anchor.split("] ")[-1][:30]!r} -> '
              f'{replacement.split("] ")[-1][:30]!r}')
        print(f'   uzasadnienie: {why}')
    changes[bonus_path] = bonus.encode('utf-8')

    for changed, payload in changes.items():
        rel = changed.relative_to(TEMPLATE).as_posix()
        sums[rel] = _digest(payload)
        print(f'  nowa suma {rel}: {sums[rel]}')

    if args.write:
        for changed, payload in changes.items():
            changed.write_bytes(payload)
        write_sums(TEMPLATE, sums)
        print('zapisano pliki wzorca i SHA256SUMS')
    else:
        print('kontrola bez zapisu — nic nie zmieniono')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ImportFailure as exc:
        print(f'ODRZUCONO — nic nie zapisano:\n{exc}')
        raise SystemExit(1)
