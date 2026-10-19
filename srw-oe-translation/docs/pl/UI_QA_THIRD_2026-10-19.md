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
ISO replacement and whether DLC/which files must be recopied. Scope not yet known.

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

Explicit source-bound plan924 edits, no DLC member/pool targets; normal snapshot
materialization passes. Eleven new focused tests + updated historical checks pass.
Full suite, size readback, standalone delivery remain pending. No game assets
or screenshots in Git.
