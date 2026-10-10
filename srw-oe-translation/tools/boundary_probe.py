"""Read-only boundary evidence for the exported text units (counts only, no decoded text).

The exported units are heuristic `FF FF ... 00 00` candidates. This probe measures how much
independent, structural support those boundaries have, so the decision to translate or to write
text back can rest on numbers instead of on the heuristic alone. It never writes to a game file
and never decodes text: every result is a count, a rate, or a short byte pattern in hex.

For each unit it re-checks the recorded offsets against the file bytes, then measures:

* **Length prefix.** Is there a 1/2/4-byte integer in the 16 bytes before the marker whose value
  equals the text length, the span length, or the envelope length? A hit rate alone means nothing
  (small integers are common), so each configuration is compared with a matched-distribution null:
  the expected number of hits if the field values found at those positions were paired at random
  with the units' lengths. Only a rate clearly above that expectation is evidence. Configurations
  with an equal lift are reported widest-field-first, because more agreeing bytes is the stronger
  claim.
* **Pointer references.** How often do the units' own offsets — the marker and the text start —
  occur inside their file as little-/big-endian u32 and u16 values (unaligned and aligned),
  against the same measurement for `marker + 1` and `start + 1`, which are never used? All sets
  are searched in the same bytes, so the comparison is matched; a pointer table shows up as a
  lift, and the match positions (by eighth of the file) say where it would sit.
* **Byte context.** The most common byte patterns just before the marker and just after the text,
  the suffix length histogram, and the byte-value profile per suffix position (a position with one
  distinct value is structure; a position with many is data).
* **Layout.** The gaps between consecutive units, their divisibility by 4, the start-offset
  alignment, and the pitch between consecutive starts (a fixed record size shows up as one delta).
* **Nesting.** How many units contain another `FF FF` inside their own text, and how many of those
  inner markers are followed by wide-script Japanese — the "string inside a string" question.
* **Repetition.** How many distinct text payloads occur more than once across the whole run, and
  how long they are. Long repeated payloads are strong evidence of real strings.
* **Companion `.dat` cross-check.** Every NUL-delimited run of at least six bytes in a package's
  `_ext.dat`/`_Entry.dat`/`_edit.dat` files is searched verbatim in that package's BIN files. A hit
  ties a companion field to event text; no hit narrows the search. Counts and lengths only.
* **Coverage.** The text exports' own manifest totals summed over the run: how many bytes are text
  units, gaps, unselected marker spans, and unterminated tails, plus the unit flags and control
  token counts (invalid CP932, private use, non-round-tripping pairs).

Every hypothesis is reported with its control and its lift. Nothing here proves a boundary; the
point is to make the remaining doubt measurable.

Usage (a finished run folder, no converter call, seconds)::

    python tools/boundary_probe.py <run folder>            # writes boundary_probe.json
    python tools/boundary_probe.py <run folder> --out x.json
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import statistics
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_event_candidates import WIDE_JAPANESE_RE  # noqa: E402  (wide-script matcher, shared)

SCHEMA = "srw-oe-boundary-probe/2"
PROBE_NAME = "boundary_probe.json"

TOP_N = 12
LENGTH_DELTAS = tuple(range(1, 17))  # field start = marker - delta
LENGTH_WIDTHS = (1, 2, 4)
ENDIANS = (("le", "little"), ("be", "big"))
POINTER_WIDTHS = (4, 2)
GAP_EXACT_MAX = 64  # larger gaps are bucketed
PITCH_EXACT_MAX = 256
SUFFIX_PROFILE_MAX_LEN = 8  # profile byte values only for short suffixes
SUFFIX_PROFILE_MAX_POS = 8
OCTILES = 8
# Pointer-scan budgets, so a run over large packages stays in the minutes, not the hours.
# A search costs one pass over the file per value, so the cost of one file is
# (offsets searched x file size) per width, endianness, and set. The per-file caps keep one
# pathological file from eating the run; the global caps keep a very large run bounded.
POINTER_UNALIGNED_FILE_BUDGET = 256 * 1024 * 1024
POINTER_ALIGNED_FILE_BUDGET = 8 * 1024 * 1024
POINTER_UNALIGNED_TOTAL_BUDGET = 2 * 1024 * 1024 * 1024
POINTER_ALIGNED_TOTAL_BUDGET = 256 * 1024 * 1024

# Companion .dat cross-check: NUL-delimited runs at least this long are searched in the BINs.
COMPANION_MIN_RUN = 6
COMPANION_RUNS_PER_PACKAGE = 512
COMPANION_CLASSES = (("_ext.dat", "ext"), ("_entry.dat", "entry"), ("_edit.dat", "edit"))

# Target names for the length-prefix scan: which length a field could be storing.
TARGET_NAMES = ("prefix", "prefix_plus_1", "prefix_plus_2", "span", "envelope")
# Pointer-scan sets: two real targets and two matched controls.
POINTER_SETS = ("marker", "start", "marker_plus_1", "start_plus_1")


def _bucket(value: int, exact_max: int) -> str:
    return str(value) if value <= exact_max else f">{exact_max}"


def _hex(data: bytes) -> str:
    return data.hex().upper()


def _wide_script_count(raw: bytes) -> int:
    """Wide-script Japanese codepoints in `raw` under strict CP932 (0 when it does not decode)."""
    try:
        return len(WIDE_JAPANESE_RE.findall(raw.decode("cp932")))
    except UnicodeDecodeError:
        return 0


class Evidence:
    """Mutable counters for one probe. Merging two probes adds their counters."""

    def __init__(self) -> None:
        self.packages: Counter = Counter()  # package id -> units
        self.sources: Counter = Counter()  # top-level input file -> units
        self.files: Counter = Counter()  # file name -> units
        self.units = 0
        self.units_with_suffix = 0
        self.marker_mismatches = 0
        self.prefix_mismatches = 0
        self.offset_problems = 0
        self.missing_files = 0
        self.length_hits: Counter = Counter()  # (delta, width, endian, target name)
        self.length_eligible: Counter = Counter()  # (delta, width, endian)
        self.length_values: Counter = Counter()  # (delta, width, endian, value) for length values
        self.length_targets: Counter = Counter()  # (target name, value) -> units
        self.pointer: Counter = Counter()  # (measure, width, endian, kind)
        self.pointer_positions: Counter = Counter()  # (width, endian, kind, octile)
        self.pre_marker: Counter = Counter()  # byte pattern hex
        self.post_text: Counter = Counter()  # byte pattern hex
        self.suffix_len: Counter = Counter()  # length -> units
        self.suffix_hex: Counter = Counter()  # (length, hex) -> units
        self.suffix_values: Counter = Counter()  # (length, position, byte hex) -> units
        self.gap_len: Counter = Counter()
        self.gap_mod4: Counter = Counter()
        self.start_mod: Counter = Counter()  # (modulus, remainder)
        self.pitch: Counter = Counter()
        self.nested: Counter = Counter()  # inner-marker measurements
        self.payloads: Counter = Counter()  # (digest, length) -> units
        self.export_bytes: Counter = Counter()  # segment kind -> bytes (from the manifests)
        self.export_flags: Counter = Counter()  # unit flag -> units
        self.export_tokens: Counter = Counter()  # token reason -> tokens
        self.exports_read = 0
        self.export_files = 0
        self.export_units = 0
        self.exports_with_tail = 0
        self.exports_without_manifest = 0
        self.companion_files: Counter = Counter()  # class -> files
        self.companion_runs: Counter = Counter()  # class -> runs searched
        self.companion_matches: Counter = Counter()  # class -> runs found in a BIN
        self.companion_hits: Counter = Counter()  # class -> total occurrences
        self.companion_payloads: Counter = Counter()  # (class, digest, length) -> runs
        self.companion_runs_capped = 0
        self.companion_bytes_searched = 0
        # Remaining global byte budgets for the bounded pointer scans (see _scan_pointers).
        self.unaligned_budget = POINTER_UNALIGNED_TOTAL_BUDGET
        self.aligned_budget = POINTER_ALIGNED_TOTAL_BUDGET
        self.pointer_files_truncated = 0

    def merge(self, other: "Evidence") -> None:
        for name, value in vars(other).items():
            if name.endswith("_budget"):
                continue  # the budgets belong to the pass that spent them
            mine = getattr(self, name)
            if isinstance(mine, Counter):
                mine.update(value)
            else:
                setattr(self, name, mine + value)


def _target_lengths(unit: dict[str, Any]) -> dict[str, int]:
    start = int(unit["start_offset"])
    text_end = int(unit["text_end_offset"])
    pair = int(unit["pair_offset"])
    marker = int(unit["marker_offset"])
    prefix = text_end - start
    return {
        "prefix": prefix,
        "prefix_plus_1": prefix + 1,
        "prefix_plus_2": prefix + 2,
        "span": pair + 2 - start,
        "envelope": pair + 2 - marker,
    }


def _int_at(data: bytes, start: int, width: int, byteorder: str) -> int:
    return int.from_bytes(data[start : start + width], byteorder)  # type: ignore[arg-type]


def _scan_lengths(acc: Evidence, unit: dict[str, Any], data: bytes, wanted: set[int]) -> None:
    """Record the integer fields before the marker and the units' length values.

    `wanted` holds every length value any unit could have. Only those field values are kept, which
    is exactly what the matched-distribution null in `_length_rows` needs: how often each length
    occurs as a field value here, and how often it occurs as a unit's length.
    """
    targets = _target_lengths(unit)
    for name, value in targets.items():
        acc.length_targets[(name, value)] += 1
    marker = int(unit["marker_offset"])
    for delta in LENGTH_DELTAS:
        field = marker - delta
        if field < 0:
            continue
        for width in LENGTH_WIDTHS:
            if field + width > len(data):
                continue
            for endian, byteorder in ENDIANS:
                value = _int_at(data, field, width, byteorder)
                key = (delta, width, endian)
                acc.length_eligible[key] += 1
                if value in wanted:
                    acc.length_values[(*key, value)] += 1
                for name in TARGET_NAMES:
                    if value == targets[name]:
                        acc.length_hits[(*key, name)] += 1
                        break


def _pointer_sets(units: list[dict[str, Any]]) -> dict[str, set[int]]:
    """The two real targets and the two matched controls, disjoint from each other."""
    markers = {int(unit["marker_offset"]) for unit in units}
    starts = {int(unit["start_offset"]) for unit in units}
    used = markers | starts
    return {
        "marker": markers,
        "start": starts,
        "marker_plus_1": {value + 1 for value in markers} - used,
        "start_plus_1": {value + 1 for value in starts} - used,
    }


def _scan_pointers(acc: Evidence, units: list[dict[str, Any]], data: bytes) -> None:
    """Count how often the unit offsets (and the +1 controls) occur as u32/u16 values in the file.

    Both scans are bounded by a byte budget, because a naive search costs one pass over the file
    per value. The budget is spent in a deterministic order (packages in registry order, values in
    ascending order) and the amount actually scanned is reported, so a truncated measurement is
    visible instead of silently looking like a negative result. Values that do not fit the width
    are skipped and counted, for targets and controls alike.
    """
    size = len(data)
    sets = _pointer_sets(units)
    unaligned_left = POINTER_UNALIGNED_FILE_BUDGET
    truncated = False
    for width in POINTER_WIDTHS:
        limit_value = 1 << (8 * width)
        for endian, byteorder in ENDIANS:
            for kind in POINTER_SETS:
                values = sorted(value for value in sets[kind] if value < limit_value)
                skipped = len(sets[kind]) - len(values)
                if skipped:
                    acc.pointer[("values_too_large", width, endian, kind)] += skipped
                room = max(0, min(unaligned_left, acc.unaligned_budget) // max(1, size))
                if len(values) > room:
                    truncated = True
                values = values[:room]
                spent = len(values) * size
                acc.pointer[("values_scanned", width, endian, kind)] += len(values)
                unaligned_left -= spent
                acc.unaligned_budget -= spent
                for value in values:
                    pattern = value.to_bytes(width, byteorder)  # type: ignore[arg-type]
                    index = data.find(pattern)
                    while index >= 0:
                        acc.pointer[("occurrences", width, endian, kind)] += 1
                        acc.pointer_positions[
                            (width, endian, kind, min(OCTILES - 1, index * OCTILES // max(1, size)))
                        ] += 1
                        index = data.find(pattern, index + 1)
            aligned_left = min(POINTER_ALIGNED_FILE_BUDGET, acc.aligned_budget)
            if aligned_left >= size:
                acc.aligned_budget -= size
                acc.pointer[("bytes_scanned_aligned", width, endian, "all")] += size
                lookup: dict[int, tuple[str, ...]] = {}
                for kind in POINTER_SETS:
                    for value in sets[kind]:
                        if value < limit_value:
                            lookup[value] = (*lookup.get(value, ()), kind)
                format_code = ("<" if endian == "le" else ">") + ("I" if width == 4 else "H")
                tail = size - size % width
                for (value,) in struct.iter_unpack(format_code, memoryview(data)[:tail]):
                    kinds = lookup.get(value)
                    if kinds:
                        for kind in kinds:
                            acc.pointer[("occurrences_aligned", width, endian, kind)] += 1
            else:
                truncated = True
    acc.pointer_files_truncated += truncated


def _scan_context(acc: Evidence, unit: dict[str, Any], data: bytes) -> None:
    marker = int(unit["marker_offset"])
    start = int(unit["start_offset"])
    text_end = int(unit["text_end_offset"])
    pair = int(unit["pair_offset"])
    acc.pre_marker[_hex(data[max(0, marker - 6) : marker])] += 1
    acc.post_text[_hex(data[text_end : text_end + 6])] += 1
    suffix = data[text_end:pair]
    acc.suffix_len[len(suffix)] += 1
    if suffix:
        acc.suffix_hex[(len(suffix), _hex(suffix))] += 1
        if len(suffix) <= SUFFIX_PROFILE_MAX_LEN:
            for position, byte in enumerate(suffix[:SUFFIX_PROFILE_MAX_POS]):
                acc.suffix_values[(len(suffix), position, "%02X" % byte)] += 1
    for modulus in (2, 4, 8):
        acc.start_mod[(modulus, start % modulus)] += 1
    payload = bytes.fromhex(unit["prefix_raw_hex"]) if unit.get("prefix_raw_hex") else b""
    acc.payloads[(hashlib.sha256(payload).hexdigest()[:16], len(payload))] += 1


def _scan_nested(acc: Evidence, unit: dict[str, Any]) -> None:
    """Look for another FF FF inside the unit's own text, and for wide-script bytes after it."""
    prefix = bytes.fromhex(unit["prefix_raw_hex"]) if unit.get("prefix_raw_hex") else b""
    inner = [index for index in range(len(prefix) - 1) if prefix[index : index + 2] == b"\xff\xff"]
    if not inner:
        return
    acc.nested["units_with_inner_marker"] += 1
    acc.nested["inner_markers"] += len(inner)
    for index in inner:
        body = prefix[index + 2 :]
        cut = body.find(b"\x00")
        span = body if cut < 0 else body[:cut]
        if _wide_script_count(span) >= 2:
            acc.nested["inner_markers_wide_script"] += 1
        if span and _wide_script_count(span) == 0 and span.isascii():
            acc.nested["inner_markers_ascii_only"] += 1


def _companion_class(name: str) -> str:
    lowered = name.lower()
    for suffix, label in COMPANION_CLASSES:
        if lowered.endswith(suffix):
            return label
    return "other_dat"


def _nul_runs(data: bytes, min_length: int) -> Iterable[tuple[int, bytes]]:
    """Every maximal run of nonzero bytes at least `min_length` long."""
    start = 0
    for index, byte in enumerate(data + b"\x00"):
        if byte:
            continue
        if index - start >= min_length:
            yield start, data[start:index]
        start = index + 1


def add_companions(acc: Evidence, dat_files: dict[str, bytes], bin_files: dict[str, bytes]) -> None:
    """Search each companion `.dat` run in the package's BIN files (counts and lengths only)."""
    if not bin_files:
        return
    runs: list[tuple[str, int, bytes]] = []
    for name in sorted(dat_files):
        data = dat_files[name]
        label = _companion_class(name)
        acc.companion_files[label] += 1
        for offset, run in _nul_runs(data, COMPANION_MIN_RUN):
            runs.append((label, offset, run))
    if len(runs) > COMPANION_RUNS_PER_PACKAGE:
        acc.companion_runs_capped += 1
        runs = runs[:COMPANION_RUNS_PER_PACKAGE]
    for label, _offset, run in runs:
        acc.companion_runs[label] += 1
        acc.companion_bytes_searched += len(run) * len(bin_files)
        hits = sum(data.count(run) for data in bin_files.values())
        if hits:
            acc.companion_matches[label] += 1
            acc.companion_hits[label] += hits
            acc.companion_payloads[(label, hashlib.sha256(run).hexdigest()[:16], len(run))] += 1


def _scan_layout(acc: Evidence, units: list[dict[str, Any]]) -> None:
    ordered = sorted(units, key=lambda unit: (unit["file"], int(unit["start_offset"])))
    previous: Optional[dict[str, Any]] = None
    for unit in ordered:
        if previous is not None and previous["file"] == unit["file"]:
            gap = int(unit["marker_offset"]) - int(previous["pair_offset"]) - 2
            acc.gap_len[_bucket(gap, GAP_EXACT_MAX)] += 1
            acc.gap_mod4[gap % 4] += 1
            acc.pitch[_bucket(int(unit["start_offset"]) - int(previous["start_offset"]), PITCH_EXACT_MAX)] += 1
        previous = unit


def add_units(
    acc: Evidence,
    package_id: str,
    units: list[dict[str, Any]],
    files: dict[str, bytes],
    source: Optional[str] = None,
) -> None:
    """Measure one package's units against its file bytes."""
    by_file: dict[str, list[dict[str, Any]]] = {}
    for unit in units:
        name = unit["file"]
        data = files.get(name)
        if data is None:
            acc.missing_files += 1
            continue
        marker = int(unit["marker_offset"])
        text_end = int(unit["text_end_offset"])
        pair = int(unit["pair_offset"])
        if text_end > pair or pair + 2 > len(data) or marker + 2 > len(data):
            acc.offset_problems += 1
            continue
        if data[marker : marker + 2] != b"\xff\xff":
            acc.marker_mismatches += 1
            continue
        prefix = bytes.fromhex(unit["prefix_raw_hex"]) if unit.get("prefix_raw_hex") else b""
        if data[int(unit["start_offset"]) : text_end] != prefix:
            acc.prefix_mismatches += 1
            continue
        acc.units += 1
        acc.files[name] += 1
        acc.units_with_suffix += bool(unit.get("suffix_raw_hex"))
        _scan_context(acc, unit, data)
        _scan_nested(acc, unit)
        by_file.setdefault(name, []).append(unit)
    measured = [unit for file_units in by_file.values() for unit in file_units]
    if measured:
        wanted = {value for unit in measured for value in _target_lengths(unit).values()}
        for unit in measured:
            _scan_lengths(acc, unit, files[unit["file"]], wanted)
        for name, file_units in by_file.items():
            _scan_pointers(acc, file_units, files[name])
    _scan_layout(acc, units)
    acc.packages[package_id] += len(units)
    if source:
        acc.sources[source] += len(units)


def add_manifest(acc: Evidence, manifest: dict[str, Any]) -> None:
    """Add one text export's manifest totals (coverage, flags, control tokens)."""
    totals = manifest.get("totals") or {}
    acc.exports_read += 1
    acc.export_files += int(totals.get("files") or 0)
    acc.export_units += int(totals.get("units") or 0)
    for kind, count in (totals.get("bytes_by_kind") or {}).items():
        acc.export_bytes[kind] += int(count)
    for flag, count in (totals.get("unit_flags") or {}).items():
        acc.export_flags[flag] += int(count)
    for reason, count in (totals.get("tokens_by_reason") or {}).items():
        acc.export_tokens[reason] += int(count)
    if int((totals.get("bytes_by_kind") or {}).get("unterminated_tail") or 0) > 0:
        acc.exports_with_tail += 1


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------


def _length_rows(acc: Evidence) -> list[dict[str, Any]]:
    """One row per field configuration: observed hits against the matched-distribution null.

    The expectation pairs the field values seen at these positions with the units' lengths at
    random: for each length value, how often it occurs as a field value here times how many units
    have it as a length, over the number of measured fields.
    """
    rows: list[dict[str, Any]] = []
    for delta, width, endian in [
        (delta, width, endian) for delta in LENGTH_DELTAS for width in LENGTH_WIDTHS for endian, _ in ENDIANS
    ]:
        key = (delta, width, endian)
        eligible = acc.length_eligible[key]
        if not eligible:
            continue
        hits = {name: acc.length_hits[(*key, name)] for name in TARGET_NAMES}
        observed = sum(hits.values())
        expected = 0.0
        for (name, value), unit_count in acc.length_targets.items():
            frequency = acc.length_values[(*key, value)]
            if frequency:
                expected += frequency * unit_count / eligible
        rows.append(
            {
                "delta": delta,
                "width": width,
                "endian": endian,
                "hits": observed,
                "eligible": eligible,
                "rate": round(observed / eligible, 4),
                "expected_hits": round(expected, 2),
                "expected_rate": round(expected / eligible, 4),
                "lift": round((observed - expected) / eligible, 4),
                "ratio": round(observed / expected, 2) if expected > 0 else None,
                "by_target": {name: count for name, count in hits.items() if count},
            }
        )
    rows.sort(key=lambda row: (-row["lift"], -row["hits"], -row["width"], row["delta"], row["endian"]))
    return rows


POINTER_MEASURES = ("occurrences", "occurrences_aligned", "values_scanned", "values_too_large")


def _pointer_rows(acc: Evidence) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for measure in POINTER_MEASURES:
        for width in POINTER_WIDTHS:
            for endian, _ in ENDIANS:
                counts = {kind: acc.pointer[(measure, width, endian, kind)] for kind in POINTER_SETS}
                if not any(counts.values()):
                    continue
                rows.append(
                    {
                        "measure": measure,
                        "width": width,
                        "endian": endian,
                        "counts": counts,
                        "targets": counts["marker"] + counts["start"],
                        "controls": counts["marker_plus_1"] + counts["start_plus_1"],
                        "lift": counts["marker"] + counts["start"] - counts["marker_plus_1"] - counts["start_plus_1"],
                    }
                )
    for width in POINTER_WIDTHS:
        for endian, _ in ENDIANS:
            scanned = acc.pointer[("bytes_scanned_aligned", width, endian, "all")]
            if scanned:
                rows.append(
                    {
                        "measure": "bytes_scanned_aligned",
                        "width": width,
                        "endian": endian,
                        "counts": {"all": scanned},
                        "targets": scanned,
                        "controls": 0,
                        "lift": 0,
                    }
                )
    return rows


def _pointer_positions(acc: Evidence) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for width in POINTER_WIDTHS:
        for endian, _ in ENDIANS:
            for kind in POINTER_SETS:
                octiles = {
                    octile: acc.pointer_positions[(width, endian, kind, octile)]
                    for octile in range(OCTILES)
                    if acc.pointer_positions[(width, endian, kind, octile)]
                }
                if octiles:
                    rows.append({"width": width, "endian": endian, "kind": kind, "by_eighth": octiles})
    return rows


def _suffix_profile(acc: Evidence) -> list[dict[str, Any]]:
    profile: list[dict[str, Any]] = []
    for length in sorted({key[0] for key in acc.suffix_values}):
        positions = []
        for position in range(SUFFIX_PROFILE_MAX_POS):
            values = {
                key[2]: count
                for key, count in acc.suffix_values.items()
                if key[0] == length and key[1] == position
            }
            if not values:
                break
            total = sum(values.values())
            common = max(values.items(), key=lambda item: (item[1], item[0]))
            positions.append(
                {
                    "position": position,
                    "distinct_values": len(values),
                    "top_value": common[0],
                    "top_share": round(common[1] / total, 4),
                    "units": total,
                }
            )
        if positions:
            profile.append({"suffix_len": length, "units": acc.suffix_len[length], "positions": positions})
    return profile


def _repeats(acc: Evidence) -> dict[str, Any]:
    lengths: list[int] = []
    for (_digest, length), count in acc.payloads.items():
        if count > 1:
            lengths.extend([length] * count)
    repeated_units = sum(count for count in acc.payloads.values() if count > 1)
    return {
        "distinct_payloads": len(acc.payloads),
        "payloads_repeated": sum(1 for count in acc.payloads.values() if count > 1),
        "units_with_repeated_payload": repeated_units,
        "max_multiplicity": max(acc.payloads.values()) if acc.payloads else 0,
        "repeated_payload_len_min": min(lengths) if lengths else None,
        "repeated_payload_len_median": statistics.median(lengths) if lengths else None,
        "repeated_payload_len_max": max(lengths) if lengths else None,
        "repeated_units_at_least_8_bytes": sum(
            count for (digest, length), count in acc.payloads.items() if count > 1 and length >= 8
        ),
    }


def _coverage(acc: Evidence) -> dict[str, Any]:
    total = sum(acc.export_bytes.values())
    return {
        "exports_read": acc.exports_read,
        "exports_without_manifest": acc.exports_without_manifest,
        "exports_with_unterminated_tail": acc.exports_with_tail,
        "files": acc.export_files,
        "units": acc.export_units,
        "bytes_total": total,
        "bytes_by_kind": dict(sorted(acc.export_bytes.items())),
        "share_by_kind": {
            kind: round(count / total, 4) for kind, count in sorted(acc.export_bytes.items())
        }
        if total
        else {},
        "unit_flags": dict(sorted(acc.export_flags.items())),
        "tokens_by_reason": dict(sorted(acc.export_tokens.items())),
    }


def _top(counter: Counter, limit: int = TOP_N) -> list[dict[str, Any]]:
    ordered = sorted(counter.items(), key=lambda item: (-item[1], str(item[0])))
    return [{"key": key, "count": count} for key, count in ordered[:limit]]


def _expand(counts: dict[int, int], cap_per_value: int = 1000) -> list[int]:
    """Value list for min/median/max, capped per value so a huge run stays cheap."""
    values: list[int] = []
    for value in sorted(counts):
        values.extend([value] * min(counts[value], cap_per_value))
    return values


def summarize(acc: Evidence) -> dict[str, Any]:
    length_rows = _length_rows(acc)
    best_length = length_rows[:8]
    gap_counts = {int(key): count for key, count in acc.gap_len.items() if key.isdigit()}
    gaps = _expand(gap_counts)
    return {
        "schema": SCHEMA,
        "generator": "tools/boundary_probe.py",
        "totals": {
            "packages": len(acc.packages),
            "files": len(acc.files),
            "units": acc.units,
            "units_with_suffix": acc.units_with_suffix,
            "offset_problems": acc.offset_problems,
            "marker_mismatches": acc.marker_mismatches,
            "prefix_mismatches": acc.prefix_mismatches,
            "missing_files": acc.missing_files,
        },
        "length_prefix": {
            "note": (
                "A 1/2/4-byte integer starting `delta` bytes before the marker that equals one of "
                "the recorded lengths, against the matched-distribution null `expected_hits` "
                "(those field values paired with the units' lengths at random)."
            ),
            "best": best_length,
            "rows": length_rows,
        },
        "pointer_references": {
            "note": (
                "Occurrences of the units' marker and text-start offsets as u32/u16 values in "
                "their own file, against marker+1 and start+1 (never used) as controls. All sets "
                "are searched in the same bytes. Both scans are budgeted; values_scanned and "
                "bytes_scanned_aligned say how much was searched, values_too_large how many "
                "offsets did not fit the width. Two-byte patterns occur often by chance, so judge "
                "a u16 lift against its control counts, not against zero."
            ),
            "budgets": {
                "unaligned_bytes_per_file": POINTER_UNALIGNED_FILE_BUDGET,
                "aligned_bytes_per_file_width_endian": POINTER_ALIGNED_FILE_BUDGET,
                "unaligned_bytes_total": POINTER_UNALIGNED_TOTAL_BUDGET,
                "aligned_bytes_total": POINTER_ALIGNED_TOTAL_BUDGET,
                "unaligned_bytes_left": acc.unaligned_budget,
                "aligned_bytes_left": acc.aligned_budget,
                "files_truncated_by_budget": acc.pointer_files_truncated,
            },
            "rows": _pointer_rows(acc),
            "positions": _pointer_positions(acc),
        },
        "pre_marker_patterns": _top(acc.pre_marker),
        "post_text_patterns": _top(acc.post_text),
        "suffix_lengths": _top(acc.suffix_len, 16),
        "suffix_patterns": _top(Counter({f"{length}:{hex_}": count for (length, hex_), count in acc.suffix_hex.items()})),
        "suffix_profile": _suffix_profile(acc),
        "gaps_between_units": {
            "min": min(gaps) if gaps else None,
            "median": statistics.median(gaps) if gaps else None,
            "max": max(gaps) if gaps else None,
            "gaps_above_exact_max": sum(count for key, count in acc.gap_len.items() if not key.isdigit()),
            "multiple_of_4": {str(key): count for key, count in sorted(acc.gap_mod4.items())},
            "top": _top(acc.gap_len),
        },
        "start_alignment": {
            f"mod{modulus}": {
                str(remainder): count for (m, remainder), count in sorted(acc.start_mod.items()) if m == modulus
            }
            for modulus in (2, 4, 8)
        },
        "pitch_between_starts": _top(acc.pitch),
        "nested_markers": {
            "note": "Another FF FF inside a unit's own text, and whether wide-script Japanese follows it.",
            "units_with_inner_marker": acc.nested["units_with_inner_marker"],
            "inner_markers": acc.nested["inner_markers"],
            "inner_markers_wide_script": acc.nested["inner_markers_wide_script"],
            "inner_markers_ascii_only": acc.nested["inner_markers_ascii_only"],
        },
        "repetition": _repeats(acc),
        "companion_dat_cross_check": {
            "note": (
                f"NUL-delimited runs of at least {COMPANION_MIN_RUN} bytes from each package's "
                "companion .dat files, searched verbatim in that package's BIN files."
            ),
            "files": dict(sorted(acc.companion_files.items())),
            "runs_searched": dict(sorted(acc.companion_runs.items())),
            "runs_found_in_bins": dict(sorted(acc.companion_matches.items())),
            "occurrences": dict(sorted(acc.companion_hits.items())),
            "distinct_payloads_found": len(acc.companion_payloads),
            "payload_len_min": min((length for _c, _d, length in acc.companion_payloads), default=None),
            "payload_len_max": max((length for _c, _d, length in acc.companion_payloads), default=None),
            "packages_capped_at_run_limit": acc.companion_runs_capped,
            "run_limit_per_package": COMPANION_RUNS_PER_PACKAGE,
        },
        "text_coverage": _coverage(acc),
        "units_per_package": _top(acc.packages, 20),
        "units_per_source": _top(acc.sources, 60),
    }


# ---------------------------------------------------------------------------
# run folder
# ---------------------------------------------------------------------------


def _read_units(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _export_sources(package: dict[str, Any]) -> list[tuple[str, Path, Path]]:
    """(package id, units.jsonl folder, source folder) for a package and its hidden entries."""
    found: list[tuple[str, Path, Path]] = []
    text = package.get("text") or {}
    export_dir = text.get("export_dir")
    output_dir = package.get("output_dir")
    if export_dir and output_dir:
        found.append((package["package_id"], Path(export_dir), Path(output_dir)))
    hidden = (package.get("hidden_entries") or {}).get("text") or {}
    hidden_export = hidden.get("export_dir")
    if hidden_export:
        found.append((f"{package['package_id']}-hidden", Path(hidden_export), Path("hidden") / package["package_id"]))
    return found


def _top_level_sources(packages: Iterable[dict[str, Any]]) -> dict[str, str]:
    """Map every package id to the name of the input file it ultimately came from."""
    by_id = {package["package_id"]: package for package in packages if package.get("package_id")}
    resolved: dict[str, str] = {}
    for package_id, package in by_id.items():
        current = package
        seen = {package_id}
        while current.get("parent_package") and current["parent_package"] in by_id:
            parent_id = current["parent_package"]
            if parent_id in seen:
                break
            seen.add(parent_id)
            current = by_id[parent_id]
        resolved[package_id] = current.get("source_path") or current.get("package_id", package_id)
    return resolved


def probe_packages(packages: Iterable[dict[str, Any]], run_dir: Path) -> dict[str, Any]:
    """Measure every text export of a run against the files it was extracted from."""
    package_list = list(packages)
    sources = _top_level_sources(package_list)
    acc = Evidence()
    errors: list[str] = []
    probed = 0
    for package in package_list:
        for package_id, export_dir, source_dir in _export_sources(package):
            units_path = run_dir / export_dir / "units.jsonl"
            if not units_path.is_file():
                continue
            try:
                units = _read_units(units_path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{package_id}: {type(error).__name__}: {str(error)[:160]}")
                continue
            manifest_path = run_dir / export_dir / "manifest.json"
            if manifest_path.is_file():
                try:
                    add_manifest(acc, json.loads(manifest_path.read_text(encoding="utf-8")))
                except (OSError, ValueError, json.JSONDecodeError) as error:
                    acc.exports_without_manifest += 1
                    errors.append(f"{package_id}/manifest.json: {type(error).__name__}: {str(error)[:120]}")
            else:
                acc.exports_without_manifest += 1
            names = {unit["file"] for unit in units}
            files: dict[str, bytes] = {}
            for name in sorted(names):
                path = run_dir / source_dir / name
                try:
                    files[name] = path.read_bytes()
                except OSError as error:
                    errors.append(f"{package_id}/{name}: {type(error).__name__}: {str(error)[:120]}")
            add_units(acc, package_id, units, files, sources.get(package["package_id"]))
            try:
                folder = run_dir / source_dir
                bins = dict(files)
                companions: dict[str, bytes] = {}
                for path in sorted(folder.rglob("*")):
                    if not path.is_file() or path.is_symlink():
                        continue
                    relative = path.relative_to(folder).as_posix()
                    suffix = path.suffix.lower()
                    if suffix == ".bin" and relative not in bins:
                        bins[relative] = path.read_bytes()
                    elif suffix == ".dat":
                        companions[relative] = path.read_bytes()
                add_companions(acc, companions, bins)
            except OSError as error:
                errors.append(f"{package_id}/companions: {type(error).__name__}: {str(error)[:120]}")
            probed += 1
    result = summarize(acc)
    result["status"] = "ok" if acc.units else "no_units"
    result["exports_probed"] = probed
    result["errors"] = errors[:50]
    result["scope_note"] = (
        "Read-only counts over the extracted packages and the text exports. Nothing was written to "
        "a game file, and no text was decoded. These are measurements, not validated boundaries."
    )
    return result


def probe_run(run_dir: Path) -> dict[str, Any]:
    """Read a finished run's registry and probe its text exports."""
    registry = json.loads((run_dir / "registry.json").read_text(encoding="utf-8"))
    return probe_packages(registry.get("packages") or [], run_dir)


def write_probe(run_dir: Path, result: dict[str, Any], out: Optional[Path] = None) -> Path:
    path = out or run_dir / PROBE_NAME
    path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "local-workflow.ini"


def latest_run_folder(config_path: Optional[Path] = None) -> Optional[Path]:
    """The newest finished run folder under the configured output base, if there is one."""
    config = config_path or DEFAULT_CONFIG
    base: Optional[str] = None
    if config.is_file():
        parser = configparser.ConfigParser()
        try:
            parser.read(config, encoding="utf-8")
            base = parser.get("local", "output_base", fallback=None)
        except configparser.Error:
            base = None
    if not base:
        return None
    root = Path(base).expanduser()
    if not root.is_dir():
        return None
    finished = [path for path in root.iterdir() if path.is_dir() and (path / "registry.json").is_file()]
    return max(finished, key=lambda path: path.name) if finished else None


def build_probe(run_dir: Path, out: Optional[Path] = None) -> dict[str, Any]:
    result = probe_run(run_dir)
    result["json"] = str(write_probe(run_dir, result, out))
    return result


def report_lines(result: dict[str, Any]) -> list[str]:
    """Short count-only lines for REPORT.txt."""
    if result.get("status") != "ok":
        detail = result.get("error") or ""
        status = result.get("status", "not_run")
        return [f"  boundary probe: {status}" + (f" ({detail})" if detail else "")]
    totals = result["totals"]
    lines = [
        f"  units probed: {totals['units']} in {totals['files']} files, {totals['packages']} exports"
        f" (offset problems {totals['offset_problems']}, marker mismatches {totals['marker_mismatches']},"
        f" prefix mismatches {totals['prefix_mismatches']}, missing files {totals['missing_files']})",
    ]
    coverage = result["text_coverage"]
    if coverage["bytes_total"]:
        shares = ", ".join(
            f"{kind} {coverage['bytes_by_kind'][kind]:,} ({coverage['share_by_kind'][kind]:.1%})"
            for kind in coverage["bytes_by_kind"]
        )
        lines.append(
            f"  text bytes: {coverage['bytes_total']:,} in {coverage['files']} files — {shares}"
            f"; exports with an unterminated tail: {coverage['exports_with_unterminated_tail']}"
        )
    if coverage["unit_flags"]:
        flags = ", ".join(f"{flag} {count}" for flag, count in sorted(coverage["unit_flags"].items()))
        lines.append(f"  unit flags: {flags}")
    if coverage["tokens_by_reason"]:
        tokens = ", ".join(f"{reason} {count}" for reason, count in sorted(coverage["tokens_by_reason"].items()))
        lines.append(f"  control tokens: {tokens}")
    rows = result["length_prefix"]["rows"]
    positive = [row for row in rows if row["hits"] and row["lift"] > 0.01]
    if positive:
        lines.append("  length-prefix fields above the matched-distribution null (a length stored before the marker):")
        lines += [
            f"    u{row['width'] * 8} {row['endian']} at marker-{row['delta']}: {row['hits']}/{row['eligible']}"
            f" ({row['rate']:.1%}) vs expected {row['expected_hits']} ({row['expected_rate']:.1%}),"
            f" lift {row['lift']:+.1%}, ratio {row['ratio']} targets {row['by_target']}"
            for row in positive[:3]
        ]
    else:
        best = max((row["lift"] for row in rows), default=0.0)
        lines.append(
            "  length-prefix scan: no 1/2/4-byte field in the 16 bytes before the marker beats the"
            f" matched-distribution null (best lift {best:+.1%})"
        )
    pointer = result["pointer_references"]
    hits = [row for row in pointer["rows"] if row["measure"] == "occurrences" and (row["targets"] or row["controls"])]
    aligned = [
        row for row in pointer["rows"] if row["measure"] == "occurrences_aligned" and (row["targets"] or row["controls"])
    ]
    if hits or aligned:
        for row in hits + aligned:
            label = "unaligned" if row["measure"] == "occurrences" else "aligned"
            lines.append(
                f"  pointer u{row['width'] * 8} {row['endian']} {label}: at marker {row['counts']['marker']},"
                f" at text start {row['counts']['start']} (controls: marker+1 {row['counts']['marker_plus_1']},"
                f" start+1 {row['counts']['start_plus_1']}), lift {row['lift']:+d}"
            )
        searched = ", ".join(
            f"u{row['width'] * 8} {row['endian']}: {row['counts']['marker'] + row['counts']['start']} offsets"
            for row in pointer["rows"]
            if row["measure"] == "values_scanned"
        )
        lines.append(f"  pointer search coverage: {searched}")
        for row in pointer["positions"]:
            if row["kind"] in ("marker", "start"):
                eighths = ", ".join(f"eighth {key}: {count}" for key, count in sorted(row["by_eighth"].items()))
                lines.append(f"  pointer match positions u{row['width'] * 8} {row['endian']} ({row['kind']}): {eighths}")
    else:
        lines.append("  pointer scan: no unit offset occurs as a u32/u16 value in its own file (targets 0, controls 0)")
    if result["post_text_patterns"]:
        top = ", ".join(f"{row['key']} x{row['count']}" for row in result["post_text_patterns"][:4])
        lines.append(f"  bytes after the text (top 4): {top}")
    if result["pre_marker_patterns"]:
        top = ", ".join(f"{row['key']} x{row['count']}" for row in result["pre_marker_patterns"][:4])
        lines.append(f"  bytes before the marker (top 4): {top}")
    suffixes = ", ".join(f"{row['key']} bytes x{row['count']}" for row in result["suffix_lengths"][:6])
    lines.append(f"  suffix lengths: {suffixes}")
    for profile in result["suffix_profile"][:3]:
        described = ", ".join(
            f"+{position['position']}:{position['distinct_values']} value(s), top {position['top_value']}"
            f" {position['top_share']:.0%}"
            for position in profile["positions"]
        )
        lines.append(f"  suffix of {profile['suffix_len']} bytes ({profile['units']} units): {described}")
    gaps = result["gaps_between_units"]
    lines.append(
        f"  gap between units: min {gaps['min']}, median {gaps['median']}, max {gaps['max']},"
        f" mod 4 {gaps['multiple_of_4']}"
    )
    pitch = ", ".join(f"{row['key']} x{row['count']}" for row in result["pitch_between_starts"][:5])
    lines.append(f"  pitch between starts (top 5): {pitch}")
    nested = result["nested_markers"]
    lines.append(
        f"  nested FF FF inside a unit: {nested['units_with_inner_marker']} units,"
        f" {nested['inner_markers']} inner markers, {nested['inner_markers_wide_script']} followed by"
        f" wide-script Japanese, {nested['inner_markers_ascii_only']} ASCII-only"
    )
    companions = result["companion_dat_cross_check"]
    if companions["runs_searched"]:
        searched = ", ".join(f"{label} {count}" for label, count in sorted(companions["runs_searched"].items()))
        found = ", ".join(f"{label} {count}" for label, count in sorted(companions["runs_found_in_bins"].items()))
        lines.append(
            f"  companion .dat runs >={COMPANION_MIN_RUN} bytes searched in the same package's BINs:"
            f" {searched}; found in a BIN: {found or 'none'}"
            f" ({companions['distinct_payloads_found']} distinct payloads,"
            f" lengths {companions['payload_len_min']}-{companions['payload_len_max']})"
        )
    repeats = result["repetition"]
    lines.append(
        f"  repetition: {repeats['payloads_repeated']} of {repeats['distinct_payloads']} payloads repeat"
        f" ({repeats['units_with_repeated_payload']} units, max x{repeats['max_multiplicity']},"
        f" repeated units >=8 bytes: {repeats['repeated_units_at_least_8_bytes']})"
    )
    per_source = result["units_per_source"]
    if per_source:
        shown = ", ".join(f"{row['key']} {row['count']}" for row in per_source[:10])
        rest = len(per_source) - min(10, len(per_source))
        lines.append(f"  units per source file (top 10 of {len(per_source)}): {shown}" + (f", +{rest} more" if rest else ""))
    return lines


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "run_dir",
        type=Path,
        nargs="?",
        help="run folder (the one containing registry.json); default: the newest run in your output folder",
    )
    parser.add_argument("--out", type=Path, help=f"JSON path (default: <run folder>/{PROBE_NAME})")
    args = parser.parse_args(argv)
    run_dir = args.run_dir.expanduser() if args.run_dir else latest_run_folder()
    if run_dir is None:
        print(
            "No run folder given and none found: pass the run folder (the one with registry.json) "
            "as an argument, or run RUN_PIPELINE.bat first.",
            file=sys.stderr,
        )
        return 2
    run_dir = run_dir.resolve()
    try:
        result = build_probe(run_dir, args.out.expanduser().resolve() if args.out else None)
    except (OSError, ValueError) as error:
        print(f"Could not probe {run_dir}: {error}", file=sys.stderr)
        return 1
    for line in report_lines(result):
        print(line)
    print(result["json"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
