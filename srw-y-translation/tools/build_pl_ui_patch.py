#!/usr/bin/env python3
"""Polish into UI prefabs — the text that is in no table at all.

The title screen, the battle HUD and the library screen keep their labels as `TMP` text
inside `MonoBehaviour` assets, next to a `GameObject` with a name like `Text (TMP)`. That
is why patching `system_text` changed the character screen but left `Start / Option /
Store / Quit Game` in English: those words simply are not in a table.

Editing one is a typetree write: read the object, change `m_text`, save the tree back.
That is only safe if the writer is faithful, so the tool proves it before it writes
anything — read the tree, save it **unchanged**, and require the bytes to match the
original. UnityPy passes this for the objects we touch (checked: 516 B, byte for byte).

Then the bundle is rebuilt by `tools/srw_y_rebuild.py`, which verifies that every other
object came back untouched.

    python3 tools/build_pl_ui_patch.py --check
    python3 tools/build_pl_ui_patch.py --base build/v3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

import UnityPy  # noqa: E402

from build_pl_table_patch import GAME_AA, plain_of, source_of  # noqa: E402
from pl_kit import write_kit  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402
from lz4_block_map import decompress_blocks, parse_container  # noqa: E402
from srw_y_rebuild import objects_of, rebuild_plain  # noqa: E402

LOCAL = HERE / 'local'
TRANS = HERE / 'translations' / 'ui_test_pl.json'
BUILD = HERE / 'build' / 'test_ui'
TEXT_FIELDS = ('m_text', 'm_Text', 'text')


def load_objects(plain: bytes):
    """UnityPy environment over an already-decrypted bundle."""
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    handle = tempfile.NamedTemporaryFile(suffix='.assets', delete=False)
    handle.write(blob)
    handle.close()
    return UnityPy.load(handle.name), Path(handle.name), blob


def faithful(env, path_id: int) -> bool:
    """Can the writer reproduce this object byte for byte with no change?

    `save_typetree` does not touch the file, it hands the new bytes to `obj.data`, and
    `get_raw_data()` keeps returning the old ones. The comparison has to be against
    `obj.data`, or every writer looks faithful.
    """
    for obj in env.objects:
        if obj.path_id != path_id:
            continue
        raw = obj.get_raw_data()
        tree = obj.read_typetree()
        obj.save_typetree(tree)
        return obj.data == raw
    return False


def text_of(tree) -> str | None:
    if not isinstance(tree, dict):
        return None
    for field in TEXT_FIELDS:
        value = tree.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return None


def edit(stem: str, strings: list[dict], start: Path, out_dir: Path) -> dict:
    plain = plain_of(stem, start)
    env, temp_path, blob = load_objects(plain)
    by_path = {obj.path_id: obj for obj in env.objects}

    done, edits = [], {}  # path_id -> new raw bytes
    for row in strings:
        path_id = row.get('path_id')
        if path_id is None:
            # locate by the text the player sees, never by position
            for obj in env.objects:
                if obj.type.name != 'MonoBehaviour':
                    continue
                try:
                    tree = obj.read_typetree()
                except Exception:                                  # noqa: BLE001
                    continue
                if text_of(tree) == row['old']:
                    path_id = obj.path_id
                    break
        if path_id is None or path_id not in by_path:
            raise SystemExit(f'{stem}: nie znaleziono tekstu {row["old"]!r}')
        obj = by_path[path_id]
        if not faithful(env, path_id):
            raise SystemExit(f'{stem}: {path_id} nie zapisuje się bajt w bajt — przerywam')
        tree = obj.read_typetree()
        current = text_of(tree)
        if current != row['old']:
            raise SystemExit(f'{stem}: {path_id} ma {current!r}, oczekiwano {row["old"]!r}')
        for field in TEXT_FIELDS:
            if isinstance(tree.get(field), str) and tree[field].strip():
                tree[field] = row['pl']
                break
        obj.save_typetree(tree)
        edits[path_id] = obj.data
        done.append({'path_id': path_id, 'old': row['old'], 'pl': row['pl']})

    # the rebuild addresses objects by name, falling back to the path id for the
    # nameless ones (UI components usually have no name of their own)
    new_edits = {}
    for path_id, raw in edits.items():
        name = by_path[path_id].peek_name()
        new_edits[name or path_id] = raw
    temp_path.unlink(missing_ok=True)

    new_plain, report = rebuild_plain(stem, plain, new_edits)
    out_cipher = encrypt(stem, new_plain)
    if decrypt(stem, out_cipher) != new_plain:
        raise SystemExit(f'{stem}: szyfrowanie nie odtwarza pliku')

    # read the result back: the Polish text has to be there, and only our objects changed
    check_env, check_path, check_blob = load_objects(new_plain)
    found = {}
    for obj in check_env.objects:
        if obj.path_id in {row['path_id'] for row in done}:
            found[obj.path_id] = text_of(obj.read_typetree())
    check_path.unlink(missing_ok=True)
    for row in done:
        if found.get(row['path_id']) != row['pl']:
            raise SystemExit(f'{stem}: {row["path_id"]} po zapisie ma {found.get(row["path_id"])!r}')

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'{stem}.bundle'
    path.write_bytes(out_cipher)
    return {
        'stem': stem,
        'start': str(start),
        'path': str(path),
        'strings': done,
        'changed_objects': report['changed_objects'],
        'original_size': start.stat().st_size,
        'size': len(out_cipher),
        'sha256': hashlib.sha256(out_cipher).hexdigest(),
    }


def build(trans: Path = TRANS, out_dir: Path = BUILD, base: Path | None = None,
          check: bool = False) -> list[dict]:
    data = json.loads(Path(trans).read_text(encoding='utf-8'))
    rows = []
    for stem, spec in sorted(data['bundles'].items()):
        if check:
            start, origin = source_of(stem, base)
            plain = plain_of(stem, start)
            env, temp_path, _blob = load_objects(plain)
            available = []
            for obj in env.objects:
                if obj.type.name != 'MonoBehaviour':
                    continue
                try:
                    tree = obj.read_typetree()
                except Exception:                                  # noqa: BLE001
                    continue
                text = text_of(tree)
                if text:
                    available.append({'path_id': obj.path_id, 'text': text,
                                      'faithful': faithful(env, obj.path_id)})
            temp_path.unlink(missing_ok=True)
            rows.append({'stem': stem, 'name': spec.get('file'), 'origin': origin,
                         'wanted': spec['strings'], 'available': available})
            continue
        start, origin = source_of(stem, base)
        rows.append(edit(stem, spec['strings'], start, out_dir) | {'origin': origin})
    return rows


README = r"""# Test 3 — polski tekst w interfejsie (prefaby)

Ten test podmienia **tekst zapisany w prefabach interfejsu** — czyli tam, gdzie gry
nie ma w żadnej tabeli. Nic więcej nie zmienia: scenariusze, dialogi i tabele
zostają takie, jakie masz po poprzednich testach.

## Co zrobić

1. Rozpakuj paczkę na Pulpit (nie na dysk C:, wystarczy Pulpit).
2. Kliknij **PATCH_PL.bat**. Skrypt sam zrobi kopię oryginałów (`*.bak`) i wgra polskie pliki.
3. Uruchom grę.

## Co powinno być widać

| gdzie | po polsku |
|---|---|
| ekran tytułowy, pod logo | **Naciśnij klawisz** (zamiast `Press Any Key`) |
| menu opcji (OPTION na ekranie tytułowym) | **Menu opcji** zamiast `オプションメニュー` |
| biblioteka / baza (jeśli do niej dojdziesz) | **Wybierz**, **Baza**, **Wstecz** |

Polskie znaki (ś, ł, ą) są tu testem samym w sobie — ten interfejs rysuje czcionka
systemowa gry, więc jeśli zobaczysz krzak albo pusty kwadrat, to znaczy, że trzeba
podmienić także czcionkę. Napisz, co widzisz.

## Czego ten test NIE tłumaczy

`Start`, `Option`, `Store`, `Quit Game` na ekranie tytułowym **nie są tekstem** —
gra rysuje je jako obrazki (atlas czcionki w pliku `OptionMenuButton_Font`).
Żeby je przetłumaczyć, trzeba przerobić grafiki. Potrzebuję do tego trzech plików
z gry — proszę o nie osobno, jednym zipem:

```
D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64\7fc03a2448f7447d2b8dc8a7fe572602.bundle
D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64\4392254603b2e07498c65fe2788b755a.bundle
D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64\06b684d7f64d1737577f15b966911236.bundle
```

Razem jakieś 1,7 MB.

## Cofnięcie

Kliknij **COFNIJ.bat** — wróci do stanu sprzed tego testu. Wcześniejsze testy
(scenariusz, tabele) zostają, bo ten kit ich nie dotyka.
"""


def write_kit_for(rows: list[dict], out_dir: Path = BUILD, zip_path: Path | None = None) -> dict:
    bundles = {f'{row["stem"]}.bundle': Path(row['path']) for row in rows}
    return write_kit(Path(out_dir) / 'kit', bundles, GAME_AA, README, zip_path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--trans', type=Path, default=TRANS)
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--base', type=Path, default=None)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--kit', action='store_true')
    parser.add_argument('--zip', type=Path, default=None)
    args = parser.parse_args(argv)
    rows = build(args.trans, args.out_dir, args.base, args.check)
    if args.kit and not args.check:
        kit = write_kit_for(rows, args.out_dir, args.zip)
        print(f"kit: {kit['kit']} ({len(kit['files'])} plików), zip {kit.get('zip')} "
              f"{kit.get('zip_size', 0):,} B")
    for row in rows:
        if args.check:
            print(f"{row['stem']} ({row['name']}, {row['origin']}):")
            for want in row['wanted']:
                print(f"   chcemy: {want['old']!r} -> {want['pl']!r}")
            print(f"   tekstów w pliku: {len(row['available'])}")
            for item in row['available'][:8]:
                print(f"      {item['path_id']:>22} {item['text']!r} "
                      f"({'zapis wierny' if item['faithful'] else 'NIE ZAPISZE SIĘ'})")
            continue
        print(f"{row['stem']} ({row['origin']}): {row['original_size']:,} -> "
              f"{row['size']:,} B, zmienione: {row['changed_objects']}")
        for item in row['strings']:
            print(f"   {item['old']!r} -> {item['pl']!r}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
