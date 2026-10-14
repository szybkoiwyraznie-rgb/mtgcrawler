#!/usr/bin/env python3
"""Move the English a translator typed into the scene view (``*.md``) back into the package.

The scene view (``tools/scene_view.py`` -> ``sceny/*.md``, shipped as ``sceny.zip``) is the reading
copy: every element of every scene in game order, with its place, its participants and its Japanese
text.  It is **not** sent to the game - it is a work card.  This tool reads the English out of it and
writes it into the package (``00_dialogue.jsonl`` for the scenes, ``05_mission_text.jsonl`` for the
mission title and notes), which stay the single source of truth the game is built from.

The view carries an empty ``EN:`` line under every element, so the translator only types after the
colon::

    ## Scena 1/293 — 初等訓練
    - odcinek: ０話 メインミッション (episode 0)

    T1. [Tytuł misji] 初等訓練
       EN: Basic Training
    1. [Dialog - セイシロウ・クサナギ] さて、訓練の時間だ。
       EN: Now then, it is time for training.

An element is addressed by the scene number of its heading (``## Scena 1/293`` = the ``seq`` of
``06_scenes.jsonl``) plus its own number ``1.``, ``2.``, …; the mission title and notes of the scene
use ``T1.`` / ``N1.``, ``N2.``.  Every following indented line belongs to the same element, so the
number of line breaks stays the same as in the Japanese text (the game draws the box around them);
the two invisible characters of the view are written back as bytes (``\u23ce`` -> carriage
return, ``<0x0F>`` -> 0x0F, the lead byte of a voiced-kana token that the English text must NOT
carry - the validator rejects it), so the translator never types an invisible byte,
and a trailing break the Japanese text ends with is restored automatically.  Elements that repeat a
line of another scene (``[kopia]``) carry no ``EN:`` line: their English comes from
``tools/translation_copy.py``.

A text that would break the game (CP932, control tokens, line breaks, control characters - the rules
of ``tools/translation_check.py``) is **refused**, not written, and reported, so a broken view can
never clobber the package.

The table views of ``tools/table_view.py`` (``postacie.md``, ``mechy.md``, ``przedmioty.md``,
``umiejetnosci.md``, ``teksty-config.md``, ``teksty-misji.md``) are read the same way: their
``## Postać 12/582`` heading is the group, the number of the element is its position inside the
group, and the Japanese text on the element line is checked before anything is written, so a view
rendered from an older package can never clobber a newer one.

Usage::

    python tools/translation_import.py --views local/translation/sceny --package local/translation
    python tools/translation_import.py --views local/translation/widoki --package local/translation
    python tools/translation_import.py --views sceny.zip widoki.zip --package local/translation --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import token_map as TMAP  # noqa: E402
import translation_check as TC  # noqa: E402

MARKERS = (("\u23ce", "\r"), ("<0x0F>", "\x0f"))   # the view shows them, the game needs bytes
GROUP_HEAD_RE = re.compile(r"^## .+? (\d+)/\d+")
SCENE_FILE_RE = re.compile(r"^- plik gry: (.+?) / (.+?)\s*$")   # older views carried the file name
ELEMENT_RE = re.compile(r"^(\d+)\. \[(.*?)\] (.*)$")
META_RE = re.compile(r"^(T\d+|N\d+)\. \[(.*?)\] (.*)$")
EN_RE = re.compile(r"^\s*EN:\s?(.*)$")


def read_views(paths: Iterable[Path]) -> Dict[Path, str]:
    """{path: text} of every ``*.md`` given, plus every ``*.md`` inside a ``*.zip``."""
    views: Dict[Path, str] = {}
    for path in paths:
        path = Path(path)
        if path.is_dir():
            for child in sorted(path.glob("*.md")):
                views[child] = child.read_text(encoding="utf-8")
        elif path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                for name in sorted(archive.namelist()):
                    if name.lower().endswith(".md"):
                        views[Path(f"{path.name}:{name}")] = archive.read(name).decode("utf-8")
        else:
            views[path] = path.read_text(encoding="utf-8")
    return views


def restore_markers(text: str) -> str:
    """Turn the visible markers of the view back into the characters the game draws with."""
    for marker, control in MARKERS:
        text = text.replace(marker, control)
    return text


def restore_trailing_breaks(text: str, jp: str) -> str:
    """Add the line breaks the Japanese text ends with - the view has no line to type them on.

    The game stores a real ``\\n`` (often ``\\r\\n``) at the end of many lines; the view shows such a
    text as the marker (``⏎``) followed by an empty continuation line, so the translator would have to
    add a blank line after every ``EN:`` just to keep the count.  Nobody should have to: when the text
    typed into the view is exactly the Japanese minus its trailing breaks, they are restored here.
    A text that is missing any *other* break is not touched - the validator reports it, the
    translator fixes the view.
    """
    tail = jp[len(jp.rstrip("\r\n")):]
    if not tail:
        return text
    body = text.rstrip("\r\n")
    # the translator may have typed the tail in full, in part (``⏎`` on its own line, without
    # the empty line that follows it in the view) or not at all - whatever was typed, the game
    # gets exactly the Japanese tail, as long as every *inner* break of the text is there
    if jp.rstrip("\r\n").count("\n") == body.count("\n"):
        return body + tail
    return text


def parse_view_full(text: str) -> Dict[Tuple[str, str], Dict[str, str]]:
    """{(group, element): {"en": english, "jp": japanese first line}} of every element of a view.

    ``group`` is ``grp:<number>`` for the heading of a view (the scene number in a scene view, the
    number of the group in a table view) or the ``container/member`` of an older view that still
    carried the game file name.  ``element`` is the number of the element (``"3"``) or the mission
    element (``"T1"``, ``"N1"``).  An element is always a group heading, one ``N. [Label] text``
    line, its continuation lines and an optional ``EN:`` block; the Japanese first line is kept so
    the importer can tell a stale view from a good one.
    """
    found: Dict[Tuple[str, str], Dict[str, str]] = {}
    group: Optional[str] = None
    token: Optional[str] = None
    jp: Optional[str] = None
    english: Optional[List[str]] = None
    blocks = 0                       # how many ``EN:`` blocks the element carries (two = a mistake)

    def close() -> None:
        nonlocal blocks
        if group is None or token is None:
            return
        joined = "\n".join(line.rstrip(" ") for line in english or []).strip("\n")
        if joined.strip():
            found[(group, token)] = {"en": restore_markers(joined),
                                     "jp": (jp or "").rstrip(" "), "blocks": blocks}
        blocks = 0

    for raw in text.splitlines():
        heading = GROUP_HEAD_RE.match(raw)
        if heading:
            close()
            english, token, jp = None, None, None
            group = f"grp:{int(heading.group(1))}"
            continue
        match = SCENE_FILE_RE.match(raw)
        if match:
            close()
            english, token, jp = None, None, None
            group = f"{match.group(1)}/{match.group(2)}"
            continue
        if raw.startswith("## ") or raw.startswith("- "):
            close()
            english, token, jp = None, None, None
            continue
        if raw.strip() == "_koniec sceny_":
            close()
            english, token, jp = None, None, None
            continue
        element = ELEMENT_RE.match(raw) or META_RE.match(raw)
        if element:
            close()
            token = element.group(1)
            jp = element.group(3)
            english = None
            continue
        if raw.strip().startswith("EN:"):
            if english is not None:
                blocks += 1          # the element had an ``EN:`` block already
            english = [raw[raw.index("EN:") + 3:].lstrip(" ")]
            continue
        if english is not None:
            english.append(raw[3:] if raw.startswith("   ") else raw)
    close()
    return found


def parse_view(text: str) -> Dict[Tuple[str, str], str]:
    """``{(group, element): english}`` - what the view holds, for comparing with the package."""
    return {key: value["en"] for key, value in parse_view_full(text).items()}


def load_rows(package: Path) -> Tuple[List[dict], Dict[str, List[dict]]]:
    """Every package row (``*.jsonl``) plus ``{file name: rows}``."""
    rows: List[dict] = []
    by_file: Dict[str, List[dict]] = {}
    for path in sorted(Path(package).glob("*.jsonl")):
        file_rows = [json.loads(line) for line in
                     path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in file_rows:
            row["_file"] = path.name
        by_file[path.name] = file_rows
        rows.extend(file_rows)
    return rows, by_file


def scene_lookup(rows: List[dict]) -> dict:
    """The index a view is resolved against: scene number -> scene, element -> package row."""
    by_row: Dict[Tuple[str, str], dict] = {}
    by_id: Dict[str, dict] = {}
    by_seq: Dict[int, str] = {}
    meta: Dict[Tuple[str, str], str] = {}
    for row in rows:
        if row.get("id"):
            by_id[row["id"]] = row
        if row.get("scene") is not None and row.get("order") is not None:
            by_row[(row["scene"], str(int(row["order"])))] = row
        if row.get("seq") is not None and row.get("container") and row.get("id"):
            by_seq[int(row["seq"])] = row["id"]
            if row.get("mission_row"):
                meta[(row["id"], "T1")] = row["mission_row"]
            for index, note in enumerate(row.get("mission_notes") or [], start=1):
                meta[(row["id"], f"N{index}")] = note
    return {"by_row": by_row, "by_id": by_id, "by_seq": by_seq, "meta": meta}


def resolve(lookup: dict, scene: str, token: str) -> Optional[dict]:
    """The package row one scene-view element belongs to, or ``None`` when the view is out of date."""
    if scene.startswith("grp:"):
        try:
            scene_id = lookup["by_seq"].get(int(scene[4:]))
        except (TypeError, ValueError):
            return None
    else:
        scene_id = scene
    if not scene_id:
        return None
    if token.isdigit():
        return lookup["by_row"].get((scene_id, token))
    row_id = lookup["meta"].get((scene_id, token))
    return lookup["by_id"].get(row_id) if row_id else None


def resolve_table(plan: List[List[List[dict]]], group: str, token: str) -> Optional[List[dict]]:
    """The package rows of a table-view element (``grp:<group>`` + element number), or ``None``.

    One element can be backed by several rows: the same field of the same character (or unit) lives
    in several chapter tables of the game and every one of them must get the same English.
    """
    if not group.startswith("grp:") or not token.isdigit():
        return None
    index = int(group[4:]) - 1
    number = int(token) - 1
    if index < 0 or index >= len(plan) or number < 0 or number >= len(plan[index]):
        return None
    return plan[index][number]


def view_kind(name: object) -> str:
    """``table`` for a table view (``postacie.md``…), ``scene`` for everything else."""
    import table_view                     # deferred: table_view imports this module for the markers
    file_name = str(name).replace("\\", "/").rsplit("/", 1)[-1]
    if ":" in file_name:                  # ``sceny.zip:epizod-00.md``
        file_name = file_name.rsplit(":", 1)[-1]
    return "table" if file_name in table_view.VIEW_TO_FILE else "scene"


def import_views(views: Dict[Path, str], package: Path, apply: bool = True) -> dict:
    """Write the English of the views into the package; ``apply=False`` only reports."""
    import table_view                     # deferred: table_view imports this module for the markers

    rows, by_file = load_rows(package)
    lookup = scene_lookup(rows)
    plan = table_view.plan_from(by_file)     # the very rows that get written back
    # tokeny.tsv (tools/token_map.py) next to the package tells the checker which %s of a
    # display-form jp is a literal placeholder (mandatory in EN) and which is a kana token
    # 0x0F (dropped from EN with the character after it); without it every %s stays mandatory
    sidecar = TMAP.find_sidecar([Path(package)])
    token_map = TMAP.load_map(sidecar) if sidecar else {}

    report = {"views": len(views), "elements_with_text": 0, "imported": 0, "unchanged": 0,
              "unknown": [], "rejected": [], "duplicated": [], "written": [], "rows": len(rows),
              "token_map": str(sidecar) if sidecar else None}
    touched: Dict[str, List[dict]] = {}
    for name, text in views.items():
        kind = view_kind(name)
        view_name = str(name).replace("\\", "/").rsplit("/", 1)[-1]
        if ":" in view_name:                  # ``sceny.zip:epizod-00.md``
            view_name = view_name.rsplit(":", 1)[-1]
        table = view_name if view_name in table_view.VIEW_TO_FILE else None
        for (group, token), content in sorted(parse_view_full(text).items()):
            report["elements_with_text"] += 1
            if kind == "table":
                element = resolve_table(plan.get(table, []), group, token)
                expected = (element[0].get("jp") if element else "") or ""
                # the view shows the first line of the Japanese with the invisible characters as
                # markers (``<0x0F>``, ``⏎`` - table_view.render_markers) and an editor may drop
                # a trailing space, so the comparison happens on the game's bytes, right-trimmed
                view_jp = restore_markers(content["jp"]).rstrip(" ")
                if element is not None and view_jp and \
                        view_jp != expected.split("\n")[0].rstrip(" "):
                    element = None           # the view was rendered from other package rows
            else:
                single = resolve(lookup, group, token)
                element = [single] if single else None
            if not element:
                report["unknown"].append(f"{name}:{group}:{token}")
                continue
            if content.get("blocks"):
                report["duplicated"].append(
                    f"{name}:{group}:{token} ({content['blocks'] + 1} linii EN — liczy się ostatnia, "
                    f"pusta: usuń nadmiarową)")
            english = restore_trailing_breaks(content["en"], element[0].get("jp") or "")
            # a translator who keeps every placeholder copies the kana tokens too
            # (``%s*%s&Damage`` for ``%s*ﾒｰ%s&``); the sidecar says which %s are kana tokens
            # and they leave the English here, with the glyph byte after them (never a bare %s)
            pct = next((token_map[row["id"]] for row in element if row.get("id") in token_map),
                       None)
            english = TC.strip_kana_tokens(english, element[0].get("jp") or "", pct)
            if all((row.get("en") or "") == english for row in element):
                report["unchanged"] += 1
                continue
            problems = []
            for row in element:
                errors, _ = TC.check_row(dict(row, en=english),
                                         pct=token_map.get(row.get("id")))
                problems.extend(f"{row.get('id', '?')}: {message}" for message in errors)
            if problems:
                report["rejected"].extend(problems)
                continue
            for row in element:
                row["en"] = english
                touched.setdefault(row["_file"], []).append(row)
            report["imported"] += 1
    if apply:
        for file_name, file_rows in by_file.items():
            if file_name not in touched:
                continue
            path = Path(package) / file_name
            with path.open("w", encoding="utf-8") as handle:
                for row in file_rows:
                    handle.write(json.dumps({k: v for k, v in row.items() if k != "_file"},
                                            ensure_ascii=False) + "\n")
            report["written"].append(file_name)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--views", nargs="+", type=Path, required=True,
                        help="scene view files, a folder of *.md, or a sceny.zip")
    parser.add_argument("--package", type=Path, default=Path("local/translation"),
                        help="folder with the package JSONL (the files that get written)")
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)

    views = read_views(args.views)
    report = import_views(views, args.package, apply=not args.check)
    summary = {key: value for key, value in report.items()
               if key not in ("unknown", "rejected", "duplicated")}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    for message in report["rejected"][:40]:
        print(f"odrzucone: {message}")
    for message in report["duplicated"][:40]:
        print(f"dwie linie EN: {message}")
    for message in report["unknown"][:40]:
        print(f"nieznane: {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
