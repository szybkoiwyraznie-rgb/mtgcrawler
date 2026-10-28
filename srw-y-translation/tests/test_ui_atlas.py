"""Drawing Polish into a UI atlas, and the kit that proves the files were replaced.

A menu label is a picture, so the only way to check the work is on the pixels: the label
has to land inside its own cell, leave the neighbours alone, and re-encode to exactly the
same number of bytes — a texture occupies a fixed slot in the archive, so anything else
would move everything after it.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from PIL import Image, ImageDraw  # noqa: E402

from build_pl_ui_atlas import BC7, draw_labels, to_bc7  # noqa: E402
from pl_kit import write_kit  # noqa: E402


def blank_atlas(columns: int, rows: int, cell=(352, 64)) -> Image.Image:
    return Image.new('RGBA', (cell[0] * columns, cell[1] * rows), (0, 0, 0, 0))


def boxes_for(columns: int, rows: int, cell=(352, 64)) -> dict[int, tuple[int, int, int, int]]:
    """Cell rects the way the sprites report them: bottom-left origin."""
    boxes = {}
    for row in range(rows):
        for column in range(columns):
            boxes[row * columns + column] = (column * cell[0], (rows - 1 - row) * cell[1],
                                             cell[0], cell[1])
    return boxes


def test_bc7_is_one_byte_per_pixel():
    """The stream slot cannot grow, so the encoder has to be fixed-rate."""
    image = blank_atlas(1, 1)
    encoded = to_bc7(image)
    assert BC7 == 25
    assert len(encoded) == image.width * image.height


def test_labels_land_in_their_own_cell_and_nowhere_else():
    columns, rows = 2, 3
    image = blank_atlas(columns, rows)
    ImageDraw.Draw(image).rectangle([0, 0, 3, 3], fill=(255, 255, 255, 255))
    boxes = boxes_for(columns, rows)
    out = draw_labels(image, boxes, ['Misje', 'Personalizacja'], columns)

    width = image.width
    for index, (x, y, w, h) in boxes.items():
        top = out.height - y - h
        cell = out.crop((x, top, x + w, top + h))
        assert cell.getbbox() is not None, f'komórka {index} jest pusta'
        assert cell.getbbox()[0] > 2 and cell.getbbox()[2] < w - 2
    # nothing outside the grid moved, and the marker in the first cell is gone
    assert out.getpixel((width - 1, 0))[3] == 0
    assert out.getpixel((1, 1))[3] == 0


def test_kit_verifies_the_copy_and_says_so(tmp_path):
    """`RAPORT.txt` is the difference between 'nie zadziałało' and 'nie skopiowało się'."""
    bundle = tmp_path / 'aaaabbbb.bundle'
    bundle.write_bytes(b'x' * 16)
    kit = write_kit(tmp_path / 'kit', {'aaaabbbb.bundle': bundle}, r'D:\Gra', '# test',
                    hashes={'aaaabbbb.bundle': 'ab' * 32})
    patch = (Path(kit['kit']) / 'PATCH_PL.bat').read_bytes()
    patch.decode('ascii')
    assert b'\r\n' in patch and b'\n\n' not in patch.replace(b'\r\n', b'\n')
    text = patch.decode('ascii')
    assert 'certutil -hashfile' in text
    assert 'AB' * 32 in text.upper()
    assert 'RAPORT.txt' in text
    assert (Path(kit['kit']) / 'COFNIJ.bat').is_file()
