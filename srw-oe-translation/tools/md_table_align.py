#!/usr/bin/env python3
"""Monospace-exact Markdown pipe table formatter optimized for Notepad++ plain-text reading.

Ensures:
1. Every column pipe `|` aligns vertically across header, separator, primary rows,
   and multi-line continuation rows in fixed-width editors (Notepad++ Courier New / Consolas),
   completely independent of editor `Tab size` settings while remaining valid Markdown.
2. Zero raw `<br>` / `<br><br>` HTML tags appear in plain-text output: multi-part descriptions
   expand into aligned continuation lines inside the target column with empty cells elsewhere.
3. Long rightmost-column descriptions soft-wrap cleanly with a 2-space hanging indent so total
   line width never exceeds `max_line_width` (default `216`, safely within a 1080p Notepad++ viewport).
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import unicodedata

DEFAULT_MAX_LINE_WIDTH = 216
MIN_LAST_COL_WIDTH = 28

_ALIGN_RE = re.compile(r"^:?-{3,}:?$")
_BR_DOUBLE_RE = re.compile(r"(?:<br\s*/?>\s*){2,}", flags=re.IGNORECASE)
_BR_SINGLE_RE = re.compile(r"<br\s*/?>", flags=re.IGNORECASE)


def cell_width(text: str) -> int:
    """Return display column width in Notepad++ monospace (`1` for Latin/Polish/symbols, `2` for CJK)."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def pad_cell(text: str, width: int, align: str = "l") -> str:
    pad = max(0, width - cell_width(text))
    if align == "r":
        return " " * pad + text
    if align == "c":
        left = pad // 2
        right = pad - left
        return " " * left + text + " " * right
    return text + " " * pad


def rule_cell(width: int, align: str = "l") -> str:
    width = max(3, width)
    if align == "r":
        return "-" * (width - 1) + ":"
    if align == "c":
        return ":" + "-" * (width - 2) + ":"
    return "-" * width


def parse_align_spec(spec: str) -> str:
    s = spec.strip()
    if s.startswith(":") and s.endswith(":"):
        return "c"
    if s.endswith(":"):
        return "r"
    return "l"


def split_row_pipes(line: str) -> list[str]:
    """Split a single `| ... |` Markdown table row respecting backslash escapes `\\|`."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith(r"\|"):
        stripped = stripped[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", stripped)]


def wrap_segment(text: str, max_width: int, sub_indent: str = "  ") -> list[str]:
    """Word-wrap `text` to `max_width` monospace cells without altering words or numbers."""
    text = text.strip()
    if not text or cell_width(text) <= max_width:
        return [text]

    # Prefer natural " / " group breaks first when present (e.g. Spirit tier summaries)
    if " / " in text:
        parts = text.split(" / ")
        grouped: list[str] = []
        cur = parts[0]
        for part in parts[1:]:
            candidate = f"{cur} / {part}"
            limit = max_width if not grouped else max_width - cell_width(sub_indent)
            if cell_width(candidate) <= limit:
                cur = candidate
            else:
                grouped.append(cur if not grouped else sub_indent + cur)
                cur = part
        grouped.append(cur if not grouped else sub_indent + cur)
        out: list[str] = []
        for g in grouped:
            if cell_width(g) <= max_width:
                out.append(g)
            else:
                lead = sub_indent if g.startswith(sub_indent) else ""
                out.extend(_wrap_words(g.strip(), max_width, lead_first=lead, lead_next=sub_indent))
        return out

    return _wrap_words(text, max_width, lead_first="", lead_next=sub_indent)


def _wrap_words(text: str, max_width: int, lead_first: str, lead_next: str) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    cur_lead = lead_first
    cur = ""
    for w in words:
        cand = w if not cur else f"{cur} {w}"
        if cur and cell_width(cur_lead + cand) > max_width:
            lines.append(cur_lead + cur)
            cur_lead = lead_next
            cur = w
        else:
            cur = cand
    if cur or not lines:
        lines.append(cur_lead + cur)
    return lines


def expand_cell_lines(raw: str, wrap_width: int | None = None) -> list[str]:
    """Expand `<br><br>`, `<br>`, and optional word-wrapping into visual lines for one cell."""
    if not raw:
        return [""]
    paragraphs = _BR_DOUBLE_RE.split(raw)
    logical_lines: list[str] = []
    for para in paragraphs:
        sublines = _BR_SINGLE_RE.split(para)
        for idx, sub in enumerate(sublines):
            cleaned = sub.strip()
            prefix = "  " if idx > 0 and cleaned else ""
            entry = prefix + cleaned
            if wrap_width is not None and cell_width(entry) > wrap_width:
                if prefix:
                    wrapped = _wrap_words(cleaned, wrap_width, lead_first=prefix, lead_next="  ")
                else:
                    wrapped = wrap_segment(cleaned, wrap_width, sub_indent="  ")
                logical_lines.extend(wrapped)
            else:
                logical_lines.append(entry)
    return logical_lines or [""]


def format_table(
    headers: list[str],
    alignments: list[str],
    rows: list[list[str]],
    max_line_width: int | None = DEFAULT_MAX_LINE_WIDTH,
) -> str:
    """Format a Markdown table with exact vertical `|` alignment and clean multi-line wrapping."""
    ncols = len(headers)
    if ncols == 0:
        return ""
    aligns = list(alignments) + ["l"] * max(0, ncols - len(alignments))
    norm_rows = [list(r) + [""] * max(0, ncols - len(r)) for r in rows]

    # Expand cols 0..ncols-2 without wrapping first so we know fixed left columns' natural widths.
    col_caps: list[int | None] = [None] * ncols
    if max_line_width is not None and ncols >= 2:
        # Compute natural widths first; if left columns squeeze last column below MIN_LAST_COL_WIDTH,
        # iteratively tighten the widest non-last column until total width <= max_line_width.
        natural_widths = [max(3, cell_width(h)) for h in headers]
        for r in norm_rows:
            for c_idx in range(ncols - 1):
                for cl in expand_cell_lines(r[c_idx], wrap_width=None):
                    natural_widths[c_idx] = max(natural_widths[c_idx], cell_width(cl))
        cur_widths = list(natural_widths[:-1])
        min_last = max(MIN_LAST_COL_WIDTH, cell_width(headers[ncols - 1]), 42)
        while 1 + sum(w + 3 for w in cur_widths) + min_last + 3 > max_line_width:
            widest_i = max(range(ncols - 1), key=lambda idx: cur_widths[idx] - max(3, cell_width(headers[idx])))
            floor_w = max(12, cell_width(headers[widest_i]))
            if cur_widths[widest_i] <= floor_w:
                break
            cur_widths[widest_i] = max(floor_w, cur_widths[widest_i] - 8)
            col_caps[widest_i] = cur_widths[widest_i]

    pre_cells: list[list[list[str]]] = []
    col_widths = [max(3, cell_width(h)) for h in headers]

    for r in norm_rows:
        row_expanded: list[list[str]] = []
        for c_idx in range(ncols - 1):
            clines = expand_cell_lines(r[c_idx], wrap_width=col_caps[c_idx])
            for cl in clines:
                col_widths[c_idx] = max(col_widths[c_idx], cell_width(cl))
            row_expanded.append(clines)
        row_expanded.append([])  # placeholder for last col
        pre_cells.append(row_expanded)

    # Determine wrap budget for last column from max_line_width:
    # Total line length for widths w_0..w_{k-1} is: 1 + sum(w_i + 3 for i in range(ncols))
    last_wrap: int | None = None
    if max_line_width is not None:
        left_overhead = 1 + sum(col_widths[i] + 3 for i in range(ncols - 1)) + 3
        last_wrap = max(MIN_LAST_COL_WIDTH, max_line_width - left_overhead)

    for r_idx, r in enumerate(norm_rows):
        last_lines = expand_cell_lines(r[ncols - 1], wrap_width=last_wrap)
        for cl in last_lines:
            col_widths[ncols - 1] = max(col_widths[ncols - 1], cell_width(cl))
        pre_cells[r_idx][ncols - 1] = last_lines

    out_lines = [
        "| " + " | ".join(pad_cell(headers[i], col_widths[i], aligns[i]) for i in range(ncols)) + " |",
        "| " + " | ".join(rule_cell(col_widths[i], aligns[i]) for i in range(ncols)) + " |",
    ]

    for row_expanded in pre_cells:
        height = max(len(col_lines) for col_lines in row_expanded)
        for line_i in range(height):
            rendered = []
            for c_idx in range(ncols):
                col_lines = row_expanded[c_idx]
                val = col_lines[line_i] if line_i < len(col_lines) else ""
                rendered.append(pad_cell(val, col_widths[c_idx], aligns[c_idx]))
            out_lines.append("| " + " | ".join(rendered) + " |")

    return "\n".join(out_lines)


def _is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(_ALIGN_RE.match(c.strip()) for c in cells)


def align_markdown_tables(markdown: str, max_line_width: int | None = DEFAULT_MAX_LINE_WIDTH) -> str:
    """Reformat all top-level Markdown pipe tables in `markdown` (ignoring fenced code blocks)."""
    src_lines = markdown.splitlines(keepends=True)
    out: list[str] = []
    in_fence = False
    i = 0
    n = len(src_lines)

    while i < n:
        raw_line = src_lines[i]
        stripped = raw_line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(raw_line)
            i += 1
            continue

        if (
            not in_fence
            and raw_line.startswith("|")
            and i + 1 < n
            and src_lines[i + 1].startswith("|")
        ):
            hdr_cells = split_row_pipes(raw_line)
            sep_cells = split_row_pipes(src_lines[i + 1])
            if len(hdr_cells) == len(sep_cells) and _is_separator_row(sep_cells):
                aligns = [parse_align_spec(c) for c in sep_cells]
                j = i + 2
                body_rows: list[list[str]] = []
                valid = True
                while j < n and src_lines[j].startswith("|"):
                    rcells = split_row_pipes(src_lines[j])
                    if len(rcells) != len(hdr_cells):
                        valid = False
                        break
                    body_rows.append(rcells)
                    j += 1
                if valid:
                    nl = "\r\n" if raw_line.endswith("\r\n") else ("\n" if raw_line.endswith("\n") else "")
                    formatted = format_table(hdr_cells, aligns, body_rows, max_line_width=max_line_width)
                    if nl and nl != "\n":
                        formatted = formatted.replace("\n", nl)
                    out.append(formatted + nl)
                    i = j
                    continue

        out.append(raw_line)
        i += 1

    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=Path, help="Markdown files to format in place")
    ap.add_argument("--max-width", type=int, default=DEFAULT_MAX_LINE_WIDTH, help="Maximum table line width")
    args = ap.parse_args(argv)
    for path in args.files:
        before = path.read_text(encoding="utf-8")
        after = align_markdown_tables(before, max_line_width=args.max_width)
        if after != before:
            path.write_text(after, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
