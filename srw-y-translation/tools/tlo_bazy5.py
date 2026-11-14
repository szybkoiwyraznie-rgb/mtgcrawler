#!/usr/bin/env python3
"""Narzędzie właściciela: **oba** tła ekranu Database na czarno, w jednej paczce.

Runda 15 (2026-11-13). v2 (`tlo_bazy.py`) wyczerniło `BG_DataBase_01` — wnętrze
A. Adventu. v3 (`tlo_bazy2.py`) wyczerniło `BG_DataBase_02` — pulsującą siatkę.
Obie paczki były robione pod grę **1.4.0** i obie zakładały, że w grze leży
dokładnie 16 plików z listy. Potem właściciel zainstalował mod 4K Visual
Overhaul, który podmienia wszystkie assety 2D na upscalowane wersje — czyli
prawdopodobnie właśnie te 16 bundli, z innymi pikselami i **innym rozmiarem
slotów**.

v4 jest jedną paczką, która:

* robi **2 w 1**: obie tekstury (`BG_DataBase_01` i `BG_DataBase_02`) w jednym
  przebiegu, w tych samych plikach — nie trzeba już pilnować kolejności v2 → v3,
  ani cofać jednej warstwy żeby założyć drugą;
* **działa na plikach z moda**: nie sprawdza sum plików, tylko zawartość —
  teksturę o danej nazwie, jej rozmiar i format odczytane **z bundla w grze**.
  Slot strumienia bierze się z metadanych tekstury, więc 4K (np. 3840×2160
  zamiast 1920×1080) jest obsłużone bez założeń;
* gdy plik z listy nie ma już tekstury (np. mod przeniósł ją do innego bundla
  albo usunął), **szuka tej tekstury po zawartości** — deszyfruje i dekompresuje
  bundle, dopóki nie znajdzie nazwy; dzięki temu paczka nie zależy od tego,
  czy mod zostawił nazwy plików na miejscu;
* nie wymaga żadnego pliku ode mnie: nie potrzebuję od Ciebie ani bundli, ani
  archiwum moda. Wszystko liczy się na Twojej kopii gry.

Czego v4 **nie** robi: nie cofa moda. Cofnięcie (`COFNIJ5.bat`) przywraca plik,
który był w grze przed v4 — czyli wersję **z moda 4K**, nie czystą 1.4.0.

    python tlo_bazy5.py install        # oba tła na czarno
    python tlo_bazy5.py restore        # powrót do stanu sprzed v4
    python tlo_bazy5.py check          # tylko raport, nic nie zapisuje

Opisy i powody decyzji: `docs/TLO_BAZY_DANYCH.md`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cipher_fast import decrypt_bundle, plain_of  # noqa: E402
from srw_y_bundle_crypt import encrypt  # noqa: E402

GAME_DATA = 'SUPER ROBOT WARS Y_Data'
AA = Path('StreamingAssets') / 'aa' / 'StandaloneWindows64'
#: Obie tekstury, które v4 wyczernia w jednym przebiegu. Kolejność jest tylko
#: porządkiem raportu — każda jest niezależna.
TEXTURES = ('BG_DataBase_01', 'BG_DataBase_02')
#: Rozmiar z 1.4.0. **Nie jest warunkiem**: po modzie 4K tekstura ma inny
#: rozmiar i to jest w porządku. Sluży tylko do tego, żeby w raporcie nazwać
#: „ten sam rozmiar co w 1.4.0” albo „rozmiar z moda”.
SIZE_140 = (1920, 1080)
#: Każdy bundle, o którym wiemy z `RAPORT_TEKSTUR.txt` (spis z 1.4.0), że
#: zawiera te dwie tekstury. Po modzie lista może się nie zgadzać — wtedy
#: wchodzi szukanie po zawartości.
BUNDLES = (
    '9ed026a1fc86446a7b96c863f449293e.bundle',
    '1b5da0ef65aef8e3db19c7f1b4a62ad2.bundle',
    '1c6bae8333d43883715cd3c80e6b06a8.bundle',
    '21483b8c72946df172995fc28fe8513c.bundle',
    '22ac8fb334093afc874a670d95b01504.bundle',
    '24389cf9b6ff0c69440a0054b07a0a9b.bundle',
    '2fcd1b5e54f206a6ecf97a71c74dcd81.bundle',
    '36f12b4c38f68ad8811ade71945010c9.bundle',
    '3de1bf33b35e63e87abb86acc029004f.bundle',
    '77a2edfda00011ae81b0d44829865614.bundle',
    '77c28b41bf3d3714c686eafb475fc32a.bundle',
    '819fcfa52c97d0420146203b181e38cf.bundle',
    '89807f3be3a7048e8e26f7e8edccb6da.bundle',
    '90eb8d46b646d92973b36bac119ca271.bundle',
    '9e56e5c953cea02a1e42b2ed1dba787f.bundle',
    'cea16a719b85736215c37206de071b72.bundle',
)
MIN_BUNDLE = 64 * 1024
BACKUP_SUFFIX = '.srwy-tlo-original.bak'
STATE = HERE / 'STAN_TLO5.json'
REPORT = HERE / 'RAPORT_TLO5.txt'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def log(lines: list[str] | None, text: str) -> None:
    print(text, flush=True)
    if lines is not None:
        lines.append(text)


def check_game_stopped() -> None:
    """Refuse to write while the game runs — Windows would keep the file open."""
    if os.name != 'nt':
        return
    try:
        output = subprocess.run(['tasklist'], capture_output=True, text=True,
                                timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return
    for row in output.splitlines():
        if row and 'super robot wars y' in row[0].lower():
            raise ValueError('gra jest uruchomiona — zamknij ją przed podmianą lub cofnięciem')


def find_game() -> Path:
    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
        for suffix in ('SUPER ROBOT WARS Y', 'SRWY',
                       'Games/SUPER ROBOT WARS Y', 'Gry/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SUPER ROBOT WARS Y',
                       'SteamLibrary/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SRWY',
                       'Program Files/Steam/steamapps/common/SRWY',
                       'Program Files (x86)/Steam/steamapps/common/SUPER ROBOT WARS Y',
                       'Program Files/Steam/steamapps/common/SUPER ROBOT WARS Y'):
            candidate = Path(f'{letter}:/{suffix}')
            if (candidate / GAME_DATA).is_dir():
                print(f'Znaleziono gre: {candidate}')
                return candidate
    return Path(input('Podaj folder gry SUPER ROBOT WARS Y: ').strip().strip('"'))


def mentions(plain: bytes, wanted: bytes) -> bool:
    """Czy ten bundle w ogóle wymienia nazwę? (bloki bywają LZ4 — stąd dekompresja)"""
    if wanted in plain:
        return True
    try:
        from lz4_block_map import decompress_blocks, parse_container

        layout = parse_container(plain)
        blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    except Exception:            # nie nasz kontener — nie nasz bundle
        return False
    return wanted in blob


def pinned_paths(streaming: Path) -> list[Path]:
    """Pliki z listy, które są w tej kopii gry — bez chodzenia po dysku."""
    return [streaming / name for name in BUNDLES if (streaming / name).is_file()]


def load_env(plain: bytes, layout: dict, streams: list[bytes]):
    """UnityPy na strumieniu serializowanym z tego bundla (bez plików tymczasowych).

    v2/v3/v4 do tej pory wypakowywały strumienie do katalogu tymczasowego tylko
    po to, żeby UnityPy miało z czego czytać. UnityPy przyjmuje bajty wprost,
    a wtedy nie ma czego sprzątać ani o co się potknąć na dysku właściciela.
    """
    import UnityPy

    from lz4_block_map import decompress_blocks

    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    return UnityPy.load(blob)


def texture_slots(plain: bytes, layout: dict, streams: list[bytes],
                  lines: list[str]) -> tuple[dict, list[str]]:
    """Gdzie leżą piksele naszych tekstur i **jak** są zapisane — czytane z bundla.

    Są dwa sposoby, w jakie Unity trzyma obrazek i oba występują w tej grze:

    * `inline` — piksele siedzą w obiekcie tekstury (`Texture2D.image_data`),
      `m_StreamData` jest puste. Tak robi **mod 4K**: przepakował assety
      i włożył obrazki do środka. Wersja v4, która szukała tylko strumienia,
      na takim pliku mówiła „nie ma strumienia (brak)” i nie robiła nic;
    * `stream` — piksele leżą w osobnym `.resS` pod `offset`/`size`
      z `m_StreamData`. Tak trzyma je gra 1.4.0.

    Zwraca `{nazwa: {mode, ...}}` plus listę problemów (tekstura jest, ale nie
    umiemy jej zapisać). Rozmiar, format i liczbę mipmap bierzemy **z pliku
    w grze**, nie z 1.4.0 — po modzie 4K obrazek ma inny rozmiar i ten sam kod
    ma go obsłużyć.
    """
    from db_black import expected_size, format_name, is_supported

    env = load_env(plain, layout, streams)
    slots, problems = {}, []
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        tree = obj.read_typetree()
        name = str(tree.get('m_Name'))
        if name not in TEXTURES:
            continue
        fmt, width, height = (int(tree['m_TextureFormat']), int(tree['m_Width']),
                              int(tree['m_Height']))
        mips = int(tree.get('m_MipCount') or 1)
        if not is_supported(fmt):
            problems.append(f'{name}: {format_name(fmt)} — czerni w tym formacie nie zapisze')
            continue
        want = expected_size(fmt, width, height, mips)
        channel = tree.get('m_StreamData') or {}
        offset, size = int(channel.get('offset') or 0), int(channel.get('size') or 0)
        stream_name = str(channel.get('path') or '').rsplit('/', 1)[-1]
        inline = tree.get('image data') or b''
        # Kolejność jest ta sama, co w `Texture2D.get_image_data()`: jeśli obiekt
        # niesie piksele, to one są obrazkiem, a `m_StreamData` bywa wtedy resztką
        # po przepakowaniu. Trzymanie się tej kolejności znaczy, że czernimy to,
        # co gra naprawdę rysuje.
        if inline or (not stream_name and not size):
            # inline: piksele w obiekcie. `image data` w typetree to surowe bajty;
            # jeśli UnityPy podało je jako listę, składamy z powrotem.
            pixels = bytes(inline) if isinstance(inline, (bytes, bytearray)) \
                else bytes(int(byte) & 0xFF for byte in inline)
            if not pixels:
                problems.append(f'{name}: {format_name(fmt)} bez pikseli w obiekcie '
                                f'i bez strumienia — nie wiem, gdzie jest obrazek')
                continue
            if len(pixels) != want:
                problems.append(f'{name}: {format_name(fmt)} {width}x{height} '
                                f'z {mips} mipmapami to {want} B, a w obiekcie jest '
                                f'{len(pixels)} B — nie ruszam')
                continue
            slots[name] = {'mode': 'inline', 'object': obj, 'path_id': obj.path_id,
                           'size': len(pixels), 'width': width, 'height': height,
                           'mips': mips, 'format': fmt}
            continue
        index = next((i for i, entry in enumerate(layout['files'])
                      if entry[3] == stream_name), None)
        if index is None:
            problems.append(f'{name}: nie ma strumienia {stream_name or "(brak)"}')
            continue
        if size != want:
            problems.append(f'{name}: {format_name(fmt)} zajmuje {size} B, '
                            f'a format kaze {want} B — nie ruszam')
            continue
        if index >= len(streams) or offset + size > len(streams[index]):
            problems.append(f'{name}: slot {offset}+{size} wychodzi poza strumien '
                            f'{stream_name} ({len(streams[index])} B)')
            continue
        slots[name] = {'mode': 'stream', 'stream': index, 'stream_name': stream_name,
                       'offset': offset, 'size': size, 'width': width, 'height': height,
                       'mips': mips, 'format': fmt}
    return slots, problems


def blacken_streams(streams: list[bytes], slots: dict,
                    lines: list[str] | None = None) -> tuple[list[bytes], dict, list[str]]:
    """Czysta część roboty: wpisz czerń w sloty **obu** tekstur, bez Unity.

    Osobno od parsowania bundla, bo to jedyne miejsce, w którym można się pomylić
    przy „2 w 1”: dwie tekstury w tym samym strumieniu, w różnych strumieniach
    albo jedna już czarna. Każdy przypadek jest sprawdzalny na bajtach, bez gry.

    Dotyczy tylko tekstur w trybie `stream`. Tekstury `inline` zapisuje
    `blacken_inline`, bo ich piksele nie są częścią żadnego strumienia.
    """
    from db_black import black_chain, format_name, verify_black_chain

    result = list(streams)
    changed, problems = {}, []
    for name, slot in slots.items():
        if slot.get('mode', 'stream') != 'stream':
            continue
        index = slot['stream']
        if index >= len(result):
            problems.append(f'{name}: nie ma strumienia o numerze {index}')
            continue
        data = bytearray(result[index])
        at, size = slot['offset'], slot['size']
        try:
            black = black_chain(slot['format'], slot['width'], slot['height'],
                                slot.get('mips', 1))
        except ValueError as error:
            # Jeden nieobsługiwany format nie może zabrać drugiej teksturze
            # szansy — reszta pliku jest od tego niezależna.
            problems.append(f'{name}: {error}')
            continue
        if len(black) != size:
            problems.append(f'{name}: {format_name(slot["format"])} koduje {len(black)} B, '
                            f'a slot ma {size} B — nie ruszam')
            continue
        if verify_black_chain(slot['format'], black, slot['width'], slot['height'],
                              slot.get('mips', 1)) is False:
            problems.append(f'{name}: zakodowana czern nie dekoduje sie na czern')
            continue
        before = bytes(data[at:at + size])
        info = {'texture': name, 'width': slot['width'], 'height': slot['height'],
                'mips': slot.get('mips', 1), 'format': format_name(slot['format']),
                'slot': size, 'mode': 'stream', 'stream': slot['stream_name'],
                'already_black': before == black, 'bytes_changed': 0}
        if before != black:
            data[at:at + size] = black
            result[index] = bytes(data)
            info['bytes_changed'] = sum(1 for a, b in zip(before, black) if a != b)
        else:
            log(lines, f'   {name}: juz czarne — zostawiam')
        changed[name] = info
    return result, changed, problems


def blacken_inline(slots: dict, lines: list[str] | None = None) -> tuple[dict, dict, list[str]]:
    """Czerń w teksturach trzymanych **w obiekcie** (tak robi mod 4K).

    To jest sedno poprawki v5: po modzie 4K `m_StreamData` jest puste, a piksele
    siedzą w `image data` obiektu tekstury. Zapisujemy nowy typetree tego jednego
    obiektu (`save_typetree`), a resztę pliku zostawia nietkniętą `rebuild_plain`
    — razem z jego sprawdzeniem, że żaden inny obiekt się nie zmienił.

    Zwraca `(nowe_surowe_bajty_obiektów, zmienione, problemy)`.
    """
    from db_black import black_chain, format_name, verify_black_chain

    edits, changed, problems = {}, {}, []
    for name, slot in slots.items():
        if slot.get('mode') != 'inline':
            continue
        obj = slot['object']
        try:
            black = black_chain(slot['format'], slot['width'], slot['height'],
                                slot.get('mips', 1))
        except ValueError as error:
            problems.append(f'{name}: {error}')
            continue
        if len(black) != slot['size']:
            problems.append(f'{name}: {format_name(slot["format"])} koduje {len(black)} B, '
                            f'a w obiekcie jest {slot["size"]} B — nie ruszam')
            continue
        if verify_black_chain(slot['format'], black, slot['width'], slot['height'],
                              slot.get('mips', 1)) is False:
            problems.append(f'{name}: zakodowana czern nie dekoduje sie na czern')
            continue
        try:
            tree = obj.read_typetree()
            before = bytes(tree.get('image data') or b'')
            if len(before) != len(black) and before:
                problems.append(f'{name}: obiekt ma {len(before)} B pikseli, '
                                f'a ma byc {len(black)} B — nie ruszam')
                continue
            tree['image data'] = black
            tree['m_CompleteImageSize'] = len(black)
            # Zapis typu tree nadpisuje surowe bajty obiektu; `rebuild_plain`
            # porówna potem, czy zmienił się **tylko** ten obiekt.
            raw = obj.save_typetree(tree)
        except (KeyError, TypeError, ValueError) as error:
            problems.append(f'{name}: nie umiem zapisac obiektu tekstury ({error})')
            continue
        key = obj.peek_name() or obj.path_id
        edits[key] = raw
        changed[name] = {'texture': name, 'width': slot['width'], 'height': slot['height'],
                         'mips': slot.get('mips', 1), 'format': format_name(slot['format']),
                         'slot': len(black), 'mode': 'inline', 'stream': '',
                         'already_black': before == black,
                         'bytes_changed': sum(1 for a, b in zip(before, black) if a != b)}
        if before == black:
            log(lines, f'   {name}: juz czarne — zostawiam')
    return edits, changed, problems


def _streams_of(plain: bytes, layout: dict) -> tuple[list[bytes], bytes]:
    """Strumienie bundla (indeks = wpis w tabeli plików) plus cały strumień 0.

    Ten sam podział co w `rebuild_plain`: strumień 0 jest plikiem serializowanym,
    reszta to `.resS` i inne poboczne pliki kontenera.
    """
    from lz4_block_map import decompress_blocks

    blob = b''.join(part[2] for part in decompress_blocks(plain, layout))
    return [blob[off:off + size] for off, size, _f, _n in layout['files']], blob


def _inline_pixels(blob: bytes, path_id: int) -> bytes | None:
    """Piksele tekstury trzymanej w obiekcie, czytane z przebudowanego pliku."""
    import UnityPy

    env = UnityPy.load(blob)
    for obj in env.objects:
        if obj.type.name != 'Texture2D' or obj.path_id != path_id:
            continue
        tree = obj.read_typetree()
        data = tree.get('image data') or b''
        return bytes(data) if isinstance(data, (bytes, bytearray)) \
            else bytes(int(byte) & 0xFF for byte in data)
    return None


def blacken(stem: str, plain: bytes, lines: list[str]) -> tuple[bytes, dict, list[str]]:
    """Wyczernia **wszystkie** nasze tekstury w jednym przebudowaniu bundla.

    v2 i v3 robiły to jedną teksturą na przebieg, więc v4 musiałaby przebudować
    i zapisać ten sam plik dwa razy — a drugi przebieg zobaczyłby piksele
    pierwszej zmiany. Tutaj obie zmiany idą do **jednego** `rebuild_plain`:
    strumieniowe przez podmianę slotów w strumieniach, inline przez nowe bajty
    obiektu tekstury. Potem sprawdzamy, czy to, co wróciło z przebudowy, nadal
    jest czarne — w tym samym trybie, w którym tekstura była zapisana.
    """
    from db_black import verify_black_chain
    from lz4_block_map import decompress_blocks, parse_container
    from srw_y_rebuild import objects_of, rebuild_plain

    layout = parse_container(plain)
    streams, blob = _streams_of(plain, layout)
    slots, problems = texture_slots(plain, layout, streams, lines)
    if not slots:
        return plain, {}, problems
    edits, inline, more = blacken_inline(slots, lines)
    problems += more
    new_streams, changed, more = blacken_streams(streams, slots, lines)
    problems += more
    changed.update(inline)
    if not changed:
        return plain, {}, problems
    stream_edits = {} if new_streams == streams else dict(enumerate(new_streams))
    new_plain, _report = rebuild_plain(stem, plain, edits, stream_edits)
    check_layout = parse_container(new_plain)
    check_streams, check_blob = _streams_of(new_plain, check_layout)

    # 1. każda zmieniona tekstura musi po przebudowie być czarna — jej własnym trybem
    for name, info in changed.items():
        slot = slots[name]
        if info['mode'] == 'stream':
            pixels = check_streams[slot['stream']][slot['offset']:slot['offset'] + slot['size']]
        else:
            pixels = _inline_pixels(check_blob, slot['path_id'])
            if pixels is None:
                raise ValueError(f'{stem}: po przebudowie nie ma tekstury {name} w obiekcie')
        verdict = verify_black_chain(slot['format'], pixels, slot['width'],
                                     slot['height'], slot.get('mips', 1))
        if verdict is False:
            raise ValueError(f'{stem}: po przebudowie piksele {name} nie sa czarne')
        info['black_verified'] = verdict is True

    # 2. nic poza naszymi teksturami nie ma prawa się zmienić
    before = objects_of(blob)
    after = objects_of(check_blob)
    if len(before) != len(after):
        raise ValueError(f'{stem}: liczba obiektow zmienila sie przy podmianie tekstur '
                         f'({len(before)} -> {len(after)})')
    allowed = {slot['path_id'] for name, slot in slots.items()
               if name in changed and changed[name]['mode'] == 'inline'}
    for (id_before, name_before, raw_before), (id_after, name_after, raw_after) \
            in zip(before, after):
        if id_before != id_after or name_before != name_after:
            raise ValueError(f'{stem}: kolejnosc obiektow zmienila sie przy '
                             f'{name_before} -> {name_after}')
        if raw_before == raw_after:
            continue
        if id_before not in allowed:
            raise ValueError(f'{stem}: {name_before} zmienil sie, choc nie mial')
    return new_plain, changed, problems


def candidates(streaming: Path, log_lines=None) -> list[Path]:
    """Awaryjnie: bundle, które wymieniają którąś z nazw — największe pierwsze.

    Chodzi po tysięcy plików i trwa minuty, więc włącza się tylko wtedy, gdy
    żaden plik z listy nie ma już tych tekstur (inna wersja gry, mod przebudował
    bundle). To jest jedyna droga, która nie zgaduje, gdzie mod położył obrazek.
    """
    wanted = [name.encode('ascii') for name in TEXTURES]
    found = []
    paths = sorted(p for p in streaming.rglob('*.bundle') if p.stat().st_size >= MIN_BUNDLE)
    for index, path in enumerate(paths, 1):
        if log_lines is not None and index % 500 == 0:
            log(log_lines, f'   przeszukane {index}/{len(paths)} plikow, trafien: {len(found)}')
        try:
            plain = plain_of(path)
        except (OSError, ValueError):
            continue
        if any(mentions(plain, name) for name in wanted):
            found.append(path)
    return sorted(found, key=lambda p: -p.stat().st_size)


def plan_bundles(streaming: Path, lines: list[str], scan: bool) -> list[Path]:
    """Które pliki brać do roboty: z listy, a gdy trzeba — z szukania po zawartości."""
    pinned = pinned_paths(streaming)
    if pinned:
        log(lines, f'W grze jest {len(pinned)} z {len(BUNDLES)} plikow z listy '
                   f'(spis tekstur z 1.4.0). Sprawdzam, ktore nadal maja nasze tekstury.')
        return pinned
    if not scan:
        raise ValueError(
            f'w grze nie ma zadnego z {len(BUNDLES)} plikow, ktore wedlug spisu tekstur '
            f'zawieraja {TEXTURES[0]} i {TEXTURES[1]} — pewnie mod 4K przebudowal bundle. '
            f'Uruchom PATCH_TLO5.bat jeszcze raz z opcja --skanuj: poszuka tekstur po '
            f'calej grze (potrwa kilka minut, ale nie zgaduje).')
    log(lines, 'Zadnego pliku z listy nie ma w grze — szukam tekstur po calej grze '
               '(to potrwa kilka minut)...')
    found = candidates(streaming, log_lines=lines)
    log(lines, f'Bundli, ktore wymieniaja ktoras z nazw: {len(found)}')
    return found


def install(game: Path, lines: list[str], scan: bool = False,
            dry_run: bool = False) -> dict:
    """Wyczernia obie tekstury we wszystkich bundlach, które je mają.

    `dry_run` (SPRAWDZ5.bat) liczy i raportuje dokładnie to samo, ale nie
    zapisuje ani bajtu — także nie tworzy kopii.
    """
    streaming = game / GAME_DATA / AA
    if not streaming.is_dir():
        raise ValueError(f'nie ma folderu {streaming}')
    paths = plan_bundles(streaming, lines, scan)
    if not paths:
        raise ValueError(f'nie znalazlem zadnego bundla z {TEXTURES[0]} ani '
                         f'{TEXTURES[1]} — gra ma inna wersje niz ta, z ktorej '
                         f'robilem spis? Wyslij mi RAPORT_TLO5.txt.')
    started = time.time()
    entries, skipped = [], []
    for index, path in enumerate(paths, 1):
        stem = path.name
        raw = path.read_bytes()
        before_hash = sha256(raw)
        plain = plain_of(path)
        names = [name for name in TEXTURES if mentions(plain, name.encode('ascii'))]
        if not names:
            skipped.append(f'{stem}: brak obu tekstur')
            log(lines, f'[{index}/{len(paths)}] {stem}: brak {"/".join(TEXTURES)} — pomijam')
            continue
        log(lines, f'[{index}/{len(paths)}] {stem}: wymienia {", ".join(names)}')
        try:
            new_plain, changed, problems = blacken(stem, plain, lines)
        except ValueError as error:
            skipped.append(f'{stem}: {error}')
            log(lines, f'   POMIJAM caly plik: {error}')
            continue
        for problem in problems:
            skipped.append(f'{stem}: {problem}')
            log(lines, f'   POMIJAM {problem}')
        for name, info in changed.items():
            note = '' if (info['width'], info['height']) == SIZE_140 else ' (rozmiar z moda)'
            where = 'w obiekcie' if info.get('mode') == 'inline' else \
                f'strumien {info.get("stream") or "?"}'
            log(lines, f'   OK {name}: {info["width"]}x{info["height"]} {info["format"]}{note}, '
                       f'{info.get("mips", 1)} mip., {where}, '
                       f'zmnienionych bajtow: {info["bytes_changed"]}')
        if not changed:
            skipped.append(f'{stem}: nie udalo sie wyczernic zadnej tekstury')
            continue
        if dry_run:
            entries.append({'bundle': str(path.relative_to(streaming)), 'path': str(path),
                            'dry_run': True, 'sha256_before': before_hash,
                            'textures': sorted(changed), 'info': changed})
            continue
        cipher = encrypt(stem, new_plain)
        if decrypt_bundle(stem, cipher) != new_plain:
            raise ValueError(f'{stem}: szyfrowanie nie odtwarza pliku')
        backup = path.parent / (path.name + BACKUP_SUFFIX)
        # Kopia tylko raz: jeśli leży tu kopia z v2/v3, trzyma **oryginał gry**
        # i musi zostać nietknięta — inaczej cofnięcie v4 cofnęłoby też mod.
        created = not backup.exists()
        if created:
            backup.write_bytes(raw)
        backup_hash = sha256(backup.read_bytes())
        path.write_bytes(cipher)
        after = path.read_bytes()
        if sha256(after) != sha256(cipher):
            raise ValueError(f'{stem}: zapisany plik nie zgadza sie z przebudowanym')
        if decrypt_bundle(stem, after) != new_plain:
            raise ValueError(f'{stem}: odczyt zapisanego pliku nie daje przebudowanego bundla')
        entries.append({'bundle': str(path.relative_to(streaming)), 'path': str(path),
                        'sha256_before': before_hash, 'sha256_after': sha256(after),
                        'sha256_backup': backup_hash,
                        'backup_from_earlier_pass': backup_hash != before_hash,
                        'backup_created_here': created,
                        'backup': str(backup), 'textures': sorted(changed), 'info': changed})
    if not entries:
        raise ValueError(f'zaden bundle nie ma {TEXTURES[0]} ani {TEXTURES[1]} — '
                         f'gra ma inna wersje niz ta, z ktorej robilem spis?')
    state = {'schema': 2, 'tool': 'tlo_bazy5', 'textures': list(TEXTURES),
             'size_140': list(SIZE_140), 'dry_run': dry_run,
             'when': time.strftime('%Y-%m-%d %H:%M:%S'), 'bundles': entries,
             'skipped': skipped}
    if not dry_run:
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf8')
    chained = sum(1 for entry in entries if entry.get('backup_from_earlier_pass'))
    if chained:
        log(lines, f'Kopie przy {chained} plikach pochodza ze starszej paczki (v2/v3). '
                   f'Trzymaja stan z tamtej chwili, wiec COFNIJ5.bat przywraca '
                   f'stan sprzed v4 dla pozostalych plikow, a dla tych — oryginal gry '
                   f'sprzed tamtej podmiany.')
    log(lines, f'{"SPRAWDZONE" if dry_run else "GOTOWE"}. Plikow: {len(entries)}. '
               f'Pominiete: {len(skipped)}. Czas: {time.time() - started:.0f} s.')
    return state


def restore(lines: list[str]) -> int:
    if not STATE.is_file():
        raise ValueError(f'nie ma pliku {STATE.name} — nie wiem, co przywrocic; '
                         f'uruchom ten plik z tego samego folderu, w ktorym robiles podmiane')
    state = json.loads(STATE.read_text(encoding='utf8'))
    if state.get('dry_run'):
        raise ValueError('STAN_TLO5.json pochodzi ze SPRAWDZ5.bat (nic nie zmieniono) — '
                         'nie ma czego cofac')
    restored = 0
    for entry in state['bundles']:
        path = Path(entry['path'])
        backup = Path(entry['backup'])
        if not backup.is_file():
            raise ValueError(f'brakuje kopii {backup} — nie ruszam {path}')
        data = backup.read_bytes()
        expected = entry.get('sha256_backup', entry['sha256_before'])
        if sha256(data) != expected:
            raise ValueError(f'kopia {backup} nie zgadza sie z zapisanym hashem — nie ruszam')
        path.write_bytes(data)
        if sha256(path.read_bytes()) != expected:
            raise ValueError(f'{path}: po przywroceniu hash sie nie zgadza')
        restored += 1
        log(lines, f'OK   przywrocono {entry["bundle"]}')
    state['restored'] = time.strftime('%Y-%m-%d %H:%M:%S')
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf8')
    log(lines, f'GOTOWE. Przywrocone bundle: {restored}.')
    return restored


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Tlo ekranu Database na czarno (v4, oba obrazy).')
    parser.add_argument('action', choices=('install', 'restore', 'check'))
    parser.add_argument('--game', type=Path, help='folder gry (ten z SUPER ROBOT WARS Y.exe)')
    parser.add_argument('--skanuj', action='store_true',
                        help='gdy lista plikow nie pasuje: szukaj tekstur po calej grze')
    args = parser.parse_args(argv)
    lines: list[str] = []
    started = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        check_game_stopped()
        if args.action == 'restore':
            count = restore(lines)
            result = 0 if count else 0
        else:
            game = args.game or find_game()
            state = install(game, lines, scan=args.skanuj, dry_run=args.action == 'check')
            result = 0 if state['bundles'] else 1
    except (OSError, ValueError) as exc:
        log(lines, f'BLAD: {exc}')
        result = 1
    header = [f'# SRW Y - tlo ekranu Database v4 ({started})',
              f'# akcja: {args.action}{" + skanuj" if args.skanuj else ""}',
              f'# wynik: {"OK" if result == 0 else "BLAD"}', '']
    REPORT.write_text('\n'.join(header + lines) + '\n', encoding='utf8')
    print(f'Szczegoly: {REPORT}')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
