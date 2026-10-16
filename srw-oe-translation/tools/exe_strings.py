#!/usr/bin/env python3
"""The executable's own strings: extract them as package rows, write the English back in place,
or emit the same edits as a CWCheat file.

Measured 2026-10-15 on the user's 1.08 update (``PBOOT.PBP`` → ``DATA.PSP``, module ``srw``
v1.1, decrypted ELF md5 ``8ba77a79e7d46473671cb87e77553deb``, 5 531 024 B): the game is a
relocatable PRX whose segment 0 loads at ``0x08804000``.  Its ``.rodata``/``.data`` hold
~400 Japanese strings no data file has - the battle pop-ups (``回避``, ``援護防御``,
``ＥＮ不足`` …), the weapon-panel words (``移動後``, ``敵``/``味方``), the 1.08 ability lines
(``＠4<貫通 Lv2>＠0 敵の防御-35%``), pilot/menu captions, save-data and DLC messages.

How they are found (no heuristics on raw bytes): the PRX relocation tables (``.rel.*``,
type ``0x700000A0``) name every pointer the code or the data holds - ``R_MIPS_32`` words and
``R_MIPS_HI16``/``LO16`` instruction pairs.  Every target inside ``.rodata``/``.data`` that
begins a NUL-terminated run of text is one row; a target *inside* a run splits it into
segments (the code prints the tail of ``＠4<連携攻撃 Lv1>＠0 包囲率+30% …`` from byte 19 on,
with a 114-byte stride for the next levels), and a segment that is not the last of its run
must be filled to EXACTLY its byte length - the English of such a row is space-padded (before
a trailing ``＠`` when the colour code straddles the split).

Writing is in place and fail-closed: nothing moves (the code addresses the strings by absolute
pointer, several tables by ``base + level * stride``), the English must fit ``max_bytes`` - the
Japanese length plus the zero alignment padding behind the terminator (``source.slack``: the
strings are 4-byte aligned, so ``敵`` owns 3 bytes and ``移動`` 7), must keep every printf conversion (``%d``, ``%2d``, ``%+3d%%``,
``%-TEXT_SPACE_ROBOs``…) in order, must not carry a ``0x0F`` kana token, and the Japanese bytes
must still be at the offset or the row is refused and reported - a different print of the game
is never half-patched.  Strings the save-data layer reads are UTF-8 (``第%d話までクリア``) and
are written back as UTF-8; everything else is cp932.

Rows follow the package schema (``category: exe``, ``mode: slot``, ``max_bytes``) so
:mod:`translation_check`, :mod:`translation_copy` and the builder treat them like the other
fixed slots.  ``source`` carries the executable (``PBOOT.PBP``/``DATA.PSP``), the ELF file
offset, the load address and the segment flag.

Usage::

    python3 tools/exe_strings.py extract --exe PBOOT.PBP --out 09_executable.jsonl
    python3 tools/exe_strings.py apply --exe PBOOT.PBP --rows 09_executable.jsonl \\
        --out out/PBOOT.PBP [--report out/exe_report.json]
    python3 tools/exe_strings.py cheat --rows 09_executable.jsonl --out NPJH50521.ini

``apply`` writes a PBP whose ``DATA.PSP`` is the patched *plain* ELF (PPSSPP loads an
unencrypted module from a PBP - ``sceKernelModule.cpp`` falls back to the ELF when the ``~PSP``
decrypt is not needed; a real PSP needs CFW and is untested), or a bare ELF when the input was
one.  ``cheat`` turns the same byte
edits into CWCheat ``_L`` lines (``memstick/PSP/Cheats/NPJH50521.ini``) for a setup where the
executable cannot be replaced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import psp_prx  # noqa: E402

LOAD_BASE = 0x08804000          # where the PSP loads segment 0 of the boot module
CWCHEAT_BASE = 0x08800000       # CWCheat addresses are offsets from here
CATEGORY = "exe"
CONTAINER = "PBOOT.PBP"
MEMBER = "DATA.PSP"
KNOWN_ELF_MD5 = {"8ba77a79e7d46473671cb87e77553deb": "SRW OE 1.08 update (PBOOT.PBP, module srw v1.1)"}

TEXT_SECTIONS = (".rodata", ".data")
R_MIPS_32, R_MIPS_26, R_MIPS_HI16, R_MIPS_LO16 = 2, 4, 5, 6
SHT_PSP_REL = 0x700000A0

#: printf conversions the game's strings use: ``%%``, ``%d`` ``%2d`` ``%+3d`` ``%02d`` ``%10d``
#: ``%s``, and the engine's own ``%-TEXT_SPACE_ROBOs`` width macros
FORMAT_RE = re.compile(r"%(?:%|-?[A-Z_]{2,}s|[-+ 0#]*\d*(?:\.\d+)?[hlL]?[diouxXeEfgGcsp])")
COLOUR_RE = re.compile("＠.")


class ExeError(Exception):
    pass


# --------------------------------------------------------------------------------------------
# ELF
# --------------------------------------------------------------------------------------------

@dataclass
class Segment:
    index: int
    p_type: int
    offset: int
    vaddr: int
    filesz: int
    memsz: int


@dataclass
class Section:
    name: str
    sh_type: int
    addr: int
    offset: int
    size: int


class Elf:
    def __init__(self, data: bytes):
        if data[:4] != psp_prx.ELF_MAGIC:
            raise ExeError("not an ELF")
        self.data = data
        (e_type, e_machine, _v, self.entry, e_phoff, e_shoff, _f, _eh, e_phentsize, e_phnum,
         e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
        self.segments: List[Segment] = []
        for i in range(e_phnum):
            p_type, p_offset, p_vaddr, _pa, p_filesz, p_memsz, _fl, _al = struct.unpack_from(
                "<8I", data, e_phoff + i * e_phentsize)
            self.segments.append(Segment(i, p_type, p_offset, p_vaddr, p_filesz, p_memsz))
        self.sections: List[Section] = []
        if e_shnum:
            strtab_off = struct.unpack_from("<10I", data, e_shoff + e_shstrndx * e_shentsize)[4]
            for i in range(e_shnum):
                sh = struct.unpack_from("<10I", data, e_shoff + i * e_shentsize)
                end = data.index(b"\0", strtab_off + sh[0])
                name = data[strtab_off + sh[0]:end].decode("ascii", "replace")
                self.sections.append(Section(name, sh[1], sh[3], sh[4], sh[5]))

    def section(self, name: str) -> Optional[Section]:
        for s in self.sections:
            if s.name == name:
                return s
        return None

    def file_offset(self, rel_addr: int) -> Optional[int]:
        """Segment-0-relative address → file offset (None outside the loaded file bytes)."""
        for seg in self.segments:
            if seg.p_type == 1 and seg.vaddr <= rel_addr < seg.vaddr + seg.filesz:
                return seg.offset + (rel_addr - seg.vaddr)
        return None

    def text_ranges(self) -> List[Tuple[str, int, int]]:
        """``(section, rel_start, rel_end)`` of the sections that hold strings."""
        out = []
        for name in TEXT_SECTIONS:
            s = self.section(name)
            if s is not None:
                out.append((name, s.addr, s.addr + s.size))
        return out

    def referenced(self) -> Counter:
        """Segment-0-relative addresses the relocations point at → reference count.

        ``R_MIPS_32`` words are direct.  ``HI16``/``LO16`` pairs follow the loader's grouping
        (the HI16s since the previous LO16 form a group) but the ``lui`` of a group is matched
        to the LO16 instruction by REGISTER (``lui rt`` ↔ ``addiu/lw … (rs)``) - the compiler
        interleaves the ``lui`` of two symbols, and pairing "last HI16" with the next LO16 then
        invents addresses in the middle of strings (2 081 of the 19 422 LO16s of the 1.08
        executable use a ``lui`` from an earlier group; none of those invented a string).
        """
        refs: Counter = Counter()
        data = self.data
        for sec in self.sections:
            if sec.sh_type != SHT_PSP_REL:
                continue
            pending: List[Tuple[int, int, int]] = []     # (hi, base, register)
            by_reg: Dict[int, Tuple[int, int, int]] = {}
            processed = False
            for k in range(sec.size // 8):
                r_offset, r_info = struct.unpack_from("<II", data, sec.offset + k * 8)
                rtype = r_info & 0xFF
                ofs_base = (r_info >> 8) & 0xFF
                addr_base = (r_info >> 16) & 0xFF
                if ofs_base >= len(self.segments) or addr_base >= len(self.segments):
                    continue
                here = self.segments[ofs_base].vaddr + r_offset
                fo = self.file_offset(here)
                if fo is None:
                    continue
                word = struct.unpack_from("<I", data, fo)[0]
                base = self.segments[addr_base].vaddr
                if rtype == R_MIPS_32:
                    refs[base + word] += 1
                elif rtype == R_MIPS_HI16:
                    if processed:
                        pending = []
                        processed = False
                    entry = (word & 0xFFFF, base, (word >> 16) & 0x1F)
                    pending.append(entry)
                    by_reg[entry[2]] = entry
                elif rtype == R_MIPS_LO16 and pending:
                    lo = word & 0xFFFF
                    if lo >= 0x8000:
                        lo -= 0x10000
                    rs = (word >> 21) & 0x1F
                    match = [p for p in pending if p[2] == rs]
                    hi = match[-1] if match else by_reg.get(rs, pending[-1])
                    refs[hi[1] + ((hi[0] << 16) + lo)] += 1
                    processed = True
        return refs


# --------------------------------------------------------------------------------------------
# text detection
# --------------------------------------------------------------------------------------------

_JP_STRONG = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\u3000-\u303f\uff01-\uff60\uffe0-\uffe6]")
_HW_KANA = re.compile(r"[\uff61-\uff9f]")
_GREEK_CYRILLIC = re.compile(r"[\u0370-\u04ff]")
_ODD = set("\\{}|^`~#$&*@=;")
_SHORT_ASCII_OK = set(" %+-.,:!()/\n")


def _decode_cp932_raw(raw: bytes) -> Optional[str]:
    """cp932 with the ``0x0F xx`` kana tokens kept verbatim (raw package form)."""
    out: List[str] = []
    i = 0
    n = len(raw)
    while i < n:
        b = raw[i]
        if b == 0x0F:
            if i + 1 >= n or not (0x20 <= raw[i + 1] <= 0x7E):
                return None
            out.append("\x0f" + chr(raw[i + 1]))
            i += 2
            continue
        if 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC:
            try:
                out.append(raw[i:i + 2].decode("cp932"))
            except UnicodeDecodeError:
                return None
            i += 2
            continue
        try:
            out.append(raw[i:i + 1].decode("cp932"))
        except UnicodeDecodeError:
            return None
        i += 1
    return "".join(out)


def _chars_ok(text: str) -> bool:
    for ch in text:
        if ch in "\n\r\t\x0f":
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("C") or cat in ("Zl", "Zp"):
            return False
    return True


def _is_level2(ch: str) -> bool:
    """JIS level-2 (and IBM/NEC extension) kanji: never seen in the game's own text, common in
    the float/int constants that happen to decode as cp932."""
    try:
        b = ch.encode("cp932")
    except UnicodeEncodeError:
        return True
    return len(b) == 2 and (b[0] > 0x98 or (b[0] == 0x98 and b[1] >= 0x9F))


def classify_text(raw: bytes) -> Optional[Tuple[str, str]]:
    """``(text, encoding)`` when ``raw`` reads as Japanese game text, else None.

    Rules, calibrated on the 5 000 relocation targets of the 1.08 executable (every reject
    was checked: float/int constants whose bytes happen to be valid cp932 - ``UUUU``,
    ``33β``, ``ｼG0``, ``囮劔`` …):

    * kana tokens are ``0x0F`` + printable ASCII; every character printable (no control,
      private-use or unassigned code points);
    * Japanese evidence: a hiragana/katakana/kanji/full-width character, or at least two
      half-width kana;
    * no ``\\r`` without ``\\n``; the ASCII symbols the game's text never uses
      (``\\ { } | ^ ` ~ # $ & * @ = ;``) and Greek/Cyrillic only inside long strings;
    * runs of ≤ 4 bytes may not mix ASCII letters/digits with Japanese (except colour codes
      ``＠4``) and may not hold a level-2 kanji; runs of ≤ 8 bytes allow only the ASCII
      punctuation that occurs in labels (``%+-.,:!()/``) and no level-2 kanji without kana.
    """
    if len(raw) < 2:
        return None
    # UTF-8 first: the save-data strings are UTF-8 and would mis-decode as cp932
    if any(b >= 0x80 for b in raw):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if text is not None and _JP_STRONG.search(text) and _chars_ok(text):
            return text, "utf-8"
    text = _decode_cp932_raw(raw)
    if text is None or not _chars_ok(text):
        return None
    plain = re.sub("\x0f.", "", text)
    strong = len(_JP_STRONG.findall(plain))
    hw = len(_HW_KANA.findall(plain))
    if strong == 0 and hw < 2:
        return None
    if plain.count("\r") and plain.count("\r") > plain.count("\n") + (1 if len(plain) > 20 else 0):
        return None
    odd = sum(1 for ch in plain if ch in _ODD)
    if odd and (len(raw) < 12 or odd / max(1, len(plain)) > 0.12):
        return None
    if len(raw) < 12 and _GREEK_CYRILLIC.search(plain):
        return None
    ascii_chars = [ch for ch in plain if ch.isascii()]
    if len(raw) <= 4:
        if ascii_chars and not re.fullmatch(r"(＠.)+", plain):
            return None
        if any(_is_level2(ch) for ch in plain):
            return None
    elif len(raw) <= 8:
        if any(not (ch.isalnum() or ch in _SHORT_ASCII_OK) for ch in ascii_chars):
            return None
        kana = sum(1 for ch in plain if "\u3040" <= ch <= "\u30ff") + hw
        if kana == 0 and any(_is_level2(ch) for ch in plain):
            return None
    return text, "cp932"


def trim_tail(text: str, encoding: str) -> Tuple[str, int]:
    """Drop a trailing level-2 kanji from an otherwise ordinary string (``パイロット：剴`` -
    the two bytes after the colon are not text); returns ``(text, trimmed_chars)``."""
    if encoding != "cp932" or len(text) < 4:
        return text, 0
    body, last = text[:-1], text[-1]
    if _is_level2(last) and not any(_is_level2(ch) for ch in body if ch != "\x0f"):
        return body, 1
    return text, 0


def encode_text(text: str, encoding: str) -> bytes:
    if encoding == "utf-8":
        return text.encode("utf-8")
    out = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "\x0f" and i + 1 < len(text):
            out += b"\x0f" + text[i + 1].encode("ascii")
            i += 2
            continue
        out += text[i].encode("cp932")
        i += 1
    return bytes(out)


# --------------------------------------------------------------------------------------------
# rows
# --------------------------------------------------------------------------------------------

def _part_of(text: str, rel: int) -> str:
    plain = re.sub("\x0f.", "", text)
    if plain.startswith("＠4<") or "発動率" in plain or "包囲率" in plain or "率+" in plain:
        return "ability"
    if len(plain) >= 24 or "。" in plain or "？" in plain or "\n" in plain:
        return "message"
    return "label"


def extract_rows(elf: Elf, container: str = CONTAINER, member: str = MEMBER,
                 include_rejects: bool = False) -> Tuple[List[dict], List[dict]]:
    """Package rows for every referenced text run (and the rejected candidates for review).

    A run is the NUL-terminated byte string around a referenced address; the referenced
    addresses inside it cut it into segments and every segment must read as text on its own.
    Leading segments that do not are skipped (float constants sit right in front of several
    strings without a NUL between); text followed by a non-text segment is a constant table
    and the run is dropped whole.
    """
    refs = elf.referenced()
    data = elf.data
    ranges = elf.text_ranges()
    targets = sorted(r for r in refs if any(a <= r < b for _n, a, b in ranges))
    target_set = set(targets)
    rows: List[dict] = []
    rejects: List[dict] = []
    done_runs = set()
    for rel in targets:
        fo = elf.file_offset(rel)
        if fo is None:
            continue
        end = data.find(b"\0", fo, fo + 4096)
        if end == -1 or end == fo:
            continue
        # the first referenced address of this run owns it (segments follow)
        prev_nul = data.rfind(b"\0", max(0, fo - 4096), fo)
        run_start = prev_nul + 1 if prev_nul != -1 else fo
        first = fo
        for o in range(run_start, fo):
            if (rel - (fo - o)) in target_set:
                first = o
                break
        if first in done_runs:
            continue
        done_runs.add(first)
        fo = first
        rel = elf_rel_of(elf, fo)
        inner = [o for o in range(fo + 1, end) if (rel + (o - fo)) in target_set]
        bounds = [fo] + inner + [end]
        segments: List[Tuple[int, bytes, str, str, int]] = []
        ok = True
        for si in range(len(bounds) - 1):
            seg_fo, seg_end = bounds[si], bounds[si + 1]
            raw = data[seg_fo:seg_end]
            verdict = classify_text(raw)
            if verdict is None:
                if segments:
                    ok = False      # text followed by a non-text segment: a constant table
                    break
                continue            # constants in front of the string (floats share the run)
            text, encoding = verdict
            trimmed = 0
            if si == len(bounds) - 2:
                text, trimmed = trim_tail(text, encoding)
            segments.append((seg_fo, raw, text, encoding, trimmed))
        if not ok or not segments:
            if include_rejects:
                raw_all = data[fo:end]
                rejects.append({"vaddr": "0x%08x" % (LOAD_BASE + rel), "bytes": len(raw_all),
                                "refs": refs[rel], "segments": len(bounds) - 1,
                                "hex": raw_all[:24].hex(),
                                "cp932": raw_all[:24].decode("cp932", "replace")})
            continue
        for si, (seg_fo, raw, text, encoding, trimmed) in enumerate(segments):
            seg_rel = rel + (seg_fo - fo)
            final = si == len(segments) - 1
            slack = 0
            if final and not trimmed:
                slack = _alignment_slack(data, end, rel + (end - fo), target_set)
            rows.append(_row(container, member, seg_rel, seg_fo, raw, text, encoding,
                             refs[seg_rel], final=final, trimmed=trimmed, slack=slack))
    rows.sort(key=lambda r: r["source"]["offset"])
    return rows, rejects


def _alignment_slack(data: bytes, nul_offset: int, nul_rel: int, targets) -> int:
    """Zero bytes after a string's terminator up to the next 4-byte boundary: alignment padding
    the English may use (``敵`` → ``Foe``, ``攻撃`` → ``Attack``).  Only padding that is all
    zero and not itself a relocation target counts; the terminator moves to its end."""
    slack = 0
    pos = nul_offset + 1
    rel = nul_rel + 1
    while rel % 4 != 0 and pos < len(data) and data[pos] == 0 and rel not in targets:
        slack += 1
        pos += 1
        rel += 1
    return slack


def elf_rel_of(elf: Elf, file_offset: int) -> int:
    for seg in elf.segments:
        if seg.p_type == 1 and seg.offset <= file_offset < seg.offset + seg.filesz:
            return seg.vaddr + (file_offset - seg.offset)
    raise ExeError("offset %d outside the loaded segments" % file_offset)


def _row(container: str, member: str, rel: int, offset: int, raw: bytes, text: str,
         encoding: str, nrefs: int, final: bool, trimmed: int = 0, slack: int = 0) -> dict:
    """One package row.  ``bytes`` is the Japanese length; ``max_bytes`` the English budget:
    the Japanese length plus the alignment padding behind the terminator (``source.slack``),
    one less than the Japanese length when the row was trimmed (the terminator must then fit
    inside), exactly the Japanese length for a non-final segment."""
    vaddr = LOAD_BASE + rel
    jp_bytes = encode_text(text, encoding)
    region = len(jp_bytes)
    budget = region - 1 if trimmed else region + slack
    source = {"container": container, "member": member, "offset": offset,
              "vaddr": "0x%08x" % vaddr, "refs": nrefs, "encoding": encoding}
    if not final:
        source["exact"] = True
    if trimmed:
        source["trimmed_tail"] = len(raw) - region
    if slack:
        source["slack"] = slack
    return {
        "id": "exe:%s/%s:0x%08x" % (container, member, vaddr),
        "category": CATEGORY,
        "part": _part_of(text, rel),
        "jp": text,
        "en": "",
        "bytes": region,
        "mode": "slot",
        "max_bytes": budget,
        "source": source,
    }


def load_rows(path: Path) -> List[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_rows(path: Path, rows: Iterable[dict]) -> int:
    n = 0
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


# --------------------------------------------------------------------------------------------
# apply
# --------------------------------------------------------------------------------------------

def check_en(row: dict) -> Tuple[Optional[bytes], Optional[str]]:
    """Encode the row's English for its region; ``(bytes, None)`` or ``(None, reason)``.

    The returned bytes are exactly ``row["bytes"]`` long: NUL-padded for an ordinary slot,
    space-padded (before a trailing split ``＠``) for an exact segment.
    """
    en = row.get("en")
    if not en:
        return None, "empty"
    source = row.get("source") or {}
    encoding = source.get("encoding") or "cp932"
    exact = bool(source.get("exact"))
    jp = row.get("jp") or ""
    if "\x0f" in en:
        return None, "english carries a 0x0F kana token"
    jp_fmt = FORMAT_RE.findall(re.sub("\x0f.", "", jp))
    en_fmt = FORMAT_RE.findall(en)
    if jp_fmt != en_fmt:
        return None, "printf conversions differ: jp %s vs en %s" % (jp_fmt, en_fmt)
    try:
        enc = encode_text(en, encoding)
        region = len(encode_text(jp, encoding))
    except (UnicodeEncodeError, UnicodeDecodeError) as exc:
        return None, "cannot encode: %s" % exc
    slack = int(source.get("slack") or 0)
    span = region + slack
    budget = int(row.get("max_bytes") or region)
    if budget > span or (exact and budget != region):
        return None, "max_bytes %d does not fit the slot (%d jp bytes + %d slack)" % (
            budget, region, slack)
    if len(enc) > budget:
        return None, "over budget: %d > max_bytes %d" % (len(enc), budget)
    if exact:
        jp_dangling = jp.endswith("＠")
        if jp_dangling != en.endswith("＠"):
            return None, "segment must end with the split colour code '＠' like the Japanese"
        pad = region - len(enc)
        if pad:
            enc = enc[:-2] + b" " * pad + enc[-2:] if jp_dangling else enc + b" " * pad
        return enc, None
    return enc + b"\0" * (span - len(enc)), None


def apply_rows(elf_bytes: bytes, rows: Sequence[dict]) -> Tuple[bytes, dict]:
    """Patch the English into the ELF in place; refuse row by row, never move a byte."""
    out = bytearray(elf_bytes)
    report = {"applied": 0, "skipped": [], "empty": 0, "elf_md5_in": hashlib.md5(elf_bytes).hexdigest()}
    for row in rows:
        if row.get("category") != CATEGORY:
            continue
        patch, reason = check_en(row)
        if patch is None:
            if reason == "empty":
                report["empty"] += 1
            else:
                report["skipped"].append({"id": row.get("id"), "reason": reason})
            continue
        source = row.get("source") or {}
        offset = int(source.get("offset", -1))
        encoding = source.get("encoding") or "cp932"
        jp_bytes = encode_text(row.get("jp") or "", encoding)
        region = len(jp_bytes)
        span = len(patch)
        if offset < 0 or offset + span + 1 > len(out):
            report["skipped"].append({"id": row.get("id"), "reason": "offset outside the file"})
            continue
        if bytes(elf_bytes[offset:offset + region]) != jp_bytes:
            report["skipped"].append({"id": row.get("id"),
                                      "reason": "japanese bytes not at offset (other build?)"})
            continue
        if not source.get("exact") and not source.get("trimmed_tail") \
                and any(elf_bytes[offset + region:offset + span + 1]):
            report["skipped"].append({"id": row.get("id"),
                                      "reason": "terminator/padding behind the string is not zero"})
            continue
        out[offset:offset + span] = patch
        report["applied"] += 1
    report["elf_md5_out"] = hashlib.md5(bytes(out)).hexdigest()
    return bytes(out), report


def verify_build(elf_bytes: bytes, rows: Sequence[dict]) -> Tuple[int, int]:
    """``(matching, total)`` rows whose Japanese bytes are where the rows say."""
    total = match = 0
    for row in rows:
        if row.get("category") != CATEGORY:
            continue
        total += 1
        source = row.get("source") or {}
        try:
            jp_bytes = encode_text(row.get("jp") or "", source.get("encoding") or "cp932")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        off = int(source.get("offset", -1))
        if off >= 0 and elf_bytes[off:off + len(jp_bytes)] == jp_bytes:
            match += 1
    return match, total


# --------------------------------------------------------------------------------------------
# CWCheat
# --------------------------------------------------------------------------------------------

def cheat_lines(elf_bytes: bytes, rows: Sequence[dict]) -> Tuple[List[str], dict]:
    """``_L`` lines writing the patched bytes of every applied row (little-endian words)."""
    patched, report = apply_rows(elf_bytes, rows)
    lines: List[str] = []
    elf = Elf(elf_bytes)
    for row in rows:
        if row.get("category") != CATEGORY:
            continue
        source = row.get("source") or {}
        offset = int(source.get("offset", -1))
        patch, _reason = check_en(row)
        budget = len(patch) if patch else 0        # the span the writer owns (incl. padding)
        if offset < 0 or budget <= 0:
            continue
        before = elf_bytes[offset:offset + budget]
        after = patched[offset:offset + budget]
        if before == after:
            continue
        vaddr = int(str(source.get("vaddr")), 16)
        addr = vaddr - CWCHEAT_BASE
        # widen to whole words: the bytes around the span are unchanged in ``patched``, so
        # writing them again is harmless and keeps the cheat list short
        while addr % 4 and offset > 0:
            addr -= 1
            offset -= 1
            budget += 1
        while (addr + budget) % 4 and offset + budget < len(patched):
            budget += 1
        after = patched[offset:offset + budget]
        # whole 32-bit words where possible, then 16-bit, then 8-bit
        pos = 0
        while pos < budget:
            remaining = budget - pos
            if remaining >= 4 and (addr + pos) % 4 == 0:
                word = struct.unpack_from("<I", after, pos)[0]
                lines.append("_L 0x2%07X 0x%08X" % (addr + pos, word))
                pos += 4
            elif remaining >= 2 and (addr + pos) % 2 == 0:
                half = struct.unpack_from("<H", after, pos)[0]
                lines.append("_L 0x1%07X 0x0000%04X" % (addr + pos, half))
                pos += 2
            else:
                lines.append("_L 0x0%07X 0x000000%02X" % (addr + pos, after[pos]))
                pos += 1
    del elf
    return lines, report


def cheat_file(elf_bytes: bytes, rows: Sequence[dict], game_id: str = "NPJH-50521",
               title: str = "Super Robot Taisen OE", name: str = "EXE strings EN") -> Tuple[str, dict]:
    lines, report = cheat_lines(elf_bytes, rows)
    text = ["_S %s" % game_id, "_G %s" % title, "_C1 %s" % name] + lines
    return "\n".join(text) + "\n", report


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

def _load_elf(path: Path) -> Tuple[bytes, str, Optional[bytes]]:
    """``(elf, kind, pbp_blob)``; decrypts ``~PSP`` inputs, keeps the PBP for rebuilding."""
    blob = path.read_bytes()
    if blob[:4] == psp_prx.PBP_MAGIC:
        psp = psp_prx.pbp_get(blob, "DATA.PSP")
        elf = psp if psp[:4] == psp_prx.ELF_MAGIC else psp_prx.decrypt_prx(psp)
        return elf, "pbp", blob
    if blob[:4] == psp_prx.ELF_MAGIC:
        return blob, "elf", None
    return psp_prx.decrypt_prx(blob), "psp", None


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("extract", help="write the package rows of the executable's strings")
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--rejects", type=Path, help="also write the rejected candidates (review)")
    p.add_argument("--container", default=CONTAINER)
    p.add_argument("--member", default=MEMBER)
    p = sub.add_parser("apply", help="write the English into a copy of the executable")
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--rows", type=Path, required=True, nargs="+")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--report", type=Path)
    p = sub.add_parser("cheat", help="emit the edits as a CWCheat file")
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--rows", type=Path, required=True, nargs="+")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--game-id", default="NPJH-50521")
    args = parser.parse_args(argv)

    if args.cmd == "extract":
        elf_bytes, kind, _ = _load_elf(args.exe)
        md5 = hashlib.md5(elf_bytes).hexdigest()
        rows, rejects = extract_rows(Elf(elf_bytes), args.container, args.member,
                                     include_rejects=bool(args.rejects))
        n = write_rows(args.out, rows)
        print("%s: %s ELF md5 %s (%s) -> %d rows, %d bytes of text, %d exact segments" % (
            args.exe.name, kind, md5, KNOWN_ELF_MD5.get(md5, "unknown build"), n,
            sum(r["bytes"] for r in rows), sum(1 for r in rows if r["source"].get("exact"))))
        if args.rejects:
            write_rows(args.rejects, rejects)
            print("rejected candidates: %d -> %s" % (len(rejects), args.rejects))
        return 0

    rows: List[dict] = []
    for path in args.rows:
        rows.extend(load_rows(path))
    elf_bytes, kind, pbp = _load_elf(args.exe)
    match, total = verify_build(elf_bytes, rows)
    if args.cmd == "apply":
        if total and match != total:
            print("ERROR: %d of %d rows do not match this executable - different build; nothing written"
                  % (total - match, total), file=sys.stderr)
            return 2
        patched, report = apply_rows(elf_bytes, rows)
        if pbp is not None:
            out_blob = psp_prx.pbp_replace(pbp, "DATA.PSP", patched)
        else:
            out_blob = patched
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(out_blob)
        report.update({"kind": kind, "out": str(args.out), "out_md5": hashlib.md5(out_blob).hexdigest(),
                       "rows_matching": match, "rows_total": total})
        if args.report:
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("applied %d rows (%d empty, %d refused) -> %s" % (
            report["applied"], report["empty"], len(report["skipped"]), args.out))
        for item in report["skipped"][:20]:
            print("  refused %s: %s" % (item["id"], item["reason"]))
        return 0 if not report["skipped"] else 1

    text, report = cheat_file(elf_bytes, rows, game_id=args.game_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print("cheat: %d lines for %d rows (%d refused, %d/%d rows match this build) -> %s" % (
        text.count("\n_L "), report["applied"], len(report["skipped"]), match, total, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
