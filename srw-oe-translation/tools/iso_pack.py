"""Rebuild (pack) an ISO9660 image from a directory tree.

The repository's ``iso9660.py`` is read-only (index + extract). This module is its writing
counterpart: given a tree of files it emits a spec-shaped ISO9660 Level-1 image whose primary
volume descriptor, path tables and directory records ``iso9660.inspect_iso9660`` /
``extract_members`` can traverse again -- which is how the writer is regression-tested
(pack -> inspect -> extract round trip).

The image preserves a caller-supplied 32 KiB system area (sectors 0..15). For a PSP UMD that
is where the boot code lives; keeping the original bytes there and re-emitting a coherent
descriptor set after it is what lets a repacked disc still boot.

Only single-extent files and directories, no Joliet, no interleaving: the subset the reader
supports and the game needs.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path
from typing import Mapping, Union

BLOCK_SIZE = 2048
PVD_LBA = 16
SYSTEM_AREA_BYTES = 16 * BLOCK_SIZE  # sectors 0..15

Tree = Mapping[str, Union[bytes, "Tree"]]  # name -> file bytes or sub-tree


def _both(value: int, width: int) -> bytes:
    return value.to_bytes(width, "little") + value.to_bytes(width, "big")


def _record(identifier: bytes, lba: int, size: int, is_dir: bool) -> bytes:
    ident_len = len(identifier)
    length = 33 + ident_len + (1 if ident_len % 2 == 0 else 0)
    out = bytearray(length)
    out[0] = length
    out[1] = 0  # extended attribute length
    out[2:6] = lba.to_bytes(4, "little")
    out[6:10] = lba.to_bytes(4, "big")
    out[10:14] = size.to_bytes(4, "little")
    out[14:18] = size.to_bytes(4, "big")
    # recording date/time: seven zero bytes is legal ("unspecified")
    out[25] = 0x02 if is_dir else 0x00
    out[26] = 0
    out[27] = 0
    out[28:30] = (1).to_bytes(2, "little")
    out[30:32] = (1).to_bytes(2, "big")
    out[32] = ident_len
    out[33:33 + ident_len] = identifier
    return bytes(out)


def _dir_name(name: str) -> bytes:
    return name.upper().encode("ascii")


def _collect(tree: Tree, prefix: str, dirs: list, files: list) -> None:
    """BFS-collect directories (root first) and their files."""
    dirs.append(prefix)
    for name, value in tree.items():
        if isinstance(value, (bytes, bytearray)):
            files.append((prefix, name, bytes(value)))
        else:
            _collect(value, f"{prefix}{name}/", dirs, files)


def _sector_pad(data: bytes) -> bytes:
    rem = len(data) % BLOCK_SIZE
    return data if rem == 0 else data + b"\x00" * (BLOCK_SIZE - rem)


def build_iso(tree: Tree, system_area: bytes = b"\x00" * SYSTEM_AREA_BYTES) -> bytes:
    if len(system_area) != SYSTEM_AREA_BYTES:
        raise ValueError("system area must be exactly 32 KiB (sectors 0..15)")

    dirs: list[str] = []
    files: list[tuple[str, str, bytes]] = []
    _collect(tree, "", dirs, files)
    dir_index = {d: i + 1 for i, d in enumerate(dirs)}  # root = 1

    # Build directory record blocks (extents) without final LBAs, then lay out.
    dir_children: dict[str, list] = {d: [] for d in dirs}
    for parent, name, blob in files:
        dir_children[parent].append((name, len(blob), False))
    for d in dirs[1:]:
        parent = d[: d.rindex("/", 0, len(d) - 1) + 1] if d.count("/") > 1 else ""
        dir_children[parent].append((d.strip("/").split("/")[-1], 0, True, d))

    # Layout: system(0..15), PVD 16, terminator 17, L path 18, M path 19, dirs, files.
    lba = 18 + 2  # placeholder; refined below after sizing path tables
    # Path table byte size depends only on names.
    def path_entry_size(name: str) -> int:
        ident = b"\x00" if name == "" else _dir_name(name.split("/")[-2] if name.endswith("/") else name)
        return 8 + len(ident) + (len(ident) % 2)
    pt_size = sum(8 + (1 if d == "" else len(_dir_name(d.rstrip('/').split('/')[-1])) +
                       (len(_dir_name(d.rstrip('/').split('/')[-1])) % 2)) for d in dirs)
    pt_sectors = max(1, (pt_size + BLOCK_SIZE - 1) // BLOCK_SIZE)
    l_path_lba = 18
    m_path_lba = 18 + pt_sectors

    dir_lba: dict[str, int] = {}
    file_lba: dict[tuple, int] = {}
    cursor = m_path_lba + pt_sectors
    # directory extents first, then file extents
    dir_blocks: dict[str, bytes] = {}
    for d in dirs:
        # build records; child dir extents unknown yet -> two passes: record sizes known after
        # we assign, so store placeholders and patch later. Instead compute sizes now with a
        # first pass assigning LBAs in order.
        dir_lba[d] = cursor
        block = bytearray()
        self_lba = dir_lba[d]
        parent = "" if d == "" else (d[: d.rindex("/", 0, len(d) - 1) + 1] if d.count("/") > 1 else "")
        block += _record(b"\x00", self_lba, 0, True)   # size patched below
        block += _record(b"\x01", dir_lba.get(parent, self_lba), 0, True)
        for child in dir_children[d]:
            if child[2]:
                block += _record(_dir_name(child[0]), 0, 0, True)
            else:
                block += _record(_dir_name(child[0]), 0, child[1], False)
        dir_blocks[d] = _sector_pad(bytes(block))
        cursor += len(dir_blocks[d]) // BLOCK_SIZE
    # file extents
    file_blobs: dict[tuple, bytes] = {}
    for parent, name, blob in files:
        file_lba[(parent, name)] = cursor
        file_blobs[(parent, name)] = _sector_pad(blob)
        cursor += len(file_blobs[(parent, name)]) // BLOCK_SIZE
    total_lba = cursor

    # Patch directory records with real extents (second pass).
    for d in dirs:
        block = bytearray(dir_blocks[d])
        # rebuild cleanly with known LBAs
        rec = bytearray()
        parent = "" if d == "" else (d[: d.rindex("/", 0, len(d) - 1) + 1] if d.count("/") > 1 else "")
        rec += _record(b"\x00", dir_lba[d], len(dir_blocks[d]), True)
        rec += _record(b"\x01", dir_lba[parent], len(dir_blocks[parent]), True)
        for child in dir_children[d]:
            if child[2]:
                sub = child[3]
                rec += _record(_dir_name(child[0]), dir_lba[sub], len(dir_blocks[sub]), True)
            else:
                rec += _record(_dir_name(child[0]), file_lba[(d, child[0])], child[1], False)
        dir_blocks[d] = _sector_pad(bytes(rec))

    # Path tables.
    def path_tables() -> tuple[bytes, bytes]:
        l = bytearray(); m = bytearray()
        for d in dirs:
            ident = b"\x00" if d == "" else _dir_name(d.rstrip("/").split("/")[-1])
            parent = "" if d == "" else (d[: d.rindex("/", 0, len(d) - 1) + 1] if d.count("/") > 1 else "")
            pad = len(ident) % 2
            l.append(len(ident)); l.append(0)
            l += dir_lba[d].to_bytes(4, "little")
            l += dir_index[parent].to_bytes(2, "little")
            l += ident + b"\x00" * pad
            m.append(len(ident)); m.append(0)
            m += dir_lba[d].to_bytes(4, "big")
            m += dir_index[parent].to_bytes(2, "big")
            m += ident + b"\x00" * pad
        return _sector_pad(bytes(l)), _sector_pad(bytes(m))

    l_path, m_path = path_tables()

    # Primary Volume Descriptor.
    pvd = bytearray(BLOCK_SIZE)
    pvd[0] = 1
    pvd[1:6] = b"CD001"
    pvd[6] = 1
    pvd[8:16] = b"SRWOE".ljust(8)          # system identifier
    pvd[40:72] = b"SRWOE_PATCH".ljust(32)   # volume identifier
    pvd[80:88] = _both(total_lba, 4)        # volume space size
    pvd[120:124] = _both(1, 2)              # volume set size
    pvd[124:128] = _both(1, 2)              # sequence number
    pvd[128:132] = _both(BLOCK_SIZE, 2)     # logical block size
    pvd[132:140] = _both(pt_size, 4)        # path table size
    pvd[140:144] = l_path_lba.to_bytes(4, "little")
    pvd[148:152] = m_path_lba.to_bytes(4, "big")
    pvd[156:190] = _record(b"\x00", dir_lba[""], len(dir_blocks[""]), True)
    terminator = bytearray(BLOCK_SIZE)
    terminator[0] = 255
    terminator[1:6] = b"CD001"
    terminator[6] = 1

    out = bytearray()
    out += system_area
    out += bytes(pvd)
    out += bytes(terminator)
    out += l_path[: pt_sectors * BLOCK_SIZE].ljust(pt_sectors * BLOCK_SIZE, b"\x00")
    out += m_path[: pt_sectors * BLOCK_SIZE].ljust(pt_sectors * BLOCK_SIZE, b"\x00")
    for d in dirs:
        out += dir_blocks[d]
    for (parent, name) in file_blobs:
        out += file_blobs[(parent, name)]
    return bytes(out)


def pack_iso(tree: Tree, out_path: Path, system_area: bytes = b"\x00" * SYSTEM_AREA_BYTES) -> None:
    out_path.write_bytes(build_iso(tree, system_area))
