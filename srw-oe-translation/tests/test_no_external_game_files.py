"""Żaden katalog, żadna czytanka i żadna łatka nie może zależeć od pliku spoza repozytorium.

Właściciel nie ma obowiązku podstawiać kontenerów gry ani odszyfrowanego programu 1.08.
Wszystko, co jest z nich potrzebne, zostało raz wyciągnięte i leży w repozytorium:

* `docs/game-data/` — tabele silnika, tabela Duchów i teksty z programu gry;
* `pakiet_katalog_EN/` — zamrożony pakiet angielski, na którym katalogi zostały zamknięte.

Testy pilnują trzech rzeczy naraz: że wyciąg jest kompletny i nienaruszony, że budowa
katalogów faktycznie przechodzi bez kontenerów i ELF-a, oraz że żadna ścieżka budowania
nie wymaga w swoim CLI argumentu wskazującego pliki gry.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import game_data_extract as GDE  # noqa: E402
import mech_catalog as M  # noqa: E402
import mech_catalog_sources as S  # noqa: E402
import pilot_catalog as PC  # noqa: E402

DOCS = ROOT / "docs"
FROZEN = ROOT / "pakiet_katalog_EN"
EXTRACT = DOCS / "game-data"

# Kontenery gry i program gry — nic z tego nie może być potrzebne do budowy.
GAME_FILE_SUFFIXES = (".cpk", ".edat", ".elf", ".pbp", ".iso", ".cso", ".bin")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class NoExternalGameFilesTests(unittest.TestCase):
    """Cały warsztat buduje się z repozytorium — CI OE używa czystego `unittest`."""


    def test_wyciag_jest_w_repozytorium_i_kompletny(self):
        assert GDE.available(), "brak wyciągu docs/game-data/ — katalogi przestałyby się budować"
        manifest = GDE.verify()
        assert manifest["executable"]["sha256"] == GDE.ORIGINAL_SHA256_EXPECTED


    def test_zamrozony_pakiet_katalogowy_zgadza_sie_z_manifestem(self):
        recorded = json.loads((DOCS / "mech-catalog/source-inventory.json").read_bytes())
        expected = recorded["summary"]["package_sha256"]
        for name, want in sorted(expected.items()):
            path = FROZEN / name
            assert path.is_file(), f"brakuje {path} — katalogu nie da się odtworzyć"
            assert sha(path.read_bytes()) == want, f"{name} rozjechał się z zamrożonym manifestem"


    def test_katalog_mechow_buduje_sie_bez_plikow_gry(self):
        source = S.collect(None, FROZEN)
        inventory = json.loads((DOCS / "mech-catalog/source-inventory.json").read_bytes())
        assert source["inputs"] == inventory["inputs"]
        assert source["summary"]["package_sha256"] == inventory["summary"]["package_sha256"]
        model = M.build_model(
            source, FROZEN, None,
            json.loads((DOCS / "mech-catalog/engine-map.json").read_bytes()),
            json.loads((DOCS / "mech-catalog/description-errata.json").read_bytes()),
        )
        expected = json.loads((DOCS / "mech-catalog/presentation-v3.json").read_bytes())["output_sha256"]
        assert sha(M.render(model)[0].encode()) == expected, "angielski katalog v3 nie odtworzył się bajt w bajt"


    def test_tabela_duchow_i_teksty_programu_pochodza_z_repozytorium(self):
        spirit = PC.read_spirit_binary(None)
        assert len(spirit) > 0
        engine_map = json.loads((DOCS / "pilot-catalog/engine-map.json").read_bytes())
        strings = GDE.load_executable_strings(engine_map)
        pointers = GDE.engine_map_pointers(
            json.loads((DOCS / "mech-catalog/engine-map.json").read_bytes()), engine_map
        )
        assert len(strings) == len(pointers)
        for entry in engine_map["skill_records"]:
            if entry.get("pointer"):
                text, offset = strings.string_at(entry["pointer"])
                assert offset == entry["file_offset"]
                assert sha(text.encode("utf-8")) == entry["english_sha256"]


    def test_uszkodzony_wyciag_jest_odrzucany(self):
        """Wyciąg nie jest zaufany na słowo: podmieniony tekst musi wywalić budowę."""
        with tempfile.TemporaryDirectory() as raw:
            tmp_path = Path(raw)
            for name in (GDE.TABLES_FILE, GDE.SPIRIT_FILE, GDE.STRINGS_FILE, GDE.MANIFEST_FILE):
                (tmp_path / name).write_bytes((EXTRACT / name).read_bytes())
            payload = json.loads((tmp_path / GDE.STRINGS_FILE).read_bytes())
            payload["strings"][0]["text"] = payload["strings"][0]["text"] + " podmienione"
            (tmp_path / GDE.STRINGS_FILE).write_text(json.dumps(payload, ensure_ascii=False))
            with self.assertRaises(ValueError):
                GDE.load_executable_strings(directory=tmp_path)


    def test_zaden_builder_nie_wymaga_plikow_gry(self):
        """CLI buildera czytanek i katalogu pilotów musi dać się wywołać bez --configs/--elf."""
        import argparse
        import build_polish_reading_editions as B

        for module, required_absent in ((B, ("--configs", "--elf")), (PC, ("--containers", "--elf"))):
            parser_actions = []

            original = argparse.ArgumentParser.parse_args

            def capture(self, argv=None, _store=parser_actions):
                _store.extend(self._actions)
                raise SystemExit(0)

            argparse.ArgumentParser.parse_args = capture
            try:
                with self.assertRaises(SystemExit):
                    module.main([])
            finally:
                argparse.ArgumentParser.parse_args = original
            by_flag = {opt: a for a in parser_actions for opt in a.option_strings}
            for flag in required_absent:
                assert flag in by_flag, f"{module.__name__}: brak flagi {flag}"
                assert not by_flag[flag].required, f"{module.__name__}: {flag} nadal jest wymagane"


    def test_repozytorium_nie_sledzi_plikow_gry(self):
        """Pliki gry zostają poza repozytorium — do budowy mają być niepotrzebne."""
        import subprocess

        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.splitlines()
        offenders = [t for t in tracked if Path(t).suffix.lower() in GAME_FILE_SUFFIXES]
        assert not offenders, f"pliki gry trafiły do repozytorium: {offenders[:5]}"
