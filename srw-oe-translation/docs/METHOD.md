# The method, taken from the people who did it

This project spent many turns measuring bytes to infer how the game addresses its strings. The method
below comes from three sources that already answer it, and it makes most of that measurement
unnecessary. It is the plan of record; `docs/STATUS.md` item 64 records why.

## The core rule: replace in place, at exactly the same byte length

**Source 1 — CrashmanX, the person who started the English patch for this exact game.**
[gbatemp thread 351431](https://gbatemp.net/threads/super-robot-wars-oe.351431/), opened 2013-07-18,
80 replies. In the first post, on why the translation is constrained:

> "Well because I'm currently dealing with the constraint of having to use **the same amount of spaces
> as the Japanese characters**, well double technically. But with the ability to edit the .pac files
> like I can in Danball then I'd be able to use as many spaces as I want."

And on tooling: "Right now I'm just using a **Hex Editor (MadEdit)** and the CPK Tools from the
Danball translation thread."

**Source 2 — `retro-trans/SRW-Z`**, the project this workflow is modelled on, `docs/FINDINGS.md`, on
the sibling engine:

> "In-place replacement must preserve each string's **exact byte length** (`apply_stage1.py` pads to
> the original `nbytes`). **This is safe and verified.** Growing strings is not safe without also
> rewriting every inline offset operand."

**Consequence for this project:** if every replacement is exactly as long as the original, **no offset
anywhere in the file can move**. The pointer layout — which `tools/boundary_probe.py` spent several
milestones trying to localise — is not needed to produce a testable patch. It only becomes necessary
if a translation must be longer than its slot, and SRW-Z's answer to that (relocate the row, rewrite
every pointer to it) is a later milestone, not a gate.

`tools/rewrite_units.py` implements exactly this rule and refuses anything else: it re-encodes each
row's `source_text` and compares it with the bytes actually in the file before writing, pads a shorter
translation with `0x20` to the exact slot, refuses a longer one, and asserts that the output file is
byte-for-byte the same length as the input.

## Repacking the CPK: it works, with compression left off

The same thread settles the question that has been gating this project:

> CrashmanX: "**It's possible to re-pack the .cpk files** as I managed to do so for the `imenu 00.cpk`
> and was able to test a few changes in there" (with an in-game screenshot of the modified menu).
> "For the .CPK repacking I used the CPK tools that I also used for Danball. **I just left 'Force
> Compress' unchecked and it worked.**"

A second participant in the thread reported the opposite — "i tried to repack 'without any changes'
the game crash so i may need a special tool for these" — so the setting matters and the tool matters.
This project's own data agrees with the uncompressed reading: run `20261010-142640` found **0
compressed entries** across the recovered packages, i.e. the members are stored, not compressed.

**Action:** repack with compression off, and verify the repacked file's TOC against the original
(`tools/cpk_table.py` already reads every row). If YACpkTool's pack mode cannot be told to store,
the fallback named in the thread is *cri packed file maker*.

## Extracting: three routes, all already known to work here

1. **YACpkTool** — what this project already uses; 453 of 497 packages extracted, with the 42
   colliding-name packages recovered read-only by `tools/cpk_table.py`.
2. **The QuickBMS CRI CPK script** posted by MrShyCity in that thread (derived from hcs's
   `cpk_unpack`): `endian big`, `comtype cpk`, `idstring "CPK "`, reading `TocOffset`,
   `ContentOffset` and `Files` from the `@UTF` table, then walking the TOC for `DirName`, `FileName`,
   `FileSize`, `ExtractSize`, `FileOffset`, and `clog`-ing when `ExtractSize > FileSize`.
3. **The DLC files are the same container**: "These can also extract the `.EDAT` file inside
   `NPJH50521` folder **by renaming `.EDAT` to `.CPK`**" — which matches what this project's
   `tools/cpk_table.py` already does.

## What nobody has published, and is therefore still ours to do

CrashmanX's own status table in that first post shows exactly where the public knowledge stops:

| Area | His progress | Note |
|---|---|---|
| Level names, song names | 100% | hex-edited in place |
| Item names | ~99% | "Some are a bit hard to read because space issues" |
| Battle menus / main menus | 90% / ~70% | the repacked `imenu00.cpk` |
| Unit and attack names | ~80% | |
| **Story** | **---%** | "**Can't exactly translate ATM because I don't have tools to work with it**" |
| **Attack shouts / talking** | **---%** | same |
| **Reference** | **0%** | same |
| **Chapter 1 (DLC)** | **0% on all** | "**Don't know how to repack the DLC properly yet**" |

So the dialogue — this project's target — has no public tooling. The Korean patches prove it was
eventually done, but neither repo publishes its tools. What is missing is narrow and concrete:
locating the story strings (this project's extractor already exports 45,325 units with exact offsets)
and the two problems below.

One more dead end recorded in that thread, so it is not retried: extracting `config00.cpk` yields a
`.pac` file the same size as the CPK, and neither CrashmanX nor the Madoka tools could open it — "I've
been unable to extract the contents of the .pac file properly."

## The font

Two proven approaches, both from sources above:

- **Glyph-table substitution** (`snake759494/NDS-SRW-K`): the font is a table of fixed-size records
  (`[u16 SJIS BE][24-byte 1bpp 12×16 bitmap]`); they overwrite the entries for codes ≥ `0x889F` with
  ~2,350 Hangul glyphs rendered from an OFL font. Documented side effect: kanji in that code range
  then print as the substituted glyphs. English needs ~95 glyphs, not 2,350.
- **Renderer remap** (`retro-trans/SRW-Z`): the dialogue font is fullwidth SJIS only and raw ASCII
  renders as blank boxes, so they patch the renderer to map ASCII onto the existing fullwidth glyphs
  at draw time. They found the routine with a **memory breakpoint in the emulator**, after static
  signature search failed to converge.
- **Anything baked into UI art** goes through **PPSSPP texture replacement** (PNGs in
  `memstick/PSP/TEXTURES/NPJH50521`), which is how the Korean patch does its menus.

## The pipeline this implies

1. **Pick one unit in one DLC file.** Not the ISO: PPSSPP reads the DLC from
   `memstick/PSP/GAME/NPJH50521` as loose files, so a DLC test needs no ISO rebuild, while a chapter-1
   test would.
2. **Write an equal-length English string** with `tools/rewrite_units.py` into a copy of the extracted
   file. The tool guarantees the length is unchanged.
3. **Repack the CPK with compression off** and check the TOC row-by-row against the original.
4. **Put it where the emulator reads it** and boot PPSSPP.
5. **If the glyphs are blank**, apply the font fix (substitution or remap) — that is a separate
   problem from the text, and it is the only thing standing between a written string and a visible one.
6. **Only after a line is visibly English** does length become interesting: measure how often English
   needs more bytes than the Japanese slot, and only then consider relocation and pointer rewriting.

## What this retires

- The pointer/offset localisation work (`boundary_probe` owner attribution, `patch_diff` of someone
  else's patch) is no longer on the critical path. It stays useful as evidence if a translation ever
  has to grow, and it stays in the repository, but it is not a gate.
- The ISO diff route was already closed by the MD5 check (`docs/STATUS.md` item 63).
