#!/usr/bin/env python3
"""Put Polish into a scenario bundle that gets **bigger** — the write mode that was never proven.

Two write modes exist for this game:

* **A, same size.** Rewrite the English bytes in place and pad with spaces, so the
  bundle keeps its exact length and header. Proven in game: the Polish opening
  narration shipped that way and the owner saw it. Its price is that Polish can never
  be longer than the English it replaces.
* **B, rebuild.** Give the object new bytes of a different length and let the object
  table, the LZ4 blocks and the container info be rebuilt. Proven offline
  (`tools/srw_y_rebuild.py --verify`), *never* proven in game: the first attempt died
  before the logo, and nobody knows whether the size or the new header killed it.

This tool makes the smallest possible in-game test of mode B: one already-translated
scene, the very first dialogue after the opening narration, so the owner needs no save
file — start a new game and the Polish is on screen within the first minute.

Text is located by the game's own string id in the literal's trailing comment (never by
position), the speaker line and the line breaks stay as they are, and every other object
in the bundle is verified byte for byte afterwards.  If anything besides the edited
script differs, the tool refuses to write the file.

    python3 tools/build_pl_scene_patch.py                    # build the test patch
    python3 tools/build_pl_scene_patch.py --check            # only report, write nothing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from pl_kit import write_kit  # noqa: E402
from s6_scenario import ID_RE, LITERAL_RE  # noqa: E402
from s6_write import split_body  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402
from lz4_block_map import decompress_blocks, parse_container  # noqa: E402
from srw_y_rebuild import rebuild_plain  # noqa: E402

LOCAL = HERE / 'local'
TRANS = HERE / 'translations' / 'scena_0000_0000300a_pl.json'
BUILD = HERE / 'build' / 'test_b'
GAME_AA = r'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'


def textasset_raw(raw: bytes, new_data: bytes) -> bytes:
    """TextAsset raw bytes with the script replaced: `u32 len, name, pad4, u32 len, data, pad4`."""
    name_len, = struct.unpack('<I', raw[:4])
    name = raw[4:4 + name_len]
    pos = 4 + name_len + (-(4 + name_len)) % 4
    out = bytearray(struct.pack('<I', name_len)) + name
    out += bytes(-len(out) % 4)
    out += struct.pack('<I', len(new_data)) + new_data
    out += bytes(-len(out) % 4)
    return bytes(out)


def scripts_of(path: Path) -> dict[str, str]:
    """Every TextAsset script inside an already-decrypted bundle, by object name."""
    plain = path.read_bytes()
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    import tempfile
    import UnityPy
    handle = tempfile.NamedTemporaryFile(suffix='.assets', delete=False)
    handle.write(blob)
    handle.close()
    env = UnityPy.load(handle.name)
    out = {}
    for obj in env.objects:
        if obj.type.name != 'TextAsset':
            continue
        name = obj.peek_name()
        if name:
            out[name] = obj.read().m_Script
    Path(handle.name).unlink(missing_ok=True)
    return out


def apply_pl(script: str, pl_by_id: dict[str, str]) -> tuple[str, set[str]]:
    """Replace the text of every literal whose string id has a translation."""
    from collections import Counter
    occurrences = Counter()
    out, last, used = [], 0, set()
    for match in LITERAL_RE.finditer(script):
        window = script[match.end():match.end() + 300].split('[[', 1)[0]
        found = ID_RE.search(window)
        if not found:
            continue
        string_id = found.group(1)
        occurrences[string_id] += 1
        exact = f'{string_id}#{occurrences[string_id]}'
        key = exact if exact in pl_by_id else string_id
        if key not in pl_by_id:
            continue
        body = match.group(1)
        speaker, separator, _old = split_body(body)
        out.append(script[last:match.start(1)])
        out.append(speaker + separator + pl_by_id[key])
        last = match.end(1)
        used.add(key)
    out.append(script[last:])
    return ''.join(out), used


def build_one(stem: str, asset: str, pl_by_id: dict[str, str], out_dir: Path) -> dict:
    cipher = (LOCAL / 's4' / f'{stem}.bundle').read_bytes()
    plain = decrypt(stem, cipher)
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))

    import tempfile
    import UnityPy
    handle = tempfile.NamedTemporaryFile(suffix='.assets', delete=False)
    handle.write(blob)
    handle.close()
    env = UnityPy.load(handle.name)
    old_raw = new_raw = None
    for obj in env.objects:
        if obj.type.name == 'TextAsset' and obj.peek_name() == asset:
            old_raw = obj.get_raw_data()
            script = obj.read().m_Script
            break
    Path(handle.name).unlink(missing_ok=True)
    if old_raw is None:
        raise SystemExit(f'{stem}: brak obiektu {asset}')

    new_script, used = apply_pl(script, pl_by_id)
    missing = sorted(set(pl_by_id) - used)
    if missing:
        raise SystemExit(f'{stem}: nie znaleziono id {missing}')
    new_raw = textasset_raw(old_raw, new_script.encode('utf-8'))

    new_plain, report = rebuild_plain(stem, plain, {asset: new_raw})
    out_cipher = encrypt(stem, new_plain)
    if decrypt(stem, out_cipher) != new_plain:
        raise SystemExit(f'{stem}: szyfrowanie nie odtwarza pliku')
    report['lines'] = len(used)
    report['script_before'] = len(script.encode('utf-8'))
    report['script_after'] = len(new_script.encode('utf-8'))
    report['original_size'] = len(cipher)
    report['size'] = len(out_cipher)
    report['sha256'] = hashlib.sha256(out_cipher).hexdigest()
    report['path'] = str(out_dir / f'{stem}.bundle')
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f'{stem}.bundle').write_bytes(out_cipher)
    return report


def build(trans: Path = TRANS, out_dir: Path = BUILD, check: bool = False) -> list[dict]:
    data = json.loads(Path(trans).read_text(encoding='utf-8'))
    pl_by_id = {row['id']: row['pl'] for row in data['lines']}
    asset = data['file']
    rows = []
    for locale, stem in data['source_bundles'].items():
        if check:
            scripts = scripts_of(LOCAL / 's4_plain' / f'{stem}.bundle')
            script = scripts[asset]
            _new, used = apply_pl(script, pl_by_id)
            rows.append({'locale': locale, 'stem': stem, 'lines': len(used),
                         'missing': sorted(set(pl_by_id) - used)})
            continue
        rows.append({'locale': locale, **build_one(stem, asset, pl_by_id, out_dir)})
    return rows


README = """# Test: czy gra przyjmuje plik, który zmienił rozmiar

To **nie jest** jeszcze polska wersja gry. To jeden test, który musi się udać, zanim
zaczniemy tłumaczyć całość.

## Co jest w środku

W grze tekst leży w plikach `.bundle`. Do tej pory umieliśmy podmienić tekst tylko tak,
żeby plik miał **dokładnie ten sam rozmiar** — tak działa polska narracja otwierająca,
którą już widziałeś. Taki sposób ma granicę: polski tekst musi się zmieścić w długości
angielskiego.

Ten test podmienia **jedną scenę** i pozwala plikowi **zmienić rozmiar**. Jeśli gra to
przyjmie, tłumaczenie nie będzie już niczym ograniczone.

Scena to pierwsze dialogi po narracji: `cse20_0000_0000300a` — 61 linii, przetłumaczone
z japońskiego. W kitcie są oba warianty językowe gry (japoński i angielski), żeby
zadziałało niezależnie od tego, jaki masz ustawiony.

## Co zrobić

1. Rozpakuj katalog na pulpit (nie na `C:` w głąb, wystarczy pulpit).
2. Zamknij grę.
3. Kliknij dwa razy **PATCH_PL.bat**.
4. Uruchom grę i **zacznij nową grę** (sejw nie jest potrzebny).

## Co powinieneś zobaczyć

Po narracji otwierającej (ta jest po polsku od poprzedniej łatki) pierwsze kwestie
powinny być po polsku:

```
（Świat się zmienia…）
（A co czeka dalej… katastrofa…
　a może zagłada…）
（Boję się…）
```

## Co mi napisz

1. Czy gra **w ogóle się uruchomiła** (doszła do logo / menu)?
2. Czy da się **zacząć nową grę**?
3. Czy pierwsze dialogi są **po polsku** — i czy znaki ą ć ę ł ń ó ś ź ż wyglądają dobrze?

Jeśli coś padnie — napisz, w którym momencie (przed logo / logo / menu / po wybraniu
nowej gry). To wystarczy, żeby wiedzieć, czy wina leży w rozmiarze pliku.

## Cofnięcie

Kliknij **COFNIJ.bat** — gra wróci do stanu sprzed testu (kopie `.bak` zostały obok
oryginałów).
"""


def write_test_kit(out_dir: Path = BUILD, zip_path: Path | None = None) -> dict:
    bundles = {path.name: path for path in sorted(Path(out_dir).glob('*.bundle'))}
    if not bundles:
        raise SystemExit(f'{out_dir}: brak zbudowanych plików')
    return write_kit(Path(out_dir) / 'kit', bundles, GAME_AA, README, zip_path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--trans', type=Path, default=TRANS)
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--kit', action='store_true', help='zapakuj gotowy kit i zip')
    parser.add_argument('--zip', type=Path, default=BUILD / 'SRW_Y_TEST_B_PL.zip')
    args = parser.parse_args(argv)
    for row in build(args.trans, args.out_dir, args.check):
        print(f"{row['locale']}  {row['stem']}: {row['lines']} linii"
              + (f", BRAK {row['missing']}" if row.get('missing') else ''))
        if 'size' not in row:
            continue
        print(f"  plik {row['original_size']:,} B -> {row['size']:,} B "
              f"({'URÓSŁ' if row['size'] > row['original_size'] else 'zmalał'}), "
              f"dane {row['data_before']:,} -> {row['data_after']:,} B")
        print(f"  skrypt {row['script_before']:,} B -> {row['script_after']:,} B, "
              f"bloków {row['blocks_before']} -> {row['blocks_after']}, "
              f"zmienione obiekty: {row['changed_objects']}")
        print(f"  {row['path']}")
    if args.kit and not args.check:
        kit = write_test_kit(args.out_dir, args.zip)
        print(f"kit: {kit['kit']} ({len(kit['files'])} plików), zip {kit['zip']} "
              f"{kit['zip_size']:,} B")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
