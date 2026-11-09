#!/usr/bin/env python3
"""Opis wydania patchera SRW Y — generowany z tego, co jest w repozytorium.

Liczby biorą się z `RELEASE_INFO.json` i `PL_COVERAGE.json` (składa je
`tools/build_y_release_meta.py`), a „Zmiany w tej wersji” z komunikatu commita,
z którego wydanie powstaje — w CI to merge do `main`. Dzięki temu opis nigdy nie
opowiada o stanie innym niż plik w załączniku.

    python3 tools/build_y_release_notes.py \\
        --info build/release_y_pl5/RELEASE_INFO.json \\
        --coverage build/release_y_pl5/PL_COVERAGE.json \\
        --tag patch-y-376-db166e36 --repo szybkoiwyraznie-rgb/mtgcrawler \\
        --out build/release_y_pl5/OPIS_WYDANIA.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

HEADER = """Częściowy polski patch do **SUPER ROBOT WARS Y** — jeden instalator, który buduje
pliki u Ciebie z Twoich oryginałów. **To nie jest pełne tłumaczenie**: tabele są
prawie całe, scenariusz jest w części.
"""

TABLE = """
## Co jest w środku

| | |
|---|---|
| tabele (widoki) | **{table_rows} z {table_total}** wierszy z japońskim tekstem — **{table_pct}%** |
| scenariusz | **{scene_lines} z {scene_total}** linii (**{scene_pct}%**), **{scene_files} z {scene_count}** scen |
| plan patchera | {records} rekordów ({slots_filled} wypełnione pola zwrotki + powtórzenia) |
| bundli przebudowywanych | {bundles} |
"""

CHANGES = """
## Zmiany w tej wersji

{changes}
"""

INSTALL = """
## Instalacja

1. Zamknij grę. Rozpakuj całą paczkę do nowego folderu, np. na Pulpicie.
2. Uruchom `PATCH_PL.bat`. Potrzebny jest **Python 3.10+** i — przy pierwszym
   uruchomieniu — internet do pobrania zależności (`UnityPy==1.25.4`,
   `pycryptodome==4.2.0`, `lz4==4.4.5`). Patcher tworzy własne środowisko w folderze
   paczki i gry nie pobiera.
3. Jeśli gra nie zostanie znaleziona, wskaż folder z `SUPER ROBOT WARS Y.exe`
   (albo przeciągnij ten folder na `PATCH_PL.bat`).
4. Poczekaj na `GOTOWE`, uruchom grę i sprawdź dialogi, opisy postaci, mechy,
   umiejętności i listę misji.

Przy każdym oryginale powstaje kopia `.srwy-original.bak`, stan instalacji ląduje
w `narzedzia/STAN_PATCHA.json`, a raport w `narzedzia/RAPORT_PATCHA.txt`.
**Cofanie:** `COFNIJ.bat` z tego samego folderu patchera — nie usuwaj kopii ani stanu.
"""

LIMITS = """
## Czego tu nie ma i czego nie sprawdzono

- W paczce **nie ma żadnych plików gry** — ani bundli, ani ISO, ani zapisów.
  Wszystko powstaje z Twojej kopii SRW Y z dodatkami, po weryfikacji zgodności.
- Czcionka, Windows/BAT i pełna rozgrywka **nie zostały zweryfikowane** w grze;
  w grze widziano okno dialogowe i listę misji.
- Limity szerokości są szacunkowe (najdłuższy napis zaobserwowany w polu), a nie
  zmierzoną szerokością glifów — część pól może wymagać dopasowania.
- Automatyczne kontrole (sumy, audyt każdego slotu, przebudowa bundli) nie
  zastępują testu w grze. Jeśli coś się nie zgadza, prześlij
  `narzedzia/RAPORT_PATCHA.txt`.
"""

ASSETS = """
## Pliki tego wydania

{lines}
"""

ENGLISH = """
---

**English:** partial Polish patch for SUPER ROBOT WARS Y. One-click installer that
rebuilds the game files locally from your own copy; it contains no game binaries.
Coverage: {table_pct}% of table rows ({table_rows}/{table_total}), {scene_pct}% of
scenario lines ({scene_lines}/{scene_total}) in {scene_files} of {scene_count} scenes —
dialogues outside that set stay Japanese. Requires Python 3.10+; keeps
`.srwy-original.bak` backups and undoes with `COFNIJ.bat`. Automated checks do not
replace in-game QA.
"""


MAX_CHANGE_LINES = 6
MAX_CHANGE_CHARS = 600


def format_message(raw: str, max_lines: int = MAX_CHANGE_LINES,
                   max_chars: int = MAX_CHANGE_CHARS) -> str:
    """Pierwsza linia commita + kilka linii treści, bez szumu i bez przepełnienia.

    Komunikat merge'a z GitHuba potrafi mieć kilkaset linii (`Co-authored-by`,
    listy podpunktów), a opis wydania ma się dać przeczytać. Bierzemy temat,
    kilka najważniejszych linii treści i ucinamy, zanim opis zamieni się w log.
    """
    lines = [' '.join(line.split()) for line in raw.splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        return ''
    subject, body = lines[0], []
    for line in lines[1:]:
        low = line.lower()
        if low.startswith('co-authored-by') or low.startswith('signed-off-by'):
            continue
        if low.startswith('*') or low.startswith('- ') or low.startswith('– '):
            continue  # podpunkty merge'a: to nie jest opis dla gracza
        if not any(ch.isalnum() for ch in line):
            continue  # kreski i separatory z komunikatu merge'a
        body.append(line)
    dropped = len(body) > max_lines
    out = [f'- {subject}'] + [f'  {line}' for line in body[:max_lines]]
    if dropped:
        out.append('  …')  # reszta treści merge'a nie jest opisem dla gracza
    text = '\n'.join(out)
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + '…'
    return text


def git_message() -> str:
    try:
        out = subprocess.run(['git', 'log', '-1', '--pretty=%B'], cwd=HERE, check=True,
                             capture_output=True, text=True).stdout
    except Exception:  # pragma: no cover - outside a checkout
        return ''
    return format_message(out)


def render(info: dict, coverage: dict, tag: str, repo: str, changes: str) -> str:
    numbers = {
        'table_rows': f'{coverage["tables"]["rows_translated"]:,}'.replace(',', ' '),
        'table_total': f'{coverage["tables"]["rows_total"]:,}'.replace(',', ' '),
        'table_pct': f'{coverage["tables"]["percent_rows"]}'.replace('.', ','),
        'scene_lines': f'{coverage["scenes"]["lines_translated"]:,}'.replace(',', ' '),
        'scene_total': f'{coverage["scenes"]["lines_total"]:,}'.replace(',', ' '),
        'scene_pct': f'{coverage["scenes"]["percent_lines"]}'.replace('.', ','),
        'scene_files': coverage['scenes']['translated_files'],
        'scene_count': coverage['scenes']['total'],
        'records': f'{info["plan_records"]:,}'.replace(',', ' '),
        'slots_filled': f'{coverage["slots_filled_in_return"]:,}'.replace(',', ' '),
        'bundles': info.get('bundles', 12),
    }
    asset = next(iter(info['assets']))
    size = f'{info["assets"][asset]["bytes"]:,}'.replace(',', ' ')
    sha = info['assets'][asset]['sha256']
    if tag and repo:
        target = f'https://github.com/{repo}/releases/download/{tag}/{asset}'
        lines = [f'- [`{asset}`]({target}) — instalator, {size} B',
                 '- `SHA256SUMS.txt` — sumy wszystkich załączników',
                 '- `PL_COVERAGE.json` — co dokładnie jest przetłumaczone',
                 '- `RELEASE_INFO.json` — wersja, `plan_sha256`, audyt, commit źródłowy']
    else:
        lines = [f'- `{asset}` — instalator, {size} B',
                 '- `SHA256SUMS.txt` — sumy wszystkich załączników',
                 '- `PL_COVERAGE.json` — co dokładnie jest przetłumaczone',
                 '- `RELEASE_INFO.json` — wersja, `plan_sha256`, audyt, commit źródłowy']

    text = HEADER + TABLE.format(**numbers)
    if changes:
        text += CHANGES.format(changes=changes)
    text += f'\nSuma kontrolna instalatora: `{sha}`\n'
    text += INSTALL + LIMITS + ASSETS.format(lines='\n'.join(lines))
    text += ENGLISH.format(**numbers)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--info', type=Path, required=True)
    parser.add_argument('--coverage', type=Path, required=True)
    parser.add_argument('--tag', default='')
    parser.add_argument('--repo', default='')
    parser.add_argument('--changes', default=None,
                        help='własny opis zmian; domyślnie komunikat ostatniego commita')
    parser.add_argument('--bundles', type=int, default=12)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)

    info = json.loads(args.info.read_text(encoding='utf-8'))
    coverage = json.loads(args.coverage.read_text(encoding='utf-8'))
    info.setdefault('bundles', args.bundles)
    changes = args.changes if args.changes is not None else git_message()
    text = render(info, coverage, args.tag, args.repo, changes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding='utf-8')
    print(f'zapisane: {args.out} ({len(text)} znaków)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
