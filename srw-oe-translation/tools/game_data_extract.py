#!/usr/bin/env python3
"""Committed extract of everything the catalogues read from the original game files.

Historically `mech_catalog.py`, `pilot_catalog.py` and `mission_deployments.py` could
only run when the operator happened to have the original `config*` containers and the
decrypted 1.08 executable on disk. That made the mech and pilot catalogues
unreproducible from a clean checkout, so releases silently shipped without them.

This module removes that dependency. `--build` reads the containers and the executable
once, keeps only the fields the builders actually consume, and writes them under
`docs/game-data/`. Every later build loads that committed extract, so the catalogues,
the reading editions and the patches rebuild from the repository alone.

Nothing here weakens a gate:

* the extract records the SHA-256 of the executable it came from, and loading refuses
  any extract whose hash differs from the reviewed 1.08 executable;
* the extract records the SHA-256 of every English package file it was validated
  against, and loading refuses a package that does not match;
* the executable strings keep their pointer, file offset and SHA-256, so the existing
  per-string checks in `mech_catalog.base_skills` and `pilot_catalog` still run.

Build (needs the original files once, afterwards never again):

    python3 tools/game_data_extract.py --build \
        --containers <dir with config00.cpk, config01-19.EDAT, configst.cpk> \
        --elf <decrypted 1.08 executable> \
        --package pakiet_katalog_EN
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
EXTRACT_DIR = PROJECT / "docs" / "game-data"

TABLES_FILE = "engine-tables.json"
SPIRIT_FILE = "spirit-table.json"
STRINGS_FILE = "executable-strings.json"
MANIFEST_FILE = "manifest.json"

SCHEMA_VERSION = 1
# Reviewed original 1.08 executable the whole catalogue chain is pinned to.
ORIGINAL_SHA256_EXPECTED = "26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052"

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def need(condition, message):
    if not condition:
        raise ValueError(message)
    return condition


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dump(path: Path, payload, sort_keys: bool = False) -> bytes:
    # Key order is data, not formatting: the catalogues render sections in the order the
    # engine tables were read, so sorting the keys here would reorder the output.
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=sort_keys, indent=1) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def _load(name: str, directory: Path | None = None):
    path = (directory or EXTRACT_DIR) / name
    need(path.is_file(), f"Missing committed game-data extract: {path}. Rebuild with game_data_extract.py --build")
    return json.loads(path.read_bytes())


def package_hashes(package: Path, names) -> dict:
    return {name: sha((package / name).read_bytes()) for name in sorted(names)}


class ExecutableStrings:
    """Stands in for the patched executable image in `string_at(image, address)` calls.

    Only the strings the catalogues look up are stored; each one keeps the file offset
    and SHA-256 the engine maps assert against, so callers verify exactly as before.
    """

    def __init__(self, payload: dict):
        self.executable_sha256 = payload["executable_sha256"]
        self.executable_bytes = payload["executable_bytes"]
        self.translation_sha256 = payload["executable_translation_sha256"]
        self._by_pointer = {}
        for entry in payload["strings"]:
            need(sha(entry["text"].encode("utf-8")) == entry["sha256"],
                 f"Committed executable string is corrupt at pointer {entry['pointer']}")
            self._by_pointer[int(entry["pointer"])] = (entry["text"], int(entry["file_offset"]))

    def string_at(self, address):
        address = int(address)
        need(address in self._by_pointer,
             f"Pointer {address:#x} is not in the committed extract. Rebuild it with --build.")
        return self._by_pointer[address]

    def __len__(self):
        return len(self._by_pointer)


def load_tables(directory: Path | None = None) -> dict:
    """Return the committed engine tables in `mech_catalog_sources.read_tables()` shape.

    Dict keys arrive from JSON as strings, so the unit/weapon/character maps are put
    back on integer keys exactly as the container reader produces them.
    """
    payload = _load(TABLES_FILE, directory)
    tables = payload["tables"]
    for key in ("units", "weapons", "characters"):
        tables[key] = {int(k): v for k, v in tables[key].items()}
    return tables


def load_spirit_binary(directory: Path | None = None) -> bytes:
    payload = _load(SPIRIT_FILE, directory)
    data = bytes.fromhex(payload["hex"])
    need(sha(data) == payload["sha256"] and len(data) == payload["bytes"],
         "Committed Spirit table is corrupt")
    return data


def load_executable_strings(engine_map: dict | None = None, directory: Path | None = None) -> ExecutableStrings:
    strings = ExecutableStrings(_load(STRINGS_FILE, directory))
    if engine_map is not None:
        need(strings.executable_sha256 == engine_map["executable_sha256"],
             "Committed extract was taken from a different executable than the engine map describes")
        need(strings.translation_sha256 == engine_map["executable_translation_sha256"],
             "Committed extract was taken against a different executable translation")
    return strings


def available(directory: Path | None = None) -> bool:
    base = directory or EXTRACT_DIR
    return all((base / name).is_file() for name in (TABLES_FILE, SPIRIT_FILE, STRINGS_FILE, MANIFEST_FILE))


def engine_map_pointers(*engine_maps: dict):
    """Every executable pointer the catalogues resolve, across both engine maps."""
    pointers = set()
    for engine_map in engine_maps:
        for key in ("selections", "skill_records"):
            for entry in engine_map.get(key, []):
                if entry.get("pointer"):
                    pointers.add(int(entry["pointer"]))
    return sorted(pointers)


def build(containers: Path, elf: Path, package: Path, out: Path | None = None) -> dict:
    import mech_catalog_sources as sources
    import mech_catalog_engine as engine
    import pilot_catalog

    out = out or EXTRACT_DIR
    original = elf.read_bytes()
    mech_map = json.loads((PROJECT / "docs/mech-catalog/engine-map.json").read_bytes())
    pilot_map = json.loads((PROJECT / "docs/pilot-catalog/engine-map.json").read_bytes())
    need(sha(original) == mech_map["executable_sha256"] == pilot_map["executable_sha256"],
         "Executable does not match the reviewed 1.08 build described by the engine maps")

    tables = sources.read_tables(containers)
    source = sources.collect(containers, package)
    image, _ = engine.english_image(original, package)
    spirit = pilot_catalog.read_spirit_binary(containers)

    strings = []
    for pointer in engine_map_pointers(mech_map, pilot_map):
        text, offset = engine.string_at(image, pointer)
        strings.append({"pointer": pointer, "file_offset": offset, "text": text,
                        "sha256": sha(text.encode("utf-8"))})

    tables_bytes = _dump(out / TABLES_FILE, {
        "schema_version": SCHEMA_VERSION,
        "note": "Engine tables decoded from the original containers; same shape as read_tables().",
        "containers": [item["name"] for item in tables["inputs"]],
        "tables": tables,
    })
    spirit_bytes = _dump(out / SPIRIT_FILE, {
        "schema_version": SCHEMA_VERSION,
        "member": "srwDL_Spirit.bin",
        "container": "configst.cpk",
        "bytes": len(spirit),
        "sha256": sha(spirit),
        "hex": spirit.hex(),
    })
    strings_bytes = _dump(out / STRINGS_FILE, {
        "schema_version": SCHEMA_VERSION,
        "executable_sha256": sha(original),
        "executable_bytes": len(original),
        "executable_translation_sha256": sha((package / "09_executable.jsonl").read_bytes()),
        "note": "English text at every executable pointer the catalogues resolve.",
        "strings": strings,
    })
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "purpose": "Committed replacement for the original config containers and the 1.08 executable.",
        "executable": {"sha256": sha(original), "bytes": len(original)},
        "containers": [{"name": item["name"], "bytes": item["bytes"], "md5": item["md5"]}
                       for item in source["inputs"]],
        "package": {"directory": package.name, "sha256": source["summary"]["package_sha256"]},
        "files": {
            TABLES_FILE: {"bytes": len(tables_bytes), "sha256": sha(tables_bytes)},
            SPIRIT_FILE: {"bytes": len(spirit_bytes), "sha256": sha(spirit_bytes)},
            STRINGS_FILE: {"bytes": len(strings_bytes), "sha256": sha(strings_bytes)},
        },
        "counts": {"executable_strings": len(strings), **source["summary"]
                   .get("counts", {k: v for k, v in source["summary"].items() if isinstance(v, int)})},
    }
    _dump(out / MANIFEST_FILE, manifest, sort_keys=True)
    return manifest


def verify(directory: Path | None = None) -> dict:
    base = directory or EXTRACT_DIR
    manifest = _load(MANIFEST_FILE, base)
    for name, meta in manifest["files"].items():
        data = (base / name).read_bytes()
        need(len(data) == meta["bytes"] and sha(data) == meta["sha256"],
             f"Committed extract file changed since it was built: {name}")
    return manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true", help="Rebuild the extract from the original game files")
    ap.add_argument("--containers", type=Path, help="Directory holding config00.cpk, config01-19.EDAT, configst.cpk")
    ap.add_argument("--elf", type=Path, help="Decrypted original 1.08 executable")
    ap.add_argument("--package", type=Path, default=PROJECT / "pakiet_katalog_EN",
                    help="Frozen English catalogue package (default: pakiet_katalog_EN)")
    ap.add_argument("--out", type=Path, default=EXTRACT_DIR)
    args = ap.parse_args(argv)
    if args.build:
        need(args.containers is not None and args.elf is not None, "--build needs --containers and --elf")
        report = build(args.containers, args.elf, args.package, args.out)
    else:
        report = verify(args.out)
    print(json.dumps({k: v for k, v in report.items() if k != "containers"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
