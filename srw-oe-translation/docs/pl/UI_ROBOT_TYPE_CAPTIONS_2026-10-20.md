# Enemy Robots: audit of weapon/type footer captions (2026-10-20)

## Scope and finding

The Zaku II screenshot exposed a source-export gap: its Japanese footer is a `config_leftover` string in a shared `RoboDictionary` member, not a structured unit-name field. I audited **every row in the current `pakiet_EN/04_config_text.jsonl`** that meets all of these conditions:

- category is `config_leftover`;
- Japanese text ends in `タイプ`;
- source member is `srw_DL_RoboDictionaryNN.bin` in a matching `configNN` or `imenuNN` package.

That inventory has **18 distinct captions represented by 36 physical source rows** (config/imenu mirrors). The four Zaku Machine Gun/Bazooka mirror rows were added in the preceding fix; this follow-up adds the other **16 captions / 32 rows**. Other unreviewed `leftover:` rows remain quarantined.

The three Zaku II unit-list records are IDs 1050 (Machine Gun), 1051 (Bazooka), and 1053 (Char). Char's red Zaku record has the same Machine Gun and Bazooka weapon labels, so it uses the two already-translated footers; the source contains no third distinct Zaku type caption. Other RoboDictionary rows do contain additional distinct weapon/type labels, listed below.

## Reviewed Polish captions

| Japanese source caption | English reference | Polish footer | Slot limit |
|---|---|---|---:|
| `「ガトリングガン」タイプ` | Gatling Gun type | `Typ: karabin Gatlinga` | 25 B |
| `「ロングキャノン」タイプ` | Long Cannon type | `Typ: długie działo` | 25 B |
| `「ドライバー攻撃」タイプ` | Driver Attack type | `Typ: atak śrubokrętem` | 25 B |
| `「ザク・マシンガン」タイプ` | Zaku Machine Gun type | `Typ: karabin maszynowy Zaku` | 27 B |
| `「ザク・バズーカ」タイプ` | Zaku Bazooka type | `Typ: bazooka Zaku` | 25 B |
| `「ジャイアント・バズ」タイプ` | Giant Bazooka type | `Typ: bazooka Gigant` | 29 B |
| `「シュツルム・ファウスト」タイプ` | Sturm Faust type | `Typ: granatnik Sturm Faust` | 33 B |
| `「速射機関砲」タイプ` | Rapid-Fire Gun type | `Typ: szybkie działko` | 21 B |
| `「カノン砲」タイプ` | Cannon type | `Typ: armata` | 19 B |
| `「ミサイル」タイプ` | Missile type | `Typ: rakietowy` | 19 B |
| `「触手」タイプ` | Tentacle type | `Typ: macki` | 15 B |
| `「レッドショルダー」タイプ` | Red Shoulder type | `Typ: Czerwone Ramię` | 27 B |
| `「レッドショルダー（ミサイル）」タイプ` | Red Shoulder (Missile) type | `Typ: Czerwone Ramię (rakiety)` | 39 B |
| `「大型ビームライフル」タイプ` | Large Beam Rifle type | `Typ: duży karabin wiązkowy` | 29 B |
| `「ショルダーミサイルポッド」タイプ` | Shoulder Missile Pod type | `Typ: zasobnik rakietowy` | 35 B |
| `「ハードブレッドガン」タイプ` | Hard Bullet Gun type | `Typ: działo kinetyczne` | 29 B |
| `「リング光線」タイプ` | Ring Beam type | `Typ: wiązka kołowa` | 21 B |
| `「大喰らい」タイプ` | Big Eater type | `Typ: żarłok` | 19 B |

All translations pass the PL codec/row checks and fit their measured byte limits. The source-bound addition plan is `config/pl/ui-robot-type-captions-2026-10-20.json`; together with the initial Zaku plan it accounts for all 36 rows. The writer routes these rows through the existing `RoboDictionary` `table_write` path. Handoff visibility is an exact 36-ID allow-list, not a general relaxation for leftovers.

## Verification and limits

The type-caption update produced 87,819 snapshot entries. A later screenshot exposed the separate `Pilot: Char` footer, documented in `UI_ZAKU_CHAR_PILOT_2026-10-20.md`; the cumulative snapshot now has **87,823 entries**. Final materialization reports **0 hard errors** (25,125 warnings remain). Regression tests check the complete 18-caption/36-row type inventory, the exact Char-pilot source bindings, Polish byte fit, PL handoff visibility, table-writer routing, and that Char's Zaku reuses the two existing weapon labels.

The original game images are not available in this workspace. No physical ISO rebuild or in-game visual confirmation is claimed. These sources include global `config00.cpk`/`imenu00.cpk` as well as extracted `configNN.EDAT`/`imenuNN.EDAT` mirrors, so the relevant installed game data must be rebuilt with the updated PL package; this is not a DLC-only or save-file change.
