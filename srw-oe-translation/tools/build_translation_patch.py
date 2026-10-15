#!/usr/bin/env python3
"""Build the translation patch: one run over the ISO and the DLC tree, every writer chained.

This is the tool ``HOKUS_POKUS.bat`` calls.  It takes

* the user's **ISO** (chapter 1 lives in ``PSP_GAME/USRDIR`` inside it),
* the user's **DLC folder** (the decrypted ``.EDAT``/``.cpk`` files of chapters 2-8 and the
  downloadable dictionaries),
* the **returned translation package** (the same folder that went out: ``00``-``08`` JSONL,
  optionally with the filled ``sceny/`` and ``widoki/`` views next to it - they are imported
  first, exactly like :mod:`translation_import` + :mod:`translation_copy` do by hand),

and writes ``out/patched.iso`` plus ``out/DLC/<the same relative paths>`` - only the files that
actually changed.  Nothing of the user's is modified in place: the ISO is read member by member
(:func:`iso_pack.read_member`) and the patched copy gets the changed members appended
(:func:`iso_pack.patch_iso`); the DLC files are read, never written.

Every row of the package is routed to the one writer that owns its bytes, in an order that keeps
offsets honest:

1. story dialogue (:mod:`event_text_apply`) and battle quotes (:mod:`quotes_apply`) - both grow
   their own containers the way the measured smoke tests proved;
2. the **fragment-pool rows** of the convention-B members (``item_skill_write.apply_tail_pool``):
   the pool behind the item/skill/spirit/status records has its own u32 pointer table (measured
   2026-10-14), so its strings are rewritten at any length and the table recomputed - *before*
   the record rebuild, which then moves the whole pool and re-points its table;
3. the record writers: :mod:`item_skill_write` (items/skills/spirits/status changes, growing the
   record region and recomputing every record's ``+36`` pool pointer) and :mod:`table_write` (the
   dictionary/pool families, growing);
4. :mod:`name_table_write` for the fixed name cells (charalist/unit_list/wp_list);
5. ``sysmes.bin`` through :mod:`sysmes_pack` (the sequential pool is rewritten string by
   string and the relative pointer table recomputed - measured layout, see that module; every
   pool string equal to a row's jp is replaced at once, at any length);
6. everything else measured as ``mode: slot`` through :mod:`slot_apply` (mission notes and
   titles, BGM titles, map/background/group names, leftover slots).

Rows the translator left empty are simply not applied - the bytes stay Japanese, which is the
contract of a partially filled package.  Rows a writer refuses (a translation too long for its
slot, a jp that no longer matches the bytes, two rows fighting over one target) are collected in
``build_report.json`` with their reason; the build does not stop, because one refused line must
not hold the other ten thousand hostage.  The exit code is 0 when every container that had rows
produced a patched file, 1 when something structural broke.  One exception: a member over its
in-game size budget (``item_skill_write.MEMBER_SIZE_LIMITS``, today ``srwDL_Skill00.bin`` at
216 768 B - the game crashes at "Loading" above it, measured 2026-10-15) refuses its WHOLE
container ("NOT written", exit 1) - shipping the container with that member left Japanese
would hide the problem; shorten the English with ``tools/skill_shrink.py`` instead.

Usage::

    python3 tools/build_translation_patch.py --iso ~/ISO/NPJH50521.iso --dlc ~/FULL_DLC \
        --package local/translation --out local/patch [--views local/translation/sceny \
        local/translation/widoki] [--dry-run]
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import sys
import traceback
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import configst_pack as CSP          # noqa: E402
import cpk_write                     # noqa: E402
import event_text_apply as ETA       # noqa: E402
import inline_names as IN            # noqa: E402
import item_skill_records as ISR     # noqa: E402
import item_skill_write as ISW       # noqa: E402
import iso_pack                      # noqa: E402
import name_table_write as NMT       # noqa: E402
import quotes_apply as QA            # noqa: E402
import slot_apply as SLA             # noqa: E402
import sysmes_pack as SMSP           # noqa: E402
import table_write as TW             # noqa: E402

PACKAGE_FILES = (
    "00_dialogue.jsonl",
    "01_battle_quotes.jsonl",
    "02_items.jsonl",
    "03_skills.jsonl",
    "04_config_text.jsonl",
    "05_mission_text.jsonl",
    "07_names_characters.jsonl",
    "08_names_units_weapons.jsonl",
)

#: categories that are never applied (measured binary noise - see docs/COVERAGE.md)
SKIP_CATEGORIES = {"config_item_drop"}


class BuildError(RuntimeError):
    pass


# --------------------------------------------------------------------------- row routing

def load_rows(package: Path) -> List[dict]:
    rows: List[dict] = []
    for name in PACKAGE_FILES:
        path = Path(package) / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            row["__file"] = name
            rows.append(row)
    return rows


def filled(row: dict) -> bool:
    return bool((row.get("en") or "").strip())


def identity(row: dict) -> bool:
    """English == Japanese (exactly or up to surrounding whitespace): nothing to write.

    The exporters showed the translator some strings that are not text at all - PSN content
    ids (``JP0700-NPJH50521_00-ADDPACKAGE000002-J001 ``, with its trailing space), column
    labels like `` N`` - and he copied them back, sometimes trimmed.  Writing the copy back
    would alter bytes the game compares (build #6 lost that trailing space), so such rows
    leave the original bytes alone.
    """
    en, jp = row.get("en"), row.get("jp")
    return isinstance(en, str) and isinstance(jp, str) and bool(en.strip()) \
        and en.strip() == jp.strip()


def owner(row: dict) -> str:
    """Which writer owns this row's bytes.

    The routing is by package file first (each exporter wrote rows only its writer reads
    back), then by member family for the mixed ``04`` file: dictionary/pool families go to
    :mod:`table_write`, item/skill/spirit/status records to :mod:`item_skill_write`, the name
    cells to :mod:`name_table_write`, everything measured as a slot to :mod:`slot_apply`.
    Tail-pool rows of the convention-B members are pulled out of their owner's bucket before
    the run (see :meth:`ContainerBuild.run`) - they belong to the slot writer, first.
    """
    category = row.get("category") or ""
    if category in SKIP_CATEGORIES:
        return "skip"
    source = row.get("source") or {}
    member = source.get("member") or ""
    which = row.get("__file") or ""
    if which.startswith("00") or category == "dialogue":
        return "eta"
    if which.startswith("01") or category == "battle_quote":
        return "qa"
    if category == "config_sysmes":
        return "sysmes"
    if which.startswith("02") or which.startswith("03"):
        return "isw"
    if which.startswith("05"):
        return "sla"
    if which.startswith("07"):
        return "nmt" if NMT.family_of(member) is not None else "tw"
    if which.startswith("08"):
        if _is_unit_series(row) or TW.family_of(member) is not None \
                or category.startswith("robo"):
            return "tw"
        return "nmt" if NMT.family_of(member) is not None else "tw"
    # 04 (and anything else): the member decides
    if TW.family_of(member) is not None:
        return "tw"
    # the DLC copies Skill01-08 / Item01-08 are convention-C pool-only files (no record
    # table, every string has its own offset): the record writer cannot rebuild them and
    # _kind_of says None - the pool writer's C path owns ALL their rows (also the leftover
    # scan's: a C rebuild changes the member's size, so later offset writes would go stale)
    if member.startswith(("srwDL_Skill", "srwDL_Item")) and ISW._kind_of(member) is None:
        return "tw"
    if category in ("config_item", "config_skill", "config_spirit", "config_status_change") \
            or ISW._kind_of(member) is not None:
        return "isw"
    return "sla"


def _is_unit_series(row: dict) -> bool:
    """08 ``unit_list`` series rows are physically RoboDict slot 3 - the table writer owns them."""
    source = row.get("source") or {}
    return (row.get("category") or "").endswith("_series") \
        and (source.get("member") or "").startswith("unit_list")


# --------------------------------------------------------------------------- containers

class ContainerStore:
    """Where each container name lives: inside the ISO, in the DLC tree, or in both."""

    def __init__(self, iso: Optional[Path], dlc: Optional[Path]):
        self.iso = iso
        self.dlc = dlc
        self._iso_keys: Dict[str, Tuple[str, int, int]] = {}
        self._dlc_paths: Dict[str, Path] = {}
        if dlc is not None:
            for path in sorted(dlc.rglob("*")):
                if path.is_file():
                    self._dlc_paths.setdefault(path.name, path)

    def locations(self, name: str) -> List[str]:
        out = []
        if self.iso is not None:
            try:
                self._iso_keys[name] = iso_pack.find_member(self.iso, f"psp_game/usrdir/{name}")
                out.append("iso")
            except ValueError:
                pass
        if name in self._dlc_paths:
            out.append("dlc")
        return out

    def read(self, name: str, where: str) -> bytes:
        if where == "iso":
            key, lba, size = self._iso_keys[name]
            return iso_pack.read_member(self.iso, key.split(";")[0].strip("/"))
        return self._dlc_paths[name].read_bytes()

    def dlc_relpath(self, name: str) -> Optional[str]:
        path = self._dlc_paths.get(name)
        if path is None or self.dlc is None:
            return None
        return str(path.relative_to(self.dlc))

    def iso_key(self, name: str) -> Optional[str]:
        found = self._iso_keys.get(name)
        return found[0] if found else None

    def candidates(self, existing: Dict[str, bytes], limit: int = 16 * 1024 * 1024
                   ) -> Dict[str, bytes]:
        """Every plausible container file not already loaded, name -> bytes."""
        pattern = _PLAUSIBLE
        out: Dict[str, bytes] = {}
        if self.dlc is not None:
            for name, path in self._dlc_paths.items():
                if name in existing or name in out:
                    continue
                try:
                    if path.stat().st_size > limit:
                        continue
                except OSError:
                    continue
                if not (path.suffix.lower() in (".cpk", ".edat") or pattern.search(name)):
                    continue
                try:
                    out[name] = path.read_bytes()
                except OSError:
                    pass
        if self.iso is not None:
            try:
                with self.iso.open("rb") as fh:
                    records = iso_pack._walk_record_offsets(fh)
            except OSError:
                records = {}
            for key, (_off, lba, size, is_dir) in records.items():
                if is_dir or size > limit or "usrdir" not in key.lower():
                    continue
                base = key.split(";")[0].split("/")[-1]
                if base in existing or base in out:
                    continue
                if not (base.lower().endswith((".cpk", ".edat")) or pattern.search(base)):
                    continue
                try:
                    blob = iso_pack.read_member(self.iso, key.split(";")[0].strip("/"))
                except (OSError, ValueError):
                    continue
                self._iso_keys[base] = (key, lba, size)
                out[base] = blob
        return out


#: file names that can hold package members, so a dictionary nobody named explicitly still
#: gets its names (the container-less 07/08 rows are matched against everything plausible)
_PLAUSIBLE = re.compile(r"(config|imenu|mesbtl|event|bgm|sys|srw_?DL|CharaDict|RoboDict)", re.I)


def container_members(blob: bytes) -> List[str]:
    """Every (sub)member name a container holds - used for the container-less 07/08 rows."""
    names: List[str] = []
    try:
        cpk = cpk_write.load_from_bytes(blob) if hasattr(cpk_write, "load_from_bytes") else None
    except Exception:
        cpk = None
    if cpk is None:
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".cpk", delete=False) as fh:
                fh.write(blob)
                tmp = Path(fh.name)
            try:
                cpk = cpk_write.load(tmp)
            finally:
                tmp.unlink(missing_ok=True)
        except Exception:
            return names
    for member in cpk.members:
        names.append(member.name)
        if member.name.lower().endswith(".pac"):
            try:
                names.extend(sub["name"] for sub in
                             CSP.parse_pac(cpk_write.decompressed(member.blob))["subs"])
            except Exception:
                pass
    return names


# --------------------------------------------------------------------------- the chain

class ContainerBuild:
    """One container: read -> every writer in order -> final bytes + report."""

    def __init__(self, name: str, blob: bytes, rows: List[dict], work: Path,
                 dry_run: bool = False):
        self.name = name
        self.rows = rows
        self.work = work
        self.dry_run = dry_run
        self.steps: List[str] = []
        self.current = blob
        self.step_no = 0
        self.report: dict = {"container": name, "rows": len(rows), "steps": [],
                             "problems": [], "changed": False}

    # -- plumbing ---------------------------------------------------------
    def _path(self, blob: bytes) -> Path:
        """Temp file for the chain - the name stays the container's, because writers
        match ``source.container`` against it."""
        folder = self.work / f"step{self.step_no}"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / self.name
        path.write_bytes(blob)
        return path

    def _advance(self, blob: bytes, step: str, summary: dict) -> None:
        if blob is None or blob == self.current:
            self.report["steps"].append({"step": step, "applied": 0, "detail": summary})
            return
        self.current = blob
        self.step_no += 1
        self.report["changed"] = True
        self.report["steps"].append({"step": step, "applied": summary.get("applied", 0)
                                     if isinstance(summary, dict) else 0,
                                     "detail": _shrink(summary)})

    def _run_container_step(self, step: str, func) -> None:
        """Run a writer whose API is ``apply_container(src, dst, rows...)`` over the chain."""
        rows = func["rows"]
        if not rows:
            return
        src = self._path(self.current)
        dst = self.work / f"step{self.step_no + 1}" / self.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            summary = func["call"](src, dst, rows)
        except ISW.SizeBudgetError:
            raise                                   # the whole container is refused (see build())
        except Exception as exc:
            self.report["problems"].append(f"{step}: {exc}")
            self._advance(None, step, {})
            return
        new = dst.read_bytes() if dst.exists() else None
        if not self.dry_run:
            for path in (src, dst):
                if path.exists():
                    path.unlink()
        self._advance(new, step, summary)
        if isinstance(summary, dict):
            self.report["problems"].extend(f"{step}: {p}" for p in summary.get("problems", []))

    # -- steps ------------------------------------------------------------
    def run(self) -> bytes:
        tails: List[dict] = []
        by_owner: Dict[str, List[dict]] = {}
        offsets: Dict[str, Optional[int]] = {}
        for row in self.rows:
            if not filled(row):
                continue
            source = row.get("source") or {}
            member = source.get("member") or ""
            offset = source.get("offset")
            if isinstance(offset, int) and ISW._kind_of(member) is not None:
                if member not in offsets:
                    offsets[member] = self._tail_offset(member)
                if offsets[member] is not None and offset >= offsets[member]:
                    tails.append(row)      # fragment pool: rebuilt with its table, before the records
                    continue
            by_owner.setdefault(owner(row), []).append(row)

        self._eta(by_owner.get("eta", []))
        self._qa(by_owner.get("qa", []))
        self._tail_pool(tails)                            # pool rows: by content or exact offset
        self._isw(by_owner.get("isw", []))
        self._tw(by_owner.get("tw", []))
        self._nmt(by_owner.get("nmt", []))
        self._sysmes(by_owner.get("sysmes", []))
        self._slot_pass("slots", by_owner.get("sla", []))
        return self.current

    def _eta(self, rows: List[dict]) -> None:
        rows = [r for r in rows if filled(r)]
        if not rows:
            return
        by_member: Dict[str, List[dict]] = {}
        for row in rows:
            by_member.setdefault((row.get("source") or {}).get("member") or "", []).append(row)
        for member in sorted(by_member):
            src = self._path(self.current)
            dst = self.work / f"step{self.step_no + 1}" / self.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                summary = ETA.apply_container(src, member, by_member[member], dst)
            except Exception as exc:
                self.report["problems"].append(f"dialogue {member}: {exc}")
                for path in (src, dst):
                    if path.exists() and not self.dry_run:
                        path.unlink()
                continue
            new = dst.read_bytes() if dst.exists() else None
            if not self.dry_run:
                for path in (src, dst):
                    if path.exists():
                        path.unlink()
            self._advance(new, f"dialogue {member}", summary or {})
            # the event writer reports its refusals (a line wider than the box) and skips (a
            # jp no longer at its offset) in their own lists - they belong in the build report
            # like every other writer's, not only in the per-step detail
            for key in ("refused", "skipped", "problems"):
                self.report["problems"].extend(f"dialogue {member}: {p}"
                                               for p in (summary or {}).get(key) or [])

    def _qa(self, rows: List[dict]) -> None:
        rows = [r for r in rows if filled(r)]
        if not rows:
            return
        by_member: Dict[str, List[dict]] = {}
        for row in rows:
            by_member.setdefault((row.get("source") or {}).get("member") or "", []).append(row)
        self._run_container_step("quotes", {"rows": rows, "call": lambda s, d, r: QA.apply_container(s, d, by_member)})

    def _tail_offset(self, member: str) -> Optional[int]:
        kind = ISW._kind_of(member)
        if kind is None:
            return None
        try:
            blob = self._member_blob(member)
            if blob is None:
                return None
            return ISR.parse_member(blob, kind, member, self.name)["tail_offset"]
        except Exception:
            return None

    def _member_blob(self, member: str) -> Optional[bytes]:
        try:
            cpk_path = self._path(self.current)
            try:
                for name, blob in _iter_members(cpk_path):
                    if name == member:
                        return blob
            finally:
                if not self.dry_run:
                    cpk_path.unlink(missing_ok=True)
        except Exception:
            return None
        return None

    def _tail_pool(self, rows: List[dict]) -> None:
        """The fragment pools behind the item/skill/spirit/status records: strings rewritten at
        any length, pointer table recomputed (``item_skill_write.apply_tail_pool``).  Runs before
        the record rebuild, which then re-points the grown pool at its new offset."""
        self._run_container_step("tail-pool", {
            "rows": rows,
            "call": lambda s, d, r: ISW.apply_tail_pool(s, d, r),
        })

    def _isw(self, rows: List[dict]) -> None:
        self._run_container_step("records", {
            "rows": rows,
            "call": lambda s, d, r: ISW.apply_container(s, d, r),
        })

    def _tw(self, rows: List[dict]) -> None:
        rows = [r for r in rows if filled(r)]
        rows = self._redirect_unit_series(rows)
        self._run_container_step("tables", {"rows": rows, "call": TW.apply_container})

    def _redirect_unit_series(self, rows: List[dict]) -> List[dict]:
        """unit_list series rows become RoboDict series rows (slot 3 of the same key)."""
        out: List[dict] = []
        robo_keys = {(r.get("key"), r.get("part")) for r in rows
                     if (r.get("source") or {}).get("member", "").startswith("srw_DL_RoboDict")}
        template = next((r for r in rows if r.get("id", "").startswith("robonote:")
                         and r.get("part") == "series"), None)
        for row in rows:
            if not _is_unit_series(row):
                out.append(row)
                continue
            key = row.get("key")
            if (key, "series") in robo_keys:
                continue                      # the RoboDict row already carries this key
            if template is None:
                self.report["problems"].append(
                    f"unit_series {key}: no RoboDict row to redirect to")
                continue
            clone = dict(template)
            clone.update({"id": row.get("id"), "jp": row.get("jp"), "en": row.get("en"),
                          "key": key, "copy_of": None, "__redirected": True})
            out.append(clone)
        return out

    def _nmt(self, rows: List[dict]) -> None:
        rows = [r for r in rows if filled(r)]
        self._run_container_step("names", {"rows": rows, "call": NMT.apply_container})

    def _sysmes(self, rows: List[dict]) -> None:
        rows = [r for r in rows if filled(r)]
        if not rows:
            return
        step = "sysmes"
        src = self._path(self.current)
        try:
            blob = None
            for name, data in _iter_members(src):
                if name == "sysmes.bin":
                    blob = data
                    break
            if blob is None:
                self.report["problems"].append(f"{step}: {self.name} holds no sysmes.bin")
                return
            edits, problems, notes = _sysmes_edits(blob, rows)
            self.report["problems"].extend(f"{step}: {p}" for p in problems)
            self.report.setdefault("info", []).extend(f"{step}: {n}" for n in notes)
            if not edits:
                self._advance(None, step, {})
                return
            # translate_bytes keeps the measured layout: count strings in sequence, the
            # k-th pointer word = relative offset of the k-th string, ids untouched
            modified, result = SMSP.translate_bytes(blob, edits)
            bad = SMSP.verify(blob, modified, edits)
            if bad:
                raise BuildError("sysmes verify: " + "; ".join(bad[:5]))
            for key in result["unmatched"]:
                self.report["problems"].append(f"{step}: {key[:16]!r} did not land in the pool")
            self.report.setdefault("info", []).append(
                f"{step}: {result['replaced']} strings -> {result['replaced_entries']} pool "
                f"entries rewritten, {result['size'][0]} -> {result['size'][1]} B")
            new = _replace_member(self.current, "sysmes.bin", modified)
            self._advance(new, step, {"applied": result["replaced"],
                                      "entries": result["replaced_entries"]})
        except Exception as exc:
            self.report["problems"].append(f"{step}: {exc}")
            self._advance(None, step, {})
        finally:
            if not self.dry_run:
                src.unlink(missing_ok=True)

    def _slot_pass(self, step: str, rows: List[dict]) -> None:
        rows = [r for r in rows if filled(r) and isinstance((r.get("source") or {}).get("offset"), int)]
        self._run_container_step(step, {"rows": rows, "call": SLA.apply_container})


def _iter_members(path: Path) -> Iterable[Tuple[str, bytes]]:
    cpk = cpk_write.load(path)
    for member in cpk.members:
        body = cpk_write.decompressed(member.blob)
        if member.name.lower().endswith(".pac"):
            try:
                for sub in CSP.parse_pac(body)["subs"]:
                    yield sub["name"], sub["data"]
                continue
            except Exception:
                pass
        yield member.name, body


def _replace_member(container: bytes, sub_name: str, data: bytes) -> bytes:
    """Swap one (sub)member of a container blob, keeping everything else byte-identical."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".cpk", delete=False) as fh:
        fh.write(container)
        tmp = Path(fh.name)
    try:
        cpk = cpk_write.load(tmp)
        replacement = None
        for member in cpk.members:
            if member.name == sub_name:
                replacement = (member.name, data)
                break
            if member.name.lower().endswith(".pac"):
                pac = CSP.parse_pac(cpk_write.decompressed(member.blob))
                changed = False
                for sub in pac["subs"]:
                    if sub["name"] == sub_name:
                        sub["data"] = data
                        changed = True
                if changed:
                    replacement = (member.name, CSP.rebuild_pac(pac))
                    break
        if replacement is None:
            raise BuildError(f"{sub_name} is not a member of the container")
        return cpk_write.rebuild(cpk, replacement=replacement)
    finally:
        tmp.unlink(missing_ok=True)


def _sysmes_edits(blob: bytes, rows: List[dict]
                  ) -> Tuple[Dict[bytes, bytes], List[str], List[str]]:
    """{whole pool string bytes: english bytes} from the rows, plus problems and notes.

    A row's jp is matched against every WHOLE string of the pool (the table has exactly one
    entry per string, :func:`sysmes_pack.parse`) in whatever form it arrived - the file's own
    or the ``%s`` display form - and the English is encoded against the file's bytes
    (:func:`table_write.encode_en`, control tokens included).  Rows whose jp is only the tail
    of a longer string (the old run scanner exported 1,141 such fragments) are not strings
    of their own: they are counted in the notes and ignored, the whole string's row wins.
    """
    edits: Dict[bytes, bytes] = {}
    problems: List[str] = []
    notes: List[str] = []
    strings = [s for s in SMSP.parse(blob).strings if s]
    decoded = [raw.decode("cp932", "replace") for raw in strings]
    displays = [TW.display(raw) for raw in strings]
    # the same lookup order as table_write.match_form: the file's own form first
    by_raw: Dict[str, bytes] = {}
    by_display: Dict[str, bytes] = {}
    for raw, text, shown in zip(strings, decoded, displays):
        by_raw.setdefault(text, raw)
        by_display.setdefault(shown, raw)
    matches: Dict[bytes, List[Tuple[dict, str]]] = {}
    unmatched_rows: List[dict] = []
    for row in rows:
        jp = row.get("jp")
        if jp in by_raw:
            matches.setdefault(by_raw[jp], []).append((row, "raw"))
        elif jp in by_display:
            matches.setdefault(by_display[jp], []).append((row, "display"))
        else:
            unmatched_rows.append(row)
    for raw, found in matches.items():
        encoded = set()
        for row, form in found:
            try:
                encoded.add(TW.encode_en(TW.english(row), raw, form))
            except TW.TableError as exc:
                problems.append(f"sysmes row {row.get('id')}: {exc}")
        if len(encoded) > 1:
            problems.append(f"sysmes string {raw[:12]!r}: {len(encoded)} different translations")
            continue
        if not encoded:
            continue
        value = encoded.pop()
        if b"\x00" in value:
            problems.append(f"sysmes string {raw[:12]!r}: translation contains NUL")
            continue
        edits[raw] = value
    fragments = 0
    stale = 0
    for row in unmatched_rows:
        jp = row.get("jp") or ""
        tail = bool(jp) and any(text.endswith(jp) and text != jp
                                for forms in (decoded, displays) for text in forms)
        if tail:
            fragments += 1
        else:
            stale += 1
    if fragments:
        notes.append(f"{fragments} sysmes rows are tails of longer strings (not pool entries), "
                     f"ignored")
    if stale:
        problems.append(f"{stale} sysmes rows do not occur in this sysmes.bin (stale jp)")
    return edits, problems, notes


def _jsonable(value, depth: int = 0):
    """Everything the writers report, made small and JSON-safe."""
    if isinstance(value, bytes):
        text = repr(value[:40])
        return text + ("…" if len(value) > 40 else "")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v, depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        out = [_jsonable(v, depth + 1) for v in value]
        if len(out) > 20:
            out = out[:20] + [f"… {len(out)} entries in total"]
        return out
    return value


def _shrink(summary) -> dict:
    """Keep the report small: numbers in, long lists and byte strings shortened."""
    if not isinstance(summary, dict):
        return {}
    return _jsonable(summary)


# --------------------------------------------------------------------------- the build

def attach_containerless(rows: List[dict], stores: Dict[str, bytes]) -> Dict[str, List[dict]]:
    """Rows per container; ``container: null`` rows go to every container holding their member."""
    per: Dict[str, List[dict]] = {name: [] for name in stores}
    members: Dict[str, List[str]] = {}
    for row in rows:
        source = row.get("source") or {}
        container = source.get("container")
        if container is not None:
            per.setdefault(container, []).append(row)
            continue
        member = source.get("member") or ""
        if member not in members:
            members[member] = [name for name, blob in stores.items()
                               if any(TW.member_matches(member, have)
                                      for have in container_members(blob))]
        for name in members[member]:
            per.setdefault(name, []).append(row)
    return per


def import_views(package: Path, views: Sequence[Path], work: Path) -> Path:
    """Copy the base package into the work dir and import the returned views into it."""
    import translation_copy
    import translation_import
    target = work / "package"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(package, target)
    args: List[str] = ["--views"] + [str(v) for v in views] + ["--package", str(target)]
    code = translation_import.main(args)
    if code != 0:
        raise BuildError(f"translation_import refused the views (exit {code})")
    code = translation_copy.main(["--package", str(target)])
    if code != 0:
        raise BuildError(f"translation_copy refused the package (exit {code})")
    return target


def container_selected(name: str, only: Sequence[str] = (), skip: Sequence[str] = ()) -> bool:
    """Case-insensitive glob filter on container file names (``configst.cpk``, ``eventP*``).

    ``only`` empty = everything; ``skip`` wins over ``only``.  This is the bisection knob: a
    build limited to one container (or one family) tells which file makes the game crash.
    """
    lower = name.lower()
    if any(fnmatch.fnmatch(lower, pat.lower()) for pat in skip):
        return False
    return not only or any(fnmatch.fnmatch(lower, pat.lower()) for pat in only)


def parse_filter(spec: str) -> Tuple[List[str], List[str]]:
    """``only=glob,glob`` / ``skip=glob,glob`` (the form the .bat passes) -> (only, skip)."""
    kind, sep, globs = spec.partition("=")
    kind = kind.strip().lower()
    if not sep or kind not in ("only", "skip"):
        raise BuildError(f"filter must be only=... or skip=..., got {spec!r}")
    names = [g.strip() for g in globs.split(",") if g.strip()]
    if not names:
        raise BuildError(f"filter {spec!r} names no container")
    return (names, []) if kind == "only" else ([], names)


def build(iso: Optional[Path], dlc: Optional[Path], package: Path, out: Path,
          views: Sequence[Path] = (), work: Optional[Path] = None,
          dry_run: bool = False, only: Sequence[str] = (), skip: Sequence[str] = ()) -> dict:
    if iso is None and dlc is None:
        raise BuildError("give --iso, --dlc or both")
    work = Path(work) if work else out / "work"
    work.mkdir(parents=True, exist_ok=True)
    if views:
        package = import_views(package, views, work)

    rows = load_rows(package)
    filled_rows = [r for r in rows if filled(r)]
    identity_rows = sum(1 for r in filled_rows if identity(r))
    filled_rows = [r for r in filled_rows if not identity(r)]
    report: dict = {"package": str(package), "rows": len(rows), "filled": len(filled_rows),
                    "identity_rows": identity_rows,
                    "containers": [], "problems": [], "dry_run": dry_run,
                    "iso": str(iso) if iso else None, "dlc": str(dlc) if dlc else None,
                    "only": list(only), "skip": list(skip), "written": []}

    store = ContainerStore(iso, dlc)
    names = sorted({(r.get("source") or {}).get("container")
                    for r in filled_rows if (r.get("source") or {}).get("container")})
    names = [n for n in names if container_selected(n, only, skip)]
    blobs: Dict[str, bytes] = {}
    for name in names:
        where = store.locations(name)
        if not where:
            report["problems"].append(f"{name}: not found in the ISO or the DLC folder")
            continue
        blobs[name] = store.read(name, where[0])
    # the container-less 07/08 rows (dictionary names) must find their containers themselves:
    # every plausible file of the DLC folder and of the ISO USRDIR becomes a candidate
    if any((r.get("source") or {}).get("container") is None for r in filled_rows):
        for name, blob in store.candidates(blobs).items():
            if container_selected(name, only, skip):
                blobs.setdefault(name, blob)
    per_container = attach_containerless(filled_rows, blobs)

    iso_patch: Dict[str, bytes] = {}
    for name in sorted(blobs):
        mine = [r for r in per_container.get(name, []) if r.get("category") not in SKIP_CATEGORIES]
        if not mine:
            continue
        builder = ContainerBuild(name, blobs[name], mine, work / name, dry_run=dry_run)
        try:
            final = builder.run()
        except ISW.SizeBudgetError as exc:
            # a member over its in-game size budget: nothing of this container is written -
            # shipping the rest with that member left Japanese would hide the problem
            builder.report["problems"].append(f"NOT written: {exc}")
            report["problems"].append(f"{name}: NOT written: {exc}")
            report["containers"].append(builder.report)
            continue
        except Exception as exc:
            report["problems"].append(f"{name}: build broke: {exc}")
            report["problems"].append(traceback.format_exc(limit=3))
            report["containers"].append(builder.report)
            continue
        report["containers"].append(builder.report)
        if not builder.report["changed"]:
            continue
        for where in store.locations(name):
            if where == "iso":
                key = store.iso_key(name)
                if key:
                    iso_patch[key] = final
            else:
                rel = store.dlc_relpath(name)
                if rel and not dry_run:
                    target = out / "DLC" / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(final)
                    report["written"].append(str(target))
                elif rel:
                    report["written"].append(f"(dry-run) DLC/{rel}")

    if iso_patch and iso is not None and not dry_run:
        out.mkdir(parents=True, exist_ok=True)
        target = out / "patched.iso"
        result = iso_pack.patch_iso(iso, target, iso_patch)
        report["written"].append(str(target))
        report["iso_members"] = result["applied"]
    elif iso_patch:
        report["iso_members"] = sorted(iso_patch)

    (out if not dry_run else work).mkdir(parents=True, exist_ok=True)
    report_path = (out / "build_report.json") if not dry_run else (work / "build_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--iso", type=Path, help="the game ISO (chapter 1 inside)")
    parser.add_argument("--dlc", type=Path, help="folder with the decrypted DLC files")
    parser.add_argument("--package", type=Path, required=True,
                        help="the translation package (base JSONL folder)")
    parser.add_argument("--views", type=Path, nargs="*", default=[],
                        help="returned sceny/ widoki/ folders or zips - imported first")
    parser.add_argument("--out", type=Path, default=Path("local/patch"))
    parser.add_argument("--work", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", nargs="*", default=[], metavar="GLOB",
                        help="patch only these containers (file-name globs, e.g. configst.cpk "
                             "eventP*); everything else stays original")
    parser.add_argument("--skip", nargs="*", default=[], metavar="GLOB",
                        help="leave these containers original (globs; wins over --only)")
    parser.add_argument("--filter", action="append", default=[], metavar="SPEC",
                        help="only=glob,glob or skip=glob,glob - the one-argument form of "
                             "--only/--skip (what BISEKCJA.bat passes); repeatable")
    args = parser.parse_args(argv)

    only, skip = list(args.only), list(args.skip)
    for spec in args.filter:
        more_only, more_skip = parse_filter(spec)
        only += more_only
        skip += more_skip
    report = build(args.iso, args.dlc, args.package, args.out, views=args.views,
                   work=args.work, dry_run=args.dry_run, only=only, skip=skip)
    if only or skip:
        print(f"Filtr kontenerów: only={only or '-'} skip={skip or '-'}")
    changed = [c["container"] for c in report["containers"] if c["changed"]]
    problems = report["problems"]
    print(f"Kontenery z tłumaczeniem: {len(changed)} -> {', '.join(changed) if changed else '(brak)'}")
    print(f"Zapisane pliki: {len(report['written'])}")
    for line in report["written"]:
        print(f"  {line}")
    if problems:
        print(f"Problemy ({len(problems)}) - szczegóły w {report.get('report_path')}:")
        for line in problems[:20]:
            print(f"  {line}")
    return exit_status(problems)


def exit_status(problems: Sequence[str]) -> int:
    """1 when a container was not produced (structural break, missing input, size budget)."""
    return 1 if any("build broke" in p or "not found" in p or "NOT written" in p
                    for p in problems) else 0


if __name__ == "__main__":
    raise SystemExit(main())
