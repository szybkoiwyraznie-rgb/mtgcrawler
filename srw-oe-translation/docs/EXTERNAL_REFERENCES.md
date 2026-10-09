# External references

These are research references, not authorities for the game's exact binary layout.

- [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z) — workflow and QA inspiration for a different PS2 title. Do not reuse its game-specific parsers as if they applied to PSP OE.
- [YACpkTool](https://github.com/Brolijah/YACpkTool) — CPK extract/pack utility used by the user. Its archived README documents `-L` (list), `-X` (extract), `-P` (pack), `-i` (input path), `-o` (output), and `-d` (directory); packing defaults to codec `none`, with LAYLA available. It labels `-R` file replacement experimental. This is a candidate local adapter only: exact executable/version, `.EDAT`-named input handling, source codec behavior, and no-change repack results must be tested before relying on it. The tool should be supplied locally and pinned/hashed, not downloaded by the pipeline.
- [Historical GBAtemp SRW OE thread](https://gbatemp.net/threads/super-robot-wars-oe.351431/) — old discussion of CPK extraction, `.EDAT` naming, inner `.PAC` files, and repacking difficulties. Treat as a lead, not a tested recipe.

Do not link to or include unauthorized game-image/DLC downloads. The game data remains local to the user.