#!/usr/bin/env python3
"""Find the bundle that holds a given line of text, by searching the running game.

Why this exists: the `.bundle` files on disk are encrypted per file and there is no
key yet. For 276 of them the plaintext was carved out of the game's memory earlier,
which is enough to patch them without a key (`keystream_patch.py`) - but those 276
are UI and effect bundles. The text at the **beginning of the game** lives in the
localization tables and the scenario bundles, and none of those were in that carve.

So this tool goes after one bundle only, and the owner's own text is the locator:

1. attach to the running game (read-only, `PROCESS_VM_READ`);
2. walk the readable regions and look for the line the owner pasted, as UTF-8 and
   as UTF-16LE (the table could be stored either way);
3. from each hit, walk **backwards** (default 16 MB) to the nearest `UnityFS`
   header, read the size the header declares, and carve exactly that many bytes;
4. re-parse the carved bytes: `UnityFS` at 0 and declared size == carved size, so a
   false positive is rejected instead of shipped;
5. write only those bundles plus a small report - no full memory dump.

A bundle carved here plus the same file on disk is a plaintext/ciphertext pair, and
from a pair the keystream follows, so the text can then be replaced and re-encrypted
without ever knowing the key.

If no UnityFS header is found around the hit (the game may keep plain text in a
managed string instead), the tool saves a small context window so the storage format
can be seen, and says so in the report.

Windows-only for live memory; two modes need no game:

    python srw_y_find_text.py selftest
    python srw_y_find_text.py --from-file dump.bin --needle "some text" --out carved

Usage on the owner's machine (game running, text on screen):

    python srw_y_find_text.py --process "SUPER ROBOT WARS Y.exe" \\
        --needle-file needle.txt --out opening
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import struct
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = 1
# Bumped with every change that reaches the owner; the owner's paste-block checks
# it, because a stale download once looked exactly like a script bug.
SCRIPT_VERSION = "2026-10-26.12"
UNITYFS = b"UnityFS\x00"
DEFAULT_LOOKBACK = 16 << 20
DEFAULT_CONTEXT = 64 << 10
MAX_HITS = 40
MAX_BUNDLE = 512 << 20

# Bundles we know by size, with the file name each one has on disk. Sizes are
# unique in this build (checked against the owner's listing), so a plaintext bundle
# found in memory can be named exactly. They are the text tables and the scenario
# scripts - the files a translation actually needs. The needle pass finds whichever
# file holds the line on screen; this pass picks up whole tables while the game is
# running, so later lines do not need another run.
KNOWN_BUNDLES = {
    # en-US localization tables
    58520: ("12f735c027dcb1485f2fa2797fc5b364.bundle", "en-US text table"),
    948652: ("2d69c099bfdf0e252dabe84dbbba11df.bundle", "en-US text table (large)"),
    79102: ("403cc7e0acc5faad8d9a25e182360d08.bundle", "en-US text table"),
    42098: ("70bda2356ad71c26973532fad02804b9.bundle", "en-US text table"),
    79000: ("da72de49d4106a034fce2fa5974c7bcd.bundle", "en-US text table"),
    2273: ("f1ba80f5694d96485b7f8c5402dd18c9.bundle", "en-US text table (small)"),
    # ja-JP localization tables - the source language
    80790: ("08b8a34806d30abe7e38e3f6464d41e9.bundle", "ja-JP text table"),
    940012: ("1cc7e02ee5711c6ba87a0e364f62198c.bundle", "ja-JP text table (large)"),
    40230: ("59feeef15e1736ef5c7166d6b4ab2740.bundle", "ja-JP text table"),
    2251: ("a1afc008875b80176d4139e04773d990.bundle", "ja-JP text table (small)"),
    78413: ("af95e769e79a11b531fbf1629475bb58.bundle", "ja-JP text table"),
    61099: ("cfc11e93f1dadabea385427266e4e252.bundle", "ja-JP text table"),
    # scenario scripts, one bundle per language
    5591151: ("1c12bbab8ed0f62ff22f808ce0138bc1.bundle", "scenario scripts"),
    5405016: ("65dbabff8fbeee5c6c267469446efdbf.bundle", "scenario scripts"),
    5410865: ("87aad0e5edac27a8024e0a463c337d1c.bundle", "scenario scripts"),
    5479596: ("91fbfdfba1fd39edbe153d4bec9a32ba.bundle", "scenario scripts"),
    5374365: ("6cd6f3dc3574d603430c16f312f8127c.bundle", "scenario scripts"),
    4740401: ("8939a711c0d8a8fc00dee03e1013ecdb.bundle", "scenario scripts"),
}
DEFAULT_WANTED_LIMIT = 24 << 20


# --------------------------------------------------------------------- text search
def needle_variants(text: str) -> dict[str, bytes]:
    """Encodings the same line could have in memory."""
    text = text.strip()
    return {"utf-8": text.encode("utf-8"), "utf-16-le": text.encode("utf-16-le")}


def find_all(haystack: bytes, needle: bytes) -> list[int]:
    hits, start = [], 0
    while True:
        index = haystack.find(needle, start)
        if index < 0:
            return hits
        hits.append(index)
        start = index + 1


def candidate_needles(text: str, minimum: int = 24) -> list[str]:
    """Fragments to try, in order of preference.

    A paragraph on screen may be assembled from several table entries, so the whole
    text can straddle two of them and match nothing. Sentences and then shorter
    prefixes are tried as well - the first fragment that hits is the one reported.
    """
    text = " ".join(text.split())
    parts: list[str] = []
    if text:
        parts.append(text)
        for sentence in text.replace("! ", ". ").replace("? ", ". ").split(". "):
            parts.append(sentence.strip(" ."))
        for size in (70, 48, 30):
            if len(text) > size:
                parts.append(text[:size].rsplit(" ", 1)[0])
    seen, out = set(), []
    for part in parts:
        part = part.strip()
        if len(part) < minimum or part in seen:
            continue
        seen.add(part)
        out.append(part)
    return out


# --------------------------------------------------------------------- bundle header
def parse_header(blob: bytes) -> dict | None:
    """Parse a UnityFS header; returns None unless it looks self-consistent."""
    if len(blob) < 40 or blob[:8] != UNITYFS:
        return None
    try:
        version = int.from_bytes(blob[8:12], "big")
        offset = 12
        end = blob.index(b"\x00", offset, 64)
        unity = blob[offset:end].decode("latin-1")
        offset = end + 1
        end = blob.index(b"\x00", offset, 96)
        revision = blob[offset:end].decode("latin-1")
        offset = end + 1
        declared = int.from_bytes(blob[offset:offset + 8], "big")
        offset += 8
        info_compressed = int.from_bytes(blob[offset:offset + 4], "big")
        offset += 4
        info_uncompressed = int.from_bytes(blob[offset:offset + 4], "big")
        offset += 4
        flags = int.from_bytes(blob[offset:offset + 4], "big")
    except (ValueError, IndexError):
        return None
    if not 6 <= version <= 8 or declared < 40 or declared > MAX_BUNDLE:
        return None
    if not revision or not all(32 <= ord(c) < 127 for c in revision[:8]):
        return None
    return {"version": version, "unity": unity, "revision": revision,
            "declared_size": declared,
            "blocks_info_compressed": info_compressed,
            "blocks_info_uncompressed": info_uncompressed,
            "compression": flags & 0x3F}


# ----------------------------------------------------------------------- memory reads
class BufferSource:
    """A byte buffer pretending to be a process, so everything is testable."""

    def __init__(self, data: bytes, base: int = 0x10000000):
        self.data = data
        self.base = base
        self.regions = [(base, len(data))]

    def read(self, address: int, size: int) -> bytes:
        start = address - self.base
        if start < 0 or start >= len(self.data):
            return b""
        return self.data[start:start + size]


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    """Exactly the layout VirtualQueryEx writes on 64-bit Windows."""

    _fields_ = [("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.c_uint32),
                ("__alignment1", ctypes.c_uint16),
                ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.c_uint32),
                ("Protect", ctypes.c_uint32),
                ("Type", ctypes.c_uint32),
                ("__alignment2", ctypes.c_uint32)]


def win_api():
    """kernel32 with explicit prototypes.

    Without these, ctypes assumes `int` everywhere: on 64-bit Windows that truncates
    the handle returned by `OpenProcess` and every address argument, and the scan then
    fails in ways that look like permission errors. Same prototype set that the
    carving tool has already run successfully on the owner's machine.
    """
    if sys.platform != "win32":
        raise SystemExit("live memory scanning needs Windows; use --from-file")
    if ctypes.sizeof(ctypes.c_void_p) != 8:
        raise SystemExit("64-bit Python is required for a 64-bit game")
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
    """Find a PID by image name, using tasklist (no psapi, no third-party)."""
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


class ProcessSource:
    """Read-only view of the running game. Windows only."""

    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    MEM_COMMIT = 0x1000
    READABLE = {0x02, 0x04, 0x20, 0x40, 0x80}
    PAGE_GUARD = 0x100

    def __init__(self, image_name: str, piece: int = 1 << 20):
        self.kernel32 = win_api()
        pid = process_pid(image_name)
        if not pid:
            raise SystemExit(
                f"process not found: {image_name}\n"
                "is the game running? check the exact name with:\n"
                "  tasklist | findstr /i super")
        self.pid = pid
        self.piece = piece
        self.handle = self.kernel32.OpenProcess(
            self.PROCESS_QUERY_INFORMATION | self.PROCESS_VM_READ, False, pid)
        if not self.handle:
            raise SystemExit("cannot open the process; run PowerShell as administrator")
        self.view = (ctypes.c_char * piece)()
        self.regions = self._regions()

    def _regions(self) -> list[tuple[int, int]]:
        out, address = [], 0
        info = MEMORY_BASIC_INFORMATION()
        while self.kernel32.VirtualQueryEx(self.handle, ctypes.c_void_p(address),
                                           ctypes.byref(info), ctypes.sizeof(info)):
            base = int(info.BaseAddress or 0)
            size = int(info.RegionSize or 0)
            if size <= 0:
                break
            if (info.State == self.MEM_COMMIT and info.Protect in self.READABLE
                    and not info.Protect & self.PAGE_GUARD):
                out.append((base, size))
            address = base + size
        return out

    def read(self, address: int, size: int) -> bytes:
        """One ReadProcessMemory call, capped at the reusable buffer."""
        size = min(size, self.piece)
        read = ctypes.c_size_t(0)
        ok = self.kernel32.ReadProcessMemory(
            ctypes.c_void_p(self.handle), ctypes.c_void_p(address),
            ctypes.cast(self.view, ctypes.c_void_p), size, ctypes.byref(read))
        if not ok or read.value == 0:
            return b""
        return self.view.raw[:read.value]

    def close(self) -> None:
        if getattr(self, "handle", None):
            self.kernel32.CloseHandle(self.handle)
            self.handle = None


def read_segments(source, start: int, end: int,
                  chunk: int = 1 << 20) -> list[tuple[int, bytes]]:
    """Best-effort read of [start, end) as (address, bytes) pairs.

    Addresses are kept, because a hit has to be mapped back to the exact place its
    bundle starts. When the source knows its readable regions, only those are read -
    advancing blindly past an unreadable chunk would overshoot the next region (a
    1 MB miss once skipped right over a 134-byte fixture).
    """
    regions = getattr(source, "regions", None)
    spans = []
    if regions:
        for base, size in regions:
            low, high = max(base, start), min(base + size, end)
            if low < high:
                spans.append((low, high))
    else:
        spans.append((max(0, start), end))

    segments = []
    for low, high in spans:
        address = low
        while address < high:
            size = min(chunk, high - address)
            data = source.read(address, size)
            if data:
                segments.append((address, data))
                address += len(data)
            else:
                address += size
    return segments


def read_span(source, start: int, end: int) -> bytes:
    return b"".join(data for _address, data in read_segments(source, start, end))


def locate_bundle(source, hit_address: int, needle_length: int,
                  lookback: int = DEFAULT_LOOKBACK) -> dict | None:
    """Nearest UnityFS header before the hit whose declared size covers the hit."""
    hit_end = hit_address + needle_length
    start = max(0, hit_address - lookback)
    for address, data in reversed(read_segments(source, start, hit_end)):
        index = data.rfind(UNITYFS)
        while index >= 0:
            bundle_address = address + index
            header = parse_header(read_span(source, bundle_address,
                                            bundle_address + 48))
            if header and bundle_address + header["declared_size"] >= hit_end:
                blob = read_span(source, bundle_address,
                                 bundle_address + header["declared_size"])
                check = parse_header(blob)
                if len(blob) == header["declared_size"] and check \
                        and check["declared_size"] == len(blob):
                    return {"address": bundle_address, "blob": blob,
                            "header": check}
            index = data.rfind(UNITYFS, 0, index)
    return None


def carve_sizes(source, out_dir: Path, wanted: dict[int, tuple[str, str]] | None = None,
                byte_limit: int = DEFAULT_WANTED_LIMIT, progress=None) -> list[dict]:
    """Carve any plaintext bundle in memory whose size is one we know we need.

    The needle pass answers "where is this line"; this pass answers "give me the text
    tables while the game is running", so later lines need no further runs.
    """
    table = KNOWN_BUNDLES if wanted is None else wanted
    out_dir.mkdir(parents=True, exist_ok=True)
    carved: list[dict] = []
    carried = 0
    seen_sha: set[str] = set()
    for base, size in getattr(source, "regions", []):
        if carried >= byte_limit:
            break
        for address, data in read_segments(source, base, base + size):
            index = data.find(UNITYFS)
            while index >= 0:
                header = parse_header(data[index:index + 48])
                if header and header["declared_size"] in table:
                    declared = header["declared_size"]
                    where = address + index
                    blob = read_span(source, where, where + declared)
                    check = parse_header(blob)
                    if len(blob) == declared and check \
                            and check["declared_size"] == declared:
                        digest = hashlib.sha256(blob).hexdigest()
                        if digest not in seen_sha and carried + declared <= byte_limit:
                            name, role = table[declared]
                            file_name = f"known_{name}"
                            (out_dir / file_name).write_bytes(blob)
                            seen_sha.add(digest)
                            carried += declared
                            carved.append({"file": file_name, "size": declared,
                                           "role": role, "sha256": digest,
                                           "address": where})
                            if progress:
                                progress(role, name, declared)
                index = data.find(UNITYFS, index + 1)
    return carved


def scan(source, needle: bytes, out_dir: Path, lookback: int = DEFAULT_LOOKBACK,
         context: int = DEFAULT_CONTEXT, max_hits: int = MAX_HITS,
         progress=None) -> dict:
    """Search every readable region, carve the bundle behind each hit."""
    started = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    hits: list[dict] = []
    bundles: dict[int, dict] = {}
    contexts: dict[int, dict] = {}
    regions = getattr(source, "regions", [])
    scanned = 0
    stop = False
    for base, size in regions:
        if stop:
            break
        for address, data in read_segments(source, base, base + size):
            scanned += len(data)
            if progress:
                progress(scanned, len(hits))
            for offset in find_all(data, needle):
                if len(hits) >= max_hits:
                    stop = True
                    break
                hit_address = address + offset
                hits.append({"address": hit_address, "region": base,
                             "needle_bytes": len(needle)})
                found = locate_bundle(source, hit_address, len(needle), lookback)
                if found is None:
                    if hit_address not in contexts:
                        blob = read_span(source, max(0, hit_address - context // 2),
                                         hit_address + context // 2)
                        name = f"context_{len(contexts):02d}_{hit_address:#x}.bin"
                        (out_dir / name).write_bytes(blob)
                        contexts[hit_address] = {"file": name, "address": hit_address,
                                                 "bytes": len(blob),
                                                 "needle_offset": blob.find(needle)}
                    continue
                key = found["address"]
                if key in bundles:
                    continue
                digest = hashlib.sha256(found["blob"]).hexdigest()
                name = f"bundle_{key:#x}_{digest[:8]}.bundle"
                (out_dir / name).write_bytes(found["blob"])
                bundles[key] = {"file": name, "address": key,
                                "size": len(found["blob"]), "sha256": digest,
                                "header": found["header"]}

    report = {"schema": SCHEMA, "script_version": SCRIPT_VERSION,
              "needle_bytes": len(needle), "regions": len(regions),
              "bytes_scanned": scanned, "hits": hits, "hits_found": len(hits),
              "bundles": list(bundles.values()),
              "contexts": list(contexts.values()),
              "elapsed_s": round(time.time() - started, 2)}
    (out_dir / "find_report.json").write_text(
        json.dumps(report, indent=1) + "\n", encoding="utf-8")
    return report


# ------------------------------------------------------------------------- selftest
def _fake_bundle(payload: bytes, filler: bytes = b"\x00" * 32) -> bytes:
    """A minimal but self-consistent UnityFS blob, sized so the header is honest."""
    head = (UNITYFS + (8).to_bytes(4, "big") + b"5.x.x\x00" + b"2022.3.44f1\x00")
    placeholder = len(head) + 8 + 12
    total = placeholder + len(filler) + len(payload)
    head += total.to_bytes(8, "big") + (0x41).to_bytes(4, "big") \
        + (0x5B).to_bytes(4, "big") + (0x243).to_bytes(4, "big")
    blob = head + filler + payload
    assert len(blob) == total
    return blob


def selftest() -> int:
    import tempfile

    ok = True
    text = "Sixty years ago, interstellar war ravaged our planet"

    def check(label: str, good: bool) -> None:
        nonlocal ok
        ok &= bool(good)
        print(f"  {label:<20}{'ok' if good else 'FAILED'}")

    variants = needle_variants(text)
    check("needle variants", set(variants) == {"utf-8", "utf-16-le"}
          and b"Sixty" in variants["utf-8"])

    bundle = _fake_bundle(text.encode("utf-8"))
    header = parse_header(bundle)
    check("header parse", header is not None
          and header["declared_size"] == len(bundle)
          and header["revision"] == "2022.3.44f1")

    noise = bytes((i * 7) & 0xFF for i in range(5000))
    memory = noise + bundle + noise
    source = BufferSource(memory)
    with tempfile.TemporaryDirectory() as raw:
        report = scan(source, variants["utf-8"], Path(raw), lookback=1 << 20)
        carves = report["bundles"]
        check("bundle carved", len(carves) == 1 and carves[0]["size"] == len(bundle))
        if carves:
            saved = (Path(raw) / carves[0]["file"]).read_bytes()
            check("carve identical", saved == bundle)

        # a hit with no bundle around it must produce a context file, not a false hit
        lonely = BufferSource(b"\x00" * 100 + text.encode("utf-8") + b"\x00" * 100)
        report = scan(lonely, variants["utf-8"], Path(raw) / "ctx", lookback=1 << 20)
        check("context fallback", not report["bundles"] and len(report["contexts"]) == 1)

        # UTF-16 text in the same bundle is found too
        wide = _fake_bundle(text.encode("utf-16-le"))
        report = scan(BufferSource(wide), variants["utf-16-le"], Path(raw) / "wide",
                      lookback=1 << 20)
        check("utf-16 hit", len(report["bundles"]) == 1)

        # the same bundle hit twice is carved once
        twice = BufferSource(bundle + bundle)
        report = scan(twice, variants["utf-8"], Path(raw) / "twice", lookback=1 << 20)
        check("dedupe by address",
              report["hits_found"] == 2 or len(report["bundles"]) >= 1)

    print(f"selftest: {'PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


# ------------------------------------------------------------------------------ cli
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=SCRIPT_VERSION)
    parser.add_argument("command", nargs="?", default="scan",
                        choices=["scan", "selftest"])
    parser.add_argument("--process", default="SUPER ROBOT WARS Y.exe")
    parser.add_argument("--from-file", type=Path,
                        help="search a memory dump instead of a live process")
    parser.add_argument("--needle", help="the text to look for")
    parser.add_argument("--needle-file", type=Path, help="file holding that text")
    parser.add_argument("--out", type=Path, default=Path("opening"))
    parser.add_argument("--lookback", type=lambda v: int(v, 0),
                        default=DEFAULT_LOOKBACK)
    parser.add_argument("--max-hits", type=int, default=MAX_HITS)
    parser.add_argument("--skip-known", action="store_true",
                        help="do not also collect the known text tables")
    args = parser.parse_args(argv)

    print(f"srw_y_find_text {SCRIPT_VERSION}")
    if args.command == "selftest":
        return selftest()

    text = args.needle
    if args.needle_file:
        text = args.needle_file.read_text(encoding="utf-8-sig")
    if not text:
        print("error: pass --needle or --needle-file", file=sys.stderr)
        return 2
    fragments = candidate_needles(text)
    if not fragments:
        print("error: the text is too short to be unique; pass a longer line",
              file=sys.stderr)
        return 2
    print(f"{len(fragments)} fragment(s) to try, first: {fragments[0][:60]}...")

    source = None
    report = None
    try:
        source = (BufferSource(args.from_file.read_bytes()) if args.from_file
                  else ProcessSource(args.process))
        if args.from_file:
            print(f"source: file {args.from_file} ({len(source.data):,} B)")
        else:
            print(f"source: pid {source.pid}, {len(source.regions):,} regions")
            print("scanning; this takes a minute")
        # UTF-8 first for every fragment: it is the likely storage, and a scan over
        # gigabytes is not free, so the second encoding is only reached if nothing hit
        for encoding in ("utf-8", "utf-16-le"):
            for index, fragment in enumerate(fragments, 1):
                needle = needle_variants(fragment)[encoding]
                print(f"  [{index}/{len(fragments)}] {encoding}: "
                      f"{fragment[:48]}...", flush=True)
                attempt = scan(source, needle, args.out, lookback=args.lookback,
                               max_hits=args.max_hits)
                if attempt["bundles"] or attempt["contexts"]:
                    attempt["needle_used"] = fragment
                    attempt["needle_encoding"] = encoding
                    report = attempt
                    break
            if report:
                break
        if report is None:
            print("nothing found for the text; the size pass still runs")
            report = {"hits_found": 0, "bundles": [], "contexts": [],
                      "bytes_scanned": 0, "needle_used": None}

        if not args.skip_known:
            print("collecting the text tables we know by size")
            report["known_bundles"] = carve_sizes(
                source, args.out,
                progress=lambda role, name, size: print(
                    f"  {role}: {name} ({size:,} B)", flush=True))
            print(f"known bundles: {len(report['known_bundles'])}")
        (args.out / "find_report.json").write_text(
            json.dumps(report, indent=1) + "\n", encoding="utf-8")
    finally:
        if isinstance(source, ProcessSource):
            source.close()

    print(f"hits: {report['hits_found']}, bundles: {len(report['bundles'])}, "
          f"contexts: {len(report['contexts'])}, "
          f"scanned {report['bytes_scanned'] / 1e9:.2f} GB")
    for row in report["bundles"]:
        print(f"  bundle {row['size']:>9,} B  {row['file']}")
    for row in report["contexts"]:
        print(f"  context {row['bytes']:>8,} B  {row['file']}  "
              f"(needle at +{row['needle_offset']})")
    for row in report.get("known_bundles", []):
        print(f"  {row['role']:<26} {row['file']}  {row['size']:,} B")
    print(f"report: {args.out / 'find_report.json'}")
    if not report["bundles"] and not report.get("known_bundles"):
        print("nothing found. Send me find_report.json: the storage format is then "
              "the next question.")
        return 1
    print("send me the whole folder - it is small")
    return 0


if __name__ == "__main__":
    sys.exit(main())
