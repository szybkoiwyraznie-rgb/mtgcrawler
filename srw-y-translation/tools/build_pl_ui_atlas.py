#!/usr/bin/env python3
"""Polish into UI atlases — the menus are pictures, not text.

The main menu (`Mission`, `Customization`, `Unlock STG Memory`, `Database`) is not a
string anywhere.  It is an atlas: one BC7 texture 1760x512 with a grid of 352x64 cells,
eight rows (two states) by five columns (Japanese, English, Korean, Chinese, Chinese).
The game shows the column of the chosen language.  So there is nothing to replace — the
words have to be **drawn**.

Drawing works because a texture lives outside the serialized file: the pixels sit in the
`.resS` stream at a fixed offset and the format is block-compressed at a fixed rate, so a
redrawn atlas is exactly the same number of bytes.  The bundle is then rebuilt with
`tools/srw_y_rebuild.py`, which carries the stream through and fails if any object moved.

The whole grid is redrawn in Polish, every column: whatever language the game thinks it
is running in, the player sees Polish.

    python3 tools/build_pl_ui_atlas.py --check
    python3 tools/build_pl_ui_atlas.py --kit --zip build/ui_atlas/TEST4_MENU_PL.zip
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import etcpak  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from build_pl_table_patch import GAME_AA, plain_of, source_of  # noqa: E402
from lz4_block_map import decompress_blocks, parse_container  # noqa: E402
from pl_kit import write_kit  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402
from srw_y_rebuild import objects_of, rebuild_plain  # noqa: E402

LOCAL = HERE / 'local'
TRANS = HERE / 'translations' / 'ui_atlas_pl.json'
BUILD = HERE / 'build' / 'ui_atlas'
FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
BC7 = 25
RGBA32 = 4
PAD = 24


def streams_of(plain: bytes) -> tuple[dict, list[bytes]]:
    """Container layout plus every stream in it, in file-table order."""
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    return layout, [blob[off:off + size] for off, size, _f, _n in layout['files']]


def atlas_of(env, name: str):
    """(object, typetree) of the texture called `name`."""
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        tree = obj.read_typetree()
        if tree.get('m_Name') == name:
            return obj, tree
    return None, None


def cells_of(env, texture: str, columns: int) -> dict[int, tuple[int, int, int, int]]:
    """Cell index -> (x, y, w, h) in texture pixels, read from the sprite rects.

    The sprites are the authority on the grid: `TOP_Font_7` is row 1, column 2, and its
    rect says where.  Nothing here is inferred from the picture.
    """
    boxes = {}
    for obj in env.objects:
        if obj.type.name != 'Sprite':
            continue
        sprite = obj.read()
        name = sprite.m_Name
        if not name.startswith(f'{texture}_'):
            continue
        suffix = name.rsplit('_', 1)[-1]
        if not suffix.isdigit():
            continue
        rect = sprite.m_Rect
        boxes[int(suffix)] = (int(rect.x), int(rect.y), int(rect.width), int(rect.height))
    for index in boxes:
        if index // columns not in range(1000):
            raise SystemExit(f'{texture}: dziwny indeks {index}')
    return boxes


def draw_labels(image: Image.Image, boxes: dict[int, tuple[int, int, int, int]],
                labels: list[str], columns: int, pad: int = PAD) -> Image.Image:
    """Redraw each cell with the Polish label for its row.

    `pad` is the total width kept clear of pixels, so the text never touches the border.
    Small cells (the 60x32 terrain chips) need a smaller pad than the wide menu cells,
    otherwise the font shrinks for no reason.
    """
    width, height = image.size
    draw = ImageDraw.Draw(image)
    for index, (x, y, w, h) in sorted(boxes.items()):
        row = index // columns
        label = labels[row % len(labels)]
        # Unity sprite rects start at the bottom-left; PIL draws from the top-left
        top = height - y - h
        draw.rectangle([x, top, x + w, top + h], fill=(0, 0, 0, 0))
        size = int(h * 0.72)
        while size > 8:
            font = ImageFont.truetype(str(FONT), size)
            left, _top, right, _bottom = draw.textbbox((0, 0), label, font=font)
            if right - left <= w - pad:
                break
            size -= 1
        font = ImageFont.truetype(str(FONT), size)
        draw.text((x + w / 2, top + h / 2), label, font=font, fill=(255, 255, 255, 255),
                  anchor='mm')
    return image


def decode_texture(fmt: int, pixels: bytes, width: int, height: int) -> Image.Image:
    """Stream bytes -> RGBA in reading order.

    Both BC7 and RGBA32 keep their rows bottom-up, so the decode is flipped once here.
    Skipping that flip was a real bug: the labels were drawn into mirrored rows, the
    original ones stayed visible, and nothing could tell it from "the game ignores us".
    """
    if fmt == BC7:
        image = Image.open(io.BytesIO(_png(pixels, width, height))).convert('RGBA')
    else:
        image = Image.frombytes('RGBA', (width, height), pixels)
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def encode_texture(fmt: int, image: Image.Image) -> bytes:
    """RGBA in reading order -> stream bytes, undoing the flip of `decode_texture`."""
    flipped = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    return to_bc7(flipped) if fmt == BC7 else flipped.tobytes()


def to_bc7(image: Image.Image) -> bytes:
    """Encode RGBA to BC7; one byte per pixel, so the stream keeps its size."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    return etcpak.compress_bc7(image.tobytes(), image.width, image.height)


def patch(stem: str, spec: dict, start: Path, out_dir: Path, preview: Path | None = None) -> dict:
    plain = plain_of(stem, start)
    layout, streams = streams_of(plain)
    import UnityPy
    import tempfile

    workdir = Path(tempfile.mkdtemp())
    for (_off, _size, _f, name), data in zip(layout['files'], streams):
        (workdir / name).write_bytes(data)
    env = UnityPy.load(str(workdir / layout['files'][0][3]))

    new_streams, done = {}, []
    for texture_name, texture_spec in spec['textures'].items():
        obj, tree = atlas_of(env, texture_name)
        if obj is None:
            raise SystemExit(f'{stem}: brak tekstury {texture_name}')
        fmt = tree['m_TextureFormat']
        if fmt not in (BC7, RGBA32):
            raise SystemExit(f'{stem}: {texture_name} ma format {fmt}, '
                             f'oczekiwano BC7 ({BC7}) albo RGBA32 ({RGBA32})')
        stream = tree['m_StreamData']
        offset, size = int(stream['offset']), int(stream['size'])
        stream_name = stream['path'].rsplit('/', 1)[-1]
        index = next((i for i, entry in enumerate(layout['files'])
                      if entry[3] == stream_name), None)
        if index is None:
            raise SystemExit(f'{stem}: nie ma strumienia {stream_name}')
        width, height = tree['m_Width'], tree['m_Height']
        # BC7 is one byte per pixel; RGBA32 is four. Either way the stream must already be
        # exactly the size the format implies, or the byte-for-byte swap is off the table.
        stride = 1 if fmt == BC7 else 4
        if size != width * height * stride:
            raise SystemExit(f'{stem}: {texture_name} format {fmt} nie pasuje do strumienia')

        data = bytearray(streams[index] if index not in new_streams else new_streams[index])
        pixels = data[offset:offset + size]
        image = decode_texture(fmt, pixels, width, height)
        boxes = cells_of(env, texture_name, texture_spec['columns'])
        if not boxes:
            raise SystemExit(f'{stem}: {texture_name} nie ma sprite\'ów')
        before = image.tobytes()
        image = draw_labels(image, boxes, texture_spec['labels'], texture_spec['columns'],
                            int(texture_spec.get('pad', PAD)))
        encoded = encode_texture(fmt, image)
        if len(encoded) != size:
            raise SystemExit(f'{stem}: format {fmt} dał {len(encoded)} B, a strumień {size} B')
        data[offset:offset + size] = encoded
        new_streams[index] = bytes(data)
        done.append({'texture': texture_name, 'width': width, 'height': height,
                     'cells': len(boxes), 'labels': texture_spec['labels'],
                     'changed_pixels': before != image.tobytes()})
        if preview is not None:
            preview.mkdir(parents=True, exist_ok=True)
            image.save(preview / f'{texture_name}_pl.png')

    if not new_streams:
        raise SystemExit(f'{stem}: nic do podmiany')
    new_plain, report = rebuild_plain(stem, plain, {}, new_streams)

    # read the result back: the drawn pixels must be there, and every object untouched
    check_layout, check_streams = streams_of(new_plain)
    for index, expected in new_streams.items():
        if check_streams[index] != expected:
            raise SystemExit(f'{stem}: strumień {index} nie wrócił z przebudowy')
    if objects_of(b''.join(part[2] for part in decompress_blocks(plain, layout))) != \
            objects_of(b''.join(part[2] for part in decompress_blocks(new_plain, check_layout))):
        raise SystemExit(f'{stem}: obiekty zmieniły się przy podmianie tekstury')

    cipher = encrypt(f'{stem}.bundle', new_plain)
    if decrypt(f'{stem}.bundle', cipher) != new_plain:
        raise SystemExit(f'{stem}: szyfrowanie nie odtwarza pliku')
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'{stem}.bundle'
    path.write_bytes(cipher)
    return {'stem': stem, 'start': str(start), 'path': str(path), 'textures': done,
            'original_size': start.stat().st_size, 'size': len(cipher),
            'changed_objects': report['changed_objects'],
            'sha256': hashlib.sha256(cipher).hexdigest()}


def _png(pixels: bytes, width: int, height: int) -> bytes:
    """BC7 block rows are top-down, so the decoded image needs no flip."""
    from texture2ddecoder import decode_bc7
    rgba = decode_bc7(pixels, width, height)
    image = Image.frombytes('RGBA', (width, height), rgba)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def build(trans: Path = TRANS, out_dir: Path = BUILD, base: Path | None = None,
          check: bool = False, preview: Path | None = None) -> list[dict]:
    data = json.loads(Path(trans).read_text(encoding='utf-8'))
    rows = []
    for stem, spec in sorted(data['bundles'].items()):
        start, origin = source_of(stem, base)
        if check:
            plain = plain_of(stem, start)
            layout, streams = streams_of(plain)
            import tempfile

            import UnityPy
            workdir = Path(tempfile.mkdtemp())
            for (_off, _size, _f, name), blob in zip(layout['files'], streams):
                (workdir / name).write_bytes(blob)
            env = UnityPy.load(str(workdir / layout['files'][0][3]))
            found = []
            for texture_name, texture_spec in spec['textures'].items():
                obj, tree = atlas_of(env, texture_name)
                if obj is None:
                    found.append({'texture': texture_name, 'error': 'brak tekstury'})
                    continue
                boxes = cells_of(env, texture_name, texture_spec['columns'])
                found.append({'texture': texture_name, 'width': tree['m_Width'],
                              'height': tree['m_Height'], 'format': tree['m_TextureFormat'],
                              'stream': tree['m_StreamData'], 'cells': len(boxes)})
            rows.append({'stem': stem, 'name': spec.get('file'), 'origin': origin,
                         'textures': found, 'labels': spec['textures']})
            continue
        rows.append(patch(stem, spec, start, out_dir, preview) | {'origin': origin})
    return rows


README = r"""# Test 4 — polskie menu jako obrazki

Główne menu gry **nie jest tekstem**. Gra rysuje je z atlasu: jeden obrazek z napisami
w pięciu językach. Dlatego podmiana tekstu nic tam nie zmieniała. W tym teście obrazek
jest przerysowany po polsku — we wszystkich pięciu kolumnach, żeby język gry nie miał
znaczenia.

## Co zrobić

1. Rozpakuj na Pulpit.
2. Kliknij **PATCH_PL.bat**.
3. Skrypt na koniec wypisze **OK** i zapisze na Pulpicie plik `RAPORT.txt`.
   Jeśli wypisze **BLAD**, od razu wiadomo, że pliki nie weszły — wyślij mi ten raport.
4. Uruchom grę i dojdź do głównego menu.

## Co powinno być widać

**Na ekranie tytułowym:** `Naciśnij klawisz` zamiast `Press Any Key`.

**W menu w grze** (to menu, które pojawia się po wybraniu trybu gry, nie na ekranie
tytułowym) cztery pozycje przerysowane na polski:

| było | ma być |
|---|---|
| Mission | **Misje** |
| Customization | **Personalizacja** |
| Unlock STG Memory | **Odblokuj STG** |
| Database | **Baza danych** |

Jeśli do tego menu nie dojdziesz bez zapisu gry — nie szkodzi. Ten test ma sens
przede wszystkim dla pierwszej linijki: czy `Naciśnij klawisz` się zmienił i czy
skrypt wypisał **OK**. To odpowiada na pytanie, którego poprzedni test nie rozstrzygnął.

## Jeśli nadal nic się nie zmieni

Kliknij **PATCH_PL.bat** i popatrz na ostatnie linijki okna — każda kończy się **OK** albo
**BLAD**. Skrypt zapisuje to samo na Pulpit do `RAPORT.txt` (razem z godziną).
**BLAD** znaczy, że plik w grze jest inny niż ten, który wysłałem — czyli gra ma inną
wersję niż ta, z której buduję. Wtedy wyślij mi `RAPORT.txt`.

## Cofnięcie

**COFNIJ.bat** przywraca oryginały.
"""


def write_kit_for(rows: list[dict], out_dir: Path = BUILD, zip_path: Path | None = None,
                  extra: list[Path] | None = None) -> dict:
    """One kit for the whole test; `extra` adds bundles built by another tool."""
    bundles = {f'{row["stem"]}.bundle': Path(row['path']) for row in rows}
    for path in extra or []:
        bundles[Path(path).name] = Path(path)
    hashes = {name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
              for name, path in bundles.items()}
    return write_kit(Path(out_dir) / 'kit', bundles, GAME_AA, README, zip_path, hashes)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--trans', type=Path, default=TRANS)
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--base', type=Path, default=None)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--kit', action='store_true')
    parser.add_argument('--zip', type=Path, default=None)
    parser.add_argument('--preview', type=Path, default=None)
    parser.add_argument('--extra', nargs='*', type=Path, default=[],
                        help='dodatkowe gotowe bundle do tego samego kita')
    args = parser.parse_args(argv)
    rows = build(args.trans, args.out_dir, args.base, args.check, args.preview)
    if args.kit and not args.check:
        kit = write_kit_for(rows, args.out_dir, args.zip, args.extra)
        print(f"kit: {kit['kit']} ({len(kit['files'])} plików), zip {kit.get('zip')} "
              f"{kit.get('zip_size', 0):,} B")
    for row in rows:
        if args.check:
            print(f"{row['stem']} ({row['name']}, {row['origin']}):")
            for item in row['textures']:
                print(f"   {item}")
            continue
        print(f"{row['stem']} ({row['origin']}): {row['original_size']:,} -> "
              f"{row['size']:,} B")
        for item in row['textures']:
            print(f"   {item['texture']} {item['width']}x{item['height']}: "
                  f"{item['cells']} komórek -> {item['labels']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
