#!/usr/bin/env python3
"""Build the translation patch: one run over the ISO and the DLC tree, every writer chained.

This is the tool ``HOKUS_POKUS.bat`` calls.  It takes

* the user's **ISO** (chapter 1 lives in ``PSP_GAME/USRDIR`` inside it),
* the user's **DLC folder** (the decrypted ``.EDAT``/``.cpk`` files of chapters 2-8 and the
  downloadable dictionaries),
* the **returned translation package** (the same folder that went out: ``00``-``08`` JSONL,
  optionally with the filled ``sceny/`` and ``widoki/`` views next to it - they are imported
  first, exactly like :mod:`translation_import` + :mod:`translation_copy` do by hand),

and writes ``out/patched.iso`` plus ``out/DLC/<container filename>`` - only the files that
actually changed. DLC output is flat, ready to copy directly into NPJH50521 even when the
selected input has chapter/decryption subfolders. Ambiguous duplicate container names are
refused, not silently resolved to the first backup.  Nothing of the user's is modified in place: the ISO is read member by member
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

``--lang pl`` switches the package language: rows are read from the ``pl`` field, the
writers encode through the Polish codec (:mod:`text_codec` → :mod:`pl_text`, the 18
diacritics as private two-byte codes), and the ISO's ``font.cpk`` is extended with the
18 glyphs (:mod:`font_pl`) before anything else is queued for ``patched.iso``.  The
executable strings step stays CP932-strict: a Polish letter in an exe row is refused
with a reason instead of written.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
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

# Written into build_report.json so a report tells which writers produced it (the user's copy
# of the tools is a branch ZIP without git metadata).  Bump when a writer invariant changes.
TOOLS_STAMP = ("2026-10-17-v17: map attr names fixed cells + batch STORED CPK, flat unambiguous DLC output + field read-back contract, conv-B +32/+36/+52, Skill00 budget 216768, DLC pool budget 15638, "
               "skill total 342194, copies resync, UI textures (stored) from ui_labels/, "
               "executable strings in place (ISO PSP_GAME/SYSDIR/EBOOT.BIN -> plain ELF in "
               "patched.iso, PBOOT.PBP -> plain-ELF DATA.PSP) + CWCheat, identical members "
               "mirrored both ways (imenuNN <-> configNN, unit_list series rows follow the "
               "RoboDictionary), viewer slots 5/11 + 2/4/5/6/10, label rows")
import cpk_write                     # noqa: E402
import event_text_apply as ETA       # noqa: E402
import exe_strings as EXE            # noqa: E402
import inline_names as IN            # noqa: E402
import item_skill_records as ISR     # noqa: E402
import item_skill_write as ISW       # noqa: E402
import iso_pack                      # noqa: E402
import name_table_write as NMT       # noqa: E402
import psp_prx                       # noqa: E402
import quotes_apply as QA            # noqa: E402
import slot_apply as SLA             # noqa: E402
import sysmes_pack as SMSP           # noqa: E402
import table_write as TW             # noqa: E402
import text_codec                    # noqa: E402
import ui_texture_patch as UTP       # noqa: E402
import terrain_names as TERRAIN      # noqa: E402
import check_dlc_titles as DLC_TITLES # noqa: E402

PACKAGE_FILES = (
    "00_dialogue.jsonl",
    "01_battle_quotes.jsonl",
    "02_items.jsonl",
    "03_skills.jsonl",
    "04_config_text.jsonl",
    "05_mission_text.jsonl",
    "07_names_characters.jsonl",
    "08_names_units_weapons.jsonl",
    "09_executable.jsonl",
    "10_map_terrain.jsonl",
)

#: categories that are never applied (measured binary noise - see docs/COVERAGE.md)
SKIP_CATEGORIES = {"config_item_drop"}

# configNN.EDAT dictionary spare slots (2026-10-16, v12A/v13/v14 user tests): the v7 viewer
# slots of the Chara/Robo dictionary copies CRASH the game when written into the configNN
# side, while the byte-identical imenuNN side runs (imenu01.EDAT v9 - doubled in size, full
# EN slots - stayed in the emulator folder through every test; v12A "#17 + v11 dictionaries
# in config01-08" crashed, v13 with these rows held back ran).  The dictionary UI reads the
# imenuNN copies (21.34), so the config side keeps name/nickname/series/length EN.
# 2026-10-17 (21.57/21.58): the Robot Viewer foe list ALSO reads the configNN copies and
# falls back to them for chapter-only units - robo_name_narrow + robo_type are ORIGINAL
# cells (present in the JP originals, in-place content replacement like name/series) and
# are RELEASED back; the v7 NEW viewer slots (voice_actor/short/alt/entry/labels) and
# note/weight stay held back - the exact toxic slot was never isolated (bisection closed).
DLC_CONFIG_RE = re.compile(r"^config\d+\.EDAT$", re.IGNORECASE)
CONFIG_DICT_SPARE_CATEGORIES = {
    "character_voice_actor", "character_short_name", "character_alt_name",
    "character_entry", "config_label", "robo_note", "robo_weight",
}


def config_side_spare_row(row: dict) -> bool:
    """True for a row that must not reach a configNN.EDAT dictionary copy: the v7 NEW viewer
    slots (voice_actor with the 'Voice:' label, short_name, alt_name, entry, labels) and
    note/weight.  robo_name_narrow/robo_type are original cells and ARE written (21.58 -
    the foe list of the Robot Viewer reads them).  The imenuNN copies keep everything."""
    return row.get("category") in CONFIG_DICT_SPARE_CATEGORIES


#: USRDIR containers whose GIM textures carry painted captions (tools/ui_texture_patch.py,
#: specs in ui_labels/).  They hold no package text; the builder rewrites them from the ISO
#: when --iso is given.  Members are written STORED - the only variant verified in the game
#: (UI_TEST1 A_stored, 2026-10-15); our CRILAYLA encoder is still untested in-game.
UI_TEXTURE_CONTAINERS = ("system.cpk", "tacsys.cpk", "IM1000.cpk", "IM3000.cpk", "IM9000.cpk", "navisys.cpk")
UI_TEXTURE_COMPRESS = "stored"


class BuildError(RuntimeError):
    pass


# --------------------------------------------------------------------------- row routing

def load_rows(package: Path, lang: str = "en") -> List[dict]:
    rows: List[dict] = []
    for name in PACKAGE_FILES:
        path = Path(package) / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if lang == "pl" and "pl" in row:
                # a Polish package translates the ``pl`` field; every writer keeps
                # reading ``en``, so the field is mapped once, here, at load time
                row["en"] = row.get("pl") or ""
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
    if category == TERRAIN.CATEGORY:
        return "terrain"        # the large map archive has a separate single-pass path
    if category == EXE.CATEGORY:
        return "exe"            # the executable's own strings: exe_step, never a container
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
        self._dlc_fold: Dict[str, Path] = {}
        if dlc is not None:
            for path in sorted(dlc.rglob("*")):
                if not path.is_file():
                    continue
                folded = path.name.casefold()
                previous = self._dlc_fold.get(folded)
                if previous is not None and path.suffix.lower() in (".edat", ".cpk", ".pbp"):
                    a, b = previous.relative_to(dlc), path.relative_to(dlc)
                    raise BuildError(f"ambiguous DLC filename {path.name}: {a} / {b}; "
                                     "select a clean decrypted-input folder, without duplicate backups")
                self._dlc_paths.setdefault(path.name, path)
                self._dlc_fold.setdefault(folded, path)

    def locations(self, name: str) -> List[str]:
        out = []
        if self.iso is not None:
            try:
                self._iso_keys[name] = iso_pack.find_member(self.iso, f"psp_game/usrdir/{name}")
                out.append("iso")
            except ValueError:
                pass
        if name.casefold() in self._dlc_fold:
            out.append("dlc")
        return out

    def read(self, name: str, where: str) -> bytes:
        if where == "iso":
            key, lba, size = self._iso_keys[name]
            return iso_pack.read_member(self.iso, key.split(";")[0].strip("/"))
        return self._dlc_fold[name.casefold()].read_bytes()

    def dlc_path(self, name: str) -> Optional[Path]:
        return self._dlc_fold.get(name.casefold())

    def dlc_relpath(self, name: str) -> Optional[str]:
        """Deployment path: game files are flat inside NPJH50521, not under input backups."""
        path = self.dlc_path(name)
        if path is None or self.dlc is None:
            return None
        return Path(name).name

    def dlc_source_relpath(self, name: str) -> Optional[str]:
        path = self.dlc_path(name)
        return str(path.relative_to(self.dlc)) if path is not None and self.dlc is not None else None

    def iso_key(self, name: str) -> Optional[str]:
        found = self._iso_keys.get(name)
        return found[0] if found else None

    def candidates(self, existing: Dict[str, bytes], limit: int = 16 * 1024 * 1024
                   ) -> Dict[str, bytes]:
        """Every plausible container file not already loaded, name -> bytes."""
        pattern = _PLAUSIBLE
        existing_folded = {name.casefold() for name in existing}
        out: Dict[str, bytes] = {}
        if self.dlc is not None:
            for name, path in self._dlc_paths.items():
                if name.casefold() in existing_folded or name.casefold() in {n.casefold() for n in out}:
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
                if base.casefold() in existing_folded or base.casefold() in {n.casefold() for n in out}:
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
            self.report["steps"].append({"step": step, "applied": 0, "detail": _shrink(summary)})
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


def member_digests(blobs: Dict[str, bytes]) -> Dict[str, Dict[str, str]]:
    """``{container: {member: md5}}`` of every (sub)member the loaded containers hold."""
    out: Dict[str, Dict[str, str]] = {}
    for name, blob in blobs.items():
        try:
            members = _members_of_blob(blob)
        except Exception:
            continue
        out[name] = {m: hashlib.md5(d).hexdigest() for m, d in members.items()}
    return out


def _feeds_member(row: dict, member: str) -> bool:
    """Does this row end up in ``member``?  By address, or by the unit_list -> RoboDict redirect."""
    source = row.get("source") or {}
    if source.get("member") == member:
        return True
    return member.startswith("srw_DL_RoboDict") and _is_unit_series(row)


def mirror_identical_members(per_container: Dict[str, List[dict]],
                             digests: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    """Rows of a member also reach every other container holding a byte-identical copy.

    The intermission reads ``imenuNN`` whose six members are byte-identical to the ``configNN``
    ones [measured 2026-10-16: imenu00-08 vs config00-08, every member; CharaDictionary and
    RoboDictionary of imenu10-19 vs config10-19], while the exporters addressed the Reference,
    Shop and DLC_ID rows to ``configNN`` only - so the config copy was English and the one the
    game draws stayed Japanese.  For every (member, md5) held by two or more loaded containers,
    each container's own rows for that member (``source.container`` = that container; the
    container-less broadcast rows already reach every copy) are duplicated to the others with
    ``source.container`` retargeted and ``mirrored_from`` naming the origin.  A row the target
    already has (same ``id`` and ``jp``) is not duplicated.  Returns ``{target: {source: n}}``.

    A row "belongs" to a member when its ``source.member`` is that member - or when the
    builder redirects it there: the 08 ``unit_list`` series rows are written into RoboDict
    slot 3 (:func:`_is_unit_series`, ``_redirect_unit_series``), so they follow the
    RoboDictionary copy too [build #22, 2026-10-16: ``unit:3600:series`` ``－－－`` -> ``---``
    reached config00's RoboDictionary and not imenu00's - 6 bytes of difference].
    """
    holders: Dict[Tuple[str, str], List[str]] = {}
    for name, members in digests.items():
        for member, digest in members.items():
            holders.setdefault((member, digest), []).append(name)
    added: Dict[str, Dict[str, int]] = {}
    for (member, _digest), names in sorted(holders.items()):
        if len(names) < 2:
            continue
        for target in names:
            own = per_container.get(target, [])
            have = {(r.get("id"), r.get("jp")) for r in own
                    if (r.get("source") or {}).get("member") == member}
            for source in names:
                if source == target:
                    continue
                for row in per_container.get(source, []):
                    src = row.get("source") or {}
                    if src.get("container") != source or row.get("mirrored_from") \
                            or not _feeds_member(row, member):
                        continue
                    key = (row.get("id"), row.get("jp"))
                    if key in have:
                        continue
                    copy = dict(row)
                    copy["source"] = dict(src, container=target)
                    copy["mirrored_from"] = source
                    per_container.setdefault(target, []).append(copy)
                    have.add(key)
                    added.setdefault(target, {}).setdefault(source, 0)
                    added[target][source] += 1
    return added


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


FONT_ISO_KEY = "psp_game/usrdir/font.cpk"


def font_step(report: dict, iso: Optional[Path], iso_patch: Dict[str, bytes],
              only: Sequence[str], skip: Sequence[str], dry_run: bool) -> None:
    """Polish only: write the 18 Polish glyphs into the ISO's ``font.cpk`` (ank.fta).

    The font lives in the disc image (USRDIR), not in the DLC, so the step needs ``--iso``.
    The patched image is queued for ``patched.iso`` like any other ISO member; a font the
    step refuses to touch is a build problem, because shipping a Polish patch without the
    letters would show every diacritic as a broken glyph.
    """
    import font_pl
    step = "font"
    entry: dict = {"containers": [], "problems": []}
    report[step] = entry
    if iso is None:
        entry["problems"].append("the Polish font patch needs the ISO (font.cpk is a disc file)")
        report["problems"].append(f"{step}: NOT written: no ISO given")
        return
    if not container_selected("font.cpk", only, skip):
        entry["skipped"] = ["font.cpk filtered out"]
        return
    try:
        key, _lba, _size = iso_pack.find_member(iso, FONT_ISO_KEY)
        image, summary = font_pl.patch_font_blob(iso_pack.read_member(iso, key))
        entry["containers"] = [{"name": "font.cpk",
                                "glyphs": summary["glyphs"],
                                "bytes": summary["bytes"],
                                "extract": [summary["extract_before"], summary["extract_after"]],
                                "stored": [summary["stored_before"], summary["stored_after"]],
                                "image_size": summary["image_size"],
                                "written": "(dry-run) queued for patched.iso" if dry_run
                                           else f"patched.iso:{key}"}]
        iso_patch[key] = image
    except Exception as exc:
        entry["problems"].append(str(exc))
        report["problems"].append(f"{step}: NOT written: font.cpk: {exc}")


def build(iso: Optional[Path], dlc: Optional[Path], package: Path, out: Path,
          views: Sequence[Path] = (), work: Optional[Path] = None,
          dry_run: bool = False, only: Sequence[str] = (), skip: Sequence[str] = (),
          ui_textures: bool = True, ui_specs: Optional[Path] = None,
          executable: bool = True, cwcheat: bool = False, lang: str = "en") -> dict:
    if iso is None and dlc is None:
        raise BuildError("give --iso, --dlc or both")
    if views and lang == "pl":
        raise BuildError("--views is the English package's import path; a Polish package "
                         "arrives filled in the 'pl' field of the JSONL files")
    text_codec.set_lang(lang)
    work = Path(work) if work else out / "work"
    work.mkdir(parents=True, exist_ok=True)
    if views:
        package = import_views(package, views, work)

    rows = load_rows(package, lang)
    filled_rows = [r for r in rows if filled(r)]
    identity_rows = sum(1 for r in filled_rows if identity(r))
    filled_rows = [r for r in filled_rows if not identity(r)]
    exe_rows = [r for r in filled_rows if owner(r) == "exe"]
    filled_rows = [r for r in filled_rows if owner(r) != "exe"]
    terrain_rows = [r for r in filled_rows if owner(r) == "terrain"]
    filled_rows = [r for r in filled_rows if owner(r) != "terrain"]
    dlc_expected = DLC_TITLES.expectations(filled_rows)
    report: dict = {"package": str(package), "rows": len(rows), "filled": len(filled_rows),
                    "identity_rows": identity_rows, "tools": TOOLS_STAMP, "lang": lang,
                    "containers": [], "problems": [], "dry_run": dry_run,
                    "iso": str(iso) if iso else None, "dlc": str(dlc) if dlc else None,
                    "only": list(only), "skip": list(skip), "written": []}

    try:
        store = ContainerStore(iso, dlc)
    except BuildError as exc:
        report["problems"].append(f"DLC inputs: NOT written: {exc}")
        target = work if dry_run else out
        target.mkdir(parents=True, exist_ok=True)
        report_path = target / "build_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        report["report_path"] = str(report_path)
        return report
    report["dlc_output_layout"] = "flat filenames; copy files directly into memstick/PSP/GAME/NPJH50521"
    names = sorted({(r.get("source") or {}).get("container")
                    for r in filled_rows if (r.get("source") or {}).get("container")})
    names = [n for n in names if container_selected(n, only, skip)]
    if dlc_expected:
        # Do not make activation-title mirroring depend on unrelated containerless
        # character/robot rows happening to be present in the selected package.
        for target in DLC_TITLES.FILES:
            if target not in names and container_selected(target, only, skip) and store.locations(target):
                names.append(target)
        names.sort()
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
    # a member held byte-identically by two containers (imenuNN <-> configNN) is translated
    # once in the package and written to both
    report["mirrored"] = mirror_identical_members(per_container, member_digests(blobs))

    iso_patch: Dict[str, bytes] = {}
    for name in sorted(blobs):
        mine = [r for r in per_container.get(name, []) if r.get("category") not in SKIP_CATEGORIES]
        reported_dlc = name.casefold() in {n.casefold() for n in DLC_TITLES.FILES} and bool(dlc_expected)
        if not mine and not reported_dlc:
            continue
        if DLC_CONFIG_RE.match(name):
            spare_count = sum(1 for r in mine if config_side_spare_row(r))
            if spare_count:
                mine = [r for r in mine if not config_side_spare_row(r)]
                report.setdefault("notes", []).append(
                    f"gate: {name}: held back {spare_count} v7 viewer-slot rows from the "
                    f"config-side dictionary copies (by design; the dictionary UI reads imenuNN)")
        builder = ContainerBuild(name, blobs[name], mine, work / name, dry_run=dry_run)
        try:
            final = builder.run()
            if reported_dlc:
                # A successful writer count is not proof that the reported titles
                # reached the output. Check actual fields by immutable payload IDs.
                check_path = builder.work / "qa-final" / name
                check_path.parent.mkdir(parents=True, exist_ok=True)
                check_path.write_bytes(final)
                try:
                    result = DLC_TITLES.inspect_container(check_path, dlc_expected)
                finally:
                    check_path.unlink(missing_ok=True)
                builder.report["dlc_title_check"] = result
                if not result["passed"]:
                    raise BuildError("reported DLC activation fields did not read back as package English")
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
                    report.setdefault("dlc_source_paths", {})[name] = store.dlc_source_relpath(name)
                elif rel:
                    report["written"].append(f"(dry-run) DLC/{rel}")

    skill_total_check(report, blobs, iso_patch, out, dry_run, store)

    if terrain_rows:
        terrain_step(report, store, terrain_rows, out, work, iso_patch, only, skip, dry_run)

    if iso is not None and ui_textures:
        ui_texture_step(report, iso, iso_patch, work, only, skip, ui_specs)

    if executable and exe_rows:
        exe_step(report, store, exe_rows, out, work, iso_patch, only, skip, dry_run,
                 cwcheat=cwcheat)

    if lang == "pl":
        font_step(report, iso, iso_patch, only, skip, dry_run)

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



def terrain_step(report: dict, store: ContainerStore, rows: List[dict], out: Path,
                 work: Path, iso_patch: Dict[str, bytes], only: Sequence[str],
                 skip: Sequence[str], dry_run: bool) -> None:
    """Keep the 81 MB map archive out of generic dictionary discovery/mirroring.

    Apply once per physical input location; never substitute the ISO's bytes for
    a different DLC-side file with the same name. Inputs are only read.
    """
    name = TERRAIN.CONTAINER
    result = {"rows": len(rows), "targets": [], "problems": []}
    report["terrain"] = result
    if not container_selected(name, only, skip):
        result["status"] = "filtered"
        return
    locations = store.locations(name)
    if not locations:
        message = f"{name}: not found in the ISO or DLC folder (terrain names)"
        result["problems"].append(message)
        report["problems"].append(message)
        return
    for where in locations:
        folder = work / "terrain" / where
        folder.mkdir(parents=True, exist_ok=True)
        src, dst = folder / name, folder / ("patched-" + name)
        try:
            src.write_bytes(store.read(name, where))
            details = TERRAIN.apply_container(src, dst, rows, dry_run=dry_run)
            result["targets"].append({"location": where, **details})
            if dry_run:
                continue
            if where == "iso":
                key = store.iso_key(name)
                if key is None:
                    raise BuildError("terrain ISO member key missing")
                iso_patch[key] = dst.read_bytes()
            else:
                rel = store.dlc_relpath(name)
                if rel is None:
                    raise BuildError("terrain DLC relative path missing")
                target = out / "DLC" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(dst, target)
                report["written"].append(str(target))
        except Exception as exc:
            message = f"{name}: NOT written: terrain name verification: {exc}"
            result["problems"].append(message)
            report["problems"].append(message)
        finally:
            # No proprietary map copies are retained among the tool files.
            src.unlink(missing_ok=True)
            dst.unlink(missing_ok=True)
    result["status"] = "failed" if result["problems"] else "verified"


EXE_ISO_MEMBER = "PSP_GAME/SYSDIR/EBOOT.BIN"      # what the emulator / console boots from the disc
EXE_ISO_KEY = "psp_game/sysdir/eboot.bin"
EXE_ISO_NAME = "EBOOT.BIN"                        # --only/--skip name of the disc target
#: ~PSP header fields two prints of the same program share (used only for the fallback below)
EXE_HEADER_FIELDS = ("modname", "module_version", "elf_size", "entry", "modinfo_offset", "bss_size",
                     "comp_size", "compressed", "devkit_version")


def _exe_elf(blob: bytes) -> Tuple[Optional[bytes], Optional[dict], Optional[str]]:
    """``~PSP`` or plain-ELF bytes → ``(elf, ~PSP header or None, error or None)``."""
    if blob[:4] == psp_prx.ELF_MAGIC:
        return blob, None, None
    try:
        header = psp_prx.psp_header(blob)
    except psp_prx.PrxError as exc:
        return None, None, str(exc)
    try:
        return psp_prx.decrypt_prx(blob), header, None
    except psp_prx.PrxError as exc:
        return None, header, str(exc)


def exe_step(report: dict, store: "ContainerStore", rows: List[dict], out: Path, work: Path,
             iso_patch: Dict[str, bytes], only: Sequence[str], skip: Sequence[str],
             dry_run: bool, cwcheat: bool = False) -> None:
    """Write the ``09_executable.jsonl`` English into the game's executable, in place.

    Two prints of the 1.08 program exist and both are patched when present:

    * ``PSP_GAME/SYSDIR/EBOOT.BIN`` inside the ISO - **the one that runs**: PPSSPP releases
      (and a console booting the disc) load the disc executable; the ISO the user dumped from
      the 1.08 PKG carries the 1.08 program there.  Decrypted by :mod:`psp_prx`, patched by
      :func:`exe_strings.apply_rows` and queued for ``patched.iso`` as a plain ELF (the loader
      takes a plain ELF in place of the signed ``~PSP``; that is how fan patches ship).
    * ``PBOOT.PBP`` of the DLC folder (its ``DATA.PSP``) - the same program as a PSN update.
      Measured 2026-10-15 (user's PPSSPP release build): swapping it alone changes NOTHING,
      the emulator never reads it; it is still written so a loader that does honour the update
      (PPSSPP master's ``FindGameUpdatePBOOT``) shows the same English.

    Nothing moves: every row is checked against the Japanese bytes at its offset, a row that does
    not fit or does not match is refused and listed.  The same edits also go out as a CWCheat
    file (``out/cheats/NPJH50521.ini``) - the route confirmed in-game the same day.

    Fallback (reported as such): when the ISO ``EBOOT.BIN`` carries a tag :mod:`psp_prx` cannot
    decrypt but its ``~PSP`` header equals the PBOOT one in every field of
    :data:`EXE_HEADER_FIELDS`, the patched PBOOT ELF is written as ``EBOOT.BIN`` and the target is
    flagged ``"source": "PBOOT.PBP"`` - the two are the same build by header, not by bytes.
    Honours --only/--skip (``EBOOT.BIN``, ``PBOOT.PBP``).
    """
    summary: dict = {"rows": len(rows), "targets": [], "applied": 0, "skipped": [], "problems": [],
                     "written": [], "notes": []}
    report["executable"] = summary
    want_iso = store.iso is not None and container_selected(EXE_ISO_NAME, only, skip)
    want_pboot = container_selected(EXE.CONTAINER, only, skip)
    if not want_iso and not want_pboot:
        summary["problems"].append("filtered out (--only/--skip)")
        return

    # ---- sources -------------------------------------------------------------------------
    sources: List[dict] = []          # each: name, label, blob, elf, header, error, rel/key
    if want_iso:
        try:
            key, _lba, _size = iso_pack.find_member(store.iso, EXE_ISO_KEY)
            blob = iso_pack.read_member(store.iso, EXE_ISO_KEY)
            elf, header, err = _exe_elf(blob)
            sources.append({"name": EXE_ISO_NAME, "label": f"ISO {EXE_ISO_MEMBER}", "blob": blob,
                            "elf": elf, "header": header, "error": err, "key": key})
        except ValueError:
            summary["notes"].append(f"{EXE_ISO_MEMBER} not in the ISO")
    pboot_path = store.dlc_path(EXE.CONTAINER) if want_pboot else None
    if pboot_path is not None:
        try:
            pbp = pboot_path.read_bytes()
            psp = psp_prx.pbp_get(pbp, EXE.MEMBER)
            elf, header, err = _exe_elf(psp)
            sources.append({"name": EXE.CONTAINER, "label": f"DLC {EXE.CONTAINER}/{EXE.MEMBER}",
                            "blob": psp, "pbp": pbp, "elf": elf, "header": header, "error": err,
                            "rel": store.dlc_relpath(EXE.CONTAINER) or EXE.CONTAINER})
        except Exception as exc:  # noqa: BLE001 - PrxError / KeyError / OSError: reported, not fatal
            sources.append({"name": EXE.CONTAINER, "label": f"DLC {EXE.CONTAINER}/{EXE.MEMBER}",
                            "blob": b"", "elf": None, "header": None, "error": str(exc),
                            "rel": store.dlc_relpath(EXE.CONTAINER) or EXE.CONTAINER})
    elif want_pboot:
        summary["notes"].append(f"{EXE.CONTAINER} not found under --dlc (the 1.08 update; optional "
                                f"now that the ISO's {EXE_ISO_MEMBER} is patched)")
    if not sources:
        msg = (f"no executable to patch: neither {EXE_ISO_MEMBER} in the ISO nor {EXE.CONTAINER} "
               f"under --dlc; {len(rows)} rows not written")
        summary["problems"].append(msg)
        report["problems"].append(f"executable: {msg}")
        return

    # ---- fallback: undecryptable disc EBOOT, header-identical to the decrypted PBOOT ---------
    by_name = {src["name"]: src for src in sources}
    disc, update = by_name.get(EXE_ISO_NAME), by_name.get(EXE.CONTAINER)
    if disc and disc["elf"] is None and disc["header"] and update and update["elf"] is not None \
            and update["header"]:
        same = all(disc["header"].get(f) == update["header"].get(f) for f in EXE_HEADER_FIELDS)
        if same:
            disc["elf"] = update["elf"]
            disc["source"] = EXE.CONTAINER
            disc["notes"] = (f"{disc['error']}; its ~PSP header equals the {EXE.CONTAINER} one in "
                             f"{', '.join(EXE_HEADER_FIELDS)} - the patched {EXE.CONTAINER} program "
                             f"is written as {EXE_ISO_MEMBER} (same build by header, not verified "
                             f"byte for byte)")
            disc["error"] = None
        else:
            diff = [f for f in EXE_HEADER_FIELDS if disc["header"].get(f) != update["header"].get(f)]
            disc["error"] += f"; ~PSP header differs from {EXE.CONTAINER} in {', '.join(diff)}"

    # ---- patch every source that yielded an ELF ---------------------------------------------
    cheat_elf: Optional[bytes] = None
    for src in sources:
        tgt: dict = {"target": src["label"], "name": src["name"], "applied": 0, "skipped": [],
                     "problems": []}
        if src.get("header"):
            tgt["tag"] = "0x%08X" % src["header"]["tag"]
            tgt["modname"] = src["header"]["modname"]
            tgt["module_version"] = src["header"]["module_version"]
        if src.get("source"):
            tgt["source"] = src["source"]
            tgt["note"] = src["notes"]
            summary["notes"].append(f"{src['label']}: {src['notes']}")
        summary["targets"].append(tgt)
        if src["elf"] is None:
            tgt["problems"].append(f"cannot read the executable: {src['error']}")
            report["problems"].append(f"executable: {src['label']}: cannot read: {src['error']}")
            continue
        elf = src["elf"]
        md5_in = hashlib.md5(elf).hexdigest()
        tgt["elf_md5_in"] = md5_in
        tgt["elf_bytes"] = len(elf)
        tgt["known"] = EXE.KNOWN_ELF_MD5.get(md5_in)
        match, total = EXE.verify_build(elf, rows)
        tgt["rows_matching_japanese"] = match
        if match == 0:
            msg = (f"none of the {total} rows finds its Japanese bytes in {src['label']} (ELF md5 "
                   f"{md5_in}): a different print of the executable - nothing written")
            tgt["problems"].append(msg)
            report["problems"].append(f"executable: {msg}")
            continue
        patched, exe_report = EXE.apply_rows(elf, rows)
        tgt["applied"] = exe_report["applied"]
        tgt["empty"] = exe_report["empty"]
        tgt["skipped"] = exe_report["skipped"]
        tgt["elf_md5_out"] = hashlib.md5(patched).hexdigest()
        if exe_report["skipped"]:
            report["problems"].append(f"executable: {src['label']}: {len(exe_report['skipped'])} "
                                      f"row(s) refused (see executable.targets in the report)")
        if not exe_report["applied"]:
            continue
        if src["name"] == EXE_ISO_NAME:
            cheat_elf = elf                      # the program that actually runs
            iso_patch[src["key"]] = patched       # plain ELF in place of the signed ~PSP
            tgt["iso_member_bytes"] = {"original": len(src["blob"]), "patched": len(patched)}
            tgt["written"] = ("(dry-run) " if dry_run else "") + f"patched.iso:{EXE_ISO_MEMBER}"
            summary["written"].append(tgt["written"])
        else:
            cheat_elf = cheat_elf or elf
            new_pbp = psp_prx.pbp_replace(src["pbp"], EXE.MEMBER, patched)
            if dry_run:
                tgt["written"] = f"(dry-run) DLC/{src['rel']}"
            else:
                target = out / "DLC" / src["rel"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(new_pbp)
                tgt["written"] = str(target)
                report["written"].append(str(target))
                back = psp_prx.pbp_get(target.read_bytes(), EXE.MEMBER)
                tgt["verified"] = back == patched
                if not tgt["verified"]:
                    report["problems"].append(f"executable: read-back of the written {EXE.CONTAINER} differs")
            summary["written"].append(tgt["written"])

    # the headline numbers follow the program that runs (disc), else the update
    primary = next((t for t in summary["targets"] if t["name"] == EXE_ISO_NAME and "elf_md5_in" in t),
                   None) or next((t for t in summary["targets"] if "elf_md5_in" in t), None)
    if primary:
        summary["applied"] = primary["applied"]
        summary["skipped"] = primary["skipped"]
        summary["primary"] = primary["name"]

    # ---- CWCheat file (opt-in, --cwcheat): the same bytes as a cheat.  Since the in-place
    # EBOOT edit is the proven route (21.55), the ini is no longer written by default.
    if not cwcheat:
        return
    if cheat_elf is None:
        return
    cheat_text, _ = EXE.cheat_file(cheat_elf, rows)
    if dry_run:
        summary["written"].append("(dry-run) cheats/NPJH50521.ini")
        return
    cheat = out / "cheats" / "NPJH50521.ini"
    cheat.parent.mkdir(parents=True, exist_ok=True)
    cheat.write_text(cheat_text, encoding="utf-8", newline="\r\n")
    summary["written"].append(str(cheat))
    report["written"].append(str(cheat))


def ui_texture_step(report: dict, iso: Path, iso_patch: Dict[str, bytes], work: Path,
                    only: Sequence[str], skip: Sequence[str], specs_dir: Optional[Path]) -> None:
    """Paint the English captions into the UI textures of the ISO's USRDIR containers.

    The originals are read from the ISO into ``work/ui_originals`` (never from the user's
    folders), rebuilt by :func:`ui_texture_patch.build` (fit is fail-closed, bytes outside the
    textures must stay identical, every member is read back) and queued for ``patched.iso``.
    A failure is a build problem (exit 1) and leaves those containers untouched; the text
    containers are not affected either way.  Honours --only/--skip like every container.
    """
    specs_dir = Path(specs_dir) if specs_dir else UTP.DEFAULT_SPECS
    summary: dict = {"compress": UI_TEXTURE_COMPRESS, "specs": str(specs_dir), "containers": [],
                     "skipped": [], "problems": []}
    report["ui_textures"] = summary
    try:
        import PIL  # noqa: F401  (the caption renderer needs Pillow; HOKUS_POKUS installs it)
    except ImportError:
        msg = ("Pillow (PIL) is not installed - the UI texture step needs it: "
               "python -m pip install pillow  (or build text only with --no-ui-textures)")
        summary["problems"].append(msg)
        report["problems"].append(f"ui textures: build broke: {msg}")
        return
    try:
        specs = UTP.load_specs(specs_dir)
    except Exception as exc:  # noqa: BLE001 - reported, never half-applied
        summary["problems"].append(f"specs: {exc}")
        report["problems"].append(f"ui textures: build broke: specs: {exc}")
        return
    originals = work / "ui_originals"
    out_dir = work / "ui_build"
    shutil.rmtree(originals, ignore_errors=True)
    shutil.rmtree(out_dir, ignore_errors=True)
    originals.mkdir(parents=True, exist_ok=True)
    keys: Dict[str, str] = {}
    for name in UI_TEXTURE_CONTAINERS:
        if not container_selected(name, only, skip):
            summary["skipped"].append(f"{name}: filtered out (--only/--skip)")
            continue
        try:
            key, _lba, _size = iso_pack.find_member(iso, f"psp_game/usrdir/{name}")
        except ValueError:
            summary["skipped"].append(f"{name}: not in the ISO")
            continue
        clean = key.split(";")[0].strip("/")
        (originals / name).write_bytes(iso_pack.read_member(iso, clean))
        keys[name] = key
    if not keys:
        return
    try:
        results = UTP.build(originals, out_dir, specs, UI_TEXTURE_COMPRESS)
    except Exception as exc:  # noqa: BLE001 - UiPatchError / LabelError / GimError / ValueError
        summary["problems"].append(str(exc))
        report["problems"].append(f"ui textures: build broke: {exc}")
        return
    for res in results:
        entry = _jsonable(vars(res))
        summary["containers"].append(entry)
        if res.name in keys:
            iso_patch[keys[res.name]] = (out_dir / res.name).read_bytes()
    built = {r.name for r in results}
    for name in keys:
        if name not in built:
            summary["skipped"].append(f"{name}: no spec'd texture inside")


# The largest "Skill00 + the eight DLC pools" that booted in the game (variant W1, 2026-10-15:
# 217 090 + 8 x 15 638).  Whether the budget is one shared arena or per member is open; this
# sum is the conservative reading and is reported, not enforced per container (each member has
# its own gate), so a build whose members all fit but whose sum does not is still flagged.
SKILL_TOTAL_LIMIT = 342_194
SKILL_MEMBERS = {"config00.cpk": "srwDL_Skill00.bin",
                 **{f"config0{n}.EDAT": f"srwDL_Skill0{n}.bin" for n in range(1, 9)}}


def skill_total_check(report: dict, blobs: Dict[str, bytes], iso_patch: Dict[str, bytes],
                      out: Path, dry_run: bool, store: Optional["ContainerStore"] = None) -> None:
    """Sum the skill members of the containers this build produced (originals for the ones it
    did not touch) and flag a sum over ``SKILL_TOTAL_LIMIT`` in the report."""
    sizes: Dict[str, int] = {}
    missing: List[str] = []
    for container, member in SKILL_MEMBERS.items():
        blob = None
        for key, patched in iso_patch.items():          # built for the ISO (config00.cpk)
            if key.rsplit("/", 1)[-1].lower() == container.lower():
                blob = patched
        rel = (store.dlc_relpath(container) if store is not None else None) or container
        written = None if dry_run else (out / "DLC" / rel)
        if blob is None and written is not None and written.exists():
            blob = written.read_bytes()                 # built for the DLC folder
        if blob is None and container in blobs:
            blob = blobs[container]                     # untouched (or refused): the original
        if blob is None:
            missing.append(container)
            continue
        try:
            subs = _members_of_blob(blob)
        except Exception as exc:                   # noqa: BLE001 - a note, never a build problem
            report.setdefault("notes", []).append(
                f"skill total: {container}: parsowanie pominione ({exc})")
            missing.append(container)
            continue
        if member not in subs:
            missing.append(container)
            continue
        sizes[member] = len(subs[member])
    total = sum(sizes.values())
    report["skill_total"] = {"members": sizes, "total": total, "limit": SKILL_TOTAL_LIMIT,
                             "missing": missing,
                             "fits": (total <= SKILL_TOTAL_LIMIT) if not missing else None}
    if missing:
        return                                      # not all nine were available - nothing to judge
    if total > SKILL_TOTAL_LIMIT:
        report["problems"].append(
            f"skill total: Skill00 + 8 DLC pools = {total} B exceeds {SKILL_TOTAL_LIMIT} B "
            f"(+{total - SKILL_TOTAL_LIMIT} B; the largest total that booted in the game) - "
            f"shorten with tools/skill_shrink.py --dlc-original before shipping")


def _members_of_blob(blob: bytes) -> Dict[str, bytes]:
    """``{sub-file name: bytes}`` of a one-``.pac`` container held in memory (``cpk_write.load``
    reads from a path, so the blob goes through a temporary file)."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".cpk", delete=False) as handle:
        handle.write(blob)
        path = Path(handle.name)
    try:
        cpk = cpk_write.load(path)
    finally:
        path.unlink(missing_ok=True)
    subs: Dict[str, bytes] = {}
    for member in cpk.members:
        body = cpk_write.decompressed(member.blob)
        if member.name.lower().endswith(".pac"):
            for sub in CSP.parse_pac(body)["subs"]:
                subs[sub["name"]] = sub["data"]
        else:
            subs[member.name] = body
    return subs


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
    parser.add_argument("--no-ui-textures", action="store_true",
                        help="leave the UI texture containers (system.cpk, tacsys.cpk, IM*.cpk) "
                             "original - text only")
    parser.add_argument("--no-exe", action="store_true",
                        help="skip the executable strings step (ISO EBOOT.BIN / PBOOT.PBP in place)")
    parser.add_argument("--cwcheat", action="store_true",
                        help="also write cheats/NPJH50521.ini (CWCheat mirror of the exe strings; "
                             "off by default - the in-place EBOOT edit is the proven route)")
    parser.add_argument("--ui-specs", type=Path, default=None,
                        help="folder with the texture caption specs (default ui_labels/)")
    parser.add_argument("--lang", choices=("en", "pl"), default="en",
                        help="package language: en = the 'en' field, CP932 (default); "
                             "pl = the 'pl' field, Polish private-code codec + font patch")
    args = parser.parse_args(argv)

    only, skip = list(args.only), list(args.skip)
    for spec in args.filter:
        more_only, more_skip = parse_filter(spec)
        only += more_only
        skip += more_skip
    report = build(args.iso, args.dlc, args.package, args.out, views=args.views,
                   work=args.work, dry_run=args.dry_run, only=only, skip=skip,
                   ui_textures=not args.no_ui_textures, ui_specs=args.ui_specs,
                   executable=not args.no_exe, cwcheat=args.cwcheat, lang=args.lang)
    if only or skip:
        print(f"Filtr kontenerów: only={only or '-'} skip={skip or '-'}")
    changed = [c["container"] for c in report["containers"] if c["changed"]]
    problems = report["problems"]
    print(f"Kontenery z tłumaczeniem: {len(changed)} -> {', '.join(changed) if changed else '(brak)'}")
    ui = report.get("ui_textures") or {}
    if ui.get("containers"):
        names = [c["name"] for c in ui["containers"]]
        print(f"Tekstury UI (napisy w grafikach): {len(names)} -> {', '.join(names)}")
    exe = report.get("executable") or {}
    if exe:
        for tgt in exe.get("targets") or []:
            if "elf_md5_in" in tgt:
                extra = f" (program wzięty z {tgt['source']})" if tgt.get("source") else ""
                print(f"Program gry [{tgt['target']}]: {tgt.get('applied', 0)} z {exe.get('rows', 0)} "
                      f"napisów wpisanych, {len(tgt.get('skipped') or [])} odrzuconych{extra}")
            else:
                print(f"Program gry [{tgt['target']}]: NIE ZAPISANY - {'; '.join(tgt.get('problems') or [])}")
        for note in exe.get("notes") or []:
            print(f"  uwaga: {note}")
        if not exe.get("targets"):
            print(f"Program gry: {'; '.join(exe.get('problems') or ['nic do zrobienia'])}")
    terrain = report.get("terrain") or {}
    for target in terrain.get("targets", []):
        print(f"Nazwy terenu [{target['location']}]: {target['copies']} map, "
              f"{target['applied']} komórek; {target['original_bytes']} -> {target['new_bytes']} B")
    print(f"Zapisane pliki: {len(report['written'])}")
    for line in report["written"]:
        print(f"  {line}")
    notes = report.get("notes") or []
    gate = [n for n in notes if n.startswith("gate:")]
    if gate:
        total = 0
        for line in gate:
            try:
                total += int(line.split("held back ")[1].split(" ")[0])
            except (IndexError, ValueError):
                pass
        print(f"Uwagi planowe (nie błędy): bramka słownikowa configNN — {total} wierszy v7 "
              f"trzymanych z dala od strony config w {len(gate)} plikach (celowe; "
              f"szczegóły w build_report.json)")
    for line in [n for n in notes if not n.startswith("gate:")]:
        print(f"Uwaga: {line}")
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
