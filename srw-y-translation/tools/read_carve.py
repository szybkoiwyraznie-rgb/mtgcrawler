#!/usr/bin/env python3
"""Read the files carved out of the game's memory and measure the text.

`tools/mem_carve.py` takes plaintext `.bundle` and `.assets` files out of the
running game. This is the second half: open them with UnityPy, list what is
inside, pull out every text asset and measure it (characters, lines, kana).

It writes a report with **counts and names only**; the text itself goes to
`--out-dir` (keep it in the ignored `local/`), never into the report.

UnityPy is not installed here by default:

    python3 -m venv .venv && .venv/bin/pip install UnityPy
    .venv/bin/python tools/read_carve.py --carve local/carve --out-dir local/text

Usage:
    python3 tools/read_carve.py --carve carve/ --report carve_read.json
    python3 tools/read_carve.py --file a.bundle b.assets --out-dir local/text
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_text as E  # noqa: E402

SCHEMA = 1


def summarize(objects: dict[str, int]) -> dict:
    """Object-type counts -> a few useful aggregates."""
    texts = objects.get("TextAsset", 0)
    mono = objects.get("MonoBehaviour", 0)
    return {
        "object_types": dict(sorted(objects.items(), key=lambda kv: -kv[1])),
        "total_objects": sum(objects.values()),
        "text_assets": texts,
        "mono_behaviours": mono,
        "has_text": texts > 0 or mono > 0,
    }


def read_one(path: Path) -> dict:
    """Open one carved file with UnityPy and return its text and inventory."""
    import UnityPy  # imported here so the module loads without UnityPy installed

    env = UnityPy.load(str(path))
    objects: dict[str, int] = {}
    texts: dict[str, str] = {}
    for obj in env.objects:
        type_name = getattr(obj.type, "name", str(obj.type))
        objects[type_name] = objects.get(type_name, 0) + 1
        if type_name not in ("TextAsset", "MonoBehaviour"):
            continue
        try:
            data = obj.read()
        except Exception:  # noqa: BLE001 - a partial carve may not deserialise
            continue
        name = getattr(data, "m_Name", "") or f"{type_name}_{obj.path_id}"
        script = getattr(data, "m_Script", None)
        if isinstance(script, str):
            texts[name] = script
        elif isinstance(script, (bytes, bytearray)):
            texts[name] = E.decode_text(bytes(script))

    summary = summarize(objects)
    summary["file"] = path.name
    summary["bytes"] = path.stat().st_size
    summary["texts"] = {name: {"chars": len(text), "class": E.classify(name)}
                        for name, text in sorted(texts.items())}
    summary["stats"] = E.text_stats(texts)
    summary.pop("object_types_detail", None)
    return {"summary": summary, "texts": texts}


def run(files: list[Path], out_dir: Path | None, max_dump: int = 0) -> dict:
    results = []
    dumped = 0
    for path in files:
        try:
            single = read_one(path)
        except Exception as error:  # noqa: BLE001 - keep going, report the failure
            results.append({"file": path.name, "error": str(error)[:200],
                            "bytes": path.stat().st_size})
            continue
        summary = single["summary"]
        results.append(summary)
        if out_dir is not None and single["texts"]:
            target = out_dir / path.stem
            target.mkdir(parents=True, exist_ok=True)
            for name, text in sorted(single["texts"].items()):
                if max_dump and dumped >= max_dump:
                    break
                safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name)
                (target / (safe or "unnamed")).write_text(text, encoding="utf-8")
                dumped += 1

    totals = {"files": len(results), "with_text": 0, "chars": 0, "lines": 0,
              "kana": 0, "errors": 0}
    classes: dict[str, dict] = {}
    for item in results:
        if "error" in item:
            totals["errors"] += 1
            continue
        if item.get("has_text"):
            totals["with_text"] += 1
        stats = item.get("stats", {}).get("total", {})
        totals["chars"] += stats.get("chars", 0)
        totals["lines"] += stats.get("lines", 0)
        for name, record in item.get("stats", {}).get("per_class", {}).items():
            bucket = classes.setdefault(name, {"files": 0, "chars": 0, "cjk": 0,
                                               "replacement": 0})
            bucket["files"] += record.get("files", 0)
            bucket["chars"] += record.get("chars", 0)
            bucket["cjk"] += record.get("cjk", 0)
            bucket["replacement"] += record.get("replacement", 0)
            totals["kana"] += record.get("cjk", 0)
    return {"schema": SCHEMA, "totals": totals, "per_class": classes,
            "files": results}


def discover(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob("*")
                  if p.suffix.lower() in (".bundle", ".assets", ".ab", ".unity3d"))


def summarise(report: dict) -> str:
    totals = report["totals"]
    lines = [f"files: {totals['files']} ({totals['with_text']} contain text, "
             f"{totals['errors']} could not be opened)"]
    lines.append(f"text: {totals['chars']:,} chars, {totals['lines']:,} lines, "
                 f"{totals['kana']:,} CJK/kana characters")
    for name, record in sorted(report["per_class"].items(),
                               key=lambda kv: -kv[1]["chars"]):
        lines.append(f"  {name:18} {record['files']:5} files  {record['chars']:>10,} chars")
    interesting = [item for item in report["files"]
                   if item.get("text_assets") or item.get("mono_behaviours")]
    for item in interesting[:10]:
        lines.append(f"  {item['file']}: {item.get('text_assets', 0)} text assets, "
                     f"{item.get('mono_behaviours', 0)} MonoBehaviours")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--carve", type=Path, help="directory produced by mem_carve")
    parser.add_argument("--file", type=Path, nargs="+", default=[])
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--max-dump", type=int, default=0)
    args = parser.parse_args(argv)

    files = list(args.file)
    if args.carve:
        if not args.carve.exists():
            print(f"error: not found: {args.carve}", file=sys.stderr)
            return 2
        files += discover(args.carve)
    if not files:
        print("error: nothing to read - pass --carve or --file", file=sys.stderr)
        return 2

    report = run(files, args.out_dir, args.max_dump)
    print(summarise(report))
    target = args.report or Path("carve_read.json")
    target.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(f"report: {target} ({target.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
