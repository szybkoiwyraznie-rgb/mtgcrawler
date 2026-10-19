# PL UI follow-up — owner crash regression and four screenshots

Owner reports v2.2-PL3-UI crashes when opening Seishiro's Spirit details from
intermission mech inspection. Previously details/levels worked (name suffix was
corrupt). Treat v2.2 cache-layout repair as runtime-regressed, not approved.
Do not ask for another font or over-budget experiment. One batched repair.

Crash screenshot (PPSSPP1.20.4/Windows): PC0x08a14904, Read Word0x0000006d;
stack return0x089a60a0 then0x089a35cc. Subtract measured load base0x08804000:
function0x210904, caller return0x1a20a0, outer return0x19f5cc. Actual caller
0x1a209c still loads drawable from cache+0x14, while v2.2 moved it to+0x2c.
The following callee reads+8 from that pointer. For ASCII `Skupienie`, old+0x14
holds0x65 (`e`) followed by NUL:0x65+8=0x6d, matching the reported bad address.
This is a concrete omitted consumer in the previous layout audit; the earlier
186 memory-only tests covered constructors/draw but NOT this details consumer.

Investigating a lower-impact repair: keep ALL original object fields/consumer
instructions at original offsets, allocate a new tail name array instead of
shifting members. Must audit name-address construction, allocation sites and
exercise actual details call chain, not merely a synthetic string check.
No new fix/runtime success claimed at this checkpoint.

Other reports:
- Saving warning lacks Polish letters in executable source row0x08bf34bf:
  `Nie wyjmuj nosnika ani nie wylaczaj konsoli.` Broad executable-caption
  spelling audit needed; distinguish CP932 game-font rows from system UTF-8.
- Button strip: Search / Upgrade / Change Unit Display overlap or clip.
- Other strip: Change Display clips; use compact source-bound prompts.

Private source ELF SHA-256 remains
26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052.
Screenshots/game assets remain ignored; no proprietary bytes committed.

## Implemented replacement (checkpoint, standalone delivery still pending)

Replace69-word v2.2 migration with14 words: ten allocations40->72 bytes;
three ctor name addresses and one draw-name address+0x0c->+0x28. Original40-byte
prefix is unchanged, including drawable+14, other members and external flags.
This avoids needing to discover/rewrite every external old-field consumer.
All ten direct constructor callsites/preceding allocations re-inspected. Four
name-address constructions in the three constructors/draw were re-inspected.
Exact original hash/words, atomic refusal and31-byte name gate remain active.
No branch/relocation/font/EN change. Must build on originals, not v2.2 output.

Extended real-MIPS probe now executes full1a201c selection caller and210904
callee, not stubs for those functions. Four additional call slices exercise
other external drawable+14 consumers at1a1d80/1a3574/1a6ccc/1a7008. OTHER external
UI/font/getter callees remain stubbed, so this is NOT PPSSPP/runtime approval.
Historical v2.2 module from6af6ece reproduces source pointer0x65 and bad read0x6d
through ALL THREE constructors. Unmodified game still corrupts the name but
passes details (consistent with owner before/after evidence). New repair:
186 name/ctor cases,930 real details calls, guards intact. Metadata receipt:
`ui-followup-cache-verification.json`.

Source-bound plan `config/pl/ui-followup-2026-10-19.json`:178 executable spelling
fixes,15 compact sysmes labels. Every spelling edit is accent-only (deaccenting
recovers exact previous text), same encoded byte length/newlines/control tokens;
no literary translation or skill mechanics rewrite. Saving and autosave warnings,
Osłona/Okrążenie/Części/etc and error prompts included. All178 pass actual
executable source geometry/target codec validator. Three system UTF-8 rows
excluded: title plus two save-list descriptions retain ASCII due to unverified
system glyphs, not because game-font encoding is broken. Additional sysmes spelling
scan produced45 candidates, ALL contextually correct words `ze`/`gra`/`grupa`;
reviewed, NOT blindly replaced. No universal all-text/proofreading completion claim.

Prompts `Zmień widok [jednostek]` ->`Widok` (12 rows), `Ulepszenia` ->`Ulepsz`
(3 rows with JP機体改造). Width5/6 native cells, no larger than original JP
slot; physical standalone readback and owner visual confirmation pending.

Checks so far:6 cache unit tests,3 new source-bound follow-up tests; authentic
configst-only rebuild reports no problems. Full suite/standalone/CI still pending.
