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
- The user reviewed four candidate rows: readable Japanese at offsets `0x158C` and `0x1D68`; coherent Japanese at `0x14E8` and `0x25A8` was followed in the decoded output by control-looking suffixes.
- Raw hex around the two noisy rows' first `00 00` pair showed:
  - Candidate `0x14E8`, pair at `0x151E`: `E8-82-DC-82-B5-82-BD-81-48-00-76-01-00-00-10-00`.
  - Candidate `0x25A8`, pair at `0x25DE`: `A6-97-CD-82-B7-82-E9-81-42-00-22-02-00-00-10-00`.
- Raw hex around the two readable rows' first `00 00` pair showed:
  - Candidate `0x158C`, pair at `0x15EC`: `82-A0-82-E8-82-DC-82-B9-82-F1-81-42-00-00-00-00`.
  - Candidate `0x1D68`, pair at `0x1D8A`: `82-AA-82-E9-82-CC-82-A9-81-49-81-48-00-00-C9-00`.
- In the readable examples, the Japanese-looking bytes are followed immediately by `00 00`. In the two noisy examples, they are followed by `00`, then `76 01` or `22 02`, then `00 00`, then `10 00`. The earlier tentative expectation of an ASCII space byte (`20`) before `76`/`22` was wrong; the raw windows contain `00` there, not `20`.

This comparison strengthens the hypothesis that the current candidate scanner reads past the visible-text boundary in the noisy cases: it only stops on a *pair* of zero bytes, so it includes a single zero and the following `76 01` / `22 02` before reaching `00 00`. A single zero may terminate the Japanese text, with following bytes being event/control data; however, the clean examples end with a zero pair, and the exact format semantics are still unverified. Do not strip or rewrite these bytes.

The user saw readable Japanese after selecting Shift-JIS in Notepad++. These observations confirm that at least some script text is stored directly in the file, not encrypted/compressed beyond recognition.

## Working hypotheses — validate before relying on them

- `FF FF` may introduce a dialogue/text block.
- A single `00` after the Japanese text may terminate a string; the `00 00` pair may mark a different boundary or field.
- `76 01` and `22 02` may be event/control opcodes with parameters or adjacent record metadata; their semantics are unknown.
- The bytes between text blocks may contain event opcodes, speaker identifiers, pointer/length data, or other fields.
- `EDAT`, `EVNT`, and `ECHK` appear to be inner format tags, but their semantics are unknown.
- A candidate scanner can try decoding bytes after `FF FF` up to `00 00` as CP932 and keep spans containing Japanese. It finds some known text but may also consume bytes after a single-NUL string end. Preserve all such bytes until mapped.

## PowerShell formatting note

The first candidate-dump script used a single-quoted format string containing `` `t``. PowerShell does not expand backtick escapes inside single quotes, so the output displayed the literal characters `` `t`` between the hexadecimal offset and candidate text. This is a formatting issue, not a game byte. For an actual tab, use:

```powershell
$results.Add(("{0:X4}`t{1}" -f $start, $text))
```

## Unknowns / risks

- Whether a single `00` terminates text and what `76 01`, `22 02`, `00 00`, and `10 00` represent.
- Whether a rebuilt archive is accepted by the game.
- Whether YACpkTool's output preserves all required CPK metadata, order, alignment, and compression flags.
- Whether the engine uses pointers or lengths that must be updated when English strings grow.
- Whether all event, menu, dictionary, battle, graphic, and DLC text is in these resources.
- Whether the game's font/runtime renders lowercase English and punctuation, and whether any font patch is required.

## References

- [YACpkTool repository and documentation](https://github.com/Brolijah/YACpkTool)
- [Historical SRW OE CPK/EDAT discussion](https://gbatemp.net/threads/super-robot-wars-oe.351431/) — useful technical lead only; it is not a verified modern rebuild recipe.
- [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z) — workflow/review inspiration only. It targets a different PS2 game; its binary parsers are not assumed compatible with OE.
