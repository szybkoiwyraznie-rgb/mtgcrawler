#!/usr/bin/env python3
"""Experimental OE startup observation, not a gameplay/safety test.

Requires websocket-client and Pillow. Runs only on explicitly supplied private
copies. Captured VRAM is heuristic and may be stale, torn or not the front buffer.
"""
from __future__ import annotations
import argparse
import base64
import json
import os
from pathlib import Path
import socket
import subprocess
import time

from PIL import Image
import websocket


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--binary', type=Path, required=True)
    ap.add_argument('--iso-copy', type=Path, required=True)
    ap.add_argument('--home-copy', type=Path, required=True, help='isolated copy of HOME with .ppsspp DLC/saves')
    ap.add_argument('--output', type=Path, required=True, help='new private directory; contains game imagery')
    ap.add_argument('--samples', type=int, default=10)
    ap.add_argument('--interval', type=float, default=2.0)
    ap.add_argument('--press-circle', action='store_true', help='press circle before each sample')
    ap.add_argument('--accept-local-debugger-risk', action='store_true', help='confirm debugger port cannot be reached externally')
    args = ap.parse_args()
    if not args.accept_local_debugger_risk:
        ap.error('confirm local debugger isolation; loopback can be proxied by containers')
    if not 1 <= args.samples <= 100 or not 0.5 <= args.interval <= 30:
        ap.error('samples must be 1..100 and interval 0.5..30 seconds')
    binary, iso, home = (x.resolve(strict=True) for x in (args.binary, args.iso_copy, args.home_copy))
    if home == Path.home().resolve() or not home.is_dir():
        ap.error('HOME must be an isolated directory, not the real home')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sock = socket.socket(socket.AF_INET6)
    sock.bind(('::1', 0))
    port = sock.getsockname()[1]
    sock.close()  # Small bind race: only run this probe in an isolated environment.
    env = dict(os.environ, HOME=str(home), PPSSPP_RESEARCH_THROTTLE='1')
    timeout = max(120, int(args.samples * (args.interval + 5) + 30))
    with (out / 'emulator.log').open('w', encoding='utf-8') as log:
        proc = subprocess.Popen([str(binary), str(iso), '--graphics=software',
                                 f'--timeout={timeout}', f'--debugger={port}'],
                                env=env, stdout=log, stderr=log)
        ws = None
        try:
            for _ in range(40):
                if proc.poll() is not None:
                    raise RuntimeError(f'emulator exited early: {proc.returncode}')
                try:
                    ws = websocket.create_connection(f'ws://[::1]:{port}/debugger', timeout=2,
                                                     http_proxy_host=None)
                    break
                except (OSError, websocket.WebSocketException):
                    time.sleep(.25)
            if ws is None:
                raise RuntimeError('debugger connection failed')
            ws.settimeout(10)

            def call(event, **params):
                ticket = str(time.monotonic_ns())
                ws.send(json.dumps(dict(event=event, ticket=ticket, **params)))
                while True:
                    result = json.loads(ws.recv())
                    if result.get('ticket') == ticket:
                        if result.get('event') == 'error':
                            raise RuntimeError(result.get('message', 'debugger error'))
                        return result

            print('Game status:', call('game.status').get('game', {}), flush=True)
            print('Initial CPU status:', call('cpu.status'), flush=True)
            ws.send(json.dumps({'event': 'cpu.resume'}))  # no immediate ticket response
            for sample in range(args.samples):
                time.sleep(args.interval)
                if args.press_circle:
                    call('input.buttons.press', button='circle', duration=30)
                for address in (0x04000000, 0x04044000):
                    result = call('memory.read', address=address, size=512 * 272 * 2)
                    raw = base64.b64decode(result['base64'], validate=True)
                    if len(raw) != 512 * 272 * 2:
                        raise RuntimeError('unexpected VRAM byte count')
                    image = Image.new('RGB', (480, 272))
                    pixels = image.load()
                    for y in range(272):
                        for x in range(480):
                            off = 2 * (y * 512 + x)
                            value = raw[off] | raw[off + 1] << 8
                            pixels[x, y] = ((value & 31) * 255 // 31,
                                            ((value >> 5) & 31) * 255 // 31,
                                            ((value >> 10) & 31) * 255 // 31)
                    image.save(out / f'vram-{sample:03}-{address:08x}.png')
                print(f'sample {sample + 1}/{args.samples} (two unsynchronized VRAM candidates)', flush=True)
        finally:
            if ws is not None:
                ws.close()
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    print('No gameplay outcome or compatibility conclusion is implied.')


if __name__ == '__main__':
    main()
