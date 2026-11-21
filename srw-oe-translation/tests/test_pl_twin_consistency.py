"""Bliźniacze wiersze jednego podpisu muszą mówić jednym głosem.

Właściciel wygenerował pliki gry z patcha PL v4.12 i dostał błąd na końcu
instalacji (`[X] Build FAILED`): `table_write` odmówił wiersze walczące o ten
sam record/slot, a `table_write._apply_sub` promuje każdą odmowę do problemów
kontenera, więc `build_translation_patch` nie zapisał `config01.EDAT`,
`config05.EDAT`, `imenu01.EDAT`, `imenu05.EDAT` i zwrócił exit 1.

Przyczyna nie była w writerze: plan `ui-robodict-remaining-captions-2026-11-11`
dołożył brakujące wiersze kopii `imenu*` z własnym brzmieniem CAPTIONS, gdy
bliźniak `config*` już miał stare — dwa różne polskie teksty na jeden fizyczny
napis. Ten test pilnuje obu nóg kontraktu, bez kontenerów gry:

1. wiersze `leftover:{container}/{member}:{offset}` — ta sama para
   (member, offset) w dwóch kontenerach (config↔imenu, identyczne bajty,
   `mirror_identical_members` duplikuje wiersze do obu) muszą mieć to samo `pl`;
2. wiersze z `copy_of` (kopie `robonote:*` idące do wszystkich rozdziałów)
   muszą mieć `pl` zgodne ze swoim źródłem.

Dodatkowo plan korekty, który to naprawił:
`config/pl/robodict-twin-unify-2026-11-20.json`.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

LEFTOVER = re.compile(r"^leftover:([^/]+)/(.+):(\d+)$")


def overlay() -> list[dict]:
    rows = []
    for line in (ROOT / "pakiet_PL" / "polish.jsonl").read_text(encoding="utf-8").splitlines():
        if line:
            rows.append(json.loads(line))
    return rows


def test_twin_containers_agree_on_one_polish_text():
    """Identyczny bajtowo member w dwóch kontenerach = jeden polski tekst.

    `mirror_identical_members` duplikuje wiersze config↔imenu, bo klucz
    deduplikacji to `(id, jp)`, a identyfikatory `leftover:` zawierają nazwę
    kontenera — nigdy nie są równe. Gdy obie strony mają tekst, writer widzi
    dwa wiersze na jeden record/slot; różne brzmienie = odmowa = kontener
    niezapisany (v4.12). Różne brzmienie jest dozwolone tylko wtedy, gdy
    wiersz nie ma bliźniaka z tekstem — wtedy mirror dopisze je sam.
    """
    twins: dict[tuple[str, int], dict[str, str]] = defaultdict(dict)
    for row in overlay():
        match = LEFTOVER.match(row.get("id") or "")
        if match and row.get("pl"):
            container, member, offset = match.groups()
            twins[(member, int(offset))][container] = row["pl"]
    diverging = {key: by for key, by in twins.items()
                 if len(by) > 1 and len(set(by.values())) > 1}
    shown = "\n  ".join(f"{member}:{offset} -> {by}"
                        for (member, offset), by in sorted(diverging.items()))
    assert not diverging, (
        f"{len(diverging)} podpisów ma dwa różne polskie brzmienia w bliźniakach "
        f"config↔imenu (build PL odmówiłby kontener):\n  {shown}")


def test_copy_of_rows_match_their_source():
    """Kopie `robonote:*` (idą do wszystkich rozdziałów) powtarzają źródło.

    `copy_of` wskazuje wiersz, z którego kopia powstała; oba leżą w overlayu
    PL. Rozjazd = rozdziały pokazują różne brzmienia tego samego napisu, a
    przy bliźniaku config↔imenu także odmowę writeera.
    """
    pl = {row["id"]: row["pl"] for row in overlay() if row.get("pl")}
    copies: dict[str, str] = {}
    for path in sorted((ROOT / "pakiet_EN").glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            row = json.loads(line)
            if row.get("copy_of"):
                copies[row["id"]] = row["copy_of"]
    checked = [(ident, source) for ident, source in copies.items()
               if ident in pl and source in pl]
    diverging = [(ident, source) for ident, source in checked
                 if pl[ident] != pl[source]]
    shown = "\n  ".join(f"{ident} -> {pl[ident]!r} != {source} -> {pl[source]!r}"
                        for ident, source in diverging[:8])
    assert not diverging, (
        f"{len(diverging)} kopii copy_of różni się od źródła "
        f"(z {len(checked)} sprawdzanych par):\n  {shown}")


def test_unify_plan_is_applied_and_still_valid():
    """Plan naprawczy jest w snapshotcie i nie rozjechał się z pakietem."""
    plan_path = ROOT / "config" / "pl" / "robodict-twin-unify-2026-11-20.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["schema"] == 1 and len(plan["changes"]) == 15
    stored = {row["id"]: row["pl"] for row in overlay()}
    for change in plan["changes"]:
        assert stored.get(change["id"]) == change["after"], change["id"]
    snapshot = json.loads((ROOT / "pakiet_PL" / "snapshot.json").read_text(encoding="utf-8"))
    ledger = snapshot["owner_ui_corrections"]
    entry = next(e for e in reversed(ledger) if e["plan"] == plan_path.name)
    assert entry["previous_data_sha256"] == "a1ed783bb1a94e2f9951b1d02bb4f509fdd59910a0c6157dd9f75b31d000f49e"
    assert entry["entries"] == 15
