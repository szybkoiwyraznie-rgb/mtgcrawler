"""CRILAYLA decompression (CRIWARE), as used by CPK entries with ExtractSize > FileSize.

Layout: 8-byte magic `CRILAYLA`, uint32 LE uncompressed size, uint32 LE compressed size, then the
compressed stream. The output is `uncompressed size + 0x100` bytes: the first 0x100 bytes are the
raw trailer stored after the stream (at 16 + compressed size), and the rest is decoded backwards
from the end of the output. The bit reader takes bits MSB-first from the last byte of the stream
and moves towards its start. Each step is one flag bit: 0 = literal byte (8 bits); 1 = back
reference: 13 bits of offset (distance = offset + 3 from the write position), then a length of
3 + a value read with 2, 3, and 5 bits, continued with 8-bit chunks while a chunk equals 255.

Algorithm follows the public reference implementation (Ultra-Despair-Extractor, cpk_extract.py).
The decoder checks sizes and reference bounds, and reports whether the stream was used up exactly.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

MAGIC = b"CRILAYLA"
HEADER_SIZE = 16
TRAILER_SIZE = 0x100


class CrilaylaError(ValueError):
    pass


@dataclass(frozen=True)
class Decoded:
    data: bytes
    bytes_consumed: int  # stream bytes read, counting from the end
    stream_size: int  # compressed size declared in the header


def is_crilayla(head: bytes) -> bool:
    return head[: len(MAGIC)] == MAGIC


def decompress(src: bytes) -> Decoded:
    if not is_crilayla(src) or len(src) < HEADER_SIZE:
        raise CrilaylaError("not a CRILAYLA stream")
    usize, csize = struct.unpack_from("<II", src, 8)
    if HEADER_SIZE + csize + TRAILER_SIZE > len(src):
        raise CrilaylaError("compressed size runs past the end of the entry")
    out = bytearray(usize + TRAILER_SIZE)
    out[0:TRAILER_SIZE] = src[HEADER_SIZE + csize : HEADER_SIZE + csize + TRAILER_SIZE]
    byte_pos = HEADER_SIZE + csize - 1
    lowest_byte = HEADER_SIZE
    pool = 0
    bits_left = 0

    def get_bits(count: int) -> int:
        nonlocal byte_pos, pool, bits_left
        value = 0
        while count > 0:
            if bits_left == 0:
                if byte_pos < lowest_byte:
                    raise CrilaylaError("compressed stream ends before the output is complete")
                pool = src[byte_pos]
                bits_left = 8
                byte_pos -= 1
            take = min(bits_left, count)
            value = (value << take) | ((pool >> (bits_left - take)) & ((1 << take) - 1))
            bits_left -= take
            count -= take
        return value

    position = TRAILER_SIZE + usize - 1
    while position >= TRAILER_SIZE:
        if get_bits(1):
            reference = position + get_bits(13) + 3
            length = 3
            for width in (2, 3, 5):
                chunk = get_bits(width)
                length += chunk
                if chunk != (1 << width) - 1:
                    break
            else:
                chunk = get_bits(8)
                length += chunk
                while chunk == 255:
                    chunk = get_bits(8)
                    length += chunk
            if reference >= len(out) or reference - length + 1 < 0:
                raise CrilaylaError("back-reference points outside the output")
            if position - length < TRAILER_SIZE - 1:
                raise CrilaylaError("back-reference writes past the start of the output")
            for _ in range(length):
                out[position] = out[reference]
                position -= 1
                reference -= 1
        else:
            out[position] = get_bits(8)
            position -= 1
    consumed = HEADER_SIZE + csize - 1 - byte_pos
    return Decoded(data=bytes(out), bytes_consumed=consumed, stream_size=csize)
