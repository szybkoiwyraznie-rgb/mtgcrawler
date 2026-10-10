# Next step — SUPERSEDED PLAN NOTICE

**Do not follow the old measurement route that used to live here.** It is kept in git history
and in `TECHNICAL_FINDINGS.md`/`EXPERIMENT_LOG.md` as context, but it was overtaken on
2026-10-10 by a chain of in-game proofs. **Read `docs/HANDOFF.md` first** — it is the current,
condensed state of the project and the single source of truth for format knowledge, proven
results, tooling and the Google Drive map.

## Where we are (2026-10-10)

- Growth of event strings **works in the real game** (root cause: a stale inner EVNT size
  field at body offset 60 = `EVNTsize - 36`; fixed in `grow_event_text.grow_record`).
- The user **deferred actual translating** to a separate workflow. The job now is the process:
  read / write / unpack ISO / pack ISO, plus readable source files for a translation AI.
- Readable exports exist: `tools/export_strings.py` → `local/strings/*.strings.json`
  (gitignored). Chapter 1 (disc `eventP00.cpk`) = 38 records; DLC `eventP01/02/03/09` =
  100/162/154/3.
- ISO: read-only `iso9660.py` + packing `iso_pack.py` (small images, tested) + `iso_prep.py`/
  `PREP_ISO.bat` (bundle a slice of the big ISO on the user's PC). The disc uses `*.cpk`,
  the DLC `*.EDAT`.

## Immediate next steps (in order)

1. **Apply step** — `tools/apply_strings.py`: read translated `*.strings.json`, enforce
   `max_line_width` (~46 half-width), rewrite records via `grow_record`, rebuild the CPK, run
   the structural gate. (Closes read → translate → write.)
2. **Streaming repack** of the 660 MB disc — `iso_pack` `repack` mode + `REPACK_ISO.bat`,
   run on the user's PC; preserve the 32 KiB system area.
3. **UI / names / menus export** as separate tables (`imenu*`, `mesbmp*`, `u16tbl.cpk`,
   `system.cpk`, `font.cpk`).

Suite is 316 tests OK (1 skipped). See `HANDOFF.md` §6 for the same list with context.
