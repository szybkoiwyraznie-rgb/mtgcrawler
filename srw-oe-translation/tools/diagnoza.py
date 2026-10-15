#!/usr/bin/env python3
"""Collect the facts about WHAT is installed where (what ``DIAGNOZA.bat`` runs).

The user reports "the same crash as before" after a full patch; from a screenshot alone it is
impossible to tell whether the crash comes from the new files or from old ones that were
never replaced.  This tool answers that without the user typing anything:

* which **tools** are next to it (fingerprint of the writers; does the +52 fix exist?),
* which **package** lies in ``pakiet_EN\\`` (v1 of 2026-10-14 / v2 "ciasny" / v3 / v4 / unknown,
  recognised by the md5 of ``03_skills.jsonl`` and ``04_config_text.jsonl``; a nested folder
  is reported too),
* what ``HOKUS_POKUS.bat`` produced in ``srw-oe-patch\\`` (``build_report.json`` summary, md5 of
  every output, the five USRDIR members read back from ``patched.iso``),
* what lies in the **emulator's DLC folder** (every file: size, md5 for the small ones; is it
  the original size, is it byte-identical to the build output, which build is a
  ``config00.cpk``/``configst.cpk``),
* optionally what the **ISO the user runs** carries under ``PSP_GAME/USRDIR`` (original /
  build #14 / known older build / unknown).

Everything is read-only; the only file written is the report (UTF-8 with BOM, CRLF, so
Notepad shows it).  Names, sizes and md5 only - never game bytes.

Usage::

    python tools/diagnoza.py --dlc <emulator DLC folder> [--iso <iso run in PPSSPP>]
                             [--root <srw-oe-translation folder>] [--out DIAGNOZA.txt]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from iso_insert import KNOWN_ORIGINALS  # noqa: E402

USRDIR_NAMES = ("config00.cpk", "configst.cpk", "eventP00.cpk", "imenu00.cpk", "mesbtl00.cpk")

# md5 -> label of every config00/configst we ever handed out (EXPERIMENT_LOG.md 21.x).
KNOWN_CONFIG: Dict[str, str] = {
    # config00.cpk
    "266366c3bee66130d4b7cb57a1b1e3d4": "ORYGINAL",
    "80b8fae61b858fb91db35532c4680c6f": "BUILD17 (pakiet v4: Skill00 215 462 B; SPRAWDZONY W GRZE 2026-10-15: Y4a/Y4/Z4)",
    "71d9fcafa37c21513b97c14d1dff8f33": "BUILD14 (poprawny, sprawdzony w grze; pakiet v2/v3 - starszy niz BUILD17)",
    "3c56686d04cb1c362c7cb72111598879": "build #12 (stary: nieswiezy +52, pada na sejwie z 2. rozdzialu)",
    "abacf828a966bb0dc1e51f555a541eab": "build #11 (stary: nieswiezy +32/+52, pada w intermisji)",
    "372513258059c47217013e0fce138d78": "build #10 (stary: Skill00 za duzy, pada na Loading)",
    "d42e1493e6e15d8484ea98c9b40fbe6e": "build #9 (stary: Skill00 za duzy, pada na Loading)",
    "202c2d2476f36e37c619fdc088d9caa3": "build #6/#7 (stary: Skill00 za duzy, pada na Loading)",
    "608ffa3c1dd9b3318649224d20411851": "wariant Y5 z rundy 8 (test, nie build)",
    # configst.cpk
    "c87e404032fc5cadc7aae22f15f6833b": "ORYGINAL",
    "6cfe245d5f6ec6dfffd2a829b778a4d7": "BUILD14 (poprawny, sprawdzony w grze)",
    "27a8cdeaa82a9e1436c18cd9a80783fa": "build #13 (stary: nieswiezy +52)",
    "856f8ba52d366bdf72bc742d50e3af5b": "build #12 (stary: nieswiezy +52)",
    "512e2397c42f8cde7d4f8ae45c0e48d7": "build #11 (stary: nieswiezy +32/+52)",
    "ee1aae959b68fc356a68b0fa86076f57": "build #10 (stary)",
    "dd7e626bd7f14645abc52a2bf5bdb7c4": "build #6/#7 (stary: zly sysmes)",
}
EXPECTED_BUILD14 = {
    "config00.cpk": "71d9fcafa37c21513b97c14d1dff8f33",
    "configst.cpk": "6cfe245d5f6ec6dfffd2a829b778a4d7",
}
# every config00/configst that is fine in the emulator folder today: BUILD14 (tested in the game)
# and BUILD17 (package v4 - keeps the DLC pools at their original size; accepted in-game 2026-10-15)
ACCEPTED_CONFIG = {
    "config00.cpk": {"71d9fcafa37c21513b97c14d1dff8f33": "BUILD14",
                     "80b8fae61b858fb91db35532c4680c6f": "BUILD17"},
    "configst.cpk": {"6cfe245d5f6ec6dfffd2a829b778a4d7": "BUILD14 (= BUILD17)"},
}
# md5 -> label of the config01-08.EDAT builds handed out (the DLC skill pools live there)
KNOWN_DLC_CONFIG: Dict[str, str] = {
    # build #15 (pakiet v3): pule Skill01-08 17 396 B - test Y 2026-10-15 padl na Loading
    "6199c7dec872e6d10767ac952e872a14": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    "e21939c44fbbedbab3e4ec2d782e08e9": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    "a701413af928d3d7ccad5233d4e78456": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    "8e4ab123da231b00f3893a76306f87da": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    "8f2a6292322f3d04d93e44277b462e48": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    "41b25268ddbd97cca2963960ca266f68": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    "75c1101fac48de719b899cf0dba95ff1": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    "bbeddd5eb5049b00e318d76128e23706": "build #15 (pakiet v3; pula 17 396 B - padl w tescie Y)",
    # build #17 (pakiet v4): pule 15 578 B (< oryginal 15 638 B)
    "7c6459fa7377b585a5176b5859361da2": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    "a7f034d10cc07c771bfc975aeec73b5b": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    "6af12bab9c1b81db9952beff2279205b": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    "9a8a771573ccd68eceadfc9a111c95b1": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    "e3694678a42f1d78d2f10d80bcfdb004": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    "ebeace423570cda94d1d3b1ea23d6435": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    "60eab71a9ff17806cbfd554401b7a46f": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    "735cdf6c59febd80d1aacce62ae87b9b": "build #17 (pakiet v4; pula 15 578 B; sprawdzony w grze Y4a/Y4/Z4)",
    # wariant testowy "pula JP": pule oryginalne (15 638 B), reszta EN
    "1bfb935293c5c2f51e719a3176420003": "wariant pulaJP (pula oryginalna, reszta EN)",
    "8eb2ef592fc15e5646df0bdfff2fae54": "wariant pulaJP (pula oryginalna, reszta EN)",
    "35face1f8c3b904d24c1b71c4b90f197": "wariant pulaJP (pula oryginalna, reszta EN)",
    "8b5f08da3c9bd9bbf2abb6c49a3487fb": "wariant pulaJP (pula oryginalna, reszta EN)",
    "0fdc2d6abce956c03fe3dfe7d6673dff": "wariant pulaJP (pula oryginalna, reszta EN)",
    "8c9216f74b6fe06371880e169e9119ce": "wariant pulaJP (pula oryginalna, reszta EN)",
    "43006c180269e950377068918179651f": "wariant pulaJP (pula oryginalna, reszta EN)",
    "e103d1efa90d620a93f321e6137a8911": "wariant pulaJP (pula oryginalna, reszta EN)",
}
# the three other USRDIR containers as built from package v3 with the 2026-10-15 tools
CANONICAL_USRDIR = {
    "eventP00.cpk": ("ac538959fdef3d47eeb38d0e2282adb0", 260568),
    "imenu00.cpk": ("ee66a6f824a54f2ee27c8309db16294a", 57512),
    "mesbtl00.cpk": ("00e10760c204e75133169b3455b19608", 994008),
}

# package versions by the md5 of 03_skills.jsonl / 04_config_text.jsonl
PACKAGE_VERSIONS: Dict[Tuple[str, str], str] = {
    ("6bccde6c26cf68079d91cc2f622954fc", "e507178333591fbfc6cfb3123239a19f"):
        "v1 (2026-10-14) - STARY: Skill00 nieskrocony, z nowymi narzedziami config00 NIE jest zapisywany",
    ("68c58d144c81b9edf27eb77164d2ca5d", "8955a292e8f084674fe174d3f49879d0"):
        "v2 'ciasny' (2026-10-15) - daje config00 jak BUILD14, ale kopie Skill01-08 nieskrocone",
    ("68c58d144c81b9edf27eb77164d2ca5d", "042cfa4abe66cfc38fe9de090dc88d2d"):
        "b13 (roboczy, nie wydany)",
    ("68c58d144c81b9edf27eb77164d2ca5d", "30f4ad0a7c8b12b7a686dcc01ee3a509"):
        "v3 (2026-10-15) - STARY: pule Skill01-08 (DLC) 17 396 B, rozdzialy 2-8 padaja na Loading",
    ("98d945607e047f4d32cf3b63f7f605d1", "fa8b0e48d2d7e4ca03757a5f731b763f"):
        "v4 (2026-10-15) - AKTUALNY",
}
CURRENT_PACKAGE = ("v4", "pakiet_EN_2026-10-15_v4.zip")
PACKAGE_FILES = ("00_dialogue.jsonl", "01_battle_quotes.jsonl", "02_items.jsonl", "03_skills.jsonl",
                 "04_config_text.jsonl", "05_mission_text.jsonl", "06_scenes.jsonl",
                 "07_names_characters.jsonl", "08_names_units_weapons.jsonl", "tokeny.tsv")

# writer features and the source text that proves they are present
TOOL_FEATURES = (
    ("item_skill_write.py", "SKILL00_LIMIT", "budzet rozmiaru Skill00 (Loading)"),
    ("item_skill_write.py", "POOL_POINTER", "wskaznik puli +36"),
    ("item_skill_write.py", "base_pointer_faults", "wskaznik bazowy +32"),
    ("item_skill_write.py", "parameter_pointer_faults", "wskaznik parametrow +52 (sejw z 2. rozdzialu)"),
    ("table_write.py", "POOL_SIZE_LIMITS", "budzet pul DLC Skill01-08 (Loading rozdzialow 2-8, test Y)"),
)
MD5_LIMIT = 8 * 1024 * 1024  # bigger files in the DLC folder are listed with their size only


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_sizes(root: Path) -> Dict[str, int]:
    """name -> original size from tools/drive_manifest.tsv (sizes only, no game content)."""
    out: Dict[str, int] = {}
    path = root / "tools" / "drive_manifest.tsv"
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 3 and parts[-1].strip().isdigit():
            out[parts[0].strip()] = int(parts[-1])
    return out


class Report:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.verdict: List[str] = []

    def h(self, title: str) -> None:
        self.lines += ["", "=" * 78, title, "=" * 78]

    def p(self, text: str = "") -> None:
        self.lines.append(text)

    def flag(self, text: str) -> None:
        self.verdict.append(text)

    def text(self) -> str:
        body = self.lines + ["", "=" * 78, "WNIOSKI (automatyczne - sprawdz z opisem wyzej)", "=" * 78]
        body += [f"- {v}" for v in self.verdict] or ["- (brak automatycznych wnioskow)"]
        return "\r\n".join(body) + "\r\n"


def section_tools(rep: Report, root: Path) -> Dict[str, bool]:
    rep.h("1. NARZEDZIA obok tego pliku (czy to swiezy ZIP galezi?)")
    rep.p(f"folder: {root}")
    found: Dict[str, bool] = {}
    for name in ("item_skill_write.py", "build_translation_patch.py", "cpk_write.py", "iso_insert.py"):
        path = root / "tools" / name
        if path.exists():
            rep.p(f"  tools\\{name:28s} {path.stat().st_size:>8} B  md5 {md5_of(path)}")
        else:
            rep.p(f"  tools\\{name:28s} BRAK")
    for file_name, marker, label in TOOL_FEATURES:
        path = root / "tools" / file_name
        ok = path.exists() and marker in path.read_text(encoding="utf-8", errors="replace")
        found[marker] = ok
        rep.p(f"  {'TAK' if ok else 'NIE'}  {label}")
    for bat in ("HOKUS_POKUS.bat", "WGRAJ_DO_ISO.bat", "BISEKCJA.bat"):
        path = root / bat
        rep.p(f"  {bat:20s} {'md5 ' + md5_of(path) if path.exists() else 'BRAK'}")
    if not found.get("parameter_pointer_faults"):
        rep.flag("NARZEDZIA SA STARE (brak poprawki +52) - sciagnij swiezy ZIP galezi i zbuduj jeszcze raz.")
    return found


def package_version(folder: Path) -> Tuple[str, Dict[str, str]]:
    sums: Dict[str, str] = {}
    for name in PACKAGE_FILES:
        path = folder / name
        if path.exists():
            sums[name] = md5_of(path)
    key = (sums.get("03_skills.jsonl", ""), sums.get("04_config_text.jsonl", ""))
    return PACKAGE_VERSIONS.get(key, "NIEZNANA (inne md5 03/04 niz w wydanych pakietach)"), sums


def section_package(rep: Report, root: Path) -> Optional[str]:
    rep.h("2. PAKIET w pakiet_EN\\ (co HOKUS_POKUS wzial jako tlumaczenie)")
    folder = root / "pakiet_EN"
    if not folder.is_dir():
        rep.p("  BRAK folderu pakiet_EN\\ - HOKUS_POKUS otwieral okno wyboru pakietu (nie wiemy ktorego).")
        rep.flag("pakiet_EN\\ nie istnieje - pakiet byl wskazywany recznie; sprawdz build_report.json (pole package).")
        return None
    if not (folder / "00_dialogue.jsonl").exists():
        nested = [p for p in folder.iterdir() if p.is_dir() and (p / "00_dialogue.jsonl").exists()]
        if nested:
            rep.p(f"  00_dialogue.jsonl lezy w PODFOLDERZE: {nested[0].name}\\ - HOKUS_POKUS tego nie widzi "
                  "(otwiera okno wyboru pakietu).")
            rep.flag(f"Pakiet rozpakowany o jeden folder za gleboko (pakiet_EN\\{nested[0].name}\\) - "
                     "przenies pliki poziom wyzej.")
            folder = nested[0]
        else:
            rep.p("  folder istnieje, ale nie ma w nim 00_dialogue.jsonl")
            rep.flag("pakiet_EN\\ jest pusty/niekompletny.")
            return None
    version, sums = package_version(folder)
    for name in PACKAGE_FILES:
        rep.p(f"  {name:28s} {sums.get(name, 'BRAK')}")
    extra = sorted(p.name for p in folder.iterdir() if p.is_file() and p.name not in PACKAGE_FILES)
    if extra:
        rep.p(f"  inne pliki: {', '.join(extra[:12])}{' ...' if len(extra) > 12 else ''}")
    rep.p(f"  WERSJA PAKIETU: {version}")
    if not version.startswith(CURRENT_PACKAGE[0]):
        rep.flag(f"Pakiet w pakiet_EN\\ to {version.split(' - ')[0]} - powinien byc "
                 f"{CURRENT_PACKAGE[0]} ({CURRENT_PACKAGE[1]}).")
    return version


def summarize_report(rep: Report, path: Path) -> Optional[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - the report is diagnostic
        rep.p(f"  build_report.json: nie da sie odczytac ({exc})")
        return None
    rep.p(f"  build_report.json: pakiet = {data.get('package')}")
    rep.p(f"    wiersze {data.get('rows')} / z angielskim {data.get('filled')} / identycznosciowe "
          f"{data.get('identity_rows')}; only={data.get('only')} skip={data.get('skip')}")
    rep.p(f"    iso = {data.get('iso')}")
    rep.p(f"    dlc = {data.get('dlc')}")
    containers = data.get("containers") or []
    changed = [c.get("container") for c in containers if c.get("changed")]
    rep.p(f"    kontenery: {len(containers)}, zmienione: {len(changed)}, zapisane pliki: "
          f"{len(data.get('written') or [])}, iso_members: {data.get('iso_members')}")
    if data.get("tools"):
        rep.p(f"    narzedzia wg raportu: {data.get('tools')}")
    problems = data.get("problems") or []
    fatal = [p for p in problems if ("NOT written" in p or "build broke" in p)]
    absent = [p for p in problems if "not found in the ISO or the DLC folder" in p]
    rep.p(f"    problemy razem: {len(problems)}; NOT written / build broke: {len(fatal)}; "
          f"kontenerow nieznalezionych w ISO/DLC: {len(absent)}")
    for line in fatal[:25]:
        rep.p(f"      ! {line[:200]}")
    for line in absent[:5]:
        rep.p(f"      ? {line[:120]}")
    if len(absent) > 5:
        rep.p(f"      ? ... i {len(absent) - 5} dalszych nieznalezionych")
    for line in fatal:
        if "NOT written" in line:
            rep.flag(f"Builder ODMOWIL zapisu: {line[:120]} - ten kontener zostal oryginalny.")
        else:
            rep.flag(f"Budowa kontenera padla: {line[:120]}")
    if absent:
        rep.flag(f"{len(absent)} kontenerow z pakietu nie bylo w ISO/DLC przy budowie - wskazano zly folder "
                 "DLC albo niepelny zestaw.")
    return data


def classify_config(name: str, digest: str) -> str:
    label = KNOWN_CONFIG.get(digest)
    if label:
        return label
    return "NIEZNANY build (nie jest to zaden z wydanych plikow)"


def section_patch_output(rep: Report, root: Path, originals: Dict[str, int]) -> Dict[str, str]:
    rep.h("3. WYNIK BUDOWY srw-oe-patch\\ (co zrobil HOKUS_POKUS)")
    out = root / "srw-oe-patch"
    built: Dict[str, str] = {}
    if not out.is_dir():
        rep.p("  BRAK folderu srw-oe-patch\\ - HOKUS_POKUS nie byl uruchamiany w tym folderze "
              "(albo wynik skasowany).")
        rep.flag("Brak srw-oe-patch\\ obok tego pliku - nie wiadomo, skad pochodza wgrane pliki.")
        return built
    report = out / "build_report.json"
    if report.exists():
        stamp = _dt.datetime.fromtimestamp(report.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        rep.p(f"  build_report.json z {stamp}")
        summarize_report(rep, report)
    else:
        rep.p("  brak build_report.json")
    iso = out / "patched.iso"
    if iso.exists():
        rep.p(f"  patched.iso {iso.stat().st_size} B (oryginal 679 243 152 B)")
        for name, digest, size in iso_members(iso):
            built[f"iso:{name}"] = digest
            rep.p(f"    w ISO {name:14s} {size:>8} B  md5 {digest}  -> {describe_usrdir(name, digest, size)}")
    else:
        rep.p("  brak patched.iso (budowa bez ISO albo ISO odrzucone)")
    dlc = out / "DLC"
    if dlc.is_dir():
        files = sorted(p for p in dlc.rglob("*") if p.is_file())
        rep.p(f"  DLC\\: {len(files)} plikow")
        for path in files:
            digest = md5_of(path)
            built[path.name] = digest
            size = path.stat().st_size
            note = describe_usrdir(path.name, digest, size) if path.name in USRDIR_NAMES else \
                size_note(path.name, size, originals)
            if digest in KNOWN_DLC_CONFIG:
                note = f"{note} {KNOWN_DLC_CONFIG[digest]}".strip()
            rep.p(f"    {path.name:18s} {size:>8} B  md5 {digest}  {note}")
    else:
        rep.p("  brak folderu DLC\\ w wyniku")
    return built


def size_note(name: str, size: int, originals: Dict[str, int]) -> str:
    orig = originals.get(name)
    if orig is None:
        return ""
    if size == orig:
        return "(rozmiar jak oryginal)"
    return f"(oryginal {orig} B, {size - orig:+d})"


def describe_usrdir(name: str, digest: str, size: int) -> str:
    if digest == KNOWN_ORIGINALS.get(name):
        return "ORYGINAL"
    if name in EXPECTED_BUILD14:
        return classify_config(name, digest)
    canon = CANONICAL_USRDIR.get(name)
    if canon and digest == canon[0]:
        return "= build z pakietu v3 i narzedzi 2026-10-15 (identyczny z moim)"
    if canon and size == canon[1]:
        return f"zmieniony, ten sam rozmiar co moj build ({size} B), inne md5"
    return f"zmieniony (nie oryginal; moj build ma {canon[1]} B)" if canon else "zmieniony"


def iso_members(iso: Path) -> List[Tuple[str, str, int]]:
    import iso_pack
    out = []
    for name in USRDIR_NAMES:
        try:
            data = iso_pack.read_member(iso, f"psp_game/usrdir/{name}")
        except Exception as exc:  # noqa: BLE001
            out.append((name, f"blad odczytu: {exc}", 0))
            continue
        out.append((name, hashlib.md5(data).hexdigest(), len(data)))
    return out


def section_dlc_folder(rep: Report, dlc: Path, built: Dict[str, str], originals: Dict[str, int]) -> None:
    rep.h("4. FOLDER DLC EMULATORA (z tego PPSSPP czyta DLC i config00/configst)")
    rep.p(f"folder: {dlc}")
    if not dlc.is_dir():
        rep.p("  nie istnieje")
        rep.flag("Wskazany folder DLC nie istnieje.")
        return
    files = sorted((p for p in dlc.iterdir() if p.is_file()), key=lambda p: p.name.lower())
    rep.p(f"  plikow: {len(files)}")
    same = diff = missing = orig_size = 0
    for path in files:
        size = path.stat().st_size
        digest = md5_of(path) if size <= MD5_LIMIT else None
        if path.name in USRDIR_NAMES and digest:
            note = describe_usrdir(path.name, digest, size)
            rep.p(f"  {path.name:18s} {size:>9} B  md5 {digest}  -> {note}")
            if path.name in ACCEPTED_CONFIG:
                accepted = ACCEPTED_CONFIG[path.name].get(digest)
                if accepted:
                    rep.flag(f"{path.name} w folderze DLC = {accepted} (dobrze).")
                else:
                    rep.flag(f"{path.name} w folderze DLC to NIE BUILD14/BUILD17: {note}.")
            continue
        notes = []
        if digest in KNOWN_DLC_CONFIG:
            notes.append(KNOWN_DLC_CONFIG[digest])
        if digest and path.name in built:
            if built[path.name] == digest:
                same += 1
                notes.append("= build")
            else:
                diff += 1
                notes.append("ROZNY od buildu")
        elif path.name in built:
            notes.append("(za duzy na md5)")
        else:
            missing += 1
        if path.name in originals:
            if size == originals[path.name]:
                orig_size += 1
                notes.append("rozmiar oryginalu")
            else:
                notes.append(f"oryginal {originals[path.name]} B")
        rep.p(f"  {path.name:18s} {size:>9} B  {('md5 ' + digest) if digest else '(bez md5)':36s} "
              f"{' '.join(notes)}")
    rep.p(f"  podsumowanie: {same} identycznych z buildem, {diff} roznych od buildu, "
          f"{orig_size} o rozmiarze oryginalu, {missing} bez odpowiednika w buildzie")
    if diff:
        rep.flag(f"{diff} plikow w folderze DLC rozni sie od wyniku budowy - wgrane cos innego niz zbudowane.")
    for name in EXPECTED_BUILD14:
        if not (dlc / name).exists():
            rep.flag(f"W folderze DLC nie ma {name} - gra wezmie go z ISO.")


def section_iso(rep: Report, iso: Path) -> None:
    rep.h("5. ISO URUCHAMIANE W PPSSPP")
    rep.p(f"plik: {iso}")
    if not iso.exists():
        rep.p("  nie istnieje")
        return
    size = iso.stat().st_size
    rep.p(f"  rozmiar {size} B ({'jak oryginal 1.08' if size == 679243152 else 'inny niz oryginal 679 243 152 B'})")
    for name, digest, msize in iso_members(iso):
        note = describe_usrdir(name, digest, msize)
        rep.p(f"  {name:14s} {msize:>8} B  md5 {digest}  -> {note}")
        if name in ACCEPTED_CONFIG and digest not in ACCEPTED_CONFIG[name] \
                and digest != KNOWN_ORIGINALS[name]:
            rep.flag(f"{name} w ISO to {note}.")
        if name not in EXPECTED_BUILD14 and digest != KNOWN_ORIGINALS.get(name):
            rep.flag(f"{name} w ISO jest zmieniony ({note}) - ten kontener nigdy nie byl testowany w grze osobno.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dlc", type=Path, required=True, help="folder DLC, z ktorego czyta PPSSPP")
    parser.add_argument("--iso", type=Path, default=None, help="ISO uruchamiane w PPSSPP (opcjonalnie)")
    parser.add_argument("--root", type=Path, default=HERE.parent, help="folder srw-oe-translation")
    parser.add_argument("--out", type=Path, default=None, help="plik raportu (domyslnie <root>/DIAGNOZA.txt)")
    parser.add_argument("--quiet", action="store_true", help="nie wypisuj raportu na ekran")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    out = args.out or (root / "DIAGNOZA.txt")
    rep = Report()
    rep.p(f"DIAGNOZA SRW OE - {_dt.datetime.now().strftime('%Y-%m-%d %H:%M')} - "
          f"Python {platform.python_version()} - {platform.platform()}")
    originals = manifest_sizes(root)
    section_tools(rep, root)
    section_package(rep, root)
    built = section_patch_output(rep, root, originals)
    section_dlc_folder(rep, args.dlc, built, originals)
    if args.iso is not None:
        section_iso(rep, args.iso)
    else:
        rep.h("5. ISO URUCHAMIANE W PPSSPP")
        rep.p("  (pominiete - nie wskazano ISO)")

    out.write_text(rep.text(), encoding="utf-8-sig")
    if not args.quiet:
        print(rep.text())
        print(f"Raport zapisany: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
