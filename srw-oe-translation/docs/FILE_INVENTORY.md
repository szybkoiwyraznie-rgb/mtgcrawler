# Local file inventory and archive audit

The user reported the original filenames/sizes. A ZIP of `eventP01` was later supplied for direct local analysis; game files are kept out of the tracked tree, while hashes and findings are recorded here.

## PPSSPP content directory

The user listed many `.EDAT` resources in `PSP/GAME/NPJH50521`, grouped under names such as `bacb*`, `BgmSet*`, `bmp*`, `bseq*`, `config*`, `credit*`, `eventP*`, `evept*`, `face*`, `imenu*`, `lmap_p*`, `mesbmp*`, `mesbtl*`, `mov*`, `robo*`, `se*`, `sprstd*`, and `voice*`. The directory also contained `PARAM.PBP`, `PARAM.SFO`, and `PBOOT.PBP`. The listing did not include the base ISO in that folder.

Specific sizes recorded from the user's listing:

- `imenu01.EDAT` — 24,744 bytes
- `eventP01.EDAT` — 326,456 bytes
- `config01.EDAT` — 247,936 bytes

The base ISO is held separately and was reported as `SRW OE 1.08.iso`, 664,324 KB (reported unit; exact byte length/hash pending).

## Extracted `imenu01.EDAT`

| File | Bytes |
| --- | ---: |
| `srwDL_BMP01.bin` | 4 |
| `srwDL_CharaDictionary01.bin` | 15,688 |
| `srwDL_DLC_ID01.bin` | 3,336 |
| `srwDL_Reference01.bin` | 4 |
| `srwDL_Shop01.bin` | 4 |
| `srw_DL_RoboDictionary01.bin` | 9,702 |

## Extracted `eventP01.EDAT`

The user reported 88 files arranged in these groups; each listed group had a `.bin`, `_edit.dat`, `_Entry.dat`, and `_ext.dat` member:

- `DL102_20`, `DL102_30`, `DL102_40`, `DL102_50`, `DL102_60`, `DL102_70`, `DL102_90`
- `DL103_11`, `DL103_12`, `DL103_20`, `DL103_30`, `DL103_40`
- `DL104_11`, `DL104_20`, `DL104_30`
- `DL105_11`, `DL105_12`, `DL105_20`, `DL105_30`, `DL105_40`
- `SM001`, `SM002`

Selected member sizes:

| File | Bytes |
| --- | ---: |
| `DL102_20.bin` | 16,216 |
| `DL102_20_edit.dat` | 28 |
| `DL102_20_Entry.dat` | 1,024 |
| `DL102_20_ext.dat` | 388 |
| `DL102_30.bin` | 15,620 |
| `DL102_40.bin` | 10,136 |
| `DL102_50.bin` | 20,820 |
| `DL102_60.bin` | 7,948 |
| `DL102_70.bin` | 11,472 |
| `DL102_90.bin` | 18,760 |
| `SM001.bin` | 1,364 |
| `SM002.bin` | 1,384 |

The names suggest event/scenario resources, but the naming semantics have not been verified.

## User-supplied `eventP01.zip` analyzed in this session

- ZIP size: 162,546 bytes; SHA-256: `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`.
- Archive integrity check passed. It contains 88 members: 22 `.bin`, 22 `_edit.dat`, 22 `_Entry.dat`, and 22 `_ext.dat`; total uncompressed size is 384,320 bytes.
- `DL102_20.bin` is 16,216 bytes; SHA-256: `47536d516a9bf0f12b8cd4ddb6f2d776749955c0b48bda65e95adea6287fb71f`.
- All 22 `_ext.dat` members are 388 bytes and contain at least one CP932-decoded Japanese run. All `_Entry.dat` sizes are divisible by 64; all `_edit.dat` sizes are divisible by 4. These are observations only, not format interpretations.
- The ZIP itself is kept only in the ignored local work area, not in the current tracked project tree. Scan details are in `CANDIDATE_SCAN_AUDIT.md`.