# Prior art and technical landscape — SRW Y

Collected 2026-10-25. Purpose: know what exists before building anything, credit
what we use, and never lift translated text from anyone.

## What we may take from prior art

| Allowed | Not allowed |
|---|---|
| Format knowledge (container layout, encryption/compression schemes, header magic) | Copying translated strings, glossaries or editing decisions from another translation |
| Tool names, public reverse-engineering notes, version numbers | Vendoring code without a recorded licence and provenance |
| Facts about the engine (Unity/IL2CPP, loader versions) | Distributing patched game files |

## SRW Y specific

1. **Accessibility mod — `stephenso1120-cmyk/SRWY-Accessibility` (GitHub, public).**
   Installs through **MelonLoader v0.7.1**, uses a native detour hook layer and
   reads, at runtime: menu labels, adventure-mode dialogue with speaker names,
   chapter titles, tutorials, battle subtitles, tactical-map cursor data.
   It ships its own localization for five languages (en, zh_CN, zh_TW, ja, ko),
   which mirrors the game's language set, and it documents a workaround for an
   IL2CPP null-pointer crash — i.e. hooking this build is non-trivial but proven.
   *Take:* proof that (a) the running build exposes displayable strings to a
   managed mod, (b) MelonLoader works with this game, (c) the practical hooking
   risks. *Not take:* its code (licence not reviewed), its text.
2. **Datamining reports (thelifestream.net forum, 2026-08).** SRW Y is described
   as the first SRW built on Unity; the main data sits in **one large `.cpk`
   archive** plus Unity bundles with non-descriptive alphanumeric names
   (~18,000 files); inside ~5 MB bundles there are **a few hundred text files in
   the five shipped languages**. A GUI CPK tool opened the archive but the
   browsing experience was poor. *Take:* the working hypothesis for step S1 of
   the spike (see `FEASIBILITY.md`).
3. **PC platform facts.** Steam listing (app `1909950`): Windows only, single
   player, In-App Purchases (DLC), no Workshop. Executable path reported by mod
   documentation: `…/steamapps/common/SRWY/SUPER ROBOT WARS Y.exe` with the
   standard `<game>_Data` folder next to it, i.e. a stock Unity layout.
   Custom BGM uses an `SRYMUSIC` folder (not the older `SRWMUSIC`), which
   confirms the PC build reads beside the executable.
4. **PC mods exist in the wild** (playable-boss roster mods distributed as
   `<game>_Data` replacement folders). *Take:* replacing data files beside the
   executable is the community's accepted installation mechanism, so
   architecture **B** (asset patch) is installable in principle.

## Same series, different engine — method transfer only

5. **SRW 30 (PC, 2021).** Text in CRI `.cpk` under `pc/`, payload
   Blowfish-encrypted + CRILAYLA-compressed, mission dialogue inside Lua scripts;
   public tooling (CriPakGUI, QuickBMS scripts) and a translation-fix project that
   ships *small patched CPKs*. *Take:* container/compression vocabulary, the
   practical "don't use CRILAYLA compression when repacking" lesson, and the
   observation that the SRW 30 English localization is widely criticised — a
   reminder that official EN for this series is a reference, not a standard.
6. **SRW V (PC) Russian fan translation — `linyaDev/SRWV-RusTranslation`.**
   Fully documented pipeline for the V/X/T generation: CPK (TOC/ITOC) extraction,
   Blowfish ECB file encryption, **BLTU** binary key→string tables (UTF-8), font
   metrics repair for Cyrillic, and separate containers per surface
   (`STGEST_EN.cpk` story, `LT00_EN.cpk` units, `SysText.cpk` menus).
   *Take:* the *method* template for a series translation on PC — one container
   per text surface, translate tables, repair font metrics, patch by file id.
   *Caveat:* Y is Unity, not the V/X/T engine, so this is a map of the problem,
   not a toolchain we can reuse.

## Consequence for our plan

The single most valuable fact is #1: **the running game hands displayable text
to a mod**. That makes a runtime translation (architecture **A**) a realistic
first target and moves the hardest unknown from "can we repack a 20 GB game" to
"does the font draw Polish letters and do the text boxes fit longer words".
Both questions are answered by an afternoon of testing on the owner's machine,
which is exactly what the phase-0 spike asks for.
