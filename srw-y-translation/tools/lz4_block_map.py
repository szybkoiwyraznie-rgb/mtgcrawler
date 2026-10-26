"""Where does a plaintext byte live in an LZ4-compressed bundle block?

Bundles in this game are a UnityFS container whose serialized file is split into
128 KiB blocks, each LZ4/LZ4HC compressed on its own.  To change text without
recompressing (and therefore without changing the file size, which the game's
keystream depends on), a replacement byte is only allowed where the original
byte was encoded as an LZ4 *literal*: a literal is copied 1:1 from the
compressed stream, so overwriting the input byte overwrites the output byte.

This module reads the container and answers, for every plaintext offset, which
compressed byte produced it (`-1` = the byte came out of a match).
"""
import struct
import sys
from pathlib import Path


def lz4_map(src, out_len):
    """Decode an LZ4 block; return (out, origin)."""
    out = bytearray()
    origin = []
    i = 0
    n = len(src)
    while len(out) < out_len:
        if i >= n:
            raise ValueError('input exhausted')
        token = src[i]
        i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        if i + lit > n:
            raise ValueError('literal run past end')
        out += src[i:i + lit]
        origin += list(range(i, i + lit))
        i += lit
        if len(out) >= out_len:
            break
        if i + 2 > n:
            raise ValueError('match offset past end')
        offset = src[i] | (src[i + 1] << 8)
        i += 2
        mlen = token & 0x0F
        if mlen == 15:
            while True:
                b = src[i]
                i += 1
                mlen += b
                if b != 255:
                    break
        mlen += 4
        start = len(out) - offset
        if offset == 0 or start < 0:
            raise ValueError('bad match offset')
        for k in range(mlen):
            out.append(out[start + k])
            origin.append(-1)
    if len(out) != out_len:
        raise ValueError(f'decoded {len(out)} != {out_len}')
    return bytes(out), origin


def parse_container(data):
    """Read a UnityFS v8 container layout (info at start, 16-byte aligned)."""
    end = data.index(b'\0')
    signature = data[:end].decode()
    if signature != 'UnityFS':
        raise ValueError(f'not a UnityFS bundle: {signature}')
    i = end + 1
    version, = struct.unpack('>I', data[i:i + 4])
    i += 4

    def cstr(pos):
        j = data.index(b'\0', pos)
        return data[pos:j].decode(), j + 1

    player, i = cstr(i)
    engine, i = cstr(i)
    size, csize, usize, flags = struct.unpack('>qIII', data[i:i + 20])
    i += 20
    if version >= 7:
        i = (i + 15) // 16 * 16
    info_at_end = bool(flags & 0x80)
    if info_at_end:
        info_off = len(data) - csize
    else:
        info_off = i
    kind = flags & 0x3F
    raw = data[info_off:info_off + csize]
    info = lz4_map(raw, usize)[0] if kind in (2, 3) else raw
    p = 16
    count, = struct.unpack('>i', info[p:p + 4])
    p += 4
    blocks = []
    for _ in range(count):
        u, c, f = struct.unpack('>IIH', info[p:p + 10])
        p += 10
        blocks.append((u, c, f))
    nfiles, = struct.unpack('>i', info[p:p + 4])
    p += 4
    files = []
    for _ in range(nfiles):
        off, fsize, fflags = struct.unpack('>qqI', info[p:p + 20])
        p += 20
        j = info.index(b'\0', p)
        name = info[p:j].decode()
        p = j + 1
        files.append((off, fsize, fflags, name))
    start = info_off + csize
    if flags & 0x200:
        start = (start + 15) // 16 * 16
    return {
        'version': version, 'player': player, 'engine': engine, 'size': size,
        'csize': csize, 'usize': usize, 'flags': flags, 'info_offset': info_off,
        'blocks': blocks, 'files': files, 'data_offset': start,
    }


def decompress_blocks(data, layout, want=None):
    """Return [(index, comp_offset, out, origin)] for the requested blocks."""
    pos = layout['data_offset']
    out = []
    for k, (u, c, f) in enumerate(layout['blocks']):
        if want is None or k in want:
            chunk = data[pos:pos + c]
            if (f & 0x3F) in (2, 3):
                plain, origin = lz4_map(chunk, u)
            else:
                plain, origin = chunk, list(range(pos, pos + u))
            out.append((k, pos, plain, origin))
        pos += c
    return out


def main(argv):
    path = Path(argv[0])
    data = path.read_bytes()
    layout = parse_container(data)
    print(f'{path.name}: {layout["size"]:,} B, flags {layout["flags"]:#x}, '
          f'{len(layout["blocks"])} blocks, info at {layout["info_offset"]}, '
          f'data at {layout["data_offset"]}')
    print('files:', [(n, s) for _, s, _, n in layout['files']])
    total = 0
    for k, (u, c, f) in enumerate(layout['blocks']):
        total += u
    print(f'uncompressed total {total:,}')
    if len(argv) > 1:
        needle = argv[1].encode()
        for k, pos, plain, origin in decompress_blocks(data, layout):
            base = sum(b[0] for b in layout['blocks'][:k])
            j = plain.find(needle)
            if j < 0:
                continue
            lit = sum(1 for o in origin[j:j + len(needle)] if o >= 0)
            print(f'block {k}: needle at plaintext {base + j:,} '
                  f'(block offset {j:,}), literal bytes {lit}/{len(needle)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
