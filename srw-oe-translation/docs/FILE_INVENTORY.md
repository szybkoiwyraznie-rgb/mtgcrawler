# Local file inventory (reported by user)

These are filenames and sizes only; the files themselves are not in Git.

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