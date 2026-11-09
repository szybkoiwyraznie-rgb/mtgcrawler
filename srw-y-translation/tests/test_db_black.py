"""Black pixels in the texture's own format: size, decode-back, refusals."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import db_black  # noqa: E402


@pytest.mark.parametrize('fmt', [db_black.BC7, db_black.BC1, db_black.BC3])
def test_compressed_black_keeps_the_slot_and_decodes_back_to_black(fmt):
    width, height = 64, 32
    data = db_black.black_bytes(fmt, width, height)
    assert len(data) == db_black.expected_size(fmt, width, height)
    assert db_black.verify_black(fmt, data, width, height) is True
    # BC7 quantises alpha to seven bits, so 255 comes back as 254 — still opaque.
    assert db_black.ALPHA_MIN <= 254


@pytest.mark.parametrize('fmt', [db_black.RGBA32, db_black.RGB24])
def test_raw_black_is_opaque(fmt):
    data = db_black.black_bytes(fmt, 8, 4)
    assert len(data) == db_black.expected_size(fmt, 8, 4)
    assert db_black.verify_black(fmt, data, 8, 4) is True


def test_a_white_texture_is_not_mistaken_for_black():
    import etcpak
    white = etcpak.compress_bc7(b'\xff\xff\xff\xff' * (16 * 16), 16, 16)
    assert db_black.verify_black(db_black.BC7, white, 16, 16) is False


def test_odd_sizes_round_up_to_whole_blocks():
    # 1920x1080 is not a multiple of 4 in height? it is; 1918x1078 is not.
    assert db_black.expected_size(db_black.BC7, 1918, 1078) == 480 * 270 * 16
    assert db_black.expected_size(db_black.RGBA32, 10, 3) == 120


def test_unsupported_format_is_refused_with_a_readable_message():
    with pytest.raises(ValueError, match='nieobsługiwany format'):
        db_black.black_bytes(63, 16, 16)          # RGBAFloat: not a slot we can fill
    assert not db_black.is_supported(63)
    assert db_black.format_name(db_black.BC7) == 'BC7'


def test_full_hd_background_fits_a_bc7_slot():
    assert db_black.expected_size(db_black.BC7, 1920, 1080) == 1920 * 1080
