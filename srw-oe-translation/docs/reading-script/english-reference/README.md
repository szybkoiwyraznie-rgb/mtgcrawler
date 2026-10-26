# English reading editions — frozen editorial reference

These 35 files (`srwoe_episode_00.md` … `srwoe_episode_34.md`) are the **editorial
reference** of the Polish reading build. They are committed here so that

```sh
python3 tools/build_polish_reading_editions.py \
  --english pakiet_EN --polish <materialized pakiet_PL> \
  --references docs/reading-script/english-reference \
  --episodes 0-34 --text-source v4.x --out <dir>
```

runs **from repository inputs only** — no Google Drive, no external download.

## What the reference is and is not

- **It is not a translation source.** Every line of the Polish reading editions comes
  from `pakiet_PL` (`00_dialogue`, `05_mission_text`, `06_scenes`,
  `07_names_characters`). No English text is ever copied into the Polish output.
- **It is the plan's checksum.** Each reviewed plan
  (`docs/reading-script/polish/episode_NN.json`) pins `reference_sha256`; the builder
  renews the plan-to-row mapping from the English blocks and refuses to render if the
  file, the mapping or the source bindings (`english_source_sha256`) changed. That is
  what stops a silent scene reordering.
- English and Polish rows are bound to the same physical game rows, so the reference
  is reproducible from the tracked `pakiet_EN` whenever its generating plan is in the
  repository.

## Provenance

- `srwoe_episode_00.md` … `srwoe_episode_33.md`: the files delivered to the `Skrzpty`
  Drive folder, verified byte-for-byte against the `reference_sha256` pinned in the
  Polish plans, then committed here (this is the copy of record; Drive is no longer an
  input).
- `srwoe_episode_34.md`: the delivered copy was lost (Drive returns 404, it is not in
  the folder or the trash), so it was **regenerated on 2026-10-24** from
  `docs/reading-script/episode_34.json` with `tools/build_reading_script.py` after
  refreshing `docs/reading-script/episode_34_sources.json` to the current `pakiet_EN`
  hashes (`05_mission_text`: `9d5ee23c…` → `8c0a8437…`; `07_names_characters`:
  `f0bb7235…` → `88e18fb3…`, the `Karen` → `Kallen` fix). It therefore differs from
  the lost original (`212,920 B`, `4f1c6c3e…`) only in the English name wording
  (`212,780 B`, `75f0cb5f…`), and `docs/reading-script/polish/episode_34.json` was
  re-pinned to the new hash.

`references.json` records the byte size and SHA-256 of every file and is re-checked by
`tests/test_reading_archive_carry.py`. Any change here must be reflected in the plan
pins; the test fails otherwise.

## Consequence for the archive

Because the whole set is now in the repository, **every episode — 34 included — is
rebuilt**, and the reading archive no longer contains any "carried over" member. The
`--carry` option of `tools/build_reading_archive.py` remains available as an
emergency escape hatch, but a normal delivery must not use it.
