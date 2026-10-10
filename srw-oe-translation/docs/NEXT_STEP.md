# Next step: read the answer somebody else already produced

A prior-art survey (milestone 62, `docs/PRIOR_ART.md`) changed the plan. **A working Korean fan patch
exists for this exact game, base and DLC**, and `retro-trans/SRW-Z` — the project this workflow is
modelled on — documents hitting this project's exact wall (no offset table; offsets inline in the
bytecode) and settling it in the emulator rather than by scanning. Continuing to measure bytes is now
the slower route to a question with a known answer.

## Do this first (milestone 62, revised by milestone 63)

**The ISO route is closed.** `certutil -hashfile "D:\SRWOE\SRW OE 1.08.iso" MD5` returned
`3bfd26f800b7b7a635df29f2c0c936ae`, and the Korean base-game patch names `ce57eb21bcdc9bdd6204f63a4fd9f716`
as the original it was built against. Different dumps — byte-exact patching cannot apply, so **do not
download the 54 MB base-game patch**. It is a dump-level difference, not a different game version: our
own measurement already showed this image is 679,243,152 bytes while its descriptor declares
673,710,080.

The DLC route does not touch the ISO at all, so it stands on its own:

1. **Download one archive** — `srwOEKDLC_v250617.7z` (2.9 MB) from the Releases page of
   `z3oo3z/PSP-SRWOEDLC-KPatch`. It holds 73 xdelta patches, an `org` folder, `1.move_org.bat`,
   `2.dlcpatch.bat` and `dlcmd5checker.exe`.
2. **Offer it the PSN-distributed `.EDAT` files** from `D:\SRWOE\NPJH50521` — **copies**, and not the
   decrypted chapter-4 files this project produced. Run their `1.move_org.bat`, then
   `dlcmd5checker.exe`: it verifies every original and prints `모두 일치!` when all match, or names the
   files that do not. **That output is worth pasting back on its own** — it says how many of the 73
   files we can actually learn from.
3. If they match, run their `2.dlcpatch.bat` and keep the patched output in its own folder.
4. **Diff, don't run.** Drop the two folders onto `COMPARE_PATCH.bat` — the `org` folder first (the
   originals), the patched folder second. Paste the console output back; `patch_diff.json` keeps every
   per-file row.

   The report answers: how many files changed; **how many changed length** (0 means every string was
   replaced at identical byte length — the byte-budget question); where the changed bytes sit (inside a
   text span, on the `FF FF` marker, on the `00 00` stop, or outside any unit); how many units were
   touched; **how many changes also cover the 8 bytes before an `FF FF`** (the record header, which is
   where an offset operand would have to be rewritten); and the byte classes of the replacement bytes
   (ASCII vs SJIS-range vs EUC-KR-range — the encoding question, which is also the font question;
   `0xE0`–`0xFC` is a lead byte in both, so read the mix rather than one label).

One caveat to expect: the patch's unit of distribution is the **`.EDAT`**, so the diff's two sides may
both be encrypted. That still answers how many files changed, by how many bytes, and whether the
length moved — but reading the changed *content* needs the patched file decrypted the same way chapter
4 was. If the diff comes back as noise-sized changes across all 73 files, that is the reason, and the
follow-up is to decrypt one patched file and diff that instead.

Boundary: format knowledge only. No translated text is taken from those projects — the user asked for
a fresh translation and rejected the Akurasu script as a source. The tool reports counts and offsets
only and never decodes text.

The rest of this page is the record of the measurement route that led here, kept because its negative
results are what make the diff worth reading.

## What the last run settled (milestone 57)

- **All 8 chapters are in.** 45,325 units from 91 packages, including `eventP00` (1,582 units) from
  the disc ISO — chapter 1 — and `eventP04`/`evept104` (3,520/3,562) from the decrypted chapter-4
  `*04` packages, which are readable CPK containers.
- **The CPK table check agrees on 495 of 497 packages.** The two mismatches are `robo01`/`robo03`,
  where one listed name each does not decode from the converter's console output — a name problem,
  not a table problem. Matching blob-layout rows by ID removed the four mismatches from the run before.
- **Colliding-name recovery is complete**: all 42 packages, `listing sizes match: True`, 0 compressed
  entries. Those packages still fail the listing gate (the converter writes one file per name), so
  their entries stay read-only.
- **No length prefix.** Not one of the 96 delta/width/endian configurations beats its
  matched-distribution null (best +0.6% lift over 163,523 units). The scan covers every unit, so a
  length field covering the event text would have shown about +25%.
- **No nested strings.** 4,757 inner `FF FF` markers inside units, 0 of them followed by wide-script
  Japanese (1,050 followed by ASCII only).
- **No fixed record layout.** Gap `mod 4` is spread over all four remainders and the pitch is `>256`
  for 114,498 of 163,523 units.
- **The pointer scan was inconclusive, not negative.** It searched 1,382 of 163,523 u32 offsets
  before its byte budget ran out on the huge battle files, and 93,113 offsets do not fit in u16.
- **Companion files:** `_Entry.dat` shares nothing with the BINs (0 of 5,472 runs of 6+ bytes);
  `_ext.dat` shares a little (12 of 242 runs, 11 distinct payloads of 10–24 bytes).
- **A structure worth chasing:** 88% of two-byte suffixes are `00 C9`, and the most common six bytes
  after the text are `0000C9000000` (×8,303). `C9 00 00 00` is 201 little-endian, and the event
  blocks' ECHK chains are known to end at u32 200 — a coincidence so far, not a finding.

## What the re-measurement found (milestone 60)

The text cohort is the script, and it behaves: no length prefix, no nested strings, suffixes of only
0/2/3 bytes, 45.1% of its bytes are text units and 0.4% unselected marker spans. It also produced the
project's first structural signal — **the units' text-start offsets occur as u32 little-endian values
in the same files, 6,335 times against 1,258 for `start + 1` and 528 for `start + 2`, where a
synthetic corpus of the same size, density and pre-marker structure gives 776 against 750 and 509.**
Marker offsets are not elevated, so whatever is involved refers to the byte after `FF FF`, not to the
marker. (The exact counts move a little between runs, because the pointer scan is budgeted and reports
how much of it searched: 39,132 of 45,252 offsets in the latest run.)

It is not an ordinary offset table: the 4-byte-aligned scan shows nothing (548 vs 542), big-endian
shows the same lift as little-endian, and the matches are spread evenly over the whole file.

**And the follow-up measurement came back negative too** (milestone 61): 98.4% of those matches sit
more than 256 bytes from the offset they encode, and the rest scatter over ~67 distances at 1–6 each
— the same picture a synthetic file with no references produces. The same-parity control `start + 2`
(528) sits *below* `start + 1` (1,258), so the excess belongs to the exact offsets, not to parity.
What that measurement could not see is a record pointing at *another* line, which sits at an
arbitrary distance by definition — so the probe now attributes every match to the record holding it.

## What changed since (milestone 58)

The pooled numbers above mix the script with 523 MB of battle data: 118,198 of the 163,523 measured
units came from the 42 recovered `bacb*`/`bseq*` exports, none of which is prose. The probe now
measures every export on its own and splits them into a `text` and a `binary` cohort (32 prose
exports / 45,252 units versus 82 binary exports / 118,271 units on the real manifests), samples
pointer offsets evenly instead of taking the first N, limits the expensive unaligned search to u32
with explicit coverage counters, measures u16 with the complete aligned scan, and reports every
truncation. `REPORT.txt` gains a `by cohort` section; `boundary_probe.json` gains `cohorts`,
`per_export`, and `text_share`.

## Immediate next step (what the user does next)

1. Download the branch ZIP: https://github.com/szybkoiwyraznie-rgb/mtgcrawler/archive/refs/heads/arena/c656a5df-mtgcrawler.zip
2. Unpack it anywhere (for example the Desktop), open `srw-oe-translation`, and double-click
   **`RUN_PROBE.bat`** — not `RUN_PIPELINE.bat`.
3. It will probably ask which run folder to measure, because a fresh download has no
   `config\local-workflow.ini` (that file is private to your PC and is not in the ZIP). Then either
   **drag the run folder onto `RUN_PROBE.bat`** in Explorer — `D:\SRW_OE_out\20261010-142640`, or the
   whole `D:\SRW_OE_out` and it picks the newest run inside — or paste that path at its
   `Run folder:` prompt and press Enter. If you unpack over the folder that already ran
   `RUN_PIPELINE.bat`, the saved settings are reused and it finds the run by itself.
4. Wait about a minute. It is read-only, calls no converter, extracts nothing, and replaces only
   `boundary_probe.json` in that run folder. Keep the console window open.
5. Copy the whole console output and paste it back to the agent. The lines that decide the next
   milestone are now inside the `text` cohort: `the u32 le start-offset matches by the record holding
   them` (a small negative distance means a header field), `what those stored offsets point at,
   relative to that record` (`own start+0` means self-reference, a constant positive value means a
   chain to the next line), and `those matches cover N distinct offsets` (one match per offset reads
   as a line table). If more detail is needed, send the new `boundary_probe.json` from the same
   folder.

No new extraction is needed, so nothing about the game files is touched. If the run folder has been
deleted, `RUN_PIPELINE.bat` reproduces it in 5–8 minutes.

What the agent does with the output:

- **If the matches cluster at one position inside the records** (for example every match 8 bytes
  before a record's `FF FF`, all pointing at their own line or at the next one), that is the game's
  own string addressing, and the next milestone pins down that record layout — the first validated
  structure in the project.
- **If they scatter the same way again**, the excess matches are not references, and the boundary
  evidence is exhausted: the units stay candidates and the next evidence has to come from outside
  these files (another resource/version, or the game's own records) — not from translation.
- Either way the run also re-states what is already settled for the text cohort: no length prefix,
  no nested strings, only 0/2/3-byte suffixes, and 45.1% of the event bytes covered as text.

## The endgame, mapped to SRW Z's workflow

The user's stated end goal (2026-10-09): **the whole game translated to English and delivered as a patch**, like `retro-trans/SRW-Z` (an `.xdelta` patch applied to the user's own Japanese image). SRW Z's pipeline maps to ours:

| SRW Z (`retro-trans/SRW-Z`) | This project | State |
| --- | --- | --- |
| `extract_script.py` — every string to editable JSON | extraction + text-unit export (`tools/extract_event_text.py`, the one-click run) | done for all 8 chapters (45,325 units; boundaries still heuristic, three hypotheses ruled out) |
| translate the `text` fields | translation phase (English; style guide + terminology glossary), workspace `translation/units.csv` + `tools/translation_tools.py check` | workspace done, no rows translated |
| `apply_script.py` — write back, exact round-trip | reinsertion + CPK container rebuild | not built |
| gates before every build (`verify_pointers.py`, `verify_elf_patches.py`, `integrity.py`) | listing check + CPK table check | in place |
| verify against the image (not a tool's report) | PPSSPP / in-game QA | not done |
| `.xdelta` patch packaging + releases | xdelta patch builder (ISO + DLC files) | not started |

Honest open items before the translation phase can start: validation of the heuristic text boundaries (45,325 units are candidates, not confirmed strings — a length prefix, nested strings, and a fixed record pitch are ruled out, the pointer question is open). Coverage is no longer one: chapter 1 comes from the ISO and chapter 4's decrypted packages extract. The colliding-name entries are recovered for **reading**; rebuilding those containers completely is still open, because the converter writes one file per name.

Keep repack, write-back, insertion, and ISO rebuilding blocked until extraction and exact round-trip tests pass and boundaries are independently validated.

The agent sandbox has neither the game files nor the converter, so the agent does not read the user's ISO or DLC; only the user's machine runs the pipeline. Keep the restored sample, exports, and decoded text under ignored `local/`.

Earlier entries below stay as the historical record of the audit. Their counts remain valid for the same sample.

## Local workflow progress (synthetic-only)

The one-command workflow now has a read-only ISO9660 PVD indexer that lists member paths/extents and flags `CPK ` signatures, including signatures crossing adjacent multi-extents. The batch report separates these nested candidates from top-level `.EDAT`/CPK inputs, but does not stage or extract them. This was tested only with synthetic images; no actual ISO/DLC or converter was opened, and no user-side action is needed now. See `LOCAL_WORKFLOW_PLAN.md` for current support limits.


## Completed on the supplied archive

- Audited all 22 BIN files with a prefix-aware CP932 heuristic: 3,277 Japanese-script candidates, including 36 half-width-Katakana-only matches kept for review.
- Generated a local JSONL candidate export with unique file/offset IDs, exact source-prefix bytes, decoded CP932 text, raw suffix bytes, wide/half-width script counts, review flags, and CR/LF counts.
- Added an optional no-filter inventory for all 3,477 literal `FF FF` starts, including all 75 alternate starts, nested/overlapping markers, empty spans, and any unbounded tails. The export records offsets, raw hex, prefix/suffix split, CP932 quality, script/ASCII/PUA/control signals, and role flags without promoting rows to the candidate table.
- Verified all 3,477 inventory IDs and byte ranges against the ZIP members: every marker, prefix-plus-suffix, raw span, and stopping pair matched; zero boundary/byte mismatches. All spans were bounded. The alternates yielded 25 half-width-only matches but no wide-script/punctuation match; no prefix had an ASCII printable run of at least three characters or a non-ASCII letter/number without recognized Japanese script. A follow-up parent/framing check found all 75 alternate starts stop no later than their nearest greedy parent and fit, including the terminal pair, in the same valid EVNT block after its ECHK terminal. The 25 half-width-only alternatives remain review-only, not new wide-script strings. See `CANDIDATE_SCAN_AUDIT.md`; all spans remain heuristic, not validated strings.
- Added `tools/audit_event_dat_runs.py` to inventory every nonempty NUL-delimited run in all 66 companion `.dat` files, without filtering out binary-looking data. Its ignored local JSONL contains 6,288 rows; every ID/raw byte range/NUL boundary was verified (zero mismatches). A stricter cohort finds 42 `_ext.dat` runs with at least two wide-Japanese codepoints, exact CP932 roundtrip, and no controls/PUA/replacements: 20 are copies of one 48-byte payload at `0x18`/`0xB8`, and 22 unique 10–28-byte payloads occur at `0x158`. Two of the latter (`SM001_ext.dat@0x158`, `SM002_ext.dat@0x158`) begin with the same nine ASCII letters, then LF, then five or nine wide-Japanese codepoints; the ASCII sequence occurs nowhere else in the sample. All 42 are bounded by NUL on both sides; the seven LF bytes occur once each in seven `0x158` runs (five at relative byte 3, two at byte 9), while the repeated 48-byte runs have none, and no cohort run contains CR. These are the strongest DAT text-like leads, not confirmed strings. `_Entry.dat`/`_edit.dat` remain noisy and no run is promoted automatically. A metadata-only `_Entry.dat` profile also keeps 222 runs with exactly one wide-Japanese codepoint visible: 86 meet strict/exact CP932 and control/PUA/replacement checks, with 50 unique payloads, 18 repeated groups covering 54 rows, and offsets concentrated at modulo-64 `0x12`, `0x16`, and `0x1A`. They remain one-codepoint review leads, not confirmed text. A synthetic CLI test covers this summary while asserting no source values appear in stdout; that milestone passed 59 tests, and the current combined suite has 66.
- Added `tools/audit_event_bin_nul_runs.py` to inventory all 33,827 nonempty NUL-runs in the 22 BINs and flag overlap with every `FF FF` envelope. Outside all marker spans, 263 runs have at least two wide-Japanese codepoints; all are NUL-bounded, and 257 are strict/roundtripping CP932 without PUA, replacement, or non-newline-control flags. The six remaining wide-script rows are all NUL-bounded but carry one raw `0x01`/`0x02` control byte; two `DL103_20.bin` rows are exact duplicate payloads. Keep them as control-bearing leads, not confirmed strings. These 257 leads contain 216 unique payloads (247 include kana, 220 Japanese punctuation), three of which recur in four marker candidate prefixes; they include 279 LF bytes and 29 CRLF pairs and occur in every BIN. The same scan inventories 525 raw printable-ASCII NUL-runs >=3 bytes (180 unique); all letter-bearing rows are 4–6 bytes, and the 177 runs >=8 bytes have spaces but no letters. The only letters-plus-space run is the EDAT header at `DL103_12.bin@0x00000000`. Keep no-space ASCII rows as potential identifiers/fields, not auto-labeled English text. A pre-run 16-byte relation covers 134 NUL-runs (133 clean wide-Japanese outside-marker rows), but its correlated extent strictly decodes as CP932 for only 78/133; never use it to trim. Two 52-byte rows (`DL105_30.bin@0x2FEC`, `DL105_40.bin@0x3A30`) share a 16-byte printable-ASCII sequence found only at those two locations among the sample members. The all-run JSONL is ignored local; no rows are auto-promoted.
- Extended `tools/audit_event_codecs.py` to compare CP932/Shift-JIS over every BIN marker prefix, all 33,827 BIN NUL-runs, and all DAT runs, without printing text. In the 257 clean wide-script BIN NUL-runs outside marker spans, all round-trip under CP932; 15 are CP932-only under Python `shift_jis`, and two more map U+FF0D to U+2212, with no length change. The 3,277 marker-candidate cohort still has five CP932-only strict prefixes, 27 failures under both, and 82 mapping-different rows at 93 punctuation positions (90 U+FF5E/U+301C and three U+FF0D/U+2212); all 42 clean wide-script `_ext.dat` leads round-trip identically under both codecs.
- Verified all 3,277 IDs are unique. Of the proposed prefixes, 3,250 strictly decode and 3,249 round-trip; 27 non-strict prefixes are all in the 36 half-width-only candidates. All 627 single-NUL prefixes contain wide-script Japanese and strictly decode/byte-round-trip under CP932 (7–123 bytes, median 59); none of the suffixes has a wide-script match, though 497 suffix byte sequences decode to half-width kana by possible binary-field coincidence. The suffixes are 2–3 bytes total: 495 contain a single byte after the NUL, and 132 contain a two-byte tail with one raw `0x01`/`0x02`/`0x03` byte. Keep the suffix interpretation provisional.
- Counted 430 CR and 2,463 LF bytes in the candidate prefixes; all CRs form CRLF pairs, and no CR/LF occurs in the recorded single-NUL suffixes.
- Mapped all 116 NUL-delimited runs in the 22 fixed-size `_ext.dat` files: they occur at eight offsets from `0x000`/`0x001` through `0x182`. The 47 script-bearing runs include five two-byte half-width/control leads at `0x00`, likely binary/header false positives; 42 pass the stricter wide-script CP932 cohort. Fifteen files also have one-byte `0x01` runs at `0x180` and `0x182`. These offsets and values are recorded without field semantics.
- Audited `_edit.dat` and `_Entry.dat` numeric values against BIN sizes and heuristic candidate ranges. Some values overlap candidate ranges, but this does not establish pointer semantics or table relationships.
- Verified exact EDAT/EVNT framing relations across all 22 BINs: outer size/count words match, all 319 EVNT size-like values end at the next EVNT tag or EOF, and every EVNT is followed by ECHK at `+12`. All 3,277 heuristic candidate spans also fit wholly inside one EVNT block.
- For all 332 ECHK markers, `q + 8 + u32(q + 4)` ends at another ECHK tag in 13 cases or before a u32 value of 200 in 319 cases. Following endpoints from all 319 EVNT `+12` ECHK tags yields chains ending at u32 200; chain lengths 1 (309), 2 (7), and 3 (3) match EVNT `+8` in every block.
- The ECHK `+4` values always equal `4 + 20*n` for `n=1..5`; partitioning as a 4-byte prefix plus 20-byte rows gives 1,066 tentative rows whose second u32 is zero. Summed per chain, row totals per block are 1 (22), 2 (44), 3 (99), 4 (139), 5 (6), 6 (5), 7 (1), and 12 (3). This is a repeated candidate layout, not a decoded ECHK schema.
- All 3,277 heuristic `FF FF` candidate markers occur after their block's terminal u32 200, with no before-terminal/unclassified markers; the minimum distance from the byte after 200 to a marker is 34 bytes. Candidate spans remain heuristic and unvalidated.
- `inspect_echk_chain()` is wired into framing and candidate-coverage summaries; ECHK row observations are stratified by chain position, c2 is compared numerically with candidate ranges, and CP932 byte-boundary alignment is checked. The latter is inconclusive (300/539 available boundary hits versus a 50.7% matched-candidate baseline; 540 total prefix overlaps).
- The candidate scanner now includes half-width Katakana in prefix matching, gates candidates on the proposed pre-NUL prefix, and exports wide/half-width counts plus review-only flags. Its wide-script ranges include Japanese iteration/long-vowel marks and CJK compatibility ideographs; that coverage update changes codepoint counts but adds no archive candidate IDs. Of 3,277 candidates, 36 are half-width-only and 27 of those fail strict CP932 decoding; overall 3,250 prefixes strictly decode and 3,249 round-trip. Nested markers, private-use/control codepoints, short matches, invalid CP932, and half-width-only matches remain review flags, never automatic exclusions.
- Among the 117 non-Japanese prefixes, 39 contain 59 CP932 private-use codepoints (U+F8F2/F8F3); 20 such prefixes strictly round-trip and 15 have nested `FF FF`. They are counted but not emitted because marker-adjacent `FE`/`FF` bytes can decode into the private-use area, and gaiji versus control/binary use is unproven.
- A separate punctuation review finds 35 script-free prefixes in 12 BINs; 34 strictly round-trip, 33 contain only Japanese punctuation plus CR/LF, and none has a single-NUL suffix. Twenty-two share the codepoint pattern U+2026/U+2026/U+3002. All 35 lie within EVNT blocks after ECHK terminal u32 200 (minimum gap 34 bytes); every such block also contains a main Japanese-script candidate, with 33 punctuation leads preceded and 33 followed by one. They appear plausibly textual but stay outside the main candidate table and range calculations; the decoded supplement is ignored local output.
- A reproducible cross-BIN control now tests each c2 value against candidate spans from other BINs. Full-span rates are 51.3% paired-BIN and 45.4% other-BIN overall, but only 9/22 source BINs have a positive nonzero lift (mean -5.0 pp; median -6.5 pp); repeated values and related layouts make this a coarse non-independent control, not pointer evidence.
- The auditor also tests six simple record-relative c2 formulas. None gives more candidate hits than raw absolute offsets, and only 68–81/171–175 nonzero targets that land in the owning EVNT block hit a candidate under these formulas. The formulas are exploratory, not a validated address model.
- Forty-two synthetic candidate/companion/DAT-run/codec/BIN-run tests cover marker-quality flags; half-width-only, malformed-CP932, suffix-only, nested/overlapping/all-marker and NUL-run exports; private-use-only, punctuation-only, compatibility-ideograph, Japanese script-mark, EVNT/ECHK framing/context, nonsemantic DAT/BIN review profiles, marker-overlap classification, metadata-only CLI output, and CP932-vs-Shift-JIS cases; endpoint traversal; malformed/truncated boundaries; marker gaps; segment aggregation; paired/unpaired c2 counts; and synthetic EVNT-relative targets. Seven tests cover read-only local inventory signatures/recursion/hashes/duplicates/symlinks/report safety; nine more test CPK batch planning, mocked `-L`/`-X` calls, path-with-spaces handling, failure/mutation/report-path checks, bounded converter discovery, and one-time INI path resolution/overrides. All 58 tests pass. The sample's 49 nested-marker starts yielded no wide-script inner-prefix matches or new matches absent from their parent prefix.

See [`CANDIDATE_SCAN_AUDIT.md`](CANDIDATE_SCAN_AUDIT.md) for detailed counts, archive/member hashes, and caveats. The JSONL remains a diagnostic candidate table, not an approved translation table.

## Next agent-side work

1. The current archive's c2/candidate, CP932-boundary, cross-BIN control, and simple base-offset checks are inconclusive; the pooled same-BIN lift is not consistent across source files, and tested record-relative formulas do not improve candidate alignment. If an independent event resource/version becomes available, repeat the comparisons and test candidate starts, prefix offsets, span ends, and address hypotheses; until then keep c2 uninterpreted, not a pointer.
2. The single-NUL split now has a metadata profile: all 627 proposed prefixes round-trip as CP932, while the short suffixes include byte-field-like values and no wide-script Japanese. This still is not independent boundary evidence; preserve the full marker span, proposed prefix, and raw suffix separately until another resource/version or a validated record layout confirms the split.
3. The 75 alternate marker starts have been checked against parent-span stops and EVNT/ECHK framing: none adds bytes beyond its nearest selected stop, and none adds a wide-script or punctuation candidate. Keep the 25 half-width-only alternatives and residual no-script/PUA prefixes as review-only rows; no promotion follows from CP932 validity or EVNT containment alone. Continue separate context review of the 263 NUL-bounded wide-script BIN runs outside marker envelopes (257 clean strict/roundtripping leads); do not merge them into the marker table or translate them until boundaries are independently supported.
4. Review the `_ext.dat` cohort against surrounding bytes/header words: 20 identical 48-byte runs at `0x18`/`0xB8` and 22 unique 10–28-byte runs at `0x158` pass strict CP932/roundtrip and control-free diagnostics, but their field semantics are not known. Review the two mixed Japanese/ASCII runs in that final group separately. For `_Entry.dat`, examine the 64-byte-relative `0x1A` run lattice (569 runs, all NUL-bounded on both sides; most seven-byte/control-bearing/half-width) and the five clean seven-byte examples in `DL102_90_Entry.dat`; an exact-byte search found each only at its own offset in the 88 sample members, but this does not establish string or identifier semantics. Keep the eight two-wide-character runs as noisy leads. One five-byte, two-wide-codepoint sequence with a trailing `0x03` repeats at `DL104_30_Entry.dat@0x00DC` and inside two longer runs in the same file; the surrounding `0x02`/`0x03` controls and field meaning remain unknown, so retain full raw runs. Use byte context and record comparisons; do not interpret any of these as translated text until boundaries/structure are independently understood.
5. The read-only inventory helper currently has only been run on the supplied ZIP sample. It now reports signatures by extension, so it can distinguish `.EDAT` files with `CPK ` signatures from other `.EDAT` files in the expected flat root. When the full source set is available, inventory the directory containing those files and the single ISO before enabling extraction; do not modify or rename inputs.
6. Validate the one-click run (`tools/run_pipeline.py`, milestone 35; see `ONE_CLICK_RUN.md`) and the older batch driver `tools/extract_cpk_batch.py` with the user's locally stored YACpkTool distribution on disposable copies. The batch driver's default is dry-run; a private `--config <local-workflow.ini>` carries the Windows input/output/converter paths once, and `--execute` batches every content-confirmed CPK (including original `.EDAT` names) through `-L`/`-X` into collision-safe output folders. Verify actual `.EDAT` path handling, complete no-change member hashes, and source immutability; do not use the tool's experimental `-R` replacement mode.
7. Prefer an automated reader for the single ISO. If no verified reader is available, accept a user-provided pre-extracted ISO contents tree as an explicit temporary fallback and mark base-image processing incomplete; do not make manual ISO extraction the default.
8. A stable source inventory with explicit control-byte placeholders now exists (`tools/extract_event_text.py`, milestone 34), with byte-identical no-change checks. Keep its boundaries heuristic until text/record boundaries are supported by independent evidence, and add no reinsertion until then.
9. Validate full CPK rebuild/re-extraction on a disposable copy. If a reachable event using the same rendering path can be identified, use it for a short display test; otherwise record in-game text QA as blocked/unknown rather than requiring access to an unreachable fragment.

## In-game test access

The user cautioned that the event fragment represented by the supplied data may not be reachable in their current playthrough. This does not block read-only format analysis, extraction, or byte-identical round-trip work. Do not make reaching that specific fragment an immediate prerequisite for progress; any eventual rendering test should use a reachable equivalent only if its resource/rendering path is genuinely comparable.

The one-click run (`RUN_PIPELINE.bat`) is now the intended user workflow. The batch driver below remains for dry-runs and comparison.

Plan a batch CPK extraction from a mixed Windows input folder (default is dry-run; the output path must be separate and fresh):

```text
python srw-oe-translation/tools/extract_cpk_batch.py "<game-input-folder>" --output "<separate-output-folder>" --tool "<path-to-YACpkTool.exe>"
```

Only after validating the converter on disposable copies, `--execute` invokes it for each CPK-signature file; this has **not** been run with the real YACpkTool executable yet.

For one-time Windows setup, copy `config/local-workflow.example.ini` to a private `local-workflow.ini`, edit its `[local]` paths (the converter can be on the Desktop or beside the game binaries), then use this one-command dry-run:

```text
python srw-oe-translation/tools/extract_cpk_batch.py --config "<path-to-private-local-workflow.ini>"
```

Once the real converter has passed disposable-copy checks, add `--execute` to that command to batch-extract the CPK-signature files. The config paths remain set for later runs.

Run the read-only inventory against the supplied archive (signature/hash only; no extraction):

```text
python srw-oe-translation/tools/inventory_local_inputs.py srw-oe-translation/local/eventP01.zip
```

Optionally write a local JSON report outside the input file, for example to ignored `local/reports/`:

```text
python srw-oe-translation/tools/inventory_local_inputs.py srw-oe-translation/local/eventP01.zip --json-out srw-oe-translation/local/reports/eventP01_inventory.json
```

Reproduce the candidate audit and local JSONL export:

```text
python srw-oe-translation/tools/audit_event_candidates.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_candidates.jsonl --export-punctuation-review-jsonl srw-oe-translation/local/eventP01_punctuation_review.jsonl --export-marker-inventory-jsonl srw-oe-translation/local/eventP01_all_markers.jsonl
```

Reproduce the companion audit without printing Japanese source text:

```text
python srw-oe-translation/tools/audit_event_companions.py srw-oe-translation/local/eventP01.zip
```

Inventory every nonempty NUL-delimited `.dat` byte run (the optional JSONL contains decoded source and must stay in ignored `local/`):

```text
python srw-oe-translation/tools/audit_event_dat_runs.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_dat_nul_runs.jsonl
```

Inventory all nonempty NUL-delimited runs in BINs, annotating overlap with every literal-marker envelope (the JSONL contains decoded diagnostics and must remain in ignored `local/`):

```text
python srw-oe-translation/tools/audit_event_bin_nul_runs.py srw-oe-translation/local/eventP01.zip --export-jsonl srw-oe-translation/local/eventP01_bin_nul_runs.jsonl
```

Compare Python CP932 and Shift-JIS across BIN marker prefixes, all BIN NUL-runs, and companion DAT runs without printing decoded source:

```text
python srw-oe-translation/tools/audit_event_codecs.py srw-oe-translation/local/eventP01.zip
```

Synthetic tests are in `tests/test_audit_event_candidates.py`, `tests/test_audit_event_companions.py`, `tests/test_audit_event_dat_runs.py`, and `tests/test_audit_event_bin_nul_runs.py`.
