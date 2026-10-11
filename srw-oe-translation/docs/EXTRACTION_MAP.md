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

## System / UI / menus / items / parts / skills text — `configst.cpk` (verified, clean)

`configst.cpk` (a nested PAC of `srwDL_*.bin` sub-files) is the **main system-text container**.
`extract_structured.py` pulls 3690 strings (1706 unique) of clean CP932, covering most of the
UI categories at once:
- menus / options / help / warnings: よろしいですか？／変身して別の形態になります。／メインテーマ曲をユニットごとに指定できます。
- spirit (精神) command names: 不屈/鉄壁/集中/熱血/加速/閃き/必中/努力/幸運
- items / upgrade parts / skills / effects: 武器, アイテム, 強化 (x38), パーツ (x112, with descriptions
  e.g. 撃破時にランダムパーツをドロップする), 精神エナジー装置, 命中ダウン１, 重複装備不可
- mission / economy UI: ミッション (x72, e.g. ミッションディスク), 資金, 経験値, DLC 購入 text

Run: `python tools\extract_structured.py configst.cpk` -> `local/tables/configst.strings.json`.

**Repacking is still open:** these are fixed-record tables with no length field, so in-place growth
is unsafe until the record stride (and any pointer table) is reversed. Read-only source for now.

## NOT text (corrected) — `tacsys` / `tactics` / `taclevup` / `navisys` / `logodata` / `system`

Verified on `tacsys.cpk`: its member is itself a PAC of `.gim` textures + numeric tables (head
`tacsys_02.gim`), i.e. **binary, not translatable text**. A byte-scan over it yields only false
positives (e.g. 遧劔誧滑葈). These were mis-triaged as "structured text" earlier; they are noise.
`extract_structured.py` should be run only on genuine text containers (configst, and the NUL-table
files via extract_tables). Where specific weapon/item/mission *name lists* live, if not inside
configst, is still to be pinned down.

## Noise (not translatable)

Audio: `se*`, `semv*`, `segu01`, `bacb00`, `bseq00`. Textures: `txa00`, `texanm`, `eftex00`.
Bitmaps/faces/font: `mesbmp00`, `face00`, `font`, `bmp00`, `svicon`. 3D/anim (only debug
"シーン/ルート" names): `robo00`, `lmap`, `btlcam`, `efmodel`, `efclump`, `smap`, `sprstd00`,
`bg2d`, `mov00`. Conversion tables: `u16tbl`.

## DLC note

Beyond the ISO, the DLC catalog adds the `eventP0x` chapters (events, covered) and the `srwDL_*`
dictionary content in `imenu00` (covered by extract_tables). Run the same tools over the unpacked
DLC `USRDIR`/`SAVEDATA` equivalents to pick those up.
