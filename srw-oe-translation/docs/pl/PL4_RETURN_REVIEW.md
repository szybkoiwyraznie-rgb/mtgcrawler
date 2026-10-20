# PL4 return — guarded merge complete (2026-10-20)

## Source and import

`PL4.zip` from Drive (`1nm7lZttX-XuBY3P-i_twFiM31k1Y2j0V`): 5,254,438 B,
SHA-256 `974d99cea64aa4e96fc14e464c16695ef8e51695e3680d30ff2892a825a20931`,
35 ZIP members/CRC pass. It contains 31 Markdown files: 22 episodes (00–21)
and all nine returned views. The nested translator state was read as data only;
none of its scripts were executed.

The archive stamp matches the earlier source only after a private projection
removes exactly the 32 later, reviewed, PL-only mission rows (22 notes + 10
base-mission titles). The original source fingerprint was not disabled or
rewritten. Those exact 32 local rows are restored in the merged snapshot.

The normal strict source-bound importer accepted all **67,143 explicit PL
blocks**: 0 unknown fields, 0 stale-source refusals, 0 duplicates, 0 hard
validation errors. The independent exact view readback checked all 67,143
blocks / 75,489 backing rows with **0 mismatches**. Six pre-existing rows were
updated; **22,185** package rows became newly nonempty, all in dialogue data.

## Preserved owner work

All **1,283** unique source bindings from the prior owner-UI plans were protected
and restored by immutable source hash, not reused row ID. Of these, 1,251 occur
in the returned views and were overlaid with the exact current local text before
import; 32 promoted mission rows are reinserted directly. The 527-title audit and all v2.6 compact labels, Spirit aliases, terrain, and
executable/system strings remain in the text snapshot; the accepted font/cache
engineering stays in the current patcher code. New translations did not replace
those values.

Episode 13's English reference has a legacy hard-coded “Seishiro” in one line;
the imported Polish line does **not** hard-code that name. Placeholder/token
checks passed. PL remains the edited language; English/reference text was not
rewritten.

The six retained episode-specific TM-fix files contain **57** corrections in
episodes 06, 08, 09, 17, 18 and 21. All 57 were compared to their corresponding
exported Polish view after restoring line-break markers: exact matches, 0 lost
fixes. The added translator brief also retains the rule not to hard-code or
inflect the player's customizable protagonist name. These files were inspected,
never executed.

## Coverage and limits

- Episodes **00–21**: 28,078 of 28,079 visible elements have Polish; the one
  empty element is a Japanese whitespace-only structural row in episode 05, not
  missing dialogue. No unresolved source entries.
- All nine view files imported/round-tripped. The other previously translated
  view categories are unchanged unless PL4 supplied a new value.
- Overall package validator: 87,794 filled / 109,176 text rows; **0 hard errors**
  and 25,165 soft layout/length or review warnings. “0 errors” is not “no UI
  warnings” or runtime approval. Some warning counts are inherited soft limits.
- Episodes 22–34 and the simulator are still unfinished. Empty text stays empty;
  no English fallback was inserted. Story/quote appearance still needs game QA.
- 22,185 new translated source rows map to these **25 DLC EDAT containers**:

  `eventP01.EDAT`, `eventP02.EDAT`, `eventP03.EDAT`, `eventP04.EDAT`,
  `eventP05.EDAT`, `eventP06.EDAT`, `eventP13.EDAT`, `eventP20.EDAT`,
  `eventP21.EDAT`, `eventP22.EDAT`, `eventP23.EDAT`, `eventP24.EDAT`,
  `eventP25.EDAT`, `eventP26.EDAT`, `eventP27.EDAT`, `eventP28.EDAT`,
  `eventP29.EDAT`, `evept101.EDAT`, `evept102.EDAT`, `evept103.EDAT`,
  `evept104.EDAT`, `evept105.EDAT`, `evept106.EDAT`, `evept107.EDAT`,
  `evept108.EDAT`.

  No newly translated row maps to an ISO or PBOOT source. This is exact
  source-container inventory, **not yet an original-asset physical build**.
  The current sandbox lacks the owner's full original ISO/DLC set, so actual
  builder output/readback and exact emitted filenames are not claimed here.

Snapshot materializes byte-for-byte in all PL rows against current `pakiet_EN`;
source hashes, order, EN/JP and other source fields are unchanged. Snapshot data
SHA-256 `876645f90b2bff7f6bfe20a9cf9d563bcb841d14a257c77866fc9d24dbf79585`,
87,783 deduplicated source bindings. Prior UI correction provenance is carried
forward. Count/hash-only merge receipt is in the snapshot manifest and kit's
`translation/PL_COVERAGE.json`; a public-source-safe summary is
`pl4-merge-audit.json`. Static kit **v2.7-PL4** is delivered:
[download](https://drive.google.com/file/d/1T4EPs_7fbJEyAVLIdCmDYLkEtNcWFViF/view),
8,119,658 B, SHA-256
`1156ffc4455a18fbb8b2151afccc71c5f0e352a58b578b2027ff3e06fbafe78d`;
Drive download-back matches byte-for-byte and CRC/90 member hashes pass. Full
suite: **1,727 tests OK, 30 skipped**. Machine receipt:
`pl4-kit-delivery.json`.

**Installation guidance is conditional on a full local build.** When upgrading
an already installed v2.6 kit, the PL4 delta is expected to require the listed
DLC files; the v2.6 ISO and PBOOT need no replacement for these new translations.
If rebuilding from original game inputs/first installation, use the full normal
patcher and keep both output classes it actually reports; this integration did
not run the physical builder, so wait for its local `build_report.json` before
copying anything. Runtime appearance is not tested.
