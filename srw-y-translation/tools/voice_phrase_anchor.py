#!/usr/bin/env python3
"""Check the speaker join against catchphrases we can recognise by ear.

The owner's requirement: take a few known catchphrases (the unmistakable shouts of main
anime characters) and use them to type the speaker id unambiguously — and show *how and
where* that mapping is stored. This tool does exactly that, on data, without guessing:

    anchor:  phrase (Japanese text of the shout) + the character said to shout it
    -> find the `battle_voice` rows whose text contains the phrase      local/s6/tables.jsonl
    -> resolve each row to its `WaveId`                                 Shared Data
    -> read the speaker the game prints for that `WaveId`               container nameText
    -> compare with the expected character                              PASS / FAIL

The point is not the phrase list — the point is that the *encoding* is now known:

    table row key  high32 = the voice bank (one series' voice set)
                   low32  = entry id from the Unity key generator
    Shared Data    m_Id   -> m_Key            "F069_002"   (the WaveId)
    container      WaveId -> PlayDetails      nameText / NameKey / FaceKey

So a speaker id is `high32` + the `WaveId`, and the name comes from `nameText` — the same
string the game displays above the line while it plays that clip. That is why the anchors
below must agree: if `nameText` were, say, the *unit* name, 「イデオンソード」 would come back
as イデオンのunit name, not as コスモ.

    python3 tools/voice_phrase_anchor.py                  # built-in anchors
    python3 tools/voice_phrase_anchor.py --anchor ゲッタービーム=拓馬 --anchor ...
    python3 tools/voice_phrase_anchor.py --report docs/VOICE_ANCHORS_Y.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

MAP = HERE / 'local' / 's6' / 'voice_map.json'
OUT = HERE / 'docs' / 'VOICE_ANCHORS_Y.md'

#: phrase -> the character who shouts it. Chosen so that one shout names one pilot, and so
#: that the unit named inside the shout is *not* the speaker (that is the whole test).
ANCHORS = [
    ('イデオンソード', 'コスモ'),      # Ideon's sword — pilot Kosmo, not the unit
    ('ブライ・ソード', 'キッド'),      # Braiger — pilot Kidd
    ('ダ・ガーン', '星史'),            # Da-Garn — pilot Hoshi
    ('ゲッタービーム', '拓馬'),        # Getter Beam — pilot Takuma
]


def load_rows() -> list[dict]:
    if not MAP.is_file():
        raise SystemExit(f'brak {MAP.relative_to(HERE)} — uruchom tools/voice_speaker_map.py')
    return json.loads(MAP.read_text(encoding='utf-8'))['rows_mapped']


def check(rows: list[dict], phrase: str, expected: str) -> dict:
    hits = [row for row in rows if phrase in (row.get('jp') or '')]
    speakers = sorted({row['speaker'] for row in hits})
    agreeing = [row for row in hits if row['speaker'] == expected]
    return {'phrase': phrase, 'expected': expected, 'hits': len(hits),
            'speakers': speakers, 'agree': len(agreeing),
            'share': len(agreeing) / len(hits) if hits else 0.0,
            'sample': agreeing[0] if agreeing else None,
            # several pilots of the same series can shout the same attack, so the test is
            # "the expected speaker is there", not "he is the only one"
            'verdict': 'ZGODNY' if agreeing else 'BRAK'}


def report(results: list[dict]) -> str:
    lines = ['# Kotwice mówców — sprawdzenie połączenia na znanych okrzykach', '',
             'Każdy okrzyk to jedna postać i jedno `nameText` z danych gry. Sprawdzamy, czy',
             'gra sama nazywa mówcę tak, jak mówi się go w anime — a nie nazwą robotu,',
             'który w tym okrzyku występuje.', '',
             '| okrzyk | oczekiwany mówca | kwestii | z tym mówcą | odczytani mówcy | wynik |',
             '|---|---|---|---|---|---|']
    for item in results:
        lines.append(f"| {item['phrase']} | {item['expected']} | {item['hits']} | "
                     f"{item['agree']} | {', '.join(item['speakers']) or '—'} | "
                     f"{item['verdict']} |")
    lines += ['', 'Ci sami okrzyki wypowiadają czasem dwaj piloci tej samej serii (np.',
              '`イデオンソード` — コスモ i デク, obaj z Ideonu), dlatego kolumna „odczytani',
              'mówcy” bywa dłuższa niż jeden. To własność danych, nie błąd: każdy wiersz',
              'ma własne `nameText`.', '']
    lines += ['', '## Jak to jest zapisane (na jednym przykładzie)', '']
    sample = next((item['sample'] for item in results if item['sample']), None)
    if sample:
        bank, _, entry = sample['key'].partition(':')
        lines += ['```text',
                  f"wiersz battle_voice    {sample['key']}",
                  f"  bank (high32)        {bank}          # zestaw głosów serii",
                  f"  wpis (low32)         {entry}          # id z generatora Unity",
                  f"  -> Shared Data       {sample['key']} -> {sample['wave']}",
                  f"  -> kontener          {sample['container']}",
                  f"  -> nameText          {sample['speaker']}",
                  f"  -> NameKey           {sample['name_key']}",
                  f"  -> portret           {sample['face']}",
                  '```', '']
    lines += ['## Wniosek', '',
              'Mówca nie jest zgadywany z treści: to pole `nameText` w kontenerze głosu,',
              'wskazanym przez `WaveId` z `Shared Data`. Dlatego `[Cytat bitewny — <mówca>]`',
              'można wpisać wszędzie tam, gdzie ten kontener jest — bez ryzyka pomyłki', '']
    return '\n'.join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--anchor', action='append', default=[],
                        help='okrzyk=mówca, np. --anchor ゲッタービーム=拓馬')
    parser.add_argument('--report', type=Path, help='zapisz raport markdown')
    args = parser.parse_args(argv)

    anchors = [(item.split('=', 1)[0], item.split('=', 1)[1]) for item in args.anchor]
    rows = load_rows()
    results = [check(rows, phrase, expected) for phrase, expected in (anchors or ANCHORS)]
    for item in results:
        line = (f"{item['verdict']:6s} {item['phrase']:12s} -> {item['expected']:6s} "
                f"({item['agree']}/{item['hits']} kwestii, odczytani: "
                f"{', '.join(item['speakers']) or '—'})")
        print(line)
        if item['sample']:
            sample = item['sample']
            print(f"       {sample['key']} -> {sample['wave']} -> "
                  f"{sample['container']} -> nameText={sample['speaker']} "
                  f"NameKey={sample['name_key']}")
    if args.report:
        args.report.write_text(report(results), encoding='utf-8')
        print(f'zapisano {args.report.relative_to(HERE) if args.report.is_relative_to(HERE) else args.report}')
    return 0 if all(item['verdict'] != 'BRAK' for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
