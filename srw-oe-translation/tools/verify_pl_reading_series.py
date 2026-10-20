#!/usr/bin/env python3
"""Verify PL4 reading-edition hashes, source bindings, and rendered PL spans."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from build_pl_reading_series import (EMPTY_STRUCTURAL_ID, JP_RE, SOURCE_FILES,
                                     PolishStorySource)
from build_reading_script import escape, render_entry
from mech_catalog_sources import need
from reading_script_source import HEADINGS, PROSE


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_text(source: PolishStorySource, episode: int) -> tuple[str, set[str], set[str]]:
    pieces = []
    prose_ids = set()
    row_ids = set()

    def put(value: str) -> None:
        pieces.append(value + "\n\n")

    put(f"# Super Robot Wars OE — Epizod {episode:02d}")
    put("*Polski scenariusz do czytania · tekst z zaakceptowanego pakietu PL4*")
    put("> **Informacja:** Dialogi i narrację pokazano w kolejności wpisów źródłowych. Wymiany mogą zależeć "
        "od przebiegu misji; kolejność w dokumencie nie oznacza, że wszystkie kwestie występują w jednej "
        "rozgrywce. Nie dopisano warunków HP/tur ani dalszych zdarzeń. Alternatywne wersje źródłowe "
        "oznaczono osobno i pokazano w całości.")
    put("---")
    for scene in source.scenes:
        put("## " + escape(source.mission_title(scene)))
        if scene.get("variant_of"):
            put(f"*Wersja alternatywna ({escape(scene.get('variant') or 'źródłowa')}); "
                "to nie dalszy ciąg tej misji. Pełny tekst zachowano.*")
        elif scene.get("variant"):
            put(f"*Wariant źródłowy {escape(scene['variant'])}; scena zachowana osobno.*")
        elif scene.get("copy_of"):
            put("*Kopia źródłowa; zachowano osobno wszystkie wpisy.*")
        for row in source.rows[scene["id"]]:
            kind = row.get("kind")
            if kind not in PROSE | HEADINGS:
                continue
            if not (row.get("pl") or "").strip():
                need(row["id"] == EMPTY_STRUCTURAL_ID and not (row.get("jp") or "").strip()
                     and not (row.get("en") or "").strip(),
                     f"Missing PL source row while verifying: {row['id']}")
                continue
            entry = source.make_entry(row)
            text = render_entry(entry, "story", 3)
            if kind in PROSE:
                text = re.sub(r"(?m)(^|\n\n)(\([^\n]*\))(?=\n\n|$)",
                              lambda m: m.group(1) + "*" + m.group(2) + "*", text)
                prose_ids.add(row["id"])
            row_ids.add(row["id"])
            put(text)
    put("---")
    put("## Uwagi redakcyjne")
    put("- Tekst pochodzi wyłącznie z polskich pól pakietu PL4; angielskie wiersze służą tylko "
        "do sprawdzania identyfikatorów i struktury. Nie ma uzupełniania braków angielskim.")
    put("- Zachowano wszystkie polskie wpisy narracji/dialogu z tego epizodu, także tekst scen "
        "alternatywnych. Nie usuwano powtórzeń między scenami.")
    put("- Pominięto techniczne pola celu/pomocy i pusty wypełniacz strukturalny; nie są narracją do czytania.")
    put(f"- Pokrycie: **{len(prose_ids)}** wpisów dialogu i narracji w **{len(source.scenes)}** scenach. "
        "Dokument nie ustala dokładnych wyzwalaczy ani kolejności kwestii warunkowych w grze.")
    put("- Znaczniki imienia/nazwiska podstawiono wyłącznie w tym dokumencie, używając domyślnej "
        "polskiej nazwy z tabel postaci; dane gry pozostają dynamiczne.")
    return "".join(pieces), prose_ids, row_ids


def verify_series(english_package: Path, polish_package: Path, output: Path) -> dict:
    output = Path(output)
    manifest_path = output / "manifest.json"
    need(manifest_path.is_file(), "Missing reading-series manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    episodes = [row["episode"] for row in manifest.get("episodes", [])]
    need(episodes == list(range(22)), "Expected exactly the currently covered episode IDs 00–21")
    results = []
    for episode in episodes:
        md = output / f"srwoe_episode_{episode:02d}_PL.md"
        audit_path = output / f"episode_{episode:02d}_audit.json"
        need(md.is_file() and audit_path.is_file(), f"Missing output/audit for episode {episode:02d}")
        text_bytes = md.read_bytes()
        text = text_bytes.decode("utf-8")
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        need(audit.get("episode") == episode, f"Audit episode mismatch: {episode:02d}")
        need(digest(text_bytes) == audit.get("output_sha256"), f"Output hash mismatch: {md.name}")
        need(len(text_bytes) == audit.get("output_bytes"), f"Output size mismatch: {md.name}")
        expected_source_hashes = {name: digest((english_package / name).read_bytes())
                                  for name in SOURCE_FILES}
        expected_pl_hashes = {name: digest((polish_package / name).read_bytes())
                              for name in SOURCE_FILES}
        need(audit.get("source_sha256") == expected_source_hashes,
             f"English source hash mismatch: {episode:02d}")
        need(audit.get("materialized_pl_sha256") == expected_pl_hashes,
             f"PL source hash mismatch: {episode:02d}")
        source = PolishStorySource(english_package, polish_package, episode)
        expected, prose_ids, row_ids = expected_text(source, episode)
        need(text == expected, f"Rendered content differs from bound PL source: {episode:02d}")
        need(set(audit.get("prose_ids", [])) == prose_ids,
             f"Audit prose IDs differ from PL source: {episode:02d}")
        need(audit.get("prose_total") == len(prose_ids), f"Audit prose count mismatch: {episode:02d}")
        need(audit.get("scene_count") == len(source.scenes), f"Audit scene count mismatch: {episode:02d}")
        need(not JP_RE.search(text), f"Residual Japanese in {md.name}")
        audited_rows = {span["row"] for span in audit.get("rendered_blocks", []) if "row" in span}
        need(audited_rows == row_ids, f"Audit rendered-row coverage mismatch: {episode:02d}")
        for span in audit.get("rendered_blocks", []):
            if "row" in span:
                need(span["binding"] == source.bindings[span["row"]],
                     f"Wrong immutable source binding in {episode:02d}/{span['row']}")
                need(text[span["start"]:span["end"]].endswith("\n\n"),
                     f"Invalid text span in {episode:02d}/{span['row']}")
        results.append({"episode": episode, "prose": len(prose_ids),
                        "scenes": len(source.scenes), "bytes": len(text_bytes),
                        "sha256": digest(text_bytes)})
    need(manifest.get("episodes") == [{"episode": r["episode"], "prose": r["prose"],
                                         "scenes": r["scenes"], "bytes": r["bytes"],
                                         "sha256": r["sha256"]} for r in results],
         "Series manifest differs from verified outputs")
    return {"episodes": len(results), "prose_rows": sum(r["prose"] for r in results),
            "scenes": sum(r["scenes"] for r in results),
            "output_bytes": sum(r["bytes"] for r in results), "verified": results}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english", type=Path, required=True)
    parser.add_argument("--polish", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = verify_series(args.english, args.polish, args.out)
    print(f"Verified {result['episodes']} episodes, {result['prose_rows']} PL prose rows, "
          f"{result['scenes']} scenes; {result['output_bytes']} Markdown bytes; no residual Japanese.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
