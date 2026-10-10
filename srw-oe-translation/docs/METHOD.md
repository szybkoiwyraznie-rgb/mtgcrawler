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

**Consequence for this project:** an equal-length replacement cannot move any offset, so it is the
safe first write — but it is a *fallback*, not the method. English needs more bytes than Japanese
almost always, so the real method is the second half of their pipeline.

**Correction (this document originally claimed equal-length was the whole method; it is not).**
`retro-trans/SRW-Z` grows strings routinely:

- `tools/apply_fixes.py`: "Rows are located by **RE-RESOLVING the pointer at apply time** ... Rows that
  outgrow their slot are **relocated (append + repoint + zero)**."
- `tools/apply_script.py`: "Longer needs relocation ... A pass that moves bytes inside a record while
  leaving the pointer table alone produces an image that boots, plays and shows the wrong text."
- `tools/verify_pointers.py`: "**Structural gate: every pointer must still land on the START of a
  string.**"

So growth = append the longer string at the record end, rewrite every pointer that referenced it,
zero the old slot, and then verify structurally that every pointer still lands on a string start.

## The pointers exist, and they are load-base-relative — which is why our search found nothing

`retro-trans/SRW-Z`, `tools/pool.py`, verbatim:

> "THE FINDING (2026-08-26). Weapon/ability/item names are NOT walked and NOT indexed. COMPDATA.BN's
> single 524,032-byte record ends in a string pool, and every string is reached through an **ABSOLUTE
> PS2 RAM POINTER** stored earlier in the same record. ... **That is why the byte budget looked
> immovable: every static search for an index, a record-relative offset, or an offset/8 failed, because
> the stored value is `0x0073xxxx`.**"

Layout they measured: pointer tables at `0x00904..0x61658` (9,483 words), string pool at
`0x61680..0x7FF00` (3,435 entries, 8-byte aligned); the pointers only ever live **before** the pool.
Their predicate (`tools/export_review.py`): "for a row at JP offset O, find a **4-aligned word equal
to `BASE+O`** in the JAPANESE record, read the word at that same position in OURS, and that value is
where the row lives now."

**This is exactly the trap this project fell into.** `tools/boundary_probe.py` searched for the bare
offsets (`start`, `marker`, `start+1`, `start+2`) — SRW-Z says a search for "an index, a
record-relative offset, or an offset/8" is precisely what fails, because the stored value carries the
load base. Milestone 61's negative result therefore rules out *bare-offset* pointers only, and says
nothing about `BASE + offset` ones.

**Two of their hard-won details worth copying:**

- **Pointer-shaped words that miss a string start are not always coincidence.** Of 91 such words, 34
  were u16 pairs reading as an address by chance, but **60 were real table entries** pointing into a
  string's NUL padding (a deliberate empty string) or a few bytes into a string (a deliberate
  substring). "0.8.81 left them alone on the coincidence argument and **broke all 60**." Their fix was
  a *stride test*: a word sitting exactly on the pointer table's stride is a real entry. `repack()`
  now runs it and **refuses** rather than guessing.
- **They measure the health of the pointer table, not just its existence**: `tools/pointer_baseline.json`
  records per-record scores on the untouched Japanese disc, noting that "rec48 scores 84.4% on Bandai
  Namco's own disc, which is why a flat `--min 85` reported a false failure" — i.e. the metric has a
  natural floor, and thresholds must be read against it.

**Ported here as `tools/pointer_base_scan.py`.** For every candidate base B (the PSP user-memory window
`0x08800000`-`0x0A000000` at 16 KiB steps, plus small constants in case the base is a header length)
and every string start S in a file, it asks whether `B + S` occurs as a u32 in that file. One file
holds only a few hundred strings, so this is cheap. It reports the best bases, the share of strings
each reaches, the same search with every start shifted by +1 as a control, and whether the winning
words sit in a dense run (a table) or scatter.

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

## What this retires, and what it puts back on the table

- **Retired:** diffing someone else's patch distribution. The method is documented, so there is nothing
  left to learn from their xdelta files, and the ISO route was already closed by the MD5 check
  (`docs/STATUS.md` item 63).
- **Back on the critical path:** finding the pointers. Not as an academic question — it is what allows
  an English line to be longer than its Japanese slot, which is the normal case. The search that
  matters is now the **load-base-relative** one (`tools/pointer_base_scan.py`), because a bare-offset
  search is documented to fail on this engine family.
- **Reframed:** the equal-length write-back (`tools/rewrite_units.py`) stays, but as the safe first
  write and as the fallback for a slot that cannot be repointed — not as the plan.
