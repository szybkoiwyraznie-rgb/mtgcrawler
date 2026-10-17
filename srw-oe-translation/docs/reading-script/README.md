# English reading edition — recovery and episode 34

This is **not a new game translation**. Use the English already in `pakiet_EN`;
never use previously generated Markdown as a translation source. See
[the recovered history](../READING_SCRIPT_HISTORY.md) for the delivered 00–33 editions.
The original recovery patch is archived in `../recovered/`.

## Checkpoint: source inventory complete; editorial plan/output still in progress

`episode_34_sources.json` is an independently recomputed inventory, not the lost
agent's plan. It records all seven scenes, 7471 nonempty prose entries and exact
source hashes. The mission-text hash differs from the old history because of the
separate v16 QA fixes; dialogue, scene index and name sources are unchanged.

- seq 251/252/254: three main missions, 134/134/1702 prose entries.
- seq 253: exact reading alias of 252 after joining soft wraps/normalizing CRLF.
- seq 255/256: 306/382 changed/new prose entries relative to 254, each with two
  additional meaningful headings (including **Adeu's card**, a `label`, not a UI
  control to discard). They require individual editorial review.
- seq 257: exact reading alias of **256**, not 254. English, paragraph boundaries,
  entry kinds, speaker identities and meaningful metadata were compared.
- The four `＃？？？` speaker overrides stay anonymous even though their portrait's
  character ID is known. Do not replace them with the character's name.

New read-only tooling and tests are **tracked and pushed**, unlike the lost tools:

```sh
python3 tools/reading_script_source.py --package pakiet_EN
python3 tools/reading_script_source.py --package pakiet_EN --review 254 --start 1 --end 180
python3 tools/reading_script_source.py --package pakiet_EN --review 255 --changed
python3 -m unittest discover -s tests -p 'test_reading_script_source.py' -v
```

The review command prints the full English of each selected entry, never an
ellipsized preview. It does not write to the package. Keep full review dumps,
generated Markdown, detailed audits and bundles in ignored `local/`; deliver the
reading edition on Drive. Commit tools, synthetic tests, editorial plans and
provenance/verification manifests to Git after each coherent checkpoint.

Pending: reviewed scene boundaries/conditional dialogue, rendering, independent
verification including mutation tests, final Drive delivery. Old PASS claims in
the recovered log are historical, not claims that the missing old tests ran here.
