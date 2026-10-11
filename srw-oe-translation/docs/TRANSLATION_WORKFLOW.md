# Translation workflow (B) — readable source files → booting patched ISO

Goal: give a specialised translation AI a **readable, editable** representation of the game's
text, and a deterministic way back to a **booting** patched ISO. The growth requirement is
honoured end to end (English may be longer than Japanese).

Only **Events** (narration records inside EDAT/EVNT members) are covered today. UI / names /
menus are a **separate, open** track (see below).

## 1. Export (JP → readable JSON)

    python tools/export_strings.py <eventP00.cpk | *.EDAT> [--out DIR]

One JSON row per narration record:

    {
      "member": "DL100_01.bin",      # container member holding the record
      "record_index": 0,             # ordinal within the member
      "record_offset": 168,          # byte offset of the record (stable key)
      "source": "地球統一政府…",       # decoded CP932 Japanese
      "lines": ["…"],                # source split on 0x0A
      "source_bytes": 154,
      "max_line_width": 42,          # display width, half-width units
      "line_count": 4,
      "target": ""                   # <-- the translator fills this (English)
    }

## 2. Translate

The AI fills `target`. Hard constraints enforced by `apply_strings` (refused, not clipped):
- every `target` line's display width ≤ **46** half-width units (in-game dialogue box);
- `target` must encode in **CP932**;
- growth is allowed and expected (target may exceed `source_bytes`).
Empty `target` = leave the record untouched.

## 3. Apply (JSON → rebuilt CPK with growth)

    python tools/apply_strings.py <package.cpk|EDAT> <strings.json> <out.cpk> [--budget 46]

Rewrites each filled record via `grow_event_text.grow_record` (in-place growth + the inner EVNT
size fields) and rebuilds the container. The replaced member is re-compressed with the
descending CRILAYLA compressor so it stays `FileSize < ExtractSize`.

## 4. Pack into the ISO and boot

    # chapter 1 lives on the disc inside eventP00.cpk:
    copy /Y <out.cpk> D:\SRWOE\patch\PSP_GAME\USRDIR\eventP00.cpk
    python tools/iso_pack.py patchiso "D:\SRWOE\SRW OE 1.08.iso" D:\SRWOE\repacked.iso D:\SRWOE\patch

`patchiso` splices the file surgically (sector-aligned append + directory-record LBA/size + PVD
volume size) and preserves the UMD structure, so the image boots (proven, STATUS 83/84).

Chapters 2–8 are PSN DLC and can instead be delivered as loose `.EDAT` on the memstick (the path
growth was first proven on).

## Scope gap — UI / names / menus NOT yet extracted

This workflow currently covers **Events only**. The UI/name/menu containers are a separate track
and are **not** readable sources yet (docs/UI_NAMES.md):
- `imenu00*.cpk` members are ID→slot maps, **no display names**;
- `u16tbl.cpk` holds jis2ucs/ucs2jis conversion tables (rendering aid, not strings);
- `font.cpk` holds glyph bitmaps (the dialogue font already has Latin, so English renders).
Producing readable name/menu tables remains open work.
