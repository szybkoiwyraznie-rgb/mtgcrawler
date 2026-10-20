# Enemy Robots: Zaku II — source-bound footer repair (2026-10-20)

Owner screenshot shows the Robot Viewer with the Japanese footer `「ザク・マシンガン」タイプ` beneath the selected Zaku II. The list's visible `Zaku II` roster name is already Romanized; the Japanese text is the shared weapon-type caption, not a missing translation of the canonical mech name.

## Exact PL additions

The screen caption is exported as a confirmed legacy visible string in `04_config_text.jsonl`, `config_leftover` category. Its bindings are in the global `srw_DL_RoboDictionary00.bin` source. The original config/imenu dictionary copies are byte-identical, so both physical rows receive the same PL value:

| Source offset | Japanese source | EN reference | PL value | Slot budget |
|---:|---|---|---|---:|
| 2124 | `「ザク・マシンガン」タイプ` | `"Zaku Machine Gun" type` | `Typ: karabin maszynowy Zaku` | 27 B |
| 2252 | `「ザク・バズーカ」タイプ` | `"Zaku Bazooka" type` | `Typ: bazooka Zaku` | 25 B |

Each caption is added for `config00.cpk` and its `imenu00.cpk` mirror: four rows total. The exact IDs, immutable binding hashes, original JP/EN, offsets, and reviewed texts are recorded in `config/pl/ui-zaku-enemy-robot-2026-10-20.json`. These are additions to the accepted PL4 text snapshot; returned PL4 text and historical corrections remain intact.

## Narrow exception and validation

These four rows were previously quarantined by the generic `leftover:` rule. The owner screenshot confirms that they are visible UI text, so only these exact source IDs are retained in Polish table views. Other leftover/binary scans remain quarantined. The correction tool requires the base source package and checks the source hash, ID, JP/EN, member, container, offset, byte budget, and PL codec before adding a snapshot row.

Offline checks confirm all four immutable bindings, PL validation, materialization with zero hard errors, and routing through the existing RoboDictionary `table_write` path. A synthetic measured-layout writer test replaces the type slot and leaves the Zaku II roster-name slots untouched. The original ISO/DLC inputs are unavailable here, so **no physical rebuild or in-game confirmation is claimed**; the user should verify the next normal PL ISO build. Because the source is `config00.cpk`, this correction belongs in the ISO build, not a DLC-only copy.
