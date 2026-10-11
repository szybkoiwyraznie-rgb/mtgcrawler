# Extraction map — where each translatable category lives (from `scan_translatable.py`)

Method: `scan_translatable.py <USRDIR>` inventories every container as `events` (EVNT narration),
`strings` (NUL-separated CP932 tables) or `binary`. Real text vs noise was then triaged by hand.
Three extractor families exist: `export_strings.py` (events), `extract_tables.py` (NUL-separated
tables), `extract_structured.py` (fixed-record tables — extraction only; repack still open).

## Covered (extractable now)

| Category | Container(s) | Tool | Notes |
|---|---|---|---|
| Event narration (ch1 disc) | `eventP00.cpk` | `export_strings.py` | EVNT records; growth proven |
| Event narration (ch2-8 DLC) | `eventP01..P09.cpk` (DLC) | `export_strings.py` | same format |
| Battle quotes / messages | `mesbtl00.cpk` | `extract_tables.py` | NUL-separated lines, e.g. 「どんな奴だろうと…」 |
| Character dictionary / encyclopedia / names | `imenu00.cpk` | `extract_tables.py` | `srwDL_CharaDictionary00.bin`: 愛称／声優／図鑑 strings (DLC dictionary) |
| Map / terrain / background names | `config00.cpk` | `extract_tables.py` | 赤宇宙／森林　山 etc. |
| Credits / copyright | `cprt0001..0004.cpk` | `extract_tables.py` (raw) | ㊤/㊦ credit lines |

## Structured — byte-scan extractor `extract_structured.py` (extraction works, repack open)

- **Menus / options / help / warnings:** `configst.cpk`, `system.cpk`
- **Items / missions / tactics / navi:** `tacsys.cpk`, `tactics.cpk`, `taclevup.cpk`,
  `navisys.cpk`, `logodata.cpk`

These are fixed-record tables (no NUL separators), so `tools/extract_structured.py` byte-scans each
decompressed member for maximal CP932 double-byte runs and writes `{member, offset, source,
source_bytes, target}` (same schema as the other extractors) to `local/tables/*.strings.json`.
Verified on `configst.cpk`: 3690 strings incl. spirit names (不屈/鉄壁/集中/熱血/加速/閃き/必中/努力/幸運)
and menu/help/warning text (合体すると…／が全回復します。／よろしいですか？／変身して別の形態になります。).

**Repacking is still open:** fixed records carry no length field, so growing a string in place is not
yet safe — an apply step needs the record stride (and any pointer table) first. Until then these are
read-only translation sources. Run: `python tools\extract_structured.py <container>.cpk [...]`.

## Noise (not translatable)

Audio: `se*`, `semv*`, `segu01`, `bacb00`, `bseq00`. Textures: `txa00`, `texanm`, `eftex00`.
Bitmaps/faces/font: `mesbmp00`, `face00`, `font`, `bmp00`, `svicon`. 3D/anim (only debug
"シーン/ルート" names): `robo00`, `lmap`, `btlcam`, `efmodel`, `efclump`, `smap`, `sprstd00`,
`bg2d`, `mov00`. Conversion tables: `u16tbl`.

## DLC note

Beyond the ISO, the DLC catalog adds the `eventP0x` chapters (events, covered) and the `srwDL_*`
dictionary content in `imenu00` (covered by extract_tables). Run the same tools over the unpacked
DLC `USRDIR`/`SAVEDATA` equivalents to pick those up.
