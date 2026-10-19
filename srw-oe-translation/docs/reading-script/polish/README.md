# Polish reading editions — work in progress

Owner request (2026-10-19): Polish counterparts of delivered episodes 01–03 and
mech catalogue v3, using the accepted PL3 snapshot. This is a reading/reference
export, not new literary translation or a game patch.

Checkpoint: the frozen catalogue EN package was recovered from commit
`aa178c7264514d0c36c102393705cdacb6e0ab77`; all original inputs match the
catalogue inventory. Regeneration reproduced the delivered 667590-byte English
v3 file exactly (`19228a10bf3dcb4d0ae404a8de08b37f316db32de7a7de0eda7b9e2d90989dd7`).
The PL catalogue localizer checks physical/JP bindings and equality of non-text
facts. It uses Polish descriptions at the 20 original override offsets, not an
invented PL executable or the 17 EN-only erratum strings. Unused binary pool
entries are not required as translations; consumed fragments must be Polish.

Early reading plans were not retained. Source mapping of all base-scene prose
in the three delivered English documents has now been recovered and checked
for full, ordered coverage. Polish editorial plans, variant rechecking,
end-to-end verification and delivery are not complete at this checkpoint.

Private Markdown, raw inputs, extracted models and materialized PL3 stay under
ignored `local/polish-reading/` / the private Drive folder. Tools never modify
source packages or game files. Current three focused unit tests pass.
