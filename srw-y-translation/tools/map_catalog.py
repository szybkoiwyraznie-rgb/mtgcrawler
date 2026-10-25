#!/usr/bin/env python3
"""Map Addressables addresses to their bundles, from a Unity Addressables catalogue.

The catalogue (`StreamingAssets/aa/catalog.json`) is the only index of what the
content-hash-named `.bundle` files contain. It is a JSON object whose four
`m_*String` fields are base64-encoded binary sections:

===============  ===========================================================
section          contents
===============  ===========================================================
m_KeyDataString  key records: ``[type:u8][len:i32][payload]``; type 0 is a
                 UTF-8 string, type 1 a UTF-16LE string, other types are
                 opaque and are reported but never guessed at
m_BucketDataString  one record per key: ``[keyOffset:i32][count:i32][entry*]``
m_EntryDataString   ``[count:i32]`` then ``count`` records of 7 int32:
                 internalId, providerIndex, dependencyKeyIndex, depHash,
                 dataIndex, primaryKey, resourceType
m_ExtraDataString   provider-specific extra data (not needed here)
===============  ===========================================================

A key that names a bundle (32 hex chars) is served by an AssetBundle provider
and its ``internalId`` is the bundle path. Any other key names an asset inside a
bundle: its ``dependencyKeyIndex`` points at the bundle's key, which is how the
bundle is found. That two-step resolution is what this tool implements.

Being wrong here is easy, so the tool also *validates*: every bundle it resolves
must exist in a supplied file listing, and the report says how many keys failed
to resolve. Nothing is guessed silently.

Usage:
    python3 tools/map_catalog.py --catalog catalog.json --out mapping.json
    python3 tools/map_catalog.py --catalog catalog.json --listing listing_sizes.txt \\
        --print-group Localization --print-group Scenario
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

SCHEMA = 1
BUNDLE_KEY = re.compile(r"^[0-9a-f]{32}$")
LOCALE = re.compile(r"_(ja-JP|en-US|ko-KR|zh-CN|zh-HK|zh-TW)$")
ENTRY_FIELDS = ("internal_id", "provider", "dependency_key", "dependency_hash",
                "data_index", "primary_key", "resource_type")
BUNDLE_PROVIDERS = (0, 1)   # CriResourceProvider, CustomAssetBundleProvider


class CatalogError(ValueError):
    """The catalogue does not look like an Addressables catalogue."""


def _b64(data: dict, name: str) -> bytes:
    value = data.get(name)
    if not isinstance(value, str):
        raise CatalogError(f"missing section {name}")
    try:
        return base64.b64decode(value, validate=False)
    except (binascii.Error, ValueError) as error:
        raise CatalogError(f"{name}: not base64 ({error})") from error


def parse_keys(blob: bytes, offsets: list[int]) -> dict[int, dict]:
    """Decode one key record per bucket offset.

    Boundaries come from the bucket section rather than from sequential parsing:
    opaque key types have no length field this tool understands, and a single
    mis-read record would desynchronise every later key.
    """
    keys: dict[int, dict] = {}
    bounds = offsets + [len(blob)]
    for start, end in zip(bounds, bounds[1:]):
        if start >= len(blob):
            continue
        kind = blob[start]
        payload = blob[start + 1:end] if kind not in (0, 1) else blob[start + 5:end]
        if kind == 0:
            text = payload.decode("utf-8", "replace")
        elif kind == 1:
            text = payload.decode("utf-16-le", "replace")
        else:
            text = ""
        keys[start] = {"type": kind, "text": text}
    return keys


def parse_buckets(blob: bytes) -> list[tuple[int, tuple[int, ...]]]:
    """``[count][ (keyOffset, entryIndices... ) ]`` — order is the key order."""
    if len(blob) < 4:
        raise CatalogError("m_BucketDataString is too short")
    count = struct.unpack_from("<i", blob, 0)[0]
    offset = 4
    buckets: list[tuple[int, tuple[int, ...]]] = []
    while offset < len(blob):
        key_offset, size = struct.unpack_from("<ii", blob, offset)
        entries = struct.unpack_from("<%di" % size, blob, offset + 8)
        buckets.append((key_offset, entries))
        offset += 8 + 4 * size
    if len(buckets) != count:
        raise CatalogError(f"bucket section holds {len(buckets)} records, header says {count}")
    return buckets


def parse_entries(blob: bytes) -> list[dict]:
    if len(blob) < 4:
        raise CatalogError("m_EntryDataString is too short")
    count = struct.unpack_from("<i", blob, 0)[0]
    size = 4 * len(ENTRY_FIELDS)
    if (len(blob) - 4) != count * size:
        raise CatalogError(
            f"entry section is {len(blob) - 4} bytes, expected {count} x {size}")
    return [dict(zip(ENTRY_FIELDS, struct.unpack_from("<%di" % len(ENTRY_FIELDS),
                                                      blob, 4 + index * size)))
            for index in range(count)]


def bundle_name(internal_id: str) -> str:
    """Last path component, with either separator — provider paths use '\\\\'."""
    return internal_id.replace("\\", "/").rstrip("/").split("/")[-1]


def load_catalog(catalog_path: Path) -> dict:
    if not catalog_path.is_file():
        raise CatalogError(f"not a file: {catalog_path}")
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as error:
        raise CatalogError(f"not JSON ({error})") from error
    for field in ("m_KeyDataString", "m_BucketDataString", "m_EntryDataString",
                  "m_InternalIds", "m_ProviderIds"):
        if field not in data:
            raise CatalogError(f"missing {field} — not an Addressables catalogue?")
    return data


class Catalog:
    """Parsed catalogue with address -> bundle resolution."""

    def __init__(self, data: dict):
        self.data = data
        self.internal_ids: list[str] = list(data["m_InternalIds"])
        self.providers: list[str] = list(data["m_ProviderIds"])
        self.buckets = parse_buckets(_b64(data, "m_BucketDataString"))
        self.entries = parse_entries(_b64(data, "m_EntryDataString"))
        self.key_offsets = [key_offset for key_offset, _ in self.buckets]
        self.keys = parse_keys(_b64(data, "m_KeyDataString"), self.key_offsets)
        self.addresses = [self.keys[offset]["text"] for offset in self.key_offsets]
        self.by_address: dict[str, int] = {}
        for index, address in enumerate(self.addresses):
            self.by_address.setdefault(address, index)

    def first_entry(self, key_index: int) -> int:
        return self.buckets[key_index][1][0]

    def entry(self, key_index: int) -> dict:
        return self.entries[self.first_entry(key_index)]

    def bundle_for(self, key_index: int) -> str | None:
        """Bundle file name serving this key, or None if it cannot be resolved."""
        entry = self.entry(key_index)
        candidates = [key_index]
        dependency = entry["dependency_key"]
        if 0 <= dependency < len(self.addresses):
            candidates.append(dependency)
        for candidate in candidates:
            candidate_entry = self.entry(candidate)
            if candidate_entry["provider"] not in BUNDLE_PROVIDERS:
                continue
            index = candidate_entry["internal_id"]
            if 0 <= index < len(self.internal_ids):
                return bundle_name(self.internal_ids[index])
        return None

    def groups(self) -> dict[str, list[str]]:
        """Coarse grouping of the addresses, purely by their name."""
        groups: dict[str, list[str]] = {}
        for address in self.addresses:
            if BUNDLE_KEY.match(address) or not address:
                name = "bundle_key"
            elif address.startswith("Assets/Datas/Scenario"):
                name = "scenario_script"
            elif "Localization/" in address or LOCALE.search(address):
                name = "localization"
            elif address.startswith("Assets/"):
                name = "asset:" + "/".join(address.split("/")[1:3])
            else:
                name = "other"
            groups.setdefault(name, []).append(address)
        return groups


def read_listing(listing_path: Path) -> dict[str, int]:
    """``size<TAB>path`` per line; also tolerates the owner's truncated prefix."""
    sizes: dict[str, int] = {}
    for line in listing_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        sizes[parts[1].replace("\\", "/").split("/")[-1]] = int(parts[0])
    return sizes


def report(catalog: Catalog, sizes: dict[str, int] | None) -> dict:
    bundles = Counter()
    unresolved = []
    for index, address in enumerate(catalog.addresses):
        if BUNDLE_KEY.match(address):
            continue
        name = catalog.bundle_for(index)
        if name is None:
            unresolved.append(address)
        else:
            bundles[name] += 1

    missing = []
    if sizes is not None:
        missing = sorted(name for name in bundles if name not in sizes)

    localization: dict[str, dict] = {}
    for index, address in enumerate(catalog.addresses):
        match = LOCALE.search(address)
        if not match or "Localization/" in address:
            continue
        name = catalog.bundle_for(index)
        record = localization.setdefault(match.group(1), {"addresses": 0, "bundles": {}})
        record["addresses"] += 1
        if name:
            record["bundles"][name] = sizes.get(name) if sizes else None

    scenarios = Counter()
    for index, address in enumerate(catalog.addresses):
        if address.startswith("Assets/Datas/Scenario"):
            name = catalog.bundle_for(index)
            if name:
                scenarios[name] += 1

    return {
        "schema": SCHEMA,
        "locator_id": catalog.data.get("m_LocatorId"),
        "build_hash": catalog.data.get("m_BuildResultHash"),
        "providers": catalog.providers,
        "counts": {
            "addresses": len(catalog.addresses),
            "keys_without_text": sum(1 for k in catalog.keys.values() if not k["text"]),
            "entries": len(catalog.entries),
            "internal_ids": len(catalog.internal_ids),
            "bundle_keys": sum(1 for a in catalog.addresses if BUNDLE_KEY.match(a)),
            "assets_in_bundles": sum(bundles.values()),
            "distinct_bundles": len(bundles),
            "unresolved": len(unresolved),
        },
        "bundles_by_address_count": bundles.most_common(50),
        "localization_by_locale": localization,
        "scenario_bundles": scenarios.most_common(30),
        "scenario_address_count": sum(scenarios.values()),
        "unresolved_sample": unresolved[:30],
        "bundles_missing_from_listing": missing[:30],
        "validated_against_listing": sizes is not None,
    }


def summarise(result: dict) -> str:
    counts = result["counts"]
    lines = [
        f"locator        : {result['locator_id']}  (build {result['build_hash']})",
        f"addresses      : {counts['addresses']:,}  "
        f"({counts['bundle_keys']:,} bundle keys, "
        f"{counts['assets_in_bundles']:,} assets resolved)",
        f"entries        : {counts['entries']:,}   "
        f"internal ids: {counts['internal_ids']:,}",
        f"distinct bundles serving assets: {counts['distinct_bundles']:,}",
        f"unresolved     : {counts['unresolved']:,}",
    ]
    if result["validated_against_listing"]:
        lines.append("validation     : "
                     + ("all resolved bundles exist in the listing"
                        if not result["bundles_missing_from_listing"]
                        else f"{len(result['bundles_missing_from_listing'])} bundles "
                             "MISSING from the listing (!)"))
    lines.append("")
    lines.append("localization tables per locale:")
    for locale, record in sorted(result["localization_by_locale"].items()):
        bundles = ", ".join(f"{name} ({size:,} B)" if size else name
                            for name, size in sorted(record["bundles"].items()))
        lines.append(f"  {locale:6} {record['addresses']:4} addresses -> {bundles}")
    lines.append("")
    lines.append(f"scenario scripts: {result['scenario_address_count']:,} addresses "
                 f"in {len(result['scenario_bundles'])} bundles")
    for name, count in result["scenario_bundles"][:8]:
        lines.append(f"  {count:5} addresses  {name}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--listing", type=Path,
                        help="owner's size<TAB>path listing, for validation and sizes")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    try:
        catalog = Catalog(load_catalog(args.catalog))
        sizes = read_listing(args.listing) if args.listing else None
    except CatalogError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    result = report(catalog, sizes)
    print(summarise(result))
    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(f"\nreport written: {args.out} ({args.out.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
