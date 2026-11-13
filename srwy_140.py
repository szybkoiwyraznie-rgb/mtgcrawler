"""SRWY 4K Resolution Patcher - native 4K resolutions, upscaled-background fixes and matching menu labels
for SUPER ROBOT WARS Y (Steam, game version 1.4.0).

Run it with no arguments for the window, or from a console:
  srwy_140.py --game-dir "L:\\SteamLibrary\\steamapps\\common\\SRWY"                       patch the game in place (originals saved as .orig)
  srwy_140.py --game-dir ... --mo2-mods "C:\\Modding\\MO2\\mods" [--mod-name "SRWY 4K Resolution Patcher"]    write an MO2 mod instead; the game is not touched
  add --check for a dry run, --revert to undo (in place: restore .orig; MO2: delete the mod folder yourself)
  add --only resolution battle story labels   to apply just some of the parts; --langs en-US ja-JP ko-KR zh-TW zh-HK zh-CN   to pick language bundles

Parts
  resolution  resolution list 3840x2160 / 2560x1440 / 1920x1080 / 1280x720.  global-metadata.dat + GameAssembly.dll
  battle      battle-event backgrounds: parallax (IC*) scrolling speed compensation for upscaled images.  GameAssembly.dll
  story       story-scene backgrounds that are 2x / 4x upscaled are recognised.  GameAssembly.dll
  labels      the four resolution names in the language bundles (system_text_*; one per language, selectable) so the menu shows the new list.
              Re-packed with the game's own layout (128 KB LZ4HC chunks), so the files stay the same size.

Every patch site is verified against the expected original bytes before anything is written; on another game build the
installer stops and changes nothing.  This edits copies of your own game files; nothing from the game is distributed.

This build is the 1.4.0 variant: the addresses and expected original bytes are the ones from the 1.4.0 GameAssembly.dll.
"""
import argparse
import hashlib
import os
import queue
import re
import shutil
import stat
import struct
import sys
import threading
from pathlib import Path

VERSION = "1.0.0-140"
PARTS = ("resolution", "battle", "story", "labels")

OLD_TABLES = (
    (1920, 1200, 1920, 1080, 1280, 800, 1280, 720),
    (3840, 2160, 1920, 1080, 2560, 1440, 1280, 720),
)
NEW_TABLE = (3840, 2160, 2560, 1440, 1920, 1080, 1280, 720)

LABELS = {
    "3840x2160": 43502921075175444,
    "2560x1440": 43502921075175445,
    "1920x1080": 43502921075175446,
    "1280x720": 51060338918539264,
}

RESOLUTION_PATCHES = (
    (
        'shared routine BestFit (rewrites dead CheckBordlessResolution body)',
        0x93f09a,
        (
            "803d826ba803007513488d0d3e2f8603e821bda6ffc6056d6ba803010f57c0488d4c243033d20f11442420e8e640"
            "7a0233d2488d4c24200f10000f11442420e8d270780233d2488d4c24308bf8e8c4407a0233d2488d4c24200f1000"
            "0f11442420e8c0d0ce004c8b05e12e86038bd84183b8e000000000750f498bc8e815c0a6ff4c8b05c62e8603498b"
            "88b8000000488b114885d2744d488b4210833801764a488b481085c97442498b80b8000000448b4c8a20488b0848"
            "8b4110488b501083fa017626413bf97c0bb8010000003b5c91247d05b803000000"
        ),
        (
            "89cf89d3803d7e6ba803007513488d0d3a2f8603e81dbda6ffc605696ba803014c8b05272f86034183b8e0000000"
            "00750f4c89c1e85dc0a6ff4c8b050e2f8603498b88b8000000488b114885d20f8491000000488b42108b08448b40"
            "1031c039c873194189c1450fafc8423b7c8a207c07423b5c8a247d07ffc0ebe38d41ff4189c1450fafc8468b548a"
            "20468b448a244489d2eb44cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
        ),
    ),
    (
        'menu: borderless uses best-fit row',
        0x93d4c8,
        (
            "4c8b05194b86038bf84183b8e000000000750f498bc8e84ddca6ff4c8b05fe4a8603498b88b8000000488b114885"
            "d20f84fd000000488b421039300f86eb000000488b481085c90f84df000000498b80b8000000448b4c8a20488b08"
            "488b4110488b50103bd60f86c0000000413be97c063b7c91247d05be03000000"
        ),
        (
            "89c789e989fae8bd1b000089c6eb6dcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
        ),
    ),
    (
        'startup: borderless uses best-fit row',
        0xcba1e0,
        (
            "488b0d017e4e03bd0100000083b9e000000000750ce8360f6fff488b0de77d4e03488b81b8000000488974245048"
            "897c2458488b104885d20f843a010000488b421039280f8634010000488b701085f60f8428010000488b81b80000"
            "008b74b220488b38488b4710488b48103bcd0f860a0100008b7c8f24443bfe7c1e443bf77c19488b0d3f6a470345"
            "33c0ba07000000e8faaa75ffe988000000488b0db6f24d034533c0ba07000000e8e1aa75ff488b0d527d4e03bd03"
            "00000083b9e000000000750ce8870e6fff488b0d387d4e03488b81b8000000488b104885d20f8495000000488b42"
            "1039280f868f0000004c8b40104585c00f84820000004b8d04408b748220488b81b8000000488b38488b4710488b"
            "481083f9017663488d04498b7c8724"
        ),
        (
            "488974245048897c24584489f94489f2e82b46c8ff89c589d64489c7e902010000cccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccc"
        ),
    ),
    (
        'display-change observer: borderless uses best-fit row',
        0x80ba97,
        (
            "488b0d4a65990341be0100000083b9e000000000750ce87ef6b9ff488b0d2f659903488b81b800000048895c2450"
            "48897c2458488b104885d20f8419010000488b42104439300f8612010000488b781085ff0f8406010000488b81b8"
            "0000008b7cba20488b18488b4310488b4810413bce0f86e70000008b5c8b24443bff7c1a3beb7c16488b0d865192"
            "034533c0ba07000000e84192c0ffeb7e488b0d00da98034533c0ba07000000e82b92c0ff488b0d9c64990341be03"
            "00000083b9e000000000750ce8d0f5b9ff488b0d81649903488b81b8000000488b104885d27479488b4210443930"
            "76764c8b40104585c0746d4b8d04408b7c8220488b81b8000000488b18488b4310488b481083f901764e488d0449"
            "8b5c8324"
        ),
        (
            "48895c245048897c24584489f989eae8e53513004189c689d74489c3e9f7000000cccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            "cccccccc"
        ),
    ),
    (
        'default resolution index 1->2 (1080p in sorted table)',
        0xcba834,
        (
            "c7474c01000000"
        ),
        (
            "c7474c02000000"
        ),
    ),
    (
        'observer exclusive-fullscreen fallback index 1->2',
        0x80c36b,
        (
            "41b901000000"
        ),
        (
            "41b902000000"
        ),
    ),
)

SCROLL_PATCHES = (
    (
        'scroll fix cave (standalone ImageBB.SetScrollSpeed) in unused debug helper',
        0x93f530,
        (
            "48895c24084889742410574883ec50803dde66a80300488bf10f297424407537488d0d912a8603e874b8a6ff488d"
            "0d75ed8203e868b8a6ff488d0d69947e03e85cb8a6ff488d0d2de98703e850b8a6ffc6059d"
        ),
        (
            "4889442430f30f109318010000488b8be00000004885c97429f30f1154243831d2e82a837f02f30f10542438b800"
            "00c842660f6ec80f2ec17608f30f59d1f30f5ed0488b44243080bb2001000000e9d80bdfff"
        ),
    ),
    (
        'scroll fix hook: standalone ImageBB.SetScrollSpeed divides _ScrollSpeed by sprite PPU/100',
        0x73014c,
        (
            "80bb2001000000f30f109318010000"
        ),
        (
            "e9dff32000cccccccccccccccccccc"
        ),
    ),
    (
        'scroll fix cave (inlined copy in ImageBB.Start (the one that actually runs)) in unused debug helper',
        0x93f5a0,
        (
            "1030e8d9aca6ff488b0d2a947e03488d542420488bd8660f7f742420e81faca6ff488bf84885db0f84fc00000048"
            "85c07418488b13488bc8488b5240e83faca6ff4885c00f84bd000000837b18000f86c30000"
        ),
        (
            "4889442420f30f109618010000488b8ee00000004885c97429f30f1154242831d2e8ba827f02f30f10542428b800"
            "00c842660f6ec80f2ec17608f30f59d1f30f5ed0488b44242080be2001000000e9b10fdfff"
        ),
    ),
    (
        'scroll fix hook: inlined copy in ImageBB.Start (the one that actually runs) divides _ScrollSpeed by sprite PPU/100',
        0x730595,
        (
            "80be2001000000f30f109618010000"
        ),
        (
            "e906f02000cccccccccccccccccccc"
        ),
    ),
)

LABEL_IDS = (43502921075175444, 43502921075175445, 43502921075175446, 51060338918539264)
LABEL_TEXT = tuple("%d%%s%d" % (NEW_TABLE[2 * i], NEW_TABLE[2 * i + 1]) for i in range(4))

LANGS = (
    ("en-US", "English", "2d69c099bfdf0e252dabe84dbbba11df", "english"),
    ("ja-JP", "Japanese", "1cc7e02ee5711c6ba87a0e364f62198c", "japanese"),
    ("ko-KR", "Korean", "ed627a03795dfcb030816d400d5e938a", "koreana"),
    ("zh-TW", "Traditional Chinese (TW)", "eea326a022bba60eaf9ae99ddaf870d0", "tchinese"),
    ("zh-HK", "Traditional Chinese (HK)", "8f7e5f08f5249593062389d15def916d", ""),
    ("zh-CN", "Simplified Chinese", "febc49b382923c22b1fdd69a9b7a9fb8", "schinese"),
)

LANG_STEMS = (
    "2d69c099bfdf0e252dabe84dbbba11df",
    "1cc7e02ee5711c6ba87a0e364f62198c",
    "8f7e5f08f5249593062389d15def916d",
    "ed627a03795dfcb030816d400d5e938a",
    "eea326a022bba60eaf9ae99ddaf870d0",
    "febc49b382923c22b1fdd69a9b7a9fb8",
)

DLL_REL = "GameAssembly.dll"

GROUPS = {
    "resolution": RESOLUTION_PATCHES,
    "battle": SCROLL_PATCHES,
}

CAVE_LEN_MAX = 112


def build_cave(cave_rva: int, back_rva: int) -> bytes:
    code = bytearray()
    code += bytes.fromhex("F30F104728")          # movss xmm0, [rdi + 0x28]   sprite width
    code += bytes.fromhex("F30F104F2C")          # movss xmm1, [rdi + 0x2c]   sprite height
    code += bytes.fromhex("0F28D0")              # movaps xmm2, xmm0
    i_a = len(code)
    code += bytes.fromhex("F30F5E15") + b"\x00\x00\x00\x00"   # divss xmm2, [rip + 1920.0]
    code += bytes.fromhex("0F28D9")              # movaps xmm3, xmm1
    i_b = len(code)
    code += bytes.fromhex("F30F5E1D") + b"\x00\x00\x00\x00"   # divss xmm3, [rip + 1080.0]
    code += bytes.fromhex("F30F5DD3")            # minss xmm2, xmm3
    i_c = len(code)
    code += bytes.fromhex("F30F5F15") + b"\x00\x00\x00\x00"   # maxss xmm2, [rip + 1.0]
    code += bytes.fromhex("F30F5EC2")            # divss xmm0, xmm2
    code += bytes.fromhex("F30F5ECA")            # mulss xmm1, xmm2
    code += bytes.fromhex("F30F2DC0")            # cvttss2si eax, xmm0
    code += bytes.fromhex("F30F2AC0")            # cvtsi2ss xmm0, eax
    code += bytes.fromhex("F30F2DC1")            # cvttss2si eax, xmm1
    code += bytes.fromhex("F30F2AC8")            # cvtsi2ss xmm1, eax
    code += bytes.fromhex("F30F114728")          # movss [rdi + 0x28], xmm0
    code += bytes.fromhex("F30F114F2C")          # movss [rdi + 0x2c], xmm1
    code += bytes.fromhex("F30F2C4728")          # cvttss2si eax, [rdi + 0x28]
    i_j = len(code)
    code += b"\xe9\x00\x00\x00\x00"              # jmp back
    while len(code) % 4:
        code += b"\xcc"
    k1920 = len(code)
    code += struct.pack("<f", 1920.0)
    k1080 = len(code)
    code += struct.pack("<f", 1080.0)
    k1 = len(code)
    code += struct.pack("<f", 1.0)
    for at, k in ((i_a, k1920), (i_b, k1080), (i_c, k1)):
        struct.pack_into("<i", code, at + 4, k - (at + 8))
    struct.pack_into("<i", code, i_j + 1, back_rva - (cave_rva + i_j + 5))
    return bytes(code)


SIGNATURE = re.compile(
    b"\\xF3\\x0F\\x2C\\x47\\x28\\x33\\xDB\\x48\\x89\\x5F\\x30\\x3D\\x80\\x07\\x00\\x00\\x0F\\x85...."
    b"\\xF3\\x0F\\x2C\\x47\\x2C\\x3D\\x38\\x04\\x00\\x00\\x0F\\x85....",
    re.S,
)
ORIGINAL_5 = bytes.fromhex("F30F2C4728")
PATCHED_SIG = re.compile(
    b"\\xE9....\\x33\\xDB\\x48\\x89\\x5F\\x30\\x3D\\x80\\x07\\x00\\x00\\x0F\\x85...."
    b"\\xF3\\x0F\\x2C\\x47\\x2C\\x3D\\x38\\x04\\x00\\x00\\x0F\\x85....",
    re.S,
)

PLUGIN_NAME = "game_superrobotwarsy.py"
PLUGIN_SRC = """
import os

from ..basic_game import BasicGame
from ..basic_features import BasicModDataChecker, GlobPatterns
import mobase


class SuperRobotWarsYGame(BasicGame):
    Name = "Super Robot Wars Y Support Plugin"
    Author = "Asterra"
    Version = "1.2.0"

    GameName = "Super Robot Wars Y"
    GameShortName = "srwy"
    GameNexusName = "superrobotwarsy"  # nexusmods.com/games/superrobotwarsy
    GameNexusId = 10044
    GameSteamId = 1909950

    GameBinary = "SUPER ROBOT WARS Y.exe"
    GameDataPath = ""

    # Saves live in <user-id> subfolders under here (the %LOCALAPPDATA% location; some sources say %APPDATA%)
    GameSavesDirectory = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "BANDAI NAMCO Entertainment",
        "SUPER ROBOT WARS Y",
        "Saved",
        "SaveGames",
    )

    def init(self, organizer: mobase.IOrganizer) -> bool:
        if not super().init(organizer):
            return False

        self._register_feature(
            BasicModDataChecker(
                GlobPatterns(
                    valid=[
                        # Game data (bundles, metadata, ...)
                        "SUPER ROBOT WARS Y_Data",
                        # Native game libraries sitting next to the exe - SRWY 4K Resolution Patcher
                        # writes a patched GameAssembly.dll here
                        "GameAssembly.dll",
                        "UnityPlayer.dll",
                        # MelonLoader-style mods
                        "Mods",
                        "Plugins",
                        "UserLibs",
                        "UserData",
                        "MelonLoader",
                        "version.dll",
                    ],
                )
            )
        )

        return True
"""


class PE:
    def __init__(self, data: bytearray):
        self.d = data
        if data[:2] != b"MZ":
            raise SystemExit("not a PE file")
        pe = struct.unpack_from("<I", data, 60)[0]
        if data[pe:pe + 4] != b"PE\x00\x00":
            raise SystemExit("bad PE header")
        (nsec,) = struct.unpack_from("<H", data, pe + 6)
        (optsz,) = struct.unpack_from("<H", data, pe + 20)
        if struct.unpack_from("<H", data, pe + 24)[0] != 523:
            raise SystemExit("this is not a 64-bit DLL")
        self.sections = []
        base = pe + 24 + optsz
        for i in range(nsec):
            o = base + 40 * i
            name = bytes(data[o:o + 8]).rstrip(b"\x00").decode("latin1")
            vsize, va, rsize, rptr = struct.unpack_from("<IIII", data, o + 8)
            self.sections.append(dict(name=name, hdr=o, vsize=vsize, va=va, rsize=rsize, rptr=rptr))

    def sec_of_off(self, off):
        for s in self.sections:
            if s["rptr"] <= off < s["rptr"] + s["rsize"]:
                return s
        return None

    def off2rva(self, off):
        s = self.sec_of_off(off)
        return s["va"] + (off - s["rptr"])

    def rva2off(self, rva):
        for s in self.sections:
            if s["va"] <= rva < s["va"] + max(s["vsize"], s["rsize"]):
                return s["rptr"] + (rva - s["va"])
        raise SystemExit("RVA %#x not in any section" % rva)

    def set_vsize(self, sec, value):
        struct.pack_into("<I", self.d, sec["hdr"] + 8, value)
        sec["vsize"] = value


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class Problem(Exception):
    pass


def story_state(data):
    """('todo'|'done', file offset) or raise Problem."""
    patched_sig = re.compile(
        b"\\xE9....\\x33\\xDB\\x48\\x89\\x5F\\x30\\x3D\\x80\\x07\\x00\\x00\\x0F\\x85...."
        b"\\xF3\\x0F\\x2C\\x47\\x2C\\x3D\\x38\\x04\\x00\\x00\\x0F\\x85....",
        re.S,
    )
    m1 = [m.start() for m in SIGNATURE.finditer(bytes(data))]
    m2 = [m.start() for m in patched_sig.finditer(bytes(data))]
    if len(m1) == 1 and not m2:
        return "todo", m1[0]
    if len(m2) == 1 and not m1:
        return "done", m2[0]
    raise Problem(
        "the story-background code was not found exactly once (%d/%d matches) - different game build?"
        % (len(m1), len(m2))
    )


def dll_plan(data, parts):
    """Check every site; return ({part: 'todo'|'done'}, list of (offset, bytes)). Nothing is modified."""
    pe = PE(data)
    state, writes = {}, []
    for g in ("resolution", "battle"):
        if g not in parts:
            continue
        todo, done = [], 0
        for name, rva, old_hex, new_hex in GROUPS[g]:
            old, new = bytes.fromhex(old_hex), bytes.fromhex(new_hex)
            o = pe.rva2off(rva)
            cur = bytes(data[o:o + len(old)])
            if cur == new:
                done += 1
                continue
            if cur == old:
                todo.append((o, new))
                continue
            raise Problem(
                "[%s] unexpected bytes at RVA 0x%X (%s): not the game build these patches were made for"
                % (g, rva, name)
            )
        if done == len(GROUPS[g]):
            state[g] = "done"
        elif done:
            raise Problem("[%s] is only partly applied - restore the .orig backup first" % g)
        else:
            state[g] = "todo"
            writes += todo
    if "story" in parts:
        st, off = story_state(data)
        state["story"] = st
    return state, writes


def dll_apply(data, parts):
    """Return (new bytes, state). Raises Problem before changing anything if a check fails."""
    data = bytearray(data)
    state, writes = dll_plan(data, parts)
    for o, new in writes:
        data[o:o + len(new)] = new
    if state.get("story") == "todo":
        pe = PE(data)
        _, hook_off = story_state(data)
        hook_rva = pe.off2rva(hook_off)
        text = next(s for s in pe.sections if s["name"] == ".text")
        cave_rva = (text["va"] + text["vsize"] + 15) & -16
        cave_off = pe.rva2off(cave_rva)
        room = text["rptr"] + text["rsize"] - cave_off
        cave = build_cave(cave_rva, hook_rva + 5)
        if room < len(cave) or any(data[cave_off:cave_off + len(cave)]):
            raise Problem("[story] no free space at the end of .text for the routine")
        new_vsize = (cave_rva - text["va"] + len(cave) + 15) & -16
        if new_vsize > text["rsize"]:
            raise Problem("[story] section would grow past its on-disk size")
        data[cave_off:cave_off + len(cave)] = cave
        data[hook_off:hook_off + 5] = b"\xe9" + struct.pack("<i", cave_rva - (hook_rva + 5))
        pe.set_vsize(text, new_vsize)
    return bytes(data), state


def pack_table(t):
    return struct.pack("<8i", *t)


def meta_apply(data):
    """Return (new bytes, 'todo'|'done')."""
    new = pack_table(NEW_TABLE)
    if data.count(new) == 1:
        return data, "done"
    for t in OLD_TABLES:
        old = pack_table(t)
        if data.count(old) == 1:
            o = data.find(old)
            return data[:o] + new + data[o + 32:], "todo"
    raise Problem("resolution table not found exactly once in global-metadata.dat - different game build?")


def _cs(d, p):
    e = d.index(b"\x00", p)
    return d[p:e].decode(), e + 1


def unityfs_read(data):
    """Return dict(platform, engine, node_name, cab). Handles the layout Unity 2022 writes (LZ4/LZ4HC or none)."""
    import lz4.block as lz4

    if data[:8] != b"UnityFS\x00":
        raise Problem("not a UnityFS bundle")
    p = 8
    ver = struct.unpack_from(">I", data, p)[0]
    p += 4
    plat, p = _cs(data, p)
    engine, p = _cs(data, p)
    size, cbi, ubi, flags = struct.unpack_from(">qIII", data, p)
    p += 20
    if ver >= 7:
        p = (p + 15) & -16
    info_off = len(data) - cbi if flags & 128 else p
    blob = data[info_off:info_off + cbi]
    comp = flags & 63
    if comp == 0:
        info = blob
    elif comp in (2, 3):
        info = lz4.decompress(blob, uncompressed_size=ubi)
    else:
        info = None
    if info is None:
        raise Problem("unsupported bundle compression %d" % comp)
    q = 16
    nb = struct.unpack_from(">I", info, q)[0]
    q += 4
    blocks = []
    for _ in range(nb):
        us, cz, fl = struct.unpack_from(">IIH", info, q)
        q += 10
        blocks.append((us, cz, fl))
    nn = struct.unpack_from(">I", info, q)[0]
    q += 4
    if nn != 1:
        raise Problem("bundle has %d files inside, expected 1" % nn)
    off, sz, fl = struct.unpack_from(">qqI", info, q)
    q += 20
    name, q = _cs(info, q)
    dstart = info_off + (0 if flags & 128 else cbi)
    if flags & 512:
        dstart = (dstart + 15) & -16
    pos, out = dstart, bytearray()
    for us, cz, fl2 in blocks:
        c = data[pos:pos + cz]
        pos += cz
        t = fl2 & 63
        if t == 0:
            out += c
        elif t in (2, 3):
            out += lz4.decompress(c, uncompressed_size=us)
        else:
            out += b""
    return dict(platform=plat, engine=engine, node=name, cab=bytes(out))


def unityfs_pack(cab_name, cab, engine="5.x.x", platform="", block=131072, level=12):
    """Write a bundle the way the game's own build does: 128 KB LZ4HC chunks, LZ4HC block table."""
    import lz4.block as lz4

    blocks, payload = [], bytearray()
    for i in range(0, len(cab), block):
        raw = cab[i:i + block]
        c = lz4.compress(raw, mode="high_compression", compression=level, store_size=False)
        if len(c) < len(raw):
            blocks.append((len(raw), len(c), 3))
            payload += c
        else:
            blocks.append((len(raw), len(raw), 0))
            payload += raw
    info = bytearray(16)
    info += struct.pack(">I", len(blocks))
    for us, cz, fl in blocks:
        info += struct.pack(">IIH", us, cz, fl)
    info += struct.pack(">I", 1) + struct.pack(">qqI", 0, len(cab), 4) + cab_name.encode() + b"\x00"
    cinfo = lz4.compress(bytes(info), mode="high_compression", compression=level, store_size=False)

    def header(total):
        return (
            b"UnityFS\x00"
            + struct.pack(">I", 8)
            + platform.encode() + b"\x00"
            + engine.encode() + b"\x00"
            + struct.pack(">qIII", total, len(cinfo), len(info), 579)
        )

    start = (len(header(0)) + 15) & -16
    dstart = (start + len(cinfo) + 15) & -16
    out = bytearray(header(dstart + len(payload)))
    out += b"\x00" * (start - len(out))
    out += cinfo
    out += b"\x00" * (dstart - len(out))
    out += payload
    return bytes(out)


LABEL_RE = re.compile(b"(\\d{3,4})(x|\\xc3\\x97)(\\d{3,4})$")


def _types_end(c):
    p = c.index(b"\x00", 48) + 1 + 4
    tree = c[p]
    p += 1
    n = struct.unpack_from("<i", c, p)[0]
    p += 4
    for _ in range(n):
        cid = struct.unpack_from("<i", c, p)[0]
        p += 7
        if cid == 114 or cid < 0:
            p += 16
        p += 16
        if not tree:
            continue
        nc, sb = struct.unpack_from("<ii", c, p)
        p += 8 + nc * 32 + sb
        p += 4 + 4 * struct.unpack_from("<i", c, p)[0]
    return p


def edit_serialized(c):
    """Rewrite the four resolution labels inside the string-table object. Only that object's bytes change; objects after
    it are moved by the (8-byte aligned) size difference and the object table / file size are updated to match.
    Returns (new bytes or None, 'todo'|'done'|'skip')."""
    if struct.unpack_from(">I", c, 8)[0] != 22 or c[16] != 0:
        raise Problem("unsupported SerializedFile version")
    file_size, data_off = struct.unpack_from(">qq", c, 24)
    p = _types_end(c)
    count = struct.unpack_from("<i", c, p)[0]
    p += 4
    objs = []
    for _ in range(count):
        p = (p + 3) & -4
        pid, start, size, tid = struct.unpack_from("<qqIi", c, p)
        objs.append([p, start, size])
        p += 24
    keys = [struct.pack("<q", i) for i in LABEL_IDS]
    target = None
    for ent, start, size in objs:
        body = c[data_off + start:data_off + start + size]
        if not all(k in body for k in keys):
            continue
        if target is not None:
            raise Problem("more than one object holds the resolution labels")
        target = (ent, start, size, body)
    if target is None:
        return None, "skip"
    ent, start, size, body = target
    new_body, pos, changed = bytearray(), 0, 0
    spans = []
    for i, k in enumerate(keys):
        hits = [m.start() for m in re.finditer(re.escape(k), body)]
        good = []
        for h in hits:
            n = struct.unpack_from("<i", body, h + 8)[0]
            if 0 < n < 24 and LABEL_RE.match(body[h + 12:h + 12 + n]):
                good.append((h, n))
        if len(good) != 1:
            raise Problem("label %d not found exactly once (%d)" % (i + 1, len(good)))
        spans.append((good[0][0], good[0][1], i))
    spans.sort()
    for h, n, i in spans:
        old = bytes(body[h + 12:h + 12 + n])
        sep = "\u00d7" if b"\xc3\x97" in old else "x"
        new = (LABEL_TEXT[i] % sep).encode("utf-8")
        field_end = h + 12 + ((n + 3) & -4)
        new_body += body[pos:h + 8] + struct.pack("<i", len(new)) + new
        new_body += b"\x00" * (((len(new) + 3) & -4) - len(new))
        pos = field_end
        if new != old:
            changed += 1
    new_body += body[pos:]
    if changed == 0:
        return None, "done"
    new_body = bytes(new_body)
    later = [o for o in objs if o[1] > start]
    if not later:
        raise Problem("string-table object is the last object; unexpected layout")
    next_old = min(o[1] for o in later)
    if next_old != (start + size + 7) & -8:
        raise Problem("unexpected padding after the string-table object")
    next_new = (start + len(new_body) + 7) & -8
    shift = next_new - next_old
    out = bytearray(c[:data_off + start])
    out += new_body
    out += b"\x00" * (next_new - start - len(new_body))
    out += c[data_off + next_old:]
    struct.pack_into("<I", out, ent + 16, len(new_body))
    for o in later:
        struct.pack_into("<q", out, o[0] + 8, o[1] + shift)
    struct.pack_into(">q", out, 24, file_size + shift)
    return bytes(out), "todo"


def _bundle_key(stem):
    v = hashlib.sha1(b"ComBBStudioSRTeam" + stem.encode()).digest()
    for _ in range(99):
        v = hashlib.sha1(v).digest()
    return v[:16]


def bundle_xor(data, stem):
    """The game's bundle cipher (AES-128 counter keystream XOR) - symmetric: encrypts and decrypts."""
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        raise Problem("the 'cryptography' Python package is needed for the game's encrypted bundles (pip install cryptography)")
    aes = Cipher(algorithms.AES(_bundle_key(stem)), modes.ECB()).encryptor()
    out = bytearray()
    ctr, CH = 1, 1048576
    for i in range(0, len(data), CH):
        ch = data[i:i + CH]
        n = (len(ch) + 15) // 16
        ks = aes.update(b"".join(struct.pack("<QQ", ctr + j, 0) for j in range(n)))
        ctr += n
        out += (
            int.from_bytes(ch, "little") ^ int.from_bytes(ks[:len(ch)], "little")
        ).to_bytes(len(ch), "little")
    return bytes(out)


def bundle_looks_ours(head, stem):
    """Cheap check on the first bytes: plain UnityFS or encrypted UnityFS."""
    return head[:8] == b"UnityFS\x00" or bundle_xor(head[:64], stem)[:8] == b"UnityFS\x00"


def bundle_apply(data, stem):
    """Return (new bundle bytes or None, 'todo'|'done'|'skip'). Handles encrypted and plain bundles; output keeps the input's form."""
    if len(data) > 8388608:
        return None, "skip"
    enc = data[:8] != b"UnityFS\x00"
    if enc:
        data = bundle_xor(data, stem)
        if data[:8] != b"UnityFS\x00":
            return None, "skip"
    try:
        info = unityfs_read(data)
        if b"system_text_" not in info["cab"]:
            return None, "skip"
        new_cab, state = edit_serialized(info["cab"])
        if state != "todo":
            return None, state
        new = unityfs_pack(info["node"], new_cab, info["engine"], info["platform"])
        return (bundle_xor(new, stem) if enc else new), "todo"
    except Exception:
        return None, "skip"


def find_steam_game():
    cands = []
    try:
        import winreg

        for hive, key, val in (
            (winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam", "SteamPath"),
            (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam", "InstallPath"),
        ):
            try:
                with winreg.OpenKey(hive, key) as k:
                    cands.append(Path(winreg.QueryValueEx(k, val)[0]))
            except OSError:
                pass
    except ImportError:
        pass
    for d in ("C:/Program Files (x86)/Steam", "C:/Program Files/Steam"):
        cands.append(Path(d))
    libs = []
    for c in cands:
        libs.append(c)
        vdf = c / "steamapps" / "libraryfolders.vdf"
        if not vdf.exists():
            continue
        try:
            for m in re.finditer('"path"\\s+"([^"]+)"', vdf.read_text(encoding="utf-8", errors="replace")):
                libs.append(Path(m.group(1).replace("\\\\", "\\")))
        except OSError:
            pass
    for lib in libs:
        common = lib / "steamapps" / "common"
        if not common.is_dir():
            continue
        for d in common.iterdir():
            if (d / "SUPER ROBOT WARS Y.exe").exists():
                return d
    return None


def detect_language(game):
    """The Steam language code that is set for this game (from its appmanifest), or None if it cannot be told."""
    game = Path(game)
    try:
        steamapps = game.parent.parent
        for mf in steamapps.glob("appmanifest_*.acf"):
            t = mf.read_text(encoding="utf-8", errors="replace")
            m = re.search('"installdir"\\s+"([^"]+)"', t)
            if not m or m.group(1).lower() != game.name.lower():
                continue
            l = re.search('"language"\\s+"([^"]*)"', t)
            for code, _, _, steam in LANGS:
                if l and steam and l.group(1).lower() == steam:
                    return code
    except OSError:
        return None
    return None


def _ini_value(text, key):
    m = re.search("^%s\\s*=\\s*(.*?)\\s*$" % re.escape(key), text, re.M | re.I)
    if not m:
        return None
    v = m.group(1)
    mb = re.match("@ByteArray\\((.*)\\)$", v)
    return (mb.group(1) if mb else v).replace("\\\\", "\\")


def mods_dir_from_ini(text, base):
    """MO2 'mods' folder from a ModOrganizer.ini text; base = the instance's base folder."""
    b = _ini_value(text, "base_directory") or str(base)
    m = _ini_value(text, "mod_directory")
    m = m.replace("%BASE_DIR%", b) if m else os.path.join(b, "mods")
    return os.path.normpath(m)


def detect_mo2(game):
    """If this program was started from inside Mod Organizer 2 (Windows: its virtual-file-system DLL is loaded), return its
    'mods' folder (or '' if that cannot be worked out); otherwise None.  Everything here is best-effort."""
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.windll.kernel32
        ctypes.c_void_p
        k.GetModuleHandleW.restype = ctypes.c_void_p
        if not (k.GetModuleHandleW("usvfs_x64.dll") or k.GetModuleHandleW("usvfs_x86.dll")):
            return None
        mods = ""
        try:
            class PE(ctypes.Structure):
                _fields_ = [
                    ("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260),
                ]

            k.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
            snap = k.CreateToolhelp32Snapshot(2, 0)
            procs = {}
            pe = PE()
            pe.dwSize = ctypes.sizeof(PE)
            ok = k.Process32FirstW(ctypes.c_void_p(snap), ctypes.byref(pe))
            while ok:
                procs[pe.th32ProcessID] = (pe.th32ParentProcessID, pe.szExeFile)
                ok = k.Process32NextW(ctypes.c_void_p(snap), ctypes.byref(pe))
            k.CloseHandle(ctypes.c_void_p(snap))
            pid, exe = os.getpid(), None
            for _ in range(6):
                pid = procs.get(pid, (0, ""))[0]
                if not pid:
                    break
                if procs.get(pid, (0, ""))[1].lower() == "modorganizer.exe":
                    k.OpenProcess.restype = ctypes.c_void_p
                    h = k.OpenProcess(4096, False, pid)
                    buf = ctypes.create_unicode_buffer(1024)
                    n = wintypes.DWORD(1024)
                    if h and k.QueryFullProcessImageNameW(ctypes.c_void_p(h), 0, buf, ctypes.byref(n)):
                        exe = Path(buf.value)
                    if h:
                        k.CloseHandle(ctypes.c_void_p(h))
                    break
        except Exception:
            exe = None
        if exe:
            inis = []
            if (exe.parent / "ModOrganizer.ini").is_file():
                inis.append((exe.parent / "ModOrganizer.ini", exe.parent))
            local = os.environ.get("LOCALAPPDATA")
            if local:
                inis += [(i, i.parent) for i in sorted(Path(local / "ModOrganizer").glob("*/ModOrganizer.ini"))]
            pick = None
            for ini, base in inis:
                t = ini.read_text(encoding="utf-8", errors="replace")
                gp = _ini_value(t, "gamePath")
                if game and gp and os.path.normcase(os.path.normpath(gp)) == os.path.normcase(os.path.normpath(str(game))):
                    pick = (t, base)
                    break
                if pick is None:
                    pick = (t, base)
            if pick:
                mods = mods_dir_from_ini(*pick)
        if not mods or not os.path.isdir(mods):
            if exe and (exe.parent / "mods").is_dir():
                mods = str(exe.parent / "mods")
    except Exception:
        return None
    return mods if mods and os.path.isdir(mods) else ""


def resolve_mods(mo2_dir):
    """Mods folder of a portable MO2 in mo2_dir (read from its ModOrganizer.ini once the instance exists)."""
    base = Path(mo2_dir)
    ini = base / "ModOrganizer.ini"
    try:
        if ini.is_file():
            return mods_dir_from_ini(ini.read_text(encoding="utf-8", errors="replace"), base)
    except OSError:
        pass
    return str(base / "mods")


def plugin_step(mo2_dir, check, log):
    """Install the MO2 game plugin into <MO2>/plugins/basic_games/games. Returns True if it was newly installed/updated."""
    if not mo2_dir:
        raise Problem("choose the MO2 folder (the one containing ModOrganizer.exe) to install the game plugin into")
    base = Path(mo2_dir)
    if not (base / "ModOrganizer.exe").is_file():
        raise Problem("%s does not look like a Mod Organizer 2 folder (ModOrganizer.exe is missing)" % base)
    dest = base / "plugins" / "basic_games" / "games" / PLUGIN_NAME
    if not dest.parent.is_dir():
        raise Problem("%s was not found - this MO2 version may not include 'basic games' support" % dest.parent)
    cur = dest.read_bytes() if dest.is_file() else None
    new = PLUGIN_SRC.replace("\r\n", "\n").encode("utf-8")
    if cur is not None and cur.replace(b"\r\n", b"\n") == new:
        log("MO2 game plugin     : already installed")
        return False
    if check:
        log("MO2 game plugin     : will be %s" % ("installed" if cur is None else "updated"))
        return False
    if cur is not None and not Path(str(dest) + ".orig").exists():
        shutil.copy2(dest, str(dest) + ".orig")
    dest.write_bytes(new)
    log("MO2 game plugin     : %s (%s)" % ("installed" if cur is None else "updated", dest))
    return True


def plugin_only(mo2_dir, log):
    """Step 1: install just the MO2 game plugin."""
    new = plugin_step(mo2_dir, False, log)
    log("")
    if new:
        log("Restart MO2 if it is running. Next: Run MO2 and create a portable instance for Super Robot Wars Y, then continue with Step 2.")
    else:
        log("The plugin is already in place. If MO2 has not created the Super Robot Wars Y instance yet, do that now, then continue with Step 2.")
    return True


def game_files(game):
    game = Path(game)
    if not (game / "SUPER ROBOT WARS Y.exe").exists() or not (game / DLL_REL).exists():
        raise Problem("%s does not look like the SRWY folder (SUPER ROBOT WARS Y.exe / GameAssembly.dll missing)" % game)
    meta = list(game.glob("*_Data/il2cpp_data/Metadata/global-metadata.dat"))
    if len(meta) != 1:
        raise Problem("global-metadata.dat not found exactly once")
    bdir = game / "SUPER ROBOT WARS Y_Data" / "StreamingAssets" / "aa" / "StandaloneWindows64"
    bundles = [bdir / (stem + ".bundle") for stem in LANG_STEMS if (bdir / (stem + ".bundle")).is_file()]
    return game / DLL_REL, meta[0], bundles


def run(game, parts, mode="inplace", mods_dir=None, mod_name="SRWY 4K Resolution Patcher", check=False,
        revert=False, log=print, langs=None, mo2_dir=None, plugin=False):
    """langs: language codes whose bundles to patch (default: the detected language, else en-US).
    mode: 'inplace' or 'mo2'. Returns True on success."""
    game = Path(game)
    dll, meta, bundles = game_files(game)
    derived = False
    if mode == "mo2":
        if not mods_dir and mo2_dir:
            mods_dir = resolve_mods(mo2_dir)
        if mods_dir and mo2_dir:
            def norm(x):
                return os.path.normcase(os.path.normpath(str(x)))

            derived = norm(mods_dir) == norm(resolve_mods(mo2_dir))
        if not mods_dir:
            raise Problem("choose the MO2 folder or its mods folder")
        root = Path(mods_dir) / mod_name
    if langs is None:
        langs = [detect_language(game) or "en-US"]
    want = {stem for code, _, stem, _ in LANGS if code in langs}
    if check:
        log("Checking: %s" % (
            "the Mod Organizer 2 mod folder, %s (any file not there yet is read from the game folder)" % root
            if mode == "mo2" else "the game's own files in %s" % game))
    if plugin and not revert:
        if plugin_step(mo2_dir, check, log):
            log("Restart MO2 if it is running so it loads the plugin.")
            if mode == "mo2" and derived and not (Path(mo2_dir) / "ModOrganizer.ini").exists():
                log("")
                log("Next: Start MO2, create a portable instance for Super Robot Wars Y, then run this installer again to write the mod.")
                return True
    if revert:
        if mode == "mo2":
            log("MO2 mode: nothing was written to the game. Remove the mod folder in MO2 (or delete %s)." % root)
            return True
        n = 0
        for p in [dll, meta] + sorted(set(bundles) | {
            Path(str(o)[:-5]) for o in (game / "SUPER ROBOT WARS Y_Data").rglob("*.bundle.orig")
        }):
            bak = Path(str(p) + ".orig")
            if not bak.exists():
                continue
            shutil.copy2(bak, p)
            n += 1
            log("restored " + p.name)
        log("%d file(s) restored." % n)
        return True

    def rd(p):
        if mode == "mo2":
            m = root / Path(p).relative_to(game)
            if m.is_file():
                return m.read_bytes()
        return Path(p).read_bytes()

    jobs = []
    dll_parts = [p for p in parts if p in GROUPS or p == "story"]
    if dll_parts or "resolution" in parts:
        if "resolution" in parts:
            data = rd(meta)
            new, st = meta_apply(data)
            log("global-metadata.dat : resolution table %s" % ("already applied" if st == "done" else "will be patched"))
            if st == "todo":
                jobs.append((meta, new, "global-metadata.dat"))
        data = rd(dll)
        new, state = dll_apply(data, dll_parts)
        for g in dll_parts:
            log("GameAssembly.dll    : %-10s %s" % (g, "already applied" if state[g] == "done" else "will be patched"))
        if new != data:
            jobs.append((dll, new, "GameAssembly.dll"))
    if "labels" in parts:
        if not want:
            raise Problem("choose at least one language for the labels")
        n_todo = n_done = 0
        for b in sorted((x for x in bundles if x.stem in want), key=lambda x: x.stem):
            new, st = bundle_apply(rd(b), b.stem)
            if st == "skip":
                continue
            if st == "done":
                n_done += 1
                continue
            n_todo += 1
            jobs.append((b, new, b.name))
        log("language bundles    : %s - %d to update, %d already done" % (", ".join(langs), n_todo, n_done))
        if n_todo + n_done == 0:
            raise Problem("none of the selected language bundles were found in StreamingAssets/aa/StandaloneWindows64 - different game build?")
    if check:
        log("Check only - nothing written.")
        return True

    def mo2_reminder(existed):
        log("")
        if existed:
            log("If the mod doesn't seem to be working, remember to refresh MO2's mod list and activate %s." % mod_name)
        else:
            log("Last Step: Refresh MO2's mod list and activate %s." % mod_name)

    if not jobs:
        log("Nothing to do.")
        if mode == "mo2" and root.is_dir():
            mo2_reminder(True)
        return True

    def write(dst, data):
        tmp = Path(str(dst) + ".tmp_srwy")
        tmp.write_bytes(data)
        try:
            os.chmod(dst, stat.S_IREAD | stat.S_IWRITE)
        except OSError:
            pass
        os.replace(tmp, dst)

    existed = mode == "mo2" and root.is_dir()
    for src, new, label in jobs:
        try:
            if mode == "inplace":
                bak = Path(str(src) + ".orig")
                if not bak.exists():
                    shutil.copy2(src, bak)
                write(src, new)
                log("patched  %s" % label)
            else:
                dst = root / Path(src).relative_to(game)
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(new)
                log("wrote    %s" % dst.relative_to(root))
        except OSError as e:
            raise Problem("could not write %s (%s). Is the game running? Close it and press Revert, then Install again."
                          % (label, e.strerror or e))
    if mode == "mo2":
        (root / "meta.ini").write_text("[General]\nversion=%s\n" % VERSION, encoding="utf-8")
        log("MO2 mod written to %s" % root)
        mo2_reminder(existed)
        return True
    log("Done. Close the game before patching; Steam 'verify files' or an update will undo this - just run the installer again.")
    return True


class Tooltip:
    """Small hover tooltip for a tkinter widget."""

    def __init__(self, widget, text, delay=500):
        import tkinter as tk

        self.tk, self.w, self.text, self.delay, self.tip, self.job = tk, widget, text, delay, None, None
        widget.bind("<Enter>", self._enter, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _enter(self, _e):
        self._hide()
        self.job = self.w.after(self.delay, self._show)

    def _show(self):
        tk = self.tk
        x, y = self.w.winfo_pointerx() + 14, self.w.winfo_pointery() + 18
        self.tip = tk.Toplevel(self.w)
        self.tip.wm_overrideredirect(True)
        tk.Label(
            self.tip, text=self.text, justify="left", background="#ffffe1", relief="solid",
            borderwidth=1, wraplength=420, padx=5, pady=3,
        ).pack()
        self.tip.update_idletasks()
        x = min(x, self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth() - 4)
        y = min(y, self.tip.winfo_screenheight() - self.tip.winfo_reqheight() - 4)
        self.tip.wm_geometry("+%d+%d" % (x, y))

    def _hide(self, _e=None):
        if self.job:
            self.w.after_cancel(self.job)
            self.job = None
        if self.tip:
            self.tip.destroy()
            self.tip = None


def work_area():
    """(left, top, width, height) of the desktop minus the taskbar, or None."""
    try:
        import ctypes
        from ctypes import wintypes

        r = wintypes.RECT()
        if ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(r), 0):
            return r.left, r.top, r.right - r.left, r.bottom - r.top
    except Exception:
        pass
    return None


def gui():
    import tkinter as tk
    from tkinter import filedialog, scrolledtext

    root = tk.Tk()
    root.title("SRWY 4K Resolution Patcher %s" % VERSION)
    root.attributes("-alpha", 0.0)
    game_v, mods_v, name_v = tk.StringVar(), tk.StringVar(), tk.StringVar(value="SRWY 4K Resolution Patcher")
    mode_v = tk.StringVar(value="inplace")
    part_v = {p: tk.BooleanVar(value=True) for p in PARTS}
    lang_v = {code: tk.BooleanVar(value=False) for code, _, _, _ in LANGS}

    def default_langs():
        d = detect_language(game_v.get()) if game_v.get() else None
        for code, var in lang_v.items():
            var.set(code == (d or "en-US"))

    g = find_steam_game()
    if g:
        game_v.set(os.path.normpath(str(g)))
    default_langs()
    mo2_v = tk.StringVar()
    mo2_found = detect_mo2(game_v.get() or None)
    if mo2_found is not None:
        mode_v.set("mo2")
        mods_v.set(mo2_found)
        if mo2_found and (Path(mo2_found).parent / "ModOrganizer.exe").is_file():
            mo2_v.set(os.path.normpath(str(Path(mo2_found).parent)))

    def pick(title, var):
        d = filedialog.askdirectory(title=title)
        return os.path.normpath(d) if d else var.get()

    def browse_game():
        old = game_v.get()
        game_v.set(pick("Select the SRWY folder (contains SUPER ROBOT WARS Y.exe)", game_v))
        if game_v.get() != old:
            default_langs()

    def row(parent, label, var, r, cmd, tip):
        tk.Label(parent, text=label, anchor="w").grid(row=r, column=0, sticky="w", padx=8, pady=3)
        e = tk.Entry(parent, textvariable=var, width=52)
        e.grid(row=r, column=1, columnspan=4, sticky="we", padx=4)
        bt = tk.Button(parent, text="Browse...", command=cmd)
        bt.grid(row=r, column=2, padx=4)
        Tooltip(e, tip)
        Tooltip(bt, tip)

    root.columnconfigure(0, weight=1)

    s1 = tk.LabelFrame(root, text="Step 1 - Install SRWY support plugin to your Mod Organizer 2 installation")
    s1.grid(row=0, column=0, sticky="we", padx=8, pady=(8, 4))
    s1.columnconfigure(1, weight=1)
    tk.Label(
        s1, justify="left", anchor="w", wraplength=640,
        text="Skip this step if you are not using Mod Organizer 2.\n"
             "Mod Organizer 2 must already be extracted to a folder of its own - the plugin is installed into that folder.\n"
             "Mod Organizer 2 cannot create a Super Robot Wars Y instance without this plugin. After installing it, run Mod Organizer 2 and create a portable instance for the game, then continue with Step 2.",
    ).grid(row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(4, 2))

    def browse_mo2():
        d = pick("Select the Mod Organizer 2 folder (contains ModOrganizer.exe)", mo2_v)
        mo2_v.set(d)
        if d and not mods_v.get():
            mods_v.set(resolve_mods(d))

    row(s1, "MO2 folder", mo2_v, 1, browse_mo2,
        "Your Mod Organizer 2 folder: the one containing ModOrganizer.exe (e.g. a portable instance). "
        "The plugin is copied to <MO2 folder>\\plugins\\basic_games\\games. Step 2 also uses this folder to find the mods folder.")
    plug_btn = tk.Button(s1, text="Install plugin", width=14)
    plug_btn.grid(row=2, column=0, columnspan=3, pady=(2, 6))
    Tooltip(plug_btn, "Copies the Super Robot Wars Y game plugin (one file) into Mod Organizer 2. Restart MO2 afterwards if it is running.")

    s2 = tk.LabelFrame(root, text="Step 2 - Install the mod")
    s2.grid(row=1, column=0, sticky="we", padx=8, pady=4)
    s2.columnconfigure(1, weight=1)
    row(s2, "SRWY game folder", game_v, 0, browse_game,
        "The folder that contains SUPER ROBOT WARS Y.exe and GameAssembly.dll. Found automatically from Steam when possible.")
    r1 = tk.Radiobutton(s2, text="Patch the game files in place (originals are saved as .orig)", variable=mode_v, value="inplace")
    r1.grid(row=1, column=0, columnspan=3, sticky="w", padx=8)
    r2 = tk.Radiobutton(s2, text="Create a Mod Organizer 2 mod instead (the game folder is not changed)", variable=mode_v, value="mo2")
    r2.grid(row=2, column=0, columnspan=3, sticky="w", padx=8)
    Tooltip(r1, "Edits the game's files directly. Each changed file is first copied to <name>.orig so Revert can restore it. "
                "Steam 'verify files' or a game update undoes the patch; run the installer again afterwards.")
    Tooltip(r2, "Writes patched copies into a new mod folder for Mod Organizer 2 and leaves the game folder untouched. "
                "Enable the mod in MO2 to use it.")
    row(s2, "MO2 'mods' folder", mods_v, 3,
        lambda: mods_v.set(pick("Select the MO2 mods folder", mods_v)),
        "Only used for the Mod Organizer 2 option: the 'mods' folder of your MO2 instance (filled in from the MO2 folder in Step 1 when possible). "
        "Check also looks here for an existing install.")
    tk.Label(s2, text="Mod name", anchor="w").grid(row=4, column=0, sticky="w", padx=8)
    ne = tk.Entry(s2, textvariable=name_v, width=30)
    ne.grid(row=4, column=1, sticky="w", padx=4)
    Tooltip(ne, "Name of the folder created inside the MO2 'mods' folder (Mod Organizer 2 option only).")

    desc = {
        "resolution": "Resolution - Replace vanilla resolutions with 4K, 1440p, 1080p and 720p",
        "labels": "Labels - Patch language bundle(s) so in-game resolution labels match the new resolutions",
        "story": "Story - Patch the game to properly handle upscaled images for story events",
        "battle": "Battle - Patch the game to properly handle upscaled backgrounds for battle events",
    }
    tips = {
        "resolution": "Patches the engine's output resolutions from 1920x1200 / 1920x1080 / 1280x800 / 1280x720 to 3840x2160 / 2560x1440 / 1920x1080 / 1280x720. Edits global-metadata.dat and GameAssembly.dll.",
        "labels": "Rewrites the four resolution labels in Option -> System -> PC Settings -> Screen Resolution so they match the above change. There are separate patches for each supported language, listed below. Tick the languages you want patched (the game's language is pre-selected if it can be detected). Unticked languages keep the old labels.",
        "story": "Lets the game properly display upscaled story-event illustrations instead of improperly scaling or displacing them. Using this patch will not break the displaying of vanilla illustrations. Edits GameAssembly.dll.",
        "battle": "Makes the individual layers of upscaled battle-event parallax backgrounds scroll at the correct speeds. Using this patch will not break the displaying of vanilla backgrounds. Edits GameAssembly.dll.",
    }
    f1 = tk.LabelFrame(s2, text="4K resolution")
    f1.grid(row=5, column=0, columnspan=3, sticky="we", padx=(6, 3), pady=8)
    f2 = tk.LabelFrame(s2, text="Upscaled backgrounds - These are safe to install even without upscale mod")
    f2.grid(row=6, column=0, columnspan=3, sticky="we", padx=8, pady=3)
    boxes = {}
    for frame, keys in ((f1, ("resolution", "labels")), (f2, ("story", "battle"))):
        for i, p in enumerate(keys):
            boxes[p] = tk.Checkbutton(frame, text=desc[p], variable=part_v[p])
            boxes[p].grid(row=i, column=0, sticky="w")
            Tooltip(boxes[p], tips[p])
    lf = tk.Frame(f1)
    lf.grid(row=2, column=0, sticky="w", padx=26)
    lboxes = []
    for i, (code, name, _, _) in enumerate(LANGS):
        text = "%s (%s)" % (name, code) if code in ("en-US", "ja-JP", "ko-KR") else name
        cb = tk.Checkbutton(lf, text=text, variable=lang_v[code])
        cb.grid(row=i // 3, column=i % 3, sticky="w", padx=(0, 10))
        lboxes.append(cb)
        Tooltip(cb, "Patch the %s (%s) language bundle." % (name, code))

    def sync_langs(*_):
        for cb in lboxes:
            cb.config(state="normal" if part_v["labels"].get() else "disabled")

    part_v["labels"].trace_add("write", sync_langs)
    sync_langs()

    out = scrolledtext.ScrolledText(root, height=8, width=80, state="disabled")
    out.grid(row=2, column=0, padx=8, pady=6, sticky="nsew")

    q = queue.Queue()
    buttons = []

    def pump():
        try:
            while True:
                m = q.get_nowait()
                if m is None:
                    for bt in buttons:
                        bt.config(state="normal")
                    continue
                if m == "@@MO2_MODE":
                    mode_v.set("mo2")
                    continue
                out.config(state="normal")
                out.insert("end", m + "\n")
                out.see("end")
                out.config(state="disabled")
        except queue.Empty:
            pass
        root.after(100, pump)

    def work(args):
        game, parts, mode, mods, name, check, revert, langs, mo2 = args
        try:
            q.put("--- %s ---" % ("revert" if revert else "check" if check else "install"))
            run(game, parts, mode, mods, name, check, revert, q.put, langs, mo2)
        except Problem as e:
            q.put("STOPPED: %s\nNothing was changed." % e)
        except Exception as e:
            q.put("ERROR: " + repr(e))
        finally:
            q.put(None)

    def go(check=False, revert=False):
        parts = [p for p in PARTS if part_v[p].get()]
        if not game_v.get():
            q.put("STOPPED: choose the SRWY folder")
            return
        for bt in buttons:
            bt.config(state="disabled")
        mods = os.path.normpath(mods_v.get()) if mods_v.get() else None
        langs = [c for c, _, _, _ in LANGS if lang_v[c].get()]
        threading.Thread(target=work, daemon=True, args=((
            os.path.normpath(game_v.get()), parts, mode_v.get(), mods,
            name_v.get() or "SRWY 4K Resolution Patcher", check, revert, langs,
            os.path.normpath(mo2_v.get()) if mo2_v.get() else None,
        ),)).start()

    b = tk.Frame(s2)
    b.grid(row=7, column=0, columnspan=3, pady=4)
    btips = {
        "Check": "Dry run: Reports which patches are still needed, without writing anything. Looks at the game's files, or at the MO2 mod folder if the MO2 option is selected.",
        "Install": "Applies the ticked patches.",
        "Revert": "Restores the original files from their .orig backups (in-place option). For an MO2 mod, just delete or disable the mod in MO2.",
    }
    for text, cmd in (("Check", lambda: go(check=True)), ("Install", go), ("Revert", lambda: go(revert=True))):
        bt = tk.Button(b, text=text, width=12, command=cmd)
        bt.pack(side="left", padx=6)
        buttons.append(bt)
        Tooltip(bt, btips[text])

    def work_plugin(mo2):
        try:
            q.put("--- install plugin ---")
            plugin_only(mo2, q.put)
            q.put("@@MO2_MODE")
        except Problem as e:
            q.put("STOPPED: %s\nNothing was changed." % e)
        except Exception as e:
            q.put("ERROR: " + repr(e))
        finally:
            q.put(None)

    def go_plugin():
        if not mo2_v.get():
            q.put("STOPPED: choose the Mod Organizer 2 folder")
            return
        for bt in buttons:
            bt.config(state="disabled")
        threading.Thread(target=work_plugin, daemon=True,
                         args=(os.path.normpath(mo2_v.get()),)).start()

    plug_btn.config(command=go_plugin)
    buttons.append(plug_btn)

    root.rowconfigure(2, weight=1)
    pump()
    if mo2_found is not None:
        q.put("Started from inside Mod Organizer 2: the Mod Organizer 2 option is selected%s. Patching the game in place from here would be captured by MO2's virtual file system instead of reaching the game folder."
              % (" and the mods folder was filled in" if mo2_found else "; choose your MO2 mods folder"))
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.update()
    ew = root.winfo_rootx() - root.winfo_x()
    w = root.winfo_reqwidth() + 2 * ew
    h = root.winfo_reqheight() + (root.winfo_rooty() - root.winfo_y()) + ew
    wa = work_area() or (0, 0, root.winfo_screenwidth(), root.winfo_screenheight())
    root.geometry("+%d+%d" % (
        wa[0] + max(0, wa[2] - w) // 2,
        wa[1] + max(0, wa[3] - h) // 2,
    ))
    root.attributes("-alpha", 1.0)
    root.mainloop()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir")
    ap.add_argument("--mo2-mods")
    ap.add_argument("--mod-name", default="SRWY 4K Resolution Patcher")
    ap.add_argument("--only", nargs="+", choices=PARTS)
    ap.add_argument("--langs", nargs="+", choices=[l[0] for l in LANGS],
                    help="language bundles to patch (default: the game's Steam language, else en-US)")
    ap.add_argument("--mo2-dir", help="MO2 program folder (contains ModOrganizer.exe); the mods folder of a portable instance is derived from it")
    ap.add_argument("--install-plugin", action="store_true", help="also install the MO2 game plugin into --mo2-dir")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--revert", action="store_true")
    a = ap.parse_args()
    if a.install_plugin and a.mo2_dir and not a.game_dir:
        try:
            plugin_only(a.mo2_dir, print)
        except Problem as e:
            sys.exit("STOPPED: %s" % e)
        return
    if not a.game_dir:
        if len(sys.argv) == 1:
            gui()
            return
        g = find_steam_game()
        if not g:
            ap.error("--game-dir is required (the Steam install could not be found)")
        a.game_dir = str(g)
    if not a.mo2_mods:
        m = detect_mo2(a.game_dir)
        if m is not None:
            if not m:
                sys.exit("STOPPED: started from inside Mod Organizer 2 but its mods folder could not be found - pass --mo2-mods.")
            a.mo2_mods = m
            print("Started from inside Mod Organizer 2 - writing an MO2 mod to %s" % m)
    try:
        run(a.game_dir, list(a.only or PARTS), "mo2" if (a.mo2_mods or a.mo2_dir) else "inplace",
            a.mo2_mods, a.mod_name, a.check, a.revert,
            langs=a.langs, mo2_dir=a.mo2_dir, plugin=a.install_plugin)
    except Problem as e:
        sys.exit("STOPPED: %s\nNothing was changed." % e)


if __name__ == "__main__":
    main()
