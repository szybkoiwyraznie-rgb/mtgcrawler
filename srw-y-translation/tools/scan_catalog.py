#!/usr/bin/env python3
"""Scan a Unity Addressables catalogue for text-bearing assets (metadata only).

SRW Y ships its assets through Unity Addressables: the game directory holds a
catalogue (`StreamingAssets/aa/catalog.json` plus one catalogue per DLC) and the
asset bundles themselves. The catalogue maps **asset addresses** to bundles, and
its binary sections are base64 in the JSON, so the address strings can be
recovered without the game.

This tool reads a catalogue and reports:

* the fields that identify the Addressables build (locator id, build hash, ...);
* every plain JSON string, classified as a bundle path, asset path or other;
* every address recovered from the base64 sections (a printable-string scan works
  regardless of the exact serialiser version, which is the point: no external
  dependency can break it);
* the **candidate text assets** — addresses whose name suggests dialogue, menu
  text, localisation tables, names, glossary, tutorials;
* for each candidate, the bundle names seen near it in the same decoded blob
  (a heuristic, labelled as such).

Nothing here needs or produces game content: only address strings and file names.

Usage:
    python3 tools/scan_catalog.py --catalog catalog.json --out catalog_summary.json
    python3 tools/scan_catalog.py --catalog Dlc1/catalog_dlc1.json --print-candidates 40
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import sys
from collections import Counter
from pathlib import Path

SCHEMA = 1

# Addresses that look like they carry readable text for the player.
# Distinctive words may match anywhere; short generic ones must be whole words,
# otherwise "UnityEngine" would count as a "unit" and the hint list would drown
# in engine identifiers.
TEXT_HINT_STRONG = re.compile(
    r"(text|message|script|dialog|localiz|localis|glossar|tutorial|briefing|"
    r"episode|scenario|character|string|weapon|skill|pilot)",
    re.IGNORECASE,
)
TEXT_HINT_WORD = re.compile(
    r"\b(unit|units|name|names|item|items|char|chars|menu|menus|help|hint|"
    r"hints|talk|word|words|lang|langs|ui|title|titles|label|labels)\b",
    re.IGNORECASE,
)


def text_hint(value: str) -> bool:
    return bool(TEXT_HINT_STRONG.search(value) or TEXT_HINT_WORD.search(value))

# Lower case only: a 32-character base64 fragment ("AAAA...") must not read as a bundle.
BUNDLE_NAME = re.compile(r"^[0-9a-f]{32}(\.bundle)?$")
PRINTABLE = re.compile(rb"[\x20-\x7e\xa0-\xff][\x20-\x7e\x80-\xff]{3,}")
# Code identifiers and JSON keys are not content; keep them out of the hints.
NOISE = re.compile(r"^(m_[A-Z]|UnityEngine\.|System\.|Assembly-CSharp|Microsoft\.)")


def is_base64_blob(value: str) -> bool:
    if len(value) < 64 or len(value) % 4:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", value))


def decode_blob(value: str) -> bytes:
    try:
        return base64.b64decode(value, validate=False)
    except (binascii.Error, ValueError):
        return b""


def scan_strings(blob: bytes) -> list[str]:
    """Printable UTF-8/ASCII strings from a binary section.

    Addressables catalogues store their keys as UTF-8, so this is a UTF-8 run
    scanner. If a catalogue ever turns out to store keys as UTF-16, this returns
    far fewer strings than the section's size suggests - the summary reports the
    counts, so that shows up immediately instead of silently.
    """
    found: list[str] = []
    for match in PRINTABLE.finditer(blob):
        try:
            text = match.group().decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            continue
        text = text.strip()
        if len(text) >= 4:
            found.append(text)
    return found


def classify(text: str) -> str:
    if BUNDLE_NAME.match(text) or text.endswith(".bundle"):
        return "bundle"
    if text.startswith("Assets/") or text.startswith("Assets\\"):
        return "asset_path"
    if text_hint(text):
        return "text_hint"
    return "other"


def is_text_candidate(text: str) -> bool:
    """An address worth opening: not a bundle/file name, not code, text-ish name.

    Asset paths are included here even though ``classify`` labels them
    ``asset_path`` — that label is about shape, not about whether the asset is
    worth inspecting, and text assets are exactly ``Assets/.../Text/...``.
    """
    if classify(text) == "bundle":
        return False
    if NOISE.match(text) or len(text) < 6:
        return False
    return text_hint(text)


def walk_json(node, out: list[str]) -> None:
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for key, value in node.items():
            out.append(key)
            walk_json(value, out)
    elif isinstance(node, list):
        for item in node:
            walk_json(item, out)


def scan(catalog_path: Path, context_bytes: int = 4096) -> dict:
    """Return a summary of one catalogue. Raises SystemExit for unreadable input."""
    if not catalog_path.is_file():
        raise SystemExit(f"not a file: {catalog_path}")
    raw = catalog_path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit(f"{catalog_path.name}: not JSON ({error})") from error

    top_level = sorted(data.keys()) if isinstance(data, dict) else []
    identity = {}
    if isinstance(data, dict):
        for key in ("m_LocatorId", "m_BuildResultHash", "m_InstanceProviderData",
                    "m_SceneProviderData", "m_ContentCatalogDataVersion"):
            if key in data and not isinstance(data[key], (dict, list)):
                identity[key] = data[key]
        for key in ("m_InternalIds", "m_ProviderIds", "m_BucketDataString",
                    "m_KeyDataString", "m_EntryDataString", "m_ExtraDataString"):
            value = data.get(key)
            if isinstance(value, list):
                identity[f"{key}_count"] = len(value)
            elif isinstance(value, str):
                identity[f"{key}_base64_bytes"] = len(value)

    plain: list[str] = []
    walk_json(data, plain)

    blobs: list[tuple[str, bytes]] = []
    for text in plain:
        if is_base64_blob(text):
            decoded = decode_blob(text)
            if decoded:
                blobs.append(("base64_section", decoded))

    recovered: list[str] = []
    for _, blob in blobs:
        recovered.extend(scan_strings(blob))

    bundle_names: set[str] = set()
    for text in plain + recovered:
        if classify(text) != "bundle":
            continue
        name = re.split(r"[/\\]", text)[-1]
        if BUNDLE_NAME.match(name):
            bundle_names.add(name)
    bundles = sorted(bundle_names)
    asset_paths = sorted({s for s in plain + recovered if classify(s) == "asset_path"})
    hints = sorted({s for s in plain + recovered if is_text_candidate(s)})

    prefixes = Counter()
    for path in asset_paths + hints:
        parts = re.split(r"[/\\]", path)
        if len(parts) >= 3:
            prefixes["/".join(parts[:3])] += 1

    # adjacency heuristic: which bundle names appear within `context_bytes` of a
    # candidate address in the same decoded blob
    context: dict[str, list[str]] = {}
    for _, blob in blobs:
        decoded_strings = scan_strings(blob)
        positions = []
        offset = 0
        for item in decoded_strings:
            found = blob.find(item.encode("utf-8", errors="ignore"), offset)
            if found < 0:
                found = blob.find(item.encode("utf-8", errors="ignore"))
            positions.append((item, found if found >= 0 else offset))
            offset = max(offset, found + len(item)) if found >= 0 else offset
        for index, (item, position) in enumerate(positions):
            if not is_text_candidate(item):
                continue
            nearby = []
            for other, other_position in positions[max(0, index - 40):index + 40]:
                if classify(other) == "bundle" and abs(other_position - position) <= context_bytes:
                    nearby.append(other)
            if nearby:
                context.setdefault(item, [])
                for name in nearby:
                    if name not in context[item]:
                        context[item].append(name)

    return {
        "schema": SCHEMA,
        "catalog": catalog_path.name,
        "bytes": catalog_path.stat().st_size,
        "top_level_keys": top_level,
        "identity": identity,
        "counts": {
            "json_strings": len(plain),
            "base64_sections": len(blobs),
            "strings_recovered_from_binary": len(recovered),
            "bundles": len(bundles),
            "asset_paths": len(asset_paths),
            "text_hint_addresses": len(hints),
            "text_hint_with_bundle_context": len(context),
        },
        "address_prefixes": dict(prefixes.most_common(40)),
        "candidate_bundles": bundles[:40],
        "candidate_text_addresses": hints,
        "text_address_to_bundle_heuristic": {key: context[key][:5] for key in list(context)[:200]},
        "notes": [
            "The base64 sections are scanned as bytes; the exact Addressables serialiser "
            "version is deliberately not assumed.",
            "text_address_to_bundle_heuristic pairs an address with bundle names seen "
            "within the same decoded section - a hint for the next step, not proof.",
        ],
    }


def summarise(report: dict, print_candidates: int = 0) -> str:
    counts = report["counts"]
    lines = [
        f"catalog        : {report['catalog']} ({report['bytes']:,} B)",
        f"addressables   : {report['identity'].get('m_LocatorId', '?')}",
        f"json strings   : {counts['json_strings']:,}",
        f"base64 sections: {counts['base64_sections']:,} "
        f"({counts['strings_recovered_from_binary']:,} strings recovered)",
        f"bundles        : {counts['bundles']:,}",
        f"asset paths    : {counts['asset_paths']:,}",
        f"text-ish addrs : {counts['text_hint_addresses']:,} "
        f"({counts['text_hint_with_bundle_context']:,} with bundle context)",
    ]
    if report["address_prefixes"]:
        lines.append("")
        lines.append("top address prefixes:")
        for prefix, count in list(report["address_prefixes"].items())[:15]:
            lines.append(f"  {count:>6}  {prefix}")
    if print_candidates:
        lines.append("")
        lines.append(f"first {print_candidates} text-ish addresses:")
        for address in report["candidate_text_addresses"][:print_candidates]:
            bundles = report["text_address_to_bundle_heuristic"].get(address, [])
            tail = f"   -> {bundles[0]}" if bundles else ""
            lines.append(f"  {address}{tail}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--print-candidates", type=int, default=0)
    args = parser.parse_args(argv)

    report = scan(args.catalog)
    print(summarise(report, args.print_candidates))
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(f"\nsummary written: {args.out} ({args.out.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
