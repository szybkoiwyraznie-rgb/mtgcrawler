# One-click local run (first slice)

**Status:** implemented and tested with synthetic data and a fake converter. Its first real run on the user's Windows PC completed on 2026-10-09 (status `completed`); the results and limits are in `EXPERIMENT_LOG.md`. Each package is now checked against its `-L` listing (one listing sample so far). Still open: packages whose entries share a name, the 47 non-CPK `.EDAT` files, and the ISO. Record the results of each further run in `EXPERIMENT_LOG.md`.

## What it does

Double-click `RUN_PIPELINE.bat` in the `srw-oe-translation` folder. After a one-time folder setup, the run is automatic:

1. **Setup.** Reads the private `config/local-workflow.ini`. If a folder is missing, it asks once with a folder dialog and saves the answer.
2. **Inventory.** Hashes every input file (SHA-256) and classifies it by content signature, never by extension. `CPK ` signatures are CPK containers even when named `.EDAT`.
3. **Preflight.** Checks the converter's SHA-256 (and an optional pinned hash), the output path, free disk space (about 4x the unique CPK size plus 512 MiB; the extra copy is the verified cache), and that output and input folders do not overlap.
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

1. Download the branch ZIP: https://github.com/szybkoiwyraznie-rgb/mtgcrawler/archive/refs/heads/arena/b2a62e8c-mtgcrawler.zip
2. Unpack it anywhere (for example the Desktop).
3. Open the unpacked folder, then `srw-oe-translation`, and double-click `RUN_PIPELINE.bat`.
4. If it asks for folders, choose: the folder with the game files (the folder that contains the `.EDAT` files and the ISO, for example `D:\SRWOE`), the output folder (for example create `D:\SRW_OE_out` with the dialog's *New folder* button), and the converter (`YACpkTool.exe`, for example `D:\YACpkTool\YACpkTool.exe`).
5. Wait. The console prints one line per stage; it is not saved to a file, so keep the window open or read `REPORT.txt`. Large files take minutes because every input is hashed. The converter's own progress may appear in the console window. Expect about 3–4 minutes in total.
6. Read `REPORT.txt` in the new run folder (`<output>\<YYYYMMDD-HHMMSS>\`), copy the whole content, and share it. Optionally zip `registry.json` from the same run folder and share that too. Old run folders can be deleted (each is about 0.8 GB).

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
- **Extraction completeness is checked against the listing, per its own column layout.** After each extraction the run compares the package's `-L` entries with the files on disk. The listing's column header decides the layout: in the third real run, of 377 listings, 246 printed `No.  ID  Filesize  Compressed  %  Contents Filename`, 89 printed no `ID` column, and 42 printed no `Contents Filename` column. With a filename column, a package passes only when every entry has exactly one file of the same name **and size** and no file is left over. Without one, the converter writes one ID-named file per entry (observed: `ID00000` for ID 0), so the package is verified by entry count and the multiset of file sizes instead. If entries share a name, the package fails as `incomplete` and its output folder is removed, because one flat folder cannot hold them all. If the listing cannot be read, does not add up, or has names that do not decode, the package fails as `unverified`. Rows are read with a strict two-space split plus a single-space fallback for narrow columns; anything still unreadable fails the package, and `REPORT.txt` shows the raw example rows, header lines, name mismatches, and file-name examples in its `Listing check diagnostics` section, so a layout change can be diagnosed from the report alone. The run still checks the converter's exit code, its `Error:` lines (captured mode only), and the repack round trip of one package.
- **Repeated entry names.** In the third real run, 38 of 377 packages failed this way (all `bacb*`/`bseq*`): 1,111 entries beyond the first per name (206,898,244 bytes, 197.3 MiB) have no file, and the converter keeps one file per name. Entries with a repeated name are not extracted by this run. Whether their content differs, and whether the game uses their IDs, is unknown. Recovering them needs a read-only CPK table reader (the container's TOC carries each entry's name, ID, size, and offset); `tools/cpk_table.py` now exists and the run cross-checks every package's TOC against its listing (report-only, see the next bullet).
- **CPK table cross-check (report-only).** Every package's TOC tables are read with `tools/cpk_table.py` and compared with its `-L` listing. The report adds a `CPK table check (TOC vs listing, report-only): agree N, mismatch N, unreadable N, no listing N` line, a mismatches section, and `packages.csv` gains `table_status`/`table_duplicate_entries`. A table mismatch never fails a package in this version — the listing check remains the authoritative completeness gate. After a run shows agreement on all packages, the table check can be promoted to fail-closed.
- **`.EDAT` names.** Whether the converter accepts an original `.EDAT` name is decided by the probe. If it rejects the name, the `.cpk` staging copy is used. The original file is never renamed.
- **Nested depth and size.** Two nesting levels are processed. Each converter call has a 30-minute timeout.
- **Path length.** Keep the output path short (for example `C:\SRW_OE_out`). Long member paths inside a package may still exceed Windows limits; if so, the package fails and the report says so.
- **ISO.** Every ISO image is inventoried and reported with its volume-descriptor facts plus a read-only member index (paths, sizes, and first-four-byte signatures; recorded in `registry.json` as `inputs[].iso_inventory`). The index tolerates an image whose file is longer than its descriptor: extents beyond the declared volume but inside the file are reported as warnings with counts (for example `3 member extents end beyond the PVD volume (max +4096 bytes; the file is 10000 bytes longer than its descriptor)`), while extents beyond the file still fail the index, and the report prints the index error when it fails. The run then extracts every ISO's **CPK-signature members read-only** into the run folder's `iso/` directory (the image is never modified) and processes them like any input package — so in this project the disc's chapter-1 and base/system packages are covered together with the DLC in the input folder. Rebuilding or repacking an ISO image is **not** automated. See `docs/EXPERIMENT_LOG.md` for the coverage picture.
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

## Verified cache

After a package is extracted and verified, a copy is kept under `<output folder>/_cache/<converter and tool digest>/<source SHA-256>/`. A later run with the same converter binary and the same tool code restores such a package instead of calling the converter again. Every cached file is hashed again before it is copied; any mismatch, missing file, or unreadable record makes the run extract that package again. Changing the converter or any of `run_pipeline.py`, `cpk_table.py`, `iso9660.py`, or `extract_event_text.py` changes the digest, so old entries are not used. The cache takes about as much space as the extracted packages, which is why the free-space check asks for four times the CPK size. To reclaim the space, delete the `_cache` folder; the next run rebuilds it. ISO CPK members are still copied out of the image on every run; only their extraction is cached.
