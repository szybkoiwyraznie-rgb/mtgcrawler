#!/usr/bin/env python3
"""Read-only ISO9660 directory inventory for local PSP images.

This small adapter uses the Primary Volume Descriptor and 2048-byte sectors to
list directory entries and detect CPK signatures from file extents. It does not
extract members, modify an image, interpret game data, or implement Joliet/Rock
Ridge semantics. A reported signature is not proof that YACpkTool can consume
the member.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from urllib.parse import quote_from_bytes

BLOCK_SIZE = 2048
PVD_LBA = 16
MAX_VOLUME_DESCRIPTORS = 64
MAX_DIRECTORY_DEPTH = 64
MAX_DIRECTORY_ENTRIES = 1_000_000
CPK_SIGNATURE = b"CPK "


class Iso9660Error(ValueError):
    """The image is not a supported, internally consistent ISO9660 volume."""


@dataclass(frozen=True)
class _Extent:
    lba: int
    byte_length: int
    extended_attribute_blocks: int

    def offset(self, block_size: int) -> int:
        return (self.lba + self.extended_attribute_blocks) * block_size

    def as_dict(self, block_size: int) -> dict[str, int]:
        return {
            "lba": self.lba,
            "extended_attribute_blocks": self.extended_attribute_blocks,
            "offset_bytes": self.offset(block_size),
            "length_bytes": self.byte_length,
        }


@dataclass(frozen=True)
class _DirectoryRecord:
    identifier: bytes
    extent: _Extent
    is_directory: bool
    continues_extent: bool


def _read_exact(stream: BinaryIO, offset: int, count: int, label: str) -> bytes:
    if offset < 0 or count < 0:
        raise Iso9660Error(f"Invalid negative {label} range")
    stream.seek(offset)
    data = stream.read(count)
    if len(data) != count:
        raise Iso9660Error(f"Truncated {label}")
    return data


def _both_endian(data: bytes, offset: int, width: int, label: str) -> int:
    end = offset + width * 2
    if width not in (2, 4) or end > len(data):
        raise Iso9660Error(f"Truncated both-endian {label}")
    little = int.from_bytes(data[offset : offset + width], "little")
    big = int.from_bytes(data[offset + width : end], "big")
    if little != big:
        raise Iso9660Error(f"Mismatched both-endian {label}")
    return little


def _parse_record(
    raw: bytes,
    *,
    block_size: int,
    volume_bytes: int,
    image_bytes: int,
) -> _DirectoryRecord:
    if len(raw) < 34 or raw[0] != len(raw):
        raise Iso9660Error("Invalid ISO9660 directory-record length")
    identifier_length = raw[32]
    minimum_length = 33 + identifier_length + (identifier_length % 2 == 0)
    if identifier_length == 0 or minimum_length > len(raw):
        raise Iso9660Error("Invalid ISO9660 file-identifier length")

    extent_lba = _both_endian(raw, 2, 4, "extent location")
    byte_length = _both_endian(raw, 10, 4, "data length")
    volume_sequence = _both_endian(raw, 28, 2, "volume sequence number")
    if volume_sequence != 1:
        raise Iso9660Error("Multi-volume ISO9660 records are unsupported")

    extended_attributes = raw[1]
    extent = _Extent(extent_lba, byte_length, extended_attributes)
    data_offset = extent.offset(block_size)
    data_end = data_offset + byte_length
    if data_end > volume_bytes or data_end > image_bytes:
        raise Iso9660Error("ISO9660 extent extends beyond the image volume")

    file_unit_size = raw[26]
    interleave_gap = raw[27]
    if file_unit_size or interleave_gap:
        raise Iso9660Error("Interleaved ISO9660 files are unsupported")

    flags = raw[25]
    return _DirectoryRecord(
        identifier=raw[33 : 33 + identifier_length],
        extent=extent,
        is_directory=bool(flags & 0x02),
        continues_extent=bool(flags & 0x80),
    )


def _read_volume_descriptor_set(
    stream: BinaryIO, image_bytes: int
) -> tuple[bytes, int, int, bool]:
    if image_bytes < (PVD_LBA + 1) * BLOCK_SIZE:
        raise Iso9660Error("Image is too small to contain an ISO9660 PVD")

    pvd: bytes | None = None
    terminator_seen = False
    joliet_seen = False
    descriptor_limit = min(MAX_VOLUME_DESCRIPTORS, image_bytes // BLOCK_SIZE - PVD_LBA)
    for index in range(descriptor_limit):
        lba = PVD_LBA + index
        descriptor = _read_exact(stream, lba * BLOCK_SIZE, BLOCK_SIZE, "volume descriptor")
        if descriptor[1:6] != b"CD001" or descriptor[6] != 1:
            raise Iso9660Error("Invalid ISO9660 volume-descriptor identifier/version")
        descriptor_type = descriptor[0]
        if descriptor_type == 1:
            if pvd is not None:
                raise Iso9660Error("Multiple Primary Volume Descriptors are unsupported")
            pvd = descriptor
        elif descriptor_type == 2 and descriptor[88:91] in (b"%/@", b"%/C", b"%/E"):
            joliet_seen = True
        elif descriptor_type == 255:
            terminator_seen = True
            break

    if not terminator_seen:
        raise Iso9660Error("ISO9660 volume-descriptor terminator was not found")
    if pvd is None:
        raise Iso9660Error("ISO9660 Primary Volume Descriptor was not found")

    block_size = _both_endian(pvd, 128, 2, "logical block size")
    if block_size != BLOCK_SIZE:
        raise Iso9660Error(f"Unsupported ISO9660 logical block size: {block_size}")
    volume_blocks = _both_endian(pvd, 80, 4, "volume-space size")
    if volume_blocks <= PVD_LBA:
        raise Iso9660Error("Invalid ISO9660 volume-space size")
    volume_bytes = volume_blocks * block_size
    if volume_bytes > image_bytes:
        raise Iso9660Error("ISO9660 volume-space size exceeds image length")
    return pvd, block_size, volume_bytes, joliet_seen


def _directory_members(
    stream: BinaryIO,
    directory: _Extent,
    *,
    block_size: int,
    volume_bytes: int,
    image_bytes: int,
) -> list[list[_DirectoryRecord]]:
    """Read directory records and coalesce consecutive multi-extent files."""
    start = directory.offset(block_size)
    cursor = 0
    groups: list[list[_DirectoryRecord]] = []
    pending: list[_DirectoryRecord] | None = None
    records_seen = 0

    while cursor < directory.byte_length:
        absolute = start + cursor
        remaining = directory.byte_length - cursor
        sector_remaining = block_size - (absolute % block_size)
        record_length = _read_exact(stream, absolute, 1, "directory record length")[0]
        if record_length == 0:
            cursor += min(sector_remaining, remaining)
            continue
        if record_length < 34 or record_length > sector_remaining or record_length > remaining:
            raise Iso9660Error("Invalid or sector-crossing ISO9660 directory record")
        raw = _read_exact(stream, absolute, record_length, "directory record")
        record = _parse_record(
            raw,
            block_size=block_size,
            volume_bytes=volume_bytes,
            image_bytes=image_bytes,
        )
        records_seen += 1
        if records_seen > MAX_DIRECTORY_ENTRIES:
            raise Iso9660Error("ISO9660 directory-entry limit exceeded")
        cursor += record_length

        if pending is not None:
            first = pending[0]
            if record.identifier != first.identifier or record.is_directory != first.is_directory:
                raise Iso9660Error("Nonconsecutive ISO9660 multi-extent records")
            if record.is_directory:
                raise Iso9660Error("Multi-extent directories are unsupported")
            pending.append(record)
            if not record.continues_extent:
                groups.append(pending)
                pending = None
        elif record.continues_extent:
            if record.is_directory or record.identifier in (b"\x00", b"\x01"):
                raise Iso9660Error("Invalid ISO9660 multi-extent record")
            pending = [record]
        else:
            groups.append([record])

        if len(groups) > MAX_DIRECTORY_ENTRIES:
            raise Iso9660Error("ISO9660 directory-entry limit exceeded")

    if pending is not None:
        raise Iso9660Error("Incomplete ISO9660 multi-extent file")
    return groups


def _member_prefix(
    stream: BinaryIO, records: list[_DirectoryRecord], block_size: int
) -> bytes:
    prefix = bytearray()
    for record in records:
        if len(prefix) >= len(CPK_SIGNATURE):
            break
        extent = record.extent
        amount = min(len(CPK_SIGNATURE) - len(prefix), extent.byte_length)
        if amount:
            prefix.extend(_read_exact(stream, extent.offset(block_size), amount, "file signature"))
    return bytes(prefix)


def _identifier_text(identifier: bytes) -> str:
    # Keep stable byte identity for non-ASCII names rather than guessing a codec.
    # Percent-escape dot-only components so later consumers cannot mistake a
    # legal-but-unusual identifier for a traversal component.
    if identifier in (b".", b".."):
        return "%2E" * len(identifier)
    return quote_from_bytes(
        identifier,
        safe="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-~;$",
    )


def inspect_iso9660(path: Path) -> dict[str, object]:
    """Inventory standard ISO9660 files and CPK signatures without extraction."""
    image = path.expanduser().resolve(strict=True)
    if not image.is_file():
        raise Iso9660Error("ISO9660 input is not a regular file")
    image_bytes = image.stat().st_size

    with image.open("rb") as stream:
        pvd, block_size, volume_bytes, joliet_seen = _read_volume_descriptor_set(
            stream, image_bytes
        )
        root_length = pvd[156]
        if root_length < 34 or 156 + root_length > block_size:
            raise Iso9660Error("Invalid ISO9660 root-directory record")
        root = _parse_record(
            pvd[156 : 156 + root_length],
            block_size=block_size,
            volume_bytes=volume_bytes,
            image_bytes=image_bytes,
        )
        if root.identifier != b"\x00" or not root.is_directory or root.continues_extent:
            raise Iso9660Error("Invalid ISO9660 root-directory record")

        files: list[dict[str, object]] = []
        directories: list[str] = [""]
        visited_directories: set[tuple[int, int]] = set()

        def walk(directory: _Extent, parent_path: str, depth: int) -> None:
            if depth > MAX_DIRECTORY_DEPTH:
                raise Iso9660Error("ISO9660 directory-depth limit exceeded")
            key = (directory.offset(block_size), directory.byte_length)
            if key in visited_directories:
                return
            visited_directories.add(key)

            for group in _directory_members(
                stream,
                directory,
                block_size=block_size,
                volume_bytes=volume_bytes,
                image_bytes=image_bytes,
            ):
                first = group[0]
                if first.identifier in (b"\x00", b"\x01"):
                    continue
                name = _identifier_text(first.identifier)
                member_path = f"{parent_path}/{name}" if parent_path else name
                if first.is_directory:
                    if len(group) != 1:
                        raise Iso9660Error("Multi-extent directories are unsupported")
                    directories.append(member_path)
                    if len(files) + len(directories) > MAX_DIRECTORY_ENTRIES:
                        raise Iso9660Error("ISO9660 directory-entry limit exceeded")
                    walk(first.extent, member_path, depth + 1)
                    continue

                total_size = sum(record.extent.byte_length for record in group)
                signature_bytes = _member_prefix(stream, group, block_size)
                signature = (
                    "cpk_signature"
                    if signature_bytes == CPK_SIGNATURE
                    else "other_signature"
                )
                files.append(
                    {
                        "path": member_path,
                        "size_bytes": total_size,
                        "content_type": signature,
                        "extent_count": len(group),
                        "extents": [
                            record.extent.as_dict(block_size) for record in group
                        ],
                    }
                )
                if len(files) + len(directories) > MAX_DIRECTORY_ENTRIES:
                    raise Iso9660Error("ISO9660 directory-entry limit exceeded")

        walk(root.extent, "", 0)

    files.sort(key=lambda member: str(member["path"]).casefold())
    directories.sort(key=str.casefold)
    cpk_count = sum(member["content_type"] == "cpk_signature" for member in files)
    warnings = []
    if joliet_seen:
        warnings.append("Joliet descriptors were detected but not used; names come from the PVD.")
    return {
        "status": "indexed",
        "format": "ISO9660 PVD",
        "primary_volume_descriptor_lba": PVD_LBA,
        "logical_block_size": block_size,
        "volume_blocks": volume_bytes // block_size,
        "volume_bytes": volume_bytes,
        "file_count": len(files),
        "directory_count": len(directories),
        "cpk_signature_count": cpk_count,
        "joliet_descriptor_detected": joliet_seen,
        "files": files,
        "directories": directories,
        "warnings": warnings,
        "scope_note": (
            "Read-only primary-volume directory inventory and first-four-byte signatures; "
            "no member was extracted, hashed, modified, or passed to a converter."
        ),
    }
