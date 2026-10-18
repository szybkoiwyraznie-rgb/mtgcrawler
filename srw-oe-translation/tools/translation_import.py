#!/usr/bin/env python3
"""Move the translation a translator typed into the scene view (``*.md``) back into the package.

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

With ``--lang pl`` the Polish views are read instead: they carry the English as a read-only
reference block (``EN:``) plus the ``PL:`` slot the translator fills, and the Polish lands in
the ``pl`` field of the package - validated with the rules of ``translation_check --field pl``
(the 18 letters as private font codes, width counted in half-width units).

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
PL_RE = re.compile(r"^\s*PL:\s?(.*)$")


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


def parse_view_full(text: str, include_empty: bool = False) -> Dict[Tuple[str, str], Dict[str, str]]:
    """{(group, element): {"en"/"pl": text, "jp": japanese first line}} of every element.

    ``group`` is ``grp:<number>`` for the heading of a view (the scene number in a scene view, the
    number of the group in a table view) or the ``container/member`` of an older view that still
    carried the game file name.  ``element`` is the number of the element (``"3"``) or the mission
    element (``"T1"``, ``"N1"``).  An element is always a group heading, one ``N. [Label] text``
    line, its continuation lines and the ``EN:``/``PL:`` blocks under it (an English view carries
    only ``EN:``; a Polish view carries the English as a read-only reference plus the ``PL:``
    slot); the Japanese first line is kept so the importer can tell a stale view from a good one.
    """
    found: Dict[Tuple[str, str], Dict[str, str]] = {}
    group: Optional[str] = None
    token: Optional[str] = None
    jp: Optional[str] = None
    jp_lines: List[str] = []
    blocks: Dict[str, int] = {}     # how many blocks of each prefix the element carries (2 = a mistake)
    text_by_field: Dict[str, List[str]] = {}
    open_field: Optional[str] = None   # the block the continuation lines belong to

    def close() -> None:
        if group is None or token is None:
            return
        entry = {"jp": (jp or "").rstrip(" "), "jp_full": "\n".join(jp_lines)}
        for field, lines in text_by_field.items():
            joined = ("\n".join(line.rstrip(" ") for line in lines).strip("\n")
                      if field == "en" else "\n".join(lines).rstrip("\n"))
            if joined.strip():
                entry[field] = restore_markers(joined)
        if include_empty or any(field in entry for field in ("en", "pl")):
            entry["blocks"] = blocks.get("en", 0)
            entry["pl_blocks"] = blocks.get("pl", 0)
            key = (group, token)
            if key in found:
                entry["duplicate_element"] = True
            entry["present_fields"] = list(text_by_field)
            found[key] = entry
        text_by_field.clear()
        blocks.clear()
        jp_lines.clear()

    for raw in text.splitlines():
        heading = GROUP_HEAD_RE.match(raw)
        if heading:
            close()
            text_by_field, token, jp, open_field = {}, None, None, None
            group = f"grp:{int(heading.group(1))}"
            continue
        match = SCENE_FILE_RE.match(raw)
        if match:
            close()
            text_by_field, token, jp, open_field = {}, None, None, None
            group = f"{match.group(1)}/{match.group(2)}"
            continue
        if raw.startswith("## ") or raw.startswith("- "):
            close()
            text_by_field, token, jp, open_field = {}, None, None, None
            continue
        if raw.strip() == "_koniec sceny_":
            close()
            text_by_field, token, jp, open_field = {}, None, None, None
            continue
        element = ELEMENT_RE.match(raw) or META_RE.match(raw)
        if element:
            close()
            token = element.group(1)
            jp = element.group(3)
            jp_lines.append(jp)
            text_by_field, open_field = {}, None
            continue
        en_match = EN_RE.match(raw)
        pl_match = PL_RE.match(raw)
        if en_match or pl_match:
            field = "en" if en_match else "pl"
            content = (en_match or pl_match).group(1)
            if field in text_by_field:
                blocks[field] = blocks.get(field, 0) + 1   # the element had a block already
            text_by_field[field] = [content.lstrip(" ") if field == "en" else content]
            open_field = field
            continue
        if raw.startswith("   limit:") or raw.startswith("   ("):
            continue
        if open_field is not None:
            if open_field == "en" or raw.startswith("   "):
                text_by_field[open_field].append(raw[3:] if raw.startswith("   ") else raw)
        elif token is not None and raw.startswith("   "):
            jp_lines.append(raw[3:])
    close()
    return found


def parse_view(text: str, field: str = "en") -> Dict[Tuple[str, str], str]:
    """``{(group, element): text}`` of one field - what the view holds, for comparing."""
    return {key: value[field] for key, value in parse_view_full(text).items() if field in value}


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


def import_views(views: Dict[Path, str], package: Path, apply: bool = True,
                 field: str = "en", require_template: bool = False) -> dict:
    """Write the translation of the views into the package; ``apply=False`` only reports.

    ``field`` says which slot the views fill: ``en`` (the ``EN:`` lines, the English flow)
    or ``pl`` (the ``PL:`` lines of the Polish views - there the ``EN:`` block is a
    read-only reference and is never imported).
    """
    import table_view                     # deferred: table_view imports this module for the markers

    rows, by_file = load_rows(package)
    lookup = scene_lookup(rows)
    plan = table_view.plan_from(by_file, lang=field)     # the very rows that get written back
    # tokeny.tsv (tools/token_map.py) next to the package tells the checker which %s of a
    # display-form jp is a literal placeholder (mandatory in EN) and which is a kana token
    # 0x0F (dropped from EN with the character after it); without it every %s stays mandatory
    sidecar = TMAP.find_sidecar([Path(package)])
    token_map = TMAP.load_map(sidecar) if sidecar else {}

    report = {"views": len(views), "field": field, "elements_with_text": 0, "imported": 0,
              "unchanged": 0, "unknown": [], "rejected": [], "duplicated": [], "written": [],
              "rows": len(rows), "token_map": str(sidecar) if sidecar else None}
    import pl_handoff as PH
    import translation_copy as COPY
    source_hash = PH.fingerprint(by_file) if field == "pl" else None
    before = {id(r): r.get(field) or "" for r in rows}
    assigned = {}
    touched: Dict[str, List[dict]] = {}
    for name, text in views.items():
        if field == "pl":
            stamps = PH.STAMP_RE.findall(text)
            if (require_template and stamps != [source_hash]) or (stamps and stamps != [source_hash]):
                report["rejected"].append(f"{name}: missing/stale PL template fingerprint")
                continue
        kind = view_kind(name)
        view_name = str(name).replace("\\", "/").rsplit("/", 1)[-1]
        if ":" in view_name:                  # ``sceny.zip:epizod-00.md``
            view_name = view_name.rsplit(":", 1)[-1]
        table = view_name if view_name in table_view.VIEW_TO_FILE else None
        for (group, token), content in sorted(parse_view_full(text, include_empty=True).items()):
            if field == "pl" and (content.get("duplicate_element") or content.get("pl_blocks")):
                report["duplicated"].append(f"{name}:{group}:{token}: duplicate PL block/element")
                continue
            if field not in content:
                continue                      # the other language's block (or none)
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
            if element and field == "pl":
                # Compare the complete source, not just a repeated first line. Preserve meaningful
                # line breaks; tolerate only editor-trimmed trailing spaces and old literal \n.
                shown = re.sub(r"\\+n", "\n", restore_markers(content["jp_full"]))
                expected = element[0].get("jp") or ""
                normalize = lambda t: "\n".join(line.rstrip(" ") for line in t.split("\n"))
                if normalize(shown) != normalize(expected) or any(PH.excluded_reason(r) for r in element):
                    element = None
            if not element:
                report["unknown"].append(f"{name}:{group}:{token}")
                continue
            if content.get("blocks" if field == "en" else "pl_blocks"):
                report["duplicated"].append(
                    f"{name}:{group}:{token} ({content['blocks' if field == 'en' else 'pl_blocks'] + 1}"
                    f" linii {field.upper()} — liczy się ostatnia, pusta: usuń nadmiarową)")
            typed = restore_trailing_breaks(content[field], element[0].get("jp") or "")
            # a translator who keeps every placeholder copies the kana tokens too
            # (``%s*%s&Damage`` for ``%s*ﾒｰ%s&``); the sidecar says which %s are kana tokens
            # and they leave the translation here, with the glyph byte after them (never a bare %s)
            pct = next((token_map[row["id"]] for row in element if row.get("id") in token_map),
                       None)
            typed = TC.strip_kana_tokens(typed, element[0].get("jp") or "", pct)
            if field == "pl" and any(id(r) in assigned and assigned[id(r)] != typed for r in element):
                report["rejected"].append(f"{name}:{group}:{token}: conflicting translations of one row")
                continue
            for r in element:
                assigned[id(r)] = typed
            if all((row.get(field) or "") == typed for row in element):
                report["unchanged"] += 1
                continue
            problems = []
            for row in element:
                candidate = dict(row)
                candidate[field] = typed
                errors, _ = TC.check_row(candidate, pct=token_map.get(row.get("id")),
                                         field=field)
                problems.extend(f"{row.get('id', '?')}: {message}" for message in errors)
            if problems:
                report["rejected"].extend(problems)
                continue
            for row in element:
                row[field] = typed
                touched.setdefault(row["_file"], []).append(row)
            report["imported"] += 1
    if field == "pl":
        # Explicit copies only, never heuristic mirroring. Source edits must reach all DLC copies.
        report["copies"] = COPY.copy_rows(rows, field=field, resync=True, token_map=token_map)
        report["rejected"].extend(report["copies"]["problems"])
        for r in rows:
            if (r.get(field) or "") != before[id(r)]:
                touched.setdefault(r["_file"], []).append(r)
        for message, _ids in TC.conflicting_duplicates(rows, field=field):
            report["rejected"].append(message)
    failed = any(report[k] for k in ("unknown", "rejected", "duplicated"))
    report["applied"] = bool(apply and not (field == "pl" and failed))
    if report["applied"]:
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
    parser.add_argument("--lang", choices=("en", "pl"), default="en",
                        help="which slot the views fill: en = the EN: lines (default), "
                             "pl = the PL: lines of the Polish views (EN: is the reference there)")
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    parser.add_argument("--require-template", action="store_true",
                        help="require the audited PL source fingerprint in every view")
    args = parser.parse_args(argv)

    views = read_views(args.views)
    report = import_views(views, args.package, apply=not args.check, field=args.lang,
                          require_template=args.require_template)
    summary = {key: value for key, value in report.items()
               if key not in ("unknown", "rejected", "duplicated")}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    for message in report["rejected"][:40]:
        print(f"odrzucone: {message}")
    for message in report["duplicated"][:40]:
        print(f"dwie linie: {message}")
    for message in report["unknown"][:40]:
        print(f"nieznane: {message}")
    return 1 if any(report[k] for k in ("unknown", "rejected", "duplicated")) else 0


if __name__ == "__main__":
    sys.exit(main())
