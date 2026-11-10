#!/usr/bin/env python3
"""Złóż 35 polskich epizodów OE w jeden plik do czytania, w układzie SRW Y.

Właściciel (2026-11-11) poprosił o trzy rzeczy naraz:

1. **jeden plik zamiast 35** — wzorem `srwy_scenariusz_PL.md` z projektu Y:
   krótka strona tytułowa, a pod nią kolejne epizody jako sekcje `# `,
   rozdzielone poziomą linią;
2. **dialogi bez pustych linii** — w wydaniach OE każda kwestia była oddzielona
   pustą linią, przez co czytanie rwało się co wers. Puste linie zostają tylko
   między blokami: nagłówkami, akapitami narracji, tabelami i listami;
3. **bez linii `>`** — stała zasada czytanek: żadnego cytatu blokowego.

Plik źródłowy nie jest modyfikowany; narzędzie czyta katalog wydań i pisze nowy
plik. Łączenie jest deterministyczne — dwa przebiegi dają ten sam bajt.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

EPISODES = 35
TITLE = 'Super Robot Wars OE — scenariusz do czytania'

#: Wiersz jest „kwestią dialogu”, gdy zaczyna się od pogrubionego imienia
#: zakończonego dwukropkiem: `**Ktoś:** tekst`. Tylko takie wersy skleja się
#: w blok — narracja, tabele i nagłówki zachowują swoje odstępy.
#:
#: Nawias i backtick są wykluczone, bo żadne z 324 imion w wydaniach ich nie ma,
#: a mają je etykiety danych w stylu ``**Premia Asa (`≥ 300`):**``, których nie
#: wolno sklejać jak dialogu.
SPEAKER = re.compile(r'^\*\*[^*`()]{1,40}:\*\* ')


def is_dialogue(line: str) -> bool:
    return bool(SPEAKER.match(line))


def tighten(text: str) -> str:
    """Usuń pustą linię pomiędzy sąsiadującymi kwestiami dialogu."""
    lines = text.split('\n')
    out: list[str] = []
    for i, line in enumerate(lines):
        if line == '' and out and is_dialogue(out[-1]):
            nxt = next((l for l in lines[i + 1:] if l != ''), None)
            if nxt is not None and is_dialogue(nxt):
                # pusta linia rozdziela dwie kwestie — pomiń ją
                if all(l == '' for l in lines[i + 1:lines.index(nxt, i + 1)]):
                    continue
        out.append(line)
    return '\n'.join(out)


def strip_blockquotes(text: str) -> str:
    """Zamień linie `> …` na zwykły akapit (zasada czytanek: bez `> `)."""
    return '\n'.join(re.sub(r'^>\s?', '', line) for line in text.split('\n'))


def episode_body(text: str) -> str:
    body = strip_blockquotes(text)
    body = tighten(body)
    return re.sub(r'\n{3,}', '\n\n', body).strip()


def front_matter(count: int, deployments: str | None) -> str:
    extra = (f'Zestawienie jednostek i profili jest w osobnym pliku `{deployments}`.'
             if deployments else '')
    return '\n'.join(x for x in [
        f'# {TITLE}',
        '',
        f'*Wszystkie epizody ({count}) w jednym pliku · tekst PL*',
        '',
        'Kwestie dialogu idą wers po wersie; pusta linia oddziela tylko bloki — '
        'nagłówki scen, akapity narracji i tabele.',
        '',
        'Dialogi warunkowe i sytuacyjne pogrupowano dla wygody lektury, a nie jako '
        'gwarantowaną kolejność wydarzeń w grze. Nie dopisujemy progów HP, tur ani '
        'innych wyzwalaczy, których nie potwierdza eksport tekstu.',
        '',
        extra,
    ] if x != '' or True).rstrip() + '\n'


def merge(editions: Path, deployments: str | None = None) -> str:
    parts = [front_matter(EPISODES, deployments)]
    for episode in range(EPISODES):
        path = editions / f'srwoe_episode_{episode:02}_PL.md'
        if not path.exists():
            raise SystemExit(f'brak wydania: {path}')
        parts.append(episode_body(path.read_text(encoding='utf-8')))
    return '\n---\n\n'.join(parts).rstrip() + '\n'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--editions', required=True, type=Path,
                    help='Katalog z srwoe_episode_NN_PL.md')
    ap.add_argument('--deployments', default='srwoe_mission_deployments.md',
                    help='Nazwa pliku z rozmieszczeniami, wspominana na stronie tytułowej')
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args(argv)
    text = merge(args.editions, args.deployments)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding='utf-8')
    data = text.encode('utf-8')
    print(f'{args.out}: {len(data)} B, {text.count(chr(10)) + 1} linii, '
          f'sha256 {hashlib.sha256(data).hexdigest()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
