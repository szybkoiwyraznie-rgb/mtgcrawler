from __future__ import annotations

import random
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import crilayla  # noqa: E402

TRAILER = bytes(range(256))


def _length_bits(length: int) -> list[int]:
    """Bits for a back-reference length (inverse of the decoder's chunk reading)."""
    bits: list[int] = []
    remaining = length - 3
    all_max = True
    for width in (2, 3, 5):
        maximum = (1 << width) - 1
        if remaining < maximum:
            bits += [(remaining >> (width - 1 - i)) & 1 for i in range(width)]
            remaining = 0
            all_max = False
            break
        bits += [1] * width
        remaining -= maximum
    if all_max:
        while remaining >= 255:
            bits += [1] * 8
            remaining -= 255
        bits += [(remaining >> (7 - i)) & 1 for i in range(8)]
    return bits


def encode(original: bytes) -> bytes:
    """Greedy test encoder: writes the CRILAYLA stream the decoder reads backwards."""
    out = TRAILER + original
    position = len(out) - 1
    decode_order: list[int] = []
    while position >= len(TRAILER):
        best = (0, 0)  # (length, reference)
        for reference in range(position + 3, min(len(out), position + 3 + (1 << 13))):
            length = 0
            while (
                length < 200
                and position - length >= len(TRAILER)
                and reference - length < len(out)
                and out[position - length] == out[reference - length]
            ):
                length += 1
            if length >= 3 and length > best[0]:
                best = (length, reference)
        if best[0] >= 3:
            length, reference = best
            offset = reference - position - 3
            decode_order += [1] + [(offset >> (12 - i)) & 1 for i in range(13)]
            decode_order += _length_bits(length)
            position -= length
        else:
            byte = out[position]
            decode_order += [0] + [(byte >> (7 - i)) & 1 for i in range(8)]
            position -= 1
    while len(decode_order) % 8:
        decode_order.append(0)
    packed = [
        int("".join(str(bit) for bit in decode_order[i : i + 8]), 2)
        for i in range(0, len(decode_order), 8)
    ]
    stream = bytes(reversed(packed))
    return b"CRILAYLA" + struct.pack("<II", len(original), len(stream)) + stream + TRAILER


class CrilaylaTests(unittest.TestCase):
    def test_round_trip_of_literals_and_back_references(self):
        original = b"SRW OE text block, SRW OE text block, " * 4 + bytes(range(40)) + b"\x00" * 300
        blob = encode(original)

        decoded = crilayla.decompress(blob)

        self.assertEqual(decoded.data[:TRAILER.__len__()], TRAILER)
        self.assertEqual(decoded.data[TRAILER.__len__():], original)
        self.assertEqual(len(decoded.data), len(original) + 0x100)
        self.assertEqual(decoded.stream_size, len(blob) - 16 - 0x100)

    def test_random_bytes_round_trip(self):
        rng = random.Random(7)
        original = bytes(rng.choice(b"abcde") for _ in range(3000)) + bytes(rng.randrange(256) for _ in range(500))
        self.assertEqual(crilayla.decompress(encode(original)).data[0x100:], original)

    def test_detects_magic_and_rejects_other_data(self):
        self.assertTrue(crilayla.is_crilayla(encode(b"abc")[:8]))
        self.assertFalse(crilayla.is_crilayla(b"CPK " + b"0" * 12))
        with self.assertRaises(crilayla.CrilaylaError):
            crilayla.decompress(b"CPK " + b"0" * 40)

    def test_truncated_stream_is_an_error_not_a_guess(self):
        blob = encode(b"abcdefghij" * 20)
        truncated = blob[:16] + blob[16:-0x100][:4] + blob[-0x100:]
        with self.assertRaises(crilayla.CrilaylaError):
            crilayla.decompress(truncated)


class CrilaylaEntryTests(unittest.TestCase):
    def test_decoded_entry_is_written_and_counted_and_a_bad_one_is_recorded(self):
        import tempfile

        import run_pipeline  # noqa: E402

        original = b"script line one. script line two. " * 10
        blob = encode(original)
        good = {"name": "r050sqs.bsb", "toc_index": 3, "extract_size": len(original) + 0x100}
        bad = {"name": "r051sqs.bsb", "toc_index": 4, "extract_size": 999999}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "hidden"
            result: dict = {}
            run_pipeline._decode_crilayla_entry(good, blob, folder, result)
            run_pipeline._decode_crilayla_entry(bad, blob, folder, result)
            written = sorted(folder.iterdir())
            payload = written[0].read_bytes() if written else b""

        summary = result["crilayla"]
        self.assertEqual(summary["attempted"], 2)
        self.assertEqual(summary["decoded"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["clean_end"], 1)
        self.assertEqual([path.name for path in written], ["00003_r050sqs.bsb"])
        self.assertEqual(payload[0x100:], original)
        self.assertIn("the table says", summary["samples"][-1]["error"])


if __name__ == "__main__":
    unittest.main()
