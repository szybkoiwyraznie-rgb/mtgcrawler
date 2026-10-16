# Brief: translate battle quotes (cytaty.md) of Super Robot Wars OE into English

Read `/home/claude/work/STYLE.md` first (binding). Battle quotes are the short lines characters shout in combat animations
(attacking, dodging, taking damage, finishing moves, special pairings). They must sound like the character — punchy, natural,
the way official English SRW battle quotes read. These are heard/seen many times, so quality and voice matter a lot.

- Worksheet given in your task: groups `#G n` = one speaker (title line shows the Japanese name and series). Each distinct Japanese
  line appears once (duplicates are filled automatically).
- For every speaker with more than ~20 lines, read their voice card in `/home/claude/work/voice_cards.md` (`grep -n "^## "` to find
  them; headings contain the English and Japanese names). English names/attacks/units: `/home/claude/work/glossary.json`,
  `/home/claude/work/glossary_extra.tsv` (all attack names from mechy are there — use them exactly when a quote names an attack).
- Keep the 「 」 brackets exactly (the tool requires them). Keep line count. ≤ 46 units per line (52 absolute max).
- Canonical catchphrases should match the English the fans know (e.g. Amuro "Gundam, launching!" style; Kamina/Simon "Just who
  the hell do you think I am?!"); record any new recurring catchphrase decision in glossary_extra.tsv.
- Quotes addressed to specific enemies/rivals (named in the line) — use the glossary name. ＜主人公名＞ tokens stay.
- Don't flatten: vary exclamations, keep each character's register (polite/rough/archaic/childish, verbal tics like "mya", "sir", "y'know").
- Speakers shown as `ID nnn` are unnamed (generic soldiers etc.): neutral military tone.

Workflow: write your translation file (path in the task), validate with
`python3 /home/claude/tool/tr.py merge /home/claude/src/w/cytaty.md /home/claude/work/val/<name>.md <your file>` (only your groups matter),
0 "BŁĄD" required. Lines starting with '#', '@' or '\' must be written with a leading backslash.
Final reply: SHORT (≤ 6 lines): groups covered, count, 0 errors, notable decisions.
- Consistency with the story script: team shouts keep the romanized form used in the episodes ("Nekketsu Saikyo!", "Genki Bakuhatsu!",
  "Matchless!" for 絶対無敵). Before inventing an English rendering of a catchphrase, grep the translated episodes
  (`grep -rh "<distinctive JP>" /home/claude/src/epizod-*.md` then look at the same element in `/home/claude/out/sceny/`).
