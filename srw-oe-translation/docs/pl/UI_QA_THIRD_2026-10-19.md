# PL UI third owner batch — seven screenshots

Owner runtime acceptance: v2.3 Skupienie works and details no longer crash.
Do NOT redo cache/font hypotheses or claim all UI is accepted.

New requested batch:
1. Remove routine PATCH.bat ISO-font explanation (keep real missing-input guard).
2. Startup SYSTEM dialog shows reserved PL bytes as Japanese/symbols: restore
   English there, not the accepted bitmap font. Earlier assumption all CP932
   executable captions use game font was too broad; audit other system strings.
3. Focus Lv1 SP-15Unik needs separation. Inspect ALL Spirit/skill compositions,
   including coloured <Penetracja Lv1>Obr-30% shown separately.
4. Results/Parts label "Większa szansa na części" overflows; shorten.
5. TeamParts/Bonus/Progress header shows leftover fragments above patched English
   text. Investigate texture rectangles/cleaning; not ordinary sysmes spelling.
6. Results stat labels collide with values in several fixed-width slots; compact.
7. Intermission Search label still overlaps next triangle despite prior reductions.

Seven private screenshots remain outside Git. Originals/saves preserved, EN
unchanged by PL-only fixes. One coherent kit, real-byte and assembly/layout checks;
no runtime claims until owner confirmation. Every delivery MUST explicitly state
ISO replacement and whether DLC/which files must be recopied. Current verified scope below: ISO yes, DLC no.

## Implemented checkpoint (not yet delivered)

Routine launcher echo removed, actual ISO-input failure retained.

System dialog proven, not inferred just from font: original data word411e78 ->
string3ef678; calla88b4 passes it to1cf5e0; call1cf73c -> imported sceUtility
MsgDialogInitStart3edeac (NID2ad8e239). Added English source-bound fallback for
that caption and two directly proven utility connection/age warnings (3eff00/1c).
Two more utility warnings come from sysmes IDs367/36a at actual pool roots39944
and40068: restored English too. IDs are read at+0x0c+i*8 by e7f10; do NOT infer
from the historically shifted `Sysmes.ids` convenience property's index. Existing
pointer/table words remain unchanged. Guards reject PL bitmap glyphs on these
known system consumers; game-font saving warning stays PL, native font untouched.
This corrects the too-broad prior assumption about all CP932 display captions.
No claim every indirect system-dialog string has now been traced.

Spacing audit reads real baseline CLI output:60 Spirit records/120 effect fields
and1469 Skill records/1985 populated effect/effect_brief fields, with four actual
argument indices+28. Proposes spaces in TEMPLATES, NEVER in shared pools; handles
colour codes split across `%s` argument/template boundary. No blanket space around
all placeholders (word-internal substitutions intentionally concatenate). After
colour handling correction:0 unresolved fragment-internal candidates for reviewed
patterns;57 Spirit fields+186spaces,412 Skill fields+689spaces. Both structured and
legacy-offset sources updated consistently (57+809 source rows). Does not claim
grammatical/numeric/literary QA completion; preserves all non-space text there.
38 executable effect overrides separately corrected, including Penetracja header.
14 tight slots needed compact labels:5 `LvN`->`LN`,9 `Obrona:`->`Obr.:`, without
changing values/meaning/control tokens or relaxing byte limits.

15 compact sysmes rows: Results fields <=10cells; drop-chance label
`Szansa części+`14cells; Search `Szk.`4cells, no larger than original 検索 slot.
Prior `Szukaj`6cells could not fit that4-cell Japanese button slot.

Texture evidence: intsys_04 original grey rows0..11/12..23/24..35, but previous
third-row boxes started at29, leaving Japanese upper halves24..28 visible over
new text. PL-only atlas layout now clears full rows/covers old glyphs and draws
in proper row24..35. English rendering uses ORIGINAL spec geometry unchanged.
PL headers include composite `Cz.`+`oddz.`, `Premia`, `Postęp`. Both authentic
IM1000/IM3000 carry identical intsys_04. Preview checked clean; actual-container
build/readback still pending, NOT PPSSPP appearance approval.

Initial source-bound plan924 edits, no DLC member/pool targets; normal snapshot
materialization passes. Eleven new focused tests + updated historical checks pass.
Full suite, size readback, standalone delivery remain pending. No game assets
or screenshots in Git.


## Final offline verification — v2.4-PL3-UI

Normal extracted ZIP CLI rebuilt authentic config00/configst/font/IM1000/IM3000
and EBOOT inside private miniature **NONPLAYABLE** ISO. Exit0, no top-level
problems. Readback receipt: `ui-third-physical-verification.json`. Not gameplay.

First full run caught a duplicate whole sysmes string:40068 shares identical JP
with44704. The existing whole-string writer correctly refused two translations.
Kept its conflict safeguard; bound the identical English caption to BOTH roots
and scoped the glyph guard to44704 too. Final plan **925** sources; exactly925
materialized value changes, zero unplanned/copy propagation. The launcher message
and all five distinct proven system captions now have source-bound English;
three sysmes roots represent two logical messages. Previous partial builds NOT
delivered. Audit recollection: prototype1102rows/863spaces superseded; authoritative
final audit is57Spirit+186spaces,412Skill+689spaces.

Actual physical comparison confirms every revised field equals the reviewed
proposal; all other text fields/names, four argument indices, numeric parameters
and numeric tails identical. Base/pool/parameter pointer relationships valid,
all records4-byte aligned, fragment pools identical, formatter/newline counts
unchanged, no remaining reviewed spacing-pattern candidates. Added fail-closed
check that visible text cannot change by splitting a colour control.

Skill00 **216488 B <=216768**, margin280 B (v2.3:215764 B). Raw689spaces plus35 B
net alignment/slack. Spirit17431->17635 B, raw186spaces+18 B net slack. No size
limits loosened. Full-total report still `fits:null` because eight DLC weren't
re-downloaded: NOT a full nine-file size test. DLC values are demonstrably unchanged
across ALL materialized source rows; base Item/Skill fragment pools byte-identical
also. No DLC reinstall required for the owner's accepted v2.3 installation.

Physical exe exact normal patcher output397writes; code .text identical to accepted
14-word cache patch, native font SHA identical to accepted v2.3. sysmes1182entries:
all keys unchanged,17actual strings changed (18source bindings incl. interior alias).
Both IM container readbacks match renderer byte-for-byte; changes isolated to
intsys_04 compared with immutable previous PL spec, and **EN render byte-identical**
on authentic GIMs. Full suite **1697 tests OK,3skipped**. Original inputs only read.
Inherited eight nested dictionary refusals and legacy CP932-only verification
noise remain documented in receipt; do not present as a globally warning-free run.

### Installation — explicit

For the owner's current **PPSSPP1.20.4 ISO-loading setup, upgrading v2.3 -> v2.4**:
**ISO: YES**, rebuild and replace `patched.iso`. **DLC: NO**, keep current DLC files;
no new EDAT/CPK transfers. Builder may regenerate them and PBOOT with full inputs,
but generated does not mean required to copy. **PBOOT.PBP: no new copy needed for
this accepted ISO path**, not a general claim about every PSP/PPSSPP update loader.

Owner test remains a single cold-start run (ordinary game save, not save-state):
startup SYSTEM is English; Skupienie Lv1 spaces and another skill header; Parts
header/drop label; Results numbers; □/△ intermission footer. No repeat cache/font
hypothesis test. Runtime acceptance of this third UI batch still pending.

### Delivered kit

[srw-oe-translation-pl-v2.4-PL3-UI.zip](https://drive.google.com/file/d/1O8p3IdvyTYLLrenmAwhj83613t20Nkjr/view)
7404376B/91members, Drive size/MD5 equals local ZIP. Local CRC + all90payload SHA
checks pass; all91members byte-identical to physically verified kit. No game assets.
Receipt `pl3-ui-third-delivery.json`. Source6797a7f pushed on assigned branch/PR20;
local EN+PL release-pair validation passes. GitHub Actions39283036474 queued at
delivery, NOT claimed successful. No merge/main publication.
