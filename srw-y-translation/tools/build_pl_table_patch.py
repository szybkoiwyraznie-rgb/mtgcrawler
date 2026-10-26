#!/usr/bin/env python3
"""Polish into the game's text tables — main menu, character select, pilot entries.

Scenes are Lua scripts; everything else the player reads is a **text table**: a
`MonoBehaviour` that holds `u32 key, u32 key, length, text` records, one object per table
per language (`system_text_en-US`, `dic_text_pilot_ja-JP`, …).  `s6_write.encode_table`
rebuilds such an object byte for byte (proven on 288/288 objects), so writing one is the
same operation as writing a scene; only the storage differs.

This tool replaces chosen rows by their key — never by position — rebuilds the bundle with
`tools/srw_y_rebuild.py` (size may change, that mode is proven in game) and verifies that
every **other** object came back untouched.  A missing key is an error, not a warning: a
silently skipped row would ship English in the middle of a Polish screen.

    python3 tools/build_pl_table_patch.py --check
    python3 tools/build_pl_table_patch.py --kit --base build/v3 \
        --kit-extra build/test_b/*.bundle

`--base` is the directory holding the already-patched bundles to build **on top of** — the
prologue narration lives in the same bundle as the base tables, so a table patch built from
the untranslated original would put the narration back into English.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

from pl_kit import write_kit  # noqa: E402
from s6_tables import table_header, walk_records  # noqa: E402
from s6_write import encode_table  # noqa: E402
from srw_y_bundle_crypt import decrypt, encrypt  # noqa: E402
from lz4_block_map import decompress_blocks, parse_container  # noqa: E402
from srw_y_rebuild import objects_of, rebuild_plain  # noqa: E402

LOCAL = HERE / 'local'
TRANS = HERE / 'translations' / 'tabele_test_pl.json'
BUILD = HERE / 'build' / 'test_tabele'
INVENTORY = LOCAL / 's6' / 'inventory.json'
GAME_AA = r'D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64'

#: base tables live in the two bundles that also carry the prologue narration
BASE_BUNDLES = {'en-US': '2d69c099bfdf0e252dabe84dbbba11df',
                'ja-JP': '1cc7e02ee5711c6ba87a0e364f62198c'}


def bundle_index() -> dict[str, str]:
    """object name -> bundle file name, from the inventory of every extracted bundle."""
    index = {}
    if INVENTORY.is_file():
        for row in json.loads(INVENTORY.read_text(encoding='utf-8')):
            for obj in row['objects']:
                name = obj.get('name')
                if name:
                    index.setdefault(name, row['bundle'].removesuffix('.bundle'))
    return index


PLAIN_ROOTS = (LOCAL / 's6' / 'plain', LOCAL / 'ui', LOCAL / 'ui6')


def source_of(stem: str, base: Path | None) -> tuple[Path, str]:
    """The bundle to start from: the already-patched copy, the original, or a plaintext copy.

    Only the four base bundles were kept encrypted in `local/s4`; DLC and free-patch
    bundles were ingested already decrypted, so for those the starting point is the
    plaintext copy and only the *output* is encrypted.
    """
    if base and (Path(base) / f'{stem}.bundle').is_file():
        return Path(base) / f'{stem}.bundle', 'z poprzedniej łatki'
    original = LOCAL / 's4' / f'{stem}.bundle'
    if original.is_file():
        return original, 'oryginał'
    for root in PLAIN_ROOTS:
        for path in root.rglob(f'{stem}.bundle'):
            return path, 'odczytany oryginał (DLC / wolna poprawka)'
    raise SystemExit(f'{stem}: nie ma skąd wziąć pliku (local/s4, local/s6/plain)')


def plain_of(stem: str, path: Path) -> bytes:
    """Decrypt when the file is still the game's ciphertext; pass plaintext through."""
    data = Path(path).read_bytes()
    return data if data[:7] == b'UnityFS' else decrypt(stem, data)


def build_one(stem: str, edits: dict[str, dict[str, str]], start: Path, out_dir: Path) -> dict:
    original_size = start.stat().st_size
    plain = plain_of(stem, start)
    layout = parse_container(plain)
    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    objects = {name: raw for _path_id, name, raw in objects_of(blob)}

    new_edits, report_rows = {}, []
    for object_name, replacements in sorted(edits.items()):
        raw = objects.get(object_name)
        if raw is None:
            raise SystemExit(f'{stem}: brak obiektu {object_name}')
        start_at, count = table_header(raw, object_name)
        rows, _ = walk_records(raw, start_at, count)
        known = {row['key'] for row in rows}
        missing = sorted(set(replacements) - known)
        if missing:
            raise SystemExit(f'{object_name}: brak kluczy {missing}')
        before = {row['key']: len(row['text'].encode('utf-8')) for row in rows}
        new_raw = encode_table(raw, replacements)
        # read the rebuilt object back: the replacement has to be in it, and nothing else
        start_at, count2 = table_header(new_raw, object_name)
        rows_after, _ = walk_records(new_raw, start_at, count2)
        if count2 != count:
            raise SystemExit(f'{object_name}: {count} wpisów stało się {count2}')
        after = {row['key']: row['text'] for row in rows_after}
        for key, text in replacements.items():
            if after.get(key) != text:
                raise SystemExit(f'{object_name}: wpis {key} nie zapisał się')
        for row in rows_after:
            if row['key'] not in replacements and after[row['key']] != next(
                    r['text'] for r in rows if r['key'] == row['key']):
                raise SystemExit(f'{object_name}: wpis {row["key"]} zmienił się bez powodu')
        new_edits[object_name] = new_raw
        report_rows.append({
            'object': object_name,
            'entries': len(replacements),
            'bytes_before': len(raw),
            'bytes_after': len(new_raw),
            'rows_grown': sum(1 for key in replacements
                              if len(replacements[key].encode('utf-8')) > before[key]),
            'rows_shrunk': sum(1 for key in replacements
                               if len(replacements[key].encode('utf-8')) < before[key]),
        })

    new_plain, report = rebuild_plain(stem, plain, new_edits)
    out_cipher = encrypt(stem, new_plain)
    if decrypt(stem, out_cipher) != new_plain:
        raise SystemExit(f'{stem}: szyfrowanie nie odtwarza pliku')
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'{stem}.bundle'
    path.write_bytes(out_cipher)
    report.update({
        'start': str(start),
        'path': str(path),
        'original_size': original_size,
        'size': len(out_cipher),
        'changed_objects': report['changed_objects'],
        'rows': report_rows,
        'sha256': hashlib.sha256(out_cipher).hexdigest(),
    })
    return report


def plan(trans: Path = TRANS) -> dict[str, dict[str, dict[str, str]]]:
    """bundle stem -> object name -> {key: polish}."""
    data = json.loads(Path(trans).read_text(encoding='utf-8'))
    index = bundle_index()
    out: dict[str, dict[str, dict[str, str]]] = {}
    for table, entries in data['tables'].items():
        texts = {key: row['pl'] for key, row in entries.items()}
        for locale, base in BASE_BUNDLES.items():
            name = f'{table}_{locale}'
            stem = index.get(name, base)
            out.setdefault(stem, {})[name] = texts
    return out


def build(trans: Path = TRANS, out_dir: Path = BUILD, base: Path | None = None,
          check: bool = False) -> list[dict]:
    rows = []
    for stem, edits in sorted(plan(trans).items()):
        if check:
            rows.append({'stem': stem, 'objects': sorted(edits),
                         'entries': {name: len(texts) for name, texts in edits.items()}})
            continue
        start, origin = source_of(stem, base)
        rows.append(build_one(stem, edits, start, out_dir) | {'origin': origin})
    return rows


README = """# Test 2: menu, wybór postaci i tabele tekstowe

Pierwszy test (dialogi) wypadł dobrze: gra przyjmuje plik, który **zmienia rozmiar**.
Ten test sprawdza drugi rodzaj tekstu w grze — **tabele**: menu tytułowe, ekran wyboru
postaci i hasło encyklopedii pilota.

## Co jest w środku

Cztery pliki gry:

* dwa z dialogami z poprzedniego testu (nadal po polsku, nic nie tracisz),
* dwa z tabelami — a w nich między innymi:

| miejsce w grze | po polsku |
|---|---|
| menu tytułowe | Nowa gra · Wczytaj · Opcje · System · Licencje · Sklep · Wyjdź z gry · Naciśnij dowolny przycisk |
| wybór trybu | Wybierz tryb · Tryb |
| wybór postaci | Wybór postaci · Wzrost · Charakter · Hobby · Ulubione danie · Ustawienia postaci · Nazwisko · Imię · Przydomek · Data urodzenia · Grupa krwi |
| profil bohaterów A i B | 180 cm / 162 cm · Chłodny, bezwzględny · Optymistka, wesoła · Czytanie książek · Oglądanie sumo · Shime saba · Yakitori + opis postaci (5 linii) |
| encyklopedia pilotów | hasło Forte Tsukinowa: NINJA, wiek, charakter + biografia |

## Co zrobić

1. Rozpakuj **do nowego folderu** na pulpicie.
2. Zamknij grę.
3. Kliknij **PATCH_PL.bat** (raz).
4. Uruchom grę.

## Co powinieneś zobaczyć

Już na **ekranie tytułowym** przyciski powinny być po polsku. Potem: `Nowa gra` →
`Wybierz tryb` → `Wybór postaci`, gdzie klawiszami Q/E przełączasz bohatera A i B.
Opis postaci pod listą cech też jest po polsku.

## Na co patrzeć (to jest sedno testu)

Część napisów jest **dłuższa** niż angielskie (np. `Ulubione danie` zamiast `Fav. Food`,
`Data urodzenia` zamiast `Birthday`). Interesuje mnie:

1. Czy napisy **mieszczą się** w przyciskach i polach, czy wychodzą poza ramkę?
2. Czy dłuższy tekst jest **przycinany** (ucięty), czy panel się rozciąga?
3. Czy polskie znaki wyglądają dobrze także w menu i w małych napisach?

Jeśli coś wychodzi poza ramkę — napisz **które**, a dopasuję długości. To nie jest błąd
podmiany, tylko szerokość pola.

## Cofnięcie

Kliknij **COFNIJ.bat** (przywraca cztery pliki z kopii `.bak`).
"""


def write_test_kit(out_dir: Path = BUILD, zip_path: Path | None = None,
                   extra: list[Path] | None = None) -> dict:
    bundles = {path.name: path for path in sorted(Path(out_dir).glob('*.bundle'))}
    for path in extra or []:
        bundles[Path(path).name] = Path(path)
    if not bundles:
        raise SystemExit(f'{out_dir}: brak zbudowanych plików')
    return write_kit(Path(out_dir) / 'kit', bundles, GAME_AA, README, zip_path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--trans', type=Path, default=TRANS)
    parser.add_argument('--out-dir', type=Path, default=BUILD)
    parser.add_argument('--base', type=Path, default=None,
                        help='katalog z już połatanymi bundle\'ami, na których budujemy')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--kit', action='store_true')
    parser.add_argument('--kit-extra', nargs='*', type=Path, default=[])
    parser.add_argument('--zip', type=Path, default=BUILD / 'SRW_Y_TEST_2_MENU_TABELE.zip')
    args = parser.parse_args(argv)

    for row in build(args.trans, args.out_dir, args.base, args.check):
        if args.check:
            print(f"{row['stem']}: {row['objects']} -> {row['entries']}")
            continue
        print(f"{row['stem']} ({row['origin']}): {row['original_size']:,} B -> "
              f"{row['size']:,} B, zmienione obiekty: {row['changed_objects']}")
        for obj in row['rows']:
            print(f"   {obj['object']}: {obj['entries']} wpisów, "
                  f"{obj['bytes_before']:,} -> {obj['bytes_after']:,} B "
                  f"(dłuższe: {obj['rows_grown']}, krótsze: {obj['rows_shrunk']})")
    if args.kit and not args.check:
        kit = write_test_kit(args.out_dir, args.zip, args.kit_extra)
        print(f"kit: {kit['kit']} ({len(kit['files'])} plików), zip {kit['zip']} "
              f"{kit['zip_size']:,} B")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
