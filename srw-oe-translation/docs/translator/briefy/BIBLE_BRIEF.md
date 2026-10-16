# Brief: story bible for the English translation of Super Robot Wars OE

Translators will work on episodes in parallel, so each needs to know what happens around their scenes.
Read the Japanese script for your assigned episodes in compact form: `/home/claude/work/compact/epizod-XX.txt`
(format: `== Scene N` then `Kind: text`, where Kind is a speaker name for dialogue, or Narracja/Miejsce/Warunek etc.).
For names use the glossary `/home/claude/work/glossary.json` (characters[].en["Imię pełne (dialogi)"], terms[]).
Read STYLE.md (`/home/claude/work/STYLE.md`) only for the name conventions.

For EACH assigned episode write `/home/claude/work/bible/epizod-XX.md` (English) containing:
1. `# Episode XX — <one-line English logline>` and a 5–10 sentence episode summary (which series' storylines are advanced, how the episode connects to the previous/next).
2. For each scene: `## Scene N — <English mission title if any> (<locations in English>)` then:
   - Present: main speakers (English names).
   - Synopsis: 3–8 sentences of what happens, in order, including emotional beats, jokes/gags, reveals.
   - Translator notes: tone of the scene (comic/tense/tragic), running jokes or callbacks, who is hostile/friendly to whom right now, any
     wordplay or culturally specific references and how to handle them, recurring phrases that must stay consistent, references to
     canonical anime events (name the original episode/event if you recognize it).
   - New names: proper nouns appearing here that are NOT in the glossary, as `JP → suggested EN (reason/confidence)`.
3. At the end: `## Character state at end of episode` — 5–15 bullets on relationships/alliances/knowledge (e.g. "Himari does not yet know Connect's true purpose").

Also append every suggested new name (one per line, `JP<TAB>EN<TAB>source/confidence (bible XX)`) to `/home/claude/work/glossary_extra.tsv` with `>>`
only if the JP is not already present there (grep first). Be concise but complete; do not translate dialogue in full.
Finish with a SHORT reply (≤10 lines): episodes done, anything surprising for translators.
