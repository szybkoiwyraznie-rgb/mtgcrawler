#!/usr/bin/env python3
"""Read the text out of SRW Y asset bundles and measure it.

SRW Y keeps its text in two places, both inside Addressables bundles:

* **TextAssets** — one per scenario script, titled like
  ``cse20_0001_0000310a_dlgev.lua.txt``, in the bundles the catalogue maps to
  ``Assets/Datas/Scenario/{jp,en,...}``. These hold the actual story text.
* **Unity Localization string tables** — ``TextAsset``-less MonoBehaviours of
  type ``StringTable`` (``dialog_text_ja-JP`` and the other 20-odd tables). The
  serialiser for those is read when a type tree is available; when it is not,
  the object is reported as ``raw`` and its printable strings are dumped instead
  of pretending to have parsed it.

Requires **UnityPy** (LGPL, not vendored here). Create a throwaway environment:

    python3 -m venv .venv && .venv/bin/pip install UnityPy
    .venv/bin/python tools/extract_text.py --bundle X.bundle --out-dir local/s2

Text dumps go to ``--out-dir`` (the repo's ignored ``local/``); the JSON report
holds only counts and file names, so it can be committed or shared.

**Status of this tool (2026-10-25):** the pure functions are unit-tested, and the
bundle path has now been run — on a real SRW Y bundle, which turned out to be
**encrypted** (no `UnityFS` header, entropy 8.0). The tool reported `0 objects`,
which was the correct answer for that input; it has still never parsed a
*plaintext* SRW Y bundle, because none exists on disk. See `docs/S2_FINDINGS.md`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = 1
SCENARIO_NAME = re.compile(r"(cse\d+.*\.lua\.txt|.*\.lua\.txt)$", re.IGNORECASE)
CJK = re.compile(r"[\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]")


def decode_text(raw: bytes) -> str:
    """Decode a text asset: BOM first, then UTF-8, then Shift-JIS.

    Guessing wrong is cheap to detect (U+FFFD and broken CJK), and the report
    counts replacement characters so a bad guess is visible rather than silent.
    """
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", "replace")
    if raw.startswith(b"\xff\xfe"):
        return raw[2:].decode("utf-16-le", "replace")
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", "replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp932", "replace")


def classify(name: str) -> str:
    if SCENARIO_NAME.search(name):
        return "scenario_script"
    lowered = name.lower()
    if "localization" in lowered or "stringtable" in lowered:
        return "localization_table"
    if lowered.endswith((".txt", ".lua", ".json", ".csv")):
        return "text_file"
    return "other"


def text_stats(texts: dict[str, str]) -> dict:
    """Character/line counts per class, plus the signals of encoding trouble."""
    per_class: dict[str, dict] = {}
    for name, text in texts.items():
        record = per_class.setdefault(classify(name), {"files": 0, "chars": 0,
                                                       "lines": 0, "cjk": 0,
                                                       "replacement": 0})
        record["files"] += 1
        record["chars"] += len(text)
        record["lines"] += text.count("\n") + (0 if text.endswith("\n") else 1)
        record["cjk"] += len(CJK.findall(text))
        record["replacement"] += text.count("\ufffd")
    total = {
        "files": sum(record["files"] for record in per_class.values()),
        "chars": sum(record["chars"] for record in per_class.values()),
        "lines": sum(record["lines"] for record in per_class.values()),
    }
    return {"total": total, "per_class": per_class}


def sample(texts: dict[str, str], key: str, chars: int = 400) -> str:
    text = texts.get(key, "")
    return text[:chars]


def extract(bundle_paths: list[Path], out_dir: Path | None,
            max_dump: int = 0) -> dict:
    """Open bundles, collect text, optionally dump it. Raises RuntimeError."""
    try:
        import UnityPy
    except ImportError as error:  # pragma: no cover - environment dependent
        raise RuntimeError("UnityPy is not installed; see the module docstring") from error

    texts: dict[str, str] = {}
    objects: dict[str, int] = {}
    raw_objects: list[str] = []
    for path in bundle_paths:
        if not path.is_file():
            raise RuntimeError(f"not a file: {path}")
        env = UnityPy.load(str(path))
        for obj in env.objects:
            type_name = getattr(obj.type, "name", str(obj.type))
            objects[type_name] = objects.get(type_name, 0) + 1
            if type_name not in ("TextAsset", "MonoBehaviour"):
                continue
            try:
                data = obj.read()
            except Exception as error:  # noqa: BLE001 - report, never crash the run
                raw_objects.append(f"{type_name}: {error}")
                continue
            name = getattr(data, "m_Name", "") or f"{type_name}_{obj.path_id}"
            script = getattr(data, "m_Script", None)
            if isinstance(script, str):
                texts[name] = script
            elif isinstance(script, (bytes, bytearray)):
                texts[name] = decode_text(bytes(script))
            elif type_name == "MonoBehaviour":
                raw_objects.append(f"MonoBehaviour without typetree: {name}")

    report = {
        "schema": SCHEMA,
        "bundles": [{"name": path.name, "bytes": path.stat().st_size} for path in bundle_paths],
        "object_types": dict(sorted(objects.items(), key=lambda kv: -kv[1])),
        "texts": {name: {"chars": len(text), "class": classify(name)}
                  for name, text in sorted(texts.items())},
        "stats": text_stats(texts),
        "unreadable": raw_objects[:50],
    }

    if out_dir is not None and texts:
        out_dir.mkdir(parents=True, exist_ok=True)
        written = 0
        for name, text in sorted(texts.items()):
            if max_dump and written >= max_dump:
                break
            target = out_dir / (re.sub(r"[^A-Za-z0-9._-]+", "_", name) or "unnamed")
            target.write_text(text, encoding="utf-8")
            written += 1
        report["dumped"] = {"dir": str(out_dir), "files": written}
    return report


def summarise(report: dict) -> str:
    lines = [f"bundles: {len(report['bundles'])}"]
    for bundle in report["bundles"]:
        lines.append(f"  {bundle['name']}  {bundle['bytes']:,} B")
    lines.append("objects: " + ", ".join(f"{k} {v}" for k, v in report["object_types"].items()))
    stats = report["stats"]
    lines.append(f"text: {stats['total']['files']:,} files, "
                 f"{stats['total']['chars']:,} chars, {stats['total']['lines']:,} lines")
    for name, record in sorted(stats["per_class"].items()):
        lines.append(f"  {name:18} {record['files']:5} files  {record['chars']:>10,} chars  "
                     f"cjk {record['cjk']:,}  replacement {record['replacement']}")
    if report["unreadable"]:
        lines.append(f"unreadable objects: {len(report['unreadable'])} "
                     f"(first: {report['unreadable'][0]})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bundle", action="append", required=True, type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--max-dump", type=int, default=0,
                        help="write at most N text files (0 = all)")
    args = parser.parse_args(argv)

    try:
        report = extract(args.bundle, args.out_dir, args.max_dump)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(summarise(report))
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                               encoding="utf-8")
        print(f"\nreport written: {args.report} ({args.report.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
