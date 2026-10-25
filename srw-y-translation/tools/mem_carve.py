#!/usr/bin/env python3
"""Carve plaintext asset bundles and text out of the running SRW Y process.

Why this exists: the `.bundle` files on disk are encrypted by the game's own
`SeekableAesStream` (password + salt, see `docs/S2_FINDINGS.md`), and static key
recovery is exhausted at the cheap end. The game itself must decrypt them to run,
so the plaintext exists in its memory. Instead of guessing the key, read the
memory of the running game and take the plaintext that is already there.

What it does, in order:

1. attaches to a process by image name (read-only: `PROCESS_VM_READ` only);
2. walks the committed, readable regions with `VirtualQueryEx`;
3. searches each chunk for `UnityFS` (a whole bundle) and `CAB-` (a serialized
   file inside one), plus a few ASCII markers that name the text assets;
4. for every `UnityFS` hit it parses the bundle header, reads the declared size
   and carves exactly that many bytes, then re-parses the carved bytes to prove
   they are a well-formed bundle;
5. writes a JSON report with **counts and file names only** - no game text, so
   the report can be shared on its own.

The report is the deliverable for the first run. Carved files stay on the
machine until we know whether they are useful.

Windows-only for live memory (`ctypes`, no third-party packages). Two modes need
no game and no Windows:

    python mem_carve.py --selftest                 # proves the script runs here
    python mem_carve.py --from-file dump.bin --out carved

Usage on the owner's machine (game running):

    python mem_carve.py --process "SUPER ROBOT WARS Y.exe" --out carve
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA = 1
SIGNATURE = b"UnityFS\x00"
CAB = b"CAB-"
MARKERS = {
    "unityfs": SIGNATURE,
    "cab": CAB,
    "scenario_name": b"cse20_",
    "localization": b"dialog_text",
    "addressables": b"StandaloneWindows64",
}
UTF16_JAPANESE = None   # compiled lazily; needs `re` only
CHUNK = 8 * 1024 * 1024
OVERLAP = 512   # a UnityFS/CAB header is far shorter than this
MAX_CARVE_BYTES = 256 * 1024 * 1024


# --------------------------------------------------------------- pure helpers


def parse_unityfs(data: bytes) -> dict | None:
    """Parse a UnityFS header. Returns None when `data` is not one.

    Layout (big-endian, Unity 5+): signature[8], version u32, unityVersion cstr,
    unityRevision cstr, size i64, compressedBlocksInfoSize u32,
    uncompressedBlocksInfoSize u32, flags u32.
    """
    if not data.startswith(SIGNATURE) or len(data) < 16:
        return None
    pos = len(SIGNATURE)
    try:
        version = struct.unpack_from(">I", data, pos)[0]
        pos += 4
        values = []
        for _ in range(2):                       # two null-terminated strings
            end = data.find(b"\x00", pos, pos + 256)
            if end < 0:
                return None
            values.append(data[pos:end].decode("latin-1", "replace"))
            pos = end + 1
        size = struct.unpack_from(">q", data, pos)[0]
        pos += 8
        compressed_blocks = struct.unpack_from(">I", data, pos)[0]
        uncompressed_blocks = struct.unpack_from(">I", data, pos + 4)[0]
        flags = struct.unpack_from(">I", data, pos + 8)[0]
    except struct.error:
        return None
    if size <= 0 or size > 1 << 33:
        return None
    return {
        "version": version,
        "unity_version": values[0],
        "unity_revision": values[1],
        "size": size,
        "compressed_blocks_info_size": compressed_blocks,
        "uncompressed_blocks_info_size": uncompressed_blocks,
        "flags": flags,
        "header_size": pos + 12,
    }


def parse_serialized_header(data: bytes) -> dict | None:
    """Parse a `CAB-` serialized file header.

    Layout (big-endian): [metadata_size u32][file_size u32][version u32]
    [data_offset u32], preceded by `CAB-` and a 16-byte hex name.
    """
    if not data.startswith(CAB) or len(data) < 48:
        return None
    try:
        metadata_size, file_size, version, data_offset = struct.unpack_from(">IIII", data, 20)
    except struct.error:
        return None
    if file_size <= 0 or file_size > 1 << 33 or file_size < 48:
        return None
    if metadata_size > file_size or data_offset > file_size:
        return None
    return {"metadata_size": metadata_size, "file_size": file_size,
            "version": version, "data_offset": data_offset,
            "name": data[4:20].decode("latin-1", "replace")}


def find_all(haystack: bytes, needle: bytes, limit: int = 0) -> list[int]:
    hits = []
    start = 0
    while True:
        index = haystack.find(needle, start)
        if index < 0:
            return hits
        hits.append(index)
        if limit and len(hits) >= limit:
            return hits
        start = index + 1


def carve_plan(hits: list[int], size: int, region_base: int,
               budget: int) -> list[dict]:
    """Turn bundle-header hits into carving tasks, skipping overlaps."""
    plan = []
    used = 0
    last_end = -1
    for offset, declared in hits:
        if offset < last_end:
            continue
        if declared <= 0:
            continue
        if used + declared > budget:
            break
        plan.append({"offset": offset, "size": declared,
                     "address": region_base + offset})
        used += declared
        last_end = offset + declared
    return plan


def scan_buffer(buffer: bytes, base: int = 0, marker_limit: int = 0) -> dict:
    """Find markers and UnityFS headers in one buffer (used by both backends)."""
    markers = {name: find_all(buffer, pattern, marker_limit)
               for name, pattern in MARKERS.items()}
    bundles = []
    for offset in markers["unityfs"]:
        header = parse_unityfs(buffer[offset:offset + 512])
        if header:
            bundles.append((offset, header["size"], header))
    serialized = []
    for offset in markers["cab"]:
        header = parse_serialized_header(buffer[offset:offset + 64])
        if header:
            serialized.append((offset, header))
    return {"base": base, "markers": markers, "bundles": bundles,
            "serialized": serialized}


def utf16_japanese_ratio(buffer: bytes) -> float:
    """Fraction of bytes inside UTF-16LE **kana** runs (0.0 - 1.0).

    Kana is the honest signal for Japanese text: U+3040-U+30FF is only 192 code
    units out of 65,536, so four consecutive kana in random bytes happen with
    probability ~1e-10. Kanji is *not* usable this way - U+4E00-U+9FFF is 31 % of
    the BMP, so any random window looks "Japanese" by kanji alone.
    """
    import re
    global UTF16_JAPANESE
    if UTF16_JAPANESE is None:
        # kana and kana punctuation: high byte 0x30, low byte 0x40-0xFF
        UTF16_JAPANESE = re.compile(rb"(?:[\x40-\xff]\x30){4,}")
    matched = sum(len(m.group()) for m in UTF16_JAPANESE.finditer(buffer))
    return matched / len(buffer) if buffer else 0.0


def kana_stats(buffer: bytes) -> dict:
    """How much Japanese (kana) text a buffer holds, without keeping the text."""
    import re
    pattern = re.compile(rb"(?:[\x40-\xff]\x30){4,}")
    runs = [len(m.group()) // 2 for m in pattern.finditer(buffer)]
    return {"runs": len(runs), "chars": sum(runs), "longest": max(runs) if runs else 0}


def buffer_report(buffer: bytes, base: int, marker_limit: int = 0) -> dict:
    scan = scan_buffer(buffer, base, marker_limit)
    return {
        "base": base,
        "bytes": len(buffer),
        "counts": {name: len(hits) for name, hits in scan["markers"].items()},
        "bundles": [{"address": base + offset, "size": size,
                     "unity_version": header["unity_version"],
                     "unity_revision": header["unity_revision"]}
                    for offset, size, header in scan["bundles"]],
        "japanese_ratio": round(utf16_japanese_ratio(buffer), 6),
        "kana": kana_stats(buffer),
        "serialized_files": [{"address": base + offset, "size": header["file_size"],
                              "name": header["name"]}
                             for offset, header in scan.get("serialized", [])],
        "sha256": hashlib.sha256(buffer).hexdigest() if len(buffer) < (64 << 20) else None,
    }


# ------------------------------------------------------------------- backend


def self_test() -> dict:
    """Build a synthetic image with a real bundle header and carve it."""
    header = (SIGNATURE + struct.pack(">I", 7) + b"5.x.x\x00" + b"2021.3.0f1\x00"
              + struct.pack(">q", 4096) + struct.pack(">I", 128)
              + struct.pack(">I", 256) + struct.pack(">I", 0x43))
    bundle = header + b"\x00" * (4096 - len(header))
    image = (b"\x00" * 1000 + bundle + b"\x00" * 500
             + CAB + b"0123456789abcdef" + b"\x00" * 200
             + "\u30c6\u30b9\u30c8".encode("utf-16-le") * 40)
    scan = scan_buffer(image)
    ok = (len(scan["bundles"]) == 1
          and scan["bundles"][0][1] == 4096
          and len(scan["markers"]["cab"]) == 1
          and utf16_japanese_ratio(image) > 0)
    with tempfile.TemporaryDirectory() as raw:
        out = Path(raw)
        carved = carve_from_buffer(image, out)
        ok = ok and carved["written"] and carved["written"][0]["size"] == 4096
        carved_bytes = (out / carved["written"][0]["name"]).read_bytes()
        ok = ok and parse_unityfs(carved_bytes) is not None
    return {"ok": ok, "bundles_found": len(scan["bundles"]),
            "carved": carved["written"], "report": buffer_report(image, 0)}


def carve_from_buffer(buffer: bytes, out_dir: Path,
                      budget: int = MAX_CARVE_BYTES) -> dict:
    """Carve every complete bundle and serialized file in `buffer`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    scan = scan_buffer(buffer)
    hits = [(offset, size) for offset, size, _ in scan["bundles"]]
    hits += [(offset, header["file_size"]) for offset, header in scan["serialized"]]
    hits.sort()
    plan = carve_plan(hits, len(buffer), 0, budget)
    written = []
    for index, task in enumerate(plan):
        offset, size = task["offset"], task["size"]
        data = buffer[offset:offset + size]
        complete = len(data) == size
        is_bundle = parse_unityfs(data) is not None
        if not is_bundle and parse_serialized_header(data) is None:
            continue
        suffix = "bundle" if is_bundle else "assets"
        name = f"{suffix}_{index:03d}_{hashlib.sha256(data).hexdigest()[:8]}.{suffix}"
        (out_dir / name).write_bytes(data)
        written.append({"name": name, "size": len(data), "declared_size": size,
                        "complete": complete, "kind": suffix,
                        "sha256": hashlib.sha256(data).hexdigest()})
    return {"written": written, "planned": len(plan)}


def run_from_file(path: Path, out_dir: Path, budget: int) -> dict:
    buffer = path.read_bytes()
    carved = carve_from_buffer(buffer, out_dir, budget)
    report = buffer_report(buffer, 0)
    report["source"] = {"file": path.name, "bytes": len(buffer)}
    report["carved"] = carved
    return report


# --------------------------------------------------------------- live memory
# Windows API through ctypes. Nothing is written to the target process: access
# is PROCESS_QUERY_INFORMATION | PROCESS_VM_READ only.

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
PAGE_NOACCESS = 0x01
READABLE = (0x02, 0x04, 0x08, 0x20, 0x40, 0x80)   # READONLY..WRITECOMBINE


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.c_uint32),
                ("PartitionId", ctypes.c_uint16),
                ("__alignment1", ctypes.c_uint16),
                ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.c_uint32),
                ("Protect", ctypes.c_uint32),
                ("Type", ctypes.c_uint32),
                ("__alignment2", ctypes.c_uint32)]


def win_api():
    """Load kernel32 with explicit prototypes.

    Without these, ctypes assumes `int` everywhere: on 64-bit Windows that
    truncates the process handle returned by `OpenProcess` and the address
    arguments, and the scan would fail in ways that look like permission errors.
    """
    if sys.platform != "win32":
        raise RuntimeError("live memory scanning needs Windows; use --from-file")
    if ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("a 64-bit Python is required for a 64-bit game; "
                           "install the normal 64-bit build of Python")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel32.CloseHandle.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.VirtualQueryEx.restype = ctypes.c_size_t
    kernel32.VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                        ctypes.POINTER(MEMORY_BASIC_INFORMATION),
                                        ctypes.c_size_t]
    kernel32.ReadProcessMemory.restype = ctypes.c_int
    kernel32.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                           ctypes.c_void_p, ctypes.c_size_t,
                                           ctypes.POINTER(ctypes.c_size_t)]
    return kernel32


def process_pid(image_name: str) -> int | None:
    """Find a PID by image name without third-party modules."""
    result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {image_name}",
                             "/FO", "CSV", "/NH"],
                            capture_output=True, text=True, check=False)
    for line in result.stdout.splitlines():
        parts = [item.strip('"') for item in line.split('","')]
        if len(parts) >= 2 and parts[0].lower() == image_name.lower():
            try:
                return int(parts[1])
            except ValueError:
                continue
    return None


def live_scan(image_name: str, out_dir: Path, budget: int,
              max_scan: int, marker_limit: int = 2000) -> dict:
    if sys.platform != "win32":
        raise RuntimeError("live memory scanning needs Windows; use --from-file")
    pid = process_pid(image_name)
    if pid is None:
        raise RuntimeError(
            f"process not found: {image_name} (is the game running?)\n"
            "if the game window is open, run:  tasklist | findstr /i super")

    kernel32 = win_api()
    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                  False, pid)
    if not handle:
        raise RuntimeError(f"OpenProcess failed (error {ctypes.get_last_error()}); "
                           "try running PowerShell as administrator")

    out_dir.mkdir(parents=True, exist_ok=True)
    totals = {name: 0 for name in MARKERS}
    regions = 0
    scanned = 0
    carved = {"written": [], "planned": 0}
    bundle_sizes = []
    japanese_windows = 0
    kana = {"runs": 0, "chars": 0, "longest": 0}
    address = 0
    mbi = MEMORY_BASIC_INFORMATION()
    try:
        while scanned < max_scan:
            if not kernel32.VirtualQueryEx(handle, ctypes.c_void_p(address),
                                           ctypes.byref(mbi), ctypes.sizeof(mbi)):
                break
            base = mbi.BaseAddress or 0
            size = mbi.RegionSize or 0
            readable = (mbi.State == MEM_COMMIT
                        and mbi.Protect in READABLE
                        and not (mbi.Protect & PAGE_GUARD))
            if readable and size > 0:
                regions += 1
                view = (ctypes.c_char * min(size, CHUNK))()
                offset = 0
                while offset < size and scanned < max_scan:
                    want = min(CHUNK, size - offset)
                    read = ctypes.c_size_t(0)
                    ok = kernel32.ReadProcessMemory(
                        ctypes.c_void_p(handle), ctypes.c_void_p(base + offset),
                        ctypes.cast(view, ctypes.c_void_p), want, ctypes.byref(read))
                    if not ok or read.value == 0:
                        break
                    buffer = bytes(view.raw[:read.value])
                    scan = scan_buffer(buffer, base + offset, marker_limit)
                    for name, hits in scan["markers"].items():
                        totals[name] += len(hits)
                    stats = kana_stats(buffer)
                    kana["runs"] += stats["runs"]
                    kana["chars"] += stats["chars"]
                    kana["longest"] = max(kana["longest"], stats["longest"])
                    if utf16_japanese_ratio(buffer) > 0.01:
                        japanese_windows += 1
                    hits = [(index, declared)
                            for index, declared, _ in scan["bundles"]]
                    hits += [(index, header["file_size"])
                             for index, header in scan["serialized"]]
                    hits.sort()
                    plan = carve_plan(hits, len(buffer), base + offset, budget)
                    for task in plan:
                        data = buffer[task["offset"]:task["offset"] + task["size"]]
                        complete = len(data) == task["size"]
                        if not complete:
                            # a serialized file may span chunks or be block-
                            # decompressed; keep what we have and say so
                            if len(data) < 64:
                                continue
                        is_bundle = parse_unityfs(data) is not None
                        if not is_bundle and parse_serialized_header(data) is None:
                            continue
                        suffix = "bundle" if is_bundle else "assets"
                        name = ("%s_%03d_%s.%s"
                                % (suffix, len(carved["written"]),
                                   hashlib.sha256(data).hexdigest()[:8], suffix))
                        (out_dir / name).write_bytes(data)
                        carved["written"].append({
                            "name": name, "size": len(data), "declared_size": task["size"],
                            "complete": complete, "kind": suffix,
                            "address": task["address"],
                            "sha256": hashlib.sha256(data).hexdigest()})
                        budget -= task["size"]
                        if budget <= 0:
                            break
                    carved["planned"] += len(plan)
                    bundle_sizes.extend(declared for _, declared in hits)
                    scanned += read.value
                    offset += read.value
                    if budget <= 0:
                        break
            next_address = base + size
            if next_address <= address:
                break
            address = next_address
    finally:
        kernel32.CloseHandle(handle)

    return {
        "schema": SCHEMA,
        "mode": "live",
        "process": {"image": image_name, "pid": pid},
        "regions_scanned": regions,
        "bytes_scanned": scanned,
        "counts": totals,
        "bundles_seen": len(bundle_sizes),
        "bundle_sizes": sorted(bundle_sizes, reverse=True)[:50],
        "japanese_windows": japanese_windows,
        "kana": kana,
        "carved": carved,
    }


# ---------------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--process", default="SUPER ROBOT WARS Y.exe")
    parser.add_argument("--out", type=Path, default=Path("srw_y_carve"))
    parser.add_argument("--report", type=Path)
    parser.add_argument("--from-file", type=Path,
                        help="scan a file instead of a process (testing)")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--carve-budget", type=int, default=MAX_CARVE_BYTES)
    parser.add_argument("--max-scan", type=int, default=8 * 1024 ** 3)
    parser.add_argument("--marker-limit", type=int, default=2000)
    args = parser.parse_args(argv)

    try:
        if args.selftest:
            result = self_test()
            print(f"self-test: {'PASS' if result['ok'] else 'FAIL'}")
            print(f"  bundles found in the synthetic image: {result['bundles_found']}")
            print(f"  carved: {result['carved']}")
            return 0 if result["ok"] else 1
        if args.from_file:
            if not args.from_file.is_file():
                print(f"error: not a file: {args.from_file}", file=sys.stderr)
                return 2
            result = run_from_file(args.from_file, args.out, args.carve_budget)
        else:
            result = live_scan(args.process, args.out, args.carve_budget,
                               args.max_scan, args.marker_limit)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    counts = result.get("counts", {})
    print(f"markers: {counts}")
    if result.get("bundles_seen") is not None:
        print(f"bundles seen: {result['bundles_seen']} "
              f"(sizes: {result.get('bundle_sizes', [])[:5]})")
    carved = result.get("carved", {})
    print(f"carved files: {len(carved.get('written', []))}")
    for item in carved.get("written", [])[:10]:
        print(f"  {item['name']}  {item['size']:,} B  {item['sha256'][:16]}")
    if result.get("kana"):
        kana = result["kana"]
        print(f"kana runs: {kana['runs']:,} ({kana['chars']:,} chars, "
              f"longest {kana['longest']})")
    if result.get("japanese_windows") is not None:
        print(f"windows with Japanese UTF-16 text: {result['japanese_windows']}")
    if result.get("bytes_scanned") is not None:
        print(f"scanned {result['bytes_scanned']:,} B in {result['regions_scanned']} regions")

    target = args.report or (args.out / "carve_report.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(f"report: {target} ({target.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
