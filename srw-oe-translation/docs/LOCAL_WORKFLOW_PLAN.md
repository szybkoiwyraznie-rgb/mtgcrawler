# Local one-command workflow for game files — plan

**Status: plan plus a first read-only inventory utility.** The inventory helper hashes and signature-probes files, but it does not extract archives, process the ISO/DLC, run the full game pipeline, or insert translations. The candidate and companion auditors continue to operate on the supplied `eventP01.zip` sample.

## User-facing goal

The user should not have to unpack or repack each archive, change extensions, move individual files between tools, or launch a separate command for every game resource. After a one-time choice of the source folder(s), the intended workflow is:

1. Put the user's original base ISO and DLC files in a configured input folder **or** configure read-only paths to the existing ISO and PPSSPP game-data directory.
2. Run one local entrypoint for the whole game set.
3. Read one summary/report and find generated work/build outputs in dedicated directories.

The pipeline should discover supported files recursively by content/signature, batch all of them, and orchestrate the required extract, scan, edit-application, repack, and verification steps. A tool may invoke a lower-level CLI once per archive internally if required; the user must not have to do that orchestration. Original names/extensions are preserved. If a dependency insists on a suffix, any temporary alias belongs inside generated staging and is never a manual rename of the user's source.

This goal concerns mechanical file handling. Translation wording, terminology review, and approval of uncertain text remain editorial tasks; the pipeline must not silently invent translations or treat heuristic candidates as approved source strings.

## Proposed workspace layout

All large/private files and generated outputs stay under the already-ignored `srw-oe-translation/local/` or another user-selected local workspace. The current files there must not be deleted or migrated automatically.

```text
local/
  config.toml                 # optional, local-only input paths and build settings
  input/                      # optional drop-in mode; preserve supplied names/extensions
  work/<run-id>/              # automatically created extraction/staging/cache
  reports/<run-id>/           # inventory, hashes, warnings, validation results
  output/<run-id>/            # rebuilt local ISO/DLC copies or patch artifacts
```

Two ways to provide sources should be supported so a second multi-gigabyte copy is not mandatory:

- **Drop-in mode:** place the base image and the complete DLC/game-data tree under `local/input/` once; the tool finds them recursively.
- **Existing-path mode:** set the base ISO path and installed DLC root in the local config once. The tool reads these paths without modifying them and writes every intermediate/output elsewhere.

The config may record the expected product ID (`NPJH50521`) and selected base/DLC roots. It must not contain credentials. It is local-only and must never be committed. The exact config schema and final command name are implementation decisions, not established interfaces.

Proposed eventual command contract (illustrative, **not implemented or runnable yet**):

```text
python srw-oe-translation/tools/local_pipeline.py run --workspace srw-oe-translation/local
```

**Implemented first slice:** `tools/inventory_local_inputs.py <file-or-directory> [--json-out <report>]` recursively inventories paths, records SHA-256/size/content-signature hints, identifies identical files, and skips symlinks. It probes CPK, ZIP, PBP, SFO, and an ISO9660 PVD signature; extensions are hints only. Its JSON report must be outside a directory input. This is a read-only signature inventory—not a parser, extractor, container validator, or adapter selector—and the ISO/CPK signatures do not by themselves prove that rebuilding is supported. It has synthetic coverage and has been run on the supplied `eventP01.zip` only.

A `--plan-only`/dry-run mode should be available for the later orchestrator. The eventual normal run should need no per-file prompts. If there are duplicate candidate base images, missing required DLC, unsupported containers, or conflicting inputs, it should stop with a precise report rather than guess or silently produce a partial build.

## Automated stages

1. **Preflight and inventory**
   - Recursively enumerate inputs and identify containers by magic/content, not just filename extension.
   - Record original path, size, SHA-256, detected signature/type, product/version evidence, and the adapter selected (or an explicit unsupported reason).
   - Recognize duplicate files by content hash; do not process duplicates twice unless their paths have distinct semantic roles.
   - Check free-space needs before extracting large containers, and refuse to place work/output under a source directory.
   - Do not print or commit decoded proprietary text in routine logs.

2. **Base-image and DLC extraction**
   - Extract the PSP base image and recursively expose supported game resources under a staging tree while preserving relative paths and a source-to-output map.
   - Scan the DLC/game-data root as a batch. Identify CPK by its `CPK ` content signature even when named `.EDAT`; do not assume every `.EDAT` is CPK or that every DLC file is a CPK.
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
| CPK in `.EDAT` resources | Several user-listed `.EDAT` samples started with `CPK `; YACpkTool extracted `imenu01.EDAT` and `eventP01.EDAT`; an unchanged `DL102_20.bin` was reported byte-identical after a CPK pack/extract cycle. | Enumerate all CPK/non-CPK variants in the real input set; pin and wrap a tested tool version; verify full member inventory, metadata, compression, and reproducible no-change rebuilds. A member-level round trip is not proof of a full ISO/DLC rebuild.
| Base PSP ISO | The user reported `SRW OE 1.08.iso` and product ID `NPJH50521`; no full ISO has been processed in this dry phase. | Select and test an ISO/UMD reader and builder on a copy; verify product/version detection, paths, alignment/boot metadata, extraction, and re-open/re-extract. Preserve and compare source hash.
| DLC/game-data set | The reported PPSSPP folder contains many `.EDAT` families plus PBP/SFO files; some `.EDAT` samples are CPK. | Inventory the complete user set and identify which assets are direct archives, encrypted wrappers, registration metadata, or unrelated files. Confirm DLC completeness/version and safe output/install behavior.
| Event BIN structure | 22 sample BINs have consistent top-level EDAT/EVNT/ECHK framing and 3,277 heuristic script candidates; candidate boundaries and ECHK semantics are still unproven. | Validate text/record boundaries and controls on independent records/resources before designating the JSONL as translation data or enabling write-back.
| Rendering/in-game QA | No modified string has been confirmed in-game; the user cautioned the supplied fragment may be inaccessible. | Use a genuinely comparable reachable resource if available. If not, record display QA as blocked/unverified; do not claim a playable patch.

YACpkTool is the existing CPK adapter candidate, not a blanket solution for all DLC or the base ISO. Its documented pack codec defaults to `none`, with LAYLA optional; the adapter must detect/preserve the source codec rather than selecting a codec by guess. Historical references to other inner formats are leads only. If a source requires decryption or a parser not yet validated, the pipeline must identify that boundary clearly and avoid a partial “successful” build.

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
2. **Read-only input inventory (done):** `tools/inventory_local_inputs.py` recursively hashes and signature-probes inputs, reports duplicate content, and does not follow symlinks or modify sources. Seven synthetic tests pass; the supplied ZIP is identified as a ZIP by signature. This tool does not parse/extract containers, estimate extraction space, or validate an image/archive.
3. **Batch CPK adapter:** wrap a pinned YACpkTool version and automate all discovered CPKs; test against disposable inputs and compare complete extracted-member manifests/bytes on no-change round trips.
4. **ISO and DLC adapters:** add only after real format samples are available and a copied source can pass extract/rebuild/re-open checks. Detect incomplete or unsupported resources explicitly.
5. **Deterministic text extraction:** validate boundaries independently; define stable IDs/control placeholders; test byte-identical no-change resource reinsertion.
6. **Translation/build pipeline:** only after pointer/length/encoding rules are known; validate translation inputs, batch apply all edits, rebuild archives/images, and report exact output hashes.
7. **End-to-end acceptance:** one user invocation processes all supported inputs without manual unpack/rename/per-file operations; originals hash unchanged; all manifests reconcile; no output described as playable before appropriate QA.

## Immediate scope

Continue read-only identification and small, safe automation steps. The real ISO/DLC are not available in this phase, so do not invent their exact wrapping or select an unverified ISO/DLC repacker. The first read-only inventory slice now exists; next, extend it only as needed and build the CPK adapter after disposable format samples and tool versions can be validated. ISO/DLC adapters require real format samples. The current scanner exports remain diagnostic, not approved translation tables.
