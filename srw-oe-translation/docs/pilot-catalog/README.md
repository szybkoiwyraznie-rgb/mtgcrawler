# `docs/pilot-catalog/` — Verification & Delivery Manifests

This directory stores the machine-readable manifests backing the Polish pilot, Spirit Command, and skill reference catalogue (`srwoe_pilot_catalog_PL.md`). In keeping with repository rules, full rendered Markdown and proprietary game binaries remain outside Git under ignored `local/` and Google Drive.

## Tracked Manifests

- **`engine-map.json`** — Output of `tools/pilot_catalog_probe.py`: records all `112` Patch 1.08 `DATA.PSP` skill description overrides (`0x0e5d44`), confirms `0` Spirit overrides across `60` records, and records `7,307 / 7,307` exact matches (`0` mismatches) against unmodified MIPS execution of `.text 0x21f4ec` in Unicorn.
- **`verification.json`** — Sanitized output of `tools/verify_pilot_catalog.py`: independent audit of all `21` source container SHA-256 digests, `1.08` executable SHA-256, `pakiet_PL` coverage digest, all `404` character records (`92 + 45 + 117 + 150`), `60` Spirit records, `536` pilot/Ace skill records, zero CJK / control-token leakage, and byte-for-byte canonical Markdown determinism.
- **`delivery.json`** — Google Drive delivery receipt for the `v4.0` edition (`1YsNL3AT6IHqxJdGXeeKwECdVz-uZSjLV`), byte count (`303,266` B, `6,276` lines), SHA-256 (`800a27fdb822fd220aebc77cc20b7ff3ee6526e21b07c7565f74d03e25facc65`), MD5 (`ea1cc66922dfc8b98cc5a2081f77d319`), and byte-identical download-back verification (base-only pilot stats, unlock level `Poz. nauki` + base effect on Spirit Commands & Pilot Skills, pilot IDs omitted, aligned for Notepad++; only the `Karen` -> `Kallen` name fix changed against the `v3.5` copy, which was trashed after `cmp -s`).

## Reproduction Commands

From repository root:

```bash
# 1. Regenerate engine-map.json and replay all 7,307 Unicorn MIPS checks (requires .venv with unicorn)
.venv/bin/python srw-oe-translation/tools/pilot_catalog_probe.py \
  --elf srw-oe-translation/local/eboot_108.elf \
  --containers srw-oe-translation/google_drive \
  --package srw-oe-translation/pakiet_EN \
  --out srw-oe-translation/docs/pilot-catalog/engine-map.json \
  --verify-progression

# 2. Render full Polish catalogue (pure Python 3.11 standard library)
python3 srw-oe-translation/tools/pilot_catalog.py \
  --containers srw-oe-translation/google_drive \
  --elf srw-oe-translation/local/eboot_108.elf \
  --english-package srw-oe-translation/pakiet_EN \
  --polish-package srw-oe-translation/local/pakiet_PL \
  --engine-map srw-oe-translation/docs/pilot-catalog/engine-map.json \
  --out-md srw-oe-translation/local/pilot-catalog/srwoe_pilot_catalog_PL.md \
  --out-json srw-oe-translation/local/pilot-catalog/pilot_catalog_PL.json

# 3. Run independent binary + localization + Markdown audit
.venv/bin/python srw-oe-translation/tools/verify_pilot_catalog.py \
  --containers srw-oe-translation/google_drive \
  --elf srw-oe-translation/local/eboot_108.elf \
  --english-package srw-oe-translation/pakiet_EN \
  --polish-package srw-oe-translation/local/pakiet_PL \
  --source-manifest srw-oe-translation/docs/mech-catalog/source-inventory.json \
  --engine-map srw-oe-translation/docs/pilot-catalog/engine-map.json \
  --markdown srw-oe-translation/local/pilot-catalog/srwoe_pilot_catalog_PL.md \
  --model-json srw-oe-translation/local/pilot-catalog/pilot_catalog_PL.json \
  --out srw-oe-translation/docs/pilot-catalog/verification.json \
  --replay-unicorn

# 4. Run test suite
python3 -m unittest discover -s srw-oe-translation/tests -p 'test_pilot_catalog.py' -v
```
