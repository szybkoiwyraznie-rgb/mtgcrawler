# SRW OE mech catalogue — delivered data-backed edition

**Completed 2026-10-17:** [srwoe_mech_catalog.md on Drive](https://drive.google.com/file/d/1cBbPxTiY-MFASz2H3UJ1aS7SmSD-8uQC/view)
— **761,353 bytes**, SHA-256
`e6891909282eb9d621bdf88229f27e47a942e88705e2110bbc206741693320ef`.
Downloaded back and compared byte-for-byte. One Markdown file, English names and
descriptions from the existing package, supplemented by the matching original game data.

## Coverage

| Category | Result |
|---|---:|
| Registered unit records (friendly/enemy/forms/objects/cinematics/spares) | 393/393 |
| Weapon/action table entries | 1485/1485 |
| Nonzero selectors / zero selectors shown separately | 1274 / 211 |
| Default crew assignments / distinct assigned character IDs | 535 / 201 |
| Native machine-skill references resolved | 514/516 |
| Concrete base descriptions / executable overrides | 249 / 20 |
| Group rosters / distinct explicit member units | 16 / 53 |
| Positive conditional weapon gates | 121 |
| Source-checked, catalogue-only wording repairs | 17 |

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
  **20 not recorded**. The method is labelled per unit; the latter include objects,
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

**1438 passed, 1 skipped, 382 subtests passed** — full project suite, 42.02 s.
Includes **59 new tests**: 33 synthetic + 26 real-input tests. The latter reject
**24 semantic mutations** even after document/audit hashes and sizes are repaired.
Original input and package hashes remained unchanged. Regeneration is byte-identical.

`verify_mech_catalog.py` checks facts against freshly read binary/English sources
without calling the generator's model/description/series helpers. It checks every
Markdown unit/pilot/profile header, complete ability bullet, and all weapon rows.
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
use that folder as `--package` below. The real-input regression test does this
read-only when the working package has changed. No branch switch or checkout is
performed. The delivered Markdown and its original hashes stay unchanged.

Use **original decrypted** config00.cpk, config01–19.EDAT and configst.cpk together
in an ignored input directory, plus the matching original EBOOT.BIN. The commands
below use the flat download directory from this session. Full outputs remain ignored.
Normal generation/verification uses Python 3.11+ and its standard library only.

```sh
python3 tools/mech_catalog.py --configs ../google_drive --package pakiet_EN \
  --elf ../google_drive/EBOOT.BIN \
  --source-manifest docs/mech-catalog/source-inventory.json \
  --engine-map docs/mech-catalog/engine-map.json \
  --errata docs/mech-catalog/description-errata.json \
  --out local/mech-catalog/srwoe_mech_catalog.md \
  --audit local/mech-catalog/catalog.audit.json
python3 tools/verify_mech_catalog.py --configs ../google_drive --package pakiet_EN \
  --elf ../google_drive/EBOOT.BIN \
  --source-manifest docs/mech-catalog/source-inventory.json \
  --engine-map docs/mech-catalog/engine-map.json \
  --errata docs/mech-catalog/description-errata.json \
  --markdown local/mech-catalog/srwoe_mech_catalog.md \
  --audit local/mech-catalog/catalog.audit.json \
  --report local/mech-catalog/verification.json
python3 -m unittest discover -s tests -p 'test_mech_catalog*.py' -v
```

To independently regenerate the engine map, install `unicorn==2.1.4` in an ignored
venv, inventory the inputs, then run the memory-only selector. The map contains
only addresses/IDs/hashes, not game code or full text:

```sh
python3 tools/mech_catalog_sources.py --configs ../google_drive --package pakiet_EN \
  --out local/mech-catalog/source-inventory.json \
  --summary local/mech-catalog/source-summary.json
python3 tools/mech_catalog_engine.py --elf ../google_drive/EBOOT.BIN \
  --package pakiet_EN --inventory local/mech-catalog/source-inventory.json \
  --out local/mech-catalog/replayed-engine-map.json
```

Alternatively add `--replay-engine` to the verifier. `mech_catalog_probe.py` is an
optional field-access research helper (`capstone==5.0.6`); its disassembly output
must remain local. Real-input tests explicitly skip when private originals are
absent, as in a public checkout; synthetic tests need no proprietary inputs.

Source/code snapshots are pinned by `delivery.json`. All eligible code, tests,
findings and manifests were committed and pushed in stages to PR #17. Full Markdown,
audit/model dumps and all game binaries remain outside Git. There is no new game kit.
