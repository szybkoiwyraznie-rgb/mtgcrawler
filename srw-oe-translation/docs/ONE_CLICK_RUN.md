# One-click local run (first slice)

**Status:** implemented and tested with synthetic data and a fake converter. Its first real run on the user's Windows PC completed on 2026-10-09 (status `completed`); the results and limits are in `EXPERIMENT_LOG.md`. Each package is now checked against its `-L` listing (one listing sample so far). Still open: packages whose entries share a name, the 47 non-CPK `.EDAT` files, and the ISO. Record the results of each further run in `EXPERIMENT_LOG.md`.

## What it does

Double-click `RUN_PIPELINE.bat` in the `srw-oe-translation` folder. After a one-time folder setup, the run is automatic:

1. **Setup.** Reads the private `config/local-workflow.ini`. If a folder is missing, it asks once with a folder dialog and saves the answer.
2. **Inventory.** Hashes every input file (SHA-256) and classifies it by content signature, never by extension. `CPK ` signatures are CPK containers even when named `.EDAT`.
3. **Preflight.** Checks the converter's SHA-256 (and an optional pinned hash), the output path, free disk space (about 3x the unique CPK size plus 512 MiB), and that output and input folders do not overlap.
4. **Probe.** Tries the converter on the smallest CPK. The original file name is tried first. A `.cpk` copy is made only inside the disposable staging folder, and only if the original name is rejected. Captured output and console output are both tried.
5. **Extract.** Unpacks every unique CPK into a fresh run folder. Duplicate content is extracted once. CPKs nested inside a package are extracted up to two levels deep. Each package is then compared with its `-L` listing (see Known limitations).
6. **Text.** Exports and verifies the event text for every `.bin` file in each extracted package (the same extractor as `tools/extract_event_text.py`). The text is a heuristic candidate list, verified only for round trips.
7. **Repack gate.** Repacks the smallest extracted package with non-empty members to a temporary CPK, unpacks it again, and checks that every member hash matches. The temporary files are deleted afterwards.
8. **Report.** Writes `registry.json`, `inputs.csv`, `packages.csv`, and `REPORT.txt` into the run folder.

## What it does not do

- It does **not** repack the game, insert or apply any text, or write a patch. Repacking is only a round-trip check of the CPK tool.
- It does **not** unpack ISO images. The base ISO is inventoried and its volume descriptor is read, but it is reported as *not processed*.
- It does **not** decode or print game text into the report, the registry, or the CSV files. Converter logs and text exports stay in the run folder you chose, which is outside this repository.
- It does **not** verify anything in the game. Nothing it produces is a playable patch.
- It never writes into the input folder. The run checks this with a before/after tree snapshot and fails if anything changed.

## Requirements (on the Windows PC)

- Windows 10 or 11.
- Python 3.9 or newer (3.11+ recommended) from python.org. During setup tick **Add python.exe to PATH** and keep **tcl/tk** selected (it is selected by default). The launcher uses `py -3`, then `python`.
- Your YACpkTool folder: `YACpkTool.exe` **and** `CpkMaker.dll` in the same folder. `YACpkTool.exe` is found automatically when it is in the input folder, in a folder named `YACpkTool` inside the input folder, or in `srw-oe-translation\tools` (or a `YACpkTool` folder there). If none or several copies are found, you are asked to choose one once. Your choice is saved only if you chose it in the dialog.
- An output folder whose path has **no spaces and no non-ASCII letters** (for example `C:\SRW_OE_out`). YACpkTool checks output paths with a URI rule that rejects them. The setup dialog warns you about this and asks again. A saved output folder with such a path is asked for again on the next double-click, so the run does not stay blocked. A Windows short name (8.3) is used automatically when the system provides one.

## First run

1. Double-click `RUN_PIPELINE.bat`.
2. Choose the folder with the game files (the folder that contains the `.EDAT` files and the ISO).
3. Choose the output folder (for example create `C:\SRW_OE_out` with the dialog's *New folder* button).
4. Wait. The console prints one line per stage; it is not saved to a file, so keep the window open or read `REPORT.txt`. Large files take minutes because every input is hashed. The converter's own progress may appear in the console window.
5. Read `REPORT.txt` in the new run folder (`<output>\<YYYYMMDD-HHMMSS>\`).

The choices are saved to `config/local-workflow.ini`, which is ignored by git. Run the file again to reuse them. To change them, run `RUN_PIPELINE.bat --reconfigure` (the same as `python tools\run_pipeline.py --reconfigure`), which asks for the folders and the converter again, or edit the file.

## Output layout

```text
<output>\<YYYYMMDD-HHMMSS>\
  REPORT.txt          human-readable summary (names and hashes only; no decoded text)
  registry.json       full machine-readable record (paths are placeholders, not user folders)
  inputs.csv          every input file: size, SHA-256, content type, pipeline status
  packages.csv        every extracted package: source, status, member counts, text status
  packages\           extracted CPK contents, one folder per unique package
  text\               event text exports (manifest.json, units.jsonl, segments.jsonl)
  logs\converter\     every converter call (list, extract, pack, unpack check, probe): exit code and captured output, or a console note
```

`staging\` (probe copies) and `gates\` (repack round-trip files) are deleted at the end of the run.

## Statuses and exit codes

| Status | Meaning | Exit code |
| --- | --- | --- |
| `completed` | Every attempted step passed. Known gaps (ISO, write-back, boundaries, in-game QA) are still listed. | 0 |
| `preflight_passed` | `--preflight-only` finished; no converter call was made. | 0 |
| `completed_with_failures` | At least one package, text export, or repack gate failed. The rest is still in the report. | 1 |
| `blocked` | A precondition failed (converter hash, output path, free space, or no converter mode worked). Nothing was extracted. | 1 |
| `error` | An unexpected error, or the input folder changed during the run. | 1 |
| `interrupted` | The run was stopped by the user. | 1 |

Setup errors (for example, no folder chosen with `--no-gui`) exit with code 2.

## Known limitations and assumptions

- **First real run done, with limits.** On the user's Windows PC the captured-output probe crashed that YACpkTool build (exit code 3762504530, 0xE0434352, an unhandled .NET exception), so extraction and repack calls ran in console-output mode. The converter behaviour is still based mainly on the archived source (2017). See `TECHNICAL_FINDINGS.md`.
- **Console output may be needed.** YACpkTool's progress display may fail when its output is redirected (observed on the user's build). The pipeline detects this in the probe and then runs that converter call with the console inherited. In that mode its error text cannot be captured, so success is judged from the output folder and the exit code only. The report says so in its `Warnings` and `Extraction` sections.
- **Extraction completeness is checked against the listing, per its own column layout.** After each extraction the run compares the package's `-L` entries with the files on disk. The listing's column header decides the layout: 246 of the 346 real listings print `No.  ID  Filesize  Compressed  %  Contents Filename`, 58 print no `ID` column, and 42 print no `Contents Filename` column. With a filename column, a package passes only when every entry has exactly one file of the same name **and size** and no file is left over. Without one, the converter writes one ID-named file per entry (observed: `ID00000` for ID 0), so the package is verified by entry count and the multiset of file sizes instead. If entries share a name, the package fails as `incomplete` and its output folder is removed, because one flat folder cannot hold them all. If the listing cannot be read, does not add up, or has names that do not decode, the package fails as `unverified`. Rows are read with a strict two-space split plus a single-space fallback for narrow columns; anything still unreadable fails the package, and `REPORT.txt` shows the raw example rows, header lines, name mismatches, and file-name examples in its `Listing check diagnostics` section, so a layout change can be diagnosed from the report alone. The run still checks the converter's exit code, its `Error:` lines (captured mode only), and the repack round trip of one package.
- **Repeated entry names.** In the second real run, 38 of 346 packages failed this way (all `bacb*`/`bseq*`): 1,111 entries beyond the first per name (206,898,244 bytes, 197.3 MiB) have no file, and the converter keeps one file per name. Entries with a repeated name are not extracted by this run. Whether their content differs, and whether the game uses their IDs, is unknown. Recovering them needs a read-only CPK table reader (the container's TOC carries each entry's name, ID, size, and offset); it does not exist yet.
- **`.EDAT` names.** Whether the converter accepts an original `.EDAT` name is decided by the probe. If it rejects the name, the `.cpk` staging copy is used. The original file is never renamed.
- **Nested depth and size.** Two nesting levels are processed. Each converter call has a 30-minute timeout.
- **Path length.** Keep the output path short (for example `C:\SRW_OE_out`). Long member paths inside a package may still exceed Windows limits; if so, the package fails and the report says so.
- **ISO.** No ISO adapter exists. Every ISO image is inventoried and reported with its volume-descriptor facts plus a read-only member index (paths, sizes, and first-four-byte signatures; recorded in `registry.json` as `inputs[].iso_inventory`), and left unprocessed. No ISO member is extracted.
- **Unrecognized inputs.** Files without a known signature are not processed. The report groups them by their first 32 bytes (hex) in an `Unrecognized inputs` section, and the registry records the same bytes in `inputs[].head_hex`. The bytes are not decoded.

## Command-line options (for developers)

```text
python tools/run_pipeline.py [--config FILE] [--input DIR] [--output DIR] [--tool EXE]
                             [--no-gui] [--reconfigure] [--preflight-only]
```

- `--input`, `--output`, `--tool` override the configuration for one run and are not saved.
- `--no-gui` never opens dialogs; a missing folder is a setup error.
- `--reconfigure` asks for the folders and the converter again.
- `--preflight-only` checks everything and makes no converter call.

The optional `expected_tool_sha256 = <64 hex digits>` key in the INI file pins the converter. A mismatch blocks the run. The example file is `config/local-workflow.example.ini`.

## Testing

`python -m unittest discover -s tests -p 'test_*.py'` (from `srw-oe-translation`) runs the synthetic suite, including `tests/test_run_pipeline.py`. Those tests use a fake converter that mimics the documented command line, its exit-code-0 errors, its output-path rule, and its piped-output crash. The CPK container in the tests is a synthetic JSON format, not the CRI format. No game file is used.

## Sharing results

Share `REPORT.txt` first. It contains file names, sizes, byte prefixes, and hashes of the game resources, which is the information needed to diagnose the run, including the `Listing check diagnostics` and `Unrecognized inputs` sections. Do not share the text exports or converter logs unless you are sure the content is acceptable to share. Do not share the INI file, which contains your local paths. If more detail is needed, `registry.json` is the next file to share. It holds names, sizes, hashes, probe attempts, ISO descriptor sizes and member indexes, unknown-input first bytes, and per-package listing results, not decoded text.
