# Name review queue (SRW OE, 2026-10-11)

Keys are the speaker/unit keys (decimal, as the user works in decimal). No game text here; the names
are in `local/speaker_names_all.json` and `local/name_units.csv` (field `field` = confidence).

Priority items from the 14 `unmarked-review` names (source `config_raw_clean` or `config_raw`):

| key (dec) | dialogue lines / battle records | current name class | why it needs review |
|---|---|---|---|
| 218 | 102 dialogue lines, 102 battle records | garbled (one half-decoded kanji + katakana) | a major speaker with no usable name; highest priority |
| 50 | 189 battle records | stat-type word (magic power), not a person | battle anchor likely belongs to a unit/skill, not a speaker; wrong label |
| 328 | 130 battle records, dialogue | generic role (bandit) | generic name, probably correct; confirm |
| 1430 | 13 battle records | personal name (short) | confirm against battle quotes |
| 2120 | dialogue only | personal name | confirm |
| 509, 512, 513, 515, 519, 520, 616, 618, 714 | dialogue only | personal names (ch2 Earth characters) | confirm spelling against script |

Not in this queue: dictionary-sourced names (216 keys, `[ZWERYFIKOWANE]` from CharaDictionary) and config-only names.

Decision rule (user): config name is authoritative; these are only flagged, not changed. Translation of
names uses the translator's knowledge; labels from scripts are calibration only.

## Battle-only keys with no name (24), queue by battle-record count

Source: `name_union` source `none`, not in dialogue. Decimal key (battle record count):

733 (77), 220 (76), 3122 (20), 3712 (17), 1005 (16), 1051 (16), 3702 (16), 4154 (15), 1048 (14),
301 (13), 1037 (13), 2251 (13), 2860 (13), 2865 (13), 3163 (13), 3165 (13), 4146 (13), 526 (2);
no battle records: 408, 525, 737, 995, 996, 1000.

Next step: for the top keys, decide whether the battle quotes name a unit or a pilot. Do not assign
names from dialogue calibration. Keys with 0 records are not checked yet.
