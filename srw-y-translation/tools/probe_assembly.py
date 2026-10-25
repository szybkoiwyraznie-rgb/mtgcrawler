#!/usr/bin/env python3
"""Look for the bundle key inside the game's native binary.

SRW Y is IL2CPP: the managed code is compiled ahead of time into
`GameAssembly.dll`, so a key that a developer wrote as a `byte[]` lives in that
binary, not in `global-metadata.dat` (which holds only names and string
literals). A sweep over every string literal in the metadata found nothing, so
this tool goes one level down:

1. parse the PE headers and print the section table (so `.rdata` can be
   identified instead of guessing);
2. report where the interesting names appear — the custom provider class, and
   crypto identifiers (`AES`, `Rijndael`, `CreateDecryptor`, `SHA256`, …) — which
   says whether the protection is AES at all and roughly where the code is;
3. hand every 16/24/32-byte window of the data sections to `keyhunt`, aligned or
   every byte, and see whether any of them decrypts a real bundle to `UnityFS`.

Step 3 is a long shot and it is presented as one: a key built at runtime from
several constants will not be found this way. But it is bounded, it is offline,
and a hit would be proof.

Pure Python, no dependencies. `tools/keyhunt.py` supplies the ciphers; the AES
there prefers `pycryptodome` when installed, which is what makes the sweep
practical.

Usage:
    python3 tools/probe_assembly.py --dll GameAssembly.dll \
        --bundle local/bundles/x.bundle --alignment 16 --out report.json
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import keyhunt as K  # noqa: E402

SCHEMA = 1
KEYWORDS = (
    "CustomAssetBundleProvider", "AssetBundleProvider", "AssetBundle",
    "AES", "Rijndael", "CreateDecryptor", "CreateEncryptor", "CipherMode",
    "SHA256", "SHA1", "MD5", "Rfc2898", "PasswordDeriveBytes", "RijndaelManaged",
    "AesManaged", "AesCryptoServiceProvider", "XOR", "Decrypt", "Encrypt",
    "UnityFS", "CAB-", "il2cpp",
)
MACHINES = {0x8664: "x86-64", 0x14C: "x86", 0xAA64: "ARM64"}


class PeError(ValueError):
    """The file is not a PE image."""


def parse_pe(data: bytes) -> dict:
    """Return the machine, the image base and the section table."""
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise PeError("no MZ header")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        raise PeError("no PE signature")
    coff = e_lfanew + 4
    machine, section_count = struct.unpack_from("<HH", data, coff)
    size_of_optional = struct.unpack_from("<H", data, coff + 16)[0]
    optional = coff + 20
    magic = struct.unpack_from("<H", data, optional)[0]
    image_base = (struct.unpack_from("<Q", data, optional + 24)[0]
                  if magic == 0x20B else struct.unpack_from("<I", data, optional + 28)[0])
    sections = []
    table = optional + size_of_optional
    for index in range(section_count):
        offset = table + index * 40
        if offset + 40 > len(data):
            raise PeError("section table runs past the end of the file")
        name = data[offset:offset + 8].rstrip(b"\x00").decode("latin-1")
        v_size, v_addr, raw_size, raw_ptr = struct.unpack_from("<IIII", data, offset + 8)
        flags = struct.unpack_from("<I", data, offset + 36)[0]
        sections.append({
            "name": name,
            "virtual_address": v_addr,
            "virtual_size": v_size,
            "raw_offset": raw_ptr,
            "raw_size": raw_size,
            "executable": bool(flags & 0x20000000),
            "readable": bool(flags & 0x40000000),
            "writable": bool(flags & 0x80000000),
        })
    return {
        "machine": MACHINES.get(machine, f"0x{machine:04x}"),
        "image_base": image_base,
        "optional_magic": f"0x{magic:04x}",
        "sections": sections,
    }


def section_bytes(data: bytes, section: dict) -> bytes:
    start = section["raw_offset"]
    return data[start:start + section["raw_size"]]


def find_keywords(data: bytes, limit: int = 8) -> dict[str, list[int]]:
    """Byte offsets of interesting names. ASCII and UTF-16LE are both searched."""
    found: dict[str, list[int]] = {}
    for word in KEYWORDS:
        hits: list[int] = []
        for encoded in (word.encode("ascii"), word.encode("utf-16-le")):
            start = 0
            while len(hits) < limit:
                index = data.find(encoded, start)
                if index < 0:
                    break
                hits.append(index)
                start = index + 1
        if hits:
            found[word] = sorted(hits)[:limit]
    return found


def candidate_windows(blob: bytes, alignment: int) -> list[bytes]:
    """Unique 16/24/32-byte windows at the given alignment."""
    seen: set[bytes] = set()
    out: list[bytes] = []
    for size in K.KEY_SIZES:
        for start in range(0, len(blob) - size + 1, alignment):
            window = blob[start:start + size]
            if window in seen:
                continue
            seen.add(window)
            out.append(window)
    return out


def scan(dll: Path, bundles: list[Path], alignment: int = 16,
         max_candidates: int = 0, include_all: bool = False) -> dict:
    if not dll.is_file():
        raise PeError(f"not a file: {dll}")
    data = dll.read_bytes()
    pe = parse_pe(data)
    for bundle in bundles:
        if not bundle.is_file():
            raise PeError(f"not a file: {bundle}")

    samples = [(bundle.name, bundle.read_bytes()[:512]) for bundle in bundles]

    report = {
        "schema": SCHEMA,
        "dll": {"name": dll.name, "bytes": len(data), **pe},
        "keyword_hits": find_keywords(data),
        "candidates": {},
        "hit": None,
    }

    # data sections first: keys are constants, not code
    chosen = [s for s in pe["sections"] if s["readable"] and not s["executable"]]
    if include_all or not chosen:
        chosen = pe["sections"]
    candidates: list[bytes] = []
    for section in chosen:
        blob = section_bytes(data, section)
        candidates += candidate_windows(blob, alignment)
        report["candidates"][section["name"]] = len(candidates)
        if max_candidates and len(candidates) >= max_candidates:
            break
    candidates = list(dict.fromkeys(candidates))
    if max_candidates:
        candidates = candidates[:max_candidates]
    report["candidates"]["total"] = len(candidates)
    report["candidates"]["alignment"] = alignment
    report["candidates"]["sections_scanned"] = [s["name"] for s in chosen]

    for key in candidates:
        for name, sample in samples:
            schemes = K.matches(key, sample)
            if schemes:
                report["hit"] = {"key_hex": key.hex(), "bundle": name, "schemes": schemes}
                return report
    return report


def summarise(report: dict) -> str:
    dll = report["dll"]
    lines = [f"{dll['name']}: {dll['bytes']:,} B, {dll['machine']}, "
             f"image base 0x{dll['image_base']:x}"]
    for section in dll["sections"]:
        flag = "X" if section["executable"] else " "
        lines.append(f"  {section['name']:8} va 0x{section['virtual_address']:08x} "
                     f"raw {section['raw_size']:>10,}  {flag}")
    lines.append("")
    if report["keyword_hits"]:
        lines.append("keyword hits (file offsets):")
        for word, hits in report["keyword_hits"].items():
            lines.append(f"  {word:28} {hits[:4]}")
    else:
        lines.append("keyword hits: none — no crypto or provider names found")
    candidates = report["candidates"]
    if "total" in candidates:
        lines.append("")
        lines.append(f"candidates tried: {candidates['total']:,} "
                     f"(alignment {candidates['alignment']}, "
                     f"sections {', '.join(candidates['sections_scanned'])})")
    if report["hit"]:
        lines.append(f"HIT: {report['hit']}")
    elif "total" in candidates:
        lines.append("no key found among those windows")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dll", required=True, type=Path)
    parser.add_argument("--bundle", required=True, nargs="+", type=Path)
    parser.add_argument("--alignment", type=int, default=16)
    parser.add_argument("--max-candidates", type=int, default=0)
    parser.add_argument("--all-sections", action="store_true")
    parser.add_argument("--no-sweep", action="store_true",
                        help="print headers and keywords only")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.no_sweep:
            data = args.dll.read_bytes()
            report = {
                "schema": SCHEMA,
                "dll": {"name": args.dll.name, "bytes": len(data), **parse_pe(data)},
                "keyword_hits": find_keywords(data),
                "candidates": {},
                "hit": None,
            }
        else:
            report = scan(args.dll, args.bundle, args.alignment,
                          args.max_candidates, args.all_sections)
    except PeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(summarise(report))
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(f"\nreport written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
