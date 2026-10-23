# SRW OE mech catalogue — delivered data-backed edition

**Current Polish presentation revision 4 (`v4.0`) — 2026-10-23:**
[srwoe_mech_catalog_v4_PL.md on Drive](https://drive.google.com/file/d/1Iom2YIbNna-djLB5em8WchoQMjdu6pSx/view)
— **873,130 bytes** (`11,953` lines), SHA-256
`07f11deb03c4533c35594d2f60a858b20687f5a1da21d27bc19a2e57392bb031`, MD5
`3b636281662186cb3d1ede67990c24c6`. Downloaded back and compared byte-for-byte
(`cmp -s`). Receipt: `docs/reading-script/polish/catalogue-v4.0.delivery.json`.

The frozen English reference edition (`srwoe_mech_catalog_v3.md`, **667,590 bytes**,
SHA-256 `19228a10bf3dcb4d0ae404a8de08b37f316db32de7a7de0eda7b9e2d90989dd7`) is not
published on Drive any more; it is reproduced byte-for-byte from the live `pakiet_EN`
by `tools/mech_catalog.py` (`collect` + `build_model` + `render`);
`tools/build_polish_reading_editions.py --catalogue-english …` refuses to localize
unless that reproduction matches the SHA-256 pinned in `presentation-v3.json`.

The owner's complete presentation request (a–h) applies to **every** unit/crew entry:
- No unit HTML anchor, “— Unit N” heading suffix or per-unit “Data: …” line (v2).
- No “— unit dictionary” tag after directly sourced series names.
- No “— Character N” or “(ID N)” suffix in any pilot/profile heading, including alternates.
- No repeated “Spirit Commands are intentionally excluded.” sentence beside pilots.
- No repeated “These are retained for completeness…” paragraph before special-entry tables.

Names, descriptions, stats, weapon tables and the distinction between ordinary and
special records remain unchanged. Inferred/unresolved series stay qualified; their
uncertainty is not promoted to a fact. All source IDs/provenance remain in the audit.
Exact diff proof: `presentation-v3.json`; the complete model hash is unchanged.

[First edition](https://drive.google.com/file/d/1cBbPxTiY-MFASz2H3UJ1aS7SmSD-8uQC/view)
and [v2](https://drive.google.com/file/d/1uDgRdtFqVVx7eel5jqkFBwT1zMCJcjlj/view)
are preserved separately, with exact metadata in `revisions/01.*.json` and
`revisions/02.*.json`. No game data or translations were changed by these revisions.

## Coverage

| Category                                                                 |     Result |
| ------------------------------------------------------------------------ | ---------: |
| Registered unit records (friendly/enemy/forms/objects/cinematics/spares) |    393/393 |
| Weapon/action table entries                                              |  1485/1485 |
| Nonzero selectors / zero selectors shown separately                      | 1274 / 211 |
| Default crew assignments / distinct assigned character IDs               |  535 / 201 |
| Native machine-skill references resolved                                 |    514/516 |
| Concrete base descriptions / executable overrides                        |   249 / 20 |
| Group rosters / distinct explicit member units                           |    16 / 53 |
| Positive conditional weapon gates                                        |        121 |
| Source-checked, catalogue-only wording repairs                           |         17 |

Every entry has name/series, pilot/crew profiles and special skills, native machine
abilities, and weapon names/effects with base power, range, hit modifier, EN and
Will fields. Spirit Commands are excluded; Spirit Power and similarly named skills
are not Spirit Commands. Linked enemy/allied pilot profiles remain separate.
All base effects use the lowest concrete record selected by the engine, not the
negative-level generic template or a max-level description.

This is **393 registered records, not 393 distinct playable mech designs**.
Animation and utility records are retained, not silently discarded or called attacks.

## Explicit limits — no guesses

- Series: **302 direct**, **57 form-derived**, **14 pilot-associated inferences**,
  **20 not recorded**. Inferred/unresolved cases are labelled; the latter include objects,
  spares and some ships/units, not just missing English. List in `delivery.json`.
- Skill reference **110** in unit **10115** (King Go-Saurer/Movie) and **230** in
  unit **491** (Fire Zephyr/Later) are unresolved and visible.
- **115 records have empty native-skill slots.** This does not mean they have no
  effects in game. Conditional group/stack systems are explained separately;
  equipment/status/scripted additions are not exhaustively reconstructed.
- Default crew/linked profiles do not establish every scenario-specific reassignment.
- Gate IDs are actual checks, but their exact unlock missions are not decoded.
  No gate is **not** a promise of availability at the start of the campaign.
- Stats are stored base data, not battle damage after upgrades/skills/terrain.
- The 17 catalogue-only description repairs have source hashes/reasons in
  `description-errata.json`. They fix damaged wording/placeholder order, **not
  balance values**. Neither the translation package nor game files were edited.
- Pure, bounded emulation of the 1.08 description selector is not a gameplay test.

## Verification

**1509 passed, 1 skipped, 382 subtests passed** — full project suite, 46.84 s.
Catalogue suite: **75 tests** (9 added for this presentation revision): 39 synthetic
+ 36 real-input tests. The latter reject **32 semantic mutations** even after document/audit hashes and sizes are repaired.
Original input and package hashes remained unchanged. Regeneration is byte-identical.

`verify_mech_catalog.py` checks facts against freshly read binary/English sources
without calling the generator's model/description/series helpers. It pairs the ordered machine-name H2 headings with verified internal IDs (including
duplicate names) and checks every Markdown unit/pilot/profile header, complete ability bullet, and all weapon rows.
Only then does shared canonical rendering seal the remaining notes/layout.
`--replay-engine` also reproduced all **254** base selector decisions.
See `verification.json`, `delivery.json` and [field evidence](../MECH_CATALOG.md).

## Reproduce (from `srw-oe-translation/`)

**Historical English snapshot:** this delivered catalogue is pinned to the
`source_package_commit` in `delivery.json` (`aa178c7...`). Subsequent game QA (v17)
changes unrelated DLC descriptions in 04; do not rewrite the historical manifest
or silently regenerate/re-upload the catalogue against new inputs. Export the
six JSONL files named by `source-inventory.json` from that Git revision into an
ignored folder (`git show <revision>:srw-oe-translation/pakiet_EN/<file>`), then
use `local/mech-catalog/frozen-source` for that folder in the commands below. The real-input regression test does this
read-only when the working package has changed. No branch switch or checkout is
performed. The first-edition Markdown/hashes are preserved in the revision archive; revisions 2 and 3
change only presentation and retains the identical frozen model.

Use **original decrypted** config00.cpk, config01–19.EDAT and configst.cpk together
in an ignored input directory, plus the matching original EBOOT.BIN. The commands
below use the flat download directory from this session. Full outputs remain ignored.
Normal generation/verification uses Python 3.11+ and its standard library only.

```sh
python3 tools/mech_catalog.py --configs ../google_drive --package local/mech-catalog/frozen-source \
  --elf ../google_drive/EBOOT.BIN \
  --source-manifest docs/mech-catalog/source-inventory.json \
  --engine-map docs/mech-catalog/engine-map.json \
  --errata docs/mech-catalog/description-errata.json \
  --out local/mech-catalog/srwoe_mech_catalog_v3.md \
  --audit local/mech-catalog/catalog_v3.audit.json
python3 tools/verify_mech_catalog.py --configs ../google_drive --package local/mech-catalog/frozen-source \
  --elf ../google_drive/EBOOT.BIN \
  --source-manifest docs/mech-catalog/source-inventory.json \
  --engine-map docs/mech-catalog/engine-map.json \
  --errata docs/mech-catalog/description-errata.json \
  --markdown local/mech-catalog/srwoe_mech_catalog_v3.md \
  --audit local/mech-catalog/catalog_v3.audit.json \
  --report local/mech-catalog/verification.json
python3 -m unittest discover -s tests -p 'test_mech_catalog*.py' -v
```

To independently regenerate the engine map, install `unicorn==2.1.4` in an ignored
venv, inventory the inputs, then run the memory-only selector. The map contains
only addresses/IDs/hashes, not game code or full text:

```sh
python3 tools/mech_catalog_sources.py --configs ../google_drive --package local/mech-catalog/frozen-source \
  --out local/mech-catalog/source-inventory.json \
  --summary local/mech-catalog/source-summary.json
python3 tools/mech_catalog_engine.py --elf ../google_drive/EBOOT.BIN \
  --package local/mech-catalog/frozen-source --inventory local/mech-catalog/source-inventory.json \
  --out local/mech-catalog/replayed-engine-map.json
```

Alternatively add `--replay-engine` to the verifier. `mech_catalog_probe.py` is an
optional field-access research helper (`capstone==5.0.6`); its disassembly output
must remain local. Real-input tests explicitly skip when private originals are
absent, as in a public checkout; synthetic tests need no proprietary inputs.

Source/code snapshots are pinned by `delivery.json`. All eligible code, tests,
findings and manifests were committed and pushed in stages to PR #17. Full Markdown,
audit/model dumps and all game binaries remain outside Git. There is no new game kit.


## Polish catalogue presentation v4 — roster-first headings

The English v3 above stays unchanged. PL-only owner revision:
[Catalogue v4 PL](https://drive.google.com/file/d/146dxudsT9vEzGua6s--Z58s_QP8m_yF0/view)
uses roster name first, followed by differing display name in parentheses; identical
names once. Example `Real PG Gundam (Gundam (Keroro))`. All393name pairs checked,
242headers changed, all other document bytes/order/stats/descriptions untouched.
[PL proof, bundle and reproduction](../reading-script/polish/README.md).
No model/game rebuild or change to numeric facts, uncertainty labels or EN output.
