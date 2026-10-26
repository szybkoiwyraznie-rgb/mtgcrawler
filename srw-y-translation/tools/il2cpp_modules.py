#!/usr/bin/env python3
"""Find IL2CPP's per-assembly method tables in `GameAssembly.dll`.

Why this is the next step for SRW Y: the bundle password is not any string in
`global-metadata.dat` or in the binary (428,538 literals tested against every cheap
key derivation and counter layout - see `key_matrix.py`), so it is either built at
runtime or stored as binary data. Either way it is only visible in the code, and to
read the code you first have to turn a *method* into an address.

IL2CPP leaves exactly one hook for that, and it does not need a full dumper. Each
managed assembly gets an `Il2CppCodeGenModule` record in `.rdata`:

    struct Il2CppCodeGenModule {          // 8-byte aligned, x64
        const char* moduleName;           // "Assembly-CSharp.dll"
        uint32_t    methodPointerCount;
        uint64_t    methodPointers;       // array of RVAs into the il2cpp section
        uint32_t    adjustorThunkCount;
        uint64_t    adjustorThunks;
        uint64_t    invokerIndices;
        ...
    };

so the record is found by looking for a pointer to the module-name string, and the
method addresses follow from it. The order of that array is the order IL2CPP emitted
the methods, which is the order of the assembly's method definitions in
`global-metadata.dat` - that is what turns an index into a name.

    python il2cpp_modules.py probe --dll GameAssembly.dll
    python il2cpp_modules.py struct --dll GameAssembly.dll --rva 0x3571d20
    python il2cpp_modules.py selftest
"""
from __future__ import annotations

import argparse
import re
import struct
import sys

SCRIPT_VERSION = "2026-10-26.14"
MODULE_NAME = re.compile(rb"^[A-Za-z0-9_.\-]{3,120}\.dll$")
IMAGE_BASE = 0x180000000


# ----------------------------------------------------------------------------- PE
def sections(data: bytes) -> list[dict]:
    """Section table of a PE32+ image, as file/virtual range pairs."""
    if data[:2] != b"MZ":
        raise ValueError("not a PE image")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        raise ValueError("no PE signature")
    count = struct.unpack_from("<H", data, pe + 6)[0]
    option_size = struct.unpack_from("<H", data, pe + 20)[0]
    option = pe + 24
    if struct.unpack_from("<H", data, option)[0] != 0x20B:
        raise ValueError("not a PE32+ image")
    base = struct.unpack_from("<Q", data, option + 24)[0]
    table = option + option_size
    out = []
    for index in range(count):
        raw = table + index * 40
        name = data[raw:raw + 8].rstrip(b"\x00").decode("latin-1")
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, raw + 8)
        out.append({"name": name, "vaddr": vaddr, "vsize": vsize,
                    "raddr": raddr, "rsize": rsize})
    return [{"image_base": base, **row} for row in out]


def rva_to_offset(table: list[dict], rva: int):
    for row in table:
        span = max(row["vsize"], row["rsize"])
        if row["vaddr"] <= rva < row["vaddr"] + span:
            delta = rva - row["vaddr"]
            if delta < row["rsize"]:
                return row["raddr"] + delta, row["name"]
            return None, row["name"]
    return None, None


# ---------------------------------------------------------------------- the records
def module_strings(data: bytes, table: list[dict]) -> dict[int, str]:
    """Offset of every `Something.dll` string in the image, by file offset."""
    out = {}
    for match in re.finditer(rb"[A-Za-z0-9_.\-]{3,120}\.dll", data):
        start = match.start()
        if start and (data[start - 1] == 0 or not chr(data[start - 1]).isalnum()):
            if MODULE_NAME.match(match.group()):
                out[start] = match.group().decode("latin-1")
    return out


def decode_module(blob: bytes, image_base: int = IMAGE_BASE) -> dict:
    """One `Il2CppCodeGenModule`, given the bytes starting at `moduleName`."""
    if len(blob) < 64:
        raise ValueError("module record needs 64 bytes")
    name = struct.unpack_from("<Q", blob, 0)[0]
    method_count = struct.unpack_from("<I", blob, 8)[0]
    method_pointers = struct.unpack_from("<Q", blob, 16)[0]
    return {
        "module_name_va": name,
        "method_pointer_count": method_count,
        "method_pointers_va": method_pointers,
        "method_pointers_rva": method_pointers - image_base if method_pointers else 0,
        "adjustor_thunk_count": struct.unpack_from("<I", blob, 24)[0],
        "adjustor_thunks_va": struct.unpack_from("<Q", blob, 32)[0],
        "invoker_indices_va": struct.unpack_from("<Q", blob, 40)[0],
    }


def find_modules(data: bytes, table: list[dict], limit: int = 64) -> list[dict]:
    """Every module record whose first field points at a module-name string."""
    image_base = table[0]["image_base"]
    names = module_strings(data, table)
    found = []
    for offset, text in names.items():
        # the string's own RVA
        string_rva = None
        for row in table:
            if row["raddr"] <= offset < row["raddr"] + row["rsize"]:
                string_rva = row["vaddr"] + (offset - row["raddr"])
                break
        if string_rva is None:
            continue
        needle = struct.pack("<Q", image_base + string_rva)
        for hit in re.finditer(re.escape(needle), data):
            start = hit.start()
            if start + 64 > len(data):
                continue
            try:
                record = decode_module(data[start:start + 64], image_base)
            except ValueError:
                continue
            count = record["method_pointer_count"]
            if 0 < count < 400000:
                found.append({"name": text, "record_offset": start,
                              "record_rva": _offset_to_rva(table, start), **record})
                if len(found) >= limit:
                    return found
    return found


def _offset_to_rva(table: list[dict], offset: int):
    for row in table:
        if row["raddr"] <= offset < row["raddr"] + row["rsize"]:
            return row["vaddr"] + (offset - row["raddr"])
    return None


def first_pointers(data: bytes, table: list[dict], record: dict, count: int = 8):
    """The first method addresses of a module, as RVAs (None if unreadable)."""
    rva = record.get("method_pointers_rva")
    if not rva:
        return []
    offset, _section = rva_to_offset(table, rva)
    if offset is None:
        return []
    image_base = table[0]["image_base"]
    out = []
    for index in range(count):
        position = offset + index * 8
        if position + 8 > len(data):
            break
        value = struct.unpack_from("<Q", data, position)[0]
        out.append(value - image_base if image_base <= value < image_base + (1 << 32) else None)
    return out


# ------------------------------------------------------------------------- selftest
def selftest() -> int:
    ok = True

    def check(label: str, good: bool) -> None:
        nonlocal ok
        ok &= bool(good)
        print(f"  {label:<34}{'ok' if good else 'FAILED'}")

    blob = (struct.pack("<Q", IMAGE_BASE + 0x1000) + struct.pack("<I", 37353)
            + b"\x00" * 4 + struct.pack("<Q", IMAGE_BASE + 0x2000)
            + struct.pack("<I", 1269) + b"\x00" * 4
            + struct.pack("<Q", IMAGE_BASE + 0x3000)
            + struct.pack("<Q", IMAGE_BASE + 0x4000) + b"\x00" * 16)
    record = decode_module(blob)
    check("module name", record["module_name_va"] == IMAGE_BASE + 0x1000)
    check("method count", record["method_pointer_count"] == 37353)
    check("method array rva", record["method_pointers_rva"] == 0x2000)
    check("adjustor thunks", record["adjustor_thunk_count"] == 1269)
    check("invoker indices", record["invoker_indices_va"] == IMAGE_BASE + 0x4000)

    check("module name pattern", bool(MODULE_NAME.match(b"Assembly-CSharp.dll")))
    check("junk rejected", not MODULE_NAME.match(b"not a module"))

    try:
        decode_module(b"\x00" * 10)
        check("short record raises", False)
    except ValueError:
        check("short record raises", True)

    print("selftest: " + ("PASS" if ok else "FAILED"))
    return 0 if ok else 1


# ------------------------------------------------------------------------------ cli
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest")

    p = sub.add_parser("probe", help="list every module record found in the image")
    p.add_argument("--dll", required=True)

    s = sub.add_parser("struct", help="decode one record and show the first methods")
    s.add_argument("--dll", required=True)
    s.add_argument("--rva", required=True, help="record RVA in hex, e.g. 0x3571d20")

    args = parser.parse_args(argv)
    if args.command == "selftest":
        return selftest()

    from pathlib import Path

    data = Path(args.dll).read_bytes()
    table = sections(data)
    print(f"il2cpp_modules {SCRIPT_VERSION}: {len(table)} sections, "
          f"image base {table[0]['image_base']:#x}")

    if args.command == "probe":
        modules = find_modules(data, table)
        for module in modules:
            print(f"  {module['name']:<32} {module['method_pointer_count']:>7} methods  "
                  f"record rva {module['record_rva']:#x}")
        print(f"{len(modules)} module records")
        return 0

    rva = int(args.rva, 16)
    offset, section = rva_to_offset(table, rva)
    if offset is None:
        print(f"{args.rva} is not in a readable section ({section})")
        return 2
    record = decode_module(data[offset:offset + 64])
    print(f"  in section {section}")
    for key, value in record.items():
        print(f"  {key:<24}{value:#x}" if isinstance(value, int) else f"  {key:<24}{value}")
    pointers = first_pointers(data, table, record)
    print("  first method rvas        " + ", ".join("—" if p is None else f"{p:#x}"
                                                   for p in pointers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
