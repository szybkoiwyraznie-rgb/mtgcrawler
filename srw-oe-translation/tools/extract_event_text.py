#!/usr/bin/env python3
"""Deterministic read-only text-unit extractor for SRW OE event BIN files.

The candidate audit selects non-overlapping ``FF FF ... 00 00`` envelopes. This
tool keeps that exact walk, partitions every BIN completely into segments, and
exports each Japanese-script candidate as a text unit with the same ``file@HEX``
ID used by ``audit_event_candidates.py``. Other selected envelopes, unselected
bytes, and any unterminated tail stay opaque and are preserved byte-for-byte.

Text units use a lossless view: CP932 characters that round-trip byte-exactly
stay readable, LF/CR stay literal, a literal ``{`` is written as ``{7B}``, and
every other byte that is not a stable character (C0/DEL/C1 controls, private-use
mappings, undecodable bytes, or valid pairs that do not re-encode exactly) is
written as an uppercase ``{XX}`` or ``{XXXX}`` token holding the raw bytes.
Single-NUL suffixes are kept as raw bytes and a token view for review.

Boundaries are heuristic and unvalidated. This tool does not parse formats,
decide field meanings, or reinsert text. It prints only counts and check results;
exports contain decoded proprietary text and belong in an ignored local folder.

Example (sample restored under the ignored local/ folder)::

    python3 tools/extract_event_text.py local/eventP01.zip --export-dir local/event_text
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from audit_event_candidates import Candidate, inputs_from_path, scan_bin_with_stats

MARKER = b"\xff\xff"
STOP = b"\x00\x00"
SCHEMA = "srw-oe-event-text-export/1"
EXPORT_FILES = ("manifest.json", "units.jsonl", "segments.jsonl")
SEGMENT_KINDS = ("gap", "text_unit", "marker_span", "unterminated_tail")
TOKEN_RE = re.compile(r"\{([0-9A-F]{2}|[0-9A-F]{4})\}")
TOKEN_REASON_FLAGS = {
    "control": "control_token",
    "pua": "pua_token",
    "invalid": "invalid_cp932_token",
    "nonroundtrip": "nonroundtrip_cp932_token",
}


@dataclass(frozen=True)
class ViewItem:
    """One byte or byte pair as rendered in a lossless text view."""

    relative_offset: int
    raw: bytes
    text: str
    is_token: bool
    reason: str  # ascii, line_break, literal, brace, control, pua, invalid, nonroundtrip


@dataclass(frozen=True)
class Envelope:
    """A literal FF FF start and the first following 00 00 stop."""

    marker_offset: int
    start_offset: int
    pair_offset: int

    @property
    def end_offset(self) -> int:
        return self.pair_offset + len(STOP)


def _decode_one_char(raw: bytes) -> Optional[str]:
    """Return the single CP932 character for ``raw`` if it decodes strictly."""
    try:
        text = raw.decode("cp932")
    except UnicodeDecodeError:
        return None
    return text if len(text) == 1 else None


def _is_byte_exact(char: str, raw: bytes) -> bool:
    try:
        return char.encode("cp932") == raw
    except UnicodeEncodeError:
        return False


def _is_lead_byte(byte: int) -> bool:
    return 0x81 <= byte <= 0x9F or 0xE0 <= byte <= 0xFC


def _token(relative_offset: int, raw: bytes, reason: str) -> ViewItem:
    return ViewItem(relative_offset, raw, "{" + raw.hex().upper() + "}", True, reason)


def _token_reason(char: str, raw: bytes) -> Optional[str]:
    """Return why a decoded character must be a token, or None if it is literal."""
    category = unicodedata.category(char)
    if category == "Co":
        return "pua"
    if category in {"Cc", "Cs", "Cn"}:
        return "control"
    if not _is_byte_exact(char, raw):
        return "nonroundtrip"
    return None


def to_view_items(raw: bytes) -> list[ViewItem]:
    """Split raw bytes into literal characters and placeholder tokens."""
    items: list[ViewItem] = []
    position = 0
    while position < len(raw):
        byte = raw[position]
        if byte in (0x0A, 0x0D):
            items.append(ViewItem(position, raw[position : position + 1], chr(byte), False, "line_break"))
            position += 1
            continue
        if 0x20 <= byte <= 0x7E and byte != 0x7B:
            items.append(ViewItem(position, raw[position : position + 1], chr(byte), False, "ascii"))
            position += 1
            continue
        if byte == 0x7B:
            items.append(_token(position, raw[position : position + 1], "brace"))
            position += 1
            continue
        if _is_lead_byte(byte) and position + 1 < len(raw):
            pair = raw[position : position + 2]
            char = _decode_one_char(pair)
            if char is not None:
                reason = _token_reason(char, pair)
                if reason is None:
                    items.append(ViewItem(position, pair, char, False, "literal"))
                else:
                    items.append(_token(position, pair, reason))
                position += 2
                continue
        single = raw[position : position + 1]
        char = _decode_one_char(single)
        if char is None:
            items.append(_token(position, single, "invalid"))
        else:
            reason = _token_reason(char, single)
            if reason is None:
                items.append(ViewItem(position, single, char, False, "literal"))
            else:
                items.append(_token(position, single, reason))
        position += 1
    return items


def render_view(items: list[ViewItem]) -> str:
    return "".join(item.text for item in items)


def to_view(raw: bytes) -> str:
    return render_view(to_view_items(raw))


def from_view(text: str) -> bytes:
    """Invert ``to_view`` for the lossless placeholder syntax."""
    out = bytearray()
    position = 0
    while position < len(text):
        char = text[position]
        if char == "{":
            match = TOKEN_RE.match(text, position)
            if match is None:
                raise ValueError(f"malformed control token at view index {position}")
            out += bytes.fromhex(match.group(1))
            position = match.end()
            continue
        category = unicodedata.category(char)
        if category == "Cc" and char not in "\r\n":
            raise ValueError(f"raw control character at view index {position}; use a {{XX}} token")
        if category in {"Co", "Cs", "Cn"}:
            raise ValueError(f"private-use or unassigned character at view index {position}; use a token")
        try:
            out += char.encode("cp932")
        except UnicodeEncodeError as exc:
            raise ValueError(f"character not representable in CP932 at view index {position}") from exc
        position += 1
    return bytes(out)


def select_envelopes(data: bytes) -> tuple[list[Envelope], Optional[int]]:
    """Replicate the candidate scanner's greedy walk without any text filter.

    Returns the selected envelopes and the offset of an unterminated marker tail,
    if the walk ends on a marker with no following ``00 00`` stop.
    """
    envelopes: list[Envelope] = []
    position = 0
    while position < len(data) - 1:
        if data[position : position + 2] != MARKER:
            position += 1
            continue
        start = position + 2
        pair = data.find(STOP, start)
        if pair < 0:
            return envelopes, position
        envelopes.append(Envelope(position, start, pair))
        position = pair + 1
    return envelopes, None


def _hex(data: bytes) -> str:
    return data.hex(" ").upper()


def _unit_flags(candidate: Candidate, items: list[ViewItem], has_suffix: bool) -> list[str]:
    flags: list[str] = []
    if candidate.nested_ff_ff_markers:
        flags.append("nested_ff_ff_marker")
    if has_suffix:
        flags.append("single_nul_suffix")
    if candidate.prefix_japanese_codepoints == 1:
        flags.append("single_japanese_codepoint")
    if candidate.prefix_halfwidth_katakana_codepoints and not candidate.prefix_wide_japanese_codepoints:
        flags.append("halfwidth_katakana_only_match")
    for item in items:
        flag = TOKEN_REASON_FLAGS.get(item.reason)
        if flag and flag not in flags:
            flags.append(flag)
    return flags


def extract_file(name: str, data: bytes) -> tuple[dict, list[dict], list[dict]]:
    """Return (file record, segment records, unit records) for one BIN."""
    envelopes, tail = select_envelopes(data)
    candidates, scan_stats = scan_bin_with_stats(name, data)

    # The existing audit is the reference for which spans are text candidates.
    if scan_stats["spans_with_double_nul"] != len(envelopes):
        raise ValueError(f"{name}: envelope walk diverged from the candidate scanner")
    if scan_stats["consumed_ff_ff_markers"] != len(envelopes) + (tail is not None):
        raise ValueError(f"{name}: marker walk diverged from the candidate scanner")
    envelope_by_start = {envelope.start_offset: envelope for envelope in envelopes}
    candidate_by_start: dict[int, Candidate] = {}
    for candidate in candidates:
        envelope = envelope_by_start.get(candidate.start)
        if envelope is None or envelope.pair_offset != candidate.pair_offset:
            raise ValueError(f"{name}: candidate at {candidate.start:#x} is not a selected envelope")
        candidate_by_start[candidate.start] = candidate

    segments: list[dict] = []
    units: list[dict] = []

    def add_segment(kind: str, start: int, end: int, unit_id: Optional[str]) -> None:
        if end <= start:
            return
        segments.append(
            {
                "file": name,
                "index": len(segments),
                "kind": kind,
                "start_offset": start,
                "end_offset": end,
                "raw_hex": _hex(data[start:end]),
                "unit_id": unit_id,
            }
        )

    position = 0
    for envelope in envelopes:
        add_segment("gap", position, envelope.marker_offset, None)
        candidate = candidate_by_start.get(envelope.start_offset)
        if candidate is None:
            add_segment("marker_span", envelope.marker_offset, envelope.end_offset, None)
        else:
            unit_id = f"{name}@{envelope.start_offset:04X}"
            add_segment("text_unit", envelope.marker_offset, envelope.end_offset, unit_id)
            units.append(_unit_record(name, data, envelope, candidate, unit_id))
        position = envelope.end_offset
    if tail is not None:
        add_segment("gap", position, tail, None)
        add_segment("unterminated_tail", tail, len(data), None)
        position = len(data)
    add_segment("gap", position, len(data), None)

    file_record = {
        "file": name,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "segments": len(segments),
        "units": len(units),
    }
    return file_record, segments, units


def _unit_record(name: str, data: bytes, envelope: Envelope, candidate: Candidate, unit_id: str) -> dict:
    body = data[envelope.start_offset : envelope.pair_offset]
    first_nul = body.find(b"\x00")
    prefix = body if first_nul < 0 else body[:first_nul]
    suffix = b"" if first_nul < 0 else body[first_nul:]
    if prefix != candidate.text_bytes or suffix != (candidate.suffix or b""):
        raise ValueError(f"{unit_id}: prefix/suffix split diverged from the candidate scanner")

    items = to_view_items(prefix)
    source_text = render_view(items)
    if from_view(source_text) != prefix:
        raise RuntimeError(f"{unit_id}: placeholder codec failed to round-trip the prefix")

    tokens = []
    line_breaks = []
    char_index = 0
    for item in items:
        absolute = envelope.start_offset + item.relative_offset
        if item.is_token:
            tokens.append(
                {"at": char_index, "offset": absolute, "raw_hex": _hex(item.raw), "reason": item.reason}
            )
        elif item.reason == "line_break":
            line_breaks.append({"at": char_index, "offset": absolute, "raw_hex": _hex(item.raw)})
        char_index += len(item.text)

    # Suffixes are control/field bytes, so every byte is shown as a token.
    suffix_view = "".join("{%02X}" % byte for byte in suffix) if suffix else None
    return {
        "unit_id": unit_id,
        "file": name,
        "status": "unreviewed",
        "boundary_status": "heuristic_unvalidated",
        "marker_offset": envelope.marker_offset,
        "start_offset": envelope.start_offset,
        "text_end_offset": envelope.start_offset + len(prefix),
        "pair_offset": envelope.pair_offset,
        "source_text": source_text,
        "prefix_raw_hex": _hex(prefix),
        "suffix_offset": envelope.start_offset + len(prefix) if suffix else None,
        "suffix_raw_hex": _hex(suffix) if suffix else None,
        "suffix_view": suffix_view,
        "tokens": tokens,
        "line_breaks": line_breaks,
        "flags": _unit_flags(candidate, items, bool(suffix)),
        "nested_ff_ff_markers": candidate.nested_ff_ff_markers,
        "reviewer_note": "",
    }


def _bytes_by_kind(segments: list[dict]) -> Counter:
    totals: Counter = Counter()
    for segment in segments:
        totals[segment["kind"]] += segment["end_offset"] - segment["start_offset"]
    return totals


def build_export(input_path: Path) -> tuple[dict, list[dict], list[dict]]:
    """Extract every BIN from a ZIP, directory, or single file, in sorted order."""
    file_records: list[dict] = []
    segments: list[dict] = []
    units: list[dict] = []
    for name, data in inputs_from_path(input_path):
        file_record, file_segments, file_units = extract_file(name, data)
        file_records.append(file_record)
        segments.extend(file_segments)
        units.extend(file_units)
    if not file_records:
        raise ValueError("no .bin members found in the input")

    if input_path.is_dir():
        input_info = {"name": input_path.name, "kind": "directory", "sha256": None}
    else:
        kind = "zip" if input_path.suffix.lower() == ".zip" else "bin"
        digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
        input_info = {"name": input_path.name, "kind": kind, "sha256": digest}

    totals_by_kind = _bytes_by_kind(segments)
    token_counts: Counter = Counter()
    flag_counts: Counter = Counter()
    for unit in units:
        token_counts.update(token["reason"] for token in unit["tokens"])
        flag_counts.update(unit["flags"])
    manifest = {
        "schema": SCHEMA,
        "generator": "tools/extract_event_text.py",
        "input": input_info,
        "codec": {
            "name": "cp932-lossless-placeholder-view",
            "literal": "CP932 characters that round-trip byte-exactly, printable ASCII except brace, LF, CR",
            "tokens": "uppercase {XX} or {XXXX} with the raw bytes; a literal brace is {7B}",
        },
        "files": file_records,
        "totals": {
            "files": len(file_records),
            "bytes": sum(record["size"] for record in file_records),
            "segments": len(segments),
            "units": len(units),
            "bytes_by_kind": {kind: totals_by_kind.get(kind, 0) for kind in SEGMENT_KINDS},
            "tokens_by_reason": dict(sorted(token_counts.items())),
            "unit_flags": dict(sorted(flag_counts.items())),
        },
    }
    return manifest, units, segments


def _group_by_file(records: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for record in records:
        grouped.setdefault(record["file"], []).append(record)
    return grouped


def _verify_file(
    record: dict,
    file_segments: list[dict],
    file_units: list[dict],
    units_by_id: dict[str, dict],
    referenced: Counter,
    errors: list[str],
) -> None:
    name = record["file"]
    size = record["size"]
    if record.get("segments") != len(file_segments):
        errors.append(f"{name}: manifest segment count does not match the records")
    if record.get("units") != len(file_units):
        errors.append(f"{name}: manifest unit count does not match the records")

    expected_start = 0
    raw_parts: list[bytes] = []
    view_parts: list[bytes] = []
    for expected_index, segment in enumerate(file_segments):
        label = f"{name} segment {expected_index}"
        if segment["index"] != expected_index:
            errors.append(f"{label}: index is not contiguous")
        if segment["start_offset"] != expected_start:
            errors.append(f"{label}: gap or overlap at {segment['start_offset']}")
        if segment["end_offset"] <= segment["start_offset"]:
            errors.append(f"{label}: empty or reversed segment")
        if segment["kind"] not in SEGMENT_KINDS:
            errors.append(f"{label}: unknown kind {segment['kind']}")
        raw = bytes.fromhex(segment["raw_hex"])
        if len(raw) != segment["end_offset"] - segment["start_offset"]:
            errors.append(f"{label}: raw length does not match offsets")
        expected_start = segment["end_offset"]
        raw_parts.append(raw)

        if segment["kind"] != "text_unit":
            if segment["unit_id"] is not None:
                errors.append(f"{label}: non-text segment references a unit")
            view_parts.append(raw)
            continue

        unit = units_by_id.get(segment["unit_id"])
        if unit is None:
            errors.append(f"{label}: unknown unit {segment['unit_id']}")
            view_parts.append(raw)
            continue
        referenced[unit["unit_id"]] += 1
        if unit["file"] != name or unit["marker_offset"] != segment["start_offset"]:
            errors.append(f"{unit['unit_id']}: unit does not start at its segment")
        if unit["pair_offset"] + len(STOP) != segment["end_offset"]:
            errors.append(f"{unit['unit_id']}: unit does not end at its segment")
        prefix = bytes.fromhex(unit["prefix_raw_hex"])
        suffix = bytes.fromhex(unit["suffix_raw_hex"] or "")
        if raw != MARKER + prefix + suffix + STOP:
            errors.append(f"{unit['unit_id']}: segment bytes differ from unit fields")
        try:
            encoded = from_view(unit["source_text"])
        except ValueError as exc:
            errors.append(f"{unit['unit_id']}: source_text does not parse ({exc})")
            view_parts.append(raw)
            continue
        if encoded != prefix:
            errors.append(f"{unit['unit_id']}: source_text does not re-encode to the prefix bytes")
        if to_view(prefix) != unit["source_text"]:
            errors.append(f"{unit['unit_id']}: source_text is not the canonical view")
        view_parts.append(MARKER + encoded + suffix + STOP)

    if expected_start != size:
        errors.append(f"{name}: segments cover {expected_start} of {size} bytes")
    for label, rebuilt in (("raw", b"".join(raw_parts)), ("view", b"".join(view_parts))):
        if len(rebuilt) != size or hashlib.sha256(rebuilt).hexdigest() != record["sha256"]:
            errors.append(f"{name}: {label} rebuild does not match the source SHA-256")


def verify_records(manifest: dict, units: list[dict], segments: list[dict]) -> list[str]:
    """Check coverage, codec invariants, and no-change rebuilds from records alone."""
    errors: list[str] = []
    units_by_id: dict[str, dict] = {}
    for unit in units:
        if unit["unit_id"] in units_by_id:
            errors.append(f"duplicate unit id {unit['unit_id']}")
        units_by_id[unit["unit_id"]] = unit

    file_names = [record["file"] for record in manifest["files"]]
    if len(set(file_names)) != len(file_names):
        errors.append("duplicate file names in manifest")
    known_files = set(file_names)
    for record in segments:
        if record["file"] not in known_files:
            errors.append(f"{record['file']}: segment file is absent from the manifest")
    for unit in units:
        if unit["file"] not in known_files:
            errors.append(f"{unit['unit_id']}: unit file is absent from the manifest")

    segments_by_file = _group_by_file(segments)
    units_by_file = _group_by_file(units)
    referenced: Counter = Counter()
    for record in manifest["files"]:
        name = record["file"]
        file_segments = sorted(segments_by_file.get(name, []), key=lambda item: item["index"])
        try:
            _verify_file(record, file_segments, units_by_file.get(name, []), units_by_id, referenced, errors)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{name}: malformed export record ({exc})")

    for unit_id in units_by_id:
        if referenced[unit_id] != 1:
            errors.append(f"{unit_id}: referenced by {referenced[unit_id]} segments, expected 1")
    return errors


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_export(export_dir: Path, manifest: dict, units: list[dict], segments: list[dict]) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    with (export_dir / "manifest.json").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write_jsonl(export_dir / "units.jsonl", units)
    _write_jsonl(export_dir / "segments.jsonl", segments)


def read_export(export_dir: Path) -> tuple[dict, list[dict], list[dict]]:
    manifest = json.loads((export_dir / "manifest.json").read_text(encoding="utf-8"))
    units = [
        json.loads(line)
        for line in (export_dir / "units.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    segments = [
        json.loads(line)
        for line in (export_dir / "segments.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    return manifest, units, segments


def _validate_export_dir(input_path: Path, export_dir: Path) -> None:
    source = input_path.resolve()
    destination = export_dir.resolve()
    if destination == source:
        raise ValueError("export directory may not be the input")
    if input_path.is_dir() and source in destination.parents:
        raise ValueError("export directory must be outside the input directory")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="event ZIP, extracted directory, or one BIN file")
    parser.add_argument(
        "--export-dir",
        type=Path,
        help="write manifest.json, units.jsonl, and segments.jsonl here; use an ignored local folder",
    )
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")

    try:
        if args.export_dir:
            _validate_export_dir(args.input, args.export_dir)
        manifest, units, segments = build_export(args.input)
    except (OSError, zipfile.BadZipFile, ValueError, RuntimeError) as exc:
        parser.error(str(exc))

    checks: list[tuple[str, list[str]]] = [("in-memory records", verify_records(manifest, units, segments))]
    if args.export_dir:
        try:
            write_export(args.export_dir, manifest, units, segments)
        except OSError as exc:
            parser.error(f"could not write export: {exc}")
        try:
            disk_manifest, disk_units, disk_segments = read_export(args.export_dir)
            disk_errors = verify_records(disk_manifest, disk_units, disk_segments)
            if disk_manifest != manifest or disk_units != units or disk_segments != segments:
                disk_errors.append("exported files do not reload to the same records")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            disk_errors = [f"exported files could not be read back: {exc}"]
        checks.append(("exported files read back", disk_errors))

    totals = manifest["totals"]
    kinds = totals["bytes_by_kind"]
    tokens = totals["tokens_by_reason"]
    segment_counts = Counter(segment["kind"] for segment in segments)
    line_break_bytes = Counter(
        line_break["raw_hex"] for unit in units for line_break in unit["line_breaks"]
    )
    print("Diagnostic only: text units are heuristic candidates, not validated strings; no game text is printed.")
    print(f"Input: {manifest['input']['name']} ({totals['files']} BIN files, {totals['bytes']} bytes)")
    print(f"Text units: {totals['units']} (same IDs as audit_event_candidates.py)")
    print(
        f"Segments: {totals['segments']} ("
        + ", ".join(f"{kind} {segment_counts.get(kind, 0)}" for kind in SEGMENT_KINDS)
        + ")"
    )
    print("Bytes by kind: " + ", ".join(f"{kind} {kinds.get(kind, 0)}" for kind in SEGMENT_KINDS))
    print(
        "Placeholder tokens in unit text: "
        + (", ".join(f"{reason} {count}" for reason, count in tokens.items()) or "none")
    )
    print(f"Literal line breaks in unit text: LF {line_break_bytes.get('0A', 0)}, CR {line_break_bytes.get('0D', 0)}")
    failed = False
    for label, errors in checks:
        if errors:
            failed = True
            print(f"Verification FAILED ({label}): {len(errors)} problem(s)")
            for error in errors[:20]:
                print(f"  - {error}")
        else:
            print(f"Verification passed ({label}): coverage, codec round trip, and no-change rebuilds")
    if args.export_dir and not failed:
        print(f"Exports: {args.export_dir} ({', '.join(EXPORT_FILES)})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
