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


def compress_literal(data: bytes) -> bytes:
    """Encode `data` as a valid CRILAYLA stream made only of literal bytes.

    The decoder's output is `trailer (0x100) + decoded`. We put the first 0x100 bytes
    of `data` in the raw trailer and emit every remaining byte as a 9-bit literal
    (flag bit 0 + the byte MSB-first), laid out so that the decoder's backwards,
    MSB-first bit reader reproduces them in order. The result is a genuine CRILAYLA
    stream: ``decompress(compress_literal(x)).data == x``. It is larger than `data`
    (9 bits per body byte) but the container records FileSize and ExtractSize
    accordingly, so a reader that always decompresses behaves correctly.
    """
    if len(data) < TRAILER_SIZE:
        raise CrilaylaError("a CRILAYLA entry needs at least the 0x100-byte trailer")
    trailer = data[:TRAILER_SIZE]
    body = data[TRAILER_SIZE:]

    bits = bytearray()
    for value in reversed(body):
        bits.append(0)  # literal flag
        for k in range(7, -1, -1):
            bits.append((value >> k) & 1)

    nbytes = (len(bits) + 7) // 8
    stream = bytearray(nbytes)
    for k, bit in enumerate(bits):
        if bit:
            stream[nbytes - 1 - k // 8] |= 1 << (7 - k % 8)

    return MAGIC + struct.pack("<II", len(body), nbytes) + bytes(stream) + trailer


def compress(data: bytes) -> bytes:
    """Encode `data` as a genuine, shrinking CRILAYLA stream (LZSS back-references).

    Mirrors :func:`decompress` exactly, so ``decompress(compress(x)).data == x`` and the
    resulting entry has FileSize < ExtractSize like a real CRI container, which the game's
    always-decompress reader expects. The output is filled backwards, so instructions are
    emitted from the last output byte to the first and packed MSB-first from the end of the
    stream, matching the decoder's backwards bit reader.
    """
    if len(data) < TRAILER_SIZE + 3:
        raise CrilaylaError("a CRILAYLA entry needs at least the trailer plus 3 bytes")
    n = len(data)
    usize = n - TRAILER_SIZE

    index = {}
    for i in range(TRAILER_SIZE, n - 2):
        index.setdefault(data[i:i + 3], []).append(i)

    bits = []

    def emit(value: int, count: int) -> None:
        for k in range(count - 1, -1, -1):
            bits.append((value >> k) & 1)

    p = n - 1
    while p >= TRAILER_SIZE:
        best_len = 0
        best_delta = 0
        if p + 3 <= n:
            for cand in index.get(data[p:p + 3], ()):
                if cand <= p:
                    continue
                delta = cand - p
                if delta < 3 or delta - 3 > 0x1FFF:
                    continue
                limit = min(n - p, n - cand, 4096, p - TRAILER_SIZE + 1)
                length = 0
                while length < limit and data[p + length] == data[cand + length]:
                    length += 1
                if length > best_len:
                    best_len = length
                    best_delta = delta
                if best_len >= 256:
                    break
        if best_len >= 4:
            emit(1, 1)
            emit(best_delta - 3, 13)
            rest = best_len - 3
            for width in (2, 3, 5):
                maxc = (1 << width) - 1
                chunk = min(rest, maxc)
                emit(chunk, width)
                rest -= chunk
                if chunk < maxc:
                    break
            else:
                while True:
                    chunk = min(rest, 255)
                    emit(chunk, 8)
                    rest -= chunk
                    if chunk < 255:
                        break
            p -= best_len
        else:
            emit(0, 1)
            emit(data[p], 8)
            p -= 1

    nbytes = (len(bits) + 7) // 8
    stream = bytearray(nbytes)
    for k, bit in enumerate(bits):
        if bit:
            stream[nbytes - 1 - k // 8] |= 1 << (7 - k % 8)
    return MAGIC + struct.pack("<II", usize, nbytes) + bytes(stream) + data[:TRAILER_SIZE]
