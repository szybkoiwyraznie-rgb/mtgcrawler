#!/usr/bin/env python3
"""Build the Polish test package: the real package plus probe texts, no translation.

The small in-game test (``TEST_PL.bat``) patches only ``eventP00.cpk config00.cpk font.cpk``.
This script takes the Polish package (``local/pakiet_PL``) and fills the ``pl`` field of exactly
the elements the player sees at the start of mission 0-0 and on the Exart unit screen with
**probe texts**: every Polish letter (ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż) in place of a real
translation, with dialogue line counts, trailing breaks and the ＜主人公名＞ token kept
(narration 3–6 is intentionally shortened in v4), so what the patcher writes is what the checker and the game accept.

Rows whose ``pl`` stays empty are left untouched by the build (the original Japanese stays in
the game), so the test patch changes nothing beyond the probed elements.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import text_codec  # noqa: E402

LETTERS = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
# v3 rendering was confirmed by owner screenshots. v4 changes only probe text.
KIT_VERSION = "4"
OPENING_PANELS = {
    1: ("PL V4 - PROBA CZYTELNOSCI",
        "Łączność działa. Słychać mnie wyraźnie?",
        "Chcę dziś dokończyć próbę osłony.",
        "Sprawdźmy też źródło zasilania."),
    2: ("PL V4 - MALE I WIELKIE LITERY",
        "Żaneta i Łukasz kończą ćwiczenia.",
        "Śmiało! Włącz osłonę i ruszaj naprzód.",
        "Zażółć gęślą jaźń. ĄĆĘŁŃÓŚŹŻ."),
}
# Invented font-test prose, NOT translations of the Japanese story. Narration
# 3..6 is deliberately shortened so the owner need not scroll 12 alphabet runs.
NATURAL_ROWS = {
    3: "To próbka do oceny czytelności napisów.\nNie jest tłumaczeniem scenariusza.",
    4: "Ważne są kształty liter i odstępy.\nPorównaj zwykłe litery z polskimi.",
    5: "Następne zdania pojawią się w dialogu.\nNie trzeba szukać niczego w menu.",
    6: "Za chwilę krótka próba łączności.\nMożesz sprawdzić ją na jednym ekranie.",
    7: "PL V4 - Próba łączności",
    8: "(Łączność działa. Słychać mnie wyraźnie?\nChcę dziś dokończyć próbę osłony.)",
    9: "(Muszę zachować spokój i czujność.\nPrzed nami jeszcze długa droga.)",
    10: "(Włączę osłonę, sprawdzę łączność\n i ostrożnie ruszę naprzód.\n Nie mogę dziś popełnić błędu.)",
    11: "(To tylko próba polskich napisów.\n Dzięki niej ocenię kształt liter.\n Sprawdzę też odstępy między słowami.)",
    12: "Stacja łączności",
    13: "Łączność działa. Możemy zacząć.",
    14: "Słyszę cię wyraźnie. Wszystko działa.",
    15: "＜主人公名＞, słyszysz mnie?",
    16: "Tak, słyszę cię. Włączam osłonę.\nMożemy rozpocząć ćwiczenia.",
}
LINE_BUDGET = 40            # the dialogue box holds 46 (52) units per line; stay clearly under
SCENE = "eventP00.cpk/DL100_01.bin"
MISSION_TITLE = "mission_note:eventP00.cpk/DL100_01_ext.dat:r0:title"
LAST_OPENING_ROW = 16       # rows 1..16: the opening narration, the location header, first lines
WEAPON_ROWS = tuple(f"weapon:3900:{n}:{part}" for n in range(8) for part in ("name", "name_short"))
UNIT_ROWS = {
    "unit:3900:name": "Zażółć",
    "unit:3900:name_display": "TEST PL: Zażółć gęślą jaźń",
    "unit:3905:name_display": "TEST PL: ĄĆĘŁŃÓŚŹŻ",
}


def probe_line(number: int, total: int, rotation: int) -> str:
    """One probe line: a label plus a run of the 18 letters, within the budget."""
    base = f"TEST PL {number}/{total}: "
    room = LINE_BUDGET - len(base)
    run = LETTERS[rotation % 18:] + LETTERS[:rotation % 18]
    while len(run) > room:
        run = run[:-1]
    return base + run


def probe_text(jp: str, index: int) -> str:
    """Natural test prose; preserve dialogue/token structure, shorten long narration."""
    lines = (jp or "").replace("\r", "").split("\n")
    if index in OPENING_PANELS:
        panel = iter(OPENING_PANELS[index])
        if sum(bool(line.strip()) for line in lines) != 4:
            raise ValueError("opening panel needs the measured four nonblank lines")
        return "\n".join(next(panel) if line.strip() else "" for line in lines)
    if index in NATURAL_ROWS:
        text = NATURAL_ROWS[index]
        if re.findall(r"＜[^＞]*＞", text) != re.findall(r"＜[^＞]*＞", jp):
            raise ValueError("natural probe would change a player-name token")
        if index >= 7 and len(text.split("\n")) != len(lines):
            raise ValueError("natural dialogue probe would change its line count")
        return text + ("\n" if jp.endswith("\n") else "")
    total = sum(1 for line in lines if line.strip())
    seen = 0
    out = []
    for line in lines:
        if not line.strip():
            out.append("")
            continue
        seen += 1
        # fullwidth tokens (＜主人公名＞) are part of the game's wiring: keep them verbatim
        token = ""
        while "＜" in line and "＞" in line:
            start = line.index("＜")
            end = line.index("＞", start) + 1
            token += line[start:end] + " "
            line = line[:start] + line[end:]
        probe = probe_line(seen, total, seen + index)
        if token:
            run = LETTERS[(seen + index) % 18:] + LETTERS[:(seen + index) % 18]
            while run and text_codec.display_width(token) + len(run) > \
                    LINE_BUDGET - len(f"TEST PL {seen}/{total}: "):
                run = run[:-1]
            probe = f"TEST PL {seen}/{total}: " + token + run
        out.append(probe)
    return "\n".join(out)


def weapon_probe(index: int, part: str) -> str:
    rotation = LETTERS[index % 18:] + LETTERS[:index % 18]
    if part == "name":
        run = rotation
        while len(run) + len(f"TEST W{index + 1}: ") > 44:      # cell: 64 bytes
            run = run[:-1]
        return f"TEST W{index + 1}: " + run
    return f"T{index + 1} {rotation[:4]}"                            # short cell: 32 bytes


def build(package: Path, out: Path) -> dict:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    counts = {"files": 0, "dialogue_rows": 0, "mission_rows": 0, "unit_rows": 0,
              "weapon_rows": 0}
    for path in sorted(package.glob("*.jsonl")):
        target = out / path.name
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if "jp" in row:
                row["pl"] = ""  # never inherit unrelated filled translator rows
            if path.name == "00_dialogue.jsonl" and row.get("scene") == SCENE \
                    and (row.get("order") or 99) <= LAST_OPENING_ROW:
                row["pl"] = probe_text(row.get("jp") or "", row["order"])
                counts["dialogue_rows"] += 1
            elif path.name == "05_mission_text.jsonl" and row.get("id") == MISSION_TITLE:
                row["pl"] = "TEST PL: Zażółć"
                counts["mission_rows"] += 1
            elif path.name.startswith("08_") and row.get("id") in UNIT_ROWS:
                row["pl"] = UNIT_ROWS[row["id"]]
                counts["unit_rows"] += 1
            elif path.name.startswith("08_") and row.get("id") in WEAPON_ROWS:
                index = int(row["id"].split(":")[2])
                row["pl"] = weapon_probe(index, row["part"])
                counts["weapon_rows"] += 1
            rows.append(row)
        with target.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        counts["files"] += 1
    for extra in package.iterdir():
        if extra.suffix != ".jsonl" and extra.is_file():
            shutil.copy(extra, out / extra.name)
    return counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package", type=Path, default=Path("local/pakiet_PL"))
    parser.add_argument("--out", type=Path, default=Path("local/test_PL"))
    args = parser.parse_args(argv)

    counts = build(args.package, args.out)
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    print(f"wrote {args.out} - check it with:")
    print(f"  python tools/translation_check.py --package {args.out} --field pl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
