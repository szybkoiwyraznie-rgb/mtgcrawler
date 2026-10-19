# PL model viewer — owner's clipped-caption screenshot

Owner screenshot: L/R unit-change prompt clipped on the right, analog rotation
label touches the next D-pad icon, SELECT show/hide label runs past the edge.
No cache/font regression reported; preserve accepted Skupienie/font work.

Reviewed source-bound plan `config/pl/ui-mech-viewer-2026-10-19.json` changes only:

| Original sysmes root | Before | After | New cells |
|---|---|---|---:|
| 19028 | Zmień jednostkę | Zmień jedn. | 11 |
| 45684 | Zmień jednostkę | Zmień jedn. | 11 |
| 21284 | Obrót | Obr. | 4 |
| 21292 | Pokaż/ukryj | Ukryj | 5 |

The two unit-change roots contain identical original JP; both must be synchronized
for the existing whole-string conflict safeguard. Original authentic sysmes proves
those are the only two whole-string duplicates of that caption. Rotation and hide
have one whole root each. No replacements in longer help text or executable fields.
All new captions fit original JP cell widths (12/4/10 respectively), reducing old
14/5/10. Screenshot remains the layout evidence; cell checks aren't runtime approval.
SELECT still toggles overlay visibility: caption names the hide action available
while these prompts are visible, not a one-way change to the control.

Snapshot applied through normal stale/binding/token/cell guards; two focused tests
pass (including duplicate relationship through normal sysmes planner on synthetic
pool). Full suite, extracted-kit actual physical readback and delivery pending.
No game bytes or owner screenshot in Git; private work under `local/pl-mech-viewer/`.

Installation scope intended and to be verified: current accepted PPSSPP ISO-loading
setup, ISO YES, DLC NO; no PBOOT copy for this loader. Expected changes isolated to
configst/sysmes; no code/font/skill/pool/reading-script changes.
