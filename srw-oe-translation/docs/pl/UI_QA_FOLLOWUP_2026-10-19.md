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
