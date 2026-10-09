# Local one-command workflow for game files — plan

**Status: plan plus read-only inventory/indexing and CPK batch preparation helpers.** The read-only inventory helper hashes and signature-probes files and now indexes standard ISO9660 PVD directories plus member-start CPK signatures without extracting anything. The batch CPK driver also reports CPK-like ISO members, but only plans or extracts top-level CPK inputs. It defaults to dry-run and has only been tested with synthetic inputs and a mocked converter—not the actual YACpkTool executable or a real `.EDAT`/ISO. No ISO/DLC extraction or rebuilding, CPK repacking, full game pipeline, or translation insertion is validated. No actual ISO/DLC was opened or processed. The candidate and companion auditors continue to operate on the supplied `eventP01.zip` sample.

## User-facing goal

The user should not have to unpack or repack each archive, change extensions, move individual files between tools, or launch a separate command for every game resource. After a one-time choice of the source folder(s), the intended workflow is:

1. Put the user's original base ISO and DLC files in a configured input folder **or** configure read-only paths to the existing ISO and PPSSPP game-data directory.
2. Run one local entrypoint for the whole game set.
3. Read one summary/report and find generated work/build outputs in dedicated directories.

The pipeline should discover supported files recursively by content/signature, batch all of them, and orchestrate the required extract, scan, edit-application, repack, and verification steps. A tool may invoke a lower-level CLI once per archive internally if required; the user must not have to do that orchestration. Original names/extensions are preserved. If a dependency insists on a suffix, any temporary alias belongs inside generated staging and is never a manual rename of the user's source.

The expected source root is usually a directory containing mostly `.EDAT` files and one base ISO; it may be flat and need not already look like a PPSSPP folder tree. The tool must inspect each `.EDAT` by content and report how many are actual CPK signatures versus other/unknown EDAT-like files. It should try to handle the ISO directly; accepting a user-pre-extracted ISO contents directory is a fallback if a verified ISO adapter is not yet available, not a default requirement.

This goal concerns mechanical file handling. Translation wording, terminology review, and approval of uncertain text remain editorial tasks; the pipeline must not silently invent translations or treat heuristic candidates as approved source strings.

## Proposed workspace layout

All large/private files and generated outputs stay under the already-ignored `srw-oe-translation/local/` or another user-selected local workspace. The current files there must not be deleted or migrated automatically.

```text
local-workspace/              # example workspace; this name/location is not required
  local-workflow.ini          # local-only source/tool paths; optional for configured batch helper
  input/                      # optional drop-in mode; preserve supplied names/extensions
  work/<run-id>/              # automatically created extraction/staging/cache
  reports/<run-id>/           # inventory, hashes, warnings, validation results
  output/<run-id>/            # rebuilt local ISO/DLC copies or patch artifacts
```

The workspace may be on the Desktop, alongside the game files, or elsewhere. The converter does **not** have to be placed inside it.

Two ways to provide sources should be supported so a second multi-gigabyte copy is not mandatory:

- **Drop-in mode:** place the base image and the complete DLC/game-data tree under `<workspace>/input/` once; the tool finds them recursively.
- **Existing-path mode:** set the base ISO path and installed DLC root in the local config once. The tool reads these paths without modifying them and writes every intermediate/output elsewhere.

On the user's Windows system, YACpkTool may stay anywhere accessible—for example, in a Desktop folder or beside the game binaries. There is no mandatory `local/bin` location. The batch helper accepts a configured path in an INI file or `--tool`; when no path is set, it searches only next to the script and directly in the configured input root (including a direct `YACpkTool/` child), not recursively across the Desktop/drive. The path is used automatically for every matching archive, with no per-file user launches. Paths with spaces are passed as separate Windows process arguments. If the converter distribution needs DLLs, keep them next to the `.exe` as supplied.

The prepared config interface is `config/local-workflow.example.ini`, with `[local]` keys `input_root`, `output_root`, and optional `tool_path`. Copy it to a private `local-workflow.ini` (under the ignored project `local/` folder or anywhere outside Git) and set those paths once. Relative paths are based on the INI's location; absolute Windows paths are fine. CLI path arguments override config values. The script will not download executables itself; it records the converter executable's SHA-256 in the run report. Do not commit the private config or converter. The later full ISO/DLC orchestrator may extend this config, but should preserve the one-time-path setup.

Proposed eventual command contract (illustrative, **not implemented or runnable yet**):

```text
python srw-oe-translation/tools/local_pipeline.py run --workspace srw-oe-translation/local
```

**Implemented first slice:** `tools/inventory_local_inputs.py <file-or-directory> [--json-out <report>]` recursively inventories paths, records SHA-256/size/content-signature hints, identifies identical files, and skips symlinks. It probes CPK, ZIP, PBP, SFO, and ISO9660 PVD signatures; for a structurally supported 2048-byte-sector ISO9660 PVD it also walks directory records and checks the first four bytes of each regular-file member by extent, reporting CPK signatures and offsets without extracting members. PVD names are used; Joliet/Rock Ridge, interleaved files, and multi-volume images are not supported. Extensions remain hints only. The JSON and console summaries group top-level signatures by extension, so a `.EDAT` input set can be reviewed without renaming. JSON reports must be outside a directory input. This is read-only inventory—not ISO extraction, container validation, an adapter selector, or proof that YACpkTool accepts any member. ISO indexing has synthetic coverage only; no actual ISO/DLC was opened or processed. The supplied `eventP01.zip` was previously inventoried by its ZIP signature only.

**Prepared CPK batch slice:** `tools/extract_cpk_batch.py` accepts direct input/output flags or `--config <private-ini>`. The tracked example is `config/local-workflow.example.ini`; copy it to a private `local-workflow.ini` and set `[local]` keys `input_root`, `output_root`, and optional `tool_path` once. The helper inventories a mixed folder and plans `-L`/`-X` only for top-level CPK-signature files; dry-run is the default. `--execute` invokes the configured/discovered local converter for those top-level inputs, with source hashes checked before/after, per-file staging paths, and unresolved `.EDAT` files reported. Indexed ISO members with `CPK ` signatures are listed separately in the report as inventory-only; they are not staged or extracted. Unsupported ISO inventories are counted explicitly. A Desktop copy can be set once in `tool_path` or passed as `--tool`; there is no requirement to move it into the repo. Ten synthetic batch tests exercise config-relative paths/CLI overrides, planning, mocked command execution, spaces in paths, failure/mutation handling, report-path safety, bounded tool discovery, and separate ISO-member reporting. **Actual YACpkTool CLI behavior, `.EDAT` input acceptance, and extracted outputs are not yet verified.** This driver does not rebuild CPKs or extract/rebuild the ISO.

A `--plan-only`/dry-run mode should be available for the later full orchestrator. The eventual normal run should need no per-file prompts. If there are duplicate candidate base images, missing required DLC, unsupported containers, or conflicting inputs, it should stop with a precise report rather than guess or silently produce a partial build.

## Automated stages

1. **Preflight and inventory**
   - Recursively enumerate inputs and identify containers by magic/content, not just filename extension.
   - Record original path, size, SHA-256, detected signature/type, product/version evidence, and the adapter selected (or an explicit unsupported reason).
   - Recognize duplicate files by content hash; do not process duplicates twice unless their paths have distinct semantic roles.
   - Check free-space needs before extracting large containers, and refuse to place work/output under a source directory.
   - Do not print or commit decoded proprietary text in routine logs.

2. **Base-image and DLC extraction**
   - Accept a flat/mixed input directory containing many `.EDAT` files and one ISO; do not require the user to reorganize or rename it. Confirm a unique base-image candidate from content/product evidence, or report ambiguity.
   - Prefer extracting the ISO automatically and exposing supported game resources under a staging tree while preserving relative paths and a source-to-output map. A pre-extracted ISO tree may be configured as a fallback; the tool must label the run as incomplete if the actual base image was not handled.
   - Scan every `.EDAT` and other source file as a batch. Identify CPK by its `CPK ` content signature even when named `.EDAT`; do not assume every `.EDAT` is CPK or that every DLC file is a CPK. Send unknown/non-CPK `.EDAT` files to explicit classification rather than silently skipping them.
   - For each CPK signature, invoke the configured local YACpkTool automatically into a separate staging directory derived from the original relative path and content hash, preventing basename collisions. Pass the original `.EDAT` path directly; never ask the user to change its extension.
   - Detect nested supported containers by content at each level, subject to recursion/depth limits and safe path handling.
   - Never overwrite source files. If a file is encrypted/unsupported or its format is ambiguous, report it and stop any build that would otherwise omit it.

3. **Read-only resource audit and deterministic extraction**
   - Run the current candidate and companion audits automatically across every matching BIN/resource, not just `eventP01`.
   - Once text boundaries and record semantics are independently validated, export a stable translation table with source resource hash, record ID/offset, original bytes, decoded text, line breaks, and explicit control-code placeholders.
   - Preserve unknown bytes and suffixes. Do not use the Akurasu script as a source.
   - Reject stale translation rows if the source hash or extracted record no longer matches. Keep translated text separate from extracted source data.

4. **Apply translations and rebuild resource archives**
   - This stage remains disabled until extraction and no-change round-trip gates pass and the target text fields, control codes, lengths, and pointer/relocation behavior are understood.
   - Validate encodability, control-token balance, line/box constraints when known, and all length/pointer bounds before writing anything.
   - Rebuild in a fresh staging copy, preserving archive metadata, compression mode, ordering, and alignment as required by the verified format. No in-place edits to originals.
   - If a safe insertion/relocation rule is not known for a row, fail the build with its stable ID; do not truncate text or guess.

5. **Rebuild game containers and verify outputs**
   - Rebuild only explicitly supported base/DLC containers into `output/<run-id>/`; do not replace files in the PPSSPP directory automatically.
   - Re-open every output with the corresponding parser, re-extract it, and compare its member inventory against the expected source-to-output manifest.
   - For unchanged resources, require byte-identical content. For edited resources, verify every intended change and prove that unmodified regions/resources remain unchanged where the format permits.
   - Hash outputs, record validation results, and leave the user's originals unchanged. Do not call an output playable unless a game-load/display test has actually passed.

## Evidence and format gates

| Area | Evidence already recorded | What must be verified before automation can build it |
| --- | --- | --- |
| CPK in `.EDAT` resources | Several user-listed `.EDAT` samples started with `CPK `; YACpkTool extracted `imenu01.EDAT` and `eventP01.EDAT`; an unchanged `DL102_20.bin` was reported byte-identical after a CPK pack/extract cycle. | The user can keep YACpkTool anywhere accessible on Windows (including the Desktop or game folder) and configure its path once; the runner may also auto-discover it in the input root or next to the script. Verify that the tool accepts the original `.EDAT` path by content without renaming; batch `-L`/`-X` inspection/extraction and use `-P` only after no-change repack tests. Do not use YACpkTool's documented experimental `-R` for automated replacement. Pin/hash the executable and verify full member inventory, metadata, compression, and reproducible no-change rebuilds. A member-level round trip is not proof of a full ISO/DLC rebuild.
| Base PSP ISO | The user reported `SRW OE 1.08.iso` and product ID `NPJH50521`; no actual ISO has been opened. A standard ISO9660 PVD-only directory walker now has synthetic tests and detects CPK signatures by file extent. | Validate directly on a copied real image only when available; confirm ISO/UDF/Joliet layout, product/version, paths, alignment/boot metadata, full extraction, rebuild, and re-open/re-extract. The current scanner is inventory-only, ignores Joliet names, and is not an ISO/UMD extractor or builder. Preserve and compare source hash.
| DLC/game-data set | The reported PPSSPP folder contains many `.EDAT` families plus PBP/SFO files; some `.EDAT` samples are CPK. | Inventory the complete user set and identify which assets are direct archives, encrypted wrappers, registration metadata, or unrelated files. Confirm DLC completeness/version and safe output/install behavior.
| Event BIN structure | 22 sample BINs have consistent top-level EDAT/EVNT/ECHK framing and 3,277 heuristic script candidates; candidate boundaries and ECHK semantics are still unproven. | Validate text/record boundaries and controls on independent records/resources before designating the JSONL as translation data or enabling write-back.
| Rendering/in-game QA | No modified string has been confirmed in-game; the user cautioned the supplied fragment may be inaccessible. | Use a genuinely comparable reachable resource if available. If not, record display QA as blocked/unverified; do not claim a playable patch.

YACpkTool is the existing CPK adapter candidate, not a blanket solution for all DLC or the base ISO. Its README documents `-L` for listing, `-X` for extraction, and `-P` for packing; these can be wrapped into one batch run over all signature-matched inputs. Its documented pack codec defaults to `none`, with LAYLA optional; the adapter must detect/preserve the source codec rather than selecting a codec by guess. The README calls its `-R` replacement command experimental, so the proposed pipeline must avoid `-R` and use a fully extracted/repacked archive only after a no-change test. The repository is archived, so pin and hash the user's local executable and record its reported version/help text; do not download or upgrade it automatically. Acceptance of the original `.EDAT` filename by `-i` remains to be tested on a disposable copy. Historical references to other inner formats are leads only. If a source requires decryption or a parser not yet validated, the pipeline must identify that boundary clearly and avoid a partial “successful” build.

## Safety, reproducibility, and error behavior

- **Read-only inputs:** use the source ISO/DLC in place or make a controlled working copy; never modify, rename, delete, or repack the user's originals.
- **Separate outputs:** stage under a unique run directory; publish outputs atomically only after verification; never place a build beside or over its source by default.
- **Content-driven, batch operation:** recurse and dispatch supported files automatically; no extension-edit instructions and no per-file user tool operation.
- **Fail closed:** unknown signatures, conflicting base candidates, missing dependencies, invalid archives, unsupported encryption, insufficient disk space, or uncertain reinsertion rules are reported as blockers. Do not skip them silently.
- **Repeatability:** key cached intermediates by source SHA-256, tool version, and configuration. A repeat run with unchanged inputs should reuse verified work or reproduce the same content manifest.
- **Audit trail:** emit a machine-readable run manifest plus a concise human-readable summary with processed/skipped/error counts, reasons, source/output hashes, tool versions, and test results. Do not log full Japanese text unless explicitly requested to an ignored local export.
- **Local/offline:** once dependencies are installed, processing should not need network access, credentials, or uploads. Pin and verify external tool versions/checksums; keep proprietary inputs, extracted text, and builds ignored/out of Git.
- **No silent claims:** distinguish `inventory complete`, `extraction verified`, `rebuild verified`, and `loaded/rendered in game`. Passing one stage does not imply later stages.

## Implementation milestones

1. **Plan recorded (done):** preserve the one-command, no-manual-packaging requirement and the evidence/unknowns above.
2. **Read-only input inventory (done):** `tools/inventory_local_inputs.py` recursively hashes and signature-probes inputs, reports duplicate content, and does not follow symlinks or modify sources. It indexes standard ISO9660 PVD directories and member-start signatures without extraction; unsupported images remain explicit. Synthetic inventory/ISO tests pass, and the previously supplied ZIP is identified by its ZIP signature. This is not a complete ISO parser/extractor, does not estimate extraction space, and does not validate CPK/YACpkTool compatibility.
3. **Batch CPK adapter (prototype prepared):** `tools/extract_cpk_batch.py` plans/extracts top-level content-detected CPKs, including `.EDAT` names, using one configured local YACpkTool path and separate per-input work directories. It lists CPK-signature files found inside indexed ISOs in the report only; they are not extracted. Ten synthetic batch tests, including a mocked CLI and ISO-candidate reporting, pass. First verify `.EDAT` path acceptance on a disposable copy, pin/hash the executable, and compare complete member manifests/bytes on no-change round trips before treating execution as supported. Do not use its experimental `-R` replacement command.
4. **ISO and DLC adapters:** the current synthetic PVD directory scan is inventory-only. Add extraction/rebuild adapters only after real format samples are available and a copied source can pass extract/rebuild/re-open checks. Detect incomplete or unsupported resources explicitly.
5. **Deterministic text extraction:** validate boundaries independently; define stable IDs/control placeholders; test byte-identical no-change resource reinsertion.
6. **Translation/build pipeline:** only after pointer/length/encoding rules are known; validate translation inputs, batch apply all edits, rebuild archives/images, and report exact output hashes.
7. **End-to-end acceptance:** one user invocation processes all supported inputs without manual unpack/rename/per-file operations; originals hash unchanged; all manifests reconcile; no output described as playable before appropriate QA.
8. **One-click local run, first slice (done; first real run recorded):** `RUN_PIPELINE.bat` and `tools/run_pipeline.py` combine items 2, 3, and 5 in one automatic run. After a one-time folder setup by dialogs, it inventories inputs by content, checks the converter's pinned hash and output path, probes the converter on the smallest CPKs (original `.EDAT` name first; a `.cpk` copy only inside staging as fallback), extracts unique CPKs (nested up to depth 2), exports and verifies event text per package, runs a CPK round-trip gate, and writes `REPORT.txt`. Its tests use a fake converter and a synthetic CPK format. Its first real run on the user's Windows PC completed on 2026-10-09 with console output after a captured-output crash (see `EXPERIMENT_LOG.md`). Items 4 and 6 (ISO unpacking, repacking into the game, insertion) are not automated. A listing check compares each package's `-L` entries with its files by count and name; a package whose entries share a name fails (see the listing entry in `EXPERIMENT_LOG.md`). See [`ONE_CLICK_RUN.md`](ONE_CLICK_RUN.md).

## Immediate scope

Continue read-only identification and small, safe automation steps. The ISO9660 PVD indexer now detects member paths/extents and CPK signatures from synthetic images only; it does not extract anything, and no real ISO/DLC was processed. Do not invent the real image's exact wrapping or select an unverified repacker. Next, validate direct member staging only when a real ISO and disposable format samples are available; meanwhile continue dry analysis of supplied text resources and keep all scanner exports diagnostic, not approved translation tables. No user-side action is needed at this stage.
