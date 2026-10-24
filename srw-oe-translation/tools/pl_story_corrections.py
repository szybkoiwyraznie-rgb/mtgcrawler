#!/usr/bin/env python3
"""Apply reviewed, source-bound Polish story-language edits to a PL snapshot.

This is the prose counterpart to ``pl_ui_corrections.py``.  Every edit is bound
to an immutable source-row hash, the exact previous Polish text and an explicit
row ID.  The tool refuses stale rows, duplicate edits, control-token changes,
line-break changes and any replacement rejected by the normal PL row checker.
It writes a new snapshot directory; promoting that directory over ``pakiet_PL``
is a separate, deliberate step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pl_release_package as R
import pl_text
import token_map as TM
import translation_check as C


LEDGER = "owner_story_language_corrections"
ALLOWED_FILES = {"00_dialogue.jsonl", "01_battle_quotes.jsonl"}


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _copy_groups(source_rows: list[dict]) -> dict[tuple[str, str], set[tuple[str, str]]]:
    """Union JP-identical ``copy_of`` chains into groups of source-binding keys.

    A later DLC scene can repeat a dialogue row under a different ID.  Such a
    copy often has its own explicit snapshot entry.  Changing only the base
    row would make release materialisation resync that explicit copy and then
    (correctly) refuse the conflicting reviewed texts.  A story plan must
    therefore spell out every explicit member of the copied line's group.
    """
    parent: dict[int, int] = {}

    def find(index: int) -> int:
        parent.setdefault(index, index)
        if parent[index] != index:
            parent[index] = find(parent[index])
        return parent[index]

    def union(left: int, right: int) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[b] = a

    by_id_jp: dict[tuple[object, object], list[int]] = {}
    for index, row in enumerate(source_rows):
        by_id_jp.setdefault((row.get("id"), row.get("jp")), []).append(index)
    for index, row in enumerate(source_rows):
        copied_from = row.get("copy_of")
        if not copied_from:
            continue
        candidates = by_id_jp.get((copied_from, row.get("jp")), [])
        # Translation_copy accepts ambiguous legacy IDs by preferring a
        # non-copy row.  Mirror that narrow rule; otherwise refuse to guess.
        roots = [candidate for candidate in candidates if not source_rows[candidate].get("copy_of")]
        chosen = roots if len(roots) == 1 else candidates
        if len(chosen) == 1:
            union(index, chosen[0])

    groups: dict[tuple[str, str], set[tuple[str, str]]] = {}
    by_root: dict[int, set[tuple[str, str]]] = {}
    for index, row in enumerate(source_rows):
        key = (row["_file"], R.binding(row))
        by_root.setdefault(find(index), set()).add(key)
    for members in by_root.values():
        if len(members) > 1:
            for key in members:
                groups[key] = set(members)
    return groups


def apply(base: Path, stored: Path, plan_path: Path, out: Path) -> dict:
    """Return the revised manifest after writing ``out``.

    ``base`` is the current EN source package, ``stored`` the PL snapshot and
    ``plan_path`` a schema-1 JSON plan with a non-empty ``changes`` list.
    """
    R.fresh(out, base)
    R.fresh(out, stored)

    manifest = json.loads((stored / R.MANIFEST).read_text(encoding="utf-8"))
    data = (stored / R.DATA).read_bytes()
    if manifest.get("schema") != R.SCHEMA or hashlib.sha256(data).hexdigest() != manifest.get("data_sha256"):
        raise ValueError("snapshot schema/hash mismatch")
    entries = _load_jsonl(stored / R.DATA)
    stored_by_key = {(entry["file"], entry["source_sha256"]): entry for entry in entries}
    if len(stored_by_key) != len(entries) or len(entries) != manifest.get("entries"):
        raise ValueError("snapshot duplicate/count mismatch")

    source_rows, _ = R.I.load_rows(base)
    source_by_key: dict[tuple[str, str], list[dict]] = {}
    for row in source_rows:
        source_by_key.setdefault((row["_file"], R.binding(row)), []).append(row)
    copy_groups = _copy_groups(source_rows)
    token_path = base / "tokeny.tsv"
    tokens_by_id = TM.load_map(token_path) if token_path.exists() else {}

    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    changes = plan.get("changes")
    if plan.get("schema") != 1 or not isinstance(changes, list) or not changes:
        raise ValueError("invalid/empty story correction plan")

    # Pre-flight copied dialogue groups before mutating any snapshot entry.
    # Copies without an explicit stored entry are filled by the release
    # materialiser; explicit copies must be reviewed in this same plan and
    # must receive exactly the same replacement text.
    planned: dict[tuple[str, str], str] = {}
    for edit in changes:
        if not isinstance(edit, dict):
            continue
        key = (edit.get("file"), edit.get("source_sha256"))
        if all(isinstance(value, str) for value in (*key, edit.get("after"))):
            planned[key] = edit["after"]
    for edit in changes:
        if not isinstance(edit, dict):
            continue
        key = (edit.get("file"), edit.get("source_sha256"))
        after = edit.get("after")
        if key not in planned or not isinstance(after, str):
            continue
        for alias_key in copy_groups.get(key, set()):
            if alias_key == key:
                continue
            alias_entry = stored_by_key.get(alias_key)
            if alias_entry is None or alias_entry.get("pl") == after:
                continue
            if planned.get(alias_key) != after:
                raise ValueError(
                    "story correction omits explicit copy alias "
                    f"{alias_entry.get('id')} for {edit.get('id')}"
                )

    seen: set[tuple[str, str]] = set()
    seen_ids: set[str] = set()
    for edit in changes:
        if not isinstance(edit, dict):
            raise ValueError("story correction is not an object")
        file_name = edit.get("file")
        row_id = edit.get("id")
        source_sha = edit.get("source_sha256")
        before = edit.get("before")
        after = edit.get("after")
        if file_name not in ALLOWED_FILES:
            raise ValueError(f"story correction outside reviewed prose files: {row_id}")
        if not all(isinstance(value, str) and value for value in (row_id, source_sha, before, after)):
            raise ValueError(f"incomplete story correction: {row_id}")
        key = (file_name, source_sha)
        if key in seen or row_id in seen_ids:
            raise ValueError(f"duplicate story correction: {row_id}")
        seen.add(key)
        seen_ids.add(row_id)

        source_candidates = source_by_key.get(key) or []
        # A binding can be shared by exact physical aliases.  All aliases must
        # carry the plan's ID; the snapshot format itself enforces the same
        # invariant when materializing.  Refuse anything less exact here.
        if not source_candidates or any(row.get("id") != row_id for row in source_candidates):
            raise ValueError(f"stale/unknown story source binding: {row_id}")
        source = source_candidates[0]
        if source.get("category") not in {"dialogue", "battle_quote", "quote"}:
            raise ValueError(f"story correction targets non-prose category: {row_id}")

        stored_entry = stored_by_key.get(key)
        if stored_entry is None or stored_entry.get("id") != row_id or stored_entry.get("pl") != before:
            raise ValueError(f"stale story correction: {row_id}")
        if after == before:
            raise ValueError(f"no-op story correction: {row_id}")
        if "\0" in after or "\x0f" in after:
            raise ValueError(f"story correction introduces a forbidden control: {row_id}")
        if after.count("\n") != before.count("\n") or after.count("\n") != (source.get("jp") or "").count("\n"):
            raise ValueError(f"story correction changes line-break count: {row_id}")
        if [ord(ch) for ch in after if ord(ch) < 32 and ch != "\n"] != [
            ord(ch) for ch in before if ord(ch) < 32 and ch != "\n"
        ]:
            raise ValueError(f"story correction changes control characters: {row_id}")
        pl_text.encode(after)  # fail closed on unsupported glyphs
        errors, _warnings = C.check_row(
            {**source, "pl": after}, pct=tokens_by_id.get(row_id), field="pl"
        )
        if errors:
            raise ValueError(f"invalid Polish story correction: {row_id}: " + "; ".join(errors))
        stored_entry["pl"] = after

    revised = "".join(
        R.canonical(entry) + "\n"
        for entry in sorted(entries, key=lambda entry: (entry["file"], entry["source_sha256"]))
    ).encode("utf-8")
    manifest["entries"] = len(entries)
    manifest["data_sha256"] = hashlib.sha256(revised).hexdigest()
    manifest.setdefault(LEDGER, []).append(
        dict(
            plan=plan_path.name,
            sha256=hashlib.sha256(plan_bytes).hexdigest(),
            previous_data_sha256=hashlib.sha256(data).hexdigest(),
            entries=len(changes),
            episode=plan.get("episode"),
            operation="source-bound PL story-language edits",
            runtime_tested=False,
        )
    )
    out.mkdir(parents=True)
    (out / R.DATA).write_bytes(revised)
    (out / R.MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("base", "stored", "plan", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(apply(args.base, args.stored, args.plan, args.out), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
