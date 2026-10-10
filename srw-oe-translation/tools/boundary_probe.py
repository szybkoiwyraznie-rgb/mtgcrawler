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
* **Pointer references.** How often do the units' own start offsets occur inside their file as
  little-/big-endian u32 values (unaligned and 4-aligned), against the same measurement for
  `start + 1`, which is never a unit start? Both sets are searched in the same bytes, so the
  comparison is matched; a pointer table shows up as a lift here.
* **Byte context.** The most common byte patterns just before the marker and just after the text,
  the suffix length histogram, and the byte-value profile per suffix position (a position with one
  distinct value is structure; a position with many is data).
* **Layout.** The gaps between consecutive units, their divisibility by 4, the start-offset
  alignment, and the pitch between consecutive starts (a fixed record size shows up as one delta).
* **Repetition.** How many distinct text payloads occur more than once across the whole run, and
  how long they are. Long repeated payloads are strong evidence of real strings.

Every hypothesis is reported with its control and its lift. Nothing here proves a boundary; the
point is to make the remaining doubt measurable.

Usage::

    python tools/boundary_probe.py <run folder>            # writes boundary_probe.json
    python tools/boundary_probe.py <run folder> --out x.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional

SCHEMA = "srw-oe-boundary-probe/1"
PROBE_NAME = "boundary_probe.json"

TOP_N = 12
LENGTH_DELTAS = tuple(range(1, 17))  # field start = position - delta
LENGTH_WIDTHS = (1, 2, 4)
ENDIANS = (("le", "little"), ("be", "big"))
GAP_EXACT_MAX = 64  # larger gaps are bucketed
PITCH_EXACT_MAX = 256
SUFFIX_PROFILE_MAX_LEN = 8  # profile byte values only for short suffixes
SUFFIX_PROFILE_MAX_POS = 8
# Pointer-scan budgets, so a run over large packages stays in the minutes, not the hours.
POINTER_UNALIGNED_BUDGET = 256 * 1024 * 1024  # one file pass per value searched
POINTER_ALIGNED_BUDGET = 64 * 1024 * 1024  # file bytes read by the 4-aligned scan, per endianness

# Target names for the length-prefix scan: which length a field could be storing.
TARGET_NAMES = ("prefix", "prefix_plus_1", "prefix_plus_2", "span", "envelope")


def _bucket(value: int, exact_max: int) -> str:
    return str(value) if value <= exact_max else f">{exact_max}"


def _hex(data: bytes) -> str:
    return data.hex().upper()


class Evidence:
    """Mutable counters for one probe. Merging two probes adds their counters."""

    def __init__(self) -> None:
        self.packages: Counter = Counter()  # package id -> units
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
        self.pointer: Counter = Counter()  # (measure, endian, kind)
        self.pre_marker: Counter = Counter()  # byte pattern hex
        self.post_text: Counter = Counter()  # byte pattern hex
        self.suffix_len: Counter = Counter()  # length -> units
        self.suffix_hex: Counter = Counter()  # (length, hex) -> units
        self.suffix_values: Counter = Counter()  # (length, position, byte hex) -> units
        self.gap_len: Counter = Counter()
        self.gap_mod4: Counter = Counter()
        self.start_mod: Counter = Counter()  # (modulus, remainder)
        self.pitch: Counter = Counter()
        self.payloads: Counter = Counter()  # (digest, length) -> units
        # Remaining byte budgets for the bounded pointer scans (see _scan_pointers).
        self.unaligned_budget = POINTER_UNALIGNED_BUDGET
        self.aligned_budget = POINTER_ALIGNED_BUDGET

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


def _scan_pointers(acc: Evidence, units: list[dict[str, Any]], data: bytes) -> None:
    """Count how often unit starts (and the start+1 control) occur as u32 values in the file.

    Both scans are bounded by a byte budget, because a naive search costs one pass over the file
    per value. The budget is spent in a deterministic order (packages in registry order, values in
    ascending order) and the amount actually scanned is reported, so a truncated measurement is
    visible instead of silently looking like a negative result.
    """
    starts = [int(unit["start_offset"]) for unit in units]
    candidates = sorted({start for start in starts})
    controls = sorted({start + 1 for start in starts} - set(candidates))
    size = len(data)
    for endian, byteorder in ENDIANS:
        limit = max(0, acc.unaligned_budget // max(1, size))
        for kind, values in (("candidate", candidates[:limit]), ("control", controls[:limit])):
            acc.pointer[("values_scanned_unaligned", endian, kind)] += len(values)
            acc.unaligned_budget -= len(values) * size
            for value in values:
                count = data.count(value.to_bytes(4, byteorder))  # type: ignore[arg-type]
                if count:
                    acc.pointer[("occurrences_unaligned", endian, kind)] += count
                    acc.pointer[("values_found_unaligned", endian, kind)] += 1
        if acc.aligned_budget >= size:
            acc.aligned_budget -= size
            acc.pointer[("bytes_scanned_aligned", endian, "candidate")] += size
            target_set = set(candidates)
            control_set = set(controls)
            tail = size - size % 4
            for start_index in range(0, tail, 4):
                value = _int_at(data, start_index, 4, "little" if endian == "le" else "big")
                if value in target_set:
                    acc.pointer[("occurrences_aligned", endian, "candidate")] += 1
                if value in control_set:
                    acc.pointer[("occurrences_aligned", endian, "control")] += 1


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


def add_units(acc: Evidence, package_id: str, units: list[dict[str, Any]], files: dict[str, bytes]) -> None:
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


def _pointer_rows(acc: Evidence) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for measure in (
        "occurrences_unaligned",
        "values_found_unaligned",
        "values_scanned_unaligned",
        "occurrences_aligned",
        "bytes_scanned_aligned",
    ):
        for endian, _ in ENDIANS:
            candidate = acc.pointer[(measure, endian, "candidate")]
            control = acc.pointer[(measure, endian, "control")]
            rows.append(
                {
                    "measure": measure,
                    "endian": endian,
                    "candidate": candidate,
                    "control": control,
                    "lift": round(candidate - control, 4),
                }
            )
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
                "Occurrences of the units' start offsets as u32 values in their own file, against "
                "start+1 (never a unit start) as the control. Both scans are budgeted; "
                "values_scanned_unaligned and bytes_scanned_aligned say how much was searched."
            ),
            "budgets": {
                "unaligned_bytes": POINTER_UNALIGNED_BUDGET,
                "aligned_bytes_per_endian": POINTER_ALIGNED_BUDGET,
                "unaligned_bytes_left": acc.unaligned_budget,
                "aligned_bytes_left": acc.aligned_budget,
            },
            "rows": _pointer_rows(acc),
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
            "gaps_above_exact_max": sum(
                count for key, count in acc.gap_len.items() if not key.isdigit()
            ),
            "multiple_of_4": {str(key): count for key, count in sorted(acc.gap_mod4.items())},
            "top": _top(acc.gap_len),
        },
        "start_alignment": {
            f"mod{modulus}": {str(remainder): count for (m, remainder), count in sorted(acc.start_mod.items()) if m == modulus}
            for modulus in (2, 4, 8)
        },
        "pitch_between_starts": _top(acc.pitch),
        "repetition": _repeats(acc),
        "units_per_package": _top(acc.packages, 20),
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


def probe_packages(packages: Iterable[dict[str, Any]], run_dir: Path) -> dict[str, Any]:
    """Measure every text export of a run against the files it was extracted from."""
    acc = Evidence()
    errors: list[str] = []
    probed = 0
    for package in packages:
        for package_id, export_dir, source_dir in _export_sources(package):
            units_path = run_dir / export_dir / "units.jsonl"
            if not units_path.is_file():
                continue
            try:
                units = _read_units(units_path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{package_id}: {type(error).__name__}: {str(error)[:160]}")
                continue
            names = {unit["file"] for unit in units}
            files: dict[str, bytes] = {}
            for name in sorted(names):
                path = run_dir / source_dir / name
                try:
                    files[name] = path.read_bytes()
                except OSError as error:
                    errors.append(f"{package_id}/{name}: {type(error).__name__}: {str(error)[:120]}")
            add_units(acc, package_id, units, files)
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
    pointer = result["pointer_references"]["rows"]
    occurrences = [row for row in pointer if row["measure"].startswith("occurrences")]
    hits = [row for row in occurrences if row["candidate"] or row["control"]]
    if hits:
        lines += [
            f"  pointer {row['measure']} {row['endian']}: candidate {row['candidate']}, control {row['control']}"
            for row in hits
        ]
    else:
        searched = {row["measure"]: row["candidate"] for row in pointer if row["measure"].startswith(("values_scanned", "bytes_scanned"))}
        lines.append(
            "  pointer scan: no unit start occurs as a u32 value in its own file (searched"
            f" {searched.get('values_scanned_unaligned', 0)} start offsets and"
            f" {searched.get('bytes_scanned_aligned', 0)} aligned bytes per endianness)"
        )
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
    repeats = result["repetition"]
    lines.append(
        f"  repetition: {repeats['payloads_repeated']} of {repeats['distinct_payloads']} payloads repeat"
        f" ({repeats['units_with_repeated_payload']} units, max x{repeats['max_multiplicity']},"
        f" repeated units >=8 bytes: {repeats['repeated_units_at_least_8_bytes']})"
    )
    return lines


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path, help="run folder (the one containing registry.json)")
    parser.add_argument("--out", type=Path, help=f"JSON path (default: <run folder>/{PROBE_NAME})")
    args = parser.parse_args(argv)
    run_dir = args.run_dir.expanduser().resolve()
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
