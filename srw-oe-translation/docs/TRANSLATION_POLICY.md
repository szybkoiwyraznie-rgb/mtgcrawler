# Translation policy (initial)

## User decisions

- Target language: English.
- Start from Japanese text in the user's game data.
- Do not use the old Akurasu machine-translated script as the source; the user considers its quality too poor.

## Still undecided

- American vs. British English.
- Character voice and level of localization versus literal fidelity.
- Per-series official names, spellings, and terminology sources.
- How to render sound effects, honorifics, and untranslated cultural terms.
- Whether text displayed in graphics and credits is in scope for the first playable build.

## Editorial/technical principles

- Keep a source ID, file, byte offset, control-code context, status, and reviewer note for every extracted string.
- Never translate or delete control bytes, variable tokens, or event opcodes as though they were prose.
- Do not edit binary assets in a general-purpose text editor and save them back.
- Prefer a consistent, sourced glossary across crossover series; record disputed choices rather than silently changing names.
- Review English line length and actual in-game rendering; a fluent translation that overflows or breaks control flow is not acceptable.
- Any machine-assisted draft must receive terminology and human/editorial review before being called final.
