#!/usr/bin/env python3
"""Offline experimental PPSSPP input/VRAM probe. No debugger server is opened.

Use only private copies, including a separately isolated HOME/memstick. Raw VRAM
is untrusted/unsynchronized and both heuristic buffers are retained. This does
not establish which screen was shown or that a game/save is safe.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

FRAME_BYTES = 512 * 272 * 2


def convert(raw: bytes, stride: int = 512, pixel_format: int = 1):
    if not 480 <= stride <= 4096 or pixel_format not in (0, 1, 2, 3):
        raise ValueError('unsupported display stride or pixel format')
    bpp = 4 if pixel_format == 3 else 2
    if len(raw) != stride * 272 * bpp:
        raise ValueError('unexpected VRAM byte count')
    from PIL import Image
    image = Image.new('RGB', (480, 272))
    pixels = image.load()
    for y in range(272):
        for x in range(480):
            offset = bpp * (y * stride + x)
            if pixel_format == 3:
                pixels[x, y] = tuple(raw[offset:offset + 3])
                continue
            value = raw[offset] | raw[offset + 1] << 8
            if pixel_format == 0:
                pixels[x, y] = ((value & 31) * 255 // 31, ((value >> 5) & 63) * 255 // 63,
                                ((value >> 11) & 31) * 255 // 31)
            elif pixel_format == 1:
                pixels[x, y] = ((value & 31) * 255 // 31, ((value >> 5) & 31) * 255 // 31,
                                ((value >> 10) & 31) * 255 // 31)
            else:
                pixels[x, y] = ((value & 15) * 17, ((value >> 4) & 15) * 17, ((value >> 8) & 15) * 17)
    return image


def frame_parameters(name: str) -> tuple[int, int]:
    match = re.fullmatch(r'vram-\d{3}-active-[0-9a-f]{8}-(\d+)-([0-3])\.raw', name)
    if match:
        return int(match[1]), int(match[2])
    if re.fullmatch(r'vram-\d{3}-(04000000|04044000)\.raw', name):
        return 512, 1  # historical candidate: format is assumed, not read from the PSP
    raise ValueError('unexpected VRAM filename')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--iso-copy', type=Path, required=True)
    p.add_argument('--home-copy', type=Path, required=True)
    p.add_argument('--schedule', type=Path, required=True,
                   help='text: wall-clock seconds, hex PSP button mask, duration seconds; one event per line')
    p.add_argument('--output', type=Path, required=True, help='new private directory for game images/logs')
    p.add_argument('--seconds', type=int, default=60)
    p.add_argument('--trace-io', action='store_true', help='log up to 2000 file-open attempts, including private paths')
    a = p.parse_args()
    if not 5 <= a.seconds <= 180:
        p.error('--seconds must be between 5 and 180')
    binary, iso, home, schedule = (x.resolve(strict=True) for x in (a.binary, a.iso_copy, a.home_copy, a.schedule))
    if home == Path.home().resolve() or not home.is_dir():
        p.error('HOME must be an isolated directory')
    out = a.output.resolve()
    if home == out or home in out.parents or out in home.parents:
        p.error('output must be separate from isolated HOME')
    if out in iso.parents or out in schedule.parents or out in binary.parents:
        p.error('output must not contain any input')
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, HOME=str(home), PPSSPP_RESEARCH_THROTTLE='1',
               PPSSPP_RESEARCH_SCHEDULE=str(schedule), PPSSPP_RESEARCH_VRAM_PREFIX=str(out / 'vram'))
    env.pop('PPSSPP_RESEARCH_TRACE_IO', None)
    if a.trace_io:
        env['PPSSPP_RESEARCH_TRACE_IO'] = '1'
    # Never pass --debugger.
    with (out / 'emulator.log').open('w', encoding='utf-8') as log:
        try:
            result = subprocess.run([str(binary), str(iso), '--graphics=software', f'--timeout={a.seconds}'],
                                    env=env, stdout=log, stderr=log, timeout=a.seconds + 45)
            exit_code, killed = result.returncode, False
        except subprocess.TimeoutExpired:
            exit_code, killed = None, True
    frames = sorted(out.glob('vram-*.raw'))
    for path in frames:
        convert(path.read_bytes(), *frame_parameters(path.name)).save(path.with_suffix('.png'))
    log = (out / 'emulator.log').read_text(encoding='utf-8', errors='replace')
    enabled = 'Offline research enabled:' in log
    receipt = {'exit_code': exit_code, 'external_timeout': killed, 'headless_timeout_in_log': 'TIMEOUT' in log,
               'instrumentation_enabled': enabled, 'raw_buffers': len(frames),
               'active_frame_candidates': sum('-active-' in f.name for f in frames), 'debugger_requested': False,
               'io_trace_requested': a.trace_io,
               'gameplay_or_save_safety_verified': False}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))
    if not enabled or not frames or killed or exit_code != 0:
        raise SystemExit('offline instrumentation did not complete; inspect private log')


if __name__ == '__main__':
    main()
