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
- A read-only candidate scanner produced 215 output lines and included the known Japanese substring.
- The user later reviewed four candidate rows: readable Japanese at offsets `0x158C` and `0x1D68`; coherent Japanese at `0x14E8` and `0x25A8` was followed in the decoded output by a space plus `v`/U+0001 and a space plus ASCII double quote/U+0002, respectively.
- If those final displayed characters are direct CP932 decodings of the source bytes, the suffixes are expected to include `20 76 01` and `20 22 02`; this still needs confirmation from a raw hex window.

These examples make a wholly random false-positive interpretation less likely for the two noisy rows: both contain coherent dialogue. They do **not** establish whether the suffix bytes are inline event/control tokens, trailing record metadata, or bytes accidentally included by the current candidate boundary.

The user saw readable Japanese after selecting Shift-JIS in Notepad++. These observations confirm that at least some script text is stored directly in the file, not encrypted/compressed beyond recognition.

## Working hypotheses — validate before relying on them

- `FF FF` may introduce a dialogue/text block.
- `00 00` may terminate a text block.
- The bytes between text blocks may contain event opcodes, speaker identifiers, pointer/length data, or other fields.
- `EDAT`, `EVNT`, and `ECHK` appear to be inner format tags, but their semantics are unknown.
- A candidate scanner can try decoding bytes after `FF FF` up to `00 00` as CP932 and keep spans containing Japanese. It found the known string in one file, but candidates with control-looking suffixes must be classified before treating output as plain text. Preserve those bytes.

## PowerShell formatting note

The first candidate-dump script used a single-quoted format string containing `` `t``. PowerShell does not expand backtick escapes inside single quotes, so the output displayed the literal characters `` `t`` between the hexadecimal offset and candidate text. This is a formatting issue, not a game byte. For an actual tab, use:

```powershell
$results.Add(("{0:X4}`t{1}" -f $start, $text))
```

## Unknowns / risks

- Exact meanings of suffix pairs such as `76 01` and `22 02`, and whether they belong to dialogue or adjacent event data.
- Whether the first `00 00` after a candidate start is always the record/string terminator.
- Whether a rebuilt archive is accepted by the game.
- Whether YACpkTool's output preserves all required CPK metadata, order, alignment, and compression flags.
- Whether the engine uses pointers or lengths that must be updated when English strings grow.
- Whether all event, menu, dictionary, battle, graphic, and DLC text is in these resources.
- Whether the game's font/runtime renders lowercase English and punctuation, and whether any font patch is required.

## References

- [YACpkTool repository and documentation](https://github.com/Brolijah/YACpkTool)
- [Historical SRW OE CPK/EDAT discussion](https://gbatemp.net/threads/super-robot-wars-oe.351431/) — useful technical lead only; it is not a verified modern rebuild recipe.
- [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z) — workflow/review inspiration only. It targets a different PS2 game; its binary parsers are not assumed compatible with OE.
