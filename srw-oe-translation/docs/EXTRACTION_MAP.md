# Extraction map — where each translatable category lives (from `scan_translatable.py`)

Method: `scan_translatable.py <USRDIR>` inventories every container as `events` (EVNT narration),
`strings` (NUL-separated CP932 tables) or `binary`. Real text vs noise was then triaged by hand.
Two extractor families exist today; a third (structured tables) is open.

## Covered (extractable now)

| Category | Container(s) | Tool | Notes |
|---|---|---|---|
| Event narration (ch1 disc) | `eventP00.cpk` | `export_strings.py` | EVNT records; growth proven |
| Event narration (ch2-8 DLC) | `eventP01..P09.cpk` (DLC) | `export_strings.py` | same format |
| Battle quotes / messages | `mesbtl00.cpk` | `extract_tables.py` | NUL-separated lines, e.g. 「どんな奴だろうと…」 |
| Character dictionary / encyclopedia / names | `imenu00.cpk` | `extract_tables.py` | `srwDL_CharaDictionary00.bin`: 愛称／声優／図鑑 strings (DLC dictionary) |
| Map / terrain / background names | `config00.cpk` | `extract_tables.py` | 赤宇宙／森林　山 etc. |
| Credits / copyright | `cprt0001..0004.cpk` | `extract_tables.py` (raw) | ㊤/㊦ credit lines |

## Open (strings present but NOT NUL-separated -> need layout-specific parsers)

- **Menus / options / help / warnings:** `configst.cpk`, `system.cpk` (samples garbled under the
  NUL heuristic; text is in a structured/length-prefixed table).
- **Items / missions / tactics / navi:** `tacsys.cpk`, `tactics.cpk`, `taclevup.cpk`,
  `navisys.cpk`, `logodata.cpk` (few garbled runs; structured tables).
Cracking these means dumping the member bytes and reversing the row/offset layout (as was done for
the EVNT inner sizes); do one container at a time.

## Noise (not translatable)

Audio: `se*`, `semv*`, `segu01`, `bacb00`, `bseq00`. Textures: `txa00`, `texanm`, `eftex00`.
Bitmaps/faces/font: `mesbmp00`, `face00`, `font`, `bmp00`, `svicon`. 3D/anim (only debug
"シーン/ルート" names): `robo00`, `lmap`, `btlcam`, `efmodel`, `efclump`, `smap`, `sprstd00`,
`bg2d`, `mov00`. Conversion tables: `u16tbl`.

## DLC note

Beyond the ISO, the DLC catalog adds the `eventP0x` chapters (events, covered) and the `srwDL_*`
dictionary content in `imenu00` (covered by extract_tables). Run the same tools over the unpacked
DLC `USRDIR`/`SAVEDATA` equivalents to pick those up.
