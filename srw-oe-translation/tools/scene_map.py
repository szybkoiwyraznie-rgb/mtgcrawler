#!/usr/bin/env python3
"""Group story text into *scenes* and put the scenes into game order.

A scene is one member of an event container (``eventP*/evept*``): ``DL100_01.bin`` is the mission
"初等訓練", ``SM004.bin`` is the simulator mission "宇宙の脅威".  The member name encodes the place
of the scene in the game [ZWERYFIKOWANE]:

    DL<volume><episode:2>_<ordinal:2><variant>.bin     e.g. DL102_50B  = volume 1, episode 2, 50, B
    SM<number:3><variant>.bin                          simulator missions (training)

``volume`` (first digit after ``DL``) is the disc/DLC pack, ``episode`` (two digits) is the episode
number the mission list (``milstP``) calls "N話" - checked against the mission titles: 79 titles
carry an ``N話`` prefix and **every** one of them matches the member name's episode, 0 mismatches
[ZWERYFIKOWANE].  ``variant`` letters B..J are the later DLC packs (``evept101`` -> B, ``evept108``
-> J), so scenes of the same ordinal are ordered by pack [HIPOTEZA co do kolejności wewnątrz misji].

Text order *inside* a scene is the byte order of the records in the member, which is the order the
game shows them (measured: ascending offsets in every member).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, Iterable, List, Optional, Tuple

EPISODE_RE = re.compile(r"^DL(\d)(\d\d)_(\d\d)([A-Z]?)\.bin$")
SIM_RE = re.compile(r"^SM(\d\d\d)([A-Z]?)\.bin$")
EPISODE_LABEL_RE = re.compile(r"^([0-9]+)話\s*メインミッション$")
VARIANT_ORDER = "BCDEFGHJ"
SECTION_KINDS = ("location", "scene_title")


def normalize(text: str) -> str:
    """Full-width digits to ASCII and every whitespace run to a single space."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text or "")).strip()


def parse_member(member: str) -> Optional[dict]:
    """Volume/episode/ordinal/variant of an event member, or None when the name fits no pattern."""
    match = EPISODE_RE.match(member)
    if match:
        volume, episode, ordinal, variant = match.groups()
        return {"series": "story", "volume": int(volume), "episode": int(episode),
                "ordinal": int(ordinal), "variant": variant or None}
    match = SIM_RE.match(member)
    if match:
        number, variant = match.groups()
        return {"series": "simulator", "volume": None, "episode": None,
                "ordinal": int(number), "variant": variant or None}
    return None


def scene_id(container: str, member: str) -> str:
    """Stable scene id (the ``scene`` field of every dialogue row and the key of ``06_scenes``)."""
    return f"{container}/{member}"


def sort_key(container: str, member: str) -> tuple:
    """Chronology: story by (episode, ordinal, DLC pack), then the simulator missions, then the rest."""
    info = parse_member(member)
    if info is None:
        return (2, 0, 0, 0, container, member)
    variant_rank = VARIANT_ORDER.find(info["variant"]) if info["variant"] else -1
    if info["series"] == "simulator":
        return (1, info["ordinal"], 0, variant_rank, container, member)
    return (0, info["episode"], info["ordinal"], variant_rank, container, member)


def episode_labels(mission_rows: Iterable[dict]) -> Dict[int, str]:
    """``{episode: "N話 メインミッション"}`` from the mission list (``milstP`` records)."""
    labels: Dict[int, str] = {}
    for row in mission_rows:
        if row.get("kind") != "mission_title" or not row.get("member", "").startswith("milstP"):
            continue
        for slot in row.get("slots", []):
            match = EPISODE_LABEL_RE.match(normalize(slot.get("text", "")))
            if match:
                labels[int(match.group(1))] = slot["text"]
    return labels


def scene_titles(mission_rows: Iterable[dict]) -> Dict[Tuple[str, str], dict]:
    """``{(container, member): {title, mission_row, notes}}`` from the ``*_ext.dat`` mission records."""
    titles: Dict[Tuple[str, str], dict] = {}
    for row in mission_rows:
        member = row.get("member", "")
        if row.get("kind") != "mission_note" or not member.endswith("_ext.dat"):
            continue
        stem = member[: -len("_ext.dat")] + ".bin"
        slots = {slot.get("role"): slot.get("text") for slot in row.get("slots", [])}
        row_id = f"mission_note:{row['container']}/{member}:r{row['record']}:"
        titles[(row["container"], stem)] = {
            "title": slots.get("title") or None,
            "mission_row": row_id + "title" if slots.get("title") else None,
            "notes": [row_id + role for role in ("note_a", "note_b") if slots.get(role)],
        }
    return titles


def build_scenes(items: List[dict], mission_rows: Iterable[dict]) -> Tuple[List[dict], List[dict]]:
    """Order the text items by scene, number them inside each scene, and describe every scene.

    ``items`` are the dialogue/narration/embedded rows of one extraction; every item keeps its
    ``id`` and gets ``scene`` (the scene id) and ``order`` (its 1-based position inside the scene).
    The second return value is the scene index (``06_scenes.jsonl`` rows), in game order.
    """
    mission_rows = list(mission_rows)
    labels = episode_labels(mission_rows)
    titles = scene_titles(mission_rows)
    by_scene: Dict[Tuple[str, str], List[dict]] = {}
    for item in items:
        key = (item["container"], item["member"])
        by_scene.setdefault(key, []).append(item)
    ordered_keys = sorted(by_scene, key=lambda key: sort_key(key[0], key[1]))

    scenes: List[dict] = []
    ordered_items: List[dict] = []
    items_by_scene: Dict[str, List[dict]] = {}
    for seq, (container, member) in enumerate(ordered_keys, start=1):
        scene_items = sorted(by_scene[(container, member)],
                             key=lambda item: item["text_offset"])
        info = parse_member(member) or {}
        ident = scene_id(container, member)
        title = titles.get((container, member), {})
        sections = []
        counts: Dict[str, int] = {}
        for order, item in enumerate(scene_items, start=1):
            item["scene"] = ident
            item["order"] = order
            ordered_items.append(item)
            kind = item.get("kind") or "unknown"
            counts[kind] = counts.get(kind, 0) + 1
            if kind in SECTION_KINDS:
                sections.append({"order": order, "kind": kind, "row": item["id"],
                                 "jp": item.get("jp") or item.get("text") or ""})
        items_by_scene[ident] = scene_items
        episode = info.get("episode")
        scenes.append({
            "id": ident,
            "seq": seq,
            "series": info.get("series"),
            "episode": episode,
            "episode_label": labels.get(episode) if episode is not None else None,
            "volume": info.get("volume"),
            "variant": info.get("variant"),
            "ordinal": info.get("ordinal"),
            "container": container,
            "member": member,
            "mission": title.get("title"),
            "mission_row": title.get("mission_row"),
            "mission_notes": title.get("notes", []),
            "sections": sections,
            "counts": dict(sorted(counts.items())),
            "rows": len(scene_items),
            "jp_bytes": sum(item.get("bytes") or 0 for item in scene_items),
            "first_row": scene_items[0]["id"] if scene_items else None,
            "last_row": scene_items[-1]["id"] if scene_items else None,
        })
    _inherit_titles(scenes)
    _mark_copies(scenes, items_by_scene)
    return ordered_items, scenes


def _scene_key(scene: dict) -> Tuple[str, int, int]:
    return (scene["series"] or "", scene["episode"] if scene["episode"] is not None else -1,
            scene["ordinal"])


def _mark_copies(scenes: List[dict], items_by_scene: Dict[str, List[dict]]) -> None:
    """Mark the DLC re-releases of a scene: identical text, so it must be translated once.

    The letter variants (B..J) are the same scene shipped again in a later DLC pack; 67 of the 293
    scenes repeat a base scene word for word [ZWERYFIKOWANE by comparing every text of the scene].
    Such a scene gets ``duplicate_of`` and every one of its rows gets ``copy_of`` pointing at the
    base row, so the translation can be copied instead of written twice (the game still needs the
    text in every container, so the rows stay).
    """
    bases: Dict[Tuple[str, int, int], str] = {}
    for scene in scenes:
        if not scene["variant"]:
            bases.setdefault(_scene_key(scene), scene["id"])
    for scene in scenes:
        base = bases.get(_scene_key(scene))
        if not base or base == scene["id"]:
            continue
        mine = items_by_scene.get(scene["id"], [])
        theirs = items_by_scene.get(base, [])
        if not mine or len(mine) != len(theirs):
            scene["variant_of"] = base
            continue
        if [item.get("jp") for item in mine] != [item.get("jp") for item in theirs]:
            # the later pack shipped an edited version of the same scene: translate the base first
            # and adjust, the row order still lines up one to one
            scene["variant_of"] = base
            for item, source in zip(mine, theirs):
                if item.get("jp") == source.get("jp"):
                    item["copy_of"] = source["id"]
            continue
        scene["duplicate_of"] = base
        for item, source in zip(mine, theirs):
            item["copy_of"] = source["id"]


def _inherit_titles(scenes: List[dict]) -> None:
    """A scene without its own ``*_ext.dat`` takes the title of its base scene (same episode+ordinal).

    The letter variants (B..J, the later DLC packs) have no ``_ext.dat`` of their own; 69 of the 293
    scenes are such variants.  They belong to the same mission as the base scene, so the title is
    inherited and marked with ``mission_inherited`` (never silently guessed).
    """
    titles: Dict[Tuple[str, int, int], str] = {}
    for scene in scenes:
        if scene["mission"]:
            titles.setdefault(_scene_key(scene), scene["mission"])
    for scene in scenes:
        if scene["mission"]:
            scene["mission_inherited"] = False
            continue
        inherited = titles.get(_scene_key(scene))
        scene["mission"] = inherited
        scene["mission_inherited"] = bool(inherited)
