# Our tools

Project-owned tools. The pinned upstream retro-trans tools live in
[`../vendor/retro-trans/tools/`](../vendor/retro-trans/tools/) and are not
edited in place (see `../vendor/retro-trans/PROVENANCE.md`); our tools
import or drive them.

| Tool | Job |
|---|---|
| `gen_pl_atlas.py` | Renders the 87-glyph half-width atlas (69 upstream Latin + 18 Polish) from one TrueType font at identical metrics (12×24, 2bpp, 72 B/glyph) + preview sheet + assignments JSON. Needs Pillow. |
| `pl_font_codes.json` | Generated code/encoding assignments (regular/bold private codes, reserved dialogue bytes). Prototype freeze candidate — see `../docs/FONT_RESEARCH.md`. |
| `patch_hwfont_pl.py` | Polish extension of the vendored hwfont patcher (imported as a library): NART=87/NGLYPH=174, Polish setText-table entries, cave PT_LOAD extended 6,320 → 8,192 B. Input: ELF already processed by vendored `patch_renderer.py`. |
| `build_test_kit.py` | Assembles the owner P3 font-test kit zip in `local/dist/` (hash-pins the atlas; fails on drift). |

Owner-side kit sources (bat + patcher + Polish instructions) live in
[`../kit/`](../kit/). The patcher verifies source extent hashes, patches
only a `*_PLTEST` copy of the ISO, and logs everything to
`srwz_patch_log.txt`.

Still to come: the production patch kit (full translation package, all
text surfaces) once phases 1–2 close — see `../docs/STATUS.md`.
