#!/usr/bin/env python3
"""Zastosuj do gotowego `srwoe_mission_deployments.md` cięcia z decyzji 2026-11-11.

Generator `mission_deployments.py` już wycina te dwie rzeczy u źródła, ale żeby go
uruchomić, trzeba mieć kontenery gry i odszyfrowany ELF 1.08 — pliki właściciela,
których w repozytorium nie ma i mieć nie będzie. Żeby dokument w repo zgadzał się
z tym, co generator wypuści przy następnym pełnym przebiegu, stosujemy **te same
funkcje** (`drop_zero_selector`, `drop_ace_bonus`), a nie ręczne poprawki.

Dzięki temu reguła ma jedną definicję w kodzie, a nie dwie rozjeżdżające się kopie.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from mission_deployments import ZERO_SELECTOR_HEADING  # noqa: E402

ACE_PREFIX = '**Premia Asa'


def trim(text: str) -> tuple[str, int, int]:
    out: list[str] = []
    skipping = False
    dropped_sections = dropped_ace = 0
    for line in text.split('\n'):
        if line.startswith(ZERO_SELECTOR_HEADING):
            skipping = True
            dropped_sections += 1
            continue
        if skipping:
            if line.startswith(('#### ', '### ', '## ', '# ')) or line.strip() == '---':
                skipping = False
            else:
                continue
        if line.startswith(ACE_PREFIX):
            dropped_ace += 1
            continue
        out.append(line)
    joined = re.sub(r'\n{3,}', '\n\n', '\n'.join(out))
    return joined.rstrip() + '\n', dropped_sections, dropped_ace


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--path', type=Path,
                    default=HERE.parent / 'docs' / 'srwoe_mission_deployments.md')
    ap.add_argument('--out', type=Path, default=None, help='Domyślnie w miejscu')
    args = ap.parse_args(argv)
    text = args.path.read_text(encoding='utf-8')
    trimmed, sections, ace = trim(text)
    target = args.out or args.path
    target.write_text(trimmed, encoding='utf-8')
    data = trimmed.encode('utf-8')
    print(f'usunięto {sections} sekcji „selektor zerowy”, {ace} wierszy „Premia Asa”')
    print(f'{target}: {len(data)} B, {trimmed.count(chr(10))} linii, '
          f'sha256 {hashlib.sha256(data).hexdigest()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
