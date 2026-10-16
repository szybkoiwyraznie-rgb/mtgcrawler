# SRW OE → English: translation style guide & technical rules (binding for every translator)

The goal: an English script that reads like a professional, official Bandai Namco localization — natural, literary where
the scene calls for it, faithful to each character's established voice, consistent across the whole game.

## Sources you must use
- Glossary (names, series, terms; official English first): `/home/claude/work/glossary.json`
  (keys per group: `characters[].en` = English for each in-game name field; `terms[]`; `series[]`).
- Voice cards (how each major character talks): `/home/claude/work/voice_cards.md` (search by name: `grep -n "^## " ...`).
- Story bible (English scene synopses, once available): `/home/claude/work/bible/epizod-XX.md`.
- Additional glossary built during translation (mecha, weapons, places): `/home/claude/work/glossary_extra.tsv` (JP<TAB>EN<TAB>note). If you coin or confirm a new recurring name not in the glossary, APPEND it there (one line, `>>`), and check the file first so you reuse existing entries.
- The pilot `/home/claude/out/sceny/epizod-00.md` shows the expected quality and format conventions.

## Style decisions (agreed with the owner)
- Official English terminology (English SRW releases V/X/T/30 > official anime English > fan convention).
- Honorifics localized: no -san/-kun/-chan/-sama/-dono/senpai in English. Convey the relationship through wording
  (Captain, Sir, Ma'am, Doctor, Teacher/Ms. Himeki, or simply the name). 先輩 from Himari → usually dropped or the name token.
- Names in Western order (Koji Kabuto). Exactly the glossary spelling. CP932 only: no macrons, accents, em/en dashes, „, •, ♥.
- Do NOT translate literally. Rewrite into idiomatic English that carries the same meaning, emotion, humor and subtext.
  Avoid translationese ("I will do my best!" for every 頑張ります; "It can't be!" spam for まさか — vary it: "No way…", "Impossible…", "That can't be right…").
  Iconic, canonical lines should land with the weight fans know (e.g. Amuro's "Gundam, launching!", Kamina's bravado).
- Keep the speaker's voice: check the voice card for every major speaker before writing their lines.
- Punctuation: "…" (single char) for ellipses, "!?" or "?!" consistently as "?!". Stutters "W-what?!". No em dashes — use "…" or "-" for cut-offs ("Nice to meet y…").
- Inner monologue （…） → ASCII parentheses "(…)"; continuation lines start with ONE space so text aligns after "(".
- Quoted text 「…」 inside story lines → “…” (or ASCII "…"); in battle quotes (cytaty.md, kind [Kwestia]) the 「 」 brackets MUST be kept exactly.
- 『…』 terms (UI commands in tutorials) → 'Move', 'Attack' etc. in single quotes.
- Mission conditions: plain English, no quotes around unit names: "Defeat all enemies", "Exart is shot down", "3 turns pass", "① White Base is shot down". Keep ①②③ etc.
- Location headers: "Connect Station / Hangar" style (slash with spaces). "U.C. 0079, Earth Sphere".
- Ranks (Gundam UC): navy system per Sunrise English — 少尉 Ensign, 中尉 Lieutenant (j.g.), 大尉 Lieutenant, 少佐 Lieutenant Commander (addressed as "Commander"), 中佐 Commander, 大佐 Captain, 艦長 Captain. Other series: follow their glossary terms.

## Hard technical rules (the import tool rejects violations)
1. Same number of lines as the Japanese (blank lines inside the text too — write `~` for a blank line in the translation file). Trailing newlines are added automatically — don't add them.
2. Keep every control token exactly, same count, in the same place: `⏎` (window-clear; stays at the same line position, usually end of line), `＃` at start, `%s`, `%d`, `%%`, `＠0`…`＠9`, `＜主人公名＞` (protagonist given name), `＜主人公姓＞` (surname), `＜特殊トラップ＞`. Never replace the name tokens with a name. `＜主人公名＞・＜主人公姓＞` → `＜主人公名＞ ＜主人公姓＞`.
3. `<0x0F>` in Japanese is an escape for a voiced half-width kana (it consumes the next byte). NEVER put `<0x0F>` in English — just write plain ASCII.
4. Width (units: ASCII char = 1, full-width/Japanese char = 2, `…` = 2, `“”` = 2, `①` = 2, the name token ＜主人公名＞ = 12):
   - dialogue / battle quotes: ≤ 46 per line recommended, 52 absolute max;
   - narration: ≤ 50 per line;
   - list/name fields: keep near the original length (soft limit shown in the worksheet as ~N; don't exceed N+1/3);
   - fields with "max NB": hard byte budget for the whole text — must fit.
5. CP932 only (see above). Use plain ASCII letters/digits for English (not full-width Ａ１).

## Workflow (tooling)
- Worksheet: `python3 /home/claude/tool/tr.py extract SRC.md [--groups A-B]` prints untranslated elements:
  `#G <group>` / `# <title | context>` / `@<id> [kind] (limit; N lines)` + JP lines (indented 2 spaces, `~` = blank line).
- Write your translation file in the SAME structure (only `#G`, `@id` and the English lines; lines starting with `#` other than `#G` are comments):
```
#G 15
@3
Our radio is being jammed.
We can't reach HQ.
```
- Validate: `python3 /home/claude/tool/tr.py merge SRC.md /home/claude/work/val/<yourname>.md YOUR.txt` — prints `wypełnione X/Y; błędy N`. "BŁĄD" = must fix; "UWAGA" = warning (width over recommended 46 / soft limit) — fix when reasonably possible. Delete your val file before re-running if you want a clean run (merge keeps previous EN from the out file).
- Iterate until 0 errors and every element in your assigned range is filled. Never edit files in `/home/claude/src` or `/home/claude/out`.
