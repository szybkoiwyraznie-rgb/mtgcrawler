# Brief: translate UI / table texts (widoki) of Super Robot Wars OE into English

Read `/home/claude/work/STYLE.md` first (binding rules + tooling). These are menus, system messages, skill/item/spirit descriptions,
mission titles, BGM titles etc. Goal: read like the UI of an official English Super Robot Wars release (SRW V/X/T/30 English UI conventions).

## Conventions (SRW English UI)
- Spirit Commands (精神コマンド): use the official English names from Bandai Namco's English SRW releases (SRW V/X/T/30), already decided (SRW T/30 English): 必中 Bullseye,
  閃き/ひらめき Flash, 幸運 Fortune, 努力 Gain; others are in glossary_extra.tsv.
  For every other spirit, verify the official English name on the web (Akurasu / SRW wiki pages for SRW 30 or T English) — do not guess.
  Record each decision in glossary_extra.tsv and use it consistently everywhere (spirit names also appear in skill/item descriptions and system messages).
- Pilot skills: use English SRW names where they exist (援護攻撃 Support Attack, 援護防御 Support Defense, 底力 Prevail, 気力限界突破 Will Limit Break,
  ニュータイプ Newtype, 強化人間 Enhanced Human / Cyber-Newtype per series, 切り払い Parry, 撃ち落とし Shoot Down,
  カウンター Counter, ヒット&アウェイ Hit & Away, 連続攻撃 Continuous Attack, 闘争心 Fighting Spirit, 指揮官 Commander, 集束攻撃 Focused Attack…).
  Verify against SRW T/30 English skill lists; record decisions in glossary_extra.tsv.
- Stats: 格闘 Melee, 射撃 Ranged, 技量 Skill, 防御 Defense, 回避 Evade, 命中 Accuracy, 気力 Will, ＳＰ SP, ＨＰ HP, ＥＮ EN, 装甲 Armor, 運動性 Mobility,
  照準値 Aim, 移動力 Move, 地形適応 Terrain (空 Air/陸 Land/海 Sea/宇 Space), 改造 Upgrade, 資金 Credits, 撃墜数 Kills, 経験値 EXP, パーツ Parts
  — follow SRW English UI wording; keep labels short (UI fields have little room).
- Mission/BGM titles: BGM = official English song titles where the song has one (anime OP/ED/insert songs often have romanized official titles —
  use the official romanization/English title, e.g. "Tobe! Gundam" style); game-original tracks: translate the title naturally.
- System messages: concise, clear, imperative where appropriate ("Save complete.", "Do you want to quit?"). Keep every token (＠0…, %s, %d, %%, ⏎).
- Descriptions: clear game-manual English. Numbers/percent: keep tokens; "%%" stays "%%".
- Length: obey the worksheet limit: `max NB` = hard byte budget (must fit!), `~N` = soft (don't exceed N+1/3), `46/line` = per-line width.
  UI is tight — prefer standard abbreviations used in English SRW (Atk, Def, Acc, Eva, Crit, Mov, Lv, EXP, HP, EN, SP, Rng).

## Workflow
1. Your worksheet is given in your task (pre-deduplicated: each distinct Japanese string appears once; duplicates are filled automatically later).
2. Write your translation file (path given in the task) in the `#G` / `@id` format (STYLE.md). Work in sections; save often.
3. Validate: `python3 /home/claude/tool/tr.py merge /home/claude/src/w/<FILE>.md /home/claude/work/val/<name>.md <your tr file>`
   — only errors in YOUR groups/elements matter. 0 "BŁĄD" required; fix width warnings where reasonable.
4. Append decided recurring terms (spirit commands, skills, stats, UI labels) to `/home/claude/work/glossary_extra.tsv` (grep first, no duplicates/contradictions).
Final reply: SHORT (≤ 8 lines): what you covered, counts, 0 errors confirmed, notable decisions.

## %s placeholders (FINAL rule from the package author, enforced by the validator)
Each `%s` is one of three kinds, listed per Japanese text in /home/claude/work/tokeny.tsv (columns: id, kinds in order of
occurrence e.g. `L,T,L`, Japanese text as JSON — look up by the Japanese text):
- L = literal engine placeholder (game inserts a number/level/threshold): KEEP in English, same count, same order relative to each
  other and to other tokens (＠0, %%). Moving a whole phrase together with its %s is fine; swapping %s is not.
- T = voiced-kana glyph token (e.g. `追加%s*ﾒｰ%s&` = 追加ダメージ): REMOVE from English together with the ONE character right after
  the %s, and translate the word naturally ("additional damage"), no %s.
- C = other control marker: KEEP as %s in the same place.
- Texts not in tokeny.tsv: keep every %s. A visible `<0x0F>` + next char is also a kana token: remove both.
`tr.py merge` checks this automatically and tells you the required %s count when it is wrong.
The English must read naturally with a value inserted at each remaining %s.
