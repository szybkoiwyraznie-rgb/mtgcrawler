# Technical findings

This document separates direct observations from hypotheses. Do not promote a hypothesis to a format fact without testing it on more files.

## Confirmed observations

### Outer resource files

- The user's local files `imenu01.EDAT`, `eventP01.EDAT`, and `config01.EDAT` each begin with ASCII `CPK ` (`43 50 4B 20`).
- YACpkTool successfully extracted them after opening/renaming a working copy as `.cpk`.
- The outer `.EDAT` extension in this game directory therefore does not, by itself, tell us that the file is a Sony-encrypted EDAT. The observed first bytes are CPK.
- YACpkTool was also able to pack the extracted `eventP01` directory. Its output was reported at about 500 KB versus 326,456 bytes (about 319 KiB) for the original `eventP01.EDAT`.
- Re-extracting that rebuilt archive produced the listed files; `DL102_20.bin` remained 16,216 bytes and had the same SHA-256 as the original extraction. The exact digest is not retained.
- YACpkTool documentation states that its packing default is no compression and offers LAYLA as an optional codec. The larger archive is plausibly due to compression/packing differences, but the source archive's exact compression profile has not been verified.

### Inner event file

User-provided hex for `DL102_20.bin` showed:

- `0x00`: `EDAT`
- `0x0C`: `EVNT`
- `0x18`: `ECHK`
- At `0x05A6`: `FF FF`
- At `0x05A8`: readable CP932 text starts in the shown sample.
- Search for the byte sequence corresponding to `自衛隊の軍用レイバー相手に` returned offset `0x05B0`.
- Japanese lines include byte `0A` line breaks. The first displayed message was followed by `00 00` at `0x060E–0x060F`; another `FF FF` appeared at `0x0626–0x0627` before a further Japanese message.

The user saw readable Japanese after selecting Shift-JIS in Notepad++. These observations confirm that at least some script text is stored directly in the file, not encrypted/compressed beyond recognition.

## Working hypotheses — validate before relying on them

- `FF FF` may introduce a dialogue/text block.
- `00 00` may terminate a text block.
- The bytes between text blocks may contain event opcodes, speaker identifiers, pointer/length data, or other fields.
- `EDAT`, `EVNT`, and `ECHK` appear to be inner format tags, but their semantics are unknown.
- A candidate scanner can try decoding bytes after `FF FF` up to `00 00` as CP932 and keep spans containing Japanese. This is only a heuristic; test on multiple blocks and files.

## Unknowns / risks

- Whether a rebuilt archive is accepted by the game.
- Whether YACpkTool's output preserves all required CPK metadata, order, alignment, and compression flags.
- Whether the engine uses pointers or lengths that must be updated when English strings grow.
- Whether all event, menu, dictionary, battle, graphic, and DLC text is in these resources.
- Whether the game's font/runtime renders lowercase English and punctuation, and whether any font patch is required.

## References

- [YACpkTool repository and documentation](https://github.com/Brolijah/YACpkTool)
- [Historical SRW OE CPK/EDAT discussion](https://gbatemp.net/threads/super-robot-wars-oe.351431/) — useful technical lead only; it is not a verified modern rebuild recipe.
- [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z) — workflow/review inspiration only. It targets a different PS2 game; its binary parsers are not assumed compatible with OE.